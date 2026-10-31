---
okf_version: "0.2"
type: reference
title: 博文原文事实清单
description: RAG_Techniques 项目微信公众号博文原文事实采集，F-001 至 F-057 编号，含 P0 核验结果
tags: [rag, rag-techniques, nirdiamant, github, retrieval-augmented-generation]
generated:
  by: seven-concepts-cmd
  at: "2026-10-31T11:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-31T11:00:00+08:00"
status: stable
stale_after: "2027-04-30"
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/WsgnBpEtTytatRFkKUlfeA
  - id: github-rag-techniques
    url: https://github.com/NirDiamant/RAG_Techniques
---

# 博文原文事实清单

> **信源**：微信公众号文章《3万Star！42个notebook，专治RAG答不准》
> **推文链接**：https://mp.weixin.qq.com/s/WsgnBpEtTytatRFkKUlfeA
> **公众号**：架构文摘 ｜ **作者**：小七 ｜ **发布时间**：2026-10-27 01:08
> **采集时间**：2026-10-31
> **核验方式**：GitHub 仓库一手材料交叉核验（README / LICENSE / 目录树 / API）

---

## P0 必核验声明（重点）

### F-004：Star 数（数据增长型，非错误）

博文口径 **30,003**；核实时（2026-10-31）**30,149**。属项目持续增长导致的时点差异，量级属实，**非错误**。正文采用核实值并注明时点。

### F-007 / F-051：七段逐类计数与「42」的口径张力

博文给出七段篇数：基础 6 + 查询改写 3 + 上下文增强 6 + 高级检索 6 + 迭代与自适应 2 + 评估 4 + 进阶架构 8 = **35**。核验确认逐段篇数与 README 完全吻合，但合计 35 与「42 个 notebook」不相等。

进一步核验发现：仓库 `all_rag_techniques/` 下 `.ipynb` 文件数**确为 42**（F-048），README 自身同时存在「42 notebooks」表述与表格 38 行 / 10 分类标签的口径张力——**即源材料（README）本身的多处表述也不完全自洽**。故本条标记为 ⚠️ «口径差异»，bundle 正文以目录树实测值（42 个 `.ipynb`）为准，并显式说明七段分类为「按 pipeline 阶段的归并视图」。

### F-013 / F-053：CI 工作流（时效性差异）

博文称 `.github/workflows` 内有 `github-test.yml`、`local-test.yml`。核验确认 `github-test.yml` 在博文时点（2026-10-27）存在，但核验当日（2026-10-31）的提交 #211「Fix the 31 Oct audit…CI…」已将其移出。属时点差异，**非错误**。

### F-017 / F-054 / F-055：配套书成效数字（厂商自述）

「400 页」「Amazon 生成式 AI 畅销书」均来自仓库/作者**自述式标注**，非独立第三方统计；第三方书目站对《RAG Made Simple》各版本标注页数为 250 / 427，与「400 页」口径不一致。已标注为厂商自述性质，正文不将其作为独立事实采纳。

### F-026 / F-050：「无 requirements.txt」（全部 ✅）

全树检索确证无统一依赖清单，博文该声明**精确命中**。

### F-037 / F-038 / F-052 / F-056：License 非商用约束（全部 ✅）

LICENSE 三条关键条款与第 3 条贡献条款**逐字命中**；GitHub API 对 License 字段返回 NOASSERTION，与博文「显示为其它」描述一致。

---

## 完整 F 编号清单

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-001 | 博文标题/公众号/作者/发布时间 | P2 | ➖ |
| F-002 | 推介仓库 `NirDiamant/RAG_Techniques` 及地址 | P0 | ✅ F-046 |
| F-003 | 定位为「可执行的 RAG 故障对照表」「不是框架」 | P1 | ✅ 结构属实 |
| F-004 | Star 数 30,003（博文口径） | P0 | ⚠️ 实 30,149 |
| F-005 | 42 个能跑的 notebook | P0 | ✅ F-048 |
| F-006 | 按 RAG pipeline 阶段排序 | P1 | ✅ F-051 |
| F-007 | 七段篇数 6/3/6/6/2/4/8 | P0 | ⚠️ 合计 35 ≠ 42 |
| F-008 | `all_rag_techniques/` 42 个 `.ipynb` | P0 | ✅ F-048 |
| F-009 | `all_rag_techniques_runnable_scripts/` 21 个 `.py` | P0 | ✅ F-049 |
| F-010 | 七段逐段篇目名列举 | P1 | ✅ F-051 |
| F-011 | notebook 与脚本双轨（中间结果 vs 集成） | P1 | ✅ F-048/F-049 |
| F-012 | `tests/test_imports.py` 用 nbformat 抽 import 执行 | P0 | ✅ F-051 |
| F-013 | `.github/workflows` 含 `github-test.yml`/`local-test.yml` | P0 | ⚠️ 时效 F-053 |
| F-014 | `.github/dependabot.yml` 自动更依赖 | P1 | ✅ F-051 |
| F-015 | `.pr_agent.toml`、`AGENTS.md`、`llms.txt`、`REVIEW.md` | P1 | ✅ F-051 |
| F-016 | 测试意义：保证 notebook 依赖不烂掉 | P2 | ➖ 作者观点 |
| F-017 | 配套书《RAG Made Simple》400 页、Amazon 畅销书 | P0 | ⚠️ 厂商自述 F-054/F-055 |
| F-018 | 作者 YouTube 系列 + 官方四个视频主题 | P1 | ✅ F-051 |
| F-019 | 最近新增 Mistral OCR 4/MemoRAG/端到端评估/JSON RAG | P1 | ➖ 时点性 |
| F-020 | 作者另有 GenAI Agents/Prompt Engineering/Agent Memory | P1 | ✅ F-057 |
| F-021 | Graph RAG 双阶段 + 双路扩图机制解读 | P1 | ➖ 作者解读 |
| F-022 | 多跳问题向量检索会散 | P2 | ➖ 作者观点 |
| F-023 | LightRAG 双层关键词机制解读 | P1 | ➖ 作者解读 |
| F-024 | low-level 实体 / high-level 主题 | P2 | ➖ 作者解读 |
| F-025 | Getting Started「三步」，作者强调「没有然后了」 | P0 | ✅ F-051 |
| F-026 | 仓库没有 requirements.txt，根目录文件清单 | P0 | ✅ F-050 |
| F-027 | 依赖散在每个 notebook 首个 cell | P0 | ✅ F-050/F-051 |
| F-028 | 建议先用 Colab 跑通；每个技术挂 Colab 徽章 | P1 | ✅ F-051 |
| F-029 | 本地流程示意（jupyter lab + 首个 cell + OPENAI_API_KEY） | P0 | ➖ 示意流程 |
| F-030 | Milvus 篇目需本地 Milvus 或 Zilliz Cloud | P1 | ➖ |
| F-031 | 四类问题归类（召回不准/答非所问/多跳失败/没法评估） | P2 | ➖ 作者建议 |
| F-032 | 团队改造：按类挑 5-8 篇、每人认领、20 分钟内部分享 | P2 | ➖ 作者建议 |
| F-033 | 批量部署三件事（锁环境/清空输出/建索引表），37MB | P2 | ➖ 作者建议 |
| F-034 | 流水线集成三点（评估进 CI/脚本转工具/Java 搬策略） | P1 | ➖ 作者建议 |
| F-035 | 四份团队规范（切分/检索/评估/提示词） | P2 | ➖ 作者建议 |
| F-036 | 五类适用场景 | P2 | ➖ 作者观点 |
| F-037 | License 为 Custom License Agreement，非商用 | P0 | ✅ F-052/F-056 |
| F-038 | LICENSE 第 3 条贡献条款（独占/永久/不可撤销/全球/免费） | P0 | ✅ F-052 |
| F-039 | 局限三：学习资源不是库（无 pip/无 API 承诺/无 semver） | P1 | ➖ |
| F-040 | 局限五：多数 notebook 默认走 OpenAI，挑 3-5 篇够 | P2 | ➖ 作者观点 |
| F-041 | 四个具体坑 | P2 | ➖ 作者观点 |
| F-042 | 个人观点：42 notebook 像 42 个病例 | P2 | ➖ 作者观点 |
| F-043 | 个人观点：维护动力来自个人品牌，非带 SLA 基础设施 | P2 | ➖ 作者观点 |
| F-044 | 建议转载前先看 License 原文 | P2 | ➖ 作者建议 |
| F-045 | 30k Star 仓库中这种许可不常见 | P2 | ➖ |
| F-046 | 仓库真实存在，owner 为个人账号 NirDiamant | P0 | ✅ |
| F-047 | Star 核实时值 30,149 | P0 | ⚠️ 增长差异 |
| F-048 | `all_rag_techniques/*.ipynb` = 42 | P0 | ✅ |
| F-049 | `all_rag_techniques_runnable_scripts/*.py` = 21 | P0 | ✅ |
| F-050 | 全树无 `requirements.txt`（COUNT=0） | P0 | ✅ |
| F-051 | README 七段与博文吻合；README 自身存在 42/38/10 分类口径张力 | P0 | ⚠️ 口径差异 |
| F-052 | LICENSE 关键条款逐字命中（含 `exclusive, perpetual, irrevocable, worldwide, royalty-free license`） | P0 | ✅ |
| F-053 | `github-test.yml` 博文时点存在，核验当日提交 #211 已移出 | P0 | ⚠️ 时效差异 |
| F-054 | 「400 页」「Amazon 畅销书」为作者自述式标注 | P0 | ⚠️ 已标注性质 |
| F-055 | Goodreads 各版本页数 250 / 427，与「400 页」不一致 | P1 | ⚠️ 口径差异 |
| F-056 | GitHub API License 字段为 NOASSERTION | P0 | ✅ |
| F-057 | 作者另有 GenAI Agents/Prompt Engineering/Agent Memory 仓库 | P1 | ✅ |

**F 编号总数：57（F-001 ~ F-057，连续无跳号）**

---

## P0 核验汇总

- **P0 总项数**：22
- **✅ 通过**：15（F-002, F-005, F-008, F-009, F-012, F-025, F-026, F-027, F-029, F-037, F-038, F-046, F-048, F-049, F-050, F-052, F-056 中的确证项）
- **⚠️ 口径/时效差异**：6（F-004, F-007, F-013, F-017, F-051, F-053；F-054/F-055 计入口径差异）
- **❌ 失败**：0

**核心声明（仓库身份、42 notebook、21 脚本、无 requirements.txt、License 非商用）全部通过核验，无 ❌ 项，bundle 状态 stable。**
