---
type: Concept
title: "团队成员体系"
description: "Jupyter Server 团队的成员分类（活跃/不活跃）、SSC代表机制、成员数据结构和当前团队构成。"
tags: [team, membership, active, inactive, ssc, representative, contributors]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: team
    resource: /references/team-source.md
    title: "团队成员列表信源"
  - id: gen-contributors
    resource: /references/gen-contributors-source.md
    title: "贡献者表格生成脚本信源"
---

## 成员分类

Jupyter Server 团队成员分为两类：

### 活跃成员 (Active members)

活跃成员积极参与 Jupyter Server GitHub 组织中项目的开发、维护、规划和讨论。活跃成员拥有以下权利和义务：

| 权利/义务 | 说明 |
|-----------|------|
| 投票权 | 在投票情境中有投票权 |
| 计入选民 | 计入投票法定人数 |
| SSC代表选举权 | 可选举和被选举为 SSC 代表 |
| 提名权 | 可提名新团队成员 |
| 参与投票 | 应参与大多数团队投票（至少2/3） |
| 参与会议 | 应同步或异步地积极参与团队会议 |

### 不活跃成员 (Inactive members)

不活跃成员是曾为活跃成员但（暂时或永久）暂停积极参与的成员。不活跃成员：

- **不投票**，不计入投票法定人数
- 可随时通过**公开声明状态变更**来"重新激活"自己
- 重新激活**不需要其他成员提名**，自助完成

## 状态切换的灵活性

成员可以随时在活跃和不活跃之间自由切换。例如，即将休长假（>2周）的成员可以暂时转为不活跃，回来后立即重新激活，无需重新提名。这种设计降低了参与负担，避免贡献者因生活变动而永久离开。

状态变更通过更新 `contributors-jupyter-server.yaml` 文件的 Pull Request 公开声明。

## SSC（软件指导委员会）代表

Jupyter 的每个官方子项目有一名 Software Steering Council 代表，参与 Jupyter 全局层面的软件方向决策。

### 选举与任期

- 由 Jupyter Server **活跃团队成员**选举产生
- 任期为**一年**
- 代表信息记录在 `contributors-jupyter-server.yaml` 的 `ssc` 字段中

### 任期记录格式

SSC 任期以 `YYYY/MM-YYYY/MM` 格式记录：
- `2024/04-` 表示任期从2024年4月开始，**仍在任**（无结束日期）
- `2023/01-2024/04` 表示任期从2023年1月到2024年4月，已结束

### 现任与历任

| 代表 | GitHub | 任期 | 机构 |
|------|--------|------|------|
| Vidar Fauske（现任） | @vidartf | 2024/04- | J.P. Morgan Chase |
| Zach Sailer（前任） | @Zsailer | 2023/01-2024/04 | Apple |

## 成员数据管理

### YAML 数据源

成员信息存储在 `docs/team/contributors-jupyter-server.yaml` 中，每个成员条目包含：

```yaml
- name: "全名"
  handle: "@github用户名"
  affiliation: "所属机构"
  team: active  # 或 inactive
  last-check-in: "2025-02"  # 最后确认日期
  ssc:  # 可选，仅SSC代表有此字段
    - "2024/04-"
```

成员列表要求**按姓氏字母顺序**排列。

### 自动生成展示

团队成员页面的 HTML 表格不是手动编写的，而是在文档构建时由 [`gen_contributors.py`](../references/gen-contributors-source.md) 脚本自动生成：

1. 读取 YAML 数据
2. 从 GitHub 获取成员头像（`https://github.com/{handle}.png?size=200`）
3. 生成每行4人的 HTML 表格
4. 输出为 reStructuredText `.. raw:: html` 指令嵌入文档
5. 自动区分现任/历任 SSC 代表

## 当前团队构成（截至2025-02）

- **活跃成员**：10人，来自 QuantStack(3)、AWS(2)、Apple(2)、UMSI/2i2c(1)、J.P.Morgan(1)、Noteable(1)
- **不活跃成员**：6人
- 机构涵盖学术界（UMSI、Cal Poly）、云计算（AWS、Apple）、金融（J.P.Morgan）、开源组织（2i2c、QuantStack）、数据科学平台（Noteable）等

## 相关概念

- [成为团队成员](02-becoming-member.md)
- [决策机制](03-decision-making.md)
- [成员指南与PR合并原则](04-member-guide.md)
- [文档构建基础设施](06-doc-infrastructure.md)
