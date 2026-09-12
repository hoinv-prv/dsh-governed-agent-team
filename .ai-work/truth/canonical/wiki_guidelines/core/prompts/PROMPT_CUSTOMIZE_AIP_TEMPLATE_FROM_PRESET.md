# PROMPT_CUSTOMIZE_AIP_TEMPLATE_FROM_PRESET_v0_1

## Purpose
Prompt mẫu để AI chọn preset AIP template rồi customize cho project cụ thể.

## Prompt
Dưới đây là:
1. task/use case cần hỗ trợ
2. preset AIP templates available
3. project profile / project constraints (nếu có)
4. wiki/knowledge expectations (nếu có)

Hãy chọn preset gần nhất và customize thành AIP template phù hợp cho project.

### Yêu cầu
1. Chỉ ra:
   - selected_preset_template
   - reason for selection
2. Customize template theo:
   - task intent
   - output type
   - project profile
   - knowledge loading hints
   - wiki dependency note
   - deliverable vs working distinction
   - wiki handoff behavior nếu relevant
3. Output rõ:
   - customization_summary
   - project_constraints_applied
   - knowledge_behavior_updates
   - wiki_handoff_behavior
   - completion_criteria_updates
   - project_reuse_note

### Rule rất quan trọng
- Không nhét full Task Lens logic vào template.
- Không tự gắn add-to-wiki step nếu project profile chưa support hoặc artifact không wiki-eligible.
- Nếu thiếu thông tin, giữ conservative và nêu rõ phần pending confirmation.
