#!/usr/bin/env python
"""
Hybrid Excel (xlsx/xlsm/xls) extractor for FORMATTING-HEAVY spreadsheets.

Plain text throws away what a spreadsheet carries visually (fills, borders, merged
cells, inserted line/arrow shapes, embedded logos). This keeps three layers:

Phase 1 (this script, mechanical, no VLM):
  1. text    xberg MARKDOWN (tables preserved)          (source.md, top)
  2. visual  Excel COM -> per-sheet PDF -> render PNG    (pages/sheet_NN.png)
  3. photos  embedded rasters pulled from the PDF         (figures/sheet_NN/*)
  4. index   a "## Renders" section in source.md pinpointing every sheet to its
             image(s) with a `<!-- summary: pending -->` marker.

Phase 2 (skill enhancement pass, opt-in): a VLM fills each summary and adds Mermaid
for diagram sheets, in this same source.md. No OCR dump, no side file.

Usage: python extract_hybrid.py <input.xlsx> [output_dir] [--dpi N] [--keep-pdf]
Requires: MS Excel + pywin32 (COM), xberg (kreuzberg).
"""
import sys, json, time, shutil, re
from pathlib import Path
import xberg
from _common import render_pdf_pages, units_section, doc_header

XL_TYPE_PDF = 0
XL_SHEET_VISIBLE = -1

# Sheets bigger than this are treated as data dumps: sampled text, no image render
# (rendering thousands of rows produces hundreds of useless pages and times out).
DATA_ROWS = 300
DATA_COLS = 60
TEXT_SAMPLE_LINES = 80   # rows of markdown kept for a data sheet
MAX_RENDER_PAGES = 12    # page cap for a rendered (visual) sheet


def _split_sheets(md: str) -> dict:
    """xberg emits xlsx as '## <sheetname>' + that sheet's markdown tables.
    Split it into {sheetname: tables} so each sheet's faithful text lives with it."""
    chunks = re.split(r'(?m)^## (.+)$', md)
    out = {}
    for k in range(1, len(chunks), 2):
        out[chunks[k].strip()] = chunks[k + 1].strip()
    return out


def _extract_photos(pdf_path, out_dir: Path):
    """Pull genuine embedded rasters (logos/screenshots) out of the sheet PDF."""
    cfg = xberg.ExtractionConfig(
        output_format=xberg.OutputFormat.MARKDOWN,
        images=xberg.ImageExtractionConfig(extract_images=True, inject_placeholders=True),
        pdf_options=xberg.PdfConfig(extract_images=True),
    )
    try:
        r = xberg.extract_file_sync(str(pdf_path), config=cfg)
    except Exception:
        return []
    saved = []
    for j, im in enumerate(r.images or [], 1):
        data = im.get("data") if hasattr(im, "get") else getattr(im, "data", None)
        if not data:
            continue
        fmt = (im.get("format") if hasattr(im, "get") else "png") or "png"
        out_dir.mkdir(parents=True, exist_ok=True)
        fn = f"img_{j:03d}.{fmt}"
        (out_dir / fn).write_bytes(bytes(data))
        saved.append(fn)
    return saved


def extract_hybrid(src, out_dir=None, dpi: int = 150, keep_pdf: bool = False) -> dict:
    src_path = Path(src).resolve()
    if not src_path.exists():
        raise FileNotFoundError(src)
    out = Path(out_dir).resolve() if out_dir else Path(f"{src_path.stem}_hybrid").resolve()
    (out / "pages").mkdir(parents=True, exist_ok=True)
    pdf_tmp = out / "_pdf"; pdf_tmp.mkdir(exist_ok=True)

    t0 = time.time()

    # 1. text layer, split into per-sheet tables
    cfg = xberg.ExtractionConfig(output_format=xberg.OutputFormat.MARKDOWN)
    r = xberg.extract_file_sync(str(src_path), config=cfg)
    text = r.content or ""
    sheet_text = _split_sheets(text)
    ordered_chunks = list(sheet_text.values())
    meta = {k: r.metadata.get(k) for k in r.metadata.keys()} if r.metadata else {}

    # 2 & 3. per-sheet render + embedded photos, via Excel COM
    import win32com.client as win32  # lazy: only needed for the Excel route (Windows)
    units, all_figs, sampled = [], [], []
    excel = win32.DispatchEx("Excel.Application")
    excel.Visible = False; excel.DisplayAlerts = False
    try:
        wb = excel.Workbooks.Open(str(src_path), ReadOnly=True)
        try:
            idx = 0
            for ws in wb.Worksheets:
                if ws.Visible != XL_SHEET_VISIBLE:
                    continue
                idx += 1
                name = str(ws.Name)
                stem = f"sheet_{idx:02d}"
                pdf_path = pdf_tmp / f"{stem}.pdf"
                try:
                    ws.PageSetup.Zoom = False
                    ws.PageSetup.FitToPagesWide = 1
                    ws.PageSetup.FitToPagesTall = False
                except Exception:
                    pass
                # faithful per-sheet tables: match by name, fall back to order
                stext = sheet_text.get(name) or sheet_text.get(name.strip())
                if stext is None:
                    stext = ordered_chunks[idx - 1] if idx - 1 < len(ordered_chunks) else ""

                # Decide render vs skip by used-range size. A giant data-dump sheet
                # (thousands of rows) renders to hundreds of pointless pages and blows
                # up time/size — for those, keep sampled text only, no image.
                try:
                    ur = ws.UsedRange
                    nrows, ncols = int(ur.Rows.Count), int(ur.Columns.Count)
                except Exception:
                    nrows = ncols = 0
                is_data = nrows > DATA_ROWS or ncols > DATA_COLS

                imgs, figs, note = [], [], ""
                if is_data:
                    lines = stext.splitlines()
                    if len(lines) > TEXT_SAMPLE_LINES:
                        kept = TEXT_SAMPLE_LINES
                        stext = ("\n".join(lines[:TEXT_SAMPLE_LINES]) +
                                 f"\n\n> ⚠️ **DATA SAMPLED — NOT COMPLETE HERE.** Showing ~{kept} of "
                                 f"{nrows} rows ({ncols} cols). This sheet is a large data table; the "
                                 f"image render was skipped and only a sample of rows is included above. "
                                 f"**For the full/exact data, open sheet `{name}` in the source file** "
                                 f"(path at the top of this document).")
                        sampled.append({"sheet": name, "rows": nrows, "cols": ncols, "kept_rows": kept})
                    note = f"  [large data sheet {nrows}×{ncols} — render skipped, text sampled]"
                else:
                    ws.ExportAsFixedFormat(XL_TYPE_PDF, str(pdf_path))
                    imgs = render_pdf_pages(pdf_path, out / "pages", stem, dpi, max_pages=MAX_RENDER_PAGES)
                    figs = _extract_photos(pdf_path, out / "figures" / stem)
                    all_figs += [f"figures/{stem}/{f}" for f in figs]

                units.append({"label": f"Sheet {idx} — {name}{note}",
                              "images": [f"pages/{im}" for im in imgs],
                              "text": stext})
        finally:
            wb.Close(SaveChanges=False)
    finally:
        excel.Quit()

    if not keep_pdf:
        shutil.rmtree(pdf_tmp, ignore_errors=True)

    # 4. source.md = one section per sheet (tables kept as each sheet's Extracted text)
    header = doc_header(src_path, "_One section per sheet: image + extracted tables + summary._")
    if sampled:
        header += ("\n> ⚠️ **{n} large data sheet(s) were sampled** (image render skipped, only a "
                   "sample of rows included). Full data is in the source file above: {lst}.\n").format(
                   n=len(sampled), lst=", ".join(f"`{s['sheet']}` ({s['rows']}×{s['cols']})" for s in sampled))
    (out / "source.md").write_text(header + units_section(units, title="Sheets"), encoding="utf-8")

    manifest = {
        "engine": "xberg (kreuzberg) + Excel COM render",
        "source": {"filename": src_path.name, "path": str(src_path.resolve()),
                   "size_bytes": src_path.stat().st_size},
        "data_sheets_sampled": sampled,
        "warnings": ([f"{len(sampled)} large data sheet(s) sampled (full data in source): "
                      + ", ".join(s["sheet"] for s in sampled)] if sampled else []),
        "elapsed_s": round(time.time() - t0, 2),
        "dpi": dpi,
        "sheet_count": meta.get("sheet_count"),
        "sheet_names": meta.get("sheet_names"),
        "quality_score": r.quality_score,
        "counts": {"content_chars": len(text), "sheets": len(units),
                   "total_pages": sum(len(u["images"]) for u in units),
                   "total_figures": len(all_figs)},
        "outputs": {"markdown": "source.md", "figures": all_figs},
        "caption_status": "pending",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    dpi = 150; keep_pdf = "--keep-pdf" in a
    a = [x for x in a if x != "--keep-pdf"]
    if "--dpi" in a:
        i = a.index("--dpi"); dpi = int(a[i + 1]); del a[i:i + 2]
    print(json.dumps(extract_hybrid(a[0], a[1] if len(a) > 1 else None, dpi=dpi, keep_pdf=keep_pdf), ensure_ascii=False, indent=2))
