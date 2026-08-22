---
type: Example
title: 将书籍转换为 Skill
description: 使用 book-to-skill CLI 工具将技术书籍/文档（PDF/EPUB/DOCX 等）转换为符合 Agent Skills 开放标准的结构化 Skill，包括依赖安装、文本提取、模式选择、SKILL.md 生成和安全验证完整流程。
tags: [book-to-skill, example, cli, pdf, epub, conversion, skill-generation]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: book-to-skill 源码事实清单
---

## 场景说明

你需要将一本技术书籍（如《Designing Data-Intensive Applications》PDF）转换为一个可以在 AI 编码助手（GitHub Copilot CLI、Amp、Claude Code）中使用的 Agent Skill。转换后的 Skill 让 AI 能够基于书中知识回答问题、提供代码示例、指导决策。

本示例演示：
1. 安装 book-to-skill 和格式依赖
2. 运行依赖预检查
3. 使用 CLI 提取书籍文本
4. 选择提取模式（text-heavy vs technical）
5. AI Agent 生成结构化 Skill（四层产出流水线）
6. 验证和安全扫描
7. 增量更新已有 Skill

## 双半架构说明

book-to-skill 采用 **Python 确定性提取器 + AI Agent 规范驱动生成器** 的双半架构：

```
┌─────────────────────────────────────────────────────┐
│              AI Agent（遵循 SKILL.md 指令）            │
│   Step 3: 结构分析 → Step 4: 用途选择 →              │
│   Step 5: 命名 → Step 7: 章节摘要 →                  │
│   Step 8: 辅助文件 → Step 9: 主 SKILL.md             │
└───────────────────────▲─────────────────────────────┘
                        │ 纯文本 + 元数据
┌───────────────────────┴─────────────────────────────┐
│          Python 提取器（确定性，无 LLM 调用）          │
│   PDF/EPUB/DOCX/HTML/RTF/MOBI → full_text.txt        │
│   + metadata.json（页数/token/章节/TOC）              │
│   CLI: book-to-skill <path> [--mode text|technical]  │
└─────────────────────────────────────────────────────┘
```

Python 代码只负责文本提取和清洗，结构化 Skill 的生成由 AI Agent 按照 SKILL.md 中的指令完成。

## 步骤 1：安装 book-to-skill

```bash
# 基础安装（支持 txt/md/html 等纯文本格式）
pip install book-to-skill

# 安装全部可选依赖（支持所有格式）
pip install "book-to-skill[all]"

# 或按需安装特定格式支持：
pip install "book-to-skill[pdf]"     # PDF 支持（pypdf + pdfminer.six）
pip install "book-to-skill[epub]"    # EPUB 支持（ebooklib + beautifulsoup4）
pip install "book-to-skill[docx]"    # DOCX 支持（python-docx）
pip install "book-to-skill[rtf]"     # RTF 支持（striprtf）
pip install "book-to-skill[technical]" # 技术文档支持（Docling，保留表格/代码块）

# 验证安装
book-to-skill --help
# 或
python -m book_to_skill --help
```

Python 依赖映射（内部自动检测）：

| 导入模块 | pip 包名 | 用途 |
|---------|---------|------|
| `bs4` | beautifulsoup4 | EPUB/HTML 解析 |
| `docx` | python-docx | DOCX 解析 |
| `pdfminer` | pdfminer.six | PDF 文本提取 |
| ebooklib | ebooklib | EPUB 解析 |
| striprtf | striprtf | RTF 解析 |

MOBI/AZW/AZW3 格式需要系统安装 Calibre 的 `ebook-convert` 命令（唯一硬依赖，无 Python 回退）。

## 步骤 2：运行依赖预检查

```bash
# 检查所有可选依赖状态
book-to-skill --check
```

输出示例：

```
📚 book-to-skill v1.3.0 - Dependency Check
─────────────────────────────────────────────
Python modules:
  ✓ yaml (json)
  ✓ bs4 (beautifulsoup4) - EPUB/HTML
  ✗ docx (python-docx) - DOCX
  ✓ pypdf - PDF
  ✓ pdfminer (pdfminer.six) - PDF fallback
  ✗ ebooklib - EPUB primary
  ✗ striprtf - RTF
  ✗ docling - Technical PDFs (recommended for code/tables)

System commands:
  ✗ pdftotext (poppler-utils) - PDF text mode (FAST)
  ✗ ebook-convert (Calibre) - MOBI/AZW

Status: 5/9 dependencies available.
Missing dependencies will use fallback extractors or fail.
```

安装缺失的推荐依赖：

```bash
# macOS
brew install poppler calibre

# Ubuntu/Debian
sudo apt install poppler-utils calibre

# Windows: 安装 Calibre 后 ebook-convert 可用
# https://calibre-ebook.com/download
```

## 步骤 3：使用 CLI 提取文本

### 3.1 选择提取模式

```bash
# 快速文本提取（散文/小说/文章，使用 pdftotext ~0.1s/页）
book-to-skill /path/to/book.pdf --mode text

# 技术文档提取（保留表格/代码块，使用 Docling ~1.5s/页）
book-to-skill /path/to/tech-book.pdf --mode technical
```

| 模式 | 提取器 | 速度 | 表格/代码 | 适用场景 |
|------|--------|------|----------|---------|
| `text`（默认） | pdftotext → pypdf → pdfminer.six | ~0.1s/页 | ❌ 丢失 | 散文、小说、文章 |
| `technical` | Docling | ~1.5s/页 | ✅ 保留为 Markdown | 技术书、教材、API 文档 |

### 3.2 基本提取命令

```bash
# 提取单个 PDF
book-to-skill ~/books/designing-data-intensive-applications.pdf --mode technical

# 提取多个文件
book-to-skill ch1.pdf ch2.pdf ch3.pdf --mode text

# 提取目录中的所有支持文件
book-to-skill ~/books/rust-book/ --mode technical

# 使用 glob
book-to-skill "~/books/*.epub" --mode text
```

### 3.3 输出结果

提取完成后，临时工作目录（默认 `<tempdir>/book_skill_work/`，可通过 `BOOK_SKILL_WORKDIR` 环境变量覆盖）包含：

```
book_skill_work/
├── full_text.txt     # 合并的纯文本（按文件分节）
└── metadata.json     # 提取元数据
```

`metadata.json` 包含：

```json
{
  "files": [
    {
      "source_file": "/path/to/book.pdf",
      "filename": "designing-data-intensive-applications.pdf",
      "format": "pdf",
      "extraction_method": "docling",
      "file_size_mb": 12.4,
      "pages": 616,
      "chars": 823456,
      "words": 134567,
      "estimated_tokens": 179423,
      "chapters_detected": 12,
      "chapter_headings_sample": ["Chapter 1: Reliable, Scalable...", "Chapter 2: Data Models..."],
      "has_toc": true
    }
  ],
  "total_tokens": 179423,
  "total_chapters_detected": 12
}
```

Token 估算公式：`estimated_tokens = len(words) / 0.75`（约 0.75 词/token）。

### 3.4 控制缺失依赖安装

```bash
# 自动安装缺失依赖（不询问）
book-to-skill book.pdf --install-missing yes

# 不安装缺失依赖（使用回退方案）
book-to-skill book.pdf --install-missing no

# 交互询问（默认，TTY 环境下）
book-to-skill book.pdf --install-missing ask

# 环境变量控制
export BOOK_SKILL_INSTALL_MISSING=yes
```

## 步骤 4：AI Agent 生成结构化 Skill

文本提取完成后，AI Agent（Claude Code / Copilot CLI 等）按照 SKILL.md 中的指令完成结构化编译。这个过程由 AI 自动执行，但你需要理解其流程来正确引导。

### 4.1 四种运行模式

| 模式 | 步骤 | 输出 | 适用场景 |
|------|------|------|---------|
| **Full Conversion** | Steps 0-9 | SKILL.md + chapters/ + glossary + patterns + cheatsheet | 首次转换 |
| **Analyze Only** | Steps 0-3 | 提取报告 | 先了解书籍结构再决定 |
| **Generate from Prior** | Steps 4-9 | 同上（跳过提取） | 已有 full_text.txt，重新生成 |
| **Update/Fold-in** | 6步 | 更新已有文件 | 增量添加新内容 |

### 4.2 Full Conversion 完整流程

**Step 0：范围检查**

AI 首先识别输入路径、可选 slug，检测是否为更新操作。你可以指定 Skill slug：

```
请将 ~/books/ddia.pdf 转换为 Skill，slug: "ddia"
```

**Step 1.5：内容类型选择**

AI 询问是 technical（代码/表格/公式）还是 text-heavy（纯散文）。这决定了提取器选择和章节 token 预算。

**Step 2：提取（Python CLI 执行）**

```bash
# AI 执行提取命令
book-to-skill ~/books/ddia.pdf --mode technical --install-missing ask
```

**Step 2.5：成本预估**

基于 metadata.json 计算 token 预估，等待用户确认：

```
📊 提取完成：616 页，~179K tokens
📋 预计生成成本：
  - 输入（分析+生成）：~200K tokens
  - 输出（SKILL.md + 12 chapters + glossary/patterns/cheatsheet）：~50K tokens
  - 预估费用（Claude Sonnet）：约 $1-2
是否继续？[Y/n]
```

**Step 2.6：REPL 式访问（大书专用）**

对于 >50K token 的大书，AI 使用 grep/sed/Read(offset/limit) 程序化探测，避免全文加载到上下文。

**Step 3：结构分析**

AI 读取前 8000 字符识别：标题、作者、章节结构、主要主题。Analyze Only 模式在此输出报告后停止。

**Step 4：用途选择**

AI 询问 Skill 用途，推导 DEPTH 级别：

| 选项 | DEPTH | 输出 |
|------|-------|------|
| 参考手册 | `reference` | 精简（800-1,800 tokens/chapter） |
| 深度学习/应用框架/思维模型 | `study` | 深入（1,000-3,000 tokens/chapter，含 worked example） |

**Step 5：命名与位置**

- Skill slug 命名规则：`作者-概念` 或标题小写连字符（如 `kleppmann-ddia`、`rust-book`）
- Skill 位置按主机类型探测 8 个可能路径：
  - `~/.copilot/skills/`
  - `~/.agents/skills/`
  - `~/.claude/skills/`
  - `.github/skills/`
  - `.claude/skills/`
  - `.agents/skills/`
  - `~/.config/agents/skills/`
  - `~/.config/amp/skills/`

**Step 7：章节摘要文件**

AI 逐章生成 `chapters/ch<NN>-<slug>.md`，每章遵循模板：

```markdown
# Chapter 1: Reliable, Scalable, and Maintainable Applications

## Core Idea
（章节核心思想，200-400 tokens）

## Key Concepts
- **Reliability**: 系统即使出现故障也能正确工作
- **Scalability**: 系统应对增长的能力
- **Maintainability**: 系统易于维护和演进

## Frameworks Introduced
（本章引入的框架/模型）

## Mental Models
（心智模型）

## Anti-patterns
（反模式）

## Code Examples
（仅 technical 模式，可运行的代码示例）

## Reference Tables
（仅 technical 模式，参考表格）

## Worked Example
（仅 study 模式，完整的解题/应用示例）

## Key Takeaways
（关键要点，3-5条）

## Connects To
（与其他章节的关联）
```

Per-chapter token 预算矩阵：

| 模式 | reference | study |
|------|-----------|-------|
| text | 800-1,200 | 1,000-1,800 |
| technical | 1,200-1,800 | 2,000-3,000 |

**Step 8：辅助文件**

AI 生成三个辅助文件：

```
<skill>/
├── glossary.md    # 术语表，≤1,500 tokens，按字母排序
├── patterns.md    # 模式库，≤2,000 tokens
└── cheatsheet.md  # 决策速查，≤1,200 tokens
```

- **glossary.md**：所有重要术语，格式 `**Term** — definition (Ch N)`
- **patterns.md**：所有技术/算法/设计模式，含 When to use / How / Trade-offs
- **cheatsheet.md**：决策规则、决策树、权衡矩阵、阈值默认值

**Step 9：主 SKILL.md**

AI 生成主 SKILL.md（正文 ≤4,000 tokens），结构：

```yaml
---
name: kleppmann-ddia
description: >
  Expert on data-intensive application design based on "Designing Data-Intensive Applications"
  by Martin Kleppmann. Covers replication, partitioning, transactions, consistency,
  batch/stream processing. Use when designing distributed systems, choosing databases,
  reasoning about consistency models, or architecting data pipelines.
---

# Designing Data-Intensive Applications

## How to Use
（使用说明）

## Core Frameworks & Mental Models
（~2,000 tokens，最重要内容前置）

## Chapter Index
| Ch | Title | Key Topics |
|----|-------|-----------|
| 1 | Reliable, Scalable... | Reliability, Scalability, Maintainability |
...

## Topic Index
（字母序术语 → 章节映射）

## Supporting Files
- `glossary.md` — Term definitions
- `patterns.md` — Design patterns with trade-offs
- `cheatsheet.md` — Decision rules and quick reference
- `chapters/` — Per-chapter detailed notes

## Scope & Limits
（Skill 覆盖范围和局限性）
```

**Step 9.5：安全扫描**

```bash
# AI 运行安全扫描工具
python tools/scan_generated_skill.py ~/.claude/skills/kleppmann-ddia
```

扫描检测 7 类 prompt 注入：
- `prompt.ignore_previous`：忽略先前指令
- `prompt.disregard_system`：忽略系统指令
- `prompt.role_reassignment`：角色重分配
- `prompt.fake_system_prefix`：伪造系统消息前缀
- `prompt.system_tag`：`<system>` 标签
- `prompt.chat_template_tag`：模型聊天模板分隔符
- `prompt.tool_call_tag`：工具调用控制 token

以及数据渗出检测（exfiltrate + curl/wget + secrets 共现）。

非零退出则停止，要求人工审查。

**Step 10：清理与报告**

AI 删除临时工作目录，打印成功报告。

### 4.3 最终产出结构

```
~/.claude/skills/kleppmann-ddia/
├── SKILL.md              # 主文件（~4K tokens，常驻上下文）
├── glossary.md           # 术语表
├── patterns.md           # 模式库
├── cheatsheet.md         # 决策速查
└── chapters/
    ├── ch01-reliable-scalable.md
    ├── ch02-data-models.md
    ├── ch03-storage-representation.md
    ├── ch04-encoding-evolution.md
    ├── ch05-replication.md
    ├── ch06-partitioning.md
    ├── ch07-transactions.md
    ├── ch08-distributed-systems.md
    ├── ch09-consistency-consensus.md
    ├── ch10-batch-processing.md
    ├── ch11-stream-processing.md
    └── ch12-future-data-systems.md
```

## 步骤 5：验证 Skill 格式

```bash
# 使用 validate_skill.py 验证格式
python tools/validate_skill.py ~/.claude/skills/kleppmann-ddia --lens claude

# --lens 可选值：claude（默认）、copilot、amp
# 不同 lens 检查不同的工具名和保留词
```

验证项：
- YAML frontmatter 存在性
- `name`：必填、≤64字符、kebab-case、非保留词
- `description`：必填、≤1024字符
- `allowed-tools` 声明合理性
- frontmatter 键识别（未知键产生 WARN）
- body 行数 >500 行时 WARN（建议拆分到 references/）

## 步骤 6：增量更新

当你有新的章节或修订内容需要合并到已有 Skill：

```
请将 ~/books/ddia-ch13-new.pdf 增量更新到 kleppmann-ddia Skill
```

Update/Fold-in 工作流（6 步）：
1. 读取已有 skill 结构
2. 匹配内容（修订 vs 新增）
3. 生成/更新章节文件
4. 合并辅助文件（glossary/patterns/cheatsheet）
5. 重新生成 SKILL.md（更新索引）
6. 扫描 + 清理 + 报告

## 支持的文件格式

| 格式 | 扩展名 | 主提取器 | 回退方案 | 硬依赖 |
|------|--------|---------|---------|--------|
| 纯文本 | .txt, .text, .md, .rst, .adoc | 直接读取 | — | — |
| HTML | .html, .htm, .xhtml | BeautifulSoup | stdlib HTMLParser | bs4（可选） |
| PDF (text) | .pdf | pdftotext | pypdf → pdfminer.six | poppler-utils（推荐） |
| PDF (technical) | .pdf | Docling | 降级到 text 模式 | docling（推荐） |
| EPUB | .epub | ebooklib + bs4 | stdlib zipfile 解析 OPF | ebooklib（可选） |
| DOCX | .docx | python-docx | stdlib ZIP/XML 解析（含XXE防护） | python-docx（可选） |
| RTF | .rtf | striprtf | 正则清洗 | striprtf（可选） |
| MOBI/AZW | .mobi, .azw, .azw3 | ebook-convert | **无回退** | Calibre（必需） |

每种格式都有 stdlib 回退方案（除 MOBI/AZW），单个文件提取失败仅跳过（批量容错），不中断整体流程。

## 8 条质量规则

AI 生成时遵循：

1. **提取结构非摘要**：不是摘要每章，而是提取知识结构
2. **保留作者精确命名**：使用书中术语原文
3. **密度优于完整性**：宁可少而精，不要多而浅
4. **实践者语气**：面向实践者而非学术读者
5. **SKILL.md 前置加载**：最重要内容放在 SKILL.md 中（始终在上下文）
6. **章节按需加载**：详细内容放在 chapters/ 中，SKILL.md 引用
7. **绝不复制原文**：用自己的话表达，不直接复制大段原文
8. **主题索引关键**：Topic Index 是快速导航的核心

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| PDF 提取乱码 | pdftotext 不可用 | 安装 poppler-utils 或使用 --mode technical |
| DOCX 提取报安全错误 | XXE 检测触发 | 检查 DOCX 是否包含恶意 DOCTYPE 声明 |
| 提取速度极慢 | 使用了 Docling | technical 模式 ~1.5s/页，100页书约2.5分钟，正常 |
| MOBI 提取失败 | 未安装 Calibre | 安装 Calibre 并确保 ebook-convert 在 PATH 中 |
| Skill 触发不精准 | description 不够明确 | 修改 SKILL.md 的 description，增加触发场景描述 |
| 发现循环 token 消耗过高 | SKILL.md 太大 | 确保 SKILL.md ≤4K tokens，详细内容移到 chapters/ |

## 发现循环税优势

book-to-skill 的核心价值是降低"发现循环税"（discovery loop tax）：

| 策略 | 每轮 token 消耗 | 倍数 |
|------|----------------|------|
| Context-dump（全书常驻） | 119K-256K tokens | 24-51× |
| Discovery-loop（导航+拉取） | 12K-78K tokens | 2.4-15.6× |
| **book-to-skill** | **~5K tokens** | **1×** |

context-dump 成本每轮重复，而 book-to-skill 的 SKILL.md 常驻（~4K tokens）+ 单章按需加载（~2K tokens）实现了 24-51 倍的 token 节省。

## 相关概念

- [四层产出流水线](../concepts/four-layer-pipeline.md)
- [多格式解析器](../concepts/multi-format-parsers.md)
- [依赖管理](../concepts/dependency-management.md)
- [安全清洗与防护](../concepts/security-sanitization.md)
