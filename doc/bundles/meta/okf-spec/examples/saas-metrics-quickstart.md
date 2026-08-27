---
type: Example
title: SaaS 指标知识包快速入门
description: 来自 okf.md/quickstart 的"5分钟创建你的第一个 OKF 知识包"教程——SaaS 业务指标（MRR/Churn/CAC/LTV）完整示例。
tags: [okf, example, tutorial, quickstart, saas, metrics]
generated: { by: reference_agent/trae-glm, at: 2026-08-21T08:00:00Z }
status: draft
stale_after: 2027-06-30T00:00:00Z
sources:
  - id: quickstart
    resource: https://okf.md/quickstart
    title: Your First OKF Bundle in 5 Minutes
  - id: okf-md-skill
    resource: https://okf.md/skill
    title: Install the Agent Skill
---

# SaaS 指标知识包快速入门

本示例来自 [okf.md/quickstart](https://okf.md/quickstart) 官方教程"Your First OKF Bundle in 5 Minutes"，展示如何从零创建一个 SaaS 业务指标知识包。[^quickstart]

## 目标

创建一个知识包 `knowledge/metrics/`，包含四个核心 SaaS 指标概念：
- **MRR**（Monthly Recurring Revenue，月经常性收入）
- **Churn Rate**（客户流失率）
- **CAC**（Customer Acquisition Cost，客户获取成本）
- **LTV**（Lifetime Value，客户终身价值）

## 步骤 1：安装 Agent Skill

在项目根目录执行：

```bash
npx okf add-agent-skill
```

这会安装 OKF Agent Skill，让 AI 智能体"学会"OKF 规范，并提供 `validate.sh` 验证脚本。详见 [tooling-agent-skill.md](../concepts/tooling-agent-skill.md)。

## 步骤 2：创建目录结构

```
knowledge/metrics/
├── index.md
├── log.md
└── concepts/
    ├── mrr.md
    ├── churn.md
    ├── cac.md
    └── ltv.md
```

或者让智能体为你完成——直接对 AI 编程助手说：

> "Create a new knowledge bundle at `knowledge/metrics/` with concepts for MRR, Churn, CAC, and LTV. Include sources and machine-confirmed verification."

## 步骤 3：编写概念文件

以下是知识包中每个文件的完整内容。

### concepts/mrr.md

```markdown
---
type: Metric
title: Monthly Recurring Revenue (MRR)
description: Predictable recurring revenue normalized to a monthly value.
tags: [revenue, saas, core-metric]
generated:
  by: claude-code/okf-skill
  at: 2026-06-15T09:00:00Z
sources:
  - id: saas-metrics-guide
    title: SaaS Metrics Guide
    author: saas-capital.com
    resource: https://www.saas-capital.com/saas-metrics/
    last_modified: 2026-03-10T00:00:00Z
    usage_count:
      value: 12400
      last_modified: 2026-06-01T00:00:00Z
      usage_window:
        from: 2026-01-01T00:00:00Z
        to: 2026-06-01T00:00:00Z
verified:
  by: analyst@mycompany.com
  at: 2026-06-15T10:00:00Z
  notes: "Confirmed against finance team definitions."
status: stable
stale_after: 2027-06-15T00:00:00Z
---

# Monthly Recurring Revenue (MRR)

MRR is the predictable, recurring revenue a company earns from subscriptions, normalized to a monthly basis.

## Calculation

Sum the monthly subscription value for all active customers:

- Monthly plans: full value counts toward MRR
- Annual plans: divide by 12
- Quarterly plans: divide by 3

Exclude:

- One-time fees
- Setup charges
- Taxes

## Variants

- New MRR: revenue from new customers
- Expansion MRR: upsell/cross-sell to existing customers
- Churned MRR: lost from cancellations
- Net New MRR = New + Expansion - Churned

## Related

- [Churn Rate](./churn.md)
- [LTV](./ltv.md)

[^saas-metrics-guide]: [SaaS Metrics Guide](https://www.saas-capital.com/saas-metrics/)
```

### concepts/churn.md

```markdown
---
type: Metric
title: Customer Churn Rate
description: Percentage of customers who cancel subscriptions in a period.
tags: [retention, saas, core-metric]
generated:
  by: claude-code/okf-skill
  at: 2026-06-15T09:05:00Z
sources:
  - id: saas-metrics-guide
    title: SaaS Metrics Guide
    author: saas-capital.com
    resource: https://www.saas-capital.com/saas-metrics/
verified:
  by: analyst@mycompany.com
  at: 2026-06-15T10:00:00Z
status: stable
stale_after: 2027-06-15T00:00:00Z
---

# Customer Churn Rate

Churn rate measures the percentage of customers lost over a given time period.

## Formula

`Churn Rate = Customers lost in period / Customers at start of period`

Typically measured monthly or annually. For SaaS, good monthly churn is below 2%; annual below 5-7% is world-class.

## Related

- [MRR](./mrr.md)
- [LTV](./ltv.md)

[^saas-metrics-guide]: [SaaS Metrics Guide](https://www.saas-capital.com/saas-metrics/)
```

### concepts/cac.md

```markdown
---
type: Metric
title: Customer Acquisition Cost
description: Total sales and marketing cost to acquire one new customer.
tags: [growth, saas, unit-economics]
generated:
  by: claude-code/okf-skill
  at: 2026-06-15T09:10:00Z
sources:
  - id: saas-metrics-guide
    title: SaaS Metrics Guide
    author: saas-capital.com
    resource: https://www.saas-capital.com/saas-metrics/
verified:
  by: analyst@mycompany.com
  at: 2026-06-15T10:00:00Z
status: stable
stale_after: 2027-06-15T00:00:00Z
---

# Customer Acquisition Cost (CAC)

CAC is the total cost to acquire a single customer, including all sales and marketing expenses.

## Formula

`CAC = Total Sales & Marketing Cost / New Customers Acquired`

Include in cost:

- Ad spend
- Sales team salaries and commissions
- Marketing tools and content production
- Conference/event costs

## Benchmarks

- LTV:CAC ratio of 3:1 or higher is considered healthy
- CAC payback period under 12 months is good

## Related

- [LTV](./ltv.md)
- [MRR](./mrr.md)

[^saas-metrics-guide]: [SaaS Metrics Guide](https://www.saas-capital.com/saas-metrics/)
```

### concepts/ltv.md

```markdown
---
type: Metric
title: Customer Lifetime Value
description: Total revenue expected from a customer over their entire relationship.
tags: [unit-economics, saas, core-metric]
generated:
  by: claude-code/okf-skill
  at: 2026-06-15T09:15:00Z
sources:
  - id: saas-metrics-guide
    title: SaaS Metrics Guide
    author: saas-capital.com
    resource: https://www.saas-capital.com/saas-metrics/
verified:
  by: analyst@mycompany.com
  at: 2026-06-15T10:00:00Z
status: stable
stale_after: 2027-06-15T00:00:00Z
---

# Customer Lifetime Value (LTV)

LTV is the total revenue a business expects from a single customer over the duration of their relationship.

## Formula (Simplified)

`LTV = ARPA * Gross Margin % / Churn Rate`

Where ARPA = Average Revenue Per Account.

More precise models account for expansion revenue, discount rates, and customer cohorts.

## Key Relationships

- LTV:CAC > 3:1 is the classic SaaS health benchmark
- High churn destroys LTV regardless of acquisition efficiency

## Related

- [CAC](./cac.md)
- [Churn Rate](./churn.md)
- [MRR](./mrr.md)

[^saas-metrics-guide]: [SaaS Metrics Guide](https://www.saas-capital.com/saas-metrics/)
```

### index.md

```markdown
# SaaS Metrics

Core SaaS business metrics catalog.

## Metrics

- [MRR](./concepts/mrr.md) — Monthly Recurring Revenue: predictable recurring revenue
- [Churn Rate](./concepts/churn.md) — Customer Churn Rate: percentage who cancel
- [CAC](./concepts/cac.md) — Customer Acquisition Cost: cost to acquire one customer
- [LTV](./concepts/ltv.md) — Customer Lifetime Value: total expected revenue per customer
```

### log.md

```markdown
# Knowledge Log

## 2026-06-15

**Create** Initialized metrics knowledge bundle with MRR, Churn, CAC, and LTV definitions. Sources from SaaS Metrics Guide, verified by finance analyst.
```

## 步骤 4：验证

运行验证脚本：

```bash
.agents/skills/okf/validate.sh knowledge/metrics/
```

或者访问 [okf.md/validator](https://okf.md/validator) 上传目录进行可视化检查。

预期结果：✅ 0 errors（所有概念文件都有 `type` 字段，frontmatter 可解析，index.md 和 log.md 格式正确）。

## 步骤 5：添加新指标（进阶）

随着业务增长，添加新指标就像创建新文件一样简单。例如添加 Net Revenue Retention：

```markdown
---
type: Metric
title: Net Revenue Retention
description: Revenue retained from existing customers including expansion and churn.
tags: [retention, saas, expansion]
generated:
  by: data-team@mycompany.com
  at: 2026-07-01T14:00:00Z
status: draft
stale_after: 2026-10-01T00:00:00Z
---

# Net Revenue Retention (NRR)

...
```

然后：
1. 在 `index.md` 的 Metrics 列表中添加新条目
2. 在 `log.md` 中记录 `**Add** Net Revenue Retention metric.`
3. 运行 `validate.sh` 验证
4. 提交变更

## 关键要点

| 要点 | 说明 |
|---|---|
| `type` 是唯一必填字段 | 即使只有 `type: Metric` 也是合规的 |
| 断链不是错误 | 先写 `[NRR](./concepts/nrr.md)` 再创建文件是完全合法的 |
| sources 建立可信度 | 引用外部信源并记录作者、使用量等信号 |
| verified 建立信任层级 | `human-reviewed` > `machine-confirmed` > `unverified` |
| log.md ≠ git log | log.md 是面向人和智能体的高层 CHANGELOG |
| 逐步扩展 | 从最小可行知识包开始，逐步添加字段和内容 |

## 相关文档

- OKF 格式概览 - 了解 OKF 的基本概念
- [知识包目录结构](../concepts/bundle-structure.md) - 目录布局规范
- [概念文档](../concepts/concept-documents.md) - frontmatter 和正文规范
- [溯源与信源](../concepts/provenance-sources.md) - sources 字段详解
- [实践指南](../concepts/practical-guidance.md) - 更多使用建议
- [OKF Agent Skill](../concepts/tooling-agent-skill.md) - 智能体技能安装与使用
- [OKF Validator](../concepts/tooling-validator.md) - 在线验证工具

[^quickstart]: OKF Quickstart 教程，原文见 [okf.md/quickstart](https://okf.md/quickstart)。
