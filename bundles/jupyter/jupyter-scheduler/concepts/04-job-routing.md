# Job ID 命名空间路由

Jupyter Scheduler v3.0 引入了多后端架构，Job ID 格式从纯 UUID 改为 `backend_id:uuid` 的复合格式，实现**命名空间路由**——同一个 HTTP API 端点可以服务多个后端，Handler 层自动将请求路由到正确的后端调度器。

## Job ID 格式

### 新式 ID（多后端）

```
{backend_id}:{uuid}
```

示例：
- `jupyter_server_nb:550e8400-e29b-41d4-a716-446655440000`
- `my_custom_backend:550e8400-e29b-41d4-a716-446655440000`

### Legacy ID（单后端兼容）

```
{uuid}
```

v3.0 之前创建的作业使用纯 UUID 格式（无冒号），这些作业通过 legacy 后端路由。

## ID 生成

在 `Scheduler.create_job()` 中生成：

```python
job_id = str(uuid4())
if self.backend_id:
    job_id = f"{self.backend_id}:{job_id}"
```

- backend_id 非空时：`backend_id:uuid`
- backend_id 为空（legacy）：纯 uuid

## ID 解析与路由

`resolve_scheduler(job_id, backend_registry)` 函数在 `job_id.py` 中实现路由逻辑：

```python
def resolve_scheduler(job_id, registry):
    if ":" not in job_id:
        # Legacy ID → legacy后端
        return registry.get_legacy_job_backend().scheduler
    
    backend_id, _ = job_id.split(":", 1)
    backend = registry.get_backend(backend_id)
    if backend:
        return backend.scheduler
    
    raise ValueError(f"Backend {backend_id} not found")
```

路由规则：
1. ID 中无冒号 → legacy 后端（`jupyter_server_nb` 默认）
2. ID 中有冒号 → 按冒号前的 backend_id 查找后端
3. 后端不存在 → 抛 ValueError，Handler 层转为 400 错误

## Handler 层的路由使用

所有带 `{job_id}` 路径参数的 Handler 方法都通过 `JobHandlersMixin.get_scheduler(job_id)` 获取调度器：

```python
class JobHandler(APIHandler):
    def get(self, job_id=None):
        if job_id:
            scheduler = self.get_scheduler(job_id)
            job = scheduler.get_job(job_id)
            ...
```

这使得 GET/PATCH/DELETE `/scheduler/jobs/{job_id}` 等操作天然支持多后端。

## 作业列表的混合处理

GET `/scheduler/jobs` 列出作业时需要处理多后端混合场景：

1. 从 legacy 后端查询所有作业（共享数据库，legacy scheduler 可访问所有作业）
2. 对 legacy 作业（无 backend_id），补填 backend_id
3. 对 QUEUED/IN_PROGRESS 状态的作业，通过对应后端的 `get_job()` 同步最新状态（支持远程后端的状态同步）
4. 同步失败仅记录 warning，不阻断响应

## 创建作业时的后端选择

创建作业时（POST `/scheduler/jobs`），后端选择优先级：

1. 请求体中显式指定 `backend_id` → 使用该后端（不存在则404）
2. 未指定 → 按 input_uri 的文件扩展名自动选择后端：
   - 查找支持该扩展名的所有后端
   - 使用 `preferred_backends` 配置中的首选后端
   - 无首选配置时按名称字母序选第一个
3. 无后端支持该扩展名 → 400错误

```python
# resolve_backend_for_job 逻辑
backend_id = payload.backend_id
if backend_id:
    backend = registry.get_backend(backend_id)
    if not backend:
        raise HTTPError(404, f"Backend {backend_id} not found")
else:
    ext = Path(payload.input_uri).suffix.lstrip(".")
    backend = registry.get_for_file(payload.input_uri)
    if not backend:
        raise HTTPError(400, f"No backend supports .{ext} files")
```

## 设计约束

- **backend_id 不能包含冒号**：BaseBackend 定义和 BackendRegistry 初始化时均验证此约束，避免 ID 解析歧义
- **split 时只分一次**：`job_id.split(":", 1)` 确保即使 uuid 部分包含冒号也不会误解析
- **Legacy 后端可配置**：通过 `SchedulerApp.legacy_job_backend` 配置项指定，默认为 `jupyter_server_nb`
- **作业定义同样遵循**：Job Definition ID 不使用命名空间格式（因为定义是后端特定的），但作业创建时会将 backend_id 注入生成的 Job ID
