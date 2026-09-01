---
type: Concept
title: "新子项目准入与孵化"
description: "新子项目可通过直接创建或外部并入两条路径加入Jupyter官方组织，准入标准包括活跃社区、软件工程质量、治理合规等，jupyter-incubator提供孵化通道。"
tags: [new-subprojects, incubation, incorporation, jupyter-incubator, graduation]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: subprojects
    resource: /references/subprojects-source.md
    title: "软件子项目信源"
---

## 两条新子项目路径

新子项目加入 Jupyter 官方组织有两条路径：

| 路径 | 适用场景 | 流程复杂度 |
|------|---------|-----------|
| **直接创建** | 现有子项目的贡献者为相关但可分离的代码创建新仓库 | 极简、非正式 |
| **外部项目并入** | 在 Jupyter 官方组织外已开发一段时间的开源项目申请加入 | 正式提案流程 |

```
新子项目申请
    │
    ├── 明显属于Jupyter现有范围？
    │       │
    │       └── 是 → 直接创建（路径1）
    │
    └── 外部项目/孵化项目毕业？
            │
            └── 是 → 并入流程（路径2）
```

## 准入标准

无论哪条路径，评估子项目是否适合成为官方 Jupyter 子项目时使用以下标准：

| 标准 | 说明 |
|------|------|
| **活跃开发者社区** | 提供可持续发展模式 |
| **活跃用户社区** | 证明项目有实际使用需求 |
| **扎实的软件工程** | 有文档和测试，使用适当技术（ReadTheDocs、CI等） |
| **持续增长发展** | 项目在积极演进 |
| **良好集成** | 与现有官方子项目能良好配合 |
| **治理合规** | 遵循 Jupyter 治理和贡献模型 |
| **明确范围** | 有清晰定义的项目边界 |
| **适当打包** | 使用 pip/conda/npm/docker 等适当技术分发 |

核心问题是：**社区和 SSC 是否广泛共识要以官方身份开发和维护该项目？**

总体原则：优先改善现有子项目，而非接纳竞争性子项目。

## 路径1：直接创建

当新子项目明显属于现有 Jupyter 范围和活动时（如现有子项目拆分出新的相关仓库），使用极简流程：

1. SSC 成员就创建子项目达成共识
2. 通知主 Jupyter 邮件列表
3. EC 批准将新项目添加到子项目列表的 PR

流程即完成。参考案例：[jupyter-book 并入 PR](https://github.com/jupyter/governance/pull/229)

## 路径2：外部项目并入

已在 Jupyter 组织外（包括 jupyter-incubator 中）开发一段时间的项目申请并入。

### 并入提案流程

1. **共识快速通道**：如果团队内共识明确且满足标准，可直接在对应组织的 team-compass 上创建 Issue 建立共识，立即采纳。

2. **正式提案流程**（需要更多讨论时）：
   - 子项目团队向 [jupyter/enhancement-proposals](https://github.com/jupyter/enhancement-proposals) 提交 PR（JEP），描述项目如何满足每项准入标准
   - 通过 PR 进行社区讨论
   - SSC 以共识方式给出推荐
   - SSC 推荐并入时，提交 PR 将新项目添加到子项目列表
   - **EC 最终决定**合并或拒绝该 PR

**时间线指导**：
- 提案后允许一周提出异议，无异议则视为同意（沉默即同意）
- 如果一个月后仍有持续活跃分歧，这是项目尚未准备好毕业的强烈信号

### SSC 可能的推荐结果
- 整合到现有官方子项目
- 作为新官方子项目并入
- 进一步内部/外部孵化（附改进建议）
- 拒绝

### 并入后步骤

项目被接纳为新官方子项目后：

1. 仓库转移到主要 Jupyter GitHub 组织之一
2. 创建 GitHub 团队，子项目团队获得读写权限
3. 向主邮件列表发送新子项目公告
4. 添加标准 Jupyter LICENSE 文件
5. 更新各文件中的版权声明为标准格式

## 孵化流程

### 何时需要孵化

建议在以下情况先孵化：
- 存在重大未解答的技术问题或不确定性
- 全新方向/范围/想法未经社区验证
- 已有大型代码库，与 Jupyter 其他部分的集成方式不明确

孵化的价值：让社区区分稳定官方项目和实验性新项目。

### jupyter-incubator 组织

[jupyter-incubator](https://github.com/jupyter-incubator) 组织提供中立的孵化场地。

**孵化申请**（轻量快速）：
1. 向 [jupyter-incubator/proposals](https://github.com/jupyter-incubator/proposals) 提交 PR 填写孵化申请
2. 向主 Jupyter 邮件列表公告
3. 必须有一名 SSC 成员作为 Advocate（倡导者）
4. 社区讨论后 SSC 以共识批准/拒绝
5. 批准后：创建仓库和团队、添加 LICENSE、SSC 成员在邮件列表公告

**孵化期**：通常至少6个月到1年，目标是证明项目能发展出活跃的开发者和用户社区。

### 外部孵化

也可不通过 jupyter-incubator，在自己的 GitHub 等平台上开发。后续想成为官方子项目时，同样需满足准入标准并走并入流程。

### 孵化仓库管理政策
- 项目名为 `foo` 可创建 `foo-X` 仓库无需额外授权
- 创建顶级名（`bar`）仓库需向主邮件列表提案讨论

## 反常识要点

- **沉默即同意有期限**：直接创建和外部并入的快速通道都使用"一周无异议视为同意"的规则，但这只在没有明确反对时生效；持续的分歧必须被正视。
- **孵化不是"二等公民"**：孵化项目承担与正式项目相同的责任（行为准则、决策流程、透明运营等），只是尚未获得官方 SSC 代表权。
- **改进现有项目优于引入竞争**：Jupyter 明确倾向于改善现有子项目而非接纳功能重叠的竞争项目，这避免了生态碎片化。
- **incubator 流程文档已过时**：官方文档明确标注 jupyter-incubator 流程包含过时内容和链接，过渡期应直接在 SSC Team Compass 上开 issue 提问。

## 相关概念

- [软件子项目体系](06-software-subprojects.md)
- [软件指导委员会（SSC）](04-software-steering-council.md)
- [执行委员会（EC）](03-executive-council.md)
- [决策制定流程](09-decision-making.md)
