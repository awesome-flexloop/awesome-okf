---
okf_version: "0.2"
type: bundle
title: VidBee 视频下载与本地转录教程
description: 微信公开文章经官方资料核验后的原创教程，覆盖视频获取、本地 ASR、AI 提示词、RSS 与自托管；操作未实测，按版本和隐私边界使用。
tags: [VidBee, 本地转录, 视频下载, AI提示词, RSS, OKF]
status: stable
verified: {by: "process:seven-concepts-v", at: "2026-10-10"}
stale_after: 2026-12-31
source: https://mp.weixin.qq.com/s/JfabWbrAcVGVQeY-vjTs3A
sources:
  - {id: article, resource: "https://mp.weixin.qq.com/s/JfabWbrAcVGVQeY-vjTs3A"}
  - {id: readme, resource: "https://github.com/nexmoe/VidBee/blob/v2.1.0/README.md"}
  - {id: release, resource: "https://github.com/nexmoe/VidBee/releases/tag/v2.1.0"}
  - {id: transcribe, resource: "https://vidbee.org/docs/transcribe/"}
  - {id: ai, resource: "https://vidbee.org/docs/ai-prompts/"}
generated: {by: "process:okf-wiki-agent", at: "2026-10-10"}
---

# VidBee 视频下载与本地转录教程

VidBee 将视频和音频获取、带时间戳的本地转录、AI 文本处理与导出集中管理。原文来自公众号芋道源码，作者 X，发布于 2026-10-07；本包于 2026-10-10 核对官方资料并原创改写。[事实登记](references/article-source.md)

**证据边界：原作者未安装实测，本包也未运行软件。** 功能来自官方资料确认，不是准确率或下载成功率保证。本地 ASR 不代表云 AI 不外发内容；官方 README、官网和发布页同属项目主体，不算独立评测。

## 阅读路径

1. [工作流与产品定位](concepts/00-workflow.md)：理解输入、转录、AI 与导出如何衔接。
2. [模型与隐私](concepts/01-transcription-and-privacy.md)：选择识别路径，明确数据去向。
3. [桌面使用](concepts/02-desktop-guide.md)：安装包选择、转录入口、供应商配置与核对。
4. [队列与自托管](concepts/03-queue-and-self-hosting.md)：RSS、Web/API 与存储管理。

核验依据见 [信源清单](references/source-manifest.md)、[逐项核验](references/verification.md)；学习后的方法论归纳见 [知识地图](references/knowledge-map.md)。

## 已知边界

- 正式发布事实固定为 v2.1.0，较新的官网指南有开发版说明；不可把兼容构建的新功能当成旧安装包能力。
- 支持 1000+ 站点是项目声明，未逐站测试；100+ 语言针对 Whisper，不针对所有模型。
- 不提供本地与云模型的泛化质量排名，也没有全流程耗时、成本或准确率实测。
- 软件 MIT 许可不替代媒体授权，个人学习不自动保证合法。
- 原文未满足实测可复现性第二问，不设置 `examples/`；桌面章节仅整理官方步骤。

## 主题关联

[AI 产品与终端工具](../index.md)提供同类工具导航。本包面向使用与证据边界，未开展 VidBee 源码教程或独立部署测试。

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
references/index
log
```
