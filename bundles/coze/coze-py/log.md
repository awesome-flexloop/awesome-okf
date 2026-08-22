# Changelog

## v0.20.0-wiki.1 (2026-08-23)

### 新增

- 初始版本，基于 cozepy v0.20.0 源码生成 OKF v0.2 Wiki
- 10 篇概念文档（concepts/），覆盖架构、认证、客户端、对话、Bot、工作流、会话、WebSocket、音频、分页
- 4 篇示例文档（examples/），覆盖基础对话、工作流执行、WebSocket 语音、OAuth PKCE/设备码
- 5 篇 API 参考文档（references/），按模块登记所有公开类和方法
- 根索引和 3 个子索引文件

### 文档结构

```
coze-py/
├── concepts/
│   ├── index.md
│   ├── 00-overview-architecture.md
│   ├── 01-auth-system.md
│   ├── 02-client-init.md
│   ├── 03-chat-streaming.md
│   ├── 04-bot-management.md
│   ├── 05-workflows.md
│   ├── 06-conversations.md
│   ├── 07-websockets-realtime.md
│   ├── 08-audio-voice.md
│   └── 09-pagination-resources.md
├── examples/
│   ├── index.md
│   ├── basic-chat.md
│   ├── workflow-execution.md
│   ├── websocket-voice-chat.md
│   └── oauth-pkce-auth.md
├── references/
│   ├── index.md
│   ├── coze-client.md
│   ├── auth-model.md
│   ├── chat-workflow.md
│   ├── websockets-audio.md
│   └── data-pagination.md
├── index.md
└── log.md
```

### 生成方法论

- 遵循 source-code-to-okf-wiki 工作流（R→I→E→V→C）
- 信源先行（references/ 先于 concepts/ 生成）
- 分批生成（每批 ≤7 文件）
- 中文撰写，API 调用与源码事实一致
- 交叉链接使用 `/` 前缀 bundle-relative 路径
