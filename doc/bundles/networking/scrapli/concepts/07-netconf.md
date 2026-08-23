---
type: Concept
title: NETCONF 驱动
description: Netconf 类详解——NETCONF 操作、数据存储类型、过滤、锁、提交、验证、通知订阅
tags: [scrapli, netconf, rpc, yang, datastore]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# NETCONF 驱动

`Netconf` 类提供 NETCONF 协议操作支持。与 `Cli` 类共享相同的 auth/session/transport 选项层，但使用独立的操作方法集和 Result 类型。

## 基本用法

```python
from scrapli import Netconf, AuthOptions, TransportBinOptions

with Netconf(
    host="192.168.1.1",
    port=830,
    auth_options=AuthOptions(username="admin", password="admin"),
    transport_options=TransportBinOptions(),
) as nc:
    result = nc.get_config(source=DatastoreType.RUNNING)
    print(result.result)
```

`Netconf.__init__` 与 `Cli` 的区别：
- 默认端口为 **830**（NETCONF 标准端口，Cli 默认 22）
- 使用 `options: Options`（NetconfOptions）而非 `cli_options`
- 无 `definition_file_or_name` 参数（NETCONF 不依赖平台 YAML 定义）
- 无 `skip_static_options` 参数

## NetconfOptions

`netconf.Options`（通过 `NetconfOptions` 别名导入）配置 NETCONF 特有行为：

```python
from scrapli.netconf import Options as NetconfOptions
from scrapli.netconf import Version

nc_opts = NetconfOptions(
    error_tag="<rpc-error>",          # 标识 RPC 错误的标签子串
    preferred_version=Version.VERSION_1_1,  # 首选 NETCONF 版本
    message_poll_interval_ns=100_000_000,   # 消息轮询间隔（纳秒）
    capabilities_callback=my_callback,      # 能力协商回调
    close_force=False,               # 上下文管理器退出时强制关闭
)
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `error_tag` | `str \| None` | 标识 RPC reply 中错误的标签子串 |
| `preferred_version` | `Version \| None` | 首选 NETCONF 版本（1.0 或 1.1） |
| `message_poll_interval_ns` | `int \| None` | 消息轮询间隔（纳秒） |
| `capabilities_callback` | `Callable[[list[str]], list[str]] \| None` | 能力协商回调，接收设备能力列表，返回用户能力列表 |
| `close_force` | `bool` | 上下文管理器退出时是否强制关闭（不等待 close-session reply） |

## 数据存储类型

`DatastoreType` 枚举定义 NETCONF 数据存储：

| 枚举值 | 字符串 | 说明 |
|--------|--------|------|
| `CONVENTIONAL` | `"conventional"` | 常规数据存储 |
| `RUNNING` | `"running"` | 运行配置（默认） |
| `CANDIDATE` | `"candidate"` | 候选配置 |
| `STARTUP` | `"startup"` | 启动配置 |
| `INTENDED` | `"intended"` | 意图配置 |
| `DYNAMIC` | `"dynamic"` | 动态配置 |
| `OPERATIONAL` | `"operational"` | 操作状态数据 |

## 核心操作

### get_config

获取配置数据：

```python
from scrapli.netconf import DatastoreType, FilterType, DefaultsType

result = nc.get_config(
    source=DatastoreType.RUNNING,
    filter_="<interfaces></interfaces>",
    filter_type=FilterType.SUBTREE,
    filter_namespace_prefix="",
    filter_namespace="",
    defaults_type=DefaultsType.UNSET,
)
```

### get

获取状态和配置数据（不限于配置）：

```python
result = nc.get(
    filter_="<system><state/></system>",
    filter_type=FilterType.XPATH,
)
```

### edit_config

编辑配置：

```python
from scrapli.netconf import DefaultOperation, TestOption, ErrorOption

result = nc.edit_config(
    config="<config><interfaces><interface><name>ge-0/0/0</name></interface></interfaces></config>",
    target=DatastoreType.CANDIDATE,
    default_operation=DefaultOperation.MERGE,
    test_option=TestOption.TEST_THEN_SET,
    error_option=ErrorOption.STOP_ON_ERROR,
)
```

`DefaultOperation`：`MERGE`（默认合并）、`REPLACE`、`NONE`、`UNSET`
`TestOption`：`TEST_THEN_SET`、`SET`、`UNSET`
`ErrorOption`：`STOP_ON_ERROR`、`CONTINUE_ON_ERROR`、`ROLLBACK_ON_ERROR`、`UNSET`

### copy_config / delete_config

```python
nc.copy_config(target=DatastoreType.STARTUP, source=DatastoreType.RUNNING)
nc.delete_config(target=DatastoreType.CANDIDATE)
```

### lock / unlock

```python
nc.lock(target=DatastoreType.CANDIDATE)
nc.edit_config(config="...", target=DatastoreType.CANDIDATE)
nc.commit()
nc.unlock(target=DatastoreType.CANDIDATE)
```

### commit / discard / validate

```python
nc.commit()                    # 提交候选配置
nc.discard()                   # 丢弃候选配置变更
nc.validate(source=DatastoreType.CANDIDATE)  # 验证配置
```

### cancel_commit

```python
nc.cancel_commit(persist_id="12345")  # 取消正在进行的提交
```

### get_schema

获取 YANG schema：

```python
from scrapli.netconf import SchemaFormat

result = nc.get_schema(
    identifier="interfaces",
    version="2020-01-01",
    format_=SchemaFormat.YANG,  # XSD, YANG, YIN, RNG, RNC
)
```

### close_session / kill_session

```python
nc.close_session()                          # 优雅关闭会话
nc.kill_session(session_id=42)              # 强制终止指定会话
```

### get_data / edit_data（NMDA）

支持 NETCONF NMDA（Network Management Datastore Architecture）：

```python
result = nc.get_data(
    source=DatastoreType.OPERATIONAL,
    filter_="<system/>",
    config_filter=ConfigFilter.FALSE,
    max_depth=3,
    with_origin=True,
)

nc.edit_data(
    content="<system><hostname>router1</hostname></system>",
    target=DatastoreType.RUNNING,
)
```

### action

执行 YANG action：

```python
result = nc.action("<action><reset/></action>")
```

### raw_rpc

发送用户自定义的原始 RPC：

```python
result = nc.raw_rpc(
    payload="<get><filter><system/></filter></get>",
    base_namespace_prefix="nc",
    extra_namespaces=[("junos", "http://xml.juniper.net/junos/20.4/0")],
)
```

`base_namespace_prefix` 和 `extra_namespaces` 用于处理厂商特殊的命名空间需求（如 Cisco NX-OS）。

## 过滤类型

`FilterType` 枚举：
- `SUBTREE`（默认）：子树过滤
- `XPATH`：XPath 过滤

## 默认值类型

`DefaultsType` 枚举：
- `REPORT_ALL`：报告所有默认值
- `REPORT_ALL_TAGGED`：报告标记的默认值
- `TRIM`：修剪默认值
- `EXPLICIT`：仅显式值
- `UNSET`：不应用默认值处理

## 通知与订阅

### 获取通知

```python
try:
    notification = nc.get_next_notification()
    print(notification)
except NoMessagesException:
    print("无待处理通知")
```

### 获取订阅消息

```python
sub_id = nc.get_subscription_id(rpc_reply_payload)
message = nc.get_next_subscription(subscription_id=sub_id)
```

## NETCONF Result

NETCONF `Result`（`netconf_result.py`）是 dataclass，与 CLI Result 不同：

| 属性 | 类型 | 说明 |
|------|------|------|
| `input_` | `str` | 发送的 RPC 输入 |
| `host` | `str` | 主机地址 |
| `port` | `int` | 端口 |
| `start_time` | `int` | 开始时间（Unix 纳秒） |
| `end_time` | `int` | 结束时间（Unix 纳秒） |
| `result` | `str` | RPC 回复（自动剥离 XML header） |
| `result_raw` | `bytes` | 原始字节（延迟重构） |
| `rpc_warnings` | `str` | RPC 警告内容 |
| `rpc_errors` | `str` | RPC 错误内容 |
| `failed` | `bool` | `bool(rpc_errors)` |
| `elapsed_time_seconds` | `float` | 耗时（秒） |

`result` 属性会自动剥离 `<?xml ...?>` XML 声明头，以便 lxml 等库直接解析。

## 异步支持

所有 NETCONF 操作均有异步版本，命名为 `{方法名}_async`：

```python
async with Netconf(host="...", auth_options=...) as nc:
    config = await nc.get_config_async(source=DatastoreType.RUNNING)
    await nc.edit_config_async(config="...", target=DatastoreType.CANDIDATE)
    await nc.commit_async()
```

## 版本枚举

`Version` 枚举：
- `VERSION_1_0 = "1.0"`
- `VERSION_1_1 = "1.1"`

## Schema 格式

`SchemaFormat` 枚举：`XSD`、`YANG`、`YIN`、`RNG`、`RNC`
