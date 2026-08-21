---
type: Reference
title: github-problem-matcher 源码信源登记
description: sphinx-doc/github-problem-matcher 源码路径、版本信息、核心文件清单与 Problem Matcher 机制说明
tags: [github-problem-matcher, source, reference, github-actions, sphinx]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T14:50:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: gpm-github
    resource: https://github.com/sphinx-doc/github-problem-matcher
    title: github-problem-matcher GitHub 仓库
    author: human:Ammar-Askar
  - id: gpm-docs
    resource: https://github.com/sphinx-doc/github-problem-matcher/blob/master/README.rst
    title: github-problem-matcher README
---

# github-problem-matcher 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | Sphinx Problem Matcher |
| 仓库 | sphinx-doc/github-problem-matcher |
| 描述 | Attaches a problem matcher that looks for errors during Sphinx builds |
| 作者 | Ammar Askar |
| 许可证 | BSD 2-Clause License |
| 版权 | Copyright (c) 2020 by the Sphinx team |
| Action 类型 | composite |
| 品牌图标 | book（黄色） |
| 官方仓库 | <https://github.com/sphinx-doc/github-problem-matcher> |

## 源码位置

github-problem-matcher 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/docs/github-problem-matcher/
```

该目录通过 git submodule 引入，本地不做修改。

## 核心文件清单

| 文件 | 行数 | 说明 |
|------|------|------|
| `action.yml` | 12 | GitHub Action 定义文件，声明 composite action，执行 `echo '::add-matcher::...'` 注册 matcher |
| `sphinx_matcher.json` | 39 | Problem Matcher JSON 配置，包含 3 个正则匹配模式（严格/宽松/兜底） |
| `test_matcher.js` | 88 | Node.js 测试脚本，使用内置 assert 模块验证 3 个 matcher 对模拟日志的匹配结果 |
| `README.rst` | 30 | 使用说明，展示如何在 GitHub Actions workflow 中引用该 Action |
| `LICENSE.rst` | 28 | BSD 2-Clause 许可证文本 |

## action.yml 结构

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

关键字段：
- `runs.using: composite`：声明为组合 Action（无 Docker/Node.js 运行时）
- `runs.steps[0].run`：通过 GitHub Actions workflow 命令 `::add-matcher::` 注册 matcher JSON 文件
- `${{ github.action_path }}`：GitHub Actions 内置变量，指向 Action 自身的目录路径

## sphinx_matcher.json 结构

JSON 顶层包含 `problemMatcher` 数组，数组内有 3 个 matcher 对象：

| Owner | 正则表达式 | 捕获组映射 | 匹配场景 |
|-------|-----------|-----------|---------|
| `sphinx-problem-matcher` | `^(.*):(\d+):\s+(\w*):\s+(.*)$` | file=1, line=2, severity=3, message=4 | 标准格式：`文件:行号: 级别: 消息` |
| `sphinx-problem-matcher-loose` | `(/.*\.rst):\s+(\w*):\s+(.*)$` | file=1, severity=2, message=3 | 宽松格式：`/路径.rst: 级别: 消息`（无行号） |
| `sphinx-problem-matcher-loose-no-severity` | `^(.*\.rst):(\d+):(.*)$` | file=1, line=2, message=3 | 兜底格式：`文件.rst:行号:消息`（无级别） |

每个 pattern 对象支持的字段：
- `regexp`：JavaScript 风格正则表达式字符串
- `file`：捕获组编号（1-based），映射为文件路径
- `line`：捕获组编号，映射为行号
- `severity`：捕获组编号，映射为严重级别（warning/error等）
- `message`：捕获组编号，映射为消息内容
- `_comment`：注释字段（以下划线开头，被 GitHub 忽略）
- `fromPath`/`toPath`/`code`/`column`：其他可选捕获组映射字段（本项目未使用）

## test_matcher.js 测试逻辑

1. 使用 `fs.readFileSync` 读取 `sphinx_matcher.json` 并 `JSON.parse`
2. 遍历 `matcher.problemMatcher`，提取每个 matcher 的第一个 pattern（本项目每个 matcher 只有一个 pattern）
3. 定义模拟 Sphinx 日志 `sphinx_log`（4 条警告样例，含多行消息）
4. 定义 `expected_matches` 数组（4 个期望匹配结果）
5. `perform_match()` 函数：用 `line.match(regexp)` 执行正则匹配，按捕获组编号映射返回结果对象
6. 逐行遍历日志，对每行尝试所有 pattern，收集匹配结果
7. `assert.deepEqual(expected_matches, matches)` 验证结果完全一致
