---
type: Example
title: "把基础设施资源链接到 runtime"
description: "使用 SST Function 的 link 属性将 Bucket 信息交给 handler，并通过 JavaScript SDK 的 Resource 对象读取。"
tags: [SST, example, linking, runtime, SDK]
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

# 把基础设施资源链接到 runtime

本例展示资源链接的使用面：在 SST 配置中创建 Bucket，将其放入 Function 的 `link` 列表，再由 handler 从 `Resource` 读取 Bucket 名称。这个配置与 handler 结构可在固定版本的 `aws-angular` 示例中核对；官网 Linking 页面也按“创建资源、声明 link、在 runtime 使用 SDK”的顺序说明该功能（F-027、W-008）。

源码层面，平台把 Linkable 属性序列化到 `SST_RESOURCE_*` 环境变量，JavaScript SDK 再解析这些变量并提供 `Resource` Proxy（F-023–F-029）。因此，业务 handler 读取的是 SDK 暴露的资源数据，不是 Pulumi 资源对象本身。

## 配置资源与链接

在 `sst.config.ts` 中创建 Bucket 和 Function：

```ts
/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "sst-resource-link",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
    };
  },
  async run() {
    const bucket = new sst.aws.Bucket("MyBucket");

    new sst.aws.Function("MyFunction", {
      url: true,
      link: [bucket],
      handler: "functions/presigned.handler",
    });
  },
});
```

`link: [bucket]` 与 handler 路径来自固定提交的 [`aws-angular` 配置](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/examples/aws-angular/sst.config.ts)。本例省略了该仓库中的前端部分，保留 Bucket 与 Function 的资源关系。

## 在 handler 中读取资源

创建 `functions/presigned.ts`：

```ts
import { Resource } from "sst";

export async function handler() {
  return {
    statusCode: 200,
    body: JSON.stringify({ bucketName: Resource.MyBucket.name }),
  };
}
```

`Resource.MyBucket.name` 的 Bucket 访问方式见固定提交中的 [`aws-angular` handler](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/examples/aws-angular/functions/presigned.ts)。JS SDK 导出 `Resource`，并从带 `SST_RESOURCE_` 前缀的环境变量装载 JSON 值（F-028、F-029）。

## 数据边界与执行说明

官网将 Resource Linking 描述为把基础设施信息传给 runtime code 的机制，并说明 `sst dev` 可在本地开发环境加载已链接资源（W-008、W-009）。源码中可追踪的数据路径为：

**Bucket Linkable 数据 → Function link 配置 → `SST_RESOURCE_*` 环境变量 → JS SDK 解析 → `Resource`**

本例中的 `url: true`、`link` 与资源读取写法都可在上述固定版本示例中找到；本任务没有安装依赖、启动 `sst dev`、调用 Function URL 或创建 AWS 资源。实际运行需要按项目配置 SST、AWS 凭证和对应依赖，并确认账号权限、stage 与费用边界。

## 相关概念

- [资源链接与 SDK 数据边界](/concepts/05-resource-linking.md)
- [组件与 provider 边界](/concepts/03-components-and-providers.md)
- [最小应用与组件](/examples/01-minimal-component-app.md)
- [本地开发到部署示例](/examples/03-local-development-and-deployment.md)
