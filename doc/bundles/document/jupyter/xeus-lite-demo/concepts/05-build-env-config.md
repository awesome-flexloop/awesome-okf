---
type: Concept
title: 构建环境配置
description: .github/build-environment.yml 的结构、核心依赖、插件安装方法和版本约束
tags: [build-environment.yml, jupyterlite-core, jupyterlite-xeus, build-tools, configuration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: build-env
    resource: /references/build-env-source.md
    title: 构建环境配置信源
  - id: deploy-wf
    resource: /references/deploy-workflow-source.md
    title: CI/CD 流水线信源
---

## build-environment.yml 结构

`.github/build-environment.yml` 定义 GitHub Actions 中执行 `jupyter lite build` 命令所需的 conda 环境。与运行时环境不同，这里安装的是 x86_64 Linux 架构的工具包。

```yaml
name: build-env
channels:
  - conda-forge
dependencies:
  - python
  - pip
  - jupyter_server
  - jupyterlite-core >=0.7
  - jupyterlite-xeus >=4.3
  - notebook >=7.5
```

## 核心依赖解析

| 依赖 | 版本约束 | 作用 |
|------|---------|------|
| `python` | latest | 运行 jupyterlite CLI 的 Python 解释器 |
| `pip` | latest | Python 包管理器，某些插件可能通过 pip 安装 |
| `jupyter_server` | latest | Jupyter 服务器组件，jupyterlite 构建时的依赖 |
| `jupyterlite-core` | >=0.7 | JupyterLite 核心 CLI，提供 `jupyter lite build` 命令 |
| `jupyterlite-xeus` | >=4.3 | xeus 内核集成插件，使 jupyterlite 能处理 WASM conda 包 |
| `notebook` | >=7.5 | Jupyter Notebook 7+ 前端界面 |

### jupyterlite-core

`jupyterlite-core` 是 JupyterLite 的核心包，提供命令行接口：

- `jupyter lite build` — 构建静态站点
- `jupyter lite serve` — 本地预览服务器
- `jupyter lite init` — 初始化新项目

版本约束 `>=0.7` 确保使用支持 xeus 集成的较新版本。

### jupyterlite-xeus

`jupyterlite-xeus` 是连接 jupyterlite 和 xeus 内核的关键插件：

- 在构建时解析 `environment.yml`
- 从 emscripten-forge 和 conda-forge 通道下载 WASM 包
- 将内核和用户包打包到静态站点中
- 处理内核启动配置

版本约束 `>=4.3` 确保与当前 jupyterlite-core API 兼容。

## 安装 JupyterLite 插件

JupyterLite 插件扩展了 JupyterLite 的界面或功能。插件是在**构建时**安装的，因此它们添加到 `.github/build-environment.yml` 而非 `environment.yml`。

### 插件类型

| 类型 | 示例 | 说明 |
|------|------|------|
| 前端扩展 | jupyterlite-terminal | 添加终端功能 |
| 内核扩展 | jupyterlite-p5-kernel | 添加新的语言内核 |
| 内容提供 | jupyterlite-github | 从 GitHub 加载内容 |
| 主题扩展 | jupyterlab-theme-* | 自定义界面主题 |

### 添加插件示例

以安装 `jupyterlite-terminal`（终端插件）为例：

```yaml
name: build-env
channels:
  - conda-forge
dependencies:
  - python
  - pip
  - jupyter_server
  - jupyterlite-core >=0.7
  - jupyterlite-xeus >=4.3
  - notebook >=7.5
  - jupyterlite-terminal   # ← 添加这一行
```

> ⚠️ 注意：不是所有 JupyterLab 扩展都能在 JupyterLite 中工作。扩展必须兼容 JupyterLite 的浏览器环境（不依赖 Node.js 或服务器端 API）。请查阅 [JupyterLite 文档](https://jupyterlite.readthedocs.io/en/latest/howto/index.html) 确认插件兼容性。

### 通过 pip 安装插件

某些插件可能在 conda-forge 上不可用，需要通过 pip 安装。在 build-environment.yml 中可以使用 pip 嵌套：

```yaml
name: build-env
channels:
  - conda-forge
dependencies:
  - python
  - pip
  - jupyter_server
  - jupyterlite-core >=0.7
  - jupyterlite-xeus >=4.3
  - notebook >=7.5
  - pip:
    - some-pip-only-plugin
```

## 版本升级策略

### 安全升级

以下升级通常是安全的（小幅版本更新）：
- `jupyterlite-core >=0.7` → 可以尝试 `>=0.8`（检查 changelog）
- `notebook >=7.5` → 可以尝试更高版本
- `python` → 通常跟随 Actions setup-python 的版本

### 需要谨慎升级

- `jupyterlite-xeus` 大版本升级可能改变 environment.yml 的解析方式
- 升级后应检查 PR 构建是否成功
- 建议在 PR 中测试而非直接 push 到 main

## 构建环境的工作流程

在 GitHub Actions 中，构建环境的使用流程如下：

1. micromamba 根据 `.github/build-environment.yml` 创建 conda 环境
2. 环境被缓存（`cache-environment: true`），加速后续构建
3. 在 login shell 中激活环境
4. 执行 `jupyter lite build --contents content --output-dir dist`
5. jupyterlite-xeus 插件读取根目录的 `environment.yml`，下载 WASM 包
6. 构建完成，输出到 dist/ 目录

## 常见问题

**Q: 为什么 jupyter 相关包不放在 environment.yml 中？**
A: 因为 jupyterlite-core、notebook 等是构建工具和前端界面，它们运行在浏览器中（以 JavaScript 形式被打包），不是作为 WASM conda 包运行的。

**Q: 我可以降级 jupyterlite-core 版本吗？**
A: 可以，但 jupyterlite-xeus 4.3+ 要求 jupyterlite-core >=0.7。如果降级 jupyterlite-core，也需要对应降级 jupyterlite-xeus。

**Q: 添加插件后站点变大怎么办？**
A: 每个插件都会增加静态文件大小。建议只安装必要的插件。构建日志会显示最终产物大小。

## 相关概念

- [双环境模型](02-dual-environment.md) — 理解构建环境与运行时环境的区别
- [运行时环境配置](04-runtime-env-config.md) — 用户包环境配置
- [CI/CD 流水线](06-cicd-pipeline.md) — GitHub Actions 工作原理
- [添加 JupyterLite 插件](../examples/05-add-jupyterlite-plugins.md) — 插件安装实操
