---
type: Concept
title: 单文件架构与 asyncio 执行模型
description: 从源码视角解析 podman-compose 的分层结构、命令注册装饰器、三种子进程调用方式与 asyncio 并发模型
tags: [podman, compose, source-code, architecture, asyncio, internals]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
  - id: readme
    resource: /references/readme-source.md
    title: podman-compose 官方 README
---

# 单文件架构与 asyncio 执行模型

[01-daemonless-arch.md](01-daemonless-arch.md) 从外部行为解释了 daemon-less 架构；本文进入 `podman_compose.py` 内部，回答一个问题：**一个约 5500 行的 Python 文件，是如何组织出完整编排能力的？**

## 分层结构：单文件内的逻辑分层

虽然没有分包，但源码按职责呈现清晰的分层顺序（信源登记中将全文划分为 10 个逻辑层，详细行号地图见[源码信源登记](../references/source-code-map.md)）：

```text
进程入口        main() → asyncio.run(async_main())
  └─ 主编排类    PodmanCompose（配置状态 + 生命周期编排）
       ├─ 配置层  文件发现 / env / 插值 / 深合并 / 归一化 / extends
       ├─ 翻译层  container_to_args：service dict → podman argv
       ├─ 执行层  Podman 类：asyncio 子进程包装
       └─ 命令层  20+ 个 compose_* 异步函数（up/down/build/...）
```

关键事实：**业务逻辑几乎全部是纯函数**（接收 dict、返回 argv 或新 dict），有状态的只有 `PodmanCompose` 单例与 `Podman` 包装器。这使得"配置怎么翻译"与"翻译后怎么执行"两件事在代码上自然分离。

## 入口链与模块级单例

启动链非常短：

```python
# 进程入口（L5532）
def main() -> None:
    asyncio.run(async_main())          # 唯一的事件循环驱动点

async def async_main() -> None:
    await podman_compose.run()         # podman_compose 是模块级单例（L3270）
```

`PodmanCompose.run()`（L2480）依次完成：

1. `_parse_args(argv)`：argparse 解析全局参数与子命令
2. 构造 `Podman` 实例，信号量为 `asyncio.Semaphore(args.parallel)`
3. 非 dry-run 时执行 `podman --version` 做存活探测（失败直接退出）
4. 除 `version` 与 `systemd create-unit` 外，调用 `_parse_compose_file()` 加载配置
5. 从 `self.commands[cmd_name]` 取出命令协程并 await，返回码为整数时 `sys.exit`

## 命令注册：装饰器即路由表

子命令不是手写 if-else 分发，而是用两个装饰器在模块导入时注册：

- `@cmd_run(podman_compose, "up", help文本)`（L3280）：包装**异步**函数（非协程会直接报错），把函数登记进 `compose.commands` 字典，并从 docstring 拆出帮助文本。
- `@cmd_parse(podman_compose, "up")`（L3305）：把该命令的 argparse 参数定义函数挂到命令对象的 `_parse_args` 列表上；支持一次绑定多个命令（如 `@cmd_parse(..., ["down", "stop", "restart"])` 复用超时参数定义）。

`_parse_args()` 动态遍历 `self.commands` 生成 argparse 子解析器。**新增一个子命令 = 写一个 async 函数并加两个装饰器**，无需改动任何分发代码。

## 三种子进程调用方式

`Podman` 类对 podman CLI 的调用分三种语义，分别对应不同场景：

| 方法 | 机制 | stdout/stderr | 典型用途 |
|------|------|---------------|---------|
| `output()`（L1858） | `create_subprocess_exec` + `communicate()` | 捕获为 bytes，非零退出抛 `CalledProcessError` | 查询类：`ps`、`inspect`、`network exists`、`volume inspect` |
| `run()`（L1940） | `create_subprocess_exec` + `wait()` | 三态：继承终端 / DEVNULL / 管道着色 | 动作类：`create`、`start`、`pull`、`build`、`stop` |
| `exec()`（L1928） | `os.execlp` | 进程映像被 podman 直接替换 | `wait` 命令：让 podman 成为前台进程直接接管信号 |

所有调用的命令行都按同一公式组装：

```text
[podman_path] + podman_args + get_podman_args(cmd) + cmd_args
```

`get_podman_args(cmd)`（L2469）注入两层用户自定义参数：全局 `--podman-args`，以及每命令的 `--podman-<cmd>-args`（仅对 `PODMAN_CMDS` 元组中的 9 个子命令开放：pull/push/build/inspect/run/start/stop/rm/volume）。

## asyncio 并发模型

### 信号量：唯一的并发闸门

`Podman` 的每个并发方法都在 `async with self.semaphore` 内启动子进程。信号量大小来自 `--parallel`，默认 `sys.maxsize`（实际无限制），也可由环境变量 `COMPOSE_PARALLEL_LIMIT` 控制。pull、build、stop、down 等所有并行操作共享这一个闸门。

### 并行模式：gather 与任务组

源码中的并发呈现两种固定模式：

- **批量同构操作**用 `asyncio.gather`：如 `compose_pull` 并行拉取去重后的镜像、`compose_down` 并行停止容器、`transfer_service_status` 并行重启服务。
- **前台 up 的任务组**用 `asyncio.wait(..., return_when=FIRST_COMPLETED)`：每个服务一个 `podman start -a` 协程；任一容器退出时，配合 `--abort-on-container-exit` / `--abort-on-container-failure` 取消其余任务，`--exit-code-from` 还会传播指定服务的退出码。

`build` 命令则是分层调度：按 `build_deps`（`additional_contexts` 中的服务间引用）找出当前无待建依赖的服务，一层并行构建、`as_completed` 收集结果后再进入下一层。

### 取消语义：terminate → 10 秒宽限 → kill

`Podman.run()` 捕获 `asyncio.CancelledError` 后不是直接杀进程，而是先 `terminate()`，用 `wait_with_timeout` 等待 10 秒，超时才 `kill()`（L1997-2005）。前台 up 的 SIGINT 处理器（仅非 Windows 注册）则先执行一次 `down` 做优雅清理，再取消所有任务。

## 日志流处理：增量解码与着色前缀

前台模式下每行容器日志都带彩色服务前缀（如 `[web_1]  |`），实现并不经过 shell sed，而是纯 Python：

1. `_readchunk()`（L1877）按 `\n` 读块，兼容半包（`IncompleteReadError`）与超长行（`LimitOverrunError`）。
2. `_format_stream()`（L1885）用 `codecs.getincrementaldecoder("utf-8")` 做**增量 UTF-8 解码**——多字节字符可能横跨两个读取块，直接 decode 会产生乱码；解码后按行注入前缀，并为没有结尾换行的"进行中行"维护状态。
3. stdout 与 stderr 各起一个独立 task 汇流到同一个 sink。

颜色取自 `console_colors` 的 5 种亮色 ANSI 序列，按服务序号取模；`--no-color` 退化为无色前缀，`--no-log-prefix` 完全去掉前缀。

一个容易忽略的实现细节：流处理 task 被显式加入一个 `task_reference` 集合并注册 `done_callback` 自动移除——这是为了规避 Python issue 91887（未被引用的 task 可能被垃圾回收导致协程静默终止）。

## dry-run 与可观测性

- `--dry-run` 在 `Podman.run()` 入口直接返回 None：所有"会执行什么命令"仍通过 `log.info` 打印，但不创建任何子进程。这是阅读翻译结果最直接的方式。
- `--verbose` 将日志级别调到 DEBUG，可以看到合并后的配置、卷/网络的 inspect-create 过程、依赖等待等内部决策。
- `--podman-path` 允许替换 podman 可执行文件（dry-run 下不做存在性检查），便于测试与多版本并存。

## 架构启示

- **编排器不持有运行态**：`PodmanCompose` 实例只在单次命令进程内存活；资源现状全部通过 `Podman` 的查询方法实时获取。这是 daemon-less 模型在代码层面的直接体现（资源身份如何跨进程延续，见[CLI 翻译层与标签状态](05-cli-translation-layer.md)）。
- **可复现性内建**：因为一切动作都是 argv 拼接，`--dry-run` 与 DEBUG 日志输出的命令行可以直接复制到终端手工执行，排障路径短。
- **单文件不等于无结构**：纯函数翻译层 + 薄执行层 + 装饰器注册的组合，让 5500 行代码保持了可导航的分层。

## 相关概念

- [daemon-less 架构](01-daemonless-arch.md)：本文的外部行为视角
- [CLI 翻译层与标签状态](05-cli-translation-layer.md)：service dict 如何变成 podman argv
- [配置加载管线](06-config-pipeline.md)：compose 文件如何变成内存中的 service dict
- [依赖图与 up/down 生命周期](07-dependency-lifecycle.md)：异步任务组在生命周期中的具体编排
- [源码信源登记](../references/source-code-map.md)：行号与符号索引
