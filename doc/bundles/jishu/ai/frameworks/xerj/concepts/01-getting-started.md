---
type: Concept
title: XERJ 安装与快速上手
description: XERJ 的安装路径与校验策略、--insecure 信任边界、admin.key 认证模型、15 个顶层子命令的全景与首次索引的最小闭环
tags: [xerj, 安装, 快速上手, CLI, 安全边界]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-facts
    resource: /references/facts.md
    title: XERJ 事实清单
  - id: xerj-source
    resource: /references/source.md
    title: XERJ 源码快照登记
---

# XERJ 安装与快速上手

XERJ 的安装 philosophy 是「一个二进制、零依赖」：没有 JVM、没有外部服务，Linux/macOS/Windows × x86-64/arm64 均有预编译产物。它同时是 ES 兼容服务器、MCP 服务器和 CLI 工具——三者共用同一个二进制。

## 安装

```sh
# Linux / macOS
curl -fsSL https://xerj.org/get | sh

# Windows PowerShell
irm https://xerj.org/get.ps1 | iex
```

安装器的行为是安全默认而非便利默认（F-162）：

- 下载 GitHub 最新 release 后校验 **SHA-256**，**缺 checksum 或不匹配一律中止**；
- `sh` 安装器依次尝试 `sha256sum`、`shasum`、`openssl`、`sha256`、`busybox`、`cksum`，**全部不可用时拒绝安装**；
- 只有显式设置 `XERJ_INSECURE_SKIP_CHECKSUM=1` 才允许跳过校验。

可选环境变量（F-164）：

| 变量 | 作用 |
|---|---|
| `XERJ_VERSION=vX.Y.Z` | 固定安装版本 |
| `XERJ_INSTALL_DIR` | 指定安装目录 |
| `XERJ_NO_PATH=1` | 不把安装目录加入用户 PATH（Windows 默认加入 `%LOCALAPPDATA%\Programs\xerj`） |

### PATH 陷阱

安装器**不修改 shell profile**（F-163）。在一个新 shell 里 `~/.local/bin` 往往不在 `PATH` 上，于是裸 `xerj` 会得到 `command not found`。解决办法二选一：

```sh
export PATH="$HOME/.local/bin:$PATH"   # 先导出
$HOME/.local/bin/xerj --help           # 或用绝对路径
```

> 这条对 MCP 宿主同样致命：从桌面图标启动的 MCP 宿主不继承你的 shell `PATH`，所以 MCP 配置里的 `command` 必须写绝对路径。

## 信任边界：`--insecure` 不是形式

XERJ 的默认是**认证开启**。不带 `--insecure` 启动（包括从配置文件启动）会铸造一个 `admin.key`（F-161）。

`--insecure` 关闭 TLS 与 API 密钥认证，于是**任何能访问该端口的调用方都是超级用户**，可以读取和删除包括每个 `/_memory` 命名空间在内的所有索引（F-160）。它的适用场景被明确限定为「一台开发机、一个用户」：全新节点只绑定 `127.0.0.1`，明文绑定到其他接口需要显式允许，否则拒绝启动（F-159）。

> **反常识**：`--insecure` 看起来只是个「开发时省事」的开关，实际是一条信任边界的显式声明。把它用在共享主机上，等于把整个索引空间（含智能体长期记忆）公开。

### 认证的实际用法

```sh
# 认证开启（默认）：启动时铸造密钥
xerj --data-dir ./data &
export XERJ_API_KEY="$(cat ./data/admin.key)"   # 密钥在 <data_dir>/admin.key

# 无认证（仅本机开发）
xerj --insecure --data-dir ./data &
```

一个容易踩的坑：`autoindex` **不会**从 `xerj.toml` 里读取密钥。它只认 `--api-key` 参数或 `XERJ_API_KEY` 环境变量；两者都没有时，每个请求都返回 `401 Unauthorized`（F-161）。

## 顶层命令全景

二进制暴露 14 个顶层子命令（F-024）：

| 命令 | 作用 | 备注 |
|---|---|---|
| `autoindex` | 把任意文件夹变成类型化索引 | 旗舰能力，详见 [02](/concepts/02-autoindex-pipeline.md) |
| `search` | 词法/结构化搜索 | 面向人的 CLI，自动发现节点、定义优先排序 |
| `def` | 跳转到定义 | 给定符号名，返回 file:line + 签名 |
| `code` | 参考编码检索 | 详见 [08](/concepts/08-reference-coding.md) |
| `corpus` | 语料库管理 | `add` / `index` / `build` / `list` |
| `hub` | Corpus Hub 目录与同步 | — |
| `ask` | 自然语言 → 校验后的查询 DSL | 确定性规则引擎，非 LLM |
| `mcp` | 启动 MCP stdio 服务器 | 详见 [03](/concepts/03-mcp-agent-surface.md) |
| `brain` | 构建第二大脑 | 关系层，详见 [06](/concepts/06-agent-memory-and-brain.md) |
| `init` | 把 XERJ 接入项目 | 注册 MCP + 写 skill |
| `gain` | 计数过的用量统计 | 搜索数、命中率、延迟 |
| `feedback` | 生成字段报告 | 可 `--submit` 直接开 PR |
| `share` | 只读分享链接 | 带口令的访客访问 |
| `index` | 直接摄入 NDJSON | 绕过 HTTP 栈的最快路径 |

智能体长期记忆没有独立 CLI 子命令，入口是 HTTP 的 `/_memory/{namespace}`（详见 [06](/concepts/06-agent-memory-and-brain.md)）。

子命令在服务器标志解析器**之前**分派；写在子命令之前的全局标志会被移到子命令之后，所以 `xerj --url URL corpus …` 是合法写法（F-025）。

另一个细节：`--flag` 后面缺值是**错误**而不是「静默未设置」。`xerj --insecure --data-dir` 过去会默默启动在默认数据目录，`xerj --data-dir --insecure` 会把名为 `--insecure` 的目录当成数据目录且认证仍开着（F-026）。

## 首次闭环

```sh
# 1. 启动节点（开发机）
xerj --insecure --data-dir ./data &

# 2. 把数据目录放到「将被索引的目录之外」
#    data/ 不在内置忽略列表中，否则节点会索引自己的存储
xerj autoindex ~/my-project

# 3. 看它造出了什么
xerj autoindex map

# 4. 查
curl "localhost:9200/ax-*/_search?q=checkout+error"
```

第 2 步的目录选择是一个真实的坑（F-057）：把 `--data-dir` 放在你随后要索引的树里，节点会把自己的 WAL 与 segment 一起索引进去。

### 索引名约定

索引名格式为 `<prefix>-<dataset-slug>`，`--prefix` 默认 `ax`（F-055）。当语料不该落进共享的 `ax-*` 通配符时，给它自己的 `--prefix`。

## 接入智能体：一条命令

```sh
xerj init
```

它在项目里做两件事（F-165）：

1. 把 MCP server 注册进 `.mcp.json`；
2. 为 Claude Code / Cursor 写一份 10 行 skill。

对它编辑的每个文件都留 `.bak` 备份。`xerj init` **有意不把凭据写进 `.mcp.json`**——那份文件是项目作用域、通常会被提交进版本库，凭据不能进。取而代之的是 MCP 服务器在回环地址上自动发现本地 `admin.key`（详见 [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md)）。

`xerj gain` 从节点的审计日志显示**计数过的**用量（搜索次数、命中率、延迟），不是估算（F-165）。

## 安全清单

| 事项 | 正确做法 |
|---|---|
| 共享主机 | 开启认证（默认），用 `--api-key` / `XERJ_API_KEY` 传递密钥 |
| 数据目录 | 放在将被索引的目录之外 |
| 索引目录 | 生产用专用 `admin.key`，不要写进项目文件 |
| MCP 配置 | `command` 用绝对路径；`env` 里放 `XERJ_URL` |
| 首次索引前 | 决定 `--embed-mode`（词法 / neural / proxy），因为它在**摄入时**生效（详见 [05](/concepts/05-vector-and-hybrid.md)） |

## 相关概念

- [00 整体架构](/concepts/00-overview.md)：crate 分层与运行形态
- [02 autoindex 零配置流水线](/concepts/02-autoindex-pipeline.md)：旗舰摄取流程
- [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md)：认证回退与工具面
- [05 向量、嵌入与混合检索](/concepts/05-vector-and-hybrid.md)：`--embed-mode` 的时机
- 事实来源：[事实清单](/references/facts.md)
