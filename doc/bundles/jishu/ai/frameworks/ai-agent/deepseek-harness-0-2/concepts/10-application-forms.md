---
type: concept
title: "应用形态——CLI / Web / Desktop / Headless / ACP / Python SDK"
description: "dsh 的六种应用形态各自的启动方式、参数、协议与适用场景：dsh CLI 启动器、Web UI、Electron Desktop、Headless 一次性运行器、ACP stdio 服务端、Python SDK。"
tags: [deepseek-harness, applications, cli, web, desktop, headless, acp, python-sdk]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 apps/、packages/bundle/、python/sdk 与 docs/user/guide
---

# 应用形态：CLI / Web / Desktop / Headless / ACP / Python SDK

## 1. 总览

| 形态 | 组合包 | 启动 | 协议/界面 |
|---|---|---|---|
| **CLI 启动器** | — | `dsh --profile <name>` | 参数解析 + profile 启动 |
| **Web** | base + web-app | `dsh web` | 浏览器 UI（默认 `127.0.0.1:3080`） |
| **Desktop** | desktop profile | Electron 应用 | 私有 Host + 打包 Web 资源 |
| **Headless** | base + headless | `dsh --profile headless "任务"` | stdout 最终答案 / stderr 推理 |
| **ACP** | base + acp-app | `dsh --profile acp` | stdio 上的 JSON-RPC（ACP） |
| **SDK** | base + sdk-app 或 sdk-minimal | `dsh --profile sdk` | stdio 上的 JSON-RPC |
| **Python SDK** | sdk-minimal | 由 Python 客户端拉起 | 同上，Python 封装 |

> **重要概念**：SDK 与 ACP 都是**profile**，不是独立可执行文件。自定义插件组合继续由 profile 与有序 patch 文件表达。

## 2. CLI 启动器

包 `@deepseek-ai/dsh`，bin `dsh` → `lib/bin.js`（源码 `apps/cli/src/bin.ts`）。自身 flag：`--profile <name>`、`--from-default-profile <name>`、`--patch <path>`（可重复）、`--dump-config`、`--dump-default-config`、`--dump-config-schema`、`-V/--version`。

`dsh <name>` 是 `dsh --profile <name>` 的简写。`plugin` 保留为插件管理命令。

启动流程：解析自身 flag → 选运行器（`runProfile` / `runPlugin` / `runDumpConfig` / `runDumpConfigSchema`）→ 组合配置树 → 挂载插件。收到 SIGINT/SIGTERM 时，挂载的根节点会先 dispose 再退出。

`--from-default-profile <template>`：用五个随附模板之一的全新副本替换自定义目标（目标名不能是随附 profile 名）。它在组合包解析之前提交，因此后续失败仍会把新 profile 留在磁盘上；失败恢复留下的旧目录保存在 `$DSH_HOME/profiles/.<name>.staging-*/previous`。

## 3. Web UI

```sh
dsh web
dsh web --host "$(hostname -i | awk '{print $1}')" --public-url https://app.example/ --trusted-host app.example
dsh web --tls-cert ./server-chain.pem --tls-key ./server-key.pem
dsh web --no-open
```

- 默认端口 **3080**；默认只监听 loopback；**通配地址被拒**（`--host 0.0.0.0` 以用法错误退出）
- 无 TLS 的非 loopback 监听会给明文 HTTP 并警告
- `--public-url` 公告唯一的 HTTP(S) 应用根（可带转发前缀），替代监听器绑定地址 URL；**它不授予信任**——浏览器可见的 authority 仍需 `--trusted-host` 点名
- `--tls-cert`/`--tls-key` 要么都给要么都不给；**绝不回退到 HTTP**；替换证书后需重载监听器或重启才生效
- 前端在 `apps/web`（Vite + React），Host 由 `packages/host/host-webserver` 提供
- Web profile 有三个 agent preset：`standard` / `cordis` / `minimal`

## 4. Desktop（Electron）

- `apps/desktop`（`@deepseek-ai/dsh-desktop`，electron ^44.7.0 + electron-builder ^26.17.0）
- `apps/desktop-host`（`@deepseek-ai/dsh-desktop-host`，private）
- Electron 以 **RunAsNode** 子进程跑共享 profile runner，从 `dsh-app://app/` 加载打包内 Web 入口
- 桌面应用在签名资源中携带**精确匹配的 dsh 生产运行时**，并拥有保留的 `$DSH_HOME/profiles/desktop`
- 默认监听**系统分配的端口**（避免与 3080 冲突），绑定 `127.0.0.1`
- Desktop 与 npm CLI 共享产品数据，但**包、启用选择与锁文件保持独立**
- `desktop` profile 保留给 Electron，CLI 拒绝启动它

## 5. Headless 一次性运行器

```sh
dsh --profile headless "run the tests"
{ echo "Summarize these changes:"; git diff --stat; } | dsh --profile headless
dsh --profile headless --json "job"
```

- 任务来自位置参数或 stdin
- 推理增量以 `dsh: reasoning:` 标题流式写入 **stderr**，最终答案只写 **stdout**
- 退出码 0 = 完成（`completed`），1 = 中止或出错
- `--json` 输出行式事件流：`session` / `status` / `text` / `thinking` / `tool_call` / `tool_result` / `final` / `error`
- `--session-id` 可续接同一对话
- headless **不挂载**浏览器 Connection、HTTP 服务器、Web 运行时或浏览器客户端，也**不打开监听端口**

## 6. ACP 服务端

`dsh --profile acp`，基于 base，挂载 `@deepseek-ai/dsh-acp`（依赖 `@agentclientprotocol/sdk@1.4.0`）。

- stdout **仅**承载换行分隔的 JSON-RPC 帧
- **禁用模型生成会话标题**（ACP 无标题能力）
- ACP bundle 在 YAML 中禁用 HMR——保证一条 stdio 连接不会观察到依赖被替换

## 7. Python SDK

pip 名 `deepseek-harness-sdk`，模块 `deepseek_harness`。

| 文件 | 职责 |
|---|---|
| `api.py` | `DeepSeekHarness`、`DeepSeekHarnessConfig`、`Session`、`RunResult` |
| `client.py` | `HarnessClient`（同步 JSON-RPC over stdio 客户端）、`HarnessConfig`、`NotificationSubscription` |
| `models.py` | `IncomingRequest` / `InitializeResponse` / `Notification` / `ServerInfo` |
| `errors.py` | `SdkProtocolError` |
| `office.py` | `convert` / `recalculate` / `render_images` |

要点：

- Python SDK **没有独立应用入口**，它以 `--profile sdk` 启动内置 `dsh` CLI，用按行分隔的 JSON-RPC over stdio 驱动
- **必须显式给 `dsh_home` 或非空 `DSH_HOME`**——SDK 刻意不发现 `~/.dsh`
- `python/sdk-runtime`（`deepseek-harness-runtime-bin`）打包原生可执行 `deepseek-harness-sdk-runtime-<platform>-<arch>`，因此用 SDK **不需要系统 Node**；`download_office()` / `download_primary_runtime()` 需显式调用
- `sdk-minimal` 的属性：系统提示词默认 `You are a helpful software engineer assistant.`；默认模型 `deepseek-v4-flash`；工具为持久 bash/pwsh + `read_image` + `working_directory`；shell 超时 300s；自动压缩；JSONL 会话存 `<dsh_home>/sessions`；**固定 `danger-full-access`**（因此建议一次性 checkout 或容器）

```python
from deepseek_harness import DeepSeekHarness

with DeepSeekHarness(provider="deepseek-official", model="deepseek-v4-flash",
                     cwd=str(workspace), dsh_home=str(dsh_home),
                     profile="sdk-minimal") as harness:
    result = harness.run("Inspect the repository and fix the failing tests.",
                         session_id="example-001")
print(result.final_response)
```

`RunResult(session_id, final_response, finish_reason, events, notifications)`；`finish_reason` 取最后一个根会话 `turn/end` 的 `kind`（`completed` / `max-tokens` / `error`）。

## 8. 插件管理命令

```sh
dsh plugin --profile <name> add ./my-bundle
dsh plugin --profile <name> remove <pkg>
dsh plugin --profile <name> version-exemptions
dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <rt> --accept-risk
```

`dsh plugin` 把参数转发给 `pnpm`（`add` / `remove` / `why` / `update` 等），**pnpm 必须在 PATH 上**。每次成功运行后会根据当前安装状态更新 `dsh.profile.bundles`。

⚠️ 添加、移除或更新组合包后**须重启该 profile**（profile 或 home 的普通 patch 编辑则通过热重载生效）。

## 下一步

- [Headless 实战](../examples/00-headless-task.md)
- [Python SDK 嵌入](../examples/04-python-sdk-embedding.md)
