---
type: concept
title: "SKILL.md 格式规范"
tags: [skills, skill.md, format, yaml, frontmatter, packaging]
sources:
  - id: anthropic-skill-format
    title: Anthropic Skills Format Specification
---

# SKILL.md 格式规范

本文档详细定义 `SKILL.md` 的标准格式——这是每个 Anthropic Skill 的核心描述文件。遵循此规范可以确保你的 Skill 能够被 Claude Code 正确识别、触发和使用。

## Skill 目录结构

每个 Skill 是一个独立目录，采用以下标准结构：

```
my-skill/
├── SKILL.md           # 必需，Skill 核心描述文件
├── scripts/           # 可选，可执行脚本
│   ├── helper.py
│   └── validate.sh
├── references/        # 可选，参考文档
│   ├── api-docs.md
│   └── specification.pdf
├── agents/            # 可选，子代理定义
│   ├── analyzer.md
│   └── grader.md
├── examples/          # 可选，使用示例
│   ├── example-1.md
│   └── example-2.md
└── evals/             # 可选，评估用例
    ├── eval-1.json
    └── run_eval.py
```

### 各目录职责

| 目录 | 必需性 | 用途 | 内容类型 |
|------|--------|------|---------|
| `SKILL.md` | ✅ 必需 | Skill 的元数据和使用指令 | YAML frontmatter + Markdown |
| `scripts/` | ❌ 可选 | 辅助脚本工具 | Python/Shell/Node.js 等可执行文件 |
| `references/` | ❌ 可选 | 参考资料和权威文档 | Markdown、PDF、文本文件等 |
| `agents/` | ❌ 可选 | 专门的子代理定义 | Markdown（子代理 system prompt） |
| `examples/` | ❌ 可选 | 输入输出示例 | Markdown、代码片段、样例文件 |
| `evals/` | ❌ 可选 | 质量评估用例（**root 级排除，不打包**） | 测试数据、评估脚本 |
| `assets/` | ❌ 可选 | 输出中使用的素材（**字面起点，非灵感**） | HTML/CSS、模板、字体 |
| `templates/` | ❌ 可选 | 起点模板 | HTML/JS/XML |
| `core/` | ❌ 可选 | 核心 Python 模块（供 import） | Python |
| `LICENSE.txt` | ❌ 可选 | 许可证全文 | 文本 |

> 💡 **简单 Skill 的最小结构**：只需要一个包含 `SKILL.md` 的目录即可，不需要任何子目录。

> 📌 **官方实测用到的目录**：`scripts/`（9 个 skill）、`examples/`（3）、`references/`（3）、`templates/`（3）、`assets/`（2）、`agents/`（1）、`core/`（1）、`eval-viewer/`（1）、`canvas-fonts/`（1）、`themes/`（1）。详见 [Skill 编写规范与可复用模式](04-authoring-patterns.md)。

## YAML frontmatter 字段详解

`SKILL.md` 文件顶部必须包含 YAML frontmatter，以 `---` 分隔。

### 必填字段

#### `name`

Skill 的唯一标识符，使用 **kebab-case**（小写字母、数字、连字符）命名。

```yaml
name: pdf-processor
```

- 命名规则：`^[a-z0-9-]+$`（小写字母、数字、连字符）
- 长度上限：64 字符
- 不得以 `-` 开头或结尾，不得包含连续连字符（`--`）
- 在同一作用域（用户全局或项目级）内必须唯一
- 应该简洁且具有描述性，让人一眼看出 Skill 的用途

> 📌 校验实现见 `skills/skill-creator/scripts/quick_validate.py` 的 `re.match(r'^[a-z0-9-]+$', name)` 及后续的 `startswith('-')` / `endswith('-')` / `'--' in name` / `len(name) > 64` 四项检查（事实编号 F-014）。

#### `description`

**最关键的字段**——这是 Skill 能否被正确触发的决定性因素。它需要同时包含：

1. **功能描述**：这个 Skill 能做什么
2. **触发条件**：明确列出何时应该使用此 Skill（使用 "TRIGGER when..." 句式）

```yaml
description: |
  Process and manipulate PDF files. Extract form fields, fill forms,
  convert PDF to images, inspect bounding boxes, populate annotations.
  Includes python scripts for reliable PDF handling using pypdf and
  pdfplumber libraries.
  TRIGGER when: user asks to work with PDF files, extract data from PDFs,
  fill PDF forms, convert PDFs, or inspect PDF content/annotations.
  TRIGGER when: user uploads a .pdf file and asks to process it.
```

### 可选字段

#### `license`

Skill 的许可证声明。**取值须与实际的 `LICENSE.txt` 内容一致**。

```yaml
license: Complete terms in LICENSE.txt
```

或专有授权：

```yaml
license: Proprietary. LICENSE.txt has complete terms
```

> ⚠️ **事实校正**：官方 19 个 Skill 采用**双轨许可**（事实编号 F-011）——
> - **14 个** Apache License 2.0（`academy-guide`、`algorithmic-art`、`brand-guidelines`、`canvas-design`、`claude-api`、`discernment-nudge`、`frontend-design`、`internal-comms`、`mcp-builder`、`skill-creator`、`slack-gif-creator`、`theme-factory`、`web-artifacts-builder`、`webapp-testing`）
> - **4 个** Anthropic 专有授权（`docx`、`pdf`、`pptx`、`xlsx`），LICENSE.txt 首行为 "© 2025 Anthropic, PBC. All rights reserved"——**source-available，非开源**
> - **1 个** 无 LICENSE.txt（`doc-coauthoring`）
>
> 仓库**不存在 MIT 许可**。写 `license: MIT` 与事实不符。

#### `compatibility`

声明 Skill 的运行环境依赖。**必须是字符串**（不是嵌套 map），长度上限 500 字符。

```yaml
compatibility: Requires Node.js 18+ and network access to the target API.
```

> ⚠️ **事实校正**：写成嵌套结构会直接校验失败——`quick_validate.py` 的检查是 `if not isinstance(compatibility, str): return False, "Compatibility must be a string, got dict"`（事实编号 F-016）。官方 19 个 Skill **均未使用**此字段。

#### `allowed-tools`

限制 Skill 可用的工具。官方 19 个 Skill **均未使用**此字段；`quick_validate.py` 只允许它存在，不校验其值（事实编号 F-018）。

#### `metadata`

自定义元数据字典。官方 19 个 Skill **均未使用**。校验时 `metadata` 下的嵌套键被豁免，不会触发"表外键"错误（事实编号 F-013）。

## description 编写最佳实践

`description` 是 Skill 中最重要的部分——一个写得不好的 description 会导致 Skill 永远不被触发（undertrigger），或者在不该触发时被错误激活（overtrigger）。

### 核心原则："Pushy" 风格

官方建议采用 **"pushy"（有推动力的）** 风格编写 description：

- **宁滥勿缺**：在边界情况下，倾向于触发 Skill。因为加载 Skill 只会增加代理的知识，不会产生有害副作用
- **避免模糊**：不要用"may be useful for"、"can help with"这类弱表述
- **直接指令**：用 "TRIGGER when..." 明确告诉代理"在这种情况下就使用我"

### 必须包含的触发场景

一个好的 description 应该覆盖以下触发场景：

| 场景类型 | 示例 |
|---------|------|
| **用户明确请求** | "用户要求处理 PDF 文件时" |
| **文件类型关联** | "用户上传 .pdf 文件时" |
| **关键词/术语** | "用户提到表单填写、PDF 转图片、标注时" |
| **任务类型** | "用户需要从文档中提取结构化数据时" |
| **特定技术栈** | "用户使用 Python 处理 PDF 且需要可靠脚本时" |

### 反模式：要避免的写法

❌ **过于模糊**：
```yaml
description: A skill for working with documents.
```

❌ **缺少触发条件**：
```yaml
description: |
  PDF processing utilities. Can extract fields and fill forms.
  Uses pypdf library.
```

❌ **过于宽泛**（会导致 overtrigger）：
```yaml
description: |
  Process any kind of document file.
  TRIGGER when: user mentions any file.
```

✅ **好的写法**：
```yaml
description: |
  Process PDF files: extract/fill form fields, convert PDF to images,
  inspect bounding boxes, populate annotations. Includes Python scripts
  using pypdf and pdfplumber for reliable PDF handling.
  TRIGGER when: user asks to work with PDFs, extract PDF data, fill forms,
  convert PDFs, or inspect PDF content/annotations.
  TRIGGER when: user uploads a .pdf file.
  TRIGGER when: user mentions PDF forms, AcroForm, PDF annotations,
  or pdfplumber/pypdf libraries.
```

### description 长度建议

- **最短**：3-5 行（功能描述 + 2-3 个触发条件）
- **推荐**：8-15 行（覆盖主要使用场景）
- **最长**：不超过 30 行（过长会稀释语义匹配的准确度）

### description 的硬性约束

`quick_validate.py` 对 description 有三条强制检查（事实编号 F-015）：

| 约束 | 违规报错 |
|------|---------|
| 必须是字符串 | `Description must be a string, got <type>` |
| 长度 ≤ 1024 字符 | `Description is too long (N characters). Maximum is 1024 characters.` |
| **不得含尖括号 `<` `>`** | `Description cannot contain angle brackets (< or>)` |

> ⚠️ 第三条容易踩坑：想在 description 里写 "output <500 lines" 之类的表述会直接校验失败——写成 "under 500 lines" 或 "少于 500 行"。

### 允许字段总表

| 字段 | 必需性 | 类型约束 | 官方使用率 |
|------|--------|---------|-----------|
| `name` | ✅ 必填 | 字符串；`^[a-z0-9-]+$`；≤64 字符 | 19/19 |
| `description` | ✅ 必填 | 字符串；≤1024 字符；无尖括号 | 19/19 |
| `license` | 可选 | 字符串（不校验值） | 17/19 |
| `allowed-tools` | 可选 | 不校验值 | 0/19 |
| `metadata` | 可选 | 字典（嵌套键豁免） | 0/19 |
| `compatibility` | 可选 | **字符串**；≤500 字符 | 0/19 |

> ⚠️ **frontmatter 只允许这 6 个键**。写入表外键会得到：`Unexpected key(s) in SKILL.md frontmatter: xxx. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name`（事实编号 F-013）。

### 🔴 关于 500 行：没有硬性要求

官方 19 个 Skill 的 `SKILL.md` 中，**`claude-api` 有 616 行、`skill-creator` 有 485 行、`algorithmic-art` 有 404 行**——均超过 500 行且能正常工作。

`quick_validate.py` **不含任何行数检查**，全文只有一处 500 相关判断，是 `len(compatibility) > 500`（事实编号 F-017）：

```python
compatibility = frontmatter.get('compatibility', '')
if compatibility:
    if not isinstance(compatibility, str):
        return False, "Compatibility must be a string, ..."
    if len(compatibility) > 500:
        return False, "Compatibility is too long (...). Maximum is 500 characters."
```

`<500 行` 是 `skill-creator/SKILL.md` 中的**散文建议**（"Keep SKILL.md under 500 lines; if you're approaching this limit, add an additional layer of hierarchy"），不是校验规则。超出仍可正常加载——但拆到 `references/` 确实能省上下文。

| 事实 | 编号 |
|------|------|
| 校验脚本无行数检查 | F-017 |
| 官方 SKILL.md 行数分布（32~616 行） | F-009、F-025~F-043 |

## Markdown body 组织方式

YAML frontmatter 之后的 Markdown 正文是 Skill 的**指令内容**，告诉代理加载此 Skill 后应该如何行动。

### 推荐的章节结构

```markdown
# PDF Processing Skill

## When to Use This Skill
（重申触发场景，比 description 更详细——什么时候应该用，什么时候不应该用）

## Key Resources
（列出本 Skill 提供的关键资源及使用方法）

### Scripts
- `scripts/extract_form_structure.py`: 提取 PDF 表单结构。Usage: `python scripts/extract_form_structure.py <input.pdf> <output.json>`
- `scripts/fill_fillable_fields.py`: 用提供的数据填充可填字段。

### References
- `forms.md`: PDF 表单字段规范（**磁盘为小写文件名**）
- `reference.md`: pypdf / pdfplumber / reportlab 用法速查

## Workflow
（推荐的标准工作流程，按步骤说明）

1. First, inspect the PDF to understand its structure using `scripts/extract_form_structure.py`
2. If extracting data, use `pdfplumber` for text and tables
3. If modifying, always work on a copy of the original file
4. Validate the output using `scripts/check_bounding_boxes.py`

## Best Practices
（最佳实践和注意事项）

- Always preserve the original PDF — never modify in place
- Use `pdfplumber` for text extraction, `pypdf` for form manipulation
- Handle encrypted PDFs by prompting for password first
- Large PDFs (>100 pages) should be processed page by page

## Common Pitfalls
（常见陷阱和如何避免）

- Don't use PyPDF2 — it's deprecated, use pypdf instead
- Image-based PDFs require OCR first (this skill doesn't include OCR)
```

### 正文编写原则

1. **直接指令式**：用祈使句告诉代理做什么，而不是描述性语言
2. **提供具体路径**：明确引用脚本和参考文档的路径（相对于 Skill 根目录）
3. **包含反例**：说明什么情况下**不应该**使用此 Skill，或常见错误做法
4. **给出完整示例**：关键操作提供可直接运行的命令示例
5. **错误处理指引**：说明遇到常见错误时应该如何排查和解决

## 资源引用约定

### 引用 scripts/ 中的脚本

在 Markdown 正文中引用脚本时，使用相对于 Skill 根目录的路径，并提供使用说明：

```markdown
Run the extraction script:
\```bash
python "$SKILL_DIR/scripts/extract_form_structure.py" input.pdf out.json
\```
```

> 💡 `$SKILL_DIR` 是一个约定变量，指代当前 Skill 所在的目录。代理在执行时会自动替换为实际路径。

### 引用 references/ 中的文档

```markdown
For detailed API documentation, see [reference.md](reference.md).

Before handling complex forms, read the [forms specification](forms.md).
```

> ⚠️ **实测缺口**：官方 `pdf` skill 的 SKILL.md 正文引用的是 `FORMS.md` / `REFERENCE.md`（大写），而磁盘上实际是 `forms.md` / `reference.md`（小写）。**Linux 环境大小写敏感，按正文指引会取不到文件**（事实编号 F-052）。写 skill 时应确保正文路径与磁盘文件名逐字符一致。

### 引用 agents/ 中的子代理

当 Skill 包含专门的子代理时，明确说明何时调用它们：

```markdown
For analyzing PDF structure, delegate to the `agents/analyzer.md` agent.
For grading output quality, use `agents/grader.md`.
```

### 调用外部工具

如果 Skill 依赖外部命令行工具，明确说明安装方法：

```markdown
**Prerequisite**: Install required dependencies first:
\```bash
pip install pypdf pdfplumber
\```
```

## Skill 打包与分发

### 本地安装

最简单的分发方式是直接复制目录：

```bash
# 安装到用户全局 Skills（所有项目可用）
cp -r my-skill ~/.claude/skills/

# 安装到项目级 Skills（仅当前项目可用）
cp -r my-skill /path/to/project/.claude/skills/
```

### 通过 Git 分发

对于需要版本管理的 Skills，可以通过 Git 仓库分发：

```bash
# 用户全局安装
git clone https://github.com/yourname/my-skill.git ~/.claude/skills/my-skill

# 更新
cd ~/.claude/skills/my-skill && git pull
```

### 作为 Claude Code 插件分发

Skills 可以打包为 Claude Code 插件的一部分，通过插件市场分发。插件结构：

```
my-plugin/
├── plugin.json          # 插件元数据
├── skills/
│   └── my-skill/        # 你的 Skill（完整目录）
│       ├── SKILL.md
│       └── scripts/
├── commands/
├── agents/
└── hooks/
```

`plugin.json` 示例：

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My custom plugin with PDF skills",
  "author": "Your Name"
}
```

> 🔗 插件体系详见 [/claude-code/concepts/01-plugin-system.md](../../claude-code/concepts/01-plugin-system.md)

### 发布检查清单

发布 Skill 前，确认以下事项：

- [ ] `SKILL.md` 包含有效的 `name` 和 `description`
- [ ] `description` 有明确的 "TRIGGER when..." 触发条件
- [ ] `description` 不含尖括号 `<` `>`，长度 ≤1024 字符
- [ ] frontmatter 只用了 6 个允许字段之一
- [ ] `compatibility`（若写）是字符串且 ≤500 字符
- [ ] 所有引用的脚本路径正确、文件存在（含**大小写**）
- [ ] 脚本有基本的使用说明和错误处理
- [ ] 敏感信息（API keys、密码）未被硬编码
- [ ] 包含 `license` 字段且与实际 LICENSE.txt 一致（如适用）
- [ ] 已在实际场景中测试触发和执行效果

## 相关概念

- [Skills 生态概览](00-overview.md) — Skills 的基本概念和生态定位
- [Skill Creator 工具详解](02-skill-creator.md) — 使用官方元技能辅助创建高质量 Skills
- [Claude API Skill 详解](03-claude-api-skill.md) — 官方 claude-api Skill 的实际案例参考
- [Skill 编写规范与可复用模式](04-authoring-patterns.md) — 从 19 个官方 Skill 反向提炼的编写规范
- [从零造一个 Skill](../examples/01-author-a-skill.md) — 校验、打包、评估的完整实操
- [全部 Skills 索引](../references/skills-index.md) — 19 个官方 Skills 的完整清单，可作为格式参考
- [事实登记表](../references/facts.md) — 本文档全部断言的实测底账
- [Claude Code 插件体系](../../claude-code/concepts/01-plugin-system.md) — Skills 如何融入插件分发体系

## 与其他扩展机制的格式区别

为避免混淆，以下是各扩展机制的文件命名对比：

| 扩展机制 | 核心文件 | 位置 |
|---------|---------|------|
| **Skill** | `SKILL.md` | `skills/<skill-name>/SKILL.md` |
| **Command** | `<command-name>.md` | `commands/<command-name>.md` |
| **Agent** | `<agent-name>.md` | `agents/<agent-name>.md` |
| **Hook** | `<hook-name>.md` | `hooks/<hook-event>/<hook-name>.md` |

注意：只有 Skill 使用全大写的 `SKILL.md` 作为入口文件名（在独立目录下），其他扩展机制直接使用 kebab-case 命名的 `.md` 文件。
