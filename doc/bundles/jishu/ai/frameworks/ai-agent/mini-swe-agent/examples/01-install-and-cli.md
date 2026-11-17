---
type: Example
title: "示例一：安装与 mini CLI"
description: "三种安装方式、mini 的四个常用参数、confirm/yolo/human 三模式与配置文件位置；官方文档命令，未在本机实测"
tags: [安装, CLI, mini, uvx, pipx, yolo, confirm]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:03:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-mini-swe-agent
    resource: /references/repo-source.md
    title: "仓库事实清单（F-035 ~ F-100）"
  - id: official-quickstart
    resource: https://mini-swe-agent.com/latest/quickstart/
    title: "官方 Quick Start"
  - id: official-mini-cli
    resource: https://mini-swe-agent.com/latest/usage/mini/
    title: "官方文档：Using the mini CLI"
---

# 示例一：安装与 mini CLI

> ⚠️ **执行边界**：以下命令来自官方文档与 v2.4.6 源码（F-067、F-065），**本知识包未在本机执行**。不同平台（Windows/macOS/Linux）与容器环境可能需要额外配置；请以官方文档为准。

## 1. 三种安装方式

### 方式 A：临时试用（不污染当前环境）

```bash
pip install uv && uvx mini-swe-agent
# 或
pip install pipx && pipx ensurepath && pipx run mini-swe-agent
```

来源：README（F-039 的同一份 Quick Start）。

### 方式 B：安装到当前环境

```bash
pip install mini-swe-agent
mini
```

安装后可用入口：`mini`、`mini-swe-agent`、`mini-extra`、`mini-e`（F-047）。

### 方式 C：源码开发

```bash
git clone https://github.com/SWE-agent/mini-swe-agent.git
cd mini-swe-agent
pip install -e .
mini
```

要求 Python >= 3.10（F-045）。

## 2. 首次运行

直接执行：

```bash
mini
```

默认行为：

1. 进入 `confirm` 模式（F-063、F-065）。
2. 提示输入任务（也可以用 `-t` 直接给）。
3. 打印全局配置目录位置；API Key 存在该目录的 `.env`（F-065 的官方说明）。
4. 每一步模型提出命令，你按 Enter 确认，或输入拒绝理由。

## 3. 四个常用参数

| 参数 | 作用 | 示例 |
|---|---|---|
| `-t/--task` | 直接给任务，跳过交互输入 | `mini -t "给这个仓库加一个 healthcheck"` |
| `-m/--model` | 指定模型 | `mini -m anthropic/claude-sonnet-4-5-20250929` |
| `-c/--config` | 指定 YAML 配置，可多次叠加 | `mini -c mini.yaml -c agent.step_limit=50` |
| `-y/--yolo` | 跳过确认，直接执行 | `mini -y -t "..."` |

> `-c` 的注意点：一旦使用 `-c`，不会自动加载完整默认配置；要显式带上基础配置再叠加覆盖（F-062）。

## 4. 三种运行模式

| 模式 | 进入方式 | 行为 | 适合 |
|---|---|---|---|
| `confirm` | 默认，或 `/c` | 每个动作需确认 | 第一次用、改真实仓库 |
| `yolo` | `-y` 或 `/y` | 直接执行 | 受信任沙箱、批量任务 |
| `human` | `/u` | 你接管输入命令 | 卡住时手动救场 |

运行中随时 `Ctrl+C` 可中断当前动作并切换模式（F-065）。

## 5. 一个最小会话（示意）

```text
$ mini -m anthropic/claude-sonnet-4-5-20250929 -t "修复 tests/test_login.py 的失败用例"
mini-swe-agent 2.4.6
Loading global config from '~/.config/mini-swe-agent/.env'

mini-swe-agent (step 1, $0.00):
我先看一下仓库结构和失败测试。

bash: ls -la && pytest -q tests/test_login.py
[Enter 确认 / 输入理由拒绝]
```

> 以上输出为结构示意，不是实际终端录制。真实输出会包含模型回复、returncode 与截断后的 observation（F-064）。

## 6. 配置文件放哪

1. 全局配置目录由 `platformdirs.user_config_dir("mini-swe-agent")` 决定（F-038 的代码基础）。
2. API Key 推荐用 `mini-extra config set KEY VALUE` 写入 `.env`（官方 FAQ，F-072 同页）。
3. 项目级配置用 `-c` 指定，不要改包内 `config/mini.yaml`。

## 7. 常见问题

| 现象 | 处理 |
|---|---|
| 提示没有默认模型 | 用 `-m` 指定，或 `mini-extra config setup` |
| 认证失败 | 检查 `.env` 里的 Key 与模型 provider 是否匹配 |
| 命令一直等待确认 | 你在 `confirm` 模式，按 Enter 或 `/y` 切换 |
| 输出太长被截断 | 让模型用 `sed -n`/`grep` 缩小输出（F-064） |
| Windows 上 shell 行为不同 | 优先用 Docker/Singularity 环境，或 WSL |

## 8. 下一步

- 想嵌入自己的 Python 程序：[02-python-bindings](02-python-bindings.md)
- 想跑 SWE-bench：[03-swebench-batch](03-swebench-batch.md)
- 想理解 CLI 背后的循环：[concepts/02-architecture-and-code](../concepts/02-architecture-and-code.md)
