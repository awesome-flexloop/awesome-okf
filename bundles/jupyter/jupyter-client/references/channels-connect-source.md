---
okf_version: "0.2"
type: reference
title: "通道与连接 (channels.py / connect.py)"
description: "ZMQSocketChannel/HBChannel/ConnectionFileMixin 源码——通道基类实现、心跳线程、连接文件读写、端口发现、Socket创建"
tags: ["channels", "zmq", "connection-file", "heartbeat", "socket", "port-discovery"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: channels-py
    resource: jupyter_client/channels.py
    title: jupyter_client/channels.py
  - id: connect-py
    resource: jupyter_client/connect.py
    title: jupyter_client/connect.py
---

# 通道与连接 (channels.py / connect.py)

## 通道实现 (channels.py)

```python
major_protocol_version = protocol_version_info[0]  # 5

class HBChannel(Thread):
    """心跳通道——守护线程，定期发送 ping 监控内核存活"""
    time_to_dead: float = 1.0
    daemon = True

    def __init__(self, context, session, address, *, curve_serverkey=None):
        # 创建 REQ socket，支持 CurveZMQ

    def _create_socket(self):
        # 创建 zmq.REQ socket，连接到 hb 端口

    async def _async_run(self):
        # 循环：send(b"ping") → wait(time_to_dead) → poll → recv or call_handlers+重连

    def run(self):
        # 在新 asyncio event loop 中运行 _async_run

    def pause(self): ...      # 暂停心跳
    def unpause(self): ...    # 恢复心跳
    def is_beating(self) -> bool: ...  # 是否在正常跳动
    def call_handlers(self, since_last_heartbeat): ...  # 心跳失败回调

class ZMQSocketChannel:
    """ZMQ socket 通道包装（同步版本）"""
    def __init__(self, socket, session, loop=None): ...

    def get_msg(self, timeout=None) -> dict:
        # poll(timeout) → recv_multipart → feed_identities → deserialize
        # 无消息时抛出 queue.Empty

    def get_msgs(self) -> list: ...  # 获取所有就绪消息
    def msg_ready(self) -> bool: ...  # 是否有消息待读
    def send(self, msg) -> None: ...  # session.send(socket, msg)
    def start(self): pass
    def stop(self): ...  # close socket
    def is_alive(self) -> bool: ...

class AsyncZMQSocketChannel(ZMQSocketChannel):
    """异步 ZMQ 通道——使用 zmq.asyncio.Socket"""
    async def get_msg(self, timeout=None) -> dict: ...
    async def get_msgs(self) -> list: ...
    async def msg_ready(self) -> bool: ...
```

## 连接管理 (connect.py)

```python
class KernelConnectionInfo(TypedDict):
    """连接信息类型"""
    shell_port: int
    iopub_port: int
    stdin_port: int
    control_port: int
    hb_port: int
    ip: str
    key: str
    transport: str
    signature_scheme: str
    kernel_name: str
    curve_publickey: str
    curve_secretkey: str

channel_socket_types = {
    "hb": zmq.REQ,
    "shell": zmq.DEALER,
    "iopub": zmq.SUB,
    "stdin": zmq.DEALER,
    "control": zmq.DEALER,
}

def write_connection_file(fname=None, shell_port=0, iopub_port=0, ...):
    """生成连接 JSON 文件，自动发现随机端口"""
    # 1. bind 到 (ip, 0) 获取随机端口
    # 2. 构建 cfg 字典
    # 3. secure_write 写入 JSON（权限 600）
    # 4. 设置父目录 sticky bit

def find_connection_file(filename="kernel-*.json", path=None, profile=None):
    """查找连接文件（支持 glob 匹配，返回最新访问的文件）"""

def tunnel_to_kernel(connection_info, sshserver, sshkey=None):
    """通过 SSH 建立隧道，返回本地端口元组"""

class ConnectionFileMixin(LoggingConfigurable):
    """连接文件读写 Mixin——KernelClient 和 KernelManager 都继承"""

    transport = CaselessStrEnum(["tcp", "ipc"], default_value="tcp")
    ip = Unicode(default_value=localhost())
    connection_file = Unicode("")
    shell_port = Integer(0)
    iopub_port = Integer(0)
    stdin_port = Integer(0)
    hb_port = Integer(0)
    control_port = Integer(0)
    session = Instance(Session)
    curve_publickey = Bytes(allow_none=True)
    curve_secretkey = Bytes(allow_none=True)

    def write_connection_file(self, **kwargs): ...
    def load_connection_file(self, connection_file=None): ...
    def load_connection_info(self, info): ...
    def get_connection_info(self, session=False) -> KernelConnectionInfo: ...
    def cleanup_connection_file(self): ...
    def blocking_client(self) -> BlockingKernelClient: ...

    # URL 构建
    def _make_url(self, channel) -> str:
        # tcp://ip:port 或 ipc://ip-port

    # Socket 创建
    def _create_connected_socket(self, channel, identity=None):
        # 创建 socket → 设置 linger → 设置 identity → CurveZMQ → connect
    def connect_iopub(self, identity=None): ...  # 额外 SUBSCRIBE b""
    def connect_shell(self, identity=None): ...
    def connect_stdin(self, identity=None): ...
    def connect_control(self, identity=None): ...
    def connect_hb(self, identity=None): ...

class LocalPortCache(SingletonConfigurable):
    """本地端口缓存，防止多内核端口竞争"""
    def find_available_port(self, ip) -> int: ...
    def return_port(self, port) -> None: ...
```

**关键设计点**：
- **通道类型映射**：五个通道使用不同 ZMQ socket 类型——shell/stdin/control 用 DEALER（异步请求-应答），iopub 用 SUB（订阅发布），hb 用 REQ（简单请求-应答）
- **IOPub 订阅**：iopub 通道创建后必须 `setsockopt(zmq.SUBSCRIBE, b"")` 订阅所有消息
- **心跳线程独立 Event Loop**：HBChannel 在独立线程中创建 asyncio event loop 运行心跳循环，失败时重建 socket
- **连接文件安全**：通过 `secure_write` 确保文件权限为用户私有（600），设置父目录 sticky bit
- **CurveZMQ 加密**：socket 创建时自动配置 curve_secretkey/curve_publickey/curve_serverkey
- **端口自动发现**：通过 bind 到 port 0 让 OS 分配随机端口，LocalPortCache 防止多进程竞态
