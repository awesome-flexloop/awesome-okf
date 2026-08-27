---
type: Concept
title: 项目目录结构解析
description: sphinx-demo 项目根目录结构、两个示例站点的内部结构、各目录和文件的职责说明
tags: [project-structure, directory, organization]
difficulty: beginner
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: structure
    resource: /references/conf-py-source.md
    title: sphinx-demo 目录结构
---

## 根目录结构

sphinx-demo 项目根目录采用"双示例+共享部署"的组织方式：

```
sphinx-demo/
├── .github/workflows/pages.yml    # CI/CD 工作流
├── pyodide-kernel-example/        # Pyodide 内核示例站点
├── xeus-kernel-example/           # Xeus 内核示例站点
├── index.html                     # 部署根页面（内核选择器）
├── switcher.json                  # 版本切换器配置
└── README.md                      # 项目说明
```

根目录不包含 Sphinx 构建配置——Sphinx 配置和源码分别在两个示例目录内部。

### 共享部署文件

根目录的 `index.html` 和 `switcher.json` 仅在部署阶段使用。构建时各示例独立生成 HTML，部署时 CI 将两个构建产物目录和根页面一起上传到 gh-pages。

## 示例站点内部结构

以 `pyodide-kernel-example/` 为例：

```
pyodide-kernel-example/
├── docs/
│   ├── Makefile                   # Sphinx 构建命令封装
│   └── source/
│       ├── _static/               # 静态资源（CSS/JS/图标）
│       │   ├── button_styling.css # TryExamples 按钮自定义样式
│       │   ├── icon.svg           # 站点 Logo
│       │   ├── jupyter.svg        # Jupyter 图标（自定义图标链接）
│       │   └── pypi.js            # PyPI 链接脚本
│       ├── conf.py                # Sphinx 核心配置文件
│       ├── custom_contents/       # JupyterLite 预装内容（Notebook/数据）
│       │   ├── arrays_in_numpy.ipynb
│       │   └── data/
│       ├── disabled_examples/     # TryExamples 禁用示例
│       │   ├── demo.md
│       │   └── disabled_example.py
│       ├── example.py             # NumPy 风格 docstring 示例模块
│       ├── index.md               # 文档首页
│       ├── jupyter-lite.json      # JupyterLite 运行时配置
│       ├── jupyter_lite_config.json  # JupyterLite 构建配置
│       ├── jupyterlite/           # JupyterLite 指令演示页
│       │   └── demo.md
│       ├── matplotlib_demo.md     # NotebookLite + Matplotlib 演示
│       ├── notebooks/             # 其他 Notebook
│       ├── notebooklite/          # NotebookLite 指令演示
│       │   └── demo.md
│       ├── overrides.json         # JupyterLab 插件覆盖配置
│       ├── replite/               # REPL 指令演示
│       │   └── demo.md
│       ├── try_examples.json      # TryExamples 运行时配置
│       ├── try_examples.md        # TryExamples 功能演示页
│       └── voici/                 # Voici 指令演示
│           └── demo.md
└── requirements.txt               # Python 依赖
```

## 文件职责速查表

| 文件/目录 | 职责 | 修改频率 |
|----------|------|---------|
| `conf.py` | Sphinx 核心配置——扩展列表、主题、JupyterLite 设置 | 低 |
| `jupyter-lite.json` | JupyterLite 运行时配置——appName、默认内核 | 低 |
| `jupyter_lite_config.json` | JupyterLite 构建配置——sourcemap、输出选项 | 极低 |
| `overrides.json` | JupyterLab 插件覆盖——工具栏按钮等 | 低 |
| `try_examples.json` | TryExamples 行为配置——高度、页面忽略规则 | 中（热更新，无需重建） |
| `example.py` | 文档示例代码——展示 NumPy docstring + TryExamples | 中 |
| `custom_contents/` | 预装到 JupyterLite 的 Notebook 和数据文件 | 中 |
| `_static/` | 自定义 CSS/JS/图标等静态资源 | 低 |
| `requirements.txt` | pip 依赖列表 | 低 |

## Xeus 示例的额外文件

Xeus 示例与 Pyodide 示例的目录结构几乎完全相同，额外包含：

| 文件 | 职责 |
|------|------|
| `docs/source/environment.yml` | 定义 WASM 环境中的预安装包（numpy, scipy, matplotlib 等） |

此外，`requirements.txt` 中使用 `jupyterlite-xeus` 替代 `jupyterlite-pyodide-kernel`。

## 构建输出目录

执行 `make html` 后，构建产物生成在 `docs/build/html/` 目录：

```
docs/build/html/
├── index.html              # Sphinx 文档首页
├── jupyterlite/demo.html   # 各指令演示页
├── lite/                   # JupyterLite 完整应用（被 _static/ 重定向替代）
├── _static/                # 重定向到 lite/ 目录
└── ...
```

JupyterLite 的实际构建产物在 `docs/build/html/lite/` 中，`_static/` 下的 JupyterLite 文件是指向 `lite/` 的重定向。

## 相关内容

- [03-sphinx-conf](03-sphinx-conf.md)：conf.py 配置详解
- [05-config-files](05-config-files.md)：四层 JSON 配置文件
- [09-ci-deployment](09-ci-deployment.md)：CI/CD 部署流程
