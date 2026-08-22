---
type: Concept
title: Host 运行时与服务编排
description: Zleap-Agent @zleap/host 包的宿主运行时架构——PostgreSQL 四级回退自动管理、runServe 服务编排主管、安装/升级生命周期、运行时锁与多实例防护、配置体系与环境变量映射。
tags: [zleap-agent, host, runtime, supervisor, postgres, lifecycle, service-orchestration, lock, config]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: host-supervisor
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/host/src/supervisor.ts
    title: runServe 服务编排主管
  - id: host-postgres
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/host/src/postgres.ts
    title: PostgreSQL 自动管理
  - id: host-lifecycle
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/host/src/lifecycle.ts
    title: 安装/setup 生命周期
  - id: host-config
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/host/src/config.ts
    title: 配置加载与环境变量映射
  - id: host-constants
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/host/src/constants.ts
    title: 默认常量
  - id: host-paths
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/host/src/paths.ts
    title: 路径解析
  - id: host-lock
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/host/src/lock.ts
    title: 运行时锁
---

# Host 运行时与服务编排

`@zleap/host` 是 Zleap-Agent 的宿主运行时层，负责在用户机器上管理完整的服务栈生命周期：PostgreSQL 数据库的自动发现/启动/初始化、Web 服务（Next.js）、Worker（任务调度+记忆抽取）、Gateway（IM 网关）四个子进程的编排与监控，以及安装、配置、升级、锁管理等基础设施。host 包被 CLI 和桌面端（Tauri）共同调用，是 Zleap-Agent 作为本地应用运行的核心引擎。

## 整体架构

host 包的核心是 `runServe()` 函数——服务编排主管。它按严格顺序启动 PostgreSQL → 构建 → 迁移 → Web → Worker → Gateway，并维护一个 `ServeState` 状态文件实现多实例协调：

```mermaid
graph TB
    subgraph 入口
        CLI[CLI serve 命令]
        DESKTOP[Tauri Desktop bootstrap]
        SETUP[zleap setup/init]
    end

    subgraph host 运行时
        LOCK[运行时锁<br/>acquireRuntimeLock]
        direction TB
        PG[ensurePostgres<br/>四级回退]
        BUILD[runDevBuild /<br/>runWebProductionBuild]
        MIGRATE[runMigrate]
        WEB[Web Server<br/>Next.js dev / server.js]
        WORKER[Worker<br/>tasks+gateway runner]
        GW[Gateway<br/>Feishu/WeChat/FeishuCli]
        STATE[(serve.json<br/>ServeState)]
    end

    subgraph 外部依赖
        POSTGRES[(PostgreSQL<br/>127.0.0.1:5433)]
        BROWSER[浏览器 onboarding]
    end

    CLI --> LOCK
    DESKTOP --> LOCK
    SETUP --> LOCK

    LOCK --> PG
    PG --> BUILD
    BUILD --> MIGRATE
    MIGRATE --> WEB & WORKER
    WEB --> STATE
    WORKER --> STATE
    GW --> STATE

    PG --> POSTGRES
    WEB -.->|health check| BROWSER
```

### 服务拓扑

```
┌─────────────────────────────────────────────────────────────┐
│                    runServe Supervisor                      │
│                     (Node.js 主进程)                         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  PostgreSQL │  │  Web (Next)  │  │  Worker (Child)      │ │
│  │  (managed/  │  │  dev:pnpm    │  │  ├─ Tasks Scheduler  │ │
│  │   bundled/  │  │  prod:server │  │  ├─ Memory Dream     │ │
│  │   local/    │  │   .js :4789  │  │  └─ Compaction       │ │
│  │   docker)   │  │              │  │                      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                    │        │
│                                        ┌───────────┘        │
│                                        ▼                    │
│                              ┌─────────────────────┐       │
│                              │  Gateway (Child)     │       │
│                              │  ├─ Feishu           │       │
│                              │  ├─ WeChat/iLink     │       │
│                              │  └─ Feishu CLI       │       │
│                              └─────────────────────┘       │
│                                                             │
│  状态文件: ~/.zleap/state/serve.json                         │
│  锁文件:   ~/.zleap/state/serve.lock                         │
└─────────────────────────────────────────────────────────────┘
```

## runServe 服务编排

`runServe()` 是 host 包最核心的函数，负责完整服务栈的启动、监控和优雅关闭：

```typescript
// supervisor.ts L74-L201
export async function runServe(options: ServeOptions = {}): Promise<number> {
  const repoRoot = options.repoRoot ?? resolveRepoRoot();
  const mode = options.mode ?? (process.env.ZLEAP_SERVE_MODE === 'production' ? 'production' : 'dev');
  const env = buildServeEnv({ ...options.env, ZLEAP_REPO_ROOT: repoRoot, ZLEAP_SERVE_MODE: mode });
  const startedBy = options.startedBy ?? inferStartedBy(env, mode);
  const sessionId = options.sessionId ?? env.ZLEAP_LAUNCHER_SESSION_ID ?? randomUUID();
  const stopPolicy = options.stopPolicy ?? inferStopPolicy(env, startedBy);
  const lock = await acquireRuntimeLock(layout.serveLockPath, { owner: `serve:${startedBy}` });

  // 1. 端口检查（dev 模式）
  if (mode === 'dev') await prepareDevServe(Number(webPort));
  else { /* production 模式检测是否已运行 */ }

  // 2. PostgreSQL
  if (!options.skipPostgres) await ensurePostgres(env);

  // 3. 构建
  if (!skipBuild) {
    if (mode === 'production') { await runDevBuild(repoRoot, env); await runWebProductionBuild(repoRoot, env); }
    else { await runDevBuild(repoRoot, env); }
  }

  // 4. 数据库迁移
  await runMigrate(repoRoot, env);

  // 5. 启动 Web
  const web = mode === 'production'
    ? spawnDetached(nodeBin, ['server.js'], { cwd: webCwd, env: { PORT: webPort } })
    : spawnDetached(pnpm.command, [...pnpm.argsPrefix, '--filter', '@zleap/web', 'dev:next'], { cwd: repoRoot, env });

  // 6. 启动 Worker（自动重启）
  spawnWorker(repoRoot, env, services, entries);

  // 7. 条件启动 Gateway
  if (startGateway) spawnGateway(repoRoot, env, services, entries);

  // 8. 持久化状态并释放锁
  await persistServeState(state);
  await lock.release();

  // 9. 等待 web 退出 + 信号处理
  process.on('SIGINT', () => void shutdown(0));
  process.on('SIGTERM', () => void shutdown(0));
  await waitForWebExit(web);
  await shutdown(0);
  return 0;
}
```

### ServeState 状态模型

服务启动后将完整状态写入 `serve.json`，供 CLI 状态查询、桌面端会话管理和健康检查使用：

```typescript
// supervisor.ts L47-L61
export type ServeState = {
  pid: number;                    // Supervisor 进程 PID
  startedAt: string;              // ISO 时间戳
  mode: ServeMode;                // 'dev' | 'production'
  home: string;                   // ~/.zleap
  runtimeRoot: string;            // 运行时根目录
  runtimeVersion: string;         // 版本号
  runtimeBuiltAt?: string;        // 构建时间
  startedBy: ServeStartedBy;      // 'cli' | 'desktop' | 'service' | 'dev'
  sessionId: string;              // 启动会话 UUID
  stopPolicy: ServeStopPolicy;    // 'explicit' | 'onDesktopQuit' | 'keepAlive'
  webPort: string;                // Web 端口
  webUrl: string;                 // Web URL
  services: ServeServiceState[];  // 子服务列表
};
```

### 启动来源与停止策略

启动来源通过环境变量自动推断，不同来源有不同的默认停止策略：

```typescript
// supervisor.ts L458-L481
function inferStartedBy(env: NodeJS.ProcessEnv, mode: ServeMode): ServeStartedBy {
  if (raw === 'cli' || raw === 'desktop' || raw === 'service' || raw === 'dev') return raw;
  if (env.ZLEAP_DESKTOP === '1' || env.ZLEAP_INSTALL_METHOD === 'desktop') return 'desktop';
  return mode === 'dev' ? 'dev' : 'cli';
}

function inferStopPolicy(env: NodeJS.ProcessEnv, startedBy: ServeStartedBy): ServeStopPolicy {
  if (raw === 'explicit' || raw === 'onDesktopQuit' || raw === 'keepAlive') return raw;
  if (startedBy === 'desktop') return 'onDesktopQuit';  // 桌面退出即停
  if (startedBy === 'service') return 'keepAlive';      // 系统服务常驻
  return 'explicit';                                    // CLI 需显式停止
}
```

| startedBy | 默认 stopPolicy | 说明 |
|-----------|-----------------|------|
| `desktop` | `onDesktopQuit` | Tauri 桌面端启动，桌面窗口关闭时停止服务 |
| `service` | `keepAlive` | 系统服务模式常驻，不自动停止 |
| `cli` | `explicit` | CLI 启动，需 `zleap stop` 显式停止 |
| `dev` | `explicit` | 开发模式 |

### Worker/Gateway 自动重启

Worker 和 Gateway 子进程崩溃后自动 1 秒重启，保证服务高可用：

```typescript
// supervisor.ts L311-L323
worker.on('exit', (code, signal) => {
  if (shuttingDown) return;
  process.stderr.write(`worker 退出 (${signal ?? code})，1 秒后重启…\n`);
  setTimeout(() => {
    if (shuttingDown) return;
    spawnWorker(repoRoot, env, services, entries);
  }, 1_000);
});
```

### stopServe 会话所有权检查

停止服务时支持会话所有权校验，防止误杀其他启动方的服务：

```typescript
// supervisor.ts L216-L226
if (options.onlyIfSessionOwned) {
  if (options.sessionId && state.sessionId !== options.sessionId) {
    return { stopped: [], missing: false, skipped: `runtime started by another session` };
  }
  if (options.startedBy && state.startedBy !== options.startedBy) {
    return { stopped: [], missing: false, skipped: `runtime started by ${state.startedBy}` };
  }
  if (state.stopPolicy !== 'onDesktopQuit') {
    return { stopped: [], missing: false, skipped: `runtime stop policy is ${state.stopPolicy}` };
  }
}
```

桌面端退出时只停止自己启动的（startedBy==='desktop' 且 sessionId 匹配且 stopPolicy==='onDesktopQuit'）服务，不会影响 CLI 启动的服务。

## PostgreSQL 四级回退

`ensurePostgres()` 实现了数据库的自动发现和启动，按优先级依次尝试四个来源：

```mermaid
flowchart TD
    START[ensurePostgres] --> CFG{自定义 URL?<br/>ZLEAP_DATABASE_URL<br/>/DATABASE_URL}
    CFG -->|是且非本地| EXT[使用外部数据库<br/>直接返回]
    CFG -->|否/本地| BUNDLED{bundled PG?<br/>随包分发/懒安装}
    BUNDLED -->|找到| LOCAL1[ensureLocalPostgres<br/>启动 bundled PG]
    BUNDLED -->|未找到| LOCALBIN{本地安装 PG?<br/>Homebrew/系统PATH<br/>检查 pgvector}
    LOCALBIN -->|找到且有pgvector| LOCAL2[ensureLocalPostgres<br/>启动本地 PG]
    LOCALBIN -->|未找到| DOCKER{Docker Compose<br/>可用?}
    DOCKER -->|是| DC[docker compose up -d postgres<br/>等待 pg_isready]
    DOCKER -->|否| ERR[抛出错误:<br/>要求安装 PG/Docker/配置URL]

    LOCAL1 --> INIT[初始化 PG: initdb → pg_ctl start<br/>→ CREATE ROLE → CREATE DB → vector 扩展]
    LOCAL2 --> INIT
    DC --> READY[PostgreSQL 就绪]
    EXT --> READY
    INIT --> READY
```

```typescript
// postgres.ts L19-L66
export async function ensurePostgres(env: PostgresEnv): Promise<void> {
  // Level 0: 自定义数据库 URL（非本地托管的）
  const configuredDatabaseUrl = env.ZLEAP_DATABASE_URL ?? env.DATABASE_URL ?? ...;
  if (configuredDatabaseUrl && !isManagedLocalDatabaseUrl(configuredDatabaseUrl)) return;

  // Level 1: Bundled PG（随包分发/懒安装）
  let bundled = resolveBundledPostgresBin(repoRoot);
  if (!bundled) {
    try { bundled = await ensurePostgresToolsInstalled({ repoRoot }); }
    catch { /* lazy install failed, try next */ }
    bundled = resolveBundledPostgresBin(repoRoot);
  }
  if (bundled) { await ensureLocalPostgres(bundled, env); return; }

  // Level 2: 本地安装 PG（Homebrew/系统 PATH）
  const local = await findLocalPostgresBin();
  if (local) { await ensureLocalPostgres(local, env); return; }

  // Level 3: Docker Compose
  if (await runQuiet('docker', ['compose', 'version'], { env })) {
    await run('docker', ['compose', 'up', '-d', 'postgres'], { env, cwd: repoRoot });
    await waitForPostgres({ command: 'docker', args: ['compose', 'exec', '-T', 'postgres', 'pg_isready', ...], env, cwd: repoRoot });
    return;
  }

  throw new Error('Postgres is required. Set ZLEAP_DATABASE_URL, allow bootstrap to download portable Postgres, ...');
}
```

### 本地 PG 自动初始化

当使用 bundled 或本地 PG 时，`ensureLocalPostgres()` 自动完成全套初始化：

```typescript
// postgres.ts L68-L124
async function ensureLocalPostgres(pgBin: string, env: PostgresEnv): Promise<void> {
  // 1. 检查 PG 是否已运行
  if (!(await runQuiet(pgIsready, ['-h', DEFAULT_PG_HOST, '-p', DEFAULT_PG_PORT, '-d', 'postgres'], { env: pgEnv }))) {
    // 2. initdb（首次）
    await mkdir(dataDir, { recursive: true });
    if (!existsSync(join(dataDir, 'PG_VERSION'))) {
      await run(initdb, ['-D', dataDir, '--auth=trust'], { env: pgEnv });
    }
    // 3. pg_ctl start（端口 5433）
    await run(pgCtl, ['-D', dataDir, '-l', join(dataDir, 'postgres.log'), '-o', `-p ${DEFAULT_PG_PORT}`, 'start'], { env: pgEnv });
    await waitForPostgres({ command: pgIsready, args: [...], env: pgEnv });
  }

  // 4. 创建 zleap 角色（SUPERUSER, 密码 zleap）
  await run(psql, [..., '-c',
    `DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DEFAULT_PG_USER}')
     THEN CREATE ROLE ${DEFAULT_PG_USER} LOGIN SUPERUSER PASSWORD '${DEFAULT_PG_PASSWORD}';
     ELSE ALTER ROLE ${DEFAULT_PG_USER} WITH LOGIN SUPERUSER PASSWORD '${DEFAULT_PG_PASSWORD}';
     END IF; END $$;`], { env: pgEnv });

  // 5. 创建 zleap 数据库
  if (!databaseExists) {
    await run(createdb, ['-h', DEFAULT_PG_HOST, '-p', DEFAULT_PG_PORT, '-U', DEFAULT_PG_USER, '-O', DEFAULT_PG_USER, DEFAULT_PG_DATABASE], { env: pgEnv });
  }

  // 6. 启用 vector 扩展（失败静默降级）
  await ensurePgVectorExtension(psql, pgEnv);
}
```

关键设计：
- **端口 5433**：非默认 5432，避免与用户已有 PG 冲突
- **`--auth=trust`**：本地信任认证，仅监听 127.0.0.1
- **pgvector 失败静默降级**：无 vector 扩展时使用 faux embeddings，功能受限但不阻断启动
- **数据目录隔离**：`~/.zleap/postgres-{major}/` 按 PG 大版本隔离

### pgvector 扩展

```typescript
// postgres.ts L142-L165
async function ensurePgVectorExtension(psql: string, env: PostgresEnv): Promise<void> {
  try {
    await run(psql, [..., '-c', 'CREATE EXTENSION IF NOT EXISTS vector;'], { env });
  } catch {
    // Bundled/dev PG without pgvector still works with faux embeddings.
  }
}
```

启用失败时静默忽略，store 层在无向量列时自动跳过向量搜索路径，仅用词法/实体/图三路召回。

## 安装与 Setup 生命周期

### finishInstall 安装后流程

桌面端首次安装或 CLI 首次运行后调用 `finishInstall()`：

```typescript
// lifecycle.ts L31-L64
export async function finishInstall(options: FinishInstallOptions = {}): Promise<void> {
  // 1. 确保目录结构
  await ensureLayoutDirs();  // state/data/config/logs

  // 2. 写入安装状态
  await writeInstallState({ method: options.method ?? 'cli', version: options.version, ... });

  // 3. 写入 bootstrap 状态
  if (options.version) {
    await writeBootstrapState({ completedAt: new Date().toISOString(), version: options.version, ... });
  }

  // 4. 启动 detached serve
  if (options.startServe !== false) {
    await startDetachedServe({ env });
    const ok = await waitForHealthLive(env, 120_000);  // 120 秒超时
    if (!ok) process.stderr.write('警告：服务启动超时，请运行 zleap doctor 排查\n');
  }

  // 5. 打开浏览器 onboarding 页面
  if (options.openBrowser !== false) {
    await openOnboardingUrl(env);
  }
}
```

### Zleap Home 目录结构

```
~/.zleap/
├── config.json          # 配置文件（模型、数据库、embedding）
├── state/
│   ├── serve.json       # ServeState 运行时状态
│   └── serve.lock       # 运行时锁
├── data/                # 数据目录
├── logs/
│   └── serve.log        # 服务日志
├── app/
│   └── current/         # 当前版本运行时（fat 模式）
├── postgres-{major}/    # 本地 PostgreSQL 数据目录
├── gateway/             # 网关去重/会话存储
├── tools/               # 托管工具（Node.js 等）
└── bootstrap/           # 引导状态
```

```typescript
// lifecycle.ts L18-L24
export async function ensureLayoutDirs(): Promise<void> {
  const layout = zleapLayout();
  await mkdir(layout.stateDir, { recursive: true });
  await mkdir(layout.dataDir, { recursive: true });
  await mkdir(layout.configDir, { recursive: true });
  await mkdir(layout.logsDir, { recursive: true });
}
```

### runSetupFlow CLI setup 流程

```typescript
// lifecycle.ts L87-L108
export async function runSetupFlow(options: { openBrowser?: boolean } = {}): Promise<number> {
  await ensureLayoutDirs();
  const runtime = await ensureRuntimeInstalled({ method: 'cli', downloadIfMissing: true });
  // 健康检查
  const healthy = await waitForHealthLive(env, 3_000);
  if (!healthy) {
    await startDetachedServe({ env, startedBy: 'cli', stopPolicy: 'explicit' });
    const ok = await waitForHealthLive(env, 120_000);
    if (!ok) { process.stderr.write('无法启动本地服务，请运行 zleap doctor\n'); return 1; }
  }
  if (options.openBrowser !== false) await openOnboardingUrl(env);
  return 0;
}
```

## 运行时锁

为防止多实例并发启动导致端口冲突和数据库损坏，host 使用文件锁实现互斥：

```typescript
// 锁获取在 runServe 入口
const lock = await acquireRuntimeLock(layout.serveLockPath, { owner: `serve:${startedBy}` });
try {
  // ... 启动服务 ...
  await persistServeState(state);
  await lock.release();  // 启动成功后释放锁（允许管理操作）
  // ... 持续运行 ...
} catch (error) {
  await stopTrackedChildren();
  await lock.release();
  throw error;
}
```

同时支持 `reclaimStaleRuntimeLock()` 回收陈旧锁（进程崩溃后锁文件残留）。

## 健康检查

`healthCheck()` 对四个服务分别探活，返回结构化报告：

```typescript
// supervisor.ts L260-L294
export async function healthCheck(env: NodeJS.ProcessEnv = buildServeEnv()): Promise<HealthReport> {
  // PostgreSQL: pg.Client 连接测试
  const pgOk = databaseUrl ? await probePostgres(databaseUrl) : false;

  // Web: HTTP /api/health/live（5 秒超时）
  const res = await fetch(`${url}/api/health/live`, { signal: AbortSignal.timeout(5_000) });

  // Worker/Gateway: 通过 serve.json 中的 PID 检查进程存活
  const workerPid = state?.services.find((s) => s.name === 'worker')?.pid;
  const gatewayPid = state?.services.find((s) => s.name === 'gateway')?.pid;

  return {
    postgres: { ok: pgOk, detail: pgOk ? sanitizedUrl : '无法连接' },
    web: { ok: webOk, detail: webDetail, url },
    worker: { ok: Boolean(workerPid && await pidAlive(workerPid)), detail: workerPid ? `pid ${workerPid}` : '未记录' },
    gateway: { ok: gatewayPid ? await pidAlive(gatewayPid) : false, detail: gatewayPid ? `pid ${gatewayPid}` : '未启动' },
  };
}
```

进程存活检查使用 `process.kill(pid, 0)`（发送信号 0 不影响进程，仅检查权限）：

```typescript
// supervisor.ts L504-L511
async function pidAlive(pid: number): Promise<boolean> {
  try { process.kill(pid, 0); return true; }
  catch { return false; }
}
```

## 配置体系

配置存储在 `~/.zleap/config.json`，支持环境变量覆盖和密钥脱敏显示：

```typescript
// config.ts L15-L24
export type CliConfig = {
  model?: CustomModelConfig;       // { model, baseUrl, apiKey, protocol, displayName }
  database?: { url: string };
  embedding?: EmbeddingConfig;     // { model, baseUrl, apiKey, dimension }
  gateway?: { stateDir?: string };
  onboarded?: boolean;
  session?: CliSessionPrefs;
};
```

### 环境变量映射

9 个配置点映射到环境变量，环境变量优先级高于 config.json：

```typescript
// config.ts L156-L166
export const CONFIG_ENV_MAP: Record<string, string> = {
  'database.url': 'ZLEAP_DATABASE_URL',
  'model.baseUrl': 'ZLEAP_MODEL_BASE_URL',
  'model.apiKey': 'ZLEAP_MODEL_API_KEY',
  'model.model': 'ZLEAP_MODEL_NAME',
  'model.protocol': 'ZLEAP_MODEL_PROTOCOL',
  'embedding.model': 'ZLEAP_EMBED_MODEL',
  'embedding.baseUrl': 'ZLEAP_EMBED_BASE_URL',
  'embedding.apiKey': 'ZLEAP_EMBED_API_KEY',
  'embedding.dimension': 'ZLEAP_EMBED_DIM',
};
```

同时追踪 15 个环境变量（含 `ZLEAP_302_API_KEY`、`LLM_BASE_URL/API_KEY/MODEL` 等）在 `zleap config` 命令中展示。

### 密钥脱敏

```typescript
// config.ts L145-L153
function formatConfigValue(key: string, value: unknown): string {
  if (value === undefined || value === null) return '—';
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  const text = String(value);
  if (/secret|apikey|api_key|password|token/i.test(key) && text.length > 0) return '***';
  return text;
}
```

匹配 `secret/apikey/api_key/password/token` 的 key 值显示为 `***`，防止密钥泄漏。

### dotted-path 读写

```typescript
// config.ts L103-L129
export function getConfigValue(config: CliConfig, path: string): unknown {
  // 按 '.' 分割路径逐级访问，如 'model.baseUrl'
}

export function setConfigValue(config: CliConfig, path: string, value: unknown): CliConfig {
  // immutable 地设置 dotted path，中间缺失对象自动创建
  const clone = structuredClone(config);
  // ... 逐级创建嵌套对象 ...
  return clone;
}
```

## 路径解析

`resolveRuntimeRoot()` 按 6 级优先级解析运行时根目录，适配 dev monorepo、打包安装、bundled 等多种运行环境：

```typescript
// paths.ts L19-L43
export function resolveRuntimeRoot(start = import.meta.url): string {
  // 1. ZLEAP_REPO_ROOT 环境变量
  if (process.env.ZLEAP_REPO_ROOT?.trim()) return process.env.ZLEAP_REPO_ROOT.trim();
  // 2. ZLEAP_APP_ROOT 环境变量
  if (process.env.ZLEAP_APP_ROOT?.trim()) return process.env.ZLEAP_APP_ROOT.trim();
  // 3. dev monorepo root（pnpm-workspace.yaml + packages/runtime/package.json）
  const devRoot = devMonorepoRoot(start);
  if (isDevMonorepoRoot(devRoot)) return devRoot;
  // 4. ~/.zleap/app/current（安装后的 runtime）
  if (isAppComplete(layout.current, 'base')) return layout.current;
  // 5. ZLEAP_BUNDLED_ROOT
  if (bundled && isAppComplete(bundled, 'base')) return bundled;
  // 6. fallback devRoot
  return devRoot;
}
```

### isBundledInstall 判定

```typescript
// paths.ts L77-L92
export function isBundledInstall(repoRoot = resolveRuntimeRoot()): boolean {
  if (process.env.ZLEAP_APP_ROOT?.trim() || process.env.ZLEAP_BUNDLED_ROOT?.trim()) {
    if (isAppComplete(repoRoot, 'base')) return true;
  }
  if (process.env.ZLEAP_SKIP_BUILD === '1' || process.env.ZLEAP_SERVE_MODE === 'production') {
    if (existsSync(join(repoRoot, 'node', 'bin', 'node')) || existsSync(join(repoRoot, 'node', 'node.exe'))) return true;
    if (existsSync(join(repoRoot, 'web', 'server.js'))) return true;
  }
  // 无 packages/web/package.json 但有 web/server.js = 打包安装
  return existsSync(join(repoRoot, 'web', 'server.js'))
    && !existsSync(join(repoRoot, 'packages', 'web', 'package.json'));
}
```

## Dev 模式端口回收

开发模式启动前自动清理残留进程和占用端口：

```typescript
// supervisor.ts L514-L553
async function prepareDevServe(webPort: number): Promise<void> {
  // 检查是否已有运行中的 serve
  const existing = await readServeState();
  if (existing?.pid && await pidAlive(existing.pid)) {
    throw new Error(`Zleap 本地服务已在运行：${existing.webUrl}`);
  }
  // 停止旧 serve 和孤儿进程
  await stopServe();
  await stopOrphanDevServices(resolveRepoRoot());
  // 回收被占用的 Web 端口
  await reclaimDevWebPort(webPort);
}
```

端口回收在 Unix 上通过 `lsof -ti tcp:{port} -sTCP:LISTEN` 查找占用进程，先 SIGTERM 再 SIGKILL。Windows 上不做自动回收（提示用户手动处理）。

## 默认常量

```typescript
// constants.ts
export const DEFAULT_DATABASE_URL = 'postgres://zleap:zleap@127.0.0.1:5433/zleap';
export const DEFAULT_EMBED_DIM = '1536';
export const DEFAULT_PG_HOST = '127.0.0.1';
export const DEFAULT_PG_PORT = '5433';
export const DEFAULT_PG_USER = 'zleap';
export const DEFAULT_PG_PASSWORD = 'zleap';
export const DEFAULT_PG_DATABASE = 'zleap';
export const DEFAULT_WEB_PORT = 4789;
export const DEFAULT_DEV_WEB_PORT = 3000;
export const STATE_FILE = 'serve.json';
```

| 常量 | 值 | 说明 |
|------|----|------|
| 数据库 URL | `postgres://zleap:zleap@127.0.0.1:5433/zleap` | 本地托管 PG 默认连接串 |
| PG 端口 | 5433 | 非默认 5432，避免冲突 |
| Web 端口 | 4789 | 生产模式 Web 服务端口 |
| Dev Web 端口 | 3000 | Next.js dev server 默认端口 |
| Embedding 维度 | 1536 | OpenAI text-embedding-ada-002 维度 |
| 健康检查超时 | 120 秒 | 首次启动等待超时 |
| Worker 重启延迟 | 1 秒 | 崩溃后自动重启等待时间 |
| PG 就绪轮询 | 最多 40 次 × 1.5 秒 = 60 秒 | waitForPostgres 超时 |
| Pool 连接超时 | 3 秒 | createStore 快速失败 |

## 类型签名速查

```typescript
// 服务编排
type ServeMode = 'dev' | 'production';
type ServeStartedBy = 'cli' | 'desktop' | 'service' | 'dev';
type ServeStopPolicy = 'explicit' | 'onDesktopQuit' | 'keepAlive';
type ServeServiceState = { name: string; pid?: number; status?: 'starting' | 'running' | 'stopped' | 'failed' };
type ServeState = { pid: number; startedAt: string; mode: ServeMode; home: string; runtimeRoot: string;
  runtimeVersion: string; runtimeBuiltAt?: string; startedBy: ServeStartedBy; sessionId: string;
  stopPolicy: ServeStopPolicy; webPort: string; webUrl: string; services: ServeServiceState[]; };
type HealthReport = { postgres: { ok: boolean; detail: string }; web: { ok: boolean; detail: string; url: string };
  worker: { ok: boolean; detail: string }; gateway: { ok: boolean; detail: string } };

function runServe(options?: ServeOptions): Promise<number>;
function stopServe(options?: StopServeOptions): Promise<{ stopped: string[]; missing: boolean; skipped?: string }>;
function readServeState(): Promise<ServeState | undefined>;
function healthCheck(env?: NodeJS.ProcessEnv): Promise<HealthReport>;

// PostgreSQL
function ensurePostgres(env: PostgresEnv): Promise<void>;
function probePostgres(databaseUrl: string): Promise<boolean>;
function isManagedLocalDatabaseUrl(databaseUrl: string): boolean;

// 生命周期
function finishInstall(options?: FinishInstallOptions): Promise<void>;
function runSetupFlow(options?: { openBrowser?: boolean }): Promise<number>;
function ensureLayoutDirs(): Promise<void>;

// 配置
type CliConfig = { model?: CustomModelConfig; database?: { url: string }; embedding?: EmbeddingConfig;
  gateway?: { stateDir?: string }; onboarded?: boolean; session?: CliSessionPrefs; };
function loadConfig(): Promise<CliConfig>;
function saveConfig(config: CliConfig): Promise<void>;
function getConfigValue(config: CliConfig, path: string): unknown;
function setConfigValue(config: CliConfig, path: string, value: unknown): CliConfig;
function resolvePersistence(config: CliConfig): PersistenceConfig;

// 路径
function resolveRuntimeRoot(start?: string): string;
function isBundledInstall(repoRoot?: string): boolean;
```
