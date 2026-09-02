---
type: Concept
title: Git 学习路线与 Git Flow 分支模型导论
description: 基于 2020 年前后《开源的世界》Git 学习笔记——Git 学习资源路线、gitk 中文乱码处理、中心版本库 master/develop 双主分支与 feature/release/hotfix 辅助分支模型
tags: [git, 分支模型, git-flow, 学习路径]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-1a4c45c12dee
    resource: /references/source-1.md
    title: 《2.1 Git 学习笔记》
---
# Git 学习路线与 Git Flow 分支模型导论

> **时点说明**：本文基于 2020 年前后教程（简书连载《开源的世界》第 2.1 篇《2.1 Git 学习笔记》）整理。Git 的基础心智模型（仓库、提交、分支、合并）与"分支纪律"至今仍然成立，但具体行为、默认命名与工具生态可能已演进，实操时以当前官方文档为准。

## Git 学习资源路线（F-213、F-214）

文章推荐的 Git 学习资源覆盖「原理图解 — 常用命令 — 进阶主题」三个层次：

- 《图解 Git》（marklodato.github.io）——可视化理解 Git 内部对象与操作
- Git 图解、常用命令和廖雪峰教程笔记总结——入门命令速查
- 《Git Rebase 原理以及黄金准则详解》——rebase 机制与使用边界
- Git 的原理简介和常用命令——内部原理入门
- 《图解 git 原理与日常实用指南》——原理图解与日常用法结合
- ssh-agent 使用指南——SSH 密钥代理配置
- Git 远程操作详解（阮一峰）——remote/fetch/pull/push 等远程操作
- 《标签管理》（廖雪峰）——tag 的创建、查看与发布

## gitk 中文乱码处理（F-215）

gitk（Git 自带的图形化仓库查看工具）在中文环境下可能出现乱码，文章给出的处理命令是设置 GUI 编码：

```bash
git config --global gui.encoding utf-8
```

## 中心版本库与双主分支（F-216）

文章转载《GIT分支管理是一门艺术》（英文原文 http://www.nvie.com/posts/a-successful-git-branching-model/），其核心建议是：**Git 在技术层面是无中心的分布式版本控制系统，但在管理层面上应保持一个中心版本库（origin）**。

中心版本库至少包含两个主分支：

| 分支 | 状态保证 |
|------|---------|
| master（主分支） | 团队成员从 master 获得的都是**可发布状态**的代码 |
| develop（开发分支） | 从 develop 能获得**最新开发进展**的代码 |

## 三类辅助分支（F-217）

在团队开发协作中建议引入"辅助分支"概念，其最大特点是**生命周期十分有限**，完成使命后即可被清除。至少应设置三类：

| 辅助分支 | 起源 | 归宿 | 命名约定 |
|---------|------|------|---------|
| Feature branches（功能分支） | develop | 最终归于 develop | - |
| Release branches（发布分支） | develop | develop 或 master | `release-*` |
| Hotfix branches（修复分支） | master | develop 或 master | `hotfix-*` |

- Feature branches 常用于开发一个独立的新功能，典型存在于团队开发者本地而非中心版本库
- Release branches 负责短期发布前准备、小 bug 修复与版本号等元信息准备，期间 develop 可继续承接新功能开发
- Hotfix branches 用于修复非预期的关键 BUG，避免 develop 上新功能的开发为 BUG 修复让路

## 分支操作命令与 `--no-ff`（F-218、F-219）

创建 feature 分支（基于 develop）：

```bash
git checkout -b myfeature develop
```

合并 feature 分支回 develop：

```bash
git checkout develop
git merge --no-ff myfeature
git branch -d myfeature
git push origin develop
```

`--no-ff`（not fast forward）的作用是要求 `git merge` 即使在可以 fast forward 的条件下也产生一个新的 merge commit，其目的在于**保持 Feature branches 整个提交链的完整性**。

Release 分支达到可发布状态后需完成三个动作（F-219）：

1. 将 Release 分支合并到 master 分支
2. 为 master 上的新提交打 TAG（记录里程碑）
3. 将 Release 分支合并回 develop 分支

示例命令：

```bash
git checkout master
git merge --no-ff release-1.2
git tag -a 1.2
git checkout develop
git merge --no-ff release-1.2
git branch -d release-1.2
```

Hotfix 分支修复后同样需合并回 master 并打 TAG：

```bash
git checkout master
git merge --no-ff hotfix-1.2.1
git tag -a 1.2.1
git checkout develop
git merge --no-ff hotfix-1.2.1
git branch -d hotfix-1.2.1
```

## 现状

- 本文基于 2020 年前后教程。分支模型（master/develop 双主分支 + feature/release/hotfix 辅助分支）属于**方法论层面的约定**，不随 Git 版本改变而失效；但 `master`/`develop` 是 2020 年前后的默认命名，当前不少平台与团队已改用 `main` 等命名或采用更轻量的工作流（如 GitHub Flow、Trunk-Based Development）。
- 文中列出的学习资源链接来自 2020 年前后，部分站点（如 marklodato.github.io）地址与内容可能迁移或失效，仅作历史参考。
- 本概念的分支模型导论与 [分支模型与团队协作](01-branch-model.md) 互补：本文讲模型与动机，后者给出基于 git-flow 扩展插件的团队实战命令。

## 相关概念

- [Git Flow 分支模型与团队协作](01-branch-model.md)
- [Git 下载代码加速与容量限制解除](02-download-acceleration.md)
- [GitHub Actions 工作流](../../github/concepts/01-actions-workflow.md)
