#!/usr/bin/env python3
"""
render-3d.py — Render 3D views from STEP files
Part fills ~82% of the frame. White background. Isometric view.

Usage:
    # Single STEP file
    python3 tools/render-3d.py path/to/part.step

    # Whole job folder (all STEP files in client-files/)
    python3 tools/render-3d.py storage/2026-06/EMT-LM762-Q001-v1

    # Force re-render even if output exists
    python3 tools/render-3d.py storage/2026-06/EMT-LM762-Q001-v1 --force

Output saved to: client-files/renders/<part-key>-3d.jpg
Requires: pip3 install trimesh cascadio "pyglet<2" pillow numpy
"""

import sys
import io
import re
from pathlib import Path


# ── Config ─────────────────────────────────────────────────────────────────────
OUTPUT_SIZE     = 500    # Output image pixels (square)
FILL_RATIO      = 0.82   # Part occupies this fraction of the output frame
ROTATION_X_DEG  = 25     # Isometric tilt
ROTATION_Z_DEG  = 45     # Isometric rotation
MIN_VALID_BYTES = 5_000  # Files smaller than this are rejected as blank render

STEP_EXTENSIONS = {".step", ".stp"}
ASSEMBLY_KEYWORDS = {"-00", "assembly", "assy", "-00.00"}


# ── Core render ────────────────────────────────────────────────────────────────
def extract_dimensions(step_path: Path) -> dict | None:
    """Return bounding box in mm as {L, W, H} sorted largest first. None on failure."""
    try:
        import trimesh
        mesh = trimesh.load(str(step_path), force="mesh")
        if isinstance(mesh, trimesh.Scene):
            geoms = list(mesh.geometry.values())
            mesh = trimesh.util.concatenate(geoms) if geoms else None
        if mesh is None or len(mesh.vertices) == 0:
            return None
        e = sorted((mesh.extents * 1000).tolist(), reverse=True)  # metres → mm
        def fmt(v): r = round(float(v), 1); return int(r) if r == int(r) else r
        return {"L": fmt(e[0]), "W": fmt(e[1]), "H": fmt(e[2])}
    except Exception:
        return None


def render_step_to_jpg(step_path: Path, out_path: Path) -> tuple[bool, str]:
    """
    Render one STEP file to an isometric JPEG.
    Returns (success, message).
    """
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
            return False, "Empty mesh — STEP file may be a sketch or assembly reference"

        # Centre on mass, normalise to unit cube
        mesh.vertices -= mesh.center_mass
        max_extent = max(mesh.extents)
        if max_extent > 0:
            mesh.apply_scale(1.0 / max_extent)

        # Isometric rotation
        rx = trimesh.transformations.rotation_matrix(
            np.radians(ROTATION_X_DEG), [1, 0, 0]
        )
        rz = trimesh.transformations.rotation_matrix(
            np.radians(ROTATION_Z_DEG), [0, 0, 1]
        )
        mesh.apply_transform(rx)
        mesh.apply_transform(rz)

        png = mesh.scene().save_image(
            resolution=[OUTPUT_SIZE, OUTPUT_SIZE], visible=True
        )
        if png is None:
            return False, "Renderer returned None — check pyglet<2 is installed"

        # Composite onto white background
        img = Image.open(io.BytesIO(png)).convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])

        # Scale part to fill FILL_RATIO of the frame
        result = _fit_to_canvas(bg)
        result.save(str(out_path), "JPEG", quality=88)

        size = out_path.stat().st_size
        if size < MIN_VALID_BYTES:
            out_path.unlink(missing_ok=True)
            return False, f"Output too small ({size} bytes) — likely blank render"

        return True, "ok"

    except ImportError as e:
        missing = str(e)
        hint = 'pip3 install trimesh cascadio "pyglet<2" pillow numpy'
        return False, f"Missing dependency: {missing}  →  {hint}"
    except Exception as e:
        return False, str(e)


def _fit_to_canvas(img, bg=(255, 255, 255)):
    """Scale content so it fills FILL_RATIO of a square canvas."""
    from PIL import Image

    # Auto-crop white margin first
    import numpy as np
    arr = np.array(img)
    mask = (arr < 240).any(axis=2)
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if len(rows) > 0 and len(cols) > 0:
        pad = 10
        h, w = arr.shape[:2]
        img = img.crop((
            max(0, cols[0] - pad),
            max(0, rows[0] - pad),
            min(w, cols[-1] + pad),
            min(h, rows[-1] + pad),
        ))

    content_w, content_h = img.size
    canvas_px = int(max(content_w, content_h) / FILL_RATIO)
    canvas = Image.new("RGB", (canvas_px, canvas_px), bg)
    scale = (canvas_px * FILL_RATIO) / max(content_w, content_h)
    new_w = int(content_w * scale)
    new_h = int(content_h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas.paste(resized, ((canvas_px - new_w) // 2, (canvas_px - new_h) // 2))
    return canvas.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.LANCZOS)


# ── Helpers ────────────────────────────────────────────────────────────────────
def extract_part_key(stem: str) -> str:
    m = re.search(r'(\d{2}-\d{2}\.\d{2})', stem)
    return m.group(1) if m else stem


def is_assembly(stem: str) -> bool:
    s = stem.lower()
    return any(k in s for k in ASSEMBLY_KEYWORDS)


def find_step_files(folder: Path) -> list[Path]:
    files = []
    for ext in STEP_EXTENSIONS:
        files += list(folder.glob(f"*{ext}"))
        files += list(folder.glob(f"*{ext.upper()}"))
    return sorted(f for f in files if not is_assembly(f.stem))


# ── Entry points ───────────────────────────────────────────────────────────────
def process_single(step_path: Path, force: bool = False):
    if not step_path.exists():
        print(f"File not found: {step_path}")
        return

    if is_assembly(step_path.stem):
        print(f"Skipped (assembly): {step_path.name}")
        return

    out_dir = step_path.parent / "renders"
    out_dir.mkdir(exist_ok=True)
    key = extract_part_key(step_path.stem)
    out = out_dir / f"{key}-3d.jpg"

    if out.exists() and not force:
        print(f"Already rendered (use --force to re-render): {out.name}")
        return

    print(f"Rendering {step_path.name} ...", end=" ", flush=True)
    ok, msg = render_step_to_jpg(step_path, out)
    if ok:
        kb = out.stat().st_size // 1024
        print(f"✓  saved {out.name} ({kb} KB)")
    else:
        print(f"✗  {msg}")


def process_job_folder(job_folder: Path, force: bool = False):
    client_files = job_folder / "client-files"
    if not client_files.exists():
        print(f"Error: {client_files} does not exist")
        return

    renders_dir = client_files / "renders"
    renders_dir.mkdir(exist_ok=True)

    step_files = find_step_files(client_files)

    if not step_files:
        print(f"No STEP files found in {client_files}")
        print("Drop .step files into client-files/ and re-run.")
        return

    print(f"\nJob: {job_folder.name}")
    print(f"STEP files found: {len(step_files)}")
    print(f"Mode: {'force re-render' if force else 'skip cached'}\n")

    ok_count = 0
    fail_count = 0
    dimensions = {}

    # Load existing dimensions so cached parts keep their values
    dim_path = renders_dir / "dimensions.json"
    if dim_path.exists():
        import json
        with open(dim_path) as f:
            dimensions = json.load(f)

    for step in step_files:
        key = extract_part_key(step.stem)
        out = renders_dir / f"{key}-3d.jpg"

        if out.exists() and not force:
            kb = out.stat().st_size // 1024
            dim = dimensions.get(key)
            dim_str = f"  {dim['L']}×{dim['W']}×{dim['H']} mm" if dim else ""
            print(f"  ✓ {key} (cached, {kb} KB){dim_str}")
            ok_count += 1
            continue

        print(f"  → {key} ...", end=" ", flush=True)
        # Extract dimensions before rendering (same mesh load)
        dim = extract_dimensions(step)
        if dim:
            dimensions[key] = dim

        ok, msg = render_step_to_jpg(step, out)
        if ok:
            kb = out.stat().st_size // 1024
            dim_str = f"  {dim['L']}×{dim['W']}×{dim['H']} mm" if dim else ""
            print(f"✓  ({kb} KB){dim_str}")
            ok_count += 1
        else:
            print(f"✗  {msg}")
            fail_count += 1

    # Save dimensions
    import json
    with open(dim_path, "w") as f:
        json.dump(dimensions, f, indent=2)

    print(f"\n{'─'*50}")
    print(f"✅ Done: {ok_count}   ❌ Failed: {fail_count}")
    print(f"Dimensions saved: {dim_path}")
    print(f"Renders saved to: {renders_dir}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = Path(sys.argv[1])
    force = "--force" in sys.argv

    if target.is_file() and target.suffix.lower() in STEP_EXTENSIONS:
        process_single(target, force)
    elif target.is_dir():
        process_job_folder(target, force)
    else:
        print(f"Error: {target} is not a STEP file or job folder")
        sys.exit(1)


if __name__ == "__main__":
    main()
