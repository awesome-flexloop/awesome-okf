---
type: Concept
title: 快速开始
description: 从零开始安装 Copier、生成第一个 JupyterLab 扩展项目、安装开发环境并运行的完整步骤。
tags: [getting-started, installation, quickstart, setup, development]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/copier-config.md
    title: Copier 配置参数全参考
  - id: contributing
    resource: /references/package-json-source.md
    title: package.json 模板字段解析
---

## 快速开始

本指南将带你从零开始，使用 extension-template 生成一个 JupyterLab 扩展项目并在开发模式下运行。

## 步骤 1：安装 Copier

首先安装 Copier 和 jinja2-time 插件。推荐使用 pip 安装：

```bash
pip install "copier~=9.2" jinja2-time
```

或者使用 conda/mamba：

```bash
conda install -c conda-forge "copier>=9.2,<10" jinja2-time
```

确保你也已安装 JupyterLab >= 4.0.0 和 Node.js（LTS 版本）：

```bash
pip install "jupyterlab>=4.0.0"
# Node.js 可从 https://nodejs.org 安装，或通过 conda:
# conda install -c conda-forge nodejs
```

## 步骤 2：生成扩展项目

创建项目目录并运行 copier copy：

```bash
mkdir myextension
cd myextension
copier copy --trust https://github.com/jupyterlab/extension-template .
```

Copier 会提示你回答一系列问题来配置你的扩展。以下是关键问题的说明：

| 问题 | 默认值 | 说明 |
|------|--------|------|
| What is your extension kind? | frontend | 选择扩展类型：frontend/mimerenderer/frontend-and-server/theme |
| Extension author name | My Name | 你的名字 |
| Extension author email | (空) | 你的邮箱 |
| JavaScript package name | myextension | NPM 包名 |
| Python package name | myextension | Python 包名（自动从 JS 名转换） |
| Extension short description | A JupyterLab extension. | 简短描述 |
| Does the extension have user settings? | No | 是否包含用户设置界面 |
| Do you want to set up Binder example? | No | 是否生成 Binder 配置 |
| Do you want to set up tests? | Yes | 是否生成测试配置 |
| Include AI assistant rules (AGENTS.md)? | No | 是否生成 AI 编码规范 |
| Git remote repository URL | (空) | GitHub 仓库地址 |

回答完所有问题后，Copier 会在当前目录生成完整的项目结构。

## 步骤 3：安装开发环境

生成项目后，需要安装依赖并以开发模式安装扩展：

```bash
# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装 Python 包（开发模式）
pip install -e ".[dev]"

# 链接前端扩展到 JupyterLab
jupyter-builder develop . --overwrite
```

如果选择了 frontend-and-server 类型，还需要启用服务端扩展：

```bash
jupyter server extension enable myextension
```

安装 NPM 依赖：

```bash
# jlpm 是 JupyterLab 内置的 yarn，随 JupyterLab 一起安装
jlpm install
```

## 步骤 4：构建并运行

首次构建前端代码：

```bash
jlpm build
```

启动 JupyterLab：

```bash
jupyter lab
```

在浏览器中打开 JupyterLab 后，打开浏览器开发者工具（F12）的 Console 面板，你应该能看到类似这样的日志：

```
JupyterLab extension myextension is activated!
```

恭喜！你的第一个 JupyterLab 扩展已经运行起来了。

## 步骤 5：开发模式（自动重载）

开发时推荐使用 watch 模式，修改 TypeScript 代码后自动重新构建：

```bash
# 终端 1：启动监听模式（自动重新构建前端）
jlpm run watch

# 终端 2：启动 JupyterLab
jupyter lab
```

保存对 `src/index.ts` 的修改后，等待几秒让构建完成，然后在浏览器中刷新页面即可看到变化。

**记忆口诀**："改了什么，重启什么"
- 改了 TypeScript/JavaScript → 等待自动构建 → 刷新浏览器
- 改了 Python 代码（frontend-and-server 类型）→ 重启 `jupyter lab` 服务

## 验证安装

可以通过以下命令检查扩展是否正确安装：

```bash
# 检查前端扩展
jupyter labextension list
# 应显示：myextension v0.1.0 enabled OK

# 检查后端扩展（frontend-and-server 类型）
jupyter server extension list
# 应显示：myextension enabled OK
```

## 生成旧版本扩展

如果你需要为旧版 JupyterLab 生成扩展，可以指定模板版本：

```bash
copier copy --vcs-ref v4.0.0 --trust https://github.com/jupyterlab/extension-template .
```

## 更新已有项目

当模板发布新版本后，可以在项目目录中运行更新命令，将最新的模板改进合并进来：

```bash
copier update --trust
```

Copier 会交互式地让你审核每个变更，避免覆盖你的自定义代码。

## 常见问题排查

### `jlpm: command not found`

你没有激活正确的虚拟环境，或 JupyterLab 未安装。确保 `pip install jupyterlab` 在当前环境中执行。

### 扩展不显示在 JupyterLab 中

1. 运行 `jupyter labextension list` 确认扩展在列表中且显示 OK
2. 确保已执行 `jupyter-builder develop . --overwrite`
3. 尝试重启 JupyterLab（不是只刷新浏览器）
4. 执行 `jlpm build` 确保前端代码已编译
5. 检查浏览器控制台是否有 JavaScript 错误

### `pip install -e .` 报错

确保在项目根目录（包含 pyproject.toml 的目录）执行命令，且 Python 版本 >= 3.10。

## 相关概念

- [项目结构详解](/concepts/04-project-structure.md)
- [双包构建系统](/concepts/05-build-system.md)
- [前端扩展开发](/concepts/06-frontend-extension.md)
- [Copier 模板引擎基础](/concepts/02-copier-basics.md)
