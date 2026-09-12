"""PASS 1 — walk the source tree and build the symbol table.

Scope note that is easy to get wrong: PASS 1 covers the WHOLE tree even when the build
only emits metas for one library. Edges resolve against a system-wide index, so scanning
only the emit scope would turn every call out of that library into an unresolved
reference. That is why `--scan-root` and `--root` are separate arguments.

The result is written to a JSON sidecar rather than kept in memory. It costs one file and
buys two things measured to matter: a one-library refresh without re-reading the tree, and
a readable artifact to open when an edge resolves to the wrong target — which, on this
corpus, was where every single missing-edge defect turned out to live.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from . import handlers as handler_registry


class ScanRecord(dict):
    """One scanned file. A dict so the sidecar round-trips without a schema layer."""


def _iter_source_files(scan_root: Path, cfg):
    """Yield (system, library, path) for every file the extension table knows.

    Layout is `{source_root}/{system}/{library}/…`; a single-system project (`systems: []`)
    is handled by treating the root itself as the one system.
    """
    systems = cfg.systems or [""]
    for system in systems:
        base = scan_root / system if system else scan_root
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            ext = path.suffix.lstrip(".").upper()
            if ext not in cfg.by_extension:
                continue
            rel = path.relative_to(base)
            # `library` is the first directory (that is what the meta records), but the id
            # is built from EVERY directory level: nested sub-libraries like `FQYO/FQYO`
            # appear in full in the reference ids, and collapsing them to the first level
            # produced a colliding id for every file under one.
            dirs = [p.upper() for p in rel.parts[:-1]]
            library = dirs[0] if dirs else ""
            yield system, library, "-".join(dirs), path


def scan(project_root: Path, cfg, *, scan_root: Path | None = None, limit: int = 0) -> dict:
    """Build the symbol table for the whole tree."""
    root = scan_root or (project_root / cfg.source_root)
    cfg.load_explicit_map(project_root)
    files: dict[str, dict] = {}
    counts: dict[str, int] = {}

    for n, (system, library, lib_path, path) in enumerate(_iter_source_files(root, cfg)):
        if limit and n >= limit:
            break
        data = path.read_bytes()
        ext = path.suffix.lstrip(".").upper()

        # The extension is only a hint. Sniffing needs text, so decode cheaply first —
        # every `.PRC` in the reference corpus is COBOL despite the table saying CL.
        #
        # `errors="replace"` is load-bearing, not laziness: a fixed byte slice cuts through
        # multi-byte characters, and a strict decode of the fragment then raises for EVERY
        # candidate encoding, leaving an empty probe that silently falls back to the
        # extension. Exactly one file in the reference corpus landed on that boundary, and
        # it cost both its file_type and one of its call edges. The probe is only ever
        # pattern-matched, never stored, so replacement characters are harmless.
        probe = ""
        for enc in cfg.encoding_try_order:
            try:
                probe = data[:4096].decode(enc, errors="replace")
                break
            except LookupError:
                continue
        locator = path.relative_to(project_root).as_posix()
        file_type = cfg.file_type_for(ext, probe, locator)
        if not file_type or file_type == cfg.SKIP:
            # Known extension, deliberately not built (e.g. `.md` outside the converted
            # definition directory). Counted so the number is visible, never silent.
            counts["_skipped"] = counts.get("_skipped", 0) + 1
            continue

        handler = handler_registry.for_file_type(file_type, cfg)
        result = handler.extract(path, data, cfg, file_type=file_type)

        rec = {
            "locator": locator,
            "system": system,
            "library": library,
            "lib_path": lib_path,
            "file_name": path.name,
            "name": path.stem.upper(),
            "ext": ext,
            "file_type": result.file_type or file_type,
            "encoding": result.encoding,
            "line_count": result.line_count,
            "program_id": result.program_id,
            "business_name": result.business_name,
            "facts": result.facts,
            "cautions": result.cautions,
            "refs": [asdict(r) for r in result.refs],
        }
        files[locator] = rec
        counts[rec["file_type"]] = counts.get(rec["file_type"], 0) + 1

    _resolve_pending_roles(files, cfg)

    return {
        "version": 1,
        "source_root": str(cfg.source_root),
        "systems": cfg.systems,
        "counts": counts,
        "files": files,
    }


PENDING_FILE_ROLE = "file:pending"


def _resolve_pending_roles(files: dict, cfg) -> None:
    """Decide the role of file references that carried no device prefix.

    A `SELECT … ASSIGN TO DA-VI-x` states the category in the token. A CL `CRTFILE x` does
    not, and measurement showed neither the command nor the target's type predicts it. What
    does carry signal is the file itself: where the SAME file is also assigned WITH a prefix
    somewhere in the corpus, that category is the file's.

    The majority table is built from the pack's own prefixed extractions — never from the
    reference — so this stays a derivation rather than a copy. Files that never appear with
    a prefix fall to the default role, which is what the corpus majority does anyway.
    """
    from collections import Counter, defaultdict

    votes: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for rec in files.values():
        for ref in rec["refs"]:
            kind = ref.get("kind", "")
            if kind.startswith("ASSIGN/"):
                votes[(rec["system"], ref["name"])][kind.split("/", 1)[1]] += 1

    for rec in files.values():
        for ref in rec["refs"]:
            if ref["role"] != PENDING_FILE_ROLE:
                continue
            cnt = votes.get((rec["system"], ref["name"]))
            category = cnt.most_common(1)[0][0] if cnt else ""
            ref["role"] = (
                cfg.file_roles.get(category, cfg.file_role_default)
                if category else cfg.file_role_default
            )
            ref["kind"] = f"{ref['kind']}->{category or 'no-prefixed-occurrence'}"


def write_sidecar(symbols: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(symbols, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)
    return path


def read_sidecar(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
