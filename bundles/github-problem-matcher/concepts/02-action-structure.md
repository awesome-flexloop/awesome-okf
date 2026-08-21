---
type: Concept
title: Action 结构解析
description: action.yml 逐行解析、composite action 机制、::add-matcher:: workflow 命令与 GitHub Actions 上下文变量
tags: [github-problem-matcher, action.yml, composite-action, workflow-command, github-actions]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T14:50:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: gpm-source
    resource: /references/github-problem-matcher-source.md
---

# Action 结构解析

## action.yml 全文件解析

`action.yml` 是 GitHub Action 的元数据文件，GitHub 通过它识别 Action 的名称、用途和执行方式。github-problem-matcher 的 `action.yml` 全文如下：

```yaml
name: Sphinx Problem Matcher
description: Attaches a problem matcher that looks for errors during Sphinx builds
author: Ammar Askar
branding:
  icon: book
  color: yellow
runs:
  using: composite
  steps:
  - name: Activate the problem matcher
    run: echo '::add-matcher::${{ github.action_path }}/sphinx_matcher.json'
    shell: sh
```

逐字段解析：

| 字段 | 值 | 说明 |
|------|-----|------|
| `name` | `Sphinx Problem Matcher` | Action 显示名称，出现在 GitHub Marketplace 和 workflow 运行日志中 |
| `description` | `Attaches a problem matcher that looks for errors during Sphinx builds` | Action 的简短描述 |
| `author` | `Ammar Askar` | 作者名称 |
| `branding.icon` | `book` | GitHub Marketplace 中的图标（可选值：book、bug、check、circle 等） |
| `branding.color` | `yellow` | 图标背景色（可选值：white、yellow、blue、green、orange、red、purple、gray-dark） |
| `runs.using` | `composite` | Action 运行类型 |
| `runs.steps` | （包含一个步骤） | 要执行的步骤列表 |

## composite action 机制

GitHub Actions 支持三种 Action 类型：

| 类型 | `using` 值 | 运行环境 | 适用场景 |
|------|-----------|---------|---------|
| JavaScript Action | `node20`（或其他 Node 版本） | Node.js 运行时 | 需要复杂逻辑、调用 API、处理文件的 Action |
| Docker Container Action | `docker` | Docker 容器 | 需要特定系统依赖、隔离环境的 Action |
| **Composite Action** | **`composite`** | **宿主 runner 直接执行** | **组合多个 workflow step、简单命令的 Action** |

github-problem-matcher 使用 composite 类型，原因在于：

1. **不需要运行时**：它只需要执行一行 shell 命令，不需要 Node.js 或 Docker
2. **轻量快速**：没有 Docker 拉取或 Node.js 启动开销
3. **跨平台**：`shell: sh` 在 Linux/macOS runner 上直接可用（Windows runner 也有 sh 兼容层）

composite action 的 `runs.steps` 支持：
- `run`：执行 shell 命令
- `uses`：调用其他 Action
- `with`：传递输入参数给被调用的 Action

## ::add-matcher:: workflow 命令

Action 的核心是这一行命令：

```sh
echo '::add-matcher::${{ github.action_path }}/sphinx_matcher.json'
```

这是 GitHub Actions 的 **workflow command**（工作流命令）语法。Workflow commands 是通过向 stdout 输出特定格式的字符串来与 GitHub Actions runner 通信的机制。

### 语法格式

```
::<命令名>::<参数>
```

或者带参数的形式：

```
::<命令名> <参数1>=<值1>,<参数2>=<值2>::<消息内容>
```

### Problem Matcher 相关命令

| 命令 | 作用 | 示例 |
|------|------|------|
| `::add-matcher::<path>` | 注册一个 problem matcher JSON 文件 | `echo '::add-matcher::$ matcher-path'` |
| `::remove-matcher owner=<owner>` | 移除指定 owner 的 problem matcher | `echo '::remove-matcher owner=sphinx-problem-matcher::'` |

### add-matcher 的行为

1. Runner 解析 `::add-matcher::` 后的文件路径
2. 读取该 JSON 文件
3. 将 JSON 中定义的所有 matcher 注册到当前运行上下文
4. 从这之后输出的所有日志都会被这些 matcher 扫描
5. 注册立即生效，不需要重启或额外配置

### remove-matcher 的使用场景

一个 job 中可能有多个构建步骤使用不同工具。如果你只想让 matcher 应用于特定步骤，可以在步骤结束后移除它：

```yaml
- name: Activate matcher
  run: echo '::add-matcher::${{ github.action_path }}/sphinx_matcher.json'
  shell: sh

- name: Build Sphinx docs
  run: make html

- name: Remove matcher
  run: echo '::remove-matcher owner=sphinx-problem-matcher::'
  shell: sh

- name: Build other stuff
  run: npm build  # 这些日志不会被 sphinx matcher 扫描
```

注意：`::remove-matcher::` 通过 `owner` 字段匹配，而 sphinx_matcher.json 注册了 3 个不同 owner 的 matcher，需要分别移除：

```sh
echo '::remove-matcher owner=sphinx-problem-matcher::'
echo '::remove-matcher owner=sphinx-problem-matcher-loose::'
echo '::remove-matcher owner=sphinx-problem-matcher-loose-no-severity::'
```

## ${{ github.action_path }} 上下文变量

`${{ github.action_path }}` 是 GitHub Actions 的内置上下文变量，指向当前正在执行的 Action 所在的目录路径。

在 github-problem-matcher 中：
- 当 workflow 执行 `uses: sphinx-doc/github-problem-matcher@master` 时
- GitHub runner 将该 Action 下载到本地缓存目录
- `${{ github.action_path }}` 就指向那个缓存目录
- 通过拼接 `/sphinx_matcher.json` 得到 matcher JSON 文件的绝对路径

为什么不用相对路径？因为 composite action 中 `run` 命令的工作目录是**项目代码目录**（`${{ github.workspace }}`），而不是 Action 自身的目录。如果直接写 `echo '::add-matcher::sphinx_matcher.json'`，runner 会在项目代码目录中查找这个文件，自然找不到。

### 常用 GitHub 上下文变量

| 变量 | 指向 |
|------|------|
| `${{ github.action_path }}` | 当前 Action 的目录 |
| `${{ github.workspace }}` | 项目代码检出目录 |
| `${{ github.repository }}` | 仓库名（`owner/repo` 格式） |
| `${{ github.sha }}` | 当前 commit SHA |
| `${{ github.ref }}` | 当前分支或 tag 的 ref |
| `${{ github.event_name }}` | 触发事件名（push/pull_request 等） |
| `${{ runner.os }}` | runner 操作系统（Linux/macOS/Windows） |

## shell: sh 的作用

```yaml
shell: sh
```

这一声明告诉 GitHub runner 使用 `sh` shell 来执行 `run` 命令。在 composite action 中，`shell` 字段是**必须的**（与直接在 workflow 中写 `run` 不同，workflow 步骤有默认 shell）。

可选的 shell 值：
- `sh`：POSIX shell（Linux/macOS 上通常是 bash 或 dash）
- `bash`：Bash shell
- `pwsh`：PowerShell Core（跨平台）
- `python`：Python 解释器
- `cmd`：Windows Command Prompt（仅 Windows）

选择 `sh` 是因为 `echo` 是 POSIX 标准命令，在所有 Linux/macOS runner 上可用，且命令足够简单不需要 bash 特有的语法。

## 为什么没有输入参数

注意 `action.yml` 中没有 `inputs` 字段。这意味着这个 Action 不接受任何配置参数——它总是注册同一个 `sphinx_matcher.json` 文件。如果需要自定义匹配行为，你需要创建自己的 Problem Matcher（参见 [自定义 Problem Matcher 示例](/examples/custom-matcher.md)）。

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [Problem Matcher JSON 格式](/concepts/03-matcher-json.md)
- [三种正则模式详解](/concepts/04-regex-patterns.md)
- [测试 Problem Matcher](/concepts/05-testing.md)
- [自定义 Problem Matcher 示例](/examples/custom-matcher.md)
- [源码信源登记](/references/github-problem-matcher-source.md)
