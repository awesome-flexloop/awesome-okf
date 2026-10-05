---
type: Concept
title: "消息网关进阶：slash 流水线、HITL、语音与定时任务"
description: "v1.0.2b5 网关深化面：25 条 slash 命令、GlobalProcessor 42 方法处理流水线、媒体入库与视觉限制、HITL 人审、WS/CLI 通道细节、扫码绑定与 bot 创建、语音预设、cron 双默认值。"
tags: [octop, gateway, slash, hitl, media, voice, cron, websocket]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: "Octop 源码事实清单 F-329~F-381"
  - id: gateway
    resource: /references/gateway.md
    title: Gateway 源码信源
---

# 消息网关进阶：slash 流水线、HITL、语音与定时任务

网关与通道的基础架构（Gateway/ChannelManager、内置 WS/CLI 通道、IM 注册、抢占式 `/stop`、media backend 装配时机）已在 [03-gateway-channels.md](03-gateway-channels.md) 讲过，本章只展开 v1.0.2b5 新增与深化的面：slash 目录全貌、消息处理流水线、媒体/HITL/语音/cron 子系统与扫码绑定。

## slash 命令：25 条与 5 个类目

命令元数据是 frozen dataclass `SlashCommandSpec`（slash/catalog.py:19-66），携带 name、aliases、category、origins、client_action、hidden、persist_checkpoint 等字段；类目 Literal 为 `core/session/media/system/debug`，显示顺序 `CATEGORY_ORDER` 同序（F-337）。`CATALOG` 经计数恰 25 条，但分布并不均匀（F-338）：

| 类目 | 条数 | 命令（主名逐字） |
|------|------|------------------|
| core | 8 | status、model、mode、new、compact、stop、history、token |
| session | 10 | list、switch、resume、approve、reject、pending、title、delete、pin、unpin |
| system | 7 | help、memory、cron、agent、skills、connectors、exit |
| media | 0 | 类目保留，CATALOG 内零条目 |
| debug | 0 | 类目保留，CATALOG 内零条目 |

别名与可见性是目录的重要组成（F-339）：model→models；mode→ask/plan/craft；new→clear；stop→cancel；list→topics/sessions；exit→quit。hidden 的有 unpin、exit。origins 收窄的有：memory/cron/agent/skills/connectors 仅 `{"ui","cli"}`，approve/reject/pending 仅 `{"im","cli"}`，exit 仅 `{"cli"}`。client_action 映射 new→new_chat、stop→cancel_stream、agent→switch_agent。命令语法由 `_COMMAND_RE = re.compile(r"^\s*/[a-zA-Z][\w-]*(?:\s[\s\S]*)?$")` 识别（F-340）。

### dispatcher / runner / ctx 三件套

- **Handler 签名**：`Callable[[SlashDispatcher, SlashCommand, SlashCtx, SlashSink], Awaitable[None]]`（F-340）。自注册 handler 未命中时委托 harness 的 RuntimeSlashDispatcher；register 同时注册主名与别名；OctopError 输出为 `sink.text(f"error: {exc.message}")`（F-342）。
- **SlashCtx**：locale 默认 "zh"、时区默认 "Asia/Shanghai"；subject_id/chat_type 由 `session_key.split(":", 3)` 解析；短名找线程用后缀匹配，list_threads 取 limit=200（F-341）。
- **runner**：`try_handle_slash` 返回三元组 `(handled, lines, actions)`，sink 是 BufferSink；help 输出按 CATEGORY_ORDER 分组（F-342）。
- **handler 合成**：`GATEWAY_HANDLERS` 由 memory(1) + SESSION(8) + PLATFORM(6: help/token/cron/agent/connectors/exit) + COMPOSITE(6) + HITL(3) 合并而成（F-343、F-344）。runtime bridge 里仅 stop/cancel 不创建 thread；HITL 三命令在 Dashboard 侧只给引导提示（F-342、F-344）。

## GlobalProcessor：42 个方法的一条流水线

`GlobalProcessor` 定义于 process/processor.py:131，类内经计数有 42 个方法，入口 `__call__`，核心流式路径为 iter_turn_chunks / iter_hitl_resume_chunks / _build_dashboard_request（F-348）。一条入站消息依次穿过 process/ 包 9 个模块的协作：

```
InboundMessage
  ├─ message_keys      元数据键、chat_type 归一、user_id 解析      (F-345,F-346)
  ├─ response_mode     invoke / stream，QQ c2c 流式特判            (F-347)
  ├─ harness_request   构造 harness 请求 + 群聊上下文              (F-349)
  ├─ stream_project    token/tool/hitl/state 事件投影             (F-350)
  ├─ usage             token 七字段记账                            (F-351)
  └─ agent_resolve     media backend 解析                         (F-352)
```

- **message_keys**：持久化元数据键经点算 19 个，另有 7 个"即用即抛"的推送键（msg_id、response_url、webhook_url 等）；`chat_type == "single"` 归一为 dm；dashboard/cli 的 subject_id 直接当 user_id，外部 IM 回落 agent_owner_id（F-345、F-346）。
- **response_mode**：`ChannelResponseMode = Literal["invoke","stream"]`，默认 invoke；collapse 投影里 TOOL_START 仅对 tool_key=="ask_agent" 保留前置文本，ERROR 清缓冲，COMPLETED 产出最终 MESSAGE（F-347）。
- **harness_request**：必填键 messages/thread_id/user/source；群聊注入两段固定标题，中文字面"【群聊背景｜仅供参考】""【当前群消息｜请回复这条消息】"，匿名成员名"群成员{n}"（F-349）。
- **stream_project**：分支覆盖 token、reasoning、tool_call_chunk、tool_result、hitl_required、state_update；投影状态记录 hitl_paused/hitl_pending_id 与每个工具的节点/缓冲（F-350）。
- **usage**：记录 7 个 token 字段（input/uncached_input/cache_read/cache_write/output/reasoning/total），source 字面 `f"{msg.channel_type}/{msg.channel_id}"`（F-348、F-351）。
- **agent_resolve**：用 Agent 的 config.max_upload_bytes 构造 AgentBackedMediaBackend（F-352）。频道侧的"💭 Thinking: {content}"清洗模板通过 install_channel_thinking_clean 猴子补丁 BaseChannel._clean_output 实现，模块级 `_PATCHED` 防重入（F-352）。

会话侧另有关键常量：session key 全局唯一格式 `f"{agent_id}:{channel_type}:{channel_subject_id}:{channel_chat_type}"`，thread_id 用 `f"thr_{new_ulid()}"`；团队房间键带 "team:"/"peer:" 前缀（F-330、F-331）。历史回填队列默认容量 100、按 key 去重、满则返回 False（F-332）。

## 媒体：142 扩展名、视觉四限与路径封锁

入站文件识别表经计数含 **142 个扩展名键**，另有 **37 个别名键**（两字典合计 179 键）（F-354）。文件名经过控制字符与 `<>:"/\|?*` 清洗，时间戳命名正则 `^(\d{10,})_(.+)$`（F-355）；上传落盘走 Agent 工作区的 inbound/outbound 目录，read 不到数据抛 FileNotFoundError（F-353、F-356）。

发给多模态模型的图片有四条硬限制（F-358）：

```python
VISION_MAX_BYTES = 2 * 1024 * 1024   # 单张 2MB
VISION_MAX_COUNT = 4                 # 每轮最多 4 张
VISION_MAX_SIDE  = 1568              # 最长边压缩到 1568
VISION_JPEG_QUALITY = 85             # 重编码 JPEG 质量 85
```

工具产物侧，6 个媒体推送工具（send_file、send_file_to_user、desktop/mobile_screenshot、generate_image/video）的输出路径会被正则捞出并转成附件（F-357）。为防止 Agent 借媒体能力读取宿主敏感文件，backend_files 显式封锁 Unix 7 个前缀（/users/、/tmp/、/home/、/var/、/private/、临时目录与 IE 缓存）和 Windows 4 个盘符前缀（c:/users/ 等），连同浏览器画像目录 `.harness-browser`/`.octop-browser` 一并拒绝（F-359）。

## HITL 人审：30 分钟 TTL 的待审批存储

- **store**：状态 Literal 4 值 pending/approved/rejected/expired；`_DEFAULT_TTL_SECONDS = 30 * 60`（1800 秒）；pending_id 用 `secrets.token_hex(2)` 生成去重；记录 12 字段；register 时先 GC，并把同一 session_key 的旧 pending 置 expired（F-360、F-361）。
- **coordinator**：3 个 dataclass（HitlStreamContext、HitlSlashOutcome、HitlAnswerOutcome）+ HitlChannelCoordinator，文件内 20 个函数/方法，覆盖 register_from_request、决策构建、ask 回复收集与两条迭代解决路径（F-362）。
- **format**：ask_user_question 工具转 ask 卡片；选项键用 ascii_lowercase，选择输入正则支持中英文逗号/顿号/空白分隔；参数截断上限 400 字符（F-363）。会话策略侧还定义了 ask/allow_all/allow_tools 三模式与最多 64 个工具名的门控（F-264）。

## WS hub 与 CLI 通道细节

WebSocketHub 内部维护 6 个容器（连接、线程订阅、连接→线程/用户反向映射、活跃 turn）（F-335）；单连接同时最多订阅一个 thread，切换先退订（F-335）。通道 ID 逐字 `WS_CHANNEL_ID = "octop-dashboard"`、`CLI_CHANNEL_ID = "octop-cli"`，两虚拟通道默认 show_thinking=True、show_tool_hints=True、不限速、无 debounce（F-336）。WS 帧 type 字面集合为 error/done/token/attachment，attachment 载荷含 kind/mime_type/data（F-336）。Dashboard 主动推送帧 type 为 "dashboard_push"（F-333）。CLI 侧的每轮入站由 prepare_cli_turn / build_cli_inbound 两个 async 函数构造，cli 包注释自述为"进程内聊天传输：连接 hub + 虚拟 IM 通道"（F-364）。

## 扫码绑定与 bot 创建器

- **企业微信**：两 URL 模型——生成二维码 `https://work.weixin.qq.com/ai/qc/generate?source=octop&plat={code}`，轮询 `https://work.weixin.qq.com/ai/qc/query_result`；plat 按系统 darwin/windows/linux=1/2/3；generate 超时 15s、poll 10s，成功取 bot_info.botid 与 secret（F-365）。
- **钉钉**：三端点设备码流——`/app/registration/init`、`/app/registration/begin`、`/app/registration/poll`（基址 `https://oapi.dingtalk.com`，超时 15s，errcode!=0 即失败；begin 必返 device_code/user_code/verification_uri_complete）（F-366）。
- **飞书 bot 创建器**：支持 feishu/lark 两平台，open_base `https://open.feishu.cn`，状态文件前缀 octop-feishu-bot/octop-lark-bot，最低 OAPI 版本 (1,5,5)，暴露 init/create/cleanup 命令（F-367、F-369）。
- **元宝 bot 创建器**：域 `bot.yuanbao.tencent.com`，扫码绑定两接口 get-scan-bind-code / check-scan-bind-status，轮询间隔 3s、最多 3 次，并在云主机上读取 metadata.tencentyun.com 的实例 ID 与公网 IPv4（F-368）。

## 语音：5 个 kind、6 条预设

预设加载后逐条点算为 6 个 dict：browser、edge、tencent、openai、mimo-stt、mimo-tts——即 5 个 kind、其中 mimo 拆成 STT/TTS 两条（F-370）。browser/edge/tencent 标记 free=True，openai 与两条 mimo 非免费（mimo-tts 另有 limited_free）（F-370）。

| kind | 要点 |
|------|------|
| browser | 浏览器原生语音；服务端调用抛 BrowserOnlyError（F-371） |
| edge | TTS 默认音色 zh-CN-XiaoxiaoNeural（F-371） |
| tencent | ASR action SentenceRecognition（16k_zh，ap-guangzhou）；TTS TextToVoice，VoiceType 101001、mp3（F-372） |
| openai | base `https://api.openai.com/v1`，STT whisper-1，TTS tts-1/alloy（F-371） |
| mimo | base `https://api.xiaomimimo.com/v1`，模型 mimo-v2.5-asr / mimo-v2.5-tts，8 个预设音色（冰糖、茉莉、苏打、白桦、Mia、Chloe、Milo、Dean），SSE 结束标记 `[DONE]`（F-373） |

支持的输出格式共 8 种：mp3、wav、ogg-opus、m4a、amr、silk、speex、pcm（F-372）；STT 超时 60s、TTS 120s（F-371）。编排面很薄：voice/manager.py 只有两个类——ResolvedVoiceProvider 与 VoiceManager，按 kind 分派到上述适配器函数对（F-374）；STT 失败统一结果类型 STTResult（text、confidence）（F-371）。

## cron：6 个工具、3 种触发器前缀与两处默认值

Agent 可调用的定时任务工具恰 6 个：cronjob_list/get/create/update/delete/run_now；run_now 返回 `{"triggered": cron_id}`，delete 返回 `{"deleted": cron_id}`（F-377）。触发器用前缀字符串表达（F-376）：

- `interval:N`——N 转 int 且必须 >0；
- `cron:`——后接标准 5 字段 unix crontab（周几用 sun..sat）；
- `date:`——后接 datetime.fromisoformat 可解析的一次性时刻。

任务有两种投递类型（F-375）：`text`（直接向通道推原文）与 `agent`（构造 harness 请求让 Agent 跑一遍，[03-gateway-channels.md](03-gateway-channels.md) 的 push_text_from_session 即此链路）。

**需要如实注意的两处字面默认值**（F-375、F-377、F-379）：

| 入口 | task_type 默认 |
|------|----------------|
| 领域常量 `DEFAULT_CRON_TASK_TYPE` | `"agent"`（task_type.py:8） |
| `CronCreateSpec` dataclass 字段 | `"agent"`（manager.py 侧 CronCreateSpec，F-379） |
| LLM 工具 `cronjob_create` 的形参默认 | `"text"`（cron/tools.py:151-154，F-377） |

即：经 Agent 工具创建的定时任务，模型不显式给 task_type 时落为 text；经程序内部 spec 构造时缺省为 agent。越界值经 require 校验报错 "task_type must be 'text' or 'agent'"，normalize 则把未知值归一成 agent（F-375、F-377）。ID 形如 `f"c{new_short_id(6)}"`（如 cA1B2C3），Crockford base32 字母表去除了易混字符（F-381）；调度器默认时区 Asia/Shanghai，运行计数指标 cron_runs_total / cron_errors_total（F-378、F-379）；投递命令是含 10 字段的 frozen dataclass，fresh_thread 为真时先按 session key 重置上下文（F-380）。

## 相关概念

- [/concepts/03-gateway-channels.md](03-gateway-channels.md) —— 网关基础架构与通道注册
- [/concepts/10-agent-teams.md](10-agent-teams.md) —— team host 通道强制 stream 模式（F-334）
- [/concepts/06-cli-commands.md](06-cli-commands.md) —— /exit 等仅 CLI 命令的宿主侧处理
