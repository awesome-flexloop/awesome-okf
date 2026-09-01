---
okf_version: "0.2"
type: "example"
title: "本地构建 conda-docs 文档"
sources:
  - README.md
  - Makefile
  - docs/source/conf.py
  - docs/source/requirements.txt
---

# 本地构建 conda-docs 文档

本示例展示如何在本地从零构建 conda-docs 的 Sphinx 文档站点，用于预览修改或离线阅读。

## 前置条件

- Python 3.9+（推荐 Python 3.10+）
- pip（最新版本）
- Make（Linux/macOS）或可用的 Sphinx 命令（Windows）
- Git

## 步骤 1：克隆仓库

```bash
git clone https://github.com/conda/conda-docs.git
cd conda-docs
```

## 步骤 2：安装文档依赖

```bash
pip install -r docs/source/requirements.txt
```

依赖包包含（见 requirements.txt）：
- `sphinx` — 文档构建引擎
- `conda-sphinx-theme` — Conda 官方 Sphinx 主题
- `sphinx-design` — UI 组件扩展（卡片、标签页、网格）
- `sphinx-reredirects` — 重定向支持
- `myst-parser`（如配置）— Markdown 支持
- `sphinx-copybutton` — 代码块复制按钮
- `sphinx-sitemap` — 站点地图生成

## 步骤 3：构建 HTML 文档

**Linux/macOS**：
```bash
cd docs
make html
```

**Windows（无 make）**：
```bash
cd docs
sphinx-build -b html source _build/html
```

## 步骤 4：预览文档

构建成功后，用浏览器打开：
```
docs/_build/html/index.html
```

或使用 Python 内置 HTTP 服务器：
```bash
cd docs/_build/html
python -m http.server 8000
# 访问 http://localhost:8000
```

## 常见构建问题

### 问题 1：`conda-sphinx-theme` 未找到

```bash
pip install git+https://github.com/conda/conda-sphinx-theme.git
```

### 问题 2：重定向警告（`sphinx-reredirects` 相关）

本地构建时，`reredirects` 配置指向外部 `https://docs.conda.io/...` URL。这些警告可忽略——重定向在 ReadTheDocs 生产环境生效。

### 问题 3：`sphinx-design` 组件渲染异常

确保 `sphinx-design` 版本与 Sphinx 版本兼容：
```bash
pip install --upgrade sphinx sphinx-design
```

## 启用自动重建（开发模式）

使用 `sphinx-autobuild` 在文件修改时自动重建并刷新浏览器：

```bash
pip install sphinx-autobuild
sphinx-autobuild docs/source docs/_build/html --open-browser
```

## 构建清理

清理构建产物：
```bash
cd docs
make clean
# 或手动删除
rm -rf docs/_build
```

## ReadTheDocs 等价配置

`.readthedocs.yml` 定义了 CI 构建流程，本地构建与 RTD 构建的对应关系：

| RTD 配置项 | 本地等价操作 |
|---|---|
| `python.install.requirements: docs/source/requirements.txt` | `pip install -r docs/source/requirements.txt` |
| `sphinx.configuration: docs/source/conf.py` | `sphinx-build -c docs/source ...` |
| `sphinx.builder: dirhtml`（如配置） | `make dirhtml` 或 `-b dirhtml` |
| `build.commands`（如有） | 执行对应 shell 命令 |

> 📌 **提示**：本地构建用于预览，正式发布到 ReadTheDocs 只需推送代码到 GitHub，RTD 自动触发构建。
