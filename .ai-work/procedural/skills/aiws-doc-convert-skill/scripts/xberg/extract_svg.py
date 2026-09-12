#!/usr/bin/env python
"""
SVG extractor. An SVG is XML with embedded <text> plus vector graphics, so grab
both layers:

  1. text    parse <text> elements       (source.md)
  2. visual  render to PNG via PyMuPDF    (pages/svg.png)

Usage: python extract_svg.py <file.svg> [output_dir] [--dpi N]
Requires: xberg env; PyMuPDF (fitz) for the raster render.
"""
import sys, json, time, re
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import doc_header


def _svg_texts(path: Path):
    try:
        root = ET.parse(str(path)).getroot()
    except Exception:
        return []
    out = []
    for el in root.iter():
        if el.tag.endswith("}text") or el.tag == "text":
            t = "".join(el.itertext()).strip()
            if t:
                out.append(t)
    return out


def extract_svg(src, out_dir=None, dpi: int = 150) -> dict:
    src_path = Path(src).resolve()
    if not src_path.exists():
        raise FileNotFoundError(src)
    out = Path(out_dir).resolve() if out_dir else Path(f"{src_path.stem}_svg").resolve()
    (out / "pages").mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    texts = _svg_texts(src_path)

    rendered = None
    render_note = ""
    try:
        import fitz  # PyMuPDF renders SVG
        doc = fitz.open(str(src_path))
        pix = doc[0].get_pixmap(dpi=dpi)
        rendered = out / "pages" / "svg.png"
        pix.save(str(rendered))
    except Exception as e:
        render_note = f"render failed ({e}); text still extracted"

    md = [doc_header(src_path)]
    if texts:
        md.append("## Text in SVG\n")
        md += [f"- {t}" for t in texts]
        md.append("")
    if rendered:
        md.append(f"![render](pages/{rendered.name})")
    (out / "source.md").write_text("\n".join(md), encoding="utf-8")

    manifest = {
        "engine": "SVG XML text + PyMuPDF render",
        "source": {"filename": src_path.name, "path": str(src_path.resolve()),
                   "size_bytes": src_path.stat().st_size},
        "elapsed_s": round(time.time() - t0, 2),
        "counts": {"text_elements": len(texts), "pages": 1 if rendered else 0},
        "render_note": render_note,
        "outputs": {"markdown": "source.md",
                    "pages": [f"pages/{rendered.name}"] if rendered else []},
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
    print(json.dumps(extract_svg(a[0], a[1] if len(a) > 1 else None, dpi=dpi), ensure_ascii=False, indent=2))
