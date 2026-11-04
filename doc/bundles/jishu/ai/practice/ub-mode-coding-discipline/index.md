---
okf_version: "0.2"
type: bundle
title: "ub-mode：用可打分的检查约束 AI 编码纪律的 Skill"
description: "微信公众号「开源日记」2026-10-28 博文经 OKF v0.2 转化——unclebob 的 ub-mode 是一个只有 3 个文件的 agent skill，把「让 AI 好好写代码」压缩成三步（Make it Work → Make it Right → Practice），并以 Crapper/Dryer/Mutator（+uml-viewer）四个可打分工具检验结果；含 P0 核验与勘误 E-1~E-4（概念解读，非操作教程）"
tags: [ub-mode, agent-skill, unclebob, clean-code, tdd, 变异测试, 代码质量, 博文转化]
generated: { by: "process:wechat-public-okf", at: 2026-11-04T10:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-11-04T10:00:00Z }
status: draft
stale_after: 2027-01-31
sources:
  - id: refs
    resource: /references/article-source.md
  - id: blog
    url: https://mp.weixin.qq.com/s/vgwzE-3XGKN1VSjaIoZ_BA
  - id: github
    url: https://github.com/unclebob/ub-mode
  - id: github-api
    url: https://api.github.com/repos/unclebob/ub-mode
---

# ub-mode：用可打分的检查约束 AI 编码纪律的 Skill

> 📊 **数据性质提示**：本条目是对一篇公众号博文的**概念解读**（非操作教程）——文章主结论「用可打分的检查约束 AI 编码」有官方 `SKILL.md` 全文支撑；但其中的**检查工具 CLI 用法与 `.metrics` 产物为博文单源**、**Star 数为动态数字**、**文件/工具数量存在口径差异**（见[勘误 E-1~E-4](references/verification.md)）。引用数字前请先读[已知边界](#已知边界)与[P0 核验报告](references/verification.md)。

## 项目速览

**ub-mode** 是《Clean Code》作者 Robert C. Martin（`unclebob`）发布的 **agent skill**——不是一个应用、不是一个框架，而是**一篇写给 AI 编程助手读的规则文档**。它把「让 AI 好好写代码」从一长串容易失效的规则，压缩成三步：**First Make it Work**（先让代码能跑）→ **Then Make it Right**（再让它变好，且可打分）→ **Practice**（说明改动并交付）。整个仓库只有 3 个文件（`LICENSE` + `README.md` + `SKILL.md`），却把「先测试、最小改动、复杂度 <10、重复度 <0.8、变异测试」这些可度量的工程纪律固化成 AI 每次改动都必须走的链路。

| 项 | 值 | 编号 |
|----|----|:----:|
| 项目 | ub-mode（作者 Robert C. Martin / `unclebob`） | F-004、F-036 |
| 类型 | **Agent Skill**（非应用 / 非框架 / 无可执行代码） | F-012、F-007 |
| 许可 | MIT License | F-009 |
| GitHub | github.com/unclebob/ub-mode（默认分支 `master`） | F-003、F-006 |
| 仓库规模 | **3 个文件**，合计 7,226 B | F-008 |
| 上游溯源 | 松散衍生自 `@poteto's rules`（`poteto-mode` / `pstack`） | F-013 |
| 核心阈值 | CRAP < 10；重复相似度 ≥ 0.8 | F-024、F-025 |
| Star | 博文口径 2,900（2026-10-28）/ 核验口径 3,951（2026-11-04） | F-010 |

## 阅读路径

1. [ub-mode 是什么：定位、作者与极轻量仓库](concepts/00-overview-and-philosophy.md)——agent skill 定位、作者与溯源、3 文件仓库形态、博文痛点（「写规则越写越不听话」）；
2. [三步机制：Make it Work → Make it Right → Practice](concepts/01-three-step-mechanism.md)——三大节共 24 组原则清单，及博文「修好 → 检验 → 说明」的对应关系；
3. [可打分的检查：Crapper、Dryer、Mutator 与 uml-viewer](concepts/02-scoreable-checks.md)——四个 companion 工具、明确阈值、命令与产物的口径差异；
4. [安装与触发：把它装进你的 AI 编程助手](concepts/03-install-and-usage.md)——官方三路径安装、博文「上手三步」与其中的断点；
5. [边界、勘误与已知限制](concepts/04-boundaries-and-gotchas.md)——自动推送保留意见、工具需另装、勘误 E-1~E-4、未实测声明。

## 已知边界

- ❌ **不设 `examples/`**：博文虽给出安装三步与三条检查命令，但**检查工具需要单独安装而博文未给安装方式**（F-034），照做链路在第三步断裂；且无版本号、无 Release/tag（F-037）、官方无 CLI 文档（E-4）。按「操作可复现性两问」（Q1 是 / Q2 否）判定为**概念骨架**，故本包为「概念解读，非操作教程」；
- ⚠️ **勘误 E-1**（口径）：博文「只有两个文件 6KB」→ 实为 **3 个文件**（含 `LICENSE`），约 7.2 KB；
- ⚠️ **勘误 E-2**（漏提）：检查工具**四个**（Crapper / Dryer / Mutator / **uml-viewer**），博文只提三个；
- ⚠️ **勘误 E-3**（时效）：Star **2,900 → 3,951**，属动态增长，引用须重新取数；
- ⚠️ **勘误 E-4**（单源）：三条检查命令与 `.metrics` 产物为**博文单源**，官方仓库无对拍文档；
- ⚠️ **作者保留意见**：官方要求 AI「提交并推送到主线」（F-023），博文作者对此「不放心」（F-033）——启用前建议按团队流程收紧；
- ⚠️ **未实测**：本项目未真机复测三个检查工具，亦未运行 `invoke gates.*`，故不对工具实际行为作断言。

## 主题关联

- [📄 answer-me-with-html：让 Agent 交付可视化页面的 Skill](../answer-me-with-html/index.md)——同为 Agent Skill 博文转化条目，两者都体现「把一件事做成一条短链路」的思路；
- [🧘 上下文优化（Context Optimization）](../context-optimization/index.md)——ub-mode 的 Practice 节含「Guard the Context Window」，与本主题的上下文管理取向相关；
- [🗜️ planning-with-files 像 Manus 一样工作](../planning-with-files/index.md)——同属给 AI 编码助手外加工程纪律/脚手架的思路；
- [🛠️ 工程实践、方法论与行业洞察](../index.md)——返回分组总览。

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
references/index
log
```
