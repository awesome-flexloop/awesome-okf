---
okf_version: "0.2"
type: bundle
title: NVIDIA OpenShell 参考架构
description: 新闻稿与官方文档驱动的架构学习教程，覆盖软件信任边界、企业工作区、Sentry、部署验收与单案例治理模式，非实测操作教程
source: https://blogs.nvidia.cn/blog/openshell-reference-architecture/
sources:
  - id: article
    resource: https://blogs.nvidia.cn/blog/openshell-reference-architecture/
  - id: design
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/index.html
  - id: runtime
    resource: https://docs.nvidia.com/openshell/latest/about/architecture.html
  - id: sentry
    resource: https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/
tags: [OpenShell, Agent安全, 参考架构, Sentry, BlueField, 企业工作区]
generated: {by: "process:okf-wiki-author", at: "2026-10-27"}
status: draft
stale_after: 2026-12-31
---

# NVIDIA OpenShell 参考架构

**厂商自述边界：** Vera 最高 2 倍、Agent 容量最高提升 20% 和毫秒级隔离没有本次独立复现，不能作为通用性能或安全保证。[关键声明核验](references/verification.md)保留具体限定。

NVIDIA 在 2026 年 GTC 柏林发布的 OpenShell 参考架构，把 Agent 工作区、软件运行时、身份和凭证治理、独立硬件控制放进企业基础设施设计。本包依据中文新闻稿与 14 个已读官方页面组织，包含 66 条编号事实、6 篇概念/模式文档、3 条洞察和 1 个单案例 L1 候选模式（F-001、F-002）。[^article]

## 学习目标

- 区分 OpenShell 软件、企业参考架构与 Sentry 的职责和交付阶段。
- 解释 Supervisor、外围 fence、策略生效及凭证生命周期。
- 分开评估 VM 隔离、治理成熟度与硬件放置。
- 识别“组件已装”“策略已发布”“隔离成功”各自缺少的证据。

## 内容导航

| 页面 | 主线 |
|---|---|
| [范围与术语](concepts/00-scope-and-terms.md) | 三个实体、新闻可用性与排除范围 |
| [软件执行边界](concepts/01-runtime-trust-boundary.md) | Gateway / Sandbox / Supervisor、驱动与凭证 |
| [企业工作区](concepts/02-enterprise-workspace.md) | 七逻辑平面、Phase 0/I/II、策略与撤销 |
| [Sentry 硬件治理](concepts/03-sentry-hardware-governance.md) | Flow / Tower / Argus、身份、证据与时序 |
| [部署与验收](concepts/04-deployment-and-acceptance.md) | 五部署层级、隔离/控制/放置验收 |
| [洞察与迁移](concepts/05-insights-and-pattern.md) | 三条四元组洞察与边界先行治理 |
| [事实台账](references/article-source.md) | F-001～F-066 与规范信源 |
| [核验记录](references/verification.md) | 性能、阶段、伙伴与审查证据 |

适合了解 Agent 工具调用、基本 Linux/容器/VM 概念的工程读者。建议按上述顺序阅读，再用部署页对照现有系统；它不提供未经测试的一键部署命令。

## 已知边界

参考设计文档已开放，Sentry 技术博客写的是计划 2027 年初可用（F-002、F-011）。官方 `latest` 路径会变化，本包是 2026-10-27 阅读口径；新版本或到期时需重新核对。

全部信源来自 NVIDIA，伙伴集成阶段没有逐家独立确认，SAP 原文读取受阻。未部署软件或硬件，未实测性能、绕行、策略撤销、设备清理。原稿没有带版本和输入输出的完整实测流程，因此没有 `examples/` 空目录。

## 主题关联

[Microsoft MXC Agent containment](../../../practice/microsoft-mxc-agent-containment/index.md)侧重 Windows 执行容器与隔离，本包侧重跨平台参考设计和 OpenShell 可信授权边界。[AI Agent 基础](../ai-agent-fundamentals/index.md)提供 Agent 循环和工具调用的前置概念。

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
references/index
log
```

[^article]: [NVIDIA 中文新闻稿](https://blogs.nvidia.cn/blog/openshell-reference-architecture/)
