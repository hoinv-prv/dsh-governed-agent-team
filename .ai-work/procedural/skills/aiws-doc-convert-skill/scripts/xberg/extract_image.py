#!/usr/bin/env python
"""
Image extractor (png/jpg/jpeg/tif/tiff/bmp/gif/webp).

An image's meaning is visual, so the image is the artifact: source.md just
pinpoints it with a `<!-- summary: pending -->` marker. The enhancement pass
(a VLM) reads the image and writes a summary — and, if it's a graph, Mermaid —
into this same source.md. No flat OCR dump.

An optional local tesseract OCR (`--ocr`) can pre-fill text for unattended
offline runs with no VLM in the loop; off by default.

Usage: python extract_image.py <image> [output_dir] [--ocr]
Requires: xberg. --ocr also needs a tesseract binary on PATH.
"""
import sys, json, time, shutil
from pathlib import Path
import xberg
from _common import renders_section, doc_header


def extract_image(src, out_dir=None, ocr: bool = False) -> dict:
    src_path = Path(src).resolve()
    if not src_path.exists():
        raise FileNotFoundError(src)
    out = Path(out_dir).resolve() if out_dir else Path(f"{src_path.stem}_img").resolve()
    (out / "figures").mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, out / "figures" / src_path.name)

    t0 = time.time()
    ocr_text, ocr_used = "", False
    if ocr and shutil.which("tesseract"):
        try:
            cfg = xberg.ExtractionConfig(
                output_format=xberg.OutputFormat.MARKDOWN,
                ocr=xberg.OcrConfig(backend="tesseract"), force_ocr=True)
            ocr_text = xberg.extract_file_sync(str(src_path), config=cfg).content or ""
            ocr_used = True
        except Exception as e:
            ocr_text = f"<!-- OCR failed: {e} -->"

    md = doc_header(src_path)
    md += renders_section([{"label": src_path.name, "images": [f"figures/{src_path.name}"]}])
    if ocr_used:
        md += f"\n## Tesseract OCR (pre-fill)\n\n{ocr_text}\n"
    (out / "source.md").write_text(md, encoding="utf-8")

    manifest = {
        "engine": "xberg (kreuzberg); VLM enhancement for summary",
        "source": {"filename": src_path.name, "path": str(src_path.resolve()),
                   "size_bytes": src_path.stat().st_size},
        "elapsed_s": round(time.time() - t0, 2),
        "ocr_used": ocr_used,
        "counts": {"images": 1, "content_chars": len(ocr_text)},
        "outputs": {"markdown": "source.md", "figures": [f"figures/{src_path.name}"]},
        "caption_status": "pending",  # VLM writes summary (+Mermaid if graph) in source.md
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    ocr = "--ocr" in a
    a = [x for x in a if x != "--ocr"]
    print(json.dumps(extract_image(a[0], a[1] if len(a) > 1 else None, ocr=ocr), ensure_ascii=False, indent=2))
