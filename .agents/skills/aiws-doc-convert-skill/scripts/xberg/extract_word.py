#!/usr/bin/env python
"""
Word (docx/doc) extractor. Word docs mix flowing text with floating images,
diagrams and screenshots, so keep text AND visuals:

Phase 1 (mechanical): text (source.md) + Word COM -> PDF -> page renders
(pages/page_NN.png) + embedded media (figures/*) + a "## Renders" pinpointer
section with `<!-- summary: pending -->` per page.
Phase 2 (opt-in enhancement): VLM fills summaries / adds Mermaid, in source.md.

Requires: MS Word + pywin32 (COM), xberg. (.doc legacy opens via COM too.)
"""
import sys, json, time, zipfile, tempfile, os
from pathlib import Path
import xberg
from _common import units_section, doc_header

WD_FORMAT_PDF = 17


def extract_word(src, out_dir=None, dpi: int = 150) -> dict:
    src_path = Path(src).resolve()
    if not src_path.exists():
        raise FileNotFoundError(src)
    out = Path(out_dir).resolve() if out_dir else Path(f"{src_path.stem}_word").resolve()
    (out / "pages").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    cfg = xberg.ExtractionConfig(output_format=xberg.OutputFormat.MARKDOWN)
    r = xberg.extract_file_sync(str(src_path), config=cfg)
    text = r.content or ""

    # Word COM -> PDF -> render
    import win32com.client as win32  # lazy: only needed for the Word route (Windows)
    pdf_tmp = Path(tempfile.gettempdir()) / f"_word_{os.getpid()}.pdf"
    word = win32.DispatchEx("Word.Application"); word.Visible = False
    try:
        doc = word.Documents.Open(str(src_path), ReadOnly=True)
        try:
            doc.SaveAs(str(pdf_tmp), FileFormat=WD_FORMAT_PDF)
        finally:
            doc.Close(SaveChanges=False)
    finally:
        word.Quit()

    # per-page faithful text from the rendered PDF (Word reflows, so pages are
    # only meaningful after layout — read them from the PDF)
    per_page_text = []
    try:
        import fitz
        d = fitz.open(str(pdf_tmp))
        per_page_text = [d[i].get_text().strip() for i in range(d.page_count)]
        d.close()
    except Exception:
        per_page_text = []

    units = []
    i = 0
    while i < 2000:
        try:
            b = bytes(xberg.render_pdf_page(str(pdf_tmp), i, dpi=dpi))
        except Exception:
            break
        name = f"page_{i + 1:02d}.png"
        (out / "pages" / name).write_bytes(b)
        ptext = per_page_text[i] if i < len(per_page_text) else ""
        units.append({"label": f"Page {i + 1}", "images": [f"pages/{name}"], "text": ptext})
        i += 1
    pdf_tmp.unlink(missing_ok=True)

    figures = []
    if src_path.suffix.lower() == ".docx":
        with zipfile.ZipFile(str(src_path)) as z:
            for nm in z.namelist():
                if nm.startswith("word/media/"):
                    fn = Path(nm).name
                    (out / "figures" / fn).write_bytes(z.read(nm))
                    figures.append(f"figures/{fn}")

    header = doc_header(src_path, "_One section per page: image + extracted text + summary._")
    (out / "source.md").write_text(header + units_section(units, title="Pages"), encoding="utf-8")

    manifest = {
        "engine": "xberg (kreuzberg) + Word COM render",
        "source": {"filename": src_path.name, "path": str(src_path.resolve()),
                   "size_bytes": src_path.stat().st_size},
        "elapsed_s": round(time.time() - t0, 2),
        "dpi": dpi,
        "counts": {"pages": len(units), "figures": len(figures), "content_chars": len(text)},
        "quality_score": r.quality_score,
        "outputs": {"markdown": "source.md",
                    "pages": [u["images"][0] for u in units], "figures": figures},
        "caption_status": "pending",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    dpi = 150
    if "--dpi" in a:
        i = a.index("--dpi"); dpi = int(a[i + 1]); del a[i:i + 2]
    print(json.dumps(extract_word(a[0], a[1] if len(a) > 1 else None, dpi=dpi), ensure_ascii=False, indent=2))
