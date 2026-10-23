# Concepts

- [00 - 入门指引：安装、运行与目录结构](00-getting-started.md) — npm/源码两条启动路径、五个内置 profile、DSH_HOME 布局、首次配模型与启动诊断
- [01 - 架构总览：一切皆插件与能力缝](01-architecture-overview.md) — 插件树、profile 叠加、三事件域、turn/step 流程、seam 三角色与全局纪律
- [02 - Cordis 插件模型](02-cordis-plugin-model.md) — Context/Service/Plugin/Fiber 四抽象、声明合并与 DI、五种事件模式、effect 副作用栈
- [03 - Profile 与组合包](03-profile-and-bundle.md) — 两种 manifest、四层叠加顺序与整行替换语义、组合包解析、五 profile 初始化
- [04 - Agent 循环](04-agent-loop.md) — turn/step 定义与实际顺序、pre-step 准入、提示词准入规则、取消语义与工具结果补记
- [05 - 会话与持久化](05-session-and-persistence.md) — 14 个 SessionEvent 变体、deriveMessages 投影、两套 generation、JSONL 发布与迁移链
- [06 - 工具系统](06-tool-system.md) — defineTool 与 schema DSL、作用域注册与 restrict/guard、执行流水线、工具分类全景
- [07 - LLM 抽象层](07-llm-abstraction.md) — 适配器契约、ContentBlock 词汇表、StreamChunk 联合类型、模型路由、compaction 与 token 计费
- [08 - 能力 seam 与子系统地图](08-capability-seams.md) — 22 个子系统的职责/ctx 键/包名总览，以及 MCP、Subagent、Skills、LSP、Workflow、Browser 细节
- [09 - 安全模型](09-security-model.md) — 沙箱三档模式与 fail-closed、审批结果闭合与策略、权限预设默认表与部署建议
- [10 - 应用形态](10-application-forms.md) — CLI/Web/Electron/Headless/ACP/Python SDK 七形态总览与各自边界

```{toctree}
:hidden:
:maxdepth: 7

00-getting-started
01-architecture-overview
02-cordis-plugin-model
03-profile-and-bundle
04-agent-loop
05-session-and-persistence
06-tool-system
07-llm-abstraction
08-capability-seams
09-security-model
10-application-forms
```
