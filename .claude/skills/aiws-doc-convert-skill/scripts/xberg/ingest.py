#!/usr/bin/env python
"""
Unified ingestion dispatcher — one command for every file type.

Detects the file extension and routes to the right handler, each of which
produces the same shape: source.md (+ pages/ + figures/) + manifest.json with
caption_status. The skill then runs the VLM enhancement pass on any visual output.

Usage:
    python ingest.py <file> [output_dir] [--dpi N]

Routes:
    xlsx xlsm xls        -> extract_hybrid  (Excel COM: text + sheet PNG + photos)
    pptx ppt             -> extract_pptx    (PowerPoint COM: text + slide PNG + media)
    docx doc             -> extract_word    (Word COM: text + page PNG + media)
    pdf                  -> extract_pdf     (xberg native text + page render)
    png jpg jpeg tif tiff bmp gif webp -> extract_image (copy + pinpoint; VLM summary)
    drawio               -> extract_drawio  (XML -> Mermaid + CLI render)
    svg                  -> extract_svg     (XML text + PyMuPDF render)
    csv txt md rtf html htm json xml yaml yml eml msg -> extract (generic xberg text)

Handlers are imported lazily (only the one a file needs), so a missing optional
dependency (e.g. pywin32/Office on a non-Windows box) only affects that one route
— the dispatcher and the other routes keep working.
"""
import sys, json, importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ext -> (route label, module name, function name)
ROUTES = {
    "xlsx": ("excel", "extract_hybrid", "extract_hybrid"),
    "xlsm": ("excel", "extract_hybrid", "extract_hybrid"),
    "xls":  ("excel", "extract_hybrid", "extract_hybrid"),
    "pptx": ("ppt",   "extract_pptx",   "extract_pptx"),
    "ppt":  ("ppt",   "extract_pptx",   "extract_pptx"),
    "docx": ("word",  "extract_word",   "extract_word"),
    "doc":  ("word",  "extract_word",   "extract_word"),
    "pdf":  ("pdf",   "extract_pdf",    "extract_pdf"),
    "drawio": ("drawio", "extract_drawio", "extract_drawio"),
    "svg":  ("svg",   "extract_svg",    "extract_svg"),
}
IMAGE_EXTS = {"png", "jpg", "jpeg", "tif", "tiff", "bmp", "gif", "webp"}
TEXT_EXTS = {"csv", "txt", "md", "rtf", "html", "htm", "json", "xml", "yaml", "yml", "eml", "msg"}


def dispatch(src, out_dir=None, dpi=150) -> dict:
    ext = Path(src).suffix.lower().lstrip(".")
    if ext in ROUTES:
        kind, mod, fnname = ROUTES[ext]
    elif ext in IMAGE_EXTS:
        kind, mod, fnname = "image", "extract_image", "extract_image"
    elif ext in TEXT_EXTS:
        kind, mod, fnname = "text", "extract", "extract"
    else:
        kind, mod, fnname = "text(auto)", "extract", "extract"  # xberg handles 96+ formats

    try:
        fn = getattr(importlib.import_module(mod), fnname)
    except Exception as e:
        raise RuntimeError(
            f"The '{kind}' handler ({mod}) for .{ext} could not load — a dependency is "
            f"probably missing: {e}\n"
            f"Install core: pip install xberg python-pptx pymupdf\n"
            f"For Office routes (xlsx/pptx/docx) on Windows also: pip install pywin32 "
            f"(and MS Office must be installed)."
        ) from e

    try:
        m = fn(src, out_dir, dpi=dpi)      # visual handlers accept dpi
    except TypeError:
        m = fn(src, out_dir)               # text/image/drawio handlers don't
    if isinstance(m, dict):
        m["route"] = kind
    return m


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    dpi = 150
    if "--dpi" in a:
        i = a.index("--dpi"); dpi = int(a[i + 1]); del a[i:i + 2]
    m = dispatch(a[0], a[1] if len(a) > 1 else None, dpi=dpi)
    print(json.dumps(m, ensure_ascii=False, indent=2))
