#!/usr/bin/env python3
"""
Simple ffmpeg batch converter: convert .webm -> .mp4

Usage examples:
  python aac.py file1.webm file2.webm
  python aac.py --dir .         # convert all .webm in current dir
  python aac.py --dir videos --overwrite

This script calls the system ffmpeg via subprocess. Ensure ffmpeg is installed and on PATH.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def convert_file(input_path: Path, output_path: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-c:v",
        "libx264",
        "-preset",
        "superfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        str(output_path),
    ]
    print(f"Converting: {input_path} -> {output_path}")
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Convert .webm files to .mp4 using ffmpeg")
    parser.add_argument("files", nargs="*", help="Input files (if omitted, search directory for .webm)")
    parser.add_argument("--dir", "-d", default=".", help="Directory to search when no files are given")
    parser.add_argument("--overwrite", "-o", action="store_true", help="Overwrite existing outputs")
    args = parser.parse_args()

    if args.files:
        paths = [Path(p) for p in args.files]
    else:
        paths = sorted(Path(args.dir).glob("*.webm"))

    if not paths:
        print("No input files found.", file=sys.stderr)
        return 1

    for p in paths:
        out = p.with_suffix(".mp4")
        if out.exists() and not args.overwrite:
            print(f"Skipping existing file: {out}")
            continue
        try:
            convert_file(p, out)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {p}: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())