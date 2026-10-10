---
okf_version: "0.2"
type: concept
title: "oil-ui 是什么：一个给 AI 的 UI 设计 Skill"
description: "项目定位、作者线索、三大痛点——为什么 AI 做的界面总是模板味"
sources:
  - id: github-repo
    resource: https://github.com/oil-oil/oil-ui
  - id: blog
    resource: https://mp.weixin.qq.com/s/JqY_1JW1FSMQU3XAQyTRPA
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T00:00:00+08:00"
status: stable
stale_after: 2027-03-31
---

# oil-ui 是什么：一个给 AI 的 UI 设计 Skill

## 一句话定位

[oil-ui](https://github.com/oil-oil/oil-ui) 不是"教 AI 什么是好设计"，而是一套**给 AI 编程 Agent 装的设计方法论 Skills**——把设计过程拆成一行行可执行的施工图纸（八步设计法），强制 AI 跳出"默认 Inter + Tailwind + 圆角卡片"的模板思维，一次产出多个**可对比**的设计方向（F-003）。

它是 **Agent Skill**，不是独立工具：安装在 Claude Code、Cursor、Codex 等 Agent 上，参与 Agent 生成界面的决策过程（F-001）。

## 作者线索

作者油子（Zhihuang Lin）此前做过两个相邻项目（F-002 / F-021✅）：

- [beautify-github-readme](https://github.com/oil-oil)：GitHub README 画廊级排版美化。
- [oiloil-ui-ux-guide](https://github.com/oil-oil/oiloil-ui-ux-guide)：风格中性的 UI/UX 咨询 Skill，引入 CRAP（对比/重复/对齐/邻近）与 Fitts's law。

oil-ui 是他"从**教设计**到**给施工图纸**"的转向之作（F-002）。

## 三大痛点：为什么 AI 界面总"一眼假"

oil-ui 针对三类典型问题（F-005 ~ F-007）：

| # | 痛点 | 表现 |
|---|------|------|
| 痛点一 | 缺乏判断标准 | 不知道什么样算"好"，只能堆通用组件 |
| 痛点二 | 默认懒方案 | 每个页面长一个样：Inter 字体 + Tailwind 默认调色板 + 8px 圆角 + 淡阴影（F-007） |
| 痛点三 | 不会拉开方向 | 给一个需求只出一个方案，无法在风格间取舍、迭代 |

## 与相邻概念的关系

- **不是设计规范文档**：它是可执行的流程，不是风格指南。
- **不是 UI 组件库**：它不提供按钮/卡片，而是决定"该用什么样的按钮/卡片"的方法。
- **输入→输出**：输入需求与受众 → 输出 3 个拉开差别的对比方向 + 推荐 + 修改建议（F-004）。

## 何时适合用它

- 用 Agent 生成落地页、Dashboard、表单、产品界面，但嫌输出"模板气"。
- 需要在多个设计方向间做决策，而不只是接受唯一答案。
- 想让 Agent 具备可解释的设计理由（每步有判断依据）。

---
**本概念支撑事实**：F-001、F-002、F-003、F-004、F-005、F-006、F-007、F-021。