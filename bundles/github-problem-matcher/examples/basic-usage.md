---
type: Example
title: 基础使用示例
description: 在 Sphinx 文档 CI 中集成 github-problem-matcher 的完整 workflow 配置、多场景配置与常见问题排查
tags: [github-problem-matcher, example, workflow, ci, sphinx-docs]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T14:50:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: gpm-source
    resource: /references/github-problem-matcher-source.md
---

# 基础使用示例

## 最简 Workflow 配置

以下是一个最小可用的 Sphinx 文档 CI workflow，保存为 `.github/workflows/docs.yml`：

```yaml
name: Documentation
on: [push, pull_request]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install sphinx
          pip install -r docs/requirements.txt

      # 关键步骤：在构建之前注册 Problem Matcher
      - uses: sphinx-doc/github-problem-matcher@master

      - name: Build docs
        run: |
          cd docs
          make html
```

添加后，所有 Sphinx 警告（格式错误、断链、未知指令、文档不在 toctree 中等）都会在 PR 的 Files changed 页面中显示为内联注解。

## 生产级配置

包含缓存、质量门禁、多格式构建的完整配置：

```yaml
name: Documentation
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Install dependencies
        run: |
          pip install sphinx sphinx-rtd-theme myst-parser sphinx-autobuild
          if [ -f docs/requirements.txt ]; then pip install -r docs/requirements.txt; fi
          pip install -e .  # 如果需要 autodoc 导入项目代码

      - name: Activate Sphinx Problem Matcher
        uses: sphinx-doc/github-problem-matcher@master

      - name: Check for broken links
        run: |
          cd docs
          sphinx-build -b linkcheck . _build/linkcheck

      - name: Build HTML (warnings as errors)
        run: |
          cd docs
          sphinx-build -W -b html . _build/html

      - name: Build PDF (LaTeX)
        run: |
          cd docs
          sphinx-build -b latex . _build/latex
          # 需要安装 LaTeX 环境：sudo apt-get install texlive-latex-recommended texlive-fonts-recommended texlive-latex-extra

      - name: Upload documentation artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: documentation-html
          path: docs/_build/html/

      - name: Deploy to GitHub Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/_build/html
```

## 多 Python 版本矩阵测试

如果你的项目支持多个 Python 版本，可以测试文档在所有版本下的构建：

```yaml
jobs:
  build-docs:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install sphinx && pip install -r docs/requirements.txt

      - uses: sphinx-doc/github-problem-matcher@master

      - name: Build docs with Python ${{ matrix.python-version }}
        run: |
          cd docs
          sphinx-build -W -b html . _build/html
```

注意：每个 matrix job 独立运行，matcher 注册在每个 job 内部生效。

## 配合 MyST-Parser 使用

如果你的 Sphinx 项目使用 MyST-Parser 编写 Markdown 格式的文档：

```yaml
- name: Install dependencies
  run: |
    pip install sphinx myst-parser sphinx-rtd-theme
```

github-problem-matcher 的正则模式匹配 `.rst` 文件路径（`\\.rst`），但 MyST 文档使用 `.md` 扩展名。此时只有严格模式（`^(.*):(\\d+):\\s+(\\w*):\\s+(.*)$`）和宽松无级别模式（`^(.*\\.rst):(\\d+):(.*)$`）会匹配 `.md` 文件吗？

实际上：
- 严格模式的文件捕获组是 `(.*)`（任意字符），**可以匹配 `.md` 文件**
- 宽松模式要求 `(/.*\\.rst)`，**只匹配 `.rst` 文件**
- 兜底模式要求 `(.*\\.rst)`，**只匹配 `.rst` 文件**

对于 MyST 项目，Sphinx 的警告格式仍然是 `file.md:line: SEVERITY: message`，严格模式可以正常捕获。如果需要更好的 `.md` 支持，建议创建自定义 matcher（参见 [自定义 Problem Matcher 示例](/examples/custom-matcher.md)）。

## 条件性启用 Matcher

如果只想在特定条件下启用 matcher（如只在 PR 中启用），可以使用条件：

```yaml
- name: Activate Sphinx Problem Matcher
  uses: sphinx-doc/github-problem-matcher@master
  if: github.event_name == 'pull_request'
```

## 移除 Matcher

如果同一个 job 中有多个构建步骤，不希望 matcher 应用于后续步骤，可以手动移除：

```yaml
- uses: sphinx-doc/github-problem-matcher@master

- name: Build Sphinx docs
  run: cd docs && make html

- name: Remove Sphinx matcher
  run: |
    echo '::remove-matcher owner=sphinx-problem-matcher::'
    echo '::remove-matcher owner=sphinx-problem-matcher-loose::'
    echo '::remove-matcher owner=sphinx-problem-matcher-loose-no-severity::'
  shell: bash

- name: Build other things
  run: npm run build  # 此步骤的日志不会被 sphinx matcher 扫描
```

## 常见问题排查

### 警告没有显示为注解

可能的原因：

1. **Matcher 注册在构建之后**：确保 `uses: sphinx-doc/github-problem-matcher@master` 步骤在 `sphinx-build` 步骤之前
2. **警告格式不匹配**：检查 Sphinx 输出格式是否与三种正则模式匹配。Sphinx 的警告格式可能因版本或配置不同而变化
3. **日志被折叠**：在 Actions 日志页面展开相关步骤的日志，查看是否有匹配
4. **使用了 `-Q`（安静模式）**：`sphinx-build -Q` 会抑制警告输出，导致 matcher 无法匹配

### 注解没有关联到正确的行号

可能的原因：

1. **文件路径是绝对路径**：Sphinx 输出绝对路径时，GitHub 可能无法将其与 PR 中的文件关联。在 `sphinx-build` 命令中使用相对路径或配置 `source` 目录为相对路径
2. **行号指向了错误的位置**：Sphinx 报告的行号可能因为指令包含多行内容而指向指令起始行而非实际错误行——这是 Sphinx 的行为，不是 matcher 的问题

### 误报（非警告行被匹配）

如果非警告行被错误匹配：
1. 检查该行的格式是否恰好匹配某条正则（如代码示例中出现 `file.rst:42: text` 格式）
2. 考虑创建自定义 matcher，使用更严格的正则（参考 [自定义 Problem Matcher 示例](/examples/custom-matcher.md)）

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [Action 结构解析](/concepts/02-action-structure.md)
- [三种正则模式详解](/concepts/04-regex-patterns.md)
- [自定义 Problem Matcher 示例](/examples/custom-matcher.md)
