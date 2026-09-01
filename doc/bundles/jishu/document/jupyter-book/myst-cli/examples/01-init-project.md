---
type: example
title: "初始化MyST项目"
description: "使用myst init初始化新的MyST项目，包括配置生成、TOC创建和Git设置"
tags: [myst-cli, init, getting-started, setup]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/init/init.ts"
    facts: [F-039, F-040, F-041, F-042, F-043]
---

# 初始化 MyST 项目

本文档演示如何使用 `myst init` 初始化一个新的 MyST 项目。

## 前提条件

- 已安装 mystmd（`npm i -g mystmd` 或 `pip install mystmd`）
- 项目目录中有一些 Markdown 文件或 Jupyter Notebook

## 步骤一：创建项目目录

```bash
mkdir my-myst-book
cd my-myst-book
```

## 步骤二：创建第一篇文档

```bash
cat > index.md << 'EOF'
---
title: 我的第一本MyST书
---

# 欢迎

这是我的第一本 MyST 书籍！

## 第一章

这是第一章的内容。
EOF

cat > chapter1.md << 'EOF'
# 第一章

这是第一章的详细内容。

```{note}
这是一个提示框。
```
EOF
```

## 步骤三：运行 init 命令

### 交互式初始化（推荐新手）

```bash
myst init
```

init 命令会：
1. 显示欢迎信息
2. 自动创建/更新 `.gitignore`（添加 `_build`）
3. 检测到没有 myst.yml 配置文件
4. 生成默认的 `myst.yml`（包含 project 和 site 配置）
5. 询问是否立即启动开发服务器

生成的 `myst.yml` 如下：

```yaml
# See docs at: https://mystmd.org/guide/frontmatter
version: 1

project:
  id: <自动生成的UUID>
  # title:
  # description:
  # keywords: []
  # authors: []
  # To autogenerate a Table of Contents, run "myst init --write-toc"

site:
  template: book-theme
  # options:
  #   favicon: favicon.ico
  #   logo: site_logo.png
```

### 仅初始化项目配置

```bash
myst init --project
```

仅生成 `project:` 段，不含站点配置。适用于只需要构建 PDF/DOCX 导出而不需要网站的场景。

### 仅初始化站点配置

```bash
myst init --site
```

仅生成 `site:` 段。

## 步骤四：自动生成 TOC

```bash
myst init --write-toc
```

该命令会扫描目录中的 Markdown/Notebook 文件，自动生成目录结构并写入 myst.yml：

```yaml
project:
  id: <UUID>
  toc:
    - file: index.md
    - file: chapter1.md
```

## 步骤五：（可选）配置 GitHub Pages 部署

```bash
myst init --gh-pages
```

生成 GitHub Actions 工作流文件，自动部署到 GitHub Pages。

## 步骤六：验证项目

```bash
# 启动开发服务器预览
myst start

# 或构建所有导出
myst build --all
```

## 从 Jupyter Book 1.x 迁移

如果目录中存在 `_config.yml`（Jupyter Book 1.x 的配置文件），init 会检测到并提示升级：

```
📘 Found a legacy Jupyter Book. To proceed, myst needs to perform an upgrade which will:
‣ Upgrade any Sphinx-style glossaries to MyST-style glossaries
‣ Upgrade any case-insensitive admonition names to lowercase (Note → note)
‣ Migrate configuration from _config.yml and (if applicable) _toc.yml files
‣ Rename any modified or unneeded files so that they are hidden

Are you willing to proceed with the upgrade? (Y/n)
```

选择 "Y" 后，`upgradeJupyterBook()` 会自动完成迁移。

如果想继续使用 Jupyter Book 1.x，可以运行：
```bash
pip install "jupyter-book<2"
```

## 常见问题

### Q: init 后如何修改配置？

直接编辑 `myst.yml` 文件即可。常用配置项：

```yaml
project:
  title: 我的书籍
  description: 一本使用MyST编写的技术书籍
  authors:
    - name: 作者名
      github: username
  keywords: [myst, 技术写作]
  github: https://github.com/username/repo

site:
  template: book-theme  # 或 article-theme
  options:
    logo: logo.png
    favicon: favicon.ico
```

### Q: 如何手动编辑 TOC？

编辑 myst.yml 中的 `project.toc` 数组，支持嵌套结构：

```yaml
project:
  toc:
    - file: index.md
    - title: 第一部分
      children:
        - file: chapter1.md
        - file: chapter2.md
    - title: 第二部分
      children:
        - file: chapter3.md
    - url: https://example.com
      title: 外部参考
```

## 下一步

- [构建站点](02-build-site.md)
- [启动开发服务器](03-dev-server.md)
- [CLI 架构](../concepts/00-cli-architecture.md)
