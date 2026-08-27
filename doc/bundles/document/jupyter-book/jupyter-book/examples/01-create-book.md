---
type: example
title: "创建你的第一本书"
description: "从零开始安装 Jupyter Book v2、初始化项目、添加内容、配置导出格式，并在浏览器中预览"
tags: [jupyter-book, example, getting-started, init, preview]
generated: 2026-08-23
verified: false
status: stable
stale_after: 2027-12-31
sources:
  - path: "py/jupyter_book/__main__.py"
    facts: [F-001, F-002]
  - path: "ts/init.ts"
    facts: [F-017, F-018]
  - path: "ts/index.ts"
    facts: [F-011]
---

# 创建你的第一本书

本示例带你从零开始创建一个 Jupyter Book 项目：安装、初始化、添加内容、预览。

## 前提条件

- Python 3.9+
- pip 包管理器
- 网络连接（首次运行时自动下载 Node.js，约 30-50MB）

> 如果你的系统已有 Node.js 18+，Jupyter Book 会直接使用，无需额外下载。

## 步骤 1：安装 Jupyter Book

```bash
pip install jupyter-book>=2.0
```

验证安装：

```bash
jupyter-book --version
# 或
jupyter-book --help
```

首次运行时，如果系统没有合适的 Node.js，Jupyter Book 会提示是否自动安装：

```
[Node.js] No suitable Node.js found on your system.
Would you like to download and install Node.js v22.17.0?
This will create an isolated environment in your user data directory.
[y/N]: y

Downloading Node.js v22.17.0...
Installing nodeenv environment...
Done!
```

输入 `y` 回车即可（CI 环境可设置 `JB_ALLOW_NODEENV=1` 跳过交互）。

## 步骤 2：初始化项目

创建一个新目录并初始化：

```bash
mkdir my-first-book && cd my-first-book
jupyter-book init
```

`jupyter-book init` 会启动交互式向导（因为没有带任何参数，init 是默认命令），询问：

1. **项目名称**：默认为目录名 "my-first-book"
2. **作者姓名**：你的名字
3. **项目描述**：简短描述
4. **是否包含示例内容**：Yes（推荐，首次使用）
5. **是否配置 GitHub Pages**：No（稍后可以手动配置）
6. **是否生成 TOC**：Yes

向导完成后，项目结构如下：

```
my-first-book/
├── myst.yml          # 项目配置文件
├── intro.md          # 首页
├── markdown.md       # Markdown 语法示例（如果选了示例内容）
├── markdown-notebooks.md  # Notebook 示例
└── _static/          # 静态资源（如果有）
```

### myst.yml 配置文件

自动生成的 `myst.yml` 类似：

```yaml
version: 1
project:
  title: "My First Book"
  author: "Your Name"
  description: "A sample Jupyter Book"
  keywords: []

site:
  template: book-theme
  options:
    logo: _static/logo.png  # 如果有 logo

build:
  exports:
    - format: html
  execute:
    execute_notebooks: "auto"
```

## 步骤 3：添加内容

使用你喜欢的编辑器创建和编辑 Markdown 文件。创建一个新章节 `chapters/installation.md`：

```bash
mkdir chapters
```

`chapters/installation.md`：

```markdown
---
title: "安装指南"
description: "如何安装 Jupyter Book 和相关工具"
---

# 安装指南

## 使用 pip 安装

Jupyter Book v2 可以通过 pip 安装：

```bash
pip install jupyter-book>=2.0
```

## 使用 conda 安装

如果你使用 Anaconda/Miniconda：

```bash
conda install -c conda-forge jupyter-book
```

## 验证安装

安装后，运行以下命令验证：

```bash
jupyter-book --help
```

如果看到帮助信息，说明安装成功。

{note}
首次运行 `jupyter-book build` 时可能需要下载 Node.js 运行时。
这是正常行为，只需要约 1 分钟。
```

更新 `intro.md` 作为首页：

```markdown
---
title: "欢迎来到我的第一本书"
---

# 我的第一本书

这是用 Jupyter Book v2 创建的示例书籍。

## 目录

- 安装指南（`chapters/installation.md`）
- Markdown 示例（`markdown.md`）

## 关于本书

本书展示了 Jupyter Book 的核心功能：
- 使用 MyST Markdown 编写内容
- 多格式导出（HTML、PDF、DOCX）
- 实时预览和热重载
```

## 步骤 4：启动开发服务器预览

```bash
jupyter-book start
```

输出类似：

```
🔌 Jupyter Book server started on http://localhost:3000
📖 Serving project: my-first-book
```

在浏览器中打开 http://localhost:3000，你会看到：
- 左侧导航栏（自动生成的目录）
- 右侧内容区域
- 顶部工具栏（搜索、目录切换、主题切换）
- 深色/浅色模式切换

开发服务器支持热重载：编辑 Markdown 文件后保存，浏览器会自动刷新。

## 步骤 5：构建静态 HTML 网站

停止开发服务器（Ctrl+C），然后构建静态网站：

```bash
jupyter-book build --html
```

构建产物在 `_build/site/` 目录：

```
_build/
└── site/
    ├── index.html
    ├── chapters/
    │   └── installation.html
    ├── markdown.html
    ├── _static/
    └── myst.xlsx  # 构建元数据
```

你可以用任何静态文件服务器预览构建结果：

```bash
cd _build/site
python -m http.server 8080
# 或使用 npx serve
npx serve
```

## 步骤 6：构建 PDF

构建 PDF 需要安装 LaTeX 发行版（TeX Live 推荐）。如果未安装，可以跳过此步骤，稍后安装后再试。

配置 PDF 导出，在 `myst.yml` 中添加：

```yaml
build:
  exports:
    - format: html
    - format: pdf
      template: default
      output: exports/my-book.pdf
```

然后构建：

```bash
jupyter-book build --pdf
```

输出在 `_build/exports/my-book.pdf`。

如果不想安装 LaTeX，可以尝试 Typst PDF 路径（需安装 [typst CLI](https://github.com/typst/typst)）：

```yaml
build:
  exports:
    - format: typst
```

```bash
jupyter-book build --typst
```

## 步骤 7：构建 Word 文档

```bash
jupyter-book build --docx
```

输出 `.docx` 文件，可以用 Microsoft Word 或 Google Docs 打开编辑。

## 常用命令速查

| 命令 | 说明 |
|------|------|
| `jupyter-book init` | 初始化新项目 |
| `jupyter-book start` | 启动开发服务器 |
| `jupyter-book build` | 构建文档（默认 HTML）|
| `jupyter-book build --html` | 构建 HTML 网站 |
| `jupyter-book build --pdf` | 构建 PDF（LaTeX 路径）|
| `jupyter-book build --docx` | 构建 Word 文档 |
| `jupyter-book build --all` | 构建所有配置的格式 |
| `jupyter-book clean` | 清理构建产物 |
| `jupyter-book templates list` | 列出可用模板 |
| `jupyter-book templates download <name>` | 下载模板 |
| `jupyter-book --debug <command>` | 调试模式（显示详细日志）|

## 项目结构参考

一个典型的 Jupyter Book 项目：

```
my-book/
├── myst.yml               # 主配置文件
├── intro.md               # 首页（必须）
├── references.bib         # 参考文献（可选）
├── _static/               # 静态资源
│   ├── logo.png
│   └── custom.css
├── chapters/              # 章节目录
│   ├── chapter1.md
│   └── chapter2.md
├── notebooks/             # Jupyter 笔记本
│   └── analysis.ipynb
├── _templates/            # 自定义模板（可选）
│   └── my-template/
│       ├── template.tex
│       └── template.yml
└── _build/                # 构建产物（自动生成，不纳入版本控制）
    ├── site/
    ├── exports/
    └── myst.build.json
```

## 下一步

- 学习 MyST Markdown 的更多语法：角色、指令、交叉引用
- 配置自定义模板
- 添加参考文献
- 发布到 GitHub Pages
- 执行 Jupyter 笔记本中的代码

## 相关概念

- [00-v2-architecture](../concepts/00-v2-architecture.md)：v2 双层架构
- [02-ts-cli-commands](../concepts/02-ts-cli-commands.md)：CLI 命令详解
- [04-template-system](../concepts/04-template-system.md)：模板系统
- [02-build-publish](02-build-publish.md)：构建与发布
