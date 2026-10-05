---
type: Concept
title: "插件与技能包：双扩展体系"
description: "Octop 的两条扩展轴：kind=tool/hook/skill 插件（PluginManager 装载、plugin.yaml 清单、ctx 三 API、26 个 bundled 实测）与 SkillHub 技能包（2000 文件/64MiB 硬上限、榜单与重试码）。"
tags: [octop, plugin, skill-package, skillhub, plugin-yaml, extension, catalog]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-231~F-242、F-471~F-479（v1.0.2b5）
---

# 插件与技能包：双扩展体系

Octop 有两条正交的扩展轴，初学者很容易混淆：

```
插件（plugin）                     技能包（skill package）
~/.octop/plugins/<id>/             DB 行 + 工作区 skills/ 落盘
plugin.yaml + main.py + ui/        包根必须有 SKILL.md
setup(ctx) 在 Agent 启动时装载      作为知识/指令素材被模型读取
提供 tool / hook(middleware)       不注册可调用工具
        │                                  ▲
        └──────────────┬───────────────────┘
                       └─ kind=skill 插件可把自带技能同步进工作区
```

插件是**代码扩展**（随 Agent 链装载），技能包是**内容扩展**（SKILL.md 驱动的指令素材）。两者唯一的交集是 `kind: skill` 插件：它用 `ctx.skills(...)` 声明一个目录，由 Octop 同步到 Agent 工作区（F-241、F-232）。

## 1. PluginManager：装载、seed 与默认开关

插件子系统位于 `infra/agents/plugins/`，由 manager.py、seed.py、plugin_tool_names.py、plugin_tool_defaults.py、legacy_imports.py 组成。

启动时服务器执行两步（F-166）：`PluginManager.seed_bundled()` 刷新内置副本，随后 `load_installed(install_deps=True)` 装载 `~/.octop/plugins/` 下的已装插件并按需安装依赖。

**seed 只升级、不新装**（F-233）。`seed_bundled_plugins(...)` 的 docstring 明确："Upgrade already-installed bundled plugins when the catalog version is newer."，模块注释为 "not by seed. Seed only refreshes local copies when the catalog version is newer."。逻辑要点：

- 目标目录不存在则跳过（新插件由市场安装，`install_from_market` 当前从树内目录拷贝，未来才支持远程 ZIP）（F-233）；
- 仅当 bundled 版本更高时覆盖：`if _plugin_version(child) <= _plugin_version(dest): continue`（F-233）；
- 覆盖时保留原有 `enabled` 开关位（F-233）；
- config.json 损坏时直接抛错而非按空 dict 合并，避免清空其他设置（issue #730）（F-233）。

默认开关在不同位置有不同答案：市场工具默认补 `{"enabled": True}`（`expand_plugin_tools_default_on`，F-235）；但仓库根 `plugins/` 里 bilibili-anime、server-status 两个目录只各放一个 README，声明「已随安装包分发」，由 `octop init`/`octop run` 复制到 `~/.octop/plugins/<id>/` 且**默认关闭**（F-242）。

### legacy 导入兼容

1.0.2b3 把运行时依赖从 harness-agent 切换为 octop-harness 后，旧插件里的 `import harness_agent` 仍需工作（F-236）：

```python
_PREFIX = "harness_agent"
_TARGET = "octop_harness"
ensure_legacy_harness_agent_alias()
# importlib.util.find_spec(_PREFIX) 为 None 时：
# sys.meta_path.insert(0, _LegacyHarnessAgentFinder())
```

finder/loader 把旧包名别名到新包，这也是 1.0.2b5 CHANGELOG 记载的「旧插件 `harness_agent` 导入」修复点（F-236、F-150）。

## 2. plugin.yaml 清单 schema

清单为插件根目录下的 `plugin.yaml`，由 `yaml.safe_load` 读取。以 bundled weather 插件为实测样本（F-240）：

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

根 `plugins/` 三个 demo 的清单展示了最小字段集——`id/version/name/description/icon/kind/entry`（demo 均无 group/requires/ui）（F-241）。schema 的治理规则：

| 字段 | 规则 |
|------|------|
| `kind` | 实测出现 `tool`/`hook`/`skill` 三种（三个 demo 各一）（F-241） |
| `group` | 稳定分组 slug 限 8 个：lifestyle/news/finance/media/fun/games/tools/ops；未知值仍透传（F-231） |
| `ui.entry` | 缺省 `ui/dist/index.js`；`ui.manifest` 缺省 `ui/dist/manifest.json`；entry 文件缺失则视为纯后端插件返回 None（F-231） |
| ZIP 安装 | 校验头两字节 `head[:2] != b"PK"`，非 ZIP 抛 `PLUGIN_INVALID_ARCHIVE`（F-231） |

入口约定为 `def setup(ctx: PluginContext) -> None:`，三个 demo 与 weather 的 setup 均为此签名（F-240、F-241）。

## 3. ctx 三 API 与「26 个全 tool」的治理取舍

理论上 `PluginContext` 暴露三个注册 API，分别对应三种 kind（F-239、F-241）：

| API | 用途 | 实测样例 |
|-----|------|----------|
| `ctx.tool(...)` | 注册可调用工具 | demo-toolkit 注册 3 个（get_current_time/text_stats/echo_prefix），echo_prefix 带 `config_fields=[{"name":"prefix","type":"text","required":False}]`（F-241） |
| `ctx.middleware(mw, priority=100)` | 注册 LangChain 中间件（hook） | demo-turn-logger 的 `TurnLoggerMiddleware(AgentMiddleware[Any, Any])`，注释原文 "Lower priority runs earlier; 100 is a common default."（F-241） |
| `ctx.skills("skills")` | 声明技能目录（不注册工具） | demo-greeting-skill，目录含 `skills/polite-greeting/SKILL.md`（F-241） |

但对 `bundled/` 的实测呈现出鲜明的治理取舍（2026-10-04，PowerShell 逐目录清点，F-237、F-239）：

- bundled 下 **26 个插件子目录、26 个 plugin.yaml，kind 全部是 `tool`（26/26）**；
- 每个目录都齐备四件套：`main.py`（26）、`icon.svg`（26）、`ui/index.js`（26）；
- 全量 .py 扫描：`ctx.tool(` 命中 26 个文件共 33 处，`ctx.skills` 命中 0 文件，`ctx.middleware` 命中 0 文件。

即：hook 与 skill 两种扩展点已在平台层打通并有示例，但**官方随包的 26 个插件全部是纯工具插件**，UI 卡片通过工具返回值承载，不向 Agent 链注入中间件。

### group 分布（26 个 bundled）

| group | tools | lifestyle | fun | news | games | media | finance | ops |
|-------|------:|----------:|----:|-----:|------:|------:|--------:|----:|
| 数量 | 8 | 5 | 4 | 3 | 2 | 2 | 1 | 1 |

来源：F-238。市场列表条目 dict 含 id/version/name/kind/description/icon/group/requires/installed/installed_version/update_available 等键（F-232）。

## 4. 工具名清洗与 octop_ui 信封

插件工具名要进 LLM，必须可预测。`plugin_tool_names.py` 的规则（F-234）：

```python
_LLM_TOOL_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
_MAX_NAME_LEN = 64
# 冲突加 _2/_3 后缀；超长截到 60 字符并兜底 "plugin_tool"
# 原名保留前缀："[原名: {name}] "
```

UI 渲染走统一信封。weather 插件的 `_payload` 返回逐字 JSON（F-240）：

```json
{"octop_ui": {"renderer": renderer, "version": 1}, "data": data, "text": text}
```

demo-ui-card 的 renderer 字面为 `"demo_card"`（F-241）。harness 侧还有 `OctopUiOffloadMiddleware`：当 data 超过 `_OFFLOAD_MIN_CHARS = 4000` 时把大 payload 移到 `ToolMessage.artifact`，content 只留 `{"data_ref": "artifact"}`，防止撑爆模型上下文（F-230）。

## 5. 技能包体系

技能包子系统位于 `infra/skills/`，按职能可分六块（F-471~F-479）：

| 职能块 | 模块 | 职责 |
|--------|------|------|
| ① 校验/上限 | `skill_packages.py` | 源中立的包校验与路径归一（F-472） |
| ② 落盘协议 | `install.py` | `SkillInstallTarget` Protocol（skill_exists/write_files/after_install 三方法）；异常 `SkillAlreadyExistsError`；octop_meta 写 `source="skillhub"`（F-477） |
| ③ DB/包 id | `skill_package_store.py` | 包 id 调 `new_short_id` 重试 16 次，冲突判定靠 skill_packages 表 name 唯一约束（F-478） |
| ④ 导入导出 | `skill_transfer.py` | 异常 `SkillTransferConflict`/`SkillTransferNotFound`；目录环检测；manifest 的 removed 键按路径存活判定（F-478） |
| ⑤ SkillHub 建包 | `skill_package_from_skillhub.py` | `create_package_from_skillhub` 失败时调 `delete_package` 回滚（F-478） |
| ⑥ 市场与下载 | `skillhub_common.py` / `skillhub_market.py` / `skills_hub.py` | host、安全上限、榜单、URL 导入与重试（F-471、F-473~F-476） |

### 5.1 三道硬上限

包校验与 ZIP 下载共享同一组数字（F-471、F-472）：

```python
# skill_packages.py
MAX_SKILL_FILES = 2_000
MAX_SKILL_BYTES = 64 * 1024 * 1024
# skillhub_common.py
MAX_HTTP_BYTES = 32 * 1024 * 1024          # HTTP 直读上限 32 MiB
MAX_ZIP_ENTRIES = 2_000
MAX_ZIP_UNCOMPRESSED_BYTES = 64 * 1024 * 1024
MAX_ZIP_COMPRESSION_RATIO = 100.0          # zip 炸弹比率上限 100
HTTP_READ_CHUNK = 64 * 1024
```

包根必须存在可按 UTF-8 解码的 `SKILL.md`；拒绝绝对路径与 `..` 路径段、拒绝符号链接；CLI 一次传多个包直接报错（F-472）。超限报错文案逐字为 `"SkillHub package uncompressed size exceeds 64 MB"`（F-474）。

### 5.2 SkillHub：host、榜单与重试码

```python
DEFAULT_SKILLHUB_HOST = "https://api.skillhub.cn"   # 可被 SKILLHUB_HOST 覆盖
SEARCH_ENDPOINT   = "/api/v1/search"
DOWNLOAD_ENDPOINT = "/api/v1/download"
RANKING_ENDPOINTS = 6 个：hot/featured/newest/recommended/trending/paid
                     # 前缀 /api/v1/showcase/
```

User-Agent 字面 `"octop-skillhub-market/1.0"`；搜索/下载 httpx 超时为 30/10/30/10 秒四档（F-473、F-474）。

第三方技能 URL 导入仅接受 4 个 https 域名前缀：`skills.sh`、`clawhub.ai`、`skillsmp.com`、`github.com`，可用 `OCTOP_SKILLS_IMPORT_URL_PREFIXES` 覆盖（F-475）。可重试 HTTP 状态码 8 个：408/409/425/429/500/502/503/504；超时由 `OCTOP_SKILLS_HUB_HTTP_TIMEOUT` 控制（默认 15、下限 3），retries 默认 3（F-476）。

### 5.3 展示与工作区目录

`presentation.py` 内置 5 个扩展命名空间：octop、harness、lightclaw、orca、openclaw，本地化回退顺序 locale → en → zh（F-479）。`workspace_catalog.py` 把工作区散落技能标为 kind `"workspace"`，损坏包标 corrupt，错误码有 `"missing"` 与 `"invalid_utf8"`（F-479）。插件同步技能到工作区时，目标已存在 `SKILL.md` 则跳过，避免覆盖用户改动（F-232）。

## 相关概念

- [/concepts/12-agent-runtime-internals.md](12-agent-runtime-internals.md)——插件中间件如何进入 Agent 链
- [/concepts/02-agent-runtime.md](02-agent-runtime.md)——PluginManager 在启动流程中的位置
- [/concepts/15-backup-and-storage.md](15-backup-and-storage.md)——plugins 与 skill-packages 是备份六目录之二
