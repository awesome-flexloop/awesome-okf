# Jupyter Scheduler 源码信源索引

> 信源登记：所有概念文档引用的源码解析文档。

| 信源文档 | 源码路径 | 行数 | 说明 |
|---------|---------|------|------|
| [app-entry-source.md](app-entry-source.md) | `jupyter_scheduler/extension.py` | 193 | SchedulerApp扩展应用、路由注册、初始化流程 |
| [scheduler-source.md](scheduler-source.md) | `jupyter_scheduler/scheduler.py` | 934 | BaseScheduler/Scheduler/ArchivingScheduler调度器实现 |
| [handlers-source.md](handlers-source.md) | `jupyter_scheduler/handlers.py` | 531 | REST API Handler体系与请求处理 |
| [executor-source.md](executor-source.md) | `jupyter_scheduler/executors.py` | 265 | ExecutionManager执行管理器与Notebook执行 |
| [task-runner-source.md](task-runner-source.md) | `jupyter_scheduler/task_runner.py` | 344 | TaskRunner定时调度、优先队列与缓存 |
| [models-source.md](models-source.md) | `jupyter_scheduler/models.py` | 314 | Pydantic数据模型定义 |
| [orm-source.md](orm-source.md) | `jupyter_scheduler/orm.py` | 165 | SQLAlchemy ORM、表结构与自动迁移 |
| [backend-registry-source.md](backend-registry-source.md) | `backend_registry.py`/`backends.py`/`base_backend.py`/`backend_utils.py` | 434 | 后端注册体系、BackendRegistry、entry_points发现 |

## 其他源码文件

以下文件在概念文档中引用但未单独做信源解析：

| 文件 | 说明 |
|-----|------|
| `jupyter_scheduler/environments.py` | 环境管理器（CondaEnvironmentManager/StaticEnvironmentManager） |
| `jupyter_scheduler/job_files_manager.py` | 作业文件下载管理器（JobFilesManager/Downloader） |
| `jupyter_scheduler/python_executor.py` | Python脚本执行管理器 |
| `jupyter_scheduler/parameterize.py` | Notebook参数注入 |
| `jupyter_scheduler/job_id.py` | Job ID生成/解析/路由 |
| `jupyter_scheduler/utils.py` | 工具函数（时间戳/文件名/目录复制/cron计算） |
| `jupyter_scheduler/exceptions.py` | 异常类定义 |
| `src/index.tsx` | 前端插件入口（命令/菜单/面板） |
| `src/tokens.ts` | 前端Token定义（IAdvancedOptions/TelemetryHandler） |
| `src/handler.ts` | 前端SchedulerService API客户端 |
| `src/model.ts` | 前端数据模型 |

```{toctree}
:maxdepth: 7

app-entry-source
backend-registry-source
executor-source
handlers-source
models-source
orm-source
scheduler-source
task-runner-source
```
