#!/usr/bin/env python3
"""Convert one or more PNG/JPEG images into a PDF."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import img2pdf
from PIL import Image
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def parse_args() -> argparse.Namespace:
    """
    Docstring for parse_args
    
    :return: Description
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path, help="Input PNG/JPEG files in page order.")
    parser.add_argument("-o", "--output", required=True, type=Path, help="Output PDF path.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing output file.",
    )
    return parser.parse_args()


def normalized_image_paths(images: list[Path], temp_dir: Path) -> list[Path]:
    """
    Docstring for normalized_image_paths
    
    :param images: Description
    :type images: list[Path]
    :param temp_dir: Description
    :type temp_dir: Path
    :return: Description
    :rtype: list[Path]
    """
    paths: list[Path] = []
    for image_path in images:
        if not image_path.is_file():
            raise SystemExit(f"Image does not exist: {image_path}")
        if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise SystemExit(f"Unsupported image type: {image_path}")

        with Image.open(image_path) as image:
            has_alpha = image.mode in {"RGBA", "LA"} or (
                image.mode == "P" and "transparency" in image.info
            )
            if has_alpha:
                background = Image.new("RGB", image.convert("RGBA").size, "white")
                background.paste(image.convert("RGBA"), mask=image.convert("RGBA").getchannel("A"))
                normalized_path = temp_dir / f"{image_path.stem}-flattened.png"
                background.save(normalized_path)
                paths.append(normalized_path)
            else:
                paths.append(image_path)
    return paths


def main() -> int:
    """
    Docstring for main
    
    :return: Description
    :rtype: int
    """
    args = parse_args()
    output_pdf = args.output

    if output_pdf.exists() and not args.overwrite:
        raise SystemExit(f"Output already exists; pass --overwrite to replace: {output_pdf}")
    if output_pdf.suffix.lower() != ".pdf":
        raise SystemExit(f"Output must be a PDF: {output_pdf}")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_name:
        image_paths = normalized_image_paths(args.images, Path(temp_name))
        with output_pdf.open("wb") as output:
            output.write(img2pdf.convert([str(path) for path in image_paths]))

    page_count = len(PdfReader(str(output_pdf)).pages)
    if page_count != len(args.images):
        raise SystemExit(f"Validation failed: expected {len(args.images)} pages, found {page_count}.")

    print(f"Wrote: {output_pdf}")
    print(f"Pages: {page_count}")
    print("Images:")
    for image_path in args.images:
        print(f"- {image_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
