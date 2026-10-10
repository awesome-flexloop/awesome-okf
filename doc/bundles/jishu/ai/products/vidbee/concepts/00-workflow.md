---
type: Concept
title: VidBee 工作流与产品定位
status: stable
verified: {by: "process:seven-concepts-v", at: "2026-10-10"}
stale_after: 2026-12-31
source: ../references/article-source.md
sources:
  - {id: facts, resource: "../references/article-source.md"}
  - {id: readme, resource: "https://github.com/nexmoe/VidBee/blob/v2.1.0/README.md"}
generated: {by: "process:okf-wiki-agent", at: "2026-10-10"}
---

# VidBee 工作流与产品定位

一段录音的价值通常藏在具体句子和上下文里。VidBee 把媒体获取、带时间戳转录、AI 文本处理和导出组织到同一工具中；来源可以是支持站点的视频，也可以是已有本地音视频。[F-008、F-013～F-015](../references/article-source.md)

## 从媒体到笔记

| 阶段 | 输入 | 处理结果 | 人工需要判断的内容 |
|---|---|---|---|
| 获取 | 授权 URL 或本地文件 | 下载任务或媒体条目 | 是否有使用权限，内容是否完整 |
| 转录 | 媒体、源字幕或 ASR 模型 | 带时间戳的文字及说话人标签 | 专名、数字、误听与分人错误 |
| AI | 转录、提示词、所选供应商 | 摘要、翻译、问答等 | 是否漏掉限定语或添加原文没有的结论 |
| 导出 | 文字或视频 | 文本、Markdown、字幕视频 | 引用上下文、公开权限及目标播放器支持 |

表格是教程对官方能力的教学重组，不是额外的软件模块承诺。[F-011～F-019](../references/article-source.md)

ASR 是自动语音识别，把声音转换成文字；说话人分离把片段分组，不等于识别真实身份。字幕可能由站点提供，也可能来自机器生成，不能仅凭“有字幕”判定准确。AI 则处理已有文字，无法自然修复没有证据的误听。把转录核对放在摘要之前，是本教程的实践建议。

## 三种产品形态

| 形态 | 官方材料确认 | 不能据此推定 |
|---|---|---|
| 桌面端 | 本地媒体、ASR、文本与 AI 工作流 | 所有机器均有相同速度或 GPU 支持 |
| Web/API | 共用下载核心，提供服务端管理 | 下载文件已经在浏览器所在计算机 |
| 浏览器扩展 | WXT 扩展目录存在 | 在浏览器直接运行桌面本地 ASR |

共享核心指 yt-dlp/ffmpeg 下载核心，不代表三端全部功能相同。扩展 ASR 和新桌面桥接的限制以当前指南为准。[F-009、F-026、F-036](../references/article-source.md)

## 适合与不适合

访谈可先检查分人和原话，课程可围绕时间戳定位解释，播客可结合 RSS 管理后续更新。需要纸面证据、司法逐字转录或正式医学记录时，不能把未校对的机器输出作为定稿；这是风险控制建议，不是产品认证结论。

原文作者没有实测，项目资料也没有证明所有语言、设备及大文件表现。学习本工具应从一份有使用权、可回听的材料开始，而不是据 Star 数量决定批量迁移。[F-003、F-005、F-037](../references/article-source.md)

继续阅读：[转录与隐私](01-transcription-and-privacy.md) · [桌面使用](02-desktop-guide.md) · [队列与自托管](03-queue-and-self-hosting.md)。
