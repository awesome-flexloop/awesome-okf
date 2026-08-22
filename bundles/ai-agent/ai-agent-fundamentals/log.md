# 更新日志

## 2026-08-22

### 新增
- 创建 AI Agent 框架核心架构知识包（ai-agent bundle）
- 10 个核心概念文档：
  - 00-introduction：AI Agent框架导论，覆盖12个开源项目全景
  - 01-agent-loop：Agent核心循环（think-act-observe工程实现）
  - 02-tool-system：工具系统（注册/授权/工具集组合/Capability Seam）
  - 03-memory-architecture：记忆架构（ST/LT分离、HMM三层模型）
  - 04-multi-agent：多智能体编排（MoA/Workspace/Subagent/AI Space）
  - 05-provider-abstraction：模型Provider抽象（适配器/注册表/运行时委托）
  - 06-context-management：上下文管理（滑动窗口/压缩/知识蒸馏）
  - 07-skill-persona：技能与Persona系统（SKILL.md/280+角色/知识编译）
  - 08-plugin-architecture：插件化架构（注册表→Fiber→Capability Seam）
  - 09-agent-protocols：Agent通信协议（MCP/ACP/COM/OSC）
- 4 个深度示例文档：
  - hermes-agent架构深度走读（Python，75+参数、MoA、13种设计模式）
  - Cordis插件系统深度解析（TypeScript，Context原型链、Fiber生命周期）
  - Second-Me分层记忆模型解析（L0→L1→L2 HMM、LoRA/DPO、人格阴影）
  - Intelligent Terminal ACP集成模式（C++/Rust双语言、COM/NamedPipe/OSC）
- 1 个信源登记簿：12个项目的源码路径、关键文件、核心类索引
- 分析覆盖 12 个开源项目：hermes-agent, veadk-python, Zleap-Agent, deepseek-harness, Cordis, agency-agents, anthropics/skills, book-to-skill, i-have-adhd, intelligent-terminal, Second-Me(mindverse)
