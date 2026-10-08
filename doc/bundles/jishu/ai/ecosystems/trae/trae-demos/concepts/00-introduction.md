---
type: Concept
title: TRAE Demos 定位与期数制组织
description: trae-demos 作为 TRAE 构建项目展示平台的定位、period-N 期数制组织和 Markdown 驱动展示
tags: [demos, trae, period-based, showcase, trae-demos]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/demos-source.md
    title: "Trae Demos 源码信源"
---

# TRAE Demos 定位与期数制组织

## 仓库定位

trae-demos 是 TRAE 社区驱动的**项目展示平台**，MIT 许可证，展示"用 TRAE 构建的优秀项目"。与 awesome-trae 的资源索引定位不同，trae-demos 是**深度展示**——每个 Demo 有独立 Markdown 页面，包含项目介绍、核心亮点、技术栈、运行方式和预览截图。

## 期数制（Period-based）组织

trae-demos 采用**"期"（period）**作为内容组织单位，类似技术期刊：

```
demos/
├── period-1/demo-1.md, demo-1.zh-CN.md, demo-2.md, demo-2.zh-CN.md
└── period-2/...
```

期数制的优势：发布仪式感、追更体验、批次质量控制、时间线叙事。命名规范：目录 `period-N`，文件 `demo-M.md` / `demo-M.zh-CN.md`。

当前 period-1（2026.03）收录 2 个 Demo：Minecraft Guilin City Walk 和 TraeClaw。

> ⚠️ **事实记录**：Demo #2 文件头标注"Issue: #2 | April 2026"，与 README 中"Issue #1"汇总不一致，期数标注待统一。

## 双层结构

- **主 README**：汇总表格（Past Issues/往期内容）按期数导航
- **每期独立文件**：双语 Markdown 文件对，文件头标注期号和时间

## Markdown 驱动与双语策略

展示完全由 Markdown 驱动，Git 友好、可静态部署、贡献门槛低。维护完整中英双语体系（README/CONTRIBUTING/Demo/Issue 模板均中英双语独立维护）。

## 相关链接

- [Demo Markdown 文档格式](01-demo-format.md)
- [投稿流程与多场景 Issue 模板](02-contribution-process.md)
- [提交 Demo 示例](../examples/submit-demo.md)
- [TRAE Demos 仓库资源索引](../references/demos-source.md)
