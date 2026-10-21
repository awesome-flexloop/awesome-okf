---
type: "Wiki Tutorial"
title: "源码层事实清单（F-101 ~ F-178）"
description: "Open Code Review 源码层事实采集清单——按差异获取链、文件选择过滤、分组调度主循环、LLM 客户端 Provider、工具与输出契约、扩展与集成六主题编号，共 78 条带行号锚点的客观事实，并列出源码层与官方文档层的四处口径差。"
tags: ["open-code-review", "source-code", "fact-ledger", "ai-code-review"]
sources:
  - id: ocr-src-commit
    resource: "https://github.com/alibaba/open-code-review/tree/375f64cd6f67a48a135da83cfcf59c52669a09cb"
    title: "alibaba/open-code-review 源码快照 commit 375f64cd"
  - id: ocr-src-layer
    resource: "source-code-layer.md"
    title: "源码层信源登记与覆盖矩阵"
generated: { by: process:seven-concepts, at: 2026-10-21 }
verified: { by: process:seven-concepts-v, at: 2026-10-21 }
---

# 源码层事实清单（F-101 ~ F-178）

> **采集范围**：`alibaba/open-code-review` commit `375f64cd6f67a48a135da83cfcf59c52669a09cb` 的 Go 源码，采集日期 2026-10-21。
>
> **口径纪律**：只记录源码中可定位的客观陈述，不含因果推断词（「因为／所以／导致／因此／由于／使得」）。行号锚点指向该 commit 下文件的 1-based 行号。等级标记 L1=直接读值、L2=片段读值、L3=声明转述，定义见[信源登记页](source-code-layer.md#4-六主题覆盖矩阵)。
>
> **与文档层的关系**：本页编号从 F-101 起，**F-101 是源码层编号起点**，续接[官方文档层 F-001~F-100](official-doc-facts.md)。两层的分歧集中在文末[「源码层与文档层的四处口径差」](#源码层与文档层的四处口径差)一节，不在正文里静默改写。

## 主题 A：差异获取链（10 条）

| 编号 | 事实 | 锚点 | 字面值 | 等级 |
|------|------|------|--------|:---:|
| F-101 | 每个变更 hunk 携带的上下文行数是固定常量 3 | `internal/diff/git.go:24-25` | `const DiffContextLines = 3` | L1 |
| F-102 | diff provider 层无条件排除 11 个目录前缀：`.idea/`、`.vscode/`、`.svn/`、`.git/`、`vendor/`、`node_modules/`、`target/`、`.happypack/`、`.cachefile/`、`_packages/`、`rpm/` | `internal/diff/git.go:26-39` | `var providerDirIgnoreDirs = []string{` | L1 |
| F-103 | diff 获取模式是三值枚举：workspace（staged + unstaged + untracked）、commit（单提交对其父提交）、range（merge-base(from,to)..to） | `internal/diff/git.go:44-48` | `ModeWorkspace Mode = iota` | L1 |
| F-104 | 三种模式各有独立构造函数：`NewProvider`（range）、`NewCommitProvider`（commit）、`NewWorkspaceProvider`（workspace） | `internal/diff/git.go:97-125` | `func NewWorkspaceProvider(repoDir string, runner *gitcmd.Runner) *Provider {` | L1 |
| F-105 | range 模式执行 `git diff --no-ext-diff --no-textconv --find-renames --src-prefix=a/ --dst-prefix=b/ --no-color -U3 --end-of-options <base> <to> --`，且先求 merge-base，merge-base 为空时返回错误 | `internal/diff/git.go:220-230` | `--end-of-options` | L1 |
| F-106 | commit 模式执行 `git show` 并附加 `--diff-merges=first-parent`，源码注释记明普通 `git show` 对合并提交产出 `diff --cc` 组合差异、解析器无法解析 | `internal/diff/git.go:232-241` | `--diff-merges=first-parent` | L1 |
| F-107 | workspace 模式由 tracked 差异与 untracked 文件差异两段拼接而成，untracked 段逐个文件追加并以空行分隔 | `internal/diff/git.go:243-264` | `p.untrackedFileDiffs(ctx)` | L1 |
| F-108 | 差异集合用 `DiffSet` 结构承载，`Included` 与 `Excluded` 分别保存可评审与被 provider 内置目录规则排除的差异，`excludedAt` 记录被排除项在混合流中的原始序号 | `internal/diff/git.go:65-95` | `func (s DiffSet) ForEachInOrder(visit func(d model.Diff, providerExcluded bool)) {` | L1 |
| F-109 | `.gitignore` 匹配按 git 语义执行：按文件顺序遍历、最后一条匹配者决定结果、`!` 前缀反转该条判定、目录型模式（尾随 `/`）不作用于文件、否定型目录模式被跳过 | `internal/diff/git.go:281-332` | `strings.CutPrefix(pat, "!")` | L1 |
| F-110 | git 对非 ASCII 与含特殊字符路径输出 C 风格引用，源码实现 `unquoteGitPath` 处理反斜杠转义与八进制转义 | `internal/diff/quotedpath.go:23-94` | `unquoteGitPath` | L2 |

## 主题 B：文件选择与过滤（12 条）

| 编号 | 事实 | 锚点 | 字面值 | 等级 |
|------|------|------|--------|:---:|
| F-111 | 文件选择函数 `selectFiles` 是纯函数：不产生输出、不做变更、不访问 git 或 LLM；源码注释记明 `--preview` 与真实运行消费同一份选择结果 | `internal/agent/selection.go:33-43` | `func (a *Agent) selectFiles(diffs []model.Diff) []fileDecision {` | L1 |
| F-112 | 静态过滤门按固定顺序执行六道：binary → secret（内置密文路径）→ user exclude → user include → 扩展名白名单 → 默认排除路径 | `internal/agent/selection.go:65-102` | `func (a *Agent) whyExcluded(d model.Diff) ExcludeReason {` | L1 |
| F-113 | 密文路径门位于两道用户规则之前：源码注释写明「没有任何 include 通配符可以放行凭据路径，也没有任何用户 exclude 能以别的理由声称它」 | `internal/agent/selection.go:78-82` | `if allowedext.IsSecretPath(d.OldPath) || allowedext.IsSecretPath(d.NewPath) {` | L1 |
| F-114 | 用户 include 命中时函数立即返回 `ExcludeNone`，跳过后续扩展名白名单与默认排除路径两道门 | `internal/agent/selection.go:88-90` | `if f != nil && f.HasInclude() && f.IsUserIncluded(path) {` | L1 |
| F-115 | 排除原因码共 8 个非空字面量：`user_exclude`、`unsupported_ext`、`default_path`、`secret_exclude`、`provider_directory`、`deleted`、`binary`、`too_large`；未排除时取空串 | `internal/model/preview.go:11-25` | `ExcludeSecret ExcludeReason = "secret_exclude"` | L1 |
| F-116 | 扩展名白名单与默认排除模式由两份内嵌 JSON 提供，均以 `//go:embed` 引入，支持扩展名清单 123 项、默认排除模式 102 条 | `internal/config/allowlist/allowed_ext.go:39-43` | `//go:embed supported_file_types.json` | L1 |
| F-117 | 扩展名判定大小写不敏感；默认排除模式支持 `**` 递归匹配、`*` 单段通配与 `{a,b,c}` 花括号展开，由 `doublestar.Match` 执行 | `internal/config/allowlist/allowed_ext.go:75-100` | `doublestar.Match(pattern, lowerPath)` | L1 |
| F-118 | 默认排除模式按生态分组，覆盖测试文件（`*_test.go`、`*.test.{js,ts}`、`__tests__/**` 等）、前端依赖与构建产物、Ruby/Java/Rust/Python/JavaScript 包管理目录、C/C++ 产物目录、Python 虚拟环境与缓存目录、iOS 依赖目录、.NET 产物目录、Haskell/Julia/Nim/Solidity/Vyper 测试与生成物 | `internal/config/allowlist/default_exclude_patterns.json:1-103` | `**/*_test.go` | L1 |
| F-119 | 密文路径判定由独立的 `IsSecretPath` 实现，先匹配环境变量类路径再匹配通配模式，全部在转小写后进行 | `internal/config/allowlist/secret_path.go:47-59` | `func IsSecretPath(filePath string) bool {` | L2 |
| F-120 | 删除文件被标记为 `ExcludeDeleted` 并保留在 agent 的工作差异集合中：源码注释写明删除文件不携带待评审的新内容，但仍属于提示词展示的变更文件清单 | `internal/agent/selection.go:26-31` | `func (d fileDecision) retained() bool {` | L1 |
| F-121 | 单文件体积门的上限取 `PromptTokenLimit(MaxTokens)`；仅在配置了上限时才对 diff 做分词计数，`max_tokens=0` 时跳过整个分词过程，超限标记为 `ExcludeTooLarge` | `internal/agent/selection.go:44-58` | `dec.DiffTokens = llm.CountTokens(d.Diff)` | L1 |
| F-122 | 规则解析优先级为 custom → project → global → system，合并后构建同一个 `FileFilter`；`FileFilter` 的用户 include/exclude 匹配支持花括号展开、大小写不敏感与 doublestar glob | `internal/config/rules/system_rules.go:220-263`、`:288-347` | `func NewResolver` | L2 |

## 主题 C：分组调度与评审主循环（14 条）

| 编号 | 事实 | 锚点 | 字面值 | 等级 |
|------|------|------|--------|:---:|
| F-123 | 待审差异数量 ≤ 1 时直接构造单文件分组，不发起分组 LLM 请求 | `internal/agent/grouping.go:69-85` | `toSingleFileGroups` | L2 |
| F-124 | 分组 LLM 请求体只有三个字段：Model、Messages、MaxTokens；请求不含 diff 内容 | `internal/agent/grouping.go:214-218` | `resp, err := client.CompletionsWithCtx(ctx, llm.ChatRequest{` | L1 |
| F-125 | 分组请求的 `MaxTokens` 未指定时取 4096 | `internal/agent/grouping.go:210-212` | `maxTokens = 4096` | L1 |
| F-126 | 分组提示词的唯一占位符是 `{{file_list}}`，以字符串替换方式注入 | `internal/agent/grouping.go:186-192` | `strings.ReplaceAll(m.Content, "{{file_list}}", fileList)` | L1 |
| F-127 | 文件清单逐行输出，格式为 `[序号] 路径与变更统计`，序号从 0 起，是模型分组时使用的索引 | `internal/agent/grouping.go:255-261` | `fmt.Fprintf(&sb, "[%d] %s\n", i, formatDiffEntry(d))` | L1 |
| F-128 | 分组响应是 JSON 数组，元素含 `label` 与 `files` 两个字段（`files` 为整型索引数组而非路径数组）；解析前先剥离 markdown 代码围栏，JSON 解析失败（含因补全上限被截断的响应）返回错误并回退到逐文件派发 | `internal/agent/grouping.go:41-49`、`internal/agent/grouping.go:263-284` | `type groupingResponse struct {` | L1 |
| F-129 | 分组响应中越界的文件索引与重复索引被跳过 | `internal/agent/grouping.go:289-303` | `if seen[idx] {` | L1 |
| F-130 | 未被任何分组覆盖的文件各自成为单文件分组，其 Label 取该文件的新路径 | `internal/agent/grouping.go:309-314` | `groups = append(groups, FileGroup{Label: d.NewPath, Diffs: []model.Diff{d}})` | L1 |
| F-131 | 单组文件数上限常量为 10，超限的组按 10 个一组切片、Label 保持不变 | `internal/agent/grouping.go:22`、`:322-342` | `const maxFilesPerGroup = 10` | L1 |
| F-132 | 组级 token 预算阀门在分组结果上生效：超出预算的组被拆为每文件一组，Label 追加拆分后缀 | `internal/agent/grouping.go:344-367` | `enforceGroupTokenBudget` | L2 |
| F-133 | plan 阶段双阈值写在评审模板里：单文件变更行数阈值 50，组内文件数 ≥ 2 且合计变更行数阈值 100 | `internal/config/template/task_template.json:39-40` | `"PLAN_MODE_LINE_THRESHOLD": 50` | L1 |
| F-134 | main 阶段轮次上限由模板常量 `MAX_REVIEW_ROUNDS` 给出，默认值为 2；effort 档位覆写该值，low=1、medium=2、high=3 | `internal/config/template/task_template.json:43` | `"MAX_REVIEW_ROUNDS": 2` | L1 |
| F-135 | 主循环的连续无有效结果上限为 3 轮，达到即停止 | `internal/llmloop/loop.go:389` | `const maxConsecutiveEmptyRounds = 3` | L1 |
| F-136 | 停止原因以枚举区分，至少含 `StopNone`、`StopMaxRounds`、`StopEmptyRounds`、`StopCompression` 与 token 预算类停止；停止原因在 agent 层归类为预算失败或未知失败 | `internal/llmloop/loop.go:401-537`、`internal/agent/agent.go:1223-1228` | `StopMaxRounds` | L2 |

## 主题 D：LLM 客户端与 Provider 解析（12 条）

| 编号 | 事实 | 锚点 | 字面值 | 等级 |
|------|------|------|--------|:---:|
| F-137 | provider 注册表是 `registry = []Provider{...}`，当前条目数为 30 | `internal/llm/providers.go:45-516` | `var registry = []Provider{` | L1 |
| F-138 | 30 个 provider 名为：anthropic、bedrock、chatgpt、openai、openai-responses、openrouter、edenai、gemini、dashscope、dashscope-tokenplan、volcengine、deepseek、tencent-tokenhub、hy-tokenplan、iflytek、kimi、kimi-global、z-ai、z-ai-coding、mimo、minimax、minimax-cn、baidu-qianfan、ollama-cloud、novita、xai、litellm、siliconflow、siliconflow-cn、mistral | `internal/llm/providers.go:47-501` | `Name:        "anthropic",` | L1 |
| F-139 | 协议常量共 4 个：`anthropic`、`anthropic-bedrock`、`openai`、`openai-responses` | `internal/llm/protocol.go:22-37` | `ProtocolAnthropicBedrock = "anthropic-bedrock"` | L2 |
| F-140 | Provider 记录的字段包括 Name、DisplayName、Protocol、BaseURL、AuthHeader、EnvVar、AmbientAuth、ExternalAuth、RequiresStreaming、RejectsSamplingParams 与 Models | `internal/llm/providers.go:23-41` | `RejectsSamplingParams bool` | L1 |
| F-141 | 客户端按解析出的协议四路分发到 Anthropic、Anthropic-Bedrock、OpenAI Responses 与 OpenAI Chat Completions 实现，未知协议落到 openai | `internal/llm/client.go:486-515` | `NewAnthropicBedrockClient` | L2 |
| F-142 | 端点解析顺序为：OCR 配置文件 → OCR 环境变量 → Claude Code 环境 → shell rc 文件 | `internal/llm/resolver.go:133-141` | `{"OCR environment"` | L2 |
| F-143 | OCR 侧环境变量名为 `OCR_LLM_URL`、`OCR_LLM_TOKEN`、`OCR_LLM_MODEL`、`OCR_LLM_AUTH_HEADER`、`OCR_LLM_EXTRA_HEADERS`、`OCR_LLM_PROTOCOL`、`OCR_LLM_TIMEOUT`，另有 `OCR_USE_ANTHROPIC` | `internal/llm/resolver.go:56-73` | `OCR_LLM_PROTOCOL` | L2 |
| F-144 | 重试报告的 schema 标识为 `ocr.llm-retry-report/v1`，分类枚举含 `rate_limited`、`overloaded`、`authentication`、`timeout`、`network` | `internal/llm/retry_report.go:18`、`:26-35` | `"ocr.llm-retry-report/v1"` | L2 |
| F-145 | HTTP 状态码到重试分类的映射为：429→rate_limited、529→overloaded、401/403→authentication、408/504→timeout、其余非 2xx→provider；`context.Canceled`→cancelled、`DeadlineExceeded`→timeout | `internal/llm/retry_report.go:26-35`、`internal/llm/retry_report.go:182-218` | `rate_limited` | L2 |
| F-146 | SDK 层重试次数统一设置为 5 次 | `internal/llm/client.go:594-633` | `WithMaxRetries(5)` | L2 |
| F-147 | 单次请求默认超时 5 分钟：OpenAI 与 Anthropic 两个客户端构造函数都在 `cfg.Timeout <= 0` 时补 `5 * time.Minute`；另有 Bedrock 配置加载超时 60 秒与响应头超时余量 30 秒两个独立常量 | `internal/llm/client.go:594-596`、`internal/llm/client.go:1161-1163`、`internal/llm/client.go:46`、`internal/llm/client.go:56` | `cfg.Timeout = 5 * time.Minute` | L2 |
| F-148 | token 计数使用 tiktoken 加内嵌 BPE 数据，编码文件以 `//go:embed bpe_data/*.tiktoken` 引入；编码选择规则为 o1/o3/o4 系列用 `o200k_base`、默认 `cl100k_base`，加载失败时回退为字节数除以 4 | `internal/llm/embedded_loader.go:16-17`、`:43-48`；`internal/llm/client.go:553-581` | `//go:embed bpe_data/*.tiktoken` | L2 |
| F-149 | ChatGPT 端点被强制约束：协议固定 `openai-responses`、要求流式、拒绝采样参数，且不接受 url、protocol、api_key、auth_header 的覆盖 | `internal/llm/chatgpt.go:34-36`、`internal/llm/chatgpt.go:75` | `RequiresStreaming` | L2 |
| F-150 | ChatGPT 登录使用 OAuth 授权码 + PKCE（S256）流程，issuer 为 `https://auth.openai.com`，scope 含 `offline_access` 与 `chatgpt.tokens.use.direct`；凭据存放于 `~/.opencodereview/auth/chatgpt` 下的 `accounts.json`，目录权限 0700 | `internal/chatgptauth/oauth.go:23-27`、`:134-140`；`internal/chatgptauth/store.go:85-100` | `Issuer = "https://auth.openai.com"` | L2 |
| F-151 | 原始请求/响应报文日志由环境变量 `OCR_RAW_LOGGING` 开启，取值为 `1` 时启用 | `internal/llm/raw.go:24-28` | `const rawLoggingEnv = "OCR_RAW_LOGGING"` | L2 |

## 主题 E：内置工具与输出契约（14 条）

| 编号 | 事实 | 锚点 | 字面值 | 等级 |
|------|------|------|--------|:---:|
| F-152 | 内置工具为 6 个：`task_done`、`code_comment`、`file_read`、`file_find`、`file_read_diff`、`code_search`；另有一个 `unknown` **内部哨兵常量**用于未识别工具名，该哨兵不注册为工具、不进入对外工具名集合，故对外工具数仍为 6 | `internal/tool/definitions.go:17-38` | `CodeSearch   = Tool{name: "code_search"}` | L1 |
| F-153 | 工具参数 schema 的权威来源是内嵌 `tools.json`，条目字段为 name、plan_task、main_task、definition，按阶段取用；`code_search`、`file_read_diff`、`file_find` 两个阶段均可用，其余三个仅 main 阶段可用 | `internal/config/toolsconfig/toolsconfig.go:15-57` | `//go:embed tools.json` | L2 |
| F-154 | `code_comment` 参数含 comments 数组，数组项字段为 content、existing_code、suggestion_code、category、severity、path；数组项必填字段为 content、existing_code、category、severity、path，外层必填字段为 comments | `internal/config/toolsconfig/tools.json:28-99` | `"required": [` | L2 |
| F-155 | `task_done` 参数只有一个 state 字段，取值为 `DONE` 或 `FAILED`，且 state 是唯一必填字段 | `internal/config/toolsconfig/tools.json:3-26` | `"DONE"` | L2 |
| F-156 | 其余工具参数名为：`code_search` 的 search_text（必填）、file_patterns、case_sensitive、use_perl_regexp；`file_read` 的 file_path（必填）、start_line、end_line；`file_read_diff` 的 path_array（必填）；`file_find` 的 query_name（必填）、case_sensitive | `internal/config/toolsconfig/tools.json:101-212` | `"query_name"` | L2 |
| F-157 | 评论参数解析后对 path 做规范化（反斜杠转 `/`、路径清理、去前导 `/`），category 非法值归为 other、severity 非法值归为 low，path 或 content 为空的条目被丢弃 | `internal/tool/code_comment.go:161-196` | `normalizeCommentPath` | L2 |
| F-158 | 评论参数存在自动修复机制：对序列化字符串逐字节转义（非法反斜杠、非结构引号、控制字符）；修复函数在 `internal/tool/comment_args_repair.go`，修复成功后在主循环记录 warning `comment_args_repaired` | `internal/tool/comment_args_repair.go:98-151`、`internal/llmloop/loop.go:732` | `comment_args_repaired` | L2 |
| F-159 | 行号锚定为三级链路：先在本文件解析、再跨文件重定位、最后交由 LLM 重定位任务；未锚定表示为起止行号均为 0 | `internal/diff/resolver.go:62-139`；`internal/llmloop/loop.go:759-780` | `comment_refiled` | L2 |
| F-160 | CLI 的 JSON 输出恒为 stdout 上的单个对象，顶层字段含 status、llm、trace_id、message、summary、tool_calls、comments、groups、warnings、project_summary、resume、session_id、manifest、retry_report，输出带两空格缩进 | `cmd/opencodereview/output.go:337-370` | `enc.SetIndent("", "  ")` | L2 |
| F-161 | 无评论产出时的 message 为 `No comments generated. Looks good to me.`；无可评审文件时 status 为 `skipped`、message 为 `No supported files changed.`；失败时另向 stderr 写出 status 为 `failed` 的 JSON 对象 | `cmd/opencodereview/output.go:651-663`、`:665-720` | `No supported files changed.` | L2 |
| F-162 | CLI 退出码集合为 {0, 1}：根命令返回错误时退出 1、否则 0；第二次 SIGINT 强制 `os.Exit(1)`；review 场景仅在运行级失败或 manifest 终态为 failed 时返回非零，存在可用覆盖时退出 0 | `cmd/opencodereview/main.go:18-31`；`cmd/opencodereview/interrupt.go:19-20` | `os.Exit(1)` | L2 |
| F-163 | SARIF 输出为 2.1.0 格式，工具名 `OpenCodeReview`，规则集 8 条（bug、security、performance、maintainability、test、style、documentation、other）；category 映射为 ruleId，critical/high 映射为 error、medium 映射为 warning、low 映射为 note，指纹为 path、category 与 existing_code（或起始行）的 sha256，域前缀 `ocrFinding/v1` | `cmd/opencodereview/sarif.go:26-32`、`:155-185`、`:228-318` | `sarifFingerprintKey = "ocrFinding/v1"` | L2 |
| F-164 | 运行清单 schema 标识为 `ocr.run-manifest/v1`，字段含 run_id、parent_run_id、operation、terminal_state、repository、input、execution、coverage、run_failure、elapsed_ms；终态取 complete、partial、failed、skipped；coverage 由 selected、completed、reused、failed、waived 五个集合构成 | `internal/session/manifest.go:23`、`:163-170`、`:181-188`、`:231-237` | `ManifestSchemaVersion = "ocr.run-manifest/v1"` | L2 |
| F-165 | 委托模式预览 JSON 的 schema 标识为 `1`，字段含 mode、repository、from、to、commit、merge_base、background、total_files、reviewable_count、excluded_count、total_insertions、total_deletions、reviewable_files、excluded_files；文件项含 path、status、insertions、deletions、exclude_reason | `cmd/opencodereview/delegate_cmd.go:246-285` | `delegateSchemaVersion = "1"` | L2 |
| F-166 | `file_read` 单次读取上限 500 行，输出含 `IS_TRUNCATED` 与 `LINE_RANGE` 标记；`code_search` 以 `git --no-pager -c core.quotepath=false grep -n --no-color --max-count 101 -e` 执行，上限 100 条、超时 10 秒；`file_find` 上限 100、超时 10 秒，未命中时输出 `// The file was not found` | `internal/tool/file_read.go:12`；`internal/tool/code_search.go:18-20`；`internal/tool/file_find.go:111-115` | `fileReadMaxLines = 500` | L2 |

## 主题 F：扩展与集成面（11 条）

| 编号 | 事实 | 锚点 | 字面值 | 等级 |
|------|------|------|--------|:---:|
| F-167 | MCP 集成方向是客户端：OCR 作为 MCP client 连接外部 MCP server，传输形式为 stdio 子进程（客户端实现名 `open-code-review`）与 remote Streamable HTTP | `internal/mcp/client.go:43-56` | `mcp.CommandTransport` | L2 |
| F-168 | MCP 配置键为 `mcp_servers`，条目字段含 type、command、args、env、url、headers、tools、setup；注册时按 allowedTools 过滤，与内置工具同名的条目被跳过并告警 `conflicts with built-in tool` | `internal/mcp/provider.go:33-49`、`cmd/opencodereview/config_cmd.go:335-359` | `conflicts with built-in tool` | L2 |
| F-169 | 仓库内没有 MCP server 实现（`mcp.NewServer` 仅出现在测试文件中）；CLI 子命令集合为 version、review、scan、delegate、session、config、auth、llm、rules、viewer、completion | `cmd/opencodereview/root.go:15-17`、`cmd/opencodereview/root.go:56-66` | `Use:   "ocr",` | L2 |
| F-170 | 会话查看器是只读 HTTP 服务，默认地址 `localhost:5483`，仅暴露 GET 静态资源、GET 首页、GET 仓库列表、GET 仓库对比、GET 单会话五条路由，非 GET 请求由 `ServeMux` 返回 405 | `cmd/opencodereview/viewer_cmd.go:37`；`internal/viewer/server.go:44-152` | `localhost:5483` | L2 |
| F-171 | 查看器带 DNS rebinding 防护：Host 白名单默认含 localhost、127.0.0.1、::1，非通配绑定的主机自动加入，通配绑定（空串、0.0.0.0、::）不加入，额外主机经 `OCR_VIEWER_ALLOWED_HOSTS` 逗号分隔追加，非白名单返回 403 `forbidden host` | `internal/viewer/hostguard.go:15`、`:61-105` | `OCR_VIEWER_ALLOWED_HOSTS` | L2 |
| F-172 | 查看器响应头含 CSP（`default-src 'self'`、`frame-ancestors 'none'`、`form-action 'none'` 等）、`X-Content-Type-Options: nosniff`、`X-Frame-Options: DENY`、Referrer-Policy 与 Permissions-Policy | `internal/viewer/securityheaders.go:14-35` | `frame-ancestors 'none'` | L2 |
| F-173 | 遥测默认关闭，由 `OCR_ENABLE_TELEMETRY=1` 开启；存在 `OTEL_EXPORTER_OTLP_ENDPOINT` 时 exporter 取 otlp，`OTEL_EXPORTER_OTLP_PROTOCOL` 默认 grpc；配置优先级为 defaults < config.json < env | `internal/telemetry/config.go:45-62`、`internal/telemetry/config.go:112-125` | `OCR_ENABLE_TELEMETRY` | L2 |
| F-174 | 遥测 span 名含 `llm.request` 与 `review.run`；指标名含 `ocr.review.duration_seconds`、`ocr.files_reviewed_total`、`ocr.comments_generated_total`、`ocr.llm.requests_total`、`ocr.llm.tokens_used`、`ocr.tool.calls_total` | `internal/telemetry/span.go:87-112`；`internal/telemetry/metrics.go:40-70` | `llm.request` | L2 |
| F-175 | scan 路径由独立的 `internal/scan` agent 实现，其 `RunManifest()` 恒返回 nil（源码注释写明 scan 有意不在 v1 运行清单范围内）；scan 模板 `MAX_TOKENS` 为 58888、`MAX_COMPLETION_TOKENS` 为 16384、`MAX_TOOL_REQUEST_TIMES` 为 60，评审模板对应值为 200000、16384、100 | `internal/scan/agent.go:187-190`、`internal/config/template/scan_template.json:80-82`、`internal/config/template/task_template.json:38`、`internal/config/template/task_template.json:44-45` | `func (a *Agent) RunManifest() *session.RunManifest { return nil }` | L2 |
| F-176 | ACP 适配器是独立 Go 模块 `github.com/alibaba/open-code-review/acp`，使用 stdio 传输，暴露 `/review` 与 `/scan` 两个命令，调用时恒定追加 `--format json --audience human --color never`；其 Extra 标志白名单 review 为 effort、no-filter、background、background-file，scan 为 batch、no-plan、no-dedup、no-summary、background | `acp/go.mod:1-5`；`acp/README.md:218-231` | `module github.com/alibaba/open-code-review/acp` | L3 |
| F-177 | 官方为 OpenCode 提供 TypeScript 插件，注册 `ocr_review` 与 `ocr_health` 两个工具及 `ocr-review`、`ocr-health` 两个命令，基础参数为 `review --audience agent`，非预览模式追加 `--format json`；子进程默认超时 15 分钟、输出上限 10 MiB | `plugins/open-code-review/opencode/open-code-review.ts:99-101`、`plugins/open-code-review/opencode/open-code-review.ts:170-171`、`plugins/open-code-review/opencode/open-code-review.ts:389` | `ocr_review` | L2 |
| F-178 | 官方文档站的中文源文件随仓库一同版本控制，可与实现按同一 commit 对照：`pages/src/content/docs/zh/` 下共 18 个 Markdown 文件（含 `integrations/` 子目录 5 篇），每篇带 `title` / `sidebar.order` frontmatter | `pages/src/content/docs/zh/architecture.md:1-5` | `title: 架构` | L1 |

## 源码层与文档层的四处口径差

以下四条是源码层与[官方文档层](official-doc-facts.md) 对同一对象的表述差异。源码层取值来自 commit `375f64cd` 的实现常量与清单，文档层取值来自 2026-10-21 采集的文档站文本。

| # | 对象 | 文档层口径 | 源码层口径 | 源码层锚点 | 差异范围 |
|---|------|-----------|-----------|-----------|---------|
| **D-1** | 内置 provider 数 | **25 个**（F-049） | **30 个** | `internal/llm/providers.go:45-516` | 源码多出 5 个：edenai、z-ai-coding、ollama-cloud、litellm、mistral |
| **D-2** | 静态过滤门道数 | **5 道**：binary → user_exclude → user_include → unsupported_ext → default_path（F-015） | **6 道**：在 binary 之后、user_exclude 之前插入 secret 门 | `internal/agent/selection.go:65-102` | 顺序与门数均变；secret 门不可被用户 include 放行 |
| **D-3** | 排除原因码数 | **7 种**（F-014、F-018） | **8 种非空字面量** | `internal/model/preview.go:11-25` | 源码含 `provider_directory` 一项 |
| **D-4** | `MAX_TOOL_REQUEST_TIMES` | 单一取值 **100**（F-029） | **review 100 / scan 60** 两套 | `internal/config/template/task_template.json:38`、`internal/config/template/scan_template.json:82` | scan 路径单独一套上限 |

> **使用规则**：引用 OCR 当前行为时以源码层口径为准；引用「文档站声明了什么」时以文档层为准。两层不得互相静默覆盖。
