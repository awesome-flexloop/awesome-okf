---
type: Concept
title: 5分钟快速上手
description: 从创建 Cli 对象到第一个连接、发送命令、获取结果的快速入门
tags: [scrapli, getting-started, cli, quickstart]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 5分钟快速上手

## 第一个 Cli 连接

使用 scrapli2 连接网络设备只需三步：创建 `Cli` 对象、打开连接、发送命令。

```python
from scrapli import Cli, AuthOptions

cli = Cli(
    host="192.168.1.1",
    auth_options=AuthOptions(
        username="admin",
        password="admin",
    ),
    transport_options=TransportBinOptions(),
)

cli.open()

result = cli.send_input("show version")
print(result.result)

cli.close()
```

### Cli 构造参数

`Cli.__init__` 的完整签名：

```python
Cli(
    host: str,                                    # 设备主机名或 IP（必填）
    *,
    port: int | None = None,                      # 端口，默认 SSH=22，Telnet=23
    definition_file_or_name: str | LoadedDefinition | None = None,  # 平台名或 YAML 路径
    cli_options: Options | None = None,           # CLI 选项
    auth_options: AuthOptions | None = None,      # 认证选项
    session_options: SessionOptions | None = None, # 会话选项
    transport_options: TransportOptions | None = None, # 传输选项
    logging_uid: str | None = None,               # 日志标识
    skip_static_options: bool = False,            # 跳过平台特定 Python 钩子
)
```

关键点：

- `host` 是唯一必填的位置参数
- 所有选项均为关键字参数
- 不指定 `definition_file_or_name` 时使用 `"default"` 平台定义
- 不指定 `transport_options` 时默认使用 `TransportBinOptions()`（系统 SSH）

### 平台参数

`definition_file_or_name` 接受三种形式：

1. **内置平台名**（字符串）：如 `"cisco_iosxe"`、`"arista_eos"`、`"juniper_junos"`，自动从包内 `definitions/` 目录加载对应 YAML
2. **YAML 文件路径**（字符串）：如 `"/path/to/custom.yaml"`，从文件系统加载
3. **`LoadedDefinition` 对象**：包含已加载的 `platform_name` 和 `definition` 字符串

```python
from scrapli import Cli, LoadedDefinition

cli = Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(username="admin", password="admin"),
)
```

环境变量 `SCRAPLI_DEFINITIONS_PATH` 可覆盖内置定义目录路径。

## 使用上下文管理器

推荐使用 `with` 语句自动管理连接生命周期：

```python
from scrapli import Cli, AuthOptions, TransportBinOptions

with Cli(
    host="192.168.1.1",
    auth_options=AuthOptions(username="admin", password="admin"),
) as cli:
    result = cli.send_input("show version")
    print(result.result)
```

`__enter__` 调用 `open()`，`__exit__` 调用 `close()`。异步版本使用 `async with`。

## 发送命令

`send_input()` 发送单条命令并返回 `Result` 对象：

```python
result = cli.send_input("show version")

print(result.result)           # 清理后的输出文本
print(result.failed)           # 是否检测到失败指示器
print(result.elapsed_time_seconds)  # 耗时（秒）
print(result.results_raw)      # 原始字节（延迟重构）
```

### send_input 参数

```python
cli.send_input(
    "show version",
    requested_mode="",                    # 在指定模式下发送
    input_handling=InputHandling.FUZZY,   # 输入匹配模式
    retain_input=False,                   # 结果中保留输入命令
    retain_trailing_prompt=False,         # 结果中保留尾部提示符
)
```

`InputHandling` 枚举：
- `EXACT`：精确匹配输入
- `FUZZY`（默认）：模糊匹配
- `IGNORE`：忽略输入匹配

### 批量发送命令

`send_inputs()` 一次发送多条命令：

```python
result = cli.send_inputs(["show version", "show interfaces", "show ip route"])
print(result.result)  # 所有结果以换行连接
```

`send_inputs` 额外支持 `stop_on_indicated_failure: bool = True`，在检测到失败时停止后续命令发送。

### 从文件发送命令

```python
result = cli.send_inputs_from_file("commands.txt")
```

文件中每行作为一条命令发送，尾部换行符被忽略。

## Result 对象

`Result` 对象封装了操作的全部输出信息：

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `result` | `str` | 所有结果以 `\n` 连接的文本 |
| `results` | `list[str]` | 各条命令的结果列表 |
| `failed` | `bool` | 是否检测到失败指示器 |
| `elapsed_time_seconds` | `float` | 操作耗时（秒） |
| `start_time` | `int` | 开始时间（Unix 纳秒） |
| `end_time` | `int` | 结束时间（Unix 纳秒） |
| `inputs` | `list[str]` | 发送的输入列表 |
| `host` | `str` | 主机地址 |
| `port` | `int` | 端口 |
| `results_raw` | `list[bytes]` | 原始字节输出（延迟重构） |
| `textfsm_parse()` | - | TextFSM 结构化解析 |
| `genie_parse()` | - | Cisco Genie 结构化解析 |

## 完整示例

```python
from scrapli import Cli, AuthOptions, TransportBinOptions

with Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(
        username="admin",
        password="admin",
    ),
    session_options=SessionOptions(
        operation_timeout_s=30,
    ),
) as cli:
    result = cli.send_input("show version")

    if result.failed:
        print("命令执行失败")
    else:
        print(result.result)
```

## 下一步

- [传输层详解](02-transport-layer.md) — 了解四种 Transport 模式的选择
- [认证与会话配置](03-auth-session.md) — 配置用户名/密码/密钥和会话参数
- [Cli 驱动详解](04-cli-driver.md) — 深入 Cli 类的全部方法
- [异步模式](05-async-mode.md) — 使用 async/await 并发连接多设备
