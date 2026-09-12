#!/usr/bin/env python
"""
PDF extractor. xberg reads the native text layer directly (no COM). Pages are
rendered for visual/diagram context and pinpointed in source.md. If the text
layer is empty/tiny (scanned PDF), that is flagged so the enhancement pass OCRs
the rendered pages instead.

Phase 1 (mechanical): text (source.md) + page renders (pages/page_NN.png) +
a "## Renders" pinpointer section with `<!-- summary: pending -->` per page.
Phase 2 (opt-in enhancement): VLM fills summaries / OCRs scans, in source.md.

Usage: python extract_pdf.py <input.pdf> [output_dir] [--dpi N] [--no-pages]
Requires: xberg.
"""
import sys, json, time
from pathlib import Path
import xberg
from _common import units_section, doc_header


def extract_pdf(src, out_dir=None, dpi: int = 150, render_pages: bool = True) -> dict:
    src_path = Path(src).resolve()
    if not src_path.exists():
        raise FileNotFoundError(src)
    out = Path(out_dir).resolve() if out_dir else Path(f"{src_path.stem}_pdf").resolve()
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    cfg = xberg.ExtractionConfig(output_format=xberg.OutputFormat.MARKDOWN)
    r = xberg.extract_file_sync(str(src_path), config=cfg)
    text = r.content or ""  # whole-doc text (for the scan heuristic / fallback)

    # per-page faithful text via PyMuPDF, per-page image via xberg render
    per_page_text = []
    try:
        import fitz
        doc = fitz.open(str(src_path))
        per_page_text = [doc[i].get_text().strip() for i in range(doc.page_count)]
    except Exception:
        per_page_text = []

    units = []
    if render_pages:
        pdir = out / "pages"; pdir.mkdir(exist_ok=True)
        i = 0
        while i < 2000:
            try:
                b = bytes(xberg.render_pdf_page(str(src_path), i, dpi=dpi))
            except Exception:
                break
            name = f"page_{i + 1:02d}.png"
            (pdir / name).write_bytes(b)
            ptext = per_page_text[i] if i < len(per_page_text) else ""
            units.append({"label": f"Page {i + 1}", "images": [f"pages/{name}"], "text": ptext})
            i += 1

    header = doc_header(src_path, "_One section per page: image + extracted text + summary._")
    (out / "source.md").write_text(header + units_section(units, title="Pages"), encoding="utf-8")

    likely_scanned = bool(units) and (len(text) / max(len(units), 1) < 50)
    manifest = {
        "engine": "xberg (kreuzberg)",
        "source": {"filename": src_path.name, "path": str(src_path.resolve()),
                   "size_bytes": src_path.stat().st_size},
        "elapsed_s": round(time.time() - t0, 2),
        "dpi": dpi,
        "counts": {"pages": len(units), "content_chars": len(text)},
        "quality_score": r.quality_score,
        "likely_scanned_needs_ocr": likely_scanned,
        "scan_note": "text layer sparse - enhancement pass should OCR the rendered pages" if likely_scanned else "",
        "outputs": {"markdown": "source.md", "pages": [u["images"][0] for u in units]},
        "caption_status": "pending",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    dpi = 150; rp = "--no-pages" not in a
    a = [x for x in a if x != "--no-pages"]
    if "--dpi" in a:
        i = a.index("--dpi"); dpi = int(a[i + 1]); del a[i:i + 2]
    print(json.dumps(extract_pdf(a[0], a[1] if len(a) > 1 else None, dpi=dpi, render_pages=rp), ensure_ascii=False, indent=2))
