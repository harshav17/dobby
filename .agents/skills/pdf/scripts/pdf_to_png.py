#!/usr/bin/env python3
"""Render PDF pages to PNG images."""

from __future__ import annotations

import argparse
from pathlib import Path

import fitz


def parse_page_spec(spec: str | None, page_count: int) -> list[int]:
    if spec is None:
        return list(range(1, page_count + 1))

    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            if start > end:
                raise ValueError(f"Invalid descending range: {part}")
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))

    if not pages:
        raise ValueError("No pages specified.")
    if any(page <= 0 for page in pages):
        raise ValueError("Page numbers are 1-based; page 0 and negative pages are invalid.")
    if len(set(pages)) != len(pages):
        raise ValueError("Duplicate pages are ambiguous; specify each page once.")

    invalid_pages = [page for page in pages if page > page_count]
    if invalid_pages:
        raise ValueError(f"Pages out of range for {page_count}-page PDF: {invalid_pages}")

    return pages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--pages", help="1-based pages or ranges to render, for example '1,3-5'.")
    parser.add_argument("--dpi", type=int, default=144, help="Render resolution.")
    parser.add_argument("--prefix", default="page", help="Output filename prefix.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing existing PNG files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_pdf = args.input_pdf

    if not input_pdf.is_file():
        raise SystemExit(f"Input PDF does not exist: {input_pdf}")
    if input_pdf.suffix.lower() != ".pdf":
        raise SystemExit(f"Input must be a PDF: {input_pdf}")
    if args.dpi <= 0:
        raise SystemExit("--dpi must be positive.")

    doc = fitz.open(input_pdf)
    try:
        pages = parse_page_spec(args.pages, doc.page_count)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scale = args.dpi / 72
    matrix = fitz.Matrix(scale, scale)
    generated: list[Path] = []

    for page_number in pages:
        output_path = args.output_dir / f"{args.prefix}_{page_number:03d}.png"
        if output_path.exists() and not args.overwrite:
            raise SystemExit(f"Output already exists; pass --overwrite to replace: {output_path}")

        page = doc.load_page(page_number - 1)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        pixmap.save(output_path)
        generated.append(output_path)

    if len(generated) != len(pages):
        raise SystemExit(f"Validation failed: expected {len(pages)} images, wrote {len(generated)}.")

    print(f"Saved {len(generated)} images to {args.output_dir}")
    for output_path in generated:
        print(f"- {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
