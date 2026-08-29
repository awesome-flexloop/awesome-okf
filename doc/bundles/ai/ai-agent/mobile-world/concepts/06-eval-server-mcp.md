---
type: Concept
title: "eval-server 与 MCP：tmux + SQLite 队列编排 40 容器，工具按任务过滤注入"
description: "eval-server 子命令参数、SQLite WAL jobs 表、FastHTML 应用与路由、后台 worker（40 容器/tmux/5 秒轮询）、log_viewer；MCP_CONFIG 五个远端服务、SyncMCPClient 串行化、AndroidMCPEnvClient 按 tag/apps 过滤"
tags: [MobileWorld, eval-server, MCP, SQLite, tmux, FastHTML]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobile-world-facts
    resource: /references/facts.md
    title: MobileWorld 源码事实台账
  - id: mobile-world-sources
    resource: /references/source-registry.md
    title: MobileWorld 信源登记
---

# eval-server 与 MCP：tmux + SQLite 队列编排 40 容器，工具按任务过滤注入

单机评测（runner + joblib 线程并行）之上，MobileWorld 还有一层集群编排：eval-server 以 SQLite WAL 队列 + 轮询 worker + tmux 会话管理至多 40 个评测容器。MCP 侧则把 5 个远端服务封装成工具，按任务元数据过滤后注入 Agent。本篇精读这两块能力。

## eval-server 子命令

```bash
mw eval-server --port 8800 --max-containers 40 --data-dir . --base-path / --shell-prefix ""
```

参数默认值（F-029）：`--port`（8800）、`--max-containers`（40）、`--data-dir`（"."）、`--base-path`（"/"）、`--shell-prefix`（""）；调用 `eval_server.app.main(...)`。

## SQLite WAL 任务队列

`core/eval_server/db.py` 使用 SQLite（WAL 模式）库文件 `{data_dir}/eval_jobs.db`，表 `jobs` 的字段（F-041）：

```text
id TEXT PRIMARY KEY, label TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'queued',
agent_type/model_name/llm_base_url TEXT NOT NULL, api_key TEXT DEFAULT '',
env_count INTEGER NOT NULL, max_round INTEGER DEFAULT 50, step_wait_time REAL DEFAULT 1.0,
auto_retry INTEGER DEFAULT 0, enable_user_interaction INTEGER DEFAULT 0,
env_image TEXT DEFAULT '', container_prefix TEXT NOT NULL,
log_dir/tmux_session/log_file TEXT DEFAULT '',
total_tasks/successful_tasks INTEGER, success_rate REAL, scores_json TEXT DEFAULT '',
created_at REAL DEFAULT (strftime('%s','now')), started_at/finished_at TEXT
```

含 `auto_retry`/`env_image` 两段 ALTER TABLE 迁移。`create_job(...)` 用 `uuid.uuid4().hex[:12]` 生成 id，`container_prefix = f"eval_{job_id}"`；`count_running_envs()` 汇总 status='running' 的 env_count——大规模评测前先核对它与 Docker 资源（F-041）。

## FastHTML 应用与路由

`app, rt = fast_app()`；`async def main(port=8800, max_containers=40, data_dir=".", base_path="/", shell_prefix="")` 的启动序列：`db.init_db` → `register_routes(rt, base_path)` → 挂载 log_viewer 路由至 `{base_path}/log-viewer/` → `start_worker(max_containers, shell_prefix)` → uvicorn（`ws="none"`）（F-042）。

routes 内 `@rt` 路由清单（F-042）：`/`、`/dashboard-content`、`/agent-types`、`/image-versions`、`/submit-form`、`/jobs/{job_id}/copy-form`、`POST /submit`、`/jobs/{job_id}`、`/jobs/{job_id}/log-tail`、`POST /jobs/{job_id}/cancel`、`POST /jobs/{job_id}/rerun`。

## 后台 worker：40 容器 + tmux + 5 秒轮询

`core/eval_server/worker.py` 常量（F-043）：`MAX_CONTAINERS = 40`、`POLL_INTERVAL = 5`（秒）、`LOG_BASE_DIR = "eval_server_logs"`、`SHELL_PREFIX = ""`。

- `get_docker_containers()` 用 `docker ps --format '{{.Names}}\t{{.Status}}\t{{.Image}}'`
- `get_available_images(repo="ghcr.io/tongyi-mai/mobile_world")`
- `_start_job(job)` 在 tmux 会话 `eval_{job_id}` 中启动容器与 eval 命令，日志写 `output.log`

大规模评测的"调度器"不是 celery/k8s，而是 tmux 会话 + 5 秒轮询 SQLite 的单 worker——理解这一点就能解释它对宿主 tmux/docker CLI 的依赖（F-043）。

## log_viewer

`core/log_viewer/` 由 app.py/routes.py/styles.py/static_export.py/utils.py/__main__.py 组成；`routes.register_routes(rt, base_path="/", route_prefix="")` 注册路由（FastHTML 星号导入，pyproject 对该文件豁免 F403/F405）；`logs view` 子命令默认端口 8760（F-044、F-028）。eval-server 将其挂载在 `{base_path}/log-viewer/` 下（F-042）。

## MCP：五个远端服务

`runtime/mcp_server.py` 的模块级 `MCP_CONFIG = {"mcpServers": {...}}` 固定 5 项（F-052）：

| 名称 | 协议 | 提供商 |
|---|---|---|
| `amap` | SSE（`https://dashscope.aliyuncs.com/api/v1/mcps/amap-maps/sse`） | DashScope |
| `stockstar` | SSE（dashscope） | DashScope |
| `gitHub` | HTTP（modelscope `.../c3c76357651542/mcp`） | ModelScope |
| `jina` | HTTP（modelscope `.../25a924b9ce914b/mcp`） | ModelScope |
| `arXiv` | HTTP（modelscope `.../d9b238e019f04e/mcp`） | ModelScope |

鉴权头 `Authorization: Bearer {DASHSCOPE_API_KEY}` 或 `Bearer {MODELSCOPE_API_KEY}`（模块加载时 `os.getenv`）。docs/mcp_setup.md 声明这两个提供商：DashScope（amap=AMap Maps SSE、stockstar=证券金融数据 SSE）与 ModelScope（gitHub/jina/arXiv，均 HTTP），市场入口 `https://bailian.console.aliyun.com/#/mcp-market` 与 `https://modelscope.cn/mcp`（F-076，密钥配置见 `/concepts/01-quickstart-installation.md` 的 .env 六变量）。

### SyncMCPClient 串行化与重试

`class SyncMCPClient`（F-053）：`__init__(self, url=None, config=None, max_retries=5, retry_delay=10, retry_backoff=2)`，`self.timeout = 120`；`list_tools()`/`call_tool(name, arguments=None)` 为 async，重试延迟指数递增（`delay *= retry_backoff`）；`list_tools_sync()`/`call_tool_sync()` 用模块级 `client_lock`（`threading.Lock`）串行化，并在已有事件循环时经 ThreadPoolExecutor 提交 `asyncio.run`。`init_mcp_clients() -> SyncMCPClient` 单例化全局 `CLIENT`。

## AndroidMCPEnvClient：按任务过滤注入

`class AndroidMCPEnvClient(AndroidEnvClient)`（F-048）：`__init__` 调 `init_mcp_clients()` 后 `self.tools = mcp_client.list_tools_sync()`，`self.tool_map = {tool["name"]: mcp_client for tool in self.tools}`。

`reset_tools(self, filters=None, task_type=None)` 的过滤规则：查任务 metadata，**无 `"agent-mcp"` tag 时置空 tools**；有则按 `metadata["apps"]` 中含 `"MCP"` 的项取 `app.split("-")[-1]` 作为过滤词。`execute_action` 中 `action.action_type == MCP` 时 `client.call_tool_sync(action_name, action_args)`，结果若以 `<!DOCTYPE html>` 开头经 `markdownify` 转换（`_truncate_tool_call`）。

任务集合随开关变化：`get_suite_task_list` 按 `"agent-mcp"` 与 `"agent-user-interaction"` tag 过滤（F-047），对应 CLI 的 `--enable-mcp`/`--enable-user-interaction` 开关（F-019）。runner 的 `_init_env` 在 enable_mcp 时创建 AndroidMCPEnvClient（F-039）。

## 相关概念

- [/concepts/02-architecture-layers.md](/concepts/02-architecture-layers.md)——单机 runner 主循环（eval-server 编排的下一层）
- [/concepts/05-runtime-controller.md](/concepts/05-runtime-controller.md)——MCP 动作常量与 call_tool_sync 的数据通路
- [/concepts/04-tasks-registry.md](/concepts/04-tasks-registry.md)——task_tags 与用户代理配置的来源
- [../mobilepa-bench/index.md](../mobilepa-bench/index.md)——同为工具调用维度但采用托管私有评测的规划基准（互补层级）
