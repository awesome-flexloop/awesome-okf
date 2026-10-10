---
okf_version: "0.2"
type: bundle
title: "oil-ui：AI Agent 用的界面设计 Skill（八步设计法）"
description: "开源星探公众号博文经官方仓库核验转化——给 AI 编程 Agent 装的 UI 设计方法论 Skill：八步设计法、五种调性刻度、风格对比页、老项目改造与 Oil UI Pro 边界（核心声明官方核验一致，作品数 52→65 时效勘误）"
tags: [oil-ui, agent-skill, ui-design, eight-step-design, design-method, ai-agent, claude-code, cursor, codex, style-comparison, 博文转化]
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T00:00:00+08:00"
status: stable
stale_after: 2027-03-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/JqY_1JW1FSMQU3XAQyTRPA
    title: 《这个刚开源一周的 Skill 极大的提升了 AI 的 UI 设计能力！八步设计法绝了！》（微信公众号"开源星探"，2026-10-06，作者开源星探）
  - id: github-repo
    url: https://github.com/oil-oil/oil-ui
    title: oil-oil/oil-ui GitHub 仓库（MIT，v0.14.0，作者 Zhihuang Lin）
  - id: gallery
    url: https://ui.oiloil.org
    title: oil-ui 官方作品画廊（含 65 作品与模型标签）
  - id: pro
    url: https://ui.oiloil.org/pro
    title: Oil UI Pro 官方售卖页（69 元买断）
  - id: companion
    url: https://github.com/oil-oil/draw-ui
    title: draw-ui 搭配工具
  - id: companion2
    url: https://github.com/oil-oil/oil-motion
    title: oil-motion 搭配工具
---

# oil-ui：AI Agent 用的界面设计 Skill（八步设计法）

> **类型**：技术教程/选型（含可照做 examples/，操作可复现性两问皆"是"——安装命令与使用提示皆可重复执行并观察输出）
> **信源**：微信公众号「开源星探」博文（2026-10-06，作者开源星探）→ 2026-10-10 经 GitHub 官方仓库、官方画廊与 Pro 售卖页逐项核验
> **核验结论**：文章断言 11 项 P0/P1 中 **9✅ / 2⚠️ / 0❌**，安装命令逐字一致，作者既有项目、八步法、调性刻度、对比页、Pro 版本全部官方证实；仅**作品数 52 与模型名称为时效/口径差异**（详见"勘误提示"）

## 本文概要

[oil-ui](https://github.com/oil-oil/oil-ui) 是一个给 **AI 编程 Agent**（Claude Code、Cursor、Codex 等）装的 **Agent Skill**——不教 AI"什么是好设计"，而是给它一套**可直接执行的八步设计方法论**（施工图纸式工作流），从认品类到定稿，强制 AI 跳出模板思维，一次产出多个可对比的设计方向（F-003~F-004）。

作者油子（Zhihuang Lin）此前做过 [beautify-github-readme](https://github.com/oil-oil)（GitHub README 画廊级排版）与 [oiloil-ui-ux-guide](https://github.com/oil-oil/oiloil-ui-ux-guide)（风格中性 UI/UX 咨询 Skill，CRAP/Fitts's law）。oil-ui 是他"从教设计到给施工图纸"的转向之作（F-002 / F-021✅）。项目 MIT 许可、2026-09-30 开源，当前 v0.14.0、203 Stars、21 commits（F-022✅）。

## 阅读路径

**先建立概念（8 分钟）**

1. [oil-ui 是什么：一个给 AI 的 UI 设计 Skill](concepts/00-what-is-oil-ui.md)——项目定位、作者线索、三大痛点（F-005~F-007）
2. [八步设计法与五种调性刻度](concepts/01-eight-step-design-method.md)——方法论核心：八步逐一"做什么/不做什么"，五刻度把审美形容词翻成数字
3. [安装、使用与风格对比页](concepts/02-install-usage-and-comparison.md)——两种安装法、六个可直接复制的提示、对比页交互

**再深入边界**

4. [Oil UI Pro、老项目改造与版本检查](concepts/03-pro-legacy-and-update.md)——免费/Pro 功能图谱、老项目"先分清再体检"、版本检查与相邻工具

**动手落**（examples/）

5. [六条可直接复制给 Agent 的提示](examples/00-quickstart-prompts.md)
6. [用风格对比页在多方向间决策](examples/01-style-comparison-page.md)

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 作者 | [oil-oil/oil-ui](https://github.com/oil-oil/oil-ui)（作者 Zhihuang Lin，贡献者含 claude） |
| 开源时间 / 许可 | 2026-09-30 / MIT / Python 53.3% + HTML 45.6% |
| 社区数据 | Star 203、Fork 6、（**2026-10-10 时点**） |
| 安装 | `npx skills add oil-oil/oil-ui`（Node.js 18+）或自然语言交给 Agent |
| 核心资产 | 八步设计法 + 五种调性刻度 + 自带风格对比页（HTML/图片/运行页） |
| 作品画廊 | [ui.oiloil.org](https://ui.oiloil.org)——当前 65 作品、6 种模型标签 |
| Pro 版本 | [ui.oiloil.org/pro](https://ui.oiloil.org/pro)（69 元买断、永久更新） |
| 先决条件 | 版本检查需 Python 3（`python3`/`python`/Windows `py -3`） |

## ⚠️ 阅读前必知的两条口径勘误

1. **作品数"52"是发文时快照**：博文称画廊"目前展示了 52 个作品"（F-012），核验时官方画廊已增长到 **65 个**（F-026）。动态数字须以可访问、带时点的官方页面为准。
2. **模型名称是画廊标签而非官方背书**：博文列出的"GPT 6.1 Sol / GPT 6 Luna / Claude Opus 5.5 / Claude Sonnet 5.5"（F-014）是**画廊作品的分组标签**（官方画廊真实存在这些标签，F-027），用途是说明"oil-ui 不绑定单一模型"的方法论主张（F-015），**不是**对所谓模型能力的背书或评测结论。

## 采用提示与已知边界

- **开源版能力有裁剪**：八步法、对比页、视觉层级、截图还原、老项目基础体检为免费版；交互/状态、页面布局适配、组件极致打磨、SVG/着色器特效、按三种立场出方案为 **Pro 专有**（F-023 / F-028，见 [concepts/03](concepts/03-pro-legacy-and-update.md) 功能图谱）。
- **单 AI 协作维护的早期项目**：仓库贡献者仅作者 + claude、25 天内发布到 v0.14.0、文档与画廊在快速迭代；作为方法论学习价值稳定，生产依赖前宜锁定版本（F-022）。
- **建议与独立评审工具**：README 明确"以实际画面为准"、可请独立评审（开源版每阶段一轮，Pro 以 9 分目标最多三轮），这是方法论的一部分而非可选点缀（F-030）。
- **相邻工具**：官方推荐搭配 [draw-ui](https://github.com/oil-oil/draw-ui)（生图出设计稿）与 [oil-motion](https://github.com/oil-oil/oil-motion)（滚动/拖动网页动画），本文未展开（F-029）。

## 信源与可信度

- 事实清单与逐条核验状态：[references/article-source.md](references/article-source.md)（F-001 ~ F-030）
- P0 核验报告与勘误说明：[references/verification.md](references/verification.md)
- 信源距离：第三方开源推介号「开源星探」→ 已升级为 GitHub 官方仓库 + 官方画廊一手核验；方法论陈述以官方 README 为唯一权威口径

## 主题关联

- [todesk-ai](../todesk-ai/index.md)：另一类给 Agent 的跨设备助手工具（Agent 工具生态相邻）
- [wigolo](../wigolo/index.md)：以 Skill/工具形态提升 Agent 能力（信息获取侧），oil-ui 专注"界面表达侧"，互补
- [ian-xiaohei-illustrations](../ian-xiaohei-illustrations/index.md)：同属"开源 AI Skill 做视觉产出"主题，前者定位中文文章配图、后者定位界面向

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```