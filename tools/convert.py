#!/usr/bin/env python3
"""Convert a virtual-grid JSON layout for use in MOSS-Image."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import convert_text  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Source relative_1000 JSON file")
    parser.add_argument("--width", type=int, required=True, help="Render width in pixels, multiple of 16")
    parser.add_argument("--height", type=int, required=True, help="Render height in pixels, multiple of 16")
    parser.add_argument("-o", "--output", type=Path, help="Output path; defaults to stdout")
    args = parser.parse_args()
    try:
        result = convert_text(args.input.read_text(encoding="utf-8"), args.width, args.height, pretty=True)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    if args.output:
        args.output.write_text(result + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
