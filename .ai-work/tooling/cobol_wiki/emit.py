"""PASS 2 — render one wiki source meta per scanned file.

Two rules shape what lands in a meta.

**Omit what cannot be derived.** Several fields in the reference corpus come from
classifiers this pack does not (yet) carry — display-vs-batch, COBOL dialect, media type.
Emitting a plausible-looking guess for those would be worse than leaving them out: a wrong
value is indistinguishable from a right one downstream, whereas an absent field is visibly
absent and the golden diff reports it.

**Say what could not be resolved.** A reference the resolver could not map does not vanish;
it goes to `## Cautions` with the name as written in source, so the gap is inspectable
rather than silently missing from the edge list.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from . import ids as ids_mod
from . import objects as objects_mod
from . import syscmd as syscmd_mod
from .resolve import Resolver

#: Fields the reference carries that this pack cannot derive yet. Listed so the omission
#: is a documented decision rather than an oversight.
NOT_DERIVED = ("disp_print", "cobol_variant", "med_type")

KNOWLEDGE_TARGETS = ("module", "function", "reference")


def _tooling(project_root: Path):
    tooling = project_root / ".ai-work" / "tooling"
    if str(tooling) not in sys.path:
        sys.path.insert(0, str(tooling.resolve()))
    import _common  # type: ignore

    return _common


def _yaml_scalar(value) -> str:
    """Quote only when the value would otherwise change meaning.

    A newline is collapsed rather than quoted. Quoting does not save a multi-line value in
    this format: the continuation lines are read as further KEYS, so one runaway extraction
    corrupts every field after it. That happened for real — an unterminated quote in a CL
    header produced a twelve-line `business_name` — and the defence belongs here as well as
    in the extractor, because any extractor can return a value with a newline in it.
    """
    text = "" if value is None else str(value)
    if "\n" in text or "\r" in text:
        text = " ".join(text.split())
    if text == "":
        return ""
    if text[0] in "\"'[{&*#?|->%@`!" or ": " in text or text.strip() != text:
        return '"' + text.replace('"', '\\"') + '"'
    return text


def summary_for(rec: dict, edges: list[dict]) -> str:
    """A structured summary built from extracted fields.

    Deliberately NOT a raw head-of-file excerpt. The reference corpus's summaries are hard
    truncations at a fixed width — `… ; PROGRAM-I`, `RECORD KAMR` — which are unusable for
    lookup; reproducing that shape would carry the defect into every project that installs
    this pack.
    """
    name = rec.get("program_id") or rec["name"]
    bits: list[str] = []
    biz = (rec.get("business_name") or "").strip()
    head = f"{name} — {biz}." if biz else f"{name}."
    facts = rec.get("facts") or {}
    if facts.get("not_meta_applicable"):
        return f"{name} — binary artifact ({facts.get('binary_reason', 'binary')}); no text meta applicable."
    if facts.get("binary") or rec.get("encoding") == "binary":
        return f"{head} (binary)"
    counts = defaultdict(int)
    for e in edges:
        counts[e["role"]] += 1
    if counts.get("calls"):
        bits.append(f"{counts['calls']} call target(s)")
    if counts.get("x:uses"):
        bits.append(f"{counts['x:uses']} copybook/form reference(s)")
    if rec["file_type"] == "fdg" and facts.get("directives"):
        bits.append("file definition: " + "; ".join(facts["directives"][:3]))
    tail = " ".join(f"{rec['file_type']}." for _ in (1,)) + (" " + ", ".join(bits) + "." if bits else "")
    return f"{head} {tail}".strip()


def lookup_keys_for(rec: dict) -> list[str]:
    keys = [rec.get("program_id") or rec["name"], rec["library"], rec["file_type"], rec["system"]]
    biz = (rec.get("business_name") or "").strip()
    if biz:
        keys.append(biz)
    out, seen = [], set()
    for k in keys:
        k = str(k).strip()
        if k and k.lower() not in seen:
            seen.add(k.lower())
            out.append(k)
    return out


def build_meta_text(
    rec: dict,
    cfg,
    resolver: Resolver,
    *,
    updated_at: str,
    emit_partial: bool = False,
) -> tuple[str, dict]:
    """Render one meta. Returns (text, stats)."""
    sid = ids_mod.source_id(
        cfg,
        system=rec["system"],
        library=rec["library"],
        lib_path=rec.get("lib_path", ""),
        file_type=rec["file_type"],
        name=rec["name"],
    )
    facts = rec.get("facts") or {}
    # A file is a stub when the dedicated binary handler said so, OR when ANY handler found
    # binary content. The second case was being missed: 58 definition files went through a
    # text handler, decoded as binary, and were emitted without the markers — so downstream
    # code filtering on `not_meta_applicable` would have tried to read them.
    is_stub = bool(facts.get("not_meta_applicable")) or rec.get("encoding") == "binary"
    if is_stub and not facts.get("binary_reason"):
        facts = dict(facts, binary_reason=f"{rec['file_type']}_binary")
    title = f"{rec['file_name']} — {rec['system']}/{rec['library']}"

    edges: list[dict] = []
    cautions: list[str] = list(rec.get("cautions") or [])
    stats = defaultdict(int)
    for ref in rec.get("refs", []):
        # A command invoked by nearly every program contributes an edge to nearly every
        # meta. The node still records how many callers it has; the edges themselves are
        # suppressed because they would swamp the graph without distinguishing anything.
        if (
            ref.get("kind") == syscmd_mod.SYSCMD_KIND
            and ref["name"].upper() in getattr(cfg, "syscmd_ubiquitous_resolved", ())
        ):
            stats["skipped_ubiquitous_syscmd"] += 1
            continue
        res = resolver.resolve(
            ref["name"],
            system=rec["system"],
            role=ref["role"],
            library_hint=ref.get("lib_hint", ""),
            caller_id=sid,
            kind=ref.get("kind", ""),
        )
        stats[res.reason] += 1
        if res.ok:
            edges.append(
                {
                    "target": res.source_id,
                    "role": ref["role"],
                    "note": f"{rec['name']} {ref['role']} {ref['name']}",
                }
            )
        elif cfg.on_unresolved == "cautions":
            detail = (
                f"ambiguous between {', '.join(res.candidates)}"
                if res.reason == "ambiguous"
                else res.reason
            )
            cautions.append(f"{ref['role']} → {ref['name']}: {detail}; no edge emitted")

    # Membership is mechanical and always known, so it is asserted unconditionally rather
    # than resolved: the library node is derived from the same path this file came from.
    if cfg.emit_part_of and rec["library"]:
        edges.append({
            "target": objects_mod.module_id(cfg, rec["system"], rec["library"]),
            "role": "part_of",
            "note": f"{rec['name']} is part of {rec['library']}",
        })

    fm: list[tuple[str, str]] = [
        ("artifact_type", "wiki_source_meta"),
        ("source_id", sid),
        ("title", title),
        ("source_type", cfg.source_type),
        ("status", "active"),
        ("file_name", rec["file_name"]),
        ("library", rec["library"]),
        ("system", rec["system"]),
        ("file_type", rec["file_type"]),
    ]
    if is_stub:
        fm += [
            ("not_meta_applicable", "true"),
            ("artifact_kind", "binary"),
            ("binary_reason", str(facts.get("binary_reason", "binary"))),
        ]
    else:
        if rec.get("program_id"):
            fm.append(("program_id", rec["program_id"]))
        if rec.get("business_name"):
            fm.append(("business_name", rec["business_name"]))
    # Outside the branch on purpose. `not_meta_applicable` means "do not parse this as
    # text", not "nothing is known about it" — and the encoding IS known, because deciding
    # it was binary is how we got here. Emitting the marker but dropping the field cost
    # 1170 files their `encoding` the first time this was written.
    if rec.get("encoding"):
        fm += [("encoding", rec["encoding"]), ("line_count", str(rec["line_count"]))]
    fm += [
        ("artifact_locator", rec["locator"]),
        ("updated_at", updated_at),
        ("profile_id", cfg.profile_id),
    ]
    if emit_partial and not is_stub:
        # The canonical completion seam: mechanical fields now, an LLM pass improves the
        # semantic ones later, and lint blocks the partial from being treated as finished.
        fm.append(("needs_completion", "[summary, lookup_keys, related_sources]"))

    lines = ["---"]
    lines += [f"{k}: {_yaml_scalar(v)}".rstrip() for k, v in fm]
    lines += ["---", "", f"# {title}", ""]

    if is_stub:
        lines += [
            "Binary artifact — no text-source meta applicable.",
            "",
        ]
    lines += ["## Summary", summary_for(rec, edges), ""]
    lines += ["## Knowledge Targets"] + [f"- {t}" for t in KNOWLEDGE_TARGETS] + [""]
    lines += ["## Lookup Keys"] + [f"- {k}" for k in lookup_keys_for(rec)] + [""]
    if edges:
        lines += ["## Related Sources"]
        for e in sorted(edges, key=lambda x: (x["role"], x["target"])):
            lines.append(f"- **{e['target']}** — role: {e['role']} — {e['note']} [asserted]")
        lines.append("")
    if cautions:
        lines += ["## Cautions"] + [f"- {c}" for c in dict.fromkeys(cautions)] + [""]

    return "\n".join(lines).rstrip() + "\n", dict(stats)


#: Frontmatter this builder OWNS. On a rebuild its answer replaces whatever was there,
#: including by being absent — "I did not find a program_id" is itself a finding.
OWNED_FIELDS = frozenset({
    "artifact_type", "source_id", "title", "source_type", "status", "file_name", "library",
    "system", "file_type", "not_meta_applicable", "artifact_kind", "binary_reason",
    "encoding", "line_count", "artifact_locator", "updated_at", "profile_id",
    "needs_completion",
})

#: `business_name` and `program_id` are deliberately NOT owned. The builder's value wins
#: whenever it has one — the merge only carries forward keys absent from the new meta — but
#: where extraction found nothing, the existing value survives. Deleting a curated value and
#: putting nothing in its place is not a refresh, it is data loss with extra steps. Measured
#: here: 18 real business names (`ﾎﾝﾀﾞｶﾚﾝﾀﾞｰ` among them) and 2 program ids.

#: Body sections this builder owns, by heading.
OWNED_SECTIONS = frozenset({
    "Summary", "Knowledge Targets", "Lookup Keys", "Related Sources", "Cautions",
})


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Body -> [(heading, text-including-heading)], preserving order and any preamble."""
    parts: list[tuple[str, str]] = []
    current, buf = "", []
    for line in (body or "").split("\n"):
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if buf:
                parts.append((current, "\n".join(buf)))
            current, buf = m.group(1), [line]
        else:
            buf.append(line)
    if buf:
        parts.append((current, "\n".join(buf)))
    return parts


def merge_preserving_unknown(new_text: str, existing_path: Path, common) -> tuple[str, dict]:
    """Carry forward everything in an existing meta that this builder does not own.

    Rebuilding a meta by writing a fresh file DELETES every field another tool put there.
    Measured on this project's own corpus: a straight rewrite of 8857 metas would have
    dropped 3843 `disp_print`, 3843 `cobol_variant`, 2821 `cl_callers`, 2666
    `copybooks_used` and 1638 `med_type` real values, plus a `vld_usage` section on 79
    files — none of which this builder can regenerate. That is not a refresh; it is a
    partial rewrite dressed as one.

    Owned fields are replaced outright, absence included. Unowned fields and unowned body
    sections are preserved verbatim, in their original order.
    """
    if not existing_path.is_file():
        return new_text, {}
    try:
        old_meta, old_body = common.parse_frontmatter(common.read_text(existing_path))
    except Exception:  # noqa: BLE001 - a corrupt existing meta must not stop the rebuild
        return new_text, {"unparsable_existing": 1}
    if not old_meta:
        return new_text, {}

    new_meta, new_body = common.parse_frontmatter(new_text)
    kept_fields = [k for k in old_meta if k not in OWNED_FIELDS and k not in (new_meta or {})]
    old_sections = _split_sections(old_body)
    kept_sections = [
        (h, txt) for h, txt in old_sections
        if h and h not in OWNED_SECTIONS
        and h not in {n for n, _ in _split_sections(new_body)}
    ]
    if not kept_fields and not kept_sections:
        return new_text, {}

    head, _, rest = new_text.partition("\n---\n")
    lines = head.split("\n")
    for k in kept_fields:
        lines.append(f"{k}: {_yaml_scalar(old_meta[k])}".rstrip())
    out = "\n".join(lines) + "\n---\n" + rest
    if kept_sections:
        out = out.rstrip() + "\n\n" + "\n\n".join(txt.strip() for _h, txt in kept_sections) + "\n"
    return out, {"fields_preserved": len(kept_fields),
                 "sections_preserved": len(kept_sections),
                 "metas_merged": 1}


def meta_path(rec: dict, cfg, out_root: Path, meta_subdir: str) -> Path:
    rel = Path(meta_subdir) if meta_subdir else Path(cfg.source_type)
    parts = [p for p in (rec["lib_path"] or rec["library"]).split("-") if p]
    return out_root / rel / rec["system"] / Path(*parts) / f"{rec['file_name']}.md"


def emit_all(
    symbols: dict,
    cfg,
    resolver: Resolver,
    *,
    project_root: Path,
    out_root: Path,
    meta_subdir: str,
    updated_at: str,
    only_under: str = "",
    emit_partial: bool = False,
    dry_run: bool = False,
    preserve_unknown: bool = True,
) -> dict:
    common = _tooling(project_root)
    written = 0
    totals: dict[str, int] = defaultdict(int)
    merge: dict[str, int] = defaultdict(int)
    for locator, rec in symbols["files"].items():
        if only_under and not locator.startswith(only_under.replace("\\", "/").rstrip("/") + "/"):
            continue
        text, stats = build_meta_text(
            rec, cfg, resolver, updated_at=updated_at, emit_partial=emit_partial
        )
        for k, v in stats.items():
            totals[k] += v
        path = meta_path(rec, cfg, out_root, meta_subdir)
        if preserve_unknown:
            text, mstats = merge_preserving_unknown(text, path, common)
            for k, v in mstats.items():
                merge[k] += v
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            common.write_meta_if_changed(path, text)
        written += 1
    return {"written": written, "resolution": dict(totals), "merge": dict(merge)}
