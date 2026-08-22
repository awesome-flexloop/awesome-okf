---
type: Example
title: "本地构建与预览站点"
description: "从零开始在本地构建Try Jupyter站点并预览，包含pixi环境安装、构建、后处理、启动预览服务器的完整可执行步骤。"
tags: [example, local-build, preview, pixi, getting-started]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: getting-started
    resource: "/concepts/01-getting-started.md"
    title: "快速开始"
  - id: build-pipeline
    resource: "/concepts/05-build-pipeline.md"
    title: "构建管线"
---

# 示例：本地构建与预览站点

本示例演示如何从零开始在本地构建Try Jupyter站点并通过浏览器预览。

## 前置条件

- 已安装 [Pixi](https://pixi.sh)（跨平台包管理器）
- 约3GB可用磁盘空间（依赖+构建产物）
- 现代浏览器（Chrome/Firefox/Edge）

## 步骤1：获取代码

```bash
git clone https://github.com/jupyter/try-jupyter.git
cd try-jupyter
```

## 步骤2：安装依赖

```bash
pixi install
```

此命令会自动：
1. 创建 `.pixi/` 隔离环境
2. 下载并安装Python 3.12+、Node.js 22+
3. 安装JupyterLite、JupyterLab、所有扩展和依赖
4. 安装Playwright测试框架

首次运行可能需要5-15分钟（取决于网络速度），完成后会生成 `pixi.lock` 锁定文件。

## 步骤3：构建站点

```bash
# 准备README（CI中执行的步骤，本地也推荐执行）
cp README.md content

# 执行JupyterLite构建
pixi run build
```

构建过程包括：
- JupyterLab前端编译
- Pyodide内核打包
- Xeus内核环境下载和打包（4个语言内核）
- 所有扩展安装
- 内容文件（notebooks + data）打包

构建完成后，`dist/` 目录包含完整静态站点。首次构建约3-10分钟。

## 步骤4：过滤内核（推荐）

```bash
pixi run filter-kernels
```

此脚本将 `dist/xeus/kernels.json` 从完整内核列表精简为5个精选内核：
- xpython（Python）
- xcpp23/xc23（C++23）
- xr（R）
- xsqlite（SQLite）

输出示例：
```
Found 8 kernels: ['xpython', 'xcpp17', 'xcpp23', 'xc23', 'xr', 'xsqlite', 'xlua', 'xrust']
Keeping 5 kernels: ['xpython', 'xcpp23', 'xc23', 'xr', 'xsqlite']
Updated dist/xeus/kernels.json
Done!
```

## 步骤5：启动预览服务器

```bash
pixi run python -m http.server 8000 --directory dist
```

## 步骤6：访问站点

在浏览器中打开：http://localhost:8000/lab/index.html

你应该看到：
- JupyterLab界面加载完成
- 左侧文件浏览器显示 `notebooks/` 和 `data/` 目录
- 右上角可切换内核（Python/C++/R/SQLite）
- 终端可用（File → New → Terminal）

## 步骤7：验证Notebook

1. 双击打开 `notebooks/Intro.ipynb`
2. 点击 Run → Run All Cells
3. 等待所有cell执行完成
4. 确认没有红色错误输出

## 常用命令

```bash
# 清理并重新构建
pixi run clean && pixi run build && pixi run filter-kernels

# 启动预览（端口8000）
pixi run python -m http.server 8000 --directory dist

# 运行UI测试（需要先构建）
pixi run playwright install --with-deps chromium  # 首次
pixi run test
```

## 常见问题

**Q: 构建时网络错误/超时？**
A: Pixi使用conda-forge，国内网络可能需要配置镜像。设置环境变量 `CONDA_CHANNEL_ALIASES` 或使用 `RATTLER_CONDA_CHANNEL_ALIASES` 指向镜像源。

**Q: 浏览器中内核启动失败？**
A: 检查浏览器控制台是否有WASM加载错误。某些浏览器隐私模式可能限制WASM。

**Q: dist/目录为空？**
A: 确认 `pixi run build` 执行成功且没有报错。检查 `.jupyterlite.doit.db` 是否存在（doit构建数据库）。

## 相关示例

- [自定义内核环境](02-custom-kernel.md)
- [添加新Notebook](03-add-notebook.md)
