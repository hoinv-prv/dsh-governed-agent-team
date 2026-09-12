# PROJECT_ROLLOUT_GUIDELINE_v0_5_0

## 1. Goal
Hướng dẫn rollout package Wiki này vào một project đang hoặc sắp dùng AI Work System.

## 2. Rollout principles
- rollout theo objective thực tế của project, không ép triển khai tất cả cùng lúc
- bắt đầu từ artifact/task có ROI cao nhất cho BrSE
- ưu tiên các luồng dùng nhiều:
  - requirement understanding
  - BD / DD / testcase review support
  - traceability support
  - weekly reporting support
- giữ governance đủ nhẹ để project dùng được

## 3. Recommended rollout phases

### Phase 1 — Bootstrap
- align project profile
- identify artifact classes
- decide deliverable vs working
- decide wiki-eligible vs not
- onboard key BrSE/owner

### Phase 2 — Knowledge initialization
- artifact understanding
- canonical mapping
- first mapping pattern
- first meta build

### Phase 3 — Runtime adoption
- use Wiki-first runtime in selected tasks
- test notebook + Wiki Meta / Index usage
- observe insufficiency patterns

### Phase 4 — AIP alignment
- customize most-used AIP templates
- align add-to-wiki handoff behavior
- align candidate / CR / governance path

### Phase 5 — Stabilization
- refine meta/index
- refine mapping pattern
- refine AIP templates
- identify patterns worth commonization/promote-back

## 4. Suggested rollout owner roles
- BrSE owner / rollout lead
- wiki manager
- one or more pilot task users
- optional reviewer for project-specific customization quality

## 5. Success signs
- fewer repeated raw-document rereads
- faster relation lookup
- clearer BD/DD/testcase linkage
- clearer supplemental status understanding
- more stable AIP behavior
- less ad hoc prompting for repeated tasks
