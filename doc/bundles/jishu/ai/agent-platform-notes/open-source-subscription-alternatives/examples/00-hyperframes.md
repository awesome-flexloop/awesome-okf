---
type: Example
title: "HyperFrames 本地渲染路径"
description: "从 HTML 项目初始化到预览、检查和 MP4 输出的非实测路径"
tags: [HyperFrames, 安装, 视频]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-11-30
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: official, resource: "https://github.com/heygen-com/hyperframes" }
---

# HyperFrames 本地渲染路径

**非实测示例**：以下命令来自文章与官方 README 的组合，未在本任务执行。

```bash
npx hyperframes init my-video
cd my-video
npx hyperframes preview
npx hyperframes lint
npx hyperframes render
```

前置条件是 Node.js 22+ 与 FFmpeg。[F-015] 需要 Agent 工作流时，可另行安装项目 skills：

```bash
npx skills add heygen-com/hyperframes
```

先用低质量档验证布局和时间线，再考虑高分辨率或云渲染；云路径会引入额外平台成本。
