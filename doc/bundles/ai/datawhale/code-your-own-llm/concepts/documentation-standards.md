---
title: 文档写作规范体系
type: concept
bundle: /datawhale/code-your-own-llm
description: code-your-own-llm 在 AGENTS.md 中定义的七大维度 Markdown 写作规范，涵盖结构、内容、图像、表格、代码、公式和参考文献。
related:
  - /datawhale/code-your-own-llm/concepts/fullstack-learning-path
  - /datawhale/code-your-own-llm/references/readme-source
sources:
  - id: github-repo
    resource: /references/readme-source.md
    title: code-your-own-llm GitHub 仓库
---

# 文档写作规范体系

code-your-own-llm 将文档质量视为项目成熟度的核心指标。项目根目录的 `AGENTS.md` 实际是"第零章 格式模板和规范指南"，为所有 Markdown 文档定义了统一的写作标准。这套规范覆盖七个维度，确保全书风格一致、可读性强。

## 规范的定位

`AGENTS.md` 不是普通的贡献指南，而是被提升为"第零章"的正式教学内容。这意味着：

- 规范本身是学习者需要了解的第一课
- 文档与代码具有同等重要性
- 所有贡献者（包括 AI Agent）必须遵循同一套标准

## 七大维度概览

### 1. 结构规范

- 采用三级标题体系（`#` 章节、`##` 一级、`###` 二级、`####` 三级）
- 禁止出现孤立的三级标题
- 章节标题后必须有一段无标题序言概括核心内容
- 每个一级标题段落前后空行
- 段落长度适中，适合阅读并保持注意力

### 2. 内容规范

- 中文为主，英文作为辅助语言
- 英文术语使用反引号包裹（如 `transformer`）
- 中英文混排时英文两侧留空格（紧邻标点侧除外）
- 首行缩进使用 `&emsp;` 实现
- 叙述主体统一使用"我们"
- 强调用 `<strong>`，引用标记用 `<sup>`

### 3. 图像规范

- 格式：PNG 或 GIF
- 图中文字：中文宋体、英文 Times New Roman
- 必须包含 caption（图像下方居中）
- 编号格式 `x.y`（章节号.序号）
- 正文必须引用对应图像

### 4. 表格规范

- 必须包含 caption（表格上方居中）
- 编号格式 `x.y`
- 正文必须引用对应表格

### 5. 代码规范

代码规范是七维度中最详细的部分，核心要求包括：

- **语言标注**：代码块开头必须标注语言（`python`/`bash`/`json`）
- **风格指南**：遵循 Google Python Style Guide
- **文档字符串**：函数必须包含 docstring，含描述、Args、Returns、Raises
- **类型注解**：所有函数参数和返回值使用 Type Hints
- **类文档**：类需说明用途和 Attributes
- **行内代码**：用单反引号包裹
- **命令行**：统一用 `bash` 标注
- **长度控制**：代码块不超过 50 行，超长代码只展示关键部分或引用 `code/` 目录

### 6. 公式规范

- 使用 LaTeX 语法
- 行内公式 `$...$`，独立公式 `$$...$$`
- 重要公式编号 `(x.y)`
- 排版约定：变量斜体、函数名正体、向量矩阵粗体、集合花体
- 统一了六类数学符号：数组、集合索引、线性代数、微积分、概率信息论、常用函数

### 7. 参考文献规范

- 遵循 APA Style
- 一般链接直接用 markdown 语法
- 正式出版物需添加引用标记和参考文献列表

## 规范背后的设计意图

这套规范的严格程度远超一般开源项目，原因在于：

1. **教学场景需求**：读者是学习者，不一致的格式会分散注意力
2. **多人协作保障**：Datawhale 社区多人协作，统一规范降低合并冲突
3. **AI 协作友好**：AGENTS.md 的命名暗示它也面向 AI Agent，明确的规范让 AI 生成内容时有据可依
4. **出版级质量**：规范接近技术书籍的排版标准，而非随意的博客文章

## 对贡献者的启示

为项目贡献内容前，应先逐条对照 AGENTS.md 检查：

- 标题层级是否正确，有无孤立三级标题
- 英文术语是否用反引号，中英文空格是否规范
- 代码是否有完整的 docstring 和类型注解
- 图表是否有 caption 和编号，正文是否引用
- 公式排版是否符合斜体/正体/粗体约定

## 相关概念

- [全栈式 LLM 学习路径](fullstack-learning-path.md)——规范所服务的 12 章教学内容
- [信源登记](../references/readme-source.md)——AGENTS.md 所在的官方仓库
