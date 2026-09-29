---
type: Concept
title: 共享治理与三个缺口
description: AAIF三层Agent栈（模型/MCP/A2A）、采纳数据（MCP下载量/服务器数/A2A组织数含勘误）、四大工作流（含勘误）、企业端跟进（AWS日期勘误/Google Gemini Enterprise）、协议层之上归因授权追索三缺口、买家五问、EU AI Act、三条战略判断
tags: [AAIF, 治理, 三层栈, 采纳数据, 归因, 授权, 追索, EU AI Act, 选型建议, Bedrock AgentCore]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-aiganhuo
    resource: https://mp.weixin.qq.com/s/rhw4xEncNH-t7xcwrj_Hfw
    title: 《A2A 与 MCP》（AI干活我偷懒，2026-08-26）
  - id: lf-press-aaif
    resource: https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation
    title: Linux Foundation AAIF 新闻稿
  - id: eu-ai-omnibus
    resource: https://digital-strategy.ec.europa.eu/en/news/ai-omnibus-enters-force
    title: 欧盟：AI Omnibus 生效
  - id: aws-agentcore-ga
    resource: https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available/
    title: AWS Bedrock AgentCore GA 公告
---

# 共享治理与三个缺口

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验结论见 [references/verification.md](../references/verification.md)。

## 1. AAIF 三层 Agent 栈

AAIF 把 Agent 栈抽象成三层（F-038）：

```
┌─────────────────────────────────────┐
│  A2A 层：Agent 协调                  │  ← Agent 间发现/委派/协商
├─────────────────────────────────────┤
│  MCP 层：工具集成                    │  ← 连接数据源/工具/工作流
├─────────────────────────────────────┤
│  模型层：推理规划                    │  ← LLM 推理与决策
└─────────────────────────────────────┘
```

一个生产环境的 Agent 栈通常同时需要 MCP 和 A2A 两层（F-039）：
- **MCP** 连公司内部工单系统、CRM、数据库
- **A2A** 在 Agent 到达能力边界时，把任务路由到其他供应商的专门 Agent

### 共享治理的意义

共享治理不会消除两套协议的区别，它**保护这种区别**（F-040）：
- 一套安全审查
- 一条合规轨道
- 一个解决重叠问题的统一场所

分散治理的风险是两协议各自演变、彼此偏离，逼每个框架做自定义桥接——这正是 AAIF 要避免的。

## 2. 采纳数据

### MCP 采纳

| 指标 | 博文数据 | 核验情况 |
|------|---------|---------|
| 月度 SDK 下载 | 超 1.1 亿（截至 2026-04） | ⚠️ 无法从权威来源直接证实；官方数据点为 9700 万（2025年底）和近 5 亿（2026年7月） |
| 公共服务器 | 超 1 万个 | ✅ 2025年12月官方已确认"more than 10,000" |

> ⚠️ **勘误（F-050）**：1.1 亿月下载量来自 neuralcoretech 博客（非权威来源），无官方来源直接证实。但增长曲线上合理（9700万→1.1亿→5亿），引用时应标注为第三方估算。

### A2A 采纳

| 指标 | 博文数据 | 核验情况 |
|------|---------|---------|
| 采纳组织 | 超 150 家 | ✅ AAIF 官方博客和 LF 一周年新闻稿确认 |

A2A 在 150+ 组织的生产环境中运行（F-041）。

## 3. AAIF 工作流与企业端跟进

### 四大工作流（F-042）

博文列出 AAIF 四大工作流持续推进到 2027 年：

| 工作流 | 目标 | 核验情况 |
|--------|------|---------|
| MCP v2 规范 | 流式支持与认证改进 | ⚠️ MCP 2026-07-28 已有重大更新（无状态核心/OAuth 2.1+OIDC），"v2"可能已部分交付 |
| A2A 治理规范 | 2026 Q3 完成 RFC | ⚠️ 第三方博客提及 Q3-Q4 2026，AAIF 官网未直接确认 |
| AGENTS.md v1.0 | 标准 1.0 版 | ⚠️ 散见第三方来源，无官方时间表 |
| 安全一致性认证 | 安全合规认证项目 | ⚠️ 同上 |

> ⚠️ **勘误（F-052）**：这四个"工作流"的明确框架主要来自 genee.tech 等第三方博客综合，AAIF 官网未直接列出"四大工作流至 2027 年"的官方路线图。各要素确实存在，但是否构成 AAIF 正式的工作组架构无法从官网直接确认。

### 企业端跟进（F-043）

| 厂商 | 动作 | 核验情况 |
|------|------|---------|
| **AWS** | Bedrock AgentCore 进入 GA | ❌ **日期有误**：AgentCore 2025-10-13 已 GA；2026年8月 GA 的是 Payments（8/18）和 Registry（8/6）子功能 |
| **Google** | Cloud Next 2026 发布 Gemini Enterprise Agent Platform，A2A 作协调层 | ✅ 2026年4月22-24日，TheNextWeb 等多家确认 |

> ❌ **硬性勘误（F-051）**：博文称"AWS Bedrock AgentCore 于 2026-08-21 进入 GA"是错误的。AWS 官方"What's New"明确标注 AgentCore GA 日期为 **2025 年 10 月 13 日**。2026 年 8 月 AWS 确实有 AgentCore 相关发布，但都是子功能 GA 而非平台整体 GA。

## 4. 协议层之上的三个缺口

博文核心观点：**标准合流把风险转移，而不是消除**（F-044）。协议覆盖"怎么通信"，但三个缺口协议层解决不了：

### 缺口一：归因（Attribution）

一条多 Agent 链没有明确的"作者"。日志记录了发生了什么，但日志不是问责模型——当多个 Agent 协作产出错误结果时，谁负责？

### 缺口二：授权（Authorization）

协议描述"可以请求什么"，政策才描述"被允许做什么"。A2A/MCP 定义了通信接口，但不定义权限边界——Agent A 能调用 Agent B 的哪些功能、在什么条件下、需要谁批准，这些是政策层的事。

### 缺口三：追索（Recourse）

补救是**合同性的**，不是技术性的。当 Agent 造成损失，技术协议无法自动赔偿——需要合同、保险、法律框架。

```
协议层（A2A + MCP）
  ↓ 标准化"怎么通信"
┌─────────────────────────────────┐
│  归因：谁负责？                   │
│  授权：被允许做什么？              │
│  追索：出事怎么补救？              │
└─────────────────────────────────┘
  ↑ 竞争差异化正在移到这里
```

## 5. 买家选型五问

博文建议买方下订单前问五个问题（F-045）：

1. **你的 Agent 无需人批就能做什么？**（决策边界）
2. **调用外部 Agent 时保留了什么记录？**（可审计性）
3. **重大错误输出，合同承诺什么？**（追索条款）
4. **如何版本化与测试？**（工程质量）
5. **合作伙伴 Agent 中途离线怎么办？**（容错兜底）

博文建议把评估清单从"支持哪些协议"改成这五项——协议支持将成为默认基线，而非差异化卖点。

## 6. 监管背景

EU AI Act Digital Omnibus 于 **2026-07-27** 生效（F-046），Annex III 高风险义务推迟到 **2027-12-02**。

> ✅ 经欧盟数字战略官网完全确认。官方称为"AI Omnibus"，博文称"EU AI Act Digital Omnibus"指向同一法案。

博文提醒：统一治理不等于更安全——广泛采用的协议一旦有漏洞，爆炸半径更大。

## 7. 三条战略判断

博文结尾给出三条可带走的判断（F-047）：

1. **互操作从差异化变成入场券**——"与一切集成"只是默认基线，不再是卖点
2. **廉价互操作对买家是好消息，对薄软件是坏消息**——仅靠集成做差异化的产品将被 commoditize
3. **持久优势是结果质量、问责清晰度，以及出事时是否有人信任你**——竞争移到协议之上

### 年底悬念（F-048）

> 如果 A2A 与 MCP 的采纳真正产出跨供应商 Agent，共享栈就是真的。如果只是各玩各的，那只是一次 branding。

历史类比：从 HTTP API 到 OAuth 再到 USB，每一轮标准化都让连接变便宜、让治理变贵。

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- A2A技术架构：[02-a2a-architecture.md](02-a2a-architecture.md)
