---
type: Example
title: "插件开发：从 tool 骨架到 UI 卡片"
description: "以仓库 plugins/ 下四个 demo 为样板，编写 tool/skill/hook 三类插件：目录约定、plugin.yaml 字段、ctx.tool 注册、octop_ui 卡片信封，以及安装启用与排错。"
tags: [octop, plugin, tool, ui-card, skill, hook]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: plugin
    resource: /concepts/13-plugin-system.md
    title: 插件系统
  - id: dashboard
    resource: /concepts/19-dashboard-frontend.md
    title: Dashboard 前端
---

# 插件开发：从 tool 骨架到 UI 卡片

本示例演示如何从零写一个 Octop 插件，并在聊天里渲染自定义卡片。所有代码与字段均取自仓库自带 demo（v1.0.2b5，`plugins/` 目录）。

## 场景与前置条件

- 已安装 Octop，`octop --version` 可用；开发机有 Python 3.12 环境
- 插件目录最终安装到 `~/.octop/plugins/<plugin-id>/`（F-231）
- 仓库根 `plugins/` 下实测有四个 demo，可直接复制当骨架：

| 目录 | `kind` | 注册内容 |
|------|--------|----------|
| `plugins/demo-toolkit` | `tool` | 3 个工具：get_current_time、text_stats、echo_prefix（F-241） |
| `plugins/demo-turn-logger` | `hook` | 1 个 `TurnLoggerMiddleware`，`priority=100`（F-241） |
| `plugins/demo-ui-card` | `tool` | 1 个工具，返回 `demo_card` 渲染器信封（F-241） |
| `plugins/demo-greeting-skill` | `skill` | 同步 `skills/polite-greeting/SKILL.md`（F-241） |

## 1. 目录约定

一个插件是独立文件夹，至少包含 `plugin.yaml` 与入口 `main.py`。随安装包分发的完整产品插件（如 `bundled/weather`）是「四件套」形态（F-240）：

```text
weather/
├── plugin.yaml      # 清单：id/version/name/icon/group/kind/entry/requires/ui
├── main.py          # 必须定义 setup(ctx: PluginContext)
├── icon.svg         # 清单 icon: icon.svg 指向的图标
└── ui/
    ├── index.js     # 卡片前端 ESM
    └── manifest.json
```

注意仓库根 demo 的实测差异：`demo-toolkit` 只有 `main.py` + `plugin.yaml`，图标用 emoji（`icon: "🧰"`）；`demo-ui-card` 的清单声明 `ui.entry: ui/dist/index.js`，但该前端产物未提交进仓库（由打包流程提供），缺失时后端按「无 UI」处理。

## 2. 编写 plugin.yaml

`demo-toolkit/plugin.yaml` 逐字：

```yaml
id: demo-toolkit
version: 0.1.0
name: Demo Toolkit
description: Sample tool plugin (kind=tool) — current time, text stats, configurable echo prefix
icon: "🧰"
kind: tool
entry: main.py
```

带 UI 与依赖的完整清单可参考 `bundled/weather/plugin.yaml`（F-240）：

```yaml
id: weather
version: 0.2.2
name: 天气
description: 查询全球城市天气与未来预报，在聊天中展示天气卡片
icon: icon.svg
group: lifestyle
kind: tool
entry: main.py
requires:
  - httpx>=0.27
ui:
  entry: ui/index.js
  manifest: ui/manifest.json
```

字段要点：

- `id` / `version` / `name` / `kind` / `entry` 为必备项；`kind` 实测取值 `tool`、`hook`、`skill`（bundled 目录 26 个插件全部为 `tool`，F-237）
- `group` 用于 Dashboard 分组，合法 slug 共 8 个：lifestyle、news、finance、media、fun、games、tools、ops（F-231）；未知值仍会透传
- `icon` 可填 emoji、`http(s)://`/`/api/` URL 或插件内相对路径（如 `icon.svg`）；`ui.entry`/`ui.manifest` 缺省 `ui/dist/index.js`、`ui/dist/manifest.json`（F-231），路径含 `..` 或文件缺失时忽略 UI 段

## 3. 在 main.py 注册工具

`demo-toolkit/main.py` 的注册段逐字：

```python
from octop_harness.plugins import PluginContext, get_tool_config


async def echo_prefix(message: str) -> str:
    """Echo a message with an optional admin-configured prefix."""
    cfg = get_tool_config("echo_prefix") or {}
    prefix = str(cfg.get("prefix") or "")
    return f"{prefix}{message}"


def setup(ctx: PluginContext) -> None:
    # 另两个工具 get_current_time / text_stats 同形注册，此处从略
    ctx.tool(
        "echo_prefix",
        echo_prefix,
        description="Echo a message with a configurable prefix",
        config_fields=[
            {"name": "prefix", "type": "text", "required": False},
        ],
    )
```

约定（F-241）：

- 入口文件必须定义 `setup(ctx)`；工具函数可以是 `async def`，函数参数即 Agent 调用 schema
- `ctx.tool(name, fn, description=..., config_fields=...)` 注册可调用工具
- `config_fields` 声明的字段不是 Agent 参数，而是在 Dashboard「工具管理」里逐 Agent 编辑，运行时用 `get_tool_config("<tool_name>")` 读取
- 工具名需匹配 LLM 工具命名规则 `^[a-zA-Z0-9_-]{1,64}$`；冲突时自动加 `_2`/`_3` 后缀并截断到 64 字符（F-234）

## 4. 返回 UI 卡片（octop_ui 信封）

`demo-ui-card/main.py` 的工具逐字：

```python
async def demo_ui_card(title: str = "Hello from plugin UI", count: int = 1) -> str:
    """Return a structured card payload for the Dashboard plugin renderer."""
    payload = {
        "octop_ui": {"renderer": "demo_card", "version": 1},
        "data": {
            "title": title,
            "count": int(count),
            "note": "Click Refresh on the card to patch this result (L2).",
        },
        "text": f"{title} (count={count})",
    }
    return json.dumps(payload, ensure_ascii=False)
```

信封三键：`octop_ui.renderer` 与前端注册的渲染器对应（此处为 `demo_card`，F-241），`data` 是卡片数据，`text` 是纯文本回退。Dashboard 通过 `GET /api/plugins/{id}/ui/…` 加载 ESM 并调用其 `setup(host)` 注册渲染器；`host.patchResult(callId, data)` 可不重跑 LLM 直接刷新气泡。bundled 的 weather 插件返回同一信封形态（`{"octop_ui": {"renderer": renderer, "version": 1}, "data": data, "text": text}`，F-240）。

## 5. skill 与 hook 型插件

- **skill**：`demo-greeting-skill/main.py` 全文仅 `ctx.skills("skills")`（相对插件根），携带 `skills/polite-greeting/SKILL.md`；Agent 启动时同步进工作区 `skills/`，已存在则跳过（F-232、F-241）。SKILL.md 须可按 UTF-8 解码（F-472）。
- **hook**：`TurnLoggerMiddleware(AgentMiddleware[Any, Any])` 经 `ctx.middleware(TurnLoggerMiddleware(), priority=100)` 注册；注释逐字「Lower priority runs earlier; 100 is a common default.」（F-241）。bundled 26 个官方插件中 `ctx.tool(` 命中 26 文件 33 处而 `ctx.skills`/`ctx.middleware` 为 0（F-239）——两 API 仅 demo 使用，升级大版本时建议回归。

## 6. 安装、启用与验证

```bash
# 从本地目录安装（开发时最常用）
octop plugin install ./plugins/demo-toolkit --force
octop plugin list
# - demo-toolkit v0.1.0 (tool) [loaded]
```

安装后启用分两级：

1. **全局开关**：`config.json` 的 `plugins.<id>.enabled`；管理员可 `PATCH /api/plugins/demo-toolkit`，请求体 `{"enabled": true}`（需 plugins 权限）。CLI/市场安装缺省即启用；`seed_bundled` 只升级已装插件、不自动复制新插件（F-233），随包 README 则声明产品插件在 `octop init`/`octop run` 时复制且默认关闭、卸载过的 id 不会装回（F-242）
2. **Agent 级开关**：`PATCH /api/plugins/agents/<agent-id>`，请求体 `{"plugins": {"demo-toolkit": {"enabled": true}}}`；tool 型还要在工具管理里逐个工具启用，`GET /api/plugins/agents/<agent-id>/tools` 可查清单

运行中的服务装新插件后，调 `POST /api/plugins/reload` 或重启 `octop run`。

## 排错

| 现象 | 原因与处理 |
|------|-----------|
| 安装 ZIP 报 `BadZipFile`/「file is not a valid ZIP archive」 | 用了 GitHub `/blob/` 页面地址；安装器只认头两字节为 `PK` 的 ZIP，改用 `raw.githubusercontent.com` 直链（F-231） |
| 插件列表显示 `not loaded` | 全局开关关闭或 `main.py` 导入失败；查 `~/.octop/logs/octop.log` 中 `failed to load plugin` 堆栈 |
| 旧插件 `import harness_agent` 报错 | 加载器已注入兼容别名，把 `harness_agent` 重定向到 `octop_harness`（F-236）；新代码请直接 import `octop_harness.plugins` |
| UI 卡片不渲染、只显示 text | `plugin.yaml` 的 `ui.entry` 文件缺失（demo-ui-card 的 ui/dist 需自行构建），或 renderer 名与信封 `octop_ui.renderer` 不一致 |
| 改了代码不生效 | `octop plugin install <dir> --force` 重装，再 `POST /api/plugins/reload`；ZIP 内只能有一个带 `plugin.yaml` 的插件根目录 |
| Agent 看不到工具 | 全局开关、Agent 级开关、工具级开关三层都要打开；工具名非法字符会被归一化，超长名兜底为 `plugin_tool`（F-234） |

## 相关概念

- [/concepts/13-plugin-system.md](../concepts/13-plugin-system.md)
- [/concepts/19-dashboard-frontend.md](../concepts/19-dashboard-frontend.md)
