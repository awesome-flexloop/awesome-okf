---
type: Reference
title: "CodeBuddy Security 官网信源"
description: "CodeBuddy Security 安全审计平台官网（codebuddy.cn/security）的事实登记，记录六步安全闭环、对抗性 AI 审查、PoC 验证与 CVE 战绩。"
tags: [codebuddy, security, reference, official-site, sast, ai-security]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: security-official
    resource: https://www.codebuddy.cn/security/
    title: CodeBuddy Security 安全审计平台
---

# CodeBuddy Security 官网信源

本文件登记 CodeBuddy Security 安全审计平台官网（https://www.codebuddy.cn/security/）的公开事实，对应事实编号 F-061 ~ F-079。

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | security-official |
| URL | https://www.codebuddy.cn/security/ |
| 类型 | 产品官网 |
| 抓取日期 | 2026-08-23 |
| 对应事实 | F-061 ~ F-079 |
| 购买入口 | https://buy.cloud.tencent.com/cbsec |

## 产品定位

CodeBuddy Security 定位为新一代 AI 代码安全审计平台（F-061），基于腾讯云代码分析 TCA-Xcheck 与 AI 安全 Agent 多引擎驱动（F-062）。标语为"让每一行代码都值得信赖"（F-063）。

## 六步安全闭环

| 步骤 | 名称 | 核心能力 | 事实 ID |
|------|------|----------|---------|
| 1 | 威胁建模 | 攻击面识别 | F-064 |
| 2 | 漏洞发现 | Xcheck 静态分析 + AI 深度审计多引擎并扫 | F-065 |
| 3 | 对抗审查 | 先假设误报再证伪，多 Agent 独立论证消除幻觉 | F-066 |
| 4 | 动静验证 | 自动生成 PoC，隔离沙箱实际运行 | F-067 |
| 5 | 自动修复 | 针对性补丁，建议人工复核 | F-068 |
| 6 | 人工审核 | 最终人工确认 | F-069 |

## 核心特性

- **对抗性 AI 审查**（F-070）：以"先假设误报再证伪"的方式降低假阳性。
- **AI 规则反哺闭环**（F-071）：验证后漏洞沉淀为静态规则，持续增强检测能力。
- **自动化 PoC 验证**（F-072）：自动生成概念验证代码并在沙箱运行。
- **多引擎并扫**（F-073）：静态分析与 AI 审计多引擎并行扫描。
- **智能成本优化**（F-074）：多档模型 + 缓存，控制大规模审计成本。

## 战绩

| 指标 | 数值 | 事实 ID |
|------|------|---------|
| 发现漏洞总数 | 18 个 | F-075 |
| 严重/高危漏洞 | 14 个 | F-075 |
| CVE 编号 | 18 个 | F-076 |
| 覆盖开源项目 | 11 个 | F-077 |

覆盖的开源项目包括（F-077）：Suricata、Apache IoTDB、Model-Optimizer、mermaid、mapserver、FreeRDP、ImageMagick、Megatron-LM、LiteLLM、Langflow、Mastodon、React 等。

## 与传统 SAST 对比

| 维度 | 传统 SAST | CodeBuddy Security |
|------|-----------|-------------------|
| 召回率 | 较低 | 高召回率 |
| 误报率 | 较高 | 低误报率 |
| 未知漏洞 | 难以发现 | 可发现未知漏洞 |
| 规则维护成本 | 高 | 低（AI 规则反哺） |
| 验证方式 | 仅静态 | PoC 动态验证 |
| 修复建议 | 通用 | 针对性修复补丁 |

以上对比见 F-078。

## 购买

购买入口为 https://buy.cloud.tencent.com/cbsec（F-079）。

## 事实索引

| 事实 ID | 内容摘要 |
|---------|----------|
| F-061 | 新一代 AI 代码安全审计平台 |
| F-062 | 基于 TCA-Xcheck 与 AI 安全 Agent 多引擎驱动 |
| F-063 | 标语"让每一行代码都值得信赖" |
| F-064 | 威胁建模：攻击面识别 |
| F-065 | 漏洞发现：Xcheck + AI 深度审计多引擎并扫 |
| F-066 | 对抗审查：假设误报再证伪，多 Agent 独立论证 |
| F-067 | 动静验证：自动生成 PoC 隔离沙箱运行 |
| F-068 | 自动修复：针对性补丁，建议人工复核 |
| F-069 | 人工审核 |
| F-070 | 对抗性 AI 审查 |
| F-071 | AI 规则反哺闭环 |
| F-072 | 自动化 PoC 验证 |
| F-073 | 多引擎并扫 |
| F-074 | 智能成本优化（多档模型+缓存） |
| F-075 | 18 个漏洞，14 个严重/高危 |
| F-076 | 18 个 CVE 编号 |
| F-077 | 覆盖 11 个开源项目 |
| F-078 | 对比传统 SAST 六项优势 |
| F-079 | 购买入口 buy.cloud.tencent.com/cbsec |

## 相关概念

- [Security 安全审计](/concepts/05-security.md) — 六步闭环与对抗性审查详解
- [产品矩阵总览](/concepts/00-product-matrix.md) — Security 在矩阵中的定位
- [CodeBuddy IDE](/concepts/01-ide.md) — 代码审查能力与安全审计的协同
- [NPC 云端 AI 员工](/concepts/03-npc.md) — 自主修复构建与安全闭环的关联
