---
okf_version: "0.2"
---

# AI Agent 框架核心架构知识库

本知识包系统分析了 12 个 AI Agent 相关开源项目的源码，覆盖 Python、TypeScript、C++/Rust 四种语言生态，提炼出 AI Agent 框架的 9 大核心架构概念，通过 hermes-agent、Cordis、Second-Me、Intelligent Terminal 四个深度示例进行代码级走读。所有内容均溯源至 `external/libs/models/ai/` 目录下的源码文件，遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 项目覆盖

| 项目 | 语言 | 核心特色 |
|------|------|---------|
| hermes-agent | Python | 75+参数可配置Agent、ToolRegistry单例、MoA多代理、工具集DAG组合 |
| veadk-python | Python | Agent/Runner分层、长短记忆分离、运行时委托（adk/codex/piagent） |
| Zleap-Agent | TypeScript | Workspace-first上下文隔离、Run/Work/Step三级状态机、Hook系统 |
| deepseek-harness | TypeScript | "一切皆插件"Cordis架构、Capability Seam模式、ACP支持 |
| Cordis | TypeScript | 时空可组合性元框架：Context原型链+Fiber生命周期+5种事件模式 |
| agency-agents | Markdown | 280+专业Agent persona、18部门、多工具适配脚本 |
| anthropics/skills | MD+Python | Anthropic官方Skills参考实现、SKILL.md标准 |
| book-to-skill | Python | 编译时知识蒸馏、四层产出结构、24-51×token节省 |
| i-have-adhd | MD+Shell | 认知科学驱动的输出风格技能、10条规则 |
| intelligent-terminal | C++/Rust | Windows Terminal原生Agent集成、ACP协议、COM/OSC |
| Second-Me | Python/TS | 三层记忆HMM（L0→L1→L2）+ LoRA个性化+去中心化Agent网络 |

## 基础概念（concepts/）

* [AI Agent 框架导论](concepts/00-introduction.md) — 什么是AI Agent框架、核心子系统、12个项目全景、学习路径与前置知识
* [Agent 核心循环](concepts/01-agent-loop.md) — think-act-observe循环的工程实现、三种执行模式（并发/顺序/分段）、状态机设计、waterfall事件链、运行时委托
* [工具系统](concepts/02-tool-system.md) — 工具注册、Function Calling、授权门控、ToolRegistry单例、工具集DAG组合、Capability Seam三角色模式
* [记忆架构](concepts/03-memory-architecture.md) — 短期/长期记忆分离、分区记忆+RRF向量召回、Second-Me三层记忆建模（L0原始摄取→L1身份洞察→L2 LoRA对齐）

## 进阶架构（concepts/）

* [多智能体编排](concepts/04-multi-agent.md) — MoA两阶段推理（fan-out→aggregator）、Workspace流水线、子代理委派、去中心化AI Space、Persona+Playbook编排
* [模型 Provider 抽象](concepts/05-provider-abstraction.md) — 适配器模式、ProviderRegistry/ModelRegistry双注册表、模型级能力覆盖、Service Seam、运行时委托
* [上下文管理](concepts/06-context-management.md) — 滑动窗口+摘要压缩、Workspace级上下文隔离、编译时知识蒸馏、token预算分配、发现循环税

## 扩展与生态（concepts/）

* [技能与 Persona 系统](concepts/07-skill-persona.md) — SKILL.md开放标准、280+ Persona角色库、知识编译四层产出、认知适配风格技能、信任/风险审计、模型内化人格
* [插件化架构模式](concepts/08-plugin-architecture.md) — 从简单注册表到Cordis Fiber生命周期、Context原型链（extend/isolate/intercept）、五种事件分发模式、Capability Seam、声明式YAML组合
* [Agent 通信协议](concepts/09-agent-protocols.md) — MCP（模型上下文协议）、ACP（Agent客户端协议）、多平台传输层抽象、COM进程外服务器、OSC 133错误事件总线

## 实战示例（examples/）

* [hermes-agent 架构深度走读](examples/hermes-agent-deep-dive.md) — AIAgent入口、75+参数配置、ToolRegistry单例、工具集DAG解析、MoA两阶段实现、13种设计模式盘点、安全多层防御
* [Cordis 插件系统深度解析](examples/cordis-plugin-system.md) — Context原型链Object.create()、Fiber PENDING→LOADING→ACTIVE→DISPOSED状态机、Service依赖注入、五种事件分发模式（emit/parallel/serial/bail/waterfall）、YAML声明式组合
* [Second-Me 分层记忆模型解析](examples/second-me-memory-model.md) — L0 FileInfo/BioInfo、L1 Chunk/MemoryType/TimeType/Shade阴影生成、L2 SelfQA+Preference Pairs+LoRA+DPO、GraphRAG+ChromaDB、AI Space host/participant策略
* [Intelligent Terminal ACP 集成模式](examples/intelligent-terminal-acp.md) — C++/Rust双语言架构、helper+master双进程、COM进程外服务器、Named Pipe/stdio双通道、预热启动+Stash模式、OSC 133错误自动检测、wtcli终端控制

## 信源登记簿（references/）

* [AI Agent 框架源码信源登记](references/ai-agent-sources.md) — 12个项目的源码路径、版本信息、核心目录结构、关键文件清单、核心类索引、跨项目架构概念映射

## 信任与生命周期说明

* **status 判定依据**：全部 15 个内容文档（10 个概念 + 4 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 `external/libs/models/ai/` 目录下 12 个开源项目源码的逐模块阅读与事实提取，经 source-code-to-okf-wiki 五阶段流程（R→I→E→V→C）生成。
* **stale_after 解释**：统一设置为 `2027-08-22`。AI Agent 框架领域迭代迅速（MCP/ACP等新协议持续演进），但核心架构模式（Agent循环、工具注册表、插件系统、记忆分层）具有较长时效性；该日期作为对框架生态重大变化（如MCP/ACP标准正式发布1.0、Agent协议格局变化）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-22）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-22），两者分离、可追溯。
* **内容敏感度**：本知识包分析的全部 12 个项目均为公开开源代码（GitHub 公开仓库），无访问控制要求，属公开内容（Public），遵循标准工作流。

本知识包共收录 15 个内容文档（10 个概念 + 4 个示例 + 1 个信源登记），另含 3 个子目录 index.md、1 个 bundle 根 index.md、1 个 group 索引和 1 个 log.md。
