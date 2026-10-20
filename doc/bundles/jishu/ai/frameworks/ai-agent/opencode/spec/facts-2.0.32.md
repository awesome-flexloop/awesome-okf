---
type: spec
scope: opencode
name: facts
version: "2.0.32"
source: "https://github.com/anomalyco/opencode/tree/6ec56821d63100fe5bda45b759364f561c56b359"
description: "OpenCode 2.0.32 固定源码快照的包清单、关键接口与执行路径事实"
---

# OpenCode 2.0.32 源码事实

本文件只记录 `anomalyco/opencode` 固定快照 `6ec56821d63100fe5bda45b759364f561c56b359` 中可定位的内容。原 bundle 的 `F-001`～`F-080` 属于 2026-08-23、版本 `1.18.21` 的历史快照；本轮从 `F-081` 续接，不覆盖旧事实。下列源码链接均固定到本轮 commit，不依赖本地 checkout 或浮动分支。

## 根配置与工作区包地图

- **F-081**：根 `package.json` 声明项目版本为 `2.0.32`，包管理器为 `bun@1.4.2`。[`package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/package.json#L5-L8)
- **F-082**：根 `package.json` 的 workspace glob 为 `packages/*`、`packages/plugins/*`、`services/*`、`packages/console/*`、`packages/stats/*`。[`package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/package.json#L38-L45)
- **F-083**：按 F-082 的五个 glob 对工作树中的 `package.json` 文件逐项枚举，得到 39 个匹配项。该数量只表示匹配的 manifest 文件，不代表发布包、运行时组件或源代码目录的数量。计数分组为 `packages/*` 29、`packages/plugins/*` 1、`services/*` 4、`packages/console/*` 2、`packages/stats/*` 3；清单如下。

| 工作区匹配路径 | Manifest 中声明的包名 |
|---|---|
| [`packages/ai/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/ai/package.json) | `@opencode/ai` |
| [`packages/app/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/app/package.json) | `@opencode/app` |
| [`packages/cli/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/cli/package.json) | `@opencode/cli` |
| [`packages/client/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/client/package.json) | `@opencode/client` |
| [`packages/codemode/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/package.json) | `@opencode/codemode` |
| [`packages/console/app/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/console/app/package.json) | `@opencode/console-app` |
| [`packages/console/resource/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/console/resource/package.json) | `@opencode/console-resource` |
| [`packages/core/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/package.json) | `@opencode/core` |
| [`packages/desktop/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/package.json) | `@opencode/desktop` |
| [`packages/function/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/function/package.json) | `@opencode/function` |
| [`packages/gui-extensions/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/gui-extensions/package.json) | `@opencode/gui-extensions` |
| [`packages/http-recorder/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/http-recorder/package.json) | `@opencode/http-recorder` |
| [`packages/httpapi-codegen/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/httpapi-codegen/package.json) | `@opencode/httpapi-codegen` |
| [`packages/latex/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/latex/package.json) | `@opencode/latex` |
| [`packages/merman/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/merman/package.json) | `@opencode/merman` |
| [`packages/plugin-browser/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/plugin-browser/package.json) | `@opencode/plugin-browser` |
| [`packages/plugin/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/plugin/package.json) | `@opencode/plugin` |
| [`packages/plugins/figma/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/plugins/figma/package.json) | `@opencode/plugin-figma` |
| [`packages/posts/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/posts/package.json) | `@opencode/posts` |
| [`packages/protocol/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/package.json) | `@opencode/protocol` |
| [`packages/schema/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/schema/package.json) | `@opencode/schema` |
| [`packages/script/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/script/package.json) | `@opencode/script` |
| [`packages/sdk/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/sdk/package.json) | `@opencode/sdk` |
| [`packages/server/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/server/package.json) | `@opencode/server` |
| [`packages/session-ui/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/session-ui/package.json) | `@opencode/session-ui` |
| [`packages/simulation/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/simulation/package.json) | `@opencode/simulation` |
| [`packages/stats/app/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/stats/app/package.json) | `@opencode/stats-app` |
| [`packages/stats/core/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/stats/core/package.json) | `@opencode/stats-core` |
| [`packages/stats/server/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/stats/server/package.json) | `@opencode/stats-server` |
| [`packages/storybook/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/storybook/package.json) | `@opencode/storybook` |
| [`packages/theme/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/theme/package.json) | `@opencode/theme` |
| [`packages/tui/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/tui/package.json) | `@opencode/tui` |
| [`packages/ui/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/ui/package.json) | `@opencode/ui` |
| [`packages/util/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/util/package.json) | `@opencode/util` |
| [`packages/web/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/web/package.json) | `@opencode/web` |
| [`services/changelog/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/services/changelog/package.json) | `@opencode/changelog` |
| [`services/files/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/services/files/package.json) | `@opencode/files` |
| [`services/update/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/services/update/package.json) | `@opencode/update` |
| [`services/www/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/services/www/package.json) | `@opencode/www` |

  R 阶段计数方式：对上述五个 glob 分别枚举 `package.json`，将结果按路径排序并统计总行数；计数对象为 manifest 路径，且每个 glob 分组互不重叠。V 阶段将改用 Python `Path.glob` 对同五个 glob 重新计数，并与此清单逐项集合比对。

- **F-084**：仓库另有 [`github/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/github/package.json) 与 [`sdks/vscode/package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/sdks/vscode/package.json)，但这两个路径不匹配 F-082 列出的五个 workspace glob。
- **F-085**：根 `turbo.json` 声明 `typecheck`、`build` 与 `test` 任务；`build` 和 `test` 都依赖 `transit`，`build` 输出 `dist/**`，`test` 输出列表为空。根 `package.json` 的 `test` 脚本明确退出失败并提示不要从根运行测试。 [`turbo.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/turbo.json#L13-L48) [`package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/package.json#L27-L36)

## Core 服务、Provider 与权限

- **F-086**：`packages/core/src/agent.ts` 的 `Agent.Interface` 声明 `get`、`resolve`、`select` 和 `list`；其 `node` 通过 `makeLocationNode` 注册 `Service`，依赖 `Bus.node`。 [`agent.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/agent.ts#L40-L47) [`agent.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/agent.ts#L116)
- **F-087**：`packages/core/src/provider.ts` 的 `Provider.Interface` 声明 `get`、`all`、`available`、`snapshot`；Provider node 使用 `makeLocationNode`，依赖 `Bus.node`、`Integration.node` 和 `Location.node`。 [`provider.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/provider.ts#L315-L323) [`provider.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/provider.ts#L508)
- **F-088**：Provider 源码维护内置包映射；`loadPackage` 先按 specifier 查内置映射，再尝试模块解析；未解析且没有 `npm` 接口时返回 `LoadError`，有 `npm` 接口时调用 `npm.add(root)` 后解析并加载模块。 [`provider.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/provider.ts#L47-L48) [`provider.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/provider.ts#L154-L183)
- **F-089**：`Permission.evaluate(action, resource, ...rulesets)` 将规则集展平，查找最后一条 action 与 resource 均匹配的规则；没有匹配时返回 `effect: "ask"` 的规则。 [`permission.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/permission.ts#L87-L100)
- **F-090**：`packages/core/src/tool/runtime.ts` 将输入交给 schema 解码；声明 output schema 的工具若没有返回 `output` 会产生工具错误，返回值则经过输出 schema 编码。 [`runtime.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/tool/runtime.ts#L29-L59) [`runtime.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/tool/runtime.ts#L77-L80)
- **F-091**：`packages/core/src/tool/mcp.ts` 为发现的 MCP 工具添加 namespace、description、输入与输出 schema；MCP 工具执行路径调用 `permission.assert(...)`；该 node 依赖 `Tool.node`、`Mcp.node`、`Bus.node` 和 `Permission.node`。 [`tool/mcp.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/tool/mcp.ts#L38-L52) [`tool/mcp.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/tool/mcp.ts#L148-L152)
- **F-092**：`PluginHost.make` 从 Effect Context 获取 Agent、Provider、Model、MCP、Tool、Permission、Session、Worktree 等服务；插件存储前缀由 `plugin:`、`pluginID` 中各 UTF-16 code unit 的四位十六进制表示和末尾 `:` 拼接而成。 [`host.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/plugin/host.ts#L47-L73) [`host.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/plugin/host.ts#L623-L647)

## 会话执行、事件与持久化

- **F-093**：`SessionRunCoordinator.make<Key, E, Reason>` 的 `drain` 按 `Key` 接收工作；执行状态按 key 存储，`pendingWake` 记录活动执行期间新增的唤醒，循环在有待处理唤醒时继续 drain。 [`run-coordinator.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/run-coordinator.ts#L32-L47) [`run-coordinator.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/run-coordinator.ts#L60-L85)
- **F-094**：协调器对同 key 的活动执行提供 join、wake、interrupt 和 `awaitIdle` 操作；`wake` 会记录活动 key 的待处理唤醒，空闲 key 则启动执行。 [`run-coordinator.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/run-coordinator.ts#L11-L29) [`run-coordinator.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/run-coordinator.ts#L124-L144)
- **F-095**：`SessionExecution` 将 `SessionEvent.Execution.Started` 发布与 `SessionStore.claim(sessionID)` 作为同一 commit 回调；成功与失败终态发布时调用 `release`，shutdown 中断发布不携带 release 回调，其他中断携带 release 回调。 [`execution.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/execution.ts#L76-L86) [`execution.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/execution.ts#L111-L145)
- **F-096**：会话 LLM runner 的 drain 循环先准备 context、提升可处理的 inbox 项，再调用 `runStep` 并增加 step 序号。 [`llm.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/runner/llm.ts#L166-L194)
- **F-097**：一次 runner step 调用 `llm.stream(input.prepared.request, input.prepared.options)`；收到非 provider 执行的 `tool-call` 事件后，创建本地工具执行 fiber，并在流结束后等待工具 fiber。 [`step.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/runner/step.ts#L86-L107) [`step.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/runner/step.ts#L120-L129) [`step.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/runner/step.ts#L143-L153)
- **F-098**：`packages/core/src/session/sql.ts` 声明 `session_v2`、`session_message`、`session_pending`、`session_inbox`、`instruction_entry`、`instruction_blob` 和 `instruction_state` SQLite 表。 [`sql.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/sql.ts#L22-L28) [`sql.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/sql.ts#L79-L173)
- **F-099**：`packages/core/src/session/projector.ts` 使用 `bus.project` 将 Session 事件（包括 Created、MessageContentUpdated、InboxEnqueued、Execution.Succeeded/Failed/Interrupted、Step 与 Tool 事件）投影到数据库处理函数。 [`projector.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/projector.ts#L445-L447) [`projector.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/projector.ts#L631-L699) [`projector.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/projector.ts#L705-L753)
- **F-100**：固定快照中的 `packages/core/src/database/migration/` 有 50 个 `.ts` 迁移文件；`migration.gen.ts` 中有 50 行 `import mNN from "./migration/...` 的迁移导入。计数口径不包括 `import type`。[`migration.gen.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/database/migration.gen.ts#L1-L53)

  R 阶段计数方式：PowerShell 分别统计迁移目录内 `*.ts` 文件，以及仅匹配 `^import m\d+ from` 的生成导入行；两项均为 50。V 阶段将以解析生成文件中的默认导入声明并枚举迁移目录文件的方式重新核对。

## Protocol、Server、Client 与 SDK

- **F-101**：`packages/protocol/src/api.ts` 组合 API group middleware，并在默认 API 上挂载 `Authorization` 与 `SchemaErrorMiddleware`；`makeDefaultApi` 为 API 构造入口。 [`api.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/src/api.ts#L137-L201) [`api.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/src/api.ts#L232-L245)
- **F-102**：`packages/protocol/src/groups/session.ts` 声明 `session.list`、`session.create`、`session.prompt` 和 `session.interrupt` 等 session API endpoint；本事实不声明该 group 的 endpoint 总数。 [`session.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/src/groups/session.ts#L101-L157) [`session.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/src/groups/session.ts#L320-L335) [`session.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/src/groups/session.ts#L670-L683)
- **F-103**：`packages/server/src/api.ts` 通过 `makeDefaultApi` 注入 Server middleware；`packages/server/src/routes.ts` 导出 `createRoutes` 和 `createEmbeddedRoutes`。 [`api.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/server/src/api.ts#L1-L12) [`routes.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/server/src/routes.ts#L81-L105)
- **F-104**：Protocol 导出 `ClientApi`；Client 的 build script 分别用 `ClientApi` 编译 promise contract 和 Effect contract；promise client 的 `make(options)` 调用生成客户端的 `OpenCode.make(options)`。 [`client.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/src/client.ts#L18-L36) [`build.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/client/script/build.ts#L42-L46) [`client.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/client/src/promise/client.ts#L8-L13)
- **F-105**：SDK 入口将 `./opencode` 与 `./tool` 分别作为 `OpenCode`、`Tool` namespace 导出；SDK manifest 的 `dependencies` 声明 `@opencode/client`、`@opencode/core`、`@opencode/plugin`、`@opencode/schema`、`@opencode/server` 和 `@opencode/util`，`devDependencies` 声明 `@opencode/ai`、`@opencode/httpapi-codegen` 和 `@opencode/protocol`。 [`index.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/sdk/src/index.ts#L1-L6) [`package.json`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/sdk/package.json#L30-L42)

## CLI 与交互界面入口

- **F-106**：CLI 入口将 `Commands` 与 `Runtime.handlers` 组合；默认命令处理器及 upgrade 等处理器通过动态 `import()` 加载。 [`index.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/cli/src/index.ts#L7-L36)
- **F-107**：`packages/tui/src/index.tsx` 从 `./app` 导出 `run` 与类型 `TuiInput`。 [`index.tsx`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/tui/src/index.tsx#L1)
- **F-108**：`packages/app/src/entry.tsx` 通过 Solid `render` 渲染 `AppInterface`；`packages/desktop/src/renderer/index.tsx` 渲染 `DesktopApp`。 [`entry.tsx`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/app/src/entry.tsx#L96-L112) [`index.tsx`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/src/renderer/index.tsx#L18-L22)
- **F-109**：`packages/desktop/src/shared/ipc-rpc.ts` 将 `AppRpcs` 与 `StorageRpcs`、`FileRpcs`、`WindowRpcs`、`MenuRpcs`、`EventRpcs`、`ExtensionRpcs` 合并为 `DesktopRpcs`。 [`ipc-rpc.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/src/shared/ipc-rpc.ts#L21-L26)

## 本轮覆盖边界

- **F-110**：F-083 清单覆盖根 workspace glob 匹配到的全部 manifest；下表逐包记录本轮源码抽样等级、包角色线索及未深读部分。标注“深读”表示围绕关键路径读取代表性实现，不表示通读该包全部源码；“入口/接口读取”与“清单级”只支持表中注明的有限范围，不据此推导未检查实现的行为。
- **F-111**：session endpoint 数量不纳入本轮数量断言；当前可证事实只列举了源码可定位的 endpoint 名称，避免把不同匹配表达式的原始命中数误报为 API 总数。
- **F-112**：`.github/workflows/test.yml` 定义 affected-package 检查、Linux/Windows unit job 和 build job；Linux unit 步骤还检查生成的 client 与 www 文档，另有受 affected app 输出控制的浏览器测试 job。 [`test.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/test.yml#L23-L56) [`test.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/test.yml#L99-L139) [`test.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/test.yml#L141-L205) [`test.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/test.yml#L207-L230)
- **F-113**：`.github/workflows/publish.yml` 的 `version` job 产出版号、release 和 tag 输出；后续 job 构建 CLI、Node CLI 与 Electron 桌面包，`publish` job 汇集这些 job 的结果并运行 `script/publish.ts`。 [`publish.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/publish.yml#L41-L74) [`publish.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/publish.yml#L76-L115) [`publish.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/publish.yml#L216-L266) [`publish.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/publish.yml#L343-L349) [`publish.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/publish.yml#L540-L549) [`publish.yml`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/.github/workflows/publish.yml#L644-L654)
- **F-114**：Server 的 `session.prompt` handler 将 session ID、消息 ID、文本、文件、agents、skills、metadata、delivery 和 resume 字段传给 `session.prompt`；Core 的 Session service 将调用转发至对应 session，其 prompt 实现准备输入、调用 `admission.admit`，并在 `resume !== false` 时调用 `execution.wake(sessionID)`。 [`session.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/server/src/handlers/session.ts#L279-L293) [`session.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session.ts#L450) [`session.ts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/session.ts#L155-L185)

### Workspace 包覆盖矩阵

覆盖等级：

- **深读**：检查包内多个关键源码文件，并沿接口或调用链核验职责边界。
- **入口/接口读取**：检查包入口、导出、生成契约或代表性接线文件；不声称覆盖其内部实现。
- **清单级**：检查 manifest 中的名称、依赖和脚本线索；实现源码不纳入本轮深读，避免把包清点误述为实现覆盖。

| 工作区包 | 子系统/角色线索 | 覆盖等级与范围边界 |
|---|---|---|
| [`@opencode/ai`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/ai/package.json) | LLM 流式抽象 | 深读：检查 `src/llm.ts` 及 core runner 的调用；未逐一检查全部 provider adapter。 |
| [`@opencode/app`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/app/package.json) | 应用 UI 入口 | 入口/接口读取：检查 `src/entry.tsx` 的渲染入口；页面与组件实现未深读。 |
| [`@opencode/cli`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/cli/package.json) | 命令行与运行时分发 | 深读：检查入口、runtime handlers 和 `run` 命令路径；其他命令处理器未逐项深读。 |
| [`@opencode/client`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/client/package.json) | HTTP API 客户端 | 深读：检查生成脚本、promise client 及其 Protocol 契约来源；未逐项检查所有生成 endpoint。 |
| [`@opencode/codemode`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/package.json) | 受限代码执行 | 清单级：依据 manifest 描述、依赖和脚本登记；执行沙箱实现未深读。 |
| [`@opencode/console-app`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/console/app/package.json) | Console Web 应用 | 清单级：登记独立 Web 应用边界；不属于本轮本地 agent 执行主路径，未深读页面与服务端逻辑。 |
| [`@opencode/console-resource`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/console/resource/package.json) | Console 资源包 | 清单级：登记 workspace 成员；未深读资源内容及消费路径。 |
| [`@opencode/core`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/package.json) | Agent、Provider、权限、工具、MCP、插件、会话及存储 | 深读：检查服务接口、会话协调和执行、LLM runner、工具/MCP/权限/插件、SQLite 与事件投影；未逐文件通读 core。 |
| [`@opencode/desktop`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/package.json) | 桌面壳与 IPC | 入口/接口读取：检查 renderer 入口与 RPC 类型合并；主进程启动、打包和平台适配未深读。 |
| [`@opencode/function`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/function/package.json) | 部署函数 | 清单级：登记包及测试脚本；云端 handler 与部署实现不属于本轮本地 agent 主路径，未深读。 |
| [`@opencode/gui-extensions`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/gui-extensions/package.json) | GUI 扩展集成 | 清单级：由名称和本地依赖登记 UI/插件边界；扩展加载实现未深读。 |
| [`@opencode/http-recorder`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/http-recorder/package.json) | HTTP/WebSocket 记录与回放 | 清单级：manifest 描述与脚本登记；录制、回放实现未深读。 |
| [`@opencode/httpapi-codegen`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/httpapi-codegen/package.json) | HTTP API 客户端代码生成 | 清单级：登记为生成工具包；生成器内部实现未深读。 |
| [`@opencode/latex`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/latex/package.json) | LaTeX 扩展包 | 清单级：登记其 workspace 与 plugin 依赖；渲染实现及调用点未深读。 |
| [`@opencode/merman`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/merman/package.json) | Mermaid/图表扩展包 | 清单级：登记其布局审计与测试脚本；图表布局实现未深读。 |
| [`@opencode/plugin`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/plugin/package.json) | 插件 API/类型包 | 清单级：登记导出包与依赖；插件公共接口本体未完整深读，运行时 host 由 core 覆盖。 |
| [`@opencode/plugin-browser`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/plugin-browser/package.json) | 桌面浏览器插件 | 清单级：manifest 描述及 plugin/schema 依赖；浏览器工具实现未深读。 |
| [`@opencode/plugin-figma`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/plugins/figma/package.json) | Figma MCP 集成与 skills | 清单级：登记 manifest 描述和同步脚本；集成协议与 skills 内容未深读。 |
| [`@opencode/posts`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/posts/package.json) | 内容发布包 | 清单级：登记 build/deploy 脚本；内容与部署流程不属于本轮 agent 核心架构，未深读。 |
| [`@opencode/protocol`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/protocol/package.json) | 类型化 API 契约 | 深读：检查 API 组装、session group 与 client API 导出；未枚举所有 API group 的端点。 |
| [`@opencode/schema`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/schema/package.json) | 共享 schema | 清单级：登记基础契约包；schema 全集与各消费点未深读。 |
| [`@opencode/script`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/script/package.json) | 脚本工具包 | 清单级：登记包和测试脚本；脚本实现未深读。 |
| [`@opencode/sdk`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/sdk/package.json) | 嵌入式/开发者 SDK 门面 | 入口/接口读取：检查 `src/index.ts` 导出及依赖分组；SDK 各 namespace 实现未深读。 |
| [`@opencode/server`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/server/package.json) | HTTP API 与 session handlers | 深读：检查 API 装配、routes 和 session handler；其他 route handler 未逐项深读。 |
| [`@opencode/session-ui`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/session-ui/package.json) | 会话 UI 组件 | 清单级：登记与 client/UI/util 的依赖及组件测试脚本；组件行为未深读。 |
| [`@opencode/simulation`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/simulation/package.json) | 仿真/测试支持 | 清单级：登记依赖 core/AI 等包的边界；仿真模型与测试场景未深读。 |
| [`@opencode/stats-app`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/stats/app/package.json) | Stats Web 应用 | 清单级：登记应用与 stats-core/UI 依赖；分析界面不属于本轮 agent 主路径，未深读。 |
| [`@opencode/stats-core`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/stats/core/package.json) | Stats 数据与迁移任务 | 清单级：登记数据库相关脚本；业务 schema 与数据处理未深读。 |
| [`@opencode/stats-server`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/stats/server/package.json) | Stats 服务入口 | 清单级：登记启动脚本与 stats-core 依赖；服务 handler 未深读。 |
| [`@opencode/storybook`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/storybook/package.json) | UI Storybook | 清单级：登记 storybook/build 脚本和 UI 依赖；stories 与展示层未深读。 |
| [`@opencode/theme`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/theme/package.json) | 主题包 | 清单级：登记构建与测试脚本；tokens 和主题解析实现未深读。 |
| [`@opencode/tui`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/tui/package.json) | 终端 UI | 入口/接口读取：检查 `src/index.tsx` 导出；终端组件与交互循环未深读。 |
| [`@opencode/ui`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/ui/package.json) | 共享 UI 包 | 清单级：登记构建、测试和生成脚本；组件实现未深读。 |
| [`@opencode/util`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/util/package.json) | 共享工具包 | 清单级：登记构建、测试和类型检查脚本；工具函数全集未深读。 |
| [`@opencode/web`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/web/package.json) | Astro Web 站点 | 清单级：登记框架/站点脚本；网站内容不属于本轮 agent 主路径，未深读。 |
| [`@opencode/changelog`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/services/changelog/package.json) | Changelog 服务 | 清单级：登记服务构建与部署脚本；服务实现未深读。 |
| [`@opencode/files`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/services/files/package.json) | 文件服务 | 清单级：登记服务构建与部署脚本；服务实现未深读。 |
| [`@opencode/update`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/services/update/package.json) | 更新服务 | 清单级：登记部署及数据库迁移脚本；更新协议未深读。 |
| [`@opencode/www`](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/services/www/package.json) | 官网服务 | 清单级：登记站点生成、校验和部署脚本；网站内容不属于本轮 agent 主路径，未深读。 |

矩阵所列 39 个 workspace 包与 F-083 清单按路径一一对应。另有 F-084 的 `github/package.json` 和 `sdks/vscode/package.json` 不匹配根 workspace glob，因此不计入这 39 个 workspace 包；本轮仅登记其边界，未深读其实现。
