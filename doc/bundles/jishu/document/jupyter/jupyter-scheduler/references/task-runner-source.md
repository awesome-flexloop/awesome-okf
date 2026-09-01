---
source: jupyter_scheduler/task_runner.py
title: TaskRunner 定时调度源码解析
---

# TaskRunner 定时调度源码解析

> 信源路径：`jupyter_scheduler/task_runner.py`（344行）

## 类继承体系

```
LoggingConfigurable
└── BaseTaskRunner (抽象基类)
    └── TaskRunner (默认实现，优先队列+内存缓存)
```

## BaseTaskRunner 抽象基类

| 配置/方法 | 说明 |
|----------|------|
| `poll_interval` | 轮询间隔（默认10秒，可配置） |
| `start()` | async方法，服务器启动时调用 |
| `add_job_definition(id)` | 添加新定时作业到队列 |
| `update_job_definition(id, model)` | 更新作业定义 |
| `delete_job_definition(id)` | 删除作业定义 |
| `pause_jobs(id)` | 暂停作业（抽象） |
| `resume_jobs(id)` | 恢复作业（抽象） |

## TaskRunner 默认实现

### 核心数据结构

**PriorityQueue**（基于heapq）：
- 最小堆，按 `next_run_time` 排序
- 存储 `JobDefinitionTask(job_definition_id, next_run_time)`
- `peek()` 获取最早任务（不弹出）
- `push(task)` / `pop()` 入队/出队

**Cache**（内存SQLite `"sqlite://"`）：
- 表 `job_definitions_cache`：job_definition_id（主键）、next_run_time、active、timezone、schedule
- 提供 load/get/put/update/delete CRUD操作
- 用于持久化调度状态（与主数据库分离，避免跨进程并发问题）

### 启动流程 start()

```
1. populate_cache()：从数据库加载所有带schedule的JobDefinition
   - 计算每个作业的next_run_time
   - 写入Cache
   - active的作业加入PriorityQueue
2. 无限循环：
   a. process_queue() 处理到期任务
   b. await asyncio.sleep(poll_interval)
```

### process_queue() 调度逻辑

```
while 队列非空:
    task = queue.peek()  // 取最早任务
    cache = cache.get(task.job_definition_id)
    
    if cache不存在 → queue.pop()，continue（已删除）
    if !cache.active 或 queue_run_time != cache_run_time → queue.pop()，continue（已更新/暂停）
    
    time_diff = 当前时间 - task.next_run_time
    if time_diff < 0 → break（未到时间）
    
    // 执行作业
    try:
        create_job(task.job_definition_id)  // 从staging读取input_uri创建作业
    except:
        log.exception()
    
    queue.pop()
    next_time = compute_next_run_time(cache.schedule, cache.timezone)
    cache.update(next_run_time=next_time)
    queue.push(JobDefinitionTask(id, next_time))
```

**关键设计**：Queue中的任务可能是过期的（已更新/删除/暂停），process_queue在执行前通过Cache校验任务有效性，无效任务直接弹出跳过。这避免了在update/delete时需要搜索并修改堆中元素。

### 时间计算

- `compute_next_run_time(schedule, timezone)`：使用croniter计算下次执行时间
- 有timezone时使用pytz时区的本地时间，否则使用UTC
- 时间戳使用毫秒级Unix时间戳

### 增删改处理

**add_job_definition(id)**：计算next_run_time，写入Cache，active则加入队列。

**update_job_definition(id, model)**：合并Cache中的旧值和新值，计算新next_run_time，更新Cache；若时间变化或从暂停恢复则推入新任务到队列（旧任务在process_queue时被Cache校验跳过）。

**delete_job_definition(id)**：仅从Cache删除（队列中的过期任务在process_queue时自动跳过）。
