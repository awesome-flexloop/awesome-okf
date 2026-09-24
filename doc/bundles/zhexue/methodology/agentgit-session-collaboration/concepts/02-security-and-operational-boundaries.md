---
type: Concept
title: "分享、安全与运行边界"
description: "梳理 AgentGit 的发布、只读分享、Remote Control 和敏感信息处理边界。"
tags: [AgentGit, Security, Remote Control, Sharing]
generated: { by: "reference_agent/trae", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: verification
    resource: /references/verification.md
  - id: sharing
    resource: https://agent-git.com/docs/sharing/
  - id: remote-control
    resource: https://agent-git.com/docs/remote-control/
---

# 分享、安全与运行边界

## 三种协作边界

- **私有发布**：用于团队持续协作，仓库可按官方文档设置为 private（F-019）。
- **只读分享**：通过链接查看 Session，不授予写权限（F-022）。
- **Remote Control**：浏览器连接运行在本机的 Agent，项目文件、运行时登录态和模型配置保留在设备侧（F-020）。

## 敏感信息处理

文章声称推送前会自动扫描并脱敏 API Key（F-013），但官方 FAQ 的可核验要求是：Session 可能在 prompt、工具调用和命令输出中包含敏感信息，分享前应按代码审查材料处理并主动移除（F-021）。因此，当前可靠的工程规则是：

1. 默认把完整 Session 当作敏感工程记录。
2. 发布前人工检查 prompt、工具调用、命令输出和日志。
3. 只在明确需要时开放只读链接或邀请权限。
4. 对跨运行时恢复做损失评估，不把“继续”理解为完全无损复制。

## 历史不可变性

官方 FAQ 说明已发布历史为 append-only，不支持 rebase 或 force-push（F-023）。这使 Session 历史更接近审计记录，也意味着错误信息不能依赖重写历史来消除，应通过新分支、新说明或撤回权限处理。
