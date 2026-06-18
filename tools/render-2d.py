#!/usr/bin/env python3
"""
render-2d.py — Extract part drawing from engineering PDF
Removes: sheet border, title block, notes, revision table
Keeps:   only the part geometry / drawing view

Usage:
    # Single file
    python3 tools/render-2d.py path/to/part.pdf

    # Whole job folder (all PDFs in client-files/)
    python3 tools/render-2d.py storage/2026-06/EMT-LM762-Q001-v1

    # Force re-render even if output exists
    python3 tools/render-2d.py storage/2026-06/EMT-LM762-Q001-v1 --force

Output saved to: client-files/renders/<part-key>-2d.jpg
"""

import sys
import io
import re
from pathlib import Path


# ── Config ─────────────────────────────────────────────────────────────────────
RENDER_SCALE    = 3.0    # PDF zoom — higher = more detail
OUTPUT_SIZE     = 500    # Output image pixels (square)
FILL_RATIO      = 0.82   # Part occupies this fraction of the output frame
BORDER_MARGIN   = 0.04   # Sheet border to strip from each side (fraction)
TITLE_BLOCK     = 0.28   # Title block height to strip from bottom (fraction)
CONTENT_THRESH  = 200    # Pixels darker than this are considered drawing content
CONTENT_PADDING = 15     # Pixels of padding around detected content bounding box
MIN_VALID_BYTES = 5_000  # Files smaller than this are rejected as blank

ASSEMBLY_KEYWORDS = {"-00", "assembly", "assy", "-00.00"}


# ── Core render ────────────────────────────────────────────────────────────────
def render_pdf_to_part(pdf_path: Path, out_path: Path) -> tuple[bool, str]:
    """
    Extract part geometry from one PDF drawing.
    Returns (success, message).
    """
    try:
        import fitz
        import numpy as np
        from PIL import Image

        doc = fitz.open(str(pdf_path))
        if doc.page_count == 0:
            return False, "PDF has no pages"

        page = doc[0]
        mat = fitz.Matrix(RENDER_SCALE, RENDER_SCALE)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        w, h = img.size

        # Step 1 — strip outer sheet border and title block
        mx = int(w * BORDER_MARGIN)
        my = int(h * BORDER_MARGIN)
        title_h = int(h * TITLE_BLOCK)
        drawing_area = img.crop((mx, my, w - mx, h - title_h))

        # Step 2 — detect bounding box of actual drawing content
        arr = np.array(drawing_area)
        mask = (arr < CONTENT_THRESH).any(axis=2)
        rows = np.where(mask.any(axis=1))[0]
        cols = np.where(mask.any(axis=0))[0]

        if len(rows) == 0 or len(cols) == 0:
            part_img = drawing_area
        else:
            da_w, da_h = drawing_area.size
            r0 = max(0, rows[0]  - CONTENT_PADDING)
            r1 = min(da_h, rows[-1] + CONTENT_PADDING)
            c0 = max(0, cols[0]  - CONTENT_PADDING)
            c1 = min(da_w, cols[-1] + CONTENT_PADDING)
            part_img = drawing_area.crop((c0, r0, c1, r1))

        # Step 3 — scale to fill FILL_RATIO of a square canvas
        result = _fit_to_canvas(part_img)
        result.save(str(out_path), "JPEG", quality=88)

        size = out_path.stat().st_size
        if size < MIN_VALID_BYTES:
            out_path.unlink(missing_ok=True)
            return False, f"Output too small ({size} bytes) — likely blank page"

        return True, "ok"

    except ImportError as e:
        return False, f"Missing dependency: {e}  →  pip3 install pymupdf pillow numpy"
    except Exception as e:
        return False, str(e)


def _fit_to_canvas(img, bg=(255, 255, 255)):
    from PIL import Image
    content_w, content_h = img.size
    canvas_px = int(max(content_w, content_h) / FILL_RATIO)
    canvas = Image.new("RGB", (canvas_px, canvas_px), bg)
    scale = (canvas_px * FILL_RATIO) / max(content_w, content_h)
    new_w = int(content_w * scale)
    new_h = int(content_h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    x = (canvas_px - new_w) // 2
    y = (canvas_px - new_h) // 2
    canvas.paste(resized, (x, y))
    return canvas.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.LANCZOS)


# ── Part key extraction ────────────────────────────────────────────────────────
def extract_part_key(stem: str) -> str:
    m = re.search(r'(\d{2}-\d{2}\.\d{2})', stem)
    return m.group(1) if m else stem


def is_assembly(stem: str) -> bool:
    s = stem.lower()
    return any(k in s for k in ASSEMBLY_KEYWORDS)


# ── Entry points ───────────────────────────────────────────────────────────────
def process_single(pdf_path: Path, force: bool = False):
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        return

    if is_assembly(pdf_path.stem):
        print(f"Skipped (assembly drawing): {pdf_path.name}")
        return

    out_dir = pdf_path.parent / "renders"
    out_dir.mkdir(exist_ok=True)
    key = extract_part_key(pdf_path.stem)
    out = out_dir / f"{key}-2d.jpg"

    if out.exists() and not force:
        print(f"Already rendered (use --force to re-render): {out.name}")
        return

    print(f"Rendering {pdf_path.name} ...", end=" ", flush=True)
    ok, msg = render_pdf_to_part(pdf_path, out)
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

    pdfs = sorted([
        p for p in client_files.glob("*.pdf")
        if not is_assembly(p.stem)
    ])

    if not pdfs:
        print("No part PDFs found in client-files/")
        return

    print(f"\nJob: {job_folder.name}")
    print(f"PDFs found: {len(pdfs)}")
    print(f"Mode: {'force re-render' if force else 'skip cached'}\n")

    ok_count = 0
    fail_count = 0

    for pdf in pdfs:
        key = extract_part_key(pdf.stem)
        out = renders_dir / f"{key}-2d.jpg"

        if out.exists() and not force:
            kb = out.stat().st_size // 1024
            print(f"  ✓ {key} (cached, {kb} KB)")
            ok_count += 1
            continue

        print(f"  → {key} ...", end=" ", flush=True)
        ok, msg = render_pdf_to_part(pdf, out)
        if ok:
            kb = out.stat().st_size // 1024
            print(f"✓  ({kb} KB)")
            ok_count += 1
        else:
            print(f"✗  {msg}")
            fail_count += 1

    print(f"\n{'─'*50}")
    print(f"✅ Done: {ok_count}   ❌ Failed: {fail_count}")
    print(f"Saved to: {renders_dir}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = Path(sys.argv[1])
    force = "--force" in sys.argv

    if target.is_file() and target.suffix.lower() == ".pdf":
        process_single(target, force)
    elif target.is_dir():
        process_job_folder(target, force)
    else:
        print(f"Error: {target} is not a PDF file or job folder")
        sys.exit(1)


if __name__ == "__main__":
    main()
