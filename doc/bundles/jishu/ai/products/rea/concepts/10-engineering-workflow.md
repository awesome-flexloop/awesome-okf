---
type: Concept
title: "工程与管理：可审计的重建工作流"
description: "REA 的工程层能力 —— 重建就绪 9 阶段、重建义务台账 build_reconstruction_obligation_ledger、MCP 契约输入 schema profile、安装/Node/客户端/DeepSeek Harness、agent 提示词、工具命名族、测试/CI/发布、6.2 迁移、崩溃记录分析与 CLI 退出码（事实层）"
tags: [rea, reconstruction-workflow, engineering, cli, mcp, testing, migration, crash-analysis, project-profile]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T14:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: docs-full
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/docs"
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
---

# 工程与管理：可审计的重建工作流

> 事实层（How it stays auditable / 工程过程）。本页覆盖事实清单 N 节（F-119~F-131）的工程与管理事实；方法论推导见末尾的事实对应。

## 一句话定位

REA 的深层文档不只描述「命令与工具」，还描述了一整条**可审计的重建工程闭环**：从声明式重建请求（就绪 9 阶段，F-129）到义务核对与闭包摘要（`build_reconstruction_obligation_ledger` + `ledger_id`/`closure_digest`，F-130/F-131），再配合输入契约的 profile 分档（F-120）、版本化发布（F-125）与迁移固化（F-126），把「逆向结果是否可信」形式化为可检查的义务/证据/闭包，让 agent 知道「做到哪一步算完成、什么算证明、什么仍未知」。

## 重建就绪 9 阶段（F-129）

REA 文档把「重建一个应用」拆成 9 个就绪阶段（`reconstruction-readiness.md:35-43`，F-129）：

`discover-classify` / `diagnose-environment` / `declare-request` / `static-analysis` / `reactive-scenarios` / `compare-authority-candidate` / `preserve-contradictions` / `verify-reconstruction-closure` / `export-replay`

这 9 阶段构成从「发现并分类目标 → 环境诊断 → 声明请求 → 静态分析 → 反应式场景 → 与权威候选对比 → 保留矛盾 → 验证重建闭包 → 导出可重放」的递进流程。其中 `verify-reconstruction-closure` 是「做到哪一步算完成」的核对点，`export-replay` 是「可重放」的出产物。

## 重建义务台账 build_reconstruction_obligation_ledger（F-130 / F-131）

为把「未知」「矛盾」显式留痕，REA 提供义务台账机制：

- **输入**：`evidence_bundle`，内含 `artifacts` / `providers` / `environments` / `scenarios` / `captures` / `unknowns` / `records` 数组（F-130）。
- **输出**：结果含 `ledger_id` 与 `closure_digest`（F-130），标识包括限制与未闭合义务在内的完整结果。摘要存在不证明闭包完成；空 Evidence 请求也会返回零义务的 `unknown` 台账。
- **入口**：`build_reconstruction_obligation_ledger`（MCP 工具），CLI 侧为 `rea build-reconstruction-obligation-ledger`（F-130）。
- **内部结构**：台账的 `manifest` 对象含 `bindings` / `contradictions` 数组；`required_case_kinds` 数组可含 `positive` / `negative` / `malformed` / `cancellation`（多态用例种类，F-131）；`reviewed_obligations` 含 `obligation_id` / `obligation_version` / `title` / `application_layer` / `family` 字段（F-131）。

这与洞察六的「声明式重建请求 → 分阶段执行 → 义务核对 → 闭包摘要 → 可重放」闭环对应（见本文末尾勾连）。

## MCP 契约输入 schema profile（F-120）

为适配模型提供方的工具定义大小限制，REA对广告输入JSON Schema提供profile分档（F-120）：

- `REA_MCP_INPUT_SCHEMA_PROFILE`默认`full`，完整广告保持不变。
- 可选`compact`将每个广告输入schema限制在**13,312字节**；删除嵌套描述、examples、defaults、titles，保留根描述，并在预算内展开schema-local refs。
- 六个复杂工具可约化嵌套验证广告，但工具全集、输出schema、annotations和canonical服务端验证不变；不是固定“9字段/24字段”分档。

设置在服务启动时读取，改动需重启。它不压缩真实Evidence，也不减少canonical请求的必填参数。

## 安装 / Node / 17 客户端 / DeepSeek Harness（F-119 / F-121 / F-122）

- **Node运行时**要求`^22.19.0 || ^24.11.0 || >=26.0.0`，不能只按主版本判断（F-119）。
- **客户端覆盖**：17个文件型ID为`claude_code`/`claude_desktop`/`codex`/`cursor`/`gemini_cli`/`windsurf`/`devin`/`opencode`/`antigravity`/`copilot_cli`/`commandcode`/`qwen_code`/`vscode`/`grok_build`/`omp`/`pi`/`hermes`。源码额外登记`grok_bot`，但其连接器需账户内手动配置，故是18登记而非18文件型配置（F-121）。
- **DeepSeek Harness 集成**：需 `@deepseek-ai/dsh@0.2.0-rc.2`；配置文件路径为 `$DSH_HOME/cordis.patch.yml`；`REA_MCP_INPUT_SCHEMA_PROFILE` 支持 `compact` / `full`（`installation.md:260,271,306-307`，F-122）。

## agent 提示词 6 个（F-119）

`mcp-prompts.md` 提供 **6** 个 agent 提示词（`mcp-prompts.md:9-14`，F-119）：

`investigate_feature` / `compare_application_versions` / `verify_reconstruction` / `trace_crash` / `audit_residual_unknowns` / `prepare_bounded_process_capture`

这 6 个提示词对应典型重建任务：特性调查、版本对比、重建验证、崩溃追踪、残留未知审计、有界进程捕获准备。

## 工具设计命名族（F-123）

`tool-design.md` 给出工具命名族（`tool-design.md:16-22`，F-123）：

`inspect` / `search` / `trace` / `compare` / `workflow` / `observe` / `capture`

即工具命名遵循一组动词族（检查/搜索/追踪/对比/流程/观察/捕获），使工具分层之间的关系可预期。

## 测试 / CI / 发布（F-124 / F-125）

- **测试与 CI**（`testing.md`，F-124）：
  - `verify:deepseek-client` 需 `@deepseek-ai/dsh@0.2.0-rc.2`。
  - 多数job读取`.nvmrc`的Node24.18.0，路径边界专项另用22.19.0；package矩阵按变更选择Linux/macOS的x64/arm64。
  - Ghidra接受12.1.x，记录基线12.1.4/JDK21；JDK上下界以安装中的`application.java.min/max`为准。
  - Hopper FAT/FAT64轨道记录6.1.0-demo，仅证明REA prepared FAT64 workflow，不证明Hopper原生FAT64 loader支持。
  - IDA已记录Windows x64 9.3、macOS arm64 headless Professional9.1 build9.1.250226；modern supervisor固定`c133c3853faa111a9b00ee615c013b720d0c4acd`，legacy attached GUI为upstream1.4.0。Linux headless、modern attached GUI、其他版本/架构及真实HTTP supervisor仍未验证。
- **发布策略**（`releasing.md`，F-125）：Release Please 使用 `always-bump-minor`；版本格式 `v${major}.${minor}.${patch}`，预发布 `v${major}.${minor}.${patch}-${prerelease}`。

## 6.2 迁移（F-126）

`migration-6.2.md` 定义了迁移固化点（F-126）：

- `evidence` 字段的 MCP wrapper 已移除。
- `analysis_profile` 由可选变为**必填**。
- 迁移工具路径为 `tools/migration-6.2.mjs`。

## 崩溃记录分析（F-127）

`recorded-crashes.md` 定义已记录崩溃的分析约定（F-127）：

- `inspect_recorded_crash` 使用 27-register 扩展 ABI。
- `mcp_inspect_recorded_crash` 支持 `compact` / `full` profile。
- 测试环境为 pwndbg 2026.09.15 + GDB 13.1。

## CLI 退出码（F-128）

CLI 退出状态码约定（`cli.md:206-209`，F-128）：

- `0` 成功
- `1` 一般错误
- `2` 分析错误
- `3` 证据保留错误

进程化调用者在自动化场景可据此区分成功/一般错误/分析错误/证据保留错误。

## 勾连：与洞察六的事实对应

本文是方法论点 [references/insights.md](../references/insights.md)「洞察六（重建工程工作流）」的**事实层**。洞察六的结论「REA 正从『一次性逆向工具』走向『可审计的重建工程工作流』」由本文的下列事实支撑：

- 重建就绪 9 阶段（F-129）→ 声明式重建请求与分阶段执行
- 义务台账 `build_reconstruction_obligation_ledger` + `ledger_id`/`closure_digest`（F-130）→ 义务核对与闭包摘要
- 台账 `required_case_kinds` 多态、`manifest` 的 `bindings`/`contradictions` 与 `reviewed_obligations`（F-131）→ 义务与矛盾显式留痕
- MCP输入schema profile（F-120）→ 广告schema的兼容性分档，不改变真实Evidence与canonical验证
- 6.2 迁移固化 `analysis_profile` 必填（F-126）→ 契约演进与迁移治理
- Release Please `always-bump-minor`（F-125）→ 每次新能力上 minor，契约演进节奏统一

若需要带具体步骤的重建工作流走查，可参见 [示例索引](../examples/index.md)。

## 阅读下一篇

- [回到 REA 概念索引](index.md)——按知识地图回到 01~09 各篇
- 示例侧：[重建工作流](../examples/reconstruction-workflow-example.md)提供 9 阶段与义务台账的走查，命令未在本机实跑。
