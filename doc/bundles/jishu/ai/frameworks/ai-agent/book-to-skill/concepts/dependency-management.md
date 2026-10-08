---
type: Concept
title: 依赖管理系统
description: book-to-skill的三层依赖分组体系——core（python-docx+BeautifulSoup4+striprtf，2.5MB）、advanced（ebooklib+pypdf+pdfminer.six，6.4MB）、full（docling，2.5GB+）、stdlib零依赖回退链、uv run一键安装、4种CLI安装模式（--install/--interactive/--docling/--no-deps）、Claude Code自动安装（uv+venv检测）、跨平台支持（Windows/macOS/Linux，含WSL）、pip installable包发布。
tags: [book-to-skill, dependencies, uv, pip, stdlib-fallback, optional-dependencies, installation, venv, cross-platform]
generated: { by: "agent:okf-doc-generator", at: "2026-08-22T22:44:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject
    resource: ../../../../../../external/libs/models/ai/book-to-skill/pyproject.toml
    title: 项目配置和依赖声明
  - id: cli
    resource: ../../../../../../external/libs/models/ai/book-to-skill/book_to_skill/cli.py
    title: CLI入口和安装检查逻辑
  - id: deps
    resource: ../../../../../../external/libs/models/ai/book-to-skill/book_to_skill/deps.py
    title: 依赖可用性检测
  - id: setup
    resource: ../../../../../../external/libs/models/ai/book-to-skill/SETUP.md
    title: 安装指南
  - id: skill-md
    resource: ../../../../../../external/libs/models/ai/book-to-skill/SKILL.md
    title: Skill定义（自动安装指令）
---

# 依赖管理系统

book-to-skill 采用**分层可选依赖**策略，将第三方库按功能分为 core/advanced/full 三个分组，每个格式解析器都有 stdlib 零依赖回退方案。用户可以按需安装最小依赖子集（仅 core 即可处理 DOCX/HTML/RTF + 部分 PDF/EPUB），也可以一键安装 full 组获取最佳提取质量。系统还支持 uv 包管理器自动安装、交互式依赖选择、pip 可安装包发布。

## 设计原理

1. **最小可用**：仅 core 依赖（2.5MB）即可处理 DOCX/HTML/RTF/纯文本 + PDF/EPUB 的 stdlib 回退
2. **优雅降级**：每个可选依赖缺失时自动回退到 stdlib 方案，不中断流程
3. **按需扩展**：advanced 组（+6.4MB）获得更好的 PDF/EPUB 质量；full 组（+2.5GB Docling）获得技术文档结构化提取
4. **零配置安装**：Claude Code 环境下自动检测 uv 并创建 venv，用户无需手动配置
5. **跨平台**：支持 Windows/macOS/Linux，含 WSL 路径处理

## 依赖分层架构

```mermaid
graph TB
    CORE["Core层<br/>~2.5MB"] -->|基础| STDLIB["stdlib<br/>(零依赖回退)"]
    ADV["Advanced层<br/>~6.4MB"] -->|扩展| CORE
    FULL["Full层<br/>~2.5GB"] -->|最佳| ADV
    SYS["系统工具"] -->|外部| FULL

    CORE --> C1["python-docx<br/>DOCX解析"]
    CORE --> C2["BeautifulSoup4<br/>HTML解析"]
    CORE --> C3["striprtf<br/>RTF解析"]

    ADV --> A1["ebooklib<br/>EPUB解析"]
    ADV --> A2["pypdf<br/>PDF快速解析"]
    ADV --> A3["pdfminer.six<br/>PDF深度解析"]

    FULL --> F1["docling<br/>技术PDF<br/>(表格/代码块)"]
    SYS --> S1["pdftotext<br/>(poppler)"]
    SYS --> S2["ebook-convert<br/>(Calibre)"]

    STDLIB --> Z1["zipfile+xml<br/>DOCX/EPUB回退"]
    STDLIB --> Z2["html.parser<br/>HTML回退"]
    STDLIB --> Z3["正则RTF<br/>RTF回退"]
    STDLIB --> Z4["pathlib<br/>纯文本读取"]

    style CORE fill:#22c55e,color:#000
    style ADV fill:#f97316,color:#000
    style FULL fill:#ef4444,color:#fff
    style STDLIB fill:#8b5cf6,color:#fff
```

## 依赖分组详情

### Core 组（必选，~2.5MB）

| 包名 | 版本要求 | 用途 | 缺失影响 |
|------|---------|------|---------|
| python-docx | ≥0.8.11 | DOCX 段落/表格提取 | DOCX 回退到 stdlib ZIP/XML 解析 |
| beautifulsoup4 | ≥4.12.0 | HTML/EPUB 文本提取 | HTML 回退到 stdlib html.parser；EPUB 回退到 stdlib zipfile |
| striprtf | ≥0.0.26 | RTF 转纯文本 | RTF 回退到正则表达式清洗 |

```toml
# pyproject.toml
dependencies = [
    "python-docx>=0.8.11",
    "beautifulsoup4>=4.12.0",
    "striprtf>=0.0.26",
]
```

### Advanced 组（可选，+6.4MB）

| 包名 | 版本要求 | 用途 | 缺失影响 |
|------|---------|------|---------|
| ebooklib | ≥0.18 | EPUB 结构化解析（manifest/spine） | EPUB 回退到 stdlib zipfile |
| pypdf | ≥4.0 | PDF 快速文本提取 | PDF 回退链退化为 pdftotext→pdfminer→stdlib |
| pdfminer.six | ≥20231228 | PDF 深度文本提取 | 作为 pypdf 失败后的备用方案 |

```toml
[project.optional-dependencies]
advanced = [
    "ebooklib>=0.18",
    "pypdf>=4.0",
    "pdfminer.six>=20231228",
]
```

### Full 组（可选，+2.5GB）

| 包名 | 版本要求 | 用途 | 缺失影响 |
|------|---------|------|---------|
| docling | ≥2.0 | 技术文档结构化提取（表格/代码块 → Markdown） | technical 模式 PDF 退化为 text-heavy 提取 |

```toml
full = [
    "book-to-skill[advanced]",
    "docling>=2.0",
]
```

> **注意**：Docling 依赖 PyTorch 和多个 ML 模型，首次使用会下载模型文件。提取速度约 1.5 秒/页（pdftotext 约 0.1 秒/页），但能保留表格和代码块的 Markdown 结构。

### 系统工具（外部）

| 工具 | 提供方 | 用途 | 缺失影响 |
|------|--------|------|---------|
| `pdftotext` | Poppler | PDF 快速布局提取（`-layout` 模式） | PDF 回退链起点不可用 |
| `pdfinfo` | Poppler | PDF 页数统计 | 页数统计回退到 pypdf |
| `ebook-convert` | Calibre | MOBI/AZW/AZW3 转 EPUB 后提取 | MOBI/AZW 格式完全不可用（唯一硬依赖） |

### Stdlib 零依赖回退

所有格式都有 Python 标准库回退方案，确保在任何 Python 3.10+ 环境中都能运行：

| 格式 | stdlib 回退 | 质量 |
|------|-----------|------|
| DOCX | `zipfile` + `xml.etree` | 可提取段落文本和表格，无 python-docx 的样式/格式信息 |
| EPUB | `zipfile` + `html.parser.HTMLParser` | 可按 spine/manifest 顺序提取 HTML 文本 |
| HTML | `html.parser.HTMLParser` | 基础纯文本提取，无 BeautifulSoup 的容错性 |
| RTF | 正则表达式 | 基础转义解码，无 striprtf 的完整 RTF 指令处理 |
| PDF | 无纯 stdlib 方案 | 依赖 pdftotext 或 pypdf/pdfminer |
| 纯文本 | `pathlib` + 多编码检测 | 完整支持 |

## 依赖可用性检测

`deps.py` 模块在运行时检测各依赖是否可用：

```python
# deps.py
class DependencyStatus:
    def __init__(self):
        self.has_python_docx = self._try_import('docx')
        self.has_bs4 = self._try_import('bs4')
        self.has_striprtf = self._try_import('striprtf')
        self.has_ebooklib = self._try_import('ebooklib')
        self.has_pypdf = self._try_import('pypdf')
        self.has_pdfminer = self._try_import('pdfminer')
        self.has_docling = self._try_import('docling')
        self.has_pdftotext = self._check_command('pdftotext')
        self.has_pdfinfo = self._check_command('pdfinfo')
        self.has_ebook_convert = self._check_command('ebook-convert')

    def format_report(self) -> str:
        """生成依赖可用性报告"""
        lines = ["Dependency status:"]
        for name, available in self._asdict().items():
            icon = "✓" if available else "✗"
            lines.append(f"  {icon} {name}")
        return "\n".join(lines)
```

## CLI 安装模式

```bash
# 核心依赖（最小可用）
uv pip install book-to-skill
# 或
pip install book-to-skill

# 高级依赖（更好的PDF/EPUB质量）
uv pip install "book-to-skill[advanced]"
pip install "book-to-skill[advanced]"

# 完整依赖（含Docling，~2.5GB）
uv pip install "book-to-skill[full]"
pip install "book-to-skill[full]"
```

CLI 提供 4 种安装相关标志：

| 标志 | 行为 |
|------|------|
| `--install` | 自动检测 uv/pip 并安装 core 依赖 |
| `--interactive` | 交互式选择安装层级（core/advanced/full） |
| `--docling` | 安装 full 组（含 Docling） |
| `--no-deps` | 不检查依赖，直接运行（假设依赖已就绪） |

```mermaid
graph TB
    CLI["book-to-skill CLI"] --> CHECK["依赖检查"]
    CHECK -->|全部可用| RUN["直接运行"]
    CHECK -->|缺失| MODE{"安装模式?"}
    MODE -->|--install| AUTO["自动安装core<br/>(检测uv→pip)"]
    MODE -->|--interactive| INT["交互式选择<br/>core/advanced/full"]
    MODE -->|--docling| FULL["安装full组<br/>(含Docling)"]
    MODE -->|--no-deps| SKIP["跳过检查<br/>(运行时可能失败)"]
    MODE -->|无标志| WARN["警告缺失<br/>提示安装命令"]

    style CHECK fill:#8b5cf6,color:#fff
    style AUTO fill:#22c55e,color:#000
    style INT fill:#f97316,color:#000
    style FULL fill:#ef4444,color:#fff
```

## Claude Code 自动安装

在 Claude Code 环境中（Skill 被触发时），book-to-skill 提供零配置自动安装流程：

```
Step 1: 检测 CLI 是否可用
  → which book-to-skill / python -m book_to_skill

Step 2: 不可用时自动安装
  → 优先检测 uv（UV_REQUIRED=true）
    - 已有项目 venv → uv pip install book-to-skill
    - 无 venv → uv tool install book-to-skill
  → uv 不可用 → pip install book-to-skill

Step 3: 安装后再次验证
  → book-to-skill --version
```

### UV_REQUIRED 策略

book-to-skill 优先使用 uv 作为包管理器（比 pip 快 10-100 倍）：

```python
# SKILL.md 中的自动安装逻辑
def ensure_installed():
    if shutil.which('uv'):
        # uv 可用：优先使用
        if in_venv():
            subprocess.run(['uv', 'pip', 'install', 'book-to-skill'], check=True)
        else:
            subprocess.run(['uv', 'tool', 'install', 'book-to-skill'], check=True)
    elif shutil.which('pip'):
        # pip 回退
        subprocess.run(['pip', 'install', 'book-to-skill'], check=True)
    else:
        raise InstallationError("Neither uv nor pip found")
```

## 跨平台支持

| 平台 | 支持状态 | 注意事项 |
|------|---------|---------|
| macOS | ✅ 完全支持 | Homebrew 安装 poppler/calibre |
| Linux | ✅ 完全支持 | apt/yum 安装 poppler-utils/calibre |
| Windows | ✅ 支持 | WSL 推荐用于 poppler/calibre；原生 Windows 使用 pip 安装 Python 依赖 |
| WSL2 | ✅ 完全支持 | Windows 路径通过 `/mnt/c/...` 访问 |

### WSL 路径处理

在 WSL 环境中，如果输入路径是 Windows 路径（`C:\...`），自动转换为 WSL 路径（`/mnt/c/...`）。

## Pip Installable 包发布

book-to-skill 配置为标准的 pip-installable Python 包：

```toml
# pyproject.toml
[project]
name = "book-to-skill"
version = "0.1.0"
requires-python = ">=3.10"

[project.scripts]
book-to-skill = "book_to_skill.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["book_to_skill"]
```

CLI 入口点 `book-to-skill` 指向 `book_to_skill.cli:main`，安装后可直接在命令行使用。

## 提取器与依赖的映射关系

```mermaid
graph LR
    subgraph 格式解析器
        PDFX[PDF解析器]
        EPUBX[EPUB解析器]
        DOCXX[DOCX解析器]
        HTMLX[HTML解析器]
        RTFX[RTF解析器]
        TEXTX[文本读取器]
        CALX[Calibre解析器]
    end

    subgraph Core依赖
        PD[python-docx]
        BS[BeautifulSoup4]
        SR[striprtf]
    end

    subgraph Advanced依赖
        EL[ebooklib]
        PP[pypdf]
        PM[pdfminer.six]
    end

    subgraph Full依赖
        DC[docling]
    end

    subgraph 系统工具
        PT[pdftotext]
        PI[pdfinfo]
        EC[ebook-convert]
    end

    subgraph Stdlib回退
        ZF[zipfile]
        ZX[xml.etree]
        ZH[html.parser]
        ZR[正则]
        ZP[pathlib]
    end

    PDFX -->|text-heavy首选| PT
    PDFX -->|technical首选| DC
    PDFX -->|回退1| PP
    PDFX -->|回退2| PM
    PDFX -->|页数统计| PI

    EPUBX -->|首选| EL
    EPUBX -->|辅助| BS
    EPUBX -->|回退| ZF

    DOCXX -->|首选| PD
    DOCXX -->|回退| ZF
    DOCXX -->|回退| ZX

    HTMLX -->|首选| BS
    HTMLX -->|回退| ZH

    RTFX -->|首选| SR
    RTFX -->|回退| ZR

    TEXTX -->|首选| ZP

    CALX -->|硬依赖| EC

    style ZF fill:#8b5cf6,color:#fff
    style ZX fill:#8b5cf6,color:#fff
    style ZH fill:#8b5cf6,color:#fff
    style ZR fill:#8b5cf6,color:#fff
    style ZP fill:#8b5cf6,color:#fff
```

## 相关概念

- [四层产出流水线](four-layer-pipeline.md) — 依赖管理在流水线中的角色（Step 0-1 环境检查阶段）
- [多格式解析器](multi-format-parsers.md) — 各格式解析器的依赖链和回退逻辑
- [安全清洗机制](security-sanitization.md) — 安全扫描脚本无外部依赖（stdlib only）
