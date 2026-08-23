# SchedulerApp 扩展应用与启动流程

SchedulerApp 是 Jupyter Scheduler 的 Jupyter Server 扩展入口，负责注册 HTTP 路由、发现和初始化后端、注入服务到 settings。

## 扩展注册

SchedulerApp 继承自 `jupyter_server.extension.application.ExtensionApp`，扩展名为 `"jupyter_scheduler"`。

Jupyter Server 启动时自动发现已安装的扩展，调用 `initialize_settings()` 方法初始化。安装时通过 `jupyter-config/server-config/` 和 `jupyter-config/nb-config/` 目录下的JSON配置文件自动注册扩展。

## HTTP 路由

SchedulerApp 注册以下 REST API 端点（路径前缀为 `/scheduler/`）：

| 方法 | 路径 | 用途 |
|-----|------|------|
| GET/POST | `/backends` | 列出可用后端 |
| GET/POST | `/jobs` | 列出/创建作业 |
| GET | `/jobs/count` | 统计作业数 |
| GET/PATCH/DELETE | `/jobs/{job_id}` | 查询/更新/删除作业 |
| GET | `/jobs/{job_id}/download_files` | 下载作业文件 |
| DELETE | `/batch/jobs` | 批量删除作业 |
| GET/POST | `/job_definitions` | 列出/创建作业定义 |
| GET/PATCH/DELETE | `/job_definitions/{id}` | 查询/更新/删除作业定义 |
| POST | `/job_definitions/{id}/jobs` | 从定义创建作业 |
| GET | `/runtime_environments` | 列出运行时环境 |
| GET | `/config` | 获取配置信息 |

## 配置项

通过 Jupyter 配置系统（命令行参数或配置文件）可配置以下选项：

```python
# jupyter_server_config.py
c.SchedulerApp.db_url = "sqlite:///path/to/scheduler.sqlite"
c.SchedulerApp.drop_tables = False  # 启动时重建表（开发用）
c.SchedulerApp.legacy_job_backend = "jupyter_server_nb"
c.SchedulerApp.scheduler_class = "jupyter_scheduler.scheduler.Scheduler"
c.SchedulerApp.environment_manager_class = "jupyter_scheduler.environments.CondaEnvironmentManager"
c.SchedulerApp.job_files_manager_class = "jupyter_scheduler.job_files_manager.JobFilesManager"

# 每后端配置覆盖
c.SchedulerApp.backend_config = {
    "my_backend": {
        "db_url": "postgresql://user:pass@host/db",
        "metadata": {"key": "value"}
    }
}

# 文件扩展名首选后端
c.SchedulerApp.preferred_backends = {
    "ipynb": "jupyter_server_nb",
    "py": "jupyter_server_py"
}
```

## 启动流程

`initialize_settings()` 的执行顺序：

### 1. 发现后端

```python
backend_classes = discover_backends(log=self.log)
```

通过 `importlib.metadata.entry_points()` 扫描 `jupyter_scheduler.backends` 入口组，加载所有注册的后端类。内置两个后端：
- `jupyter_server_nb`：Notebook 执行后端
- `jupyter_server_py`：Python 脚本执行后端

第三方包可通过在 pyproject.toml 中注册 entry points 添加后端：

```toml
[project.entry-points."jupyter_scheduler.backends"]
my_backend = "my_package.backends:MyBackend"
```

### 2. 构建后端配置

```python
backend_configs = self._build_backend_configs(backend_classes)
```

为每个后端类创建 BackendConfig 对象，应用 `backend_config` 中的 per-backend 覆盖。

### 3. 确定 Legacy 后端

```python
default_id = get_legacy_job_backend_id(backend_classes, legacy_job_backend=self.legacy_job_backend)
```

Legacy 后端用于路由 v3.0 之前创建的纯UUID格式作业ID。优先级：配置值 > `jupyter_server_nb`。

### 4. 初始化组件

```python
environments_manager = self.environment_manager_class()
registry = BackendRegistry(backend_configs, default_id, self.preferred_backends)
registry.initialize(root_dir=self.serverapp.root_dir, environments_manager=..., db_url=..., config=...)
scheduler = legacy_backend.scheduler
job_files_manager = self.job_files_manager_class(backend_registry=registry)
```

BackendRegistry.initialize() 为每个后端：
1. 动态 import scheduler_class
2. 创建数据库表（若使用默认SQLAlchemy存储）
3. 实例化 Scheduler
4. 动态设置 execution_manager_class
5. 建立文件扩展名到后端的映射

### 5. 注入 Settings

```python
self.settings.update({
    "environments_manager": environments_manager,
    "scheduler": scheduler,  # 向后兼容，指向legacy后端
    "backend_registry": registry,
    "job_files_manager": job_files_manager,
})
```

`scheduler` 键保留以向后兼容旧版 handler 代码。新代码应使用 `backend_registry` 进行多后端路由。

### 6. 启动 TaskRunner

```python
loop = asyncio.get_event_loop()
for backend in registry.backends:
    if hasattr(backend.scheduler, "task_runner") and backend.scheduler.task_runner:
        loop.create_task(backend.scheduler.task_runner.start())
```

对有 task_runner 的后端（默认为所有 Scheduler 实例），异步启动定时任务轮询。

### 7. 启动日志

```
Initialized 2 backend(s): ['jupyter_server_nb', 'jupyter_server_py'] (legacy_job_backend: jupyter_server_nb)
```
