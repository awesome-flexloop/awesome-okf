---
type: Reference
title: "AgentGit 核验报告"
description: "对博文中的产品定位、运行时支持、分享协作与敏感信息声明进行官方资料核验。"
tags: [AgentGit, 核验, 安全边界]
generated: { by: "reference_agent/trae", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: stable
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/A8Dm2FSpfNmqpUf4nqCcHg?from=industrynews&color_scheme=light#rd
  - id: official-home
    resource: https://agent-git.com/en/
  - id: official-quickstart
    resource: https://agent-git.com/docs/quickstart/
  - id: official-sharing
    resource: https://agent-git.com/docs/sharing/
  - id: official-remote-control
    resource: https://agent-git.com/docs/remote-control/
---

# AgentGit 核验报告

## 核验结论

| 核验项 | 结果 | 事实编号 |
|---|---|---|
| 产品定位为保存、分享和继续 Agent Session | 通过 | F-004、F-016 |
| 支持的 Agent 运行时 | 通过 | F-010、F-017 |
| 私有发布、只读链接和邀请协作 | 通过 | F-019、F-022 |
| Remote Control 的本机数据边界 | 通过 | F-020 |
| 发布历史 append-only、禁止 force-push | 通过 | F-023 |
| 跨运行时交接可能有损 | 通过 | F-024 |
| 推送前自动扫描 API Key 并脱敏 | ⚠️ 未证实且与官方安全提示不一致 | F-013、F-021 |

## 勘误

博文将安全机制描述为“推送前扫描疑似密钥、阻止上传并开始脱敏”。官方 FAQ 的可核验表述是：Session 可能在 prompt、工具调用和命令输出中包含密钥，分享前应按代码审查材料处理并主动审查、移除敏感内容。本文正文采用官方可证实口径，不把自动扫描或自动脱敏写成已确认功能。

## 已知边界

- 博文中的胸牌打印案例、效率体验和“Agent Knowledge Network”属于作者一手体验或设想，不等同于官方产品承诺。
- repo、branch、commit 与 Agent repo、Session、对话轮次的对应关系是文章类比，不能当作官方数据模型。
- 官方支持列表与跨运行时恢复能力会随版本变化，本文仅记录 2026-09-23 可见资料。
