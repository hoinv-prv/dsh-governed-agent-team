#!/usr/bin/env python
"""
draw.io (.drawio) extractor. A .drawio file *is* a graph (mxGraph XML), so the
best AI representation is a graph too:

  1. structure  parse mxGraph -> Mermaid flowchart   (source.md)
  2. visual     draw.io CLI -> PNG (if CLI present)   (pages/*.png)

The Mermaid is derived directly from the file's nodes/edges (not guessed from a
picture), so it is faithful. The PNG render is the ground-truth fallback.

Usage: python extract_drawio.py <file.drawio> [output_dir]
Requires: nothing for Mermaid; draw.io desktop CLI for the PNG render.
"""
import sys, json, time, re, base64, zlib, subprocess, shutil
import urllib.parse as up
import xml.etree.ElementTree as ET
from pathlib import Path
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import doc_header

DRAWIO_EXES = [
    r"C:\Program Files\draw.io\draw.io.exe",
    r"C:\Program Files (x86)\draw.io\draw.io.exe",
]


def _find_drawio():
    for p in DRAWIO_EXES:
        if Path(p).exists():
            return p
    return shutil.which("drawio")


def _decode_diagram(diagram_el) -> str:
    """A <diagram> holds either raw mxGraphModel XML or compressed content."""
    inner = diagram_el.find("mxGraphModel")
    if inner is not None:
        return ET.tostring(inner, encoding="unicode")
    raw = (diagram_el.text or "").strip()
    if not raw:
        return ""
    try:  # base64 -> raw deflate -> url-decode
        data = base64.b64decode(raw)
        xml = zlib.decompress(data, -15).decode("utf-8")
        return up.unquote(xml)
    except Exception:
        return raw


def _sanitize(cid: str) -> str:
    return "n" + re.sub(r"\W", "_", cid or "")


def _model_to_mermaid(model_xml: str) -> str:
    try:
        root = ET.fromstring(model_xml)
    except Exception:
        return ""
    cells = root.iter("mxCell")
    nodes, edges = {}, []
    for c in cells:
        cid = c.get("id")
        val = re.sub(r"<[^>]+>", " ", c.get("value") or "").strip()
        if c.get("vertex") == "1":
            nodes[cid] = val or cid
        elif c.get("edge") == "1":
            s, t = c.get("source"), c.get("target")
            if s and t:
                edges.append((s, t, val))
    if not nodes:
        return ""
    lines = ["```mermaid", "flowchart TD"]
    for cid, label in nodes.items():
        lines.append(f'  {_sanitize(cid)}["{label}"]')
    for s, t, lbl in edges:
        if s in nodes and t in nodes:
            arrow = f'-- "{lbl}" -->' if lbl else "-->"
            lines.append(f"  {_sanitize(s)} {arrow} {_sanitize(t)}")
    lines.append("```")
    return "\n".join(lines)


def extract_drawio(src, out_dir=None) -> dict:
    src_path = Path(src).resolve()
    if not src_path.exists():
        raise FileNotFoundError(src)
    out = Path(out_dir).resolve() if out_dir else Path(f"{src_path.stem}_drawio").resolve()
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    tree = ET.parse(str(src_path))
    root = tree.getroot()
    diagrams = root.findall("diagram") or [root]

    md_parts, page_count = [doc_header(src_path)], 0
    for idx, d in enumerate(diagrams, 1):
        name = d.get("name") or f"diagram {idx}"
        model = _decode_diagram(d) if d.tag == "diagram" else ET.tostring(d, encoding="unicode")
        mer = _model_to_mermaid(model)
        md_parts.append(f"\n## {name}\n\n<!-- xberg:caption type=graph (from drawio XML) -->\n")
        md_parts.append(mer if mer else "_(no parseable nodes)_")
        md_parts.append("")

    # PNG render via CLI (ground-truth fallback)
    pages = []
    exe = _find_drawio()
    if exe:
        pdir = out / "pages"; pdir.mkdir(exist_ok=True)
        png = pdir / "diagram.png"
        try:
            subprocess.run([exe, "--export", "--format", "png", "--output", str(png), str(src_path)],
                           timeout=90, capture_output=True)
            if png.exists():
                pages.append("pages/diagram.png"); page_count = 1
        except Exception:
            pass

    for i, p in enumerate(pages):
        md_parts.append(f"\n![render]({p})")
    (out / "source.md").write_text("\n".join(md_parts), encoding="utf-8")

    manifest = {
        "engine": "drawio XML -> Mermaid + draw.io CLI render",
        "source": {"filename": src_path.name, "path": str(src_path.resolve()),
                   "size_bytes": src_path.stat().st_size},
        "elapsed_s": round(time.time() - t0, 2),
        "counts": {"diagrams": len(diagrams), "pages": page_count},
        "drawio_cli": bool(exe),
        "render_note": "" if pages else "draw.io CLI missing or export failed - Mermaid still produced",
        "outputs": {"markdown": "source.md", "pages": pages},
        "caption_status": "done (Mermaid derived from source XML)",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    print(json.dumps(extract_drawio(a[0], a[1] if len(a) > 1 else None), ensure_ascii=False, indent=2))
