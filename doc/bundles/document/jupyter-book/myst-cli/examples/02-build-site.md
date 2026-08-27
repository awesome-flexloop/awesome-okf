---
type: example
title: "构建站点和导出"
description: "使用myst build命令构建静态站点和多格式文档导出（PDF/Word/LaTeX/HTML等）"
tags: [myst-cli, build, export, pdf, site, html]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/build.ts"
    facts: [F-010, F-011, F-012, F-013, F-014, F-015]
---

# 构建站点和导出

本文档演示如何使用 `myst build` 命令构建站点和导出多种文档格式。

## 前置条件

- 已有初始化的 MyST 项目（包含 myst.yml）
- 项目中有 Markdown 或 Jupyter Notebook 文件

## 构建交互式站点

### 构建站点内容

```bash
# 构建站点（根据 myst.yml 中的 site 配置）
myst build --site

# 构建静态 HTML 站点
myst build --html

# 构建所有内容（站点 + 所有导出格式）
myst build --all
```

构建输出位于 `_build/site/` 目录：
- `_build/site/content/`：JSON 格式的页面内容
- `_build/site/public/`：静态资源（图片、CSS、JS）

### 构建并监视变化

```bash
myst build --site --watch
```

监视文件变化并自动重建。注意：站点的热重载推荐使用 `myst start`。

## 导出文档格式

### 导出 PDF

```bash
# 导出所有声明了 PDF export 的文件
myst build --pdf

# 导出指定文件为 PDF
myst build my-document.md --pdf

# 指定输出文件名
myst build my-document.md --pdf -o output.pdf
```

### 导出 Word 文档

```bash
myst build --docx
# 或
myst build my-document.md --docx -o output.docx
```

### 导出 LaTeX

```bash
myst build --tex
# 生成 .tex 源文件，可用于进一步 LaTeX 编辑
```

### 导出 Typst

```bash
myst build --typst
# 使用 Typst 后端生成 PDF（比 LaTeX 更快）
```

### 导出 Markdown

```bash
myst build --md
# 生成简化的 Markdown（移除 MyST 特有语法）
```

### 导出 JATS XML（学术出版）

```bash
myst build --jats
# 生成 Journal Article Tag Suite XML，用于期刊投稿
```

### 导出 MECA 压缩包

```bash
myst build --meca
# 生成 MECA（Manuscript Exchange Common Approach）压缩包
```

### 导出 CFF 引用文件

```bash
myst build --cff
# 生成 Citation File Format 文件
```

## Frontmatter 中声明导出

可以在文件的 YAML frontmatter 中声明需要的导出格式：

```markdown
---
title: 我的论文
exports:
  - format: pdf
    template: default
  - format: docx
  - format: tex
---

# 论文内容
```

然后运行 `myst build`（不加格式标志）会自动构建所有声明的导出。

使用 `--force` 标志可以忽略 frontmatter 声明，强制构建指定格式：

```bash
myst build my-document.md --pdf --force
```

## 带 Notebook 执行的构建

```bash
# 构建前执行所有 Notebook
myst build --site --execute

# 控制并行执行数
myst build --site --execute --execute-parallel 4
```

## 链接检查

```bash
# 构建时检查外部链接
myst build --site --check-links
```

## 严格模式

```bash
# 警告视为错误，非零退出码
myst build --site --strict
```

适用于 CI/CD 环境。

## CI 模式

```bash
myst build --all --ci
```

CI 模式会优化输出格式和行为，适用于自动化构建环境。

## 构建单个文件

```bash
# 构建单个文件的所有格式（默认启用全格式）
myst build my-file.md

# 构建单个文件的指定格式
myst build my-file.md --pdf --docx

# 构建多个文件
myst build file1.md file2.md --pdf
```

## 图片优化

```bash
# 设置 WebP 转换阈值（默认 1.5MB）
myst build --site --max-size-webp 2
```

大于阈值的图片会自动转换为 WebP 格式以减小体积。

## 构建输出结构

```
_build/
├── site/
│   ├── content/      # JSON 页面内容
│   ├── public/       # 静态资源
│   └── config.json   # 站点配置
├── exports/          # 导出的文档（PDF/DOCX/TEX等）
├── temp/             # 中间产物（LaTeX编译等）
├── cache/            # HTTP缓存
├── logs/             # 构建日志
└── myst.build.json   # 构建元数据日志
```

## 典型工作流

```bash
# 1. 初始化（仅首次）
myst init

# 2. 开发时使用 start 预览
myst start

# 3. 构建生产版本
myst build --all

# 4. 清理构建产物（如需要）
myst clean --all
```

## 相关命令

- [启动开发服务器](03-dev-server.md)
- [初始化项目](01-init-project.md)
- [Build 管线](../concepts/01-build-pipeline.md)
