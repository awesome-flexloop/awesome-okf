---
type: example
title: "构建与发布"
description: "配置多格式导出、执行 Jupyter 笔记本代码、部署到 GitHub Pages 和生成出版级 PDF"
tags: [jupyter-book, example, build, publish, github-pages, deployment]
generated: 2026-08-23
verified: false
status: stable
stale_after: 2027-12-31
sources:
  - path: "ts/build.ts"
    facts: [F-016]
  - path: "ts/site.ts"
    facts: [F-020]
  - path: "myst-cli/src/build/utils/localArticleExport.ts"
    facts: [F-039, F-040]
---

# 构建与发布

本示例演示如何为 Jupyter Book 项目配置多格式构建、执行代码笔记本、生成出版级 PDF，以及部署到 GitHub Pages。

## 完整项目配置示例

以下是一个功能完整的 `myst.yml` 配置：

```yaml
version: 1
project:
  title: "数据科学导论"
  author: "张教授"
  description: "面向本科生的数据科学入门教材"
  keywords: [data-science, python, machine-learning]
  github: https://github.com/your-username/data-science-book
  bibliography: references.bib

  # 目录结构
  toc:
    - file: intro.md
      title: 前言
    - title: 基础篇
      children:
        - file: chapters/01-getting-started.md
        - file: chapters/02-python-basics.md
        - file: chapters/03-data-structures.md
    - title: 进阶篇
      children:
        - file: chapters/04-numpy.md
        - file: chapters/05-pandas.md
        - file: chapters/06-visualization.md
    - file: chapters/references.md
      title: 参考文献

site:
  template: book-theme
  options:
    logo: _static/logo.png
    favicon: _static/favicon.ico
    # 编辑链接
    edit_url: https://github.com/your-username/data-science-book/edit/main
    # 导航栏链接
    nav:
      - title: 课程主页
        url: https://example.com/course
  # 自定义样式
  styles:
    - _static/custom.css

build:
  # 执行笔记本配置
  execute:
    execute_notebooks: "auto"  # auto | force | off | cache
    timeout: 120               # 单格超时秒数
    allow_errors: false        # 是否允许代码错误

  # 多格式导出
  exports:
    # HTML 网站
    - format: html

    # PDF (LaTeX 路径，出版级)
    - format: pdf
      template: arxiv_two_column
      output: exports/textbook.pdf
      template_options:
        font_size: 11
        papersize: a4

    # PDF (Typst 路径，快速预览)
    - format: typst
      output: exports/textbook-preview.pdf

    # Word 文档（给编辑审阅）
    - format: docx
      output: exports/textbook.docx

    # JATS XML（提交到期刊平台）
    - format: xml
      output: exports/textbook.xml

    # MyST Markdown（备份/归档）
    - format: md
      output: exports/textbook.md
```

## 构建命令

### 构建 HTML 网站

```bash
jupyter-book build --html
# 或简写（默认构建 HTML）
jupyter-book build
```

输出在 `_build/site/`。

### 构建 PDF

```bash
# LaTeX 路径（高质量，需要 TeX Live）
jupyter-book build --pdf

# Typst 路径（快速，需要 typst CLI）
jupyter-book build --typst
```

### 构建所有格式

```bash
jupyter-book build --all
```

### 构建指定文件

```bash
jupyter-book build chapters/04-numpy.md --pdf
```

### 清理构建产物

```bash
# 清理所有
jupyter-book clean

# 只清理 HTML
jupyter-book clean --html

# 只清理导出文件
jupyter-book clean --exports

# 清理临时文件（保留最终产物）
jupyter-book clean --temp
```

## 执行 Jupyter 笔记本

Jupyter Book v2 内置代码执行支持，可以在构建时执行 `.ipynb` 笔记本或 Markdown 中的代码单元格。

### 配置执行模式

在 `myst.yml` 的 `build.execute` 中配置：

| execute_notebooks 值 | 行为 |
|---------------------|------|
| `"auto"` | 笔记本修改后重新执行（基于缓存）|
| `"force"` | 每次构建都强制执行 |
| `"off"` | 不执行，使用笔记本中已有的输出 |
| `"cache"` | 使用缓存，未修改的笔记本不重新执行 |

### 代码单元格示例

在 Markdown 中使用 `{code-cell}` 指令：

````markdown
```{code-cell} python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title("Sine Wave")
plt.show()
```
````

或直接使用 `.ipynb` 文件（在 toc 中引用即可）。

### 执行注意事项

1. **内核**：确保 Python 环境安装了所需的包（numpy、pandas、matplotlib 等）
2. **超时**：长时间运行的代码可能需要增大 `timeout` 值
3. **错误处理**：设置 `allow_errors: true` 允许代码出错继续构建
4. **缓存**：使用 `"auto"` 或 `"cache"` 模式加速增量构建
5. **Binder**：可以配置 Binder 链接让读者在线执行代码

## 选择和下载模板

### 查看可用模板

```bash
# 列出所有模板
jupyter-book templates list

# 按类型过滤
jupyter-book templates list --pdf
jupyter-book templates list --site

# 按标签过滤
jupyter-book templates list --tag paper

# 查看特定模板详情
jupyter-book templates list arxiv_two_column
```

### 下载模板到本地

```bash
# 下载到 _templates 目录
jupyter-book templates download arxiv_two_column ./_templates/arxiv

# 覆盖已存在的模板
jupyter-book templates download arxiv_two_column ./_templates/arxiv --force
```

下载后在 myst.yml 中使用本地路径：

```yaml
build:
  exports:
    - format: pdf
      template: _templates/arxiv
```

### 自定义模板

参考 [自定义 jtex 模板示例](../../myst-exporters/examples/02-custom-jtex-template.md)。

## 部署到 GitHub Pages

### 方法一：使用 --gh-pages 选项

初始化时配置 GitHub Pages：

```bash
jupyter-book init --gh-pages
```

或在现有项目中手动配置。Jupyter Book 会创建 GitHub Actions 工作流文件。

### 方法二：手动配置 GitHub Actions

在项目中创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy Jupyter Book

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Jupyter Book
        run: |
          pip install jupyter-book>=2.0
          # 如需 PDF 导出，安装 TeX Live
          # sudo apt-get install texlive-latex-recommended texlive-xetex texlive-fonts-recommended

      - name: Build book
        run: jupyter-book build --html
        env:
          JB_ALLOW_NODEENV: "1"  # 自动安装 Node.js

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./_build/site
```

提交并推送到 GitHub，在仓库设置中启用 GitHub Pages（Source: GitHub Actions）。

### 方法三：手动部署

```bash
# 构建
jupyter-book build --html

# 使用 gh-pages 工具
npx gh-pages -d _build/site
```

## 出版级 PDF 工作流

### 配置学术模板

```yaml
build:
  exports:
    - format: pdf
      template: arxiv_two_column
      output: exports/paper.pdf
      template_options:
        font_size: 10
        papersize: letter
        line_numbers: false
        keywords: true
```

### 添加参考文献

创建 `references.bib`：

```bibtex
@article{smith2023example,
  title     = {An Example Paper},
  author    = {Smith, John and Doe, Jane},
  journal   = {Journal of Examples},
  volume    = {5},
  number    = {2},
  pages     = {1--10},
  year      = {2023},
  publisher = {Example Publisher}
}
```

在 myst.yml 中引用：

```yaml
project:
  bibliography: references.bib
```

在 Markdown 中引用：

```markdown
如 Smith 和 Doe [-@smith2023example] 所示...
```

### 添加摘要和作者信息

在文档 frontmatter 中：

```markdown
---
title: "论文标题"
authors:
  - name: "张三"
    affiliations:
      - "某某大学计算机系"
    corresponding: true
    email: "zhangsan@example.edu"
  - name: "李四"
    affiliations:
      - "某某研究院"
date: 2026-08-23
parts:
  abstract: |
    本文提出了一种新方法...
keywords:
  - 关键词1
  - 关键词2
---
```

### 导出 JATS XML 供期刊提交

```yaml
build:
  exports:
    - format: xml
```

```bash
jupyter-book build --jats
```

生成的 JATS XML 可以直接提交到支持 JATS 的期刊平台（如 eLife、PubMed Central 等）。

## 构建检查清单

发布前检查：

- [ ] `jupyter-book build --all` 无错误
- [ ] 所有交叉引用正确解析（无 ?? 问号）
- [ ] 图片路径正确，图片加载正常
- [ ] 代码单元格执行无错误
- [ ] PDF 编译通过，排版正确
- [ ] 内部链接和外部链接可访问
- [ ] 参考文献格式正确
- [ ] 目录（TOC）顺序正确
- [ ] `jupyter-book clean && jupyter-book build --all` 干净构建通过

## 常见问题

### Node.js 安装慢

首次构建时自动下载 Node.js，国内用户可以：
1. 提前安装 Node.js 18+ 并加入 PATH
2. 设置 npm 镜像：`npm config set registry https://registry.npmmirror.com`

### PDF 编译失败

- 检查 TeX Live 是否完整安装
- 查看 `_build/exports/*.log` 中的错误
- 尝试简单模板：`--template default`
- 缺失包用 `tlmgr install <package>` 安装

### 代码执行失败

- 检查 Python 环境是否安装了所需包
- 增大 timeout 值
- 设置 `allow_errors: true` 调试

### 图片路径问题

- 使用相对路径（相对于 Markdown 文件位置）
- 图片放在项目目录内
- PDF 中推荐使用 PDF/EPS/PNG 格式

## 相关概念

- [00-v2-architecture](/concepts/00-v2-architecture.md)：v2 双层架构
- [02-ts-cli-commands](/concepts/02-ts-cli-commands.md)：CLI 命令详解
- [04-template-system](/concepts/04-template-system.md)：模板系统
- [01-create-book](/examples/01-create-book.md)：创建第一本书
