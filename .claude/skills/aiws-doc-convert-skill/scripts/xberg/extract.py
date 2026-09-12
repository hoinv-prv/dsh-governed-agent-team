#!/usr/bin/env python
"""
xberg document extractor — counterpart to the docling-extract skill.

xberg (pip package) is a thin shim over the Rust `kreuzberg` engine.
Emits Markdown + HTML + JSON + manifest + extracted figures, mirroring
the output layout of ../conversion_test so the two engines can be compared
side by side.

Usage:
    python extract.py <input_file> [output_dir]

If output_dir omitted, defaults to ./<stem>_out
"""
import sys, json, time, base64
from pathlib import Path

import xberg


def _meta_to_dict(md):
    """Metadata is a mapping-like object; coerce to a plain dict."""
    if md is None:
        return {}
    if hasattr(md, "keys"):
        return {k: md.get(k) for k in md.keys()}
    return {k: getattr(md, k) for k in dir(md) if not k.startswith("_")}


def extract(src: str, out_dir: str | None = None) -> dict:
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError(src)

    out = Path(out_dir) if out_dir else Path(f"{src_path.stem}_out")
    (out / "figures").mkdir(parents=True, exist_ok=True)

    # One extraction per output format (engine is fast; ~0.2s each).
    fmts = {
        "md":   xberg.OutputFormat.MARKDOWN,   # proper "| ... |" tables — best for AI
        "html": xberg.OutputFormat.HTML,
    }
    results = {}
    t0 = time.time()
    for ext, fmt in fmts.items():
        cfg = xberg.ExtractionConfig(output_format=fmt)
        r = xberg.extract_file_sync(str(src_path), config=cfg)
        (out / f"source.{ext}").write_text(r.content or "", encoding="utf-8")
        results[ext] = r
    elapsed = round(time.time() - t0, 2)

    md_res = results["md"]
    meta = _meta_to_dict(md_res.metadata)

    # Figures (if the engine surfaced any embedded images).
    figures = []
    for i, im in enumerate(md_res.images or [], 1):
        data = getattr(im, "data", None)
        if not data:
            continue
        fname = f"fig_{i:03d}.png"
        (out / "figures" / fname).write_bytes(bytes(data))
        figures.append({"filename": fname, "relative_path": f"figures/{fname}"})

    # JSON dump: metadata + tables (as markdown) + full markdown content.
    tables = []
    for i, tb in enumerate(md_res.tables or [], 1):
        tables.append({
            "index": i,
            "markdown": getattr(tb, "markdown", None) or getattr(tb, "content", None),
        })
    doc_json = {
        "metadata": meta,
        "tables": tables,
        "content_markdown": md_res.content,
    }
    (out / "source.json").write_text(
        json.dumps(doc_json, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "engine": "xberg (kreuzberg Rust core)",
        "source": {"filename": src_path.name, "size_bytes": src_path.stat().st_size},
        "outputs": {"markdown": "source.md", "html": "source.html", "json": "source.json"},
        "elapsed_s": elapsed,
        "mime": md_res.mime_type,
        "quality_score": md_res.quality_score,
        "sheet_count": meta.get("sheet_count"),
        "sheet_names": meta.get("sheet_names"),
        "counts": {
            "content_chars": len(md_res.content or ""),
            "tables": len(md_res.tables or []),
            "images": len(figures),
        },
        "warnings": md_res.processing_warnings,
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    m = extract(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps(m, ensure_ascii=False, indent=2))
