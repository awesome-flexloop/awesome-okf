---
type: Concept
title: "常设委员会与工作组"
description: "Jupyter通过常设委员会(永久)和工作组(临时)承担非软件工作，DEI、CoC、商标、社区建设等有正式制度地位。"
tags: [committees, working-groups, standing-committees, DEI, coc, non-software]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: committees
    resource: /references/committees-source.md
    title: "委员会与工作组信源"
---

## 非软件工作的组织

Jupyter 的工作不仅仅是写代码。行为准则事件响应、多元公平包容（DEI）、运营、法律、筹款、活动、社区建设、营销等非软件工作，通过**常设委员会（Standing Committees）**和**工作组（Working Groups）**承担。它们由 EC 委派授权，向 EC 报告并对 EC 负责。

## 共同点

常设委员会和工作组有以下共同特征：

- 都有明确定义的 **Council**（委员会），使用 Jupyter 决策指南做决策
- 遵循各自章程（charter）中规定的 Council 任命流程
- 由 EC 管理、向 EC 报告、对 EC 负责
- 拥有定义范围和目的的章程，在章程范围内自主决策
- 尽可能开放透明地运作
- 维护公开的 GitHub 仓库，公布 Council 成员、章程、公开会议、SSC 代表等信息

## 常设委员会（Standing Committees）

常设委员会是**永久性**机构，专注于对项目治理至关重要的领域。

### 特性
- **创建/解散门槛高**：需 EC + SSC **联合投票**决定
- **章程变更**：需 EC + SSC 联合批准
- **SSC 代表权**：始终在 SSC 拥有代表，由其 Council 选举产生
- **资源保障**：EC 负责确保持续获得适当资源

### 当前常设委员会

| 委员会 | 职责 |
|--------|------|
| **Diversity, Equity, and Inclusion (DEI)** | 领导战略举措改善项目领导层、贡献者和用户的多元公平包容；提出、执行和评估 DEI 举措；研究和收集 DEI 指标；倡导代表性不足群体的参与 |
| **Code of Conduct Incident Response** | 拥有和管理 CoC 举报与事件响应流程，对具体事件做出裁决 |
| **Conflict of Interest** | 确保领导层的联合利益和利益冲突得到适当披露、透明处理和诚信缓解 |
| **Community Advisory Panel** | 向 EC 提供可能超越活跃 Jupyter 社区的视角和人脉建议 |

### DEI 委员会运作细节
- 会议频率：至少每两周一次
- 参与要求：90天内缺席超过2/3例会可能被要求卸任
- 报告：每半年向 EC 提交报告（1月15日和7月15日前）
- 章程每年审查一次，实质性变更需 EC+SSC 批准

## 工作组（Working Groups）

工作组是为特定领域设立的**临时性/专题性**机构。

### 特性
- **创建/解散灵活**：由 EC **单独决定**，无需 SSC 批准
- **章程变更**：由 EC 批准
- **SSC 代表权**：默认无 SSC 代表；EC 可提名，经 SSC 批准后获得
- **更灵活**：适合特定任务或阶段性工作

### 当前工作组

| 工作组 | 职责 |
|--------|------|
| **Trademark and Branding** | 许可、保护和推广 Jupyter 商标及视觉/文字品牌 |
| **Jupyter Community Building (JCB)** | 发展、建设和连接全球 Jupyter 用户和贡献者社区；管理 Jupyter Community Workshops 和 JupyterCon |
| **Jupyter Media Strategy** | 确保 Jupyter 官方渠道的传播具有战略性，惠及项目 |
| **Jupyter Documentation** | 作为支持、帮助和咨询机构，协助改善 Jupyter 各子项目的文档各方面 |

### 社区建设工作组（JCB）重点
- 管理 Jupyter Community Workshops（2018年设立，小型面对面战略工作会议）
- 监督 JupyterCon 全球大会
- 与 EC 协作管理活动预算
- 与 DEI 委员会合作推动社区 DEI  efforts
- 每季度向 EC 报告，每年发布一篇博客

## 常设委员会 vs 工作组对比

| 维度 | 常设委员会 | 工作组 |
|------|-----------|--------|
| 存续期 | 永久 | 可由 EC 随时创建/解散 |
| 创建/解散 | EC+SSC联合投票 | EC单独决定 |
| 章程变更 | EC+SSC联合批准 | EC批准 |
| SSC代表 | 始终有 | 默认无，EC提名+SSC批准后可获得 |
| 资源保障 | EC必须保障 | 按需分配 |
| 典型领域 | DEI、CoC等核心治理 | 商标、社区、媒体、文档等专题 |

## 反常识要点

- **DEI 和 CoC 是"硬制度"不是"软倡议"**：在许多开源项目中，DEI 和行为准则被边缘化，但 Jupyter 将它们设为**常设委员会**——拥有与 SSC 的代表权、章程、正式流程和资源保障，制度地位与软件工程同等。
- **工作组不是"二等公民"**：虽然创建更灵活，但工作组在其章程范围内享有充分自主权，且可通过 EC 提名获得 SSC 代表权。
- **文档有专门工作组**：Jupyter 设立了 Documentation Working Group，这在开源项目中相对少见，反映了对文档质量的重视。

## 相关概念

- [三主体治理模型](/concepts/01-governance-model.md)
- [执行委员会（EC）](/concepts/03-executive-council.md)
- [软件指导委员会（SSC）](/concepts/04-software-steering-council.md)
- [行为准则与执行机制](/concepts/13-code-of-conduct.md)
- [决策制定流程](/concepts/09-decision-making.md)
