---
okf_version: "0.2"
type: Concept
title: "MXC 是什么：微软的 Agent 执行隔离容器"
description: "Microsoft Execution Containers 发布信息、双向限权机制、四种隔离后端、三种运行模式、政策五领域与官方支持产品名单"
tags: [微软, MXC, 执行隔离, 容器, Agent安全]
generated: { by: "blog-article-to-okf-bundle", at: "2026-10-10T09:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-10T09:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-mxc
    resource: /references/verification.md
  - id: blog
    resource: https://mp.weixin.qq.com/s/5bHJopj6-WOIBWeR68iaVA
---

# MXC 是什么：微软的 Agent 执行隔离容器

## 发布信息

**Microsoft Execution Containers（MXC）** 是微软推出的面向 AI Agent 的执行隔离工具，面向 Windows 11 正式开放。微软官方博客确认其 **generally available**（美西时间 2026-10-07；博文按北京时间记 10-08，时区口径差异，见核验 [verification.md](../references/verification.md) 勘误①）（F-001、F-026）。

MXC 旨在为 Agent 访问系统资源建立安全边界：开发者与企业可定义 Agent 能访问的**文件**和**网络**等资源，并在运行过程中强制执行这些规则（F-002）。它诞生于一个前提——微软在官方文章中指出，**传统沙箱并非专为 Agent 设计**，因为 Agent 的隔离需求可能随每一次提示词输入与工具调用而变化（F-006）。

## 双向限权机制

MXC 的关键设计是**政策边界独立于 Agent 之外**：开发者声明工作负载所需的资源（文件、网络目标），MXC 用合适的容器在运行时强制该边界；政策不受 Agent 工作负载控制，因此 Agent 或生成代码**无法自行授予自身额外访问权限**（F-030 政策五领域之一"Containment"，见下）。这正是"给 Agent 划定执行范围"——例如整理项目资料的 Agent 可被限制在指定目录内读取，避免接触无关数据（F-002）。

## 四种隔离后端

MXC 提供从轻到重的隔离谱系（F-003、F-028）：

| 后端 | 可用平台 | 适用场景 | 关键特性 |
|------|---------|---------|---------|
| **进程容器 Process** | Win11、macOS、Linux | 轻量负载（模型生成代码、工具执行） | AppContainer / Seatbelt / Bubblewrap |
| **会话容器 Session** | 仅 Win11 | 长运行 Agent / 需要桌面或更强隔离 | 独立账户 + 隔离桌面、剪贴板、UI、输入 |
| **WSL 容器 WSLc** | 仅 Win11 | Linux 优先的 Agent 工具链 | 通过 WSL 提供 Linux 执行环境 |
| **微型虚拟机 MicroVM** | Win11、Linux（实验） | 高风险负载 | 硬件虚拟化隔离、完整 Linux 兼容 |

此外 **Windows 365 云端执行环境** 已支持 MXC（GA），开发者可在 Cloud PC 上运行 Agent 并保持执行隔离（F-003、F-028）。

## 三种运行模式

| 模式 | 未授权访问 | 活动报告 | 用途 |
|------|-----------|---------|------|
| **Enforcement** | 拦截 | 无 | 生产环境按正式策略运行 |
| **Learning** | 拦截并记录 | 有（JSON） | 诊断失败、验证策略仅授权所需 |
| **Permissive** | 允许并记录 | 有 | 不强制策略下观察 Agent 活动 |

仅 Windows 的进程容器可产出 **agent activity report**，辅助撰写最小权限策略（F-029）。

## 政策五领域

MXC 策略覆盖五类资源（F-030）：

1. **Containment** — 隔离环境（进程/会话容器）
2. **Process** — 启动工作负载的命令、参数、工作目录、环境
3. **File system** — 可修改/只读/禁访问的位置
4. **Network** — 出入站连接（含是否可通过宿主 loopback）
5. **User interface** — 是否可访问/交互桌面与 UI 资源

## 官方支持产品名单

微软官方 MXC 博客公布的支持情况（F-027，**以官方名单为准**，博文"首批"名单不完整，见勘误②）：

- **已支持**：GitHub Copilot、OpenClaw、OpenAI Codex、Replit、LM Studio、Unsloth AI
- **已集成（NVIDIA 单列）**：OpenShell——补充了"凭证管理 + OCSF 审计（企业）"能力（博文未提）
- **即将支持**：Anthropic Claude Code、Box、Egnyte、Heidi Health、Hermes Agent（Nous Research）、Manus、Perplexity、Raycast、Simular

> **博文口径对照**：博文（F-004/F-014）称"首批支持 OpenAI Codex、GitHub Copilot、OpenClaw、英伟达 OpenShell，Replit 已支持，Claude Code/Manus/Perplexity 计划接入，Meta Muse 将推 Windows 原生应用"。该名单未含 LM Studio、Unsloth AI 与 Box/Egnyte/Heidi Health/Hermes Agent/Raycast/Simular，且 OpenShell 以"已集成"单列。本文按官方名单呈现。

## 小结

MXC 是把"Agent 安全控制"下沉到**操作系统执行层**的产品化尝试：用一轮可强制、可策略化的隔离边界，替代对模型"自觉遵守规则"的依赖。它不叠加在某个 Agent 产品上，而是作为跨 Agent 的执行基础设施存在（F-021，官方确认可跨 Windows/macOS/Linux 使用，Windows 集成更深入）。