---
okf_version: "0.2"
type: Concept
title: "边界、勘误与已知限制"
description: "使用 ub-mode 前必读：作者对自动推送的保留意见、检查工具需单独安装、博文与官方源的四项口径差异（E-1~E-4）、未实测声明与时效性提示"
tags: [ub-mode, 勘误, 边界, 已知限制, 时效性, 核验]
source: /references/verification.md#E-1-E-4
status: draft
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/vgwzE-3XGKN1VSjaIoZ_BA
  - id: github
    url: https://github.com/unclebob/ub-mode
  - id: github-api
    url: https://api.github.com/repos/unclebob/ub-mode
---

# 边界、勘误与已知限制

本篇汇总使用 ub-mode 前需要知道的所有注意事项，以及博文与官方源之间的口径差异。所有勘误的完整核验过程见 [P0 核验报告](../references/verification.md)。

## 一、作者保留意见：自动提交并推送

官方 Practice 节的 **Commit and Push** 原则要求「Push to the main line at the end」（最后推送到主线）（F-023）。

⚠️ **博文作者对此明确表示「不放心」**（F-033）——这是博文中唯一被标注为保留意见的一节，作者观点，**不是官方缺陷**，但值得使用前留意：

- 若你所在的仓库有分支保护、Code Review 或 CI 门禁，「AI 直接推送到主线」可能与流程冲突；
- 稳妥做法是在启用前把该条规则收紧（例如改为「只提交到工作分支，不推送」），或在受控分支上使用。

## 二、检查工具需单独安装

ub-mode 本身**只提供规则**，四个 companion 工具（Crapper / Dryer / Mutator / uml-viewer）需要**单独安装**（F-034、F-027）。

| 项 | 说明 | 编号 |
|----|------|------|
| ub-mode 提供 | 仅 `SKILL.md` 规则文本 | F-031 |
| 工具提供方 | 四个独立仓库（`unclebob/crapper` 等） | F-027 |
| 官方是否给安装方式 | ❌ 官方仓库不含安装/CLI 用法文档 | F-037、E-4 |
| 博文是否给安装方式 | ❌ 博文要求安装但未给方式 | F-032、F-034 |

**结论**：默认安装下，「用分数检验代码」这一步无法真正执行——你得到的是「AI 承诺遵守规则」，而非「代码被自动打分」。

## 三、口径差异：勘误 E-1 ~ E-4

| 编号 | 类型 | 博文口径 | 官方事实 | 处理 |
|:----:|------|---------|---------|------|
| **E-1** | ⚠️ 口径 | 「只有两个文件，加起来 6KB」 | **3 个文件**（+ `LICENSE`），合计 7,226 B；README+SKILL = 6,153 B 才≈6KB | 正文按「3 文件 ≈7.2 KB；其中正文两文件 ≈6 KB」呈现 |
| **E-2** | ⚠️ 漏提 | 配套工具**三个** | **四个**（另有 `uml-viewer`） | 正文补齐 `uml-viewer` 并标注博文未提及 |
| **E-3** | ⚠️ 时效 | 标题 Star **2,900** | 核验时点 **3,951**（动态数字） | 双时点并列，引用时须重新取数 |
| **E-4** | ⚠️ 单源 | 三条检查命令 + `.metrics` 产物 | 官方**无** CLI 用法文档，无从对拍 | 正文标注为「博文单源」，使用前查各工具仓库 README |

> **注意方向**：E-1 与 E-2 都是**低估**（少算文件、少列工具），而非拔高；E-3 属时间推移导致的**正常增长**，不是错误。**三项均不改变文章主旨**（ub-mode 确实极轻量、确实配套可打分工具）。

### 关联事实索引

| 勘误 | 相关事实编号 | 见 |
|------|-------------|-----|
| E-1 | F-008（文件树 3 文件）、F-035（博文 6KB 口径） | [项目定位](00-overview-and-philosophy.md)、[可打分的检查](02-scoreable-checks.md) |
| E-2 | F-027（4 个工具）、F-028（uml-viewer） | [可打分的检查](02-scoreable-checks.md) |
| E-3 | F-010（Star 双时点）、F-011（forks 等） | [项目定位](00-overview-and-philosophy.md) |
| E-4 | F-029（命令）、F-030（`.metrics` 产物） | [可打分的检查](02-scoreable-checks.md) |

## 四、博文未提但重要的事实（非勘误）

| 事实 | 编号 | 为什么重要 |
|------|------|-----------|
| 默认分支是 **`master`**（非 `main`） | F-006 | 按 `main` 拼 raw/克隆路径会失败 |
| 上游溯源：`@poteto's rules`（`poteto-mode` / `pstack`） | F-013 | 引用「原创」会遗漏谱系 |
| 仓库**无 Release、无 tag**，自创建后未再改动 | F-037 | 说明其处于「单次定稿」形态，无版本可锁 |

## 五、未实测声明与时效性

- ⚠️ **本知识包未做真机复测**：未在本地安装三个检查工具、未实际运行 `/ub-mode` 观察行为。因此对工具的实际输出格式、命令参数是否如博文所述**不作任何断言**。
- ⚠️ **未运行 CI 质量门**：本次未执行 `invoke gates.*`（环境未安装 `.[doc]` 依赖），故不声称门禁通过。
- 🕐 **时效性**：本包 `stale_after: 2027-01-31`。动态度量（Star、fork）与仓库形态随时可能变化；引用前请重新核对 [GitHub 仓库](https://github.com/unclebob/ub-mode) 当前状态。

## 六、一句话总结

> ub-mode 的价值在于**把「让 AI 好好写代码」从口号变成一条有阈值、有次序、可打分的短链路**；但它的「可打分」部分需要你**自己接上四个工具**，而它的「自动推送」部分**建议按团队流程收紧**。

---

- 完整核验过程与四张勘误清单：[P0 核验报告](../references/verification.md)
- 事实编号全集：[博文与官方源事实清单](../references/article-source.md)
- 返回：[知识包首页](../index.md)
