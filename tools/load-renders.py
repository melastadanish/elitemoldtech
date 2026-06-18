#!/usr/bin/env python3
"""
load-renders.py — Load saved part renders for quote generation.

Rules:
  - Has 3D          → use 3D
  - Has 3D + 2D     → use 3D (preferred)
  - Has 2D only     → use 2D
  - Neither         → key absent from result

Returns: dict of part_key → base64 JPEG string (best available image)

Usage (import into quote generator):
    import sys; sys.path.insert(0, "tools")
    from load_renders import load_best_renders
    imgs = load_best_renders("storage/2026-06/EMT-LM762-Q001-v1")
    # imgs["20-02.01"] → base64 string

Usage (CLI check):
    python3 tools/load-renders.py storage/2026-06/EMT-LM762-Q001-v1
"""

import base64
import json
from pathlib import Path


MIN_VALID_BYTES = 5_000


def load_best_renders(job_folder: str) -> dict[str, str]:
    """Load best available render per part. Returns {part_key: base64_jpeg}."""
    renders_dir = Path(job_folder) / "client-files" / "renders"
    manifest_path = renders_dir / "manifest.json"
    imgs = {}

    if not renders_dir.exists():
        return imgs

    # Use manifest if available (authoritative)
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        for key, info in manifest.items():
            best = info.get("best")
            if best is None:
                continue
            img_path = renders_dir / f"{key}-{best}.jpg"
            if img_path.exists() and img_path.stat().st_size >= MIN_VALID_BYTES:
                with open(img_path, "rb") as fh:
                    imgs[key] = base64.b64encode(fh.read()).decode()
        return imgs

    # Fallback: scan folder directly (no manifest)
    keys_3d = {f.stem.replace("-3d", "") for f in renders_dir.glob("*-3d.jpg")
               if f.stat().st_size >= MIN_VALID_BYTES}
    keys_2d = {f.stem.replace("-2d", "") for f in renders_dir.glob("*-2d.jpg")
               if f.stat().st_size >= MIN_VALID_BYTES}

    for key in sorted(keys_3d | keys_2d):
        # 3D preferred
        if key in keys_3d:
            p = renders_dir / f"{key}-3d.jpg"
        else:
            p = renders_dir / f"{key}-2d.jpg"
        with open(p, "rb") as fh:
            imgs[key] = base64.b64encode(fh.read()).decode()

    return imgs


def print_summary(job_folder: str):
    renders_dir = Path(job_folder) / "client-files" / "renders"
    manifest_path = renders_dir / "manifest.json"

    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        print(f"Manifest: {manifest_path}")
        for key in sorted(manifest.keys()):
            info = manifest[key]
            has3d = "✅ 3D" if info["has_3d"] else "—    "
            has2d = "✅ 2D" if info["has_2d"] else "—    "
            best = f"→ using {info['best'].upper()}" if info["best"] else "⚠️  NO IMAGE"
            print(f"  {key}:  {has3d}  {has2d}  {best}")
    else:
        imgs = load_best_renders(job_folder)
        print(f"No manifest found — scanned folder directly")
        for key, _ in sorted(imgs.items()):
            print(f"  {key}: loaded")

    imgs = load_best_renders(job_folder)
    print(f"\nTotal loaded: {len(imgs)} parts ready for quote generation")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 tools/load-renders.py <job-folder>")
        sys.exit(1)
    print_summary(sys.argv[1])
