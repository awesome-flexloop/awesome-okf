---
okf_version: "0.2"
type: bundle
title: "ZDTaichu5.0-9B：空间具身多模态模型"
description: "基于公开博文与官方资料整理的 ZDTaichu5.0-9B 学习教程，覆盖模型定位、空间推理、训练管线和具身部署边界；属于技术综述/资讯，非操作教程。"
tags: [ZDTaichu5.0-9B, 紫东太初, 空间推理, 具身智能, 多模态模型]
generated: { by: "process:seven-concepts-e", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: flagged
stale_after: "2026-12-31"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/YOW4mB8Dg6loiKDfzF_NHQ?from=industrynews&color_scheme=light#rd
  - id: official-blog
    url: https://taichu-ai.github.io/ZDTaichu5.0-9B/
  - id: github
    url: https://github.com/Taichu-AI/ZDTaichu5.0-9B
  - id: huggingface
    url: https://huggingface.co/TaichuAI/ZDTaichu5.0-9B
---

# ZDTaichu5.0-9B：空间具身多模态模型

> **内容性质**：技术综述/资讯，非操作教程。本包不包含 `examples/`，因为源文没有提供版本化安装、配置、输入输出和实测步骤。

> **状态提示**：基准排名、具体分数和真实场景效果属于发布方报告，尚未找到独立复现实验；阅读时请把它们当作待复核证据。

ZDTaichu5.0-9B 是一个 9B 级多模态基础模型，尝试把通用视觉理解扩展到空间关系、视角变换、工具调用和具身任务。它的学习价值不只在于模型大小，也在于“空间推理 + 高层规划 + 外围控制系统”的组合方式。

## 内容导航

- [模型定位与发布事实](concepts/00-model-and-release.md)
- [空间推理与训练管线](concepts/01-spatial-reasoning-and-training.md)
- [具身部署边界](concepts/02-embodied-deployment-boundaries.md)
- [原文事实清单](references/article-source.md)
- [核验报告](references/verification.md)

## 已知边界

- 评测分数采用官方报告口径，不代表独立复现。
- 文章中的“小模型更有优势”是作者观点。
- 演示案例说明能力方向，不构成生产环境成功率或安全保证。
- 模型代码、权重、评测表和依赖版本可能变化，应在 `stale_after` 前复核。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
