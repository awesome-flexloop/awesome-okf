---
type: Example
title: "最小安装与创作请求"
description: "按官方 README 骨架完成 OpenMontage 的最小准备，并设计一个可审查的视频请求"
tags: [OpenMontage, 快速开始, 视频流水线]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-12-31
sources:
  - { id: repo, resource: "https://github.com/calesthio/OpenMontage" }
  - { id: article, resource: "/references/article-source.md" }
---

# 最小安装与创作请求

以下是官方 README 的结构化复述，不代表本次环境已运行成功。[F-004、F-005](../references/article-source.md)

## 准备环境

- Python 3.10+
- FFmpeg
- Node.js 18+
- 一个能读文件并运行代码的 AI 编程助手

## 初始化

```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup
```

然后在 AI 编程助手中打开仓库。先要求它读取 `AGENT_GUIDE.md`、选择流水线并说明将要使用的工具和外部服务。

## 设计请求

```text
Make a 60-second animated explainer about how neural networks learn.
Before production, show the selected pipeline, provider choices, estimated
cost, source plan, and approval points. Run the final audio, subtitle, frame,
and delivery checks before presenting the render.
```

如果要走真实素材路径：

```text
Make a 75-second documentary montage about city life in the rain.
Use real footage only, no narration, with music. Show source licenses and
the proposed edit before downloading or rendering.
```

## 验收

不要只检查“生成了 mp4”。还要保存研究来源、脚本、镜头计划、素材授权、成本日志、渲染参数和自检结果。[F-007、F-012](../references/article-source.md)

## 相关概念

- [从提示词到视频生产系统](../concepts/00-system-positioning.md)
- [成本、质量与许可证治理](../concepts/02-governance-and-evaluation.md)
