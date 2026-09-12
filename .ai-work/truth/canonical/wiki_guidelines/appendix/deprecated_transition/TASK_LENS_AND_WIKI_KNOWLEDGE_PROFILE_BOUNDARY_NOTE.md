# TASK_LENS_AND_WIKI_KNOWLEDGE_PROFILE_BOUNDARY_NOTE_v0_1

## Summary
This note clarifies the boundary between:
- Task Lens
- Wiki Knowledge Profile
- Wiki Meta / Index

## 1. Task Lens
Task Lens connects **task → knowledge**.

It helps AI determine:
- what kind of knowledge is needed
- where to start in the Knowledge Hub
- what keyword / alias / semantic direction to use
- how to expand once the first relevant knowledge item is found

Task Lens is primarily about:
- routing
- retrieval orientation
- knowledge targeting

Task Lens is **not** the profile that describes how knowledge itself should be built into the Wiki.

## 2. Wiki Knowledge Profile
Wiki Knowledge Profile is the profile AI uses mainly for:
- build
- update
- maintenance

It helps AI determine:
- what source artifacts this knowledge comes from
- what metadata/index/link structure should be created
- what this knowledge means
- what scope it covers
- what related knowledge it has
- when existing meta is usually sufficient
- when source/profile reference is still needed

Wiki Knowledge Profile is primarily about:
- knowledge build basis
- knowledge meaning / scope
- relation / sufficiency
- supplemental / reflection handling

It is **not** the task-to-knowledge routing layer. That remains the role of Task Lens.

## 3. Wiki Meta / Index
Wiki Meta / Index is the layer AI will consult most often during runtime.

It is the structured result of building knowledge into Wiki form:
- metadata
- aliases
- links
- traceability
- unresolved markers
- supplemental status/reflection markers

Runtime should mostly use:
- Task Lens
- Wiki Meta / Index

Profile reference is expected mainly when:
- building Wiki
- updating Wiki
- fixing weak meta
- diagnosing why a knowledge structure is insufficient

## 4. Anti-confusion notes
- Task Lens = helps AI know **what knowledge to find**
- Wiki Knowledge Profile = helps AI know **how that knowledge should be built and what it means**
- Wiki Meta / Index = helps AI **use the already-built knowledge in normal runtime**
