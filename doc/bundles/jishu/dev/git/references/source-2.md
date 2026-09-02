---
type: Reference
title: 信源：《2.2 使用 Git 管理配置团队项目》（简书连载《开源的世界》）
description: 简书文章《2.2 使用 Git 管理配置团队项目》信源登记——项目配置管理 PCM、Git Flow 规则表与 feature/release/hotfix 实战、裸库共享、版本号 x.y.z（2020 年前后）
tags: [git, git-flow, 信源登记, 简书, 开源的世界]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-65dc83219330
    url: https://www.jianshu.com/p/65dc83219330
    title: 《2.2 使用 Git 管理配置团队项目》
---
# 信源：《2.2 使用 Git 管理配置团队项目》

本文是简书连载《开源的世界》（nb/40234132）的第 2.2 篇（使用 Git 管理配置团队项目），作者为"水之心"，内容时点为 2020 年前后。本 git 束的分支模型与团队协作内容以其为事实依据（F-238~F-247）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | 2.2 使用 Git 管理配置团队项目 |
| 作者 | 水之心 |
| 所属连载 | 开源的世界（https://www.jianshu.com/nb/40234132） |
| 原文 URL | https://www.jianshu.com/p/65dc83219330 |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- 项目配置管理（Project Configuration Management，PCM）：采用 Git（git-scm.com）与 vscode（code.visualstudio.com）搭配进行项目管理
- 项目初始化流程（git clone / .gitignore / git flow init / 目录骨架）
- Git Flow 规则表：master/develop 两主分支 + feature/release/hotfix 三辅助分支
- 三个实战场景：feature（开发新功能）、release（发布版本）、hotfix（紧急修复）
- 创建裸库（`git clone --bare`）共享、局域网克隆格式 `git clone lxw@IP:/path/to/bare.git`
- 版本号格式 `x.y.z`：x 重大重构、y 新特性、z 修复 bug
- 参考资料：git-flow 备忘清单（danielkummer.github.io/git-flow-cheatsheet）

## 覆盖事实编号

F-238 ~ F-247
