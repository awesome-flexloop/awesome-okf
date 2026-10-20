---
type: Reference
title: "SST OKF Wiki 独立验证记录"
description: "记录 SST 教程在固定源码符号、示例、frontmatter、链接、导航、计数和项目质量门上的独立核验结果。"
tags: [SST, verification, quality, OKF]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T04:15:52Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T04:15:52Z" }
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
| 示例 API 回源 | PASS（定向） | 使用 `git show <commit>:<path>` 独立取回 `aws-angular` 配置、handler 与 SDK Resource 导出；确认 `sst.aws.Bucket`、`sst.aws.Function`、`link: [bucket]`、handler 路径及 `Resource.MyBucket.name`。 |
| Bundle frontmatter 与内部链接预检 | PASS（正文） | 对现有 12 篇概念/示例/参考 Markdown 检查非空 `type`、`sources` 与 `/` 开头 bundle 内链接目标；概念 7 篇、示例 3 篇、参考 2 篇。 |
| 官网使用方式 | PASS（来源登记） | `sst dev`、`sst diff`、`sst deploy --stage <name>` 引用 2026-10-20 官方 CLI 页面 W-010/W-011；未描述为本次执行结果。 |
| 云端部署边界 | PASS（文本检查） | 示例明确未运行安装、`sst dev`、`sst diff`、`sst deploy`，未配置凭证或创建/更新 AWS 资源。 |

## 待完成检查

| 检查项 | 状态 | 验收方式 |
|---|---|---|
| Bundle 与父级 toctree 可达性 | PENDING | 运行 `invoke gates.toctrees`，逐级确认 SST bundle 和 iac 分组可从文档根到达。 |
| 全库 bundle/group/domain 计数 | PENDING | 运行 `invoke gates.bundles`；OpenTUI 并行变更已在当前索引形成基线，新增 SST 后按工作树目录树复算。 |
| 文档构建与全量质量门 | PENDING | 运行 `invoke gates.all` 与 `invoke build`，将本任务结果与其他在途 bundle 的失败分开归属。 |
| GATE-SPS 全仓稳定性 audit | UNKNOWN | 既有后台任务 `job-e4ed73ba75fb44738dafb54d95983286` 的输出日志在本轮检查时为空且无退出码；不据此宣称通过。束内持久引用使用固定 GitHub commit 和公开官网 URL。 |

## 范围与限制

- 本教程覆盖固定源码快照中登记的 F-001–F-034，以及 2026-10-20 官网页面登记的 W-001–W-015；不穷举所有组件、provider 或 API。
- 官网页面为采集时点材料，不自动证明 v4.17.2 的实现。
- 示例命令和配置经静态来源核验，不代表依赖安装、应用运行或真实云部署已经验证。

## 相关概念

- [SST v4.17.2 固定源码快照](/references/source-v4.17.2.md)
- [SST 官方文档（2026-10-20 采集）](/references/official-docs-2026-10-20.md)
- [CLI 到项目执行生命周期](/concepts/02-cli-project-lifecycle.md)
