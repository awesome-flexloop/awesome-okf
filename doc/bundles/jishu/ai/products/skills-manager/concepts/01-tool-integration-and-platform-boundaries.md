---
okf_version: "0.2"
type: concept
title: 工具集成与平台边界
description: Skills Manager 的 Agent 管理与 CLI、桌面平台与安装资产、Windows junction 与 WSL 边界
tags: [skills-manager, agent, cli, windows, wsl, junction]
generated:
  by: process:seven-concepts
  at: "2026-10-10T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T00:00:00+08:00"
status: flagged
stale_after: "2026-12-31"
sources:
  - id: wechat-article
    url: "https://mp.weixin.qq.com/s/G4jm1Y2wAJUWSSnazAGdxg"
  - id: github-readme
    url: "https://raw.githubusercontent.com/xingkongliang/skills-manager/9e03d833829bc5e004263f61dec75f3bc8e39062/README.md"
  - id: github-release-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager/releases/latest"
---

# 工具集成与平台边界

## Agent 工作区与管理

- 文章称每个工具有独立工作区，可列出该工具实际可见的技能，包括非经该应用安装的技能（F-036）。
- 文章称可在 Dashboard 中启用 Agent 管理，并通过 `manage-skills` 能力和 CLI 管理 Agent（F-011）。
- 文章称启用 Agent 管理时，应用会安装 `manage-skills` 技能，并将 CLI 放在 `~/.skills-manager/bin/`，Agent 可不配置 PATH 调用（F-037）。

## 桌面平台与安装

- 文章称 macOS、Windows、Linux 均可安装，并给出 macOS Homebrew 安装方式（F-009）；官方 README 记载支持这三平台并列出相应桌面安装方式（F-029）。
- 文章称 GitHub Releases 提供 `.dmg`、`.exe`、`.msi`、`.AppImage`、`.deb`、`.rpm` 安装包并覆盖 x64 与 arm64（F-039）。**注意**：发布资产随版本变化，具体格式与架构覆盖应以当时 Release 为准。

## Windows junction 边界

- 文章称 Windows 可用 junction 方式把技能连接到各工具（F-010）。
- 实现层面的行为：Windows 链接实现优先尝试目录符号链接，在本地 NTFS 上可回退到 junction；远程/UNC（包括 `\\wsl.localhost`）无法使用该 junction 路径时走复制回退（F-027）。**这是源码分支描述，不代表实机测试。**

## WSL 边界

- 文章称 WSL 中桌面应用只能复制技能；若要使用 Linux 软链接，应安装 Linux 版 CLI（F-038）。该主张目前为**文章单源**，最终以官方资料为准，作为边界待核验项。
- 官方 README 对 WSL 场景的建议为复制技能，而非依赖 Windows junction（F-028）。

## 平台机制总结

Skills Manager 在 Windows 本地 NTFS 上可借助符号链接/junction 把集中技能库“连接”到各工具目录，但在 WSL/远程路径上与 Linux 侧无法用同一链接机制时，采用**复制**方式回退。应用集成依赖 `manage-skills` CLI 与独立 Agent 工作区，使不同工具各自可见技能而不相互污染。