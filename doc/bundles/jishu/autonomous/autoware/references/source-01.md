---
type: Reference
title: 信源：《Ubuntu 搭建 AutowareAuto》（简书连载《☠️无人驾驶(停止维护)》）
description: 简书文章《Ubuntu搭建AutowareAuto》信源登记——ADE开发环境原理、adehome主目录约定、克隆与构建测试命令（2020 年前后）
tags: [autoware, ADE, Ubuntu, 信源登记, 简书, 无人驾驶]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-7218542ae424
    url: https://www.jianshu.com/p/7218542ae424
    title: 《Ubuntu 搭建 AutowareAuto》
---
# 信源：《Ubuntu 搭建 AutowareAuto》

本文是简书连载《☠️无人驾驶(停止维护)》（nb/47487870）中关于在 Ubuntu 上搭建 Autoware.Auto 开发环境的文章，作者为"水之心"，内容时点为 2020 年前后。本 autoware 束的 ADE 开发环境内容以其为事实依据（F-319~F-323）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | Ubuntu 搭建 AutowareAuto |
| 作者 | 水之心 |
| 所属连载 | ☠️无人驾驶(停止维护)（https://www.jianshu.com/nb/47487870） |
| 原文 URL | https://www.jianshu.com/p/7218542ae424 |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- 使用 Agile Development Environment（ADE）开发 Autoware.Auto 应用，参考来源为 gitlab.com/ApexAI/autowareclass2020 的 lectures/01_DevelopmentEnvironment/devenv.md 与 AutowareAuto 官方 installation 文档（F-319）
- ADE 需要一个主机目录作为用户在容器内的主目录挂载，该目录填充 dotfiles 且必须与容器外部用户的主目录不同；多项目场景下每个项目使用专用的 adehome 目录（F-320）
- ADE 通过查找包含 `.adehome` 文件的目录（从当前工作目录向上回溯）识别要挂载的 ADE 主目录；Autoware.Auto 提供 `.aderc` 文件，可通过环境变量覆盖默认配置（F-321）
- 克隆命令：`git clone --recursive https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto.git`（F-322）
- 初始化与测试：`ade start --update --enter` 后依次执行 `colcon build`、`colcon test`、`colcon test-result`（F-323）

## 覆盖事实编号

F-319 ~ F-323
