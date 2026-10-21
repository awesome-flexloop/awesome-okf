---
type: "Wiki Tutorial"
title: "官方文档事实清单（编号事实 F-001~F-100）"
description: "Open Code Review 官方文档站 open-codereview.ai 全部子页面的客观事实采集清单——按身份安装、架构流水线、规则过滤、LLM Provider、CLI 输出契约、集成模式、可观测性安全、基准效果八组编号，每条附官方来源编号，无因果推断词。"
tags: ["open-code-review", "official-docs", "fact-ledger", "ai-code-review"]
sources:
  - id: ocr-docs-root
    resource: "https://open-codereview.ai/"
    title: "Open Code Review 官方文档站首页"
  - id: ocr-docs-architecture
    resource: "https://open-codereview.ai/docs/architecture/"
    title: "官方文档 · 架构（Architecture）"
  - id: ocr-docs-review-rules
    resource: "https://open-codereview.ai/docs/review-rules/"
    title: "官方文档 · 评审规则（Review Rules）"
  - id: ocr-docs-configuration
    resource: "https://open-codereview.ai/docs/configuration/"
    title: "官方文档 · 配置（Configuration）"
  - id: ocr-docs-cli-reference
    resource: "https://open-codereview.ai/docs/cli-reference/"
    title: "官方文档 · CLI 参考（CLI Reference）"
  - id: ocr-docs-tools
    resource: "https://open-codereview.ai/docs/tools/"
    title: "官方文档 · 工具（Tools）"
  - id: ocr-docs-faq
    resource: "https://open-codereview.ai/docs/faq/"
    title: "官方文档 · FAQ"
  - id: ocr-docs-viewer
    resource: "https://open-codereview.ai/docs/viewer/"
    title: "官方文档 · 会话查看器（Viewer）"
  - id: ocr-docs-telemetry
    resource: "https://open-codereview.ai/docs/telemetry/"
    title: "官方文档 · 遥测（Telemetry）"
  - id: ocr-docs-agent-skill
    resource: "https://open-codereview.ai/docs/agent-skill/"
    title: "官方文档 · Agent Skill 集成"
  - id: ocr-docs-claude-code
    resource: "https://open-codereview.ai/docs/claude-code/"
    title: "官方文档 · Claude Code 集成"
  - id: ocr-docs-delegate
    resource: "https://open-codereview.ai/docs/delegate/"
    title: "官方文档 · 委托模式（Delegate）"
  - id: ocr-docs-chatgpt-preview
    resource: "https://open-codereview.ai/docs/chatgpt-preview/"
    title: "官方文档 · ChatGPT 登录预览版"
  - id: ocr-docs-installation
    resource: "https://open-codereview.ai/docs/installation/"
    title: "官方文档 · 安装（Installation）"
  - id: ocr-github-repo
    resource: "https://github.com/alibaba/open-code-review"
    title: "官方仓库 alibaba/open-code-review"
generated: { by: process:seven-concepts, at: 2026-10-21 }
verified: { by: process:seven-concepts-v, at: 2026-10-21 }
---

# 官方文档事实清单（F-001 ~ F-100）

> **采集范围**：open-codereview.ai 全部子页面（首页 + 快速开始 + 安装 + 配置 + CLI 参考 + 评审规则 + 架构 + 工具 + FAQ + 查看器 + 遥测 + Agent Skill + Claude Code + 委托模式 + ChatGPT 预览版），采集日期 2026-10-21。
>
> **口径纪律**：本清单只记录官方页面上的客观陈述，不含因果推断词（「因为／所以／导致／因此／由于／使得」）。每条事实后标注来源编号，来源对照表见文末。既有 bundle 内基于二手文章推导的数值与官方口径的冲突记录在[官方文档勘误表](official-doc-corrections.md)。

## 来源编号对照

| 编号 | 页面 | 地址 |
|------|------|------|
| S1 | 首页 | <https://open-codereview.ai/> |
| S2 | 快速开始 | <https://open-codereview.ai/docs/> |
| S3 | 安装 | <https://open-codereview.ai/docs/installation/> |
| S4 | 配置 | <https://open-codereview.ai/docs/configuration/> |
| S5 | CLI 参考 | <https://open-codereview.ai/docs/cli-reference/> |
| S6 | 评审规则 | <https://open-codereview.ai/docs/review-rules/> |
| S7 | 架构 | <https://open-codereview.ai/docs/architecture/> |
| S8 | 工具 | <https://open-codereview.ai/docs/tools/> |
| S9 | FAQ | <https://open-codereview.ai/docs/faq/> |
| S10 | 查看器 | <https://open-codereview.ai/docs/viewer/> |
| S11 | 遥测 | <https://open-codereview.ai/docs/telemetry/> |
| S12 | Agent Skill | <https://open-codereview.ai/docs/agent-skill/> |
| S13 | Claude Code 集成 | <https://open-codereview.ai/docs/claude-code/> |
| S14 | 委托模式 | <https://open-codereview.ai/docs/delegate/> |
| S15 | ChatGPT 预览版 | <https://open-codereview.ai/docs/chatgpt-preview/> |
| S16 | 官方仓库 | <https://github.com/alibaba/open-code-review> |

## A. 身份、安装与状态目录

- **F-001** Open Code Review（下称 OCR）由 Alibaba Group 开源，npm 包名为 `@alibaba-group/open-code-review`，可执行文件名为 `ocr`。［S1 S3］
- **F-002** OCR 以 Go 实现；官方提供 npm、Homebrew、curl-sh、PowerShell、GitHub Release 与源码构建六条安装路径。［S3］
- **F-003** 官方列出的运行前置条件为 Git ≥ 2.41、Node.js ≥ 18；LLM API key 在委托模式下不列为必需。［S2］
- **F-004** OCR 的状态目录为 `~/.opencodereview/`，内含 `config.json`、`rule.json`、`sessions/<encoded-repo-path>/<session-id>.jsonl` 与三个更新检查文件。［S3 S9］
- **F-005** 会话目录名对仓库路径的编码规则为：`/` 与 `\` 替换为 `-`，`:` 替换为 `_`（示例 `/Users/foo/my-repo` → `Users-foo-my-repo`）。［S9］
- **F-006** 官方仓库 `alibaba/open-code-review` 的根目录含 13 个 Markdown 文件，`docs/` 目录不在该仓库内；open-codereview.ai 为独立文档前端。［S16］
- **F-007** 官方提供 `OCR_UPDATE_INTERVAL` 与 `OCR_NO_UPDATE` 两个环境变量控制更新检查。［S3］

## B. 架构与审查流水线

- **F-008** 编排代码位于 `internal/agent/` 包，主要文件为 `agent.go`（分发与按组编排）、`grouping.go`（语义文件分组）、`selection.go`（文件过滤）、`preview.go`（`--preview` 报告）、`util.go`；工具调用循环与记忆压缩位于相邻的 `internal/llmloop/` 包。［S7］
- **F-009** 流水线顶部入口为 `Agent.Run`，按组扇出入口为 `Agent.dispatchSubtasks`。［S7］
- **F-010** diff provider 由 `internal/diff/git.go` 的 `Provider` 结构实现，其未导出字段 `mode`（`Mode` 整数枚举）对应三种模式。［S7］
- **F-011** Workspace 模式（无参数）返回 staged + unstaged + untracked 变更；Commit 模式（`--commit <sha>` / `-c`）等价于 `<sha>^..<sha>` diff；Range 模式（`--from <a> --to <b>`）等价于 `merge-base(a,b)..b`。［S7］
- **F-012** 每个 diff 记录 old/new path、old/new hunk、插入与删除计数、二进制标志与重命名检测；`DiffContextLines` 固定为 3。［S7］
- **F-013** untracked 文件从磁盘读取，按整文件新增处理。［S7］
- **F-014** 文件过滤函数 `whyExcluded`（`internal/agent/selection.go`）返回四类原因之一：`binary`、`user_exclude`、`unsupported_ext`、`default_path`；文件被保留时返回空值。［S7］
- **F-015** 过滤门按固定顺序执行：`binary` → `user_exclude` → `user_include` → `unsupported_ext` → `default_path`。［S7］
- **F-016** `user_include` 命中时立即保留文件，并跳过 `unsupported_ext` 与 `default_path` 两道门。［S7］
- **F-017** `default_path` 匹配内置测试文件排除模式，样例包括 `**/*_test.go`、`**/*.test.{js,jsx,ts,tsx}`、`**/__tests__/**`、`**/*_test.py`、`**/*_spec.rb`、`**/*.test.ets`，每个模式以 `**/` 为根前缀。［S7］
- **F-018** `deleted` 与 `too_large` 两类排除由 `selectFiles` 在各门之后施加；`too_large` 的判定标准为该文件 diff 本身超过**本次运行生效的** `max_tokens` 取值的 80%（`ocr review` 默认 200000、`ocr scan` 为 58888），阈值随 `--max-tokens` / `max_tokens` 配置变动。［S7 S9 S5］
- **F-019** 噪声目录（`vendor/`、`node_modules/`、`target/` 等）由 diff provider 层的 `providerDirIgnoreDirs` 列表剔除；preview 将这类文件报告为 `provider_directory`，include 规则不改变该结果。［S7］
- **F-020** `providerDirIgnoreDirs` 按路径前缀匹配，只覆盖仓库根目录下的同名目录；嵌套同名目录（如 `api/vendor/pkg/x.go`）进入 per-file 过滤并按 `default_path` 排除，且可被 include 规则重新纳入。［S7］
- **F-021** 语义分组由单次 `GROUPING_TASK` LLM 调用完成，输入仅含文件元数据（路径、状态、`+`/`-` 行数），不含 diff 内容。［S7］
- **F-022** 每个文件恰好归属一个分组，单组文件数上限 `maxFilesPerGroup = 10`；分组调用失败、返回空或仅含 1 个文件时退化为每文件一组。［S7］
- **F-023** 一组 diff 的合计 token 超限时，`enforceGroupTokenBudget` 将该组拆为单文件组。［S7］
- **F-024** 每个文件组启动一个子 agent，运行于独立 goroutine，受 `--concurrency`（默认 8）约束，并持有独立的 LLM 消息缓冲区。［S7 S5］
- **F-025** plan 阶段的触发条件为：组内单文件变更行数 ≥ `PLAN_MODE_LINE_THRESHOLD`（50），或组内文件数 ≥ 2 且合计变更行数 ≥ `PLAN_MODE_GROUP_LINE_THRESHOLD`（100）。［S7 S9］
- **F-026** plan 阶段为单次 `PLAN_TASK` 调用，不发送 Tools 字段；只读工具子集 `code_search`、`file_read_diff`、`file_find`（`tools.json` 中 `plan_task` 标志为 true 的三个）以纯文本经 `{{plan_tools}}` 占位符嵌入，返回清单经 `{{plan_guidance}}` 传入 main prompt。［S7］
- **F-027** main 循环最多重复 `MAX_REVIEW_ROUNDS` 轮：`low` = 1 轮，`medium` = 2 轮（默认），`high` = 3 轮。［S4 S7］
- **F-028** 第 2 轮起剥离 plan 结果，并把上一轮已确认的评论作为「已发现」上下文回传给模型。［S7］
- **F-029** main 循环的工具调用轮次上限为 `MAX_TOOL_REQUEST_TIMES`（模板默认 100）。［S7 S9］
- **F-030** main 循环的五个退出条件为：调用 `task_done`；`MAX_TOOL_REQUEST_TIMES` 耗尽；连续 3 轮无有效工具结果（`maxConsecutiveEmptyRounds = 3`）；context 被取消；`addNextMessage` 返回 false。［S7］
- **F-031** 六个 prompt 模板位于 `internal/config/template/task_template.json`：`GROUPING_TASK`、`PLAN_TASK`、`MAIN_TASK`、`MEMORY_COMPRESSION_TASK`、`REVIEW_FILTER_TASK`、`RE_LOCATION_TASK`。［S7］
- **F-032** 记忆压缩阈值：`MAX_TOKENS` 的 60% 启动异步后台压缩（`tokenSoftThreshold`），80% 在发送下一请求前同步压缩（`tokenWarningThreshold`）。［S7］
- **F-033** 压缩后的消息结构为 `frozen[2] + compressed_user_msg + active`；压缩摘要以 `<previous_review_summary>` 标签包裹并追加到原始 user 消息。［S7］
- **F-034** 评论处理五步为：行解析（`existing_code` 用滑动窗口算法与 diff 匹配以计算 `start_line` / `end_line`，失败时两者为 0）→ 可选 `RE_LOCATION_TASK` 重定位 → `REVIEW_FILTER_TASK` 对照 diff 移除可证明为错的评论 → 第二轮行解析（`Agent.Run` 返回后由 `cmd/opencodereview/review_cmd.go` 重跑 `diff.ResolveLineNumbers`）→ 渲染。［S7］
- **F-035** token 预算守卫为 fail-fast 检查 `countMessagesTokens(messages) > MaxTokens * 4 / 5`（80%），超限时记录 `token_threshold_exceeded` 警告并跳过该组。［S7］
- **F-036** 工具集共六个：`task_done`、`code_comment`、`file_read`、`file_read_diff`、`file_find`、`code_search`；plan 阶段仅 `file_read_diff`、`file_find`、`code_search` 三个只读工具可用。［S8 S7］
- **F-037** 首页把架构描述为「确定性工程（任务拆分、文件过滤、行号定位、规则路由、异步调度）」与「LLM Agent 推理（风险检测、上下文探索、问题分类）」的混合体。［S1］
- **F-038** 首页声明评论定位由独立的行级定位模块配合三级渐进式 LLM 策略完成，并设有独立的反射模块拦截幻觉与知识漂移。［S1］
- **F-039** 首页列出的三类目标用户为 Individual Developers、Platform Teams、ML Researchers；面向 ML 场景的定位是把 OCR 作为 RL 训练流水线中的代码质量验证器，提供奖励信号。［S1］

## C. 规则系统与文件过滤

- **F-040** 规则来源四层优先级：`--rule` 参数 > `<repoDir>/.opencodereview/rule.json` > `~/.opencodereview/rule.json` > 内嵌 `system_rules.json`。［S6］
- **F-041** 高优先级层的规则文件不存在时被静默跳过；系统层随二进制发布，始终存在。［S6］
- **F-042** 规则文件字段为 `include`（数组）、`exclude`（数组）、`rules`（数组）；`rules` 条目字段为 `path` 与 `rule`，可选第三字段 `merge_system_rule`（默认 `false`）。［S6］
- **F-043** `merge_system_rule` 为 `false` 时匹配条目替换该文件的内置系统规则，为 `true` 时用户规则与系统规则合并。［S6］
- **F-044** glob 匹配由 `bmatcuk/doublestar/v4` 实现，支持 `{ts,tsx}` 花括号；`{ts, tsx}` 中的空格使 `tsx` 静默不匹配。［S6 S9］
- **F-045** 同一 `rules` 数组中首条匹配的 glob 生效。［S6 S9］
- **F-046** `ocr rules check <file-path>` 输出匹配的来源层、glob 模式与规则正文。［S6 S9］
- **F-047** 首页声明内置规则覆盖 40+ 语言与文件类型，含 NPE、线程安全、XSS、SQL 注入等内置检查项。［S1］

## D. LLM 端点与 Provider

- **F-048** 内置 provider 共 25 个，协议字段取值为 `anthropic`、`anthropic-bedrock`、`openai`、`openai-responses` 四种。［S4］
- **F-049** 内置 provider 清单为：anthropic、bedrock、chatgpt、openai、openai-responses、openrouter、gemini、dashscope、dashscope-tokenplan、volcengine、deepseek、tencent-tokenhub、hy-tokenplan、iflytek、kimi、kimi-global、z-ai、mimo、minimax、minimax-cn、baidu-qianfan、siliconflow、siliconflow-cn、novita、xai。［S4］
- **F-050** 内置 provider 中 21 个使用 `openai` 协议，1 个使用 `anthropic`，1 个使用 `anthropic-bedrock`，2 个使用 `openai-responses`。［S4］
- **F-051** provider 的 API key 优先级为静态 `providers.<name>.api_key` > `api_key_cmd` 命令输出 > 该 provider 对应的环境变量；静态 key 与 `api_key_cmd` 同时设置时忽略命令并打印警告。［S4］
- **F-052** `api_key_cmd` 在 Windows 上经 `cmd.exe` 执行而非 `sh`；`%VAR%` 与 `^` 是 cmd.exe 元字符，`$VAR` 展开与 `\` 转义不适用；带引号的参数原样传递。［S4］
- **F-053** `config.json` 中的 `api_key_cmd` 会被当作 shell 命令执行；OCR 写入该文件时使用 `0600` 权限。［S4］
- **F-054** `retry_codes` 为整数数组，可配置于 `llm.retry_codes` 或 `custom_providers.<name>.retry_codes`，用于把限流等非标准 4xx（如 403、400）纳入 SDK 现有重试机制。［S4］
- **F-055** `max_tokens` 只约束提示词；模型输出上限由 `MAX_COMPLETION_TOKENS`（默认 16384）单独控制；`--max-tokens-budget` 与之相互独立。［S4 S5 S9］
- **F-056** `effort` 配置项决定每个子任务的 main 循环轮数，优先级为 `--effort` 参数 > 已保存的 `effort` > 默认 `medium`。［S4］
- **F-057** 端点解析按顺序取第一个完整的 `(URL, token, model)` 三元组，环境变量优先于配置文件。［S9］
- **F-058** `ocr llm test` 用于验证端点连通性；401 / 403 对应 token 缺少 scope、已过期或厂商不匹配。［S9］
- **F-059** Anthropic 协议要求 URL 以 `/v1/messages` 结尾且 `use_anthropic=true`；OpenAI 兼容协议要求 URL 以 `/v1/chat/completions` 结尾且 `use_anthropic=false`。［S9］
- **F-060** `chatgpt` provider 使用 OpenAI 公开 Responses API，凭证来自 `ocr auth login` 创建的 ChatGPT 登录；凭证库位于 `~/.opencodereview/auth/chatgpt/accounts.json`，安装主机 ID 存于同目录 `host.json`，两者均采用原子替换写入。［S15］
- **F-061** `chatgpt` provider 的 OAuth 范围为 `openid`、`profile`、`email`、`offline_access`、`resource.invoke`、`chatgpt.tokens.use.direct`；首次注册发送 `agent_name_hint=OpenCodeReview`；登录只监听 `127.0.0.1`，不支持设备码登录。［S15］
- **F-062** `chatgpt` provider 只向 `https://api.openai.com/v1/responses` 发送请求，使用流式传输与 `store: false`；`extra_body` 仅接受 `reasoning`、`text`、`prompt_cache_key` 三个字段。［S15］
- **F-063** `extra_body` 中的推理强度是 API 参数，与 review 的 `--effort` 参数（控制评审轮次与工具预算）分属两层。［S15］

## E. CLI 参数与输出契约

- **F-064** `ocr review` 参数默认值：`--audience` 为 `human`；`--concurrency` 为 8；`--timeout` 为 15 分钟（按 effort 线性缩放为 15 / 30 / 45）；`--max-tokens` 为 200000；`--max-tools` 为模板默认 100；`--max-git-procs` 为 16；`--max-tokens-budget` 为 0（无限制）；`--effort` 为 `medium`。［S5］
- **F-065** `--max-tools` 只能上调：0 使用模板默认 100，1–49 先被上调到 50，解析后的值只在大于模板默认值时生效。［S5 S9］
- **F-066** 单次请求超时独立于 `--timeout`，由 `OCR_LLM_TIMEOUT` 或 provider 的 `timeout_sec` 设置，单位秒，默认 300。［S5］
- **F-067** `--audience human` 流式输出进度行（`--format` 为 json / sarif 时进度行输出到 stderr，使 stdout 保持为单个可解析文档）；`--audience agent` 完全抑制进度行，只打印最终摘要或 JSON。［S5 S9］
- **F-068** 退出码只有两种：0 表示评审完成（可能零评论，可能带非致命警告），1 表示致命错误（参数错误、无法解析 LLM 端点、全部 per-file 子 agent 失败等），错误文本打印到 stderr。［S5］
- **F-069** 非致命警告（单个子 agent 失败、某文件超 token 阈值等）内联打印，并在 JSON 模式下进入 `warnings` 数组。［S5］
- **F-070** `ocr review --format json` 始终向 stdout 写出恰好一个 JSON 对象，不输出裸数组；`summary.files_reviewed` 表示实际评审文件数。［S5 S9］
- **F-071** 带 manifest 的输出用 `manifest.terminal_state` 表示终态；无合格文件的路径下 `status` 为 `skipped`，`message` 为 `Review skipped: no items were selected.`，`manifest` 各数组为空。［S9］
- **F-072** manifest-less 的无文件路径省略 `summary` 与 `manifest`，`message` 为 `No supported files changed.`，`tool_calls` 始终存在；`ocr scan` 始终走 manifest-less 路径。［S9］
- **F-073** `ocr scan` 不依赖 Git diff，直接读取工作树中每个文件的当前内容；未传入 `--path` 时扫描整个仓库；`ocr scan` 使用的 `max_tokens` 为 58888。［S5 S9］
- **F-074** `ocr review --preview` 不消耗 LLM token，输出每个候选文件被保留或丢弃的原因；preview 报告的原因取值包括 `binary`、`user_exclude`、`unsupported_ext`、`default_path`、`provider_directory`、`deleted`、`too_large`。［S6 S9］
- **F-075** `ocr review` 对当前目录运行 `git diff`（以及对 untracked 文件运行 `git ls-files`），非 Git 工作树下提前退出；可用 `--repo /path/to/repo` 指定仓库根。［S9］

## F. 集成模式

- **F-076** 官方文档给出的集成形态为 Agent Skill、Claude Code Command、委托模式三种；委托模式由宿主 Agent 调用 LLM，另两种由 OCR 调用 LLM。［S14］
- **F-077** 委托模式子命令为 `ocr delegate preview` 与 `ocr delegate rule <path...>`；委托模式在 OCR 端不调用任何 LLM，无需配置模型或 API Key。［S14］
- **F-078** `ocr delegate preview` 输出 mode、ref 元数据（from、to、commit、merge_base）、可审查文件列表与已排除文件及原因。［S14］
- **F-079** 委托模式下的 Git 调用统一使用 `git --no-pager`，并附加 `--no-ext-diff --no-textconv --no-color`。［S14］
- **F-080** 委托模式报告字段为 `total_files`、`reviewed_files`、`skipped_files`、`coverage_rate`。［S14］
- **F-081** 委托模式的严重度分级为 Critical/High（始终报告）、Medium（附带上下文报告）、Low（静默丢弃，除非确有价值）。［S14］
- **F-082** Agent Skill 安装命令为 `npx skills add alibaba/open-code-review --skill open-code-review`；技能清单位于仓库 `skills/open-code-review/SKILL.md`。［S12］
- **F-083** Agent Skill 的七步流程为：前置检查（`which ocr` + `ocr llm test`）、CLI 缺失时自动执行 `npm install -g`、无 LLM 配置时停止并询问用户、提取 `--background` 业务上下文、运行 `ocr review --audience agent --background`、按 High/Medium/Low 分类、按需修复。［S12］
- **F-084** Agent Skill 在 `ocr llm test` 失败时不编造凭证，向用户展示环境变量与 `ocr config set` 两种方式并等待 API key。［S12］
- **F-085** Agent Skill 首次运行时会自行安装 `ocr` CLI（前提是二进制不在 `PATH` 上），且不提示用户。［S12］
- **F-086** Claude Code plugin 安装命令为 `/plugin marketplace add alibaba/open-code-review` 与 `/plugin install open-code-review@open-code-review`；直接复制命令文件到 `.claude/commands/` 时注册为 `/open-code-review`。［S13］
- **F-087** Claude Code Command 的三步为：以 `ocr review --audience agent` 运行评审（输出在 5 分钟超时内捕获）、按 High/Medium/Low 过滤与评估（低置信评论静默丢弃）、对 High/Medium 项自动应用修复。［S13］
- **F-088** Claude Code Command 默认自动应用修复；Agent Skill 默认在修改代码前先询问；两者共用同一 CLI 与同一底层 prompt，差别在默认值。［S12 S13］
- **F-089** Anthropic Agent SDK 接入方式为 `Agent(skill_paths=["/path/to/open-code-review/skills/open-code-review"])`。［S12］

## G. 可观测性与安全边界

- **F-090** `ocr viewer` 为内嵌 HTTP 服务器，默认地址 `localhost:5483`，前台运行，`Ctrl+C` 停止；会话在每次请求时从 `~/.opencodereview/sessions/` 惰性扫描。［S10］
- **F-091** 查看器对照 loopback 白名单（`localhost`、`127.0.0.1`、`::1`）校验 `Host` 头；具体绑定主机自动加入白名单，通配绑定（`:3000`、`0.0.0.0`、`::`）不加入并返回 `forbidden host`；`OCR_VIEWER_ALLOWED_HOSTS` 可配置允许主机名。［S10］
- **F-092** 遥测默认关闭，支持 `console` 与 `otlp` 两种 exporter；配置项为 `telemetry.enabled`、`telemetry.exporter`、`telemetry.otlp_endpoint`、`telemetry.content_logging`，环境变量为 `OCR_ENABLE_TELEMETRY` 与 `OTEL_EXPORTER_OTLP_ENDPOINT`。［S11］
- **F-093** 遥测 span 包括 `review.run`、`diff.parse`、`subtask.execute.group.<group-key>`、`llm.request`、`tool.execute.<tool-name>` 与 `event.*`；event 包括 `plan.skipped`、`token.threshold.exceeded`、`review.started`。［S11］
- **F-094** 遥测 metric 包括 `ocr.llm.tokens_used`（counter，标签 model、type）、`ocr.llm.requests_total`（counter，标签 model、status）、`ocr.llm.request_duration_seconds`（histogram，标签 model）。［S9 S11］
- **F-095** `chatgpt` provider 的凭证文件在 Unix 上使用 `0600` 权限、存储目录使用 `0700`；Windows 上访问权限取决于从用户配置文件目录继承的 ACL，OCR 不设置也不校验 DACL。［S15］

## H. 基准与效果口径

- **F-096** AACR-BENCH 由 50 个热门开源仓库、200 个真实 PullRequest、10 种编程语言构成，交叉验证者超过 80 名高级工程师。［S1］
- **F-097** AACR-BENCH 榜首为 Claude-4.6-Opus + Open Code Review v1.3.1：F1 25.10%、Precision 33.90%、Recall 20.00%、平均 1m23s、385K / 375K + 10K token。［S1］
- **F-098** Claude Code v2.1.169 在同一基准上的最高 F1 为 14.13%（Claude-4.8-Opus）与 11.57%（Claude-4.6-Opus）；Codex v0.140.0 的 GPT-5.5 为 8.36%。［S1］
- **F-099** Open Code Review 在该榜单前 8 名的 F1 区间为 17.90%–25.10%；Claude Code 与 Codex 条目的 F1 区间为 8.36%–14.13%。［S1］
- **F-100** 首页统计区（内部活跃用户数、真实任务数、npm 下载量、token 成本占比、AACR-BENCH SEM.F1）的数值以动效计数器呈现；抓取时该区域显示为 `0K+` / `0M+` / `0K+` / `0/9` / `0.10%` / `0/9` 等占位形态。［S1］

## 已知边界

- 本清单基于官方文档站公开页面，未执行本地安装与实机评审，所有行为类陈述均为「文档声明」而非「实测结论」。
- 官方文档站 `/docs/` 页面尾部的「集成」链接指向 `../integrations/agent-skill/`，该路径在站点上返回「页面找不到了」；实际可用路径为 `/docs/agent-skill/` 与 `/docs/delegate/`。链接断裂记录见[官方文档勘误表](official-doc-corrections.md) E-06。
- 官方文档站未公开 `internal/` 源码中除 F-008 至 F-036 以外的具体实现细节；F-008 至 F-036 全部为文档中直接列出的常量、文件名与函数名。
