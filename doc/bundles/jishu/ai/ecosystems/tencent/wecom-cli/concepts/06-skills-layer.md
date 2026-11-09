---
type: concept
title: Skills 层：业务域契约与可执行性检查
description: 说明内置 Skills 的目录组织、依赖声明、shared 前置检查及计数口径差异。
tags: [wecom, wecom-cli, skills]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# Skills 层：业务域契约与可执行性检查

`skills/` 实际有 15 个目录，覆盖日程、通讯录、微盘、文档、邮件、会议、消息、表格、智能页面、智能表格、PPTX、媒体与待办等域（F-137、F-150）。目录体量差异明显：calendar 与 email 各 8 个文件，sheet 20 个，pptx 84 个，smartpage 14 个，smartsheet 32 个（F-141–F-147）。

## 可执行性契约

除 `wecomcli-shared` 外，其余 14 个 `SKILL.md` 均声明 `metadata.requires.bins: ["wecom-cli"]`；shared 的 frontmatter 只有 name 和 description，并承担版本下限 1.2.1 与首次执行前置检查（F-138–F-140、F-153）。因此判断一个 Skill 能否执行，应先检查二进制依赖和 shared 前置，而不是只看目录是否存在。

## 计数差异

`AGENTS.md` 仍记为 14 个，`docs/skills.md` 与实际目录为 15 个；两组登记均保留在事实层（F-151、F-152）。该差异属于文档口径问题，不能据此否定 15 个目录的存在；更新导航时应以目录清单和 bins 覆盖率为核对依据（F-137、F-139、F-154）。
