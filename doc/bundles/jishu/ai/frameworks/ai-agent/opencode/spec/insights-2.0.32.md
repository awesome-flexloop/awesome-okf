---
type: spec
scope: opencode
name: insights
version: "2.0.32"
source: "facts-2.0.32.md"
description: "从 OpenCode 2.0.32 固定源码事实提炼的架构洞察与增量学习地图"
---

# OpenCode 2.0.32 架构洞察与学习地图

本文件只解释本轮事实 `F-081`～`F-114` 所呈现的架构关系。旧版 `insights.md` 继续代表 2026-08-23 的历史快照，不在此重写。

## 核心洞察

### 洞察一：Prompt 被接纳不等于模型执行已经完成

- **陈述**：Server 收到 `session.prompt` 后将请求交给对应 session；Core 先准备输入并写入 admission，再按 `resume` 决定是否唤醒执行。唤醒后的工作由按 session key 管理的协调器排空，执行事件再参与持久化投影。
- **证据**：F-093～F-100、F-114。
- **反常识**：一次 prompt API 调用不是“把文本同步塞进模型并等到回答”的同义词。默认 `resume` 会触发执行唤醒，但 `resume: false` 允许只接纳输入；因此“输入已接收”“执行已开始”“执行已结束”是不同状态。
- **行动**：学习或排查会话时沿 `handler → Session.prompt → admission → execution.wake → coordinator/runner → event projector` 分段定位，不以 HTTP 请求完成推断模型 step 已完成。

### 洞察二：模型流与工具副作用之间有显式运行时边界

- **陈述**：会话 step 消费 `llm.stream` 事件；本地执行的 tool call 会进入工具执行 fiber。工具运行时解码输入并可校验输出，MCP 工具执行路径还调用 Permission 断言。
- **证据**：F-090、F-091、F-097。
- **反常识**：模型流中出现 tool call 不代表 provider 已替 OpenCode 完成该工具副作用；源码区分 provider 执行与本地执行，并且 MCP 工具并非绕开权限层的任意函数调用。
- **行动**：读工具路径时分别追踪模型事件、工具定义/schema、权限断言和执行 fiber；不要把 tool call 名称列表当作实际执行语义。

### 洞察三：Protocol 是 API 契约边界，Server 与 Client 围绕它装配

- **陈述**：Protocol 组合 API group 与 middleware 并导出 `ClientApi`；Server 将 API、handlers 和 middleware 装配为 routes；Client 构建脚本以 `ClientApi` 生成客户端契约，SDK 再导出 OpenCode 与 Tool namespace。
- **证据**：F-101～F-105。
- **反常识**：客户端类型并非需要由每个调用方从 Server handler 手工猜测；本快照明确存在 Protocol 到生成 Client 的构建路径。SDK 的包依赖同时包含 client/core/server 等模块，也不能简单等同于仅包装远端 HTTP 的薄客户端。
- **行动**：追踪 API 变化时从 Protocol group 开始，继续核对 Server handler 接线、Client 生成产物和 SDK 导出；分别判断远端 client contract 与 SDK 包边界。

### 洞察四：Monorepo 包清点与源码覆盖是两种不同的完成度

- **陈述**：五个 workspace glob 可枚举出 39 个 manifest，但该清单不代表 39 个包都经过实现深读；本轮覆盖矩阵将 6 个包标为深读、4 个包标为入口/接口读取、29 个包标为清单级。
- **证据**：F-082～F-084、F-110，以及本轮事实文件的 Workspace 包覆盖矩阵。
- **反常识**：清单数量完整并不自动等于架构理解完整；另一方面，未深读也不等于可以从 bundle 的包地图中消失。边界标注能同时保留整体视野与证据诚实度。
- **行动**：使用包地图选择阅读入口，并在引用“覆盖”时同时声明覆盖等级和未检查范围；本轮矩阵中的清单级角色只作为导航线索，不作实现行为证据。

### 洞察五：产品入口与工程交付由多个独立边界组成

- **陈述**：CLI、TUI、App、Desktop 分别有可定位的入口或接线；CI workflow 将 affected-package、跨平台 unit/build、浏览器测试和生成文件检查分段执行；发布 workflow 则协调 CLI、Node CLI、Electron 包构建与发布。
- **证据**：F-085、F-106～F-109、F-112～F-113。
- **反常识**：monorepo 中 package 数量不等于用户可见产品数，产品入口也不等于单一 UI。测试通过某一类 job 不能替代其他构建、生成检查或桌面打包边界的验证。
- **行动**：先按入口辨认运行形态，再按 CI/release workflow 找与目标改动对应的验证链；不要把某个 unit job 的成功扩写成全平台发布已验证。

## 增量知识地图

本轮新增 5 篇概念文档和 1 篇示例文档；按“先认包边界，再沿会话路径，再分解执行机制，最后看 API 与产品交付”的顺序阅读。每批 E 阶段新增文件不超过 7 个。

| 顺序 | 文档 | 学习目标与事实覆盖 | 前置关系 | 计划来源 |
|---|---|---|---|---|
| 1 | `concepts/05-monorepo-package-map.md` | 建立 39 个 workspace manifest 的目录视图，说明重点包角色、覆盖等级及 `github/`、`sdks/vscode/` 边界；F-082～F-084、F-110。 | 无；作为本轮入口。 | `/references/source-code-map-2.0.32.md` |
| 2 | `concepts/06-session-execution-lifecycle.md` | 从 Protocol prompt handler 追至 durable admission、wake/coordinator、runner、SQLite 与 event projector；F-093～F-100、F-102、F-114。 | 先读包地图；本轮核心路径。 | `/references/source-code-map-2.0.32.md` |
| 3 | `concepts/07-model-tool-extensibility.md` | 解释 Agent/Provider、模型包加载、tool schema、Permission、MCP/Plugin host 及本地 tool-call 执行边界；F-086～F-092、F-097。 | 建议先读会话生命周期。 | `/references/source-code-map-2.0.32.md` |
| 4 | `concepts/08-protocol-server-client-sdk.md` | 说明 Protocol group/middleware、Server handler 接线、生成式 Client contract 与 SDK 导出边界；F-101～F-105、F-114。 | 可与会话篇交叉阅读。 | `/references/source-code-map-2.0.32.md` |
| 5 | `concepts/09-product-surfaces-and-delivery.md` | 对照 CLI/TUI/App/Desktop 入口及 workflow 中的测试、构建和发布阶段；F-085、F-106～F-109、F-112～F-113。 | 建议先读包地图；作为系统视角收束。 | `/references/source-code-map-2.0.32.md` |
| 6 | `examples/02-session-prompt-trace.md` | 以源码跟踪一条 prompt 从 handler 到 admission/wake，再到 runner、tool 与事件投影；F-090、F-093～F-103、F-114。内容是源码导读轨迹，不承诺可直接运行。 | 先读会话生命周期；需要时回查工具/API 篇。 | `/references/source-code-map-2.0.32.md` |

每篇新增教程的 `sources` 均计划指向上述固定 commit 信源登记，并在正文引用对应事实编号；索引和变更日志留待全部 E 阶段内容完成后统一更新。

## 旧章节关系

- 既有 `concepts/00`～`04` 与 `examples/01` 保留为旧快照教程；本轮新增文件以 2.0.32 为事实边界，不重排旧编号。
- 新会话篇深化旧 `concepts/03-session-tools.md` 涉及的主题，但不复制旧内容，也不在未经版本对照前宣称旧章节完全适用于 2.0.32。
- 新产品交付篇只描述本轮可定位的入口与 workflow 事实，不延伸旧基础设施章节中的部署结论。
