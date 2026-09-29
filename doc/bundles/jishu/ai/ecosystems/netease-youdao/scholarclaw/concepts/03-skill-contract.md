---
type: concept
title: SKILL.md 技能契约与调用时序
description: "SKILL.md 面向 LLM 的五重契约：触发条件、响应时间期望、SSE 事件过滤、博客异步三步法、重试退避策略，以及与 shell 实现层常量的差异。"
tags: [scholarclaw, skill, llm-contract, sse, retry, polling]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: ScholarClaw 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: ScholarClaw 架构洞察
---

# SKILL.md 技能契约与调用时序

`SKILL.md`（frontmatter：`name: scholarclaw`、`version: 1.4.1`、`official: false`）（F-sc-043）承担的不是 README 式说明，而是**面向 LLM 的运行时契约**：任何遵循该文档的 LLM 客户端都能正确驱动远端服务，无需 SDK。理解这一点是正确集成 ScholarClaw 的前提（参见 [/concepts/00-overview.md](/concepts/00-overview.md)）。

## 五重契约

### 1. 触发条件

SKILL.md 声明：学术场景（论文检索、文献调研、学术问答等）下应使用本 skill 替代 web-search（F-sc-044）。这意味着该 skill 预期被宿主 Agent 的 skill 路由机制加载——评估其效果时应放在 Agent 的 skill 选择链路中，而非孤立测试单条命令。

### 2. 响应时间期望

SKILL.md 给出分场景的响应时间期望表，区分简易搜索、AI 模式、博客生成等场景的耗时预期（F-sc-045），约束 LLM 的等待与降级决策。能力清单共 7 项（F-sc-049）。

### 3. SSE 事件契约：少即是多

SSE 流中仅提取 `final_response` 与 `response_chunk` 两类事件；`session_start`、`tool_call_*` 事件被忽略（F-sc-046）。这不是功能缺失，而是刻意约定——LLM 只需消费两类事件即可完成 SOTA 对话；其余事件留给需要过程可视化的场景（`benchmark_chat.sh -s` 的 SSE 模式则原样透传，见 F-sc-038）。SSE 消费端只解析这两类事件名，其余事件记录后丢弃，不要因出现未知事件而中断解析。

### 4. 博客异步三步法

博客生成按「提交 → 轮询任务状态 → 获取结果」三步执行（F-sc-047），对应 TS 侧 `submitBlog()` → `getBlogTask()` → `getBlogResult()` 三个路由（F-sc-015、F-sc-016），shell 侧 `blog_submit.sh` → `blog_status.sh` → `blog_result.sh` 三个脚本（F-sc-035、F-sc-036）。SKILL.md 约定**轮询间隔 10–15 秒、最多轮询 40 次**（最坏约 10 分钟）。分步演练见 [/examples/blog-three-step-pipeline.md](/examples/blog-three-step-pipeline.md)。

### 5. 重试退避策略

HTTP 503/504 按 2s、4s、8s 指数退避重试，最多 3 次；HTTP 400/404 不重试（F-sc-048）。建议把重试语义实现为可配置策略对象（retryable=[503,504]、backoff=[2,4,8]、max=3、non_retryable=[400,404]），而非散落的状态码 if-else，便于与服务端演进解耦。

## 契约层 vs 实现层：两套时序各自演进

一个关键事实：SKILL.md 的轮询约定（10–15s × 40 轮）与 `blog.sh` 的实现常量（`POLL_INTERVAL=5` 秒、总超时 600 秒）**不一致**（F-sc-047、F-sc-037）。这不是疏漏，而是架构的真实面貌：SKILL.md 面向"下一代调用方"（LLM），shell 脚本面向"上一代调用方"（人类/CI），两代调用方允许各自演进，**契约层才是 skill 的长期稳定面**。自研 LLM 客户端时，以 SKILL.md 的时序参数为准，不要照抄 `blog.sh` 的 5s 常量；两者冲突时契约层优先。

## 配置与依赖声明

- 配置取值优先级声明：环境变量 > OpenClaw 配置 > 配置文件 > 默认值（F-sc-050），与 `common.sh` 的取值优先级（环境变量 > 配置文件 > 默认值，F-sc-030）层次不同——前者多了宿主工具（OpenClaw）配置层。
- Dependencies 节声明：`curl` 必需、`jq` 可选（F-sc-051）。

## 配套示例文档

`examples/` 目录含 4 个示例文档（F-sc-052）：`basic-search.md` 演示通用搜索命令与响应 JSON 形状（F-sc-053）；`scholar-search.md` 演示学术搜索（`scholar.sh`）用法，含查询分析模式调用示例与响应结构（F-sc-054）；`sota-chat.md` 演示 SOTA 对话（SSE 流式）场景的命令与事件序列（F-sc-055）；`blog-generation.md` 演示博客生成的异步提交流程、轮询与结果获取的命令序列（F-sc-056）。

## 相关概念

- [/concepts/00-overview.md](/concepts/00-overview.md)
- [/concepts/02-shell-toolchain.md](/concepts/02-shell-toolchain.md)
- [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)
- [/examples/blog-three-step-pipeline.md](/examples/blog-three-step-pipeline.md)
- [/examples/scholar-search-walkthrough.md](/examples/scholar-search-walkthrough.md)
