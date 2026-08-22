---
type: Facts
okf_version: "0.2"
generated: "2026-08-22"
bundle: jupyter-chat
tags: [jupyter, chat, jupyterlab-extension, yjs, real-time, ui-components]
---

# jupyter-chat 事实集

## 项目元数据

- F-001: package.json:2 — 根包名为 `jupyter-chat-root`，私有包（private: true）。
- F-002: package.json:3 — 版本号为 `0.25.0-alpha.4`。
- F-003: package.json:4 — 项目描述为 "A chat package for Jupyterlab extension"。
- F-004: package.json:15 — 使用 BSD-3-Clause 许可证。
- F-005: package.json:24-27 — 使用 Yarn workspaces，工作区包含 `packages/*` 和 `docs/jupyter-chat-example`。
- F-006: package.json:65 — packageManager 指定为 `yarn@3.5.0`。
- F-007: pyproject.toml:9 — Python 包名为 `jupyterlab_chat`。
- F-008: pyproject.toml:12 — Python 版本要求 `>=3.10`，支持 3.10-3.14。
- F-009: pyproject.toml:29-34 — 核心依赖：jupyter_server>=2.0.1,<3、jupyter_events>=0.6.0、jupyter_ydoc>=3.0.0,<5.0.0、pycrdt>=0.12.48,<0.15.0。
- F-010: pyproject.toml:42-44 — collaboration 可选依赖：jupyter_collaboration>=4,<6。
- F-011: pyproject.toml:5 — 构建系统使用 hatchling+jupyter-builder。

## 包结构

- F-012: packages/jupyter-chat/ — 核心 UI 组件包 `@jupyter/chat`，提供聊天组件、模型、Token、类型定义等可复用基元。
- F-013: packages/jupyterlab-chat/ — JupyterLab 集成包 `jupyterlab-chat`，基于共享文档实现 RTC 聊天功能。
- F-014: packages/jupyterlab-chat-extension/ — JupyterLab 扩展插件包，注册命令、聊天命令提供者（emoji、@提及）。
- F-015: python/jupyterlab-chat/ — Python 后端包，提供 ChatManager、YChat 模型、WebSocket handler、事件系统。
- F-016: docs/jupyter-chat-example/ — 示例扩展包，展示如何基于 @jupyter/chat 构建聊天扩展。

## @jupyter/chat 核心包

- F-017: packages/jupyter-chat/package.json:2 — 包名为 `@jupyter/chat`。
- F-018: packages/jupyter-chat/package.json:4 — 描述为 "A package that provides UI components that can be used to create a chat in a Jupyterlab extension"。
- F-019: packages/jupyter-chat/package.json:46-74 — UI 依赖包括 @mui/material ^7.3.2、@mui/icons-material ^7.3.2、@emotion/react、@emotion/styled（MUI 组件库）、react ^18.2.0、react-dom ^18.2.0、@jupyter/react-components。
- F-020: packages/jupyter-chat/package.json:49 — 依赖 `@jupyter/ydoc: ^3.0.0 || ^4.0.0` 用于共享文档集成。
- F-021: packages/jupyter-chat/src/index.ts — 导出所有核心模块（components、widgets、model、message、types、tokens、input-model、active-cell-manager、selection-watcher、context、icons、utils、theme-provider）。

## 类型定义

- F-022: packages/jupyter-chat/src/types.ts:13-33 — `IUser` 接口包含 username、name、display_name、initials、color、avatar_url、mention_name、bot 字段。
- F-023: packages/jupyter-chat/src/types.ts:24-28 — mention_name 计算规则：取 display_name/name/username 中第一个非空值，空格替换为 `-`。
- F-024: packages/jupyter-chat/src/types.ts:38-67 — `IConfig` 接口包含 sendWithShiftEnter、stackMessages、unreadNotifications、enableCodeToolbar、sendTypingNotification、showDeleted、sendWithSelection 配置项。
- F-025: packages/jupyter-chat/src/types.ts:92-146 — `IMessageContent` 类型定义消息结构：type、body(markdown)、id、time(epoch 秒)、sender(IUser)、attachments、mentions、raw_time、deleted、edited、stacked、metadata、mime_model。
- F-026: packages/jupyter-chat/src/types.ts:87 — `IMessageMetadata` 为空接口，支持 TypeScript 模块增强（declare module）扩展自定义字段。
- F-027: packages/jupyter-chat/src/types.ts:148-165 — `IMessage` 接口继承 IMessageContent，增加 update()方法、content 属性、changed 信号、renderedDelegate（PromiseDelegate）。
- F-028: packages/jupyter-chat/src/types.ts:194 — 附件类型 `IAttachment` 为 `IFileAttachment | INotebookAttachment` 的联合类型，通过 type 字段区分。
- F-029: packages/jupyter-chat/src/types.ts:196-211 — `IFileAttachment` 包含 type:'file'、value(文件路径)、mimetype、selection(选区范围)。
- F-030: packages/jupyter-chat/src/types.ts:239-253 — `INotebookAttachment` 包含 type:'notebook'、value(notebook 路径)、mimetype、cells(单元格列表)。
- F-031: packages/jupyter-chat/src/types.ts:255-268 — `IAttachmentSelection` 包含 start:[行,列]、end:[行,列]、content(选区初始内容)。
- F-032: packages/jupyter-chat/src/types.ts:278 — `ChatArea` 类型为 `'sidebar' | 'main'`，标识聊天显示区域。

## Message 类

- F-033: packages/jupyter-chat/src/message.ts:20 — `Message` 类实现 `IMessage` 接口。
- F-034: packages/jupyter-chat/src/message.ts:26-28 — 构造函数接收 IMessageContent，存储为私有 `_content`。
- F-035: packages/jupyter-chat/src/message.ts:97 — `update()` 方法更新消息字段，对 body/id/sender/time/attachments/mentions/mime_model 等关键字段触发重渲染。

## ChatModel

- F-036: packages/jupyter-chat/src/model.ts:35 — `IChatModel` 接口继承 IDisposable，是聊天模型的核心抽象。
- F-037: packages/jupyter-chat/src/model.ts:39 — id 属性为聊天唯一标识，由 AbstractChatModel 实现。
- F-038: packages/jupyter-chat/src/model.ts:61 — ready 属性为 Promise<string>，解析后返回稳定的 chat id。
- F-039: packages/jupyter-chat/src/model.ts:69 — awareness 属性为可选的 IAwareness，允许扩展通过协作状态读取会话信息。
- F-040: packages/jupyter-chat/src/model.ts:84-89 — 核心属性：messages(IMessage[])、input(IInputModel)、writers(IWriter[])。
- F-041: packages/jupyter-chat/src/model.ts:99-109 — 集成属性：activeCellManager、selectionWatcher、documentManager。
- F-042: packages/jupyter-chat/src/model.ts:114-144 — 信号系统：messagesUpdated、configChanged、unreadChanged、viewportChanged、writersChanged、messageChanged、messageEditionAdded。

## Token 系统

- F-043: packages/jupyter-chat/src/tokens.ts:17-34 — `IChatPanel` 接口定义聊天面板：widget(ChatWidget)、model(IChatModel)、area(ChatArea)、toolbar(Widget)。
- F-044: packages/jupyter-chat/src/tokens.ts:39 — `IChatTracker` 类型为 `IWidgetTracker<IChatPanel>`。
- F-045: packages/jupyter-chat/src/tokens.ts:44-47 — `IChatTracker` Token 标识为 `@jupyter/chat:IChatTracker`。
- F-046: packages/jupyter-chat/src/tokens.ts:52-60 — `IChatPlaceholderFactory` 接口用于自定义多聊天面板的空状态占位符。
- F-047: packages/jupyter-chat/src/tokens.ts:75-95 — `IChatBodyPlaceholderFactory` 接口用于自定义空聊天的消息区域占位符，接收 onSend 回调。

## UI 组件结构

- F-048: packages/jupyter-chat/src/components/ — React UI 组件目录，包含 chat.tsx（主聊天组件）、avatar.tsx（头像）、attachments.tsx（附件）、writing-indicator.tsx（写作指示器）、scroll-container.tsx（滚动容器）。
- F-049: packages/jupyter-chat/src/components/input/ — 输入区组件：chat-input.tsx、submit-message.ts、toolbar-registry.tsx、use-chat-commands.tsx、buttons/（发送/取消/附件/停止/保存编辑按钮）。
- F-050: packages/jupyter-chat/src/components/messages/ — 消息区组件：messages.tsx、message.tsx、message-renderer.tsx、header.tsx、footer.tsx、toolbar.tsx、navigation.tsx、preamble.tsx、welcome.tsx、chat-body-placeholder.tsx。
- F-051: packages/jupyter-chat/src/components/code-blocks/ — 代码块组件：code-toolbar.tsx（复制/替换等工具栏）、copy-button.tsx。
- F-052: packages/jupyter-chat/src/widgets/ — Lumino Widget 封装：chat-widget.tsx、chat-sidebar.tsx、multichat-panel.tsx、chat-selector-popup.tsx、chat-error.tsx、placeholder.tsx。
- F-053: packages/jupyter-chat/src/registers/ — 注册器模块：attachment-openers.ts、chat-commands.ts、footers.ts、preambles.ts。

## jupyterlab-chat 集成包

- F-054: packages/jupyterlab-chat/package.json:2 — 包名为 `jupyterlab-chat`。
- F-055: packages/jupyterlab-chat/package.json:4 — 描述为 "The library to build a chat based on shared document"。
- F-056: packages/jupyterlab-chat/package.json:46 — 依赖 `@jupyter/collaborative-drive: ^4.4.0 || ^5.0.0` 用于 RTC 集成。
- F-057: packages/jupyterlab-chat/src/token.ts:24-32 — 定义 chat 文件类型：扩展名 `.chat`，MIME 类型 `text/json`/`application/json`，contentType 为 `'chat'`，fileFormat 为 `'text'`。
- F-058: packages/jupyterlab-chat/src/token.ts:37-39 — `IChatFactory` Token 标识为 `jupyterlab-chat:IChatFactory`。
- F-059: packages/jupyterlab-chat/src/token.ts:53-55 — `IChatToolbarFactory` Token 用于共享工具栏工厂（主区和侧边栏共享注册）。
- F-060: packages/jupyterlab-chat/src/token.ts:98-131 — 定义命令 ID：createChat、openChat、createAndOpen、moveChat、markAsRead、focusInput、renameChat、openWithMessage。
- F-061: packages/jupyterlab-chat/src/token.ts:136-138 — `IMultiChatPanel` Token 标识多聊天面板。
- F-062: packages/jupyterlab-chat/src/token.ts:159-161 — `IWelcomeMessage` Token 允许第三方扩展提供欢迎消息字符串。

## YChat 共享文档模型（前端）

- F-063: packages/jupyterlab-chat/src/ychat.ts:14 — `IYmessage` 类型为 `IMessageContent<string, string>`，sender 和 attachments 序列化为字符串。
- F-064: packages/jupyterlab-chat/src/ychat.ts:24-45 — `IChatChanges` 接口扩展 DocumentChange，包含 messageListChanges(Delta)、messageChanges、userChanges、attachmentChanges、metadataChanges。
- F-065: packages/jupyterlab-chat/src/ychat.ts:75 — `YChat` 类继承 `YDocument<IChatChanges>`。
- F-066: packages/jupyterlab-chat/src/ychat.ts:81-91 — 构造函数初始化四个 Yjs 共享类型：users(Y.Map)、messages(Y.Array)、attachments(Y.Map)、metadata(Y.Map)，并分别注册 observe 回调。
- F-067: packages/jupyterlab-chat/src/ychat.ts:97 — document version 为 `'1.0.0'`。
- F-068: packages/jupyterlab-chat/src/ychat.ts:108-118 — id 属性存储在 metadata map 中，setter 使用 transact 确保只设置一次。

## Python 后端：YChat 模型

- F-069: python/jupyterlab-chat/jupyterlab_chat/ychat.py:37 — `WRITERS_AWARENESS_KEY = "writers"`，在 Awareness 中发布正在写作的用户列表（服务端 AI persona 无独立 awareness 客户端，统一发布在文档 awareness 槽位）。
- F-070: python/jupyterlab-chat/jupyterlab_chat/ychat.py:40 — Python 端 `YChat` 类继承 `YBaseDoc` 和 `BaseChatModel`。
- F-071: python/jupyterlab-chat/jupyterlab_chat/ychat.py:51-54 — 初始化四个 pycrdt 共享类型：users(Map)、messages(Array)、attachments(Map)、metadata(Map)。
- F-072: python/jupyterlab-chat/jupyterlab_chat/ychat.py:65 — 维护 `_indexes_by_id: dict[str, int]` 查找表，通过消息 ID 快速定位数组索引。
- F-073: python/jupyterlab-chat/jupyterlab_chat/ychat.py:69 — `_writers: dict[str, dict]` 内存字典存储正在写作的用户。

## Python 后端：数据模型

- F-074: python/jupyterlab-chat/jupyterlab_chat/models.py:17-28 — `MimeModel` 数据类包含 data(dict)、metadata(dict)、trusted(bool) 字段。
- F-075: python/jupyterlab-chat/jupyterlab_chat/models.py:31-81 — `Message` 数据类（kw_only）包含 body、id、time、sender（必填），type(默认"msg")、attachments、mentions、raw_time、deleted、edited、metadata、mime_model（可选）。
- F-076: python/jupyterlab-chat/jupyterlab_chat/models.py:84-98 — `NewMessage` 数据类包含 body、sender、mime_model。
- F-077: python/jupyterlab-chat/jupyterlab_chat/models.py:101-115 — `User` 类继承 JupyterUser，增加 bot 字段（默认 False），mention_name 属性计算规则为 display_name/name/username 中空格替换为 `-`。

## Python 后端：ChatManager

- F-078: python/jupyterlab-chat/jupyterlab_chat/chat_manager.py:46 — `ChatManager` 类继承 LoggingConfigurable，负责聊天生命周期管理。
- F-079: python/jupyterlab-chat/jupyterlab_chat/chat_manager.py:50-56 — 三大职责：事件总线（observe_chats/发射 opened|closed|deleted 事件）、模型访问（get/create）、内存管理（inactivity_timeout_s 后释放）。
- F-080: python/jupyterlab-chat/jupyterlab_chat/chat_manager.py:59-61 — inactivity_timeout_s 配置默认 300 秒（5 分钟），无连接客户端后释放聊天模型。
- F-081: python/jupyterlab-chat/jupyterlab_chat/chat_manager.py:62-64 — poll_interval_s 配置默认 60 秒，轮询检查不活跃/已删除的聊天。
- F-082: python/jupyterlab-chat/jupyterlab_chat/chat_manager.py:76-77 — `_chats_by_id` 和 `_last_activity_by_id` 使用稳定的 chat_id 作为 key（路径可变，room_id 仅 RTC 使用）。
- F-083: python/jupyterlab-chat/jupyterlab_chat/chat_manager.py:81 — 将 `_chats_by_id` 字典暴露到 settings["chats_by_id"]，供服务端消费者（如 jupyter-ai-router）访问。
- F-084: python/jupyterlab-chat/jupyterlab_chat/chat_manager.py:84-85 — rtc_enabled 为 true 时通过 `_wire_rtc_forwarding()` 将 collaboration 房间事件转发为通用 ChatEvent。
- F-085: python/jupyterlab-chat/jupyterlab_chat/chat_manager.py:87-89 — 使用 tornado 的 PeriodicCallback 实现定时轮询。

## 扩展插件

- F-086: packages/jupyterlab-chat-extension/ — 扩展插件包，包含 schema/commands.json、schema/factory.json、schema/toolbar-factory.json 配置文件。
- F-087: packages/jupyterlab-chat-extension/src/chat-commands/providers/emoji.ts — 提供 emoji 自动补全命令提供者。
- F-088: packages/jupyterlab-chat-extension/src/chat-commands/providers/user-mention.tsx — 提供 @用户提及 自动补全命令提供者。
