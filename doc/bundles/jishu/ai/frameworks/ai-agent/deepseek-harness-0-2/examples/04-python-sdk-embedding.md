---
type: example
title: "Python SDK 嵌入与子 Agent 委派"
description: "把 DeepSeek Harness 0.2 当作嵌入式运行时：在 Python 进程里跑任务、接管会话与通知、配置 profile 与 patch 叠加层，以及启用 subagent 委派族。"
tags: [deepseek-harness, python, sdk, subagent, example]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: 官方仓库 docs/user/guide/python-sdk.zh.md 与 python/sdk/README.zh.md
---

# Python SDK 嵌入与子 Agent 委派

> 场景：把 dsh 当作一个**被自己程序驱动的 agent 运行时**——不是 CLI 黑盒，而是一组可嵌入的 API。

## 1. 心智模型：SDK 是运行时外壳，不是 Python 实现

关键事实（源码事实）：

- Python SDK 包名 `deepseek-harness-sdk`，它**不内含一个 Python 版 agent loop**。SDK 延迟启动随包附带的 `dsh --profile <profile>` 原生进程，协议走 **JSON-RPC over stdio**。
- 因此**普通 SDK 运行不需要系统 Node.js**——wheel 内已带匹配的原生运行时与 `dsh` 命令。
- 不存在"独立 Python 运行时 bin"，也不存在"完整配置选项"；Python 侧只有**配置选择**，实际配置树由 profile + patch 决定。

安装：

```sh
python -m pip install deepseek-harness-sdk
```

要求 Python ≥ 3.10，且平台为 Linux x64 / Linux arm64 / macOS arm64 (14+) / Windows x64。

## 2. 最小嵌入

```python
from pathlib import Path
from deepseek_harness import DeepSeekHarness

workspace = Path("/absolute/path/to/disposable-workspace").resolve()
dsh_home = Path("/absolute/path/to/example-dsh-home").resolve()

with DeepSeekHarness(
    provider="deepseek-official",
    model="deepseek-v4-flash",
    max_tokens=49_152,
    cwd=str(workspace),
    dsh_home=str(dsh_home),
    profile="sdk-minimal",
) as harness:
    result = harness.run(
        "Inspect the repository and fix the failing tests.",
        session_id="example-001",
    )

print(result.final_response)
```

`DeepSeekHarness` 的构造参数（源码事实，来自 `DeepSeekHarnessConfig`）：

| 字段 | 默认 | 含义 |
|------|------|------|
| `provider` | `deepseek-official` | 模型提供方 |
| `model` | `deepseek-v4-flash` | 模型名 |
| `reasoning_effort` | `None` | 推理强度 |
| `max_tokens` | `None` | 单次生成上限 |
| `cwd` / `runtime_cwd` | `None` | agent 工作目录 / 运行时工作目录 |
| `dsh_bin` | `None` | 指定 dsh 可执行文件 |
| `profile` | `sdk` | 使用的 profile 名 |
| `patches` | `()` | 有序 patch 文件元组 |
| `dsh_home` | `None` | 隔离的 Harness home |
| `env` | `{}` | 传给子进程的环境变量 |
| `base_url` / `api_key` | `None` | 端点与凭据直传 |
| `initialize_timeout_seconds` | `30.0` | 初始化握手超时 |
| `request_timeout_seconds` / `shutdown_timeout_seconds` | `None` / `1.0` | 请求与关闭超时 |

## 3. RunResult 与会话生命周期

`run()` 返回 `RunResult`（源码事实）：

| 字段 | 类型 | 含义 |
|------|------|------|
| `session_id` | `str` | 本次会话标识 |
| `final_response` | `str` | 末尾 assistant 文本 |
| `finish_reason` | `str \| None` | 结束原因，取自最后一个 `turn/end` |
| `events` | `list[JsonObject]` | 本次运行的协议事件流 |
| `notifications` | `list[Notification]` | 订阅到的通知 |

会话 API 分三层：

```python
# ① 一次性 run（自动开/复用会话）
result = harness.run("prompt", session_id="example-001")

# ② 显式会话对象
session = harness.start_session("example-002")   # 或 harness.resume_session("example-001")
print(session.get_working_directory())
session.set_working_directory("/abs/path")
res = session.run("继续", on_notification=lambda n: print(n.method))

# ③ 底层协议客户端
client = harness.client
client.subscribe_session_notifications("example-001")
```

`Notification` 是 `@dataclass(slots=True)`，字段 `method: str` 与 `payload: JsonObject`；`IncomingRequest` 字段为 `id` / `method` / `payload`。

> `on_notification` 回调用于流式观察；`session.run()` 也可传入 `notifications` / `events` 列表由 SDK 自行累积。

## 4. profile 与 patch 的叠加

配置来源遵循"谁添加谁对账"的四层叠加（见 [Profile 与组合包](../concepts/03-profile-and-bundle.md)）：

```text
bundle patch → profile cordis.patch.yml → $DSH_HOME/cordis.patch.yml → --patch overlay
```

SDK 侧的三条实操纪律：

1. **profile 必须真实存在**。`sdk-minimal` 是随 SDK 附带的独立 profile；其他 profile 只有在包含 `@deepseek-ai/dsh-sdk-app` 或另一个 JSON-RPC server 配置项时才有效。
2. **不静默回退**。缺失 server 配置项、无法解析的插件、非法 patch 会在启动时**直接失败**，不会悄悄换成别的组合。
3. **绝不静默读 `~/.dsh`**。示例与 SDK 只会读写你显式给的 `dsh_home`。

一次性 patch 通过 `patches=` 传入（有序元组）：

```python
harness = DeepSeekHarness(
    profile="sdk-minimal",
    dsh_home="/abs/example-dsh-home",
    patches=("/abs/editor.patch.yml",),
)
```

持久 patch 写进 `$DSH_HOME/profiles/sdk-minimal/cordis.patch.yml`。

### 启用 `str_replace_editor`（源码事实）

随附运行时**包含** `str_replace_editor`，但 `sdk-minimal` 的默认 Cordis tree **不挂载**它。要用就得显式 patch：

```yaml
- insert:
    - id: tool-str-replace-editor
      name: '@deepseek-ai/dsh-tool-str-replace-editor'
```

`insert` 会新增 editor 并**复用已有的文件系统后端**；本地文件系统后端以运行时工作目录解析相对路径，且**不把访问限制在该目录内**。

## 5. sdk-minimal profile 的真实边界

| 属性 | 值 |
|------|-----|
| 系统提示词 | `DSH_SYSTEM_PROMPT`，未设置时为 `You are a helpful software engineer assistant.` |
| 模型优先级 | `--model` → `DSH_MODEL` → `deepseek-v4-flash` |
| 面向模型的工具 | Linux/macOS 为持久 `bash`，Windows 为 `pwsh`；另有 `read_image`、`working_directory` |
| Shell 超时 | 300 秒 |
| 上下文压缩 | 自动，用额外模型请求生成早期历史摘要 |
| 会话持久化 | `<dsh_home>/sessions` 下的**未压缩** JSONL |
| 沙箱模式 | **固定 `danger-full-access`** |

**不存在的组件**：文本文件工具、settings、托管凭据、OTel 遥测、Web 工具、subagent、本地指令发现。

> ⚠️ **安全警告**：`sdk-minimal` 固定 `danger-full-access`，持久 shell 可以修改运行时可见的**任何路径**。生产使用请用一次性 checkout 或容器。详见 [安全模型](../concepts/09-security-model.md)。

> ⚠️ `session-log-deepseek` 默认随 DeepSeek 请求上传**未被接受的日志事件**（每次请求上限 8 MiB）。在 profile patch 中设 `session-log-deepseek.enabled: false` 可关闭。

## 6. 启用子 Agent 委派

`sdk-minimal` **不含** subagent 族。要委派就得自己挂载对应组合包：

| 包 | 作用 | 挂载后提供 |
|----|------|-----------|
| `subagent` | 委派服务：提供方注册表、一次性运行、可继续子级、发现 | `ctx.subagents` |
| `subagent-spawn-in-process` | 全新进程内子 agent | 注册到 `ctx.subagents` |
| `subagent-fork-in-process` | 从父级已完成历史派生的进程内子 agent | 注册到 `ctx.subagents` |
| `subagent-acp` | 经 ACP 跑进程外子 agent | 注册到 `ctx.subagents` |
| `subagent-codex` | 经 app-server 协议跑真实 Codex 子 agent | 注册到 `ctx.subagents` |
| `subagent-claude-code` | 经 Agent SDK 跑真实 Claude Code 子 agent | 注册到 `ctx.subagents` |
| `subagent-dsh-sdk` | 经 TypeScript SDK 跑进程外 Harness 子 agent | 注册到 `ctx.subagents` |
| `tool-subagent` | 向模型暴露"委派"动作 | 注册到 `ctx.tools` |
| `tool-subagent-control` | 向模型暴露控制动作 | 注册到 `ctx.tools` |

### 委派工具

- `tool-subagent`：默认模型可见工具名为 **`subagent`**（`toolName` 可改），每个实例必须用**互不相同**的名字。
- `tool-subagent-control` 暴露三个控制工具（源码事实，工具名取自 `packages/subagent/tool-subagent-control/src/`）：
  - `send_message`——向相邻 agent 发送消息
  - `interrupt_agent`——中断其工作
  - `list_agents`——列出子级状态
- `tool-subagent` 另配 `list_subagent_models`（列出可用子 agent 模型）。

### 深度上限

`tool-subagent` 的 `maxDepth` 配置语义（源码事实）：

- 非负安全整数，`0` 禁止委派；
- `'provider-managed'` 表示不设上限（用于递归预算归子运行时或自有部署管理的进程外提供方）；
- 数字上限要求提供方具备 `depthLimit` 能力，否则**挂载时大声失败**；
- 省略时读取 Host 当前的 subagent 深度设置（**默认 1**）；
- 提供方在每次启动时检查调用方当前深度——即使工具保持模型可见，**拒绝权归运行时策略**。

### 委派配置样例

```yaml
- insert:
    - id: subagent-core
      name: '@deepseek-ai/dsh-subagent'
    - id: subagent-spawn
      name: '@deepseek-ai/dsh-subagent-spawn-in-process'
    - id: tool-subagent
      name: '@deepseek-ai/dsh-tool-subagent'
      config:
        provider: 'spawn'
        toolName: 'subagent'
        maxDepth: 1
    - id: tool-subagent-control
      name: '@deepseek-ai/dsh-tool-subagent-control'
```

再把它写进 `$DSH_HOME/profiles/sdk-minimal/cordis.patch.yml` 或通过 `patches=` 单次传入。

## 7. 部署要点

- 需要**浏览器应用**时，对显式 `DSH_HOME` 运行 `dsh web`；`web` 是独立 CLI 应用，**不能**为 Python SDK client 提供服务。
- 需隔离 profile、插件、凭据、设置与会话 → 用**新的 home**。
- 独立工作 → 用**新的 session id**；只有继续同一段持久对话与资源时才同时复用 harness + home + id。
- SDK 提示词文本**不会**执行 `/compact` 或其他斜杠命令。
- `dsh plugin --profile sdk-minimal add file:/abs/path/to/my-plugin-bundle` 可持久保存依赖与 bundle 层；该管理命令需要 `pnpm` 在 PATH 上（启动已安装 SDK 不需要）。

## 相关

- [应用形态](../concepts/10-application-forms.md)
- [Profile 与组合包](../concepts/03-profile-and-bundle.md)
- [安全模型](../concepts/09-security-model.md)
- [能力 seam 与子系统地图](../concepts/08-capability-seams.md)
- [一次性 Headless 任务](00-headless-task.md)
