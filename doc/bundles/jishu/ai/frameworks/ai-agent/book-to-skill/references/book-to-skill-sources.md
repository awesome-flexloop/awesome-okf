---
type: Reference
title: book-to-skill 源码信源登记
description: Python 知识编译系统（文档→Agent Skill 转换器）源码结构、多格式解析器、章节检测系统、SKILL.md 生成流水线与安全扫描信源清单
tags: [book-to-skill, python, skill-converter, pdf, epub, docx, agent-skill, knowledge-compilation, source, reference]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T23:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: book-to-skill-github
    resource: https://github.com/anthropics/book-to-skill (presumed)
    title: book-to-skill 源码仓库
---

# book-to-skill 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | book-to-skill |
| 版本 | v1.3.0 |
| 许可证 | MIT |
| Python 版本要求 | ≥3.9 |
| 构建系统 | hatchling（build-backend） |
| CLI 入口 | `book-to-skill` → `book_to_skill.cli:main` |
| 描述 | 将技术书籍/文档（PDF/EPUB/DOCX/HTML/RTF/MOBI/AZW 等）转换为结构化 Agent Skill 的 Python 知识编译系统 |
| 兼容平台 | GitHub Copilot CLI、Amp、Claude Code（遵循 Agent Skills 开放标准） |
| 源码位置 | `d:\spaces\SpecWeave\external\libs\models\ai\book-to-skill\` |

## 架构概览

**双半架构**：
1. **Python 确定性提取器**：从多种文档格式提取纯文本 + 元数据（章节、字数、token 估算）
2. **Agent 规范驱动生成器**：AI Agent 遵循 SKILL.md 指令完成结构化编译（章节摘要、术语表、模式表、速查表、主 SKILL.md）

Python 仅负责文本提取和安全扫描，结构化 Skill 生成由 AI Agent 执行。

## 核心目录结构

```
book-to-skill/
├── pyproject.toml               # 项目配置、依赖、入口点
├── README.md                    # 项目说明
├── SKILL.md                     # AI Agent 遵循的生成流程规范（~650行）
├── LICENSE                      # MIT
├── book_to_skill/               # Python 包
│   ├── __init__.py              # 导出 resolve_input_files/extract_single_file/main/ExtractionError
│   ├── __main__.py              # python -m book_to_skill 入口
│   ├── cli.py                   # CLI 层（UTF-8 强制）
│   ├── config.py                # 配置常量（支持扩展名、依赖映射、token 估算）
│   ├── exceptions.py            # ExtractionError 异常类
│   ├── sanitize.py              # 零宽字符/Tag 区块清洗
│   ├── dependencies.py          # 依赖分组探测/安装/预检查
│   ├── utils.py                 # 核心工具（章节检测、参数解析、提取主流程、main）
│   └── parsers/                 # 格式解析器
│       ├── pdf.py               # PDF（pdftotext/pypdf/pdfminer/Docling）
│       ├── epub.py              # EPUB（ebooklib/zipfile OPF 解析）
│       ├── docx.py              # DOCX（python-docx/zipfile+XXE防护）
│       ├── html.py              # HTML（BeautifulSoup/stdlib HTMLParser）
│       ├── rtf.py               # RTF（striprtf/正则清洗）
│       ├── text.py              # 纯文本（BOM 检测 + 多编码回退）
│       └── calibre.py           # Calibre ebook-convert（MOBI/AZW）
├── scripts/
│   ├── extract.py               # 向后兼容 shim 入口
│   └── banner.txt               # ASCII art 横幅
├── tools/
│   ├── discovery_tax.py         # 发现循环税测量（3策略对比）
│   ├── scan_generated_skill.py  # 生成 Skill 安全扫描（7类注入+渗出检测）
│   └── validate_skill.py        # Skill 格式校验（三主机透镜）
├── tests/                       # pytest 测试（4 个文件）
├── docs/
│   ├── ARCHITECTURE.md          # 架构设计文档
│   └── PERFORMANCE.md           # 性能指标与发现循环税数据
```

## 关键文件清单

### Python 包核心

| 文件 | 内容 |
|------|------|
| `book_to_skill/__init__.py` | 公开 API 导出：`resolve_input_files`、`extract_single_file`、`main`、`ExtractionError` |
| `book_to_skill/cli.py` | CLI 层：强制 stdout/stderr UTF-8（Windows 兼容），调用 `utils.main()` |
| `book_to_skill/config.py` | 常量：WORKDIR、WORDS_PER_TOKEN=0.75、SUPPORTED_EXTENSIONS（13 种）、PYTHON_DEPENDENCIES 映射 |
| `book_to_skill/exceptions.py` | `ExtractionError(Exception)`：单文件提取失败异常（批量模式下非致命） |
| `book_to_skill/sanitize.py` | `sanitize_extracted_text()`：移除零宽字符(U+200B/C/D/U+2060)、BOM(U+FEFF)、Unicode Tag 区块(U+E0000–E007F) |
| `book_to_skill/dependencies.py` | 7 个格式分组依赖、模块探测、自动安装(pip install, 600s 超时)、交互提示、`run_dependency_check()` 报告 |
| `book_to_skill/utils.py` | ~735 行核心文件：多语言章节正则、中文/罗马/泰语/韩文章节检测、`detect_structure()`、`extract_single_file()`、`main()` |

### 格式解析器（parsers/）

| 文件 | 内容 |
|------|------|
| `parsers/pdf.py` | 4 种 PDF 提取：pdftotext（-layout, 120s超时, 页眉页脚频率统计清洗）→ pypdf → pdfminer.six → Docling（technical 模式保留表格/代码块为 markdown）；页数统计（pdfinfo→pypdf） |
| `parsers/epub.py` | ebooklib+bs4 → stdlib zipfile OPF 解析（container.xml→OPF manifest→spine 顺序→HTML 提取）；OPF 章节计数 |
| `parsers/docx.py` | python-docx（段落+表格）→ stdlib ZIP/XML 解析（word/document.xml 按顺序遍历块元素）；XXE/Billion-Laughs 安全校验 |
| `parsers/html.py` | BeautifulSoup（去 script/style/head + get_text）→ stdlib `_HTMLTextExtractor`（跳过 script/style/head，块级标签插换行） |
| `parsers/rtf.py` | striprtf → 正则回退（Unicode 转义 `\uN`、十六进制转义、`\par`→换行、花括号移除、HTML entity unescape） |
| `parsers/text.py` | BOM 优先级编码检测（UTF-8 BOM→UTF-32→UTF-16）→ UTF-8→CP1252→Latin-1 回退链 |
| `parsers/calibre.py` | `ebook-convert` 调用（300s 超时），MOBI/AZW/AZW3 唯一提取途径 |

### 工具脚本（tools/）

| 文件 | 内容 |
|------|------|
| `tools/discovery_tax.py` | 三策略 token 测量：context-dump vs discovery-loop vs book-to-skill；`split_chapters()`、`best_chapter()`；优先 tiktoken(cl100k_base) |
| `tools/scan_generated_skill.py` | 安全扫描：7 类 prompt 注入检测（ignore_previous/disregard_system/role_reassignment/fake_system_prefix/system_tag/chat_template_tag/tool_call_tag）+ 数据渗出检测（exfiltrate+curl/wget+secrets 共现）+ frontmatter 权限扩大检查；Finding 数据类；限制 1000 文件/2MB 单文件/20MB 总量 |
| `tools/validate_skill.py` | 三主机透镜（claude/copilot/amp）：各有工具名/frontmatter 键/保留词；校验 name/description/allowed-tools/body 行数 |

### AI Agent 生成规范

| 文件 | 内容 |
|------|------|
| `SKILL.md` | AI Agent 遵循的完整生成流水线（~650行）：4 种运行模式、10 步流程、产出物结构、token 预算、质量规则、Update/Fold-in 工作流 |

### 架构与性能文档

| 文件 | 内容 |
|------|------|
| `docs/ARCHITECTURE.md` | 双半架构、分层安全（5 层）、优雅降级策略 |
| `docs/PERFORMANCE.md` | 实测性能：pdftotext 0.1s/0表格 vs Docling 164s/48表格/36代码块；全书转换成本 ~$1/书；发现循环税优势 ~5K vs 119K-256K tokens |

### 测试

| 文件 | 内容 |
|------|------|
| `tests/` | 4 个测试文件：EPUB 提取修复、批量容错、输入顺序保留、Glob 过滤、参数解析、Token 估算、12 语言章节检测、Markdown/AsciiDoc/RST 结构标题、Setext 误报防护、代码块标题忽略、DOCX XXE 拒绝、RTF Unicode、依赖检查、安全扫描器、discovery_tax 排序不变量、sanitize 清洗 |

## 支持的文件格式

| 格式类别 | 扩展名 | 首选提取器 | 回退方案 | 硬依赖 |
|---------|--------|-----------|---------|--------|
| 纯文本 | `.txt`, `.text`, `.md`, `.markdown`, `.rst`, `.adoc`, `.asciidoc` | 直接读取（多编码检测） | — | — |
| HTML | `.html`, `.htm`, `.xhtml` | BeautifulSoup | stdlib HTMLParser | — |
| PDF text-heavy | `.pdf` | pdftotext（系统命令） | pypdf → pdfminer.six | pdftotext 可选 |
| PDF technical | `.pdf` | Docling（保留表格/代码块） | 降级到 text 模式 | docling 可选 |
| EPUB | `.epub` | ebooklib + bs4 | stdlib zipfile（OPF 解析） | — |
| DOCX | `.docx` | python-docx | stdlib ZIP/XML | — |
| RTF | `.rtf` | striprtf | 正则清洗 | — |
| Calibre 电子书 | `.mobi`, `.azw`, `.azw3` | Calibre ebook-convert | 无回退 | Calibre（必选） |

## 多语言章节检测系统

`utils.py` 中的章节检测支持 **13 种语言**：

| 语言 | 匹配模式 | 特殊处理 |
|------|---------|---------|
| English | `Chapter N`/`Ch. N`（1-99 阿拉伯数字 + 罗马数字 I-VII...） | `_HEADING_TAIL` 区分标题和交叉引用 |
| French | `Chapitre N` | 同上 |
| German | `Kapitel N` | 同上 |
| Spanish | `Capítulo N` | 同上 |
| Italian | `Capitolo N` | 同上 |
| Dutch | `Hoofdstuk N`/`ch.N` | 同上 |
| Portuguese | `Capítulo N` | 同上 |
| Chinese | `第N章/回/卷/节/篇/讲` | 中文数字解析（`_cn_numeral_to_int`，支持"一百零八"=108）、全角阿拉伯数字、CJK 序号标题（`## 一 · 缘起`） |
| Japanese | 同上 CJK 模式 | 同上 |
| Korean | `제N장/편/절/관` | 支持插入后缀(`제6장의2`)，尾部语义区分标题/引用 |
| Thai | `บทที่ N`/`ตอนที่ N`/`ภาคที่ N` | 泰语数字映射(U+0E50-0E59) |
| Markdown/AsciiDoc | `# Title`/`== Section`/`===` 下划线 | `_structural_chapter_count()` 跳过代码块内标题 |
| RST/Setext | 下划线标题（`===`/`---`） | 同上 |

附加检测：
- **目录检测**：`_TOC_HEADERS` 含 13 种语言的目录标题词，仅在前 30K 字符内搜索
- **罗马数字转换**：`_int_to_roman()`/`_roman_to_int()` 含回转校验拒绝非规范形式（IIII/VV）
- **章节号识别**：`_chapter_number()` 综合所有模式，行长>80 跳过
- **结构检测主函数**：`detect_structure()` 先数字章节匹配，回退结构标题计数

## 可选依赖组

| 组名 | pip 包名 | 覆盖格式 |
|------|---------|---------|
| `epub` | ebooklib, beautifulsoup4 | EPUB |
| `pdf` | pypdf, pdfminer.six | PDF（text 模式） |
| `docx` | python-docx | DOCX |
| `rtf` | striprtf | RTF |
| `technical` | docling | PDF（technical 模式，保留表格/代码块） |
| `all` | 全部 | 全部格式 |

## SKILL.md 生成流水线（AI Agent 执行）

### 4 种运行模式

| 模式 | 步骤范围 | 输出 |
|------|---------|------|
| Mode 1 (Full Conversion) | Steps 0-9 | SKILL.md + chapters/ + glossary + patterns + cheatsheet |
| Mode 2 (Analyze Only) | Steps 0-3 | 提取报告 |
| Mode 3 (Generate from Prior Analysis) | Steps 4-9 | 跳过提取，从已有分析生成 |
| Mode 4 (Update/Fold-in) | 6 步增量 | 合并新内容到已有 Skill |

### 10 步流程

| 步骤 | 内容 | 关键操作 |
|------|------|---------|
| Step 0 | 范围检查 | 识别输入路径/slug/更新操作 |
| Step 1.5 | 内容类型选择 | technical（Docling）vs text-heavy（pdftotext） |
| Step 2 | 提取 | 运行 extract.py，生成 full_text.txt + metadata.json |
| Step 2.5 | 成本预估 | 基于 metadata 计算 token 预估，等待用户确认 |
| Step 2.6 | REPL 式访问 | >50K token 大书使用 grep/sed/Read 程序化探测 |
| Step 3 | 结构分析 | 读取前 8000 字符识别标题/作者/章节/主题 |
| Step 4 | 用途选择 | 应用框架/思维模型/参考/全部 → DEPTH=reference/study |
| Step 5 | 命名与位置 | slug 命名、SKILLS_HOME 探测（8 个可能位置）、重名检测 |
| Step 7 | 章节摘要 | `chapters/ch<NN>-<slug>.md`（per-chapter token 预算 800-3000） |
| Step 8 | 辅助文件 | glossary.md（≤1500 tokens）、patterns.md（≤2000）、cheatsheet.md（≤1200） |
| Step 9 | 主 SKILL.md | frontmatter + Core Frameworks + Chapter Index + Topic Index + Supporting Files（≤4000 tokens） |
| Step 9.5 | 安全扫描 | 运行 scan_generated_skill.py |
| Step 10 | 清理报告 | 删除临时目录，打印成功报告 |

### Per-chapter Token 预算矩阵

| 模式 | reference | study |
|------|-----------|-------|
| text | 800–1,200 | 1,000–1,800 |
| technical | 1,200–1,800 | 2,000–3,000 |

### 章节模板

Core Idea → Frameworks Introduced → Key Concepts → Mental Models → Anti-patterns → Code Examples(technical) → Reference Tables(technical) → Worked Example(study) → Key Takeaways → Connects To

### 8 个 SKILLS_HOME 探测位置

1. `~/.copilot/skills/`
2. `~/.agents/skills/`
3. `~/.claude/skills/`
4. `.github/skills/`
5. `.claude/skills/`
6. `.agents/skills/`
7. `~/.config/agents/skills/`
8. `~/.config/amp/skills/`

## 8 条质量规则

1. 提取结构非摘要
2. 保留作者精确命名
3. 密度优于完整性
4. 实践者语气
5. SKILL.md 前置加载
6. 章节按需加载
7. 绝不复制原文
8. 主题索引关键

## 分层安全架构

| 层 | 措施 | 位置 |
|----|------|------|
| 1 | 零宽字符/Tag 区块清洗 | `sanitize.py` |
| 2 | DOCX XXE/Billion-Laughs 防护 | `parsers/docx.py`（`validate_docx_xml_safety()`） |
| 3 | 子进程路径绝对化防参数注入 | `dependencies.py`/`parsers/` |
| 4 | 生成后安全扫描（7 类注入+渗出） | `tools/scan_generated_skill.py` |
| 5 | CI 层 CodeQL/Bandit/Zizmor | `.github/` |

## 核心函数索引

| 函数 | 文件 | 说明 |
|------|------|------|
| `extract_single_file()` | `utils.py:410-599` | 单文件提取主流程（格式嗅探→提取→清洗→元数据返回） |
| `main()` | `utils.py:612-735` | 批量处理入口：参数解析→逐文件提取→合并文本→结构检测→输出 |
| `detect_structure()` | `utils.py:292-323` | 返回 {chapters_detected, chapter_headings_sample, has_toc} |
| `resolve_input_files()` | `utils.py:362-407` | 文件/目录/glob 三种输入处理，去重保留顺序 |
| `sanitize_extracted_text()` | `sanitize.py:4-24` | 零宽字符/BOM/Tag 区块清洗 |
| `prepare_dependencies()` | `dependencies.py:166-213` | 按格式准备依赖（检查+提示安装） |
| `run_dependency_check()` | `dependencies.py:216-289` | 所有可选依赖扫描报告 |
| `clean_pdftotext()` | `parsers/pdf.py:14-47` | 换页分页、页眉页脚频率移除、连字符断词合并 |
| `extract_with_zipfile()` (EPUB) | `parsers/epub.py:49-111` | OPF manifest+spine 解析，按阅读顺序提取 |
| `validate_docx_xml_safety()` | `parsers/docx.py:71-92` | XXE/Billion-Laughs 检测 |
| `_cn_numeral_to_int()` | `utils.py:214-229` | 中文数字→整数（1-999） |
| `_roman_to_int()` | `utils.py:244-257` | 罗马数字→整数（回转校验） |
| `estimate_tokens()` | `utils.py:50-51` | `len(text.split()) / 0.75` |
