# Partitioned memory verification — attempt-gat-memory-002

WBS v22; charge 34; fresh STEP-08. The exact hash-pinned cleanup command exited 0 and removed the two unauthorized attempt-1 tests.

Exact verification command exited 1: eight tests, seven pass, one fail. `prepared/local crashes are invisible while anchored/published recover once` failed because `create()` checked `RECORD_EXISTS` before consulting the published idempotency result after anchored/published recovery. This is a real retry-order defect; no acceptance/review is claimed.

Hashes: source `9b45bfb6169e7e08996f9b0961332805a2c78c292010355d2a279145da08fc4d`; declarations `2d553bb727b3ed5b6f04805dea9e687356f137b06bbd4e7d3b9868a1139f7b79`; tests `d8dd8b876cabf731523a08c6ae38cf1b031d59ab04157498fa485d533d5841cd`, `e9f606267a28294d14cc65b5ac52015be55fa282dbeb52f76ad6d441e2f7cc7f`, `1a196a000edbf6203cc16574226126ced292cf96e94cda16daf6eef717821f7e`.
