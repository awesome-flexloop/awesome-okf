# Deep Agents 核心洞察

> 基于 spec/facts.md 的事实提炼，形成对项目架构与设计哲学的深层理解。

## 洞察一：三层栈架构——"框架而非运行时"的定位哲学

Deep Agents 最核心的设计决策是**不重新发明运行时**。它明确地将自己定位为 LangChain `create_agent()` 之上的"有主见的框架"（opinionated harness），而 LangChain 又构建在 LangGraph 运行时之上。这种三层分工——LangGraph 负责状态/检查点/流式/中断，LangChain 负责模型+工具+中间件的 Agent 循环，Deep Agents 负责打包长周期 Agent 所需的默认组件——意味着 Deep Agents 的价值不在于执行引擎，而在于**组装和默认值**。

`create_deep_agent()` 作为唯一组装点，通过中间件栈（而非继承或重写）注入文件系统、子 Agent、摘要、记忆、权限等行为。中间件可以在模型调用前后、工具执行前后介入，这比单纯的工具回调强大得多——工具只能在模型选择后被动执行，中间件却能主动改写工具列表、注入提示、压缩历史。这种"组合优于继承"的设计使得每个组件都可独立替换，是 Extensible 原则的架构基础。

## 洞察二：Monorepo 的独立版本化与清晰模块边界

仓库采用 monorepo 但**每个包独立版本化**，没有根 `pyproject.toml`。七个包（deepagents、code、cli、acp、evals、talon、partners）各自拥有 `pyproject.toml`、`uv.lock`、`Makefile`，通过 uv 的 editable 本地依赖相互引用。这种设计在统一开发体验和独立发布节奏之间取得了平衡：

- **deepagents**（核心 SDK）是地基，版本 0.7.8，被所有上层包依赖。
- **code**（dcode）是最大的消费者，精确钉住 SDK 版本（`deepagents==0.7.8`），CI 强制检查 pin 不过期——这反映了 SDK 与终端产品之间的紧耦合需求。
- **cli** 和 **acp** 是横向扩展：前者面向部署运维，后者面向编辑器集成。
- **evals** 和 **talon** 处于不同成熟度阶段：evals 已深度集成 Harbor 和 CI 流水线，talon 明确标记为实验性 Alpha，单操作者设计，不接受安全漏洞报告。
- **partners** 是插件式沙箱/提供商集成，每个子包独立。

包边界通过 AGENTS.md 中的"搜索卫生"（search hygiene）指南进一步强化：开发者被引导定向搜索特定路径，避免全仓库漫游。libs/Makefile 的 fan-out 目标（lint、format、lock-check）则在保持独立性的同时提供了全局一致性保障。

## 洞察三：Code 模块的客户端/服务器分离与 Textual TUI 工程

`deepagents-code` 是整个仓库中最复杂的产品包，其架构值得关注的是**客户端/服务器双进程分离**。终端客户端（Textual TUI）和 Agent 服务器运行在不同进程中，通过流式协议通信。这种分离带来了三个关键收益：(1) UI 响应性不受 Agent 执行阻塞；(2) Agent 核心可脱离 UI 独立测试；(3) 会话状态通过 LangGraph 检查点持久化，支持恢复。

Code 模块的 AGENTS.md 展现了极高的工程规范密度：Textual 的 `Content` vs Rich `Text` 的精确使用规则、f-string 标记注入的安全防护、字形/动画的单一来源真理、UI 组件目录组织约定（screens/modals/widgets）、模态框测试必须模拟真实按键路径、启动热路径禁止重型导入。这些规则的存在说明 TUI 工程有其独特的复杂性——从渲染安全（标记注入）、性能（延迟导入）、到可访问性（ASCII 降级），每一项都有具体的教训沉淀为强制规范。

特别值得注意的是 SDK 依赖 pin 策略和启动性能要求：精确版本钉住确保产品稳定性，而"不得在模块级别导入 deepagents/LangChain/LangGraph"的规则则直接回应了终端工具"瞬间启动"的用户期望。

## 洞察四：ACP 协议——将 Agent 嵌入编辑器的标准化桥接

ACP（Agent Client Protocol）集成代表了 Deep Agents 从终端向**编辑器原生体验**扩展的战略方向。`AgentServerACP` 将编译后的 LangGraph 图适配为 ACP 服务器，使 Zed 等编辑器可以直接内嵌 Agent 线程。关键设计点包括：

- **会话持久化**：通过 LangGraph checkpointer 实现 `session/load`，重启后恢复线程并回放对话。
- **动态模型切换**：通过 Session Config Options 在会话中切换模型，Agent 工厂模式（`build_agent(context)`）根据上下文模型构建不同 Agent。
- **双模式**：既可包装自定义 Deep Agent，也可通过 `dcode --acp` 直接暴露完整编码 Agent，降低使用门槛。

ACP 的意义在于它定义了一个**与传输无关的 Agent 接口标准**——Agent 不再绑定到特定 UI，而是可以作为协议端点被任何兼容客户端消费。这与 Talon 的通道适配（WhatsApp/Telegram）形成互补：ACP 面向开发者工具场景，Talon 面向消息平台场景，两者都体现了"Agent 核心与交互通道分离"的架构思想。

## 洞察五：评估驱动的工程文化与 Harbor 沙箱基准

Evals 模块不是附属品，而是 Deep Agents 工程方法论的核心支柱。它运行**真实 LLM**（非 mock），捕获完整轨迹（工具调用、文件变更、最终响应），从正确性和效率两个维度评分。`deepagents-evals` CLI 提供了从单次试跑到多次试验聚合、失败重试、雷达图生成的完整工作流，退出码设计（0/1/2/3）明确支持自动化。

更重要的是 Harbor 集成——这是一个沙箱化基准测试框架，支持 Terminal Bench 2.0 等外部基准。drbench 和 contextbench 适配器展示了如何将外部评估集封装为 Harbor 可运行的格式，而 `.github/scripts/evals/` 下的大量脚本（shard_matrix、unified_prep、aggregate_unified、prune_agent_deps）则揭示了 CI 中大规模评估编排的复杂性：分片执行、统一聚合、依赖修剪、实验命名、失败分析。

评估结果与 LangSmith 深度集成，每次试验都产生 experiment URL，形成可追溯的质量基线。`pytest_reporter` 插件将 pytest 退出码重写为 0（避免 CI shell 步骤失败），转而通过 `trials_summary.json` 的 `counts.failed.mean` 判断成功——这种设计确保了 CI 工作流不会因个别评估失败而中断，同时保留了精确的失败信号。这是一种"测量而非阻断"的成熟工程文化。
