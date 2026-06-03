---
name: pdf
description: Work with PDF files, including reducing/compressing PDFs, deleting or dropping pages, converting PNG/images to PDF, converting PDF pages to PNG/images, inspecting PDFs, and building or adjusting PDF transformation automation while preserving document quality.
---

# PDF

## Overview

Use this skill for agent-run PDF transformations with a quality-first workflow: inspect inputs, choose the least destructive operation, write a new output file, and verify the result.

## General Rules

- Preserve source files unless the user explicitly asks to overwrite them.
- Use clear output names such as `document-reduced.pdf`, `document-pages-1-3.pdf`, or `page-001.png`.
- Validate file existence, file type, output size, and page count where applicable.
- Preserve page order, orientation, searchable text, annotations, forms, bookmarks, and signatures unless the user accepts changing them.
- Report meaningful tradeoffs, especially quality loss, rasterization, grayscale conversion, removed pages, or metadata changes.

## Script Layout

Place reusable PDF automation in `scripts/`. Prefer deterministic command-line scripts with explicit input/output paths and safe defaults.

These scripts are intended to be run by agents, not manually operated by end users. Keep interfaces non-interactive, validate arguments before writing outputs, print concise success summaries, and use non-zero exits for failures.

Expected script names:

- `scripts/reduce_pdf.py`
- `scripts/drop_pages.py`
- `scripts/png_to_pdf.py`
- `scripts/pdf_to_png.py`

Scripts should exit non-zero when inputs are invalid, outputs cannot be written, or validation fails.

## Reduce PDF

Use when the user wants to reduce, compress, optimize, or shrink a PDF for upload, sharing, email, archival, or storage limits.

Workflow:

1. Record input file size and page count.
2. Determine whether the PDF is mostly scanned images, generated text/vector content, or mixed.
3. Prefer metadata cleanup, object stream optimization, and duplicate resource removal for text/vector PDFs.
4. Prefer image recompression, image downsampling, and grayscale conversion only when image-heavy PDFs need meaningful reduction.
5. Avoid rasterizing searchable/vector PDFs unless the user accepts loss of text selection and likely quality degradation.
6. If attempting a target size, iterate from conservative to stronger settings and stop once the target is met with acceptable quality.
7. Verify output size, page count, and readability.

Expected `reduce_pdf.py` behavior:

- Accept one input PDF and one output path.
- Support a target size when practical.
- Expose quality presets such as `screen`, `ebook`, and `print`.
- Return or print input size, output size, percent reduction, page count, and warnings.

## Drop Pages

Use when the user wants to remove one or more pages from a PDF.

Workflow:

1. Confirm whether page numbers are user-facing 1-based page numbers.
2. Validate requested pages exist.
3. Write a new PDF without the dropped pages.
4. Verify the output page count equals input page count minus removed pages.
5. Report removed pages and output path.

Expected `drop_pages.py` behavior:

- Accept one input PDF, one output path, and a page list or page ranges.
- Treat CLI page numbers as 1-based unless a flag says otherwise.
- Reject page `0`, negative pages, duplicates if ambiguous, and pages beyond the document length.

## PNG To PDF

Use when the user wants to convert one or more PNG files into a PDF.

Workflow:

1. Preserve image order explicitly; do not rely on ambiguous shell expansion order when order matters.
2. Validate image dimensions and orientation.
3. Create a PDF with one image per page unless the user asks for a different layout.
4. Report output path, page count, and any image scaling.

Expected `png_to_pdf.py` behavior:

- Accept one or more PNG input paths and one output PDF path.
- Support preserving original pixel dimensions or fitting to standard page sizes.
- Handle transparency predictably, usually by compositing onto a white background unless requested otherwise.

## PDF To PNG

Use when the user wants to convert PDF pages into PNG images.

Workflow:

1. Identify requested page range or default to all pages.
2. Choose a resolution appropriate to the purpose: lower for previews, higher for print/OCR/inspection.
3. Write stable numbered output files.
4. Verify the number of PNG files matches the selected page count.

Expected `pdf_to_png.py` behavior:

- Accept one input PDF and an output directory or filename pattern.
- Support page ranges.
- Support a DPI or scale setting.
- Print generated file paths and warnings.
