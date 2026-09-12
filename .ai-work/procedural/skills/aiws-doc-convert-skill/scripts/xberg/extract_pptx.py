#!/usr/bin/env python
"""
PPTX/PPT extractor — visual-heavy slide decks.

Phase 1 (mechanical, no VLM) — one section per slide, keeping content together:
  **Image:**     PowerPoint COM -> pages/slide_NN.png
  **Extracted:** python-pptx -> the text actually on that slide (faithful)
  <!-- summary: pending -->   (filled in Phase 2)

Per-slide text (not one big blob) means a diagram that repeats on 3 slides shows up
inside those 3 slide sections — no scattered duplicate dump. Embedded media -> figures/.

Phase 2 (skill enhancement pass, opt-in): a VLM fills each summary and adds Mermaid
for diagram slides, in this same source.md. No OCR dump, no side file.

Usage: python extract_pptx.py <input.pptx> [output_dir] [--dpi N]
Requires: MS PowerPoint + pywin32 (COM), python-pptx, xberg.
"""
import sys, json, time, zipfile
from pathlib import Path
import xberg
from _common import units_section, doc_header


def _md_table(tbl) -> str:
    """Render a PowerPoint table shape as a proper GitHub-flavored Markdown table."""
    def cell(c):
        return c.text.strip().replace("\r", " ").replace("\n", "<br>").replace("|", "\\|")
    rows = [[cell(c) for c in row.cells] for row in tbl.rows]
    if not rows:
        return ""
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]      # pad ragged rows
    out = ["| " + " | ".join(rows[0]) + " |",
           "| " + " | ".join(["---"] * ncol) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def _slide_text(slide) -> str:
    """Faithful text of one slide: shape text + real Markdown tables, reading order."""
    parts = []
    for shape in slide.shapes:
        if shape.has_table:
            t = _md_table(shape.table)
            if t:
                parts.append(t)
        elif shape.has_text_frame:
            buf = []
            for para in shape.text_frame.paragraphs:
                s = "".join(r.text for r in para.runs).strip()
                if s:
                    buf.append(s)
            if buf:
                parts.append("\n".join(buf))
    return "\n\n".join(parts)


def extract_pptx(src, out_dir=None, dpi: int = 150) -> dict:
    src_path = Path(src).resolve()
    if not src_path.exists():
        raise FileNotFoundError(src)
    out = Path(out_dir).resolve() if out_dir else Path(f"{src_path.stem}_pptx").resolve()
    (out / "pages").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    t0 = time.time()

    # lazy import: only the pptx route needs PowerPoint COM
    import win32com.client as win32

    # Per-slide faithful text via python-pptx — OpenXML .pptx only. Legacy binary
    # .ppt has none of those parts, so fall back to render-only (the enhancement
    # pass reads the rendered slide images for text).
    slide_info, legacy_note = None, ""
    try:
        from pptx import Presentation
        prs = Presentation(str(src_path))
        slide_info = []
        for slide in prs.slides:
            title = ""
            try:
                if slide.shapes.title and slide.shapes.title.text:
                    title = slide.shapes.title.text.strip().replace("\r", " ").replace("\n", " ")
            except Exception:
                pass
            slide_info.append((title, _slide_text(slide)))
    except Exception as e:
        legacy_note = (f"per-slide text not extracted ({type(e).__name__}) — likely a legacy .ppt. "
                       "Slides are still rendered as images; text is added by the enhancement pass.")

    # render each slide to pages/slide_NN.png via PowerPoint COM (works for .ppt AND .pptx)
    ppt = win32.DispatchEx("PowerPoint.Application")
    n_slides = 0
    try:
        pres = ppt.Presentations.Open(str(src_path), ReadOnly=True, Untitled=False, WithWindow=False)
        try:
            sw = float(pres.PageSetup.SlideWidth); sh = float(pres.PageSetup.SlideHeight)
            W = int(sw / 72 * dpi); H = int(sh / 72 * dpi)
            n_slides = pres.Slides.Count
            for i in range(1, n_slides + 1):
                pres.Slides(i).Export(str(out / "pages" / f"slide_{i:02d}.png"), "PNG", W, H)
        finally:
            pres.Close()
    finally:
        ppt.Quit()

    units = []
    for i in range(1, n_slides + 1):
        title, text = slide_info[i - 1] if (slide_info and i - 1 < len(slide_info)) else ("", "")
        label = f"Slide {i}" + (f" — {title}" if title else "")
        units.append({"label": label, "images": [f"pages/slide_{i:02d}.png"], "text": text})

    # embedded media — only .pptx is a zip; legacy .ppt is an OLE compound file, so guard.
    figures = []
    try:
        with zipfile.ZipFile(str(src_path)) as z:
            for nm in z.namelist():
                if nm.startswith("ppt/media/"):
                    fn = Path(nm).name
                    (out / "figures" / fn).write_bytes(z.read(nm))
                    figures.append(f"figures/{fn}")
    except zipfile.BadZipFile:
        pass

    header = doc_header(src_path, "_One section per slide: image + extracted text + summary. "
                                  "Flowcharts also get Mermaid in the enhancement pass._")
    if legacy_note:
        header += f"\n> ⚠️ **Legacy .ppt:** {legacy_note}\n"
    (out / "source.md").write_text(header + units_section(units, title="Slides"), encoding="utf-8")

    manifest = {
        "engine": "xberg + python-pptx (per-slide text) + PowerPoint COM render",
        "source": {"filename": src_path.name, "path": str(src_path.resolve()),
                   "size_bytes": src_path.stat().st_size},
        "elapsed_s": round(time.time() - t0, 2),
        "dpi": dpi,
        "counts": {"slides": len(units), "figures": len(figures),
                   "content_chars": sum(len(u["text"]) for u in units)},
        "outputs": {"markdown": "source.md",
                    "slides": [u["images"][0] for u in units], "figures": figures},
        "warnings": ([legacy_note] if legacy_note else []),
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
    print(json.dumps(extract_pptx(a[0], a[1] if len(a) > 1 else None, dpi=dpi), ensure_ascii=False, indent=2))
