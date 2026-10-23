---
type: concept
title: "入门指引——安装、运行与目录结构"
description: "DeepSeek Harness 0.2 的最小可用路径：npm 一行启动、源码构建、五个内置 profile、DSH_HOME 目录布局、首次配置模型与凭据。"
tags: [deepseek-harness, dsh, getting-started, cli, profile]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 README / docs/user/guide
---

# 入门指引：安装、运行与目录结构

## 1. 它是什么

DeepSeek Harness（`dsh`）是一个开源的 **agent harness**：模型负责"想"，harness 负责"干"——读文件、改代码、跑命令、校验结果、管会话、控权限。它以 npm 包 `@deepseek-ai/dsh` 发布，MIT 许可。

> ⚠️ 官方明确标注 dsh 处于 **developer preview**，会频繁出现**破坏性变更**；运行前应阅读仓库的 `SAFETY.md`（harness 会执行模型生成的代码与命令，并加载第三方插件）。

## 2. 三分钟跑起来

### 从 npm 跑（最省事）

```sh
npx @deepseek-ai/dsh web
```

启动 Web UI，默认 `http://127.0.0.1:3080` 并自动打开浏览器。SSH 场景下只打印主机 URL（转发地址由 SSH 客户端或编辑器掌握）；加 `--no-open` 可不打开浏览器。

### 从源码跑（要改代码时）

```sh
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

`pnpm run build` 只准备构建产物；`pnpm dsh web` 使用已构建产物而不重建。开发时用 `pnpm run dev:web`（构建 + 服务 + 客户端热重建同在一个终端）。

环境要求：Node.js `^22.19.0 || >=24.0.0`，包管理器 pnpm `11.28.5`（Corepack）。

## 3. 五个内置 profile

`dsh <name>` 是 `dsh --profile <name>` 的简写。每个 profile 是 `$DSH_HOME/profiles/<name>` 下的一个目录，装着自己的组合包清单与 patch。

| Profile | 组合 | 用途 |
|---------|------|------|
| `web` | base + web-app | 浏览器 UI（默认形态） |
| `headless` | base + headless | 一次性命令行任务，无 GUI、无端口 |
| `sdk` | base + sdk-app | JSON-RPC over stdio 的 SDK 服务端 |
| `sdk-minimal` | 独立组合包（**不叠 base**） | 最小 SDK 运行时，显式配置树 |
| `acp` | base + acp-app | Agent Client Protocol（stdio）服务端，供编辑器接入 |

`desktop` profile 是 Electron 桌面应用保留的，CLI 拒绝启动它。

```sh
dsh web                                   # 启动 Web UI
dsh --profile headless "run the tests"   # 一次性任务
dsh --profile acp                         # ACP 服务端
dsh --profile web --port 8080             # 换端口
```

> **profile 与应用参数的分界**：启动器自身的 flag（`--profile` / `--patch` / `--dump-config` 等）必须写在最前，遇到第一个无法识别的 token 就结束，其后全部原样交给 profile 应用（如 `--port 8080` 归 Web 解析）。`plugin` 紧跟 `dsh` 时是插件管理命令，要启动同名 profile 须写 `dsh --profile plugin`。

## 4. DSH_HOME 目录布局

`DSH_HOME` 默认是 `~/.dsh`（目录名常量 `DSH_HOME_DIR_NAME = '.dsh'`，见 `packages/util/home-paths`）。全部状态集中在这里：

```text
$DSH_HOME/
├── profiles/<name>/
│   ├── package.json          # profile manifest，声明 dsh.profile.bundles
│   ├── cordis.patch.yml      # 该 profile 的 patch
│   └── compatibility.json    # 版本豁免记录
├── cordis.patch.yml          # home 级共享 patch（优先级高于 profile 层）
├── .env                      # 环境变量分层
├── .credentials.yaml         # 凭据
├── sessions/                 # 会话事件日志（JSONL）
├── storages/                 # 非会话持久数据
├── cache/
├── attachments/v1/           # 内容寻址的附件
└── logs/                     # 启动诊断报告
```

`.env` 分层：调用目录的 `.env` 优先于 home 的 `.env`，两者都低于继承环境；`PATH` / `DSH_*` / `XDG_*` 等启动变量会被拒绝；四个代理类变量只接受来自 home `.env` 的值。

## 5. 第一次配置模型

Web UI 在设置里填模型与 API 密钥；命令行侧则通过组合包行读取凭据（base bundle 里挂了 `dsh-llm-deepseek-api-key`）。凭据也可写进 `$DSH_HOME/.credentials.yaml`。

想看清自己机器上到底组合出了什么配置树，不用启动应用：

```sh
dsh --profile web --dump-default-config   # 只看各组合包层
dsh --profile web --dump-config            # 再叠加 profile/home/--patch 层
dsh --profile web --dump-config-schema     # 输出 JSON Schema 2020-12
```

dump 输出是一份**可加载的 YAML**，并用 `# ==` 注释标明每一行来自哪个文件、哪一层 patch；`!!js` 表达式保持未求值。三种 dump flag 互斥，且都拒绝应用参数（dump 是 boot-free 的）。

## 6. 遇到问题时

启动失败时 CLI 会先打印失败插件与原始堆栈，再列出等待中的插件与缺失服务；末尾 `Full diagnostics:` 指向 `$DSH_HOME/logs/startup-<timestamp>-<uuid>.log`（含 DSH/Node 版本、平台、profile、根配置路径、每个未激活插件的模块与状态）。CLI 随后以退出码 1 结束。

诊断报告**不做脱敏**，分享前需自行检查其中的配置或凭据值。

## 下一步

- 想理解"profile 里的配置是怎么拼出来的" → [Profile 与组合包](03-profile-and-bundle.md)
- 想直接跑一个任务 → [Headless 实战](../examples/00-headless-task.md)
- 想看六种形态各自适合什么 → [应用形态](10-application-forms.md)
