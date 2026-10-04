# Reviewer evidence-packet A/B benchmark

`reviewer-ab-benchmark.mjs` compares two reviewer contexts for the same bounded task evidence:

- **A — full worker chat:** immutable packet, identical authorized artifact bytes, plus the seeded worker-chat transcript.
- **B — fresh evidence packet:** immutable packet and the same authorized artifact bytes; no worker chat or worker memory.

## Experimental contract

The harness has two semantic-defect fixtures and two correct controls, externally named only `case-01` through `case-04`. Ground truth (`expectedAccept` and case labels) stays in the fixture object and is not serialized into either reviewer prompt. Both prompts share exactly the same instruction, packet, artifact bytes, and common detection taxonomy; only lane A appends worker chat. A digest-mismatch fixture is separately labelled a **machine gate**: the actual `createReviewPacket()` builder must reject it before any reviewer call, so it is not mistaken for a semantic reviewer result. The shared `json-parser-suite` parses every artifact, deliberately showing that parser success does not prove the semantic requirement.

Each fixture is run in both lanes with the same declared model, tool, and budget. Replicates alternate A→B and B→A (ABBA); default live-ready requests use two repeats, or 16 reviewer calls for four fixtures × two lanes × two repeats. The output records false accepts/rejects, detected defects, resource observations (input/output tokens, cost, latency), and the number of reviews reporting a rationale request (`rationaleRequested` is a boolean, not a count of multiple tool calls). Machine-checkable failures are reported separately from semantic detection.

## Running it

Build first because the harness calls the real built `createReviewPacket()` API rather than recreating its schema:

```sh
pnpm build
node scripts/reviewer-ab-benchmark.mjs
```

The no-bridge command uses a deterministic synthetic oracle only to smoke-test fixture pairing and metrics. Its JSON has `"mode":"deterministic-smoke"`; it is **not** a model experiment and must not be reported as model performance.

For a real pilot, the host supplies a module without changing providers or credentials:

```sh
node scripts/reviewer-ab-benchmark.mjs --bridge /absolute/path/to/host-review-bridge.mjs --repeats 2
```

The bridge must export `async review({ prompt, lane, fixtureId, replicate, model, tool, budget })` and return `verdict: 'accept' | 'reject'`, optionally `detectedDefects`, `usage`, `cost`, `latencyMs`, and `rationaleRequested`. The harness neither configures a provider nor fabricates a live result. Omitted usage, cost, or latency remain `null` in metrics, rather than being converted to zero.

## External response scoring

`buildPairedRequestEnvelope()` returns immutable public requests:

```json
{"format":"durable-agent-reviewer-ab-requests/1","runId":"…","requestsSha256":"…","requests":[{"runId":"…","index":0,"requestSha256":"…","prompt":"…"}]}
```

Collect raw reviewer output without editing it, then score a complete collection using `scoreExternalResponses({ envelope, responses })`. The response file must be exactly:

```json
{"format":"durable-agent-reviewer-ab-responses/1","runId":"…","requestsSha256":"…","responses":[{"runId":"…","index":0,"requestSha256":"…","response":{"verdict":"reject","detectedDefects":["missing-required-risks"],"rationaleRequested":false}}]}
```

Missing, duplicate, stale, or hash-mismatched entries fail closed. `rawResponse` is retained verbatim in the scored output; truth is joined only internally for metrics. Score with `node scripts/reviewer-ab-benchmark.mjs --responses responses.json --repeats 2`; this emits `mode: externally-collected-live-model` only when an actual response file is supplied. The generic response-file CLI reports transport as `response-file-unspecified`; pilot-specific transport provenance must be recorded separately. Unknown model identity and unavailable tokens/cost stay `null`.

## Recorded result status

A bounded live pilot was collected after the frozen envelope below was dispatched. It is not evidence of a comparative improvement: both lanes had 8 runs, 0 false accepts, 0 false rejects, and detected all 4 seeded semantic defects (100%). No machine-gate case entered model review; the built packet API separately rejected its deliberately mismatched digest. Token usage, cost, and latency are `null` because native subagent telemetry was unavailable; the requested 1200-token budget was not tool-enforced. The synthetic one-line chat and two related defect fixtures limit any generalization, and concurrent paired completion order was unconstrained.

| Lane | Reviews | Defective / correct observations | False accepts | False rejects | Defects detected |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full synthetic worker chat | 8 | 4 / 4 | 0 | 0 | 4 / 4 |
| Fresh evidence packet | 8 | 4 / 4 | 0 | 0 | 4 / 4 |

- [Frozen requests](reviewer-ab-pilot-requests.json): `runId` `06b84d5ea523edca0feea67a3eb12ae304cdac2be17d4df91fc4ce31da7ddc1f`; envelope SHA-256 `da5a20bc8a746a50229dcaaed9f8cf1bb206b7e06ffea7d7b2e5f52778aab0e5`.
- [Verbatim response strings](reviewer-ab-live-responses.json), hash-bound by run, index, and per-request SHA-256.
- [Collection provenance and leaf IDs](reviewer-ab-pilot-provenance.json): all sixteen calls used the same native subagent default route; its exact model ID was not exposed. This collection record is not an authenticated provider receipt.

Reproduce scoring: `node scripts/reviewer-ab-benchmark.mjs --responses docs/reviewer-ab-live-responses.json --repeats 2`.

This pilot evaluates simplified `accept`/`reject` output with inline, identical evidence in both lanes; it does not run model tool calls through `runFreshReview`. The host adapter's versioned verdict, tool access, state revalidation and no-commit boundary are covered separately by deterministic integration/fault tests. Neither lane exercises long-running relationships or actual collusion; this result does not establish a causal improvement in defect detection or token savings.

The deterministic smoke remains solely a harness reproducibility check.
