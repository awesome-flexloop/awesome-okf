---
type: Example
title: Bot 集成示例
description: 使用消息观察者模式实现聊天机器人，包括自动回复、斜杠命令和 AI 响应
tags: [example, bot, integration, observer, advanced]
sources:
  - id: models-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/models.py
    title: models.py
  - id: ychat-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/ychat.py
    title: ychat.py
  - id: chat-manager-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/chat_manager.py
    title: chat_manager.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# Bot 集成示例

本示例演示如何通过 Python 后端的消息观察者模式实现聊天机器人。

## 基本概念

Bot 通过 `model.observe_messages(callback)` 注册消息回调，在收到消息时执行自定义逻辑（如自动回复、命令处理、AI 推理）。

关键 API：

```python
# 注册观察者，返回 MessageObserver 句柄
observer = model.observe_messages(callback)

# 注销观察者
model.unobserve_messages(observer)

# 发送回复
model.add_message(NewMessage(body="回复内容", sender="bot-name"))

# 广播"正在输入"状态
model.broadcast_writing_status(bot_user, {"typingIndicator": "正在思考..."})
```

## 示例 1：简单 Echo Bot

```python
from jupyterlab_chat.models import (
    NewMessage, User, ChatMessageEvent, ChatMessageAction,
    MessageObserverCallback
)

# Bot 用户身份
BOT_USER = User(
    username="echo-bot",
    name="Echo Bot",
    display_name="Echo Bot",
    bot=True  # 标记为机器人
)

def echo_bot_callback(event: ChatMessageEvent):
    """简单的回声机器人"""
    # 只响应客户端新消息（避免响应自己的消息造成循环）
    if event.action != ChatMessageAction.CLIENT_MSG_RECEIVED:
        return

    message = event.message

    # 忽略自己发的消息
    if message.sender == BOT_USER.username:
        return

    # 简单回声
    reply = NewMessage(
        body=f"Echo: {message.body}",
        sender=BOT_USER.username
    )
    # 注意：需要通过 model 发送，此处 model 通过闭包或类获取
    # model.add_message(reply)
```

## 示例 2：斜杠命令 Bot

```python
import re
from jupyterlab_chat.models import NewMessage, User, ChatMessageEvent, ChatMessageAction

BOT_USER = User(username="cmd-bot", name="Command Bot", display_name="Cmd Bot", bot=True)

class CommandBot:
    """支持斜杠命令的机器人"""

    def __init__(self):
        self._observer = None
        self._model = None

    def attach(self, model):
        """将 bot 附加到聊天模型"""
        self._model = model
        # 注册 bot 用户
        model.set_user(BOT_USER)
        # 注册消息观察者
        self._observer = model.observe_messages(self._on_message)

    def detach(self):
        """从模型分离"""
        if self._observer and self._model:
            self._model.unobserve_messages(self._observer)
            self._observer = None
            self._model = None

    def _on_message(self, event: ChatMessageEvent):
        if event.action != ChatMessageAction.CLIENT_MSG_RECEIVED:
            return

        msg = event.message
        if msg.sender == BOT_USER.username:
            return

        body = msg.body.strip()

        # 处理斜杠命令
        if body.startswith('/'):
            self._handle_command(body, msg.sender)
        elif body.startswith('@Cmd Bot') or body.startswith('@cmd-bot'):
            # @提及 bot 时回复
            self._handle_mention(body)

    def _handle_command(self, body: str, sender: str):
        """处理斜杠命令"""
        parts = body.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        commands = {
            '/help': self._cmd_help,
            '/echo': self._cmd_echo,
            '/time': self._cmd_time,
            '/clear': self._cmd_clear,
        }

        handler = commands.get(cmd)
        if handler:
            reply_body = handler(args, sender)
        else:
            reply_body = f"未知命令: {cmd}\n输入 /help 查看可用命令"

        self._reply(reply_body)

    def _cmd_help(self, args: str, sender: str) -> str:
        return """可用命令:
- `/help` - 显示帮助
- `/echo <text>` - 回声消息
- `/time` - 显示当前时间
- `/clear` - 清空聊天记录（仅清除本地）"""

    def _cmd_echo(self, args: str, sender: str) -> str:
        return args if args else "你想说什么？"

    def _cmd_time(self, args: str, sender: str) -> str:
        from datetime import datetime
        return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    def _cmd_clear(self, args: str, sender: str) -> str:
        # 注意：clearMessages 需要前端权限，后端只能发消息告知
        return "请在 UI 中使用清空功能"

    def _handle_mention(self, body: str):
        """处理 @提及"""
        # 移除 @mention 部分
        clean_body = re.sub(r'@\S+\s*', '', body).strip()
        self._reply(f"收到你的消息: {clean_body}")

    def _reply(self, body: str):
        """发送回复"""
        if self._model:
            self._model.add_message(
                NewMessage(body=body, sender=BOT_USER.username)
            )
```

## 示例 3：异步 AI Bot（带"正在输入"状态）

```python
import asyncio
from jupyterlab_chat.models import (
    NewMessage, User, ChatMessageEvent, ChatMessageAction
)

BOT_USER = User(
    username="ai-assistant",
    name="AI Assistant",
    display_name="AI Assistant",
    bot=True
)

class AIBot:
    """模拟 AI 助手，带"正在输入"状态"""

    def __init__(self):
        self._model = None
        self._observer = None
        self._model_set_user(BOT_USER)

    def attach(self, model):
        self._model = model
        model.set_user(BOT_USER)
        self._observer = model.observe_messages(self._on_message)

    def detach(self):
        if self._observer and self._model:
            self._model.unobserve_messages(self._observer)

    def _on_message(self, event: ChatMessageEvent):
        if event.action != ChatMessageAction.CLIENT_MSG_RECEIVED:
            return

        msg = event.message
        if msg.sender == BOT_USER.username:
            return
        if msg.body.startswith('/'):
            return  # 不处理命令

        # 创建异步任务处理
        asyncio.create_task(self._async_reply(msg))

    async def _async_reply(self, msg):
        """异步回复，带 typing indicator"""
        model = self._model
        if not model:
            return

        try:
            # 1. 广播"正在思考"状态
            model.broadcast_writing_status(
                BOT_USER,
                {"typingIndicator": "正在思考..."}
            )

            # 2. 模拟 AI 推理延迟（实际中替换为 LLM 调用）
            await asyncio.sleep(2)

            # 3. 更新 typing 状态
            model.broadcast_writing_status(
                BOT_USER,
                {"typingIndicator": "正在生成回复..."}
            )

            # 4. 生成回复
            reply_body = await self._generate_reply(msg.body)

            # 5. 发送回复（自动清除 writing 状态）
            model.add_message(
                NewMessage(
                    body=reply_body,
                    sender=BOT_USER.username,
                    mime_model=None  # 可设置富内容
                )
            )

        finally:
            # 6. 清除 writing 状态
            model.broadcast_writing_status(BOT_USER, None)

    async def _generate_reply(self, prompt: str) -> str:
        """生成 AI 回复（示例）"""
        # 实际实现中调用 LLM API
        await asyncio.sleep(1)
        return f"关于「{prompt}」，这是我的回复..."
```

## 示例 4：在 Chat 打开时自动注册 Bot

通过监听 Chat 生命周期事件，在新 chat 打开时自动附加 bot：

```python
from jupyterlab_chat.events import CHAT_ROOM_EVENT_SCHEMA_ID, ChatEventAction

class BotManager:
    """管理多个 chat 中的 bot 实例"""

    def __init__(self, chat_manager):
        self._chat_manager = chat_manager
        self._bots: dict[str, CommandBot] = {}  # chat_id -> bot

    async def start(self):
        """启动监听"""
        event_logger = self._chat_manager.event_logger
        event_logger.add_listener(
            schema_id=CHAT_ROOM_EVENT_SCHEMA_ID,
            listener=self._on_chat_event
        )

    async def _on_chat_event(self, logger, schema_id: str, data: dict):
        action = data.get("action")
        chat_id = data.get("chat_id")
        path = data.get("path")

        if action == ChatEventAction.OPENED.value:
            # Chat 打开时创建 bot
            model = self._chat_manager.get_chat(chat_id)
            if model:
                bot = CommandBot()
                bot.attach(model)
                self._bots[chat_id] = bot
                # 发送欢迎消息
                model.add_message(NewMessage(
                    body="你好！我是 Cmd Bot。输入 `/help` 查看可用命令。",
                    sender="cmd-bot"
                ))

        elif action == ChatEventAction.CLOSED.value:
            # Chat 关闭时清理 bot
            bot = self._bots.pop(chat_id, None)
            if bot:
                bot.detach()
```

## 示例 5：WebSocket 模式下的 Bot

WebSocket 模式下，Bot 使用 WsChatModel 的相同接口（BaseChatModel 统一接口保证一致）：

```python
# WsChatModel 和 YChat 都实现 BaseChatModel
# Bot 代码无需修改即可在两种模式下工作

def create_bot_for_ws_chat(ws_model):
    """为 WebSocket 模式的 chat 创建 bot"""
    bot = CommandBot()
    bot.attach(ws_model)  # 接口完全相同
    return bot
```

在 WSChatHandler 中集成：

```python
# 可在自定义 WSChatHandler 子类中
def open(self, *args, **kwargs):
    super().open(*args, **kwargs)
    # 连接建立后创建 bot
    self._bot = CommandBot()
    self._bot.attach(self._model)
```

## 注意事项

1. **避免消息循环**：始终检查 `message.sender`，忽略 bot 自己发送的消息
2. **异步处理**：长时间操作（如 AI 调用）应使用异步，避免阻塞消息处理
3. **清理资源**：在 chat 关闭时调用 `unobserve_messages()` 移除观察者
4. **bot 用户标记**：设置 `user.bot = True`，前端可据此显示机器人图标和不同样式
5. **writing 状态**：长时间操作前广播 writing 状态，完成后清除（传 `None`）
6. **错误处理**：观察者回调中的异常会被捕获并记录日志，但建议自行 try-except 处理
7. **双模式兼容**：使用 BaseChatModel 接口，确保 bot 在 RTC 和 WebSocket 模式下都能工作

## 相关概念

- [生命周期事件](../concepts/lifecycle-events.md)
- [消息生命周期](../concepts/message-lifecycle.md)
- [双传输架构](../concepts/dual-transport.md)
- [ChatManager 生命周期管理](../concepts/chat-manager.md)
- [Python 后端 API 参考](../references/api-python.md)
