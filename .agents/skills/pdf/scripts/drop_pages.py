#!/usr/bin/env python3
"""Drop pages from a PDF using 1-based page numbers."""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def parse_page_spec(spec: str) -> list[int]:
    """
    Docstring for parse_page_spec
    
    :param spec: Description
    :type spec: str
    :return: Description
    :rtype: list[int]
    """
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
    return pages


def parse_args() -> argparse.Namespace:
    """
    Docstring for parse_args
    
    :return: Description
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument(
        "--drop",
        required=True,
        help="1-based pages or ranges to remove, for example '1,3-5'.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing output file.",
    )
    return parser.parse_args()


def main() -> int:
    """
    Docstring for main
    
    :return: Description
    :rtype: int
    """
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

    try:
        drop_pages = parse_page_spec(args.drop)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if any(page <= 0 for page in drop_pages):
        raise SystemExit("Page numbers are 1-based; page 0 and negative pages are invalid.")
    if len(set(drop_pages)) != len(drop_pages):
        raise SystemExit("Duplicate dropped pages are ambiguous; specify each page once.")

    reader = PdfReader(str(input_pdf))
    page_count = len(reader.pages)
    invalid_pages = [page for page in drop_pages if page > page_count]
    if invalid_pages:
        raise SystemExit(f"Pages out of range for {page_count}-page PDF: {invalid_pages}")
    if len(drop_pages) == page_count:
        raise SystemExit("Refusing to create an empty PDF.")

    drop_indexes = {page - 1 for page in drop_pages}
    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        if index not in drop_indexes:
            writer.add_page(page)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with output_pdf.open("wb") as output:
        writer.write(output)

    output_pages = len(PdfReader(str(output_pdf)).pages)
    expected_pages = page_count - len(drop_pages)
    if output_pages != expected_pages:
        raise SystemExit(f"Validation failed: expected {expected_pages} pages, found {output_pages}.")

    print(f"Wrote: {output_pdf}")
    print(f"Dropped pages: {sorted(drop_pages)}")
    print(f"Pages: {page_count} -> {output_pages}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
