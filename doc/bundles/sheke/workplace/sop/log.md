# 更新日志

> 本文件记录 SOP 标准作业程序知识包的创建与修订历史。每次修订须在标题下新增日期章节，末尾更新 metadata 中的 `generated` 与 `status` 字段。

## 2026-09-08

**创建本 bundle**（七概念方法论编排，session `sc-20260908-sop-okf-bundle`）。

### 本次新增内容

| 类型 | 文件 | 说明 |
|------|------|------|
| index.md | `index.md` | 束根导航，含快速导航 + toctree |
| facts.md | `facts.md` | 32 条事实（F-001～F-032），10 条信源（S1～S10） |
| insights.md | `insights.md` | 5 条四元组洞察 |
| concepts/01-what-is-sop.md | 概念 01 | 词源、定义、四项特征、起源 |
| concepts/02-elements-and-structure.md | 概念 02 | 组成要素、格式类型、四层体系 |
| concepts/03-industry-practices.md | 概念 03 | 医疗·航空·制药·IT 四大行业实证 |
| concepts/04-runbook-playbook-sop.md | 概念 04 | runbook / playbook / SOP 辨析与选型矩阵 |
| concepts/05-anti-patterns.md | 概念 05 | 五类失效模式 + SOP debt |
| examples/01-sop-template.md | 示例 01 | 通用 SOP 模板（可复制） |
| examples/02-runbook-vs-playbook-example.md | 示例 02 | 数据库宕机场景对照 |
| references/01-source-registry.md | 信源登记 | 10 条信源的详细可信度说明 |
| log.md | 本文件 | 本日志 |

### 计数影响

- 新增 1 个 bundle：`sheke/workplace/sop`
- 总束数 507 → **508**
- sheke 域：33 → **34**
- workplace 分组：7 → **8**
- groups 总数不变：**58**

### 索引同步清单

需同步更新以下索引文件：

- [ ] `doc/bundles/index.md` — frontmatter `total_bundles: 508`，L15 计数行，sheke 节（L114/L118）
- [ ] `doc/bundles/sheke/index.md` — workplace 行束数 7→8
- [ ] `doc/bundles/sheke/workplace/index.md` — 新增 SOP 分组导航 + toctree

### 质量门执行

- [ ] `python scripts/check-bundles-index.py` — 预期 0 退出
- [ ] `python scripts/check-toctrees.py` — 预期无断链
- [ ] 对抗审查（4 视角）— 见下方记录

---

## 版权说明

本知识包由 reference_agent 基于公开信源调研生成，遵循 OKF v0.2 规范。外部知识在 frontmatter 中通过 `sources` 字段标注。放弃核验的自媒体数据独立列于 facts.md 末尾清单，不作为本知识包断言。
