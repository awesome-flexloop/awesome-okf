---
okf_version: "0.2"
---

# scrapli 实战示例

* [基础连接与命令发送](basic-connect.md) — 使用 Cli 连接设备、发送 show 命令、处理 Result
* [单条与批量命令发送](send-commands.md) — send_input/send_inputs/send_inputs_from_file、失败处理、TextFSM/Genie 解析
* [异步并行连接多设备](async-parallel.md) — asyncio.gather 并发连接、Semaphore 限流、异步 NETCONF
* [自定义平台定义与高级用法](custom-driver.md) — 自定义 YAML、LoadedDefinition、回调读取、会话录制

```{toctree}
:hidden:

async-parallel
basic-connect
custom-driver
send-commands
```
