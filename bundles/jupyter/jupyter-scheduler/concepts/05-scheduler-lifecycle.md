# 作业生命周期管理

作业从创建到结束经历明确的状态流转。Scheduler 和 ExecutionManager 协同管理作业的完整生命周期。

## 作业状态

```python
class Status(Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
```

## 状态流转图

```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌───────────┐
│ CREATED │────→│ QUEUED  │────→│ IN_PROGRESS │────→│ COMPLETED │
└─────────┘     └─────────┘     └──────┬──────┘     └───────────┘
                                       │
                                       ├────────────→┌────────┐
                                       │             │ FAILED │
                                       │             └────────┘
                                       │
                                       └────→┌──────────┐    ┌─────────┐
                                             │ STOPPING │───→│ STOPPED │
                                             └──────────┘    └─────────┘
```

### 状态转换说明

| 转换 | 触发点 | 位置 |
|-----|-------|------|
| → CREATED | `create_job()` 创建ORM记录 | scheduler.py |
| CREATED → QUEUED | 定时作业等待下一次执行 | task_runner.py |
| CREATED/QUEUED → IN_PROGRESS | 子进程启动，`before_start()` | executors.py |
| IN_PROGRESS → COMPLETED | `execute()` 正常返回，`on_complete()` | executors.py |
| IN_PROGRESS → FAILED | `execute()` 抛异常，`on_failure()` | executors.py |
| IN_PROGRESS → STOPPING | 用户调用 `stop_job()` | scheduler.py |
| STOPPING → STOPPED | 进程被kill | scheduler.py |

## 创建流程（create_job）

`Scheduler.create_job()` 的完整执行步骤：

### 1. 输入验证

```python
if not job_definition_id:
    if not self.file_exists(job.input_uri) and not self.dir_exists(job.input_uri):
        raise InputUriError(f"Input URI {job.input_uri} not found")
```

### 2. Notebook 内核验证

对于 Notebook 后端，使用 execution_manager_class.validate() 检查 notebook 是否包含 kernelspec 元数据。

### 3. 幂等性检查

```python
if idempotency_token:
    existing = db.query(Job).filter_by(idempotency_token=token).first()
    if existing:
        raise IdempotencyTokenError("Job with same idempotency token already exists")
```

相同 idempotency_token 的重复创建返回 409 Conflict。

### 4. 生成 Job ID

```python
job_id = str(uuid4())
if self.backend_id:
    job_id = f"{self.backend_id}:{job_id}"
```

### 5. 创建数据库记录

创建 Job ORM 对象，初始 status 为 STOPPED（等子进程启动后改为 IN_PROGRESS），commit 到数据库。

### 6. 复制输入文件到 Staging

- **package_input_folder=False**（默认）：仅复制输入文件到 staging 目录
- **package_input_folder=True**：复制输入文件所在目录的所有内容到 staging 目录

Staging 路径格式：`{staging_path}/{job_id}/`

### 7. 启动子进程

```python
mp_ctx = mp.get_context("spawn")
p = mp_ctx.Process(
    target=execution_manager_class(
        job_id=job_id,
        root_dir=self.root_dir,
        db_url=self.db_url,
        staging_paths=staging_paths,
    ).process
)
p.start()
```

使用 **spawn** 上下文创建子进程（而非 fork），原因是 Python <3.12 中 fork 的 asyncio 事件循环存在已知 bug。

### 8. 记录进程ID

```python
db_job.pid = p.pid
session.commit()
```

### 9. 返回结果

返回 `{"job_id": job_id}`。

## 子进程执行流程

子进程运行 `ExecutionManager.process()` 模板方法：

```python
def process(self):
    self.before_start()        # 标记 IN_PROGRESS
    try:
        self.execute()         # 子类实现具体执行
    except Exception as e:
        self.on_failure(e)     # 标记 FAILED
    else:
        self.on_complete()     # 标记 COMPLETED
```

### before_start()

```python
job = self.db_job
job.status = Status.IN_PROGRESS
job.start_time = get_utc_timestamp()
self.db_session.commit()
```

子进程独立连接数据库，通过 job_id 查询和更新记录，不依赖父进程内存。

### execute()（DefaultExecutionManager）

1. 读取 staging 中的 notebook（nbformat）
2. 若有 parameters，注入参数 cell（tagged cell）
3. 创建 ExecutePreprocessor，设置 kernel_name 和 cwd
4. `ep.preprocess(nb, {"metadata": {"path": staging_dir}})` 执行 notebook
5. finally：
   - `add_side_effects_files()` 捕获副作用文件
   - `create_output_files()` 生成各格式输出

### on_complete()

```python
job.status = Status.COMPLETED
job.end_time = get_utc_timestamp()
self.db_session.commit()
```

### on_failure(e)

```python
job.status = Status.FAILED
job.status_message = str(e)
self.db_session.commit()
```

## 停止作业（stop_job）

用户发起 PATCH 请求将 status 设为 STOPPED：

1. 从数据库查询作业，验证状态不是 COMPLETED/STOPPED/FAILED
2. 获取 pid，使用 psutil 查找子进程树
3. 递归 kill 所有子进程（处理 Notebook kernel 等嵌套进程）
4. 更新数据库状态为 STOPPED，设置 end_time
5. commit

```python
import psutil
try:
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()
except psutil.NoSuchProcess:
    pass
```

使用 `recursive=True` 确保 kernel 进程及其子进程也被终止。

## 删除作业（delete_job）

1. 若作业正在运行（IN_PROGRESS/QUEUED），先调用 stop_job()
2. 删除 staging 目录
3. 删除数据库中的 Job 记录（ORM层可能级联删除关联记录）

## 作业列表查询

list_jobs 支持以下过滤和分页：

- **过滤**：status、job_definition_id、start_time范围、name前缀、tags包含
- **排序**：多字段排序，支持 asc/desc
- **分页**：max_items（默认1000）+ next_token（偏移量，基于已返回项数）

状态同步：QUEUED/IN_PROGRESS 状态的作业会通过对应后端的 get_job() 同步最新状态。
