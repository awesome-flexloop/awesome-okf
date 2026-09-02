---
type: Concept
title: 创建 Gist 与分享代码片段
description: 基于 2020 年前后《开源的世界》Gist 教程——公开/机密 Gist 的区别与隐私边界、Gist 即 Git 仓库、创建步骤、嵌入文本字段与 GeoJSON 地图
tags: [github, gist, 代码分享]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-5a939f2c6b79
    resource: /references/source-1.md
    title: 《3 创建 Gist》
---
# 创建 Gist 与分享代码片段

> **时点说明**：本文基于 2020 年前后教程（简书连载《开源的世界》第 3 篇《3 创建 Gist》）整理。Gist 的公开/机密机制与创建流程长期稳定，仅界面细节可能演进。

## 公开与机密 Gist（F-225、F-226）

GitHub 的 Gist 是一种轻量的代码片段分享方式，可以创建两种 Gist：**公开（public）** 和**机密（secret）** Gist。如果准备与世界分享想法，创建公开 Gist，否则创建机密 Gist。

关键区别与限制（F-226）：

- 每个 gist 都是一个 **Git 仓库**，可以复刻（fork）和克隆（clone）
- 公开 gists 显示在 Discover 中且可供搜索
- 机密 gists 不显示在 Discover 中，也不可搜索
- **创建 gist 后，无法将其从公共转换为机密**

## 机密 Gist 不是私人的（F-227）

机密 Gist 并不等同私人内容：将机密 gist 的 URL 发送给朋友即可查看；如果不认识的人发现了该 URL，也能看到你的 gist。如果需要让代码不被偷窥，建议改为**创建私有仓库**（private repository）。

## 创建 Gist 的步骤（F-228）

创建 Gist 的步骤：

1. 登录 GitHub
2. 导航到 gist 主页（gist.github.com）
3. 键入 Gist 的说明（可选）和名称
4. 在文本框中键入 Gist 的文本内容
5. 执行以下操作之一：
   - 单击 **Create public gist（创建公开 gist）**
   - 单击 **Create secret Gist（创建机密 Gist）**

也可以将桌面上的文本文件直接拖放到 Gist 编辑器中。

## 嵌入与地图支持（F-229）

- 可以将 gist 嵌入到支持 JavaScript 的任何文本字段中，如博文
- 要嵌入特定的 gist 文件，使用 `?file=FILENAME` 附加嵌入 URL
- Gist 支持地图 GeoJSON 文件，这些地图显示在嵌入的 Gist 中，方便分享和嵌入地图

## 现状

- 本文基于 2020 年前后教程。Gist 的"每个 gist 都是 Git 仓库""公开可搜索、机密不可搜索""机密非私人、不可从公共转机密"等核心机制至今仍然成立，Gist 主页与创建表单的界面细节可能已演进。
- 机密 Gist 适合"仅对特定人分享链接"的场景；对需要访问控制的内容，GitHub 私有仓库仍是更合适的选择（与原文建议一致）。

## 相关概念

- [GitHub Actions 工作流](01-actions-workflow.md)
- [Git 学习路线与 Git Flow 分支模型导论](../../git/concepts/00-learning-path.md)
