---
type: Playbook
title: VidBee 桌面使用与结果核对
status: stable
verified: {by: "process:seven-concepts-v", at: "2026-10-10"}
stale_after: 2026-12-31
source: ../references/article-source.md
sources:
  - {id: facts, resource: "../references/article-source.md"}
  - {id: release, resource: "https://github.com/nexmoe/VidBee/releases/tag/v2.1.0"}
  - {id: transcribe, resource: "https://vidbee.org/docs/transcribe/"}
  - {id: ai, resource: "https://vidbee.org/docs/ai-prompts/"}
generated: {by: "process:okf-wiki-agent", at: "2026-10-10"}
---

# VidBee 桌面使用与结果核对

**以下步骤根据官方文档整理，本包没有安装或运行 VidBee。** 使用自有或有明确授权的材料，先核对转录，再接入 AI；官网指南更新于 2026-10-08，具体按钮可能与旧发布包不同。[F-031～F-037](../references/article-source.md)

**版本先决条件：** 下列转录库流程属于滚动官网指南，官方标记为 Experimental，不是 v2.1.0 的逐按钮验收教程。v2.1.0 仅作为已确认的正式安装资产；若安装后没有对应入口，先核对构建版本与官方说明，不把新版界面说明当成旧版保证。新 Transcript/Overview 桥接明确晚于 v2.1.0。[F-036](../references/article-source.md)

## 获取软件

访问 [正式发布页](https://github.com/nexmoe/VidBee/releases/tag/v2.1.0)。2026-10-10 的 latest release API 返回 v2.1.0，发布时间为 2026-08-30 11:43:40 UTC。[F-006](../references/article-source.md)

| 系统 | 已确认资产 | 选择依据 |
|---|---|---|
| Windows | setup.exe、portable.exe、windows-portable.zip | 安装版或便携版；不要下载 blockmap/yml 当安装包 |
| macOS | arm64/x64 的 dmg、zip | 匹配处理器架构 |
| Linux | AppImage、amd64.deb | 匹配发行版与架构，不能假定 ARM 包存在 |

[F-007](../references/article-source.md)。不提供关闭系统安全保护的安装建议；遇到签名或兼容性问题，停下查对应版本说明。

## 完成一次转录

1. 在 Settings → Transcription 查看模型目录，按语言与机器推荐选择；首次运行会下载所选模型，观察进度完成。[F-031、F-033](../references/article-source.md)
2. 在 Transcripts → Add audio or video 导入材料，也可拖放或粘贴本地文件。在线材料先等下载成功，再从下载行选择 Transcribe / View transcript。[F-031](../references/article-source.md)
3. 观察 Queued、Processing、Transcript ready 等状态；No speech 不代表输入必然无语音，先回听再决定是否 Transcribe anyway。[F-032](../references/article-source.md)
4. 搜索关键句并点击时间戳，核对术语和数字；若分人不合理，用 Adjust speakers 调整，不把标签当实名。[F-012、F-013](../references/article-source.md)
5. 通过 Export 保存文本或 Markdown，打开结果核对内容。[F-014](../references/article-source.md)

这里的“模型目录”是设置内可选模型列表，不是推定的磁盘路径；具体选项随构建变化。先按材料语言筛选，再比较官方推荐、模型大小与可用内存，不提供未经测试的硬件门槛。[F-010、F-034](../references/article-source.md)

在线下载的准备流程是：确认媒体授权与公开可访问性，提交链接到当前版本的下载入口，检查保存位置及队列完成状态，再进入上述转录流程。README 确认下载与队列能力，但本包没有核验下载按钮的逐版本名称，因此这不是完整的下载 UI 操作手册。[F-008、F-020、F-024](../references/article-source.md)

自动转录在 Settings → Transcription → Transcribe after download 开启。官方提醒关闭开关不会取消已有排队任务；资源有限时先保持默认并发，再评估内存。[F-021、F-034](../references/article-source.md)

## 接入 AI

在 Settings → Providers 选择服务。预设一般填写 API key 与 Model ID；Custom 还需名称和 Base URL，要求兼容 OpenAI `/v1` 端点。先 Test connection，再保存并点 Use；保存不等于已经切换到活动供应商。[F-017、F-035](../references/article-source.md)

Ollama、LM Studio 本地服务按官方指南无需 API key，但服务本身仍需就绪。云服务收费、额度及模型权限由供应商决定，不从截图复制过时的模型 ID，也不宣称应用免费等于推理免费。[F-016、F-018](../references/article-source.md)

本地 AI 前置条件由读者另行完成：安装并启动所选服务、准备可运行模型、确认实际端点和 Model ID，再在 VidBee 测试连接。本教程不覆盖两种服务的安装，不编造端口与模型名称；连接成功后还需用一份已授权短转录验证结果。

打开已有转录，选择摘要或翻译提示词。内置七类用途可修改，也可新建提示词。下面是本教程拟定的提示词，不是官方默认模板：

```text
基于这份转录整理中文笔记。
保留原始人名、数字、否定词和条件限制。
仅在输入含时间戳时引用对应时间戳，不编造定位。
将原话概括与解释分开；资料不足时注明无法判断。
列出需要回听核对的专名与有歧义句子。
```

[F-015、F-017](../references/article-source.md)。输出不因语句流畅就自动可信；统计提取要与原转录逐项核对。

## 常见停点

| 现象 | 官方路径或本教程建议 |
|---|---|
| 模型下载受阻 | 官方允许在 Advanced → Download source 切换来源；不要反复创建任务 |
| 转录识别差 | 使用换模型重跑入口，对照同一段录音；旧转录可留历史 |
| AI 没有结果 | 先确认转录有文本、供应商测试成功且已 Use，再查供应商额度 |
| 视频导出不可用 | 检查输入是否音频，区分文本导出和 Video + Subs |
| 扩展没有本地转录 | 扩展不运行本地 ASR；不要用此判断桌面转录故障 |

[F-032、F-033、F-035、F-036、F-038](../references/article-source.md)。这些是排查起点，不是所有故障的已验证根因。
