---
type: Concept
title: "分层架构：CLI 八子命令、FastAPI 19 端点与 runner 主循环"
description: "agents/core/runtime/tasks 四层架构地图、CLI 8 子命令全家福与公共参数、FastAPI 服务 19 端点全表、/step 动作分发表、/health 自愈、runner 主循环与 joblib 并发"
tags: [MobileWorld, 架构, CLI, FastAPI, runner]
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

# 分层架构：CLI 八子命令、FastAPI 19 端点与 runner 主循环

MobileWorld 的 `src/mobile_world/` 分为四层：**agents**（模型接入）、**core**（CLI/服务/编排）、**runtime**（环境客户端/设备控制）、**tasks**（任务体系）。本篇给出四层地图，并精读 core 层的三根支柱：CLI 八个子命令、容器内 FastAPI 控制服务的 19 个端点、以及驱动评测的 runner 主循环。

## 四层架构地图

| 层 | 职责 | 核心文件 | 详见 |
|---|---|---|---|
| agents/ | Agent 抽象、注册表、动作映射 | base.py、registry.py | `/concepts/03-agent-registry.md` |
| core/ | CLI 子命令、FastAPI 服务、评测 runner、eval-server、log_viewer | cli.py、server.py、runner.py、eval_server/ | 本篇 + `/concepts/06-eval-server-mcp.md` |
| runtime/ | 环境客户端、AndroidController、JSONAction、MCP 客户端 | client.py、controller.py、utils/models.py | `/concepts/05-runtime-controller.md` |
| tasks/ | BaseTask、TaskRegistry、10 场景任务定义 | base.py、registry.py、definitions/ | `/concepts/04-tasks-registry.md` |

层间数据流：CLI（core）创建环境客户端（runtime）与 Agent（agents）→ runner（core）驱动 `predict → execute_action` 循环 → 服务端 `/step` 把 JSONAction 分发到 AndroidController（runtime）→ 判分走 tasks 层（F-038、F-034）。

## CLI 八个子命令

`create_parser()` 依次注册 8 个子命令配置函数：**server、eval（别名 `run`）、test、device（别名 `viewer`）、logs、env、info、eval-server**；`async_main()` 按 `args.command` 分发到 `subcommands.execute_*`，`main()` 用 `asyncio.run(async_main())`（F-018）。

| 子命令 | 用途 | 关键默认值 |
|---|---|---|
| `server` | 启动 FastAPI 控制服务 | `--host 0.0.0.0 --port 6800`（F-023） |
| `eval`（`run`） | 批量评测 | 日志根 `./traj_logs`、`device emulator-5554`（F-020） |
| `test` | 单任务交互式运行 | 无 `--device` 时 `adb devices` 自动发现（F-030） |
| `device`（`viewer`） | 设备屏幕查看器 | entrypoint 以 `--port 7860` 启动（F-045） |
| `logs` | 日志查看/结果打印 | `view --port 8760`（F-028） |
| `env` | 容器生命周期 | `run/rm/list/info/restart/exec/check`（F-024） |
| `info` | task/agent/app/mcp 查询 | 支持导出 Excel（Tasks/Statistics/Tag Statistics 三 sheet，F-027） |
| `eval-server` | 集群评测编排 | `--port 8800 --max-containers 40`（F-029） |

### eval 公共参数组

`_add_common_arguments(parser)` 注册的公共参数（每个均提供下划线别名）（F-019）：`--agent-type`（required）、`--model-name`、`--llm-base-url`、`--api-key`、`--log-file-root`、`--max-round`（别名 `--max-step`）、`--aw-host`、`--timeout`、`--output`、`--executor-llm-base-url`、`--executor-model-name`、`--executor-agent-class`、`--device`、`--step-wait-time`（default 1.0）、`--suite-family`（choices=["mobile_world"]）、`--env-name-prefix`（default "mobile_world_env"）、`--env-image`（default "mobile_world"）、`--enable-mcp`、`--enable-user-interaction`、`--scale-factor`（default 1000）。

eval 专有参数（F-020）：`--task`（逗号分隔或 `"ALL"`）、`--auto-retry`（default 10）、`--dry-run`、`--max-concurrency`、`--shuffle-tasks`、`--pass-k`（default 1）；`log_file_root = args.log_file_root or args.output or "./traj_logs"`，`device=args.device or "emulator-5554"`，`api_key=args.api_key or os.getenv("API_KEY")`。

### 两种报告

- `--pass-k`：`generate_pass_k_report` 逐次读取 `log_file_root/run_{i}/`（i∈1..k），任务判过条件为 `score > 0.99` 且至少一次；报告写 `pass_k_report_{YYYYmmdd_HHMMSS}.json`，含 `summary/metadata/tasks` 三键（F-021）。
- `--task ALL`：统计 `successful_tasks`（同样以 `score > 0.99` 为准），报告写 `eval_report_{timestamp}.json`，含 `summary.total_tasks_assigned/total_tasks_with_results/successful_tasks/total_tasks_with_no_results/overall_success_rate/total_duration_seconds`（F-022）。

注意成功阈值是 **0.99 而非 1.0**（容浮点误差）。

## FastAPI 控制服务与 19 端点

容器内的控制服务是 `FastAPI(title="Mobile GUI Agent Benchmark Server", version="0.1.0")`，模块常量 `SUITE_FAMILY = "mobile_world"`、`AVD_MAPPING = {"mobile_world": "Pixel_8_API_34_x86_64"}`、`CONTROLLERS: dict[str, AndroidController] = {}`、`RESTART_COOLDOWN_SECONDS = 300`，CORS `allow_origins=["*"]`；`initialize_suite_family` 创建 `TaskRegistry()` 并打印 `Loaded {n} mobile_world tasks`（F-031）。

路由全表共 19 个端点（F-033）：

```text
GET  /health                       服务与设备健康
GET|POST /init                     初始化
GET  /state                        设备状态
GET  /screenshot                   截图（参数 device/prefix/return_b64）
GET  /download                     文件下载
GET  /task-asset/{asset_path:path} 任务资产（rel 以 ".." 开头或缺 "assets" 段则 400）
GET  /xml                          XML（mode: Literal["uia","ac"]）
POST /sms                          模拟短信
POST /step                         执行动作（见下）
GET  /task/list                    任务清单
GET  /task/goal                    任务目标
GET  /task/metadata                任务元数据
POST /task/init                    任务初始化
GET  /task/eval                    任务判分
POST /task/tear_down               任务清理
GET  /task/complexity              任务复杂度
POST /task/callback                任务回调
GET  /config/callback              回调配置
POST /suite_family/switch          切换 suite family
```

### /health 自愈

`GET /health` 遍历 CONTROLLERS 调 `controller.check_health(try_times=2)`；不健康时在 `_restart_lock` + 300 秒冷却窗口内调用 `restart_emulator_with_avd(AVD_MAPPING[SUITE_FAMILY])`；健康返回 200 `{"ok": true, "devices": [...], "device_status": {...}}`，否则 503（F-032）。这个端点同时是镜像 `HEALTHCHECK` 的探测目标（F-067）。

### /step 动作分发表

`POST /step` 按 `action.action_type` 分发到 AndroidController（F-034）：

| action_type | 分发 |
|---|---|
| CLICK | `ctr.tap(int(x), int(y))` |
| SWIPE | `ctr.swipe(x, y, direction or "up")` |
| INPUT_TEXT | `ctr.text(text)`（空串跳过） |
| NAVIGATE_BACK / NAVIGATE_HOME | `ctr.back()` / `ctr.home()` |
| KEYBOARD_ENTER | `ctr.enter()` |
| LONG_PRESS | `ctr.long_press(x, y, 1000)` |
| DOUBLE_TAP | `ctr.double_tap(x, y)` |
| DRAG | `ctr.drag(start_x, start_y, end_x, end_y)` |
| SCROLL | 映射为 `ctr.swipe(None, None, direction)`——**scroll 的 up/down 与 swipe 相反** |
| OPEN_APP | `ctr.launch_app(app_name)` |
| WAIT | `time.sleep(1.0)` |
| ANSWER | `ctr.answer(text)` |
| STATUS | 返回 goal_status |
| ASK_USER | `ctr.ask_user(agent_question)` |
| UNKNOWN | 返回 `"UNKNOWN_ACTION"` |

## runner 主循环

编程入口 `run_agent_with_evaluation(...)`（F-037）：aw_urls 为空时 `discover_backends(image_filter=env_image, prefix=env_name_prefix)` 自动发现容器。`_init_env` 按 `enable_mcp` 分派 `AndroidMCPEnvClient` 或 `AndroidEnvClient`，随后 `env.switch_suite_family(suite_family)`（F-039）。

单任务主循环 `_execute_single_task`（F-038）：

```python
env.get_task_goal(task_type=task_name)   # 取目标
agent.initialize(task_goal)              # Agent 初始化
while True:
    observation = agent.predict({"screenshot", "tool_call", "ask_user_response"})
    traj_logger.log_traj(...)
    action = ...                          # 解析 JSONAction
    env.execute_action(action)
    # 终止条件：action_type in [ENV_FAIL, FINISHED, UNKNOWN]；
    # ANSWER 执行后终止；step >= max_step 终止
env.get_task_score() → traj_logger.log_score → env.tear_down_task() → agent.done()
```

并发与重试（F-038）：`joblib.Parallel(backend="threading")` + `Queue` 分配 env；异常消息含 `"Device is not healthy"` 时 sleep(20) 重试（`retry_on_device_unhealthy: int = 2`）；`max_attempts = min(1 + auto_retry, 10)`。

## 服务编程接口与容器管理

- `start_server(host="0.0.0.0", port=6800, debug=False, suite_family="mobile_world", enable_mcp=False, suppress_health_logs=True)`：`HealthCheckFilter` 过滤含 `/health` 的 access 日志；enable_mcp 时打印 `MCP server available at http://{host}:{port}/mcp-server/mcp`；另有 `create_server_config(...) -> uvicorn.Config` 与 `get_server_app()`（F-035）。
- `core/api/env.py` 提供容器管理函数族：`find_available_ports`、`launch_container(s)`、`list_containers`、`remove_container(s)`、`kill/restart_server_in_container`、前置检查 `check_docker_installed/check_docker_permission/check_docker_running/check_kvm_available/check_iptables_nat`、`check_prerequisites()`、`check_image_status`、`pull_image` 等（F-036）。

## 交互式运行器

`core/user_task_runner/runner.py` 提供 `run_user_task(...)`（`test` 子命令调用）与 `_execute_user_task/_ask_user_interactive/_print_step_header/_print_observation/_print_agent_response/_print_task_start/_print_task_end` 等内部函数；`_ask_user_interactive` 供无 USER_AGENT 配置时用 `input()` 人工应答（F-040）。

## 相关概念

- [/concepts/01-quickstart-installation.md](/concepts/01-quickstart-installation.md)——env 子命令的容器启动实操
- [/concepts/05-runtime-controller.md](/concepts/05-runtime-controller.md)——JSONAction 模型与 AndroidController（/step 分发的另一端）
- [/concepts/03-agent-registry.md](/concepts/03-agent-registry.md)——predict 返回 JSONAction 的 Agent 契约
- [/concepts/06-eval-server-mcp.md](/concepts/06-eval-server-mcp.md)——runner 之上的集群编排层
