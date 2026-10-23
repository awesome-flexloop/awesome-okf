---
type: concept
title: "文档处理类 Skills 详解"
description: "docx/pdf/pptx/xlsx/doc-coauthoring 五个文档类 Skill 的用途、结构、编写规范与可复用模式，含 OOXML 共享子树设计与三层 QA 机制。"
tags: [skills, docx, pdf, pptx, xlsx, ooxml, document, official-skills]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# 文档处理类 Skills 详解

覆盖 5 个 skill：`docx`、`pdf`、`pptx`、`xlsx`、`doc-coauthoring`。

它们是 19 个官方 skill 中**最重工程化**的一组——前四个都把 OOXML/文档格式的脏活封装成可复用脚本，第五个则把"写文档"这件事本身流程化。

---

## 一、共同架构：共享的 `office/` 子树

`docx`、`pptx`、`xlsx` 三个 skill 的 `scripts/office/` 子树**逐字节完全相同**（F-044，逐文件 md5 比对一致），各 50 个文件：

```
scripts/office/
├── soffice.py          # LibreOffice headless 封装（沙箱适配）
├── validate.py         # OOXML 文件校验入口
├── helpers/            # 4 文件：__init__.py, pptx_chart.py, pptx_slide.py, pptx_theme.py
├── validators/         # 5 文件：__init__.py, base.py, docx.py, pptx.py, redlining.py
└── schemas/            # 39 个 XSD
```

### 39 个 XSD 的构成（F-046）

| 来源 | 数量 | 用途 |
|------|------|------|
| ISO-IEC 29500-4_2016 | 27 | OOXML 主规范（wordprocessingml / spreadsheetml / presentationml / dml 等） |
| ECMA | 1 | ECMA-376 基础 |
| MCE | 1 | Markup Compatibility and Extensibility |
| Microsoft | 7 | MS 扩展（vml / office 扩展等） |

### 🔴 一个反直觉的设计细节

`helpers/` 下的三个文件**全是 PPTX 专用**（`pptx_chart.py`、`pptx_slide.py`、`pptx_theme.py`），但 `docx` 和 `xlsx` **也各自携带一份**（F-047）。

原因：共享子树是**整块复制**而非按需裁剪。代价是 docx/xlsx 多带了约 3 个无用文件，收益是三个 skill 的 `office/` 目录结构永远一致——**升级、审计、验证只需维护一份**。

> 🟢 **可复用模式**：当多个 skill 共享同一套基础设施时，**宁可整块复制也不要抽公共包**。独立目录让每个 skill 都能被单独分发、单独版本化，不会因公共依赖变动而连带失效。

### 三件套的差异化

| skill | 顶层脚本 | 模板 | 总文件 | .py |
|-------|---------|------|-------|-----|
| **docx** | `__init__.py` `accept_changes.py` `comment.py` `merge_runs.py` | `scripts/templates/`（5 XML） | 61 | 15 |
| **pptx** | `__init__.py` `add_slide.py` `clean.py` `thumbnail.py` | — | 56 | 15 |
| **xlsx** | `recalc.py`（**无 `__init__.py`**） | — | 53 | 12 |

⚠️ `docx/scripts/templates/` 与 `scripts/office/` 是**兄弟目录**，模板不在 office 内（F-050）。5 个模板文件：

```
comments.xml  commentsExtended.xml  commentsExtensible.xml  commentsIds.xml  people.xml
```

这些是 Word 批注功能的 XML 骨架——`comment.py` 往里写入批注，`accept_changes.py` 处理修订。

---

## 二、docx —— Word 文档

| 维度 | 内容 |
|------|------|
| **用途** | 创建、读取、编辑 `.docx` / `.dotx`；接受修订、加批注、合并 run、OOXML 校验 |
| **SKILL.md** | 91 行（最短的工程类 skill） |
| **资源** | `scripts/`（4 顶层 py）+ `scripts/templates/`（5 XML）+ 共享 `scripts/office/` |
| **许可** | Anthropic 专有（source-available，非开源） |

### 结构骨架

```
# DOCX creation, editing, and analysis
## Creating with docx-js — gotchas
## Verify the output
## Editing existing documents
## Comments
## Dependencies
```

### 编写规范要点

1. **"gotchas" 段独立成节**——专门记录"照着官方文档做也会错"的地方
2. **编辑现有文档时禁止重排 XML**：`edit unpacked/word/document.xml in place — do NOT reformat or pretty-print`（原文注释即规范）
3. **redlining 需指定作者**：`add --author "<the name you redlined under>" to check every edit is tracked`
4. **验证独立成节**——`## Verify the output` 与创建段并列，不是可选尾巴

### 可复用模式

🟢 **XML 原地编辑原则**：解压 → 改 XML → 重新打包，任何格式化（pretty-print）都会改变字节流、可能破坏 OOXML 校验。这条对所有 OOXML 处理场景通用。

---

## 三、pdf —— PDF 处理

| 维度 | 内容 |
|------|------|
| **用途** | 读写 PDF 全流程：提取文本/表格、合并拆分、旋转、水印、表单填充、OCR |
| **SKILL.md** | 314 行 |
| **资源** | `scripts/`（8 个 py）+ `forms.md` + `reference.md` |
| **许可** | Anthropic 专有 |

### 8 个脚本的职责

| 脚本 | 职责 |
|------|------|
| `extract_form_structure.py` | 提取表单结构 |
| `extract_form_field_info.py` | 提取字段信息 |
| `fill_fillable_fields.py` | 填充可填字段 |
| `fill_pdf_form_with_annotations.py` | 用批注方式填充（不可填表单的降级路径） |
| `check_fillable_fields.py` | 检查可填字段 |
| `check_bounding_boxes.py` | 检查边界框（验证渲染是否越界） |
| `convert_pdf_to_images.py` | PDF 转图片（供视觉检查） |
| `create_validation_image.py` | 生成验证用对照图 |

### 编写规范要点

正文覆盖三个 Python 库的分层用法：

- **pypdf** —— 基本操作（读、合并、拆分、旋转、加水印、加密）
- **pdfplumber** —— 文本与表格提取
- **reportlab** —— 创建 PDF

并附 CLI 工具（`pdftotext` 等 poppler-utils）。

### 🔴 两个真实存在的文档缺口（F-051、F-052）

| 缺口 | 表现 | 实务影响 |
|------|------|---------|
| **正文从不引用自己的 `scripts/` 目录** | SKILL.md 全文 grep `scripts` 仅 4 处命中，且全部是 "sub**scripts**"/"super**scripts**" 子串 | 脚本是"孤立资产"——必须自行判断该调哪个，无法照着正文直接用 |
| **参考文档大小写不一致** | 磁盘上是 `forms.md` / `reference.md`（小写），正文引用 `FORMS.md` / `REFERENCE.md`（大写） | **Linux 上按正文指引会取不到文件**；Windows/macOS 默认大小写不敏感，掩盖了这个问题 |

> 🟢 **可复用模式（反向）**：写 skill 时，**正文中出现的每个资源路径都要能被人和模型找到**。作者本机的大小写不敏感会掩盖错误，直到 skill 在 Linux 沙箱里跑才暴露。

---

## 四、pptx —— PowerPoint

| 维度 | 内容 |
|------|------|
| **用途** | `.pptx` / `.potx` 的创建、读取、编辑、拆分合并；设计规范与三层 QA |
| **SKILL.md** | 238 行 |
| **资源** | `scripts/`（4 顶层 py）+ 共享 `scripts/office/` |

### 结构骨架

```
# PPTX creation, editing, and analysis
## Scripts
## Creating with pptxgenjs — gotchas
## Editing existing decks and templates
## Design Ideas
   ### Before Starting / Color Palettes / For Each Slide / Typography / Spacing / Avoid (Common Mistakes)
## QA (Required)
   ### Content QA / File QA (required) / Visual QA
## Converting to Images
## Dependencies
```

### 🔴 三层 QA 机制（本 bundle 最值得抄的模式）

`## QA (Required)` 被**显式标为必需**，分三层：

| 层 | 检查什么 | 怎么查 |
|----|---------|--------|
| **Content QA** | 内容正确性（文字、逻辑、占位符残留） | 读生成的 XML/文本 |
| **File QA (required)** | 文件结构合法（能否被 PowerPoint 打开、XML 是否合规） | `scripts/office/validate.py` + XSD 校验 |
| **Visual QA** | 视觉呈现（排版、溢出、重叠） | `scripts/thumbnail.py` 转图后**看图** |

> 🟢 **可复用模式**：任何"生成可交付物"的 skill 都该有这三层——内容对不对、文件合不合法、看起来好不好。**三层缺一不可**：只有 Content QA 会漏掉打不开的文件，只有 File QA 会漏掉排版崩掉的稿。
>
> `pptx` 还提供了 `Avoid (Common Mistakes)` 反面清单，与 `Color Palettes`/`Typography`/`Spacing` 正向规范并列——**正面给标准 + 反面给禁区**，比单给标准有效得多。

### 编辑既有演示文稿的路径

```
# reorder / delete slides = edit <p:sldIdLst> in ppt/presentation.xml
# edit slide content in ppt/slides/slideN.xml
```

即：同样遵循"改 XML 不重排"的原地编辑原则（与 docx 一致）。

---

## 五、xlsx —— 电子表格

| 维度 | 内容 |
|------|------|
| **用途** | `.xlsx`/`.xlsm`/`.xltx`/`.csv`/`.tsv` 的读写、清洗、公式、报表 |
| **SKILL.md** | 99 行（最短的工程类 skill） |
| **资源** | `scripts/recalc.py` + 共享 `scripts/office/` |

### 结构骨架

```
# XLSX creation, editing, and analysis
## Requirements for every output
## Recalculate (mandatory whenever the file contains formulas)
## Choosing formulas that survive verification
## openpyxl gotchas
## Financial models
## Dependencies
```

### 编写规范要点

1. **公式必须重算**——`## Recalculate (mandatory whenever the file contains formulas)`。openpyxl 写公式只是写字符串，不算结果；必须调 `scripts/recalc.py`（经 LibreOffice）让缓存值落地，否则用 Excel 打开前读到的是空值。
2. **选"能通过验证的公式"**——`## Choosing formulas that survive verification`：优先选能被工具校验的表达式，而非只在新版 Excel 里才支持的动态数组公式。
3. **有独立的财务模型约定段**——`## Financial Models` 针对金融场景补充了建模规范。

> 🟢 **可复用模式**："写出来 ≠ 用户看到的结果"——凡是程序写入的内容需要被目标应用**重新计算**才能呈现的场景（Excel 公式、Word 域、PPT 图表数据），skill 都必须显式规定重算步骤并把它标为 mandatory。

---

## 六、doc-coauthoring —— 文档协作流程

| 维度 | 内容 |
|------|------|
| **用途** | 结构化写作工作流：从上下文收集到读者验收 |
| **SKILL.md** | 375 行 |
| **资源** | **无**（整个 skill 只有 SKILL.md 一个文件，F-085） |
| **许可** | **无 LICENSE.txt**（19 个中唯一，F-010） |

### 三阶段结构（F-085）

```
Stage 1: Context Gathering
  ### Initial Questions
  ### Info Dumping
Stage 2: Refinement & Structure
  ### Step 1: Clarifying Questions
  ### Step 2: Brainstorming
  ### Step 3: Curation
  ### Step 4: Gap Check
  ### Step 5: Drafting
  ### Step 6: Iterative Refinement
  ### Quality Checking
  ### Near Completion
Stage 3: Reader Testing
  ### Step 1: Predict Reader Questions
  ### Step 2: Test with Sub-Agent
  ### Step 3: Run Additional Checks
  ### Step 4: Report and Fix
  ### Step 1: Predict Reader Questions   ← 第二轮
  ### Step 2: Setup Testing
  ### Step 3: Additional Checks
  ### Step 4: Iterate Based on Results
```

`### Step` 小节共 **14 个**（Stage 2 六个 + Stage 3 两轮各四个，F-086）。

### 为什么它值得单独讲

它把"写文档"从一次性生成变成了**三阶段收敛流程**：

- **Stage 1 收集上下文**——先问清背景，避免基于错误前提动笔
- **Stage 2 六步精炼**——澄清 → 头脑风暴 → 筛选 → 查缺 → 起草 → 迭代，每步都有明确产出
- **Stage 3 读者测试**——**预测读者会问什么问题，然后交给子代理真的去回答**，再据此补齐

### 🔴 Stage 3 是最可迁移的一段

「预测读者问题 → 子代理作答 → 发现读者没被说服的地方 → 补齐」这个闭环，与内容类型无关——写技术规格、写周报、写教程、写 README 全都适用。

> 🟢 **可复用模式**：产出面向人阅读的文档时，把验收环节从"我读一遍觉得没问题"换成"让一个不知道背景的人来读并提问"。前者有严重的上下文污染，后者能暴露真实缺口。

---

## 七、五者的横向对比

| skill | 输出格式 | 核心机制 | 是否有脚本 | 三层 QA |
|-------|---------|---------|-----------|---------|
| docx | OOXML (Word) | XML 原地编辑 + 批注/修订 | ✅ 15 py | ❌（仅 Verify the output 段） |
| pdf | PDF | 三库分工（pypdf/pdfplumber/reportlab）+ 表单双路径 | ✅ 8 py | ✅ 隐含（check_bounding_boxes / create_validation_image） |
| pptx | OOXML (PPT) | XML 原地编辑 + 三层 QA | ✅ 15 py | ✅ **显式 Required** |
| xlsx | OOXML (Excel) | 强制重算 + 公式可验证性 | ✅ 12 py | ❌（靠 recalc） |
| doc-coauthoring | Markdown/文本 | 三阶段写作 + 读者测试 | ❌ 纯指令 | ✅ 读者测试即验收 |

---

## 相关文档

- [全部Skills索引](../references/skills-index.md) — 19 个 skill 速查
- [事实登记表](../references/facts.md) — F-044~F-052 共享子树与缺口事实
- [Skill 编写规范与可复用模式](04-authoring-patterns.md) — 跨 skill 通用模式
