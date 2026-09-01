---
type: Concept
title: 官方示例体系解读
description: 解读 scrapli 仓库 16 个官方示例的共享 containerlab 拓扑契约、CLI 与 NETCONF 示例主题矩阵，以及从 sending_inputs 到 read_callbacks 的渐进式学习路径
tags: [scrapli, examples, containerlab, clab, learning-path, netconf]
generated: { by: "doc_agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
    title: scrapli2 源码信源登记
---

## 示例体系总览

scrapli 仓库的 `examples/` 目录提供 16 个可运行的官方示例：12 个 CLI 示例（`examples/cli/`）与 4 个 NETCONF 示例（`examples/netconf/`）。除非特定示例另有说明，所有示例的目标设备都是 "scrapli_clab" containerlab 测试拓扑中的 srlinux 设备，具体为该拓扑的 "ci" 变体——可在任意 linux 或 darwin 设备上运行，且仅使用公开可用镜像（F-001）。

## 共享拓扑契约

### "ci" 变体拓扑组成

"ci" 变体拓扑包含三部分（F-004）：

- 一个 **srlinux** 设备（CLI 与 NETCONF 双角色）
- 一个 **netopeer** netconf server
- 一个用于测试 proxy-jump ssh 行为的 **dummy linux container**

### 启动方式

在仓库根目录运行 make 目标启动测试拓扑，需要 docker（F-002）：

```bash
make run-clab-ci
```

拓扑会启动一个绑定 docker sock 的 launcher pod，使 containerlab 在 darwin 主机上也能原生运行（F-003）。

### 端口与凭据

srlinux 设备暴露 SSH/Telnet/Netconf 端口 22/23/830；darwin 用户的 NAT 端口为 21022/21023/21830；凭据为 `admin` / `NokiaSrl1!`（F-005）。每个示例按运行系统选择端口（检测到 darwin 则 SSH 连 21022）（F-006）。

| 服务 | 标准端口（linux） | darwin NAT 端口 |
|------|------------------|-----------------|
| SSH | 22 | 21022 |
| Telnet | 23 | 21023 |
| NETCONF | 830 | 21830 |

### 环境变量覆盖

示例支持通过环境变量覆盖默认连接参数（F-007）：

| 环境变量 | 默认值 |
|----------|--------|
| platform | srlinux |
| host | — |
| port | — |
| username | — |
| password | — |

## CLI 示例矩阵（12 个）

| 目录名 | 主题 | 核心 API |
|--------|------|----------|
| `sending_inputs` | `Cli` 的三种输入发送方法 | `send_input` / `send_inputs` / `send_inputs_from_file`（F-029、F-030） |
| `input_modes` | 设备可能存在不同 mode/权限级别，按定义中的 mode 发送输入 | `enter_mode(requested_mode="configuration")` + `send_input(..., retain_trailing_prompt=True)`（F-015、F-016） |
| `sending_configs` | 向设备发送配置——配置本质上是发送到设备的输入 | `send_input(..., requested_mode="configuration")` / `send_inputs(inputs=[...], requested_mode="configuration")`（F-027、F-028） |
| `misc_options` | 覆盖 `send_input` 的多种选项 | `retain_trailing_prompt` / `retain_input=True` / `operation_timeout_ns` / `input_handling=InputHandling.EXACT`（F-019、F-020） |
| `handling_interactions` | 处理设备上的半交互式提示（配置写入确认、删除文件确认） | `send_prompted_input(input_, prompt, prompt_pattern, response, requested_mode="bash")`（F-013、F-014） |
| `output_parsing` | 使用 textfsm / ntc-templates 将非结构化输出解析为结构化对象 | `result.textfsm_parse(...)` / `results.textfsm_parse(..., index=1, to_dict=False)`（F-021、F-022） |
| `logging_setup` | 使用标准 Python logging 进行日志配置 | `logging.basicConfig(level=logging.DEBUG)` + `send_input`（F-017、F-018） |
| `session_recorder` | 将底层 session 的所有读取记录到文件 | `Cli(..., session_options=SessionOptions(recorder_path=...))`（F-031、F-032） |
| `custom_definition` | platform definitions 概念与自定义 YAML 定义接入未内置平台 | `Cli(definition_file_or_name=...)` + `send_input`（F-011、F-012） |
| `async_usage` | 连接目标设备并异步执行 `show version`，同时运行后台任务以体现 async/await 交错 | `async with cli as c` + `await c.send_input_async(...)` + 5 个 `Cli` 实例经 `asyncio.as_completed` 并发（F-008~F-010） |
| `proxy_jump_cli` | 使用 libssh2 和 bin transport 实现 proxy jump——先连 bastion host 再跳连目标设备 | `TransportBinOptions(ssh_config_path=...)` / `TransportSsh2Options(proxy_jump_host/username/password/...)`（F-023、F-024） |
| `read_callbacks` | 终端服务器、设备 console、零接触 provisioning、tail 日志或长输出触发回调场景 | `read_with_callbacks(initial_input=..., callbacks=[...])` + `ReadCallback(name/contains/callback/once/completes)`（F-025、F-026） |

## NETCONF 示例矩阵（4 个）

| 目录名 | 主题 | 核心 API |
|--------|------|----------|
| `get_operations` | 覆盖 `get`、`get-config`、`get-schema`、`get-data` RPC | `get_config()` / `get()` / `get_schema()` / `get_data()`（后者连接 Netopeer 服务器）（F-035、F-036） |
| `edit_config` | `edit-config` RPC 及锁定、提交、解锁配置数据 store 的流程 | `lock()` → `edit_config()` → `commit()` → `unlock()`（F-033、F-034） |
| `subscriptions` | 通过 `raw_rpc` 创建订阅（scrapli 未封装多种 RFC 订阅方式），分别获取通知与订阅消息 | `create-subscription`（raw_rpc）+ `get_next_notification()`；`establish-subscription`（raw_rpc）+ `get_subscription_id()` + `get_next_subscription()`（F-039、F-040） |
| `proxy_jump_netconf` | 与 CLI 版本类似，Netconf 连接同样支持 ProxyJump | `TransportBinOptions`（SSH config 跳转）/ `TransportSsh2Options`（`proxy_jump_*` 参数跳转）（F-037、F-038） |

## 渐进式学习路径

示例目录天然构成一条由浅入深的学习曲线。建议按以下顺序推进：

1. **sending_inputs** — 最基础的连接与三种输入发送方法，建立"inputs 统一一切"的心智模型
2. **input_modes** — 理解 modes 取代 privilege levels 后如何进入指定 mode 发送输入
3. **sending_configs** — 体会"配置只是输入"：在 configuration mode 下发送配置与提交
4. **misc_options** — 精细控制 `send_input` 行为（保留输入/尾随提示符、超时、精确输入处理）
5. **handling_interactions** — 应对半交互式提示；复杂场景进一步学习 `read_with_callbacks`
6. **output_parsing** — 用 textfsm/ntc-templates 把输出变成结构化数据
7. **logging_setup** 与 **session_recorder** — 可观测性两件套：调试日志与会话录制
8. **custom_definition** — 脱离内置平台，用自定义 YAML 接入任意设备
9. **async_usage** — 从同步迈向并发：5 个连接的异步交错执行
10. **proxy_jump_cli** — 经 bastion host 跳连的两种 transport 配置方式
11. **read_callbacks** — 最进阶的读取模式：回调驱动的长输出/日志 tail 场景

NETCONF 侧建议路径：**get_operations**（读操作全家桶）→ **edit_config**（锁定-编辑-提交-解锁事务流程）→ **subscriptions**（raw_rpc 建订阅 + 通知获取）→ **proxy_jump_netconf**（跳连场景下的 NETCONF）。

## 相关概念

- [/examples/basic-connect.md](/examples/basic-connect.md) — 基础连接示例
- [/examples/proxy-jump.md](/examples/proxy-jump.md) — proxy jump 示例详解
- [/examples/output-parsing.md](/examples/output-parsing.md) — 输出解析示例详解
- [/examples/session-recorder.md](/examples/session-recorder.md) — 会话录制示例详解
- [/concepts/09-testing-system.md](/concepts/09-testing-system.md) — 测试体系与示例的联动
