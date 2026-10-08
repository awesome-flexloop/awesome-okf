---
type: spec-insights
title: Octop 架构洞察
---

# Octop 架构洞察

> I阶段产出：基于 F-001~F-133 源码事实提炼的架构洞察。

## I-01：Greenfield 延迟绑定——首次启动不打开数据库

**陈述**：OctopServer 在全新 SQLite 安装时故意延迟打开控制面数据库，先以"无 DB"状态启动 HTTP 服务，等 setup wizard 通过 `/setup/database` 选择后端后再调用 `bind_control_plane()` 热绑定。

**证据**：F-035（`start()` 中 `should_defer_control_plane_db` 判断为 True 时仅生成 wizard 密码后返回，services/app_runtime 均为 None）、F-036（`bind_control_plane()` 幂等绑定 DB 并 boot runtime）、F-099（`should_defer_control_plane_db` 仅对无 DB 文件、无 PG 配置、无 `OCTOP_DATABASE_*` 环境变量的全新 SQLite 返回 True）、F-033（`AppRuntime.replace_services` 支持运行时热交换 SharedServices）。

**反常识**：多数自托管应用在启动时即打开数据库并迁移 schema；Octop 反其道而行——HTTP 层先活起来，让用户通过浏览器向导完成数据库选型（SQLite vs PostgreSQL），再热绑定运行时。这意味着 FastAPI 路由必须能处理 `server.services is None` 的"未绑定"状态，setup lockdown 中间件在此期间封锁非 setup 路由。

**行动**：理解 `database_bound` 属性和 setup lockdown 中间件的协作；新增路由时须考虑 services 可能为 None 的窗口期；二次开发若需在启动时访问 DB，应挂在 `_boot_runtime` 之后而非 `start()` 早期。

## I-02：组合根独占——launch.py 是唯一同时接触 infra 与 api 的模块

**陈述**：架构通过严格的依赖方向禁令（dashboard→api→infra→utils）保证领域层不感知传输层，`launch.py` 作为唯一的组合根（composition root）同时导入 `OctopServer` 和 `build_app`，将二者在 uvicorn 进程中装配。

**证据**：F-029（launch.py 同时导入 `infra/server` 和 `api/app`）、F-128（依赖流向内）、F-129（硬禁令：infra 不得导入 api/cli/launch；api 不得导入 cli/launch；cli 不得导入 api）、F-130（只有 launch.py 可同时导入二者）、F-108（`build_app(server)` 接收已启动的 OctopServer 实例而非自己构造）。

**反常识**：许多 FastAPI 项目在 app 工厂内部直接初始化数据库连接和业务服务；Octop 的 `build_app` 只接收一个已构造好的 `OctopServer`，自身不做任何领域初始化。这使得同一 OctopServer 可以被 CLI embedded 模式（`octop acp`、`chats repl`）独立启动，无需经过 HTTP 层。

**行动**：新增领域服务时在 `infra/` 中实现并在 `_boot_runtime` 中装配；新增 HTTP 路由时只做"校验→调用 infra→映射错误"；不要在 router 中 import repos 或构造服务。

## I-03：外部 Harness 三件套委托——Octop 自身不实现 Agent 运行时

**陈述**：Octop 的核心 AI 能力（Agent 执行、IM 网关、记忆、浏览器）全部委托给腾讯内部的外部包 `orcakit-harness-agent`、`harness-gateway`、`harness-memory`、`harness-browser`，Octop 自身只做编排、持久化、多租户和 HTTP/CLI 适配。

**证据**：F-007（核心依赖包含四个 harness 包）、F-052（AgentManager 从 `harness_agent` 导入 HarnessAgent/HarnessAgentConfig/HarnessAgentManager/SecurityPolicy）、F-074（Gateway 从 `harness_gateway` 导入 ChannelManager/ChannelKind/ChannelSubject）、F-056（AgentManager.boot 构造 HarnessAgentManager 并将 agents 注册进去）、F-079（Gateway.boot 构造 harness_gateway ChannelManager）、F-068（MCP 工具通过 `harness_agent.mcp.aload_mcp_tools` 加载）。

**反常识**：名为"AI assistant"的 Octop 并不包含模型调用、工具执行、对话图编排等核心 AI 逻辑——这些在 harness-agent（基于 LangGraph）中。Octop 的代码量集中在多用户管理、CRUD、IM 通道注册、配置持久化、setup wizard、TLS/备份等"平台外壳"。这使得 Octop 可以独立于 AI 运行时演进，但也意味着脱离 harness 包 Octop 无法独立运行。

**行动**：文档中只描述 Octop 如何调用 harness 包的公共 API，不虚构其内部实现；调试 AI 行为需查看 harness-agent 源码；升级 harness 包版本时关注 `HarnessAgentConfig` 字段变化（F-080 的 `_HARNESS_AGENT_CONFIG_FIELDS` 反射机制即为此设计）。

## I-04：CLI 延迟加载 + 三层传输——20 个子命令零启动成本

**陈述**：CLI 使用 `_LazyCLI`  click.Group 在调用时才 import 命令模块，且每个子命令根据需求选择 Offline（直读本地 SQLite）、Embedded（进程内启动 OctopServer）或 External（直接 OS 调用）三种传输层之一，避免无谓的服务器启动。

**证据**：F-114（_LazyCLI.get_command 通过 importlib 按需导入）、F-116（20 个命令在 COMMANDS 字典中注册为模块路径元组）、F-120（三层传输定义）、F-117（UTF-8 stdio 强制处理 Windows GBK 兼容）、F-125（`octop acp` 启动独立 OctopServer 而不依赖 `octop run`）。

**反常识**：典型 Click 应用在根 group 加载时导入所有子命令模块，即使执行 `octop version` 也要加载整个依赖树；Octop 的 lazy registry 使 `--help` 和 version 几乎瞬时返回。更关键的是三层传输设计——`octop agent list` 直接读 SQLite 文件，`octop chats send` 在进程内启动完整 OctopServer，`octop models ollama-pull` 直接调用本地 Ollama HTTP——同一 CLI 工具根据操作语义选择最经济的执行路径。

**行动**：新增 CLI 命令时在 registry.py 注册元组而非直接 import；根据命令是否需要运行时选择 transport 层；Offline 命令不得构造 OctopServer；Embedded 命令须确保正确 shutdown。

## I-05：单进程多 Agent + 有界并行热重载

**陈述**：Octop 采用单进程 asyncio 模型承载所有用户和 Agent，AgentManager 在进程内维护所有 HarnessAgent 实例；配置变更（provider/model/tool guard）触发有界并行热重载（并发上限 6），无需重启进程。

**证据**：F-037（_boot_runtime 在单个 asyncio 事件循环中构造所有运行时单例）、F-066（`_PROVIDER_RELOAD_CONCURRENCY = 6`，`on_provider_changed` 使用 asyncio.Semaphore 并行 reload）、F-057/F-060（Agent 启停均在进程内通过 harness_manager 完成）、F-067（三种热重载粒度：单 agent、全部 agent、仅 harness 侧重建）、F-083（Cron 投递在同一进程内通过 agent_manager.stream 执行）。

**反常识**：多用户 AI 平台常采用每用户/每 Agent 独立进程或容器隔离；Octop 选择单进程多租户——所有 Agent 共享同一个 asyncio 事件循环和 HarnessAgentManager。这降低了部署复杂度（无需编排器），但要求 Agent 间通过 harness 的安全策略（SecurityPolicy）和工具审批（guardrails）隔离，而非 OS 级隔离。热重载的有界并行设计避免了 provider 变更时同时重建数十个 Agent 导致的资源尖峰。

**行动**：不在 async 路径中做阻塞 I/O（F-131 禁止 blocking I/O）；理解 `asyncio.Lock` 在 AgentManager 中的保护范围；新增全局配置变更时通过 `on_provider_changed` 模式计算影响集合并有界重载，而非全量重启。

---

# 第二轮洞察：v1.0.2b5（基于 F-134~F-592）

> 2026-10-04 第二轮 I 阶段产出：基于 tag v1.0.2b5（commit e473dd3c）459 条增量事实提炼，承接 I-01~I-05（v0.9.25）。凡新旧轮命名/计数冲突，以本轮为准。

## I-06：品牌独立——harness 四包全面更名 octop-* 与旧名兼容层

**陈述**：1.0.2b3 起运行时依赖从 orcakit/harness 系四包切换为独立品牌的 `octop-harness`/`octop-gateway`/`octop-memory`/`octop-browser` 1.0.0；仓库内对旧包名的依赖声明零残留，但代码侧保留 legacy import 修复与 extras 兼容别名。

**证据**：F-136（四包逐字约束 octop-*>=1.0.0，对 pyproject.toml 与 uv.lock grep 旧名命中数 = 0）、F-141（uv.lock 钉扎 octop-harness 1.0.0 及其 14 个传递依赖）、F-149（1.0.2b3 CHANGELOG 逐字"运行时依赖切换为 octop-harness / octop-gateway / octop-memory / octop-browser 1.0.0"）、F-150（1.0.2b5 修复项含"旧插件 `harness_agent` 导入"）、F-231~F-236（plugins/legacy_imports.py 提供旧模块名导入桥）、F-138（`browser` extras 保留并注释 "Kept for backward compatibility"）。

**反常识**：更名通常是"一刀切"的破坏性发布；Octop 在包依赖层面彻底切换（grep 零残留），却在插件导入面保留 legacy shim 并专发 beta 修复旧插件导入——品牌独立与生态兼容被拆成两个独立时间点处理。这说明插件作者直接 import 内部模块名构成了事实上的公共 API，官方不能假设插件只走声明式清单。

**行动**：二次开发只 import octop-* 新包名；排查遗留集成时 grep `harness_agent|harness_gateway|orcakit` 定位 legacy 路径；评估插件市场上架规则时应禁止裸 import 内部包，改走声明式 plugin.yaml + ctx API。

## I-07：装配序列膨胀至 17 步——热绑定面出现"不可逆服务"

**陈述**：v1.0.2b5 的 `AppRuntime` 从 5 单例扩到 8 字段（新增 trajectory_service、history_archive、bridge_manager），`_boot_runtime` 装配序列扩到 17 步；其中 history_v2 归档库一旦绑定，`replace_services` 直接抛错拒绝热交换，要求重启进程。

**证据**：F-163（AppRuntime 8 字段逐字，docstring "Live singletons — constructed after boot"）、F-168（`_boot_runtime` 磁盘顺序 17 步：browser idle→AgentManager→TrajectoryStore/LiveBus→HistoryArchive 条件替换→Gateway→slash meta→Cron→TLS job→backup job→HITL/team processor→proactive→registry.boot/UserManager→BridgeManager→AppRuntime→resume index jobs→bridge auto-resume）、F-169（history v2 三触发条件 `history_v2_enabled or archive_path.exists() or .required.exists()`，非 sqlite 控制面抛 ValueError）、F-164（`replace_services` 首行检查 `history_archive is not None` 即 raise "Restart the server to rebind a database with versioned history"）、F-170（BridgeManager 在序列尾部装配并消费 public_base_url）、F-171（stop 按依赖逆序关闭，history_archive.store 单独 close）。

**反常识**：I-01 记录的 greenfield 延迟绑定曾让全部服务都可热交换；v1 主动收缩了这一能力——SQLite 归档库连接与长连接桥接隧道成为"不可逆服务"。架构不是单调向更灵活演进：当新子系统的资源句柄无法安全迁移时，显式 fail-fast（抛错要求重启）比维持半失效的热切换更可靠。17 步顺序耦合也意味着单进程组合根正在逼近可维护性上限。

**行动**：新增运行时服务必须同时登记 boot 步骤与 stop 逆序位置；文档须注明开启 history_v2 后变更数据库需重启；二次开发大功能前评估是否应拆出独立进程（bridge 已具备跨进程隧道先例）。

## I-08：连接器即 MCP 工具——25 连接器三模式统一网关

**陈述**：连接器子系统把所有外部 SaaS/CLI 能力统一建模为 MCP 工具：`ConnectorCatalog` 登记 25 个连接器，支持 remote/gateway/internal 三种 McpMode、8 种 AuthKind、7 类 ConnectorCategory；gateway 模式下 13 个进程内适配器把飞书 CLI、腾讯系网页服务等包装为标准 MCP 工具，经内部 HTTP 路径暴露。

**证据**：F-276~F-294（`_CATALOG` 25 项；mcp_mode 分布 gateway 13/internal 1（qcc）/remote 11；AuthKind 8、ConnectorCategory 7；凭证 Fernet 键 `connector_fernet`）、F-295~F-299（oauth/ 实现 OAuth2 PKCE、DCR 动态客户端注册、RFC9728 保护元数据）、F-300~F-305（gateway 注册表、MCP 协议版本字面 `2024-11-05`、内部路径模板 `/api/internal/mcp/{gateway_kind}/{instance_id}`、CLI 指纹/安装目录管理）、F-306~F-315（13 个适配器实测工具面：tencent_ima 14 工具、qq_music 5、yuandian 5、qq_mail 3、weknora 3、baidu_map 3 等）、F-382~F-383（企查查五类 Server/6 精选工具的官方文档口径）。

**反常识**：常见做法为每个 SaaS 写一套独立 HTTP client + 独立配置页；Octop 反其道把"调外部 API"与"MCP 工具调用"收敛为同一件事——连只能通过本机 CLI 访问的服务（飞书 CLI、企微 CLI）都经适配器翻译成 MCP 工具，Agent 侧无需感知凭证/协议差异。代价是连接器目录与适配器注册表成为单点扩张面（25 项/13 适配器均为手工登记）。

**行动**：新增集成先判模式（标准 MCP 服务器→remote；需本机 CLI/网页态→gateway 适配器；内置特殊服务→internal）；凭证一律走 Fernet 加密与 OAuth registry，禁止在适配器内自管 token；适配器工具面必须可经 catalog 枚举，不得隐式注入。

## I-09：零外部依赖 RAG——每库一个 SQLite + 全表内存余弦

**陈述**：知识库不使用向量数据库：每个知识库在 `knowledge_dir/{kb_id}/index.sqlite` 独立存放，chunks 表 6 列，embedding 以 float32 字节串存储，检索时 struct.pack 解包后全表内存算余弦；用一组硬上限约束规模（100 文档/库、20 库/用户、max_documents 10000、top-k 1-20 默认 8、并发 2、嵌入批 20）。

**证据**：F-316~F-328（物理布局、chunks 六列 chunk_id/doc_id/ordinal/text/embedding/meta_json、22 个支持扩展名、chunk 800/overlap 120、三级上限、工具名 `search_knowledge`、引用注入标记字面 `<!--octop-kb-citations:...-->`、UTF-8 失败回退 GB18030、OCR 走可选依赖 `knowledge-ocr`）、F-226 区段（KnowledgeSearchHintMiddleware 装配于 agents 中间件链，位于 `knowledge/hint.py:93`）。

**反常识**：项目已支持 PostgreSQL（README 声明 pgvector 服务 agent memory），知识库却坚持每库独立 SQLite 文件 + 全量内存扫描——在"向量库是 RAG 标配"的共识下选择了零额外服务、零扩展安装、可整库备份/删除（文件即库）的方案。可行性完全建立在硬上限上：100 文档 × 800 字 ≈ 数万 chunk 的内存余弦在单进程内可接受，超过规模即不是目标场景。

**行动**：文档必须明确规模天花板，企业语料需外接 MCP RAG 连接器；调参只在 top-k（≤20）/并发度边界内；新增文档解析器同步登记扩展名与 MIME 映射；引用标记是前端渲染归因的唯一契约，不得改名。

## I-10：团队主持人靠"剥权"隔离——5 工具与 45 秒空闲等待

**陈述**：Teams 把主持人（host）实现为工具面最窄的特殊 agent：kind="team"、模板 "team-host"、成员 ≥2，host 仅允许 5 个协调/只读工具（agent_list/ask_agent/memory_search/memory_get/current_time），空闲等待 `_HOST_IDLE_WAIT_SEC=45.0` 秒后收尾。

**证据**：F-215（`TEAM_MIN_MEMBERS=2`）、F-216（`HOST_TOOLS_ALLOWED` 5 键逐字与 45.0 秒常量）、F-217~F-223（teams/service.py 派工改写、team_manager、jobs.py 异步收尾、welcome.py 迎新消息、成员回复同步 IM）、F-224~F-230（8 个显式中间件 TokenQuota/Reasoning/KnowledgeSearchHint/BrowserProfile/BinaryReadGuard/WorkspaceImage/ThreadArtifacts/OctopUiOffload 的能力注入链）。

**反常识**：直觉上"编排者需要更大权限"（能调度所有成员就应能调用所有工具）；Octop 的 host 反向裁剪到只剩"问人、查记忆、看时间"——主持人无法直接执行任何业务工具，协作产出必须经成员 agent 完成。隔离不靠沙箱而靠工具清单剥夺：host 被攻陷或 prompt injection 后的爆炸半径天然被 5 个只读/协调工具封死。

**行动**：自定义团队模板不得为 host 增加执行类工具；跨 agent 通信只走 ask_agent/memory_*；团队类问题排查先查 45 秒收尾 job 与主持人改写日志。

## I-11：跨 Octop 联邦——影子 ID + 28 子路径白名单 + SSRF 黑名单的受限隧道

**陈述**：1.0.2b5 新增的 Octop↔Octop 桥接不提供通用代理：经 ASGI 内部隧道（基址 `http://bridge.local`、120s）+ Fernet 对等鉴权（键 `bridge_fernet`）+ 协议版本握手，远端能力按 `_AGENT_RESOURCE` 白名单逐项开放，本地侧以影子 ID 键映射隔离远端 agent/会话标识。

**证据**：F-384（自动重连 5 次、退避序列 (2,4,8,16,30) 秒）、F-385~F-389（WS 帧超时 open 20s/hello ack 20s/入站 hello 30s/turn 600s、关闭码 4000×2、4002 协议不符、4003）、F-395/F-396（ids.py 中 `_TUNNEL_AGENT_ID_KEYS` 6 键+2 列表键、`_TUNNEL_URL_KEYS` 6 键的影子映射）、F-397（tunnel_policy.py 白名单实测 28 子路径 9+9+10；SSRF 黑名单覆盖 169.254/fe80/::ffff:169.254 link-local 网段）、F-401（Fernet 键 `bridge_fernet` 字面值与各超时）、F-170（BridgeManager 在 _boot_runtime 尾部装配）。

**反常识**："连另一台 Octop 用专家"最直白的实现是 HTTP 反向代理或 VPN；本方案在服务内部起 ASGI 隧道、对每个 URL 子路径白名单校验、对每个 ID 做影子重写——默认拒绝一切，仅放行枚举的 28 个 agent 资源。link-local 黑名单显示对云元数据端点 SSRF 的显式防御。联邦的信任模型是"单资源授权"而非"主机互信"。

**行动**：桥接排障按关闭码分流（4000 握手缺字段/4002 版本/4003 拒绝）；新增需要跨联的 agent 资源必须同步登记白名单与影子 ID 键；部署文档须强调 advertise base URL 的正确推导（public_base_url_from_config）。

## I-12：history v2 内容寻址归档——6 表 3 索引、digest 去重与 50 轮热窗

**陈述**：版本化历史用独立 SQLite 库分层存储：archive_meta/segments/turns/bodies/documents/body_refs 6 表 3 索引，正文入 bodies 按内容寻址（body keys 7 个、digest 字段），turns 经 body_refs 引用正文，TrajectoryKind 枚举 7 种轨迹；热会话仅保留 `TRAJECTORY_RETENTION_USER_TURNS=50` 轮。

**证据**：F-169（独立 history_v2.sqlite 与三触发条件）、F-164（绑定后拒绝热重绑）、F-425（TrajectoryKind 7 值逐字）、F-426（TrajectoryEvent 11 字段）、F-429（6 表 3 索引实测、文本块 1024）、F-430（body keys 7 与 digest/body_refs 机制）、F-438/F-439（忽略事件类型 10 个、TrajectoryMetrics 10 字段）、F-425~440 区段（projector 投影、live 总线、metrics 聚合、reader/legacy 兼容读取）。

**反常识**：归档系统常见做法是给主库表加 archived 标志或整库 dump；v2 把"正文"与"事件结构"拆表并对正文做内容寻址去重（同内容多轮次只存一份），再以 50 轮热窗把冷数据驱逐出 agent memory——这是对象存储式设计思路下沉到 SQLite 本地文件。代价是归档库成为 I-07 所述的不可逆服务，且只支持 SQLite 控制面。

**行动**：历史取证读 projector/reader 视图而非直接 join 表；容量评估按 bodies 去重后体量；备份/恢复流程必须包含独立 history_v2.sqlite 文件（已纳入备份六内容）。

## I-13：插件扩展"开放三 API、官方只用一 API"的治理取舍

**陈述**：插件 ctx 暴露 tool/skills/middleware 三类注册 API，但内置 26 个 bundled 插件全部 kind=tool，全目录仅见 ctx.tool 调用（26 文件 33 处），ctx.skills/ctx.middleware 零调用；根目录 demo 插件才演示其余两类 API 与 UI 信封。

**证据**：F-237（bundled 26 目录/26 plugin.yaml，kind=tool 26/26）、F-238（group 分布 tools 8/lifestyle 5/fun 4/news 3/games 2/media 2/finance 1/ops 1）、F-239（每目录四件套 main.py/icon.svg/ui/index.js；ctx.tool 命中 26 文件 33 处，另两类 0）、F-241/F-242（根 plugins/ 6 目录：4 demo + 2 个仅 README 的已分发占位）、F-231~F-236（PluginManager 装载、seed、默认开关、legacy_imports 兼容）、F-471~F-479（技能包体系独立于插件：2000 文件/64MiB 上限、zip 比率校验 100、SkillHub host `https://api.skillhub.cn`）。

**反常识**：平台型产品通常在官方功能中率先使用全部扩展点以证明其可靠；Octop 官方插件刻意只使用 tool 面，把 middleware（可拦截全部消息）与 skills（可下发可执行脚本包）留给显式安装的第三方扩展。高权限扩展点"可用但不示范"，配合技能包的文件数/体积/压缩比三重硬上限，构成分层防御。

**行动**：新插件默认按 kind=tool 实现；middleware 类插件须在安全评审中确认拦截面；技能包分发走 SkillHub 通道并遵守 2000/64MiB/比率 100 限制；UI 一律走 octop_ui 信封与 `/api/plugins/{id}/ui/`。

## I-14：登录前策略面收敛——SSO 4 提供商 × 验证码 7 提供商 × 26 条权限

**陈述**：多租户安全由三个可插拔子系统拼成：SSO 支持 oidc/feishu/dingtalk/wecom 4 provider（state 600s/码 60s、独立 `sso_fernet`、ID Token 算法白名单仅 RS256/ES256）；验证码 7 provider（slider 本地 + 6 云服务含 geetest-v4）；授权端 26 条权限分 settings 4/control 4/admin 18 三组，邀请码 11 字符、有效期 1-90 天默认 7、限流 20 次/60 秒，密码 Argon2id 最短 8 位。

**证据**：F-442/F-443（permissions.py:50-216 实测 26 条=4+4+18）、F-449（弱口令表 14 个、用户名上限 64、Argon2id）、F-451（邀请码 11 字符、MIN=1/默认 7/上限 90 天）、F-445~448（限流 20/60s、侧边导航 19 键、审计动作 11 个）、F-480~489（SSO 四 provider、600s/60s TTL、sso_fernet、PKCE、discovery、redirect_after）、F-482/F-486（ID Token 仅收 RS256/ES256 不对称算法）、F-490~496（captcha 7 provider、geetest 别名 3、CaptchaEnv 6 字段、v3 分阈值 0.5、`octop captcha reset` CLI）。

**反常识**：SSO（企业登录）与验证码（防机器人登录）常被视为互斥场景——"都 SSO 了还要什么滑块"；Octop 把二者同置于登录前策略面并可叠加（CHANGELOG 1.0.1 同期引入），且对 OIDC ID Token 显式拒绝 HS 对称算法与 alg=none，防止 discovery 文档投毒。权限侧用 26 条细粒度权限替代"管理员布尔位"，连侧边栏可见性都由 19 个导航键的策略驱动。

**行动**：接入企业 IdP 走 providers/base.py 子类，不在路由内自写 OAuth；安全审计依次核对算法白名单、state TTL、邀请限流、权限三组归属；新管理功能必须注册权限条目而非复用 admin 角色。

## I-15：异构数据面的统一容灾——tar.gz 清单、pg_dump -Fc 与 SQLite online backup 同 job 调度

**陈述**：自动备份（job id `octop_auto_backup`、cron `0 4 * * *`、保留 7 份）在同一调度内处理三种不一致数据面：六内容目录（config/db/workspaces/skill-packages/plugins/knowledge）打 tar.gz（13 个跳过目录名）、PostgreSQL 走 pg_dump -Fc、SQLite 走 online backup API，工作区 zip 支持 merge/replace 双恢复模式，全程以 manifest 描述；存储后端另立 10 kind 体系（5 个对象存储 + filesystem/shell/postgres/docker/opensandbox）。

**证据**：F-402~414（system_archive 六内容目录与 _SKIP_DIR_NAMES 13、workspace_archive 跳过 4 目录与 merge/replace、pg_dump.py、snapshot.py SQLite online backup、manifest.py、chats.py、auto.py 调度与 retention_count 默认 7）、F-415（backend 对象 kind 5、可解析 kind 10）、F-416~424（沙箱前缀 `octop_sandbox`、docker 透传键实测 18、scope agent/user/fixed、opensandbox 可选依赖、probe 探测）。

**反常识**：备份系统一般按数据库类型分叉成两套互不相干的工具链；Octop 用一个归档清单把文件集、逻辑转储、热库快照缝合为单一可恢复单元，并把"备份存到哪"（10 kind 后端适配）与"备份怎么产"（三路采集器）正交拆解。5 vs 10 的双 kind 计数揭示另一层取舍：配置里可写的后端种类多于当前二进制实际内置探针支持的种类。

**行动**：恢复演练以 manifest 为入口核对六内容齐备；PG 部署验证 pg_dump 版本匹配；新存储后端在 resolver/adapter 双注册点登记并区分"可解析"与"可内置探测"；Docker 沙箱能力变更须同步 18 个透传键清单。

---

# 增量知识地图（v1.0.2b5 轮，E 阶段执行依据）

> 既有 concepts/00-06、examples/3、references/6 保持不动；本轮新增文档与 F 事实覆盖映射如下。子目录 index 与根 index 在全部正文生成后最后更新。

## 新增 references（信源先行，4 篇）

| 文档 | 覆盖事实 |
|---|---|
| references/source-v1-map.md | F-134~F-171（版本/构建/配置/装配）、全仓模块地图、20 个 infra 子域索引、dashboard/desktop/docker 布局（F-566~F-592） |
| references/connectors-catalog.md | F-276~F-315、F-382~F-383（25 连接器×3 模式×8 AuthKind 总目，13 适配器工具面） |
| references/api-surface.md | F-503~F-555（60 挂载/472+9 端点/40 tag 全表、JWT 豁免、chat SSE/WS 事件面） |
| references/bridge-protocol.md | F-384~F-401（协议常量表、关闭码、超时表、28 白名单、影子 ID 键、SSRF 黑名单） |

## 新增 concepts（15 篇，编号 07-21）

| 文档 | 覆盖事实 |
|---|---|
| concepts/07-connector-system.md | F-276~F-315、F-382~F-383 |
| concepts/08-knowledge-rag.md | F-316~F-328（含 hint 中间件 F-226 区段交叉引用） |
| concepts/09-gateway-advanced.md | F-329~F-381（slash/process/media/hitl/ws/channels/bot_creators/voice/cron） |
| concepts/10-agent-teams.md | F-215~F-230 |
| concepts/11-agent-marketplace.md | F-243~F-253、F-272~F-275（experts 18 manifest、子代理库 zh272/en217、MBTI 16、内置技能、docs 声明） |
| concepts/12-agent-runtime-internals.md | F-206~F-214、F-254~F-271（Manager 常量/会话模式/reasoning×8/ONNX×3/工具目录 42/HITL 策略/memory slim/workspace 与 threads） |
| concepts/13-plugin-system.md | F-231~F-242、F-471~F-479（插件 + 技能包双扩展体系） |
| concepts/14-bridge-federation.md | F-384~F-401 |
| concepts/15-backup-and-storage.md | F-402~F-424 |
| concepts/16-history-trajectory.md | F-164、F-169、F-425~F-440 |
| concepts/17-users-auth-security.md | F-441~F-454、F-480~F-496 |
| concepts/18-mobile-desktop-proactive.md | F-455~F-470、F-497~F-502 |
| concepts/19-dashboard-frontend.md | F-566~F-575 |
| concepts/20-api-cli-surface.md | F-556~F-565、F-503~F-522（CLI 22 命令/REPL/support；与 19 篇共用 API 装配事实） |
| concepts/21-packaging-deployment.md | F-576~F-592（Go/Wails、便携 runtime、Docker 三件套、FnOS） |

## 新增 examples（5 篇，kebab 命名沿用旧例）

| 文档 | 覆盖事实 |
|---|---|
| examples/plugin-development.md | F-231~F-242（以 demo-toolkit/demo-ui-card 为样板） |
| examples/knowledge-base-use.md | F-316~F-328（建库/上传/检索/引用标记端到端） |
| examples/bridge-remote-expert.md | F-384~F-401（配置云端桥接使用远程专家） |
| examples/expert-team-setup.md | F-215~F-223（组队/host 派工/IM 同步） |
| examples/docker-compose-deploy.md | F-586~F-590（含 postgres/mobile 两套 compose） |
