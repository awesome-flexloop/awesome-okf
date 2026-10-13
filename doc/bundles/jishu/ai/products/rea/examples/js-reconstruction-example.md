---
type: Example
title: "REA：JavaScript 应用重建示例"
description: "用 rea analyze-javascript-application 对给定 Electron/JavaScript 应用目录走通一次静态重建，配合 compare_application_versions / trace_application_feature 工作流、trace_web_source_location Web 源定位，以及 observe-javascript-runtime / reconcile-javascript-runtime 运行时观测与协同（证据 F-067/069/070/072/073/074/075/076/077）"
tags: [rea, example, javascript, application-graph, reconstruction, runtime-reconciliation, web-source-location]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T15:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: docs-full
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/docs"
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
---

# 示例：JavaScript 应用重建示例

> 命令与输入契约经固定源码和官方文档核对，未在本机运行 REA。静态分析、版本对比与特性追踪给出输入生成步骤；Web 定位与运行时协同仅展示调用接口，需按对应官方 schema 准备真实证据，不能把整页当作独立端到端脚本。

## 目标

用 REA 对给定的 Electron/JavaScript 应用目录（或 `.asar`）做一次**静态重建**——不执行应用代码，把它投影为 JavaScript Application Graph 并附加 Electron 边界摘要；再在此基础上演示版本对比、特性追踪、Web 源定位，以及运行时观测与静态/运行时协同。

## 输入

- 一台满足 Node 支持范围的机器（`^22.19.0 || ^24.11.0 || >=26.0.0`，F-007），npm 存量 `npm@11.16.0`（F-008）。
- 一个 Electron/JavaScript 应用目录（或直接 `.asar` 文件），例如 `/absolute/path/to/apps/app`。
- 若要验证 ASAR 完整性失败场景，可准备好配套的 `.asar.unpacked` 说明（F-073）。
- JavaScript 恢复解析器接受 Wakaru `^1.13.0`，REA 以 Wakaru **1.14.0** 验证（F-074）——按需满足版本约束。

## 步骤

### 1. 静态重建入口

对目录（或 `.asar`）调用专用命令：

```bash
rea analyze-javascript-application /absolute/path/to/apps/app --json
```

**说明**：
- `analyze_javascript_application`（CLI `rea analyze-javascript-application`）是 JavaScript 工件重建入口，支持 `.js/.jsx/.mjs/.cjs/.ts/.tsx/.mts/.cts` 共 8 种扩展名的文本解析；TypeScript 也按惰性文本解析，分析不会执行它们（F-072）。
- 通用 `rea analyze PATH` 在未给 `--provider`/`--snapshot` 时对目录/`.asar` **自动选择**同一静态 JavaScript 应用图 + Evidence 工作流（F-056）。
- 重建产出的是 schema 值为 `"JavaScriptApplicationGraph"` 的有向图；观察 ID 用 `semantic-content-sha256` 推导、边缘 ID 用 `relationship-exact` 稳定性（F-067）。

**预期**：返回一个 Evidence envelope，内含 JavaScript Application Graph、静态 Electron 摘要、重建统计与显式局限。结果不需要活动的 Hopper/Ghidra/浏览器或 Electron 进程。

### 2. 选择源文件（可选）

若只关心已知入口源，可给出精确的 artifact 相对路径，只对所选文件分配源码文本并做静态分析；未选文件在本阶段保持 `outside-analysis-scope`，覆盖为部分（F-072 所属源文档语义）：

```bash
rea analyze-javascript-application /absolute/path/to/apps/app \
  --source-path package.json --source-path main.js --json
```

### 3. 完整性策略与 ASAR 完整性

```bash
rea analyze-javascript-application /absolute/path/to/apps/app.asar \
  --integrity-policy record-and-continue --json
```

**说明**：
- 重建的 `integrity_policy` 接受 `fail`（默认）或 `record-and-continue`（F-073）。
- ASAR 完整性检查使用 **SHA-256**：对嵌入条目与配套 `.asar.unpacked` 文件核对声明值与计算值；默认 `fail` 遇到不匹配即返回失败并带上 artifact 上下文（F-073）。
- 显式选择 `record-and-continue` 后，REA 仍分析观察到的字节，但把每个矛盾的声明哈希与观察哈希连同 `observed-untrusted` 信任标记保留下来；这类结果把应用图覆盖标记为部分，并把每个矛盾路径写进局限（F-073）。

### 4. Wakaru 恢复与安全边界

- JavaScript 恢复解析器接受 Wakaru `^1.13.0`，并以 Wakaru **1.14.0** 验证；其 SHA-256 为 `664fa06782a61eda7ed15885134b52525fd565dd77607e642062ceb6cd927c38`；第三方源代码修订固定于 commit `8219bf5016a063d7fb215101a8c45d5959ec733f`（F-074）。
- 恢复进程使用 util-linux `prlimit`（默认 `/usr/bin/prlimit`）约束自身（F-074）。
- 重建路径**从不执行** `eval`/`Function`/`vm.runInContext`/DOM/应用 bootstrap 代码——所有 JS/TS 源均作为惰性文本解析，不落入运行时（F-072 安全边界）。

### 5. 应用图关系与身份策略（概念校对）

重建出的有向关系词汇表含 `contains`/`loads`/`imports`/`maps_to`/`exposes`/`sends`/`invokes`/`handles`/`calls`/`persists_to`/`observed_as`/`changed_from` 共 12 个值（F-068）。身份策略集合含 `content-digest`/`source-map-original`/`canonical-path`/`artifact-local-key`/`structural-fingerprint`/`runtime-instance`/`observation-fingerprint` 等值（F-069）。这些是理解下游追踪与版本对比输出字段时的参考。

### 6. 版本对比：compare_application_versions

JS 工作流共有 6 个 MCP 工具，CLI 名用连字符替换下划线同名（F-070）：`inspect_analysis_view`/`trace_application_feature`/`trace_javascript_semantics`/`compare_application_versions`/`compare_source_to_bundle`/`compare_javascript_export_shapes`。这里演示版本对比：

```bash
# 先独立重建两个版本，再喂给对比命令
rea analyze-javascript-application /absolute/path/to/version-a --json > version-a-evidence.json
rea analyze-javascript-application /absolute/path/to/version-b --json > version-b-evidence.json
```

其中 `compare-input.json` 携带完整 Evidence 记录。以下脚本读取上一步保存的真实结果，不添加不存在的 `from` 字段：

```bash
node --input-type=module -e '
import { readFileSync, writeFileSync } from "node:fs";
const read = path => JSON.parse(readFileSync(path, "utf8"));
writeFileSync("compare-input.json", JSON.stringify({
  left: read("version-a-evidence.json"),
  right: read("version-b-evidence.json")
}));'
rea compare-application-versions ./compare-input.json --json
```

**说明**：
- `compare_application_versions` 按层级基线配对实体：exact content digest → exact module-source digest → exact node identity → source-map identity → structural fingerprint → non-module 实体语义键，**低层不覆盖更高唯一匹配**（F-070 所属源文档语义）。
- 每个条目被分类为 `unchanged`/`added`/`removed`/`changed`/`unknown`，并返回 basis、candidates、changed dimensions、Evidence 链接与局限，以及包含全部对比节点的 `changed_from` 图（F-068/F-070 语义）。
- 单侧缺失仅在对方图覆盖完整时才判 `added`/`removed`；部分/不可用/截断输入时该条件为 `unknown`（F-070 语义）。

### 7. 特性追踪：trace_application_feature

一旦某个 module、route、字符串种子已知，用 `trace_application_feature` 从完整到可及的应用图里取一条可及特性足迹：

```bash
# 先对给定树分析一次并按保存的 Evidence 构造输入（可仿照官方 workflow 文档做法）
rea analyze-javascript-application /absolute/path/to/app --json > application-evidence.json
```

```bash
node --input-type=module -e '
import { readFileSync, writeFileSync } from "node:fs";
const application = JSON.parse(readFileSync("application-evidence.json", "utf8"));
writeFileSync("trace-input.json", JSON.stringify({
  application, seed: { kind: "string", value: "search-result" }, direction: "both"
}));'
rea trace-application-feature ./trace-input.json --json
```

**说明**：
- `trace_application_feature` 选择一种字面量种子 kind：node ID、route、string、API、IPC channel、module 或 native export；匹配为 exact 或字面子串，**不接收正则或可执行谓词**（F-070 语义）。
- 结果包含匹配 basis、完整可达子图、terminal paths、authority 摘要与 native handoffs；Hopper/Ghidra Evidence 仅在 subject digest 精确匹配时才被链接，否则推荐 provider 中立后续工具并报告 `requires-provider-analysis`（F-070 语义）。
- `inspect_analysis_view` 投影已完成 Evidence 的 summary/module 页，**不遍历关系**（F-071）。

### 8. Web 源定位：trace_web_source_location

对被动捕获的 Web 或 Electron 源做原始源映射定位：

CLI 接受六个位置参数，不接受单个 JSON 请求文件。准备真实 `export_web_scripts` 导出 manifest 与本地 source map 后，按以下形态调用；路径和位置须替换为该次导出的实际值，本节未生成这些文件。

```bash
rea trace-web-source-location \
  "D:/analysis/export-manifest.json" 0 \
  "D:/analysis/app.js.map" "https://example.test/app.js.map" \
  1 0 --json
```

**说明**：
- `trace_web_source_location`（CLI `rea trace-web-source-location`）适配器锁定上游 `@jridgewell/trace-mapping` **0.3.31**（F-077）。
- 参数依次为 manifest 路径、从零开始的 script index、本地 source map 路径、source map URL 上下文、生成行号、生成列号；script index 必须指向 manifest 中精确的脚本。
- URL 仅作为解析上下文，不触发 fetch。manifest 和 map 必须真实存在；不能把普通应用 Evidence 文件当作导出 manifest。
- 生成位置用从 1 开始的行号、从 0 开始的 UTF-16 列号（F-077）。

### 9. 运行时观测：observe_javascript_runtime

静态图工作流不执行恢复出的代码。当需要运行时语义时，通过运行时观测获取被动观察：

```bash
rea list-javascript-runtime-targets http://127.0.0.1:9229 --json
rea observe-javascript-runtime http://127.0.0.1:9229 TARGET_ID --runtime-kind node --json
```

**说明**：
- JS 运行时观测含 2 个 MCP 工具 `list_javascript_runtime_targets`/`observe_javascript_runtime`（CLI 同名，连字符化；F-075）。
- 前提是调用方已经启动 Inspector 目标；`TARGET_ID` 替换为发现结果中的精确 ID。REA 不启动、暂停、恢复或结束该目标。
- 声明 4 种角色 `node`/`electron-main`/`electron-preload`/`electron-renderer`；捕获预算 8 MiB 聚合、CDP 消息传输上限 16 MiB（F-075）。

### 10. 协同：reconcile_javascript_runtime

把静态重建的 Evidence 与被动运行时捕获 Evidence 合并——第二操作不重跑静态分析、不接触 CDP，保留静态、运行时与跨层推断三者的独立 authority：

`reconcile-input.json` 须按固定 `docs/javascript-runtime-reconciliation.md` 准备完整静态层、运行时层及映射。本节未生成这些输入。

```bash
rea reconcile-javascript-runtime ./reconcile-input.json --json
```

**说明**：
- `reconcile_javascript_runtime`（CLI `rea reconcile-javascript-runtime`）要求 `static_layers` 恰好一个 `application` 角色（F-076）。
- 映射类型含 `file-root`/`url-prefix` 两种（F-076）。
- 跨层 `observed_as` 边缘的 `authority` 为 `cross-layer-reconciliation`、`state` 为 `inferred`（F-076）。

## 输出 / 验收

- [ ] `rea analyze-javascript-application <dir>` 返回含 JavaScript Application Graph 与 Electron 边界摘要的 Evidence（F-072/F-067）
- [ ] `.asar` 场景下 `--integrity-policy record-and-continue` 保留矛盾哈希并标 `observed-untrusted`，覆盖标记为部分（F-073）
- [ ] `rea compare-application-versions` 输出含 `unchanged`/`added`/`removed`/`changed`/`unknown` 分类与 `changed_from` 图（F-070/F-068）
- [ ] `rea trace-application-feature` 按字面量种子返回完整可达子图与 native handoffs（F-070）
- [ ] `rea trace-web-source-location` 用 `@jridgewell/trace-mapping@0.3.31` 给出 1-based 行、0-based UTF-16 列（F-077）
- [ ] `rea reconcile-javascript-runtime` 以单一 `application` 层产生 `cross-layer-reconciliation`/`inferred` 的跨层 `observed_as` 边（F-076）

## 反模式提醒

- `inspect_analysis_view` 只投影 summary/module 页、不遍历关系；需要关系遍历请走 `trace_application_feature`/`trace_javascript_semantics`（F-071/F-070）。
- 静态图工作流不执行恢复出的代码：当运行时语义重要时，直接用浏览器/Electron/process 工作流对相关版本跑行为探针，观察到的不证明未观察版本或环境里的行为（F-070 源文档语义）。
- 不要在 CLI 独立进程之间依赖保留的 MCP 连接状态：一个独立 CLI 进程没有保留的 MCP 连接状态，完整 Evidence 记录需作为后续 CLI 输入内联传入（F-070 源文档语义）。

## 阅读下一篇

- [重建工作流示例](reconstruction-workflow-example.md)——重建就绪阶段与义务台账的端到端流程
