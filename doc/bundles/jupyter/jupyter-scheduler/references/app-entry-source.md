---
source: jupyter_scheduler/extension.py
title: SchedulerApp 扩展应用源码解析
---

# SchedulerApp 扩展应用源码解析

> 信源路径：`jupyter_scheduler/extension.py`（193行）

## 类定义

`SchedulerApp` 继承自 `jupyter_server.extension.application.ExtensionApp`，是 Jupyter Scheduler 的服务器扩展入口点。

```python
class SchedulerApp(ExtensionApp):
    name = "jupyter_scheduler"
```

## HTTP 路由表

SchedulerApp 注册 11 个 REST API 端点：

| 路由模式 | Handler | 用途 |
|---------|---------|------|
| `scheduler/backends` | BackendsHandler | 列出可用后端 |
| `scheduler/jobs` | JobHandler | 创建/列出作业 |
| `scheduler/jobs/count` | JobsCountHandler | 统计作业数 |
| `scheduler/jobs/{job_id}` | JobHandler | 查询/更新/删除单个作业 |
| `scheduler/jobs/{job_id}/download_files` | FilesDownloadHandler | 下载作业文件 |
| `scheduler/batch/jobs` | BatchJobHandler | 批量删除作业 |
| `scheduler/job_definitions` | JobDefinitionHandler | 创建/列出作业定义 |
| `scheduler/job_definitions/{id}` | JobDefinitionHandler | 查询/更新/删除作业定义 |
| `scheduler/job_definitions/{id}/jobs` | JobFromDefinitionHandler | 从定义创建作业 |
| `scheduler/runtime_environments` | RuntimeEnvironmentsHandler | 列出运行时环境 |
| `scheduler/config` | ConfigHandler | 返回配置和功能支持 |

- Job ID 正则：`r"(?P<job_id>[\w:%-]+)"`，支持 `backend_id:uuid` 格式
- JobDefinition ID 正则：`r"(?P<job_definition_id>\w+(?:-\w+)+)"`，匹配 UUID 格式

## 配置项（Traitlets）

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `drop_tables` | Bool | False | 启动时删除数据库表重建 |
| `db_url` | Unicode | `sqlite:///{jupyter_data_dir()}/scheduler.sqlite` | 数据库连接URI |
| `legacy_job_backend` | Unicode | None | 路由legacy作业（纯UUID）的后端ID |
| `backend_config` | Dict | {} | 每后端配置覆盖（db_url, metadata） |
| `preferred_backends` | Dict | {} | 文件扩展名到后端ID的默认选择映射 |
| `environment_manager_class` | Type | CondaEnvironmentManager | 环境管理器类 |
| `scheduler_class` | Type | Scheduler | 默认Notebook后端的调度器类 |
| `job_files_manager_class` | Type | JobFilesManager | 文件下载管理器类 |

## 初始化流程 initialize_settings()

```
1. super().initialize_settings()
2. discover_backends() → 发现所有已注册后端（entry_points）
   - 若无后端，抛出 ValueError
3. _build_backend_configs() → 为每个后端构建 BackendConfig
   - 对默认Notebook后端特殊处理 scheduler_class 覆盖
4. get_legacy_job_backend_id() → 确定legacy后端
5. 创建 EnvironmentManager 实例
6. 创建 BackendRegistry 并 initialize()
   - 为每个后端动态import scheduler_class
   - 创建数据库表（若使用默认SQLAlchemy存储）
   - 实例化scheduler
   - 建立扩展名→后端映射
7. 创建 JobFilesManager
8. self.settings.update() 注入：environments_manager, scheduler, backend_registry, job_files_manager
9. 启动各后端的 task_runner（asyncio.create_task）
10. 日志输出初始化的后端列表
```

## _build_backend_configs 方法

该方法遍历发现的后端类，为每个后端创建 BackendConfig 对象：
- 从 `backend_config` trait 读取 per-backend 覆盖
- 对 `jupyter_server_nb` 后端，若用户自定义了 `scheduler_class`，使用自定义类路径
- 支持通过字符串类路径或类对象两种方式配置 scheduler_class

## 关键设计决策

1. **向后兼容**：settings 中同时注入 `scheduler`（指向legacy后端）和 `backend_registry`，旧代码通过 `self.settings["scheduler"]` 仍可工作
2. **多后端并行**：所有后端共享同一个 Jupyter server 进程，但各自有独立的 scheduler 实例和可选的独立数据库
3. **延迟启动**：task_runner 通过 `loop.create_task()` 异步启动，不阻塞服务器初始化
