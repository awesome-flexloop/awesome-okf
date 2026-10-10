---
okf_version: "0.2"
type: "Wiki Tutorial"
title: "huashu-art-motion：项目身份与定位"
description: "花叔（alchaincyf）的开源艺术动画 Skill——用代码让艺术风格动起来，35 风格配方卡、9 解说语法、MIT 许可，附 Star 数勘误"
tags: [huashu-art-motion, ai-skill, art-animation, code-drawing, canvas, open-source]
sources:
  - id: wechat
    url: https://mp.weixin.qq.com/s/BbsIpq82oAq7RPusw_jHXA
  - id: github-repo
    url: https://github.com/alchaincyf/huashu-art-motion
generated:
  by: "seven-concepts-cmd+wechat-public-okf:I"
  at: "2026-10-10T12:40:00+08:00"
status: stable
stale_after: 2027-01-31
---

# huashu-art-motion：项目身份与定位

> **信源**：微信公众号「开源星探」推介文（2026-10-07）经 GitHub 一手 README 交叉核验。本页为事实层。
> **必读勘误**：文章标题称「开源一天收获 1.3K Star」**失实**——GitHub 实测仅 **41 stars**（2026-10-10），见 [references/verification.md](../references/verification.md)。

## 一、它是什么

**huashu-art-motion**（"艺术动画"）是独立开发者花叔（Huashu，GitHub `alchaincyf`）开源的一个 **AI coding Agent Skill**，目标是让 coding agent 用**纯代码绘制**把艺术风格"做成会动的画"（[F-006](../references/article-source.md)）。

核心口径（官方副标题）：**35 种艺术风格 · 9 种解说语法 · 8 种参数化片段 · 口播整片参考代码**（F-037）。

## 二、关键身份事实

| 项 | 值 | 出处 |
|----|-----|------|
| 仓库 | `https://github.com/alchaincyf/huashu-art-motion` | F-004/F-032 |
| 作者 | 花叔（Huashu），GitHub `alchaincyf`，官网 bookai.top / huasheng.ai | F-053/F-004 |
| 开源时间 | 首批 commit `445c075` 于 2026-10-06 | F-032/F-034 |
| 许可 | MIT（代码与文档）；角色帧/字体有例外 | F-049/F-053 |
| 语言 | JavaScript 96.1% + Python 3.8% + HTML | F-051 |
| 热度（2026-10-10 时点） | **41 stars** / 6 forks / 0 watching | F-034 |

## 三、它解决的独特问题

这不是 AI 生图那种「画得像梵高」，而是**纯代码绘制**：

- 星星的位置用数学公式算，笔触的粗细和颜色用参数控制，画面用代码一层层叠出来（F-006）。
- 「真正意义上的用代码画画」——每个画风配一个可运行的 Canvas 场景、一个渲染器、一个签名转场（F-008）。

它与 AI 生图的分工（F-031/F-049）：**场景、转场、运动**用代码完成；只有**"人"**很难用代码画得像，所以人物交给生图模型出帧，代码负责帧间过渡、换帧节奏和材质合成——让卡通形象在不同画风里保持一致。

## 四、来源背景（一文读懂演化脉络）

1. 花叔此前做过更出名的 **huashu-design**——让 coding agent 一句话生成可交付的 App 原型、PPT、时间轴动画（F-005）。
2. huashu-art-motion 是把「终端里做设计」往深走，聚焦"纯代码绘制艺术风格动画"这个更难的具体方向（F-005）。
3. 官方自述演化史：X 上看到 Tak 的 15 秒《Art History Speedrun》→ 让 Claude 复刻并积累经验 → 派 4 组只读 agent 做 20 种新风格、收成统一库 → 接 8 种解说语法进口播管线 → 最后做成《花叔穿越名画》23 画风、2 分 08 秒（F-041）。

## 五、三条谨慎边界

1. **不要引用"1.3K Star"**——实测 41，动态数，引用须带时点（F-007/verification ①）。
2. **解说语法是 9 种不是 8 种**——8 种附示范片 + 第9种讲解员式财经科普（F-013/F-037）。
3. **"万星项目"未经本仓库核证**——指 huashu-design 的 Star 量级，不擅自引用（F-046）。

---
下一步：[35 风格配方卡与 9 解说语法机制](01-art-style-recipes.md) → [动画工程工作流与可迁移实践](02-engineering-workflow.md)