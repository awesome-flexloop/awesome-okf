---
type: Concept
title: 消息网关与 Cron 调度——GatewayRunner、平台双轨制与会话存储
description: 讲清 GatewayRunner 生命周期、22 枚举/21 实现/32 文件三个口径、会话三件套 SQLite 存储，以及没有 Scheduler 类的函数式 Cron 调度。
tags: [kylin-agent-runtime, gateway, cron, messaging, session]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
---

# 消息网关与 Cron 调度

> 术语速记：**GatewayRunner**（网关主类，管理所有消息平台适配器的生命周期）、**Platform**（内置平台枚举）、**SessionStore**（多平台会话身份与用量的持久化存储）、**tick**（Cron 的函数式轮询入口）。

消息网关把 Agent 同时挂到 Telegram、飞书、钉钉、微信等二十余个消息面上；Cron 则让 Agent 以定时作业方式无人值守运行。两者共享会话模型与投递设施，但在架构风格上一个是面向对象装配，一个是纯函数式调度。平台接入机制还体现了洞察 I-2 所说的"双轨制"，是全仓扩展哲学最不一致的地方。

## GatewayRunner：生命周期与装配

网关主类 `class GatewayRunner` 位于 gateway/run.py:1401，构造器 `__init__(config: Optional[GatewayConfig] = None)`（:1424）（F-102）。它的生命周期方法只有三个：

| 方法 | 位置 | 职责 |
|---|---|---|
| `async start()` | run.py:3595 | 装配并连接全部已配置适配器，开始消费消息 |
| `async stop(restart, detached_restart, service_restart)` | run.py:5564 | 关停适配器，可按标志请求重启 |
| `request_restart(detached, via_service)` | run.py:3501 | 请求重启（脱离进程或走 systemd 服务） |

注意 **GatewayRunner 没有 `run` 方法**（F-102）——启动语义在 `start()`，不要按类名想当然地找 `runner.run()`。

装配字段（F-103）：`self.adapters: Dict[Platform, BasePlatformAdapter]` 持有平台到适配器实例的映射；`session_store` 复用 `SessionStore`；`delivery_router` 为 `DeliveryRouter`；`_agent_cache` 是按会话缓存 Agent 的 `OrderedDict`；另有 `_failed_platforms` 记录启动失败的平台，使单个平台故障不拖垮整个网关。适配器由工厂 `_create_adapter(platform, config)`（run.py:5899）创建，**先查插件注册表 `platform_registry`，未命中再走内置 if/elif 链**。

## 启动入口

进程级入口是模块级协程 `start_gateway(config, replace, verbosity)`（run.py:17793）；`main()`（:18216）用 argparse 接 `--config/-c` 与 `--verbose/-v`，文件尾部 `__main__` 守卫在 :18248（F-104）。用户日常通常不直接调用它，而是走 CLI 的 `gateway` 二级命令或 systemd 服务（见 [示例 02](/examples/02-gateway-and-cron-usage.md)）。

## 网关配置对象

配置层由一组 dataclass 描述（F-109，gateway/config.py）：`PlatformConfig`（单平台开关与参数）、`StreamingConfig`（流式输出策略）、`HomeChannel`（家庭频道/默认投递目的地）、`SessionResetPolicy`（会话重置策略），聚合为 `GatewayConfig`。加载入口 `load_gateway_config()`（config.py:682）先经 `_validate_gateway_config` 校验，再由 `_apply_env_overrides` 用环境变量覆盖文件配置——大量平台凭证与行为开关以 `TELEGRAM_*` 等环境变量形式在加载期回填（config.py:1019-1051 可见 Telegram 一组变量的回填）。

## 一条消息的生命周期

1. 适配器 `connect()` 后把入站消息规范化为 `MessageEvent`，经 `MessageDeduplicator` 去重与 `TextBatchAggregator` 批量聚合后进入网关（F-111/F-114）；
2. 网关以 `SessionSource` 构建 `session_key`，从 `SessionStore` 取对应 `SessionEntry`（token 用量、成本、重置/挂起状态）；
3. 命中 `_agent_cache` 或新建 `AIAgent`，执行对话环；产出经 `DeliveryRouter` 投递，单条输出受 4000 字符上限约束（F-115）；
4. 流式场景由 stream_consumer "先发后编辑"持续更新消息，运行时页脚附 `(model, context_pct, cwd)`（F-116）。

## 会话三件套与 SessionStore

多平台身份与会话状态由三个数据类描述（F-105，gateway/session.py）：

- `SessionSource`（:71）：消息来源身份，含 `platform` / `chat_id` / `chat_name` / `chat_type` / `user_id` / `thread_id` 等，带 `to_dict` / `from_dict`；
- `SessionContext`（:160）：一次会话的聚合上下文，含 source、`connected_platforms`、`home_channels`、`shared_multi_user_session`、`session_key`、`session_id`；
- `SessionEntry`（:425）：会话计量与状态条目，含 **input/output/cache token 计数、`estimated_cost_usd` 成本估算、`was_auto_reset` 自动重置标记、`suspended`、`resume_pending`** 等字段。

`class SessionStore`（session.py:668）持有内存 `_entries` 与一个 SQLite SessionDB；**SQLite 不可用时回退到旧版 JSONL 文件**（:673、:691 的回退警告）（F-106）。它还提供 `build_session_key`（:600）与 `is_shared_multi_user_session`（:578）处理多用户共享会话的身份归并。

会话身份在异步任务间靠 ContextVar 传播（F-107，gateway/session_context.py:51-70）：**11 个会话变量**（平台、chat_id、chat_name、thread_id、user_id、user_name、session_key、session_id、TERMINAL_CWD、project_id、message_id）加 **3 个 cron 投递变量**（platform/chat_id/thread_id），`get_session_env` 在未设置时回退 `os.environ`。模型切换则由 `SessionModelController`（session_models.py:96）按 revision 生效。

## 平台双轨制：22 / 21 / 32 三个口径

这是最容易混淆的部分（洞察 I-2、勘误 E-002），必须分清三个数字：

| 口径 | 数值 | 含义 |
|---|---|---|
| `Platform` 枚举内置成员 | 22 | `LOCAL` + 21 个外部平台（F-108，config.py:100-129），计数见 Q-002 |
| 适配器实现 | 21 | 20 个一对一适配器文件 + qqbot 子包里的 1 个（F-112/F-113） |
| platforms/ 直接子文件 | 32 | 20 适配器 + `base.py` + `helpers.py` + 10 个辅助文件 = 32（Q-002） |

22 个枚举成员按用途分三类：

| 分类 | 成员 |
|---|---|
| 国际消息/SaaS（11） | telegram、discord、whatsapp、slack、signal、mattermost、matrix、bluebubbles、email、sms、homeassistant |
| 国产平台（7） | dingtalk、feishu、wecom、wecom_callback、weixin、qqbot、yuanbao |
| 工程/本地接口（4） | local、api_server、webhook、msgraph_webhook |

双轨的关键事实（I-2）：

1. **内置平台硬连**：`Platform` 枚举固定 22 个成员，`_create_adapter` 用 if/elif 链逐个绑定适配器；枚举通过 `_missing_`（config.py:131）支持插件名动态造成员，`_scan_bundled_plugin_platforms`（:176）扫描插件平台。
2. **注册表只服务插件**：`PlatformRegistry`（platform_registry.py）的 `PlatformEntry` 默认 `source="plugin"`，模块单例 `platform_registry` 提供 register/get/all_entries/plugin_entries/create_adapter；快照内观察不到内置平台的注册调用方（F-110）。
3. 因此新增一个**内置**平台要同时改枚举与工厂两处；新增**插件**平台只需注册。这与工具"丢文件即注册"的开放模型形成鲜明对比。

## 适配器基类与平台实现

所有适配器继承 `class BasePlatformAdapter(ABC)`（gateway/platforms/base.py:1290），必须实现 **4 个抽象方法**（F-111）：

1. `async connect()`（:1564）；
2. `async disconnect()`（:1573）；
3. `async send(chat_id, content, reply_to, metadata) -> SendResult`（:1578）；
4. `async get_chat_info(chat_id)`（:3661）。

基类还配套 `MessageEvent` / `SendResult` / `MessageType` / `ProcessingOutcome` 等数据类型，并提供 `send_draft`、`send_clarify`、`send_typing` 等非抽象能力。20 个一对一适配器覆盖 Telegram/Discord/Slack/邮件/钉钉/飞书/企业微信/微信/元宝等（F-112）；QQ 适配器 `QQAdapter` 单独位于 `platforms/qqbot/adapter.py:155` 子包，`platforms/__init__.py` 以 PEP 562 `__getattr__` 惰性再导出 QQAdapter 与 YuanbaoAdapter（F-113）。共享逻辑沉在 helpers.py 的 `MessageDeduplicator`（:27）、`TextBatchAggregator`（:81）、`ThreadParticipationTracker`（:201），另有 10 个辅助文件处理飞书评论、企微加解密、元宝协议/贴图、Signal 限流、Telegram 网络等（F-114）。

## 投递、配对、目录与运维套件

- **投递**：`DeliveryRouter` 的 `deliver` / `_deliver_to_platform` 统一出口，单条消息上限 `MAX_PLATFORM_OUTPUT = 4000`（F-115）。
- **配对授权**：`PairingStore` 管理新用户准入，含 `is_approved` / `list_approved` / `revoke`，以及配对码 TTL、限流与最大失败次数等常量（F-115）。
- **频道目录**：`build_channel_directory` / `resolve_channel_name` 把人类可读的频道名解析为平台投递目标（F-115）。
- **运维**：HookRegistry 从钩子目录发现网关钩子；运行锁/PID（`acquire_gateway_runtime_lock` / `write_pid_file` / `is_gateway_running`）；服务重启退出码 `GATEWAY_SERVICE_RESTART_EXIT_CODE = 75`；RSS 内存监控线程（默认 300 秒）；关停取证 shutdown_forensics；"先发后编辑"的流式消费 stream_consumer；默认运行时页脚字段 `(model, context_pct, cwd)`；斜杠命令授权 slash_access（F-116）。
- 另有会话镜像 mirror_to_session、WhatsApp 标识归一化、贴图缓存等本地化设施（F-117）。

## Cron：没有 Scheduler 类的函数式调度

`cron/` 包刻意采用函数式风格——**不存在 Scheduler 类**（F-125）：

- 执行入口 `run_job(job)`（cron/scheduler.py:1232）与实现体 `_run_job_impl`（:1239）；轮询入口 `tick(verbose=True, adapters=None, loop=None)`（:1885），由外部（CLI `cron tick` 或常驻进程）周期性调用。
- 投递由 `_resolve_delivery_targets` / `_deliver_result` 负责，可把结果发回来源平台或本地。
- **Prompt 注入拦截**：作业提示词由 `_build_job_prompt`（:1042）组装后，必经 `_scan_assembled_cron_prompt`（:1207）扫描注入模式，命中则抛出 `CronPromptInjectionBlocked`（:48），防止脚本 stdout 或技能内容伪造指令。

作业是普通 **dict 记录**而非 ORM 对象（F-126，cron/jobs.py）：`create_job`（:509-527）的字段包括 `prompt` / `schedule` / `name` / `repeat` / `deliver` / `origin` / `skill` / `skills` / `model` / `provider` / `base_url` / `script` / `context_from` / `enabled_toolsets` / `workdir` / `profile` / `no_agent`；配套 `parse_schedule` / `compute_next_run` / `load_jobs` / `save_jobs` / `list_jobs` / `pause_job`，歧义引用抛 `AmbiguousJobReference`。其中 `script` 支持用脚本 stdout 喂给作业、`no_agent=True` 时可只跑脚本不调模型。桌面侧会话由 `reconcile_desktop_job_sessions(jobs, db)`（cron/desktop_sessions.py:15）对账（F-127）。

CLI 侧提供 `gateway` 二级命令（run/start/stop/restart/status/install/uninstall/list/setup/migrate-legacy，F-136）与 `cron` 二级命令（list/create/edit/pause/resume/run/remove/status/tick，其中 tick 为"运行一次到期作业后退出"），具体操作见 [示例 02](/examples/02-gateway-and-cron-usage.md)。

## 相关概念

- [07-memory-and-context](/concepts/07-memory-and-context.md)：SessionDB（SessionStore 的 SQLite 后端）与 InsightsEngine 的 gateway 渲染。
- [04-tool-system](/concepts/04-tool-system.md)：对照工具注册表的开放模型，理解平台双轨制。
- [09-acp-mcp-protocols](/concepts/09-acp-mcp-protocols.md)：MCP 服务器把网关会话/事件暴露给外部客户端。
- [示例 02：网关与 Cron 实操](/examples/02-gateway-and-cron-usage.md)
