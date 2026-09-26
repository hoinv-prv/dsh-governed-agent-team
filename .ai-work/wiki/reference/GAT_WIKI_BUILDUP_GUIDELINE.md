# GAT Wiki Build-up Guideline

## Purpose

Maintain a focused Knowledge Hub for Governed Agent Team design work. It supports Q&A plus design, implementation, and review tasks; it is a navigation surface, not project Truth or activation authority.

## Scope

Register the approved GAT design corpus only:

- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`
- `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
- `docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md`
- `wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v39.md`

Do not register source code, tests, WBS evidence, council snapshots, reports, or superseded control-plane design versions through this corpus rule.

## Authority and use

- Project Truth, executable source, tests, installation records, and approved Human decisions take precedence over this wiki.
- Proposals, the V1 golden design, the threat model, and control-plane v39 are not activation or execution authority.
- Use metadata to orient first; open the source artifact to verify substantive claims.

## Metadata and relations

- Use profile `gat_design_document` and PMP `PMP-DSH-GAT-DESIGN-DOCUMENT-V1`.
- Keep the generic metadata builder; do not create object nodes for this docs-only corpus.
- Add document-to-document relations only when a source-grounded relationship is clear and Human-approved.
- Rebuild `index.jsonl` and `relations.jsonl` after metadata or relation changes; never hand-edit either projection.

## Maintenance

For a changed registered document, use the wiki refresh flow. For a new GAT design document, propose its inclusion, source type, and relation candidates for Human review before registration. When a later `control-plane-stabilization-design.vNN.md` becomes the accepted final version, mark the previous registered version superseded and register the new one only after Human confirmation.

## Verification

- Run targeted lookup smoke tests using domain phrases and document titles.
- Run `python3 .ai-work/tooling/lint_wiki.py --sources-only`.
- Rebuild overview pages after material corpus changes.

## Bootstrap record

Built under `AIP-EXEC-020` on 2026-09-26. Initial corpus: six GAT design documents; four approved document relations; no object nodes.
