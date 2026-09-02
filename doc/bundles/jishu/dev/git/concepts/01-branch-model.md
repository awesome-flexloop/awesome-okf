---
type: Concept
title: Git Flow 分支模型与团队协作
description: 基于 2020 年前后《开源的世界》团队项目配置管理教程——项目配置管理 PCM、Git Flow 规则表、feature/release/hotfix 三场景实战、裸库共享、版本号 x.y.z 与局域网协作
tags: [git, git-flow, 团队协作, 分支模型]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-65dc83219330
    resource: /references/source-2.md
    title: 《2.2 使用 Git 管理配置团队项目》
---
# Git Flow 分支模型与团队协作

> **时点说明**：本文基于 2020 年前后教程（简书连载《开源的世界》第 2.2 篇《2.2 使用 Git 管理配置团队项目》）整理。文中使用 git-flow 扩展插件（`git flow` 子命令）与 `master`/`develop` 命名，属于 2020 年前后的团队协作主流做法；方法论仍具参考价值，命令与命名以当前工具链为准。

## 项目配置管理（F-238）

项目配置管理（Project Configuration Management，PCM）是为了更加方便地管理项目而对每个项目进行统一规范的做法。文章采用 Git（git-scm.com）与 vscode（code.visualstudio.com）搭配进行项目管理。

## 项目初始化（F-239）

以"使用 Python 创建一个计算机视觉库（命名为 cvsome）"为例，初始化步骤：

```bash
# 克隆项目模板
git clone git@github.com:xinetzone/projects.git cvsome
cd cvsome

# 复制 Python 忽略规则，过滤编译中间文件
cp demo.gitignore/python.gitignore .gitignore

# 提交改动
git add .
git commit -m "修改 gitignore"

# 创建目录骨架
mkdir data draft models outputs app notebook

# 初始化 Git Flow 扩展
git flow init
```

其中 `data`、`draft`、`models`、`outputs`、`app`、`notebook` 各目录承担不同职责（数据/草稿/模型/输出/应用代码/笔记）。

## Git Flow 规则表（F-240）

Git Flow 将分支分成 2 个主要分支（master、develop）和 3 个临时的辅助分支（feature、release、hotfix）：

| 分支 | 简介 |
|------|------|
| master | 永远处在即将发布（production-ready）状态 |
| develop | 最新的开发状态 |
| feature | 开发新功能的分支，基于 develop，完成后 merge 回 develop |
| release | 准备要发布版本的分支，用来修复 bug；基于 develop，完成后 merge 回 develop 和 master |
| hotfix | 修复 master 上的问题，等不及 release 版本就必须马上上线；基于 master，完成后 merge 回 master 和 develop |

## 场景 1：开发新功能（F-241）

应用场景：开发一个用于爬取百度图片的 API（spide）：

```bash
git flow feature start spide
```

该操作创建了基于 develop 的特性分支 `feature/spide` 并切换过去。在 `app/` 目录下创建代码（含 `baiduimages.py`，用于按关键字从百度图片下载图片）。功能完成并提交后：

```bash
git flow feature finish spide
```

该操作完成：`feature/spide` 分支代码合并到 develop，删除该分支并切回 develop。

## 创建裸库共享（F-242）

对于公司场景，项目即资产，可能不想托管到 GitHub 等公开平台，而希望放在公司局域网内。此时可舍弃源库，重新创建裸库（相当于服务器）：

```bash
# 切到 cvsome 项目之外
cd ..

# 创建名为 cvsome.git 的裸库
git clone --bare cvsome/ cvsome.git
```

`cvsome.git` 便是需要的服务器。同一台电脑不同目录克隆副本：

```bash
git clone cvsome.git/ test/cvsome
cd test/cvsome
git branch -a   # 查看分支
```

克隆后可看到本地分支 master 与远程分支 `remotes/origin/develop`、`remotes/origin/master`，远程 HEAD 指向 `origin/master`。

## 版本号约定 x.y.z（F-243）

版本号格式为 `x.y.z`：

- `x`：在重大重构时升级
- `y`：在发布新的特性时升级
- `z`：在修改某个 bug 后升级

每个微服务都需要严格按照该开发模式执行。

## 场景 2：发布上线版本（F-244、F-245）

以发布上线版本代号 0.0.1 为例：

```bash
# 创建 release/v0.0.1 分支（基于 develop 最新提交）
git flow release start v0.0.1

# 提交到服务器
git flow release publish v0.0.1

# 追踪远端 release 分支（他人协作时）
git flow release track v0.0.1

# 完成发布
git flow release finish v0.0.1 -m "发布 v0.0.1"
```

`git flow release finish` 完成的工作（F-245）：

1. 归并 release 分支到 master 分支，并用 release 分支名打 Tag
2. 归并 release 分支到 develop，并移除 release 分支与远端分支 `remotes/origin/release/v0.0.1`
3. 切换到 develop 分支

## 场景 3：紧急修复（F-246）

生产环境版本处于不预期状态需立即修正时：

```bash
# VERSION 参数标记修正版本；[BASENAME] 为 finish release 时填写的版本号
git flow hotfix start VERSION [BASENAME]

# 修复完成，代码归并回 develop 和 master，master 打上修正版本 TAG
git flow hotfix finish VERSION
```

注意：feature 与 hotfix 也都有 `publish`、`track`，作用与 release 相类似。

## 局域网协作（F-247）

多人协作时通过裸库建立联系，使用 `push` 与 `pull` 进行更新。同一局域网不同电脑进行通信的克隆格式：

```bash
git clone lxw@192.168.20.57:/home/lxw/utils/sdk.git
```

其中 `@` 之前（`lxw`）为目标主机电脑的用户名，中间（`192.168.20.57`）为 IP 地址，最后（`/home/lxw/utils/sdk.git`）为裸库所在绝对路径。参考资料：git-flow 备忘清单（danielkummer.github.io/git-flow-cheatsheet）。

## 现状

- 本文基于 2020 年前后教程。Git Flow 属于较重度的分支模型，适合有明确发布节奏与版本管理的团队；`git flow` 子命令由第三方扩展（git-flow）提供，需要额外安装，当前团队也有采用更轻量工作流（GitHub Flow 等）的取向，可视团队规模与发布节奏选择。
- 示例中的默认分支名称为 `master`，当前 GitHub 等平台新建仓库默认分支已采用 `main`，实际项目以仓库配置为准。
- 裸库共享与局域网克隆的做法（`git clone --bare`、`git clone user@ip:/path`）是 Git 原生能力，不依赖托管平台，仍适用于内网开发场景。

## 相关概念

- [Git 学习路线与 Git Flow 分支模型导论](00-learning-path.md)
- [Git 下载代码加速与容量限制解除](02-download-acceleration.md)
- [创建 Gist 与分享代码片段](../../github/concepts/00-gist.md)
