# 实战示例（Examples）

> ⚠️ **统一执行边界**：本目录三篇示例的命令与代码来自官方文档，并已对 v2.4.6 源码核对类名/入口；**均未在本机执行**。需要模型 API Key、Docker 或对应平台环境，真实运行会产生费用。

## 示例清单

| 顺序 | 示例 | 你会得到 | 前置条件 |
|---|---|---|---|
| 1 | [安装与 mini CLI](01-install-and-cli.md) | 能启动 `mini`，理解 confirm/yolo/human | Python >= 3.10 |
| 2 | [Python 嵌入](02-python-bindings.md) | 20 行代码把 Agent 接进自己的程序 | 模型 API Key |
| 3 | [SWE-bench 批处理](03-swebench-batch.md) | 跑子集、生成预测文件、单实例调试 | Docker（x86 Linux）+ API Key |

## 建议顺序

1. 先跑示例一，确认模型与 Key 可用，理解确认模式。
2. 再跑示例二，把 Agent 嵌入脚本，观察 `exit_status` 与轨迹 JSON。
3. 最后跑示例三，先用 `--slice 0:5` 估算成本，再扩到全量。

## 不要照抄博客的快速开始

博客里的 `MiniSWEAgent`、`result.passed`、`result.patch` 在 v2.4.6 中不存在（E-3）。正确入口是 `DefaultAgent`，返回值是 `exit_status`/`submission` 字典。详见 [references/verification.md](../references/verification.md)。

```{toctree}
:hidden:
:maxdepth: 2

01-install-and-cli
02-python-bindings
03-swebench-batch
```
