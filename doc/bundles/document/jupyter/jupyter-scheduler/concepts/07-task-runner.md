# TaskRunner 定时调度

TaskRunner 负责管理基于 cron 表达式的定时作业（Job Definition）的调度执行。它使用优先队列（PriorityQueue）管理待执行任务，并通过轮询机制触发到期作业。

## 核心设计

### 为什么不直接用 APScheduler？

Jupyter Scheduler 选择了轻量级的自研实现而非 APScheduler，原因是：
1. 作业状态需要与 ORM 层的 JobDefinition 表同步
2. 多进程场景下需要避免重复执行（通过SQLAlchemy数据库+内存缓存双层校验）
3. 与 Scheduler 的 create_job 流程深度集成

### 数据结构

**优先队列**（`heapq` 最小堆）：
```python
@dataclass(order=True)
class JobDefinitionTask:
    next_run_time: int     # 毫秒时间戳，优先队列排序键
    job_definition_id: str
```

队列按 `next_run_time` 升序排列，`peek()` 始终返回最早待执行的任务。

**内存缓存**（内存 SQLite `sqlite://`）：
```sql
CREATE TABLE job_definitions_cache (
    job_definition_id VARCHAR(36) PRIMARY KEY,
    next_run_time BIGINT,
    active BOOLEAN,
    timezone VARCHAR(36),
    schedule VARCHAR(256)
)
```

缓存用于快速校验队列中任务的有效性（任务可能已被删除/更新/暂停）。

## 启动流程

`TaskRunner.start()` 在 SchedulerApp 初始化时被异步启动：

```python
async def start(self):
    self.populate_cache()
    while True:
        self.process_queue()
        await asyncio.sleep(self.poll_interval)
```

默认轮询间隔为 10 秒（可配置 `poll_interval`）。

### populate_cache()

1. 从数据库查询所有带 `schedule`（cron表达式）的 JobDefinition
2. 使用 croniter 计算每个作业的 `next_run_time`
3. 将记录写入内存缓存
4. active=True 的作业推入优先队列

## 调度逻辑 process_queue()

```python
def process_queue(self):
    while not self._queue.empty():
        task = self._queue.peek()
        cache_entry = self._cache.get(task.job_definition_id)
        
        # 有效性校验：任务已删除
        if not cache_entry:
            self._queue.pop()
            continue
        
        # 有效性校验：任务已暂停或时间已更新（队列中的是过期条目）
        if not cache_entry.active or task.next_run_time != cache_entry.next_run_time:
            self._queue.pop()
            continue
        
        # 时间未到，退出循环
        now = get_utc_timestamp() * 1000  # 毫秒
        time_diff = now - task.next_run_time
        if time_diff < 0:
            break
        
        # 执行作业
        try:
            self.scheduler.create_job_from_definition(task.job_definition_id)
        except Exception:
            self.log.exception("Error creating job from definition")
        
        # 弹出当前任务，计算下次执行时间，推入新任务
        self._queue.pop()
        next_time = compute_next_run_time(cache_entry.schedule, cache_entry.timezone)
        self._cache.update(task.job_definition_id, next_run_time=next_time)
        self._queue.push(JobDefinitionTask(task.job_definition_id, next_time))
```

### 关键设计：过期任务的惰性清理

队列中的任务可能已经过期（作业被更新/删除/暂停），但堆结构不支持高效的随机删除。TaskRunner 采用**惰性清理**策略：

1. 在 process_queue 每次 peek 时，通过缓存校验任务有效性
2. 无效任务直接 pop 跳过，不执行
3. 新任务（更新后）通过 push 入队

这避免了在 update/delete 时需要搜索堆中元素的 O(n) 开销。

## 时间计算

### compute_next_run_time(schedule, timezone)

使用 `croniter` 库计算下次执行时间：

```python
def compute_next_run_time(schedule: str, timezone: str = None) -> int:
    base = datetime.datetime.now(tz=pytz.timezone(timezone)) if timezone else datetime.datetime.utcnow()
    cron = croniter(schedule, base)
    next_time = cron.get_next(datetime.datetime)
    
    if timezone:
        next_time = next_time.astimezone(pytz.utc)
    
    return int(next_time.timestamp() * 1000)  # 毫秒时间戳
```

- 有 timezone 时，使用 pytz 时区的本地时间作为基准计算
- 无 timezone 时，使用 UTC 时间
- 返回毫秒级 Unix 时间戳

## CRUD 操作

### add_job_definition(job_definition_id)

创建新的定时作业定义时调用：
1. 从数据库查询 JobDefinition
2. 计算 next_run_time
3. 写入缓存
4. active 时推入队列

### update_job_definition(job_definition_id, model)

更新作业定义时调用（包括暂停/恢复/schedule变更）：
1. 合并缓存中的旧值和新值
2. 重新计算 next_run_time
3. 更新缓存
4. 若时间变化或从暂停恢复，推入新任务（旧任务在 process_queue 时被惰性清理）

### delete_job_definition(job_definition_id)

删除作业定义时调用：
1. 从缓存删除记录
2. 不直接操作队列（旧任务在 process_queue 时发现缓存缺失，被惰性跳过）

### pause_jobs(job_definition_id)

暂停作业：
1. 更新缓存中 active=False
2. 不直接操作队列

### resume_jobs(job_definition_id)

恢复作业：
1. 更新缓存中 active=True
2. 计算新的 next_run_time
3. 推入新任务

## create_job_from_definition

定时任务触发时，TaskRunner 调用 `scheduler.create_job_from_definition(id)` 创建一次性作业实例：

1. 从 staging 目录读取输入文件（create_job_definition 时已复制到 staging）
2. 构造 CreateJob 参数（继承自 JobDefinition 的配置）
3. 调用 create_job() 创建并执行作业
4. 新作业的 job_definition_id 字段关联到原定义

## 多后端支持

TaskRunner 是 Scheduler 实例的属性，每个后端的 Scheduler 可以有自己的 TaskRunner。SchedulerApp 启动时遍历所有后端的 Scheduler，为有 task_runner 的启动轮询循环。

## 配置

| Trait | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| poll_interval | Integer | 10 | 轮询间隔（秒） |
| db_url | Unicode | "" | 数据库连接URL（继承自Scheduler） |
| scheduler | Instance | None | 关联的Scheduler实例 |

默认 TaskRunner 类在 BaseScheduler 中配置为 `jupyter_scheduler.task_runner.TaskRunner`，可通过 `scheduler.task_runner_class` 覆盖。
