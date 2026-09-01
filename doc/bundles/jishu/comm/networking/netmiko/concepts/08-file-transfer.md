---
type: Concept
title: SCP 文件传输
description: FileTransfer、SCPConn、file_transfer 便捷函数、verify_space、MD5 校验、InLineTransfer
tags: [netmiko, file-transfer, scp, FileTransfer, SCPConn]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# SCP 文件传输

netmiko 通过 SCP（Secure Copy Protocol）支持向网络设备上传和从网络设备下载文件。文件传输需要一个独立的 SSH 连接作为控制通道。

## 架构概览

```
netmiko SSH 连接（控制通道）── 发送 dir/verify 等 CLI 命令
    │
SCPConn（独立 SSH 连接）── SCP 文件传输
    │
scp.SCPClient ── paramiko Transport
```

- **SCPConn**：建立独立的 SSH 连接，封装 `scp.SCPClient`，提供 put/get 操作
- **BaseFileTransfer**：高级管理类，处理文件系统检测、空间验证、MD5 校验、文件存在检查
- **FileTransfer()**：工厂函数，根据 device_type 选择厂商特定的 FileTransfer 子类
- **file_transfer()**：一站式便捷函数，封装完整传输流程

## 支持 SCP 的平台

仅18个平台在 `FILE_TRANSFER_MAP` 中注册了专用 FileTransfer 类：

- Cisco: IOS, IOS XE, NX-OS, XR, ASA
- Arista EOS, Aruba OS
- Juniper Junos
- Linux
- Nokia SR OS
- Dell OS10, Dell SONiC
- Extreme EXOS
- MikroTik RouterOS
- Ciena SAOS
- Ubiquiti EdgeRouter
- ZPE Nodegrid

## FileTransfer 工厂

```python
from netmiko import ConnectHandler, FileTransfer

conn = ConnectHandler(device_type="cisco_ios", host="10.0.0.1",
                      username="admin", password="pass")

scp_transfer = FileTransfer(
    ssh_conn=conn,
    source_file="config.txt",
    dest_file="config.txt",
    file_system="flash:",       # 目标文件系统（Cisco IOS 自动检测）
    direction="put",            # "put"（上传）或 "get"（下载）
    socket_timeout=10.0,
    # progress=progress_bar,    # 可选进度回调
)
```

`file_system` 参数：
- Cisco IOS/IOS XE/XR：如果不指定，自动通过 `_autodetect_fs()` 检测（执行 `dir` 命令解析）
- 其他平台：必须显式指定，否则抛出 `ValueError`

## 完整传输流程

### 手动控制各步骤

```python
with FileTransfer(
    ssh_conn=conn,
    source_file="new_ios.bin",
    dest_file="new_ios.bin",
    file_system="flash:",
    direction="put",
) as scp_transfer:

    # 1. 检查文件是否已存在
    if not scp_transfer.check_file_exists():
        # 2. 验证远程空间
        if not scp_transfer.verify_space_available():
            raise ValueError("远程设备空间不足")

        # 3. 执行传输
        scp_transfer.transfer_file()

        # 4. MD5 校验
        if scp_transfer.verify_file():
            print("文件传输成功，MD5 校验通过")
        else:
            raise ValueError("MD5 校验失败")
    else:
        print("文件已存在")
```

`FileTransfer` 支持上下文管理器（`with` 语句），进入时建立 SCP 连接，退出时自动关闭。

### BaseFileTransfer 核心方法

| 方法 | 说明 |
|------|------|
| `check_file_exists()` | 检查目标文件是否已存在（put 检查远程，get 检查本地） |
| `verify_space_available()` | 验证目标有足够空间 |
| `remote_space_available()` | 获取远程可用空间（字节） |
| `local_space_available()` | 获取本地可用空间（字节） |
| `transfer_file()` | 执行 SCP 传输（put 或 get） |
| `verify_file()` | 通过 MD5 比较验证文件完整性 |
| `compare_md5()` | 比较源和目标的 MD5 |
| `remote_md5()` | 计算远程文件 MD5（执行 `verify /md5` 命令） |
| `file_md5()` | 计算本地文件 MD5 |
| `remote_file_size()` | 获取远程文件大小 |
| `enable_scp()` | 在远程设备启用 SCP 服务（Cisco: `ip scp server enable`） |
| `disable_scp()` | 禁用远程 SCP 服务 |
| `put_file()` / `get_file()` | 单独执行上传/下载 |

## file_transfer 便捷函数

`file_transfer()` 函数封装了完整的传输决策逻辑：

```python
from netmiko import file_transfer

result = file_transfer(
    ssh_conn=conn,
    source_file="config.txt",
    dest_file="config.txt",
    file_system="flash:",
    direction="put",
    overwrite_file=False,    # 文件存在时是否覆盖
    disable_md5=False,       # 禁用 MD5 校验
    # inline_transfer=True,  # Cisco IOS TCL 内联传输（仅文本文件）
)

print(result)
# {
#     "file_exists": True,        # 文件是否存在于目标
#     "file_transferred": True,   # 是否实际传输了文件
#     "file_verified": True,      # MD5 是否校验通过
# }
```

函数逻辑：
1. 文件不存在 → 验证空间 → 传输 → （可选）MD5 校验
2. 文件存在且 `overwrite_file=False` → 不传输，仅验证 MD5（如果启用）
3. 文件存在且 `overwrite_file=True` → 验证空间 → 传输 → MD5 校验
4. MD5 不匹配且不允许覆盖 → 抛出 `ValueError`
5. 传输后 MD5 校验失败 → 抛出 `ValueError`

## InLineTransfer（Cisco IOS 专用）

对于不支持 SCP 的 Cisco IOS 设备，可以使用 TCL 内联传输：

```python
result = file_transfer(
    ssh_conn=conn,
    source_file="config.txt",
    dest_file="config.txt",
    direction="put",
    inline_transfer=True,  # 使用 TCL 内联传输
)
```

限制：
- 仅支持 Cisco IOS/IOS XE
- 仅支持文本文件（不支持二进制）
- 仅支持 put（上传）
- 不支持进度回调
- 要求设备支持 TCL shell

## SCPConn 低级接口

直接使用 SCPConn 进行简单传输：

```python
from netmiko import SCPConn

scp_conn = SCPConn(
    ssh_conn=conn,
    socket_timeout=10.0,
    # progress=progress_bar,
)

# 上传文件
scp_conn.scp_put_file("local_config.txt", "flash:/remote_config.txt")

# 下载文件
scp_conn.scp_get_file("flash:/remote_config.txt", "local_config.txt")

# 必须关闭连接才能刷新写入
scp_conn.close()
```

## progress_bar 进度显示

netmiko 内置了一个 ASCII 进度条回调：

```python
from netmiko import progress_bar, file_transfer

result = file_transfer(
    ssh_conn=conn,
    source_file="large_firmware.bin",
    dest_file="firmware.bin",
    file_system="flash:",
    direction="put",
    progress=progress_bar,
)
```

输出类似：

```
[2J
Transferring file: large_firmware.bin

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>| (100.00%)
```

## 文件系统自动检测

Cisco 平台支持文件系统自动检测：

```python
# CiscoBaseConnection._autodetect_fs()
# 执行 "dir" 命令，解析 "Directory of (.*)/" 模式
# 例如输出 "Directory of flash:/" → file_system = "flash:"
```

检测后会通过 `dir flash:` 验证文件系统是否有效。

## 跨束参考

- [paramiko SFTP 文件传输](../../paramiko/concepts/07-sftp.md) — paramiko 的 SFTP 接口（netmiko SCP 底层使用 paramiko Transport）
