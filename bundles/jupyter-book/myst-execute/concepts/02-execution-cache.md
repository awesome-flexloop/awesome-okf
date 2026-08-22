---
type: concept
title: "执行缓存与输出转换"
description: "详解 myst-execute 的多级缓存架构：ICache 接口、LocalDiskCache、LegacyExecutionCache、NotebookExecutionCache、TieredExecutionCache 及缓存键计算"
tags: [myst-execute, cache, md5, ipynb, notebook-cache, tiered-cache]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-execute-src.md"
    facts: [F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035]
---

# 执行缓存与输出转换

myst-execute 实现了一套多级缓存系统，在构建时避免重复执行未变化的 Notebook 单元，显著提升增量构建速度。缓存系统基于 ICache<T> 接口抽象，提供四种实现，支持从旧格式迁移和分层查找。

## ICache<T> 接口

所有缓存实现遵循统一的泛型接口：

```ts
export interface ICache<T> {
  test(key: string): boolean;    // 检查 key 是否存在
  get(key: string): T | undefined;  // 获取缓存值
  set(key: string, result: T): void; // 写入缓存
}
```

这个简单的三方法接口使得不同的存储后端（文件系统、内存等）可以互换使用。

## LocalDiskCache<T>：基础磁盘缓存

`LocalDiskCache<T>` 是最基础的实现，将数据序列化为 JSON 文件存储到磁盘：

```ts
export class LocalDiskCache<T> implements ICache<T> {
  constructor(cachePath: string, extension: string);
  private _makeKeyPath(key: string): string;
  test(key: string): boolean;
  get(key: string): T | undefined;
  set(key: string, document: T): void;
}
```

### 实现细节

- 构造时通过 `mkdirSync(cachePath, { recursive: true })` 递归创建缓存目录
- `_makeKeyPath(key)` 使用 `path.join(cachePath, `${key}${extension}`)` 生成文件路径
- `get()` 使用 `JSON.parse(readFileSync(keyPath, 'utf8'))` 反序列化
- `set()` 使用 `writeFileSync(keyPath, JSON.stringify(document), 'utf8')` 序列化写入
- key 通常是 MD5 哈希值（十六进制字符串），不包含路径分隔符，可直接作为文件名

## LegacyExecutionCache：旧格式兼容

`LegacyExecutionCache` 是一个适配器，将旧版缓存格式（IOutput[] 数组）转换为新的 DocumentExecutionResult 格式：

```ts
export class LegacyExecutionCache implements IDocumentExecutionCache {
  constructor(cachePath: string);  // 内部创建 LocalDiskCache<LegacyExecutionResult[]>
}
```

### 格式转换逻辑

**读取时（旧→新）**：
```ts
// 旧格式：每个单元直接是 IOutput[] 或 IExpressionResult
// 新格式：{ type: 'code', responses: IOutput[] } 或 { type: 'inlineExpression', response: ... }
return {
  context: {},
  results: legacyHit.map((item) => {
    if (Array.isArray(item)) {
      return { type: 'code', responses: item };
    } else {
      return { type: 'inlineExpression', response: item };
    }
  }),
};
```

**写入时（新→旧）**：
```ts
const legacyDocument = document.results.map((result) => {
  if (result.type === 'code') return result.responses;
  else return result.response;
});
this.cache.set(key, legacyDocument);
```

LegacyExecutionCache 的存在确保了升级 myst-execute 版本后，旧缓存仍然可用，不会触发全部重新执行。

## NotebookExecutionCache：ipynb 格式缓存

`NotebookExecutionCache` 将执行结果存储为标准 Jupyter Notebook 格式（nbformat 4.5），使缓存文件本身就是可被 Jupyter 打开的合法 .ipynb 文件：

```ts
export class NotebookExecutionCache implements IDocumentExecutionCache {
  constructor(baseCache: ICache<INotebookContent>);
}
```

### 存储格式

写入时构造 INotebookContent 对象：

```ts
const notebook: INotebookContent = {
  nbformat: 4,
  nbformat_minor: 5,
  metadata: {
    mystContext: document.context,  // 执行上下文（kernelspec、时间戳、耗时等）
  },
  cells: document.results.map((result, index) => {
    if (isCodeResult(result)) {
      return {
        cell_type: 'code',
        source: [],
        metadata: { mystResultType: 'code' },
        outputs: result.responses,
        execution_count: index,
      };
    } else {
      // inlineExpression → display_data 或 error 输出
      return {
        cell_type: 'code',
        source: [],
        metadata: { mystResultType: 'inlineExpression' },
        outputs: [/* 转换后的 output */],
        execution_count: index,
      };
    }
  }),
};
```

关键设计：
- code 类型结果直接将 responses（IOutput[]）存入 cell.outputs
- inlineExpression 的 ok 结果转为 `display_data` 输出（含 data/metadata）
- inlineExpression 的 error 结果转为 `error` 输出（含 ename/evalue/traceback）
- 通过 `cell.metadata.mystResultType` 区分原始结果类型
- `metadata.mystContext` 存储执行上下文（kernelspec 名称、时间戳、执行耗时 duration_ms）

读取时反向转换：遍历 cells，根据 metadata.mystResultType 判断原始类型，提取 outputs 构造 DocumentExecutionResult。

## TieredExecutionCache：分层缓存

`TieredExecutionCache` 实现主备两级缓存查找：

```ts
export class TieredExecutionCache implements IDocumentExecutionCache {
  constructor(primary: IDocumentExecutionCache, secondary: IDocumentExecutionCache);
  test(key: string): boolean;    // primary 或 secondary 任一命中即返回 true
  get(key: string): DocumentExecutionResult | undefined;  // 先查 primary，未命中回退 secondary
  set(key: string, document: DocumentExecutionResult): void;  // 只写入 primary
}
```

典型用法：primary 使用新格式缓存（NotebookExecutionCache），secondary 使用 LegacyExecutionCache。这样新构建的结果写入新格式，旧缓存仍可读取，实现平滑迁移。

## 缓存键计算

`buildCacheKey()` 函数使用 MD5 哈希生成确定性缓存键：

```ts
function buildCacheKey(
  kernelSpec: KernelSpec,
  nodes: ExecutableNode[],
  envVars: Record<string, string | undefined>,
): string
```

### 哈希输入

1. **kernelSpec.name**：内核名称（如 "python3"）。换内核必然导致缓存失效。
2. **hashableItems 数组**：每个可执行节点的三元组：
   - `kind`：节点类型（"block" 或 "inlineExpression"）
   - `content`：代码文本或表达式文本
   - `raisesException`：是否标记了 raises-exception
3. **环境变量**（可选）：如果 frontmatter 中 `execute.depends_on_env` 指定了依赖的环境变量，这些变量的键值对排序后也参与哈希。空环境对象不参与哈希（避免破坏现有缓存）。

```ts
const hash = createHash('md5')
  .update(kernelSpec.name)
  .update(JSON.stringify(hashableItems));
if (envKeys.length) {
  hash.update(JSON.stringify(hashableEnv));
}
return hash.digest('hex');
```

### 缓存失效条件

缓存会在以下情况下失效（miss）：
- 代码内容变化（最常见）
- 内核名称变化（如从 python3 切换到 ir）
- raises-exception 标签变化
- 依赖的环境变量值变化（如果配置了 depends_on_env）
- 用户设置 `execute: cache: false`（文档级禁用缓存）
- 命令行使用 `--ignore-cache` 标志（全局禁用缓存）

## transform 中的缓存流程

`kernelExecutionTransform()` 中的缓存检查逻辑：

```ts
// 1. 构建缓存键
const cacheKey = buildCacheKey(kernelspec, executableNodes, cacheEnv);

// 2. 尝试读取缓存
const cacheHit = opts.cache.get(cacheKey);
let cachedResults = cacheHit?.results;

// 3. 判断是否跳过缓存
const ignoreCachedDocument = opts.ignoreCache || executeConfig?.cache === false;

// 4. 命中且未跳过缓存 → 直接应用
if (!ignoreCachedDocument && cachedResults !== undefined) {
  log.info(`💾 Adding cached notebook outputs (${vfile.path})`);
  applyComputedOutputsToNodes(executableNodes, cachedResults);
  return;
}

// 5. 未命中 → 执行内核
log.info(`💿 Executing notebook (${vfile.path}) ...`);
const sessionManager = await opts.sessionFactory();
// ... 创建内核连接、执行节点 ...

// 6. 执行成功 → 写入缓存
if (!errorOccurred) {
  opts.cache.set(cacheKey, {
    context: { kernelspec, path, timestamp, duration_ms },
    results,
  });
}

// 7. 应用结果到 AST
applyComputedOutputsToNodes(executableNodes, cachedResults);
```

注意：只有 `errorOccurred === false` 时才写入缓存——执行出错的不完整结果不会被缓存，下次构建会重新执行。

## 输出写回 MDAST

`applyComputedOutputsToNodes()` 将执行结果转换回 MDAST 节点：

**Code block 输出**：
```ts
outputs.children = (thisResult?.responses ?? []).map((data, index) => {
  const identifier = outputs.identifier ? `${outputs.identifier}-${index}` : undefined;
  return { type: 'output', children: [], jupyter_data: data, identifier };
});
```

每个 Jupyter IOutput 对象直接存入 output 节点的 `jupyter_data` 字段。

**Inline expression 输出**：
```ts
matchedNode.result = thisResult?.response;
```

结果对象（IExpressionResult）直接挂到 inlineExpression 节点的 result 属性。

## 相关概念

- [00-execution-architecture.md](/concepts/00-execution-architecture.md)：执行架构总览
- [01-myst-execute-kernel.md](/concepts/01-myst-execute-kernel.md)：内核连接和执行机制
- [01-configure-notebook-execution.md](/examples/01-configure-notebook-execution.md)：缓存配置示例
