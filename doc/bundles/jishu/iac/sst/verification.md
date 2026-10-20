---
type: Reference
title: "SST OKF Wiki 独立验证记录"
description: "记录 SST 教程在固定源码符号、示例、frontmatter、链接、导航、计数和项目质量门上的独立核验结果。"
tags: [SST, verification, quality, OKF]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T04:15:52Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T05:30:35Z" }
status: draft
stale_after: 2027-10-20
sources:
  - id: source
    resource: /references/source-v4.17.2.md
    title: SST v4.17.2 固定源码快照
  - id: docs
    resource: /references/official-docs-2026-10-20.md
    title: SST 官方文档（2026-10-20 采集）
---

# SST OKF Wiki 独立验证记录

本页记录 SST v4.17.2 / `e49ac31411f63ab4ed0d802b7e15d95f6b827e47` 教程束的独立验证证据。源码符号通过固定 commit 的 Git 对象复核；项目导航、索引和构建结果在本页更新为最终结果。

## 已完成检查

| 检查项 | 结果 | 证据与口径 |
|---|---|---|
| 示例 API 回源 | PASS（固定 commit） | 使用 `git show` / `git grep` 独立复核 `aws-angular` 配置、handler 与 SDK Resource 导出；确认 `sst.aws.Bucket`、`sst.aws.Function`、`link: [bucket]`、handler 路径及 `Resource.MyBucket.name`。 |
| Bundle 元数据与本地链接 | PASS | 独立解析 18 篇 Markdown：14 篇含 frontmatter，所有 `type` 与 bundle 内 `sources` 均有效；74 个本地 Markdown 链接目标存在。概念 7 篇、示例 3 篇、参考 2 篇。 |
| 官网使用方式 | PASS（来源登记） | `sst dev`、`sst diff`、`sst deploy --stage <name>` 引用 2026-10-20 官方 CLI 页面 W-010/W-011；未描述为本次执行结果。 |
| 云端部署边界 | PASS（文本检查） | 示例明确未运行安装、`sst dev`、`sst diff`、`sst deploy`，未配置凭证或创建/更新 AWS 资源。 |
| 本地路径与范围声明 | PASS | 对 SST bundle 搜索未发现 `file:///`、本机绝对路径或临时目录引用；全文明确不穷举所有组件、provider 或 API。固定 checkout 的 HEAD/tag 与规格一致，工作树干净。 |

## 质量门结果

| 检查项 | 状态 | 验收方式 |
|---|---|---|
| Bundle 与父级 toctree | PASS | `python scripts/check-toctrees.py` 通过；全库内容均可达，包含 SST 与 `iac` 分组。 |
| 全库 bundle/group/domain 计数 | PASS（实时工作树） | `python scripts/check-bundles-index.py` 与 `invoke gates.all` 通过：9 域 / 63 组 / 654 束；`jishu` 为 484 束 / 19 组，均按目录树和索引五面核对。比规格初始预期多 2 束，计数包含 OpenCode/OpenTUI 并行新增内容；本任务未修改其 bundle。 |
| UTF-8 与全部项目质量门 | PASS | `py314 -m invoke gates.all` 通过，UTF-8、toctree、总索引及各检查器自检均通过。 |
| 完整文档构建 | PASS（有全库警告） | 最终 `py314 -m invoke build` 退出码为 0，HTML 构建成功，Sphinx 报告 `build succeeded, 268 warnings`；未发现指向 SST 文档的构建告警，SST 定向 `-W` 检查的告警来自其他 bundle。 |
| GATE-SPS 信源稳定性 | 分范围记录 | `--target external/dao/anomalyco/sst` 清理前扫描结果为 0 处引用。全仓 audit 检出大量既有临时/失效/环境绑定路径；扫描结果中未出现 SST bundle 路径，故不将全仓 audit 记为通过，也未修改无关引用。 |
| 严格定向 Sphinx 检查 | 有限告警 | SST 18 篇均被读取并写出；`-W` 定向运行因全局既有重复 toctree 引用告警而返回非零，告警均位于其他 bundle。完整 HTML 构建成功。 |

## 范围与限制

- 本教程覆盖固定源码快照中登记的 F-001–F-034，以及 2026-10-20 官网页面登记的 W-001–W-015；不穷举所有组件、provider 或 API。
- 官网页面为采集时点材料，不自动证明 v4.17.2 的实现。
- 示例命令和配置经静态来源核验，不代表依赖安装、应用运行或真实云部署已经验证。
- 完整构建成功但含 268 条全库 warning；严格定向检查仍会被其他 bundle 的既有重复 toctree 引用告警阻断，不据此宣称全库零警告。

## 相关概念

- [SST v4.17.2 固定源码快照](/references/source-v4.17.2.md)
- [SST 官方文档（2026-10-20 采集）](/references/official-docs-2026-10-20.md)
- [CLI 到项目执行生命周期](/concepts/02-cli-project-lifecycle.md)
