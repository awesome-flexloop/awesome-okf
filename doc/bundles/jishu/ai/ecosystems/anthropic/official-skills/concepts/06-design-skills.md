---
type: concept
title: "设计与创意类 Skills 详解"
description: "algorithmic-art/canvas-design/theme-factory/frontend-design/brand-guidelines/slack-gif-creator/web-artifacts-builder 七个设计类 Skill 的用途、结构、编写规范与可复用模式。"
tags: [skills, design, creative, generative-art, theme, frontend, official-skills]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# 设计与创意类 Skills 详解

覆盖 7 个 skill：`algorithmic-art`、`canvas-design`、`theme-factory`、`frontend-design`、`brand-guidelines`、`slack-gif-creator`、`web-artifacts-builder`。

这组 skill 呈现两种截然不同的取向：**生成型**（靠"哲学生成"骨架产出作品）与**规范型**（提供配色/字体/组件的固定约束）。

---

## 一、生成型：共享"哲学生成"骨架

`algorithmic-art`（404 行）与 `canvas-design`（129 行）的 SKILL.md **前 5 个二级标题完全同构**（F-060、F-096）：

```
DESIGN PHILOSOPHY CREATION / DESIGN PHILOSOPHY CREATION
  THE CRITICAL UNDERSTANDING
  HOW TO GENERATE A VISUAL PHILOSOPHY
  PHILOSOPHY EXAMPLES
  ESSENTIAL PRINCIPLES
DEDUCING THE CONCEPTUAL SEED / SUBTLE REFERENCE
<实现阶段>
```

### 为什么先写"哲学"

两个 skill 都**拒绝直接给参数**。流程是：

```
理解主题本质（CRITICAL UNDERSTANDING）
  → 推导出一句"视觉哲学"（HOW TO GENERATE A VISUAL PHILOSOPHY）
  → 从哲学推出具体参数（ESSENTIAL PRINCIPLES）
  → 实现
```

区别只在推导的对象：

| skill | 推导物 | SKILL.md 章节名 |
|-------|-------|---------------|
| algorithmic-art | **概念种子**（conceptual seed） | `DEDUCING THE CONCEPTUAL SEED` |
| canvas-design | **微妙参照**（subtle reference） | `DEDUCING THE SUBTLE REFERENCE` |

`algorithmic-art` 还多一整节 `## INTERACTIVE ARTIFACT CREATION`，专门讲生成器与查看器的分离。

### algorithmic-art 的独有机制

| 机制 | 说明 |
|------|------|
| **种子随机**（F-093） | seeded randomness 保证同种子同结果，可复现 |
| **FIXED vs VARIABLE**（F-092） | 独立段落声明哪些不变、哪些每次变 |
| **生成器/查看器分离** | `templates/generator_template.js` + `templates/viewer.html`（F-059）——生成与预览解耦 |
| **版权自律** | description 明写 "Create original algorithmic art rather than copying existing artists' work" |
| **资源收尾** | `## RESOURCES` 段落列出可用素材 |

> 🟢 **可复用模式（生成类）**：把"创意"拆成**抽象层 → 推导层 → 实现层**三段，抽象层先固定一个可复述的一句话判断标准。这样输出多样性可控，且失败时能定位是抽象偏了还是实现偏了。

### canvas-design 的独有资源

`canvas-fonts/` 含 **54 个 TTF、27 个 OFL.txt、29 个字体家族**（F-053）。家族包括 ArsenalSC、BigShoulders、Boldonse、BricolageGrotesque、CrimsonPro、DMMono、EricaOne、GeistMono、Gloock、IBMPlexMono、IBMPlexSerif、InstrumentSans、InstrumentSerif、Italiana、JetBrainsMono、Jura、LibreBaskerville、Lora、NationalPark、NothingYouCouldDo、Outfit、PixelifySans、PoiretOne、RedHatMono、Silkscreen、SmoochSans、Tektur、WorkSans、YoungSerif。

🔴 **`IBMPlexSerif` 与 `InstrumentSerif` 两个家族缺少 OFL.txt 许可声明**（F-054）。商用前须单独确认授权。

---

## 二、规范型：把设计系统固化成资源

### theme-factory —— 主题工厂

| 维度 | 内容 |
|------|------|
| **用途** | 10 套预设主题，套用到幻灯片/文档/落地页/报表；也可即时生成新主题 |
| **SKILL.md** | 59 行（19 个中最短的有资源 skill） |
| **资源** | `themes/`（10 个 **`.md`**）+ `theme-showcase.pdf` |

### 🔴 主题是 Markdown 不是 JSON（F-055）

社区与多数人的预期是 `themes/*.json`，实际磁盘上是 **10 个 `.md` 文件**（F-055）。这带来一个直接好处——**主题本身是人读散文**，不需要解析器就能理解。

统一结构（F-057）：

```markdown
# Arctic Frost

A cool and crisp winter-inspired theme that conveys clarity, precision, and professionalism.

## Color Palette

- **Ice Blue**: `#d4e4f7` - Light backgrounds and highlights
- **Steel Blue**: `#4a6fa5` - Primary accent color
- **Silver**: `#c0c0c0` - Metallic accent elements
- **Crisp White**: `#fafafa` - Clean backgrounds and text

## Typography

- **Headers**: DejaVu Sans Bold
- **Body Text**: DejaVu Sans

## Best Used For

Healthcare presentations, technology solutions, winter sports, clean tech, pharmaceutical content.
```

每个主题 4 段固定：**标题 → 一句话定位 → Color Palette（命名色 + hex + 用途）→ Typography → Best Used For**。

> 🟢 **可复用模式（主题/配色类）**：色板用**「命名色 + hex + 用途」三段式**而非裸 hex 列表。命名色（Ice Blue）给 AI 语义锚点，hex 给程序锚点，用途说明防止误用（如只适合背景的浅色不能拿去当正文色）。
>
> `Best Used For` 段同样重要——它让 AI **能判断适不适合当前场景**，而不是无脑套用。

### brand-guidelines —— 品牌规范

| 维度 | 内容 |
|------|------|
| **用途** | 应用 Anthropic 官方品牌色与排版 |
| **SKILL.md** | 73 行 |
| **资源** | 无（纯指令，色彩与字体写在正文里） |

结构：

```
# Anthropic Brand Styling
## Overview
## Brand Guidelines
  ### Colors
  ### Typography
## Features
  ### Smart Font Application
  ### Text Styling
  ### Shape and Accent Colors
## Technical Details
  ### Font Management
  ### Color Application
```

注意 `## Features` 与 `## Technical Details` 的分工：**Features 讲"怎么用"（智能字体应用、文本样式化、形状与强调色），Technical Details 讲"底层怎么管"（字体管理、颜色应用）**。

> 🟢 **可复用模式**：品牌/规范类 skill 要同时给出**面向应用者的用法**与**面向实现的细节**两段。只给色值表，AI 不知道何时该用哪个色。

### frontend-design —— 前端设计方向

| 维度 | 内容 |
|------|------|
| **用途** | 有意图的视觉设计指导——字体、排版、克制原则，规避"模板感"默认输出 |
| **SKILL.md** | 71 行 |
| **资源** | 无（纯指令） |

结构：

```
# Frontend Design
## Ground your designs in the subject matter
## Design principles
## Process: plan, review against the brief, build, critique
## Restraint and self-critique
## More on writing in design
```

两个亮点：

1. **`## Process: plan, review against the brief, build, critique`**——四步闭环，其中 "review against the brief"（对照需求复核）与 "critique"（自我批判）是与 `pptx` 三层 QA 呼应的方法论。
2. **`## Restraint and self-critique`**——单独立段讲克制与自省。这针对的是模型默认输出"看起来很 AI"的问题。

> 🟢 **可复用模式**：设计类 skill 应把**"对照 brief 复核"与"自我批判"写成流程步骤**，而非指望模型自觉。只给原则不给复核步骤，模型不会真的回头看。

---

## 三、工程型创意：把产出物交给脚本

### slack-gif-creator —— Slack 动图

| 维度 | 内容 |
|------|------|
| **用途** | 生成适配 Slack 规格的动图（尺寸/帧率/体积受限） |
| **SKILL.md** | 254 行 |
| **资源** | `core/`（4 py）+ `requirements.txt` |

### core/ 四个模块（F-072）

| 模块 | 职责 |
|------|------|
| `gif_builder.py` | `GIFBuilder` 类——默认 **480×480 @ 15fps**，add_frame / add_frames / optimize_colors / deduplicate_frames / save |
| `frame_composer.py` | 帧合成 |
| `easing.py` | 缓动函数库 |
| `validators.py` | 校验（快速检查 + 详细验证两档） |

`easing.py` 通过 `EASING_FUNCTIONS.update({... "back_out": ease_back_out ...})` 注册缓动函数，**包含 `back_out`**（F-073）。

结构骨架：

```
# Slack GIF Creator
## Slack Requirements
## Core Workflow
## Drawing Graphics
  ### Working with User-Uploaded Images / Drawing from Scratch
  ### Making Graphics Look Good
## Available Utilities
  ### GIFBuilder / Validators / Easing Functions
```

### 编写规范要点

- **先讲平台约束**（`## Slack Requirements` 置于最前）——目标平台的规格决定一切，先说清约束
- **两档校验**——quick check 与 detailed validation 分开，匹配不同阶段的成本
- **导入式接口**——与 `with_server.py` 的命令行式不同，这个 skill 鼓励 `from core.gif_builder import GIFBuilder` 的模块导入用法

### web-artifacts-builder —— 复杂 Web 构件

| 维度 | 内容 |
|------|------|
| **用途** | 多组件 HTML artifact（React + Tailwind + shadcn/ui），**不适合简单单文件 HTML/JSX** |
| **SKILL.md** | 73 行 |
| **资源** | `scripts/`（**2 个 shell 脚本** + 1 个 tar.gz） |

### 🔴 唯一使用 Shell 脚本的 skill（F-074）

```
scripts/init-artifact.sh
scripts/bundle-artifact.sh
scripts/shadcn-components.tar.gz
```

19 个 skill 中只有它用 shell 而非 Python——因为流程本质是 **scaffold → 开发 → 打包成单文件**（见 [skills-index](../references/skills-index.md) 的 5 步 Quick Start）。

description 里明确划界：*"Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts."*

> 🟢 **可复用模式**：**description 里写清"何时不适用"**。web-artifacts-builder 的边界声明（复杂构件 vs 单文件）让它不会在简单场景被误触发——这正是 `claude-api` 的 SKIP 机制的一般化版本。

---

## 四、七者横向对比

| skill | 体量 | 有无脚本 | 核心资产 | 输出类型 |
|-------|------|---------|---------|---------|
| algorithmic-art | 404 行 SKILL.md + 2 模板 | ❌ | 哲学生成骨架 + 种子随机 | 交互式生成艺术（JS） |
| canvas-design | 129 行 + 54 字体 | ❌ | 同上骨架 + 字体库 | 静态视觉（PNG/PDF） |
| theme-factory | 59 行 + 10 主题 | ❌ | 主题集 | 配色/字体方案 |
| frontend-design | 71 行 | ❌ | 设计原则 + 四步流程 | 设计方向（指导） |
| brand-guidelines | 73 行 | ❌ | 色值 + 字体规范 | 品牌化产出 |
| slack-gif-creator | 254 行 + 4 py | ✅ | GIFBuilder + 缓动 + 校验 | GIF |
| web-artifacts-builder | 73 行 + 2 sh | ✅ | scaffold + 打包流程 | 单文件 HTML |

> 📊 值得注意：7 个设计类 skill 中 **5 个零脚本**。设计的产出质量主要靠**约束与流程**保证，不靠工具保证——只有需要生成特定二进制/工程文件时才引入脚本。

---

## 相关文档

- [全部Skills索引](../references/skills-index.md) — 19 个 skill 速查
- [事实登记表](../references/facts.md) — F-053~F-060 资源实测
- [Skill 编写规范与可复用模式](04-authoring-patterns.md) — 跨 skill 通用模式
