---
type: Example
title: 添加 JupyterLite 插件
description: 通过 build-environment.yml 添加 jupyterlite-terminal 等 JupyterLite 插件，扩展站点功能
tags: [plugins, jupyterlite-terminal, build-environment, extensions]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
  - id: build-env
    resource: /references/build-env-source.md
    title: 构建环境配置信源
---

## 目标

为 JupyterLite 站点添加功能插件，以终端插件（jupyterlite-terminal）为例演示插件安装流程。

## 重要提醒

JupyterLite 插件是**构建时依赖**，必须添加到 `.github/build-environment.yml`，**不要**添加到根目录的 `environment.yml`。

> 如果还不理解两个 environment 文件的区别，请先阅读[双环境模型](../concepts/02-dual-environment.md)。

## 步骤1：编辑 .github/build-environment.yml

1. 在 GitHub 仓库中，进入 `.github/` 目录
2. 点击 `build-environment.yml` 文件
3. 点击编辑图标（铅笔 ✏️）
4. 在 `dependencies` 列表中添加插件包名

### 示例：添加终端插件

将文件内容修改为：

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
  - jupyterlite-terminal
```

5. Commit changes 到 main 分支

## 步骤2：等待构建

1. 进入 Actions 标签页
2. 等待构建完成（添加新插件可能需要 3-5 分钟）
3. 刷新 JupyterLite 站点

## 步骤3：使用终端

构建完成后，刷新站点，你应该能在 JupyterLab 界面中看到终端功能：

- **方法1**：点击 **File** → **New** → **Terminal**
- **方法2**：在 Launcher 页面中找到 Terminal 图标

终端在浏览器中运行，可以执行基本的 shell 命令。

## 其他可用插件

| 插件名 | 功能 | conda 安装 | pip 安装 |
|--------|------|-----------|---------|
| jupyterlite-terminal | 终端 | ✅ conda-forge | ✅ PyPI |
| jupyterlite-p5-kernel | p5.js 内核 | ✅ conda-forge | ✅ PyPI |
| jupyterlite-xeus | xeus 内核（已预装） | ✅ conda-forge | ✅ PyPI |

### 通过 pip 安装插件

某些插件可能不在 conda-forge 上，需要通过 pip 安装。使用 pip 嵌套语法：

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
  - jupyterlite-terminal
  - pip:
    - some-pip-only-plugin
```

## 插件安装决策树

```
我要安装一个插件/扩展：
├─ 这个插件是在 Notebook 中 import 的 Python/R 包？
│  └─ ✅ 添加到根目录 environment.yml
│     例：numpy, pandas, matplotlib, r-tidyverse
│
├─ 这个插件扩展了 JupyterLab 界面功能？
│  └─ ✅ 添加到 .github/build-environment.yml
│     例：jupyterlite-terminal, jupyterlite-p5-kernel
│
└─ 不确定？
   └─ 看插件文档：如果安装说明说 "pip install jupyterlite-xxx" 且
      它是 UI 功能扩展 → build-environment.yml
```

## 常见问题

**Q: 添加插件后构建失败？**
A: 检查插件名拼写是否正确，确认插件在 conda-forge 上存在。如果 conda 上找不到，尝试 pip 安装方式。

**Q: 插件安装了但界面看不到？**
A: 某些插件可能需要额外配置，或与当前 jupyterlite-core 版本不兼容。尝试升级 jupyterlite-core 和 jupyterlite-xeus 版本。

**Q: 安装多个插件后站点变慢？**
A: 每个插件都会增加静态文件体积。建议只安装真正需要的插件。

**Q: 可以安装 JupyterLab 扩展吗？**
A: 部分 JupyterLab 扩展可以在 JupyterLite 中工作，但不是全部。扩展必须兼容 JupyterLite 的浏览器环境（不能依赖 Node.js 原生 API 或服务器端功能）。建议查看插件文档是否标注 JupyterLite 兼容。

**Q: 如何卸载插件？**
A: 从 build-environment.yml 中删除对应行，commit 并等待重新部署即可。

## 插件开发提示

如果你想开发自己的 JupyterLite 插件：

1. JupyterLite 插件基于 JupyterLab 扩展系统
2. 使用 TypeScript 开发，遵循 JupyterLab 扩展 API
3. 插件需要被打包为可在浏览器中运行的格式
4. 参考 [JupyterLite 官方文档](https://jupyterlite.readthedocs.io/en/latest/extensionpoints.html) 的扩展点说明

## 相关概念

- [构建环境配置](../concepts/05-build-env-config.md) — build-environment.yml 详解
- [双环境模型](../concepts/02-dual-environment.md) — 理解两个配置文件的区别
- [CI/CD 流水线](../concepts/06-cicd-pipeline.md) — 构建流程如何使用 build-environment.yml
