---
okf_version: "0.2"
type: bundle
title: "huashu-art-motion：用代码让艺术风格动起来"
description: "花叔（alchaincyf）开源的艺术动画 Skill——35 风格配方卡、9 解说语法、8 参数化片段、拆解/QA 工程闭环，源自开源星探微信推介文经 GitHub 一手核验"
tags: [huashu-art-motion, ai-skill, art-animation, code-drawing, canvas, open-source, 博文转化]
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T13:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T13:05:00+08:00"
status: stable
stale_after: 2027-01-31
sources:
  - id: wechat
    url: https://mp.weixin.qq.com/s/BbsIpq82oAq7RPusw_jHXA
  - id: github-repo
    url: https://github.com/alchaincyf/huashu-art-motion
  - id: github-readme
    url: https://raw.githubusercontent.com/alchaincyf/huashu-art-motion/main/README.md
---

# huashu-art-motion：用代码让艺术风格动起来

> **类型**：技术教程 / 开源 Skill 产品解析（含可照做示例，操作可复现性两问皆"是"）
> **信源**：微信公众号「开源星探」推介文（2026-10-07）→ 2026-10-10 经 GitHub 官方仓库页与 README 逐项核验
> **核验结论**：15 项 P0/P1 声明 **12✅ / 1⚠️ / 2❌**；两处必读勘误（Star 数、语法数 8 vs 9）
> **数据时点**：Star 等动态数字为 2026-10-10 快照

## 本文概要

[huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) 是独立开发者花叔（alchaincyf）开源的一支 **Coding Agent Skill**，用**纯代码绘制**把艺术风格做成"会动的画"：`35 种艺术风格配方卡·9 种解说语法·8 种参数化片段·口播整片参考代码`。场景/转场/运动用代码完成，只有"人"交给生图模型出帧再合成，从而在不同画风里保持角色一致。配套拆解脚本（转场/节拍/运动热图）、QA 脚本（五维度数字验收 + 旁观者审查）、纯代码配乐与长卷穿越片骨架，官方把它定位为一个**动画工程的脚手架**。

## 阅读路径

**先建立概念（15 分钟）**

1. [项目身份与定位](concepts/00-what-is-huashu-art-motion.md)——它是谁、解决什么独特问题、3 条谨慎边界（含 Star 数勘误）
2. [35 艺术风格配方卡与 9 解说语法机制](concepts/01-art-style-recipes.md)——三套核心资产 + 长卷穿越片骨架
3. [动画工程工作流与可迁移实践](concepts/02-engineering-workflow.md)——拆解/QA/配乐闭环 + 3 条跨场景洞察 + 版权合规范式

**再动手实操**（见 concepts/02 §5）

4. `npx skills add alchaincyf/huashu-art-motion` → 试渲梵高一帧 → 渲完整财经图表动画

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 作者 | [alchaincyf/huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion)（花叔 Huashu） |
| 开源时间 / 许可 | 2026-10-06 / MIT（角色帧/字体有例外） |
| 社区数据（2026-10-10 时点） | **41 stars**、6 forks、0 watching |
| 核心资产 | 35 风格配方卡 + 35 场景代码、9 解说语法（8 附示范片）、8 参数化片段、17 动画库、12 方法文档 |
| 工程脚本 | `scripts/analyze/breakdown.py`（拆解）、`scripts/qa.py`（验收）、`scripts/audio/`（配乐） |
| 试渲命令 | `python scripts/engine/render.py --solo 09_postimp --stills 0.3 --out 试渲` |
| 依赖 | uv / ffmpeg / Playwright Chromium |
| 语言 | JavaScript 96.1% + Python 3.8% |

## ⚠️ 阅读前必知的两条勘误

1. **Star 数失实**：文章标题「开源一天收获 1.3K Star」与 GitHub 实测 **41 stars**（2026-10-10）严重不符，正文一律不沿用，引用须带时点。
2. **语法数是 9 非 8**：文章衔接处写"8 种解说语法"，官方 README 为 **9 种**（8 种附示范片 + 第9种讲解员式财经科普）；文章核心段其实也写 9，属内部自相矛盾，以官方 9 为准。

## 采用提示与已知边界

- **热度很低但工程价值高**：当前仅 41 stars，是刚开源一天的新项目，动态迭代快；但拆解/QA/配方卡/版权合规等方法论对"生产型 AI Skill 设计"有可复用价值。
- **"万星项目"未经核证**：指 huashu-design（另一项目）的 Star 量级，本知识包不擅自引用。
- **安装坑真实存在**：skill 为多目录结构（非单 SKILL.md），skills CLI 旧版只同步单文件会缺依赖；"≤1.5.15""99 处"为文章口径，官方未列版本阈值。
- **数字时效**：Star/功能集为 2026-10-10 快照，`stale_after: 2027-01-31`，到期前复核。

## 信源与可信度

- 事实清单与逐条核验状态：[references/article-source.md](references/article-source.md)（F-001~F-054）
- P0 核验报告与勘误清单：[references/verification.md](references/verification.md)（15 项：12✅/1⚠️/2❌）
- 信源距离：第三方开源推介号（开源星探）转述 → 已升级为 GitHub 官方 README 一手交叉核验；推介文特有数值（1.3K、8 语法、99 处、1.5.15）均已按官方口径指正或标注文章口径

## 主题关联

- [ian-xiaohei-illustrations](../ian-xiaohei-illustrations/index.md)：同为开源 AI Skill 视觉类产品（中文文章认知锚点配图），对比"生图配图"vs"代码绘制动画"两种风格路线
- [3Blue1Brown 生态](../../../viz/3b1b/index.md)：同属"用代码做视觉/动画"方向（Manim vs 纯 Canvas 艺术动画）
- [text-to-cad](../text-to-cad/index.md)：同为面向 Agent 的技能库，输出确定性工程产物（CAD 源码 vs 动画）

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```