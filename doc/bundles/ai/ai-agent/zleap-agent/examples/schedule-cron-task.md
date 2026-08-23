---
okf_version: "0.2"
type: example
title: 定时任务调度
description: 使用 pg-boss 队列实现 cron 定时任务调度，注册任务处理器、创建/管理定时任务、处理任务执行和死信队列
tags: [zleap-agent, example, tasks, cron, pg-boss, scheduled-task, queue, worker]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/pg-boss-task-queue.md
  - /concepts/agent-core-loop.md
  - /concepts/workspace-pipeline.md
sources:
  - id: zleap-agent-self
    resource: /references/zleap-agent-sources.md
    title: Zleap-Agent 源码参考
---

# 定时任务调度

## 场景说明

本示例演示如何使用 Zleap Agent 的定时任务系统，基于 pg-boss（PostgreSQL 作业队列）实现 cron 定时任务调度。包括：创建和管理定时任务、注册自定义任务处理器、启动 Worker 消费任务队列、处理任务执行结果和死信队列。定时任务可用于定期报告、数据同步、记忆整理（memory_dream）等场景。

**前置条件**：
- 已完成 Zleap Agent 安装配置（参见 [安装配置 Zleap Agent](setup-zleap-agent.md)）
- PostgreSQL + pgvector 数据库已启动并可连接
- 已构建所有包（`pnpm build`）
- 了解 cron 表达式语法（5 字段格式：分 时 日 月 周）

## 完整代码示例

### 示例 1：启动任务 Worker

```bash
# 方式 A：开发模式启动任务 Worker
pnpm dev:tasks

# 方式 B：通过 Docker Compose 启动（独立 worker profile）
docker compose --profile worker up -d

# 方式 C：先启动主服务，再启动 worker
pnpm serve &
pnpm tasks:worker
```

Worker 进程会自动：
1. 连接 PostgreSQL 数据库
2. 确保 pg-boss 队列表和迁移已就绪
3. 注册内置任务处理器（如 `memory_dream`）
4. 开始消费 `zleap.task.run` 队列中的任务
5. 将失败任务移入死信队列 `zleap.task.run.dlq`

### 示例 2：通过代码创建定时任务

```typescript
// examples/schedule-task.ts
// 演示：通过 TaskManagementService 创建定时任务

import { TaskManagementService } from '@zleap/tasks/service';
import { PgBossTaskQueue } from '@zleap/tasks/queue';
import { normalizeCron, normalizeTimezone } from '@zleap/tasks/cron';
import type { CreateTaskInput, TaskActor, TaskRuntimeDefaults } from '@zleap/tasks/types';

// ── 步骤 1：初始化队列和服务 ──
const connectionString = process.env.ZLEAP_DATABASE_URL
  ?? 'postgres://zleap:zleap@127.0.0.1:5433/zleap';

// 创建队列客户端（role: 'client' 用于管理任务，不消费）
const queue = new PgBossTaskQueue({
  connectionString,
  role: 'client',
});

await queue.start();

// 创建 TaskManagementService（需要 store 实现）
// 实际使用时，store 由 @zleap/store 包提供完整实现
declare const taskStore: import('@zleap/tasks/types').TaskServiceDeps['store'];

const taskService = new TaskManagementService({
  store: taskStore,
  queue,
});

// ── 步骤 2：定义执行身份 ──
const actor: TaskActor = {
  userId: 'local-user',
  role: 'admin',  // 'admin' 可以管理所有任务；普通用户只能管理自己的任务
};

// ── 步骤 3：创建 Agent 类型定时任务 ──
const defaults: TaskRuntimeDefaults = {
  avatarId: 'default',
  projectId: null,
  conversationId: null,
  modelConfigId: null,
  permissionMode: 'request_approval',
  targetSpace: null,
  timezone: 'Asia/Shanghai',
};

// 创建一个每天早上 9 点的日报任务
const dailyReportInput: CreateTaskInput = {
  name: '每日日报生成',
  type: 'agent',               // 使用内置 Agent 处理器
  prompt: '请生成今日工作日报：总结今天完成的任务、遇到的问题和明日计划。',
  cron: '0 9 * * *',           // 每天 09:00（cron 5 字段格式）
  timezone: 'Asia/Shanghai',
  enabled: true,
  permissionMode: 'full_access',  // 定时任务通常需要 full_access（无人工审批界面）
  targetSpace: null,           // null = 使用 main workspace
};

const dailyReport = await taskService.createTask(actor, dailyReportInput, defaults);
console.log('✅ 已创建定时任务:');
console.log(`  ID: ${dailyReport.id}`);
console.log(`  名称: ${dailyReport.name}`);
console.log(`  Cron: ${dailyReport.cron} (${dailyReport.timezone})`);
console.log(`  类型: ${dailyReport.type}`);
console.log(`  启用: ${dailyReport.enabled}`);

// ── 步骤 4：创建更多定时任务示例 ──

// 每小时同步一次新闻
const newsSync = await taskService.createTask(actor, {
  name: '新闻同步',
  type: 'agent',
  prompt: '搜索过去一小时内的 AI 领域重要新闻，整理成简报。',
  cron: '0 * * * *',           // 每小时整点
  timezone: 'Asia/Shanghai',
  enabled: true,
  permissionMode: 'request_approval',
}, defaults);

// 每周一早上 8 点发送周报复盘
const weeklyReview = await taskService.createTask(actor, {
  name: '周报复盘',
  prompt: '回顾过去一周的对话记录和工作成果，生成本周复盘报告。',
  cron: '0 8 * * 1',           // 每周一 08:00
  timezone: 'Asia/Shanghai',
  enabled: true,
}, defaults);

// ── 步骤 5：验证 cron 和 timezone ──
try {
  const validCron = normalizeCron('*/30 * * * *');  // 每30分钟
  console.log(`\n验证 cron: ${validCron}`);

  const validTz = normalizeTimezone('Asia/Shanghai');
  console.log(`验证 timezone: ${validTz}`);

  // 无效 cron 会抛出异常
  // normalizeCron('* * *');  // Error: cron_must_have_5_fields
  // normalizeTimezone('Invalid/Zone');  // Error: invalid_timezone
} catch (error) {
  console.error('配置验证失败:', error);
}

// ── 步骤 6：手动触发任务（立即执行一次）──
const { task, run } = await taskService.runNow(actor, dailyReport.id);
console.log(`\n🚀 手动触发任务: ${task.name}`);
console.log(`  Run ID: ${run.id}`);
console.log(`  状态: ${run.status}`);

// 清理
await queue.stop();
```

### 示例 3：注册自定义任务处理器

```typescript
// examples/custom-task-handler.ts
// 演示：注册自定义任务类型的处理器

import { TaskHandlerRegistry } from '@zleap/tasks/registry';
import type { TaskHandler, TaskRunContext, TaskRunResult } from '@zleap/tasks/types';

// ── 自定义任务处理器 1：数据同步 ──
class DataSyncHandler implements TaskHandler {
  readonly type = 'data-sync';

  validate(input: { payload?: Record<string, unknown> }): void {
    // 创建时验证 payload
    if (!input.payload?.sourceUrl) {
      throw new Error('data-sync 任务需要 payload.sourceUrl');
    }
  }

  async run(ctx: TaskRunContext, signal?: AbortSignal): Promise<TaskRunResult> {
    const { task, run } = ctx;
    const sourceUrl = task.payload?.sourceUrl as string;
    const targetTable = (task.payload?.targetTable as string) ?? 'synced_data';

    console.log(`[data-sync] 开始同步: ${sourceUrl} -> ${targetTable}`);
    console.log(`[data-sync] Run ID: ${run.id}, 触发方式: ${run.trigger}`);

    try {
      // 实际实现中：
      // 1. 从 sourceUrl 拉取数据（HTTP GET / 文件读取）
      // 2. 数据转换和清洗
      // 3. 写入目标表
      // 4. 支持 signal 取消

      // 模拟工作
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => resolve(), 1000);
        signal?.addEventListener('abort', () => {
          clearTimeout(timeout);
          reject(new Error('Task aborted'));
        });
      });

      console.log(`[data-sync] 同步完成`);

      return {
        status: 'completed',
        summary: `成功从 ${sourceUrl} 同步数据到 ${targetTable}`,
        metadata: {
          sourceUrl,
          targetTable,
          syncedAt: new Date().toISOString(),
          recordCount: Math.floor(Math.random() * 1000),
        },
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        status: 'failed',
        error: `数据同步失败: ${message}`,
      };
    }
  }
}

// ── 自定义任务处理器 2：系统健康检查 ──
class HealthCheckHandler implements TaskHandler {
  readonly type = 'health-check';

  async run(ctx: TaskRunContext, signal?: AbortSignal): Promise<TaskRunResult> {
    const checks = [
      { name: 'database', ok: true, latency: 12 },
      { name: 'llm-api', ok: true, latency: 230 },
      { name: 'disk-space', ok: true, free: '45GB' },
    ];

    // 模拟检查一个失败项
    if (Math.random() < 0.1) {
      checks[1]!.ok = false;
    }

    const failed = checks.filter(c => !c.ok);
    if (failed.length > 0) {
      return {
        status: 'failed',
        error: `健康检查失败: ${failed.map(f => f.name).join(', ')}`,
        metadata: { checks },
      };
    }

    return {
      status: 'completed',
      summary: `所有 ${checks.length} 项检查通过`,
      metadata: { checks },
    };
  }
}

// ── 注册处理器到注册表 ──
const registry = new TaskHandlerRegistry();
registry.register(new DataSyncHandler());
registry.register(new HealthCheckHandler());

// 查看已注册的任务类型
console.log('已注册的任务处理器类型:');
for (const type of registry.types()) {
  console.log(`  - ${type}`);
}

// 解析处理器
const dataSyncHandler = registry.resolve('data-sync');
console.log(`\n查找 'data-sync' 处理器: ${dataSyncHandler?.type ?? '未找到'}`);

// 未知类型会返回 undefined；undefined/falsy 类型名默认解析为 'agent'
const defaultHandler = registry.resolve(undefined);
console.log(`默认处理器类型: ${defaultHandler?.type ?? '未找到'}`); // 输出 'agent'（如果已注册）
```

### 示例 4：配置 Worker 消费队列

```typescript
// examples/task-worker.ts
// 演示：启动 Worker 消费任务队列

import { PgBossTaskQueue } from '@zleap/tasks/queue';
import { TaskHandlerRegistry, DEFAULT_TASK_TYPE } from '@zleap/tasks/registry';
import type { TaskRunRequest, TaskHandler } from '@zleap/tasks/types';

// ── 步骤 1：创建 Worker 模式队列 ──
const connectionString = process.env.ZLEAP_DATABASE_URL
  ?? 'postgres://zleap:zleap@127.0.0.1:5433/zleap';

const queue = new PgBossTaskQueue({
  connectionString,
  role: 'worker',             // worker 模式：拥有 cron 调度 + 维护 + 消费
  expireInSeconds: 3600,      // 单个任务最大执行时间 1 小时
  heartbeatSeconds: 60,       // Worker 心跳间隔 60 秒
});

// ── 步骤 2：注册任务处理器 ──
const registry = new TaskHandlerRegistry();
// 注册内置 agent 处理器（实际由 @zleap/tasks/execution 提供）
// registry.register(new AgentTaskHandler(...));
// 注册自定义处理器
// registry.register(new DataSyncHandler());

// ── 步骤 3：启动队列并开始消费 ──
async function startWorker() {
  await queue.start();
  console.log('[task-worker] 队列已启动，等待任务...');

  // 消费运行队列
  await queue.workRuns(async (request: TaskRunRequest, signal?: AbortSignal) => {
    const { taskId, runId, trigger, scheduledFor } = request;
    console.log(`[task-worker] 收到任务: taskId=${taskId}, runId=${runId}, trigger=${trigger}`);

    try {
      // 实际实现中：
      // 1. 从 store 读取任务记录（获取 type、prompt、payload 等）
      // 2. 根据 type 从 registry 解析 handler
      // 3. 调用 handler.run(ctx, signal)
      // 4. 将结果写入 store（更新 run 状态、summary、error 等）
      // 5. 如果是 agent 类型，触发 Agent 执行

      // 模拟处理
      // const task = await store.getTask(taskId);
      // const handler = registry.resolve(task.type) ?? registry.resolve(DEFAULT_TASK_TYPE);
      // if (!handler) throw new Error(`No handler for task type: ${task.type}`);
      // const result = await handler.run({ task, run }, signal);
      // await store.updateRun(runId, { status: result.status, ... });

      console.log(`[task-worker] 任务完成: runId=${runId}`);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`[task-worker] 任务失败: runId=${runId}, error=${message}`);
      // 失败的任务由 pg-boss 自动重试（retryLimit=2, retryDelay=30s）
      // 重试耗尽后进入死信队列
    }
  });

  // 消费死信队列（记录失败日志或发送告警）
  await queue.workDeadLetter(async (request: TaskRunRequest) => {
    console.error(`[task-worker:DLQ] 死信任务: taskId=${request.taskId}, runId=${request.runId}`);
    // 实际实现中：
    // - 记录失败详情到日志/监控系统
    // - 发送告警通知
    // - 可以触发人工介入流程
  });

  console.log('[task-worker] Worker 已就绪');
}

// ── 步骤 4：优雅关闭 ──
async function shutdown() {
  console.log('[task-worker] 正在关闭...');
  await queue.stop();
  console.log('[task-worker] 已停止');
  process.exit(0);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

// startWorker().catch(console.error);
```

### 示例 5：Cron 表达式与常用模式

```typescript
// examples/cron-patterns.ts
// 演示：Zleap 支持的 cron 格式和常用模式

import { normalizeCron, normalizeTimezone, systemTimezone } from '@zleap/tasks/cron';

// ── Cron 格式（5 字段）──
// ┌───────── 分钟 (0-59)
// │ ┌─────── 小时 (0-23)
// │ │ ┌───── 日期 (1-31)
// │ │ │ ┌─── 月份 (1-12)
// │ │ │ │ ┌─ 星期 (0-6, 0=周日)
// │ │ │ │ │
// * * * * *

const patterns = [
  // 常用模式
  { cron: '0 9 * * *',     desc: '每天早上 9:00' },
  { cron: '0 * * * *',     desc: '每小时整点' },
  { cron: '*/30 * * * *',  desc: '每 30 分钟' },
  { cron: '0 9 * * 1-5',   desc: '工作日（周一到周五）9:00' },
  { cron: '0 8 * * 1',     desc: '每周一 8:00' },
  { cron: '0 0 1 * *',     desc: '每月 1 号 0:00' },
  { cron: '0 22 * * *',    desc: '每天晚上 10:00' },
  { cron: '*/5 * * * *',   desc: '每 5 分钟' },
  { cron: '0 12 * * 0,6',  desc: '周末中午 12:00' },
  { cron: '30 14 1,15 * *',desc: '每月 1 号和 15 号 14:30' },
];

console.log('=== 常用 Cron 模式 ===');
for (const { cron, desc } of patterns) {
  try {
    const normalized = normalizeCron(cron);
    console.log(`  ${normalformed.padEnd(20)} ${desc}`);
  } catch {
    console.log(`  ${cron.padEnd(20)} ❌ 无效`);
  }
}

// ── 时区 ──
console.log('\n=== 时区配置 ===');
console.log(`系统时区: ${systemTimezone()}`);

const timezones = ['Asia/Shanghai', 'UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo'];
for (const tz of timezones) {
  try {
    const valid = normalizeTimezone(tz);
    console.log(`  ✓ ${valid}`);
  } catch {
    console.log(`  ✗ ${tz} (无效)`);
  }
}

// ── pg-boss 调度特性 ──
// 1. singletonKey: 同一任务的多次调度不会并发执行
// 2. tz: 时区感知（cron 在指定时区下解释）
// 3. 重试策略: retryLimit=2, retryDelay=30s, retryBackoff=true, retryDelayMax=600s
// 4. 过期时间: expireInSeconds=3600（1 小时超时视为失败）
// 5. 死信队列: 重试耗尽后自动移入 DLQ
// 6. 清理策略: deleteAfterSeconds=7*24*3600（7 天后清理完成的任务）
```

### 示例 6：管理任务的完整生命周期

```typescript
// examples/task-lifecycle.ts
// 演示：任务的增删改查和生命周期管理

import type { TaskManagementService } from '@zleap/tasks/service';
import type { TaskActor } from '@zleap/tasks/types';

async function demoTaskLifecycle(taskService: TaskManagementService) {
  const actor: TaskActor = { userId: 'admin', role: 'admin' };
  const defaults = { avatarId: 'default', timezone: 'Asia/Shanghai', permissionMode: 'request_approval' as const };

  // ── 1. 创建任务 ──
  const task = await taskService.createTask(actor, {
    name: '测试周报任务',
    prompt: '生成本周工作周报',
    cron: '0 18 * * 5',  // 每周五 18:00
    timezone: 'Asia/Shanghai',
    enabled: true,
  }, defaults);
  console.log('1. 创建任务:', task.id, task.name);

  // ── 2. 列出所有任务 ──
  const allTasks = await taskService.listTasks(actor, { all: true });
  console.log('2. 任务总数:', allTasks.length);

  // ── 3. 更新任务 ──
  const updated = await taskService.updateTask(actor, task.id, {
    name: '周报生成（已修改）',
    cron: '0 17 * * 5',  // 改为每周五 17:00
    enabled: true,
  });
  console.log('3. 更新任务:', updated.name, updated.cron);

  // ── 4. 禁用/启用任务 ──
  await taskService.updateTask(actor, task.id, { enabled: false });
  console.log('4. 禁用任务');

  await taskService.updateTask(actor, task.id, { enabled: true });
  console.log('   重新启用');

  // ── 5. 手动执行 ──
  const { run } = await taskService.runNow(actor, task.id);
  console.log('5. 手动执行, run ID:', run.id, '状态:', run.status);

  // ── 6. 查看执行历史 ──
  const runs = await taskService.listRuns(actor, task.id, { limit: 10 });
  console.log('6. 执行历史:');
  for (const r of runs) {
    const status = r.status === 'completed' ? '✅' : r.status === 'failed' ? '❌' : '⏳';
    console.log(`   ${status} ${r.id} - trigger: ${r.trigger}`);
  }

  // ── 7. 删除任务 ──
  await taskService.deleteTask(actor, task.id);
  console.log('7. 删除任务');

  // 内置任务（如 memory_dream）不可删除
  try {
    // await taskService.deleteTask(actor, 'builtin-memory-dream-id');
  } catch (error) {
    console.log('   内置任务不可删除 (预期行为)');
  }
}
```

## 逐步解释

### 1. 任务系统架构

Zleap 的定时任务系统由以下核心组件构成：

| 组件 | 包 | 职责 |
|---|---|---|
| `TaskManagementService` | `@zleap/tasks` | 任务 CRUD、手动触发、cron 同步 |
| `PgBossTaskQueue` | `@zleap/tasks` | 基于 pg-boss 的队列实现（调度/入队/消费） |
| `TaskHandlerRegistry` | `@zleap/tasks` | 任务类型→处理器的注册表 |
| `TaskHandler` | `@zleap/tasks` | 任务处理器接口（自定义类型需实现） |
| `ScheduledTaskStore` | `@zleap/store` | 持久化层（任务记录/运行记录的数据库操作） |

### 2. 队列配置

`PgBossTaskQueue` 支持两种角色：

- **`worker`**：完整功能，负责 cron 调度（`schedule: true`）、维护（`supervise: true`）、任务消费
- **`client`**：轻量客户端，仅用于任务管理（创建/更新/删除/手动触发），不消费任务

队列策略配置：
- `policy: 'stately'`：保证任务按状态机流转
- `retryLimit: 2`：失败后最多重试 2 次
- `retryDelay: 30`：首次重试延迟 30 秒
- `retryBackoff: true`：指数退避重试
- `retryDelayMax: 600`：最大重试延迟 600 秒（10 分钟）
- `expireInSeconds: 3600`：任务执行超过 1 小时视为失败
- `heartbeatSeconds: 60`：Worker 心跳间隔，宕机后 60 秒可被其他 Worker 接管
- `deadLetter: 'zleap.task.run.dlq'`：重试耗尽后进入死信队列
- `deleteAfterSeconds: 7*24*3600`：完成的任务 7 天后自动清理

### 3. Cron 规范

```typescript
function normalizeCron(value: string): string {
  const parts = value.trim().split(/\s+/).filter(Boolean);
  if (parts.length !== 5) throw new Error('cron_must_have_5_fields');
  return parts.join(' ');
}
```

Zleap 使用标准 5 字段 cron 格式（**不支持** 6 字段含秒的格式）。时区通过 IANA 标准时区名指定（如 `Asia/Shanghai`、`UTC`），由 `normalizeTimezone()` 验证有效性。

### 4. 任务类型与处理器

任务通过 `type` 字段区分处理方式：

- **`agent`（默认）**：触发 Agent 执行，使用 `prompt` 作为用户输入，执行结果作为对话回复。这是最常用的类型。
- **自定义类型**：通过 `TaskHandlerRegistry.register()` 注册自定义处理器，执行任意逻辑（数据同步、API 调用、健康检查等）。

处理器接口：
```typescript
interface TaskHandler {
  readonly type: string;
  validate?(input: CreateTaskInput): void;  // 可选：创建时验证
  run(ctx: TaskRunContext, signal?: AbortSignal): Promise<TaskRunResult>;
}
```

返回 `TaskRunResult`：
- `status: 'completed' | 'failed'`
- `summary?: string`：执行摘要
- `error?: string`：失败原因
- `agentRunId?: string`：关联的 Agent 运行 ID
- `metadata?: Record<string, unknown>`：附加数据

### 5. 内置任务：memory_dream

`memory_dream` 是内置的记忆整理任务，属于 `BUILT_IN_SCHEDULED_TASK_TYPES`：
- 定期将短期记忆压缩整合为长期记忆
- 不可通过 API 删除（`isBuiltInScheduledTask()` 检查）
- 默认在低峰时段自动运行

### 6. 任务权限模型

- 普通用户只能管理自己创建的任务（`ownerOf(actor)` 过滤）
- `role: 'admin'` 的用户可以管理所有任务
- 删除操作是软删除（`softDeleteTask`），记录保留在数据库中
- 内置任务不可删除

### 7. 活跃运行保护

`runNow()` 方法在手动触发前会检查是否有正在运行的同类任务：
1. 先回收"僵尸"运行（超过 `STALE_ACTIVE_RUN_SECONDS` 秒的活跃运行，默认 1 小时）
2. 如果有活跃运行，新触发会被标记为 `skipped`，避免并发执行
3. pg-boss 的 `singletonKey` 机制保证同一任务不会并发调度

### 8. Worker 独立部署

在生产环境中，Worker 应作为独立进程部署：
- Docker Compose 中使用 `profile: ['worker']` 隔离
- Worker 连接同一个 PostgreSQL 数据库
- 可以运行多个 Worker 实例实现水平扩展（pg-boss 保证任务不被重复消费）
- Web 进程作为 `client` 角色只负责任务管理，不消费任务

## 输出结果

**启动 Worker 输出**：
```
[task-worker] 队列已启动，等待任务...
[task-worker] Worker 已就绪
[task-worker] 收到任务: taskId=task-xxx, runId=run-xxx, trigger=scheduled
[task-worker] 任务完成: runId=run-xxx
```

**创建任务输出**：
```
✅ 已创建定时任务:
  ID: task-abc123
  名称: 每日日报生成
  Cron: 0 9 * * * (Asia/Shanghai)
  类型: agent
  启用: true
```

**Docker Compose Worker 日志**：
```
$ docker compose --profile worker up -d
✔ Container zleap-postgres   Running
✔ Container zleap-worker     Started

$ docker compose logs -f worker
zleap-worker  | [task-queue] Worker started, connection: postgres://zleap:***@postgres:5432/zleap
zleap-worker  | [task-worker] 队列已就绪，等待任务...
```

## 注意事项

1. **Cron 表达式必须是 5 字段**：Zleap 不支持 6 字段（含秒）的 cron 格式。`normalizeCron()` 会验证字段数量，不合法会抛出 `cron_must_have_5_fields` 错误。

2. **时区必须是有效的 IANA 名称**：如 `Asia/Shanghai`、`UTC`、`America/Los_Angeles`。`normalizeTimezone()` 通过 `Intl.DateTimeFormat` 验证时区有效性，`Asia/Beijing` 等非标准名称会被拒绝。

3. **定时任务权限模式**：由于定时任务执行时没有交互式审批界面，推荐使用 `full_access` 权限模式。如果使用 `request_approval`，需要审批的工具会被自动拒绝。

4. **任务执行超时**：默认 1 小时（`expireInSeconds: 3600`）。长时间运行的任务需要确保在超时内完成，或通过心跳机制更新进度。超时后任务会被标记为失败并重试。

5. **幂等性**：任务处理器应设计为幂等的——重复执行同一任务不应产生副作用。因为网络问题或 Worker 宕机可能导致任务被重复投递。

6. **AbortSignal 支持**：处理器必须尊重 `signal` 参数，在收到中止信号时尽快清理资源并退出。这支持 Worker 优雅关闭和任务取消。

7. **死信队列处理**：重试 2 次仍失败的任务会进入 DLQ。务必监控 DLQ，对失败任务进行告警或人工处理。可以通过 `workDeadLetter()` 注册处理器来记录日志或发送通知。

8. **Singleton 保证**：pg-boss 的 `singletonKey` 确保同一任务不会有多个并发执行。但如果任务执行时间超过 cron 间隔，下一次调度会被跳过（不是排队等待）。

9. **系统时区默认值**：如果创建任务时不指定 timezone，会使用 `systemTimezone()`（Node.js 运行环境的时区）。在 Docker 容器中默认是 UTC，可能导致时间不符合预期。**始终显式指定 timezone**。

10. **数据库连接**：Worker 和 Web 进程共享同一个 PostgreSQL 数据库。确保 `pg-boss` 所需的表和扩展已正确创建（由 `@zleap/store` 的迁移机制自动处理）。
