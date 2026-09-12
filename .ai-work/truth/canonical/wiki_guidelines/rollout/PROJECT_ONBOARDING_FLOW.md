# PROJECT_ONBOARDING_FLOW_v0_5_0.md

## Recommended onboarding flow for a new project/member

1. Read:
   - `README.md`
   - `core/guidelines/GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1.md`
2. Understand project profile basics:
   - artifact classes
   - deliverable vs working
   - wiki-eligible vs not
3. Walk through one real artifact understanding example
4. Walk through one canonical slot mapping example
5. Walk through one meta build/update example
6. Walk through one candidate / CR / governance example
7. Walk through one AIP customization example
8. Start using package on a pilot task
9. Verify lookup quality with a real task:
   - Run `/aiws-wiki test-lookup` (Mode C — natural language) with a sample task, e.g.:
     *"review tài liệu basic design"*
   - Skill parses the task → builds a multi-angle query plan → runs lookups → reports which sources were found
   - Pass condition: task-critical sources appear in top-5; score ≥ 15 for key queries
   - If gaps found → improve `lookup_keys` in the affected meta → rebuild index → re-test
   - Repeat until coverage is satisfactory before going live with AI-assisted tasks
