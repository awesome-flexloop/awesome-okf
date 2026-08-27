---
type: concept
title: "安装与快速上手"
description: "安装 jupyterlab-latex 扩展、系统依赖配置、验证安装、首次编译预览 LaTeX 文档的完整流程"
tags: [install, setup, quickstart, pip, conda, requirements, verification]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/README.md"
    title: "README.md"
  - id: pyproject
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/pyproject.toml"
    title: "pyproject.toml"
  - id: install-json
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/install.json"
    title: "install.json"
---

# 安装与快速上手

## 前置条件

在安装 jupyterlab-latex 之前，确保系统已具备：

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| JupyterLab | ≥ 4.0 | 扩展运行的宿主环境 |
| Python | ≥ 3.8 | 服务端扩展运行环境 |
| LaTeX 发行版 | - | TeX Live（推荐）、MiKTeX（Windows）或 Tectonic |
| BibTeX 工具 | - | 处理参考文献（如 `bibtex`、`biber`） |

LaTeX 发行版必须安装在 Jupyter Server 运行的同一环境中，且 `xelatex`（默认引擎）或其他配置的引擎命令可在 PATH 中找到。

## 安装扩展

### pip 安装

```bash
pip install jupyterlab-latex
```

pip 包同时包含预构建的前端扩展（labextension）和服务端扩展，无需单独安装 npm 包。

### conda 安装

```bash
conda install conda-forge::jupyterlab-latex
```

## 验证安装

### 检查服务端扩展

```bash
jupyter server extension list
```

应看到类似输出：

```
jupyterlab_latex enabled
    - Validating jupyterlab_latex...
      jupyterlab_latex 4.x.x OK
```

### 检查 Lab 扩展

```bash
jupyter labextension list
```

应看到类似输出：

```
@jupyterlab/latex v4.x.x enabled OK (python, jupyterlab-latex)
```

两个扩展都显示 enabled OK 即为安装成功。

## 快速上手：第一个 LaTeX 文档

### 步骤 1：新建 .tex 文件

方式一：点击 Launcher 中的 "LaTeX File" 卡片（在 Other 分类下）。

方式二：通过菜单 File → New → LaTeX File。

方式三：右键文件浏览器 → New → 新建文件，手动命名为 `*.tex`。

### 步骤 2：编写 LaTeX 内容

使用项目自带的示例作为起点（sample.tex），或写入一个最小文档：

```latex
\documentclass{article}
\begin{document}
Hello, \LaTeX!
\end{document}
```

### 步骤 3：打开预览

有两种方式触发编译预览：

1. **右键菜单**：在编辑器中右键 → 选择 "Show LaTeX Preview"
2. **工具栏按钮**：点击编辑器工具栏上的 "Preview" 按钮

首次预览时，扩展会：
1. 向服务端发送 `/latex/build/{path}` 请求
2. 服务端调用 LaTeX 引擎编译 `.tex` 文件
3. 编译成功后，PDF 在右侧面板（split-right 模式）打开
4. 如果编译失败，底部面板（split-bottom）显示错误日志

### 步骤 4：实时更新

在编辑器中修改 `.tex` 文件并保存（Ctrl+S），扩展自动重新编译并更新 PDF 预览。编译成功后错误面板自动关闭。

### 步骤 5：使用编辑工具栏

当打开 `.tex` 文件时，编辑器工具栏自动显示 LaTeX 专用按钮：

| 按钮 | 功能 |
|------|------|
| **Preview** | 打开/刷新 PDF 预览 |
| **Xᵧ / Xⁿ** | 下标/上标（选中文字包裹或弹出输入框） |
| **X/Y** | 分数（弹出对话框输入分子分母） |
| **左/中/右对齐** | 对齐命令（\leftline, \centerline, \rightline） |
| **B / I / U** | 粗体/斜体/下划线（\textbf, \textit, \underline） |
| **列表图标** | 无序列表（itemize 环境） |
| **编号图标** | 有序列表（enumerate 环境） |
| **表格图标** | 表格创建对话框（输入行列数） |
| **图表图标** | 插入绘图（6种 pgfplots 类型） |

## 常见安装问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 点击 Preview 报 404 错误 | 服务端扩展未启用 | `jupyter server extension enable jupyterlab_latex` |
| 编译报错 "xelatex not found" | LaTeX 未安装或不在 PATH | 安装 TeX Live 或切换引擎 |
| SyncTeX 不工作 | 编译时未生成 .synctex.gz | 确保 synctex 设置为 true（默认） |
| Windows 下编译失败 | 使用 async subprocess | 已自动切换为同步模式（util.py 平台检测） |

## 开发模式安装

如需修改扩展源码，参考 README 开发安装 中的 Development install 章节：

```bash
git clone https://github.com/jupyterlab/jupyterlab-latex.git
cd jupyterlab-latex
pip install -e .
jupyter labextension develop . --overwrite
jupyter server extension enable jupyterlab_latex
jlpm run build
# 开发时自动重建
jlpm run watch
```

---

**下一步阅读：**
- [架构总览](02-architecture-overview.md) — 理解前后端如何协作完成编译预览
- [LaTeX 编译流程](03-latex-compilation.md) — 深入编译命令序列和引擎配置
