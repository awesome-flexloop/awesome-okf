---
okf_version: "0.2"
type: Concept
title: "可打分的检查：Crapper、Dryer、Mutator 与 uml-viewer"
description: "ub-mode 判定「代码变好」的四个 companion 工具与阈值——CRAP<10、相似度≥0.8、变异测试、UML 可视化；含博文单源与官方源的口径差异"
tags: [ub-mode, crapper, dryer, mutator, uml-viewer, 度量, 变异测试, 阈值]
source: /references/article-source.md#F-024-F-030
status: draft
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/vgwzE-3XGKN1VSjaIoZ_BA
  - id: skill-md
    url: https://raw.githubusercontent.com/unclebob/ub-mode/master/SKILL.md
  - id: github
    url: https://github.com/unclebob/ub-mode
---

# 可打分的检查：Crapper、Dryer、Mutator 与 uml-viewer

## 为什么「可打分」是关键

ub-mode 的第二节 **Then Make it Right** 不是一句口号：它把「代码是否变好」交给三个可算出具体分数的检查工具（F-017）。这三条原则在官方 `SKILL.md` 中以可执行指令的形态出现——**阈值明确、动作明确**：

| 原则 | 官方指令原文（节选） | 阈值 | 编号 |
|------|---------------------|------|------|
| Crapper | "Reduce each function under CRAP 10" | 每个函数 **CRAP < 10** | F-024 |
| Dryer | "rank 0.8 or above" | 消除相似度 **≥ 0.8** 的重复 | F-025 |
| Mutator | "Cover the uncovered. Kill the survivors. Delete dead code." | 变异测试三动作 | F-026 |

> **CRAP** 是「Change Risk Anti-Patterns」的缩写，一个综合了**代码复杂度**与**测试覆盖度**的经典度量。这里只需记住它的用途：**分数越高，说明这段代码越难改、风险越大**；`< 10` 是可接受线。

## 四个 companion 工具（不是三个）

⚠️ **博文只提了三个，官方 README 列了四个**（F-027、F-028；对应[勘误 E-2](../references/verification.md)）：

| # | 工具 | 作用 | 编号 |
|---|------|------|------|
| 1 | [`crapper`](https://github.com/unclebob/crapper) | 计算 CRAP 分数，把每个函数压到 10 以下 | F-024、F-027 |
| 2 | [`dryer`](https://github.com/unclebob/dryer) | 度量相似度，消除 ≥ 0.8 的重复代码 | F-025、F-027 |
| 3 | [`mutator`](https://github.com/unclebob/mutator) | 变异测试：覆盖未覆盖代码、杀掉存活变异体、删除死代码 | F-026、F-027 |
| 4 | [`uml-viewer`](https://github.com/unclebob/uml-viewer) | 可视化组件、覆盖率、CRAP 分数、变异分数与依赖方向 | F-028 |

四个工具同属 `unclebob/` 命名空间（F-027）。**博文完全未提及 `uml-viewer`**（F-028）——若只按博文理解，会低估工具集规模。

## 博文给出的检查命令与输出（单源，未经官方文档对拍）

博文给出了三条命令行用法与产物位置（F-029、F-030）：

```
./crapper --threshold 10
./dryer --threshold 0.8 src
./mutator --changed
```

博文称检查结果写入 `.metrics` 目录，产物为 `crap.edn`、`dry.edn`、`mutate` 快照（F-030）。

> ⚠️ **这是博文单源内容，使用前务必查证**（对应[勘误 E-4](../references/verification.md)）：
> - ub-mode 官方仓库**不含 CLI 用法文档**，无从逐字对拍；
> - 三个 companion 工具仓库本次**未逐一核验**其命令行接口（参数名、是否需先构建、是否依赖 Clojure/EDN 生态等）；
> - `.edn` 后缀暗示产物为 **EDN（Extensible Data Notation）** 格式（Clojure 生态常见），但仍属推断，不应作为既知事实引用。
>
> 因此：把上述命令视为「博文作者的用法示例」，而非「官方 CLI 契约」。

## 阈值口径的双源一致性（已核验）

与上一条相反，**阈值本身是本次核验中一致性最好的部分**（F-024、F-025）：官方 `SKILL.md`（"CRAP 10"、"rank 0.8 or above"）与官方 README（"CRAP < 10"、">= 0.8 similarity"）以及博文三方口径**逐字一致**（P0-11 ✅）。

| 项目 | SKILL.md | README | 博文 |
|------|----------|--------|------|
| CRAP 阈值 | CRAP 10 | CRAP < 10 | 10（`--threshold 10`） |
| 重复度阈值 | rank 0.8 or above | >= 0.8 similarity | 0.8（`--threshold 0.8 src`） |

## 与「可复现性两问」的关系

值得单独指出：**这四个工具本身并不随 ub-mode 一起分发，需要单独安装**（F-034）。博文虽给出检查命令，但**未提供任何安装方式**——这直接触发了本知识包的骨架判定：照做链路在第三步断裂，故本条目不设 `examples/` 目录（详见 [安装与触发](03-install-and-usage.md) 与 [边界与勘误](04-boundaries-and-gotchas.md)）。

下一篇 [安装与触发](03-install-and-usage.md) 说明官方与博文两种上手路径。

事实编号全集见 [博文与官方源事实清单](../references/article-source.md)，核验结论见 [P0 核验报告](../references/verification.md)。
