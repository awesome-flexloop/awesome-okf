---
type: reference
title: LobsterAI 架构洞察（I 阶段，基线 2026.9.4）
description: 基于 R 阶段事实清单（F-la-001~074）提炼的 LobsterAI 架构核心洞察与 concepts/ 知识地图规划。洞察采用「陈述+证据+反常识+行动」四元组结构，证据全部锚定编号事实，不新增事实陈述。
tags: [lobsterai, electron, ai-agent, architecture, insights, i-phase]
sources:
  - id: lobsterai-facts
    resource: doc/bundles/jishu/ai/netease-youdao/lobsterai/references/facts.md
    title: LobsterAI 源码事实清单（R 阶段，基线 2026.9.4）
    source: vendor/netease-youdao/LobsterAI @ 7592cd034a7cb458a8650df0325b4980dd1bc162
  - id: lobsterai-vendor
    resource: vendor/netease-youdao/LobsterAI
    title: LobsterAI 源码（固定基线 2026.9.4 @ 7592cd0）
---

# LobsterAI 架构洞察（I 阶段）

> 本文档为 OKF Wiki I 阶段产物：在 R 阶段事实清单之上提炼架构洞察并规划 concepts/ 知识地图。
> 所有洞察的「证据」字段仅引用 F-la 编号，不引入 facts.md 之外的新事实；E 阶段（concepts/examples）不在本文档范围。

## 一、核心洞察

### 洞察 1：主进程即 AI Agent 运行时中枢——IM 网关、MCP 运行时、技能系统三重角色全部驻留 Electron 主进程

- **陈述**：LobsterAI 把通常分散在后端服务的三类子系统——多平台 IM 网关（`IMGatewayManager` + `NimGateway` 等九个平台）、MCP 工具运行时（`McpStore` + `McpRuntime` + `McpBridgeServer`）、技能系统（`SkillManager` 及 29 个内置 SKILL.md）——全部实现在 `src/main/` 主进程内；渲染进程（13 个 Redux slice + 6 大视图）只承担展示与交互，不直接触碰任何运行时子系统，双方以 30+ 命名空间的 IPC 通道契约通信。
- **证据**：F-la-008（AGENTS.md 声明 Cowork 为产品/会话层、OpenClaw 为唯一 Agent 运行时/网关）、F-la-025/F-la-026/F-la-028（IM 网关类）、F-la-029/F-la-031/F-la-032（MCP 存储/运行时/桥接）、F-la-033（SkillManager）、F-la-037/F-la-038/F-la-039（IPC 通道命名空间与流事件）、F-la-041/F-la-042（渲染进程仅视图路由 + Redux slice）。
- **反常识**：主流认知中「Electron 主进程 = 窗口管理 + 菜单托盘」，重型运行时逻辑应放在独立后端进程或服务中；LobsterAI 反其道而行——把 IM Bot 网关、MCP 工具注册与桥接（含 AskUser 回调、媒体生成、浏览器工具三类工具请求/响应类型）、技能下载升级等「服务端级」能力全部压进单一主进程，以 EventEmitter 事件流而非 HTTP/RPC 连接子系统。其代价与收益只能从源码层推断：换来的是单进程数据零拷贝（同进程直读 SQLite）与部署零依赖，代价是主进程单点复杂度（main.ts 约 1.3 万行）。
- **行动**：借鉴此架构时，先做「运行时负载是否必须跨进程」的判定——若子系统间只共享同一份本地数据（如 SQLite 会话/消息），主进程内聚优于独立服务；同时必须为 IPC 通道建立 `as const` 常量对象契约（LobsterAI 的 `CoworkIpcChannel`/`IpcChannel` 模式），避免手写字符串通道散落各处。

### 洞察 2：btw / goal / rail / steer 四类协议把「人机协作」编码成显式的共享层类型契约

- **陈述**：「打断提问（btw）、持续目标（goal）、会话轨道索引（rail）、流内纠偏（steer）」四种人机协作语义不是 UI 状态机的附属品，而是被建模为 `src/shared/cowork/` 下的独立类型模块：各自有状态枚举（btw 四态、goal 六态、steer 三态+7 种拒绝原因）、上下文/内容长度常量（如 btw 上下文上限 16k 字符、线程内容 50 万字符）、请求/响应接口，再由 `CoworkIpcChannel` 常量对象映射为 IPC 通道。
- **证据**：F-la-043~F-la-052（btw/goal/rail/steer 四大模块的类型、枚举与常量定义）、F-la-044（btw 的六组限长常量）、F-la-051（steer 拒绝原因枚举）、F-la-052（steer 请求可携带附件/图片/选中文本/浏览器标注/kit 等多模态负载）、F-la-055（协议操作映射到 IPC 通道）。
- **反常识**：常见 Agent 产品把「追问、中断、纠偏」实现为前端局部状态 + 一次性消息，协作语义随 UI 重构而漂移；LobsterAI 把每个协作动词提升为一等协议类型（含独立的运行 ID 生成规则、限长常量和可中止的生命周期），且 btw 的 `/btw`、`/side` 双命令别名说明协议设计时已考虑 IM 场景（手机端输入 `/btw` 比找按钮自然）。这类「协议先于界面」的设计使同一套协作语义可复用于 GUI、IM Bot、定时任务等多种入口。
- **行动**：设计 Agent 协作功能时，先为每个协作动词写共享层类型模块（状态枚举 + 限长常量 + 请求/响应接口 + IPC 通道键），再让渲染层与 IM 网关各自消费；限长常量应与状态枚举同文件声明，避免「魔法数字」随实现漂移。

### 洞察 3：SKILL.md 约定 + skills.config.json 注册表构成「文件即技能」的去中心化技能注册机制

- **陈述**：技能的完整元数据约定为单个 `SKILL.md` 文件（frontmatter 含 name/description/official/version），技能的启用与排序由独立的 `skills.config.json` 注册表（version: 1，29 个 defaults 条目，每条形如 `{order, enabled}`）管理；`SkillManager` 负责把内置技能同步到用户数据目录、从 OpenClaw 反向同步、下载升级、启停切换与自动路由提示词构建，形成「内置技能随包分发、用户态技能独立演化」的双层结构。
- **证据**：F-la-033（SkillManager 13 个方法）、F-la-065（29 个 SKILL.md，Glob 实测）、F-la-066（skills.config.json 顶层 version 与 29 条 defaults）、F-la-067（SKILL.md frontmatter 四字段）、F-la-068（29 条 order 全清单）、F-la-069（仅 skin-creator 与 technology-news-search 显式禁用）、F-la-007（README「28 built-in skills」为过期声明，实测 29——注册表与文件双计数可互相校验）、F-la-036（kits IPC 处理器定义 `SKILLS_DIR_NAME='SKILLs'`、`SKILL_FILE_NAME='SKILL.md'` 常量）。
- **反常识**：一般插件系统用中心清单（manifest 索引所有插件）或数据库注册；LobsterAI 让「文件目录结构即技能本体」（每个技能一个子目录、一份 SKILL.md），注册表只携带 order/enabled 两个运行时旋钮，目录清点与注册表计数互相校验（29=29）即可发现文档过期。order 编号还暴露了技能分类的隐性拓扑：10-90 为文档/开发类（docx/web-search/pptx/pdf），110-122 为内容/股票类，200-224 为本地工具/媒体类，298-300 为技能治理三件套（youdaonote/skill-vetter/skill-creator），治理类技能被刻意排在最高段。
- **行动**：实现可扩展技能/插件体系时，用「每技能一目录 + 单约定文件」替代中心清单，注册表只存运行时差异（启用/排序）；CI 中加入「目录 Glob 计数 == 注册表条目数」的一致性断言，可同时拦截文档过期与注册遗漏。

### 洞察 4：13 张表的本地优先 SQLite 承载全部会话状态，迁移用 ad-hoc 列存在性检查而非版本化迁移框架

- **陈述**：应用全部持久化状态集中在一个 SQLite 数据库（better-sqlite3）：13 张表覆盖键值存储（kv）、会话/消息/胶囊（cowork_sessions 含 fork 与 scheduled_task_id 列、cowork_messages、cowork_session_capsules）、配置与记忆（cowork_config、user_memories、user_memory_sources）、Agent/MCP/插件（agents 表 21 列、3 张 MCP 表、user_plugins）、子代理运行（subagent_runs、subagent_messages）；`SqliteStore.create()` 工厂统一建库，迁移通过 `PRAGMA table_info()` 做逐列存在性检查（如 `messages_persisted`）。
- **证据**：F-la-004（better-sqlite3 依赖）、F-la-015（工厂方法 + PRAGMA 迁移）、F-la-016（13 张表逐条计数与全清单）、F-la-017（消息表外键级联删除 + 会话索引）、F-la-018（agents 表 20 列含 JSON 存储的 skill_ids）、F-la-019~F-la-022（CoworkStore 40+ 方法分会话/消息/配置记忆/其他四组）、F-la-073（tests/ 含 sqlite-backup 子目录）。
- **反常识**：「Agent 应用需要服务端 + 云端同步」是默认假设；LobsterAI 证明会话、消息、记忆、Agent 定义、MCP 服务器配置、定时任务绑定、插件安装、子代理运行记录全部可以落在用户本机一个 SQLite 文件里，多平台 IM 网关反而成为「把本地 Agent 暴露到云端」的反向桥。迁移策略同样反主流：不用 knex/drizzle 等版本化迁移框架，而是对每张表做 `PRAGMA table_info()` 列存在性检查就地补列——代码量小且无迁移历史包袱，适合「schema 演进以加列为主」的场景。
- **行动**：本地优先 Agent 产品的数据层可直接参考此表划分（会话/消息/配置记忆/外部集成/子代理五域）；选择 ad-hoc 迁移前须确认团队能接受「无迁移历史、无法回滚」的约束，若 schema 会出现改列/删列需求则应回到版本化迁移。

### 洞察 5：定时任务子系统用 15 秒轮询 + 三层映射取代事件驱动调度，把 cron 语义委托给 OpenClaw 网关

- **陈述**：定时任务采用 Renderer → Main → OpenClaw Gateway 三层架构，主进程 `CronJobService` 以 15 秒轮询（`pollOnce`/`startPolling`）与网关对账任务状态，而非依赖推送/事件；调度模型为策略模式（`ScheduleAt`/`ScheduleEvery`/`ScheduleCron` 判别联合），负载为判别联合（`AgentTurnPayload`/`SystemEventPayload`），并配三组正交的运行旋钮：投递模式（none/announce/webhook）、会话目标（main/isolated）、唤醒模式（now/next-heartbeat），全部任务状态经 `mapGatewaySchedule/TaskState/Job/Run` 四组映射函数规整为本域模型。
- **证据**：F-la-057/F-la-058（三层架构与四大设计理念）、F-la-059（Schedule 判别联合）、F-la-060（Payload 判别联合与任务/运行接口）、F-la-061（DeliveryMode/SessionTarget/WakeMode 枚举）、F-la-062（TaskStatus 四态 + DefaultAgentId='main'）、F-la-063（17 个 `scheduledTask:` 前缀 IPC 通道）、F-la-064（CronJobService 方法清单含轮询与四组映射）、F-la-016（cowork_sessions 含 `scheduled_task_id` 列——定时任务与会话双向绑定）。
- **反常识**：定时调度通常追求「精确触发」（系统 cron、setTimeout 队列、时间轮）；LobsterAI 明示采用 15 秒轮询——故意用轻微延迟换取「网关是唯一调度事实源」的架构纪律：本地只是网关任务状态的镜像视图，断线重连后对账即可自愈，不存在本地已触发但网关不知情的状态不一致。WakeMode 的 `next-heartbeat` 进一步说明轮询节奏与心跳周期对齐，任务执行被建模为「请求网关安排一次 Agent turn」而非本地直接执行。
- **行动**：当调度的事实源在远端（网关/SaaS）时，优先用「短周期轮询 + 全量对账 + 映射函数规整」替代本地预调度；判别联合建模（kind 字段）让 Schedule/Payload 的可扩展性优于枚举拼接，新增一种调度类型无需改动既有类型分支。

## 二、知识地图（concepts/ 规划）

> LobsterAI 为 6 束中规模最大的完整 Electron 应用，规划 11 篇概念文档（00-10），按「入门→高级」递进。编号即推荐阅读顺序；「前置依赖」列为空者可直接阅读。各篇引用的事实编号区间供 E 阶段撰写时取材。

| 编号 | 标题 | 一句话概要 | 前置依赖 | 引用事实编号 |
|---|---|---|---|---|
| 00 | 全景与分层架构 | Cowork（产品/会话层）与 OpenClaw（唯一 Agent 运行时/网关）的职责切分，及 Electron 主进程/渲染进程/共享层/定时任务四区布局总览。 | — | F-la-001~F-la-009, F-la-041, F-la-042, F-la-057 |
| 01 | 主进程窗口模型与安全基线 | 无边框窗口的主题化配置、严格 webPreferences 安全基线（nodeIntegration 关闭/contextIsolation/sandbox），及 webview 挂载时的强制偏好重写。 | 00 | F-la-010~F-la-014 |
| 02 | IPC 通道契约体系 | preload 按命名空间分组的 30+ 通道、流式推送事件族、平台参数化通道模式，与 `as const` 常量对象契约规范。 | 00 | F-la-037~F-la-040, F-la-055, F-la-063 |
| 03 | SQLite 本地优先存储层 | SqliteStore 工厂建库、13 张表的五域划分、PRAGMA 列存在性迁移，以及消息级联删除与索引设计。 | 00 | F-la-004, F-la-015~F-la-018 |
| 04 | 会话与消息数据管理 | CoworkStore 四组 40+ 方法、会话 fork（含 worktree 模式）与分页/搜索/连续性胶囊的数据访问模式。 | 03 | F-la-019~F-la-022, F-la-056 |
| 05 | 人机协作四类协议 | btw（打断提问）/goal（持续目标）/rail（轨道索引）/steer（流内纠偏）的状态机、限长常量与多模态请求负载设计。 | 02, 04 | F-la-043~F-la-054 |
| 06 | Agent 与预设体系 | AgentManager 委托模式、agents 表 20 列（含 JSON skill_ids）、内置预设 Agent 的增删查。 | 03, 04 | F-la-018, F-la-023 |
| 07 | MCP 集成与桥接运行时 | MCP 服务器 CRUD、launch resolution（来源指纹/npx 判定）、AskUser/媒体生成/浏览器工具三类桥接工具协议。 | 02, 03 | F-la-029~F-la-032 |
| 08 | 多平台 IM 网关 | IMGatewayManager 九平台实例管理、NIM 网关方法族、QQ 媒体下载的限额与清理策略、配对审批通道。 | 02, 05 | F-la-025~F-la-028, F-la-039 |
| 09 | 技能系统与注册机制 | SKILL.md 单文件约定、skills.config.json 注册表（order/enabled）、SkillManager 同步/下载/升级/自动路由全生命周期。 | 02 | F-la-033, F-la-036, F-la-065~F-la-069 |
| 10 | 定时任务子系统 | 三层架构与 15 秒轮询对账模型、Schedule/Payload 判别联合、投递/会话/唤醒三组正交旋钮与映射函数。 | 05, 07 | F-la-057~F-la-064, F-la-016 |

> 说明：测试与质量工程（F-la-070~F-la-074，vitest 双 include、tests/ 顶层 38 个测试文件（递归 43 个）、skins 8 个并置测试）与 skins/插件扩展面（F-la-035、F-la-006、F-la-034）因篇幅未单列概念文档，其事实已由 E 阶段撰写 00/09 等篇时按引用区间取用。
