# API 参考文档

本目录包含 cozepy SDK 的信源登记（API 参考）文档，按模块组织。每个概念文档的 frontmatter `sources` 字段指向本目录的文件，确保所有 API 描述都有可溯源的信源。

- [Coze 客户端入口与基础设施参考](coze-client.md) — Coze/AsyncCoze 入口类、配置常量、版本、Requester、HTTP 层、Stream、异常体系、日志、工具函数
- [认证体系参考](auth-model.md) — TokenAuth、JWTAuth、OAuthApp（Web/PKCE/Device）、OAuthToken、DeviceAuthCode、Scope、load_oauth_app_from_config
- [对话与工作流参考](chat-workflow.md) — ChatClient/AsyncChatClient、Message、ChatEvent/ChatEventType、ChatPoll、工具调用模型、WorkflowsClient/runs/chat、WorkflowEvent
- [WebSocket 实时通信与音频参考](websockets-audio.md) — WebsocketsBaseClient、EventHandler、Builder 模式、Chat/Audio WS 客户端、音频配置模型、Audio HTTP 客户端（Speech/Transcriptions/Voices/Rooms/Live/VoiceprintGroups）
- [数据模型、分页与资源管理参考](data-pagination.md) — CozeModel、DynamicStrEnum、NumberPaged/TokenPaged/LastIDPaged、Bot 模型/枚举、Conversation/Section、File、Dataset/Document/Photo、Workspace、Templates、Variables、Folders、Connectors

```{toctree}
:hidden:
:maxdepth: 7

auth-model
chat-workflow
coze-client
data-pagination
websockets-audio
```
