---
type: Example
title: "最小应用与组件"
description: "从固定版本的 SST 配置骨架创建一个 AWS Bucket 组件，并区分代码示例与真实部署验证。"
tags: [SST, example, component, AWS, 入门]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T04:13:29Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T04:13:29Z" }
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

# 最小应用与组件

本例展示 SST 配置入口如何声明一个 AWS Bucket 组件。配置外壳采用固定提交中 `aws-base` 示例的应用结构，Bucket 声明则与官网 Basics 页面展示的组件写法一致（W-001、W-004、W-005）。

本例用于学习配置和组件的关系；本任务没有运行 SST，也没有在 AWS 创建资源。

## 前提

- 使用 Node.js 项目，并在项目内安装 SST。官网 CLI 文档建议 JavaScript 项目本地安装；本示例将版本固定到本教程的源码基线：

```bash
npm install sst@4.17.2
```

- AWS 凭证和账号须由使用者按自身环境配置。本例不收集凭证，也不代替账号权限、预算或资源清理策略的检查。
- 需从项目根目录运行命令，使 SST 能发现 `sst.config.ts`（F-003）。

## 配置

在项目根目录创建 `sst.config.ts`：

```ts
/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "sst-minimal",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
    };
  },
  async run() {
    new sst.aws.Bucket("MyBucket");
  },
});
```

`$config`、`app`、`home` 与 `run` 的结构可在固定提交的 [`aws-base` 配置](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/examples/aws-base/sst.config.ts)核对；`new sst.aws.Bucket("MyBucket")` 与官网 Basics 页面中的组件写法相符（W-001）。源码快照导出了 AWS 组件命名空间（F-021），官网 Components 页面列出 `sst.aws.*` built-in components（W-005）。

## 运行方式

在真实项目中，官网给出的本地开发与部署命令包括：

```bash
npx sst dev
npx sst deploy --stage dev
```

`sst dev` 与 `sst deploy --stage <name>` 是官网采集日记录的使用方式（W-010、W-011）。运行这些命令可能访问云 provider 并创建或更新资源；这不是纯本地预览。执行前应检查当前账号、stage、费用和资源保留策略。

本教程只核验了示例代码与固定版本仓库/官网文档的一致性，未运行 `npm install`、`sst dev`、`sst deploy`，也未验证 AWS 部署结果。

## 相关概念

- [SST 应用模型与阅读边界](/concepts/00-application-model.md)
- [配置、stage 与 state](/concepts/01-config-stage-state.md)
- [组件与 provider 边界](/concepts/03-components-and-providers.md)
- [本地开发到部署示例](/examples/03-local-development-and-deployment.md)
