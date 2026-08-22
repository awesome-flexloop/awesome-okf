---
type: Example
title: 使用 Space 策略
description: 通过 Second-Me 的 Space 多Agent讨论功能，使用策略模式（Strategy Pattern）配置不同角色的讨论行为，实现AI之间的多方对话与协作。
tags: [second-me, example, space, strategy, multi-agent, discussion, collaboration]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: Second-Me 源码事实清单
---

## 场景说明

Second-Me 的 Space 功能允许多个 Second-Me 实例（或其他兼容 OpenAI API 格式的AI服务）之间进行多方讨论。你需要：
1. 创建一个 Space 讨论空间
2. 理解三种内置策略（主持开场、主持总结、参与者发言）
3. 配置讨论参与者
4. 启动并监控讨论流程
5. 获取讨论结论

Space 使用**策略模式**（Strategy Pattern）和**装饰器模式**来构建不同角色的系统提示词。

## Space 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    Space Service                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │           DiscussionService (编排器)               │  │
│  │  max_rounds=3: ①开场 → ②多轮讨论 → ③总结          │  │
│  └─────────────┬───────────────────┬─────────────────┘  │
│                │                   │                     │
│  ┌─────────────▼──────┐  ┌────────▼────────────────┐    │
│  │ HostOpeningStrategy│  │ ParticipantStrategy      │    │
│  │ (主持开场策略)      │  │ (参与者发言策略)          │    │
│  └────────────────────┘  └─────────────────────────┘    │
│                │                   │                     │
│  ┌─────────────▼───────────────────▼─────────────────┐  │
│  │           HostSummaryStrategy (主持总结策略)        │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  SpaceContextManagerFactory → SpaceContextManager       │
│  (管理讨论历史、轮次、消息格式化)                          │
└─────────────────────────────────────────────────────────┘
           │ HTTP 请求 (OpenAI 兼容格式)
           ▼
┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐
│  Host Second-Me  │ │ Participant A    │ │ Participant B  │
│  (localhost:8002)│ │ (remote:8002)    │ │ (remote2:8002) │
└──────────────────┘ └──────────────────┘ └────────────────┘
```

## 创建和使用 Space

### 1. 创建 Space

通过 API 创建一个讨论空间：

```bash
curl -X POST http://localhost:8002/api/space/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI 产品功能设计讨论",
    "objective": "讨论如何在AI助手中加入日程管理功能，需要考虑用户体验、技术可行性和隐私保护",
    "host": "http://localhost:8002",
    "participants": [
      "http://participant-a:8002",
      "http://participant-b:8002"
    ]
  }'
```

请求字段说明：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 讨论主题标题 |
| objective | string | 是 | 讨论目标/议题描述 |
| host | string (URL) | 是 | 主持人端点（自动加入 participants 去重） |
| participants | string[] | 是 | 参与者端点 URL 列表（host 自动加入去重） |

host 和 participants 必须是 http(s) URL（由 `@validator` 校验）。创建后自动在后台线程启动讨论。

响应示例：

```json
{
  "id": "space-uuid-xxx",
  "title": "AI 产品功能设计讨论",
  "objective": "讨论如何在AI助手中加入日程管理功能...",
  "status": 2,
  "participants": ["http://localhost:8002", "http://participant-a:8002", "..."],
  "messages": [],
  "create_time": "2026-08-22T10:00:00"
}
```

### 2. 监控讨论状态

```bash
# 获取 Space 状态
curl http://localhost:8002/api/space/{space_id}/status

# 获取完整 Space 详情（含消息）
curl http://localhost:8002/api/space/{space_id}
```

Space 状态码：

| 状态值 | 常量名 | 含义 |
|--------|--------|------|
| 1 | STATUS_INITIALIZED | 已创建，讨论未开始 |
| 2 | STATUS_DISCUSSING | 讨论进行中 |
| 3 | STATUS_INTERRUPTED | 讨论中断 |
| 4 | STATUS_FINISHED | 讨论完成 |

### 3. 手动控制讨论

```bash
# 手动启动讨论（创建时未自动启动时使用）
curl -X POST http://localhost:8002/api/space/{space_id}/start

# 删除 Space
curl -X DELETE http://localhost:8002/api/space/{space_id}

# 分享 Space 到远程注册中心
curl -X POST http://localhost:8002/api/space/{space_id}/share
```

### 4. 获取所有 Space

```bash
# 获取所有 Space
curl http://localhost:8002/api/space/all

# 按 host 过滤
curl "http://localhost:8002/api/space/all?host=http://localhost:8002"
```

## 策略模式详解

Space 的核心是策略模式，所有策略继承自 `SpaceBaseStrategy`。

### 策略基类

```python
# lpm_kernel/api/domains/space/strategies/base.py（概念示意）
from abc import ABC, abstractmethod

class SystemPromptStrategy(ABC):
    """系统提示词策略抽象基类"""
    @abstractmethod
    def build_prompt(self) -> str:
        pass

class SpaceBaseStrategy(SystemPromptStrategy, ABC):
    """Space 策略基类"""
    def __init__(self, base_strategy: 'SpaceBaseStrategy' = None):
        # base_strategy 形成装饰器链
        self.base_strategy = base_strategy

    def build_prompt(self) -> str:
        """模板方法：先执行自身逻辑，再委托给 base_strategy"""
        prompt = self._build_space_prompt()
        if self.base_strategy:
            prompt += "\n\n" + self.base_strategy.build_prompt()
        return prompt

    @abstractmethod
    def _build_space_prompt(self) -> str:
        """子类实现具体的提示词构建"""
        pass

    def _format_message_for_context(self, message: dict) -> str:
        """格式化单条消息为 'Host/Participant endpoint: content' 格式"""
        sender = message.get('sender_endpoint', 'unknown')
        role = 'Host' if sender == self.host_endpoint else 'Participant'
        return f"{role} ({sender}): {message['content']}"

    def _build_context_from_messages(self, messages: list) -> str:
        """按 round 组织消息上下文"""
        context_parts = []
        current_round = None
        for msg in messages:
            if msg.get('round') != current_round:
                current_round = msg.get('round')
                context_parts.append(f"\n--- Round {current_round} ---")
            context_parts.append(self._format_message_for_context(msg))
        return "\n".join(context_parts)

    def _get_space_info(self) -> str:
        """格式化讨论主题和目标"""
        return f"Discussion Topic: {self.title}\nObjective: {self.objective}"
```

### 三种具体策略

#### HostOpeningStrategy（主持开场策略）

负责生成讨论开场词，欢迎参与者并提出首轮讨论观点。

```python
class HostOpeningStrategy(SpaceBaseStrategy):
    """主持开场策略"""
    def __init__(self, ctx, space_info, has_user_context=False):
        super().__init__()
        self.space_info = space_info
        self.has_user_context = has_user_context  # 是否有用户加载的额外上下文

    def _build_space_prompt(self) -> str:
        if self.has_user_context:
            # 有用户上下文的 prompt 模板
            return """You are the host of this multi-AI discussion.
A human user has provided context for this discussion.
Welcome all participants, acknowledge the user's context,
and open the discussion with your initial perspective.
Keep your opening concise (2-3 paragraphs)."""
        else:
            # 无用户上下文的 prompt 模板
            return """You are the host of this multi-AI discussion.
Welcome all participants, briefly frame the discussion topic,
and share your initial perspective to kick things off.
Keep your opening concise (2-3 paragraphs)."""
```

#### ParticipantStrategy（参与者策略）

维护参与者状态，基于完整讨论历史构建发言 prompt。固定 3 轮讨论。

```python
class ParticipantStrategy(SpaceBaseStrategy):
    """参与者发言策略"""
    def __init__(self, ctx, space_info, participant_endpoint):
        super().__init__()
        self.space_info = space_info
        self.participant_endpoint = participant_endpoint
        self.context_manager = None
        self.current_participant = None

    def _build_space_prompt(self) -> str:
        return """You are a participant in this multi-AI discussion.
You have been invited because of your unique perspective.
Rules:
1. Read all previous messages carefully before responding
2. Build on others' points, don't just repeat them
3. Offer your distinct viewpoint
4. If you disagree, explain why constructively
5. Keep each response focused (3-4 paragraphs max)
6. You will speak in your assigned round only
The discussion will run for exactly 3 rounds."""
```

#### HostSummaryStrategy（主持总结策略）

基于完整讨论记录生成总结。

```python
class HostSummaryStrategy(SpaceBaseStrategy):
    """主持总结策略"""
    def _build_space_prompt(self) -> str:
        return """You are the host wrapping up this multi-AI discussion.
Based on the complete discussion transcript, provide:
1. Key viewpoints raised by participants
2. Areas of consensus
3. Points of disagreement or tension
4. Your concluding recommendation or synthesis
Structure your summary clearly."""
```

## DiscussionService 编排流程

```python
# lpm_kernel/api/domains/space/services/discussion_service.py（概念示意）
class DiscussionService:
    def __init__(self):
        self.max_rounds = 3  # 固定 3 轮讨论

    async def run_discussion(self, space):
        """编排讨论流程"""
        # 1. 创建上下文管理器
        context_manager = SpaceContextManagerFactory.create(space)

        # 2. Host Opening（主持人开场）
        opening_strategy = HostOpeningStrategy(
            ctx=space,
            space_info={"title": space.title, "objective": space.objective},
            has_user_context=False
        )
        opening_prompt = opening_strategy.build_prompt()
        opening_msg = await self._call_participant(space.host, opening_prompt)
        context_manager.add_message(opening_msg, round=0, role="host")

        # 3. 多轮参与者发言
        for round_num in range(1, self.max_rounds + 1):
            for participant in space.participants:
                if participant == space.host:
                    continue
                # 每轮推进轮次
                participant_strategy = ParticipantStrategy(
                    ctx=space,
                    space_info={"title": space.title, "objective": space.objective},
                    participant_endpoint=participant
                )
                prompt = participant_strategy.build_prompt()
                context = context_manager.get_context_for_participant(participant)
                full_prompt = f"{prompt}\n\nDiscussion History:\n{context}"
                msg = await self._call_participant(participant, full_prompt)
                context_manager.add_message(msg, round=round_num, role="participant")

        # 4. Host Summary（主持人总结）
        summary_strategy = HostSummaryStrategy(ctx=space, space_info=...)
        summary_prompt = summary_strategy.build_prompt()
        full_context = context_manager.get_full_context()
        summary_msg = await self._call_participant(
            space.host,
            f"{summary_prompt}\n\nFull Discussion:\n{full_context}"
        )
        context_manager.add_message(summary_msg, round=self.max_rounds + 1, role="host")

        # 5. 标记完成
        space.status = STATUS_FINISHED
```

讨论流程时间线：

```
Round 0 (Opening)        Round 1                  Round 2                  Round 3                  Summary
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Host 开场    │───▶│ Participant A│───▶│ Participant A│───▶│ Participant A│───▶│ Host 总结    │
│ 欢迎+观点    │    │ 发言         │    │ 发言         │    │ 发言         │    │ 共识+分歧+   │
│              │    │              │    │              │    │              │    │ 建议         │
│              │    │ Participant B│    │ Participant B│    │ Participant B│    │              │
│              │    │ 发言         │    │ 发言         │    │ 发言         │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### HTTP 调用协议

参与者通过 OpenAI 兼容的 Chat Completions API 格式调用：

```python
async def _call_participant(self, endpoint: str, prompt: str) -> dict:
    """调用参与者端点（OpenAI 兼容格式）"""
    import httpx
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{endpoint.rstrip('/')}/api/talk/chat_json",
            json={
                "message": prompt,
                "enable_l0_retrieval": True,
                "enable_l1_retrieval": True,
                "temperature": 0.8
            }
        )
        result = response.json()
        return {
            "sender_endpoint": endpoint,
            "content": result.get("response", ""),
            "message_type": "text",
            "role": "assistant"
        }
```

## Space 数据模型

```python
# SpaceDTO 字段
class SpaceDTO:
    STATUS_INITIALIZED = 1
    STATUS_DISCUSSING = 2
    STATUS_INTERRUPTED = 3
    STATUS_FINISHED = 4

    id: str              # UUID
    title: str
    objective: str
    participants: list   # 端点 URL 列表
    host: str            # 主持人端点
    create_time: datetime
    messages: list       # SpaceMessageDTO 列表
    conclusion: str      # 讨论结论
    status: int          # 状态码
    space_share_id: str  # 分享ID（可选）

# SpaceMessageDTO 字段
class SpaceMessageDTO:
    id: str
    space_id: str
    sender_endpoint: str  # 发送者端点
    content: str
    message_type: str     # 消息类型
    round: int            # 讨论轮次
    create_time: datetime
    role: str             # host/participant
```

## Prompt 构建的装饰器链

Space 策略和 Talk 聊天都使用装饰器模式构建系统提示词。Talk 领域的 Prompt 构建链：

```
用户消息
  │
  ▼
BasePromptStrategy          # 基础策略：从 messages 中提取 system message
  │ (装饰器)
  ▼
RoleBasedStrategy           # 角色策略：优先使用 role_id 对应的 system_prompt
  │ (装饰器)
  ▼
KnowledgeEnhancedStrategy   # 知识增强：注入 L0/L1 检索结果
  │ (可选装饰器)
  ▼
ContextEnhancedStrategy     # 上下文增强：返回 CONTEXT_PROMPT
  │ (可选装饰器)
  ▼
ContextCriticStrategy       # 上下文批评：返回 JUDGE_PROMPT
  │
  ▼
最终 System Prompt
```

Talk 领域策略接口：

```python
# lpm_kernel/api/domains/kernel2/services/prompt_builder.py
class SystemPromptStrategy(ABC):
    @abstractmethod
    def build_prompt(self, messages, **kwargs) -> str:
        pass

class BasePromptStrategy(SystemPromptStrategy):
    """从 messages 中提取 system message"""
    def build_prompt(self, messages, **kwargs):
        system_msgs = [m for m in messages if m.get('role') == 'system']
        return system_msgs[-1]['content'] if system_msgs else ""

class KnowledgeEnhancedStrategy(SystemPromptStrategy):
    """装饰器：注入 L0/L1 检索知识"""
    def __init__(self, base_strategy, l0_context="", l1_context=""):
        self.base = base_strategy
        self.l0_context = l0_context
        self.l1_context = l1_context

    def build_prompt(self, messages, **kwargs):
        base = self.base.build_prompt(messages, **kwargs)
        knowledge = ""
        if self.l0_context:
            knowledge += f"\n\nRetrieved Knowledge (L0):\n{self.l0_context}"
        if self.l1_context:
            knowledge += f"\n\nIdentity Insights (L1):\n{self.l1_context}"
        return base + knowledge
```

## 消息上下文格式化

`_format_message_for_context` 将消息统一格式化为：

```
Host (http://localhost:8002): Welcome everyone to this discussion about...

--- Round 1 ---
Participant (http://participant-a:8002): Thank you for having me. I think...
Participant (http://participant-b:8002): Building on that point, I'd add...

--- Round 2 ---
Participant (http://participant-a:8002): To address the concern about...
```

这种格式让所有参与者能清楚区分：
- 谁在发言（Host 还是 Participant）
- 发言来自哪个端点
- 当前在第几轮讨论

## 使用建议

1. **参与者选择**：选择训练自不同领域资料的 Second-Me 实例，可以产生更有价值的多视角讨论
2. **Objective 描述**：清晰具体的讨论目标能引导出更聚焦的发言
3. **轮次控制**：默认 3 轮适合大多数场景；如需更长讨论可以调整 `max_rounds`
4. **错误处理**：某个参与者不可用时，DiscussionService 会继续其他参与者的发言
5. **异步处理**：`start_discussion` 在后台线程执行，通过 status 接口轮询进度
6. **跨网络部署**：参与者端点需要网络可达，部署时注意防火墙和 CORS 配置

## 相关概念

- [Space 策略模式](../concepts/space-strategy.md)
- [Flask API 服务](../concepts/flask-api-server.md)
- [L2 推理模型层](../concepts/l2-inference-model.md)
- [三层记忆架构 HMM](../concepts/three-layer-memory-hmm.md)
