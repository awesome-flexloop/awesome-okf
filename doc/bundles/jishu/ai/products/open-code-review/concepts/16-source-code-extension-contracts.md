---
type: "Wiki Tutorial"
title: "源码层扩展契约 — Provider、工具、输出与集成面"
description: "基于 commit 375f64cd 的源码静态阅读重建 OCR 的扩展契约——30 个 provider 注册表与四协议分发、6 个内置工具与参数修复链、JSON/SARIF/manifest 三套输出契约、MCP 客户端方向、查看器安全边界、遥测开关与六宿主插件；附与官方文档层的数值差异标注。"
tags: ["open-code-review", "source-code", "integration", "ai-code-review"]
sources:
  - id: ocr-src-commit
    resource: "https://github.com/alibaba/open-code-review/tree/375f64cd6f67a48a135da83cfcf59c52669a09cb"
    title: "alibaba/open-code-review 源码快照 commit 375f64cd"
  - id: ocr-src-facts
    resource: "/jishu/ai/products/open-code-review/references/source-code-facts.md"
    title: "源码层事实清单 F-101 ~ F-178"
  - id: ocr-src-layer
    resource: "/jishu/ai/products/open-code-review/references/source-code-layer.md"
    title: "源码层信源登记与覆盖矩阵"
generated: { by: process:seven-concepts, at: 2026-10-21 }
verified: { by: process:seven-concepts-v, at: 2026-10-21 }
---

# 源码层扩展契约 — Provider、工具、输出与集成面

本章是[官方集成契约](13-integration-contracts.md)的**源码侧对照**。第 13 章讲「四种使用形态的 LLM 归属与修复权限」，本章讲「commit `375f64cd` 的代码把这些契约具体实现成了什么」——provider 注册表、工具 schema、输出 JSON 字段、扩展面清单。

> **口径边界**：全部结论来自**静态源码阅读**，未运行 `ocr` 二进制、未调用任何 LLM、未发起任何网络请求。**本章 F-1xx 编号均指源码层（F-101 起），非文档层 F-001~F-100**。证据等级定义见[信源登记页](../references/source-code-layer.md#4-六主题覆盖矩阵)。

> **与本章配套的兄弟页**：[15 章](15-source-code-runtime-model.md) 讲「代码怎么跑」（运行时实现链）；[17 章](17-source-code-verification-playbook.md) 讲「怎么核验这些说法、怎么裁决口径冲突」；本章讲「provider / 工具 / 输出 / 扩展面的具体契约」。需要「怎么用 OCR」请先看[官方集成契约](13-integration-contracts.md)与[官方验证手册](14-verification-playbook.md)。

## 1. Provider：注册表是唯一事实来源

### 30 个 provider

`internal/llm/providers.go` 的注册表 `var registry = []Provider{...}` 当前条目数为 **30**（F-137），provider 级 `Name:` 字段精确取值（F-138）：

anthropic、bedrock、chatgpt、openai、openai-responses、openrouter、**edenai**、gemini、dashscope、dashscope-tokenplan、volcengine、deepseek、tencent-tokenhub、hy-tokenplan、iflytek、kimi、kimi-global、z-ai、**z-ai-coding**、mimo、minimax、minimax-cn、baidu-qianfan、**ollama-cloud**、novita、xai、**litellm**、siliconflow、siliconflow-cn、**mistral**

> **与官方文档层差 5 个**（加粗项）：文档站列 25 个（D-1）。这 5 个是**源码有、文档无**，不是文档有、源码无——方向与「文档过期」相反。

### Provider 记录的结构

字段包括 Name、DisplayName、Protocol、BaseURL、AuthHeader、EnvVar、AmbientAuth、ExternalAuth、RequiresStreaming、RejectsSamplingParams 与 Models（F-140）。**`RequiresStreaming` 与 `RejectsSamplingParams` 是行为开关而非展示字段**——前者决定客户端是否强制流式，后者决定是否剥离采样参数。

### 4 种协议 → 4 路分发

协议常量共 4 个：`anthropic`、`anthropic-bedrock`、`openai`、`openai-responses`（F-139）。客户端按解析出的协议四路分发到 Anthropic、Anthropic-Bedrock、OpenAI Responses 与 OpenAI Chat Completions 实现，**未知协议落到 openai**（F-141）。

> **「未知协议落到 openai」是兜底而非报错**——这意味着配置写错协议名不会失败，而是静默走 OpenAI 兼容通道。调试 provider 问题时，这是一个必须先排除的解释。

### 端点解析的四路优先级

顺序为：OCR 配置文件 → OCR 环境变量 → Claude Code 环境 → shell rc 文件（F-142）。OCR 侧环境变量共 8 个（F-143）：

`OCR_LLM_URL`、`OCR_LLM_TOKEN`、`OCR_LLM_MODEL`、`OCR_LLM_AUTH_HEADER`、`OCR_LLM_EXTRA_HEADERS`、`OCR_LLM_PROTOCOL`、`OCR_LLM_TIMEOUT`，另有开关 `OCR_USE_ANTHROPIC`。

**Claude Code 环境与 shell rc 文件在 OCR 自己的配置之后**——意味着 OCR 会**继承**已登录的 Claude Code 环境变量，这是「零配置能用」的来源，也是「配置不生效」最常见的排查盲区。

### 重试、超时与编码

| 维度 | 源码口径 |
|------|----------|
| 重试报告 schema | `ocr.llm-retry-report/v1`（F-144） |
| 错误分类枚举 | `rate_limited`、`overloaded`、`authentication`、`timeout`、`network`（F-144） |
| 状态码映射 | 429→rate_limited、529→overloaded、401/403→authentication、408/504→timeout、其余非 2xx→provider；`context.Canceled`→cancelled、`DeadlineExceeded`→timeout（F-145） |
| SDK 重试次数 | 统一 5 次（F-146） |
| 单请求默认超时 | **5 分钟**（`cfg.Timeout = 5 * time.Minute`，OpenAI 与 Anthropic 两个构造函数各一处）（F-147） |
| 其他独立超时 | Bedrock 配置加载 60 秒、响应头超时余量 30 秒（F-147） |
| token 计数 | tiktoken + 内嵌 BPE 数据（`//go:embed bpe_data/*.tiktoken`）；o1/o3/o4 系列用 `o200k_base`、默认 `cl100k_base`，加载失败回退为字节数除以 4（F-148） |
| 原始报文日志 | 环境变量 `OCR_RAW_LOGGING` 开启，取值 `1` 时启用（F-151） |

**「加载失败回退为字节数 ÷ 4」是一个精度降级点**：token 估算从精确切分变成粗略估算，体积门（F-121）的判定精度随之下降。

### ChatGPT 端点的强制约束

协议固定 `openai-responses`、要求流式、拒绝采样参数，且**不接受 url、protocol、api_key、auth_header 的覆盖**（F-149）。登录走 OAuth 授权码 + PKCE（S256），issuer 为 `https://auth.openai.com`，scope 含 `offline_access` 与 `chatgpt.tokens.use.direct`；凭据存放于 `~/.opencodereview/auth/chatgpt` 下的 `accounts.json`，目录权限 **0700**（F-150）。

## 2. 工具：6 个内置 + 参数修复链

### 工具集合

内置工具 6 个：`task_done`、`code_comment`、`file_read`、`file_find`、`file_read_diff`、`code_search`；另有 `unknown` **内部哨兵常量**（用于未识别工具名，**不注册为工具、不进入对外工具名集合**，故对外工具数仍为 6）（F-152）。

参数 schema 的权威来源是内嵌 `tools.json`（`//go:embed tools.json`），条目字段为 name、plan_task、main_task、definition，按阶段取用（F-153）：

| 工具 | plan 阶段 | main 阶段 | 参数 |
|------|:---------:|:---------:|------|
| `code_search` | ✅ | ✅ | search_text（必填）、file_patterns、case_sensitive、use_perl_regexp（F-156） |
| `file_read_diff` | ✅ | ✅ | path_array（必填）（F-156） |
| `file_find` | ✅ | ✅ | query_name（必填）、case_sensitive（F-156） |
| `code_comment` | ❌ | ✅ | comments 数组（F-154） |
| `file_read` | ❌ | ✅ | file_path（必填）、start_line、end_line（F-156） |
| `task_done` | ❌ | ✅ | state（DONE / FAILED，唯一必填）（F-155） |

**三个只读工具两阶段可用，三个写入/终结工具仅 main 阶段可用**——与[官方文档层](13-integration-contracts.md)的「plan 阶段仅后三个只读工具可用」一致，源码给出了逐工具的字段级依据。

### `code_comment` 的字段契约

参数含 comments 数组，数组项字段为 content、existing_code、suggestion_code、category、severity、path；**数组项必填** content、existing_code、category、severity、path；**外层必填** comments（F-154）。

### 参数规范化与自动修复

解析后对 path 做规范化（反斜杠转 `/`、路径清理、去前导 `/`），category 非法值归为 other，severity 非法值归为 low，path 或 content 为空的条目被丢弃（F-157）。

另有自动修复机制：对序列化字符串逐字节转义（非法反斜杠、非结构引号、控制字符）；修复函数在 `internal/tool/comment_args_repair.go`，修复成功后在主循环记录 warning `comment_args_repaired`（F-158）。

> **这是「容错即证据」的设计**：模型偶尔吐出非法 JSON 转义，OCR 不丢弃整轮结果，而是修好参数继续跑，并在 warnings 里留下痕迹。**这直接对应官方文档层 I-4 洞察里「显式信号」的设计意图**——warnings 数组不是日志装饰，是契约的一部分。

### 行号锚定的三级链路

先在本文件解析、再跨文件重定位、最后交由 LLM 重定位任务；**未锚定表示为起止行号均为 0**（F-159）。

### 工具自身的资源上限

| 工具 | 上限 | 超限行为 |
|------|------|---------|
| `file_read` | 单次 500 行 | 输出含 `IS_TRUNCATED` 与 `LINE_RANGE` 标记（F-166） |
| `code_search` | 100 条、超时 10 秒 | 以 `git --no-pager -c core.quotepath=false grep -n --no-color --max-count 101 -e` 执行（F-166） |
| `file_find` | 100、超时 10 秒 | 未命中输出 `// The file was not found`（F-166） |

`code_search` 用 `git grep` 而非自研索引——**代价是每次调用都付一次进程启动 + git 遍历**，收益是零索引维护成本与 gitignore 语义一致性。`--max-count 101` 多取一条用于判断是否被截断。

## 3. 输出契约：三套并行格式

### JSON 输出

CLI 的 JSON 输出**恒为 stdout 上的单个对象**，顶层字段含 status、llm、trace_id、message、summary、tool_calls、comments、groups、warnings、project_summary、resume、session_id、manifest、retry_report，输出带两空格缩进（F-160）。

三种「空」的消息互斥（F-161）：

| 情形 | status | message |
|------|--------|---------|
| 有评论 | — | — |
| 无评论产出 | — | `No comments generated. Looks good to me.` |
| 无可评审文件 | `skipped` | `No supported files changed.` |
| 失败 | `failed`（写 stderr） | — |

### 退出码只有两个值

集合为 `{0, 1}`：根命令返回错误时退出 1、否则 0；第二次 SIGINT 强制 `os.Exit(1)`；**review 场景仅在运行级失败或 manifest 终态为 failed 时返回非零，存在可用覆盖时退出 0**（F-162）。

> **「存在可用覆盖时退出 0」的含义**：部分文件评审成功、部分失败时，退出码仍是 0。CI 判定必须读 JSON 的 `manifest.terminal_state`（`partial`），不能只看退出码。

### SARIF 输出

格式 2.1.0，工具名 `OpenCodeReview`，规则集 8 条（bug、security、performance、maintainability、test、style、documentation、other）；category 映射为 ruleId，critical/high 映射为 error、medium 映射为 warning、low 映射为 note，指纹为 path、category 与 existing_code（或起始行）的 sha256，域前缀 `ocrFinding/v1`（F-163）。

**规则集 8 条与工具 schema 的 category 取值是同一套枚举**——SARIF 不是另起一套分类，而是把工具契约映射到 SARIF 词汇。

### 运行清单（manifest）

schema 标识 `ocr.run-manifest/v1`，字段含 run_id、parent_run_id、operation、terminal_state、repository、input、execution、coverage、run_failure、elapsed_ms；终态取 complete、partial、failed、skipped；**coverage 由 selected、completed、reused、failed、waived 五个集合构成**（F-164）。

五个集合是**集合而非计数**——`selected` 减去 `completed + waived` 就是未完成部分，`reused` 单独分离（复用既有会话结果的运行）。这让「覆盖率」可以从集合运算直接得出，不需要额外字段。

### 委托模式预览

JSON 的 schema 标识为 `1`，字段含 mode、repository、from、to、commit、merge_base、background、total_files、reviewable_count、excluded_count、total_insertions、total_deletions、reviewable_files、excluded_files；文件项含 path、status、insertions、deletions、exclude_reason（F-165）。

**委托模式预览是唯一同时暴露「总数 / 可评审数 / 被排除数」与逐文件 exclude_reason 的输出**——这是零 LLM 成本评估「哪些文件会被审」的唯一入口。

## 4. 扩展与集成面

### MCP：只有客户端，没有服务端

MCP 集成方向是**客户端**：OCR 作为 MCP client 连接外部 MCP server，传输形式为 stdio 子进程（客户端实现名 `open-code-review`）与 remote Streamable HTTP（F-167）。

配置键为 `mcp_servers`，条目字段含 type、command、args、env、url、headers、tools、setup；注册时按 allowedTools 过滤，**与内置工具同名的条目被跳过并告警 `conflicts with built-in tool`**（F-168）。

仓库内**没有 MCP server 实现**——`mcp.NewServer` 仅出现在测试文件中（F-169）。这意味着 OCR 不会「提供」MCP 服务给别的 agent，它只是「消费」外部 MCP 工具。

### CLI 子命令集合

version、review、scan、delegate、session、config、auth、llm、rules、viewer、completion（F-169），根命令 `Use: "ocr"`。

### 查看器：只读 + 三重安全边界

| 维度 | 源码口径 |
|------|---------|
| 监听地址 | 默认 `localhost:5483`（F-170） |
| 路由 | 仅 5 条 GET：静态资源、首页、仓库列表、仓库对比、单会话；非 GET 由 `ServeMux` 返回 405（F-170） |
| DNS rebinding 防护 | Host 白名单默认含 localhost、127.0.0.1、::1；非通配绑定的主机自动加入，通配绑定（空串、0.0.0.0、::）不加入；额外主机经 `OCR_VIEWER_ALLOWED_HOSTS` 逗号分隔追加；非白名单返回 403 `forbidden host`（F-171） |
| 响应头 | CSP（`default-src 'self'`、`frame-ancestors 'none'`、`form-action 'none'` 等）、`X-Content-Type-Options: nosniff`、`X-Frame-Options: DENY`、Referrer-Policy 与 Permissions-Policy（F-172） |

> **「通配绑定不加入白名单」是一道易被忽略的正确性细节**：当用户用 `--addr 0.0.0.0` 想从别的机器访问时，Host 校验会拒绝请求——除非显式配 `OCR_VIEWER_ALLOWED_HOSTS`。**这既是安全设计，也是用户会遇到的功能性阻断点。**

### 遥测：默认关闭，三层开关

由 `OCR_ENABLE_TELEMETRY=1` 开启；存在 `OTEL_EXPORTER_OTLP_ENDPOINT` 时 exporter 取 otlp，`OTEL_EXPORTER_OTLP_PROTOCOL` 默认 grpc；**配置优先级为 defaults < config.json < env**（F-173）。

span 名含 `llm.request` 与 `review.run`；指标名含 `ocr.review.duration_seconds`、`ocr.files_reviewed_total`、`ocr.comments_generated_total`、`ocr.llm.requests_total`、`ocr.llm.tokens_used`、`ocr.tool.calls_total`（F-174）。

**内容日志是独立开关**：`OCR_CONTENT_LOGGING` 与 `OCR_RAW_LOGGING` 分列——前者是遥测侧的载荷控制，后者是客户端侧的原始报文记录，两者的隐私边界不同（F-151、F-173）。

### scan 是独立路径，不是 review 的参数

scan 由独立的 `internal/scan` agent 实现，其 `RunManifest()` **恒返回 nil**（源码注释写明 scan 有意不在 v1 运行清单范围内）。scan 模板 `MAX_TOKENS` 为 58888、`MAX_COMPLETION_TOKENS` 为 16384、`MAX_TOOL_REQUEST_TIMES` 为 **60**；评审模板对应值为 200000、16384、**100**（F-175）。

> **这是 D-4 的来源**：文档层记 `MAX_TOOL_REQUEST_TIMES` 为单一值 100，源码层是 review 100 / scan 60 两套。**在 scan 路径上，manifest 恒为 nil——CI 不能对 scan 依赖 manifest.terminal_state。**

### ACP 适配器：独立 Go 模块

模块名 `github.com/alibaba/open-code-review/acp`，独立 `go.mod`（`go 1.23`，比主模块的 `go 1.26.9` 低），使用 stdio 传输，暴露 `/review` 与 `/scan` 两个命令，调用时恒定追加 `--format json --audience human --color never`；Extra 标志白名单 review 为 effort、no-filter、background、background-file，scan 为 batch、no-plan、no-dedup、no-summary、background（F-176，等级 L3，仅读 README 与 go.mod）。

### 六宿主插件

官方在 `plugins/open-code-review/` 下为六个宿主提供插件：Claude Code、Codex、Cursor、Kimi、**OpenCode**、QCA。

以 OpenCode 插件为例（`plugins/open-code-review/opencode/open-code-review.ts`）：注册 `ocr_review` 与 `ocr_health` 两个工具及 `ocr-review`、`ocr-health` 两个命令；基础参数为 `review --audience agent`，非预览模式追加 `--format json`；子进程默认超时 **15 分钟**、输出上限 **10 MiB**（F-177）。

> **`--audience agent` 是宿主集成的关键**：`--audience` 决定输出面向人还是面向 agent，宿主插件统一用 agent 模式 + JSON 格式，而 ACP 适配器用 `human`。**同一条命令在两种集成形态下走不同的输出分支**——这是[官方集成契约](13-integration-contracts.md)在源码层的具体体现。

### 文档站源码在仓库内

官方文档站的中文源文件随仓库一同版本控制：`pages/src/content/docs/zh/` 下共 18 个 Markdown 文件（含 `integrations/` 子目录 5 篇），每篇带 `title` / `sidebar.order` frontmatter（F-178）。

**这一事实把「文档 vs 实现」的验证从跨仓库比对变成了同 commit 内比对**——是[17-verification-playbook](17-source-code-verification-playbook.md)口径裁决方法的物理基础。

## 5. 与官方文档层的数值差异汇总

| 对象 | 文档层 | 源码层 | 差异 |
|------|-------|--------|------|
| 内置 provider | 25 个（F-049） | **30 个**（F-137） | D-1：源码多 edenai、z-ai-coding、ollama-cloud、litellm、mistral |
| `MAX_TOOL_REQUEST_TIMES` | 单一值 100（F-029） | **review 100 / scan 60**（F-175） | D-4：scan 路径单独一套 |
| MCP 方向 | 文档表述为「MCP 集成」 | **仅客户端**，仓库内无 MCP server 实现（F-169） | 源码明确 |
| 查看器默认地址 | localhost:5483（F-090） | localhost:5483（F-170） | 一致 |
| 遥测默认关闭 | 是（F-092） | 是，`OCR_ENABLE_TELEMETRY=1` 开启（F-173） | 一致 |
| 工具集 | 6 个（F-036） | 6 个 + `unknown` 哨兵（F-152） | 一致（哨兵为内部常量） |
| 退出码 | 0/1（F-068） | {0, 1}（F-162） | 一致 |

## 6. 本章的未覆盖边界

以下属[信源登记页](../references/source-code-layer.md#5-未读边界)列出的未读范围，本章不作结论：`internal/mcp/` 除 `client.go`、`provider.go` 外的文件；`internal/viewer/handler.go`、`store.go`；`internal/llm/client.go` L652–L1795 区段（流式响应解码逐行实现）；`acp/internal/` 全部 Go 源码；`extensions/frontend|idea|vscode` 实现源码；`examples/` 中 `codeup`、`bitbucket`、`gitflic` 三个示例的完整文件；全部 `*_test.go`。
