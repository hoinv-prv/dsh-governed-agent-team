"""
extract.py - Universal document content extractor

Extract structured content from documents to MD/JSON/HTML with optional rich pipeline.

Usage:
    python extract.py <file> [--format md|json|html|rich] [--out-dir output/]

Examples:
    extract.py document.pdf                    # Simple MD
    extract.py report.xlsx --rich              # Full pipeline
    extract.py chart.pdf --extract-charts      # Extract charts to CSV
"""
import argparse
import base64
import json
import re
import sys
from pathlib import Path


def extract_simple(input_path: Path, out_dir: Path, format: str, **options):
    """
    Simple extraction: input → single output file (MD/JSON/HTML/text).
    """
    try:
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import PdfFormatOption
        from docling_core.types.doc.base import ImageRefMode
    except ImportError:
        print("ERROR: docling not installed. Run: pip install docling", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting {input_path.name} → {format.upper()}...")

    # Build pipeline options
    format_options = {}
    if input_path.suffix.lower() == ".pdf":
        pdf_opts = PdfPipelineOptions(
            do_chart_extraction=options.get("extract_charts", False),
            do_formula_enrichment=options.get("extract_formulas", False),
            do_picture_description=options.get("caption_images", False),
            do_picture_classification=options.get("classify_images", False),
        )

        if options.get("force_ocr"):
            from docling.datamodel.pipeline_options import RapidOcrOptions
            pdf_opts.ocr_options = RapidOcrOptions(
                force_full_page_ocr=True,
                lang=options.get("ocr_lang", [])
            )

        format_options[InputFormat.PDF] = PdfFormatOption(pipeline_options=pdf_opts)

    # Convert
    converter = DocumentConverter(format_options=format_options)
    result = converter.convert(str(input_path))

    # Export based on format
    out_path = out_dir / (input_path.stem + f".{format}")

    if format == "md":
        content = result.document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)
    elif format == "json":
        json_data = result.document.export_to_dict()
        strip_embedded_base64(json_data)
        content = json.dumps(json_data, indent=2, ensure_ascii=False)
    elif format == "html":
        content = result.document.export_to_html(image_mode=ImageRefMode.EMBEDDED)
    elif format == "text":
        content = result.document.export_to_text()
    else:
        print(f"ERROR: Unknown format: {format}", file=sys.stderr)
        sys.exit(1)

    out_path.write_text(content, encoding="utf-8")
    size_kb = len(content) // 1024
    print(f"  → {out_path.name} ({size_kb} KB)")

    return out_path


def strip_embedded_base64(obj, _placeholder="<base64 image stripped; see figures/>"):
    """Recursively replace base64 `data:image...` URIs in a docling dict with a
    short marker. Images are saved separately to figures/, so the inline base64
    is pure bloat — an image-heavy workbook can otherwise produce a ~1 GB JSON.
    Structure, coordinates, and text are preserved. Returns count stripped.
    """
    count = 0
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str) and v.startswith("data:image"):
                obj[k] = _placeholder
                count += 1
            else:
                count += strip_embedded_base64(v, _placeholder)
    elif isinstance(obj, list):
        for item in obj:
            count += strip_embedded_base64(item, _placeholder)
    return count


def extract_rich(input_path: Path, out_dir: Path, **options):
    """
    Rich extraction. Default (lean): MD + HTML + figures/ + manifest, plus
    per-sheet screenshots & collapsed MD for Excel, pages/ for PDF (--render-pages).
    With options["full_output"]: also JSON structure + image index.
    """
    try:
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import PdfFormatOption
        from docling_core.types.doc.base import ImageRefMode
    except ImportError:
        print("ERROR: docling not installed. Run: pip install docling", file=sys.stderr)
        sys.exit(1)

    print(f"Rich extraction: {input_path.name}")
    print("=" * 60)

    # Build pipeline options with rich features enabled
    format_options = {}
    if input_path.suffix.lower() == ".pdf":
        pdf_opts = PdfPipelineOptions(
            generate_picture_images=True,       # Extract picture images
            do_chart_extraction=options.get("extract_charts", False),
            do_formula_enrichment=options.get("extract_formulas", False),
            do_picture_description=options.get("caption_images", False),
            do_picture_classification=options.get("classify_images", False),
        )

        if options.get("force_ocr"):
            from docling.datamodel.pipeline_options import RapidOcrOptions
            pdf_opts.ocr_options = RapidOcrOptions(
                force_full_page_ocr=True,
                lang=options.get("ocr_lang", [])
            )

        format_options[InputFormat.PDF] = PdfFormatOption(pipeline_options=pdf_opts)

    # Step 1: Convert
    print("[1/7] Converting with docling...")
    converter = DocumentConverter(format_options=format_options)
    result = converter.convert(str(input_path))

    full = options.get("full_output", False)
    suffix = input_path.suffix.lower()
    is_excel = suffix in ['.xlsx', '.xlsm', '.xls']

    # JSON structure — full mode only. Verbose machine data, not read during
    # normal AI ingestion, and can be enormous on big workbooks (900MB+).
    json_name = None
    json_data = None
    if full:
        print("Exporting JSON structure...")
        json_data = result.document.export_to_dict()
        n_stripped = strip_embedded_base64(json_data)
        if n_stripped:
            print(f"    (stripped {n_stripped} inline base64 image(s) — kept in figures/)")
        json_path = out_dir / (input_path.stem + ".json")
        json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
        json_name = json_path.name
        print(f"    → {json_name} ({json_path.stat().st_size // 1024} KB)")

    # Markdown (primary output; also the source for figure extraction)
    print("Exporting Markdown...")
    md_text = result.document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)
    if is_excel and full and json_data is not None:
        md_text = add_excel_sheet_markers(md_text, json_data)

    # Extract embedded images to figures/ and rewrite refs
    print("Extracting figures...")
    figures_dir = out_dir / "figures"
    figures_dir.mkdir(exist_ok=True)
    md_with_refs, figures_meta = extract_images_from_md(md_text, figures_dir)
    md_path = out_dir / (input_path.stem + ".md")
    md_path.write_text(md_with_refs, encoding="utf-8")
    print(f"    → {md_path.name} ({md_path.stat().st_size // 1024} KB)")
    print(f"    → {len(figures_meta)} figures extracted")

    # HTML — kept (human-viewable: formatted, merged cells render, selectable text)
    print("Exporting HTML...")
    html_text = result.document.export_to_html(image_mode=ImageRefMode.EMBEDDED)
    html_path = out_dir / (input_path.stem + ".html")
    html_path.write_text(html_text, encoding="utf-8")
    print(f"    → {html_path.name} ({html_path.stat().st_size // 1024} KB)")

    # Page renders (PDF only, when requested)
    pages_meta = []
    if options.get("render_pages", False) and suffix == ".pdf":
        print("Rendering pages...")
        pages_meta = render_pdf_pages(input_path, out_dir, dpi=options.get("dpi", 300))
    elif options.get("render_pages", False):
        print("    Skipping page renders (PDF only)")

    # Manifest — small index of what was produced
    outputs = {"markdown": md_path.name, "html": html_path.name}
    if json_name:
        outputs["json"] = json_name
    manifest = {
        "version": "1.0",
        "source": {
            "filename": input_path.name,
            "path": str(input_path.absolute()),
            "size_bytes": input_path.stat().st_size,
        },
        "outputs": outputs,
        "assets": {"figures": figures_meta, "pages": pages_meta},
        "stats": {"total_pages": len(pages_meta), "total_figures": len(figures_meta)},
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Image index for Excel — full mode only (redundant with the collapsed MD)
    if full and is_excel and figures_meta:
        print("Building image index...")
        try:
            import importlib.util
            index_script = Path(__file__).parent / 'build_image_index.py'
            if index_script.exists():
                spec = importlib.util.spec_from_file_location("build_image_index", index_script)
                index_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(index_module)
                index_data = index_module.build_index(out_dir)
                index_module.write_json_index(index_data, out_dir / 'image_index.json')
                index_module.write_markdown_index(index_data, out_dir / 'IMAGE_INDEX.md')
                print(f"    → image_index.json + IMAGE_INDEX.md")
        except Exception as e:
            print(f"    Warning: image index failed: {e}")

    # Step 9: Per-sheet screenshots (Excel visual truth) + navigation MD
    if (input_path.suffix.lower() in ['.xlsx', '.xlsm']
            and options.get("screenshot_sheets", True)):
        print("Screenshotting sheets (Excel renderer)...")
        shots = screenshot_excel_sheets(input_path, out_dir, dpi=options.get("screenshot_dpi", 150))
        if shots:
            build_excel_sheets_md(input_path, out_dir, shots)

    print("\n" + "=" * 60)
    print(f"OK extraction complete: {out_dir}/")
    print(f"  - {md_path.name}")
    print(f"  - {html_path.name}")
    if json_name:
        print(f"  - {json_name}")
    print(f"  - manifest.json")
    if pages_meta:
        print(f"  - pages/ ({len(pages_meta)} pages)")
    if figures_meta:
        print(f"  - figures/ ({len(figures_meta)} figures)")


def add_excel_sheet_markers(md_text: str, json_data: dict) -> str:
    """
    Add per-sheet markers to Excel MD output.

    Detects sheet boundaries from JSON structure and inserts '# Sheet: SheetName' headers.
    """
    try:
        # Check if this is Excel content (has table groups or sheet-like structure)
        if 'groups' not in json_data or not json_data.get('groups'):
            return md_text  # Not Excel or no groups, return as-is

        # Extract sheet names from groups (docling groups tables by sheet)
        sheets = []
        for group in json_data.get('groups', []):
            if 'name' in group and group['name']:
                sheets.append(group['name'])

        if not sheets:
            return md_text  # No sheet info found

        # Insert sheet markers
        # Strategy: Split by table blocks and insert sheet headers
        lines = md_text.split('\n')
        result_lines = []
        current_sheet_idx = 0

        for i, line in enumerate(lines):
            # Insert sheet marker before first table or at start
            if current_sheet_idx < len(sheets):
                # Detect table start (markdown table header with |)
                if line.strip().startswith('|') and i > 0:
                    # Check if this is start of a new table block
                    prev_line = lines[i-1].strip()
                    if not prev_line.startswith('|'):
                        # New table block - insert sheet marker
                        if current_sheet_idx == 0 or result_lines:
                            result_lines.append('')
                            result_lines.append(f'# Sheet: {sheets[current_sheet_idx]}')
                            result_lines.append('')
                        current_sheet_idx += 1

            result_lines.append(line)

        # If we added markers, return modified; otherwise return original
        if current_sheet_idx > 0:
            return '\n'.join(result_lines)
        else:
            return md_text

    except Exception as e:
        print(f"Warning: Could not add Excel sheet markers: {e}", file=sys.stderr)
        return md_text  # Return original on error


def extract_images_from_md(md_text: str, figures_dir: Path) -> tuple[str, list]:
    """Extract base64 images from MD, save to figures/, return MD with refs + metadata."""
    figures_meta = []
    fig_counter = 1

    def replace_image(match):
        nonlocal fig_counter
        img_data = match.group(1)

        # Detect format
        if img_data.startswith("iVBOR"):
            ext = "png"
        elif img_data.startswith("/9j/"):
            ext = "jpg"
        else:
            ext = "png"

        # Save image
        filename = f"fig_{fig_counter:03d}.{ext}"
        filepath = figures_dir / filename

        try:
            img_bytes = base64.b64decode(img_data)
            filepath.write_bytes(img_bytes)

            figures_meta.append({
                "filename": filename,
                "figure_num": fig_counter,
                "size_bytes": len(img_bytes),
                "format": ext,
                "relative_path": f"figures/{filename}"
            })

            fig_counter += 1
            return f"![Figure {fig_counter - 1}](figures/{filename})"
        except Exception as e:
            print(f"Warning: Failed to extract image {fig_counter}: {e}", file=sys.stderr)
            return match.group(0)

    pattern = r"!\[.*?\]\(data:image/[^;]+;base64,([A-Za-z0-9+/=]+)\)"
    modified_md = re.sub(pattern, replace_image, md_text)

    return modified_md, figures_meta


def render_pdf_pages(pdf_path: Path, out_dir: Path, dpi: int = 300) -> list:
    """Render PDF pages to PNG using PyMuPDF at specified DPI."""
    try:
        import fitz
    except ImportError:
        print("Warning: PyMuPDF not installed. Skipping page renders. Install: pip install pymupdf", file=sys.stderr)
        return []

    pages_dir = out_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    pages_meta = []

    try:
        doc = fitz.open(str(pdf_path))

        for page_num in range(len(doc)):
            page = doc[page_num]
            zoom = dpi / 72  # Convert DPI to zoom factor
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            filename = f"page_{page_num + 1:03d}.png"
            filepath = pages_dir / filename
            pix.save(str(filepath))

            pages_meta.append({
                "filename": filename,
                "page": page_num + 1,
                "width": pix.width,
                "height": pix.height,
                "dpi": dpi,
                "relative_path": f"pages/{filename}"
            })

        doc.close()
        print(f"    → {len(pages_meta)} pages rendered to pages/")

    except Exception as e:
        print(f"Warning: Page rendering failed: {e}", file=sys.stderr)

    return pages_meta


def extract_excel_formulas(input_path: Path, out_dir: Path) -> Path | None:
    """Extract cell formulas (=SUM(), =VLOOKUP(), ...) from Excel via openpyxl.

    Writes one markdown file grouping formulas per sheet by cell address.
    Returns the output path, or None if no formulas / unsupported.
    """
    if input_path.suffix.lower() not in (".xlsx", ".xlsm"):
        print("    Skipping cell formulas (only .xlsx/.xlsm supported)")
        return None
    try:
        from openpyxl import load_workbook
    except ImportError:
        print("    Skipping cell formulas (openpyxl not installed: pip install openpyxl)", file=sys.stderr)
        return None

    # data_only=False keeps the formula strings instead of cached values
    wb = load_workbook(input_path, data_only=False, read_only=True)
    lines = []
    total = 0
    for ws in wb.worksheets:
        sheet_formulas = []
        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                if isinstance(v, str) and v.startswith("="):
                    sheet_formulas.append((cell.coordinate, v))
        if sheet_formulas:
            lines.append(f"# Sheet: {ws.title}")
            lines.append("")
            for coord, formula in sheet_formulas:
                lines.append(f"- `{coord}`: `{formula}`")
            lines.append("")
            total += len(sheet_formulas)
    wb.close()

    if total == 0:
        print("    No cell formulas found")
        return None

    out_path = out_dir / (input_path.stem + "_formulas.md")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"    → {out_path.name} ({total} formulas)")
    return out_path


def screenshot_excel_sheets(input_path: Path, out_dir: Path, dpi: int = 150) -> list:
    """Render each Excel sheet to PNG via Excel's own renderer (COM).

    Captures the visual truth — grid, merged cells, borders, fills — which the
    docling structural pass and figure extraction do NOT (a table is cells, not
    an image). Returns ordered [(sheet_name, [relative_png_paths])].

    Requires Windows + Excel + pywin32 + pymupdf. Returns [] gracefully otherwise.
    """
    try:
        import win32com.client
    except ImportError:
        print("    Skipping sheet screenshots (pywin32 not installed: pip install pywin32)")
        return []
    try:
        import fitz
    except ImportError:
        print("    Skipping sheet screenshots (pymupdf not installed: pip install pymupdf)")
        return []

    sheets_dir = out_dir / "sheets"
    sheets_dir.mkdir(exist_ok=True)
    shots = []
    excel = None
    wb = None
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(str(input_path.resolve()))
        scale = dpi / 96.0
        mat = fitz.Matrix(scale, scale)
        for i in range(1, wb.Sheets.Count + 1):
            sheet = wb.Sheets(i)
            name = sheet.Name
            safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
            # Fit to 1 page wide so wide sheets aren't cut horizontally
            ps = sheet.PageSetup
            ps.Zoom = False
            ps.FitToPagesWide = 1
            ps.FitToPagesTall = False
            pdf_path = sheets_dir / f"sheet_{i:02d}_{safe}.pdf"
            try:
                # Type=0 xlTypePDF, Quality=0 standard (keyword args, omit From/To)
                sheet.ExportAsFixedFormat(
                    Type=0,
                    Filename=str(pdf_path.resolve()),
                    Quality=0,
                    IncludeDocProperties=False,
                    IgnorePrintAreas=False,
                    OpenAfterPublish=False,
                )
            except Exception as e:
                print(f"    sheet {i} '{name}' -> skipped ({e})")
                shots.append((name, []))
                continue
            pngs = []
            doc = fitz.open(str(pdf_path))
            for pnum, page in enumerate(doc):
                pix = page.get_pixmap(matrix=mat)
                suffix = f"_p{pnum + 1}" if len(doc) > 1 else ""
                png_path = sheets_dir / f"sheet_{i:02d}_{safe}{suffix}.png"
                pix.save(str(png_path))
                pngs.append(f"sheets/{png_path.name}")
            doc.close()
            pdf_path.unlink(missing_ok=True)
            shots.append((name, pngs))
            print(f"    sheet {i} '{name}' -> {len(pngs)} PNG")
    except Exception as e:
        print(f"    Warning: sheet screenshots failed: {e}", file=sys.stderr)
    finally:
        if wb is not None:
            try:
                wb.Close(SaveChanges=False)
            except Exception:
                pass
        if excel is not None:
            try:
                excel.Quit()
            except Exception:
                pass
    return shots


def _sheet_text_from_openpyxl(ws) -> str:
    """Serialize one worksheet's used cells to a valid markdown table.

    openpyxl gives merged-cell values once (top-left) with blanks elsewhere, so
    this avoids docling's merge-duplication. A proper header + separator row make
    it render as a grid (not a clumped wall of literal pipes). Empty rows are
    dropped; leading empty columns are kept so the outline/indent is preserved.
    """
    from openpyxl.utils import get_column_letter

    rows = []
    max_cols = 0
    for row in ws.iter_rows(values_only=True):
        cells = ["" if c is None else str(c).replace("\n", " ").replace("|", "\\|").strip()
                 for c in row]
        if any(cells):                      # skip fully-empty spacer rows
            rows.append(cells)
            max_cols = max(max_cols, len(cells))

    if not rows:
        return ""

    # Excel spec sheets use a fine grid (many narrow columns), so most columns
    # are empty. Keep only columns that carry content anywhere — collapses a
    # 40-column sparse grid to the handful that matter, preserving indentation.
    rows = [r + [""] * (max_cols - len(r)) for r in rows]
    used = [j for j in range(max_cols) if any(r[j] for r in rows)]
    if not used:
        return ""

    header = "| " + " | ".join(get_column_letter(j + 1) for j in used) + " |"
    sep = "| " + " | ".join("---" for _ in used) + " |"
    body = ["| " + " | ".join(r[j] for j in used) + " |" for r in rows]
    return "\n".join([header, sep] + body)


def build_excel_sheets_md(input_path: Path, out_dir: Path, shots: list) -> Path | None:
    """Collapse screenshots + text into ONE per-sheet MD, overwriting <stem>.md.

    Each sheet section = heading + screenshot pointer(s) + that sheet's text
    (read authoritatively from openpyxl, not docling's unreliable sheet markers).
    shots = [(sheet_name, [png_rel_paths])] in sheet order.
    """
    if not shots:
        return None

    text_by_sheet = {}
    try:
        from openpyxl import load_workbook
        wb = load_workbook(input_path, data_only=True, read_only=True)
        for ws in wb.worksheets:
            text_by_sheet[ws.title] = _sheet_text_from_openpyxl(ws)
        wb.close()
    except Exception as e:
        print(f"    Warning: per-sheet text unavailable ({e})", file=sys.stderr)

    lines = [f"# {input_path.name}", ""]
    for name, pngs in shots:
        lines.append(f"# Sheet: {name}")
        lines.append("")
        if pngs:
            for p in pngs:
                lines.append(f"**Screenshot:** ![{name}]({p})")
        else:
            lines.append("**Screenshot:** _(empty / unprintable sheet)_")
        lines.append("")
        body = text_by_sheet.get(name) or text_by_sheet.get(name.strip())
        if body:
            lines.append(body)
            lines.append("")
        lines.append("---")
        lines.append("")

    out_path = out_dir / (input_path.stem + ".md")  # overwrite the flat main MD
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"    → {out_path.name} (collapsed: {len(shots)} sheets, screenshot + text)")
    return out_path


def main():
    # Force UTF-8 stdout/stderr so status prints (→, —, Japanese names) never
    # crash under a non-UTF-8 locale (e.g. cp932) when output is piped/redirected.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Universal document content extractor")
    parser.add_argument("input", help="Input file")
    parser.add_argument("--format", choices=["md", "json", "html", "text", "rich"], default=None,
                        help="Output format (default: rich for all types; use md/json/html/text for one plain file)")
    parser.add_argument("--out-dir", default="output", help="Output directory")

    # Extraction options
    parser.add_argument("--force-ocr", action="store_true", help="Force full-page OCR")
    parser.add_argument("--ocr-lang", help="OCR languages (comma-separated, e.g. jpn,eng)")
    parser.add_argument("--extract-charts", action="store_true", help="Extract charts to CSV")
    parser.add_argument("--extract-formulas", action="store_true", help="Extract math formulas")
    parser.add_argument("--caption-images", action="store_true", help="Auto-generate image captions")
    parser.add_argument("--render-pages", action="store_true", help="Render pages to PNG (recommended)")
    parser.add_argument("--dpi", type=int, default=300, help="Page render DPI (default: 300, higher = sharper)")
    parser.add_argument("--excel-formulas", action="store_true", help="Extract cell formulas from Excel")
    parser.add_argument("--classify-images", action="store_true", help="Classify image types (chart/diagram/photo)")
    parser.add_argument("--no-screenshots", action="store_true", help="Skip per-sheet Excel screenshots (Excel COM)")
    parser.add_argument("--full", action="store_true", help="Also emit JSON structure + image index (default: lean — MD + HTML + figures + screenshots)")

    # Mode flags
    parser.add_argument("--rich", action="store_true", help="Rich extraction (same as --format rich)")
    parser.add_argument("--non-interactive", action="store_true", help="Skip interactive prompts")

    args = parser.parse_args()

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Prepare output directory
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Parse OCR languages
    ocr_lang = args.ocr_lang.split(",") if args.ocr_lang else []

    # Options dict
    options = {
        "force_ocr": args.force_ocr,
        "ocr_lang": ocr_lang,
        "extract_charts": args.extract_charts,
        "extract_formulas": args.extract_formulas,
        "caption_images": args.caption_images,
        "render_pages": args.render_pages,
        "dpi": args.dpi,
        "excel_formulas": args.excel_formulas,
        "classify_images": args.classify_images,
        "screenshot_sheets": not args.no_screenshots,
        "full_output": args.full,
        "non_interactive": args.non_interactive,
    }

    # Default to rich (lean) for ALL types — best for AI ingestion: extracts
    # figures to files (vs base64 blobs in plain MD), plus screenshots for Excel
    # and page renders for PDF. Pass --format md/json/html/text for a single
    # plain output file instead.
    if args.format is None:
        args.format = "rich"

    # Explicit --rich also forces rich
    if args.rich:
        args.format = "rich"

    # --render-pages needs rich
    if args.render_pages and args.format != "rich":
        print("Note: --render-pages requires rich mode. Enabling rich automatically.")
        args.format = "rich"

    # Execute
    if args.format == "rich":
        extract_rich(input_path, out_dir, **options)
    else:
        extract_simple(input_path, out_dir, args.format, **options)

    # Excel cell-formula extraction (opt-in via --excel-formulas)
    if args.excel_formulas:
        print("Extracting Excel cell formulas...")
        extract_excel_formulas(input_path, out_dir)


if __name__ == "__main__":
    main()
