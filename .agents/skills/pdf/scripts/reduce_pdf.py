#!/usr/bin/env python3
"""Reduce PDF file size by recompressing embedded images."""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter


PRESET_QUALITY = {
    "screen": 55,
    "ebook": 70,
    "print": 85,
}


def file_size(path: Path) -> int:
    return path.stat().st_size


def format_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size = size / 1024
    return f"{size:.1f} GB"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument(
        "--preset",
        choices=sorted(PRESET_QUALITY),
        default="ebook",
        help="Quality preset for image recompression.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        help="JPEG quality override from 1 to 95.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing output file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_pdf = args.input_pdf
    output_pdf = args.output_pdf

    if not input_pdf.is_file():
        raise SystemExit(f"Input PDF does not exist: {input_pdf}")
    if input_pdf.suffix.lower() != ".pdf":
        raise SystemExit(f"Input must be a PDF: {input_pdf}")
    if output_pdf.exists() and not args.overwrite:
        raise SystemExit(f"Output already exists; pass --overwrite to replace: {output_pdf}")
    if output_pdf.resolve() == input_pdf.resolve():
        raise SystemExit("Refusing to overwrite the input PDF.")

    quality = args.quality if args.quality is not None else PRESET_QUALITY[args.preset]
    if not 1 <= quality <= 95:
        raise SystemExit("--quality must be between 1 and 95.")

    reader = PdfReader(str(input_pdf))
    input_pages = len(reader.pages)
    input_size = file_size(input_pdf)

    writer = PdfWriter(clone_from=str(input_pdf))
    images_seen = 0
    images_recompressed = 0
    warnings: list[str] = []

    for page_index, page in enumerate(writer.pages, start=1):
        for image in page.images:
            images_seen += 1
            try:
                image.replace(image.image, quality=quality)
                images_recompressed += 1
            except Exception as exc:  # pypdf image handling varies by PDF encoding.
                warnings.append(f"page {page_index}: could not recompress {image.name}: {exc}")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with output_pdf.open("wb") as output:
        writer.write(output)

    output_pages = len(PdfReader(str(output_pdf)).pages)
    if output_pages != input_pages:
        raise SystemExit(f"Validation failed: page count changed from {input_pages} to {output_pages}.")

    output_size = file_size(output_pdf)
    reduction = 0 if input_size == 0 else (1 - output_size / input_size) * 100

    print(f"Wrote: {output_pdf}")
    print(f"Pages: {input_pages}")
    print(f"Images: {images_recompressed}/{images_seen} recompressed at quality {quality}")
    print(f"Size: {format_size(input_size)} -> {format_size(output_size)} ({reduction:.1f}% reduction)")
    for warning in warnings:
        print(f"Warning: {warning}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
