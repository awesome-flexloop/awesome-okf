---
okf_version: "0.2"
type: Concept
title: "可组合配方：workspace 成员 + entry points + extras + MCP 的完整插件包方案"
description: "「插件 = workspace 成员包 + entry points 声明 + optional-dependencies extras」的完整可组合配方；MCP Server 作为 workspace 成员的同构方案；版本、测试与升级策略"
tags: [可组合, 插件包, workspace, entry-points, extras, optional-dependencies, MCP]
generated: { by: "agent/seven-concepts-research", at: "2026-10-28T18:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-28T18:00:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: uv-workspaces
    resource: https://docs.astral.sh/uv/concepts/projects/workspaces/
  - id: importlib-metadata
    resource: https://docs.python.org/3/library/importlib.metadata.html
  - id: mcp-spec-2026
    resource: https://modelcontextprotocol.io/specification/2026-07-28
---

# 可组合配方：workspace 成员 + entry points + extras + MCP 的完整插件包方案

uv 官方文档把「带插件系统的库：每个插件是一个独立 workspace 包并依赖根包」列为 workspace 的标准用例。本篇把它展开为可直接套用的完整配方。

## 配方总览：一个插件的四个面

```
agent-plugin-<name>/            # 插件 = workspace 成员包
├── pyproject.toml              # ① 包声明面：[project] + entry-points + extras
├── src/agent_plugin_<name>/
│   ├── __init__.py             # ② 代码面：register() 注册函数
│   └── ...
├── tests/                      # ③ 测试面：独立可测（workspace 允许按成员跑）
└── skills/                     # ④ 知识面（可选）：SKILL.md 渐进披露
```

一个插件包可以同时携带**代码注册**（entry points）、**可选依赖组**（extras）、**知识文件**（SKILL.md）——三形态在包级别合体。

## ① 包声明面：pyproject.toml 三段式

```toml
[project]
name = "agent-plugin-search"
version = "0.3.0"
requires-python = ">=3.12"
dependencies = ["agent-core"]          # 依赖宿主（workspace 内 editable 直连）

[project.entry-points."agent_stack.tools"]     # 进程内注册
web_search = "agent_plugin_search.tools:register"

[project.optional-dependencies]               # 按需重依赖（extras 分组）
local = ["duckduckgo-search>=8"]              # 轻依赖：装
browser = ["playwright>=1.40"]                # 重依赖：可选
```

**extras 的组合语义**：宿主或用户按 `agent-plugin-search[local,browser]` 选择性启用能力梯度——「包可组合」的直接体现：同一插件包，装 `[local]` 是轻量版，装 `[browser]` 解锁浏览器自动化。安装决策从「装不装这个包」细化为「这个包装到什么深度」。

## ② 代码面：注册函数契约

```python
# src/agent_plugin_search/__init__.py
from agent_core.registry import ToolRegistry

def register(registry: ToolRegistry) -> None:
    registry.add_tool(
        name="web_search",
        handler=_run_search,
        description="检索公开网页并返回结构化摘要",
    )
```

宿主的发现循环（[插件发现机制四谱](03-plugin-discovery.md)）：

```python
from importlib.metadata import entry_points

def load_plugins(registry) -> list[str]:
    loaded = []
    for ep in entry_points(group="agent_stack.tools"):
        ep.load()(registry)      # 调用插件的 register()
        loaded.append(ep.name)
    return loaded
```

**契约要点**：插件只做注册不做副作用（import 时零动作，`register()` 被显式调用）；宿主保留开关/优先级/去重的最终裁决权；注册函数签名稳定是插件 API 的兼容性底线。

## ③ 测试面：成员级独立测试

workspace 下每插件可独立测试：`uv run --package agent-plugin-search pytest`（从任意目录执行）。这直接对冲了 uv 官方声明的边界——「uv 无法保证包不偷用别人的依赖」——**用测试强制隔离**：

- 每插件的测试在自己成员的依赖闭包内跑，引用了未声明依赖即 import 失败；
- 宿主侧再跑一层集成测试（全插件装配后的行为）。

## ④ 知识面：SKILL.md 随包分发

插件包内嵌 `skills/` 目录（SKILL.md + 参考文件），安装后由宿主或用户复制/链接到项目的 `.claude/skills/<name>/`。知识（怎么用好这个插件）与代码（插件本体）同版本演进——知识不再漂移于文档仓库之外。

## MCP Server 插件的同构方案

进程间插件同样可以是 workspace 成员，形态同构：

```toml
# agent-mcp-browser/pyproject.toml（workspace 成员）
[project]
name = "agent-mcp-browser"
dependencies = ["mcp>=1.0"]            # MCP Python SDK

[project.scripts]
agent-mcp-browser = "agent_mcp_browser.server:main"   # console script 入口
```

宿主配置层（而非 entry points）负责发现：

```json
{
  "mcpServers": {
    "browser": { "command": "agent-mcp-browser", "args": [] }
  }
}
```

**混合布局建议**：同一仓库内，进程内插件放 `packages/plugins/`（entry points 组统一 `agent_stack.tools`），进程间插件放 `packages/mcp/`（各自 console script）。两类插件共享 workspace 的单一 lockfile——「组合」在依赖层统一裁决，运行时按进程边界分流。

## 版本与升级策略

| 场景 | 策略 |
|------|------|
| 插件间兼容 | 单一 lockfile 天然保证安装一致性；API 兼容靠宿主 `agent-core` 的版本约束（`dependencies = ["agent-core>=0.3,<0.4"]`） |
| 宿主升级 | 插件包在 CI 矩阵里对宿主多版本跑测试（注意 workspace 单一 requires-python 交集的约束，跨大版本测试用 `uv pip` 单独环境） |
| 外发插件 | 独立插件包可发布 PyPI，脱离 workspace 独立版本化——workspace 是开发态拓扑，发布态按包独立 |
| 知识同步 | SKILL.md 随包版本走，changelog 记录知识变更 |

## 反模式清单

1. **插件 import 即副作用**（连数据库、起线程）——破坏宿主对装配顺序的控制，必须收敛到 `register()`。
2. **宿主硬编码插件清单**（`PLUGINS = ["search", "fetch"]`）——退化回手工配置，entry points 的环境即插件集合语义被废弃；清单只允许作为「禁用名单」存在。
3. **重依赖进必装依赖**——浏览器/OCR/DB 驱动必须走 extras，否则安装面不可组合。
4. **插件间直接 import**——绕过宿主 API 形成shadow 耦合；插件只许依赖宿主与公共库。
5. **把不可信能力做成 entry points 插件**——放弃了进程隔离；不可信/第三方一律走 MCP（[插件三形态选型](04-plugin-forms-matrix.md)的故障半径轴）。

## 关键要点回顾

- 完整配方 = workspace 成员（拓扑）+ entry points（注册）+ extras（深度）+ SKILL.md（知识），四合一。
- MCP 插件同构：console script 入口 + 宿主配置发现，与 entry points 插件共享 workspace 依赖裁决。
- 测试强制隔离是 uv 官方声明的「无法保证包间依赖纪律」的工程补位。
- 组合性的三个操作语义：环境即插件集合（换 venv 换插件）、extras 控制安装深度、单一 lockfile 统一版本裁决。
