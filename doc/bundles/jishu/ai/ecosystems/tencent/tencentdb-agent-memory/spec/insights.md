---
type: spec-insights
title: TencentDB Agent Memory 核心洞察
status: stable
generated: { by: reference_agent/trae-solo, at: 2026-10-04T00:00:00Z }
---

# TencentDB Agent Memory Insights

> 6 条核心洞察，每条遵循四元组结构（陈述 / 证据 / 反常识 / 行动），证据均回引 [facts.md](facts.md) 编号事实。全部洞察基于仓库固定截面（commit 8b86874，2026-10-04 采集）。

## 洞察一：以「协议不变」替代插件生态——Proxy 是接入层的反向选择

**陈述**：让一个 coding agent 获得记忆能力，业界主流路径是为每个 Agent 写插件/Hook/MCP connector；TencentDB Agent Memory 选择了相反的接入形态：MemoryProxy 同时讲 OpenAI 与 Anthropic 两套协议（F-219），Agent 只需把 base URL 指向 proxy（Claude Code 为 `http://127.0.0.1:8096/claude-code/default`，F-029），官方表述为「不需要插件、Hook 或 MCP」（F-026、F-245）。差异成本被收敛到 proxy 一侧：agent-adapters 工厂注册 8 个适配器（F-220），会话表单/分页/清洗按客户端分目录适配（F-231），而 Agent 侧零安装。

**证据**：F-026（README 零代码接入原文）、F-219/F-220（双协议 + 8 适配器）、F-223（鉴权与记忆读写全部由 proxy 回源 Core）、F-232（sessionInit 首轮引导完成 team/agent/task 绑定）、F-270（PROXY_FULL_STACK=1 同时拉起 auth/sessionInit/注入三段）、F-027/F-028（客户端支持数随版本从 7 扩到 8，新增 OpenCode 等四款仅靠 proxy 侧升级获得，F-013）。

**反常识**：「中间代理」通常被视为透明管道，而这个 proxy 是一个重业务系统——它做首轮问答引导、逐轮系统提示词注入（8 个注入器与 6 个边界标记，F-024/F-025）、会话内 `mem:` 指令解析（6 个命令，F-234）、频控、计费上报与 trace 归档（F-229/F-240）。也就是说，它不替代插件生态，而是把「每个 Agent 各写一遍插件」的 N×M 适配矩阵，改写成「N 个 Agent 协议适配器 × 1 套记忆业务内核」——重逻辑从客户端搬到了网络路径上的必经节点。代价是所有对话流量（含流式 SSE）都经过 proxy（F-219），这是企业可接受、个人用户需知情的信任边界。

**行动**：① 评估接入时优先用 proxy 路径（零改造），但部署文档必须向用户明示流量中转与系统用户透传机制（F-228/F-243）；② 二开新 Agent 支持时只需在 agent-adapters/ 与 session/<client>/ 各加一个适配器，勿改 Core；③ 安全敏感场景可用 `/direct/*` 旁路与 Bearer 网关（F-156/F-221）做分层豁免；④ 设计同类系统时，「协议复用 + 侧车承载业务」可作为避免 M×N 插件碎片的参考架构。

## 洞察二：两条管线刻意分离——「记忆沉淀」（L0→L3）与「上下文压缩」（offload L1.5/L2/L3/L4）共用编号、不共路径

**陈述**：仓库里存在两套都叫 L2/L3 的机制，极易误读为一套。其一是记忆核心的沉淀管线：L0 JSONL 原始对话（F-038）→ L1 原子记忆抽取/去重/双写（F-061~F-065）→ L2 scene_blocks/*.md 场景（F-040、F-081~F-083）→ L3 Persona（F-085），产物是**跨会话持久资产**。其二是 offload 插件内的上下文工程管线：L1 批量上报（5 条/批、3 次重试，F-175）、L1.5 任务边界判定（F-176）、L2 每 30 条/5 秒轮询产出 MMD 任务节点（F-177/F-178）、L3 token 溢出三级压缩（F-180）、L4 create-skill 斜杠命令（F-179），产物服务于**当前会话的上下文预算管理**，其中 Skill 成果才回写沉淀管线。

**证据**：F-037~F-040（README 的四层资产模型）、F-061~F-065 与 F-081~F-087（沉淀侧默认参数与作用域）、F-173~F-184（offload 侧独立的批大小/轮询/超时/压缩级联）、F-185（offload 甚至有独立 offload_server 与 context-engine client）、F-073（Core 侧 timer-member 也分别映射 L1/L2/L3/flush，证明同名层级在两侧各自实现）。

**反常识**：直觉上「记忆系统」应当只有一条从对话到长期记忆的提取链；本仓库把**记得住**（沉淀，异步、可降级、追求召回）与**装得下**（压缩，同步、有 token 阈值、追求少拿但拿对 F-019）拆成两个工程问题。二者连编号语义都不共享：沉淀侧 L3 是 Persona，offload 侧 L3 是 emergencyCompress 压缩函数。这种同名不同义不是混乱，而是对 Agent 运行时两类失败模式（跨会话失忆 vs 当前会话爆上下文）的分别建模。理解这一点是读通全仓目录结构的前提——MemoryCore/src/core 与 MemoryCore/src/offload 是两个世界。

**行动**：① 运维排障时先判断症状属于哪条管线（记忆缺失查 l1-*/scene/persona，上下文超限查 llm-input-l3 与 l15Judge），勿跨层找原因；② 调参时注意两侧阈值独立（maxMemoriesPerSession=10 与 L1_BATCH_SIZE=5 无联动）；③ 教程将二者分篇（本知识包 02/03 篇与 11 篇），避免读者把 MMD 节点误当场景文件；④ 自研记忆系统可复用「沉淀/压缩双轨 + 仅在 Skill 产物处汇合」的切分。

## 洞察三：降级优先（fail-open）的检索与写入美学——无 embedding、无 LLM、无 BM25 服务都能继续运转

**陈述**：系统在多个关键路径上选择「能力降级但不中断」：L1 写入 JSONL 为主存、向量为副写，嵌入失败只丢向量元数据、向量失败不阻塞 JSONL（F-065）；去重 LLM 超时/失败降级为全量 store，召回能力缺失同样全存（F-063/F-064）；TCVDB 无 embedding 配置时建 dim=1 占位索引、用 sparse vector 承载 BM25（F-110）；BM25 sidecar 不可达返回空向量并标不健康而非请求失败（F-116）；BM25 用 TS 实现（tcvdb-text）替掉 Python sidecar（F-115）；召回 hook 超时返回 error 结果且不向上抛错（F-068）。

**证据**：F-063/F-064/F-065（L1 三处降级）、F-110/F-115/F-116（检索面三处降级）、F-068（hook 层不抛错）、F-175（offload L1 重试耗尽写 `[L1 degraded]` 占位条目而非丢数据）、F-176（L1.5 判定失败 fail-safe 推 short boundary）。

**反常识**：检索系统的教科书做法是把召回质量当作硬正确性——抽不出好 embedding 就不应写入；本系统反过来：**记下来优先于记得好**。这是「记忆」与「搜索」两类产品的目标差异：搜索结果差是质量问题，记忆漏记是数据永久丢失（L0/L1 原文一旦未落盘不可重建）。与之配套，检索侧用 RRF 做后融合（RRF_K=60，F-114）而非学习排序——简单融合天然允许单路缺席。需要注意 fail-open 的代价是降级期数据质量偏差只能事后补偿，运维必须消费「不健康」标记而不能只看请求成功率。

**行动**：① 部署最小化形态时可先不配 embedding/BM25 sidecar 跑通全链路，再逐步加能力；② 监控不能只看 HTTP 200，需把 bm25-client 健康位、`[L1 degraded]` 条目占比、RecallResult.error 率纳入看板；③ 自研写入路径可复用「主存不可降级（JSONL）、派生索引全部可重建」的原则；④ 容量规划时预期降级期全量存储带来的数据膨胀（skip/merge 去重失效）。

## 洞察四：自定义 Prompt 与固定输出协议分离——策略可编辑，契约不可改，且正文不留痕

**陈述**：多租户记忆系统面临「每个团队想要自己的记忆抽取风格」与「系统必须能机器解析产物」的矛盾。memory-prompt 的解法是分层：解析优先级 agent → team → instance → 内置（F-088），每 instance 最多 500 条、单条 ≤10000 Unicode 字符（F-089），自定义内容经 composer 注入 `<CUSTOM_MEMORY_STRATEGY>` 并配 `<SYSTEM_CUSTOM_STRATEGY_GUARD>` 守卫（F-090）；而 L1=JSON、L2=Scene Markdown、L3=Persona+Doctrine 的输出协议被钉死、不可通过 prompt 修改（F-091）。审计侧只记 Prompt ID/版本/来源/SHA-256，不存正文（F-092）。

**证据**：F-088~F-093（解析、限额、守卫、协议、审计、API 全套）、F-159（memory-prompt 与 generation-log 独立 API 面）、F-048（Loadout 与 prompt 一样是 per-agent 装配维度）、F-146（service 模式 per-instance SkillCore 解析，与 per-instance prompt 同一多租户模式）。

**反常识**：「让用户自定义 prompt」在多数产品里等于把输出格式也交出去，随后解析器被各种自由文本击穿；这里把 prompt 拆成**可变策略文本**与**不可变协议骨架**两半，用户能改的是「怎么判断/怎么措辞」，不能改的是「以什么结构交卷」。更反直觉的是审计不留正文只留 SHA-256——团队 prompt 可能含业务 know-how，把它当机密而非日志，复现靠哈希对拍而非调阅原文。版本递增而 memory_prompt_id 不变（F-089）则保留了「同一策略的演化史」与「策略实体」两个维度。

**行动**：① 二次开发自定义 prompt 时把解析器期望的 JSON/MD schema 视为冻结接口，升级走版本灰度；② 合规审计用 generation-log 的 SHA-256 与现存 prompt 对拍，不要试图从日志还原正文；③ 多 Agent 场景按 agent 级 prompt 做差异化、team 级放共性，避免 500 条上限被单实例耗尽；④ 设计同类「可定制 + 可解析」系统时直接套用「占位符注入 + GUARD 约束 + 协议骨架外置」三件套。

## 洞察五：v3 三元组强隔离与数据面/元数据面拆分——多租户是写进存储格式的，不是查询时补的

**陈述**：v3 契约把 team_id + agent_id + user_id 升为强制三元组（缺失即 422），允许来自 body 或三组 x-tdai-* 请求头（F-153）；隔离不是查询层的 WHERE 拼装，而是贯穿三层：SQLite 的 l0/l1/FTS/vec 表全部直接包含 team_id/user_id/agent_id/session_key/session_id/task_id 隔离列（F-066/F-111/F-112），scope 串 `team:...|agent:...` 配 profileRowInScope 行级函数（F-086），Proxy 侧用 user_key 换 user_id 后按用户维度过滤可见资产（F-233）。与此同时元数据面（team/agent/user/key 管理，tdai_metadata_<instance>）与数据面（tdai_memory）物理分库（F-097/F-098）。

**证据**：F-153/F-154（v3 强制三元组 + 18 个受控子路径）、F-111/F-112（隔离字段进入 FTS5 与 vec0 虚表）、F-071（IsolationFilter 六字段）、F-086（行级 scope 校验）、F-046/F-047（private/team/restricted/agent 四值与两级角色）、F-198（Knowledge 侧幂等键也以 service_id+team_id 起头）、F-030（Service/Standalone 两形态共享同一隔离模型）。

**反常识**：多租户常见做法是应用层拼过滤条件，一旦某条查询忘加 tenant 条件即数据越权；本系统把隔离字段做进 FTS 虚表 schema（F-112）意味着连全文检索都无法绕过租户维度——隔离是存储格式的一部分。另一反差点：private 资产对团队管理员不可见（F-046），可见性模型刻意不给管理员上帝视角；而 user_key→user_id 的换发放在 proxy→meta 鉴权链路（F-233），密钥与身份解耦，面板还能用 OAuth2 把企业 OA 身份自动映射到 user_key（F-011/F-262）。元数据/数据面分库则让 K8s 多副本（Service 形态）可以共享元数据控制面而独立扩缩数据面。

**行动**：① 接入 v3 接口先在客户端初始化处固定三元组（TS/Python SDK 顶级导出已强制，F-290/F-293），避免每个调用点手传；② 审计越权风险时直接查 FTS/vec 表定义是否含隔离列，作为「不可绕过隔离」的验收项；③ 企业接入优先走 OAuth2 映射而非手工下发 sk-mem- key；④ 借鉴 scope 串 + 行级纯函数（F-140 同类纯函数风格）做资产可见性测试，四值各建用例。

## 洞察六：Wiki/CodeGraph/Skill 是「随用随取的工具」而非灌进提示词的知识库——只读工具面 + 异步构建状态机

**陈述**：系统对四类资产采取两种注入策略：Chat Memory 的 L2/L3 每轮拼入 system prompt（CHANGELOG 描述），而 Wiki、CodeGraph、Skill 以「工具 + 索引」形态按需调用：MemoryKnowledge 的 MCP 只暴露 12 个只读工具（8 code + 4 wiki），管理操作不进 MCP（F-202）；CodeGraph/Wiki 是 pending→processing→ready/failed 的异步构建状态机，消费端只能在 ready 后查询，busy/not_found 有独立返回（F-199）；Wiki 每个库独立 index.db，BM25 虚表 + wikilink 图谱边 (source,target) 去重（F-204~F-206）；Skill 以不可变多版本快照存储、FTS 仅索引 head、content 超 4000 字不进 FTS（F-131~F-139）。Proxy 侧再用独立的 knowledge-tools / skill-tools 注入器按场景挂载（F-225）。

**证据**：F-202（12 个只读 MCP 工具）、F-197~F-201（状态枚举、幂等键、自动同步 FIFO 调度）、F-204~F-207（索引库结构与 14 段 ingest 流水线）、F-134/F-136（FTS head-only + 4000 字上限）、F-142（抽取前三档预检索 full/relevant/recent）、F-225/F-224（注入器与 `<tdai_memory_tools>` 边界标记）、F-049（仅公开 HTTPS 仓库、异步等 ready 的使用约束）、F-241（dsh 的 compaction/title-gen 短路旁路保证辅助请求不触发资产注入）。

**反常识**：RAG 的惯性思维是「知识库越全越好，全部向量化后每轮召回」；本系统把组织资产分成**每轮必在场的认知**（Persona/场景索引，量小）与**带着触发器的工具**（技能/代码图谱/Wiki，量大），后者通过工具调用协议让模型自取，并配合可见性四值（F-046）与 Loadout（F-048）做 per-agent 裁剪。Skill 表把每个版本设计为不可变快照、name 唯一索引只作用于 head 行（F-133），体现的是「资产可演化、调用可钉版本」的双重诉求；自动同步只扫 ready 且 inFlight 去重（F-200）则防止重建风暴污染工具面。

**行动**：① 接入团队先建 CodeGraph/Wiki 后必须轮询 ready 再让 Agent 使用，脚本勿假设导入即可搜；② 给 Agent 配资产时用 Loadout 显式绑定而非依赖全员可见，配合 restricted 做最小授权；③ Skill 长文（content>4000 字）需自行保证名称/描述含检索关键词，正文不进 FTS；④ 评估 Agent 记忆产品成熟度时，可观察「资产是否区分常驻注入与按需工具、工具面是否只读、构建是否异步状态机」三个特征。

## 知识地图

### 概念文档（13 篇，入门 → 核心管线 → 平台能力 → 部署）

| 文档 | 覆盖事实 | 主题 |
|------|---------|------|
| concepts/00-overview | F-001~F-036 | 产品定位、四件架构、版本口径、部署形态 |
| concepts/01-four-layer-memory | F-037~F-056 | L0-L3 四层模型、四类资产、可见性与角色 |
| concepts/02-l0-l1-pipeline | F-057~F-080 | 抽取/去重/双写/降级、hooks、状态与服务 |
| concepts/03-l2-scene-l3-persona | F-081~F-093 | 场景文件、Persona 触发、自定义 Prompt |
| concepts/04-storage-retrieval | F-094~F-130 | 三后端、RRF/BM25、SQLite schema、配额（含洞察三） |
| concepts/05-skill-memory | F-131~F-150 | Skill 版本化存储、17 端点、提取与权限 |
| concepts/06-gateway-isolation | F-151~F-172 | v2/v3 API、信封、三元组隔离、鉴权 |
| concepts/07-offload-context | F-173~F-190 | 双管线辨析、L1.5/L2 MMD/L3 压缩/L4 |
| concepts/08-memory-knowledge | F-191~F-216 | Wiki/CodeGraph、12 MCP 工具、状态机、llm-binding |
| concepts/09-memory-proxy | F-217~F-246 | 双协议、8 适配器、注入器、mem 指令 |
| concepts/10-panel-acl | F-247~F-262 | Hub 面板、16 action、Loadout、OAuth2 |
| concepts/11-deploy-topology | F-263~F-286 | start-all、端口卷、两组 LLM、健康检查 |
| concepts/12-sdk-engineering | F-287~F-300 | TS/Python SDK、CI、工程脚本 |

### 实战示例（4 篇）

| 示例 | 对应事实 | 场景 |
|------|---------|------|
| examples/01-quickstart | F-035、F-263~F-279 | start-all.sh 一键拉起三件套并验证 |
| examples/02-claude-code-proxy | F-029、F-219~F-233 | Claude Code 经 proxy 零插件接入 |
| examples/03-custom-memory-prompt | F-088~F-093 | 用 v3 API 创建/校验自定义 Prompt |
| examples/04-wiki-codegraph-ingest | F-197~F-209 | 导入仓库/文档、轮询 ready、MCP 工具调用 |

### 信源登记（5 份 references）

| 文件 | 内容 |
|------|------|
| references/01-source-code-map.md | commit/tag/目录地图/组件清单/计数复核记录 |
| references/02-readme-changelog.md | README_CN、CHANGELOG 五版本、ROADMAP、口径差异 |
| references/03-api-references.md | 三个 v3-api 文档与 openapi.yaml 摘要 |
| references/04-deploy-install.md | INSTALL_CN 八客户端、deploy 脚本与 env 清单 |
| references/05-sdk-ci.md | TS/Python SDK 结构、CI 与工程脚本 |
