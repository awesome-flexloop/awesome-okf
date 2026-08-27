---
type: reference
scope: deepagents
name: backends
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: deepagents 后端系统——BackendProtocol、七种内置后端与沙箱执行协议
---

# 后端系统参考

后端是 Deep Agents 中文件存储、shell 执行和内存持久化的抽象层。所有后端实现 `BackendProtocol` 接口，中间件通过后端 API 访问文件，不直接接触文件系统。

## BackendProtocol

**模块路径**：`deepagents.backends.protocol.BackendProtocol`

定义所有后端必须遵循的统一文件操作接口，包括：读取、写入、编辑、删除、列出（ls）、glob 匹配、grep 搜索等操作。后端可将文件存储在不同位置（内存、磁盘、数据库、远程沙箱等）。

### 标准化错误码

`FileOperationError` 字面量类型定义四种 LLM 可理解和修复的错误：

| 错误码 | 含义 |
|---|---|
| `file_not_found` | 请求的文件不存在 |
| `permission_denied` | 操作被拒绝 |
| `is_directory` | 尝试将目录作为文件下载 |
| `invalid_path` | 路径语法错误或包含无效字符 |

### Grep 超时

- `DEFAULT_GREP_TIMEOUT = 15` 秒（单次同步 grep 阶段）
- `ASYNC_GREP_TIMEOUT = 35` 秒（异步 grep 包装器，为 ripgrep 超时加 Python 回退留出余量）

## SandboxBackendProtocol

后端若实现 `SandboxBackendProtocol` 则支持 shell 命令执行。`create_deep_agent()` 检测后端是否实现该协议：

- **实现了**：`execute` 工具可用，代理可运行 shell 命令
- **未实现**：`execute` 工具从模型请求中移除，shell 相关提示文本省略

这是运行时动态检测的，由 `FilesystemMiddleware` 在每次模型调用时判断。

## 内置后端

`deepagents.backends` 包公开以下后端（源码：`backends/__init__.py`）：

| 后端 | 用途 | 持久化 |
|---|---|---|
| `StateBackend` | 默认后端，线程作用域的内存存储 | 线程生命周期 |
| `FilesystemBackend` | 本地磁盘文件系统 | 跨会话持久 |
| `CompositeBackend` | 按路径路由到多个后端的组合后端 | 取决于子后端 |
| `StoreBackend` | 基于 LangGraph `BaseStore` 的持久化 | 跨会话持久 |
| `LocalShellBackend` | 本地 shell 执行后端，含 `DEFAULT_EXECUTE_TIMEOUT` | N/A |
| `LangSmithSandbox` | LangSmith 托管沙箱 | 平台管理 |
| `ContextHubBackend` | 上下文中心存储后端 | 取决于配置 |

### StateBackend（默认）

线程作用域的内存后端，文件在单次线程（thread）的多次调用间保持，但不跨线程持久。适合无状态部署和测试。使用 `StateBackend` 时，技能文件需通过 `invoke(files={...})` 传入。

### FilesystemBackend

将文件存储在本地磁盘的指定 `root_dir`。支持 POSIX 路径约定，处理平台特定的路径转换。生产环境中应配合沙箱或人工审批使用，因为它允许读写整个文件系统。

### CompositeBackend

按路径前缀将文件操作路由到不同后端。例如 `/outputs/` 路由到持久化存储，`/skills/` 路由到只读后端。`_route_for_path()` 函数确定给定路径应路由到哪个子后端。

### StoreBackend

基于 LangGraph `BaseStore` 的后端，支持命名空间工厂（`NamespaceFactory`）。适合需要跨线程、跨会话持久化文件的生产部署，需要传入 `store` 参数。

### LocalShellBackend

在本地机器上执行 shell 命令的后端，定义了 `DEFAULT_EXECUTE_TIMEOUT`。实现了 `SandboxBackendProtocol`，使 `execute` 工具可用。

## 文件下载/上传响应

`FileDownloadResponse` 和 `FileUploadResponse` 数据类支持批量操作的部分成功：

```python
@dataclass
class FileDownloadResponse:
    path: str
    content: bytes | None = None
    error: FileOperationError | str | None = None
```

每个结果独立报告成功或失败，错误使用标准化的 `FileOperationError` 字面量或后端特定的错误字符串。

## 后端与中间件的关系

```
create_deep_agent(backend=...)
    ↓
FilesystemMiddleware(backend=backend)     ← 文件工具通过后端访问
SummarizationMiddleware(backend=backend)  ← 卸载消息到后端
SkillsMiddleware(backend=backend)         ← 从后端加载技能
MemoryMiddleware(backend=backend)         ← 从后端加载 AGENTS.md
SubAgentMiddleware(backend=backend)       ← 子代理共享同一后端
```

所有中间件共享同一个后端实例，确保文件操作的一致性。子代理默认继承父代理的后端。

## 安全模型

Deep Agents 遵循"信任 LLM"模型——代理可以做其工具允许的任何事。安全边界在工具/沙箱层强制执行：

1. **后端能力**：非沙箱后端不暴露 `execute` 工具
2. **文件权限**：`FilesystemPermission` 规则在工具级别强制执行（allow/deny/interrupt）
3. **人工审批**：interrupt 模式通过 `HumanInTheLoopMiddleware` 暂停执行
4. **沙箱隔离**：`LangSmithSandbox` 在隔离环境中执行命令

不期望模型自我约束——所有边界都在代码层面强制执行。

## 相关概念

- 核心 API — `create_deep_agent(backend=)` 参数
- Todo 与上下文管理 — 摘要卸载如何使用后端
- lca-deepagents 变体 — 课程示例中的后端使用模式
