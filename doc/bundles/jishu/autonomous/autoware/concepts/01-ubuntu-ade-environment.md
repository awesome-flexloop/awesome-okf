---
type: Concept
title: Ubuntu 与 ADE 开发环境
description: Autoware.Auto 的开发环境 ADE（Agile Development Environment）——Docker 包装器定位、adehome 主目录约定、克隆与构建测试命令（2020 年前后）
tags: [autoware, ADE, Ubuntu, docker, 开发环境]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-7218542ae424
    resource: /references/source-01.md
    title: 《Ubuntu 搭建 AutowareAuto》
---
# Ubuntu 与 ADE 开发环境

本文基于 2020 年前后教程，介绍在 Ubuntu 上使用 Agile Development Environment（ADE）开发 Autoware.Auto 应用的环境原理与操作命令（F-319~F-323）。ADE 是 Autoware.Auto 官方推荐的开发环境，也是 [WSL2 环境搭建](00-wsl2-environment.md) 与 [Autoware.Auto 基础](02-autoware-auto-basics.md) 两篇所依赖的公共底座。

## ADE 是什么

文章描述使用 ADE 开发 Autoware.Auto 应用，参考来源为 gitlab.com/ApexAI/autowareclass2020 的 lectures/01_DevelopmentEnvironment/devenv.md 与 AutowareAuto 官方 installation 文档（F-319）。

## adehome 主目录

ADE 需要一个在主机上的目录作为用户在容器内的主目录挂载，该目录填充 dotfiles，且必须与容器外部用户的主目录不同；文章建议多项目场景下每个项目使用专用的 adehome 目录（F-320）。

## .adehome 与 .aderc

ADE 寻找一个包含名为 `.adehome` 文件的目录（从当前工作目录开始并继续到父目录）来标识要挂载的 ADE 主目录；Autoware.Auto 提供 `.aderc` 文件，该文件应存在于当前工作目录或任何父目录中，可通过设置环境变量覆盖默认配置值（F-321）。

## 克隆 AutowareAuto

文章给出的克隆命令（F-322）：

```bash
git clone --recursive https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto.git
```

## 初始化与测试

初始化与测试命令（F-323）：

```bash
ade start --update --enter
colcon build
colcon test
colcon test-result
```

## 现状

本文基于 2020 年前后教程，涉及的 Autoware.Auto 早期版本与 ADE 环境可能存在结构差异，ADE 本身与 Autoware 生态仍在演进。当前安装与使用请以 Autoware 官方当前文档为准。

## 事实溯源

- F-319~F-323（[source-01.md](../references/source-01.md)）
