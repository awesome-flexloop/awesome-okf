---
type: spec
scope: openwork
name: facts
version: "0.1.0"
source: https://github.com/langchain-ai/openwork
description: openwork 源码事实验证清单——从 package.json、bin/cli.js、src/main/ 提取的可验证事实
---

# openwork 事实清单

## 项目元信息（package.json）

F-001: 文件 `package.json` 第2-4行，包名 `openwork`，版本 `0.1.0`，描述为 "A tactical agent interface for deepagentsjs"，作者 LangChain，许可证 MIT。

F-002: 文件 `package.json` 第13-15行，`bin` 字段声明 CLI 命令 `openwork` 指向 `./bin/cli.js`。`main` 字段指向 `./out/main/index.js`。要求 Node.js >= 18（第35-37行）。

F-003: 文件 `package.json` 第71行，核心依赖 `deepagents` 版本 `^1.5.1`；第52行依赖 `@langchain/langgraph` 版本 `^1.0.15`；第49-55行集成三家 LLM 提供商 SDK：`@langchain/anthropic`、`@langchain/openai`、`@langchain/google-genai`。

F-004: 文件 `package.json` 第80行，使用 `sql.js`（`^1.12.0`）作为纯 JavaScript SQLite 实现，无需原生编译；第83行使用 `zustand`（`^5.0.3`）做前端状态管理；第72行 `electron` 版本 `^43.4.0`。

## CLI 入口（bin/cli.js）

F-005: 文件 `bin/cli.js` 第16-20行，CLI 支持 `--version`/`-v` 标志，从 `package.json` 读取版本号输出 `openwork v${version}`。第23-33行支持 `--help`/`-h` 标志，输出用法说明。

F-006: 文件 `bin/cli.js` 第36-43行，CLI 通过 `require("electron")` 获取 Electron 路径，使用 `child_process.spawn` 启动 Electron 子进程，主进程入口为 `out/main/index.js`，`stdio: "inherit"` 直接继承父进程标准流。第53-54行将 SIGINT/SIGTERM 信号转发给子进程。

## Electron 主进程（src/main/index.ts）

F-007: 文件 `src/main/index.ts` 第13-27行，`createWindow()` 创建 1440×900 的 `BrowserWindow`，最小尺寸 1200×700，背景色 `#0D0D0F`，`titleBarStyle: "hiddenInset"`，preload 脚本路径为 `../preload/index.js`，`sandbox: false`。

F-008: 文件 `src/main/index.ts` 第82-87行，应用就绪后依次执行 `initializeDatabase()`、`registerAgentHandlers(ipcMain)`、`registerThreadHandlers(ipcMain)`、`registerModelHandlers(ipcMain)`，然后创建窗口。

## Agent 运行时（src/main/agent/runtime.ts）

F-009: 文件 `src/main/agent/runtime.ts` 第122-179行，`createAgentRuntime(options)` 函数接收 `{ threadId, modelId?, workspacePath }`，调用 `createDeepAgent()` 创建深度代理，配置项包括 `model`、`checkpointer`（SqlJsSaver）、`backend`（LocalSandbox）、`systemPrompt`、`filesystemSystemPrompt`、`interruptOn: { execute: true }`（所有 shell 命令需人工审批）。

F-010: 文件 `src/main/agent/runtime.ts` 第62-108行，`getModelInstance(modelId?)` 根据模型 ID 前缀选择提供商：`claude` → `ChatAnthropic`，`gpt`/`o1`/`o3`/`o4` → `ChatOpenAI`，`gemini` → `ChatGoogleGenerativeAI`。未匹配时返回模型字符串交由 deepagents 处理。API 密钥从 `getApiKey(provider)` 获取。

F-011: 文件 `src/main/agent/runtime.ts` 第40-51行，使用模块级 `Map<string, SqlJsSaver>` 缓存每线程的 checkpointer 实例，`getCheckpointer(threadId)` 懒加载并初始化，数据库路径由 `getThreadCheckpointPath(threadId)` 生成。

## LocalSandbox（src/main/agent/local-sandbox.ts）

F-012: 文件 `src/main/agent/local-sandbox.ts` 第53行，`LocalSandbox` 类继承自 `deepagents` 的 `FilesystemBackend` 并实现 `SandboxBackendProtocol`。第90-220行，`execute(command)` 方法使用 `child_process.spawn` 在工作目录执行 shell 命令，Windows 用 `cmd.exe /c`，Unix 用 `/bin/sh -c`。

F-013: 文件 `src/main/agent/local-sandbox.ts` 第70-71行，默认命令超时 120,000ms（2分钟），最大输出 100,000 字节（~100KB）。第117-129行超时后先发 SIGTERM，1秒后发 SIGKILL。第153-161行 stderr 每行添加 `[stderr]` 前缀。

## 系统提示词（src/main/agent/system-prompt.ts）

F-014: 文件 `src/main/agent/system-prompt.ts` 第6行导出 `BASE_SYSTEM_PROMPT` 常量，规定代理行为：简洁直接（4行以内）、主动但不越界、遵循代码约定（不添加注释除非要求）、使用 `write_todos` 管理复杂任务、文件读取分页（>500行先读100行）、子代理委派策略、代码引用格式 `file_path:line_number`。

F-015: 文件 `src/main/agent/system-prompt.ts` 第90-98行，HITL 工具审批规则：工具调用被拒绝后立即接受、不重试相同命令、建议替代方案。第76行明确所有 `execute` 命令需用户批准。

## IPC 处理器（src/main/ipc/）

F-016: 文件 `src/main/ipc/agent.ts` 第16行，`registerAgentHandlers(ipcMain)` 注册四个 IPC 通道：`agent:invoke`（发起对话）、`agent:resume`（中断后恢复）、`agent:interrupt`（HITL 决策响应）、`agent:cancel`（取消运行）。第14行使用 `Map<string, AbortController>` 跟踪活跃运行。

F-017: 文件 `src/main/ipc/agent.ts` 第77-85行，代理流式调用配置 `streamMode: ["messages", "values"]`（同时获取 token 流和完整状态），`recursionLimit: 1000`，通过 `AbortController.signal` 支持取消。第95-99行将流事件通过 `agent:stream:${threadId}` 通道发送给渲染进程。

F-018: 文件 `src/main/ipc/models.ts` 第23-27行，配置三个 LLM 提供商：Anthropic、OpenAI、Google（ollama 在类型中声明但未配置）。第30-205行声明 20+ 个可用模型，默认模型为 `claude-sonnet-4-5-20250929`（第219行）。

F-019: 文件 `src/main/ipc/models.ts` 第228-240行，API 密钥通过 `setApiKey`/`getApiKey`/`deleteApiKey` 管理；第432-436行和第486-490行，文件读取操作包含路径遍历安全检查：`resolvedPath.startsWith(resolvedWorkspace)` 防止访问工作区外文件。

F-020: 文件 `src/main/ipc/threads.ts` 第46-61行，`threads:create` 使用 `uuid` v4 生成线程 ID，标题默认格式 `Thread ${date}`。第88-110行删除线程时同步关闭 checkpointer 并删除检查点数据库文件。第113-129行 `threads:history` 返回最近 50 个检查点。

## 存储与持久化（src/main/storage.ts, src/main/db/index.ts, src/main/checkpointer/）

F-021: 文件 `src/main/storage.ts` 第6行，所有数据存储在 `~/.openwork/` 目录下：`openwork.sqlite`（应用数据）、`.env`（API 密钥）、`threads/{threadId}.sqlite`（每线程 LangGraph 检查点）。

F-022: 文件 `src/main/db/index.ts` 第73-108行，应用数据库包含三张表：`threads`（线程元数据）、`runs`（运行记录）、`assistants`（助手配置）。第13-29行使用 100ms 防抖写入磁盘。

F-023: 文件 `src/main/checkpointer/sqljs-saver.ts` 第45行，`SqlJsSaver` 继承 `BaseCheckpointSaver`，使用 sql.js 纯 JS SQLite。第69行数据库文件大小限制 100MB，超出时备份旧文件并创建新库。第155-161行防抖 100ms 写入磁盘。实现了 `getTuple`、`list`、`put`、`putWrites`、`deleteThread`、`close` 方法。

## 类型定义（src/main/types.ts, src/types.ts）

F-024: 文件 `src/main/types.ts` 第2行，`ThreadStatus` 类型为 `"idle" | "busy" | "interrupted" | "error"`；第70行 `RunStatus` 为 `"pending" | "running" | "error" | "success" | "interrupted"`；第83行 `ProviderId` 为 `"anthropic" | "openai" | "google" | "ollama"`。

F-025: 文件 `src/main/types.ts` 第112-122行，`StreamEvent` 联合类型包含 10 种事件：`message`、`tool_call`、`tool_result`、`interrupt`、`token`、`todos`、`workspace`、`subagents`、`done`、`error`。第160-165行 `HITLDecision` 支持 `"approve" | "reject" | "edit"` 三种决策。

## 工作区监听（src/main/services/workspace-watcher.ts）

F-026: 文件 `src/main/services/workspace-watcher.ts` 第17行，`startWatching(threadId, workspacePath)` 使用 `fs.watch` 的 `recursive: true` 选项递归监听目录变化。第11行防抖延迟 500ms。第39行跳过隐藏文件和 `node_modules` 目录。第106行变化后向所有窗口发送 `workspace:files-changed` 事件。
