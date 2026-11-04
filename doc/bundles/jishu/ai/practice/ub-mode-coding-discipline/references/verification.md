---
okf_version: "0.2"
type: Reference
title: "ub-mode P0 核验报告"
description: "博文与 GitHub 官方源的关键声明 P0 交叉核验（含 Star 数、文件数量、工具清单、阈值、许可证），含勘误 E-1~E-4 与勘误四张清单"
tags: [ub-mode, p0-核验, 勘误, github, agent-skill, clean-code]
generated: { by: "process:seven-concepts-v", at: 2026-11-04T10:00:00Z }
status: draft
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/vgwzE-3XGKN1VSjaIoZ_BA
  - id: github
    url: https://github.com/unclebob/ub-mode
  - id: github-api
    url: https://api.github.com/repos/unclebob/ub-mode
  - id: skill-md
    url: https://raw.githubusercontent.com/unclebob/ub-mode/master/SKILL.md
---

# ub-mode P0 核验报告

## 信源距离预判

| 信源 | 距离分类 | 核验待遇 |
|------|---------|---------|
| 公众号「开源日记」博文 | 第三方综述（开源项目推介号） | 数字与命令按 P0 处理，优先与官方源对拍 |
| GitHub 仓库 `README.md` / `SKILL.md` / `LICENSE` | 一手权威（开源项目自述） | 作为交叉核验主锚 |
| GitHub REST API 元数据 | 一手权威（平台数据） | 仓库身份、时间线、动态数字的判定依据 |

> 说明：本项目**无出版社/厂商自宣属性**，博文不含提效倍数、成本下降等营销数字，故「成效数字溯源」风险低；主要风险集中在**动态数字（Star）**与**清点类口径（文件数、工具数）**。本次未做真机复测（未在本地安装三个检查工具）。

## P0 核验总表

图例：✅ 与权威源一致 / 补充；⚠️ 单源或口径差异、方向一致；❌ 与权威源矛盾。

| # | 声明 | 结论 | 核验依据 |
|---|------|:----:|---------|
| P0-1 | 项目是装在 AI 编程助手里的 agent skill，而非独立应用 | ✅ | F-012；README 自述 "an agent skill"，安装方式为复制到 agent 技能目录 |
| P0-2 | 仓库地址 `github.com/unclebob/ub-mode` 存在 | ✅ | F-003/F-004；GitHub API 返回仓库对象 |
| P0-3 | 作者 Robert C. Martin（写过《Clean Code》） | ✅ | F-036；LICENSE 署名 `Copyright (c) 2026 Robert C. Martin`，owner `unclebob` |
| P0-4 | 许可证 | ✅ | F-009；仓库 LICENSE 为 MIT（API `license` 字段为 null，以文件为准） |
| P0-5 | 仓库"只有一个 Skill"、极轻量 | ✅ | F-007/F-008；文件树仅 3 个文本文件、`language: null`，无可执行代码 |
| P0-6 | 博文「只有两个文件，加起来 6KB」 | ⚠️ | F-008/F-035；实为 3 个文件（另含 LICENSE），合计 7,226 B；README+SKILL = 6,153 B 才≈6KB。**E-1** |
| P0-7 | 标题 Star「2900」 | ⚠️ | F-010；发文时点量级合理，核验时点 API 为 3,951，属**时效增长**非硬错。**E-3** |
| P0-8 | 三步机制：修好 → 检验 → 说明修改 | ✅ | F-016/F-017/F-018；与官方 SKILL.md 三大节 First Make it Work / Then Make it Right / Practice 结构一致 |
| P0-9 | 第一步「先写测试再做最小改动」 | ✅ | F-016；官方 TDD 节逐条对应 |
| P0-10 | 三个检查工具 Crapper / Dryer / Mutator | ⚠️ | F-027；官方 companion 工具为 **4 个**，博文漏提 `uml-viewer`。**E-2** |
| P0-11 | Crapper 复杂度阈值、Dryer 重复度阈值 0.8 | ✅ | F-024/F-025；官方 SKILL.md「CRAP 10」「rank 0.8 or above」与 README「CRAP < 10」「>= 0.8 similarity」逐字一致 |
| P0-12 | 检查工具 CLI 用法与 `.metrics` 输出 | ⚠️ | F-029/F-030；官方仓库未提供 CLI 用法与产物文档，**仅博文单源**。**E-4** |
| P0-13 | 安装目录 `~/.claude/skills/ub-mode/` 与 `/ub-mode` 触发 | ✅ | F-031/F-032；官方 README Installation 节逐字一致（官方另支持 `~/.grok/`、`~/.cursor/`） |

**汇总：13 项 → ✅ 7 / ⚠️ 6 / ❌ 0。** 无核心声明失败（文章主结论「用可打分检查约束 AI 编码」有官方 SKILL.md 全文支撑），故不适用 `status: flagged`；但本次未做真机复测，取 `status: draft`。

## 勘误登记

### E-1（⚠️ 口径）：博文「只有两个文件，加起来 6KB」

- 博文口径：仓库「只有两个文件，加起来 6KB」（F-035）。
- 官方事实：文件树为 **3 个文件** —— `LICENSE` 1,073 B + `README.md` 2,195 B + `SKILL.md` 3,958 B = **7,226 B**（F-008）。
- 处理：正文按「3 个文件、约 7.2 KB；其中正文两文件（README + SKILL）≈6 KB」呈现，保留博文口径说明。该差异不改变文章主旨（仓库确实极轻量）。

### E-2（⚠️ 漏提）：检查工具为 4 个而非 3 个

- 博文口径：配套检查工具三个（Crapper / Dryer / Mutator）（F-034）。
- 官方事实：README 的 **Companion Tool Repositories** 列出 **4 个** —— `crapper`、`dryer`、`mutator`、[`uml-viewer`](https://github.com/unclebob/uml-viewer)（F-027/F-028）。
- 处理：正文补齐 `uml-viewer`（可视化组件、覆盖率、CRAP、变异分数与依赖方向），并标注博文未提及。

### E-3（⚠️ 时效）：Star 数 2,900 → 3,951

- 博文口径：标题「2900 Star」（发文时点 2026-10-28）（F-010）。
- 核验时点（2026-11-04）：GitHub API `stargazers_count` = **3,951**（F-010），`forks` 214（F-011）。
- 处理：属**动态数字随时点增长**，非博文错误。正文以「博文口径 / 核验口径」双值并列，并提示引用时须重新取数。

### E-4（⚠️ 单源）：工具 CLI 用法与 `.metrics` 产物无官方文档

- 博文口径：`./crapper --threshold 10`、`./dryer --threshold 0.8 src`、`./mutator --changed`；输出写入 `.metrics`（`crap.edn`、`dry.edn`、`mutate`）（F-029/F-030）。
- 官方事实：ub-mode 仓库不含 CLI 用法文档；三个 companion 仓库本次**未逐一核验**其命令行接口。
- 处理：正文将上述命令明确标注为「博文单源、未经官方文档对拍」，使用前须查各 companion 仓库 README。

### 补充事实（非勘误，但博文未提）

- **默认分支为 `master` 而非 `main`**（F-006）——按 `main` 拼 raw 路径会 404；
- **上游溯源**：README 声明 ub-mode "loosely based on portions of @poteto's rules（`poteto-mode` / `pstack`）"（F-013）——博文未提及；
- **仓库无 Release、无 tag**，自初始推送后未再改动（F-037）——说明其处于「单次定稿」形态。

## 勘误四张清单（逐项过筛）

| 清单 | 核验要点 | 本次结论 |
|------|---------|---------|
| ① 日期/版本表 | 发文日、仓库创建日、版本号逐项对官方源 | 发文 2026-10-28（博文）；创建 2026-10-25（API）✅；无版本号可核，无 Release/tag（F-037）⚠️ 属事实而非缺失 |
| ② 成效数字溯源表 | 提效倍数/节省工时/成本下降须有原始出处 | 博文**无任何**提效/成本类数字 → 不适用；唯一动态数字 Star 已双时点登记（F-010） |
| ③ 口径对照表 | 规模数字核对限定词、警惕拔高 | 命中两处：文件数量 E-1、工具数量 E-2；均为**低估而非拔高**，方向一致 |
| ④ 引文逐字核对表 | 官方定位/引语须核对原文 | 「CRAP 10」「0.8」阈值与官方逐字一致 ✅；「写规则越写越不听话」为作者自述（无引号转述官方）✅ |

## 核验方法与限制

- 核验手段：GitHub REST API（仓库元数据、文件树）+ `raw.githubusercontent.com`（`master` 分支三文件原文）。
- 本次**未运行** `invoke gates.*`（环境未安装 `.[doc]` 依赖），亦未安装三个检查工具做真机复测；因此不对这些工具的实际行为作任何断言。
