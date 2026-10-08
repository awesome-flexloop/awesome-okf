---
type: Concept
title: "任务体系：快照 + 冻结时钟 + 后台清理的确定性复现"
description: "BaseTask 抽象接口与类属性、initialize_task 初始化流程（快照加载+冻结日期+双后端停止+配置清理）、用户代理注入与 ModelConfig、TaskRegistry 自动扫描、10 场景任务目录"
tags: [MobileWorld, 任务体系, 快照, 冻结时钟, TaskRegistry]
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

# 任务体系：快照 + 冻结时钟 + 后台清理的确定性复现

MobileWorld 任务的"确定性"靠三件事共同保证：任务初始化统一加载 `init_state` 模拟器快照、默认日期字面量冻结在 2025-10-16、初始化时强制停 Mattermost/Mastodon 后端并清空 mall 配置与回调文件。本篇精读 tasks 层：BaseTask 抽象接口、initialize_task 流程、用户代理注入、TaskRegistry 自动扫描与 10 场景任务目录。

## BaseTask 抽象接口

`class BaseTask(abc.ABC)`（`tasks/base.py`，F-060）：

- 类属性 `start_on_home_screen = True`
- `__init__(self, params: dict[str, Any] = None)` 设 `initialized=False`、`self.apps_require_time_sync = ["Chrome", "Maps", "MCP-arXiv"]`
- 抽象 property：`app_names -> set[str]`、`goal -> str`
- 非抽象 property：`task_tags -> set[str]`（默认空集）、`name -> str`（返回 `self.__class__.__name__`）、`snapshot_tag -> str | None`（默认 `"init_state"`）

### 冻结时钟

`_compute_current_date()` 的规则（F-060）：`app_names` 含 time_sync 应用（`Chrome/Maps/MCP-arXiv`）时返回当天日期，否则返回字面量 `"2025-10-16"`。模拟环境里"今天几号"默认是写死的——只有任务显式声明依赖时间敏感应用才同步真实日期，这让"周二发消息"类任务的 ground truth 永远稳定。自建时间敏感任务须显式维护 `apps_require_time_sync`。

## initialize_task 流程

`initialize_task(self, controller: AndroidController) -> bool | None` 的固定顺序（F-061）：

```text
reset_task_state()
→ 刷新 current_date
→ controller.load_snapshot(self.snapshot_tag)   # 成功后 app_switch()+home()+sleep(2)
→ 时间同步（app_names 命中 apps_require_time_sync 时 time_sync_to_now()）
→ mattermost.stop_mattermost_backend() + mastodon.stop_mastodon_backend()
→ clear_config() + clear_callback_files(controller.device)
→ initialize_task_hook(controller)              # 默认实现 time_sync_to_now()
→ initialize_user_agent_hook(controller)
→ controller.home()
→ 清空 controller.interaction_cache / user_agent_chat_history，置 initialized = True
```

reset 纪律：快照加载、双后端停止、配置/回调文件清理**缺一不可**（F-061）。这些后端与配置对应 runtime 层 app_helpers 的 mall/mattermost/mastodon 模块（F-059）。快照本体在镜像里由 Dockerfile 复制的 AVD 提供（F-067），也可按八步流程重制（见 `/examples/02-customize-avd-snapshot.md`）。

## 用户代理注入

`initialize_user_agent_hook`（F-062）：

- 默认 `self.relevant_information = "No more task-related information can be provided."`
- 构造 user_sys_prompt：含 goal、relevant_information、拒绝无关提问规则、`Today is {self.current_date}`
- 无 `self.model_config` 时用 `ModelConfig(model_name=os.getenv("USER_AGENT_MODEL", "gpt-4o-mini"), api_key=os.getenv("USER_AGENT_API_KEY", ""), url=os.getenv("USER_AGENT_BASE_URL", "https://api.openai.com/v1"))`

也就是说评测态下 ask_user 的"用户"是另一个 LLM（环境变量 `USER_AGENT_MODEL` 可换模型），它与被测 Agent 各持独立对话历史（F-051、F-062）。应答参数固定 `temperature=0.0, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0, seed=42`（F-064）——复现分数时必须注明用户代理模型配置。

判分约定（F-062）：`is_successful(self, controller) -> float | tuple[float, str]`，`(0.0, reason)` 失败 / `(1.0, reason)` 成功，未被子类覆盖时转调 `is_successful_async`；`tear_down` 清空 interaction_cache/user_sys_prompt/model_config/chat_history。

`ModelConfig` 是 `tasks/utils.py` 中的 `@dataclass`（字段 `model_name/api_key/url`）；同文件的 `wait_for_execution(controller=None, answer_text=None)` 用 `input()` 等待人工执行，仅测试用（F-064）。

## TaskRegistry 自动扫描

`class TaskRegistry`（`tasks/registry.py`，F-063）：

- `__init__(self, task_set_path: str | None = None)`：默认路径为 `Path(mobile_world.__file__).parent / "tasks" / "definitions"`
- `_scan_and_register_tasks()` 用 `Path(self.task_set_path).rglob("*.py")` 递归扫描（跳过 `__init__.py`），逐文件 `spec_from_file_location` 动态加载
- 注册条件：`issubclass(obj, BaseTask) and obj is not BaseTask and obj.__module__ == module.__name__`，键为类名，重复时覆盖并 warning
- 查询接口：`get_task(task_name)`（缺失抛 KeyError）、`list_tasks()`、`has_task(task_name)`；类属性 `_scan_logged: set[str]` 防重复日志

**新增任务 = 新建一个 .py 文件放进 definitions/ 子目录，重启服务即自动注册**——服务启动时 `initialize_suite_family` 会创建 TaskRegistry 并打印 `Loaded {n} mobile_world tasks`（F-031）。

## 10 场景任务目录

`tasks/definitions/` 下 10 个场景子目录（F-066，任务文件数不含 `__init__.py`）：

| 目录 | 规模 | 代表任务 |
|---|---|---|
| `work/` | 35 个（mattermost_* 16 个） | 办公协作场景：mattermost_*、search_*/extract_*/email 类 |
| `settings/` | 7 个 | open_flight_mode、close_flight_mode、change_wallpaper、adjust_font_icon_min/max、adjust_brigtness_min/max |
| `native/` | 33 个 | set_alarm、take_selfie、read_paper_1..5、check_invoice_1..4、sms_management |
| `messages/` | 23 个 | send_weather_sms、plan_*_route_sms、check_candidate_ask_user |
| `mastodon/` | 41 个 | mastodon_follow、mastodon_post_poll、mastodon_mall_purchase_commodity |
| `map/` | 10 个 | check_distance、check_phone_numbers、text_arrival_time |
| `mall/` | 13 个 | cart_management、item_checkout、buy_cola_ask_user |
| `gmail/` | 21 个 | 邮件场景 |
| `chrome/` | 4 个 | 浏览器场景 |
| `calendar/` | 14 个 | 日历场景 |

`work/assets/visual_instruction/generate_images.py` 为资产生成脚本（F-066）。

## 任务测试脚本

`tasks/test_task.py` 的 argparse 参数：`--task/-t`、`--device/-d`（default "emulator-5554"）、`--question/-q`、`--list/-l`（F-065）：

- `--list` 打印 `registry.list_tasks()` 排序清单
- 否则 `task.run_task(controller=controller, agent_question=args.question)`（注：BaseTask.run_task 实际签名为 `run_task(self, agent_question=None)`，自行创建 `AndroidController(device="emulator-5554")`）

## 相关概念

- [/concepts/05-runtime-controller.md](/concepts/05-runtime-controller.md)——initialize_task 依赖的 AndroidController（load_snapshot/home 等）与 app_helpers
- [/concepts/03-agent-registry.md](/concepts/03-agent-registry.md)——ask_user 交互对端的 Agent 侧
- [/concepts/06-eval-server-mcp.md](/concepts/06-eval-server-mcp.md)——task_tags（"agent-mcp"/"agent-user-interaction"）如何决定工具注入与任务筛选
- [/examples/02-customize-avd-snapshot.md](/examples/02-customize-avd-snapshot.md)——init_state 快照的重制实操
