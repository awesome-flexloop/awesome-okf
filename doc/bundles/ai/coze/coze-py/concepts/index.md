# 概念文档

本目录包含 cozepy SDK 的概念文档，按学习路径从基础到高级排列。

## 基础篇

- [00 整体架构概览](/concepts/00-overview-architecture.md) — 同步/异步双轨设计、懒加载服务组合、模块组织
- [01 认证体系](/concepts/01-auth-system.md) — PAT Token、JWT、Web OAuth、PKCE、设备码流程
- [02 客户端初始化与配置](/concepts/02-client-init.md) — base_url 选择、超时配置、自定义 http_client、日志

## 核心篇

- [03 对话与流式处理](/concepts/03-chat-streaming.md) — SSE 流式对话、ChatEvent 事件、Message 模型、工具调用
- [04 Bot 管理](/concepts/04-bot-management.md) — Bot CRUD、发布/取消发布、版本管理、配置模型
- [05 工作流](/concepts/05-workflows.md) — 工作流执行、流式对话、异步运行、中断恢复
- [06 会话管理](/concepts/06-conversations.md) — 会话生命周期、消息管理、消息反馈

## 高级篇

- [07 WebSocket 实时通信](/concepts/07-websockets-realtime.md) — Builder 模式、EventHandler、实时对话/语音
- [08 音频与语音](/concepts/08-audio-voice.md) — TTS、ASR、声音管理、实时房间、直播、声纹
- [09 分页模式与资源管理](/concepts/09-pagination-resources.md) — 三种分页器、文件、数据集、工作空间等

```{toctree}
:hidden:
:maxdepth: 7

00-overview-architecture
01-auth-system
02-client-init
03-chat-streaming
04-bot-management
05-workflows
06-conversations
07-websockets-realtime
08-audio-voice
09-pagination-resources
```
