# 示例文档

本目录包含 cozepy SDK 的完整可运行示例代码，每个示例覆盖一个核心使用场景。

- [基础对话示例](/examples/basic-chat.md) — TokenAuth 初始化 → SSE 流式对话 → 事件处理 → Token 用量（含单轮/多轮/异步版本）
- [工作流执行示例](/examples/workflow-execution.md) — 工作流式对话 → runs 流式执行 → 事件类型处理 → 中断恢复模式
- [WebSocket 语音对话示例](/examples/websocket-voice-chat.md) — EventHandler 继承 → Builder 模式 → 实时文本/TTS/ASR（异步）
- [OAuth PKCE 与设备码认证示例](/examples/oauth-pkce-auth.md) — PKCE 流程（含本地回调服务器）→ 设备码流程（轮询）→ Token 使用

```{toctree}
:maxdepth: 7

basic-chat
oauth-pkce-auth
websocket-voice-chat
workflow-execution
```
