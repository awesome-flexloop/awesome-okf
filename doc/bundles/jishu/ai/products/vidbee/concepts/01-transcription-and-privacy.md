---
type: Concept
title: 本地转录、模型选择与隐私边界
status: stable
verified: {by: "process:seven-concepts-v", at: "2026-10-10"}
stale_after: 2026-12-31
source: ../references/article-source.md
sources:
  - {id: facts, resource: "../references/article-source.md"}
  - {id: readme, resource: "https://github.com/nexmoe/VidBee/blob/v2.1.0/README.md"}
  - {id: transcribe, resource: "https://vidbee.org/docs/transcribe/"}
  - {id: ai, resource: "https://vidbee.org/docs/ai-prompts/"}
generated: {by: "process:okf-wiki-agent", at: "2026-10-10"}
---

# 本地转录、模型选择与隐私边界

VidBee 的本地识别支持 Whisper、SenseVoice、Parakeet、Qwen3-ASR 系列；具体可下载模型、硬件推荐和语言覆盖以当前模型目录为准。官方说明 Whisper 支持 100+ 语言，但不能把这一范围套给每个系列。[F-010、F-034](../references/article-source.md)

## 模型选择的依据

先按语言、可用内存和材料长度筛选，再用同一录音对照。官方指南把 Tiny 偏向速度、Base/Small 作为一般机器选项，更大模型偏向准确度；这是项目建议，不是本包实测排名。不要按系列名称推定模型大小、所有语言效果、GPU 加速或最低内存。[官方转录指南](https://vidbee.org/docs/transcribe/)

本教程建议记录关键术语、数字和人名的误识别数量，查看时间戳是否能回到对应句子。噪声、口音和多人重叠需要单独核对；当前没有足够数据写出某个模型的准确率或速度。[F-037](../references/article-source.md)

源字幕可避免重新识别，但也可能错误。若字幕缺失或质量不满足用途，再尝试本地 ASR。说话人重新标记不会改识别文字，因此“人数已修正”与“文字已校对”应分别验收。[F-011、F-012](../references/article-source.md)

## 数据实际流向

| 操作 | 官方资料所述边界 | 教程建议 |
|---|---|---|
| 在线下载 | 需要访问源站 | 使用有授权内容，遵守访问限制 |
| 初次模型下载 | 下载所选模型 | 完成下载后再判断离线能力 |
| 本地 ASR | 音频不需上传转录服务 | 仍保护本地文件、日志和备份 |
| 云 AI 提示词 | 提示词与转录内容送往所选供应商 | 先检查隐私、合同和保留政策 |
| 本地 AI 端点 | 可让 AI 步骤留在本机 | 核对实际 Base URL、路由及后端依赖 |

[F-018、F-019、F-033](../references/article-source.md)。本地保存 API key 是项目声明，不等于已证明加密存储、没有遥测或任何进程都不能读取。本次没有抓包和安全审计。

“全程离线”至少需要已有本地材料、已缓存的识别与 AI 模型，以及真实本地端点；仅选了 Ollama 或 LM Studio 名称仍不足以证明网络隔离。涉及内部会议和个人信息时，应先确认授权，再决定是否交给云端处理。

## 导出方式的差异

文本/Markdown 适合检索和知识整理；带可选择字幕的视频允许播放器切换显示；Hard 烧录字幕需要重编码，不能关闭。官方指南指出音频材料只能导出文本而非视频。导出后用目标工具打开验证，不用“导出成功”推定格式兼容。[F-014、F-038](../references/article-source.md)

软件采用 MIT 只说明软件许可，不能授予视频、音乐、课程或人物声音的使用权。“个人学习”“不收费”“翻译加解说”都不是本教程可保证的免责条件。[F-004、F-028](../references/article-source.md)

## 使用前的责任清单

下表是本教程提出的治理建议，不是已核验的 VidBee 内置功能。

| 对象 | 使用者或部署者应确认 |
|---|---|
| 媒体与人物声音 | 分别确认下载、转录、云处理、翻译、改编、分发的授权范围，不用一种许可代替所有用途 |
| 原媒体、转录与 AI 输出 | 指定保留期限和删除责任人，删除后复查实际文件及应用记录；应用是否完整清除所有副本本包未核验 |
| 日志、缓存和备份 | 单独制定访问和过期清理规则，备份有独立保留期限，不能以删除任务认定备份同步消失 |
| 云端副本 | 核查供应商保留、训练使用与删除政策；本地删除不证明云副本删除 |
| 模型与依赖 | 软件 MIT 不代表所有模型及依赖商用许可一致；本包未逐项核验，商业使用前另行确认 |

投入评估应计入人工回听校对、模型下载和推理资源、存储备份、云 API 额度及维护成本。没有实际样本对照时，不承诺降本比例或节省工时。
