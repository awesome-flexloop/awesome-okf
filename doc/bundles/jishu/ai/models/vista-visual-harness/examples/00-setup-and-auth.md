---
type: example
title: "环境准备与授权配置"
description: "从零到可运行：Python 3.12 虚拟环境、固定版本依赖、ARC API Key 与 Claude Token 配置、两个 Docker 镜像的构建与自检清单。"
tags: [vista, setup, auth, docker, prerequisite]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-01-20
sources:
  - id: source-code-map
    resource: /references/source-code-map.md
  - id: article-source
    resource: /references/article-source.md
  - id: vista-commit
    url: "https://github.com/joshhhhhan/VISTA/tree/c97c354f0a8948256545a3e8850a1848f8e5b8c1"
---

# 环境准备与授权配置

> 目标：从一个空的 Linux x86_64 机器，走到"能跑一次单局"的状态。
> 命令原文来自仓库固定 commit `c97c354f` 的 README 与脚本 [F-086]；前置条件见 [08 复现与运维](../concepts/08-reproduction-and-operations.md)。

## 0. 前置检查表

| 项 | 要求 | 检查命令 | F |
|----|------|---------|---|
| 架构 | x86_64 | `uname -m` | [F-075] |
| Python | 3.12（**且仅 3.12**） | `python3.12 --version` | [F-090] |
| Docker | Engine 可用 | `docker info` | [F-075] |
| Agent CLI | Codex **0.145.0** 或 Claude Code **2.1.220** | `codex --version` / `claude --version` | [F-075][F-110] |
| 批量 | `tmux` | `tmux -V` | [F-075] |
| 磁盘 | 官方镜像与数据集需数 GB | `df -h .` | [F-091] |

> **Python 版本是硬约束**：`requires-python = ">=3.12,<3.13"` [F-090]。3.13 会被 pip 直接拒绝。

## 1. 取源码（固定到不可变 commit）

```bash
git clone https://github.com/joshhhhhan/VISTA.git
cd VISTA
git checkout c97c354f0a8948256545a3e8850a1848f8e5b8c1
git rev-parse HEAD   # 应输出 c97c354f0a8948256545a3e8850a1848f8e5b8c1
```

> 仓库**没有任何 release tag** [F-086]，所以必须固定到 commit。核验命令输出的 40 位哈希是否与上面一致。

## 2. 建虚拟环境并安装

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
```

安装的核心依赖全部固定版本：`arc-agi==0.9.9`、`arcengine==0.9.3`、`numpy==2.5.1`、`pillow==12.2.0`、`python-dotenv==1.2.2`、`requests==2.34.2`、`urllib3==2.7.0` [F-091]。

**自检**：

```bash
.venv/bin/vista --help
```

应看到 `--profile`（四选一）与 `--backend`（二选一）两个必填参数 [F-092]。

## 3. 配置凭证

```bash
cp .env.example .env
chmod 600 .env
```

编辑 `.env`：

```dotenv
ARC_API_KEY=your-arc-prize-key
ARC_BASE_URL=https://three.arcprize.org
CLAUDE_CODE_OAUTH_TOKEN=your-claude-token
```

| 变量 | 何时需要 | 来源 | F |
|------|---------|------|---|
| `ARC_API_KEY` | online / competition 模式**必需** | ARC Prize 平台个人页 API Keys | [F-094] |
| `ARC_BASE_URL` | 默认即 `https://three.arcprize.org` | `.env.example` | [F-094] |
| `CLAUDE_CODE_OAUTH_TOKEN` | 仅 Claude Code 后端 | `claude setup-token` 生成 | [F-094] |
| `CLAUDE_CODE_OAUTH_TOKEN_2/_3` | 仅竞争模式的账号池 | 可选，`.env.example` 中已注释 | [F-094] |

> **凭证隔离是内置的**：即使你配了 `ARC_API_KEY`，MCP 子进程也拿不到它——`FORBIDDEN_SUBPROCESS_CREDENTIALS` 明确禁止把 `CLAUDE_CODE_OAUTH_TOKEN`、`ANTHROPIC_API_KEY`、`ARC_API_KEY` 带入子进程 [F-117]。

## 4. 安装 Agent CLI

```bash
# Codex CLI 0.145.0
npm install --prefix ~/.local/share/arc3-codex/0.145.0 \
  --omit=dev --no-audit --no-fund @openai/codex@0.145.0
~/.local/share/arc3-codex/0.145.0/node_modules/.bin/codex login
```

```bash
# Claude Code 2.1.220
curl -fsSL https://claude.ai/install.sh | bash -s 2.1.220
~/.local/share/claude/versions/2.1.220 setup-token
```

> 源码把版本号写进了默认安装路径常量（`PINNED_CODEX_CLI_VERSION` / `DEFAULT_PINNED_CODEX_BIN` / `PINNED_CLAUDE_VERSION` / `DEFAULT_PINNED_CLAUDE_BIN`），因此**版本号必须一字不差**，否则运行时找不到二进制 [F-132]。

## 5. 构建 Docker 镜像

```bash
docker build -t arc3-codex-player:0.1 -f Dockerfile.codex-player .
docker build -t arc3-claude-player:0.1 -f Dockerfile.claude-player .
```

镜像名必须与源码常量 `PLAYER_IMAGE` 一致，否则运行时会找不到镜像 [F-132]。

**自检**：

```bash
docker images | grep -E "arc3-(codex|claude)-player"
```

## 6. 完成检查表

```bash
echo "python : $(.venv/bin/python --version)"      # 3.12.x
echo "codex  : $(codex --version 2>/dev/null || echo 'n/a')"
echo "claude : $(claude --version 2>/dev/null || echo 'n/a')"
echo "docker : $(docker --version)"
echo "tmux   : $(tmux -V 2>/dev/null || echo 'n/a (批量必需)')"
grep -E '^(ARC_API_KEY|ARC_BASE_URL)=' .env | sed 's/ARC_API_KEY=.*/ARC_API_KEY=<已设置>/'
```

| 检查项 | 通过标准 |
|-------|---------|
| Python | 3.12.x |
| CLI | Codex 0.145.0 或 Claude Code 2.1.220，二者至少其一 |
| Docker | 两个 `arc3-*-player:0.1` 镜像之一已构建 |
| `.env` | `ARC_API_KEY` 非空（若只用 offline 模式可跳过） |
| tmux | 仅批量运行需要 |

## 7. 下一步

- 跑通一局 ARC-AGI-3 → [01 ARC-AGI-3 单局与批量](01-arc3-single-and-batch.md)
- 跑其余三个基准 → [02 其余三个基准](02-other-benchmarks.md)

## 相关

- [08 复现与运维](../concepts/08-reproduction-and-operations.md) · [06 源码架构总览](../concepts/06-source-architecture.md)
- [源码快照登记](/references/source-code-map.md)
