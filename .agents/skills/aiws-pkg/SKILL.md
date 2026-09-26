---
name: aiws-pkg
description: >
  AIWS package lifecycle: build a versioned self-contained install package from product/, install
  it into a new project, upgrade an existing installation, or quick-install straight from the dev
  working tree for a trial (dev-only, not shipped). VERBS: build / install / upgrade /
  quick-install. TRIGGER when user says: "tạo package AIWS", "đóng gói AIWS", "xuất package",
  "build install package", "release new AIWS version"; "setup project mới", "cài AIWS vào
  project", "khởi tạo project", "init new project", "install AI Work System"; "cập nhật AIWS",
  "nâng cấp AI Work System", "upgrade AIWS", "update aiws package", "install new version"; "cài
  thử AIWS vào dự án", "cài nhanh AIWS", "dùng thử AIWS trước khi release", "quick install AIWS",
  "install AIWS from source". Version is pinned in product/aiws_version.md; installs/upgrades are
  HUMAN-confirmed and temp-first; never touches Truth files or project runtime. Covers former
  aiws-pkg-* skills.
user-invocable: true
---

# SKILL: aiws-pkg

> **Full definition (common):** [.ai-work/procedural/skills/aiws-pkg/SKILL.md](../../../.ai-work/procedural/skills/aiws-pkg/SKILL.md)
> Read that router first, then read `operations/<verb>.md` for the chosen verb BEFORE executing.
