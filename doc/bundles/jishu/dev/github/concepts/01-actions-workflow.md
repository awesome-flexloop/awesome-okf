---
type: Concept
title: GitHub Actions 工作流
description: 基于 2020 年前后《开源的世界》GitHub Actions 手册——核心概念、.github/workflows 目录约定、触发事件 on、runs-on、构建矩阵、checkout 引用语法、jobs/needs 依赖与状态徽章
tags: [github, github-actions, CI, CD, 工作流]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-161b4241bc09
    resource: /references/source-2.md
    title: 《5 GitHub Actions 手册》
---
# GitHub Actions 工作流

> **时点说明**：本文基于 2020 年前后教程（简书连载《开源的世界》第 5 篇《5 GitHub Actions 手册》）整理。文中示例使用 2020 年时点的 Actions 语法与运行器版本（如 `ubuntu-18.04`、`actions/checkout@v1`），已过时部分在「现状」小节说明，实操时以官方文档为准。

## 核心概念（F-203）

GitHub Actions（GitHub 操作）可让您直接在 GitHub 仓库中创建自定义的软件开发生命周期工作流程。核心概念：

- **Workflow（工作流程）**：可在仓库中创建的自定义自动化流程，用于构建、测试、封装、发行或部署代码项目，由一个或多个 jobs 组成，可借由 event 部署和激活
- **Workflow run**：workflow 在预先配置的事件发生时运行的实例
- **Workflow file**：使用至少一个作业定义工作流配置的 YAML 文件，位于仓库根目录 `.github/workflows` 位置
- **Job（作业）**：由 step 组成的任务定义，每个作业在虚拟环境的新实例中运行
- **Step（步骤）**：作业执行的一组任务，可通过 `commands` 或 `actions` 运行
- **Action（操作）**：作为步骤合并的独立任务，是工作流中最小的可移植构建基块
- **CI / CD**：持续集成（Continuous integration）通过即时反馈更快检测和解决 Bug；持续部署（Continuous deployment）基于 CI，新代码通过测试后自动部署到生产
- **Virtual environment（虚拟环境）**：GitHub 托管 Linux、macOS 和 Windows 虚拟环境以运行工作流
- **Runner**：在每个虚拟环境中等待可用作业的 GitHub 服务，一次运行一个作业
- **Event（事件）**：触发工作流运行的特定活动
- **Artifact（工件）**：构建和测试代码时创建的文件，如二进制文件、包文件、测试结果、日志等

## 配置工作流（F-204）

工作流程必须存储在仓库根目录的 `.github/workflows` 目录中，至少包含一项作业，作业包含一组用于执行个别任务的步骤。可以使用 YAML 语法配置工作流并将其作为工作流文件存储。

创建 workflow 文件的步骤：

1. 在仓库根目录创建 `.github/workflows` 目录，并在此目录下新建 `.yml` 文件（如 `continuous-integration-workflow.yml`）
2. 参考工作流语法文档选择可触发操作的事件、添加操作以及自定义工作流
3. 将工作流文件的更改提交到希望运行工作流的分支

## 通过事件触发工作流（F-205、F-206、F-207）

在工作流程名称后面添加 `on:` 指定触发条件（通常是某些事件）和事件值，例如推送时触发：

```yaml
name: descriptive-workflow-name
on: push
```

`on` 字段也可以是事件的数组：

```yaml
on: [push, pull_request]
```

使用 POSIX cron 语法计划工作流运行，例如每小时触发一次：

```yaml
on:
  schedule:
    # * is a special character in YAML so you have to quote this string
  - cron: '0 * * * *'
```

周一至周五的 2:00 UTC 时间运行：

```yaml
on:
  schedule:
  - cron: "0 2 * * 1-5"
```

限定在特定分支运行，并使用可选的 `paths` 字段限定事件考虑的文件路径：

```yaml
on:
  push:
    branches:
    - master
    # file paths to consider in the event. Optional; defaults to all.
    paths:
      - test/*
```

## 选择虚拟环境（F-208）

可以为工作流中的每项作业指定虚拟环境。可以选择不同类型和版本的虚拟主机，包括 Ubuntu、Linux 和 macOS。例如：

```yaml
runs-on: ubuntu-18.04
```

## 配置构建矩阵（F-209）

要同时在多个操作系统、平台和语言版本上测试，可以配置构建矩阵。使用矩阵在 `strategy:` 下列出配置选项。例如，通过不同版本的 Node.js 和 Ubuntu/Linux 操作系统运行作业：

```yaml
strategy:
  matrix:
    node: [6, 8, 10]
    os: [ubuntu-14.04, ubuntu-18.04]
```

## 使用检出操作（F-210）

检出（checkout）操作是标准操作，在工作流需要仓库代码副本时，必须位于其他操作前面。使用标准检出操作：

```yaml
- uses: actions/checkout@v1
```

浅层克隆（只复制仓库最新版本），使用 `with` 语法设置 `fetch-depth`：

```yaml
- uses: actions/checkout@v1
  with:
    fetch-depth: 1
```

引用操作的语法取决于操作定义的位置：

- **公共仓库**：`{owner}/{repo}@{ref}` 或 `{owner}/{repo}/{path}@{ref}`，例如 `uses: actions/setup-node@v1`
- **同一仓库**：`{owner}/{repo}@{ref}` 或 `./path/to/dir`，例如 `uses: ./hello-world-action`
- **Docker Hub 容器**：`docker://{image}:{tag}`，例如 `uses: docker://alpine:3.8`

一个完整示例：

```yaml
name: Greet Everyone
on: [push]
jobs:
  build:
    name: Greeting
    runs-on: ubuntu-latest
    steps:
      - name: Hello world
        uses: actions/hello-world-javascript-action@v1
        with:
          who-to-greet: 'Mona the Octocat'
        id: hello
      - name: Echo the greeting's time
        run: echo 'The time was ${{ steps.hello.outputs.time }}.'
```

## 多任务依赖（F-211）

`jobs` 字段是 workflow 文件的主体，表示要执行的一项或多项任务。需要创建有依赖关系的任务时借助 `needs` 字段：

```yaml
jobs:
  job1:
  job2:
    needs: job1
  job3:
    needs: [job1, job2]
```

上面代码中，job1 必须先于 job2 完成，job3 等待 job1 和 job2 的完成才能运行，运行顺序依次为 job1、job2、job3。

## 状态徽章（F-212）

状态徽章显示工作流目前失败还是通过。常见添加位置是仓库的 README.md 文件，也可添加到任何网页。徽章显示默认分支的状态，也可用 branch 和 event 查询参数显示特定分支或事件的工作流状态。URL 格式：

```
https://github.com/<OWNER>/<REPOSITORY>/workflows/<WORKFLOW_NAME>/badge.svg
```

## 现状

- 本文基于 2020 年前后教程。GitHub Actions 的总体心智模型（workflow/job/step/action、`.github/workflows` 目录、`on` 触发、`runs-on`、`strategy.matrix`、`jobs.<id>.needs`）至今仍然成立。
- 已过时的示例细节（按原文 2020 年时点，实际请以官方文档为准）：
  - 运行器镜像 `ubuntu-18.04`/`ubuntu-14.04` 属于 2020 年前后版本，当前官方推荐 `ubuntu-latest` 等新镜像标签
  - `actions/checkout@v1` 等 `@v1` 引用是 2020 年时点的稳定版本，后续已有多个大版本，建议使用当前稳定标签
  - 默认分支在示例中写作 `master`，当前 GitHub 新仓库默认分支为 `main`
  - 语法细节（如 `steps.with` 的写法、表达式 `${{ }}` 上下文）持续演进，具体字段与取值以 [GitHub 官方工作流语法文档](https://docs.github.com/actions/reference/workflow-syntax-for-github-actions) 为准
- 学习资源（github.com/actions 的 starter-workflows、sdras 的 awesome-actions 等，F-202）仍可作为参考。

## 相关概念

- [创建 Gist 与分享代码片段](00-gist.md)
- [Git 学习路线与 Git Flow 分支模型导论](../../git/concepts/00-learning-path.md)
