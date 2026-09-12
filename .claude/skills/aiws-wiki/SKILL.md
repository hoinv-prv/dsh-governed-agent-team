---
name: aiws-wiki
description: >
  AIWS wiki domain — build, search, and maintain the project Knowledge Hub: Wiki Source Index,
  source metas, relations, mapping patterns (PMP), local knowledge, overview + curated pages.
  Verbs: lookup, register, register-batch, build-meta, refresh, refresh-meta, deregister,
  build-pattern, refresh-pattern, test-lookup, add-local-knowledge, build-overview, build-pages,
  bootstrap. TRIGGER: "tìm trong wiki / tra cứu spec / wiki có gì về X", "add/đăng ký tài liệu
  (toàn bộ thư mục) vào wiki", "register this file / bulk ingestion", "update/refresh/cập nhật
  wiki (meta) / source đã thay đổi", "gỡ/xóa source khỏi wiki / dọn orphan meta", "tạo/cập nhật
  mapping pattern / build PMP / format đã thay đổi", "test/kiểm tra wiki lookup", "thêm knowledge
  source local", "tạo wiki overview", "build trang wiki dự án / onboarding pages", "bootstrap
  wiki". Route NL → verb, then follow operations/<verb>.md — all HUMAN gates, promotion HARD
  STOPs, and multi-system --system rules survive unchanged; covers former aiws-wiki-* skills.
user-invocable: true
---

# SKILL: aiws-wiki

> **Full definition (common):** [.ai-work/procedural/skills/aiws-wiki/SKILL.md](../../../.ai-work/procedural/skills/aiws-wiki/SKILL.md)
> Read that router first, then read `operations/<verb>.md` for the chosen verb BEFORE executing.
