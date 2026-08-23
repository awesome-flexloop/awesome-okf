---
type: Reference
title: "ResponseManager加密通信源码"
description: "ResponseManager单例：RSA+AES加密的连接信息回传通道、Response事件机制、KernelChannel枚举"
tags: [response-manager, encryption, rsa, aes, connection-info, zmq]
sources:
  - id: processproxy
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/processproxy.py"
    title: "processproxy.py"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
---

# ResponseManager加密通信源码

本信源登记 `processproxy.py` 中 `ResponseManager`、`Response`、`KernelChannel` 三个相关类的源码。

## 设计背景

本地内核场景下，Jupyter通过connection file（JSON文件）传递5个ZMQ端口信息。远程内核场景下，内核运行在远端机器/容器中，无法通过文件系统共享连接信息。ResponseManager通过TCP监听端口+RSA+AES加密解决了这一问题 [I-02洞察2]。

## ResponseManager 单例 [F-091~F-102]

继承自 `SingletonConfigurable`，整个进程只有一个实例。

### RSA密钥生成 [F-092]

```python
KEY_SIZE = 1024

def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self._private_key = RSA.generate(self.KEY_SIZE, Random.new().read)
    self._public_key = self._private_key.publickey()
    self._public_pem = self._public_key.exportKey("PEM")
```

公钥通过 `public_key` 属性暴露，格式为去除PEM头尾和换行符的纯Base64字符串 [F-093]。

### 响应地址 [F-094]

```python
@property
def response_address(self):
    return f"{self.ip}:{self.port}"
```

响应端口默认8877，可通过 `EG_RESPONSE_PORT` 环境变量配置。

### Socket监听 [F-095,F-096]

```python
def _prepare_response_socket(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((self.ip, self.port))
    s.listen(128)
    s.settimeout(self.socket_timeout)  # 0.005秒超时，非阻塞轮询
    self._response_socket = s
```

`_start_response_manager()` 创建socket后启动 `ioloop.PeriodicCallback`（0.1秒间隔）调用 `_process_connections()`。

### 连接处理循环 [F-097]

```python
def _process_connections(self):
    try:
        while True:
            connection, addr = self._response_socket.accept()
            data = b""
            while True:
                buffer = connection.recv(1024)
                if buffer:
                    data += buffer
                else:
                    break
            connection.close()
            if data:
                connection_info = self._decode_payload(data)
                self._post_connection(connection_info)
    except socket.timeout:
        pass
```

非阻塞轮询accept，接收完一个连接的所有数据后关闭连接，解密payload，分发连接信息。

### 加密Payload解码 [F-098,F-099]

支持两个版本的payload格式：

**v1版本（当前标准）**：
```python
{
    "version": 1,
    "key": "<base64 RSA加密的AES密钥>",
    "conn_info": "<base64 AES加密的连接信息JSON>"
}
```

解密流程：
1. Base64解码key → RSA私钥解密得到AES密钥
2. Base64解码conn_info → AES-CBC解密得到连接信息JSON字符串
3. JSON解析为dict

**v0版本（遗留兼容）**：
- 使用kernel_id前16字节作为AES密钥（MD5 hash）
- Base64解码 → AES解密 → JSON解析

### 连接信息分发 [F-100]

```python
def _post_connection(self, connection_info):
    kernel_id = connection_info.get("kernel_id")
    if kernel_id in self._response_registry:
        self._response_registry[kernel_id].response = connection_info
```

### 事件注册与等待 [F-101,F-102]

```python
def register_event(self, kernel_id):
    self._response_registry[kernel_id] = Response()

async def get_connection_info(self, kernel_id):
    response = self._response_registry.get(kernel_id)
    try:
        await asyncio.wait_for(response.wait(), timeout=self.connection_interval)
        connection_info = response.response
        return connection_info
    finally:
        self._response_registry.pop(kernel_id, None)
```

`connection_interval = poll_interval / 100 = 0.005`秒超时。RemoteProcessProxy在confirm_remote_startup中循环调用此方法等待连接信息到达。

## Response 事件类 [F-103]

```python
class Response(asyncio.Event):
    def __init__(self):
        super().__init__()
        self._response = None

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value
        self.set()  # 触发事件
```

扩展asyncio.Event，增加一个response属性存储连接信息。setter自动调用set()唤醒等待协程。

## KernelChannel 枚举 [F-104]

```python
class KernelChannel(Enum):
    SHELL = "shell"
    IOPUB = "iopub"
    STDIN = "stdin"
    HB = "hb"
    CONTROL = "control"
    EG_COMM = "eg_comm"  # 非ZMQ通道，用于launcher中断通知
```

定义6个通道名称，其中EG_COMM是EG扩展的通信通道，用于向launcher发送中断通知（非标准ZMQ通道）。

## 通信流程

```
EG侧                                  Launcher侧（远程主机/容器内）
1. 生成RSA密钥对
2. 启动TCP监听(ResponseManager)
3. 启动命令中携带:
   {response_address}, {public_key}
                                      4. 启动kernel进程
                                      5. 从kernel获取5个ZMQ端口
                                      6. 生成随机AES密钥
                                      7. RSA公钥加密AES密钥
                                      8. AES加密连接信息JSON
                                      9. TCP连接response_address
                                     10. 发送加密payload
11. 接收并解密payload
12. 触发Response事件
13. 通过SSH隧道连接ZMQ端口
                                     14. ZMQ通道就绪，开始执行代码
```
