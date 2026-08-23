---
type: Concept
title: SCP 文件复制
description: asyncssh.scp() 协程、本地/远程/第三方复制、preserve/recurse 参数、进度回调、run_scp_server
tags: [asyncssh, scp, file-transfer, copy]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# SCP 文件复制

## scp() 函数

asyncssh 提供模块级协程 `scp()`（scp.py:931），使用 SCP 协议在本地和远程之间复制文件。SCP 比 SFTP 更简单，但功能较少——不支持断点续传、文件属性精细控制等。

函数签名：

```python
async def scp(
    srcpaths, dstpath=None, *,
    preserve=False,
    recurse=False,
    block_size=262144,
    progress_handler=None,
    error_handler=None,
    **kwargs
) -> None
```

默认块大小为 256 KiB。

## 路径格式

源路径和目标路径支持以下形式：

| 形式 | 含义 |
|------|------|
| `'/local/path'`（str/bytes） | 本地文件系统路径 |
| `(conn, '/remote/path')` | 已建立的 `SSHClientConnection` 上的远程路径 |
| `(('host', port), '/path')` | 自动建立连接的远程路径 |
| `'host:path'`（str） | 便捷格式，自动连接到默认端口 |
| `(conn, None)` 或 `(conn, '')` | 远程默认工作目录 |

路径支持 `*` 和 `?` 通配符。

## 基本用法

### 上传文件

```python
await asyncssh.scp('local.txt', ('hostname', '/remote/path/'),
                   username='user', password='secret')
```

使用已有连接：

```python
async with asyncssh.connect('hostname') as conn:
    await asyncssh.scp('local.txt', (conn, '/remote/path/'))
```

### 下载文件

```python
await asyncssh.scp(('hostname', '/remote/file.txt'), 'local.txt',
                   username='user')
```

### 多源文件

```python
await asyncssh.scp(['file1.txt', 'file2.txt'],
                   (conn, '/remote/dir/'))
```

## 递归复制目录

```python
await asyncssh.scp('local_dir/', (conn, '/remote/'),
                   recurse=True)
```

`recurse=True` 时，源路径指向目录会复制整个子树。

## 保留属性

```python
await asyncssh.scp('local.txt', (conn, '/remote/'),
                  preserve=True)
```

`preserve=True` 保留访问时间、修改时间和权限。

## 进度回调

```python
def progress(src_path, dst_path, copied_bytes, total_bytes):
    pct = copied_bytes * 100 // total_bytes if total_bytes else 0
    print(f'\r{pct}% ({copied_bytes}/{total_bytes})', end='')

await asyncssh.scp('large.iso', (conn, '/remote/'),
                   progress_handler=progress)
```

回调参数：相对路径、已复制字节数、总字节数。

## 错误处理

批量复制时使用 `error_handler` 收集错误而不中断：

```python
errors = []

def on_error(exc):
    errors.append(exc)

await asyncssh.scp('/data/*.log', (conn, '/backup/'),
                   recurse=True, error_handler=on_error)

for err in errors:
    print(f'复制失败: {err}')
```

错误处理器可抛出异常以中止复制，否则继续下一个文件。

## 第三方远程复制

源和目标都可以是远程连接，实现服务器间直接复制（数据经客户端中转）：

```python
async with asyncssh.connect('host1') as conn1, \
           asyncssh.connect('host2') as conn2:
    await asyncssh.scp((conn1, '/data/file.txt'),
                       (conn2, '/backup/file.txt'))
```

## 块大小调整

```python
await asyncssh.scp('large.bin', (conn, '/remote/'),
                   block_size=1024*1024)  # 1 MiB blocks
```

更大的块大小可提高高延迟网络的吞吐量，但消耗更多内存。

## SCP 与 SFTP 对比

| 特性 | SCP | SFTP |
|------|-----|------|
| 协议复杂度 | 简单 | 复杂（v3-v6） |
| 文件传输 | ✅ | ✅ |
| 目录列表 | ❌ | ✅ |
| 文件属性 | 仅 preserve | 完整（stat/chmod/chown） |
| 断点续传 | ❌ | ✅（通过 seek） |
| 远程复制 | 经客户端中转 | 支持 copy-data 扩展 |
| 通配符 | 客户端展开 | 支持 glob() |
| 进度回调 | ✅ | ✅ |
| 性能 | 流式，较快 | 请求-应答，有开销 |

对于简单文件传输，SCP 通常更快；对于需要文件管理、属性操作、断点续传的场景，SFTP 更合适。

## SCP 服务端

asyncssh 服务端通过 `sftp_factory` 和 `allow_scp=True` 参数自动处理 SCP 连接。`run_scp_server()`（scp.py:1129）由 `SSHServerStreamSession` 在检测到 `scp` 命令时内部调用：

```python
await asyncssh.create_server(
    MySSHServer, '', 22,
    server_host_keys=['host_key'],
    sftp_factory=True,
    allow_scp=True
)
```

设置 `allow_scp=True` 后，当客户端执行 `scp` 命令时，asyncssh 自动创建 SFTPServer 实例并调用 `run_scp_server()` 处理协议。也可直接导入 `run_scp_server` 进行自定义处理。

## 相关概念

- [SFTP 文件传输](/concepts/07-sftp.md) —— 更完整的文件管理协议
- [流与进程](/concepts/04-streams-processes.md) —— SCP 底层通道
- [实战示例：SFTP 传输](/examples/sftp-transfer.md)

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
