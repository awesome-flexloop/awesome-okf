---
type: Concept
title: 项目的 README 模板要素
description: 基于 2020 年前后《开源的世界》README 模板教程（翻译自 @PurpleBooth）——项目标题/获得开始/运行测试/部署/内置/投稿/版本/作者/许可证/致谢的结构要素与写法
tags: [开源, README, 模板, 文档]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-37d5fd7792ae
    resource: /references/source-3.md
    title: 《项目的自述文档（README）模板》
---
# 项目的 README 模板要素

> **时点说明**：本文基于 2020 年前后教程（简书连载《开源的世界》中的《项目的自述文档（README）模板》）整理，内容翻译自 @PurpleBooth 的 README 模板（https://gist.github.com/PurpleBooth/109311bb0361f32d87a2，F-220）。该模板结构与写法通用性较强，至今仍可参考。

## 模板整体结构（F-221）

README 模板的完整结构（按顺序）：

1. **项目标题**——使用一段话简要描述项目内容
2. **获得开始**——说明如何在本地计算机启动和运行项目副本以进行开发和测试
   - 先决条件：需要安装什么软件以及如何安装
   - 安装使用：提供部署运行环境的步骤示例
3. **运行测试程序**——解释如何提供自动化测试
   - 分解为端到端测试
   - 编码样式测试
4. **部署**——添加有关如何在实时系统部署的说明
5. **内置**——列出使用的框架与依赖
6. **投稿**——指向 CONTRIBUTING.md，说明行为准则与提交拉取请求的过程
7. **版本**——说明使用的版本控制方案
8. **作者**——列出作者与贡献者
9. **许可证**——说明项目许可证并指向许可证文件
10. **致谢**——感谢所有使用项目的人等

## 各部分的示例要素（F-222）

- **内置（Built With）**：示例框架与工具包括 Dropwizard（Web 框架）、Maven（依赖项管理）、ROME（生成 RSS 源）
- **版本（Versioning）**：使用 https://semver.org/lang/zh-CN/（语义化版本规范）进行版本控制
- **投稿（Contributing）**：指向 CONTRIBUTING.md
- **许可证（License）**：以 MIT 许可证为例，指向 LICENSE.md 文件
- **作者（Authors）**：以模板原作者 Billie Thompson（PurpleBooth）为例，并附贡献者列表

## 与「开启开源项目」中 README 建议的呼应

本模板是 [开启一个开源项目](01-start-a-project.md) 中 README 五问（What/Why/How/Help/Who，F-253）的可执行落地方案：模板的"项目标题 + 获得开始"对应 What/How，"内置 + 版本 + 作者 + 许可证 + 致谢"补充了 Why/Who 与合规信息。

## 现状

- 本文基于 2020 年前后教程。README 模板的章节划分与写作要点至今仍普遍适用，现代开源项目常在此基础上增补徽章（badge）、使用示例（screenshot）、文档链接（docs）等区块。
- 文中具体示例（Dropwizard/Maven/ROME）为 2020 年前后技术栈，仅作"内置"章节的写法示范，非推荐清单。

## 相关概念

- [开启一个开源项目](01-start-a-project.md)
- [开源参与指南](00-participation-guide.md)
- [GitHub Actions 工作流](../../github/concepts/01-actions-workflow.md)
