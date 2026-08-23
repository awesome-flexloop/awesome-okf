---
title: Agent-Learning-Hub GitHub 仓库
type: reference
bundle: /datawhale/Agent-Learning-Hub
description: Datawhale 出品的 AI Agent 学习路线图仓库，包含 README.md（Markdown 信源）和 index.html（交互式 Web 视图）两个核心文件。
sources:
  - id: github-repo
    resource: https://github.com/datawhalechina/Agent-Learning-Hub
    title: datawhalechina/Agent-Learning-Hub GitHub 仓库
---

# Agent-Learning-Hub GitHub 仓库

## 基本信息

- **仓库地址**：https://github.com/datawhalechina/Agent-Learning-Hub
- **出品方**：Datawhale
- **维护者**：陈思州（https://github.com/jjyaoao）
- **项目定位**：A curated AI Agent learning roadmap——不是随机链接收集，而是可照着执行的 AI Agent 学习 todo list

## 仓库内容概述

仓库只维护两个核心文件，形成"源-视图"结构：

| 文件 | 角色 | 说明 |
|------|------|------|
| `README.md` | Markdown 信源 | 完整的学习路线图，包含所有文字内容，面向 GitHub 原生渲染 |
| `index.html` | 交互式 Web 视图 | 单文件 HTML 应用，内嵌 CSS+JS，复刻 README 内容并增加进度追踪、搜索、主题切换、笔记等功能 |

## README.md 核心板块

1. **How To Use**：四类用户（新手/有经验者/做项目/找资料）的使用方式
2. **What To Learn Now**：当前 5 个优先学习方向
3. **Learning Todo List**：Stage 0-8 共 9 个递进阶段，每阶段含 checklist、推荐阅读、产出物
4. **Project Ladder**：11 级项目阶梯，从 Calculator Agent 到 Production Harness
5. **Curated Resources**：官方指南、项目地图、Skills/协议、现代系统、遗留框架、论文、GitHub 仓库、博客、Claude Code 学习路径
6. **Learning Principles**：8 条学习原则
7. **Contributing**：贡献指南

## index.html 技术实现

- 单文件 HTML，无构建工具、无前端框架
- 外部依赖仅 marked.js（CDN 加载，用于笔记 Markdown 渲染）
- 三个 JS 数据对象：`learningData`（阶段数据）、`ladderData`（阶梯数据）、`resourcesData`（资源数据）
- 交互功能：进度条（localStorage 持久化）、实时搜索高亮、暗色/亮色主题、Markdown 笔记编辑器、响应式移动端布局
