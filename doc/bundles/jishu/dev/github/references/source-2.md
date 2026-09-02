---
type: Reference
title: 信源：《5 GitHub Actions 手册》（简书连载《开源的世界》）
description: 简书文章《5 GitHub Actions 手册》信源登记——Actions 核心概念、.github/workflows 配置、触发事件 on、runs-on、构建矩阵、checkout 引用、jobs/needs、状态徽章（2020 年前后）
tags: [github, github-actions, CI, CD, 信源登记, 简书, 开源的世界]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-161b4241bc09
    url: https://www.jianshu.com/p/161b4241bc09
    title: 《5 GitHub Actions 手册》
---
# 信源：《5 GitHub Actions 手册》

本文是简书连载《开源的世界》（nb/40234132）的第 5 篇（GitHub Actions 手册），作者为"水之心"，内容时点为 2020 年前后。本 github 束的 GitHub Actions 工作流内容以其为事实依据（F-201~F-212）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | 5 GitHub Actions 手册 |
| 作者 | 水之心 |
| 所属连载 | 开源的世界（https://www.jianshu.com/nb/40234132） |
| 原文 URL | https://www.jianshu.com/p/161b4241bc09 |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- 学习资源：GitHub 帮助（help.github.com/cn）、关于自述文件、忽略文件、github.com/actions 组织及其 starter-workflows 仓库、sdras 的 awesome-actions 仓库
- 核心概念：Workflow、Workflow run、Workflow file、Job、Step、Action、CI、CD、Virtual environment、Runner、Event、Artifact
- 工作流程必须存储在仓库根目录 `.github/workflows` 中，至少包含一项作业（Job）
- 通过事件触发：`on: push`、事件数组 `on: [push, pull_request]`、POSIX cron 计划（`on: schedule`）、分支过滤（`on: push: branches: - master`）与可选的 `paths` 字段
- 选择虚拟环境：`runs-on: ubuntu-18.04`，可选 Ubuntu、Linux、macOS 等
- 构建矩阵：`strategy: matrix:` 下配置 `node: [6, 8, 10]`、`os: [ubuntu-14.04, ubuntu-18.04]`
- 检出操作：`- uses: actions/checkout@v1`、浅层克隆 `with: fetch-depth: 1`；引用操作语法 `{owner}/{repo}@{ref}`、同一仓库 `./path/to/dir`、Docker Hub `docker://{image}:{tag}`
- `jobs` 字段是 workflow 主体，作业间依赖用 `needs`
- 状态徽章 URL 格式 `https://github.com/<OWNER>/<REPOSITORY>/workflows/<WORKFLOW_NAME>/badge.svg`，常见添加位置为 README.md

## 覆盖事实编号

F-201 ~ F-212
