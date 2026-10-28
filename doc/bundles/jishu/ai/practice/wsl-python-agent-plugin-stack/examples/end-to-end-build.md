---
okf_version: "0.2"
type: Example
title: "端到端实战：从 Win11 裸机到可组合插件栈"
description: "五阶段搭建路径——WSL 安装与配置基线、uv 安装与 workspace 初始化、宿主框架与两个 entry points 插件、MCP Server 插件装配、验证与发布清单"
tags: [实战, WSL, uv, workspace, entry-points, MCP, 验证清单]
generated: { by: "agent/seven-concepts-research", at: "2026-10-28T18:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-28T18:00:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: ms-wsl-config
    resource: https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config
  - id: uv-workspaces
    resource: https://docs.astral.sh/uv/concepts/projects/workspaces/
---

# 端到端实战：从 Win11 裸机到可组合插件栈

本篇给出完整搭建路径的**决策点与命令基线**。前置阅读：[技术栈总架构](../concepts/00-stack-architecture.md)。WSL 安装细节（`wsl --install` 等）见 [WSL 子系统中文教程](../../../systems/wsl/index.md)。

## 阶段一：WSL 底座（约 15 分钟）

```powershell
# Windows 侧（PowerShell）
wsl --install -d Ubuntu-24.04
wsl --version          # 确认 Store 版 WSL（systemd 支持）
```

**配置基线**（两个文件的建议稿，进 git 仓库的 `docs/env/` 目录作为团队约定）：

```ini
# .wslconfig（%UserProfile%\.wslconfig，Windows 侧全局 VM）
[wsl2]
memory=8GB                 # 上限防挤占宿主（默认是宿主 50%）
processors=4
networkingMode=mirrored    # Win11 22H2+：localhost 双向互通
autoMemoryReclaim=gradual  # 缓存内存渐进回收
[experimental]
sparseVhd=true             # 新 VHD 自动稀疏，控磁盘膨胀
```

```ini
# /etc/wsl.conf（发行版内）
[boot]
systemd=true               # 长驻服务交给 systemd
[interop]
appendWindowsPath=false    # 阻止 Windows PATH 注入，减少同名命令错绑
```

修改后执行 `wsl --shutdown`，等约 8 秒再启动（配置生效的 8 秒规则）。

**布局纪律**：工作区放 `~/agent-stack/`（Linux ext4，原生 IO 性能）；`/mnt/c` 仅作与 Windows 的成果物交换区。

## 阶段二：uv 与 workspace 初始化（约 5 分钟）

```bash
# WSL 内
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12     # 解释器层：多版本管理

mkdir -p ~/agent-stack && cd ~/agent-stack
uv init --package agent-stack            # 根（宿主应用）
mkdir -p packages/plugins packages/mcp
uv init --package packages/plugins/agent-plugin-search
uv init --package packages/plugins/agent-plugin-report
uv init --package packages/mcp/agent-mcp-browser
```

根 `pyproject.toml` 落成 workspace 声明：

```toml
[tool.uv.workspace]
members = ["packages/plugins/*", "packages/mcp/*"]

[tool.uv.sources]
agent-plugin-search = { workspace = true }
agent-plugin-report = { workspace = true }
```

`uv lock && uv sync` —— 单一 `uv.lock` 锁定全仓（含全部插件成员）。

## 阶段三：宿主 + entry points 插件（进程内轴）

**宿主发现循环**（`src/agent_stack/registry.py`）：

```python
from importlib.metadata import entry_points

def load_plugins(registry):
    for ep in entry_points(group="agent_stack.tools"):
        ep.load()(registry)
```

**插件注册声明**（`packages/plugins/agent-plugin-search/pyproject.toml`）：

```toml
[project.entry-points."agent_stack.tools"]
web_search = "agent_plugin_search:register"

[project.optional-dependencies]
local = ["duckduckgo-search>=8"]     # extras：安装深度可组合
```

```bash
uv add --package agent-plugin-search duckduckgo-search   # 或走 extras
uv run --package agent-plugin-search pytest              # 成员级独立测试
```

## 阶段四：MCP Server 插件（进程间轴）

`packages/mcp/agent-mcp-browser/pyproject.toml`：

```toml
[project]
name = "agent-mcp-browser"
dependencies = ["mcp>=1.0"]

[project.scripts]
agent-mcp-browser = "agent_mcp_browser.server:main"
```

宿主侧注册（stdio 传输，本地子进程）：

```json
{
  "mcpServers": {
    "browser": { "command": "agent-mcp-browser", "args": [] }
  }
}
```

**进程边界对照验证**：kill 掉 `agent-mcp-browser` 进程，宿主应降级（该工具不可用）而非崩溃；同 venv 卸载 `agent-plugin-search` 后 `entry_points()` 枚举自然消失（环境即插件集合）。

## 阶段五：验证与发布清单

**环境自由验证（重建演练）**：

```bash
# 1. 快照 OS 层（可选加速）
wsl --export Ubuntu-24.04 D:\backups\agent-env.tar

# 2. 新机器/新实例重建
wsl --import agent-stack-2 D:\wsl\agent-stack-2 D:\backups\agent-env.tar
git clone <repo> ~/agent-stack && cd ~/agent-stack
uv sync          # uv.lock 精确复现依赖闭包
uv run agent-stack --check-plugins
```

**发布前自检清单**：

| # | 检查项 | 通过标准 |
|---|--------|---------|
| 1 | 插件 import 零副作用 | `python -c "import agent_plugin_search"` 无输出无网络活动 |
| 2 | 注册契约稳定 | 插件全部经 `register(registry)` 注册，无直连宿主内部模块 |
| 3 | extras 梯度安装 | `[local]`/`[browser]` 两档安装各自可用 |
| 4 | 成员级测试 | 每插件 `uv run --package <name> pytest` 绿 |
| 5 | 集成测试 | 全插件装配后宿主行为测试绿 |
| 6 | MCP 故障降级 | kill MCP Server 进程宿主不崩 |
| 7 | 依赖闭包锁定 | `uv.lock` 已提交，CI 用干净缓存 `uv sync --frozen` 复现 |
| 8 | 布局纪律 | 仓库、venv、缓存均在 Linux ext4 侧 |
| 9 | 不可信隔离 | 第三方能力全部走 MCP，无一进入 entry points 组 |
| 10 | 知识面随包 | SKILL.md 随插件包版本演进，changelog 有记录 |

## 常见故障速查

| 症状 | 根因方向 |
|------|---------|
| `uv sync` 在 `/mnt/c` 下极慢 | 仓库放 Windows 文件系统，9P 跨界 IO——迁回 `~/` |
| 插件装了没生效 | venv 不对（环境即插件集合）或 entry points 组名拼写不一致 |
| systemd 服务没起来 | `wsl.conf` 改后没做 `wsl --shutdown` + 8 秒等待 |
| mirrored 网络不生效 | Windows 版本低于 22H2，回退 NAT + localhostForwarding |
| 成员 requires-python 冲突 | workspace 取交集；跨版本测试用 `uv pip` 单独环境 |

## 关键要点回顾

- 五阶段节奏：WSL 基座（15min）→ uv workspace（5min）→ 宿主与进程内插件 → MCP 插件 → 重建演练。
- 两条验证主线：组合性（故障降级/环境即插件集合）与自由度（export/import + uv.sync 重建）。
- 十项发布清单是「环境自由 + 包可组合」两个维度目标的操作化检验。
