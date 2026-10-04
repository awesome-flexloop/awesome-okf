---
type: Reference
title: "Octop v1.0.2b5 源码地图与构建清单"
description: "Octop 1.0.2b5（commit e473dd3c，MIT）仓库顶层地图、src/octop 四大区、infra 二十子域、CLI/API 子树、dashboard/桌面构建链与 Docker/fnos 部署面的信源登记。"
tags: [octop, source-map, build, hatchling, packaging, deployment]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-134~F-205、F-556~F-565、F-566~F-592（v1.0.2b5，commit e473dd3c）
---

# Octop v1.0.2b5 源码地图与构建清单

本信源登记 Octop 仓库 v1.0.2b5（`__version__ = "1.0.2b5"`（F-134），MIT 许可（F-135））的目录布局、构建分发面与部署面。所有文件计数除标注 F 事实外，均为 2026-10-04 对源码工作树的 Glob/Grep 实测（下文简称「源码实测」）。

## 1. 版本与分发面

### 1.1 版本锚点

| 项 | 逐字值 | 信源 |
|---|---|---|
| `src/octop/__init__.py:5` | `__version__ = "1.0.2b5"` | F-134 |
| 模块 docstring | `Octop — smarter self-hosted AI assistant (multi-user, multi-agent).` | F-134 |
| pyproject `name` / `version` | `octop` / `1.0.2b5` | F-135 |
| `requires-python` | `>=3.12"` | F-135 |
| license | `{ text = "MIT" }` | F-135 |
| description | `Smarter self-hosted AI assistant for multiple users and agents, built on octop-harness` | F-135 |
| 入口脚本 | `octop = "octop.cli.main:cli"` | F-135 |
| 构建后端 | hatchling：`requires = ["hatchling>=1.18"]`、`build-backend = "hatchling.build"` | F-135 |
| 版本节奏 | `[1.0.0] 2026-09-14` GA → 1.0.1（09-18）→ 1.0.2b1/b2/b3/b4/b5（09-22 至 09-29） | F-145~F-150 |

### 1.2 四个 octop-* 运行时包

运行时依赖中四个包逐字约束为（F-136）：`octop-harness[all]>=1.0.0`、`octop-memory>=1.0.0`、`octop-gateway>=1.0.0`、`octop-browser>=1.0.0`；对 `pyproject.toml` 与 `uv.lock` 全文件 grep 旧名 `orcakit|harness-agent|harness-memory|harness-gateway|harness-browser` 命中数为 0（F-136）。1.0.2b3 CHANGELOG 逐字记载「运行时依赖切换为 octop-harness / octop-gateway / octop-memory / octop-browser 1.0.0」（F-149）。

`uv.lock` 解析版本钉扎（name/version 行，source 均为 `https://pypi.org/simple`）（F-140）：

| 包 | 钉扎版本 | 包 | 钉扎版本 |
|---|---|---|---|
| acme | 5.6.0 | octop-browser | 1.0.0 |
| boto3 | 1.40.61 | octop-gateway | 1.0.0 |
| fastapi | 0.138.2 | octop-harness | 1.0.0 |
| langchain-core | 1.6.0 | octop-memory | 1.0.0 |
| langgraph-checkpoint-postgres | 3.1.0 | playwright | 1.61.0 |
| mcp | 1.28.1 | psycopg | 3.3.4 |

`octop-harness 1.0.0` 的 `[package.optional-dependencies].all` 含 15 项：agent-client-protocol、cos-python-sdk-v5、deepagents-backends、docker、esdk-obs-python、google-api-python-client、langchain-aws、langchain-community、langchain-tavily、langfuse、mss、oss2、pillow、psutil、pynput（F-141）。

### 1.3 其余核心依赖与 extras 分组

核心依赖逐字清单（`pyproject.toml:13-48`）含：`fastapi>=0.110`、`uvicorn[standard]>=0.27`、`pydantic>=2.6,<2.14`、`langchain-core>=1.4.8`、`click>=8.1`、`rich>=13.7`、`questionary>=2.0`、`apscheduler>=3.10,<4`、`argon2-cffi>=23.1`、`pyjwt>=2.8`、`lark-oapi>=1.7.3`、`cryptography>=41`、`scalar-fastapi>=1.0`、`edge-tts>=6.1`、`segno>=1.6`、`websockets>=13.0`、`acme>=5.6.0`、`josepy>=2.2.0`、`boto3>=1.40.61`、`playwright>=1.40`、`psycopg[binary]>=3.2`、`langgraph-checkpoint-postgres>=2.0`、`mcp>=1.9,<2`、`pillow>=10.0`、`pypdf>=5.0`、`python-docx>=1.2.0`、`python-pptx>=1.0`、`pypinyin>=0.53`、`openpyxl>=3.1`、`xlrd>=2.0.1`（F-137）。

`[project.optional-dependencies]` 下实测 5 个 extras 键（F-138 计数句作「4 个」，但其逐字枚举止于 `knowledge-ocr` 共列出 5 组；以 pyproject 源码为准为 5 组）：

| extras | 内容 | 备注 |
|---|---|---|
| `dev` | pytest/pytest-asyncio/pytest-cov/pytest-testmon/pytest-xdist/httpx/ruff/mypy/build/xlwt（10 项） | 与 PEP 735 `[dependency-groups].dev` 逐项相同（F-138） |
| `browser` | `playwright>=1.40` | 注释「Kept for backward compatibility; playwright is now a core dependency.」（F-138） |
| `desktop` | `mss>=9.0`, `pynput>=1.7` | 向后兼容保留（F-138） |
| `local-embedding` | `fastembed>=0.4`, `huggingface_hub>=0.20` | 本地 ONNX/fastembed 嵌入（F-138） |
| `knowledge-ocr` | `rapidocr>=3.4,<4`, `onnxruntime>=1.17`, `pymupdf>=1.24` | 知识库 OCR（F-138） |

### 1.4 hatch 打包面

wheel 目标 `packages = ["src/octop"]`（F-139）。`[tool.hatch.build] include` 实测逐字 12 条（源码实测，`pyproject.toml:101-118`）：

```
src/octop/**/*.py        src/octop/**/*.json     src/octop/**/*.md
src/octop/**/*.sql       src/octop/**/*.sh       src/octop/**/*.png
src/octop/dashboard/**/*
src/octop/infra/agents/experts/library/**/*
src/octop/infra/agents/plugins/bundled/**/*
src/octop/infra/agents/subagents/library/**/*
src/octop/infra/agents/subagents/divisions.json
src/octop/infra/desktop/scripts/**/*
```

`artifacts = ["src/octop/dashboard/**/*"]`（F-139）。注意：源码工作树中 `src/octop/dashboard/` 目录当前**不存在**（Glob 实测 0 文件），该目录由 dashboard 构建产物在打包时生成（见 §7）。pytest 配置 `testpaths = ["tests"]`、`asyncio_mode = "auto"`，markers 为 `live`/`slow`/`postgresql`（F-139）。

### 1.5 mise 工具链与 Makefile

`mise.toml [tools]` 钉扎（F-142）：`python = "3.12"`、`node = "20"`、`npm = "10"`、`uv = "latest"`；注释声明 python 3.12 跟随 CI/Makefile，node 20 跟随 docker/Dockerfile 与 release.yml，`octop-desktop.yml` 用 node 24（F-142）。

Makefile 关键目标（F-144）：`build = build-frontend + build-wheel`（前端产物从 `dashboard/` 输出到 `src/octop/dashboard`）；`publish`/`publish-test`（twine，PYPI_REPO 默认 pypi）；`install-online` 建 `.venv-online`（`uv venv --python 3.12` + `uv pip install --no-sources -e ".[dev]"`）；`test = pytest -n auto -m "not live"`；`typecheck = mypy src/octop`。

## 2. 仓库顶层地图

两层深度目录树（源码实测；仅列与构建/运行相关条目）：

```text
Octop/
├── src/octop/                  # 主包（hatch packages 根）
│   ├── api/                    # FastAPI 控制面（app.py/deps.py/openapi_meta.py + common/middleware/routers）
│   ├── cli/                    # click CLI（main.py/registry.py + commands/repl/support）
│   ├── i18n/                   # 中英文案（zh.json/en.json + domains/ 11 个域模块）
│   ├── infra/                  # 领域层（server.py/errors.py/metrics.py + 20 个子域）
│   ├── __init__.py             # __version__ = "1.0.2b5"
│   ├── __main__.py             # python -m octop → cli()
│   ├── config.py               # OctopConfig 及全部子 dataclass
│   └── launch.py               # 唯一组合根（161 行）
├── dashboard/                  # React 18 + Vite 6 + antd 5 前端（构建到 ../src/octop/dashboard）
├── desktop/
│   ├── src/                    # Go 1.25 + Wails v3 桌面壳（module octop.desktop，30 个 .go）
│   └── portable/               # 绿色便携包打包（templates/launch.py + Makefile + shell 脚本）
├── docker/                     # Dockerfile（两阶段）、3 套 compose、entrypoint、postgres/init-vector.sql
├── fnos/                       # 飞牛云应用模板：docker/ 与 native/ 两套 manifest（均 0.9.15）
├── plugins/                    # 6 个示例插件/技能（bilibili-anime、demo-* ×4、server-status）
├── docs/                       # 18 个根级 .md + adr/ 2 个（001/002），共 20 md
├── scripts/                    # 安装器（sh/ps1/bat）、wheel/fpk 构建、smoke_memory_api.py 等
├── pyproject.toml / uv.lock    # hatchling 构建 + uv 锁
├── mise.toml / Makefile        # 工具链与任务入口
├── .env.example                # 运行时环境变量样板
├── CHANGELOG.md                # 1.0.0 GA ~ 1.0.2b5
├── README.md / README_CN.md / AGENTS.md / CONTRIBUTING.md / SECURITY.md
├── LICENSE                     # MIT
└── conftest.py
```

顶层各目录角色：

| 目录/文件 | 角色 | 信源 |
|---|---|---|
| `src/octop/api/` | FastAPI 控制面：app 工厂、依赖注入、中间件、81 个 routers py | F-503~F-555 |
| `src/octop/cli/` | click 命令面：22 个命令 + REPL + 离线/嵌入式支持层 | F-556~F-565 |
| `src/octop/i18n/` | i18n 文案：`loader.py` + `zh.json`/`en.json` + `domains/` 11 个域 | 源码实测 |
| `src/octop/infra/` | 领域层：进程编排、DB、网关、代理、全部业务子域 | F-163~F-202 |
| `src/octop/config.py` | `OctopConfig` frozen dataclass（19 字段）与 env/文件解析 | F-151~F-159 |
| `src/octop/launch.py` | 唯一同时 import `infra/server` 与 `api/app` 的组合根，161 行 | F-160~F-162、F-205 |
| `src/octop/__main__.py` | `python -m octop` → `from octop.cli.main import cli; cli()`（源码实测，7 行） | 源码实测 |
| `dashboard/` | PWA 前端；name `octop-dashboard`、version `0.1.0` | F-566~F-575 |
| `desktop/` | Wails v3 桌面壳与多平台绿色便携包 | F-576~F-585 |
| `docker/` | 两阶段镜像（node:20-slim + python:3.12-slim）、三套 compose、entrypoint | F-586~F-589 |
| `fnos/` | 飞牛云 docker/native 双形态应用模板（含 cmd 回调、wizard、ui/config） | F-590 |
| `plugins/` | 随仓示例插件（含 `demo-toolkit`/`demo-turn-logger`/`demo-ui-card` 带 plugin.yaml） | 源码实测 |
| `docs/` | 用户文档 20 md：api/cli/architecture/bridge/memory-slim 等 + ADR 001/002 | F-591、F-592 |
| `scripts/` | `install.sh`/`install.ps1`/`install.bat`/`install-octop.sh`、`wheel_build.*`、`build-fpk.sh`、`smoke_memory_api.py`、`release_download_links.py`、`fnos/common.sh` | 源码实测 |

## 3. `src/octop/infra/` 二十个子域

Glob `infra/<子域>/**/*.py` 实测计数（含 `__init__.py` 与子目录嵌套文件，2026-10-04）：

| # | 子域 | .py 数 | 职责（据 F 事实与目录文件名概括） | 关键构成 |
|---|---|---:|---|---|
| 1 | `agents/` | 165 | Agent 运行时核心：AgentManager、线程/工作区、teams、provider 工厂、插件、专家库、人格/MBTI、记忆瘦身、安全中间件 | `manager.py`、`conversation_mode.py`；子包 teams(5)/threads(4)/workspace(3)/providers(14)/plugins(6+bundled 25 个 main.py)/experts(9+library 技能脚本)/persona(3)/memory(4)/middleware(7)/security(4)/settings(7)/subagents(1)+library、builtin_skills |
| 2 | `auth/` | 20 | 认证域：SSO(OIDC/OAuth) 与登录验证码 | `sso/`(8，service/pkce/id_token/crypto/discovery/redirect_after/public_base)+`sso/providers/`(6：base/oidc/feishu/dingtalk/wecom)+`captcha/`(5：config/store/providers/verify) |
| 3 | `backend/` | 7 | Agent 执行后端适配（容器/沙箱探测） | adapter、browse、probe、resolver、docker_spec、opensandbox_deps |
| 4 | `backup/` | 9 | 备份/恢复/归档 | snapshot、manifest、store、auto（定时备份）、pg_dump、workspace_archive、system_archive、chats |
| 5 | `bridge/` | 9 | Octop↔Octop 云端桥接（1.0.2b5 新增） | manager、http_tunnel、transport、peer_auth、crypto、tunnel_policy、ids、icons |
| 6 | `browser/` | 2 | 浏览器运行环境安装/配置 | setup.py（+`__init__.py`）；浏览器媒体/空闲超时常量在 `utils/browser_media.py`（F-168 ①） |
| 7 | `connectors/` | 42 | 外部连接器：自定义 MCP、企查查、邮件、OAuth、网关 CLI 适配 | 根 11（catalog/builder/service/qcc/mail_servers/custom_mcp/crypto/probe/mcp_tool_cache/default_open）+`oauth/`(6)+`gateway/`(11：cli_*、feishu/wecom 凭据、langchain、protocol、registry)+`gateway/adapters/`(14，飞书/企微/QQ 邮箱/美团/携程/百度地图等） |
| 8 | `cron/` | 7 | 定时任务 | manager、job、trigger、delivery（`CronDeliveryService`）、task_type、tools |
| 9 | `db/` | 35 | 控制面持久化 | 根 7（pool/factory/migrate/services/rebind/probe）+ `repos/` 28（26 个 repo + `_base.py` + `__init__.py`；migrations SQL 不在此包，38 文件 19 版本见 F-181） |
| 10 | `desktop/` | 5 | 远程桌面采集/输入 | session、capture、input、setup |
| 11 | `gateway/` | 53 | IM 网关与统一处理管线 | 根 4（gateway、threads、history_backfill）；process(9，processor/harness_request/stream_project/usage_record）、slash(10)+handlers(6)、media(7)、ws(3)、hitl(4)、cli(3)、channels(3，二维码绑定/钉钉注册）、bot_creators(4，飞书/元宝） |
| 12 | `history/` | 17 | 版本化历史（history v2） | 根 8（store/service/recorder/reader/projection/legacy/trajectory_compat）+`trajectory/`(9：live bus/projector/turn_context/metrics/settings） |
| 13 | `knowledge/` | 17 | 知识库解析/索引/检索/OCR | service、index、jobs（`resume_pending_index_jobs`）、parse、chunk、embed、retrieve、ocr、citations、gate、files、tools、params、hint、relpath、default_open |
| 14 | `mobile/` | 10 | 远程 Android（physical/redroid/emulator） | adb、agent_control、h264、probe、config_probe、docker_install、setup、tools、`__main__.py` |
| 15 | `proactive/` | 4 | 主动关怀 | service、scheduler（`ProactiveCareScheduler`）、picker |
| 16 | `setup/` | 15 | 首启向导/系统服务/自升级/TLS | 根 5（password_file、wizard_tokens、service、self_update）+`tls/`(10：listeners/modes/challenge/http_companion/acme_issue/store/manager/preflight/renewal） |
| 17 | `skills/` | 11 | 技能包与 Skill Hub | skill_packages、skill_package_store、install、skills_hub、skillhub_market/common、skill_transfer、skill_package_from_skillhub、workspace_catalog、presentation |
| 18 | `users/` | 11 | 用户/角色/邀请/权限/偏好 | manager、identity、password、permissions、resource_policy、invites、preferences、profile_avatar、email、acting |
| 19 | `utils/` | 25 | leaf 工具层（AGENTS.md 规定不得被高层编排反向依赖） | bwrap、browser_media、env_file、paths、host_dirs、json_file、locale、ollama_manager、ssrf_guard、tencent_sign、subprocess_io(_win)、frontmatter、doc_edit、llm_text、ulid、url、utf8_text、runtime_packages、docker_env、posix_compat、search_probe、ssl_errors、thread_artifact 等 |
| 20 | `voice/` | 4 | 语音 TTS/STT | manager、adapters、presets |

infra 包根另有 4 个 .py（源码实测）：`server.py`（OctopServer/AppRuntime，详见 [server-launch.md](server-launch.md)）、`errors.py`（119 个 ErrorCode，F-172/F-173）、`metrics.py`（5 计数器 + METRICS 单例，F-174）、`__init__.py`。

模块边界纪律（Octop 仓库 `AGENTS.md` §5）：依赖流向内——「transport layers call domain; domain never calls HTTP/CLI」；leaf 模块 `utils/`、`db/repos/`、`errors.py` 不得依赖高层编排；层级图 `dashboard/ ──HTTP──► api/ ──► infra/ ──► infra/utils/, octop.config`；唯 `launch.py` 可同时 import `infra/server` 与 `api/app`（F-205）。

## 4. `src/octop/api/` 子树地图

| 路径 | 计数（源码实测） | 说明 |
|---|---:|---|
| `api/app.py` | 1 | `build_app(server) -> FastAPI`，60 个 `_RouterMount(`（59 常挂 + mobile 条件 1）（F-503）；完整挂载表见 [api-surface.md](api-surface.md) |
| `api/deps.py` | 1 | JWT 编解码、`current_user`、`require_permission`/`require_admin`、豁免表（F-513~F-515） |
| `api/openapi_meta.py` | 1 | `OPENAPI_TAGS` 40 个 tag、`API_DESCRIPTION`、BearerAuth 注入（F-511/F-512） |
| `api/common/` | 13 py | 跨 router 工具：12 个非 `__init__` 模块（F-517） |
| `api/middleware/` | 4 py | `bridge_proxy.py`、`jwt_auth.py`、`setup_lockdown.py` + `__init__.py`；安装顺序 bridge_proxy → jwt_auth → setup_lockdown（F-508，源码实测） |
| `api/routers/*.py`（顶层） | 54 py | 53 个 router 模块 + `__init__.py`（F-523；源码实测） |
| `api/routers/chat/` | 10 py | `__init__` 聚合 5 子 router（routes/history/trajectory/ws/notify_ws）+ turn/sse/serialize/models（F-549，源码实测） |
| `api/routers/browser/` | 6 py | `__init__` 聚合 env/harness/record_replay/stream/uninstall（源码实测） |
| `api/routers/desktop/` | 6 py | `__init__` 聚合 status/settings/install/uninstall/stream（源码实测） |
| `api/routers/mobile/` | 5 py | `__init__` 聚合 status/install/stream/shell_ws（源码实测） |
| **routers 合计** | **81 py** | 54 + 10 + 6 + 6 + 5 = 81（F-523；源码实测） |

`api/common/` 13 个模块（Glob 实测，F-517 记 12 个非 `__init__`）：`agent.py`（7 个属主函数，F-520）、`agent_runtime.py`（`AgentRuntimeFields`）、`agent_workspace.py`、`attachments.py`（`StoredAttachment`/`save_attachment`）、`content_disposition.py`（RFC 5987）、`memory_client.py`（进程内 JSON-RPC 调 memory bridge，F-521）、`public_base.py`、`sso_cookie.py`、`upload_limit.py`（`read_upload_capped`）、`usage_xlsx.py`（`build_usage_xlsx`）、`validators.py`、`workspace.py`（8 个 def）、`__init__.py`。

## 5. `src/octop/cli/` 子树地图

| 路径 | 计数 | 说明 |
|---|---:|---|
| `cli/main.py` / `cli/registry.py` | 2 | `_LazyCLI(click.Group)` importlib 懒加载；根选项 `-v/--version`、`--user`（OCTOP_USER）、`--agent`（OCTOP_AGENT）、`--json`（F-557）；`COMMANDS` 22 键注册表（F-556） |
| `cli/commands/` | 23 py | `__init__.py` + 22 个命令模块，与 COMMANDS 22 键一一对应（F-558，源码实测） |
| `cli/repl/` | 7 py | `__init__`、runtime（`CliChatSession`/`run_chat_turn_async`）、embedded_session（引用计数嵌入式 OctopServer）、render、session、toolbar（prompt_toolkit）、turn（F-563） |
| `cli/support/` | 13 py | `__init__`、db（`open_cli_services` 离线开库）、offline_ops、embedded_ops、skills、feishu_creator、ctx、state、acting、prompts（6 个提问函数）、qr、stub（`EXIT_NOT_APPLICABLE=2`）、errors（F-564/F-565，源码实测） |

`COMMANDS` 22 键逐字（F-556）：memory、init、run、service、config、user、agent、chats、channel、cron、provider、models、skills、admin、captcha、version、completion、update、clean、backup、acp（属性名 `acp_cmd`）、plugin。新增命令 help：memory = "Live memory maintenance (backup and slim)."；captcha = "Login captcha maintenance (lockout escape hatch)."（F-556）。命令面细节（backup 选项、admin/user 子项、init/run 选项）见 [cli-api.md](cli-api.md) 与 F-559~F-562。

## 6. `src/octop/i18n/`

Glob 实测 13 py + 2 个 JSON：`loader.py`、`__init__.py`、`zh.json`、`en.json`，`domains/` 下 11 文件：`agents`、`attachment`、`channel`、`errors`、`skills`、`slash`、`stream`、`tls`、`tools`、`voice`、`__init__`（源码实测）。dashboard 侧另有独立文案 `dashboard/src/locales/{zh,en}.json`，顶层键各 80 个（F-575）。

## 7. 前端 dashboard 构建链

| 项 | 逐字事实 | 信源 |
|---|---|---|
| package.json | name `octop-dashboard`、private、version `0.1.0`、`"type": "module"` | F-566 |
| scripts | 14 项；`build = tsc -b && vite build`、`build:docker = vite build`（镜像内跳过 tsc，见 Dockerfile:58）、dev/lint/test/format/preview 等 | F-566 |
| dependencies / devDependencies | 30 项 / 26 项（源码实测计数，与 F-566 一致） | F-566 |
| 关键版本 | react/react-dom `^18`、react-router-dom `^7.13.0`、antd `^5.29.1`、vite `^6.3.5`、typescript `~5.8.3`、vite-plugin-pwa `^0.21.2`、`@xterm/xterm` `5.5.0`、mermaid `^11.13.0`、i18next `^25.8.4`、recharts `^3.10.1` | F-566 |
| overrides | `serialize-javascript ^7.0.3`、`@rollup/plugin-terser ^1.0.0` | F-566 |
| Vite 输出 | `outDir: path.resolve(__dirname, "../src/octop/dashboard")`、`emptyOutDir=true`、`chunkSizeWarningLimit=1600`、`maxParallelFileOps=3`（`vite.config.ts:92-99`，源码实测） | F-567 |
| PWA | VitePWA：registerType="prompt"、injectRegister=false、manifest=false（用 public/manifest.json）、navigateFallback=null、clientsClaim=true、skipWaiting=false、maximumFileSizeToCacheInBytes=3MiB | F-567 |
| dev server | host 0.0.0.0，端口 VITE_DEV_PORT 默认 5173，代理 `/api` → `http://127.0.0.1:${VITE_API_PORT||8088}`，xfwd/ws=true | F-567 |
| manifest | name/short_name="Octop"、display standalone、lang zh-CN、4 图标（192/512 any、512 maskable、apple-touch 180） | F-567 |
| API 层规模 | `src/api/modules/*.ts` 55 文件（51 业务 + 4 测试）；`src/api/**/*.ts` 77 文件 | F-568 |
| 路由/页面 | routeConfigs 63 条、pathToKey 41 键；页面 index 38 个、顶层页面目录 12 个；SIDEBAR_NAV_KEYS 19 键 | F-571~F-574 |
| 请求层 | `AUTH_TOKEN_KEY="auth_token"`；5 个 fetch 封装；remember=false 用 sessionStorage；503 setup 检测；401 续期头 `X-Octop-Access-Token` | F-570 |

## 8. Go/Wails 桌面端与绿色便携包

| 项 | 逐字事实 | 信源 |
|---|---|---|
| go.mod | `module octop.desktop`、`go 1.25.0`；直接依赖 godbus/dbus/v5 v5.2.2、wails/v3 v3.0.0-beta.13、golang.org/x/sys v0.46.0；indirect 6 个 | F-576 |
| .go 文件数 | Glob `desktop/src/**/*.go` = 30（23 非测试 + 7 个 `_test.go`：desktop_copy/dock_reopen/download/portable_upgrade/settings/tray_click/window_chrome），含 `cmd/devserver/main.go`（源码实测与 F-577 一致） | F-577 |
| 主窗口 | `WebviewWindowOptions{Title:"Octop", Width:1200, Height:800, URL:"/", Frameless:true, BackgroundColour: NewRGB(247,248,250)}`；隐藏设置窗 `/?settings=1`、AlwaysOnTop、DisableResize | F-578 |
| 托盘/生命周期 | 三平台 DisableQuitOnLastWindowClosed（关窗改 hideToTray）；事件 `desktop:toggle-maximise/minimise/close/status`；SystemTray tooltip "Octop" | F-579 |
| 启动流程 | `//go:embed assets/*`；`OCTOP_DESKTOP_URL` 有值则 waitHealth 60s 后开远程 URL，否则 ensurePortable→startOctop→waitHealth 2 分钟→showDashboard | F-580 |
| build/config.yml | 顶层 `version: "3"`；productIdentifier `com.tencent.octop`；info.version `0.9.26`；注释声明 release packaging 会把 pyproject 版本盖到 .app/exe/NSIS 元数据，info.version 仅本地 generate 兜底 | F-581 |
| Windows 版本 | `build/windows/info.json` fixed.file_version 与 ProductVersion 均 `"0.9.26"`（源码实测一致）；Taskfile 含 `create:nsis:installer`；`stamp_version.py nsis-defines` 写 NSIS `!define` | F-582 |
| 便携包入口 | `portable/templates/launch.py`：校验 `packages/` 缺失写 `launch.py: packages/ missing next to {root}` 并 exit(1) → `site.addsitedir(packages)` → win32 挂 `pywin32_system32` DLL（`os.add_dll_directory`）→ 解释器目录前置 PATH → `runpy.run_module("octop", run_name="__main__", alter_sys=True)` | F-583、源码实测 |
| 便携包构建 | Makefile 目标 bootstrap/wheels/package/green/green-linux/clean；green 依赖 build-frontend+bootstrap-runtime.sh+package.sh；产物 `desktop/portable/release/`；布局 runtime/（python-build-standalone）+packages/（Octop + 依赖 site-packages）；CI `octop-desktop.yml` 在 6 个 runner 出 zip | F-584、F-585 |

版本滞后事实：Python 包 1.0.2b5（F-134），Wails build/config.yml 与 windows/info.json 仍为 0.9.26（F-581/F-582），fnos manifest 为 0.9.15（§9）；config.yml 注释说明发布打包时以 pyproject 版本盖戳（F-581）。

## 9. 容器与部署面

### 9.1 Dockerfile（`docker/Dockerfile`，源码实测复核 F-586）

- 两阶段：`FROM node:20-slim AS frontend-builder`（`npm ci` 后 `npm run build:docker`，ARG `NODE_MAX_OLD_SPACE_SIZE` 默认 2048）与 `FROM python:3.12-slim AS runtime`（F-586）。
- uv 逐字来源：`COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/`（F-586）。
- 两次 `uv sync --frozen --no-dev --extra browser`：首次带 `--no-install-project` 仅装锁依赖，第二次拷源码后全量同步（F-586，源码实测 Dockerfile:110/127）。
- ENV：`OCTOP_BIND_HOST=0.0.0.0`、`OCTOP_PORT=8088`、`HOME=/data`、`PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright`；`EXPOSE 8088`；文件内无 `USER` 指令（F-586）。
- HEALTHCHECK 逐字：`--interval=30s --timeout=10s --start-period=90s --retries=3`，CMD `curl -f http://localhost:${OCTOP_PORT:-8088}/api/health`（F-586）。
- entrypoint（`docker-entrypoint.sh`）：以 `~/.octop/octop.db` 是否存在判首启；首启 `octop init --yes --admin-username ... --admin-password ...`；未给 `OCTOP_DEFAULT_PASSWORD` 时生成 16 位随机密码（首字母、末位数字），写 `/data/.octop/credential.txt` 并 chmod 600；最终 `exec octop run --host 0.0.0.0 --port "$PORT"`（F-587）。

### 9.2 三套 compose

| 文件 | 关键事实 | 信源 |
|---|---|---|
| `docker-compose.yml` | 单服务 octop；build context `..`、image `octop:latest`、restart unless-stopped；端口 `${OCTOP_PORT:-8088}` 双侧；卷 `${OCTOP_DATA:-~/.octop}:/data/.octop`；透传 `OCTOP_DATABASE_*` 8 键与 OPENAI_API_KEY/DASHSCOPE_API_KEY/LANGFUSE_*（LANGFUSE_TRACING_ENABLED 默认 true） | F-588 |
| `docker-compose.postgres.yml` | 镜像 `pgvector/pgvector:pg16`、容器名 octop-postgres、端口 `${OCTOP_PG_PORT:-5432}`、库/用户/密码默认均 octop；挂 `postgres/init-vector.sql` 到 `/docker-entrypoint-initdb.d/01-vector.sql:ro`；该 SQL 仅 `CREATE EXTENSION IF NOT EXISTS vector;`，注释声明不属于控制面迁移（ADR 002） | F-589 |
| `docker-compose.mobile.yml` | 独立文件（注释：network_mode: host 与基础 compose 的 ports 冲突）；privileged、network_mode: host；挂 /var/run/docker.sock、/dev/binderfs、platform-tools:ro；`OCTOP_MOBILE_ADB_HOST` 默认 127.0.0.1:5555、`OCTOP_MOBILE_CONTAINER=octop-mobile-android`、`OCTOP_ENABLE_MOBILE=1`、ANDROID_HOME/ANDROID_SDK_ROOT=/opt/android-sdk | F-589 |

### 9.3 fnos 应用模板（版本锚点均 0.9.15）

| 项 | docker 形态 | native 形态 |
|---|---|---|
| manifest 路径 | `fnos/docker/manifest` | `fnos/native/manifest` |
| appname | `octop` | `octop-native` |
| version | 0.9.15 | 0.9.15 |
| service_port | 8088 | 8089 |
| desktop_applaunchname | `octop.Application` | `octop-native.Application` |
| 其他键 | display_name=OCTOP、source=thirdparty、maintainer=TencentCloud OrcaKit、micro_app=true、checkport=true、ctl_stop=true；desc 含镜像 `ghcr.io/tencentcloud/octop:latest` 与「已预装 browser / desktop 附加组件」 | `install_dep_apps=python312`；desc 默认地址 http://设备IP:8089、凭据文件 `octop-login.txt`、支持官方 octop CLI |

信源：F-590（逐字字段经源码实测复核）。两目录另含 cmd/ 回调（config/install/uninstall/upgrade 各 `_init`/`_callback` + main）、wizard/、ui/config、Dockerfile（docker 形态）、ICON 与 LICENSE（源码实测）。

## 10. 运行时默认值与文档面

- `.env.example` 默认：`OCTOP_PORT=8088`、`OCTOP_LOG_LEVEL=info`、`OCTOP_BIND_HOST=0.0.0.0`、`OCTOP_ADMIN_USERNAME=admin`、`OCTOP_DEFAULT_PASSWORD=`（空=自动生成写 `~/.octop/credential.txt`）；8 个 `OCTOP_DATABASE_*` 键、验证码键 `OCTOP_CAPTCHA_*`（默认 slider，v3_min_score=0.5）；Langfuse 无 enabled 环境变量，开关是 settings 键 `observability_langfuse_enabled`（F-143）。
- `docs/` Glob `docs/**/*.md` = 20（根 18 + adr 2：`001-single-process-model`、`002-database-backends`，源码实测与 F-591 一致）；`docs/api.md` 声明 Scalar 在 /api/docs、schema 在 /api/openapi.json、Bearer 鉴权与公共端点清单（F-591）。
- `docs/cli.md` 定义三传输层：Offline（本地库，No login）/ Attach（HTTP/WS，需 `octop user login`）/ Embedded（进程内 OctopServer）；`docs/architecture.md` 声明 Surface → API layer → Domain → octop-harness/gateway → SQLite/PostgreSQL，且「The whole stack is one process.」（F-592）。

## 相关文档

- [/concepts/00-architecture.md](../concepts/00-architecture.md)
- [/concepts/01-server-lifecycle.md](../concepts/01-server-lifecycle.md)
- [/concepts/06-cli-commands.md](../concepts/06-cli-commands.md)
- [服务器启动与组合根](server-launch.md)
- [HTTP API 挂载总表与端点计数](api-surface.md)
- [CLI 命令与 API 信源](cli-api.md)
- [DB 层信源](db-layer.md)
- [harness 技术栈](harness-stack.md)
