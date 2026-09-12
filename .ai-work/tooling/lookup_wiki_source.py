#!/usr/bin/env python3
"""Lookup sources via the Wiki Source Index.

Modes:
  - lexical  : substring match across source_id, title, lookup_keys, path
  - id       : exact source_id match
  - path     : match against path tokens of artifact_locator
  - semantic : token-level bag-of-words match — splits query into tokens,
               scores each token against lookup_keys + summary; handles
               multi-word queries and concept-level retrieval

Scope & raw search (CR-AIWS-2026-06-052):
  --scope        comma-list of registered indices (project,local,aiws; 'all' = all three).
                 Default 'project,aiws' — local is rule-#11-gated (opt-in, requires --authorized).
  --include-raw  off | on-empty | always — un-registered (raw) Glob/Grep fallback over the
                 project dirs in document_search_guidelines.md. Requires --authorized.
  --authorized   human | aip | agent-rule — REQUIRED when --include-raw != off OR scope goes
                 beyond project,aiws. Absent → the tool refuses (halt-and-ask, never silent).
  --lookup-mode  object | concept (default concept). The on-empty raw fallback fires only for
                 object lookups (0 registered hits + object mode).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_ai_work_root, parse_frontmatter, read_jsonl  # noqa: E402
from _common import score_lexical, score_semantic  # noqa: E402  CR-2026-07-001 Q3: single-source scoring
from _common import (  # noqa: E402  CR-2026-07-007 B1/B2/B3: fold + aliases + query-time DF
    wiki_tokens, compute_token_df, load_query_aliases, expand_query_tokens,
)


# CR-AIWS-2026-06-061: the multi-system primitives are centralized in _common (WIKI_META_INDEX_SPEC
# §8.5 "reuse, do not re-implement"). Keep the module-local names as thin re-exports so existing
# callers here — and smoke_test_wiki_lookup.py, which imports `_in_system` from this module — are
# unchanged. `read_project_config`/`in_system` are the single source of the config reader + gate.
from _common import read_project_config as _project_config, in_system as _in_system  # noqa: E402,F401

# CR-AIWS-2026-07-024: scope machinery promoted to _common — single resolver for every
# index-reading tool (no tool re-implements its own loader). Thin re-exports keep this
# module's public surface + behavior byte-identical (DP-024-C alias mỏng).
from _common import (  # noqa: E402,F401
    DEFAULT_SCOPE, VALID_SCOPES, parse_scope, resolve_index_paths,
)

_parse_scope = parse_scope


SUPERSEDED_PENALTY = 0.2


def _tokens(s: str) -> list[str]:
    # CR-AIWS-2026-07-007 B1: delegate to the shared folded tokenizer (two-way diacritic fold).
    return wiki_tokens(s)


def _raw_dirs_from_guidelines(ai_work: Path) -> list[str]:
    """Extract the project-internal directory list from the 'Raw search fallback'
    table in document_search_guidelines.md (CR-AIWS-2026-06-052). Each first-column
    backtick-quoted path is a directory to Glob/Grep. Returns [] if the doc is absent.
    """
    doc = ai_work / "wiki" / "reference" / "document_search_guidelines.md"
    if not doc.exists():
        return []
    text = doc.read_text(encoding="utf-8")
    m = re.search(r"##\s+Raw search fallback.*?(?=\n##\s|\Z)", text, re.S)
    section = m.group(0) if m else text
    dirs: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        bt = re.match(r"`([^`]+)`", cells[0])
        if bt:
            d = bt.group(1).strip()
            if d and d not in dirs:
                dirs.append(d)
    return dirs


def _raw_search(query: str, qtokens: set[str], ai_work: Path,
                project_root: Path, limit: int) -> list[dict]:
    """Authorization-gated raw (un-registered) fallback (CR-AIWS-2026-06-052).

    Glob/grep the project-internal dirs listed in document_search_guidelines.md.
    Match by filename-token overlap first, then a light content substring grep.
    Results are labelled 'unregistered' and ranked below any registered hit
    (the caller renders them in a separate, lower block).
    """
    results: list[dict] = []
    seen: set[str] = set()
    q = query.lower()
    for d in _raw_dirs_from_guidelines(ai_work):
        base = project_root / d
        if not base.exists() or not base.is_dir():
            continue
        for fp in base.rglob("*.md"):
            if not fp.is_file():
                continue
            try:
                rel = fp.relative_to(project_root).as_posix()
            except ValueError:
                rel = fp.as_posix()
            if rel in seen:
                continue
            name_tokens = {t.lower() for t in _tokens(fp.stem)}
            score = 2 * len(qtokens & name_tokens)
            if score == 0:
                try:
                    if q and q in fp.read_text(encoding="utf-8", errors="ignore").lower():
                        score = 1
                except OSError:
                    continue
            if score > 0:
                seen.add(rel)
                results.append({
                    "score": score,
                    "source_id": f"unregistered:{rel}",
                    "title": fp.stem,
                    "artifact_locator": rel,
                    "match_reason": "raw (un-registered) artifact — Glob/Grep fallback; "
                                    "register via /aiws-wiki build-meta if reused",
                    "recommended_next_action": "open_source_for_evidence",
                    "runtime_boundary": "unregistered raw hit; ranked below registered index results",
                    "unregistered": True,
                })
    results.sort(key=lambda r: -r["score"])
    return results[:limit]


def _apply_status_penalty(score: float, rec: dict, include_inactive: bool) -> float:
    """Apply ranking penalty for non-active entries unless include_inactive is set."""
    if include_inactive:
        return score
    if rec.get("status") == "superseded":
        return score * SUPERSEDED_PENALTY
    return score


# Q3 (CR-AIWS-2026-07-001): scoring is now the SINGLE implementation in `_common`
# (score_lexical / score_semantic) — the former inline copies here + in smoke_test drifted (CAP-902-004).
# These thin delegators keep the local names; all scoring logic (incl. the Q3 exact-name + authority
# boosts) lives in one place.
def _score(rec: dict, query: str, qtokens: set[str]) -> int:
    return score_lexical(rec, query, qtokens)


def _score_semantic(rec: dict, qtokens: set[str], query: str = "", df: dict = None) -> int:
    return score_semantic(rec, qtokens, query, df=df)



def _runtime_entry(score: int, rec: dict) -> dict:
    """Return lookup result with explicit runtime boundary fields.

    Lookup result is a route/context candidate, not evidence verification.
    """
    representation_status = rec.get("source_representation_status") or rec.get("representation_status") or ""
    recommended = "open_source_for_evidence"
    if representation_status in {"partial", "needs_review"}:
        recommended = "request_human_check"
    elif representation_status == "failed":
        recommended = "request_reconversion"
    elif representation_status == "unknown":
        recommended = "check_representation_quality"

    return {
        "score": score,
        "source_id": rec.get("source_id", ""),
        "title": rec.get("title", ""),
        "summary_short": rec.get("summary_short", ""),
        "source_type": rec.get("source_type", ""),
        "status": rec.get("status", ""),
        "authority_level": rec.get("authority_level", ""),
        "freshness_status": rec.get("freshness_status", ""),
        "promotion_status": rec.get("promotion_status", ""),
        "source_representation_status": representation_status,
        "source_representation_caution": rec.get("source_representation_caution", ""),
        "index_entry": rec,
        "meta_locator": rec.get("meta_locator", ""),
        "artifact_locator": rec.get("artifact_locator", ""),
        "original_source_locator": rec.get("original_source_locator", ""),
        "representation_locator": rec.get("representation_locator", rec.get("artifact_locator", "")),
        "representation_type": rec.get("representation_type", ""),
        "conversion_method": rec.get("conversion_method", ""),
        "conversion_limitations": rec.get("conversion_limitations", []),
        "intended_ai_use": rec.get("intended_ai_use", ""),
        "match_reason": "matched Wiki Source Index entry; open AIWS-readable representation for verification",
        "recommended_next_action": recommended,
        "runtime_boundary": "lookup result is a candidate source route, not evidence verification",
    }


def _print_raw_fallback_hint(query: str) -> None:
    print("─" * 60)
    print("Hint — Not in index. Raw fallback required:")
    print(f"  1. Retry    : --mode tokens (if this was lexical)")
    print(f"  1b. Catalog : --mode catalog (đọc-chọn từ slim catalog đã filter — CR-2026-07-007 B6)")
    print(f"  2. Raw search: check document_search_guidelines.md for artifact dirs,")
    print(f"                 then Glob/Grep '{query}' in those directories")
    print(f"  3. If no guidelines: ask HUMAN for artifact directory locations,")
    print(f"                 then promote to document_search_guidelines.md")
    print(f"  4. If found  : register source with /aiws-wiki build-meta")
    print(f"  ❌ Do NOT report 'not found' without completing steps 1–3")
    print()
    print("If artifact is reusable (template / process doc / shared spec / guideline):")
    # CR-AIWS-2026-08-075 C6 — this hint is the INPUT FUNNEL for the `[PENDING]` lines that
    # run_aip.py sweeps into captures. It used to name only `[retrieval_gap]`, which is a Capture
    # FLAG and not a legal capture `type` — so authors copied it into `type=` and every swept record
    # came out labelled a retrieval gap regardless of what it was. Name the flag and the type
    # separately, and show the type that actually belongs on a lookup miss.
    print(f"  → Mark in AIP input table : Capture flag = [retrieval_gap]")
    print(f"  → Add entry to AIP section: ## Pre-flight Pending Captures")
    print(f'     - [PENDING] type="wiki_meta_update_candidate" '
          f'candidate_kind="retrieval_improvement" artifact="<name>" '
          f'lookup_query="<query>" reason="<why it is reusable>"')
    print(f"     (`retrieval_gap` is the FLAG, not a `type=` value — `type=` takes a capture type;")
    print(f"      a different trigger uses its own type, see wiki_candidate_capture_playbook.md)")
    print(f"  → After task              : register via /aiws-wiki register")
    print("─" * 60)


def main() -> int:
    p = argparse.ArgumentParser(description="Lookup wiki source via index")
    p.add_argument("--query", required=False, default="",
                   help="Search string (required for every mode except catalog).")
    p.add_argument("--mode", choices=["lexical", "id", "path", "semantic", "tokens", "catalog"],
                   default="lexical",
                   help="tokens = per-token overlap matching (CR-2026-07-007 B4 — new name; "
                        "'semantic' is kept as a deprecated alias of the same matching). "
                        "catalog = emit the full slim catalog (filtered by --system/--source-type) "
                        "for AI read-and-pick concept recall (CR-2026-07-007 B6; no query needed).")
    p.add_argument("--index", help="Override index path (comma-separated for multiple)")
    p.add_argument("--scope", default=DEFAULT_SCOPE, metavar="LIST",
                   help="Comma-list of registered indices to search: project,local,aiws (combinable). "
                        f"Default '{DEFAULT_SCOPE}' — 'local' is rule-#11-gated (opt-in; requires "
                        "--authorized). 'all' = project,local,aiws. 'aiws' = the pre-built AIWS "
                        "methodology wiki shipped on install (index.aiws.jsonl).")
    p.add_argument("--include-raw", choices=["off", "on-empty", "always"], default="off",
                   help="Un-registered (raw) Glob/Grep fallback over project dirs in "
                        "document_search_guidelines.md (CR-AIWS-2026-06-052). off (default) | "
                        "on-empty (fires only for an object lookup with 0 registered hits) | "
                        "always. Any value != off REQUIRES --authorized.")
    p.add_argument("--authorized", choices=["human", "aip", "agent-rule"], default=None,
                   help="Authorization source for raw / beyond-default-scope search "
                        "(CR-AIWS-2026-06-052). REQUIRED when --include-raw != off OR --scope "
                        "extends beyond project,aiws. Absent → the tool refuses (halt-and-ask; "
                        "never silent raw, never silent miss for an object lookup).")
    p.add_argument("--lookup-mode", choices=["object", "concept"], default="concept",
                   help="object = a precise artifact/object lookup (enables the on-empty raw "
                        "fallback); concept = a fuzzy keyword/concept query (default; no on-empty raw).")
    p.add_argument("--limit", "--top", type=int, default=20,
                   dest="limit", metavar="N",
                   help="Max results to return (default: 20)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--slim", dest="slim", action="store_true", default=True,
                   help="One line per result (routing fields only: score, source_id, title, "
                        "source_type, status, artifact_locator, source_representation_status, "
                        "recommended_next_action, meta_locator). This is the DEFAULT; pass --full to opt out.")
    p.add_argument("--full", "--no-slim", dest="slim", action="store_false",
                   help="Verbose multi-line records per result (summary / authority / "
                        "representation fields inline). Opt out of the default slim output.")
    p.add_argument("--include-inactive", action="store_true", default=False,
                   help="Include superseded sources at full score (default: penalized at 0.2x)")
    p.add_argument("--source-type", action="append", default=None, metavar="TYPE",
                   help="Optional: keep only results whose source_type matches (repeatable or comma-list, "
                        "e.g. --source-type process_guideline,process_template). Applied AFTER matching — "
                        "does not change scoring; omitted = no filter. Bridge from Task Lens relevant_reference_types: "
                        "*_template->process_template, *_guideline/*_checklist/naming_convention->process_guideline, sop->sop.")
    p.add_argument("--excludes", "--exclude", dest="excludes", default="", metavar="IDS",
                   help="Comma-separated source_ids to drop before scoring (already-checked entries). "
                        "Pair with the has_more footer to fetch the next batch without re-seeing prior hits.")
    p.add_argument("--system", default=None, metavar="ID",
                   help="Multi-system scoping (CR-AIWS-2026-06-017): restrict to this system's docs + common docs. "
                        "In a multi_system project you MUST pass --system or --all-systems (no silent default).")
    p.add_argument("--all-systems", dest="all_systems", action="store_true", default=False,
                   help="Multi-system scoping: search across ALL systems (explicit opt-out of system scoping).")
    ns = p.parse_args()

    # CR-AIWS-2026-07-007 B4: 'tokens' is the accurate name; 'semantic' stays as deprecated alias.
    if ns.mode == "semantic":
        print("note: --mode semantic = per-token overlap matching; new name: --mode tokens "
              "(semantic kept for compatibility).", file=sys.stderr)
    if ns.mode == "tokens":
        ns.mode = "semantic"
    if ns.mode != "catalog" and not ns.query:
        print("error: --query is required (except with --mode catalog).", file=sys.stderr)
        return 2

    # Scope parsing + authorization gate (CR-AIWS-2026-06-052). Raw search OR a scope that
    # extends beyond the project,aiws default requires an explicit authorization source —
    # otherwise the tool refuses (halt-and-ask; never silent raw, never silent broad search).
    try:
        scope_set = _parse_scope(ns.scope)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    raw_requested = ns.include_raw != "off"
    scope_beyond_default = bool(scope_set - {"project", "aiws"})
    if (raw_requested or scope_beyond_default) and not ns.authorized:
        reasons = []
        if raw_requested:
            reasons.append(f"--include-raw={ns.include_raw}")
        if scope_beyond_default:
            reasons.append(f"--scope includes {sorted(scope_set - {'project', 'aiws'})}")
        print("error: " + " and ".join(reasons) + " requires --authorized {human|aip|agent-rule}. "
              "Raw / beyond-default-scope search is never silent — name the authorization source "
              "(HUMAN in conversation, the active AIP's allow_raw_search, or a standing agent rule) "
              "or STOP and ask HUMAN.", file=sys.stderr)
        return 2

    project_root = find_ai_work_root(Path.cwd())
    ai_work = project_root / ".ai-work"
    wiki_sources = ai_work / "wiki_sources"

    # Multi-system scoping (CR-AIWS-2026-06-017). HARD-REQUIRE (HUMAN-confirmed 2026-06-15):
    # in a multi_system project, refuse to search un-scoped — NO silent default, NO auto-pick.
    cfg = _project_config(ai_work)
    active_system = None
    if cfg["multi_system"]:
        if ns.all_systems:
            active_system = None                     # explicit: search all systems
        elif ns.system:
            active_system = ns.system.strip()
            if cfg["systems"] and active_system not in cfg["systems"]:
                print(f"error: --system {active_system!r} is not in this project's systems "
                      f"{cfg['systems']}.", file=sys.stderr)
                return 2
        else:
            print("error: this is a multi_system project — you MUST pass --system <id> "
                  "(restrict to that system + common docs) or --all-systems (search all). "
                  "Refusing to search un-scoped to avoid cross-system spec bleed; no silent default. "
                  f"Valid systems: {', '.join(cfg['systems']) or '(see project_profile.yml)'}",
                  file=sys.stderr)
            return 2
    # single-system project (multi_system:false / no project_profile.yml) → no scoping; flags ignored.

    if ns.index:
        index_paths = [Path(p).resolve() for p in ns.index.split(",")]
    else:
        # CR-AIWS-2026-07-024: shared resolver (same files, same order as before)
        index_paths = resolve_index_paths(wiki_sources, scope_set)

    index_paths = [p for p in index_paths if p.exists()]
    if not index_paths:
        print("error: no index file found", file=sys.stderr)
        return 2

    records: list[dict] = []
    for idx_path in index_paths:
        records.extend(read_jsonl(idx_path))
    exclude_ids = {e.strip() for e in (ns.excludes or "").split(",") if e.strip()}
    if exclude_ids:
        records = [r for r in records if r.get("source_id") not in exclude_ids]
    q = ns.query
    qtokens = {t.lower() for t in _tokens(q)}
    # CR-AIWS-2026-07-007 B2: phrase-level alias expansion (profiles/query_aliases.yml).
    qtokens = expand_query_tokens(q, qtokens, load_query_aliases(wiki_sources / "profiles"))
    # CR-AIWS-2026-07-007 B3: query-time DF over the loaded record set (no index schema change).
    df = compute_token_df(records)

    include_inactive = ns.include_inactive

    # CR-AIWS-2026-07-007 B6: catalog mode — full slim listing (registered-only) for AI
    # read-and-pick concept recall. Respects --system / --source-type / --excludes filters;
    # --limit is NOT applied (the whole filtered catalog IS the point). No raw tier.
    if ns.mode == "catalog":
        cat = records
        if ns.source_type:
            wanted = {s.strip().lower() for item in ns.source_type for s in item.split(",") if s.strip()}
            cat = [r for r in cat if r.get("source_type", "").lower() in wanted]
        if active_system is not None:
            cat = [r for r in cat if _in_system(r, active_system)]
        cat.sort(key=lambda r: (r.get("source_type", ""), r.get("source_id", "")))
        print(f"Catalog — {len(cat)} registered entries "
              f"(scope={ns.scope}; system={active_system or 'all/common'}). "
              "AI: đọc-chọn candidates khớp intent → mở meta qua --mode id --query <source_id>. "
              "Đây là concept-recall fallback (CR-2026-07-007 B6) — vẫn registered-only, không raw.")
        cur_type = None
        for r in cat:
            st = r.get("source_type", "(none)")
            if st != cur_type:
                cur_type = st
                print(f"\n## {st}")
            summ = (r.get("summary_short", "") or "").replace("\n", " ")[:120]
            keys = ", ".join((r.get("lookup_keys", []) or [])[:3])
            sys_tag = f" [{r.get('system')}]" if r.get("system") else ""
            print(f"- {r.get('source_id','')}{sys_tag} — {r.get('title','')} — {summ}"
                  + (f" — keys: {keys}" if keys else ""))
        return 0

    if ns.mode == "id":
        matches = [r for r in records if r.get("source_id") == q]
        scored = [(100, r) for r in matches]
    elif ns.mode == "path":
        scored = []
        for r in records:
            pt = {t.lower() for t in _tokens(r.get("artifact_locator", ""))}
            hit = len(qtokens & pt)
            if hit:
                scored.append((hit * 10, r))
    elif ns.mode == "semantic":
        scored = [(s, r) for r in records if (s := _score_semantic(r, qtokens, q, df=df)) > 0]
    else:  # lexical
        scored = [(s, r) for r in records if (s := _score(r, q, qtokens)) > 0]

    if ns.source_type:
        wanted = {s.strip().lower() for item in ns.source_type for s in item.split(",") if s.strip()}
        scored = [(s, r) for s, r in scored if r.get("source_type", "").lower() in wanted]

    # Multi-system filter (CR-AIWS-2026-06-017): keep the active system's docs + common docs
    # (common = no `system` field). active_system is None when single-system or --all-systems.
    if active_system is not None:
        scored = [(s, r) for s, r in scored if _in_system(r, active_system)]

    scored = [(_apply_status_penalty(s, r, include_inactive), r) for s, r in scored]
    scored.sort(key=lambda sr: -sr[0])
    total_matches = len(scored)
    scored = scored[: ns.limit]
    has_more = total_matches > len(scored)

    # CR-AIWS-2026-07-007 B5: score-floor signal — a weak top hit is "found-but-fragile";
    # suggest the catalog-scan concept-recall path BEFORE any raw escalation.
    if scored and scored[0][0] < 15 and ns.mode in ("semantic", "lexical"):
        print(f"note: top score {scored[0][0]} < 15 (fragile match) — consider "
              f"`--mode catalog` (read-and-pick from the filtered slim catalog) before widening "
              f"or raw escalation.", file=sys.stderr)

    results = [_runtime_entry(s, r) for s, r in scored]

    # Raw (un-registered) tier (CR-AIWS-2026-06-052) — authorization-gated, ranked below registered.
    # Fires when authorized AND (include-raw=always) OR (include-raw=on-empty + object lookup + 0 registered hits).
    raw_results: list[dict] = []
    if ns.authorized and (
        ns.include_raw == "always"
        or (ns.include_raw == "on-empty" and ns.lookup_mode == "object" and total_matches == 0)
    ):
        raw_results = _raw_search(q, qtokens, ai_work, project_root, ns.limit)

    if ns.format == "json":
        payload = {"matches": [], "has_more": has_more,
                   "total_matches": total_matches, "shown": len(results)}
        if raw_results:
            payload["unregistered"] = [
                {"score": r["score"], "source_id": r["source_id"], "title": r["title"],
                 "artifact_locator": r["artifact_locator"], "match_reason": r["match_reason"]}
                for r in raw_results
            ]
        if not results:
            if not raw_results:
                payload["raw_fallback_hint"] = (
                    "Not in index. Retry --mode semantic, then raw search in artifact dirs "
                    "(see document_search_guidelines.md or ask HUMAN)."
                )
            print(json.dumps(payload, ensure_ascii=False))
        elif ns.slim:
            payload["matches"] = [{"score": r["score"], "source_id": r.get("source_id", ""),
                     "title": r.get("title", ""), "source_type": r.get("source_type", ""),
                     "status": r.get("status", ""),
                     "artifact_locator": r.get("artifact_locator", ""),
                     "source_representation_status": r.get("source_representation_status", ""),
                     "recommended_next_action": r.get("recommended_next_action", ""),
                     "meta_locator": r.get("meta_locator", "")} for r in results]
            print(json.dumps(payload, ensure_ascii=False))
        else:
            payload["matches"] = results
            print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Note: aiws-wiki lookup returns candidate source routes; open source artifact for evidence.")
        if not scored and not raw_results:
            print("(no matches)")
            _print_raw_fallback_hint(ns.query)
        elif not scored:
            print("(no registered matches — see unregistered raw candidates below)")
        # CR-AIWS-2026-07-006 A3: group-by-parent — a chunk child (has section_lines) whose PARENT
        # is also in the results renders indented under it (children keep their own rank/score;
        # a child whose parent is absent renders standalone). Order: parents/standalone by rank,
        # children re-attached after their parent in child-rank order.
        _ids_in_results = {it.get("source_id", "") for it in results}
        _ordered: list = []
        _children_of: dict = {}
        for it in results:
            _sec = (it.get("index_entry") or {}).get("section_lines", "")
            _pid = it.get("source_id", "").rsplit("-SEC-", 1)[0] if _sec else ""
            if _sec and _pid and _pid in _ids_in_results and _pid != it.get("source_id"):
                _children_of.setdefault(_pid, []).append(it)
            else:
                _ordered.append(it)
        for item, _indent in [(x, ind) for top in _ordered
                              for x, ind in ([(top, "")] +
                                             [(c, "  ↳ ") for c in _children_of.get(top.get("source_id", ""), [])])]:
            _status_tag = " [SUPERSEDED]" if item.get("status") == "superseded" else ""
            if ns.slim:
                _rep = item.get("source_representation_status", "")
                _rep_tag = f" [rep:{_rep}]" if _rep in {"partial", "needs_review", "failed", "unknown"} else ""
                _sec_tag = ""
                _sl = (item.get("index_entry") or {}).get("section_lines", "")
                if _sl:
                    _sec_tag = f" [lines {_sl}]"
                print(f"{_indent}[{item['score']:>3}] {item.get('source_id', '')}{_status_tag}{_rep_tag}{_sec_tag}  "
                      f"{item.get('title', '')} | {item.get('source_type', '')} | "
                      f"artifact={item.get('artifact_locator', '')} | "
                      f"meta={item.get('meta_locator', '')}")
                continue
            print(f"[{item['score']:>3}] {item.get('source_id', '')}{_status_tag}  {item.get('title', '')}")
            _summary = (item.get("summary_short") or "").strip().lstrip("> ").strip()
            if _summary and not _summary.startswith(("Project:", "Date:", "Status:", "Version:")):
                print(f"       summary: {_summary}")
            print(f"       type={item.get('source_type', '')}  status={item.get('status', '')}")
            if item.get("authority_level") or item.get("promotion_status"):
                print(f"       authority={item.get('authority_level', '')}  promotion={item.get('promotion_status', '')}")
            if item.get("source_representation_status"):
                print(f"       representation={item.get('source_representation_status', '')}")
            if item.get("source_representation_caution"):
                print(f"       caution: {item.get('source_representation_caution', '')}")
            if item.get("intended_ai_use"):
                print(f"       use-hint: {item.get('intended_ai_use', '')}")
            print(f"       artifact: {item.get('artifact_locator', '')}")
            if item.get("representation_locator"):
                print(f"       representation: {item.get('representation_locator', '')}")
            if item.get("original_source_locator"):
                print(f"       original: {item.get('original_source_locator', '')}")
            if item.get("conversion_limitations"):
                print(f"       limitations: {item.get('conversion_limitations', '')}")
            print(f"       meta:     {item.get('meta_locator', '')}")
            print(f"       next:     {item.get('recommended_next_action', '')}")
        if has_more:
            # E1 (CR-AIWS-2026-07-003): drop the full source_id repetition (~1.6KB/call of pure
            # duplication, CAP-902-008) — the ids are already on each result line above, so paging
            # needs no re-listing. Raise --limit, or build --excludes from the source_ids shown.
            print(f"… {total_matches - len(results)} more match(es) not shown "
                  f"(showing {len(results)} of {total_matches}). To page: raise --limit, or re-run "
                  f"with --excludes set to the source_ids already shown above. Continuing is your call.")
        if scored:
            print("Enumerate one kind: --mode catalog --source-type <type> --slim  "
                  "(e.g. function | table | process_guideline; multi-system: add --system <id>)")
        if raw_results:
            print("─" * 60)
            print(f"Unregistered (raw) candidates — authorized={ns.authorized}; "
                  f"ranked below registered, NOT in index:")
            for r in raw_results:
                print(f"[{r['score']:>3}] {r['source_id']}  artifact={r['artifact_locator']}")
            print("  → open directly for this task; register via /aiws-wiki build-meta if reused.")
    return 0 if (scored or raw_results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
