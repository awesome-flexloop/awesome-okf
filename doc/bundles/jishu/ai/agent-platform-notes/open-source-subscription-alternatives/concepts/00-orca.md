---
type: Concept
title: "Orca：Agent 舰队与 worktree 隔离"
description: "用独立 git worktree 并行调度多个 CLI Agent，再以 diff 审查和择优合并形成 Agent Development Environment"
tags: [Orca, Agent, git-worktree, 并行]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-11-30
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: github, resource: "https://github.com/stablyai/orca" }
---

# Orca：Agent 舰队与 worktree 隔离

Orca 的核心不是模型，而是把多个 CLI 编程 Agent 组织成一支可比较的“舰队”：同一个任务扇出到多个独立 git worktree，完成后并排查看 diff，选择结果合并。[F-003][F-004]

## 机制

1. 调度层把同一 prompt 分发给多个 Agent。
2. 隔离层为每个 Agent 建立独立 worktree，避免文件互相覆盖。
3. 审查层比较 diff、批注和测试结果。
4. 合并层只保留被选择的方案。

Design Mode、SSH worktree、移动端通知和 CLI 是外围控制面，不是模型能力。[F-005] Orca 仍使用用户已有的 Claude、Codex 等订阅；并行五路通常意味着五路底层调用，开源软件本身不等于模型免费。[F-004]

## 适用边界

适合难以预判实现路径、可以并行探索且有明确验收测试的任务。不适合没有评审能力、无法承担多路 token/磁盘/构建成本，或需要单一长上下文连续性的任务。

**迁移洞察**：并行化解决的是探索吞吐，不替代人或测试决定“哪份 diff 正确”。
