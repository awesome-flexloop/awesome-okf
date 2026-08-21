---
okf_version: "0.2"
type: reference
title: "会话与消息协议 (session.py)"
description: "Session 类源码——消息构建/序列化/HMAC签名/收发、Message包装类、多序列化器支持（json/orjson/pickle/msgpack）"
tags: ["session", "messaging", "serialization", "hmac", "wire-protocol"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: session-py
    resource: jupyter_client/session.py
    title: jupyter_client/session.py
---

# 会话与消息协议 (session.py)

`Session` 类是 Jupyter 消息协议的核心实现，负责消息的构建、序列化、HMAC 签名和 ZMQ 收发。

```python
DELIM = b"<IDS|MSG>"  # ZMQ 多帧消息分隔符

# 序列化器选择：自动检测 orjson/msgpack 可用性
def json_packer(obj) -> bytes: ...      # 标准 json
def json_unpacker(s) -> object: ...
def orjson_packer(obj) -> bytes: ...   # orjson 加速（可选）
def orjson_unpacker(s) -> object: ...
def msgpack_packer(o) -> bytes: ...    # msgpack 二进制（可选）
def msgpack_unpacker(s) -> object: ...
def pickle_packer(o) -> bytes: ...     # pickle（不推荐跨进程）
pickle_unpacker = pickle.loads

class Message:
    """将消息字典包装为属性访问对象：msg.header.msg_type"""
    def __init__(self, msg_dict): ...  # 递归包装嵌套 dict

class Session(Configurable):
    """处理消息序列化/签名/发送的核心对象"""

    # 可配置 traitlets
    debug = Bool(False)
    check_pid = Bool(True)  # fork 安全检查
    packer = DottedObjectName("orjson" if has_orjson else "json")
    unpacker = DottedObjectName("orjson" if has_orjson else "json")
    session = CUnicode("")  # 本 session UUID
    username = Unicode(...)
    key = CBytes(...)       # HMAC 签名密钥
    signature_scheme = Unicode("hmac-sha256")
    adapt_version = Integer(0)  # 协议版本适配（0=不做适配）
    digest_history = Set()     # 防重放攻击摘要历史

    def msg(self, msg_type, content=None, parent=None, header=None, metadata=None):
        """构建标准消息字典"""
        # 返回 {header: {...}, parent_header: {...}, metadata: {...}, content: {...}, buffers: [...]}

    def send(self, stream, msg_or_type, content=None, ..., buffers=None, track=False, channel=None):
        """通过 ZMQ stream/socket 发送消息（多帧：idents → DELIM → HMAC → header → parent → metadata → content → buffers）"""

    def recv(self, socket, mode=0, content=True, copy=True):
        """从 ZMQ socket 接收并反序列化消息，验证 HMAC 签名"""

    def deserialize(self, msg, content=True, ...):
        """反序列化消息帧，返回消息字典"""

    def serialize(self, msg):
        """序列化消息为 ZMQ 多帧列表"""

    def clone(self):
        """克隆 Session（独立的 digest_history）"""
```

**关键设计点**：
- **ZMQ 多帧格式**：消息通过 `DELIM = b"<IDS|MSG>"` 分隔为 idents（路由标识）和消息体，消息体按 HMAC → header → parent_header → metadata → content → buffers 顺序排列
- **HMAC 签名**：使用 `hmac.compare_digest` 防止时序攻击；`key` 为空时不签名；`signature_scheme` 必须为 `hmac-HASH` 格式
- **序列化器自动选择**：优先使用 orjson（最快），回退到标准 json；支持 msgpack（二进制紧凑）和 pickle（Python 专用）
- **协议版本适配**：`adapt_version` 非零时通过 `adapter.py` 的 `adapt()` 函数在 v4/v5 协议间转换
- **PID 检查**：`check_pid=True` 检测 fork 后重建 auth 对象，防止多进程共享 HMAC 状态
- **feed_identities**：分离 ZMQ 路由帧（identities/delimiter）和消息帧
