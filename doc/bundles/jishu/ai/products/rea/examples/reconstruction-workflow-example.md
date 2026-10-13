---
type: Example
title: "REA：重建工程工作流示例"
description: "按重建就绪 9 阶段走查一条可审计的重建流程：构造含 artifacts/providers/environments/scenarios/captures/unknowns/records 的 evidence_bundle、调用 rea build-reconstruction-obligation-ledger 生成义务台账得到 ledger_id/closure_digest，并说明 required_case_kinds 与 manifest、REA_MCP_INPUT_SCHEMA_PROFILE=compact（证据 F-129/130/131/120）"
tags: [rea, example, reconstruction-workflow, obligation-ledger, evidence-bundle, readiness, closure-digest]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T15:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: docs-full
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/docs"
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
---

# 示例：重建工程工作流

> **范围说明**：本页是九阶段说明与空台账客户端集成示例，不提供真实应用的完整重建输入链。命令已对照固定源码和官方文档，**未在本机实跑**；空请求的`unknown`为官方预期，不是本机观测。

## 目标

理解重建就绪九阶段（F-129）和义务台账结构（F-130/F-131），使用官方合法空请求检查客户端接线，并区分广告schema兼容性与真实Evidence（F-120）。真实重建还需目标证据、原始用例、候选fixtures和相当authority的验证器，本页未提供这些产物。

## 输入

- 一台满足 Node 精确支持范围的机器（`^22.19.0 || ^24.11.0 || >=26.0.0`，F-007）。
- 一个可分析的目标（待重建的应用目录 / `.asar` / native 二进制等）。
- 若走 native 等静态分析阶段，需已装相应分析工具（Ghidra/IDA/Hopper 等），见 [provider-setup.md](provider-setup.md)。

## 阶段一：从就绪 9 阶段走查重建请求

重建就绪共有 **9 个阶段**（F-129）：`discover-classify` / `diagnose-environment` / `declare-request` / `static-analysis` / `reactive-scenarios` / `compare-authority-candidate` / `preserve-contradictions` / `verify-reconstruction-closure` / `export-replay`。

> 这 9 个阶段组成递进检查链：从「发现并分类目标 → 环境诊断 → 声明请求 → 静态分析 → 反应式场景 → 与权威候选对比 → 保留矛盾 → 验证重建闭包 → 导出可重放」（F-129）。其中 `verify-reconstruction-closure` 是「做到哪一步算完成」的核对点，`export-replay` 是「可重放」的出产物。

对每个阶段，把它与一次重建的具体动作对应起来：

| 阶段 | 本示例中的对应动作 |
|------|--------------------|
| `discover-classify` | 目标无关启动、盘点工件、确认兼容的工作流并被其精确可见限制覆盖（F-129） |
| `diagnose-environment` | 把运行时故障与分析失败分离、检测版本偏差（F-129） |
| `declare-request` | 在启动前把精确的目标（target）、操作（operation）与生命周期（lifecycle）随请求携带（F-129） |
| `static-analysis` | native / JavaScript 路由，保留歧义、截断、不支持语法与残留 unknowns（F-129） |
| `reactive-scenarios` | 谓词驱动交互、后代结算、Electron 关联、取消清理的 Evidence（F-129） |
| `compare-authority-candidate` | 显式偏序/有限迹语义、主分歧定位、不完备对比以 unknown 处理（F-129） |
| `preserve-contradictions` | 采用 record-and-continue，被影响的等价被阻断，未被影响的对比保留（F-129） |
| `verify-reconstruction-closure` | 检测不完备重建、增量验证器闭包、拒绝分权候选（F-129） |
| `export-replay` | CLI/MCP 对齐、确定性重放、篡改与陈旧输入拒绝（F-129） |

**要点**：9 阶段的每个阶段与所需「必须证明」都要恰好出现一次，并链接到内嵌 Evidence bundle 中的 Evidence（F-129，`reconstruction-readiness.md`）。`fail` / `unknown` / `unsupported` / `truncated` / `skipped` 绝不能聚合成 `pass`（F-129）。

## 阶段二：收拢 evidence_bundle

在重建过程中把静态应用图、进程捕获等产生的证据收拢进一个 `evidence_bundle`。该 bundle 内含 **7 类数组**：`artifacts` / `providers` / `environments` / `scenarios` / `captures` / `unknowns` / `records`（F-130）。

构造示例（示意结构，执行时以会话导出的真实 bundle 替换）：

```json
{
  "evidence_bundle": {
    "artifacts": [],
    "providers": [],
    "environments": [],
    "scenarios": [],
    "captures": [],
    "unknowns": [],
    "records": []
  }
}
```

> 说明：静态应用图与进程捕获记录会自动生成保守的义务候选（F-130，`reconstruction-obligation-ledgers.md`）。对于一个真实调查，应从会话导出 Evidence bundle 并替换这里的空数组；当某个必需声明未由这些来源代表时，再显式补充 `reviewed_obligations`（F-130）。

## 阶段三：生成义务台账

把上面的 bundle 交给义务台账入口（F-130）：

- MCP 工具：`build_reconstruction_obligation_ledger`
- CLI 命令：`rea build-reconstruction-obligation-ledger`

```bash
rea build-reconstruction-obligation-ledger \
  '{
    "evidence_bundle": {
      "artifacts": [],
      "providers": [],
      "environments": [],
      "scenarios": [],
      "captures": [],
      "unknowns": [],
      "records": []
    },
    "reviewed_obligations": [],
    "manifest": {
      "bindings": [],
      "contradictions": []
    }
  }' \
  --json
```

（此空请求用于快速校验客户端集成，是合法输入，返回含零义务的 `unknown` 台账——源 Evidence 缺失绝不声称闭包，F-130。）

**预期输出**：台账返回每个义务的内联结果，整体以 `ledger_id` 与 `closure_digest` 标识完整结果，涵盖摘要、报告、所有权与依赖图、Evidence 链接与限制（F-130）。

## 阶段四：理解台账结构与多态用例

- 台账的 **`manifest` 对象**含 **`bindings`** 与 **`contradictions`** 两个数组（F-131）。
- **`required_case_kinds`** 数组可含 **`positive` / `negative` / `malformed` / `cancellation`** 等多种用例种类（F-131）。
- **`reviewed_obligations`** 每个元素含 `obligation_id` / `obligation_version` / `title` / `application_layer` / `family` 字段（F-131）。

> 守恒原则：一个必需义务只在「某 manifest binding 提供唯一 owner + 所有必需 parser/schema/domain type + 每种必需用例 fixture + 通过验证器（其 authority 与原始观测相当）」时闭合（F-130，`reconstruction-obligation-ledgers.md`）。矛盾、重复定义/owner、残留 unknowns、缺失依赖、authority 不可用都会让闭合保持 open 或 failed（F-130）。一个绿色单元测试无法闭合一个 `packaged-process` 义务；纯静态的 source 无法闭合一个 runtime/process 声明（F-130）。

举例：一个协议取消义务可把 `required_case_kinds` 声明为 `["positive","negative","malformed","cancellation"]`，并在 manifest binding 里用四类 `original_cases` 与四类重建 `fixtures` 覆盖它们，再附一个 authority 相当的 `verifier`（其 status 为 `pass`），从而闭合该项义务（F-130/F-131，`reconstruction-obligation-ledgers.md` 中 `protocol.rpc.cancel` 示例）。

## 阶段五：可选 compact 广告schema兼容配置

模型提供方可能限制单工具输入schema大小。REA提供可选广告profile，默认保持完整定义（F-120）：

- `REA_MCP_INPUT_SCHEMA_PROFILE`默认`full`。
- 可选`compact`将每个广告输入JSON Schema限制在**13,312字节**，并非固定9字段。
- 工具全集、输出schema、annotations及canonical服务端验证不变；真实Evidence与实际必填参数不因此减少。

```bash
# POSIX shell；仅在提供方大小限制需要时选择compact，默认full：
REA_MCP_INPUT_SCHEMA_PROFILE=compact rea --mcp
```

> 说明：profile 在服务启动时读取，改动需重启服务生效（F-120，`mcp-contracts.md`）。对少数校验结构本身就超预算的工具（含 `build_reconstruction_obligation_ledger`），`compact` 会以精简形态投放（属性名、引用解析后的类型、首层指引与根 required 约束），嵌套校验细节被省略，但服务端仍按规范 schema 拒绝畸形调用（F-120）。

## 输出 / 验收

- [ ] 能区分九阶段名称与实际命令；不把阶段表当执行记录（F-129）。
- [ ] 空请求按官方契约返回零义务`unknown`，而非重建`pass`（本机未实跑）。
- [ ] 能解释`ledger_id`/`closure_digest`存在不等于义务闭合（F-130）。
- [ ] 真实重建逐项核对`manifest`绑定、原始用例、fixtures、验证器与矛盾（F-131）。
- [ ] 需要时配置compact并重启服务；不认为它压缩Evidence或免除canonical校验（F-120）。

## 反模式提醒

- 不要把缺 Evidence 的空 bundle 当作「已闭合」——源 Evidence 缺失绝不声称闭包（F-130）。
- 不要用一个 authority 不相当的验证器去闭合义务——绿色单测无法闭合 `packaged-process`，纯静态 source 无法闭合 runtime/process 声明（F-130）。
- 不要硬编码 9 阶段之外的阶段名/命令/字段——本示例的阶段、命令、字段、数字均来自 facts F-129/F-130/F-131/F-120，禁止编造不存在的名称。

## 阅读下一篇

- [回到 REA 工程与管理概念](../concepts/10-engineering-workflow.md)——重建工作流的事实层与勾连说明
