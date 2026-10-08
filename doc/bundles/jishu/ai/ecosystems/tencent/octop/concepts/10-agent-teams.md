---
type: Concept
title: "专家团队：主持人剥权隔离与派工"
description: "team agent 的规格与 team-host 模板、主持人 5 工具白名单与 45 秒空闲收尾、TeamService/TeamManager 的派工改写与成员回复 IM 同步、8 环中间件链，以及编排者最小权限的安全含义。"
tags: [octop, teams, multi-agent, host, middleware, least-privilege]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: "Octop 源码事实清单 F-215~F-230"
---

# 专家团队：主持人剥权隔离与派工

专家团队（team）是 Octop 多 Agent 协作的原生形态：一个**被剥掉几乎所有工具的主持人（host）**负责听取需求、向若干普通专家成员派工、汇总发言；成员各自保留完整工作区与能力，可以单独被用户聊天，也可以加入多个团队（F-273）。本章讲这套"主持人隔离 + 派工"机制在源码里如何落地。

## team 是一种 agent kind

创建 Agent 的输入是 22 字段的 `AgentCreateSpec`（src/octop/infra/agents/manager.py:285-309）：

```python
@dataclass
class AgentCreateSpec:
    name: str
    agent_id: str | None = None
    user_id: int | None = None
    description: str | None = None
    persona_mbti: str | None = None
    default_model: str | None = None
    system_prompt: str | None = None
    icon: str | None = None
    template_name: str | None = None
    is_shared: bool = False
    icon_name: str | None = None
    icon_url: str | None = None
    color: str | None = None
    skill_package_ids: list[str] | None = None
    published_expert_id: str | None = None
    welcome_message: str | None = None
    knowledge_base_ids: list[str] | None = None
    mcp_servers: list[str] | None = None
    runtime_config: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    kind: str = "expert"                       # 仅 "expert" / "team" 合法
    member_ids: list[str] = field(default_factory=list)
```

kind 经 `spec.kind if spec.kind in {"expert","team"} else "expert"` 归一（F-210）。team 分支有四条特殊处理（F-210、F-215）：

1. team **不允许共享**：is_shared 为真抛 `TEAM_NOT_SHAREABLE`，消息逐字 "teams cannot be shared"；
2. team 不挂任何 MCP：`mcp_servers_json = dump_id_list([])`；
3. 创建后 await `seed_team_template(...)`，把 `teams/template/manifest.json` 写进主持人工作区；
4. 审计动作为 `"agent.create"`。

团队侧常量集中在 teams/service.py:16-22（F-215）：

```python
TEAM_KIND = "team"
EXPERT_KIND = "expert"
TEAM_TEMPLATE_NAME = "team-host"
TEAM_MIN_MEMBERS = 2
TEAM_AVATAR_URL = "/experts/avatars/team-host.svg"
TEAM_MANIFEST_WORKSPACE = ".octop/manifest.json"
```

模板 manifest 实测 9 行，固定 `{"kind": "team", "members": [], "welcome_message": {zh/en}, "quick_prompts": []}` 结构（F-218）。成员校验两道闸：成员不可用抛 `TEAM_MEMBER_INVALID`；去重后可用成员少于 2 抛 `TEAM_MEMBERS_TOO_FEW`，details 带 `{"min_members": 2}`（F-217）。注意文档口径"至少 2 个成员（不含主持人）"（F-273）——编制写在主持人工作区的 `.octop/manifest.json`（kind + members），数据库 `agents.kind="team"` 只作列表索引（F-273）。

## 主持人剥权：5 工具白名单

团队安全模型的核心是一行注释——"Hosts only dispatch and keep light memory/time — members do the work."（teams/service.py:24）。白名单逐字为（F-216）：

```python
HOST_TOOLS_ALLOWED = frozenset({
    "agent_list",      # 只看得见成员清单
    "ask_agent",       # 派工（运行时置为异步模式）
    "memory_search",   # 轻量记忆
    "memory_get",
    "current_time",    # 时间
})
# HOST_TOOLS_DISABLED = BUILTIN_TOOL_CATALOG 中不在白名单内的全部工具
```

`_apply_team_host_config` 在装配 harness 配置时对 team 行一次性剥权（F-222）：`tools_disabled=host_tools_disabled(...)`、`team_peers=tuple(member_ids)`、`peer_invoke_mode="async"`、`mcp_server_configs={}`、`skills_dir=None`、`tools=None`、`subagents_auto_load=False`、`bootstrap_enabled=False`，并换上 `host_system_prompt`（F-220、F-222）。非 team 行则把 peer_invoke_mode 置回 "sync"（F-222）。这意味着主持人没有文件系统、浏览器、搜索、MCP、技能、插件——它无法自己"干活"，只能派工。文档决策表同样声明了这一边界（F-273）。

派工是异步的：`stamp_host_runtime` 写 `configurable["peer_invoke_mode"] = "async"`（F-221）。主持人等待成员收尾有轮询常量（F-219）：

```python
_HOST_IDLE_POLL_SEC = 0.05
_HOST_IDLE_WAIT_SEC = 45.0      # 最长等待 45 秒空闲即收尾本轮
```

## TeamService 与 TeamManager：派工改写与房间同步

`TeamService` 负责编制（roster）规则：写/读工作区 manifest、校验成员、seed 模板（F-217、F-218）。运行期的派工与消息扇出由 `TeamManager` 承担，其关键方法勾勒出一条完整链路：

```
用户在房间(room)发消息
  → install_host_dispatch：主持人接管，异步 ask_agent 派工      (F-221,F-222)
  → _assignment_text / _dispatch_message：派工词改写           (team_manager.py:651,665)
  → prepare_peer_session / record_peer_turn：成员独立会话转    (F-221)
  → on_reply：成员完成事件回灌                                 (:279)
  → fan_in_peer_turn / stream_peer_to_room：回流房间投影        (F-221,:319,:455)
  → _push_room_to_channels / _notify_channel_dispatched：IM 同步(:931,:971)
  → _wait_host_dispatch_idle：45s 空闲轮询收尾                  (F-219,:390)
```

几个值得注意的工程细节：

- **结果裁剪**：注入主持人历史的工具结果上限 `_HISTORY_TOOL_RESULT_MAX_CHARS = 4000`，追问结果上限 `_FOLLOWUP_RESULT_MAX_CHARS = 6000`，房间历史最多取 `_ROOM_HISTORY_LIMIT = 40` 条（F-219）。
- **编辑类工具的房间镜像**：write_file/edit_file/send_file/send_file_to_user 4 个基名组成 `_EDIT_CARD_TOOL_BASES`，成员产出的文件卡片要回投房间（F-220）。
- **消息身份**：房间 assistant 消息 id 带前缀 `f"team-peer:{ulid}:assistant"`、`f"team-room:{ulid}:assistant"`，human 侧为 `f"team-peer:{thread_id}:{suffix}:human"`（F-221）；模块级别名 `take_team_peer_prompt = take_peer_prompt`、`stream_team_peer_to_room = stream_peer_to_room`（F-221）。
- **IM 同步**：成员回复不只写数据库，还通过 `_push_session_channel`、`_push_room_to_channels`、`_publish_room_text` 推回成员所在会话与团队房间，外部 IM 用户能实时看到分工进展（team_manager.py:921-995）。
- **派工忙碌追踪**：`TeamJobTracker` 持线程锁，键为 (team, member) 二元组，提供 begin/end/is_busy/is_member_busy/busy_member_ids（F-223）。
- **欢迎语**：`team_host_welcome_payload` 从模板 manifest 的双语 welcome_message 生成团队开场白（`_TEAM_INTRO`，zh/en）（F-223）。
- **接线点**：`wire_host_dispatch`（team_manager.py:1577）由 `AgentManager._install_team_host_dispatch`（manager.py:3292）安装进 harness（F-222）。

## 8 环中间件链

team（以及普通 expert）每个 Agent 的中间件链在 `_build_harness_config` 中固定按序装配 8 个具名项，插件链 `PluginRegistry().build_middleware_chain(...)` 在前（F-211）：

| # | 中间件 | 作用 |
|---|--------|------|
| 1 | TokenQuotaMiddleware | before_agent 调 assert_token_quota_available 做 token 配额闸（F-225） |
| 2 | ReasoningRequestMiddleware | 读 configurable `octop_reasoning_overrides`，在模型调用钩子里覆盖 model_fields/extra_body（F-226） |
| 3 | KnowledgeSearchHintMiddleware | 按本轮知识库目录增删/改写 search_knowledge 工具描述，定义于 knowledge/hint.py:93（F-230） |
| 4 | BrowserProfileMiddleware | browser_use 调用前按 user_id 注入隔离浏览器画像；无用户则以 ToolMessage error 阻断（F-227） |
| 5 | BinaryReadGuardMiddleware | 只挂 awrap_tool_call；read_file 拒绝 14 种二进制扩展名（pdf/docx/xlsx/zip/图片等）（F-228） |
| 6 | WorkspaceImageMaterializeMiddleware | provider 调用前把 `workspace://` 视觉引用内联物化（F-229） |
| 7 | ThreadArtifactsMiddleware | 登记线程产物；peer 线程 `room~member` 也镜像到房间（F-229） |
| 8 | OctopUiOffloadMiddleware | 大段 octop_ui 数据（≥4000 字符）移到 ToolMessage.artifact，防 file:// 泄漏（F-230） |

7 个 agents/middleware 下的类与 knowledge/hint.py 的第 3 环，全部继承 `langchain.agents.middleware.AgentMiddleware[Any, Any]`（F-224、F-230）。团队主持人因 `tools=None` 且不引导导 bootstrap（构造实参 `bootstrap_enabled=not team_host`，F-211），这些中间件对它几乎只剩记忆/配额层面的意义。

## 安全含义：编排者最小权限

把这套机制反过来读，就是一条清晰的最小权限设计：

1. **主持人是高暴露面**——它直接面对群聊/IM 等不可信输入，但它手里只有派工和记忆，即使被提示注入也无法读写文件、发请求或触达 MCP（F-216、F-222、F-273）。
2. **成员是能力持有者**——每个成员用自己的工作区独立执行，主持人只能拿到经裁剪（4000/6000 字符）的文本结果（F-219）。
3. **team 不可共享、不可挂 MCP/技能**——编制变更收敛到工作区 manifest 与成员校验（F-210、F-217、F-273）。
4. **配额与二进制读防护在中间件层统一兜底**，不因团队编排而绕过（F-225、F-228）。

## 相关概念

- [/concepts/11-agent-marketplace.md](11-agent-marketplace.md) —— 成员从专家市场/内置专家库而来
- [/concepts/08-knowledge-rag.md](08-knowledge-rag.md) —— 中间件第 3 环的知识库提示机制
- [/concepts/02-agent-runtime.md](02-agent-runtime.md) —— harness 配置与 peer 调用运行时
