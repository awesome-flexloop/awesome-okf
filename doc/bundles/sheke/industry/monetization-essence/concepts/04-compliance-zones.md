---
type: Concept
title: "合规红绿区边界"
description: "agent 自动变现的禁行清单（红区）与可行边界（绿区）——反欺诈/反垃圾/ToS/隐私/金融/医疗/灵性七类红区禁行，内容/数据/工具/教育/沙箱五类绿区可行，灰区需显式确认"
tags: [合规, 变现, 红区, 信任, 风险]
generated: { by: "agent:seven-concepts-cmd", at: "2026-09-02" }
status: stable
stale_after: 2027-09-02
sources:
  - id: finance
    resource: "../../finance/index.md"
    title: "sheke/finance（防骗自查与合规底线）"
  - id: ai-security
    resource: "../../../jishu/ai/ai-security/index.md"
    title: "jishu/ai/ai-security（安全可信前提）"
  - id: adversarial
    resource: "../references/adversarial-review.md"
    title: "本束对抗审查记录"
---

# 合规红绿区边界

## 0. 依据

边界清单源自 [对抗审查](../references/adversarial-review.md)（SubTask 2.3）与公理体系中的 [A5 信任公理](00-axioms.md)（信任是变现的通用货币，透支信任即透支可持续性）。本清单是 [Agent 自动变现架构](02-agent-monetize-architecture.md) 治理层（`compliance/`）的制度化输入。

## 1. 🔴 红区（禁行，agent 不得执行）

| 类别 | 禁行行为 | 依据 |
|---|---|---|
| 反欺诈 | 虚假宣传、伪造数据、诱导点击、暗藏扣费 | A5 / 平台 ToS |
| 反垃圾 | 群发 spam、SEO 垃圾、刷量刷评 | A4（污染生态） |
| 金融 | 荐股、代客理财、无牌照证券建议 | 监管红线 |
| 医疗 | 疾病诊断、疗效承诺、替代就医 | 监管红线 |
| 灵性迷信 | 算卦/改名/开运/通灵收费 | 反迷信与产品定位 |
| 隐私 | 未授权采集/出售个人数据 | A5 / 数据合规 |
| 版权 | 抄袭、未授权转售受版权保护内容 | A5 / 平台 ToS |

## 2. 🟢 绿区（可行，agent 可自主执行）

| 类别 | 可行行为 |
|---|---|
| 内容服务 | 原创内容生成、知识解读、文档/代码/报告（有交付物、可退订） |
| 数据服务 | 公开数据聚合分析、可视化、按量计价（授权数据） |
| 工具服务 | API 封装、自动化脚本、MCP 服务器托管、自托管方案 |
| 教育咨询 | 课程、方法论训练、合规边界内的咨询（不含荐股/诊断） |
| 沙箱演示 | 虚拟货币闭环（参考平台 demo 模式） |

## 3. ⚖️ 灰区（需显式用户确认后启用）

**真实资金通道适配器**：须用户显式 `enable_real=true` + 合规确认（`confirmed_behaviors`），且参考平台本身**不含真实资金流转**。

## 4. 落地：平台 compliance 实现

在 [apps/agent-monetize](../../../../../apps/agent-monetize/README.md) 参考平台中：

- `compliance/policies.py`：红区 6 项禁行清单硬拦截（决策前过滤）；
- `adapters/`：真实适配器默认关闭，需显式配置 + 合规确认双条件；
- `tao/gates.py`：无为门/知止门提供行为层面的自我约束。

## 5. 相关概念

- [道家对齐框架](01-daojia-alignment.md)：价值观维度（合道判定）
- [变现本质公理体系](00-axioms.md)：信任公理的制度体现
- [Agent 自动变现架构](02-agent-monetize-architecture.md)：治理层承载
