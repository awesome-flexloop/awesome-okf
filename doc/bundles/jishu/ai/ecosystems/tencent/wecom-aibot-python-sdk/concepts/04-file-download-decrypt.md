---
type: concept
title: 文件下载与解密
description: 追踪 download_file 到 download_file_raw 再到 AES-256-CBC 解密的完整链路与私有填充约定
tags: [wecom, aibot, python-sdk, crypto]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
  - resource: /references/facts.md
---

# 文件下载与解密

## 三层调用链

媒体处理只有一个入口：`WSClient.download_file(url, aes_key=None)`，返回 `(bytes, Optional[str])`，即「数据 + 文件名」（F-050）。内部依次经过三层：

| 层 | 函数 | 职责 | 依据 |
|---|---|---|---|
| 门面 | `WSClient.download_file` | 判断是否需要解密，组织返回值 | F-050 |
| 传输 | `WeComApiClient.download_file_raw` | HTTPS 下载、解析文件名 | F-051、F-052 |
| 密码 | `decrypt_file` | Base64 派生密钥、AES-CBC 解密、去填充 | F-053、F-054 |

若 `aes_key` 为假值（`None`、空串），门面记 `warn` 后**原样返回密文**，不做任何解密尝试（F-050）。这意味着「文件看起来是坏的」有时不是解密失败，而是调用方忘传 `aeskey`。

## 下载：aiohttp + 证书上下文

`download_file_raw` 用 `aiohttp.TCPConnector(ssl=_SSL_CONTEXT)` 建立连接器，再以 `ClientSession(timeout=self._timeout, connector=connector)` 发起 `GET`，随后 `raise_for_status()` 并 `await response.read()`（F-051）。超时由构造参数决定：`ClientTimeout(total=timeout / 1000)`，`timeout` 默认 10000，即总超时 10 秒（F-051）。`_SSL_CONTEXT` 优先用 `certifi.where()` 提供 CA 包，导入失败时回退系统默认上下文（F-021）。

10 秒是**整个请求的总时限**，不是单次读超时。大文件或弱网下应先评估体量；该值来自 `WSClientOptions.request_timeout`，可在构造时调整（F-055、F-056）。

## 文件名：两套正则与一个兜底

文件名来自响应头 `Content-Disposition`，解析顺序固定（F-052）：

1. 先按 `filename\*=UTF-8''([^;\s]+)` 匹配，对应 RFC 5987 的编码文件名；
2. 未命中再按 `filename="?([^";\s]+)"?` 匹配普通写法；
3. 两处命中值都经 `unquote` 还原；
4. 都未命中时 `filename` 保持 `None`。

因此中文名依赖第一步；若服务端只给普通 `filename=`，非 ASCII 字符可能出现百分号编码残留。调用方不应假设文件名一定存在，落盘前需自行兜底，例如取 URL 末段或时间戳（`examples/basic.py` 即如此，F-057）。

## 解密：AES-256-CBC 的私有约定

`decrypt_file` 的输入校验在最外层：数据为空抛 `ValueError("decrypt_file: encrypted_data is empty or not provided")`；`aes_key` 不是非空字符串抛 `ValueError("decrypt_file: aes_key must be a non-empty string")`（F-053）。这两类错误**不会被包装**为 `RuntimeError`，调用方需分别捕获。

密钥派生与解密步骤（F-053、F-054）：

| 步骤 | 操作 | 细节 |
|---|---|---|
| 1 | Base64 补齐 | `aes_key + '=' * (4 - len(aes_key) % 4)` |
| 2 | 解码 | `key = base64.b64decode(...)` |
| 3 | 取 IV | `iv = key[:16]`，IV 不随包传输 |
| 4 | 补零 | 数据补齐到 16 字节整数倍 |
| 5 | 解密 | `Cipher(algorithms.AES(key), modes.CBC(iv))` |
| 6 | 去填充 | `pad_len = decrypted[-1]`，要求 `1 <= pad_len <= 32` 且不超过数据长度 |
| 7 | 校验 | 尾部每个字节都必须等于 `pad_len`，否则报 `padding bytes mismatch` |
| 8 | 包装 | 上述异常统一包为 `RuntimeError("decrypt_file: Decryption failed - ...")` |

两个与标准实现不同的点值得单独记住：

- **先补零再解密**。CBC 的解密只让最后一组受前一组密文影响，因此对密文尾部补零不会破坏原有最后一组的填充语义；这是一种容错，而不是标准流程。
- **`pad_len` 上限是 32 而非 16**。标准 PKCS#7 的填充长度不可能超过块长 16，这里放宽到 32，说明实现沿用了 32 字节块的约定（F-054）。直接套用通用 unpad 库会在这类数据上误判。

## 失败排查

| 异常 / 现象 | 含义 | 排查方向 |
|---|---|---|
| `ValueError: encrypted_data is empty` | 下载结果为空 | 检查 HTTP 状态与 `read()` 返回值 |
| `ValueError: aes_key must be a non-empty string` | 未传或类型错误 | 从 `body.image.aeskey` / `body.file.aeskey` 取值 |
| `RuntimeError: Decryption failed` | 密钥、IV 或填充不匹配 | 确认 `aeskey` 与文件同源，检查 Base64 是否被截断 |
| `KeyError` / 长度为 0 的文件 | 其实是未解密 | 确认 `aes_key` 为真值，否则门面原样返回密文 |
| 文件名是 `None` | 响应头缺失或格式不符 | 用 URL 末段兜底 |
| 下载超时 | 总时限 10 秒 | 调大 `request_timeout`，或改用流式下载自行实现 |

## 安全提示

`aeskey` 属于消息级密钥，不应写入日志或提交到仓库；本 SDK 的错误信息不打印密钥，但调用方自定义日志时容易泄露。下载仅走 HTTPS，未做额外签名校验，因此 URL 的来源可信度决定整条链路的安全性（F-021、F-051）。

## 延伸阅读

- [帧协议与事件分发](/concepts/02-frame-protocol.md)：`message.image` / `message.file` 载荷如何到达处理器。
- [连接生命周期](/concepts/01-connection-lifecycle.md)：下载使用的证书上下文与连接层配置。
- [事件回调与文件示例](/examples/03-template-card-and-file-download.md)：下载、解密、落盘的完整演示。