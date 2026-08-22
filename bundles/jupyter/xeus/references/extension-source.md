---
type: Reference
title: JupyterLab扩展注册参考
description: @jupyterlite/xeus-extension 包的JupyterLab插件注册、内核规格提供和empack元数据
tags: [extension, jupyterlab, plugin, kernel-spec, tokens, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: extension-src
    resource: /references/extension-source.md
    title: packages/xeus-extension/src/index.ts
---

## 插件概览

定义在 [index.ts](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/packages/xeus-extension/src/index.ts)。

三个核心JupyterLab插件：

| 插件ID | requires | optional | provides | autoStart |
|--------|----------|----------|----------|-----------|
| `@jupyterlite/xeus-extension:kernel` | IServiceManager, IKernelSpecs, IBrowserContext | — | — | true |
| `@jupyterlite/xeus-extension:xeus-logs` | — | ILogger | IXeusLogManager | true |
| `@jupyterlite/xeus-extension:empack-env-meta` | IKernelSpecs, IBrowserContext | — | IEmpackEnvMetaManager | true |

## kernelPlugin（内核注册）

### 激活流程

1. **读取 kernels.json**：
   ```typescript
   const response = await fetch(PageConfig.getBaseUrl() + 'xeus/kernels.json');
   const kernelsData = await response.json();
   ```

2. **为每个内核规格创建KernelSpec**：
   - 对 kernelsData 中的每个kernelSpec：
     - 获取 dir = spec.dir（相对于baseUrl的内核目录）
     - `kernelUrl = baseUrl + 'xeus/kernels/' + dir`
     - 再次fetch `kernelUrl/kernel.json` 获取完整规格
     - 构造 resources 映射（kernel-64x64.png、logo-64x64.png、logo-svg.svg）

3. **注册到 IKernelSpecs**：
   ```typescript
   kernelSpecs.register({
     name: kernelSpec.name,
     spec: kernelSpec,
     create: async (options) => new WebWorkerKernel({
       ...options,
       contentsManager: serviceManager.contents,
       kernelSpec,
       browsingContextId: await browserContext.currentId
     })
   });
   ```

### IBrowserContext 依赖

kernelPlugin 依赖 `IBrowserContext`（来自 `@jupyterlite/browser`），用于获取 `browsingContextId`——这是JupyterLite v0.6+引入的浏览器上下文隔离机制，用于区分同一用户打开的多个JupyterLite页面/tab。

## XeusLogManager（日志管理）

实现 `IXeusLogManager` 接口：

```typescript
class XeusLogManager implements IXeusLogManager {
  registerLogChannel(channel: string, kernelId?: string): BroadcastChannel;
}
```

注册名为 `xeus-log-{channel}[-{kernelId}]` 的 BroadcastChannel：

- 当可选的 `ILogger` 可用时：
  - info级别日志 → `logger.log(message)`
  - warning级别 → `logger.warn(message)`
  - critical/error级别 → `logger.error(message)`
- ILogger不可用时降级为 console.log/console.warn/console.error

### Token定义

```typescript
export const IXeusLogManager = new Token<IXeusLogManager>(
  '@jupyterlite/xeus:IXeusLogManager',
  'A service to manage xeus logs channels.'
);
```

## EmpackEnvMetaManager（环境元数据管理）

```typescript
interface IEmpackEnvMetaManager {
  getEnvMetadata(kernelSpec: ISpecModel): Promise<unknown | undefined>;
}
```

为每个内核规格获取empack环境元数据（empack_env_meta.json）：

1. 计算 `kernelUrl = baseUrl + 'xeus/kernels/' + kernelSpec.dir`
2. 构造缓存key：`kernelSpec.dir + kernelSpec.name`
3. 缓存已获取的元数据
4. fetch `kernelUrl/empack_env_meta.json`（404等错误时返回undefined）

用于 `EmpackedXeusRemoteKernel.initializeFileSystem()` 初始化文件系统时的环境元数据。

## WebWorkerKernel 实例化

create工厂函数中实例化 `WebWorkerKernel` 时传入的关键参数：

| 参数 | 来源 |
|------|------|
| contentsManager | IServiceManager.contents |
| kernelSpec | fetch获得的kernel.json完整对象 |
| browsingContextId | IBrowserContext.currentId |
| empackEnvMetaLink | kernelSpec.resources.empackEnvMetaLink（如果有） |

## 相关概念

- [扩展注册机制](../concepts/08-extension-registration.md)
- [内核生命周期](../concepts/04-kernel-lifecycle.md)
- [入门指南](../concepts/01-getting-started.md)
