#!/usr/bin/env python3
"""Smoke-test wiki lookup quality: self-findability + custom test cases.

Modes
-----
--self-test
    For every entry in the wiki source index, verify the entry can find
    itself using:
      • its source_id  (id mode — must be rank-1)
      • each of its lookup_keys up to --key-limit (semantic mode — entry
        must appear within top --top-n results)

--cases <file.jsonl>
    Run structured test cases supplied in a JSONL file.
    Each line must be a JSON object with these fields:
      query             (required) search string
      mode              lexical | id | path | semantic  (default: semantic)
      expected_source_id  (required) source_id that must appear in results
      top_n             integer, how many top results to check (default: 5)
      label             optional human-readable description for the report

Exit codes
----------
  0  all tests passed (or no tests were run)
  1  one or more tests failed
  2  error (index not found, bad input, etc.)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_ai_work_root, read_jsonl, in_system as _in_system  # noqa: E402  centralized multi-system filter (CR-AIWS-2026-06-061 §8.5; was lookup_wiki_source per CR-058)
from _common import score_lexical, score_semantic, wiki_tokens  # noqa: E402  CR-2026-07-001 Q3: single-source scoring (no more drifting copy — CAP-902-004)
from _common import (  # noqa: E402  CR-2026-07-007: smoke mirrors production fold/aliases/DF exactly
    compute_token_df, load_query_aliases, expand_query_tokens,
)


# ── re-use scoring from lookup_wiki_source without duplication ──────────────

# Q3 (CR-AIWS-2026-07-001): tokenizer + scoring come from `_common` (SINGLE source). The former inline
# `_score_lexical`/`_score_semantic` copies here drifted from lookup_wiki_source's (CAP-902-004) — the
# smoke test now scores EXACTLY like the real lookup, so PASS/FAIL reflects real behaviour.
_tokens = wiki_tokens
_score_lexical = score_lexical


_ALIASES: list = []   # CR-2026-07-007 B2: loaded once in main() from profiles/query_aliases.yml
_DF: dict = {}        # CR-2026-07-007 B3: query-time DF over the loaded record set


def _run_query(records: list[dict], query: str, mode: str, limit: int) -> list[tuple[int, dict]]:
    q = query.strip()
    qtokens = {t.lower() for t in _tokens(q)}
    # CR-2026-07-007 B2: same phrase-level alias expansion as production lookup.
    qtokens = expand_query_tokens(q, qtokens, _ALIASES)
    if mode == "id":
        matched = [r for r in records if r.get("source_id") == q]
        scored = [(100, r) for r in matched]
    elif mode == "path":
        scored = []
        for r in records:
            pt = {t.lower() for t in _tokens(r.get("artifact_locator", ""))}
            hit = len(qtokens & pt)
            if hit:
                scored.append((hit * 10, r))
    elif mode in ("semantic", "tokens"):  # CR-2026-07-007 B4: 'tokens' = new alias
        scored = [(s, r) for r in records if (s := score_semantic(r, qtokens, q, df=_DF)) > 0]
    else:  # lexical (default)
        scored = [(s, r) for r in records if (s := _score_lexical(r, q, qtokens)) > 0]
    scored.sort(key=lambda sr: -sr[0])
    return scored[:limit]


# ── result / reporting ───────────────────────────────────────────────────────

class TestResult:
    def __init__(self, label: str, query: str, mode: str,
                 expected_id: str, passed: bool,
                 rank: int | None, score: int | None, hint: str = ""):
        self.label = label
        self.query = query
        self.mode = mode
        self.expected_id = expected_id
        self.passed = passed
        self.rank = rank
        self.score = score
        self.hint = hint

    def to_line(self, verbose: bool = False) -> str:
        tag = "PASS" if self.passed else "FAIL"
        rank_str = f"rank {self.rank}" if self.rank is not None else "not found"
        score_str = f"score {self.score}" if self.score is not None else ""
        parts = [f"[{tag}]", self.expected_id]
        if self.label:
            parts.append(f"({self.label})")
        parts.append(f"—  query={repr(self.query)}  mode={self.mode}")
        parts.append(f"  {rank_str}")
        if score_str:
            parts.append(score_str)
        if not self.passed and self.hint:
            parts.append(f"\n       hint: {self.hint}")
        return "  ".join(parts)


def _find_rank(results: list[tuple[int, dict]], expected_id: str) -> tuple[int | None, int | None]:
    for i, (score, rec) in enumerate(results):
        if rec.get("source_id") == expected_id:
            return i + 1, score
    return None, None


# ── self-test mode ───────────────────────────────────────────────────────────

def run_self_test(records: list[dict], top_n: int, key_limit: int,
                  only_ids: "set[str] | None" = None) -> list[TestResult]:
    """Self-test that each entry finds itself. When only_ids is given (Q2 — CR-AIWS-2026-07-001),
    ASSERT only those source_ids (new/changed entries at build/refresh time) while still SEARCHING
    the full index corpus — so a build-time gate can check just the touched metas without a whole
    corpus run. only_ids=None → test every entry (unchanged behaviour)."""
    results: list[TestResult] = []

    for rec in records:
        sid = rec.get("source_id", "")
        if not sid:
            continue
        if only_ids is not None and sid not in only_ids:
            continue

        # Test A: find by source_id (id mode) — must be rank 1
        id_hits = _run_query(records, sid, "id", top_n + 5)
        rank, score = _find_rank(id_hits, sid)
        passed = rank == 1
        hint = ""
        if not passed:
            hint = "source_id lookup failed — check that source_id is unique and consistent in index"
        results.append(TestResult(
            label="self:id", query=sid, mode="id",
            expected_id=sid, passed=passed, rank=rank, score=score, hint=hint
        ))

        # Test B: find by each lookup_key (semantic mode)
        keys = [k for k in (rec.get("lookup_keys", []) or []) if k and k.strip()][:key_limit]
        for key in keys:
            sem_hits = _run_query(records, key, "semantic", top_n + 5)
            rank, score = _find_rank(sem_hits, sid)
            passed = rank is not None and rank <= top_n
            hint = ""
            if not passed:
                top_ids = [r.get("source_id", "") for _, r in sem_hits[:3]]
                hint = (
                    f"lookup_key {repr(key)} did not surface this entry in top-{top_n}. "
                    f"Top results: {top_ids}. "
                    "Consider making lookup_key more specific or adding T1-tier tags."
                )
            results.append(TestResult(
                label=f"self:key={repr(key)}", query=key, mode="semantic",
                expected_id=sid, passed=passed, rank=rank, score=score, hint=hint
            ))

    return results


# ── structured cases mode ────────────────────────────────────────────────────

def run_cases(records: list[dict], cases_path: Path, top_n_default: int) -> list[TestResult]:
    results: list[TestResult] = []
    raw_cases: list[dict[str, Any]] = []

    try:
        text = cases_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: cases file not found: {cases_path}", file=sys.stderr)
        sys.exit(2)

    for i, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            raw_cases.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"error: bad JSON on line {i} of {cases_path}: {e}", file=sys.stderr)
            sys.exit(2)

    for case in raw_cases:
        query = case.get("query", "").strip()
        expected_id = case.get("expected_source_id", "").strip()
        mode = case.get("mode", "semantic")
        top_n = int(case.get("top_n", top_n_default))
        label = case.get("label", "")
        # CR-AIWS-2026-06-058: optional multi-system scoping for cross-system no-bleed cases.
        system = (case.get("system") or "").strip() or None  # scope query to system + common
        forbid = [f for f in (case.get("forbid") or []) if f]  # source_ids that MUST be absent

        if not query or (not expected_id and not forbid):
            print(f"warning: skipping case missing query or (expected_source_id | forbid): {case}",
                  file=sys.stderr)
            continue

        # Full scored set so `forbid` means "absent at ANY rank"; scope via the SAME predicate
        # production uses (no re-implemented gate). system=None → _in_system is a no-op.
        hits = _run_query(records, query, mode, len(records))
        if system:
            hits = [(s, r) for s, r in hits if _in_system(r, system)]

        rank = score = None
        passed = True
        hint_parts = []
        scope_note = f" under system={system!r}" if system else ""
        if expected_id:
            rank, score = _find_rank(hits, expected_id)
            if rank is None or rank > top_n:
                passed = False
                top_ids = [r.get("source_id", "") for _, r in hits[:3]]
                hint_parts.append(f"expected {repr(expected_id)} in top-{top_n}{scope_note} "
                                  f"but got: {top_ids}")
        if forbid:
            leaked = [fid for fid in forbid
                      if any(r.get("source_id") == fid for _, r in hits)]
            if leaked:
                passed = False
                hint_parts.append(f"FORBIDDEN present{scope_note}: {leaked}")

        results.append(TestResult(
            label=label, query=query, mode=mode,
            expected_id=expected_id or f"(forbid:{','.join(forbid)})",
            passed=passed, rank=rank, score=score, hint="; ".join(hint_parts)
        ))

    return results


# ── report formatting ────────────────────────────────────────────────────────

def print_report(results: list[TestResult], fmt: str, verbose: bool) -> None:
    if fmt == "json":
        out = []
        for r in results:
            out.append({
                "passed": r.passed,
                "label": r.label,
                "query": r.query,
                "mode": r.mode,
                "expected_source_id": r.expected_id,
                "rank": r.rank,
                "score": r.score,
                "hint": r.hint,
            })
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]

    if verbose or failed:
        for r in results:
            if verbose or not r.passed:
                print(r.to_line(verbose))

    total = len(results)
    n_pass = len(passed)
    n_fail = len(failed)
    status = "OK" if n_fail == 0 else "FAIL"
    print(f"\nSummary: {n_pass}/{total} PASS  {n_fail} FAIL  [{status}]")

    if failed and not verbose:
        print("\nFailed tests:")
        for r in failed:
            print(r.to_line(verbose=True))


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(
        description="Smoke-test wiki lookup quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true",
                       help="Test each index entry can find itself")
    group.add_argument("--cases", metavar="FILE",
                       help="JSONL file with structured test cases")
    p.add_argument("--top-n", type=int, default=5,
                   help="How many top results to check (default: 5)")
    p.add_argument("--key-limit", type=int, default=3,
                   help="Max lookup_keys per entry to test in self-test (default: 3)")
    p.add_argument("--index", help="Override index path (comma-separated for multiple)")
    p.add_argument("--scope", choices=["project", "aiws", "local", "all", "project,aiws"],
                   default=None,
                   help="Which registered indices to load (CR-2026-07-007 T6 / CAP-915-001: 'aiws' "
                        "+ combined 'project,aiws' added). Default depends on mode: --cases → "
                        "'project,aiws' (MIRRORS production lookup); --self-test → 'project' "
                        "(per-corpus quality gate — gate each index separately; merged-scope "
                        "competition is a lookup concern, not a per-corpus key gate). "
                        "'all' = project+aiws+local.")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Show all results, not just failures")
    p.add_argument("--only", metavar="IDS", default="",
                   help="Q2 (CR-AIWS-2026-07-001): comma-separated source_ids to ASSERT in "
                        "--self-test (still searches the full index). Use as a build/refresh gate "
                        "over only the new/changed metas. Empty = test every entry.")
    ns = p.parse_args()

    ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
    wiki_sources = ai_work / "wiki_sources"

    # CR-2026-07-007 T6: mode-dependent default scope (see --scope help).
    if ns.scope is None:
        ns.scope = "project" if ns.self_test else "project,aiws"

    if ns.index:
        index_paths = [Path(x).resolve() for x in ns.index.split(",")]
    else:
        index_paths = []
        if ns.scope in ("project", "project,aiws", "all"):
            index_paths.append(wiki_sources / "index.jsonl")
        if ns.scope in ("aiws", "project,aiws", "all"):
            aiws_idx = wiki_sources / "index.aiws.jsonl"
            if aiws_idx.exists():
                index_paths.append(aiws_idx)
        if ns.scope in ("local", "all"):
            local_idx = wiki_sources / "index.local.jsonl"
            if local_idx.exists():
                index_paths.append(local_idx)

    index_paths = [x for x in index_paths if x.exists()]
    if not index_paths:
        print("error: no wiki source index found. Run build_wiki_source_index.py first.",
              file=sys.stderr)
        return 2

    records: list[dict] = []
    for idx in index_paths:
        records.extend(read_jsonl(idx))

    if not records:
        print("warning: index is empty — nothing to test", file=sys.stderr)
        return 0

    # CR-2026-07-007: mirror production — aliases + query-time DF over the loaded set.
    global _ALIASES, _DF
    _ALIASES = load_query_aliases(wiki_sources / "profiles")
    _DF = compute_token_df(records)

    if ns.self_test:
        _only = {s.strip() for s in ns.only.split(",") if s.strip()} or None
        results = run_self_test(records, ns.top_n, ns.key_limit, only_ids=_only)
    else:
        results = run_cases(records, Path(ns.cases), ns.top_n)

    if not results:
        print("(no tests produced)")
        return 0

    print_report(results, ns.format, ns.verbose)

    failed = [r for r in results if not r.passed]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
