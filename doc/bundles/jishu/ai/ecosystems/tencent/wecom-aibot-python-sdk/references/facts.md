---
type: reference
title: wecom-aibot-python-sdk 源码事实登记（R 阶段）
description: 企业微信智能机器人 Python SDK 固定基线的零推测源码事实，F-001 起共 59 条
tags: [wecom, aibot, python-sdk, websocket, facts]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
phase: R（事实采集）
baseline: 6bcb59a9a636c566f4c6ea5268b228e3def1611a（pyproject 1.0.1）
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
---

# wecom-aibot-python-sdk 源码事实登记

基线标注：本页证据统一取自 `vendor/WecomTeam/wecom-aibot-python-sdk/` 在 commit `6bcb59a9a636c566f4c6ea5268b228e3def1611a` 的工作树，许可证为 MIT，受控文件（排除 `.git` 目录）共 19 个。全部证据行号由逐文件通读与 `grep -n` 实测取得，路径为相对仓库根的正斜杠形式。本页不含推断性表述，仅登记取值、位置、签名与默认值。版本双口径：打包元数据为 `1.0.1`，运行期 `__version__` 为 `1.0.0`，两处并列登记于 F-002 与 F-008、F-009。

## 一、包元数据

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-001 | `pyproject.toml` 的 `[project]` 段 `name` 取值为 `wecom-aibot-python-sdk`。 | pyproject.toml:6 | `grep -n '^name' pyproject.toml` |
| F-002 | `[project]` 段 `version` 取值为 `1.0.1`。 | pyproject.toml:7 | `grep -n '^version' pyproject.toml` |
| F-003 | `requires-python` 取值为 `>=3.8`；`classifiers` 列 `Programming Language :: Python :: 3.8` 至 `3.13` 共六条，另有 `Development Status :: 4 - Beta`。 | pyproject.toml:11,16-28 | `grep -n 'requires-python\|Programming Language :: Python\|Development Status' pyproject.toml` |
| F-004 | `[build-system]` 段 `requires = ["setuptools>=61.0", "wheel"]`，`build-backend = "setuptools.build_meta"`；`[project]` 段 `license = "MIT"`。 | pyproject.toml:1-3,10 | `grep -n 'build-backend\|requires = \["setuptools\|^license' pyproject.toml` |
| F-005 | `LICENSE` 第 1 行为 `MIT License`，第 3 行为 `Copyright (c) 2026 WeCom`。 | LICENSE:1-3 | `head -3 LICENSE` |
| F-006 | `dependencies` 五项及版本下限：`websockets>=12.0`、`aiohttp>=3.9`、`pyee>=11.0`、`cryptography>=42.0`、`certifi>=2023.0`。 | pyproject.toml:30-36 | `sed -n '30,36p' pyproject.toml` |
| F-007 | `[project.optional-dependencies]` 仅 `dev` 一组，内容为 `python-dotenv>=1.0`。 | pyproject.toml:38-41 | `sed -n '38,41p' pyproject.toml` |
| F-008 | `aibot/__init__.py` 的 `__version__` 取值为 `"1.0.0"`。 | aibot/__init__.py:7 | `grep -n '__version__' aibot/__init__.py` |
| F-009 | 版本双口径并置：`pyproject.toml` 第 7 行为 `1.0.1`，`aibot/__init__.py` 第 7 行为 `1.0.0`，两处字符串不相等；`examples/comparison_test.py` 第 441 行的启动日志同样写 `version: "1.0.0"`。 | pyproject.toml:7；aibot/__init__.py:7；examples/comparison_test.py:441 | `grep -rn '1\.0\.' pyproject.toml aibot/__init__.py examples/comparison_test.py` |
| F-010 | `[tool.setuptools.packages.find]` 段 `include = ["aibot*"]`；`authors` 为 `{name = "WeCom", email = "wecom@tencent.com"}`；`[project.urls]` 的 `Homepage` 与 `Repository` 同为 `https://github.com/WecomTeam/wecom-aibot-python-sdk`。 | pyproject.toml:12-14,43-48 | `sed -n '12,14p;43,48p' pyproject.toml` |
| F-011 | `requirements.txt` 共 6 行，前 5 行与 `pyproject.toml` 的 `dependencies` 同项同下限，第 6 行为 `python-dotenv>=1.0`；`MANIFEST.in` 共 6 行，为 5 条 `include`（`README.md`、`LICENSE`、`requirements.txt`、`COMPARISON.md`、`.env.example`）加 1 条 `recursive-include examples *.py`。 | requirements.txt:1-6；MANIFEST.in:1-6 | `cat -n requirements.txt MANIFEST.in` |

## 二、公开 API 面

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-012 | `aibot/__init__.py` 的 `__all__` 列表共 17 个字符串元素。 | aibot/__init__.py:27-50 | `sed -n '27,50p' aibot/__init__.py` |
| F-013 | `__all__` 逐项为：`__version__`、`WSClient`、`WeComApiClient`、`WsConnectionManager`、`MessageHandler`、`DefaultLogger`、`decrypt_file`、`generate_req_id`、`generate_random_string`、`MessageType`、`EventType`、`TemplateCardType`、`WsCmd`、`WSClientOptions`、`WsFrame`、`WsFrameHeaders`、`Logger`；列表内注释分组为「版本 / 类 / 函数 / 枚举、常量 / 类型」。 | aibot/__init__.py:27-50 | `sed -n '27,50p' aibot/__init__.py` |
| F-014 | `WSClient` 的类声明为 `class WSClient(AsyncIOEventEmitter)`，父类来自 `pyee.asyncio`。 | aibot/client.py:11,22 | `grep -n 'AsyncIOEventEmitter\|class WSClient' aibot/client.py` |
| F-015 | `WsFrame` 与 `WsFrameHeaders` 均为类型别名而非类：`WsFrame = Dict[str, Any]`、`WsFrameHeaders = Dict[str, Any]`。 | aibot/types.py:166-170 | `sed -n '166,170p' aibot/types.py` |
| F-016 | `Logger` 为 `@runtime_checkable` 修饰的 `Protocol`，含 `debug`、`info`、`warn`、`error` 四个方法，签名均为 `(self, message: str, *args: Any) -> None`。 | aibot/types.py:20-27 | `sed -n '20,27p' aibot/types.py` |
| F-017 | `DefaultLogger.__init__` 的参数为 `prefix: str = "AiBotSDK"`；四个日志方法均调用 `print(..., file=sys.stderr)`，输出前缀形如 `[{时间}] [{prefix}] [DEBUG]`，时间取 `datetime.now(timezone.utc).isoformat()`。 | aibot/logger.py:15-46 | `sed -n '15,46p' aibot/logger.py` |
| F-018 | `WeComApiClient.__init__` 签名为 `(self, logger: Any, timeout: int = 10000)`；`MessageHandler.__init__` 签名为 `(self, logger: Any)`，其方法为 `handle_frame(self, frame: WsFrame, emitter: Any) -> None`。 | aibot/api.py:26；aibot/message_handler.py:21,24 | `grep -n 'def __init__\|def handle_frame' aibot/api.py aibot/message_handler.py` |

## 三、连接生命周期

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-019 | 模块级常量 `DEFAULT_WS_URL = "wss://openws.work.weixin.qq.com"`；`WsConnectionManager.__init__` 以 `ws_url or DEFAULT_WS_URL` 赋给 `self._ws_url`。 | aibot/ws.py:24,73 | `grep -n 'DEFAULT_WS_URL' aibot/ws.py` |
| F-020 | `connect()` 先 `await self._cleanup_ws()`，再调用 `websockets.connect(self._ws_url, ssl=_SSL_CONTEXT, ping_interval=None, ping_timeout=None, close_timeout=5)`；成功后把 `_reconnect_attempts` 与 `_missed_pong_count` 都置 0，随后依次调用 `on_connected()`、`_send_auth()`、`asyncio.ensure_future(self._receive_loop())`。 | aibot/ws.py:116-153 | `sed -n '116,153p' aibot/ws.py` |
| F-021 | `_SSL_CONTEXT` 在 `try` 分支取 `ssl.create_default_context(cafile=certifi.where())`，`ImportError` 分支回退 `ssl.create_default_context()`；`ws.py` 与 `api.py` 各有一份同构定义。 | aibot/ws.py:13-18；aibot/api.py:15-20 | `sed -n '13,20p' aibot/ws.py` |
| F-022 | `_send_auth()` 发送帧为 `{"cmd": WsCmd.SUBSCRIBE, "headers": {"req_id": generate_req_id(WsCmd.SUBSCRIBE)}, "body": {"bot_id": self._bot_id, "secret": self._bot_secret}}`；`WsCmd.SUBSCRIBE` 的字符串取值为 `aibot_subscribe`。 | aibot/ws.py:172-184；aibot/types.py:69 | `sed -n '172,184p' aibot/ws.py` |
| F-023 | `_receive_loop()` 以 `async for raw_message in self._ws` 读取，`bytes` 先 `decode("utf-8")`，再 `json.loads` 得到 `frame` 并调 `_handle_frame(frame)`；`ConnectionClosed` 分支依次调 `_stop_heartbeat()`、`_clear_pending_messages(...)`、`on_disconnected(reason)`，且 `_is_manual_close` 为 False 时调 `_schedule_reconnect()`。 | aibot/ws.py:189-214 | `sed -n '189,214p' aibot/ws.py` |
| F-024 | `_handle_frame` 中 `req_id` 以 `WsCmd.SUBSCRIBE` 开头时进入认证响应分支：`errcode != 0` 则调 `on_error`，否则调 `_start_heartbeat()` 并调 `on_authenticated()`；`req_id` 以 `WsCmd.HEARTBEAT` 开头时，`errcode != 0` 记 `warn` 后返回，否则把 `_missed_pong_count` 置 0。 | aibot/ws.py:243-273 | `sed -n '243,273p' aibot/ws.py` |
| F-025 | 心跳与重连的三个默认值：`_max_missed_pong = 2`、`_reconnect_max_delay = 30000`、`_heartbeat_interval` 由构造参数 `heartbeat_interval: int = 30000` 传入；`_heartbeat_loop` 每轮 `await asyncio.sleep(self._heartbeat_interval / 1000)`。 | aibot/ws.py:67,74,90-91,295-302 | `grep -n '_max_missed_pong\|_reconnect_max_delay\|heartbeat_interval' aibot/ws.py` |
| F-026 | `_send_heartbeat()` 的判死条件为 `self._missed_pong_count >= self._max_missed_pong`，命中时记 `warn`、调 `_stop_heartbeat()`、对 `self._ws` 调 `close()` 后返回；未命中时先 `self._missed_pong_count += 1`，再发送 `{"cmd": WsCmd.HEARTBEAT, "headers": {"req_id": generate_req_id(WsCmd.HEARTBEAT)}}`。 | aibot/ws.py:304-334 | `sed -n '304,334p' aibot/ws.py` |
| F-027 | `_schedule_reconnect()` 的上限判定为 `self._max_reconnect_attempts != -1 and self._reconnect_attempts >= self._max_reconnect_attempts`，命中时调 `on_error(Exception("Max reconnect attempts exceeded"))` 并返回；`max_reconnect_attempts` 的 docstring 写「最大重连次数，默认 10，设为 -1 表示无限重连」；退避公式为 `delay = min(self._reconnect_base_delay * (2 ** (self._reconnect_attempts - 1)), self._reconnect_max_delay)`，代码注释为「指数退避：1s, 2s, 4s, 8s … 上限 30s」。 | aibot/ws.py:338-364；aibot/types.py:46-47 | `sed -n '338,364p' aibot/ws.py` |
| F-028 | `disconnect()` 置 `_is_manual_close = True`、调 `_stop_heartbeat()` 与 `_clear_pending_messages("Connection manually closed")` 并安排 `_async_disconnect()`；`_async_disconnect()` 对连接调 `close(code=1000, reason="Manual disconnect")`；`is_connected` 返回 `self._ws is not None and _ws_is_open(self._ws)`；`_ws_is_open` 对有 `open` 属性的连接（注释写 `websockets <= 13.x`）取 `ws.open`，对 `state` 的取 `ws.state is State.OPEN`（注释写 `websockets >= 14.x`）。 | aibot/ws.py:30-42,544-574 | `sed -n '544,574p' aibot/ws.py` |

## 四、帧协议

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-029 | 帧注释声明的字段为 `cmd?: str`、`headers: dict`（内含 `req_id: str`）、`body?: Any`、`errcode?: int`、`errmsg?: str`；`WsFrame` 与 `WsFrameHeaders` 均为 `Dict[str, Any]` 别名。 | aibot/types.py:155-170 | `sed -n '155,170p' aibot/types.py` |
| F-030 | 「开发者 → 企业微信」六个 `WsCmd` 常量及取值：`SUBSCRIBE = "aibot_subscribe"`、`HEARTBEAT = "ping"`、`RESPONSE = "aibot_respond_msg"`、`RESPONSE_WELCOME = "aibot_respond_welcome_msg"`、`RESPONSE_UPDATE = "aibot_respond_update_msg"`、`SEND_MSG = "aibot_send_msg"`。 | aibot/types.py:68-85 | `sed -n '68,85p' aibot/types.py` |
| F-031 | 「企业微信 → 开发者」两个 `WsCmd` 常量及取值：`CALLBACK = "aibot_msg_callback"`、`EVENT_CALLBACK = "aibot_event_callback"`。 | aibot/types.py:87-92 | `sed -n '87,92p' aibot/types.py` |
| F-032 | `generate_req_id(prefix)` 返回 `f"{prefix}_{timestamp}_{random_str}"`，`timestamp = int(time.time() * 1000)`（毫秒），`random_str` 取默认 8 位；`generate_random_string(length: int = 8)` 返回 `os.urandom((length + 1) // 2).hex()[:length]`。 | aibot/utils.py:11-32 | `cat -n aibot/utils.py` |
| F-033 | `MessageType(str, Enum)` 五个成员：`Text = "text"`、`Image = "image"`、`Mixed = "mixed"`、`Voice = "voice"`、`File = "file"`。 | aibot/types.py:98-114 | `sed -n '98,114p' aibot/types.py` |
| F-034 | `EventType(str, Enum)` 三个成员：`EnterChat = "enter_chat"`、`TemplateCardEvent = "template_card_event"`、`FeedbackEvent = "feedback_event"`。 | aibot/types.py:120-130 | `sed -n '120,130p' aibot/types.py` |
| F-035 | `TemplateCardType(str, Enum)` 五个成员：`TextNotice = "text_notice"`、`NewsNotice = "news_notice"`、`ButtonInteraction = "button_interaction"`、`VoteInteraction = "vote_interaction"`、`MultipleInteraction = "multiple_interaction"`。 | aibot/types.py:136-152 | `sed -n '136,152p' aibot/types.py` |

## 五、流式回复

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-036 | `reply_stream` 签名为 `(self, frame: WsFrameHeaders, stream_id: str, content: str, finish: bool = False, msg_item: Optional[List[Dict[str, Any]]] = None, feedback: Optional[Dict[str, Any]] = None) -> WsFrame`。 | aibot/client.py:129-137 | `sed -n '129,137p' aibot/client.py` |
| F-037 | `reply_stream` 先构造 `stream = {"id": stream_id, "finish": finish, "content": content}`；仅当 `finish and msg_item and len(msg_item) > 0` 时写入 `stream["msg_item"]`；仅当 `feedback` 为真时写入 `stream["feedback"]`。 | aibot/client.py:149-161 | `sed -n '149,161p' aibot/client.py` |
| F-038 | `reply_stream` 的请求体为 `{"msgtype": "stream", "stream": stream}`，经 `self.reply(frame, body)` 发送。 | aibot/client.py:163-169 | `sed -n '163,169p' aibot/client.py` |
| F-039 | `reply()` 从 `frame.get("headers", {})` 取 `req_id = headers.get("req_id", "")`，调 `self._ws_manager.send_reply(req_id, body, cmd or WsCmd.RESPONSE)`；`send_reply` 组帧为 `{"cmd": cmd, "headers": {"req_id": req_id}, "body": body}`。 | aibot/client.py:125-127；aibot/ws.py:398-402 | `sed -n '125,127p' aibot/client.py; sed -n '398,402p' aibot/ws.py` |
| F-040 | 串行队列上限 `_max_reply_queue_size = 100`；`send_reply` 在 `len(queue) >= self._max_reply_queue_size` 时记 `warn` 并对该 future 调 `set_exception(RuntimeError(...))`，不再入队。 | aibot/ws.py:100,412-422 | `sed -n '412,422p' aibot/ws.py` |
| F-041 | 回执超时值 `_reply_ack_timeout = 5.0`（单位为秒，行内注释写 `# 秒`）；每发一条回复即用 `loop.call_later(self._reply_ack_timeout, self._on_reply_ack_timeout, req_id, ack_future)` 登记定时器并写入 `self._pending_acks[req_id]`；超时回调对 future 调 `set_exception(TimeoutError(...))`。 | aibot/ws.py:99,458-469,484-497 | `grep -n '_reply_ack_timeout' aibot/ws.py` |
| F-042 | `_process_reply_queue(req_id)` 对同一 `req_id` 逐条取 `queue[0]`、`await self.send(item.frame)`、再 `await ack_future`，成功收到回执后 `queue.pop(0)` 并 `set_result(ack_frame)`；发送异常或回执异常时同样 `pop(0)` 并 `set_exception`；结束处 `self._processing_queues.discard(req_id)`。 | aibot/ws.py:432-482 | `sed -n '432,482p' aibot/ws.py` |
| F-043 | 回执 `errcode != 0` 时 `_handle_reply_ack` 对 future 调 `set_exception(RuntimeError(f"Reply ack error: errcode=..."))`，否则 `set_result(frame)`；`reply_welcome` 以 `WsCmd.RESPONSE_WELCOME` 调 `reply`，docstring 写「收到事件回调后需在 5 秒内发送回复，超时将无法发送欢迎语」；`send_message` 以 `generate_req_id(WsCmd.SEND_MSG)` 生成 req_id，请求体为 `{"chatid": chatid, **body}`，cmd 为 `WsCmd.SEND_MSG`。 | aibot/ws.py:499-525；aibot/client.py:171-186,286-302 | `sed -n '499,525p' aibot/ws.py; sed -n '171,186p;286,302p' aibot/client.py` |

## 六、模板卡片

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-044 | `reply_template_card` 签名为 `(self, frame, template_card, feedback=None)`；`feedback` 为真时卡片取 `{**template_card, "feedback": feedback}`，请求体为 `{"msgtype": "template_card", "template_card": card}`，cmd 取默认 `WsCmd.RESPONSE`。 | aibot/client.py:188-207 | `sed -n '188,207p' aibot/client.py` |
| F-045 | `reply_stream_with_card` 的请求体 `msgtype` 取值为 `"stream_with_template_card"`，`stream` 字段组装规则与 `reply_stream` 相同；`template_card` 为真时写入 `body["template_card"]`，`card_feedback` 为真时先合并为 `{**template_card, "feedback": card_feedback}`。 | aibot/client.py:209-258 | `sed -n '209,258p' aibot/client.py` |
| F-046 | `update_template_card(frame, template_card, userids=None)` 的请求体为 `{"response_type": "update_template_card", "template_card": template_card}`，`userids` 非空时追加同名字段，cmd 取 `WsCmd.RESPONSE_UPDATE`（值 `aibot_respond_update_msg`）；docstring 写「此方法需要使用对应事件（template_card_event）的 req_id 才能调用」。 | aibot/client.py:260-284；aibot/types.py:81 | `sed -n '260,284p' aibot/client.py` |

## 七、事件回调

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-047 | `MessageHandler.handle_frame` 先取 `body = frame.get("body")`，`body` 为空或无 `body["msgtype"]` 时记 `warn` 并返回；否则 `frame.get("cmd") == WsCmd.EVENT_CALLBACK` 时调 `_handle_event_callback` 并返回，其余情况调 `_handle_message_callback`。 | aibot/message_handler.py:24-48 | `sed -n '24,48p' aibot/message_handler.py` |
| F-048 | `_handle_event_callback` 先 `emitter.emit("event", frame)`，再取 `event = body.get("event", {})` 与 `event_type = event.get("eventtype")`（仅当 `event` 为 dict），`event_type` 非空时 `emitter.emit(f"event.{event_type}", frame)`，为空时记 `debug`。 | aibot/message_handler.py:73-89 | `sed -n '73,89p' aibot/message_handler.py` |
| F-049 | `_handle_message_callback` 先 `emitter.emit("message", frame)`，再按 `body["msgtype"]` 分发到 `message.text`、`message.image`、`message.mixed`、`message.voice`、`message.file` 五个事件名，未命中时记 `debug`。 | aibot/message_handler.py:50-71 | `sed -n '50,71p' aibot/message_handler.py` |

## 八、文件下载与解密

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-050 | `WSClient.download_file(url, aes_key=None) -> Tuple[bytes, Optional[str]]` 先调 `self._api_client.download_file_raw(url)` 取得 `(encrypted_data, filename)`；`aes_key` 为假值时记 `warn` 并原样返回 `(encrypted_data, filename)`；否则调 `decrypt_file(encrypted_data, aes_key)` 后返回 `(decrypted_data, filename)`。 | aibot/client.py:304-333 | `sed -n '304,333p' aibot/client.py` |
| F-051 | `WeComApiClient.download_file_raw` 建 `aiohttp.TCPConnector(ssl=_SSL_CONTEXT)`，以 `aiohttp.ClientSession(timeout=self._timeout, connector=connector)` 调 `session.get(url)`，随后 `response.raise_for_status()`、`await response.read()`；`__init__` 中 `self._timeout = aiohttp.ClientTimeout(total=timeout / 1000)`，`timeout` 默认 10000。 | aibot/api.py:26-44 | `sed -n '26,44p' aibot/api.py` |
| F-052 | 文件名解析读 `response.headers.get("Content-Disposition", "")`：先按 `r"filename\*=UTF-8''([^;\s]+)"` 匹配（注释写 RFC 5987），未命中再按 `r'filename="?([^";\s]+)"?'` 匹配；两处命中值都经 `unquote` 还原，未命中时 `filename` 保持 `None`。 | aibot/api.py:46-70 | `sed -n '46,70p' aibot/api.py` |
| F-053 | `decrypt_file(encrypted_data, aes_key)` 在 `encrypted_data` 为空时抛 `ValueError("decrypt_file: encrypted_data is empty or not provided")`，`aes_key` 非非空字符串时抛 `ValueError("decrypt_file: aes_key must be a non-empty string")`；Base64 解码前按 `aes_key + '=' * (4 - len(aes_key) % 4)` 补齐 padding，`key = base64.b64decode(...)`，`iv = key[:16]`（注释写「IV 取 aesKey 解码后的前 16 字节」），再以 `Cipher(algorithms.AES(key), modes.CBC(iv))` 解密。 | aibot/crypto_utils.py:13-40 | `sed -n '13,40p' aibot/crypto_utils.py` |
| F-054 | 解密前把数据零补齐到 16 字节块整数倍（`block_size = 16`）；解密后手写 PKCS#7 去填充：`pad_len = decrypted[-1]`，`pad_len < 1 or pad_len > 32 or pad_len > len(decrypted)` 抛 `ValueError`，逐字节比对不一致抛 `ValueError("Invalid PKCS#7 padding: padding bytes mismatch")`，全部异常在外层包装为 `RuntimeError(f"decrypt_file: Decryption failed - {e}. ...")`。 | aibot/crypto_utils.py:42-73 | `sed -n '42,73p' aibot/crypto_utils.py` |

## 九、配置与示例

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-055 | `WSClientOptions` 为 `@dataclass`，字段与默认值为：`bot_id: str`（无默认）、`secret: str`（无默认）、`reconnect_interval: int = 1000`、`max_reconnect_attempts: int = 10`、`heartbeat_interval: int = 30000`、`request_timeout: int = 10000`、`ws_url: str = ""`、`logger: Optional[Any] = None`；`ws_url` 的 docstring 写「默认 wss://openws.work.weixin.qq.com」。 | aibot/types.py:33-59 | `sed -n '33,59p' aibot/types.py` |
| F-056 | `.env.example` 定义两个变量：第 2 行 `WECHAT_BOT_ID=your-bot-id`、第 5 行 `WECHAT_BOT_SECRET=your-bot-secret`；`WSClient.__init__` 把 `options.heartbeat_interval`、`options.reconnect_interval`、`options.max_reconnect_attempts` 分别作为 `heartbeat_interval`、`reconnect_base_delay`、`max_reconnect_attempts` 传入 `WsConnectionManager`，`ws_url` 取 `self._options.ws_url or None`，并调 `set_credentials(self._options.bot_id, self._options.secret)`。 | .env.example:1-5；aibot/client.py:43-52 | `cat -n .env.example; sed -n '43,52p' aibot/client.py` |
| F-057 | `examples/basic.py` 骨架：第 22 行 `load_dotenv()`；第 27-32 行 `WSClient(WSClientOptions(bot_id=os.getenv('WECHAT_BOT_ID'), secret=os.getenv('WECHAT_BOT_SECRET')))`；第 74-96 行注册 `connected`、`authenticated`、`disconnected`、`reconnecting`、`error` 五个连接事件；第 110-126 行 `message.text` 处理器内 `generate_req_id("stream")` 后两次 `reply_stream`；第 203-212 行 `event.enter_chat` 处理器内调 `reply_welcome`。 | examples/basic.py:22,27-32,74-96,110-126,203-212 | `sed -n '22,32p;74,96p;110,126p;203,212p' examples/basic.py` |
| F-058 | `examples/comparison_test.py` 骨架：第 33-41 行 `log_event` 输出格式为 `[{timestamp}] [{category}] [{event_type}] {json}`；第 54-55 行建 `downloads` 目录；第 156-166 行文本等于「卡片」时调 `reply_template_card`；第 170-194 行等于「流式卡片」时两阶段调 `reply_stream_with_card`；第 202-213 行等于「主动发送」时调 `send_message`；第 217-261 行默认路径三阶段 `reply_stream` 并在第三阶段传 `msg_item`。 | examples/comparison_test.py:33-41,54-55,156-166,170-194,202-213,217-261 | `sed -n '33,41p;54,55p;156,166p;170,194p;202,213p;217,261p' examples/comparison_test.py` |
| F-059 | 仓库受控文件（排除 `.git` 目录）共 19 个：根目录 8 个（`.env.example`、`.gitignore`、`COMPARISON.md`、`LICENSE`、`MANIFEST.in`、`pyproject.toml`、`README.md`、`requirements.txt`）、`aibot/` 9 个、`examples/` 2 个；不含 `tests/` 目录与 `test_*.py` 文件；`.gitignore` 列有 `.pytest_cache/`、`.coverage`、`htmlcov/`、`tmp/` 四项，并忽略 `.env`、`.env.local`、`downloads/`。 | 仓库根（递归文件清单）；.gitignore:40-41,10,47-50 | `Get-ChildItem -Recurse -Force <repo> -File \| Where-Object { $_.FullName -notmatch '\\.git\\' } \| Measure-Object` |

## 统计

- 事实条数：59 条，编号 F-001 至 F-059 连续，无跳号。
- 主题节数：9 节（一、包元数据；二、公开 API 面；三、连接生命周期；四、帧协议；五、流式回复；六、模板卡片；七、事件回调；八、文件下载与解密；九、配置与示例）。
- 分节条数：一 11 条、二 7 条、三 10 条、四 7 条、五 8 条、六 3 条、七 3 条、八 5 条、九 5 条。
- 版本双口径：`pyproject.toml:7` 为 `1.0.1`，`aibot/__init__.py:7` 为 `1.0.0`。