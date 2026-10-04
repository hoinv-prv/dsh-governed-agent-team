# GAT design collection — Agent Team reference hub

**Collected:** 2026-10-04 (Asia/Tokyo)  
**Status:** Formal design drafts and reference collection for review; no canonical promotion or activation grant.  
**Scope:** GAT design documents and relevant design changes from both local GAT missions in `wbs-runs` and all ten missions in `dsh-durable-agent/wbs-runs`.

## Purpose and authority

Đây là điểm vào cho agents khi làm task về Governed Agent Team. Bộ tài liệu giữ riêng current GAT behavior, Durable Agent service capability, bounded PoC conclusions và các proposal chưa triển khai. Không coi việc một mission hoàn tất là bằng chứng rằng GAT đã tích hợp capability đó.

**Source code is the source of truth for implemented behavior.** Khi source khác tài liệu cũ hoặc kết luận mission, formal design mô tả source hiện tại và ghi discrepancy. Acceptance receipts chỉ xác định phạm vi đã được chấp nhận; chúng không ghi đè source đang có. Snapshot trong `sources/` là bản tham khảo giữ nguyên bytes, không phải canonical home mới. Các link tương đối bên trong snapshot vẫn thuộc ngữ cảnh repo nguồn; dùng absolute source locator trong manifest khi cần dependency chưa được collect.

## Formal design set — start here

| Layer | Document | Content |
|---|---|---|
| Architecture design | [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md) | System context, packages, authority/storage ownership, lifecycle and architecture decisions |
| Basic design | [BASIC_DESIGN.md](BASIC_DESIGN.md) | Feature catalog, actors, inputs/outputs, flows and current-versus-target behavior |
| Detail design | [DETAIL_DESIGN.md](DETAIL_DESIGN.md) | Source-aligned data contracts, algorithms, ordering, errors and explicit target-only appendix |
| Detail → source mapping | [SOURCE_CODE_MAP.md](SOURCE_CODE_MAP.md) | 18 DD IDs mapped to implementation symbols/test files or explicit production gaps |

[Machine-readable source map](source-code-map.json) and [source baseline](source-baseline.json) bind 64 source/test files from GAT and the sibling Durable Agent checkout. Current source has pre-existing uncommitted changes; HEAD alone is insufficient. Source inspection and documentation checks do not constitute a product-suite PASS.

Architecture §5.1 and every DD entry include WHY, linked to original docs and clearly marked when inferred or unsupported. [Rationale input hashes](rationale-input-baseline.json) preserve that provenance.

The three earlier collection/synthesis pages below remain supporting references. Existing golden/frozen/proposal documents retain their original authority and status; they do not override the inspected implementation.

## Read by task

| Task | Đọc trước | Đọc tiếp khi cần |
|---|---|---|
| Team architecture, Session Enable, roster, tasks, mailbox | [GAT feature reference](../GAT_DESIGN_AND_FEATURE_REFERENCE.md) | [Golden design](../golden-reference/2026-09-12-governed-agent-team-v1-design.md), `packages/core`, `packages/tools` |
| Member initialization, attachment/binder, recovery | [Member binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md) | [Durable Agent integration design](DURABLE_AGENT_INTEGRATION.md) |
| Durable member context, selective memory, memory approval | [Durable Agent integration design](DURABLE_AGENT_INTEGRATION.md) | [Mission integration report](sources/gat-durable-agent-integration/integration-report.md), [memory protocol](sources/gat-durable-agent-integration/memory-protocol-qualification.md) |
| Durable task runner, checkpoint, terminal handoff | [Mission design deltas](MISSION_DESIGN_DELTAS.md) | P0/P1/P2 reports; BS1 projection; Agile compatibility memo |
| Install, compatibility, activation | [Installer refactor spec](../GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md) | [Extraction provenance](../source-extraction.md), `compatibility/`, `README.md` |
| Threat boundaries and proposed reference memory | [Threat model](../security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md) | [MCP memory proposal](../GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md), `docs/conformance/gat-conservative-mvp-v1.json` |
| WBS admission and procedural control plane | [Control-plane v39 snapshot](sources/gat-control-plane/control-plane-stabilization-design.v39.md) | Original mission and council review; advisory/inactive |

## Existing GAT design set

| Document | Intended use and boundary | Wiki source |
|---|---|---|
| `GAT_DESIGN_AND_FEATURE_REFERENCE.md` | Maintained behavior/navigation reference; last verified 2026-09-26. Its MiniMVP description predates the collected service mission. | `SRC-GAT-DESIGN-REFERENCE` |
| `GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` | Frozen proposed initialization/attachment seam. A frozen contract alone does not prove runtime binder adoption. | `SRC-GAT-MEMBER-BINDING-FREEZE` |
| `golden-reference/2026-09-12-governed-agent-team-v1-design.md` | Proposed V1 design baseline, compare with current source. | `SRC-GAT-V1-GOLDEN-DESIGN` |
| `GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md` | Inactive governed reference-memory proposal; distinct from Durable Agent member memory. | `SRC-GAT-MCP-MEMORY-PROPOSAL` |
| `security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md` | Pre-code security boundaries and conformance expectations. | `SRC-GAT-THREAT-MODEL` |
| `GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md` | Compatibility/source-drift/post-install verification design. | `SRC-GAT-INSTALLER-COMPATIBILITY` |
| Control-plane stabilization v39 | Procedural pre-charge admission proposal; no product activation. Original canonical home remains under `wbs-runs/multi-mission-web-ui/`. | `SRC-GAT-CONTROL-PLANE-DESIGN-V39` |

## Collection and freshness

[Collection manifest](collection-manifest.json) records source locators, exact SHA-256, byte counts, execution revisions/states, and final acceptance references. [Mission deltas](MISSION_DESIGN_DELTAS.md) covers every mission, including unexecuted planning work and cancelled/paused work.

A final report may retain pre-acceptance wording after approval. Read the matching `decisions.json` acceptance record and `execution.json` together. BS1 `CURRENT.md` still references v58/v59 while the collected execution ledger is revision 60; do not infer selected authority from that stale navigation page.

Refresh by rechecking source hashes and ledgers, then reviewing the affected summary. Keep old attempt evidence and accepted artifacts intact. Register the authored hub/design summaries as references; avoid registering duplicate snapshots as new canonical sources.

## Live wiki lookup entry points

```sh
python3 .ai-work/tooling/lookup_wiki_source.py --query 'GAT design collection'
python3 .ai-work/tooling/lookup_wiki_source.py --query 'GAT Durable Agent integration memory lifecycle'
python3 .ai-work/tooling/lookup_wiki_source.py --query 'GAT mission design deltas P0 P1 P2 BS1'
```

Registration is complete: 8 design/reference documents, 38 implementation/configuration files and 26 tests. Document relationships and document-to-code links are searchable in the wiki. See [registration report](WIKI_REGISTRATION.md).
