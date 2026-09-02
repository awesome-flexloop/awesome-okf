---
type: Guide
title: 使用场景与落地实践
description: OKF 的三种典型使用场景（数据目录/Agent 知识库/运维 Runbook）、Agent 四层架构中的知识层定位、渐进式文档化五阶段、Git 工作流结合与 Bundle SemVer 版本管理建议。
tags: [okf, adoption, scenarios, agent-knowledge, runbook, git-workflow]
generated: { by: agent:learning-bundles-merge, at: 2026-09-02T00:00:00Z }
status: draft
stale_after: 2027-09-02
sources:
  - id: learning-okf-wiki
    resource: SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/（00-overview.md、03-usage-patterns.md）
    title: OKF Wiki 教程（learning 侧合并来源）
---

# 使用场景与落地实践

本篇收录 OKF 的场景化落地经验，与规范层面的[实践指南](practical-guidance.md)互补：实践指南回答「字段与格式怎么用」，本篇回答「什么场景用、如何组织、如何演进」。

> **版本早期警示**：OKF 目前处于 v0.2 Draft 早期阶段（2026 年 6 月首次发布），生态仍在快速演进。建议先小范围试点，不建议 All-in 重投入。

## 背景：为什么需要知识层格式

- **知识碎片化**：各平台格式不兼容、知识锁定在专有系统，跨平台迁移成本极高
- **传统 RAG 的局限**：仅做文本切块，缺乏来源、可信度、结构元数据，回答质量依赖检索运气
- **Agent 知识层缺失**：当前 Agent 栈（模型/工具连接/技能程序）缺少独立的知识层，知识散落在提示词、技能描述和向量库中
- **「HTML 时刻」类比**：HTML 让网页可互操作，OKF 想让知识可互操作——就像浏览器统一解析 HTML，Agent 可统一解析 OKF

## Agent 四层架构中的知识层

OKF 的自我定位是 Agent 四层架构中的**知识层（组织记忆）**：

```
模型层（智力）：LLM、多模态模型
    ↑
连接层（手脚）：工具调用、MCP 协议、外部系统连接
    ↑
程序层（招式）：可复用技能、工作流编排、脚本执行
    ↑
知识层（组织记忆）：OKF Bundle、概念知识、操作手册、演进日志
```

为什么知识层重要：

- **模型是租的，可以换**：不同 LLM 之间随时切换
- **框架是工具，可以换**：编排框架只是工具
- **技能是招式，可以学**：新技能可以快速开发、迭代
- **知识是自己的，是长期不被商品化的护城河**：业务概念、操作流程、决策逻辑、历史经验——这些才是真正沉淀下来、不可替代的核心资产

OKF 要做的，就是让这些核心资产有一个开放、可移植、可演进的载体。

## 三种典型使用场景

### 场景一：数据目录（Data Catalog）

**适用**：数据团队文档化表、指标、字段、Pipeline、BI 仪表盘。

- **目录结构**：按业务领域分目录（`sales/`、`product/`、`infra/`）
- **典型 type**：`BigQuery Table`、`Metric`、`dbt Model`、`Kafka Topic`、`Dashboard`
- **核心字段**：`resource` 指向实际资源链接，`stale_after` 标记新鲜度
- **适用边界**：专业数据目录工具（dbt docs/DataHub）的轻量补充或上层入口索引

示例（DAU 指标，约 18 行）：

```markdown
---
type: Metric
title: Daily Active Users (DAU)
description: 过去24小时内至少产生一次有效事件的去重用户数
owner: data-team@company.com
resource: https://bi.company.com/dashboards/dau
stale_after: 2026-08-08
tags: [growth, core-metric]
---

# DAU 日活用户

## 计算逻辑
`SELECT COUNT(DISTINCT user_id) FROM events WHERE event_type != 'test'`

## 相关
- [MAU](mau.md) | [events表](../product/events.md)
```

### 场景二：Agent 配套知识库（Agent Knowledge）

**适用**：为 AI Agent 提供工具文档、API 说明、领域知识、操作规范。

- **目录结构**：`tools/`、`concepts/`、`playbooks/`、`policies/`
- **典型 type**：`Tool`、`API Endpoint`、`Concept`、`Playbook`、`Policy`
- **核心字段**：`verified` 标记人类审核状态，`sources` 带来源引用
- **适用边界**：Agent 需要结构化、可机器读取的知识时，特别适合有明确 Schema 的工具类文档

示例（API 端点文档）：

```markdown
---
type: API Endpoint
title: 创建 Jira 工单
method: POST
endpoint: /rest/api/3/issue
verified:
  - { by: human:platform-team, at: 2026-07-20T00:00:00Z }
sources:
  - resource: https://developer.atlassian.com/
    title: Atlassian REST API 文档
tags: [jira, ticket]
---

## 参数
- `project.key` (string, required)：项目 Key
- `summary` (string, required)：工单标题
- `issuetype.name` (string, required)：`Bug` / `Task`
```

### 场景三：团队运维 Runbook（Playbook）

**适用**：SRE/运维团队记录故障处理流程、操作手册、应急响应。

- **目录结构**：按服务分目录（`services/payment-service/`）或按故障类型分（`incidents/`）
- **典型 type**：`Playbook`、`Runbook`、`On-Call Guide`、`Escalation Policy`
- **核心字段**：`owner` 标记负责人，扩展字段 `last_tested`（上次演练）、`severity`（故障等级）。步骤要**极度具体**
- **适用边界**：需要 SOP 落地为可执行、可演练、可追溯文档时，比 Wiki 平台更适合版本控制和 CI

示例（服务重启 Playbook）：

```markdown
---
type: Playbook
title: Payment Service 紧急重启
owner: sre-oncall@company.com
severity: critical
last_tested: 2026-07-15
tags: [payment, restart]
---

## 前置检查
1. 确认需重启（查 Grafana）
2. #incidents 频道通知

## 重启步骤
1. `kubectl ctx prod-use1`
2. `kubectl rollout restart deployment/payment-service`
3. `kubectl rollout status deployment/payment-service`
4. 等 2 分钟确认错误率恢复

## 回滚
`kubectl rollout undo deployment/payment-service`

## 升级
10 分钟未恢复 → 联系 sre-lead
```

## 渐进式文档化五阶段

OKF 支持增量式文档化，不需要「一次写完」：

| 阶段 | 状态 | 内容要求 | Agent 可用性 |
|------|------|----------|-------------|
| 0 | 占位 | index.md 列出，或只有 frontmatter 空文件 | 知道标题和 tags |
| 1 | 骨架 | 标题+主要章节标题，正文 TODO | 知道大概结构 |
| 2 | 核心内容 | 关键信息、定义、Schema | 可使用核心信息 |
| 3 | 完善 | 示例、引用、交叉链接、边界情况 | 高置信度使用 |
| 4 | 验证 | `verified` 人类审核 | 生产可依赖 |

**实践建议**：从阶段 0 开始占位，不要因追求完美而拖延开始。Agent 从阶段 2 开始就能使用部分信息——断链即特性（见[实践指南](practical-guidance.md)）正是为渐进式文档化而设计。

## 与 Git 工作流结合

OKF 纯文本特性天生适配 Git 工作流：

- **分支策略**：知识更新用 feature branch（如 `knowledge/add-payment-runbook`），提 PR，重要知识需至少 1 人 review
- **知识评审**：像代码评审一样审知识——准确性、完整性、链接有效性、格式规范
- **Git 能力复用**：`git diff` 看清变更、`git blame` 找作者、`git log` 看演进、`git revert` 回滚
- **CI 检查**：frontmatter 校验、断链检测、废弃字段检查、index 同步检查

注意 `log.md` 与 `git log` 的分工见[实践指南](practical-guidance.md)第 6 节。

## Bundle SemVer 版本管理建议

Bundle 整体可用 SemVer（MAJOR.MINOR.PATCH）标记演进：

| 层级 | 变更类型 | 示例 |
|------|----------|------|
| **MAJOR** | 不兼容结构变更 | 删除/重命名 Concept、改 type 含义、删必填字段 |
| **MINOR** | 向后兼容新增 | 新增 Concept、新增可选字段、补充内容 |
| **PATCH** | 小幅修复 | 错别字、链接修复、内容微调 |

版本记录在根 `index.md` 或 `log.md` 中。消费端可根据版本决定索引策略：PATCH 静默更新，MINOR 增量索引，MAJOR 全量重索引。规范层面的版本规则见[版本控制](versioning.md)。

## 相关概念

- [OKF 规范动机](motivation.md)
- [OKF 设计原则](design-principles.md)
- [OKF 实践指南](practical-guidance.md)
- [知识包结构](bundle-structure.md)
- [SaaS 指标知识包快速入门](../examples/saas-metrics-quickstart.md)
