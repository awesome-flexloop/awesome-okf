---
type: Concept
title: "运行时层：JSONAction 是 Agent、服务与设备控制的通用语言"
description: "AndroidEnvClient 签名与任务生命周期（backoff 截图）、AndroidController 35 方法清单（截图双回退/快照/ask_user）、JSONAction 模型与校验器、APP_DICT、TrajLogger、docker 工具函数与 app_helpers 七模块"
tags: [MobileWorld, runtime, JSONAction, AndroidController, ADB]
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

# 运行时层：JSONAction 是 Agent、服务与设备控制的通用语言

runtime 层是 MobileWorld 的"手和眼"：`AndroidEnvClient` 把 HTTP 服务封装成环境接口，`AndroidController` 通过 ADB 直接操作设备，而 `JSONAction` 是贯穿三者的动作数据模型——Agent 的 predict 返回它（F-007），runner 把它交给 `execute_action`（F-038），服务端 `/step` 把它分发到 controller 方法（F-034）。理解 JSONAction 是理解全框架的前提。

## AndroidEnvClient：环境客户端

`class AndroidEnvClient`（`runtime/client.py`，F-046）：

```python
__init__(self, url: str = "http://localhost:8000", device: str = "emulator-5554",
         step_wait_time: float = 1.0)
```

模块常量：`TASK_META_DATA_PATH = "./new_task_metadata.json"`、`DEFAULT_MAX_STEP = 15`。`get_screenshot` 带 `@backoff.on_exception(backoff.expo, Exception, max_tries=3)` 装饰（指数退避重试截图）；`get_observation(type="screenshot")` 对 accessibility_tree 类型抛 `ValueError("Accessibility tree is not supported yet")`——当前只支持截图观测。

任务生命周期方法（F-047）：

| 方法 | HTTP | 说明 |
|---|---|---|
| `initialize_task(task_name) -> Observation` | POST `/task/init`（timeout=300） | 初始化后截图返回 Observation |
| `execute_action(action: JSONAction) -> Observation` | POST `/step` | 执行动作 |
| `get_task_score(task_type) -> tuple[float, str]` | GET `/task/eval` | 判分 |
| `get_task_goal(task_type) -> str` | GET `/task/goal` | 取目标 |
| `tear_down_task` | POST `/task/tear_down` | 清理 |
| `switch_suite_family(target_family) -> dict` | POST `/suite_family/switch`（timeout=300） | 切换任务族 |
| `get_suite_task_list(enable_mcp=False, enable_user_interaction=False)` | — | 按 tags 过滤 `"agent-mcp"` 与 `"agent-user-interaction"` |
| `health() -> bool` | GET `/health` | 查 `ok` 字段 |

设备查看器 `ScrcpyScreenViewer`（`core/device_viewer.py`，F-045）：`get_connected_devices()` 解析 `adb devices`、`take_screenshot(device_id=None)` 用 `adb exec-out screencap -p`、`start_streaming(device_id, fps=2)` 后台线程循环截图；entrypoint.sh 以 `uv run mobile-world viewer --port 7860` 启动。

## AndroidController：32 个方法的设备控制面

`class AndroidController`（`runtime/controller.py`，F-049）：`__init__(self, device="emulator-5554")` 设 `screenshot_dir = "/sdcard"`、`xml_dir = "/sdcard"`、`ac_xml_dir = "/sdcard/Android/data/com.example.android.xml_parser/files"`；`width/height` 由 `adb shell wm size` 解析；实例属性 `interaction_cache = ""`、`user_agent_chat_history = []`、`user_sys_prompt = None`、`model_config = None`。模块级 `APP_LOWER_DICT` 由 COMMON_APP_MAPPER 与 APP_DICT 小写化合并。

方法清单共 32 个（不含 `__init__`；F-050），按能力分组：

- **观测**：`get_screenshot(prefix, save_dir, try_times=0) -> AdbResponse`（先试 `exec-out screencap -p` 重定向，失败回退 `shell screencap` + `pull` + `rm` 的双回退）、`get_xml`、`get_ac_xml`、`get_current_activity`、`get_current_app`、`check_ac_survive`、`check_health(try_times=0) -> bool`
- **交互**：`tap(x, y)`、`double_tap(x, y)`、`long_press(x, y, duration=1000)`、`text(input_str)`、`swipe(...)`、`drag(...)`、`back/enter/home/app_switch()`
- **应用**：`launch_app(app_name)`、`kill_package(package_name)`
- **快照**：`list_snapshots`、`create_snapshot(tag=None)`、`load_snapshot(tag)`、`delete_snapshot(tag)`
- **交互兜底**：`ask_user(agent_question) -> str`、`answer(answer_str) -> None`
- **文件/杂项**：`push_file/pull_file/remove_file`、`refresh_media_scan(file_path)`、`simulate_sms(sender, message)`、`activate_adb_keyboard`、`get_device_size`

### ask_user 的用户模拟

`ask_user` 校验 `user_sys_prompt`/`model_config` 非空（否则 RuntimeError），调 `user_agent_answer_question(self.user_sys_prompt, agent_question, self.model_config, self.user_agent_chat_history)`，将问答以 `{"role": "user"/"assistant", ...}` 追加进 `user_agent_chat_history`；`answer(answer_str)` 仅设置 `self.interaction_cache = answer_str`（F-051）。用户侧的 sys_prompt 与 ModelConfig 由任务层注入（F-062）。

## JSONAction：动作数据模型

动作类型常量共 19 个（`runtime/utils/models.py`，F-054）：

```python
ANSWER="answer", CLICK="click", DOUBLE_TAP="double_tap", FINISHED="finished",
INPUT_TEXT="input_text", KEYBOARD_ENTER="keyboard_enter", LONG_PRESS="long_press",
NAVIGATE_BACK="navigate_back", NAVIGATE_HOME="navigate_home", OPEN_APP="open_app",
SCROLL="scroll", STATUS="status", SWIPE="swipe", UNKNOWN="unknown", WAIT="wait",
DRAG="drag", ASK_USER="ask_user", MCP="mcp", ENV_FAIL="error_env"
```

模块常量：`DEFAULT_IMAGE = "ghcr.io/tongyi-mai/mobile_world:latest"`、`DEFAULT_NAME_PREFIX = "mobile_world_env"`。

`class JSONAction(BaseModel)` 字段：`action_type/index/x/y/text/direction/goal_status/app_name/keycode/clear_text/start_x/start_y/end_x/end_y/action_name/action_json`。校验器（F-054）：

- action_type 须在 `_ACTION_TYPES` 元组内
- direction 须在 `("left","right","down","up")`
- keycode 须以 `"KEYCODE_"` 开头
- x/y 四舍五入取整、index 转 int
- `model_post_init` 校验 index 与 x/y 互斥
- `__eq__` 对 app_name/text 忽略大小写比较

请求/响应模型（F-054）：`InitRequest(device="emulator-5554", type: Literal["cmd","docker"]="cmd", instance)`、`StepRequest(device, action: JSONAction)`、`TaskOperationRequest(task_name, req_device)`、`SmsRequest(device, sender, message)`、`TaskCallbackRequest(device, callback_data)`、`Observation(screenshot, accessibility_tree=None, ask_user_response=None, tool_call=None)`、容器模型 `ContainerInfo/ContainerConfig/LaunchResult/ImageStatus`。

## 应用字典

`APP_DICT` 18 项应用名→包名（F-055），如 `"淘店": "com.testmall.app"`、`"Mattermost": "com.mattermost.rnbeta"`、`"Mastodon": "org.joinmastodon.android.mastodon"`、`"Mail": "com.gmailclone"`、`"Calendar": "org.fossify.calendar"`、`"Camera": "com.android.camera2"`；`COMMON_APP_MAPPER` 约 190 项包名→中文名映射（如 `"com.tencent.mm": "微信"`、`"com.alibaba.wireless": "阿里巴巴"`）。

## 轨迹与产物

- artifacts 常量（F-056）：`ARTIFACTS_ROOT = Path(os.getenv("ARTIFACTS_ROOT", "./artifacts")).resolve()`（导入时即 mkdir）；`device_dir(artifacts_root, device)` 返回 `artifacts_root / device` 并 mkdir。
- TrajLogger（F-057）：`SCORE_FILE_NAME = "result.txt"`；`parse_result_file` 解析格式为第 1 行 `score:<float>`、第 2 行 reason。工具函数 `save_screenshot`、`extract_click_coordinates(action)`、`extract_drag_coordinates(action)`、`draw_clicks_on_image(image_path, output_path, click_coords)`、`draw_drag_on_image(...)`；`class TrajLogger` 提供 `log_traj/log_tools/log_score/reset_traj`（runner.py 调用，F-038）。

## docker 工具函数

`runtime/utils/docker.py` 函数族（F-058）：`run_command`、`docker_ps(include_all=False)`、`list_containers_by_image_substring`、`docker_inspect`、`docker_rm(container_name, *, force=True, volumes=False)`、`build_run_command`、`docker_exec_bash`、`docker_exec_replace(container_name, command, *, interactive=True)`、`discover_backends`（runner 自动发现容器，F-037）、`restart_emulator_with_avd(avd_name: str) -> str`（返回新 device_id，/health 自愈调用，F-032）。

## app_helpers：应用后端辅助

7 个模块（F-059）：

| 模块 | 关键函数 |
|---|---|
| `mail.py` | `initialize_inbox(state)`、`initialize_attachments()`、`get_sent_email_info()` |
| `fossify_calendar.py` | `insert_calendar_event(...)`、`get_calendar_events(...)`（直写日历数据库） |
| `mall.py` | `MallConfig(BaseModel)`、`get_config/set_config/clear_config`、`write_callback_file(callback_data, task_name, device_name)`、`clear_callback_files(device_name)`、`get_recent_callback_content(num=1)` |
| `mastodon.py` | 约 50 个函数：`start/stop/restart_mastodon_backend`、`connect_to_postgres()`、`get_latest_toots_by_username(username, limit=1)`、`compute_phash(file_path) -> int`、`parse_dt(dt, tz="Europe/London")` 等 |
| `mattermost.py` | `MattermostCLI`、`mattermost_operation(...)`、`start/stop/restart_mattermost_backend`、`_extend_session_expiry()`（CHANGELOG 2026-04-15 修复的落点，F-078）、`connect_to_postgres()`、`get_latest_messages()` 等 |
| `mcp.py` | async 工具封装：`get_stocks_esg_ratings`、`get_high_dividend_stocks`、`query_weather`、`calculate_distance`、`plan_route`、`search_arxiv_papers(query, max_results=5)` 等 |
| `system.py` | `time_sync_to_now()`（initialize_task_hook 调用，F-061） |

## 相关概念

- [/concepts/02-architecture-layers.md](/concepts/02-architecture-layers.md)——/step 分发表消费 JSONAction 的服务端视角
- [/concepts/03-agent-registry.md](/concepts/03-agent-registry.md)——predict 返回 JSONAction 的 Agent 侧契约
- [/concepts/04-tasks-registry.md](/concepts/04-tasks-registry.md)——initialize_task 如何调用 controller 的快照与清理能力
- [/concepts/06-eval-server-mcp.md](/concepts/06-eval-server-mcp.md)——MCP 动作（`MCP="mcp"`）的工具注入与执行
