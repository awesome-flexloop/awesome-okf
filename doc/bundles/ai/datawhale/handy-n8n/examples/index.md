# 实战示例

本目录包含 4 个实战示例，对应 handy-n8n 教程中的核心实践，覆盖从基础自动化到 AI 应用再到自定义节点开发的完整链路。

## 基础自动化

* [GitHub Trending 每日推送](github-trending-digest.md) — C06 案例：Schedule Trigger 定时获取 GitHub Trending 数据，通过邮件发送日报。对应概念：[工作流设计](../concepts/workflow-design.md)。
* [GitHub Issue 飞书通知](github-issue-notify.md) — C06 案例：Webhook 监听 GitHub Issue 事件，新 Issue 创建时通过飞书机器人实时通知。对应概念：[工作流设计](../concepts/workflow-design.md)。

## AI 应用

* [RAG 知识库对话](rag-knowledge-chat.md) — C04 实践：Form Trigger 文件上传 → Embedding → Vector Store 构建知识库，Chat Trigger + AI Agent 检索问答。对应概念：[AI 与 API 集成](../concepts/ai-api-integration.md)。

## 扩展开发

* [自定义高德地图天气节点](custom-amap-node.md) — C05 实践：TypeScript 声明式节点开发全流程，含节点类、鉴权类、routing 配置、npm link 本地调试。对应概念：[高级实战](../concepts/advanced-practice.md)。

```{toctree}
:hidden:
:maxdepth: 7

custom-amap-node
github-issue-notify
github-trending-digest
rag-knowledge-chat
```
