#!/usr/bin/env python3
"""
render-parts.py — Elite Mold Tech image renderer
Renders 3D views (STEP) and 2D drawing thumbnails (PDF).
Saves to client-files/renders/ — quote generation reads from there automatically.

Rules:
  - Has STEP only    → render 3D
  - Has STEP + PDF   → render 3D (preferred), keep 2D as fallback
  - Has PDF only     → render 2D

Usage:
    python3 tools/render-parts.py storage/2026-06/EMT-LM762-Q001-v1
    python3 tools/render-parts.py storage/2026-06/EMT-LM762-Q001-v1 --force   # re-render all
"""

import sys
import json
import io
from pathlib import Path


MIN_VALID_BYTES = 5_000   # renders smaller than this are considered blank/corrupt
FILL_RATIO = 0.82         # part should occupy this fraction of the image frame
RENDER_SIZE = 500         # output image size in pixels (square)


# ── part key normalisation ─────────────────────────────────────────────────────
def extract_part_key(stem: str) -> str:
    """
    LM762X54-20-02.01-Shaft  →  20-02.01
    20-02.01-Shaft            →  20-02.01
    20-02.01                  →  20-02.01
    """
    import re
    # Match the numeric section like 20-02.01 or 15-07.02
    m = re.search(r'(\d{2}-\d{2}\.\d{2})', stem)
    return m.group(1) if m else stem


# ── 3D render from STEP ────────────────────────────────────────────────────────
def render_step(step_path: Path, out_path: Path) -> tuple[bool, str]:
    try:
        import trimesh
        import numpy as np
        from PIL import Image

        mesh = trimesh.load(str(step_path), force="mesh")
        if isinstance(mesh, trimesh.Scene):
            geoms = list(mesh.geometry.values())
            if not geoms:
                return False, "Scene has no geometry"
            mesh = trimesh.util.concatenate(geoms)

        if len(mesh.vertices) == 0:
            return False, "Empty mesh"

        # Centre and normalise to unit cube
        mesh.vertices -= mesh.center_mass
        max_extent = max(mesh.extents)
        if max_extent > 0:
            mesh.apply_scale(1.0 / max_extent)

        # Isometric rotation: Rx(25°) then Rz(45°)
        rx = trimesh.transformations.rotation_matrix(np.radians(25), [1, 0, 0])
        rz = trimesh.transformations.rotation_matrix(np.radians(45), [0, 0, 1])
        mesh.apply_transform(rx)
        mesh.apply_transform(rz)

        png = mesh.scene().save_image(resolution=[RENDER_SIZE, RENDER_SIZE], visible=True)
        if png is None:
            return False, "save_image returned None"

        # Composite onto white background
        img = Image.open(io.BytesIO(png)).convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])

        # Auto-crop to content then pad so part fills ~FILL_RATIO of frame
        bg = _tight_crop_and_pad(bg, fill_ratio=FILL_RATIO)
        bg.save(str(out_path), "JPEG", quality=88)

        size = out_path.stat().st_size
        if size < MIN_VALID_BYTES:
            out_path.unlink(missing_ok=True)
            return False, f"Output too small ({size} bytes) — likely blank"

        return True, "ok"

    except Exception as e:
        return False, str(e)


# ── 2D drawing thumbnail from PDF ─────────────────────────────────────────────
def render_pdf(pdf_path: Path, out_path: Path) -> tuple[bool, str]:
    """
    Extract only the part geometry from the drawing sheet.
    Strategy:
      1. Render at high resolution
      2. Strip the outer border frame (sheet margin ~4% each side)
      3. Strip the title block (bottom ~28% of sheet)
      4. Content-crop to the tightest bounding box of actual drawing lines
      5. Pad to 82% fill on square canvas
    """
    try:
        import fitz
        from PIL import Image
        import numpy as np

        doc = fitz.open(str(pdf_path))
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0), alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        w, h = img.size

        # Step 1: strip sheet border margins and title block
        margin_x = int(w * 0.04)
        margin_top = int(h * 0.04)
        title_block_h = int(h * 0.28)   # title block is bottom 28%
        drawing_area = img.crop((margin_x, margin_top, w - margin_x, h - title_block_h))

        # Step 2: content-crop to actual drawing lines (non-white, non-light-grey pixels)
        arr = np.array(drawing_area)
        # Threshold: pixels darker than 200 on any channel = drawing content
        mask = (arr < 200).any(axis=2)
        rows = np.where(mask.any(axis=1))[0]
        cols = np.where(mask.any(axis=0))[0]

        if len(rows) == 0 or len(cols) == 0:
            # Fallback: use the drawing area as-is
            part_img = drawing_area
        else:
            pad = 15
            da_w, da_h = drawing_area.size
            r0 = max(0, rows[0] - pad)
            r1 = min(da_h, rows[-1] + pad)
            c0 = max(0, cols[0] - pad)
            c1 = min(da_w, cols[-1] + pad)
            part_img = drawing_area.crop((c0, r0, c1, r1))

        # Step 3: pad to 82% fill on square canvas
        part_img = _tight_crop_and_pad(part_img, fill_ratio=FILL_RATIO, bg_color=(255, 255, 255))
        part_img.save(str(out_path), "JPEG", quality=88)

        size = out_path.stat().st_size
        if size < MIN_VALID_BYTES:
            out_path.unlink(missing_ok=True)
            return False, f"Output too small ({size} bytes)"

        return True, "ok"

    except Exception as e:
        return False, str(e)


# ── Image utilities ────────────────────────────────────────────────────────────
def _content_crop(img, padding_px: int = 20):
    """Crop to the bounding box of non-white content."""
    import numpy as np
    arr = np.array(img)
    # Non-white mask: any channel < 240
    mask = (arr < 240).any(axis=2)
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return img
    r0, r1 = max(0, rows[0] - padding_px), min(arr.shape[0], rows[-1] + padding_px)
    c0, c1 = max(0, cols[0] - padding_px), min(arr.shape[1], cols[-1] + padding_px)
    return img.crop((c0, r0, c1, r1))


def _tight_crop_and_pad(img, fill_ratio: float = 0.82, bg_color=(255, 255, 255)):
    """
    Resize image so content fills fill_ratio of a square canvas,
    then centre it on that canvas.
    """
    from PIL import Image as PILImage
    content_w, content_h = img.size
    canvas_size = int(max(content_w, content_h) / fill_ratio)
    canvas = PILImage.new("RGB", (canvas_size, canvas_size), bg_color)
    # Scale content to fill_ratio of canvas
    target = int(canvas_size * fill_ratio)
    scale = target / max(content_w, content_h)
    new_w = int(content_w * scale)
    new_h = int(content_h * scale)
    resized = img.resize((new_w, new_h), PILImage.LANCZOS)
    x = (canvas_size - new_w) // 2
    y = (canvas_size - new_h) // 2
    canvas.paste(resized, (x, y))
    # Final resize to RENDER_SIZE
    return canvas.resize((RENDER_SIZE, RENDER_SIZE), PILImage.LANCZOS)


# ── File discovery ─────────────────────────────────────────────────────────────
ASSEMBLY_KEYWORDS = {"-00", "assembly", "assy", "bom", "-00.00"}

def _is_assembly(stem: str) -> bool:
    s = stem.lower()
    return any(k in s for k in ASSEMBLY_KEYWORDS)


def discover_files(client_files: Path):
    """Return dict: part_key → {"step": Path|None, "pdf": Path|None}"""
    parts: dict = {}

    for ext in ("*.step", "*.STEP", "*.stp", "*.STP"):
        for f in client_files.glob(ext):
            if _is_assembly(f.stem):
                continue
            key = extract_part_key(f.stem)
            parts.setdefault(key, {"step": None, "pdf": None, "stem": f.stem})
            parts[key]["step"] = f

    for f in client_files.glob("*.pdf"):
        if _is_assembly(f.stem):
            continue
        key = extract_part_key(f.stem)
        parts.setdefault(key, {"step": None, "pdf": None, "stem": f.stem})
        parts[key]["pdf"] = f

    return parts


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/render-parts.py <job-folder> [--force]")
        sys.exit(1)

    job_folder = Path(sys.argv[1])
    force = "--force" in sys.argv
    client_files = job_folder / "client-files"
    renders_dir = client_files / "renders"

    if not client_files.exists():
        print(f"Error: {client_files} does not exist")
        sys.exit(1)

    renders_dir.mkdir(exist_ok=True)
    print(f"\nRendering parts for: {job_folder.name}")
    print(f"Output folder: {renders_dir}")
    print(f"Mode: {'force re-render all' if force else 'skip cached'}\n")

    parts = discover_files(client_files)
    if not parts:
        print("No STEP or PDF files found in client-files/")
        sys.exit(1)

    manifest = {}  # part_key → {best, has_3d, has_2d, status_3d, status_2d}

    for key in sorted(parts.keys()):
        info = parts[key]
        has_step = info["step"] is not None
        has_pdf = info["pdf"] is not None

        # Decide what to render
        render_3d = has_step
        render_2d = has_pdf

        result = {"key": key, "has_3d": False, "has_2d": False, "best": None,
                  "status_3d": "no_file", "status_2d": "no_file"}

        print(f"  {key}")

        # 3D render
        if render_3d:
            out_3d = renders_dir / f"{key}-3d.jpg"
            if out_3d.exists() and not force:
                print(f"    3D: cached ✓")
                result["has_3d"] = True
                result["status_3d"] = "cached"
            else:
                print(f"    3D: rendering ...", end=" ", flush=True)
                ok, msg = render_step(info["step"], out_3d)
                if ok:
                    print("✓")
                    result["has_3d"] = True
                    result["status_3d"] = "rendered"
                else:
                    print(f"✗  ({msg})")
                    result["status_3d"] = f"failed: {msg}"

        # 2D render
        if render_2d:
            out_2d = renders_dir / f"{key}-2d.jpg"
            if out_2d.exists() and not force:
                print(f"    2D: cached ✓")
                result["has_2d"] = True
                result["status_2d"] = "cached"
            else:
                print(f"    2D: rendering ...", end=" ", flush=True)
                ok, msg = render_pdf(info["pdf"], out_2d)
                if ok:
                    print("✓")
                    result["has_2d"] = True
                    result["status_2d"] = "rendered"
                else:
                    print(f"✗  ({msg})")
                    result["status_2d"] = f"failed: {msg}"

        # Pick best image (3D preferred)
        if result["has_3d"]:
            result["best"] = "3d"
        elif result["has_2d"]:
            result["best"] = "2d"
        else:
            result["best"] = None

        manifest[key] = result

    # Save manifest
    manifest_path = renders_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Summary
    total = len(manifest)
    ok_3d = sum(1 for v in manifest.values() if v["has_3d"])
    ok_2d = sum(1 for v in manifest.values() if v["has_2d"])
    no_img = sum(1 for v in manifest.values() if v["best"] is None)

    print(f"\n{'─'*50}")
    print(f"Parts: {total}  |  3D: {ok_3d}  |  2D only: {ok_2d - ok_3d}  |  No image: {no_img}")
    print(f"Manifest: {manifest_path}")
    if no_img:
        missing = [k for k, v in manifest.items() if v["best"] is None]
        print(f"⚠️  No image for: {', '.join(missing)}")
    print(f"\nDone. Quote generation will use best available image per part.")


if __name__ == "__main__":
    main()
