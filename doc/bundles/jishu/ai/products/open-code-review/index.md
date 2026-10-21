---
okf_version: "0.2"
type: bundle
title: "Open Code Review 阿里 AI 代码评审 CLI"
description: "阿里巴巴开源 AI 代码评审 CLI 工具 Open Code Review 中文教程——官方运行时模型、集成契约、可迁移模式与验证手册、官方文档事实清单与勘误表（官方文档站 16 页核验，100 条编号事实 + 11 条勘误），并叠加源码层（commit 375f64cd，78 条编号事实 + 4 处口径差）。"
tags: ["open-code-review", "ai-code-review", "alibaba", "go", "llm", "code-review", "agent", "official-docs"]
generated:
  by: process:seven-concepts
  at: "2026-10-21T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-21T00:00:00+08:00"
status: stable
stale_after: 2027-01-21
sources:
  - id: ocr-docs-root
    resource: "https://open-codereview.ai/"
    title: "Open Code Review 官方文档站首页"
  - id: ocr-docs-architecture
    resource: "https://open-codereview.ai/docs/architecture/"
    title: "官方文档 · 架构"
  - id: ocr-docs-cli-reference
    resource: "https://open-codereview.ai/docs/cli-reference/"
    title: "官方文档 · CLI 参考"
  - id: ocr-docs-configuration
    resource: "https://open-codereview.ai/docs/configuration/"
    title: "官方文档 · 配置"
  - id: ocr-docs-review-rules
    resource: "https://open-codereview.ai/docs/review-rules/"
    title: "官方文档 · 评审规则"
  - id: ocr-docs-tools
    resource: "https://open-codereview.ai/docs/tools/"
    title: "官方文档 · 工具"
  - id: ocr-docs-faq
    resource: "https://open-codereview.ai/docs/faq/"
    title: "官方文档 · FAQ"
  - id: ocr-docs-delegate
    resource: "https://open-codereview.ai/docs/delegate/"
    title: "官方文档 · 委托模式"
  - id: ocr-docs-agent-skill
    resource: "https://open-codereview.ai/docs/agent-skill/"
    title: "官方文档 · Agent Skill 集成"
  - id: ocr-docs-claude-code
    resource: "https://open-codereview.ai/docs/claude-code/"
    title: "官方文档 · Claude Code 集成"
  - id: ocr-github-repo
    resource: "https://github.com/alibaba/open-code-review"
    title: "官方仓库 alibaba/open-code-review"
---

# Open Code Review 阿里 AI 代码评审 CLI

阿里巴巴开源 AI 代码评审 CLI 工具 Open Code Review 中文教程。2026-10-21 起在原 19 页二手迁入稿之上，新增**官方文档层**（6 页），以官方文档站 `open-codereview.ai` 全部可达页面为一手信源重建运行时模型、集成契约与可迁移模式，并对既有页面做逐条口径勘误；同日再叠加**源码层**（6 页），以仓库 commit `375f64cd` 的静态源码阅读补齐数值级事实与四条实现级可迁移模式。

## 来源分层与引用规则

本 bundle 的页面分四层，**引用时按层取信**：

| 层 | 页面 | 信源性质 | 引用规则 |
|----|------|---------|---------|
| **① 源码层** | [15](concepts/15-source-code-runtime-model.md) · [16](concepts/16-source-code-extension-contracts.md) · [17](concepts/17-source-code-verification-playbook.md) · [信源登记](references/source-code-layer.md) · [事实清单](references/source-code-facts.md) · [V 记录](references/source-code-review.md) | 一手：仓库 commit `375f64cd` 静态源码阅读，78 条编号事实 | **数值、清单、默认值、字段集、顺序以源码层为准**；结论为「代码中如此声明」，非实机验证 |
| **② 官方文档层** | [12](concepts/12-official-runtime-model.md) · [13](concepts/13-integration-contracts.md) · [14](concepts/14-verification-playbook.md) · [facts](references/official-doc-facts.md) · [corrections](references/official-doc-corrections.md) · [V 记录](references/adversarial-review.md) | 一手：官方文档站 16 页 + 官方仓库，2026-10-21 采集 | **行为语义、推荐用法以官方口径为准**；数值与源码层冲突处见口径差表 |
| **③ 二手迁入层** | `concepts/00`~`11` 中除上述三页外的 12 概念页 | 二手：微信文章 + SpecWeave 学习库三源整合去重 | 叙述脉络与溯源链仍有效；**与①②层冲突的数值以勘误表为准** |
| **④ 二手迁入但受勘误约束** | `references/cli-reference.md` · `faq-troubleshooting.md` · `llm-providers-detail.md` | 二手：同上 | 使用前先查 [勘误表](references/official-doc-corrections.md) 中 E-01 ~ E-11 |

> **两层裁决表并存**：①↔② 的四处数值差异记录在[源码层事实清单](references/source-code-facts.md)的「四处口径差」一节（D-1 ~ D-4）；②↔③ 的十一处差异记录在[官方文档勘误表](references/official-doc-corrections.md)（E-01 ~ E-11）。**两张表都不回改对方页面**——只登记差异与判定，让「谁在什么时间说了什么」保持可追溯。
>
> **★ 方向性结论**：四处源码层差异全部是「源码更多」（provider 多 5 个、过滤门多 1 道、原因码多 1 种、scan 另有独立上限），没有一处「源码更少」。**文档站不是过期，而是在有意收敛叙述范围**；引用具体数值时以源码层为准。

## 核心洞察（四元组）

### I-1 · OCR 的核心创新是把可枚举的确定性工作移出模型，而不是让 LLM「更会评审代码」

- **现象**：OCR 的流水线中，diff 解析、噪声目录剔除、五重门过滤、语义分组、行号定位、规则路由、记忆压缩全部由确定性代码完成，LLM 只在「分组」与「评审」两个节点被调用。
- **证据**：分组阶段的 `GROUPING_TASK` 输入只有文件元数据（路径、状态、`+`/`-` 行数），**不含 diff 内容**（F-021）；过滤顺序固定为 binary → user_exclude → user_include → unsupported_ext → default_path（F-015）；噪声目录在 diff provider 层即被剔除（F-019）。
- **反常识**：直觉上「给模型更多上下文 = 更好的评审」，但 OCR 恰恰在**分组阶段刻意不喂 diff**，在 plan 阶段刻意不发送 Tools 字段（F-026）。喂得更多反而是编排缺陷。
- **行动**：评审任何 AI 工具时，先问「哪些环节是**可枚举的**」并把它们从模型里拿出来；模型只该处理真正需要语义判断的部分。参见 [concepts/12](concepts/12-official-runtime-model.md)。

### I-2 · 召回与精度是架构选择的函数，换模型带来的收益远小于换架构

- **现象**：同一 Claude-4.6-Opus 模型，OCR v1.3.1 的 F1 为 25.10%，Claude Code v2.1.169 为 11.57%；而 OCR 前 8 名的 F1 区间（17.90%–25.10%）**全部高于** Claude Code 与 Codex 条目区间（8.36%–14.13%）。
- **证据**：AACR-BENCH（50 仓库 / 200 PR / 10 语言 / 80+ 工程师交叉验证）中 OCR 榜首 Precision 33.90%、Recall 20.00%（F-097、F-098、F-099）。
- **反常识**：榜单上「换个更强的模型」看起来是提升手段，但在同一架构内换模型带来的 F1 变化（4.6→4.8 在 OCR 侧 F1 反而从 25.10% 降到 17.90%）甚至可能是负的；**架构差异（25.10% vs 11.57%）远大于模型代际差异**。
- **行动**：先优化编排（分组、过滤、退出条件、token 守卫），再谈换模型；评估 AI 工具时必须固定模型变量做架构对照。

### I-3 · 最贵的开关是「是否进 plan 阶段」与「跑几轮」，而不是模型档位

- **现象**：`--effort` 控制的是 main 循环轮次（low=1 / medium=2 / high=3），plan 阶段由**双阈值**独立触发（组内单文件 ≥50 行，或组内 ≥2 文件且合计 ≥100 行）。
- **证据**：F-025、F-027、F-056；FAQ 明确指出 plan 阶段会额外产生一次 LLM 调用与一次上下文探索开销。
- **反常识**：`--effort high` 只把 main 循环从 2 轮提到 3 轮，**不会**让 plan 阶段必然触发——plan 是否进入由变更规模决定，不由 effort 决定。把 effort 当作「质量旋钮」是误用。
- **行动**：成本控制优先看两个杠杆——① 用 `--preview` 先筛文件规模，判断会进几个 plan 组；② 用 `--effort low` 跑基线，再对高风险文件单独提高档位。参见 [concepts/14](concepts/14-verification-playbook.md) 的调节杆矩阵。

### I-4 · 可复现性靠显式信号，而不是靠「跑一次看看」

- **现象**：OCR 的每一次运行都留下可机器消费的结构化信号：0 表示「未锚定」的评论行号、7 种 preview 排除原因码、`manifest.terminal_state`、`warnings` 数组、恒为单个 JSON 对象的 stdout。
- **证据**：F-014/F-018（原因码）、F-034（行号解析失败时 `start_line`/`end_line` 为 0）、F-070（`--format json` 恒一个对象）、F-071/F-072（manifest 有/无两种终态）、F-069（`warnings`）。
- **反常识**：多数工具在「什么都没发生」时返回空数组或空输出，把「无文件」「未锚定」「子 agent 失败」混为一谈；OCR 明确区分 `skipped`（无合格文件）与 `No supported files changed.`（manifest-less 路径）两种终态。
- **行动**：在 CI 中消费 AI 工具输出时，先定义「空结果」与「失败」的机器可区分契约，否则无法为失败设告警。参见 [concepts/13](concepts/13-integration-contracts.md)。

### I-5 · 「不可覆盖安全门」是区分可用性与可信赖性的分界线

- **现象**：密文路径判定门（secret 门）排在两道用户规则**之前**；用户 include 命中时只跳过后续的扩展名白名单与默认排除路径两道门，不跳过 secret 门。
- **证据**：源码注释原文写明「没有任何 include 通配符可以放行凭据路径，也没有任何用户 exclude 能以别的理由声称它」（F-113）；用户 include 的早返回路径见 F-114；同类设计在查看器 Host 白名单上复现（通配绑定不自动加入白名单，F-171）。
- **反常识**：直觉上「用户配置 include = 用户想放行这些文件」，实现上 include 只放宽**选择性门**、不放宽**安全门**。若把 secret 门做成用户规则链中的一环，一条宽 include 就能让凭据文件进入评审上下文。
- **行动**：设计任何「用户可扩范围 + 系统有禁区」的系统时，先把门拆成**选择性门**与**安全门**两类，并强制安全门排在用户规则之前。参见 [concepts/17](concepts/17-source-code-verification-playbook.md) 模式 M-4。

### I-6 · 降级链必须单向：LLM 步骤失败只允许让粒度变细，不允许让流程中止

- **现象**：分组 LLM 调用失败、返回空或被补全上限截断时，回退路径是「每文件一组」；待审文件数 ≤ 1 时干脆不发起分组请求；越界索引与重复索引被跳过而非报错。
- **证据**：F-128（围栏剥离 + JSON 解析失败回退）、F-123（≤1 文件不发请求）、F-129（越界/重复跳过）、F-130（未覆盖文件各自成组）；参数修复成功后留下 warning `comment_args_repaired`（F-158）。
- **反常识**：直觉上「模型分组失败 = 这次评审不可信」，实现上分组只是**优化步骤**，其失败等价于「跳过优化」，与「LLM 做必答项」的直觉相反。把优化步骤当必要步骤，会让一个可容忍的解析错误升级为整次评审失败。
- **行动**：设计多智能体流水线时逐个 LLM 调用点回答「它失败时会发生什么」——合格答案只能是「粒度更细」或「结论更保守」。参见 [concepts/17](concepts/17-source-code-verification-playbook.md) 模式 M-2。

### I-7 · 输出状态必须分层承载：退出码、JSON 业务态、manifest 覆盖态互不替代

- **现象**：CLI 退出码集合只有 {0, 1}；review 场景「部分文件成功、部分失败」时退出码仍为 0，真实结果只在 manifest 的 `terminal_state=partial` 与 coverage 五集合中体现；scan 路径的 manifest 恒为 nil。
- **证据**：F-162（退出码 {0,1} 与「存在可用覆盖时退出 0」）、F-160（JSON 恒为单个对象，14 个顶层字段）、F-164（terminal_state 四态 + coverage 五集合）、F-161（三条互斥 message）、F-175（scan 的 `RunManifest()` 恒返回 nil）。
- **反常识**：直觉上「退出码 0 = 成功」在这里会误判——部分覆盖也是 0；反过来「所有路径都造一个 manifest」也是错的，scan 路径有意声明自己不在 v1 清单范围内。**缺失的层要显式缺失，不填假值**。
- **行动**：把工具的输出拆成进程层 / 业务层 / 覆盖层三层，每层能被不同消费者独立解析；跨层判定规则（如「退出码 0 但 terminal_state=partial」）必须写进 CI 契约。参见 [concepts/16](concepts/16-source-code-extension-contracts.md) 第 3 节与 [concepts/17](concepts/17-source-code-verification-playbook.md) 模式 M-3。

### I-8 · 文档与实现的分歧应当登记而非抹平——差异表本身就是资产

- **现象**：源码层与官方文档层存在四处数值差异（provider 30 vs 25、过滤门 6 vs 5、原因码 8 vs 7、工具轮次上限两套），两套裁决表（E-01 ~ E-11 与 D-1 ~ D-4）只登记差异与判定，**不回改对方页面**。
- **证据**：D-1 ~ D-4（见[源码层事实清单](references/source-code-facts.md#源码层与文档层的四处口径差)）；四处差异**全部是「源码更多」**，无一处「源码更少」。
- **反常识**：直觉上「发现文档与源码不符就该把文档改对」，但这会抹掉「文档站在什么时刻、用什么叙述范围写的」这一信息，且当差异成因未判定时（是「HEAD 未发布」还是「文档未穷举」）贸然改写会引入新错误。
- **行动**：跨信源核验时，差异一律登记为「对象 / 文档口径 / 源码口径 / 锚点 / 差异性质」五列，并保留指向原页面的链接；对「谁更权威」的判断交给**问题类型**而非层级高低。参见 [concepts/17](concepts/17-source-code-verification-playbook.md) 第 1、2 节。

## 官方口径速查表

> 采集日期 2026-10-21，全部条目在 [事实清单](references/official-doc-facts.md) 有对应 F 编号。

| 项 | 官方值 | F 编号 |
|----|--------|--------|
| 项目主体 | Alibaba Group 开源；npm `@alibaba-group/open-code-review`；可执行名 `ocr`；Go 实现 | F-001、F-002 |
| 运行前置 | Git ≥ 2.41、Node.js ≥ 18 | F-003 |
| 状态目录 | `~/.opencodereview/`（`config.json` / `rule.json` / `sessions/`） | F-004 |
| diff provider | 三模式：Workspace(staged+unstaged+untracked) / Commit(`<sha>^..<sha>`) / Range(`merge-base(a,b)..b`) | F-011 |
| 过滤门 | 固定序 binary → user_exclude → user_include → unsupported_ext → default_path；`deleted`/`too_large` 由 `selectFiles` 追加 | F-015、F-018 |
| 语义分组 | 单次 `GROUPING_TASK`，输入仅元数据；单组上限 `maxFilesPerGroup=10`；超限拆单文件组 | F-021~F-023 |
| plan 触发 | 单文件 ≥ `PLAN_MODE_LINE_THRESHOLD=50`，或组内 ≥2 文件且合计 ≥ `PLAN_MODE_GROUP_LINE_THRESHOLD=100` | F-025 |
| main 轮次 | `--effort`：low=1 / medium=2(默认) / high=3；工具轮次上限 `MAX_TOOL_REQUEST_TIMES=100` | F-027、F-029 |
| 退出条件 | task_done / 轮次耗尽 / 连续 3 轮无有效结果 / context 取消 / `addNextMessage` 返回 false | F-030 |
| Prompt 模板 | 6 个：`GROUPING_TASK` `PLAN_TASK` `MAIN_TASK` `MEMORY_COMPRESSION_TASK` `REVIEW_FILTER_TASK` `RE_LOCATION_TASK` | F-031 |
| 记忆压缩 | 三分区 frozen/compress/active；60% 异步、80% 同步；摘要包 `<previous_review_summary>` | F-032、F-033 |
| token 守卫 | 三道：too_large(80%) / `enforceGroupTokenBudget` / 调用前 fail-fast(`MaxTokens * 4 / 5`) | F-018、F-023、F-035 |
| 工具集 | 6 个：`task_done` `code_comment` `file_read` `file_read_diff` `file_find` `code_search`（plan 阶段仅后三个只读可用） | F-036 |
| 规则优先级 | `--rule` > 项目 `.opencodereview/rule.json` > 全局 `~/.opencodereview/rule.json` > 内嵌 `system_rules.json`；首条匹配生效 | F-040、F-045 |
| 内置 provider | **25 个**（anthropic/bedrock/chatgpt/openai/openai-responses/openrouter/gemini/dashscope/dashscope-tokenplan/volcengine/deepseek/tencent-tokenhub/hy-tokenplan/iflytek/kimi/kimi-global/z-ai/mimo/minimax/minimax-cn/baidu-qianfan/siliconflow/siliconflow-cn/novita/xai） | F-049 |
| provider 协议 | **4 种**：`anthropic` / `anthropic-bedrock` / `openai` / `openai-responses` | F-048、F-050 |
| CLI 默认值 | `--audience=human`、`--concurrency=8`、`--timeout=15` 分钟（随 effort 缩放 15/30/45）、`--max-tokens=200000`、`--max-tools=100`、`--max-git-procs=16`、`--max-tokens-budget=0`、`--effort=medium` | F-064 |
| token 上限 | `max_tokens` 只约束提示词；输出上限由 `MAX_COMPLETION_TOKENS=16384` 单独控制 | F-055 |
| 单请求超时 | `OCR_LLM_TIMEOUT` 或 provider `timeout_sec`，默认 300 秒（独立于 `--timeout`） | F-066 |
| 输出契约 | 退出码仅 0/1；`--format json` 恒为恰好一个 JSON 对象；`summary.files_reviewed` / `manifest.terminal_state` / `warnings` | F-068~F-072 |
| scan 路径 | 不依赖 Git diff；`max_tokens=58888`；始终 manifest-less | F-072、F-073 |
| 集成形态 | Agent Skill（默认先询问再改代码）/ Claude Code Command（默认自动修复）/ 委托模式（OCR 端不调 LLM） | F-076、F-088 |
| 委托模式 | `ocr delegate preview` / `ocr delegate rule`；报告字段 `total_files`/`reviewed_files`/`skipped_files`/`coverage_rate` | F-077、F-080 |
| 查看器 | `ocr viewer` 默认 `localhost:5483`；DNS-rebinding 防护 + `OCR_VIEWER_ALLOWED_HOSTS` | F-090、F-091 |
| 遥测 | 默认关闭；exporter `console`/`otlp`；span `review.run`/`diff.parse`/`llm.request` 等；metric `ocr.llm.tokens_used` 等 | F-092~F-094 |
| 基准 | AACR-BENCH 50 仓库/200 PR/10 语言；OCR 榜首 Claude-4.6-Opus v1.3.1 **F1 25.10%**（P 33.90% / R 20.00%）；Claude Code v2.1.169 最高 F1 14.13% | F-096~F-099 |

## 源码层速查表（commit 375f64cd）

> 采集日期 2026-10-21，静态源码阅读，全部条目在[源码层事实清单](references/source-code-facts.md)有对应 F 编号（F-101 ~ F-178）。**未运行 `ocr` 二进制**，行为类条目为「代码中如此声明」。

| 项 | 源码层值 | F 编号 |
|----|---------|--------|
| 信源坐标 | commit `375f64cd`（2026-10-20，`git describe` = `v1.13.2-4-g375f64c`）；模块 `github.com/alibaba/open-code-review`；`go 1.26.9` | — |
| 仓库规模 | 1125 个受控文件；`internal/` 391（19 个子包）/ `pages/` 210 / `extensions/` 160 / `acp/` 117 / `cmd/` 104 | — |
| diff 上下文行数 | `const DiffContextLines = 3` | F-101 |
| provider 层剔除目录 | 11 个前缀（`.idea/`、`.vscode/`、`.svn/`、`.git/`、`vendor/`、`node_modules/`、`target/`、`.happypack/`、`.cachefile/`、`_packages/`、`rpm/`） | F-102 |
| 静态过滤门 | **6 道**：binary → secret → user exclude → user include → 扩展名白名单 → 默认排除路径 | F-112 |
| 排除原因码 | **8 种非空**：`user_exclude`/`unsupported_ext`/`default_path`/`secret_exclude`/`provider_directory`/`deleted`/`binary`/`too_large` | F-115 |
| 白名单 / 排除模式 | 123 项扩展名 / 102 条默认排除模式（`//go:embed` 内嵌 JSON） | F-116 |
| 分组请求体 | 仅 `Model` / `Messages` / `MaxTokens` 三字段，**不含 diff 内容** | F-124 |
| 单组文件上限 | `const maxFilesPerGroup = 10` | F-131 |
| plan 双阈值 | `PLAN_MODE_LINE_THRESHOLD=50` / `PLAN_MODE_GROUP_LINE_THRESHOLD=100` | F-133 |
| 轮次 | `MAX_REVIEW_ROUNDS=2`（effort 覆写 1/2/3）；连续无结果上限 3 轮 | F-134、F-135 |
| 内置 provider | **30 个**（文档层记 25） | F-137、F-138 |
| provider 协议 | 4 种：`anthropic` / `anthropic-bedrock` / `openai` / `openai-responses`；未知协议落到 openai | F-139、F-141 |
| 端点解析顺序 | OCR 配置 → OCR 环境 → Claude Code 环境 → shell rc | F-142 |
| 重试 / 超时 | SDK 重试 5 次；单请求默认 5 分钟；重试报告 `ocr.llm-retry-report/v1` | F-144、F-146、F-147 |
| 内置工具 | 6 个（`task_done`/`code_comment`/`file_read`/`file_find`/`file_read_diff`/`code_search`）+ `unknown` 内部哨兵 | F-152 |
| JSON 输出 | stdout 恒为单个对象，14 个顶层字段，两空格缩进 | F-160 |
| 退出码 | {0, 1}；部分覆盖时仍为 0 | F-162 |
| SARIF | 2.1.0；工具 `OpenCodeReview`；规则集 8 条；指纹域 `ocrFinding/v1` | F-163 |
| 运行清单 | `ocr.run-manifest/v1`；终态 4 种；coverage 5 集合 | F-164 |
| MCP | **仅客户端**（stdio 子进程 + remote Streamable HTTP）；仓库内无 MCP server 实现 | F-167、F-169 |
| 查看器 | `localhost:5483`；5 条 GET 路由；Host 白名单 + DNS rebinding 防护 | F-170、F-171 |
| 遥测 | 默认关闭，`OCR_ENABLE_TELEMETRY=1` 开启；span `llm.request`/`review.run` | F-173、F-174 |
| scan 独立模板 | `MAX_TOKENS=58888` / `MAX_COMPLETION_TOKENS=16384` / `MAX_TOOL_REQUEST_TIMES=60`；manifest 恒 nil | F-175 |
| ACP 适配器 | 独立 Go 模块 `github.com/alibaba/open-code-review/acp`；stdio；`/review` 与 `/scan` | F-176 |
| 宿主插件 | 六宿主（Claude Code / Codex / Cursor / Kimi / OpenCode / QCA）；OpenCode 插件注册 `ocr_review`/`ocr_health` | F-177 |
| 文档站源码 | `pages/src/content/docs/zh/` 18 篇随仓库版本控制，可与实现同 commit 对照 | F-178 |

## ⚠️ 阅读前必知的勘误（11 条）

完整对照见 [官方文档勘误表](references/official-doc-corrections.md)。最常被引用的六条：

1. **内置 provider 是 25 个，不是 19/24 个**；既有 `references/cli-reference.md` 与 `references/llm-providers-detail.md` 的清单不完整（E-01）。
2. **`azure-openai` 是虚构的内置 provider**，官方 25 个清单中无此项（E-02）。
3. **provider 协议是 4 种不是 3 种**：`anthropic-bedrock` 在既有页中缺失（E-03）。
4. **`ocr review` 的 `max_tokens` 默认是 200000**；既有页的 58888 属 `ocr scan` 口径（E-04）。
5. **`--max-tools` 模板默认是 100 不是 30**；且该值只能上调（1–49 → 50）（E-05）。
6. **`--timeout` 默认 15 分钟不是 10 分钟**（E-06）。

## 内容导航

> **两组三章的分工**：**官方文档层（12/13/14）= 官方声明了什么**；**源码层（15/16/17）= 代码此刻实际怎么写的**。两者冲突处按[来源分层与引用规则](#来源分层与引用规则)取信，分歧明细见两张裁决表。**「怎么用 OCR」看 10/11/14 章，本组不是使用手册。**

### 源码层（2026-10-21 新增，commit 375f64cd）

- [源码层运行时模型 — 从 diff 到评论的六段实现链](concepts/15-source-code-runtime-model.md) —— 依据源码重建的运行时实现链：diff 三模式与 provider 层目录剔除、静态六道过滤门与两道追加门、语义分组的元数据契约与降级路径、plan/main 双阈值与三档停止原因；附与官方文档层的九项口径对照
- [源码层扩展契约 — Provider、工具、输出与集成面](concepts/16-source-code-extension-contracts.md) —— 30 个 provider 注册表与四协议四路分发、6 个内置工具的 schema 与参数修复链、JSON / SARIF / manifest 三套输出契约、MCP 仅客户端方向、查看器安全边界、遥测开关与六宿主插件
- [源码层验证与口径裁决手册](concepts/17-source-code-verification-playbook.md) —— 三层引用规则的判据、四处口径差的机械裁决流程、四条源码级可迁移模式（元数据契约式分组 / 单向降级链 / 分层输出契约 / 不可覆盖安全门）、零成本起步的源码核验八步法与三类读者学习路径
- [源码层信源登记（commit 375f64cd）](references/source-code-layer.md) —— 固定信源坐标、仓库拓扑与 `internal/` 19 子包分布、六主题覆盖矩阵与 L1~L4 证据等级、未读边界、锚点定位与计数复核纪律
- [源码层事实清单（F-101 ~ F-178）](references/source-code-facts.md) —— 78 条带行号锚点的客观事实，分六主题采集，无因果推断词；文末列源码层与文档层的四处口径差（D-1 ~ D-4）
- [源码层四视角对抗审查记录（V 阶段）](references/source-code-review.md) —— 魔鬼代言人/新人/老板/未来四视角共 9 条意见、采纳 8 条 + 核查留痕 1 条、V 门判定与 4 条遗留风险

### 官方文档层（2026-10-21 新增）

- [官方运行时模型 — 确定性前置 × 语义后置](concepts/12-official-runtime-model.md) —— 依据官方架构文档重建的运行时心智模型：diff provider 三模式、五重门过滤、语义分组、plan+main 两阶段、五个退出条件、三分区记忆压缩、评论处理五步、三道 token 守卫；附与既有「六阶段」叙述的口径对照
- [集成契约 — 谁调 LLM、谁做分级、谁动代码](concepts/13-integration-contracts.md) —— 四种使用形态（基础 CLI / 委托模式 / Agent Skill / Claude Code Command）的 LLM 归属、分级归属、修复权限与前置条件对照，含选择决策规则与 JSON 输出形状契约
- [可迁移模式与验证手册](concepts/14-verification-playbook.md) —— 三个可迁移模式（确定性前置×语义后置 / 静默前置检查×显式授权门 / 三档退出条件），每个含触发场景、核心步骤、反模式、检验标准与跨场景迁移；附零 LLM 成本起步的六步验证手册与成本—召回调节杆矩阵
- [官方文档事实清单（F-001 ~ F-100）](references/official-doc-facts.md) —— 16 个官方来源编号（S1~S16）对照的 100 条编号事实，分八组采集，无因果推断词
- [官方文档勘误表（E-01 ~ E-11）](references/official-doc-corrections.md) —— 11 条冲突（既有位置 → 既有口径 → 官方口径 → 判定）+ 3 条核对通过 + 4 条引用口径边界
- [四视角对抗审查记录（V 阶段）](references/adversarial-review.md) —— 魔鬼代言人/新人/老板/未来四视角共 6 条意见、采纳结论、V 门判定与 4 条遗留风险

### 概念层（二手迁入，叙述脉络与溯源链有效）

- [核心概念与设计理念](concepts/00-core-concepts.md)
- [Open Code Review 完全指南 — 核心架构](concepts/01-architecture.md)
- [Open Code Review 完全指南 — LLM 协议与 Provider](concepts/02-llm-providers.md)
- [Open Code Review 完全指南 — 内置工具与 MCP 集成](concepts/03-tools-mcp.md)
- [Open Code Review 完全指南 — 审查规则系统](concepts/04-review-rules.md)
- [Open Code Review 完全指南 — 会话持久化、遥测与查看器](concepts/05-session-telemetry.md)
- [Open Code Review 完全指南 — 集成与扩展](concepts/06-integrations.md)
- [关键技术优化](concepts/07-optimizations.md)
- [效果验证与质量评估](concepts/08-effectiveness.md)
- [局限性与对比](concepts/09-limitations.md)
- [安装与配置指南](concepts/10-installation.md)
- [使用流程与命令详解](concepts/11-usage.md)

### 参考层（二手迁入；数值口径受勘误表约束）

- [Open Code Review 完全指南 — CLI 命令参考](references/cli-reference.md)
- [Open Code Review 完全指南 — FAQ 与排错](references/faq-troubleshooting.md)
- [LLM 协议与 Provider 详解](references/llm-providers-detail.md)
- [资源与参考链接](references/resources.md)
- [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](references/wechat-article-source.md)

> 三源整合说明：重复章节（安装、使用流程、FAQ、总结、工具/规则/遥测平铺版）已去重，保留信息量最大的版本。

## 已知边界

- **官方文档层为文档转述**：本次未实际运行 `ocr` 二进制，所有事实均来自官方文档站与官方仓库的静态文本，**未经本地实机验证**；涉及行为语义的条目以「官方文档声明」为限。
- **官方文档站路由有断链**：`/docs/integrations/agent-skill/`、`/docs/integrations/delegate/` 返回「页面找不到了」，实际路径为 `/docs/agent-skill/`、`/docs/delegate/`（E-09）；本次按后者采集。
- **官方仓库不含 `docs/` 目录**：`alibaba/open-code-review` 根目录 13 个 Markdown，文档站为独立前端（F-006），因此架构细节以文档站描述为准。
- **首页统计区为动效占位**：内部活跃用户数、npm 下载量等在抓取时显示为 `0K+`/`0M+` 等占位形态，未采信（F-100）。
- **二手层未逐条重写**：12 概念 + 5 参考页保持原貌，只以勘误表覆盖冲突数值；二手页中的叙述性结论（如「六阶段」提法）与官方术语的差异见 [concepts/12](concepts/12-official-runtime-model.md) 的对照表（E-11）。
- **未覆盖范围**：文档站 15 个可达页面（含 `/docs/chatgpt-preview/`）；贡献指南类页面在站点导航中未发现独立入口。
- **源码层为静态阅读**：本次**未运行 `ocr` 二进制、未调用任何 LLM、未发起任何网络请求**，源码层 78 条事实均为「代码中如此声明」，非实机验证；并发调度实际时序、真实 token 消耗、重试退避表现无证据。
- **源码层 HEAD 领先发布 tag 4 个提交**：`git describe` = `v1.13.2-4-g375f64c`。涉及「发布版行为」的断言应以 `v1.13.2` 为坐标重新核对；D-1 ~ D-4 四处差异的成因（HEAD 未发布 vs 文档未穷举）本轮**未判定**。
- **源码层未读边界**：`acp/internal/` 全部 Go 源码（等级 L3）、`extensions/` 三个 IDE 扩展实现、`*_test.go` 全部测试文件、`internal/llm/client.go` 流式解码区段等，完整清单见[信源登记页](references/source-code-layer.md#5-未读边界)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/00-core-concepts
concepts/01-architecture
concepts/02-llm-providers
concepts/03-tools-mcp
concepts/04-review-rules
concepts/05-session-telemetry
concepts/06-integrations
concepts/07-optimizations
concepts/08-effectiveness
concepts/09-limitations
concepts/10-installation
concepts/11-usage
concepts/12-official-runtime-model
concepts/13-integration-contracts
concepts/14-verification-playbook
concepts/15-source-code-runtime-model
concepts/16-source-code-extension-contracts
concepts/17-source-code-verification-playbook
references/cli-reference
references/faq-troubleshooting
references/llm-providers-detail
references/resources
references/wechat-article-source
references/official-doc-facts
references/official-doc-corrections
references/adversarial-review
references/source-code-layer
references/source-code-facts
references/source-code-review
log
```
