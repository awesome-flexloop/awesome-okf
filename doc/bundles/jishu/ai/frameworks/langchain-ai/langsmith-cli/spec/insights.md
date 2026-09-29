---
type: spec
scope: langsmith-cli
name: insights
version: "0.1.0"
source: https://github.com/langchain-ai/langsmith-cli
description: langsmith-cli 架构洞察——从源码中提炼的设计决策与关键机制
---

# langsmith-cli 架构洞察

## 1. 双后端透明切换：v1/v2 API 自动适配层

langsmith-cli 最核心的工程设计是**运行时自动检测并切换 LangSmith 查询后端**，对上层命令完全透明。

LangSmith 平台存在两代 run 查询 API：v1（传统 POST `/runs/query`）和 v2（SmithDB，基于游标的分页查询）。Cloud 部署使用 v2，自托管版本在 `0.16` 及以上才支持 v2。CLI 没有让用户通过 flag 选择，而是：

1. **首次查询时探测**：`Client.UseV2API(ctx)` 调用 `GET /info` 获取部署版本（`client.go:126-137`）。
2. **版本判定**：`useV2API(version)` 解析 semver——非发布版本（"dev"，即 Cloud）或 major≠0 或 minor≥16 时使用 v2（`client.go:142-151`）。
3. **结果缓存**：判定结果存入 `cachedUseV2API *bool`，单次 CLI 调用内只探测一次。
4. **参数翻译**：`toV2Params()` 将 v1 的 `RunQueryParams` 逐字段映射为 v2 的 `RunQueryV2Params`，包括 RunType 大写、Error→HasError、StartTime→MinStartTime 等重命名（`helpers.go:137-170`）。
5. **响应归一化**：`runV2ToSchema()` 将 v2 的 `Run` 结构转回 v1 的 `RunSchema`，处理 `ProjectID→SessionID`、`ParentRunIDs→ParentRunID`（取最后一个）、metadata 合并到 Extra 等差异（`helpers.go:228-276`）。
6. **统一入口**：所有命令通过 `queryRunsAuto()` 调用，无需感知后端版本（`helpers.go:124-133`）。

这种设计的价值在于：**命令代码只写一次**，输出管道（`extract.ExtractRun` → `output.PrintRunsTable`/`OutputJSON`）完全复用，同时兼容 Cloud 和旧版自托管部署。代价是维护一层字段映射，但避免了用户面对版本碎片化问题。

## 2. 分层认证与多 Profile 配置体系

CLI 的认证系统采用**flag → 环境变量 → 配置文件 → 默认值**的四级优先级链，并支持 API Key 和 OAuth 2.0 设备码流两种认证方式的共存。

**配置解析链**（`root.go:143-227`）：

```
--api-key flag
  → LANGSMITH_API_KEY env
  → profile OAuth access token（自动刷新）
  → profile API key
```

关键设计决策：

- **Profile 路由**：当显式选择 profile 时，使用 SDK 的 `WithProfile()` 选项而非手动设置 header，让 SDK 自身管理该 profile 的认证和租户上下文（`client.go:75-76`）。这确保显式选择能替换配置中的 `current_profile`，而非继承其 tenant/base URL。
- **OAuth 自动刷新**：`resolveClientOptions(refreshOAuth=true)` 在 access token 为空或即将过期（1 分钟 leeway）时，用 refresh token 静默获取新 token 并原子写回配置文件（`root.go:200-212`）。
- **安全写入**：配置文件通过临时文件 + `Chmod(0600)` + `Sync()` + `os.Rename` 原子替换，防止凭证损坏或泄露（`config.go:116-167`）。加载时检测 group/world 可读权限并警告（`config.go:88-104`）。
- **OAuth 发现安全**：RFC 8414 元数据发现后，`validateOAuthMetadata` 强制校验 issuer 与探测 URL 匹配、所有 endpoint 与 issuer 同源，防止设备码和 refresh token 被重定向到恶意主机（`oauth.go:173-194`）。

这种分层设计使 CLI 能同时服务三类用户：临时脚本（env var）、多环境开发者（named profiles）、企业 SSO（OAuth），且认证逻辑集中在 `resolveClientOptions` 一处，各子命令无需关心凭证来源。

## 3. Agent-First 的双模式输出与脚本化设计

从 README 和代码可以看出，langsmith-cli 的首要设计目标是**同时服务人类和 AI 编码代理**，这体现在输出系统和命令结构的多个层面：

**双格式输出**：
- `--format pretty`（默认）：使用 `tablewriter` 渲染表格、`treeprint` 渲染 trace 层级树，适合终端阅读。
- `--format json`：输出缩进 JSON，适合 `jq` 处理和代理消费。
- 所有命令统一通过 `GetFormat()` 判断格式，写操作（upload/create/delete）始终输出机器可读的 JSON 状态（如 `{"status":"uploaded","id":"...","name":"..."}`）。

**脚本化设计特征**：
- `SilenceUsage: true` 和 `SilenceErrors: true`：错误时不打印 Cobra 的 usage 文本，只输出干净的错误消息，避免污染脚本输出。
- 所有列表命令支持 `-o/--output` 写文件、`--limit` 控制数量、游标/offset 分页。
- 过滤器 DSL 构建器（`buildFilterDSL`）将命令行 flag 翻译为 LangSmith 服务端过滤表达式，同时支持 `--filter` 原生 DSL 透传，兼顾易用性和灵活性。
- `langsmith api` 子命令提供通用的认证 HTTP 客户端（类似 `gh api`），支持 `-F` 类型化字段、`-f` 原始字段、stdin body、`-i` 含响应头等，代理可直接调用任意 API 端点而无需等待 CLI 覆盖。

**代码提取器**：evaluator upload 命令内置 Python/JS 函数解析器，能从源文件中提取指定函数、重命名为 `perform_eval`/`performEval`、剥离 export 关键字、将箭头函数转换为函数声明（`evaluator.go:499-629`）。这使得用户可以直接上传包含多个函数的本地文件，CLI 自动提取目标函数，无需手动复制粘贴。

**结构化命令框架**：`internal/structured/` 包提供泛型 `Command[T]` 和 `Parent`，将命令的 Action（返回 `any` 数据）与 Render（PropertyList/Template 渲染）声明式分离，新命令只需关注业务逻辑和数据结构，框架自动处理 pretty/json 双模式输出。
