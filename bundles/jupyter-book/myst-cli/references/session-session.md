---
type: reference
title: "myst-cli Session会话源码"
description: "session/session.ts 中Session类的实现、依赖注入容器、Jupyter集成与生命周期管理"
tags: [myst-cli, session, dependency-injection, redux, jupyter]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/session.ts"
    facts: [F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/cache.ts"
    facts: [F-026, F-027, F-028]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/types.ts"
    facts: [F-029]
---

# Session 会话源码分析

## Session 类职责

Session 是 myst-cli 的核心运行时容器，聚合了构建和开发服务器所需的全部依赖：

```ts
export class Session implements ISession {
  API_URL: string;               // API 端点
  configFiles: string[];         // 配置文件名
  store: Store<RootState>;       // Redux Store
  $logger: Logger;               // chalk 日志器
  doiLimiter: Limit;             // DOI 请求并发限制
  executionSemaphore: Semaphore; // Notebook 执行信号量
  proxyAgent?: HttpsProxyAgent;  // HTTPS 代理
  plugins: ValidatedMystPlugin;  // 加载的插件
  // ...
}
```

## 构造函数初始化

```ts
constructor(opts = {}) {
  this.API_URL = process.env.API_URL ?? 'https://api.mystmd.org';
  this.configFiles = opts.configFiles ? opts.configFiles : ['myst.yml', 'myst.yaml'];
  this.$logger = opts.logger ?? chalkLogger(LogLevel.info, process.cwd());
  this.doiLimiter = opts.doiLimiter ?? pLimit(3);  // DOI 最多 3 并发
  this.executionSemaphore = opts.executionSemaphore 
    ?? new Semaphore(Math.max(1, cpus().length - 1));  // CPU核数-1
  this.store = createStore(rootReducer);
  // 代理支持
  if (process.env.HTTPS_PROXY) this.proxyAgent = new HttpsProxyAgent(proxyUrl);
  // 异步检查版本更新
  latestVersion('mystmd').then(latest => { this._latestVersion = latest; });
}
```

### 关键默认值

| 属性 | 默认值 | 说明 |
|------|--------|------|
| API_URL | `https://api.mystmd.org` | 可被 `API_URL` 环境变量覆盖 |
| configFiles | `['myst.yml', 'myst.yaml']` | 配置文件候选名 |
| doiLimiter | `pLimit(3)` | DOI 请求最多 3 个并发 |
| executionSemaphore | `Semaphore(cpus-1)` | Notebook 执行并行度 |
| Logger | `chalkLogger(LogLevel.info)` | 彩色终端日志 |

## 路径方法

Session 提供统一的路径解析方法：

| 方法 | 返回路径 | 说明 |
|------|----------|------|
| `sourcePath()` | 项目根目录 | 优先 sitePath，其次 projectPath |
| `buildPath()` | `<source>/_build` | 构建输出根目录 |
| `sitePath()` | `<build>/site` | 站点输出目录 |
| `contentPath()` | `<site>/content` | 站点内容目录 |
| `publicPath()` | `<site>/public` | 静态资源目录 |

## Clone 机制

`clone()` 创建共享底层资源的子会话：

```ts
async clone() {
  const cloneSession = new Session({
    logger: this.log,           // 共享 logger
    doiLimiter: this.doiLimiter, // 共享限流器
    executionSemaphore: this.executionSemaphore, // 共享信号量
    configFiles: this.configFiles,
  });
  await cloneSession.reload();
  cloneSession._jupyterSessionManagerPromise = this._jupyterSessionManagerPromise;
  this._clones.push(cloneSession);
  return cloneSession;
}
```

克隆会话共享 logger、限流器、信号量和 Jupyter 管理器，但拥有独立的 Redux Store（通过 new Session 创建）。这使得多项目并行构建时可以隔离状态但不重复创建昂贵资源。

## Jupyter 集成

`jupyterSessionManager()` 使用懒加载单例模式：

```ts
jupyterSessionManager(): Promise<SessionManager | undefined> {
  if (this._jupyterSessionManagerPromise === undefined) {
    this._jupyterSessionManagerPromise = this.createJupyterSessionManager();
  }
  return this._jupyterSessionManagerPromise;
}
```

创建逻辑：
1. 如果设置了 `JUPYTER_BASE_URL` 环境变量，连接到已有 Jupyter 服务器
2. 否则调用 `launchJupyterServer()` 在本地启动新的 Jupyter 服务器
3. 创建 KernelManager 和 SessionManager
4. 绑定生命周期：SessionManager dispose 时清理 KernelManager 和服务器连接

## Fetch 方法

Session 封装了 node-fetch，提供：
- 自动代理支持（排除 localhost）
- 5秒超时提示（不取消请求，仅打印等待信息）
- Node 18 之前版本的 fetch polyfill

## 版本升级提示

`showUpgradeNotice()` 使用 boxen 库绘制美观的升级提示框，仅在检测到新版本且未显示过时展示。支持白标（white-labelled）部署时不显示。

## 生命周期

- `reload()`：重新加载项目和站点配置，如果有站点则重载所有配置
- `dispose()`：清理所有克隆会话和 Jupyter SessionManager，释放资源
- `getAllWarnings(ruleId)`：收集当前会话和所有克隆会话中指定规则的警告，去重后返回

## ISession 接口

```ts
type ISession = {
  API_URL: string;
  configFiles: string[];
  store: Store<RootState>;
  log: Logger;
  doiLimiter: Limit;
  executionSemaphore: Semaphore;
  reload(): Promise<ISession>;
  clone(): Promise<ISession>;
  sourcePath(): string;
  buildPath(): string;
  sitePath(): string;
  contentPath(): string;
  publicPath(): string;
  showUpgradeNotice(): void;
  plugins: ValidatedMystPlugin | undefined;
  loadPlugins(plugins: PluginInfo[]): Promise<MystPlugin>;
  getAllWarnings(ruleId: RuleId): (BuildWarning & { file: string })[];
  jupyterSessionManager(): Promise<SessionManager | undefined>;
  dispose(): void;
  fetch(url, init?): Promise<Response>;
};
```

## 缓存扩展（ISessionWithCache）

通过 `castSession()` 动态挂载的内存缓存：

| 属性 | 类型 | 索引键 |
|------|------|--------|
| `$citationRenderers` | `Record<string, CitationRenderer>` | 文件路径 |
| `$doiRenderers` | `Record<string, SingleCitationRenderer>` | DOI 字符串 |
| `$externalReferences` | `Record<string, ResolvedExternalReference>` | 引用 ID |
| `$mdast` | `Record<string, {sha256?, pre, post?}>` | 绝对文件路径 |
| `$outputs` | `MinifiedContentCache` | - |
| `$siteTemplate` | `MystTemplate` | - |

磁盘缓存通过 `writeToCache()`/`loadFromCache()`/`checkCache()` 操作 `_build/cache/` 目录，支持 `maxAge`（天）过期策略。
