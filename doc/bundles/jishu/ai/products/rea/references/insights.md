---
type: Reference
title: "REA 架构洞察（insights）"
description: "REA 的十项架构与官网调查洞察，以及基础、上手、实验和重建验证学习路径"
tags: [rea, insights, mcp, reverse-engineering, knowledge-map]
generated:
  by: source-code-to-okf-wiki:I
  at: "2026-10-12T10:00:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    resource: "https://rea.tools/zh-CN/"
  - id: rea-run
    resource: "https://rea.run/zh/"
  - id: official-site-full
    resource: official-site-source.md
---

# REA 架构洞察（insights.md）

> I 阶段分析。基于 R 阶段事实清单 F-001~F-180（`references/facts.md`）。四元组结构：**陈述 → 证据（引用具体 F-xxx）→ 反常识 → 行动**。
> 信源：本地源码 `external/dao/rea`（固定 commit `eaf88aca`，npm 包 `rea-agents` v6.4.0）+ 官方文档 `rea.tools` + 补充信源 `rea.run`。
> **范围说明**：洞察一~四于 2026-10-12 首轮生成（依据 F-001~F-066）；同日 docs/ 全量深层扩展后（F-067~F-131），在既有论述上追加洞察五（专项工具适配深度与版本钉扎）与洞察六（重建工程工作流），并更新知识地图。

> **已沉淀模式**：洞察一（统一契约工具编排层）及其支撑机制（洞察二契约单一事实源、洞察三前端投影）已于 2026-10-12 独立化为方法论模式库正式条目 [统一契约工具编排层](../../../../../../../../../docs/retrospective/patterns/methodology-patterns/product-growth/unified-contract-tool-orchestration-layer.md)（L1-draft）。本页保留为**案例版**（含具体 F-xxx 证据与八大目标域明细）；跨场景可复用版见模式库条目。

---

## 洞察一：REA 不自做反编译——它是一层「逆向工具统一证据契约」编排器，不是逆向工具本身

**陈述**：REA 的定位不是又一个反编译器，而是一层**适配编排层**：它把用户自备的逆向工具（原生二进制域的 Ghidra/IDA/Hopper，Android 域的 JADX/Apktool/ADB，字节码域的 EVM/WASM 等）通过 Provider 适配器接入一个统一的 MCP 服务，再向 AI agent 暴露 100+ 个契约化工具（TOOL_CONTRACTS 聚合）。真正的分析计算发生在被适配的工具内，REA 的职责是把「工具结果 + 静态元数据 + 运行时观测」规整为可被 agent 消费的证据，让一个 agent 只经一套 `io.github.morluto/rea` MCP 服务就能覆盖 native/Android/.NET/EVM/WASM/固件/网站/进程等目标域。

**证据**：
- F-030 / F-031 / F-032：Ghidra、IDA、Hopper 分别由 `GhidraProvider`、`IdaProvider`、`HopperProvider` 实现，类名带 `Client/Launcher/Transport/Doctor` 与 `BridgeLauncher`，说明是**外部工具具柄**而非内置引擎。
- F-033~F-041：JEB/ADB/JADX/Apktool/EVM/WASM/.NET/Browser/Firmware 各有独立 Provider 文件（`src/jeb/`、`src/adb/`、`src/android/`、`src/apktool/`、`src/evm/`、`src/wasm/`、`src/dotnet/`、`src/browser/`、`src/firmware/`），依赖第三方引擎（如 evmole、WABT、Binwalk/Unblob、playwright-core）。
- F-042：原生 Provider 统一实现 `AnalysisProviderCandidate` 接口——说明存在**可插拔适配器契约**，而非硬编码单一路径。
- F-019~F-024：所有能力聚合到单一 `TOOL_CONTRACTS`（24 组 spread），对外呈现为一个 MCP 服务（mcpName `io.github.morluto/rea`，F-004）。
- F-011：`scripts/rea.mjs` 在一套 CLI 下同时提供 MCP 服务模式与 one-shot 模式。

**反常识**：很多人看到「逆向工程」会默认 REA 自己写反编译器/调试器。实际恰好相反——REA 的「厚度」不在分析引擎，而在**编排与证据标准化**。它的价值主张是「一个 agent、一套 MCP、多种目标」：与其让 agent 分别学 Ghidra 脚本、ADB 命令、evmole 接口，REA 把它们统一成同构的工具名与证据返回（evidence/unknowns 结构，F-043），从而把 agent 的学习成本从「每工具一套协议」降为「一套 REA 契约」。这也解释了为何它对用户是**本地优先 + 自带工具**（F-050 进程捕获「非沙箱」，依赖调用方选择的命令）。

**行动**：
- 评估 REA 时，先确认你是否已有 Ghidra/IDA/Hopper 等分析工具；REA 不绑定分析引擎，但它会让你的 agent 通过 MCP 统一调用它们。
- 想深挖某个目标域时，从对应 Provider（`src/ghidra/`、`src/evm/`、`src/android/`…）入手，而不是从 CLI 命令入手——Provider 才是与工具的真实接口面（含 bridge 脚本，如 Hopper 的 `bridge/hopper_bridge.py`，F-032）。
- 新增目标域支持时，参照 `AnalysisProviderCandidate`/`*Provider.ts` 的适配器模式 + `TOOL_KINDS` 新增一个 kind（F-023），而非在 CLI 层硬塞命令。

---

## 洞察二：统一 MCP 契约是系统的「单一事实源」——CLI 与运行时能力都由它派生

**陈述**：REA 的能力边界不是散落的命令，而是集中在**契约层** `src/contracts/`。`TOOL_CONTRACTS` 以只读 `as const` 数组聚合 24 组工具契约（官方代理、增强、native、EVM、WASM、ADB、Firmware 等），每组又由 `ToolContract<Name, InputSchema, OutputSchema>` 类型约束（含 name/kind/inputSchema/outputSchema/effects）。CLI 的 129 个顶层命令通过 `CLI_COMMAND_TOOL_ALIASES` 映射到这些契约工具（F-016），MCP 运行时直接消费这些契约。会话健康/工具可用性的权威来源是 `binary_session`（F-029）。

**证据**：
- F-020 / F-021：`TOOL_CONTRACTS` = 24 组 spread，聚合自 24 个导入变量（`OFFICIAL_TOOL_CONTRACTS`、`ENHANCED_TOOL_CONTRACTS`、`NATIVE_TOOL_CONTRACTS`、`EVM_TOOL_CONTRACTS`…）。
- F-022：统一类型 `ToolContract<Name, InputSchema, OutputSchema>` 定义契约字段。
- F-013 / F-016：CLI 顶层命令 129 个，`CLI_COMMAND_TOOL_ALIASES` 把 `analyze→binary_overview`、`decompile→procedure_pseudo_code` 等命令映射到契约工具。
- F-017：存在`MCP_TOOLS_WITHOUT_DEDICATED_CLI`，说明工具与专用命令不一一对应；CLI另含setup等管理入口，不能把两种对象简单作包含集合比较。
- F-029：`binary_session` 是运行中服务目录身份与「当前哪些工具可用」的权威来源。

**反常识**：多数 CLI 工具的架构是「命令是主体，内部调用共享函数」。REA 反其道而行——**契约（MCP 工具定义）是主体，CLI 只是契约的一个前端投影**。证据是存在大量「只有 MCP 工具、没有 CLI 命令」的能力（F-017），以及 CLI 命令名与 MCP 工具名并不一一对应、需要别名映射（F-016）。这意味着：真正理解 REA 能力全集，应读 `src/contracts/` 而非 `src/cliCommandNames.ts`；CLI 只是为了让习惯终端的用户能手动触达部分能力，MCP 才是 agent 的主通道。

**行动**：
- 查看 REA 支持「什么」，以 `TOOL_CONTRACTS` 聚合清单为准（F-019~F-024），按 kind/子域分组浏览，而非数 CLI 命令。
- 写一步分析任务时，优先通过 MCP 工具名（如 `binary_overview`、`procedure_pseudo_code`）而非 CLI 命令来思考——后者只是前者的别名投影。
- 完整工具定义及输入/输出schema读`tools/list`；活动服务身份、Provider绑定和分组可用性读`binary_session`（F-029），两者不可替代。

---

## 洞察三：CLI 与 MCP 是同一内核的双入口——「安装一次，两端同源」

**陈述**：REA 不区分「CLI 用户」与「MCP 用户」：安装一个 npm 包 `rea-agents`（bin 同时注册 `rea` 与 `rea-agents`，F-010），`scripts/rea.mjs` 用一个布尔判定决定入口——单参 `--mcp`/`mcp` 进入 MCP 服务模式（加载 `dist/mcp/main.js`），否则进入 one-shot CLI 模式（加载 `dist/cli.js`）；`mcp doctor` 走 `dist/mcpDoctor.js`（F-011）。命令在两种模式下共享同一套契约与 Provider（F-016 别名映射、F-018 CLI 由 `createCli()` + 各 `registerXxxCommands()` 构建）。官方安装指引为 `npx rea-agents setup`，随后可配置到 Claude Code/Codex/Cursor/Gemini CLI/Grok Build 等多个 agent 客户端。

**证据**：
- F-010：bin 同时注册 `rea` 与 `rea-agents`，指向同一脚本 `scripts/rea.mjs`。
- F-011：`scripts/rea.mjs` 双层路由（`--mcp`/`mcp` 进 MCP，其余进 CLI），MCP doctor 单独加载。
- F-004 / F-006：最终对外只有**一个** MCP 服务名 + 统一 CLI，符合「二端一端」语义。
- F-018：CLI 命令族通过 `registerXxxCommands()` 注册，与 MCP Provider 同层复用。
- 官方安装/接入多客户端路径：`docs/`（README_zh 佐证 `npx rea-agents@latest setup` 与接入 Claude Code/Codex/Cursor/Gemini CLI/Grok Build）；直接执行 `rea` 另要求 PATH 中有全局安装入口。

**反常识**：业界常把「CLI 版」和「MCP 版/服务版」拆成两个产品两个安装（甚至两个 npm 包）。REA 用一个包、一次 `setup` 覆盖两条入口，且命令名与工具名同源映射。对用户的价值是**低迁移成本**：可以先在终端手动 `rea analyze ./target`（F-056）实验，再把它接入 IDE/agent 走 MCP，命令与工具语义保持一致，学习一次即可两处使用。

**行动**：
- 上手顺序：`npx rea-agents@latest setup`配置并重启客户端；没有全局安装时，单次CLI用`npx rea-agents@latest analyze <path>`。只有已全局安装且bin在PATH中时才直接用`rea`；setup不等于获得全局CLI。
- 若你只用自动化/agent 场景，仍建议先跑一次 CLI 冒烟——它能暴露 Provider 是否就绪（doctor 类命令），比直接走 MCP 更好排障。
- 记住命令名与 MCP 工具名的映射并非 1:1（F-016/F-017）；在 agent 端应直接使用工具名全集，而非依赖 CLI 命令名。

---

## 洞察四：广度覆盖但保持「本地优先、显式选择、有界证据」——逆向属于用户资产，REA 只做规整

**陈述**：REA 覆盖极广的目标域——native 二进制、JavaScript/Electron 应用、.NET 程序集、Android APK/设备、EVM 字节码、WASM 工制、固件、网站（F-055），并且设计刻意保持**本地优先**与**有界证据**：进程捕获运行调用方选择的命令并记录有界文件系统状态、声明**非沙箱**（F-050）；网站分析通过 CDP 附加到用户自有的浏览器、「被动逆向、非通用自动化」（F-051）；WEB 网络捕获为离线操作、不重新拉取 URL（F-053）；WASM 检查「不执行 WASM」（F-045）。同时把「什么被分析、覆盖到哪、还有哪些未知」随每条结果上报（F-043）。

**证据**：
- F-055：官网目标域概括「native binaries, JavaScript and Electron apps, .NET assemblies, Android packages, firmware, and websites」。
- F-050：Process Capture「非沙箱」，记录进程生命周期与有界文件系统状态。
- F-051：网站分析「被动逆向而非通用浏览器自动化」，页面留在用户浏览器进程内。
- F-053：`inspect_web_network_capture` 为离线操作，检查保留的 HAR，不重新拉取 URL、不启动浏览器/proxy。
- F-045：WASM 工制检查「不执行 WASM」，用 WABT 静态检查。
- F-043：结果报告 evidence、目标身份、覆盖率与 unknowns。

**反常识**：本地优先不等于无副作用。静态读取、附着已有运行时与主动启动目标是不同契约：Process Capture启动命令，Electron/Browser场景可管理生命周期与动作，ADB可安装或传输文件；导出也会写入文件。应按所选命令评估权限、网络、资源与清理，不能统称“不动资产、不托管、不联网”。本地工具部署也不保证模型客户端不上传证据。

**行动**：
- 安全评估时注意：REA 本身不虚拟化/沙箱化目标；分析目标的可信性与隔离由「你选的分析工具 + 你的命令」决定（F-050 非沙箱）。
- 网站观察附着已启动浏览器，HAR检查读取保存文件；Process Capture则启动选定命令，不能统称“默认离线附着”（F-050/F-051/F-053）。
- 判断结果时核对目标身份、覆盖范围、推断来源和矛盾；unknowns数量少不能单独证明结论可靠。

---

## 洞察五：对「分析工具」不是浅接一层，而是做深——专项 Ghidra 呈现逐格式/逐 ABI 的深度适配矩阵与版本钉扎

**陈述**：洞察一指出 REA 是「适配编排器」、不绑定分析引擎。docs 全量深层扩展进一步证明：REA 对每个被适配工具的接入**深度可观**，尤其 Ghidra 体现为「逐文件格式/逐架构/逐 ABI」的专项支撑矩阵——有 DOS MZ/COM 专项（`MzLoader` + `x86:LE:16:Real Mode`，F-090）、MIPS32r2/FPMips16/semi-float 专项（F-091/F-092）、PSP Allegrex 专项（`PspElfLoader` + `Allegrex:LE:32:default`，F-093）、.NET 8 NativeAOT（Washi1337/ghidra-nativeaot 上游分支，F-094）、Windows x64 P0 只读（25 个只读操作，F-096）。同时 IDA/JEB/Apktool/JADX 各有文档化的版本与 endpoint（F-097~F-102）。

**证据**：
- F-090：DOS 用 `MzLoader`/`BinaryLoader`、语言 `x86:LE:16:Real Mode`、COM offset zero→`1000:0100`。
- F-091/F-092：MIPS 要求 `EF_MIPS_ARCH_32R2`、拒 `EF_MIPS_FP64`/`EF_MIPS_NAN2008`，soft-float 原型策略键 `o32-soft-float-prototype-v1`。
- F-093：PSP 用 PSPDEV v20261001 + Ghidra 12.1.3 + extension v21.4 + `PspElfLoader`。
- F-094：NativeAOT 钉到上游 commit `effeb734…`，交叉核对 .NET MethodTable.h commit `a3b2d403…`。
- F-096：Windows P0 提供 25 个只读操作、MCP `timeoutMs` 默认 300000。
- F-097~F-102：IDA 钉上游 `1.4.0 legacy tools`、JEB 默认 `127.0.0.1:8425/mcp`、Apktool 2.7.0 等验证版本。

**反常识**：以为 REA 对工具只是「调用一下」是低估——它对排他性工具做了**多轮验证环境**（版本、语言、loader、上游 commit 全部文档化钉死，既能 `npm run verify:ghidra:windows` 等回归，又能防止上游行为漂移破坏解析）。这种「版本钉扎 + 专项 loader + 逐 ABI」的深度，是 REA 能稳定跨格式的关键，也是它比直接让 agent 调 Ghidra 脚本更有价值的原因之一——它把「血泪踩坑」沉淀为可复现的固化配置。

**行动**：
- 想给某个排他性格式（DOS/PSP/NativeAOT…）加支持时，参照既有专项文档模式：固定 loader + 语言/compiler + 上游 commit + `verify` 命令 + 资源限制，四件套齐备才算「适配完成」。
- 升级被适配工具（如 Ghidra 12.1.x）前，注意 REA 的专项文档与 `npm run verify:*` 是否仍通过——版本进度可能导致专项语言/loader 失配。

---

## 洞察六：REA 正从「一次性逆向工具」走向「可审计的重建工程工作流」——有就绪阶段、义务台账与闭包摘要

**陈述**：docs 深层揭示了 REA 文档中大量「工程过程」性质的能力：重建就绪分 **9 阶段**（`discover-classify`→`export-replay`，F-129）；有「重建义务台账」`build_reconstruction_obligation_ledger`，接受含 `artifacts/providers/environments/scenarios/captures/unknowns/records` 的 `evidence_bundle`，输出 `ledger_id`/`closure_digest`（F-130），台账里的 `required_case_kinds` 可含 `positive/negative/malformed/cancellation`（F-131）；MCP 契约输入 schema 有 `compact`/`full` 分档（`REA_MCP_INPUT_SCHEMA_PROFILE`，compact 预算 13,312 字节，F-120）；6.2 迁移中 `evidence` wrapper 移除、`analysis_profile` 变必填（F-126）；发布用 Release Please `always-bump-minor`（F-125）。这些共同构成一套「声明式重建请求 → 分阶段执行 → 义务核对 → 闭包摘要 → 可重放」的工程闭环。

**证据**：
- F-129：reconstruction-readiness 9 阶段命名（verify-reconstruction-closure / export-replay 等）。
- F-130/F-131：义务台账输入输出 schema、`required_case_kinds` 多态、binding/contradiction 清单。
- F-120：默认full，可选compact限制广告输入schema预算；不改变真实Evidence、工具全集或canonical服务端校验。
- F-126：6.2 迁移固化 `analysis_profile`。
- F-125：`always-bump-minor` 保证每次新能力都上 minor，契约演进节奏统一。

**反常识**：把一个「逆向 CLI」文档写得像**工程规范**（阶段、义务、闭包、迁移）是很反直觉的——多数逆向工具只给「命令参考」。REA 的文档层明显借鉴了「重建即工程」的思维：它把「逆向结果是否可信」形式化为可检查的**义务/证据/闭包**，让 agent 知道「做到哪一步算完成、什么算证明、什么仍未解决」。这与洞察二「契约单一事实源」一脉相承：不止工具签名是契约，**重建过程本身也是契约**。

**行动**：
- 按9阶段（F-129）核对重建义务。`verify-reconstruction-closure`是阶段名称，不在此当作已核对的CLI命令；`closure_digest`可标识未闭合台账，须继续检查状态、未知项与矛盾。
- 长流程分析优先用 `evidence_bundle` + `reconstruction-obligation-ledger`（F-130）收口，把「未知项」「矛盾」显式留痕，而不是只拿一条 `binary_overview` 结果当结论。

---

## 知识地图

### 概念文档分组规划

| 编号 | 文件名 | 标题 | 覆盖事实（F-xxx） | 前置依赖 |
|------|--------|------|------------------|---------|
| 01 | 01-rea-overview.md | REA 是什么：产品身份与定位 | F-001~F-009, F-055, F-006 | 无 |
| 02 | 02-mcp-contract.md | MCP 契约层：单一事实源与工具全集 | F-019~F-029, F-004 | 01 |
| 03 | 03-provider-adapters.md | Provider 适配器：如何接入分析工具 | F-030~F-042, F-023 | 01 |
| 04 | 04-analysis-domains.md | 支持的分析目标域与工具矩阵 | F-043~F-056 | 03 |
| 05 | 05-cli-and-setup.md | 安装、setup 与 CLI/MCP 双入口 | F-010~F-018, F-056 | 01, 02 |
| 06 | 06-domain-types-and-evidence.md | 领域类型与证据模型 | F-057~F-066, F-058, F-043 | 02, 03 |
| 07 | 07-js-web-domains.md | JavaScript 应用图与 Web/浏览器域 | F-067~F-082 | 04 |
| 08 | 08-native-ghidra-specialty.md | Native 与专项 Ghidra 深度适配 | F-083~F-096 | 03 |
| 09 | 09-platform-domains-deep.md | 平台分析域深层（Android/ADB/.NET/固件/Apple/Electron/Harmony） | F-103~F-118, F-097~F-102 | 03, 04 |
| 10 | 10-engineering-workflow.md | 工程与管理/重建工作流 | F-119~F-131 | 06 |

> **说明**：concepts 文档以「Facts 聚合 + 学习路径」为依据划分，覆盖是什么（01）、怎么工作（02/03/06）、能分析什么（04/07/08/09）、怎么用（05）、工程过程（10）。文档 07~10 为 2026-10-12 docs/ 全量深层扩展后追加，吸收 F-067~F-131（docs 深层事实）；01~06 覆盖范围保持不变。

### 学习路径

1. **入门（理解是什么）**：01 → 02
   - 先建立 REA 产品全局视图（npm 包、版本、授权、MCP 服务名、目标域概览），再进入契约层理解「工具全集从哪来」。
2. **核心（理解怎么工作）**：03 → 06
   - 掌握 Provider 适配器为何能统一外部工具，再看领域类型与证据模型如何把结果结构化（这是洞察一/二/四的底层支撑）。
3. **应用（理解能分析什么）**：04
   - 按目标域（native/EVM/WASM/Android/.NET/固件/网站/进程）查工具矩阵与边界。
4. **实践（理解怎么用）**：05
   - 最后看安装、setup 与 CLI/MCP 双入口，把前面理解落地成一条实际可跑的流程。
5. **深层（docs 全量扩展）**：07 → 08 → 09
   - 分别深入 JavaScript/Web 域、Native/专项 Ghidra、平台分析域的精确工具/版本/限制/环境变量细节；08 与 09 需以 03/04 为基础。
6. **工程（理解过程可信度）**：10
   - 掌握重建就绪 9 阶段、义务台账、evidence_bundle 收口与 MCP profile 机制，把「分析」提升为「可审计重建」。

### 示例文档规划

| 文件名 | 标题 | 内容要点 |
|--------|------|---------|
| cli-and-mcp-usage.md | CLI 与 MCP 使用示例 | `npx rea-agents@latest setup`、带实际目标路径的 analyze/inspect/decompile/function 调用与 PATH 条件；接入 agent 的 MCP 配置 |
| provider-setup.md | 分析工具安装与 Provider 接入 | Ghidra/IDA/Hopper/JADX/ADB/EVM/WASM/固件工具链的本地准备与 doctor 校验 |
| js-reconstruction-example.md | JavaScript 应用重建示例 | `analyze_javascript_application` + 应用图 + 运行时协同 + 完整性策略的实际走查（F-067~F-076） |
| platform-deep-example.md | 平台深层分析示例 | Apple bundle / Electron / HarmonyOS / Android / 固件 的代表性 CLI 命令与限制（F-103~F-118） |
| reconstruction-workflow-example.md | 重建工程工作流示例 | 九阶段说明与合法空台账集成请求，不是实际应用完整重建（F-129~F-131） |
| showcase-cases-example.md | 五项官网案例证据 | 对照目标版本、输入集、检查对象及剩余义务（F-153~F-172） |
| notes-first-investigation.md | Notes首次调查 | 静态IPC路径与独立formatter验证（F-141~F-144） |
| official-site-labs.md | 官网教学实验 | 计算器、恐龙与TOTP的规则、固定输入及重建范围 |

## 第四轮官网洞察

### 洞察七 先选证据问题再选目标域

- 陈述：入门从“导出后文件在哪里、字段是什么”开始，比从工具目录开始更容易检验答案。
- 证据：F-137~F-145。Notes把按钮、IPC、文件写入与formatter各自放到可检查的位置；浏览器例只证明窗口内请求。
- 反常识：静态关系图能帮助定位，但不会自动证明按钮完整执行；返回零歧义也不等于运行成功。
- 行动：安装完成后先走Notes静态调查，再独立执行formatter；涉及网页时先定义需要观察的动作与窗口。

### 洞察八 验证必须带对象和输入范围

- 陈述：相同“通过”字样背后可能是函数行为、编译字节或目标运行，不能合并成一种成功。
- 证据：F-155的DX-Ball函数用例，F-157~F-158的Notion partial/stub，F-162的Aegis Java harness，F-169的CTF原程序，F-172的TH04完整extent。
- 反常识：133例一致不等于APK运行，2139字节匹配不等于全游戏；候选满足约束不等于唯一解。
- 行动：每个案例列目标版本、原始证据、外加假设、检查对象、输入集和剩余义务。

### 洞察九 比较器也需要被证伪

- 陈述：检查器漏掉数据引用会把错误常量判为精确匹配，验证器的通过记录本身需要反例约束。
- 证据：F-175~F-177。TH08旧比较器重定位后只比指令，0.0对128.0曾通过；后续补引用数据审计和故意无效literal测试。
- 反常识：机器码一致不能独立支持名字含义、共享状态归属或现代移植正确性。
- 行动：加入应失败的常量/重定位负例，重审历史通过记录，保留原compiler与原平台运行两条验证路径。

### 洞察十 教学重建应保持声明粒度

- 陈述：从目标恢复一条规则，适合以小模块教学，但新UI与新控制逻辑需要单独归属。
- 证据：F-147~F-151的计算器和恐龙，F-161~F-164的Aegis，F-171的TH04摘要。
- 反常识：可玩的恐龙教学页并非原游戏源码恢复；可读aimed_ring_angle不能替代历史compiler-sensitive helper。
- 行动：公开模块采用固定输入验证，源码归属、许可证及未重建组件明确记录，不把教学演示包装成原应用。

## 第四轮知识地图

新手路径：[官网上手](../concepts/11-official-site-getting-started.md) → [Notes首次调查](../examples/notes-first-investigation.md) → [三类调查指南](../concepts/12-evidence-driven-investigation.md)。
进阶路径：[官网实验](../examples/official-site-labs.md) → [五案例证据](../examples/showcase-cases-example.md) → [重建验证](../concepts/13-reconstruction-verification.md)。

| 文档 | 主要事实 | 页面覆盖 |
|---|---|---|
| 11 官网上手 | F-137~F-140 | W01/W02/W04 |
| Notes首次调查 | F-141~F-144 | W03/W07 |
| 12 三类调查指南 | F-145/F-153~F-159 | W05~W08 |
| 官网实验 | F-146~F-151/F-160~F-164 | W01/W13/W15 |
| 五案例证据 | F-153~F-172 | W09~W14 |
| 13 重建验证 | F-173~F-178 | W16/W17 |

以上主题续接旧编号，不重复已有API目录。索引页W05/W09/W16作为路径连接材料，不人为生成独立“概念”。全部页面的原始归属见[逐页台账](official-site-source.md)。
