#!/usr/bin/env python3
"""Run all MVP lints (AIP, workspaces, wiki) and aggregate results.

This is a convenience driver. It runs the individual linters in-process
and combines their findings into a single report.

v0.9.16: workspace lint includes Active Step Context and
Step Output / Decision Discussion Trace checks.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    LintReport, apply_lint_accept, emit_report, find_ai_work_root,
)

import lint_aip  # noqa: E402
import lint_wiki  # noqa: E402
import lint_workspace  # noqa: E402
from _common import parse_frontmatter, read_text  # noqa: E402
from _common import (  # noqa: E402  — CR-AIWS-2026-08-127 C4: Operating Memory store lint
    OPERATING_MEMORY_BODY_MAX, OPERATING_MEMORY_EVIDENCE_MAX, OPERATING_MEMORY_GROUPS,
    OPERATING_MEMORY_REF_UNSTABLE_RE, OPERATING_MEMORY_SENTENCE_RE, read_jsonl_lenient,
)
from _common import (  # noqa: E402  — CR-AIWS-2026-08-128 C6: project-profile schema lint
    PROJECT_PROFILE_SCHEMA, ProjectProfileUnreadable, project_profile_report, read_project_config,
)


WS_MARKERS = ("00_task_brief.md", ".current_step.json")
_AIP_KINDS = ("exec", "plans", "local")
ARCHIVE_NAMES = {"done", "archive"}  # CAP-015: done/ archive handling is a separate deferred CR


def _iter_aip_files(ai_work: Path):
    """Yield every real AIP file under aip/ — RECURSIVE over per-account folders
    (aip/<account_id>/<kind>/) + legacy flat (aip/<kind>/), excluding templates, readme, and
    done/ archives (CR-AIWS-2026-06-015 v2; done/ deferred per CAP-015)."""
    aip_root = ai_work / "aip"
    if not aip_root.is_dir():
        return
    for f in sorted(aip_root.rglob("*.md")):
        rel = f.relative_to(aip_root).parts
        if f.name.lower() == "readme.md" or "templates" in rel or any(p in ARCHIVE_NAMES for p in rel):
            continue
        yield f


def _aip_scope(f: Path, ai_work: Path) -> str:
    """Account namespace of an AIP path ('(legacy)' for flat aip/<kind>/)."""
    parts = f.relative_to(ai_work / "aip").parts
    if not parts or parts[0] in _AIP_KINDS:
        return "(legacy)"
    return parts[0]


def _is_workspace(d) -> bool:
    return any((d / m).exists() for m in WS_MARKERS)


def _discover_workspaces(ws_root) -> list:
    """Discover workspaces by marker (CR-015 v2): a marker-bearing dir is a workspace; a dir
    without a marker is a CONTAINER (per-account folder <account_id>/) → recurse ONE level.
    Archive containers (done/) are skipped — deferred per CAP-015."""
    found: list = []
    for entry in sorted(ws_root.iterdir()):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name in ARCHIVE_NAMES:
            continue
        if _is_workspace(entry):
            found.append(entry)
            continue
        for sub in sorted(entry.iterdir()):
            if (sub.is_dir() and not sub.name.startswith(".")
                    and sub.name not in ARCHIVE_NAMES and _is_workspace(sub)):
                found.append(sub)
    return found


def _check_duplicate_artifact_ids(ai_work: Path, report: LintReport) -> None:
    """Cross-file uniqueness check for AIP artifact_id, ACCOUNT-SCOPED (CR-015 v2).

    Recurses per-account folders + legacy flat (via _iter_aip_files). A bare AIP-<KIND>-NNN may
    legitimately recur across account folders (the folder is the namespace), so a collision is
    only flagged WITHIN the same (account, id) scope. Added after FND-030/031 caught a silent
    duplicate that slipped past per-file lint.

    ANCHOR — do not "simplify" the sort key (CR-AIWS-2026-08-021 T3). The finding is pinned at ONE
    path and `lint_accept` matches findings by EXACT path, so the anchor must not move between
    platforms. `sorted(list[Path])` compares `PurePath._str_normcase`, lowercased on Windows and
    case-sensitive on POSIX; one account scope spans several directories (`exec/`, `exec/archived/`,
    `plan*/`), so members of one (account, id) key can live in different directories and the two
    platforms then disagree about which comes first. Same fix and same reasoning as
    `_check_duplicate_cr_ids` (Lint_and_Tooling_Spec §21). Pinned by
    .ai-work/tests/test_cr021_wave.py case P3a.
    """
    aip_root = ai_work / "aip"
    by_key: dict[tuple[str, str], list[Path]] = {}
    for f in _iter_aip_files(ai_work):
        meta, _ = parse_frontmatter(read_text(f))
        aid = meta.get("artifact_id")
        if aid:
            by_key.setdefault((_aip_scope(f, ai_work), aid), []).append(f)

    for (scope, aid), paths in sorted(by_key.items()):
        if len(paths) > 1:
            ordered = sorted(paths, key=lambda p: p.relative_to(aip_root).as_posix())
            joined = ", ".join(str(p) for p in ordered)
            report.error(
                "duplicate_artifact_id",
                f"artifact_id '{aid}' used by {len(ordered)} files in account scope '{scope}': {joined}",
                path=str(ordered[0]),
            )


def _check_duplicate_cr_ids(by_id: dict[str, list[Path]], cr_root: Path,
                            report: LintReport) -> None:
    """Cross-file `cr_id` uniqueness (CR-AIWS-2026-07-071).

    Sibling of _check_duplicate_artifact_ids (FND-030/031): per-file lint can never see a
    collision that lives in ANOTHER file. Unlike AIP — where the account folder is a legitimate
    namespace and the key is (account, id) — a `cr_id` must be unique GLOBALLY, so there is no
    scope key. `by_id` comes from the caller's single scan pass (no second rglob); files with no
    `cr_id` (intake/, drafts/, README) never enter it, so they are skipped BY CONSTRUCTION rather
    than by a path carve-out — moving those dirs around cannot break the rule.

    ANCHOR — do not "simplify" the sort key. The report pins the finding at ONE path and
    `lint_accept` matches findings by EXACT path, so the anchor must not move between platforms.
    `sorted(list[Path])` compares `PurePath._str_normcase`, which is lowercased on Windows and
    case-sensitive on POSIX; for members living in different directories the two platforms
    therefore disagree about which comes first. A bare `sorted()` would let a grandfather accept
    placed on the Windows anchor silently stop matching on a POSIX CI box (accept degrades to
    `lint_accept_unused`, the ERROR fires on the sibling file, lint goes red downstream).
    Pinned by .ai-work/tests/test_duplicate_cr_id.py case D8.
    """
    for cid, paths in sorted(by_id.items()):
        if len(paths) < 2:
            continue
        ordered = sorted(paths, key=lambda p: p.relative_to(cr_root).as_posix())
        joined = ", ".join(str(p) for p in ordered)
        report.error(
            "duplicate_cr_id",
            f"cr_id '{cid}' used by {len(ordered)} files: {joined} — every `related_cr`/"
            f"`mapped_to_cr` pointing at '{cid}' is ambiguous",
            path=str(ordered[0]),
        )


def _lint_all_aips(ai_work: Path, report: LintReport) -> None:
    # AIP (recursive: per-account folders + legacy flat, excl. templates + done/) — CR-015 v2
    for f in _iter_aip_files(ai_work):
        lint_aip._lint_file(f, ai_work, report)
    # Cross-file AIP-ID uniqueness (FND-030 / FND-031 remediation)
    _check_duplicate_artifact_ids(ai_work, report)


_APPLY_OUTCOME_RE = re.compile(r"(?mi)^#{1,6}\s.*apply outcome")

# CR Spec §16 lifecycle + folder mapping (CR-AIWS-2026-08-021). `superseded`/`deferred` are
# terminal-not-applied states that were already in de-facto use; §16 was simply incomplete. All
# three terminal states share `rejected/` — the `status` field, not the folder, says which kind.
# One folder rather than one per state is deliberate: `lint_aip._CR_SUBDIRS` pins the folder set
# for CR-reference resolution, so a new folder would be a coupled change.
_CR_STATUS_VOCAB = frozenset({
    "draft", "proposed", "approved_for_ai_update", "applied",
    "rejected", "superseded", "deferred",
})
_CR_STATUS_FOLDER = {
    "draft": "drafts",
    "proposed": ".", "approved_for_ai_update": ".",
    "applied": "applied",
    "rejected": "rejected", "superseded": "rejected", "deferred": "rejected",
}


#: Mốc grandfather của rule lời-khai-test (CR-AIWS-2026-08-103 C1). Cùng lý lẽ với mốc bên dưới:
#: 9 ca nợ cũ (3 CR hứa test chưa bao giờ tạo + các CR trích tên đã đổi) sẽ đỏ một lượt, và một
#: rule đỏ hàng loạt ngay hôm đầu là một rule bị tắt vào hôm sau.
_TEST_CLAIM_SINCE = "2026-08-19"

#: Tên file test do CR nhắc tới. Cố ý KHÔNG neo vào `.ai-work/tests/`: chính phép đo hẹp đó đã cho ra
#: "nợ" không có thật khi soạn CR-103 (5/10 tên "thiếu" thực ra chỉ nằm ở thư mục khác).
_TEST_NAME_RE = re.compile(r"\btest_[a-z0-9_]+\.py\b")


def _repo_test_names(project_root: Path) -> set:
    """Mọi tên file `test_*.py` có thật trong repo, bất kể nằm ở thư mục nào."""
    out = set()
    for d in (project_root / ".ai-work", project_root / "product"):
        if d.is_dir():
            out |= {f.name for f in d.rglob("test_*.py")}
    return out


#: Mốc grandfather của rule upgrade-impact (CR-AIWS-2026-08-102 C5, DP-102-C = a). CR tạo TRƯỚC
#: ngày này không bị đòi khai field.
#:
#: Vì sao là NGÀY SAU ngày apply chứ không phải chính ngày đó: DP-102-C viết "created_at >= ngày
#: apply CR này", nhưng 11 CR (090..100) được apply CÙNG NGÀY và ĐÓNG TRƯỚC khi rule tồn tại —
#: lấy mốc = hôm đó thì rule đỏ ngay 11 ca cho một nghĩa vụ chưa hề tồn tại lúc chúng đóng. Một
#: rule đỏ hàng loạt ngay hôm đầu là một rule bị tắt vào hôm sau. Ý định của DP là "từ đây trở đi".
_UPGRADE_IMPACT_SINCE = "2026-08-19"

#: Marker cửa sổ ledger hiện tại, do release-checklist §5 đẩy mốc mỗi lần fold + reset.
_LEDGER_WINDOW_RE = re.compile(r"<!--\s*window_start:\s*(\d{4}-\d{2}-\d{2})\s*-->")


def _upgrade_ledger_window(ai_work: Path):
    """(window_start, nội dung ledger) — hoặc None nếu không có ledger/marker.

    Không có marker ⇒ KHÔNG đoán: rule `cr_upgrade_impact_missing_entry` im lặng. Sau mỗi lần fold
    ledger vào UPGRADE_NOTES, mọi CR của đợt vừa fold sẽ không còn trong file; nếu rule cứ đòi thì
    chúng đỏ oan vĩnh viễn. Marker là thứ phân biệt "chưa viết mục" với "đã fold rồi".
    """
    led = ai_work.parent / "product" / "UPGRADE_IMPACT_NOTE_next_release.md"
    if not led.is_file():
        return None
    try:
        text = read_text(led)
    except Exception:  # noqa: BLE001
        return None
    m = _LEDGER_WINDOW_RE.search(text)
    return (m.group(1), text) if m else None


def _lint_change_requests(ai_work: Path, report: LintReport) -> None:
    """CR-doc lint leg — ONE scan pass, two rules.

    1. `applied_without_apply_outcome` (WARNING, CR-AIWS-2026-08-004): a CR with
       `status: applied` must carry an `Apply Outcome` section (CR Spec §16 status integrity).
       A missing record is ledger debt, not a broken reference key.
    1b. `cr_upgrade_impact_unset` / `cr_upgrade_impact_missing_entry` (WARNING,
       CR-AIWS-2026-08-102): một CR `applied` phải TRẢ LỜI "adopter có thấy gì không?" ngay tại
       thời điểm apply, bằng front-matter `upgrade_impact: ledger | none` (+ `upgrade_impact_reason`
       khi `none`). Cổng cũ chỉ tồn tại ở `release-checklist`, chạy MỘT lần lúc cắt bản, nhiều ngày
       sau và thường bởi người khác — đo 2026-08-18: 5/10 CR kể từ build v1.2.0 trượt qua, không
       lệnh nào đỏ.
    2. `duplicate_cr_id` (ERROR, CR-AIWS-2026-07-071): cross-file `cr_id` uniqueness — see
       `_check_duplicate_cr_ids`. Collected here rather than in a second `rglob` pass because
       both rules want exactly the same file set under exactly the same filters.

    Files without a `cr_id` (intake/, drafts/, README) are skipped by construction, not by a
    path carve-out; a malformed frontmatter is another rule's finding. Installed projects (no
    product/ tree) skip silently."""
    cr_root = ai_work.parent / "product" / "change_requests"
    if not cr_root.is_dir():
        return
    by_id: dict[str, list[Path]] = {}
    for f in sorted(cr_root.rglob("*.md")):
        try:
            text = read_text(f)
            meta, _ = parse_frontmatter(text)
        except Exception:  # noqa: BLE001 — malformed CR is another rule's finding
            continue
        cr_id = str(meta.get("cr_id") or "").strip()
        if not cr_id:
            continue
        by_id.setdefault(cr_id, []).append(f)
        status = str(meta.get("status") or "").split("#")[0].strip()
        folder = f.relative_to(cr_root).parent.as_posix()

        # `cr_status_offvocab` (WARNING, CR-AIWS-2026-08-021 T2). An empty status is another
        # rule's finding — reporting it here too would just double up.
        if status and status not in _CR_STATUS_VOCAB:
            report.warn(
                "cr_status_offvocab",
                f"status '{status}' is not in the CR Spec §16 lifecycle "
                f"{sorted(_CR_STATUS_VOCAB)} — either use one of those, or extend §16 via a CR "
                f"(that is how `superseded`/`deferred` were added)",
                path=str(f),
            )

        # `cr_placement_mismatch` (ERROR, CR-AIWS-2026-08-021 T1). Folder is how humans and tools
        # locate a CR by lifecycle stage; a file in the wrong one is a broken locating convention.
        expected = _CR_STATUS_FOLDER.get(status)
        if expected is not None and expected != folder:
            here = folder if folder != "." else "the main change_requests/ folder"
            want = expected if expected != "." else "the main change_requests/ folder"
            report.error(
                "cr_placement_mismatch",
                f"status '{status}' but the file sits in {here} — CR Spec §16 puts it in {want}. "
                f"CAUTION before moving: if this CR is the report anchor of a grandfathered "
                f"`duplicate_cr_id` finding, moving it FLIPS the anchor and its `lint_accept` must "
                f"travel with it in the same change — a misplaced accept is silent (no "
                f"`lint_accept_unused` is emitted for a file that carries no finding)",
                path=str(f),
            )

        if status != "applied":
            continue
        if not _APPLY_OUTCOME_RE.search(text):
            report.warn(
                "applied_without_apply_outcome",
                "CR is `status: applied` but carries no `Apply Outcome` section — record the "
                "apply (CR Spec §16 status integrity, CR-AIWS-2026-08-004); if the record is "
                "legacy-by-design, add a lint_accept with a reason",
                path=str(f),
            )

        # --- upgrade-impact (CR-AIWS-2026-08-102 C5; ruling HUMAN: chỉ đọc front-matter) ---
        # Grandfather theo `created_at`: ~100 CR cũ đã fold vào release trước, bắt chúng khai
        # ngược vừa vô nghĩa vừa sai lịch sử — và một rule đỏ hàng loạt ngay hôm đầu thì hôm sau
        # bị tắt (DP-102-C = a).
        created = str(meta.get("created_at") or "").strip()
        if created < _UPGRADE_IMPACT_SINCE:
            continue
        impact = str(meta.get("upgrade_impact") or "").split("#")[0].strip()
        if not impact:
            report.warn(
                "cr_upgrade_impact_unset",
                "CR is `status: applied` but does not declare `upgrade_impact` — trả lời NGAY lúc "
                "apply: `ledger` (adopter thấy ⇒ thêm mục vào product/UPGRADE_IMPACT_NOTE_next_"
                "release.md) hoặc `none` + `upgrade_impact_reason`. Không chắc target có ship "
                "không thì dùng `_common.ships(path)` (CR-AIWS-2026-08-102)",
                path=str(f),
            )
        elif impact not in ("ledger", "none"):
            report.warn(
                "cr_upgrade_impact_unset",
                f"`upgrade_impact: {impact}` không thuộc từ vựng đóng ['ledger', 'none'] "
                f"(CR Spec §7, CR-AIWS-2026-08-102)",
                path=str(f),
            )
        elif impact == "none" and not str(meta.get("upgrade_impact_reason") or "").strip():
            report.warn(
                "cr_upgrade_impact_unset",
                "`upgrade_impact: none` nhưng thiếu `upgrade_impact_reason` — lý do là thứ khiến "
                "lần rà release sau không phải suy lại (CR Spec §7)",
                path=str(f),
            )
        elif impact == "ledger" and _upgrade_ledger_window(ai_work) is not None:
            win, ledger_text = _upgrade_ledger_window(ai_work)
            if created >= win and cr_id not in ledger_text:
                report.warn(
                    "cr_upgrade_impact_missing_entry",
                    f"`upgrade_impact: ledger` nhưng {cr_id} không xuất hiện trong "
                    f"product/UPGRADE_IMPACT_NOTE_next_release.md (cửa sổ mở từ {win}) — khai "
                    f"ledger mà quên viết mục thì adopter vẫn không được báo",
                    path=str(f),
                )

        # --- lời khai về test (CR-AIWS-2026-08-103 C1) — ĐỘC LẬP với chuỗi upgrade-impact ở trên ---
        # §11.8 buộc CR đổi hành vi tool phải liệt kê test đang pin hành vi cũ, kèm chính lệnh grep.
        # Không gì kiểm lời khai đó, và nó đã trượt: 1 CR khai tên KHÔNG tồn tại (điền bằng suy đoán
        # thay vì chạy lệnh), 3 CR applied hứa tạo test mà test chưa bao giờ tồn tại.
        # Quét CẢ FILE, không tách "claim" khỏi "trích dẫn": ranh giới đó là NGỮ NGHĨA nên mọi
        # heuristic cú pháp đều sai một chiều (DP-103-A = d). Trích dẫn hợp lệ dùng `lint_accept`.
        if created >= _TEST_CLAIM_SINCE:
            claimed = sorted(set(_TEST_NAME_RE.findall(text)))
            missing = [t for t in claimed if t not in _repo_test_names(ai_work.parent)]
            if missing:
                report.warn(
                    "cr_test_claim_unresolved",
                    f"CR `status: applied` nêu {len(missing)} tên file test KHÔNG tồn tại trong repo: "
                    f"{', '.join(missing)} — hoặc §11.8 được điền bằng suy đoán thay vì bằng output "
                    f"lệnh grep, hoặc CR hứa tạo test mà chưa tạo. Nếu đây là TRÍCH DẪN có chủ đích "
                    f"(CR đang nói VỀ một tên đã mất), thêm lint_accept kèm lý do "
                    f"(CR-AIWS-2026-08-103 C1)",
                    path=str(f),
                )

    # Cross-file cr_id uniqueness, over the same pass (CR-AIWS-2026-07-071)
    _check_duplicate_cr_ids(by_id, cr_root, report)


def _lint_wiki_all(ai_work: Path, report: LintReport) -> None:
    """Wiki + wiki-sources leg of the whole-tree gate.

    CR-AIWS-2026-07-034 T2: this leg NO LONGER owns a rule list — it calls the ONE driver in
    lint_wiki (`run_wiki_source_lints`), the same one `lint_wiki.main()` uses. Before, the leg
    re-implemented a hand-picked subset, so rules added to main() were invisible to this gate
    (skill_link_broken from CR-029; rename invariants; maintenance-log / build-routing /
    curated-citation / QA-store lints). A new rule now reaches BOTH surfaces by construction.
    """
    lint_wiki.run_wiki_source_lints(ai_work, report)


def _lint_all_workspaces(ai_work: Path, report: LintReport) -> None:
    # Workspaces — CR-015 v2: discover by marker so per-account containers
    # (.ai-work/workspaces/<account_id>/) are recursed into, not mis-linted as workspaces.
    ws_root = ai_work / "workspaces"
    if ws_root.is_dir():
        for ws_dir in _discover_workspaces(ws_root):
            sub = LintReport(target=str(ws_dir))
            lint_workspace.lint_workspace_dir(ws_dir, sub)
            report.findings.extend(sub.findings)


def _lint_agents(ai_work: Path, report: LintReport) -> None:
    # Agent lint (CR-AIWS-2026-06-049 T1): fold the AI Agents Pack lint into /aiws-lint when the
    # pack runtime subtree exists. No-op (zero added output) when .ai-work/agents/ is absent —
    # a pack-less project lints exactly as before. Runs the pack-internal lint_agents.py as an
    # isolated subprocess; a structural-defect exit (≠0) becomes one aggregate error. Degrades
    # gracefully — an invocation failure is reported, never crashes the aggregate.
    agents_lint = ai_work / "agents" / "tooling" / "lint_agents.py"
    if agents_lint.exists():
        import subprocess  # stdlib
        try:
            proc = subprocess.run(
                [sys.executable, str(agents_lint)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
            )
            out = ((proc.stdout or "") + (proc.stderr or "")).strip()
            # CR-AIWS-2026-08-051 C1 — WARN passthrough: lint_agents exits 0 on warn-only runs
            # (advisory contract AP-CR-31), which used to swallow its warnings entirely — pack
            # rules (shim binding / tiers / profiles / dead-ref) were invisible to the finalize
            # lint (CAP-1047-01: 9 dead_path_ref WARNs unseen). Fold each "[warning] ..." line
            # into the aggregate; the structural-defect exit contract below is UNCHANGED.
            for _line in out.splitlines():
                _ls = _line.strip()
                if _ls.startswith("[warning]"):
                    report.warn("agent_lint",
                                _ls[len("[warning]"):].strip(), path=str(agents_lint))
            if proc.returncode != 0:
                report.error(
                    "agent_lint",
                    "lint_agents.py reported structural defects:\n" + out,
                    path=str(agents_lint),
                )
        except Exception as e:  # never let agent lint break the aggregate
            report.error(
                "agent_lint_invoke",
                f"could not run lint_agents.py: {e}",
                path=str(agents_lint),
            )


def _check_dual_tree_drift(ai_work: Path, report: LintReport, strict: bool = False) -> None:
    """Dual-tree drift leg (CR-AIWS-2026-07-030 B): compare every product/** ↔ installed pair
    (pair map derives from quick_install PAYLOAD_MAP via check_dual_tree). WARN by default
    (DP-3). CR-AIWS-2026-08-053 (DP-1025-F): in an APPLY-CR context (`strict=True` — the scoped
    driver escalates with it when the task's AIP is an APPLY_CR instantiation) drift is an
    **ERROR**: Spec §13 declares byte-identity an apply-gate, and a WARN-only gate is exactly how
    3 template pairs shipped drifted (FND-08). Skips silently on installed projects."""
    try:
        import check_dual_tree
    except ImportError:
        return
    for code, msg, path in check_dual_tree.check(ai_work.parent):
        # Escalation is scoped to BYTE-DRIFT of an existing pair (`dual_tree_drift`) — the Spec §13
        # byte-identity gate (FND-08's failure shape). `dual_tree_only_in_one` stays WARN in both
        # modes: 124 pre-existing installed-only runtime findings (agents workspaces/.gitkeep) would
        # otherwise fail every apply-CR on debt unrelated to the CR being applied.
        # CR-AIWS-2026-08-080 C1: dual_tree_eol_drift joins the escalation. Same remedy, same gate
        # it violates — most CR guardrails require byte-identity, and  calls an EOL-only
        # difference a difference. WARN outside apply-CR so a work-in-progress tree is not blocked;
        # ERROR when a CR is being closed against that guardrail. Measured 0 such pairs at wiring
        # time (DP-080-B), so this escalation costs nothing today.
        if strict and code in ("dual_tree_drift", "dual_tree_eol_drift"):
            report.error(code, msg + "  [apply-CR context: byte-identity is an ERROR gate — Spec §13 / CR-AIWS-2026-08-053]", path=path)
        else:
            report.warn(code, msg, path=path)


def _lint_test_placement(ai_work: Path, report: LintReport) -> None:
    """`test_outside_test_dir` (WARNING, CR-AIWS-2026-08-103 C2).

    Một file tên `test_*.py` nằm ngoài `.ai-work/tests/` có HAI hệ quả, và cả hai đều im lặng:
    `run_battery` glob `tests_dir` nên KHÔNG BAO GIỜ chạy nó (một test không ai chạy là một test
    luôn "xanh"), và nếu nó nằm dưới `tooling/` thì nó còn ĐI VÀO bản cài của adopter.
    Ca thật: `test_object_named_consumer.py` sống ở `tooling/` cả hai cây từ 2026-06.
    """
    root = ai_work.parent
    tests_dir = ai_work / "tests"
    for d in (ai_work, root / "product"):
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("test_*.py")):
            if tests_dir in f.parents:
                continue
            rel = f.relative_to(root).as_posix()
            ships = " — và nó nằm dưới `tooling/` nên còn SHIP tới adopter" if "/tooling/" in rel else ""
            report.warn(
                "test_outside_test_dir",
                f"file test đặt ngoài `.ai-work/tests/` nên `run_battery` không bao giờ chạy nó{ships}"
                f" — chuyển vào `.ai-work/tests/`, hoặc xoá nếu đã chết (CR-AIWS-2026-08-103 C2)",
                path=str(f),
            )


def _lint_project_profile(ai_work: Path, report: LintReport) -> None:
    """The project config must be complete, and must be readable at all (CR-AIWS-2026-08-128 C6).

    Runs UNCONDITIONALLY in the whole-tree leg, not on a footprint condition. The reason differs from
    the sibling store lint next door: an incomplete profile does not degrade when someone edits it, it
    degrades *continuously* — it gates system scoping for every lookup, every meta write and every index
    build until it is fixed. A rule that only fires on the day the file is touched would be silent for
    exactly the period the damage is doing its work.

    Severity follows DP-1119-G:
      * `project_profile_unreadable` (ERROR) — the file exists but does not parse. Before C3 this read
        as a healthy single-system project, so every guard fed by it went quiet with nothing to see.
      * `project_profile_invariant`  (ERROR) — a cross-key rule is broken. "Complete" is keys AND
        invariants (HUMAN ruling OP-1119-02): `systems: []` under `multi_system: true` carries every
        required key and still disarms the check that the pair exists to enforce.
      * `project_profile_incomplete` (WARN)  — a required key is missing. Softer on purpose: an install
        that predates the schema is behind, not broken, and `project_profile.py refresh` fixes it.

    An ABSENT profile is silent. That is a legitimate single-system project, and saying otherwise would
    turn a default into a defect for every adopter who never needed the file.
    """
    profile = ai_work / "project_profile.yml"
    if not profile.is_file():
        return
    rel = profile.as_posix()
    try:
        cfg = read_project_config(ai_work)
    except ProjectProfileUnreadable as e:
        report.error("project_profile_unreadable",
                     f"the profile exists but could not be parsed ({e}) — every system-scoping guard "
                     f"reads this file, and an unparseable one used to look like a single-system "
                     f"project. Fix it by hand; no tool will rewrite a file it cannot read",
                     path=rel)
        return

    for code, msg, guard in project_profile_report(cfg):
        report.error("project_profile_invariant",
                     f"{code}: {msg} — protects: {guard}", path=rel)

    for key, spec in PROJECT_PROFILE_SCHEMA.items():
        required = spec.get("required", False)
        iff = spec.get("required_iff")
        if iff and cfg.get(iff):
            required = True
        if required and key not in cfg["_present"]:
            report.warn("project_profile_incomplete",
                        f"required key `{key}` is missing ({spec.get('doc', '')}) — "
                        f"run `py .ai-work/tooling/project_profile.py refresh --apply`",
                        path=rel)


def _lint_operating_memory(ai_work: Path, report: LintReport) -> None:
    """Keep the Operating Memory L2 store at its §5 shape (CR-AIWS-2026-08-127 C4).

    The store grew from 68 B to 1319 B per entry across triage waves with no command turning red —
    "fold" had become "append". Four WARN codes, all soft (no truncation, no auto-fix — the
    CR-2026-07-037 soft-budget shape): `operating_memory_body_long` (> OPERATING_MEMORY_BODY_MAX bytes,
    or > 3 sentences, or a ` · ` fold-join), `operating_memory_evidence_long`,
    `operating_memory_ref_unstable` (shape only — no path resolution, so no I/O), and
    `operating_memory_group_offvocab`. A missing store is silent: it is an advisory store and an
    adopter project may legitimately have none.
    """
    store = ai_work / "memory" / "entries.jsonl"
    if not store.is_file():
        return
    rel = store.as_posix()
    for i, r in enumerate(read_jsonl_lenient(store)):
        loc = f"entry {i}: {str(r.get('title', ''))[:60]}"
        body = " ".join(str(r.get("body", "")).split())
        n_bytes = len(body.encode("utf-8"))
        n_sent = len([s for s in OPERATING_MEMORY_SENTENCE_RE.split(body) if s.strip()])
        if n_bytes > OPERATING_MEMORY_BODY_MAX or n_sent > 3 or " · " in body:
            report.warn("operating_memory_body_long",
                        f"body {n_bytes} B / {n_sent} câu{' / fold-join · ' if ' · ' in body else ''} — "
                        f"§5 shape là 1–3 câu 'triệu chứng → cách đúng' ≤ {OPERATING_MEMORY_BODY_MAX} B; "
                        f"fold = viết lại, không nối (operating_memory.md §5)", path=rel, loc=loc)
        ev = str(r.get("evidence", "") or "")
        if len(ev.encode("utf-8")) > OPERATING_MEMORY_EVIDENCE_MAX:
            report.warn("operating_memory_evidence_long",
                        f"evidence {len(ev.encode('utf-8'))} B > {OPERATING_MEMORY_EVIDENCE_MAX} — "
                        f"evidence là MỘT lệnh/output/locator, không phải chỗ kể chuyện", path=rel, loc=loc)
        ref = str(r.get("ref", "") or "")
        if ref and OPERATING_MEMORY_REF_UNSTABLE_RE.search(ref):
            report.warn("operating_memory_ref_unstable",
                        f"ref {ref!r} có hình dạng không ổn định (workspace path / CAP id / temp / số dòng) — "
                        f"dùng doc#mục · module.symbol · CR/AIP id", path=rel, loc=loc)
        grp = str(r.get("group", "") or "").strip()
        if grp not in OPERATING_MEMORY_GROUPS:
            report.warn("operating_memory_group_offvocab",
                        f"group {grp!r} ∉ 7 nhóm operating_memory.md §3", path=rel, loc=loc)


def _lint_whole_tree(ai_work: Path, report: LintReport, dual_tree_strict: bool = False) -> None:
    """Whole-tree lint — every AIP, wiki entry/source/index, workspace, and (if present) the
    agents pack. This is the DEFAULT (`--scope all`) behavior and the canonical / CR-apply
    finalize lint. Order is load-bearing: keep it identical so default output stays byte-stable.
    `dual_tree_strict` (CR-AIWS-2026-08-053): apply-CR escalation passes True → drift = ERROR."""
    _lint_all_aips(ai_work, report)
    _lint_change_requests(ai_work, report)  # CR-AIWS-2026-08-004
    _lint_wiki_all(ai_work, report)
    _lint_all_workspaces(ai_work, report)
    _lint_project_profile(ai_work, report)   # CR-AIWS-2026-08-128 C6 — unconditional:
                                             # an incomplete profile degrades continuously
    _lint_operating_memory(ai_work, report)  # CR-AIWS-2026-08-127 C4
    _lint_agents(ai_work, report)
    _lint_test_placement(ai_work, report)  # CR-AIWS-2026-08-103 C2
    _check_dual_tree_drift(ai_work, report, strict=dual_tree_strict)  # CR-2026-07-030 B / CR-2026-08-053


# --- Scoped finalize-lint (CR-AIWS-2026-06-067 T4) -------------------------------------------

def _git_footprint(root: Path) -> set:
    """Whole-repo git dirt = git-changed paths (staged ∪ unstaged ∪ untracked) as POSIX paths
    relative to the repo root. NOTE (CR-AIWS-2026-07-040 T4): this is the REPO's dirt, not the
    task's footprint — the scoped driver intersects it with the task's declared scope
    (workspace ∪ AIP ∪ declared paths) before selection/escalation decisions. Multi-system
    (rule #12): these are PATHS only and the scoped driver performs NO cross-system lookup —
    no system bleed is possible here. Returns an empty set if git is unavailable (the caller
    still lints the mandatory aip+workspace legs)."""
    import subprocess  # stdlib
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=60,
        )
    except Exception:
        return set()
    if proc.returncode != 0:
        return set()
    paths: set = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        body = line[3:] if len(line) > 3 else line.strip()
        if " -> " in body:  # rename/copy: "orig -> new"
            for part in body.split(" -> ", 1):
                paths.add(part.strip().strip('"'))
        else:
            paths.add(body.strip().strip('"'))
    return {p.replace("\\", "/") for p in paths if p}


def _aip_is_apply_cr(aip_file: Path) -> bool:
    """True iff the AIP was instantiated from an apply-CR template (template_source) — a
    deterministic 'this task applies a CR' signal independent of the git footprint."""
    try:
        meta, _ = parse_frontmatter(read_text(aip_file))
    except Exception:
        return False
    return str(meta.get("template_source", "")).startswith("AIP_EXEC_APPLY_CR")


def _resolve_aip(ai_work: Path, aip_arg: str) -> Path | None:
    """Resolve --aip given a file PATH or an artifact_id (matched against frontmatter artifact_id)."""
    cand = Path(aip_arg)
    if cand.is_file():
        return cand.resolve()
    aip_root = ai_work / "aip"
    if aip_root.is_dir():
        for f in sorted(aip_root.rglob("*.md")):
            try:
                meta, _ = parse_frontmatter(read_text(f))
            except Exception:
                continue
            if str(meta.get("artifact_id", "")) == aip_arg:
                return f.resolve()
    return None


def _path_in_scope(p: str, scope: set) -> bool:
    """True iff dirty path p intersects a scope prefix (either direction, dir-prefix match)."""
    q = p.rstrip("/")
    for s in scope:
        t = s.rstrip("/")
        if q == t or q.startswith(t + "/") or t.startswith(q + "/"):
            return True
    return False


def _task_declared_paths(aip_file: "Path | None") -> set:
    """Best-effort path-like tokens declared by the AIP under `## Expected Outputs` and the
    `### In Scope` part of `## Execution Scope` (CR-AIWS-2026-07-040 T4, DP-040-1=A). A bullet's
    FIRST token counts iff it looks like a repo path (contains '/', no URL/placeholder). Prose
    bullets are skipped — an AIP that declares no paths falls back to whole-repo dirt."""
    if aip_file is None:
        return set()
    try:
        text = read_text(aip_file)
    except Exception:  # noqa: BLE001
        return set()
    import re as _re
    out: set = set()
    section = None
    in_scope_block = True
    for line in text.splitlines():
        h = _re.match(r"^(#{2,3})\s+(.*)$", line)
        if h:
            title = h.group(2).strip().lower()
            if h.group(1) == "##":
                section = ("outputs" if title.startswith("expected outputs")
                           else "scope" if title.startswith("execution scope") else None)
                in_scope_block = True
            elif section == "scope":
                in_scope_block = title.startswith("in scope")
            continue
        if section is None or (section == "scope" and not in_scope_block):
            continue
        s = line.strip()
        if not s.startswith("- "):
            continue
        tok = s[2:].strip().split()[0] if s[2:].strip() else ""
        tok = tok.strip("`").rstrip(":,;.").replace("\\", "/")
        if tok.startswith("./"):
            tok = tok[2:]
        if ("/" not in tok or tok.startswith(("http://", "https://", "<", "("))
                or not _re.fullmatch(r"[\w.\-/*]+", tok)):
            continue
        # glob-ish declarations ("dir/*.md") scope to their directory part
        if "*" in tok:
            tok = tok.split("*", 1)[0].rstrip("/")
            if "/" in tok:
                tok = tok.rsplit("/", 1)[0]
            else:
                continue
        out.add(tok)
    return out


def _lint_scope_task(root: Path, ai_work: Path, aip_arg: str, ws_arg: str,
                     report: LintReport, footprint_paths: "str | None" = None) -> None:
    """Deterministic scoped finalize-lint for a normal task-execution finalize (CR-067 T4;
    footprint scoping CR-AIWS-2026-07-040 T4):
      1. git_dirt = git-changed paths (staged ∪ unstaged ∪ untracked) — the whole repo's dirt.
      2. task scope = --footprint-paths override, else workspace ∪ AIP file ∪ paths the AIP
         declares (Expected Outputs / In Scope). footprint = git_dirt ∩ scope. An AIP that
         declares NO paths falls back to footprint = git_dirt (legacy behavior + printed note).
      3. lint the task AIP + Task Workspace                  -> both MANDATORY.
      4. footprint ∩ {.ai-work/wiki/, .ai-work/wiki_sources/} -> also lint wiki + index projection.
      5. footprint ∩ product/  OR  task applies a CR          -> ESCALATE to whole-tree (0 errors;
         the apply-CR signal is template_source-based and ALWAYS escalates, independent of scope).
    Escalation runs the whole tree, which already subsumes the mandatory aip+workspace legs, so
    escalate-vs-scope is exclusive (no duplicated findings). No AI judgement — selection lives here."""
    git_dirt = _git_footprint(root)
    aip_file = _resolve_aip(ai_work, aip_arg)
    if aip_file is None:
        report.error("scope_task_aip_unresolved",
                     f"--aip '{aip_arg}' did not resolve to a file or known artifact_id",
                     path=aip_arg)

    ws_dir = Path(ws_arg)
    if not ws_dir.is_absolute():
        ws_dir = root / ws_arg
    ws_dir = ws_dir.resolve()

    # CR-AIWS-2026-07-040 T4 (R3-09): footprint = git_dirt ∩ task scope, so an unrelated dirty
    # file elsewhere in the repo no longer contaminates this task's legs or blocks its finalize.
    def _rel(p: Path) -> str:
        try:
            return p.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return ""
    always = {r for r in (_rel(ws_dir), _rel(aip_file) if aip_file else "") if r}
    override = [t.strip().replace("\\", "/").rstrip("/") for t in (footprint_paths or "").split(",")
                if t.strip()]
    if override:
        scope = set(override) | always
        footprint = {p for p in git_dirt if _path_in_scope(p, scope)}
    else:
        declared = _task_declared_paths(aip_file)
        if declared:
            scope = declared | always
            footprint = {p for p in git_dirt if _path_in_scope(p, scope)}
            # CR-AIWS-2026-08-065: declared paths that match NOTHING dirty, while product/ IS
            # dirty, is the silent false-green: product/ drops out of the footprint, the run
            # never escalates, and it prints "OK — no findings" over an unlinted canonical
            # change. Classic cause: an AIP declaring a CR file whose id was not minted yet
            # (`CR-…-NNN-…`). WARN ONLY — no whole-dirt fallback, no auto-escalation, so an
            # unrelated dirty repo still cannot contaminate a scoped task (CR-040 T4 / R3-09).
            declared_hits = {p for p in footprint if not _path_in_scope(p, always)}
            product_dirt = sorted(p for p in git_dirt
                                  if p == "product" or p.startswith("product/"))
            if not declared_hits and product_dirt:
                report.warn(
                    "scope_task_footprint_unmatched",
                    "declared Expected Output / In Scope paths match no dirty file while "
                    f"product/ is dirty ({len(product_dirt)} path(s), e.g. {product_dirt[0]}) — "
                    "the task scope is probably under-matched (placeholder id like "
                    "'CR-…-NNN-…'?), so this run will NOT escalate to whole-tree. Re-run with "
                    "--footprint-paths <dir> (e.g. product/change_requests), or declare the "
                    "DIRECTORY in Expected Outputs",
                    path=str(aip_file))
        else:
            footprint = git_dirt
            # AIP-EXEC-1140 (CAP-1136-04): the old note named the remedy but not the one constraint
            # that makes it work, so an author who DID list paths — just not in first position — got
            # this same note and no way to tell why. Measured on AIP-EXEC-1136: two bullets carrying
            # valid repo paths after prose were skipped entirely.
            print("note: task declares no paths (Expected Outputs / In Scope) — falling back to "
                  "whole-repo git dirt as footprint. Only a bullet's FIRST token is read, so write "
                  "`- path/to/file.md — what it is`, not `- what it is — path/to/file.md`; or pass "
                  "--footprint-paths to scope your finalize lint", file=sys.stderr)

    escalate = (
        any(p == "product" or p.startswith("product/") for p in footprint)
        or (aip_file is not None and _aip_is_apply_cr(aip_file))
    )
    if escalate:
        # CR-AIWS-2026-08-053 (DP-1025-F): an APPLY-CR task escalates with dual-tree drift as
        # ERROR — byte-identity is the apply-gate Spec §13 declares, now enforced at gate level.
        _lint_whole_tree(ai_work, report,
                         dual_tree_strict=(aip_file is not None and _aip_is_apply_cr(aip_file)))
        return

    # MANDATORY legs: task AIP + Task Workspace.
    if aip_file is not None:
        lint_aip._lint_file(aip_file, ai_work, report)
    if _is_workspace(ws_dir):
        sub = LintReport(target=str(ws_dir))
        lint_workspace.lint_workspace_dir(ws_dir, sub)
        report.findings.extend(sub.findings)
    else:
        report.error("scope_task_workspace_missing",
                     f"--workspace '{ws_arg}' is not a Task Workspace (no marker found)",
                     path=str(ws_dir))

    # CONDITIONAL leg: wiki/index integrity iff the footprint touched wiki.
    if any(p.startswith(".ai-work/wiki/") or p.startswith(".ai-work/wiki_sources/")
           for p in footprint):
        _lint_wiki_all(ai_work, report)

    # CONDITIONAL leg (CR-AIWS-2026-08-051 C1): agents-pack lint iff the footprint touched the
    # installed pack. A product/agents footprint already escalated to whole-tree above (which
    # runs the agents leg), so this covers the .ai-work-side-only case (e.g. desk config edits).
    if any(p.startswith(".ai-work/agents/") for p in footprint):
        _lint_agents(ai_work, report)

    # CONDITIONAL leg (CR-AIWS-2026-08-127 C4, DP-127-D): Operating Memory store lint iff the footprint
    # touched the store — a rule that never runs where the store is written is not a rule (CR-077).
    if any(p.startswith(".ai-work/memory/") for p in footprint):
        _lint_operating_memory(ai_work, report)


def main() -> int:
    p = argparse.ArgumentParser(description="Run AIP + workspace + wiki lints")
    p.add_argument("--project-root")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--show-accepted", action="store_true",
                   help="list lint_accept-muted findings instead of just tallying them")
    p.add_argument("--scope", choices=["all", "task"], default="all",
                   help="all (default) = whole-tree / canonical / CR-apply finalize lint; "
                        "task = scoped finalize lint (mandatory AIP+Task-Workspace, conditional "
                        "wiki/index, auto-escalates to whole-tree on a product/ or CR-apply footprint)")
    p.add_argument("--workspace", help="Task Workspace to lint (required when --scope task)")
    p.add_argument("--aip", help="active AIP file path or artifact_id (required when --scope task)")
    p.add_argument("--footprint-paths",
                   help="comma-separated repo-relative paths that OVERRIDE the derived task scope "
                        "for --scope task (CR-AIWS-2026-07-040 T4); wins over Expected-Outputs "
                        "derivation — the workspace + AIP file are always in scope")
    ns = p.parse_args()

    root = Path(ns.project_root).resolve() if ns.project_root else find_ai_work_root(Path.cwd())
    ai_work = root / ".ai-work"
    aggregate = LintReport(target=str(ai_work))

    if ns.scope == "task":
        if not ns.workspace or not ns.aip:
            sys.stderr.write(
                "lint_all.py --scope task requires both --workspace <PATH> and --aip <PATH|ID>\n")
            return 2
        _lint_scope_task(root, ai_work, ns.aip, ns.workspace, aggregate,
                         footprint_paths=ns.footprint_paths)
    else:
        _lint_whole_tree(ai_work, aggregate)

    apply_lint_accept(aggregate, ai_work)
    return emit_report(aggregate, ns.format, ns.strict, ns.show_accepted)


if __name__ == "__main__":
    raise SystemExit(main())
