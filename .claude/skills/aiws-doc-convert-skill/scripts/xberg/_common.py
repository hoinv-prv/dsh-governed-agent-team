"""Shared helpers for the xberg-extract handlers."""
import re
from pathlib import Path
import xberg


def doc_header(src_path, subtitle="") -> str:
    """Top-of-source.md header that records WHERE the original file is, so an AI
    reading the extraction can always go back to the source for full/exact data
    (complete rows beyond any sample, precise formatting, anything summarized)."""
    p = Path(src_path)
    lines = [
        f"# {p.name}",
        "",
        f"> **Source file:** `{p.resolve()}`",
        "> AI-readable extraction. For the full/exact original — complete data rows "
        "beyond any sample, precise values/formatting — open the source file above.",
    ]
    if subtitle:
        lines += ["", subtitle]
    return "\n".join(lines) + "\n"


def sanitize(name: str) -> str:
    """Filesystem-safe slug (kept for any place that still needs a name slug)."""
    return re.sub(r'[\\/:*?"<>|]+', "_", name or "").strip() or "unit"


def render_pdf_pages(pdf_path, out_dir, stem, dpi=150, max_pages=2000):
    """Render every page of a PDF to <out_dir>/<stem>.png (single page) or
    <out_dir>/<stem>_pNN.png (multi-page). Returns the list of relative names.

    stem is an index-based name like 'slide_01', 'page_01', 'sheet_03'."""
    out_dir.mkdir(parents=True, exist_ok=True)
    imgs, i = [], 0
    while i < max_pages:
        try:
            b = bytes(xberg.render_pdf_page(str(pdf_path), i, dpi=dpi))
        except Exception:
            break
        imgs.append(b); i += 1
    names = []
    for j, b in enumerate(imgs, 1):
        name = f"{stem}.png" if len(imgs) == 1 else f"{stem}_p{j:02d}.png"
        (out_dir / name).write_bytes(b)
        names.append(name)
    return names


def units_section(units, title="Units", intro=None) -> str:
    """Build the per-unit body of source.md.

    units: list of dicts { 'label': str, 'images': [rel paths], 'text': str }.
    Each unit keeps three things TOGETHER so the file stays faithful to the
    original AND easy for an AI to read:
      **Image:**     the render (ground truth, opened on demand)
      **Extracted:** the text actually pulled from that unit (faithful content)
      **Summary:**   filled by the enhancement pass (+ Mermaid for graphs)
    The `<!-- summary: pending -->` marker is where the enhancement pass writes.
    """
    if intro is None:
        intro = ("_Each unit below keeps its render (image path), the text extracted "
                 "from it, and a summary. Summary + any Mermaid are filled by the "
                 "enhancement pass; the extracted text and image are faithful from "
                 "the first conversion._")
    out = [f"\n\n---\n\n## {title}\n", intro + "\n"]
    for u in units:
        out.append(f"\n### {u['label']}")
        for img in u.get("images", []):
            out.append(f"**Image:** ![render]({img})")
        txt = (u.get("text") or "").strip()
        if txt:
            out.append("**Extracted:**\n\n" + txt + "\n")
        out.append("<!-- summary: pending -->")
    return "\n".join(out) + "\n"


# Backwards-compatible alias (older handlers call renders_section)
def renders_section(units) -> str:
    return units_section(units, title="Renders (per unit)")
