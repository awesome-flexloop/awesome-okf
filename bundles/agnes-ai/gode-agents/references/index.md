# GodeAgents 信源参考索引

本目录包含 GodeAgents (codified-smolagents) 源码 API 参考文档，作为概念文档和示例文档的溯源依据。

## API 参考

| 文档 | 说明 |
|------|------|
| [agents-api.md](agents-api.md) | Agent 类 API——MultiStepAgent/ToolCallingAgent/CodeAgent 完整构造参数、公共方法、PromptTemplates 类型定义 |
| [tools-api.md](tools-api.md) | 工具类 API——Tool 基类、@tool 装饰器、ToolCollection/PipelineTool/SpaceToolWrapper、内置工具、JSON Schema 生成 |
| [models-api.md](models-api.md) | 模型层 API——Model 基类、8 种模型后端（HfApiModel/LiteLLMModel/OpenAI/Transformers/VLLM/MLX等）、消息类型、ChatMessage 数据类 |
| [memory-api.md](memory-api.md) | 记忆层 API——AgentMemory、MemoryStep 五层继承（SystemPromptStep/TaskStep/ActionStep/PlanningStep/FinalAnswerStep）、ToolCall 数据类 |
| [executor-api.md](executor-api.md) | 执行器 API——PythonExecutor 抽象基类、LocalPythonExecutor AST 安全执行、E2BExecutor/DockerExecutor 远程执行、安全常量 |
| [utils-api.md](utils-api.md) | 工具函数 API——异常层次、parse_code_blobs/truncate_content/make_json_serializable、AgentLogger/Monitor、工具验证 |

## 模板参考

| 文档 | 说明 |
|------|------|
| [prompts-reference.md](prompts-reference.md) | YAML 提示模板参考——code_agent.yaml/toolcalling_agent.yaml 结构、Jinja2 模板变量、规划/托管/最终答案子模板 |

## 工作文档

| 文档 | 说明 |
|------|------|
| [../facts.md](../facts.md) | R 阶段产出：从源码采集的 161 条零推测事实清单（F-001~F-161） |
| [../insights.md](../insights.md) | I 阶段产出：5 个核心架构洞察四元组与知识地图设计 |
