---
type: Reference
title: VeADK-Python 源码信源登记
description: VeADK-Python 源码路径、版本信息、核心目录与关键文件清单
tags: [veadk, python, agent, ai, source, reference]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T10:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: veadk-github
    resource: https://github.com/volcengine/veadk-python
    title: VeADK-Python GitHub 仓库
  - id: veadk-docs
    resource: https://volcengine.github.io/veadk-python/
    title: VeADK 官方文档
---

# VeADK-Python 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | veadk-python (Volcengine Agent Development Kit) |
| 包名 | `veadk-python` |
| 版本 | 通过 setuptools-scm 从 git tag 动态获取，fallback 为 `"0.0.0"`；未安装时为 `"0.0.0+unknown"` |
| 描述 | 火山引擎智能体开发工具包，集成火山引擎云服务能力，基于 Google ADK 构建 |
| 作者 | Yaozheng Fang, Guodong Li, Zhi Han, Meng Wang 等 |
| 许可证 | Apache License 2.0 |
| Python 要求 | >= 3.10 |
| 官方文档 | <https://volcengine.github.io/veadk-python/> |
| 源码仓库 | <https://github.com/volcengine/veadk-python> |
| CLI 入口 | `veadk = "veadk.cli.cli:veadk"` |

## 核心依赖

| 依赖 | 版本约束 | 用途 |
|------|---------|------|
| `google-adk` | >=1.34.0 | 基础 Agent 架构（LlmAgent、Runner 等） |
| `litellm` | >=1.83.7,<=1.83.14 | LiteLlm 模型调用（兼容 OpenAI 接口的模型） |
| `pydantic-settings` | ==2.10.1 | 配置管理（BaseSettings） |
| `volcengine-python-sdk` | >=5.0.36 | 火山引擎 API 与 Ark Responses API |
| `volcengine` | >=1.0.193 | 火山引擎签名与 AgentKit Runtime API |
| `fastmcp` | >=2.12.3 | MCP 协议服务端运行时 |
| `mcp` | ==1.26.0 | MCP 协议（匹配 google-adk 要求） |
| `sqlalchemy` | >=2,<3 | 会话持久化 |
| `a2a-sdk` | ==0.3.7 | Google Agent2Agent 协议 |
| `opentelemetry-exporter-otlp` | ==1.37.0 | OpenTelemetry 链路追踪导出 |

## 源码位置

VeADK-Python 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/models/ai/veadk-python/
```

Python 包根目录：

```
external/libs/models/ai/veadk-python/veadk/
```

## 核心目录结构

### 顶层目录

| 目录/文件 | 用途 |
|-----------|------|
| `veadk/` | Python 核心包（Agent、Runner、工具、记忆等） |
| `frontend/` | 前端 React 应用（TypeScript + Vite） |
| `examples/` | 示例代码（quickstart、多 Agent、记忆、知识库等） |
| `tests/` | 单元测试与集成测试 |
| `docs/` | 文档站（Next.js + MDX） |
| `docker/` | Docker 构建文件 |
| `assets/` | 静态资源（Logo 等） |
| `pyproject.toml` | 项目构建配置与依赖声明 |
| `config.yaml.full` | 完整配置文件模板 |
| `config.yaml.simple` | 简化配置文件模板 |

### veadk/ 包目录结构

| 目录 | 用途 | 关键文件 |
|------|------|---------|
| `veadk/` (根) | 核心入口：Agent、Runner、配置、常量 | `__init__.py`、`agent.py`、`runner.py`、`config.py`、`consts.py`、`types.py`、`version.py`、`agent_builder.py`、`harness.py` |
| `veadk/agents/` | Agent 组合类型与监督者 | `sequential_agent.py`、`parallel_agent.py`、`loop_agent.py`、`supervise_agent.py` |
| `veadk/models/` | 模型适配层 | `ark_llm.py`（Ark Responses API）、`ark_embedding.py`（Embedding 模型） |
| `veadk/memory/` | 短期/长期记忆系统 | `short_term_memory.py`、`long_term_memory.py`、`save_session_callback.py`、`types.py` |
| `veadk/memory/short_term_memory_backends/` | 短期记忆后端 | `base_backend.py`、`mysql_backend.py`、`postgresql_backend.py`、`sqlite_backend.py` |
| `veadk/memory/long_term_memory_backends/` | 长期记忆后端 | `base_backend.py`、`in_memory_backend.py`、`opensearch_backend.py`、`redis_backend.py`、`vikingdb_memory_backend.py`、`mem0_backend.py`、`openviking_backend.py`、`tos_context_bucket_backend.py` |
| `veadk/knowledgebase/` | 知识库 RAG | `knowledgebase.py`、`types.py`、`entry.py` |
| `veadk/knowledgebase/backends/` | 知识库后端 | `base_backend.py`、`in_memory_backend.py`、`opensearch_backend.py`、`redis_backend.py`、`milvus_backend.py`、`vikingdb_knowledge_backend.py`、`openviking_backend.py`、`tos_vector_backend.py`、`context_search_backend.py` |
| `veadk/tools/` | 内置工具集 | `__init__.py`（工具注册表）、`ghost_char.py` |
| `veadk/tools/builtin_tools/` | 内置工具实现 | `web_search.py`、`web_fetch.py`、`run_code.py`、`ppt_generate.py`、`image_generate.py`、`video_generate.py`、`tts.py`、`load_knowledgebase.py`、`mcp_router.py` 等 |
| `veadk/skills/` | 技能管理系统 | `skill.py`、`registry.py`、`materializer.py`、`check_skills_callback.py`、`exceptions.py` |
| `veadk/cli/` | 命令行界面 | `cli.py`（主入口）、`cli_create.py`、`cli_deploy.py`、`cli_init.py`、`cli_web.py`、`cli_frontend.py`、`cli_eval.py` 等 |
| `veadk/configs/` | 配置子模型 | `model_configs.py`、`database_configs.py`、`auth_configs.py`、`tool_configs.py`、`tracing_configs.py`、`dynamic_config_manager.py` |
| `veadk/tracing/` | 链路追踪 | `base_tracer.py`、`telemetry/`（OpenTelemetry 集成） |
| `veadk/runtime/` | 多运行时支持 | `base_runtime.py`、`codex/runtime.py`、`piagent/runtime.py` |
| `veadk/a2a/` | Agent-to-Agent 协议 | `ve_a2a_server.py`、`registry_client.py`、`remote_ve_agent.py`、`agent_card.py`、`ve_agent_executor.py` |
| `veadk/a2ui/` | Agent 驱动 UI | `catalog.py`、`toolset.py` |
| `veadk/tunnel/` | MCP 隧道 | `toolset.py`、`registry.py`、`server.py`、`connector.py` |
| `veadk/flows/` | 自定义工作流 | `supervise_auto_flow.py`、`supervise_single_flow.py` |
| `veadk/prompts/` | 提示词管理 | `agent_default_prompt.py`、`prompt_manager.py`、`prompt_optimization.py`、`prompt_evaluator.py` |
| `veadk/processors/` | 运行时处理器 | `base_run_processor.py`（RunProcessor 抽象基类） |
| `veadk/auth/` | 认证与凭证 | `ve_credential_service.py`、`base_auth.py`、`veauth/`（各服务认证实现） |
| `veadk/integrations/` | 云服务集成 | `ve_faas/`、`ve_tos/`、`ve_tls/`、`ve_cozeloop/`、`ve_identity/`、`ve_cr/`、`ve_apig/`、`agentkit/` 等 |
| `veadk/evaluation/` | 评估框架 | `base_evaluator.py`、`eval_set_recorder.py`、`adk_evaluator/`、`deepeval_evaluator/` |
| `veadk/extensions/` | 扩展模块 | `harness/`（Harness 插件框架）、`feishu_channel.py`（飞书通道） |
| `veadk/multimodal/` | 多模态支持 | `api.py`、`service.py`、`storage.py`、`transport.py`、`plugin.py` |
| `veadk/realtime/` | 实时语音 | `client.py`、`live.py`、`protocol.py`、`doubao_realtime_voice_llm.py` |
| `veadk/reflector/` | 反射器 | `base_reflector.py`、`local_reflector.py` |
| `veadk/toolkits/` | 工具包 | `audio/`（ASR/TTS）、`dataset_auto_gen_callback.py` |
| `veadk/cloud/` | 云端部署 | `cloud_app.py`、`cloud_agent_engine.py`、`harness_app/` |
| `veadk/community/` | 社区适配 | `langchain_ai/`（LangChain 兼容层） |
| `veadk/examples/` | 内置示例 | `in_memory_example_store.py` |
| `veadk/utils/` | 工具函数 | `logger.py`、`misc.py`、`patches.py`、`adk_compat.py`、`auth.py`、`mcp_utils.py`、`pdf_to_images.py` 等 |

## 关键文件清单

### 核心入口与配置

| 文件 | 内容 |
|------|------|
| veadk/\_\_init\_\_.py | 包入口，延迟加载 `Agent` 和 `Runner`，导出 `__all__ = ["Agent", "Runner", "VERSION"]` |
| veadk/version.py | 版本号获取，通过 `importlib.metadata.version("veadk-python")` 读取安装时版本 |
| veadk/consts.py | 全局常量：默认 Agent 名、模型名、API Base、Embedding 配置、BytePlus 适配 |
| veadk/config.py | 全局配置聚合 `VeADKConfig`、环境变量加载（.env + config.yaml）、`getenv()` 函数、全局 `settings` 实例 |
| veadk/types.py | 公共类型定义：`MediaMessage`、`AgentRunConfig`、`RealtimeVoiceConnectConfig` |
| pyproject.toml | 项目构建配置、依赖声明、CLI 入口点、包发现规则、setuptools-scm 版本配置 |

### Agent 核心

| 文件 | 内容 |
|------|------|
| veadk/agent.py | **核心文件**：`class Agent(LlmAgent)` 定义，包含全部字段、`model_post_init` 初始化逻辑（模型创建、工具挂载、记忆集成、回调注册）、`_llm_flow` 流选择、`_run_async_impl` 运行时委托、`update_model()` 方法，以及模块级 patch（tracer/asyncio/mcp） |
| veadk/runner.py | **核心文件**：`class Runner(ADKRunner)` 定义，消息转换 `_convert_messages`、TOS 上传 `_upload_image_to_tos`、消息拦截装饰器 `intercept_new_message`、`run()` 异步执行入口、tracing 导出、评估集保存、长期记忆持久化 |
| veadk/agent_builder.py | `AgentBuilder` 类，从 YAML 配置构建 Agent，通过 `AGENT_TYPES` 字典映射类型名 |

### Agent 组合类型

| 文件 | 内容 |
|------|------|
| veadk/agents/sequential_agent.py | `class SequentialAgent(GoogleADKSequentialAgent)`，顺序执行子 Agent |
| veadk/agents/parallel_agent.py | `class ParallelAgent(GoogleADKParallelAgent)`，并行执行子 Agent |
| veadk/agents/loop_agent.py | `class LoopAgent(GoogleADKLoopAgent)`，循环执行子 Agent |
| veadk/agents/supervise_agent.py | Supervisor 模式：`build_supervisor()` 创建监督 Agent、`generate_advice()` 生成建议 |

### 记忆系统

| 文件 | 内容 |
|------|------|
| veadk/memory/short_term_memory.py | `class ShortTermMemory(BaseModel)`，支持 local/mysql/sqlite/postgresql/database 五种后端，自动创建 SessionService |
| veadk/memory/long_term_memory.py | `class LongTermMemory(BaseMemoryService, BaseModel)`，支持 local/opensearch/redis/viking/mem0/openviking/tos_context 后端，提供会话持久化与语义检索 |
| veadk/memory/save_session_callback.py | 会话保存回调，auto_save_session 功能实现 |
| veadk/memory/types.py | 记忆相关类型：`MemoryProfile` |

### 模型层

| 文件 | 内容 |
|------|------|
| veadk/models/ark_llm.py | `class ArkLlm(Gemini)`，通过火山引擎 Ark Responses API 调用模型，支持 streaming、fallback 模型链、响应缓存 |
| veadk/models/ark_embedding.py | Ark Embedding 模型封装 |

### 工具系统

| 文件 | 内容 |
|------|------|
| veadk/tools/\_\_init\_\_.py | 内置工具注册表 `_BUILTIN_TOOLS`（延迟加载）、`get_builtin_tool()`、`list_builtin_tools()` |
| veadk/tools/builtin_tools/web_search.py | 网页搜索工具 |
| veadk/tools/builtin_tools/web_fetch.py | 网页内容抓取工具 |
| veadk/tools/builtin_tools/run_code.py | 代码执行工具（沙箱） |
| veadk/tools/builtin_tools/ppt_generate.py | PPT 生成工具 |
| veadk/tools/builtin_tools/image_generate.py | 图片生成工具（豆包 Seedream） |
| veadk/tools/builtin_tools/video_generate.py | 视频生成工具（豆包 Seedance） |
| veadk/tools/builtin_tools/tts.py | 文本转语音工具 |
| veadk/tools/builtin_tools/load_knowledgebase.py | 知识库加载工具 |
| veadk/tools/builtin_tools/mcp_router.py | MCP Router 工具集（通过 HTTP 连接远程 MCP 服务） |
| veadk/tools/builtin_tools/agent_authorization.py | Agent 授权检查工具（enable_authz） |

### 知识库与技能

| 文件 | 内容 |
|------|------|
| veadk/knowledgebase/knowledgebase.py | `class KnowledgeBase(BaseModel)`，支持多种向量后端，提供文档添加/检索/Profile 生成 |
| veadk/knowledgebase/types.py | 知识库数据类型（KnowledgebaseEntry 等） |
| veadk/skills/skill.py | `class Skill(BaseModel)`，技能元数据定义（name/description/path/checklist 等） |
| veadk/skills/registry.py | 技能注册表管理 |

### CLI 命令行

| 文件 | 内容 |
|------|------|
| veadk/cli/cli.py | CLI 主入口（Click Group），注册所有子命令（deploy/init/create/web/frontend/studio/pipeline/eval/kb 等） |
| veadk/cli/cli_create.py | `veadk create` 命令：创建 Agent 项目 |
| veadk/cli/cli_web.py | `veadk web` 命令：启动 Web 服务 |
| veadk/cli/cli_deploy.py | `veadk deploy` 命令：部署 Agent |
| veadk/cli/cli_init.py | `veadk init` 命令：初始化项目配置 |

### A2A / A2UI / Tunnel

| 文件 | 内容 |
|------|------|
| veadk/a2a/ve_a2a_server.py | A2A 协议服务端实现 |
| veadk/a2a/remote_ve_agent.py | 远程 VeAgent（A2A 客户端代理） |
| veadk/a2a/registry_client.py | A2A Agent 注册中心客户端 |
| veadk/a2ui/toolset.py | A2UI 工具集：`build_a2ui_toolset()`、`_FallbackSendA2uiToClientToolset` |
| veadk/a2ui/catalog.py | A2UI 组件目录管理 |
| veadk/tunnel/toolset.py | MCP 隧道工具集：`TunnelToolset`，动态发现本地 MCP 服务器并创建代理 |
| veadk/tunnel/registry.py | 隧道注册中心：`TunnelRegistry`、`get_registry()` |
| veadk/tunnel/server.py | 隧道本地服务器：`LocalServer` |

### 配置子系统

| 文件 | 内容 |
|------|------|
| veadk/configs/model_configs.py | `class ModelConfig(BaseSettings)`，模型配置（name/provider/api_base/api_key），支持环境变量前缀 `MODEL_AGENT_` |
| veadk/configs/database_configs.py | 数据库配置：TOS/OpenSearch/MySQL/Redis/Milvus/Viking |
| veadk/configs/tracing_configs.py | 追踪配置：OpenTelemetry/APMPlus/Cozeloop/TLS/Prometheus |
| veadk/configs/auth_configs.py | 认证配置：VeIdentity |
| veadk/configs/tool_configs.py | 工具配置、PromptPilot 配置 |

### 运行时与处理器

| 文件 | 内容 |
|------|------|
| veadk/runtime/base_runtime.py | 运行时抽象基类 |
| veadk/runtime/codex/runtime.py | Codex 运行时后端 |
| veadk/runtime/piagent/runtime.py | PiAgent 运行时后端 |
| veadk/processors/base_run_processor.py | `BaseRunProcessor`（抽象）与 `NoOpRunProcessor`（空实现） |

### 提示词与评估

| 文件 | 内容 |
|------|------|
| veadk/prompts/agent_default_prompt.py | 默认系统提示词 `DEFAULT_INSTRUCTION` 和 `DEFAULT_DESCRIPTION` |
| veadk/prompts/prompt_manager.py | `BasePromptManager` 提示词管理器 |
| veadk/evaluation/eval_set_recorder.py | `EvalSetRecorder` 评估集录制器 |

### 工具函数

| 文件 | 内容 |
|------|------|
| veadk/utils/logger.py | 日志工具 `get_logger()` |
| veadk/utils/misc.py | 杂项工具：`getenv()`、`set_envs()`、`formatted_timestamp()`、`read_file_to_bytes()` |
| veadk/utils/patches.py | Monkey patches：`patch_tracer()`、`patch_asyncio()`、`patch_mcp_session_retry()` |
| veadk/utils/adk_compat.py | Google ADK 版本兼容层 |

## 核心类/函数索引

### 顶层导出

| 名称 | 类型 | 定义位置 | 说明 |
|------|------|---------|------|
| `Agent` | class | veadk/agent.py:L72 | 核心 Agent 类，继承 `google.adk.agents.LlmAgent` |
| `Runner` | class | veadk/runner.py:L329 | 执行引擎，继承 `google.adk.runners.Runner` |
| `VERSION` | str | veadk/version.py:L21 | 版本号字符串 |

### Agent 类

| 成员 | 类型 | 说明 |
|------|------|------|
| `Agent.id` | str | Agent 唯一标识，默认 UUID 首段 |
| `Agent.name` | str | Agent 名称，默认 `"veAgent"` |
| `Agent.description` | str | Agent 描述 |
| `Agent.instruction` | str | 系统指令 |
| `Agent.model_name` | Union[str, list[str]] | 模型名称，支持 fallback 列表 |
| `Agent.model_provider` | str | 模型提供商，默认 `"openai"` |
| `Agent.model_api_base` | str | API 基础 URL，默认火山引擎 Ark |
| `Agent.tools` | list[ToolUnion] | 工具列表 |
| `Agent.sub_agents` | list[BaseAgent] | 子 Agent 列表 |
| `Agent.knowledgebase` | Optional[KnowledgeBase] | 知识库 |
| `Agent.short_term_memory` | Optional[ShortTermMemory] | 短期记忆 |
| `Agent.long_term_memory` | Optional[LongTermMemory] | 长期记忆 |
| `Agent.skills` | list[str] | 技能列表 |
| `Agent.runtime` | Literal["adk","codex","piagent"] | 运行时后端选择 |
| `Agent.model_post_init()` | method | Pydantic 初始化后处理：API key 解析、模型实例化、工具自动挂载、回调注册 |
| `Agent.update_model(model_name)` | method | 切换模型 |
| `Agent._llm_flow` | property | 根据配置返回 SingleFlow/SupervisorSingleFlow/AutoFlow/SupervisorAutoFlow |
| `Agent._run_async_impl(ctx)` | method | 异步执行实现，非 adk 运行时委托给对应 runtime |

### Runner 类

| 成员 | 类型 | 说明 |
|------|------|------|
| `Runner(agent, short_term_memory, app_name, user_id, ...)` | constructor | 初始化 Runner，创建 SessionService，包装 run_async |
| `Runner.run(messages, user_id, session_id, ...)` | async method | 主执行入口，接收消息并返回文本结果 |
| `Runner.get_trace_id()` | method | 获取 Trace ID |
| `Runner.save_tracing_file(session_id)` | method | 导出 tracing 数据文件 |
| `Runner.save_eval_set(session_id, eval_set_id)` | method | 导出评估集 |
| `Runner.save_session_to_long_term_memory(...)` | method | 将会话保存到长期记忆 |
| `RunnerMessage` | type alias | 消息类型别名：str / list[str] / MediaMessage / list[MediaMessage] / list[MediaMessage \| str] |
| `_convert_messages(messages)` | function | 将 RunnerMessage 转换为 list[Content]，支持图片/视频 MIME 检测 |
| `_upload_image_to_tos(parts, ...)` | function | 将 inline_data 上传到 TOS 并替换为签名 URL |
| `intercept_new_message(process_func)` | decorator | 消息拦截装饰器，插入 pre/post run 处理和 thinking 聚合 |

### 组合 Agent 类

| 类名 | 继承 | 默认名称 | 文件位置 |
|------|------|---------|---------|
| `SequentialAgent` | `google.adk.agents.SequentialAgent` | `"veSequentialAgent"` | veadk/agents/sequential_agent.py:L31 |
| `ParallelAgent` | `google.adk.agents.ParallelAgent` | `"veParallelAgent"` | veadk/agents/parallel_agent.py:L31 |
| `LoopAgent` | `google.adk.agents.LoopAgent` | `"veLoopAgent"` | veadk/agents/loop_agent.py:L31 |

### 记忆类

| 类名 | 继承 | 支持后端 | 文件位置 |
|------|------|---------|---------|
| `ShortTermMemory` | `BaseModel` | local(InMemory)、mysql、sqlite、postgresql、database(→sqlite) | veadk/memory/short_term_memory.py:L57 |
| `LongTermMemory` | `BaseMemoryService, BaseModel` | local、opensearch、redis、viking、mem0、openviking、tos_context | veadk/memory/long_term_memory.py:L98 |

### 模型类

| 类名 | 继承 | 说明 | 文件位置 |
|------|------|------|---------|
| `ArkLlm` | `google.adk.models.Gemini` | 火山引擎 Ark Responses API 模型，支持 streaming/fallback/缓存 | veadk/models/ark_llm.py:L703 |
| `ModelConfig` | `BaseSettings` | 模型配置（环境变量前缀 MODEL_AGENT_） | veadk/configs/model_configs.py:L31 |

### 配置与类型

| 名称 | 类型 | 说明 | 文件位置 |
|------|------|------|---------|
| `VeADKConfig` | class | 全局配置聚合（model/tool/tracing/database/auth/realtime） | veadk/config.py:L64 |
| `settings` | VeADKConfig | 全局配置单例 | veadk/config.py:L146 |
| `MediaMessage` | class | 媒体消息（text + media 路径） | veadk/types.py:L25 |
| `AgentRunConfig` | class | VeFaaS 运行配置 | veadk/types.py:L33 |
| `KnowledgeBase` | class | 知识库 RAG | veadk/knowledgebase/knowledgebase.py:L92 |
| `Skill` | class | 技能元数据 | veadk/skills/skill.py:L19 |

### 处理器与工具

| 名称 | 类型 | 说明 | 文件位置 |
|------|------|------|---------|
| `BaseRunProcessor` | ABC | 运行时处理器抽象基类（process_run 抽象方法） | veadk/processors/base_run_processor.py:L27 |
| `NoOpRunProcessor` | class | 空运行时处理器（恒等装饰器） | veadk/processors/base_run_processor.py:L91 |
| `get_builtin_tool(name)` | function | 按名称获取内置工具 | veadk/tools/\_\_init\_\_.py:L49 |
| `list_builtin_tools()` | function | 列出所有内置工具名称 | veadk/tools/\_\_init\_\_.py:L60 |
| `TunnelToolset` | class | MCP 隧道工具集 | veadk/tunnel/toolset.py:L53 |

### CLI 入口

| 命令 | 定义位置 | 功能 |
|------|---------|------|
| `veadk` (group) | veadk/cli/cli.py:L64 | CLI 主入口 |
| `veadk create` | cli_create.py | 创建 Agent 项目 |
| `veadk init` | cli_init.py | 初始化配置 |
| `veadk deploy` | cli_deploy.py | 部署 Agent |
| `veadk web` | cli_web.py | 启动 Web 服务 |
| `veadk frontend` / `veadk studio` | cli_frontend.py | 前端/Studio 管理 |
| `veadk eval` | cli_eval.py | 评估 |
| `veadk kb` | cli_kb.py | 知识库管理 |
| `veadk agentkit` | cli_agentkit.py | AgentKit 相关 |
| `veadk harness` | cli_harness.py | Harness 测试 |

## 模块映射

### 用户导入路径 → 源码位置

| 导入路径 | 源码文件/目录 | 主要内容 |
|---------|-------------|---------|
| `veadk` | `veadk/__init__.py` | Agent、Runner、VERSION（延迟加载） |
| `veadk.Agent` | `veadk/agent.py` | Agent 类 |
| `veadk.Runner` | `veadk/runner.py` | Runner 类 |
| `veadk.agents` | `veadk/agents/` | SequentialAgent、ParallelAgent、LoopAgent |
| `veadk.memory` | `veadk/memory/` | ShortTermMemory、LongTermMemory |
| `veadk.models` | `veadk/models/` | ArkLlm、ArkEmbedding |
| `veadk.tools` | `veadk/tools/` | 内置工具注册表与工具函数 |
| `veadk.knowledgebase` | `veadk/knowledgebase/` | KnowledgeBase |
| `veadk.skills` | `veadk/skills/` | Skill、技能注册 |
| `veadk.config` | `veadk/config.py` | VeADKConfig、settings、getenv |
| `veadk.consts` | `veadk/consts.py` | 默认常量 |
| `veadk.types` | `veadk/types.py` | MediaMessage、AgentRunConfig |
| `veadk.a2a` | `veadk/a2a/` | A2A 协议服务端/客户端 |
| `veadk.a2ui` | `veadk/a2ui/` | A2UI 工具集与目录 |
| `veadk.tunnel` | `veadk/tunnel/` | MCP 隧道 |
| `veadk.runtime` | `veadk/runtime/` | 多运行时后端（codex/piagent） |
| `veadk.cli` | `veadk/cli/` | CLI 命令集 |
| `veadk.evaluation` | `veadk/evaluation/` | 评估框架 |
| `veadk.extensions` | `veadk/extensions/` | Harness 扩展、飞书通道 |
| `veadk.integrations` | `veadk/integrations/` | 火山引擎云服务集成 |
| `veadk.multimodal` | `veadk/multimodal/` | 多模态支持 |
| `veadk.realtime` | `veadk/realtime/` | 实时语音 |
| `veadk.processors` | `veadk/processors/` | RunProcessor |
| `veadk.prompts` | `veadk/prompts/` | 提示词管理 |
| `veadk.flows` | `veadk/flows/` | 自定义工作流（Supervisor 流） |
| `veadk.auth` | `veadk/auth/` | 认证与凭证服务 |
| `veadk.cloud` | `veadk/cloud/` | 云端部署 |
| `veadk.utils` | `veadk/utils/` | 工具函数（logger/misc/patches 等） |

### 典型使用模式

Quickstart 三步模式（来自 `examples/01_quickstart/main.py`）：

```python
from veadk import Agent, Runner

agent = Agent(
    name="my_agent",
    description="My first agent",
    instruction="You are a helpful assistant.",
)
runner = Runner(agent=agent, app_name="my_app")
result = await runner.run(
    messages="Hello!",
    session_id="my-session",
)
```

### 内置工具列表（15 个注册工具）

通过 `_BUILTIN_TOOLS` 字典注册，支持 `get_builtin_tool(name)` 按名获取：

| 工具名 | 功能 |
|--------|------|
| `web_search` | 网页搜索 |
| `web_fetch` | 网页内容抓取 |
| `parallel_web_search` | 并行网页搜索 |
| `vesearch` | 火山引擎搜索 |
| `link_reader` | 链接内容阅读 |
| `run_code` | 代码执行 |
| `coding` | 编码辅助 |
| `image_generate` | 图片生成 |
| `image_edit` | 图片编辑 |
| `video_generate` | 视频生成 |
| `video_task_query` | 视频任务查询 |
| `ppt_generate` | PPT 生成 |
| `text_to_speech` | 文本转语音 |
| `get_city_weather` | 城市天气查询 |
| `get_location_weather` | 位置天气查询 |

## 前端目录

前端位于 `frontend/`，基于 React + TypeScript + Vite：

| 目录 | 用途 |
|------|------|
| `frontend/src/adk/` | ADK 客户端（SSE 解析、认证、会话管理） |
| `frontend/src/a2ui/` | A2UI 组件系统（Surface、Registry、类型定义） |
| `frontend/src/ui/` | UI 组件（Agent 工作区、编辑器、侧边栏、追踪面板等） |
| `frontend/src/create/` | Agent 创建工作流（Skill Hub、模板创建、工作流创建） |
| `frontend/src/automations/` | 自动化集成（飞书机器人、GitHub 集成） |

## 构建系统

- **构建后端**：setuptools（`pyproject.toml` 声明 `setuptools.build_meta`）
- **版本管理**：setuptools-scm（从 git tag 自动推导版本号）
- **包发现**：`include = ["veadk*", "frontend", "frontend.server*"]`，排除 `assets*`、`ide*`、`tests*`
- **推荐环境**：uv 进行包管理（`uv sync`、`uv sync --extra extensions`）
- **Python 版本**：>= 3.10
