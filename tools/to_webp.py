#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch converter: PNG/JPG -> WebP for the RPC flagship site.

- Originals are never modified or deleted. Only new .webp files are written.
- Each file gets a max width based on how large it is actually displayed.
  Images smaller than the max width are NOT upscaled.
- Console output is ASCII only (PowerShell 5.1 mangles non-ASCII).

Usage:
    python tools/to_webp.py --dry-run     # show the plan, write nothing
    python tools/to_webp.py               # convert
    python tools/to_webp.py --quality 90  # override quality for all files
"""

import argparse
import fnmatch
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is not installed. Run: python -m pip install pillow")

# Repo-relative default. Resolved against the repository root (this file's parent).
DEFAULT_SRC = os.path.join("assets", "img")

# (glob pattern, max width, quality). First match wins.
RULES = [
    ("mc2_ss*",        1000, 80),   # hero slideshow  (displayed at 760px)
    ("mc_ep*_banner*", 1000, 80),   # episode banners (displayed at 860px)
    ("top_banner_mc*", 1000, 80),
    ("mc_extra_*",      800, 82),   # ep3 thumb, cropped and zoomed
    ("mc_deepsea_*",   1600, 80),   # kept large: possible full-width use
    ("profile_*",       800, 80),
    ("top_icon_*",      240, 82),   # displayed at 120px (2x for retina)
    ("char_*",          300, 82),
    ("award_*",         600, 85),   # award badges (displayed around 280px)
    ("fanart_*",       1200, 82),   # gallery page, not built yet
]
DEFAULT_RULE = (1200, 80)

SOURCE_EXT = (".png", ".jpg", ".jpeg")


def rule_for(name):
    for pattern, width, quality in RULES:
        if fnmatch.fnmatch(name.lower(), pattern.lower()):
            return width, quality
    return DEFAULT_RULE


def human(n):
    return "%.0fKB" % (n / 1024.0) if n < 1024 * 1024 else "%.1fMB" % (n / 1048576.0)


def convert(src_dir, dry_run, quality_override):
    names = sorted(
        f for f in os.listdir(src_dir)
        if f.lower().endswith(SOURCE_EXT)
    )
    if not names:
        print("No source images found in %s" % src_dir)
        return 0

    total_before = 0
    total_after = 0
    rows = []

    for name in names:
        src = os.path.join(src_dir, name)
        dst = os.path.join(src_dir, os.path.splitext(name)[0] + ".webp")
        max_w, quality = rule_for(name)
        if quality_override:
            quality = quality_override

        before = os.path.getsize(src)
        with Image.open(src) as im:
            w, h = im.size
            if w > max_w:
                new_h = max(1, round(h * max_w / float(w)))
                out = im.resize((max_w, new_h), Image.LANCZOS)
                resized = "%dx%d -> %dx%d" % (w, h, max_w, new_h)
            else:
                out = im.copy()
                resized = "%dx%d (kept)" % (w, h)

            # WebP has no palette mode; RGBA keeps transparency, RGB otherwise.
            if out.mode not in ("RGB", "RGBA"):
                out = out.convert("RGBA" if "A" in out.mode or out.mode == "P" else "RGB")

            if not dry_run:
                out.save(dst, "WEBP", quality=quality, method=6)

        after = os.path.getsize(dst) if (not dry_run and os.path.exists(dst)) else 0
        total_before += before
        total_after += after
        rows.append((name, resized, quality, before, after))

    width_name = max(len(r[0]) for r in rows) + 2
    print("%-*s %-24s %3s %10s %10s" % (width_name, "file", "size", "q", "before", "after"))
    print("-" * (width_name + 52))
    for name, resized, quality, before, after in rows:
        print("%-*s %-24s %3d %10s %10s" % (
            width_name, name, resized, quality, human(before),
            human(after) if after else "-"))
    print("-" * (width_name + 52))
    print("total: %s -> %s" % (
        human(total_before), human(total_after) if total_after else "(dry run)"))
    if total_after:
        print("saved: %s (%.0f%%)" % (
            human(total_before - total_after),
            100.0 * (total_before - total_after) / total_before))
    print("originals were not touched.")
    return len(rows)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)

    ap = argparse.ArgumentParser(description="Convert site images to WebP.")
    ap.add_argument("--src", default=os.path.join(root, DEFAULT_SRC),
                    help="directory holding the images (default: %s)" % DEFAULT_SRC)
    ap.add_argument("--dry-run", action="store_true", help="show the plan, write nothing")
    ap.add_argument("--quality", type=int, default=0, help="override quality (1-100)")
    args = ap.parse_args()

    if not os.path.isdir(args.src):
        sys.exit("Not a directory: %s" % args.src)

    print("source: %s" % args.src)
    print("mode  : %s" % ("DRY RUN" if args.dry_run else "convert"))
    print("")
    convert(args.src, args.dry_run, args.quality)


if __name__ == "__main__":
    main()
