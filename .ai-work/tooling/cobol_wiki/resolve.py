"""Resolve a raw reference (a name written in source) to a wiki `source_id`.

This is where the largest measured defect class lived: on the reference corpus, of 37
missing `calls` edges, **37 were resolution failures and 0 were extraction failures** —
the extractor had found every call. The rules below each close a measured gap and are
kept together so the builder and the scoring harness share ONE implementation.

Rules, in the order they apply:

  1. system scope (HARD)  Only symbols in the CALLER's system are candidates. Two systems
                          in a migration corpus are independent; a cross-system edge is
                          meaningless. Not configurable.
  2. library hint         `.LIB` in `CALL PGM-x.LIB` names the OBJECT library the program
                          runs from, not the SOURCE library its meta lives in. Try it as a
                          source library, then fall back to a name-only lookup. Measured:
                          recall 99.3% -> 100.0%. The hint is unreliable across systems
                          too (a system A file may name a system B library), which is why
                          the system always comes from the caller, never the hint.
  3. type constraint      A role only lands on certain artifact kinds — `calls` never on a
                          form/definition. Separates a program and a screen sharing a name.
  4. exclude self         With 2+ candidates left, drop the caller itself: a CL routinely
                          invokes a COBOL program of the SAME name and both are programs,
                          so the type constraint cannot separate them. Portable — no
                          per-project priority list needed for this case.
  5. library priority     Project-specific last-resort tie-break.
  6. never guess          Still ambiguous, or nothing found -> return a Miss carrying the
                          reason, for the caller to record under `## Cautions`.

The candidate index deliberately includes metas WITHOUT an `artifact_locator` (external
stubs, object nodes): 295 `calls` edges were lost by indexing only file-backed metas.
Metas are read through `_common.meta_roots()` so every namespace is covered — reading
`wiki_sources/meta/` by hand is a defect that has shipped repeatedly.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from . import syscmd as syscmd_mod


@dataclass
class Candidate:
    """One indexed meta, reduced to what resolution needs."""

    source_id: str
    system: str
    library: str
    name: str
    file_type: str
    locator: str = ""
    #: Where the meta itself lives. An object node this builder wants to write may ALREADY
    #: exist under a different file name — `ACTLF.system_command.object.md` where the
    #: builder would write `ACTLF.syscmd.object.md`. Writing its own name then produces two
    #: files with one `source_id`, which the index reports as a duplicate. Measured: 109 of
    #: them on the first live refresh. Knowing the existing path is what prevents that.
    meta_path: str = ""


@dataclass
class Resolution:
    """Outcome of one resolution attempt."""

    source_id: str | None
    reason: str  # ok | ok_via_hint | ok_tiebreak | ambiguous | not_found
    candidates: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.source_id is not None


def _tooling_dir(project_root: Path) -> Path:
    return project_root / ".ai-work" / "tooling"


def _is_sentinel(locator: str) -> bool:
    """Object / stub metas carry a SENTINEL locator, not a path (e.g. `__OBJECT__`).

    Taking `Path(locator).stem` on one yields the sentinel itself, so an external stub
    would be indexed under the wrong name and never resolve. Those stubs are exactly the
    targets that account for the largest block of otherwise-unresolvable calls.
    """
    s = locator.strip()
    return not s or (s.startswith("__") and s.endswith("__"))


def _name_from_id(source_id: str, system: str, library: str = "") -> str:
    """Recover the object name from an id whose NAME may itself contain dashes.

    Splitting on the last dash is wrong for `SRC-FILE-HONSHA-LP-04` (name `LP-04`) and
    `SRC-FILE-HONSHA-MT-20-TRMASTER` (name `MT-20-TRMASTER`): a device-qualified file name
    keeps its dashes. Cut after the SYSTEM segment instead, which is the last part of the
    id that is structural rather than data.

    Cutting there is still not enough when the id ALSO carries a library segment:
    `SRC-COPY-SYS1-COPYLIB-CUSTREC` then yields `COPYLIB-CUSTREC`, and the copybook is
    indexed under a name no source will ever write. Measured cost: 173 `x:uses` edges
    silently unresolvable. So strip the declared library prefix too — but only when the
    meta actually declares one, never by guessing that the first segment is a library.
    """
    name = source_id
    if system:
        marker = f"-{system.upper()}-"
        idx = source_id.upper().find(marker)
        name = source_id[idx + len(marker):] if idx >= 0 else source_id.rsplit("-", 1)[-1]
    else:
        name = source_id.rsplit("-", 1)[-1]
    if library:
        prefix = f"{library.upper()}-"
        if name.upper().startswith(prefix):
            name = name[len(prefix):]
    return name.upper()


def _name_of(meta: dict, locator: str, source_id: str) -> str:
    """Program name for indexing.

    Order matters and is counter-intuitive: the FILE name wins over `PROGRAM-ID`.
    A `CALL 'X'` resolves by object name, which tracks the file, and legacy sources do
    disagree with themselves — measured here: `PGM0251.CB` declares
    `PROGRAM-ID. PGM0250`. Preferring `program_id` indexed that file under its
    neighbour's name and made both unresolvable. `program_id` is therefore only the
    fallback for metas that have no file at all (external stubs, object nodes).
    """
    if not _is_sentinel(locator):
        return Path(locator).stem.upper()
    pid = str(meta.get("program_id") or "").strip()
    if pid:
        return pid.upper()
    return _name_from_id(
        source_id, str(meta.get("system") or ""), str(meta.get("library") or "")
    )


def load_candidates(project_root: Path) -> list[Candidate]:
    """Index every meta in every namespace (R6: via `_common.meta_roots`)."""
    tooling = _tooling_dir(project_root)
    if str(tooling) not in sys.path:
        sys.path.insert(0, str(tooling.resolve()))
    from _common import meta_roots, parse_frontmatter, read_text  # type: ignore

    out: list[Candidate] = []
    for root in meta_roots(project_root / ".ai-work"):
        for path in root.rglob("*.md"):
            if path.name.endswith(".refresh.md"):
                continue
            try:
                meta, _ = parse_frontmatter(read_text(path))
            except Exception:  # noqa: BLE001 - a malformed meta must not abort indexing
                continue
            if not meta:
                continue
            sid = str(meta.get("source_id") or "")
            if not sid:
                continue
            locator = str(meta.get("artifact_locator") or "")
            name = _name_of(meta, locator, sid)
            out.append(
                Candidate(
                    source_id=sid,
                    system=str(meta.get("system") or "").lower(),
                    library=str(meta.get("library") or "").upper(),
                    name=name,
                    file_type=str(meta.get("file_type") or ""),
                    locator=locator,
                    meta_path=str(path),
                )
            )
    return out


class Resolver:
    """Name -> source_id, scoped and constrained per the rules in the module docstring."""

    def __init__(self, candidates: Iterable[Candidate], cfg) -> None:
        self.cfg = cfg
        self.by_name: dict[tuple[str, str], list[Candidate]] = defaultdict(list)
        self.by_lib: dict[tuple[str, str, str], list[Candidate]] = defaultdict(list)
        self.by_id: dict[str, Candidate] = {}
        for c in candidates:
            self.by_id[c.source_id] = c
            if not c.system:
                continue
            self.by_name[(c.system, c.name)].append(c)
            if c.library:
                self.by_lib[(c.system, c.library, c.name)].append(c)

    def add(self, candidate: Candidate) -> None:
        """Register a node created during this run.

        Synthetic file nodes are derived FROM unresolved references, so they do not exist
        when the index is first built. They must be registered before metas are emitted,
        or the very edges that caused them to be created still fail to resolve.
        """
        if candidate.source_id in self.by_id:
            return
        self.by_id[candidate.source_id] = candidate
        if not candidate.system:
            return
        self.by_name[(candidate.system, candidate.name)].append(candidate)
        if candidate.library:
            self.by_lib[(candidate.system, candidate.library, candidate.name)].append(candidate)

    def resolve(
        self,
        name: str,
        *,
        system: str,
        role: str = "calls",
        library_hint: str = "",
        caller_id: str = "",
        kind: str = "",
    ) -> Resolution:
        name = name.upper()
        # A command invocation is already IDENTIFIED by the extractor: the leading verb
        # matched the platform catalog. Name resolution would be wrong here in both
        # directions — the catalog is system-independent while resolution is system-scoped,
        # and a command whose name also names a program would resolve to the program.
        if kind and kind == syscmd_mod.SYSCMD_KIND:
            return Resolution(syscmd_mod.node_id(self.cfg, name), "ok_syscmd")
        system = system.lower()
        hint = (library_hint or "").upper()
        via_hint = False

        cands: list[Candidate] = []
        if hint:
            # Rule 2: try the hint as a SOURCE library. For `calls` it is usually the
            # OBJECT library and misses, so we fall through to name-only.
            cands = list(self.by_lib.get((system, hint, name), []))
            via_hint = bool(cands)
        by_name = self.by_name.get((system, name), [])  # Rule 1 keeps it in-system
        if not cands:
            cands = list(by_name)
        elif all(_is_sentinel(c.locator) for c in cands):
            # The hint matched only an object node. A copybook usually has BOTH a
            # definition object (`COPY x OF COPYLIB`) and a source file elsewhere; the
            # artifact is the more specific target and is what the reference records.
            # Widen so Rule 3b can prefer it — measured on 165 system B `x:uses` edges
            # that resolved to the COPYLIB object while the reference named the file.
            extra = [c for c in by_name if c.source_id not in {x.source_id for x in cands}]
            if any(not _is_sentinel(c.locator) for c in extra):
                cands = cands + extra

        if not cands:
            return Resolution(None, "not_found")

        # Rule 3 — a type constraint is a CONSTRAINT, so it applies at ANY candidate
        # count, not only as a tie-break. Measured: `COPY KANAZ9FM OF XMDLIB` strips to
        # the form name `KANAZ9`, which matched a same-named CL file; with the constraint
        # only firing on ties, that single wrong candidate was accepted.
        # A candidate whose file_type is UNKNOWN (object nodes, external stubs) is not
        # type-wrong, only type-unknown, so it stays eligible — those stubs are the sole
        # representation of their target and rejecting them would break `calls`.
        allowed = self.cfg.type_constraints.get(role)
        if allowed:
            kept = [c for c in cands if not c.file_type or c.file_type in allowed]
            if kept:
                cands = kept
            else:
                return Resolution(None, "type_mismatch", [c.source_id for c in cands])

        # Rule 3b — prefer a FILE-BACKED candidate over an object node when both exist for
        # the same name. A copybook commonly has both a source file and a definition
        # object node; the artifact is the more specific answer, and the reference corpus
        # points at it. Only applied when both kinds are present, so a stub-only target
        # (the usual case for external programs) is unaffected.
        if len(cands) > 1:
            file_backed = [c for c in cands if c.locator and not _is_sentinel(c.locator)]
            if file_backed and len(file_backed) < len(cands):
                cands = file_backed

        # Rule 4 — a source never points at itself. This applies at ANY candidate count,
        # not only as a tie-break: when the ONLY match is the caller, the honest answer is
        # that the reference resolves to nothing, not that the file calls itself. Measured
        # on the reference corpus: 0 self-edges in 43033, across all four roles and both
        # systems. Guarding this behind `len(cands) > 1` let a lone self-match through.
        if self.cfg.exclude_self and caller_id:
            cands = [c for c in cands if c.source_id != caller_id]
            if not cands:
                return Resolution(None, "not_found")

        if len(cands) == 1:
            return Resolution(cands[0].source_id, "ok_via_hint" if via_hint else "ok")

        if len(cands) > 1 and self.cfg.library_priority:  # Rule 5
            def rank(c: Candidate) -> int:
                try:
                    return self.cfg.library_priority.index(c.library)
                except ValueError:
                    return len(self.cfg.library_priority) + 1

            ordered = sorted(cands, key=rank)
            if rank(ordered[0]) < rank(ordered[1]):
                return Resolution(ordered[0].source_id, "ok_tiebreak")

        # Rule 6 — never guess.
        return Resolution(None, "ambiguous", [c.source_id for c in cands])
