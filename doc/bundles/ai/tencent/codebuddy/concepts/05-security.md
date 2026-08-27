---
type: Concept
title: "CodeBuddy Security 安全审计"
description: "CodeBuddy Security 是基于 TCA-Xcheck 与 AI 安全 Agent 多引擎驱动的代码安全审计平台，通过威胁建模、对抗审查、PoC 动态验证与自动修复构成六步闭环，已获 18 个 CVE。"
tags: [codebuddy, security, sast, ai-security, poc, vulnerability, cve, tca-xcheck]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: security-official
    resource: /references/security.md
    title: CodeBuddy Security 安全审计平台
---

# CodeBuddy Security 安全审计

CodeBuddy Security 是 CodeBuddy 产品矩阵中的新一代 AI 代码安全审计平台，基于腾讯云代码分析 TCA-Xcheck 与 AI 安全 Agent 多引擎驱动（F-061, F-062），标语为"让每一行代码都值得信赖"（F-063）。它以对抗性 AI 审查和动态 PoC 验证为核心，重构了传统 SAST（静态应用安全测试）的工作方式。

## 产品定位

传统 SAST 工具依赖人工编写的静态规则，存在高误报率、难以发现未知漏洞、规则维护成本高等问题。CodeBuddy Security 将静态分析（Xcheck）与 AI 深度审计结合，并引入多 Agent 对抗论证和沙箱动态验证，旨在实现高召回率与低误报率的平衡（F-078）。

购买入口为 https://buy.cloud.tencent.com/cbsec（F-079）。

## 六步安全闭环

Security 的核心方法论是六步安全闭环（F-064 ~ F-069）：

### 第一步：威胁建模

识别代码的攻击面（F-064），确定潜在威胁入口与风险区域，为后续扫描提供方向。

### 第二步：漏洞发现

采用多引擎并行扫描（F-065）：

- **Xcheck 静态分析**：腾讯云代码分析的静态规则引擎
- **AI 深度审计**：AI 安全 Agent 进行深度代码审计

多引擎并扫（F-073）提升漏洞召回率。

### 第三步：对抗审查

这是 Security 区别于传统 SAST 的关键步骤（F-066）：

1. 先假设告警为**误报**
2. 再通过多 Agent 独立论证进行**证伪**
3. 消除 AI 幻觉导致的虚假告警

对抗性 AI 审查（F-070）通过"自我怀疑"机制降低误报率。

### 第四步：动静验证

自动生成 PoC（Proof of Concept，概念验证代码），在隔离沙箱中实际运行（F-067）。这一步从"看起来可疑"升级为"实际可利用"，是区分真实漏洞与误报的决定性环节。

### 第五步：自动修复

针对确认的漏洞生成针对性补丁（F-068），并建议人工复核。补丁是针对具体漏洞的，而非通用建议。

### 第六步：人工审核

最终由人工审核确认修复方案（F-069），形成人机协同的安全保障。

```
威胁建模 → 漏洞发现 → 对抗审查 → 动静验证 → 自动修复 → 人工审核
   │           │          │          │          │          │
 攻击面     Xcheck+AI   假设误报    PoC沙箱    针对性补丁   最终确认
 识别       多引擎并扫   多Agent证伪  实际运行   建议复核
```

## 核心特性

### AI 规则反哺闭环

验证后的漏洞沉淀为静态规则（F-071），使系统具备自增强能力。每发现一个新漏洞，后续扫描可自动检测同类模式，降低规则维护成本（F-078）。

### 智能成本优化

采用多档模型与缓存机制（F-074），在大规模代码库审计时控制 Token 消耗与成本。

## 战绩

CodeBuddy Security 的实战成果（F-075 ~ F-077）：

| 指标 | 数值 |
|------|------|
| 发现漏洞总数 | 18 个 |
| 严重/高危漏洞 | 14 个 |
| CVE 编号 | 18 个 |
| 覆盖开源项目 | 11 个 |

覆盖的开源项目包括：Suricata、Apache IoTDB、Model-Optimizer、mermaid、mapserver、FreeRDP、ImageMagick、Megatron-LM、LiteLLM、Langflow、Mastodon、React 等（F-077）。这些 CVE 编号证明该平台能发现人工审计遗漏的真实漏洞。

## 与传统 SAST 对比

| 维度 | 传统 SAST | CodeBuddy Security |
|------|-----------|-------------------|
| 召回率 | 较低 | 高召回率（多引擎并扫） |
| 误报率 | 较高 | 低误报率（对抗审查证伪） |
| 未知漏洞 | 依赖已知规则，难以发现 | AI 深度审计可发现未知漏洞 |
| 规则维护成本 | 高（人工编写维护） | 低（AI 规则反哺） |
| 验证方式 | 仅静态分析 | PoC 沙箱动态验证 |
| 修复建议 | 通用建议 | 针对性补丁 |

以上对比见 F-078。

## 在 CodeBuddy 生态中的位置

Security 与矩阵其他产品形成协同：

- 与 **IDE 代码审查**（F-012）协同：IDE 中的 `@workspace#Codebase` 代码审查可作为安全前置检查，Security 提供深度审计。
- 与 **NPC 自主修复**（F-047）协同：NPC 能自主修复构建报错，Security 能自动生成漏洞修复补丁，两者共同构成质量与安全闭环。
- 自动修复补丁建议人工复核（F-068），与 NPC 的"验收合入"（F-045）理念一致——AI 执行，人把关。

## 相关概念

- [产品矩阵总览](00-product-matrix.md) — Security 在矩阵中的定位
- [CodeBuddy IDE](01-ide.md) — 代码审查与安全审计的协同
- [NPC 云端 AI 员工](03-npc.md) — 自主修复与安全闭环的关联
- [CLI](02-cli.md) — MCP 服务器能力可被安全工具集成
- [IDE 工作流示例](../examples/ide-workflow.md) — 研发阶段安全检查参考
