# Jupyter Scheduler 概述

Jupyter Scheduler 是一个 JupyterLab 扩展，为 Jupyter 环境提供作业（Job）调度和执行能力。它允许用户在 JupyterLab 中将 Notebook 或 Python 脚本作为后台作业执行，支持立即执行和定时调度（cron表达式）。

## 核心功能

1. **Notebook 后台执行**：将 Notebook 作为后台作业运行，不阻塞 JupyterLab 界面
2. **Python 脚本执行**：支持直接执行 `.py` 脚本文件
3. **定时调度**：基于 cron 表达式创建定时作业，支持时区配置
4. **参数化执行**：向 Notebook 注入参数，实现同一份代码的不同参数运行
5. **多格式输出**：Notebook 作业支持 ipynb、html 等多种输出格式
6. **文件下载**：作业完成后下载输出文件到工作区
7. **多后端支持**：可插拔后端架构，支持自定义执行后端（如远程集群、云服务）

## 架构总览

Jupyter Scheduler 采用前后端分离架构，后端是 Jupyter Server 扩展，前端是 JupyterLab 扩展：

```
┌─────────────────────────────────────────────────────┐
│                   JupyterLab 前端                     │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ 命令面板  │  │ Notebook面板 │  │  文件浏览器    │  │
│  └────┬─────┘  └──────┬───────┘  └──────┬────────┘  │
│       │               │                 │            │
│  ┌────┴───────────────┴─────────────────┴────────┐   │
│  │         SchedulerService (handler.ts)          │   │
│  └────────────────────┬──────────────────────────┘   │
└───────────────────────┼─────────────────────────────┘
                        │ REST API (/scheduler/*)
┌───────────────────────┼─────────────────────────────┐
│              Jupyter Server 后端                      │
│  ┌────────────────────┴──────────────────────────┐   │
│  │            SchedulerApp (extension.py)         │   │
│  │  ┌─────────────┐  ┌────────────────────────┐  │   │
│  │  │  Handlers   │→ │    BackendRegistry     │  │   │
│  │  └─────────────┘  │  ┌──────────────────┐  │  │   │
│  │                   │  │ BackendInstance  │  │  │   │
│  │                   │  │  ┌────────────┐  │  │  │   │
│  │                   │  │  │ Scheduler  │  │  │  │   │
│  │                   │  │  │  ┌───────┐ │  │  │  │   │
│  │                   │  │  │  │Executor│ │  │  │  │   │
│  │                   │  │  │  └───────┘ │  │  │  │   │
│  │                   │  │  │  ┌───────┐ │  │  │  │   │
│  │                   │  │  │  │TaskRun│ │  │  │  │   │
│  │                   │  │  └──┴───────┘  │  │  │   │
│  │                   │  └──────────────────┘  │  │   │
│  │                   └────────────────────────┘  │   │
│  └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 核心组件

| 组件 | 职责 | 源码 |
|-----|------|------|
| SchedulerApp | Jupyter Server 扩展入口，注册路由和初始化 | [extension.py](../../references/app-entry-source.md) |
| BackendRegistry | 后端注册中心，管理多后端路由 | [backend_registry.py](../../references/backend-registry-source.md) |
| BaseBackend | 后端基类，声明后端能力 | [base_backend.py](../../references/backend-registry-source.md) |
| BaseScheduler/Scheduler | 作业调度核心，CRUD+执行调度 | [scheduler.py](../../references/scheduler-source.md) |
| ExecutionManager | 执行管理器，模板方法定义执行生命周期 | [executors.py](../../references/executor-source.md) |
| TaskRunner | 定时任务运行器，优先队列+cron调度 | [task_runner.py](../../references/task-runner-source.md) |
| Handlers | REST API 请求处理 | [handlers.py](../../references/handlers-source.md) |
| ORM | SQLAlchemy 数据持久化 | [orm.py](../../references/orm-source.md) |
| Models | Pydantic 数据模型 | [models.py](../../references/models-source.md) |
| JobFilesManager | 输出文件下载管理 | `job_files_manager.py` |

## 作业生命周期

```
CREATED → QUEUED → IN_PROGRESS → COMPLETED
                  ↓              ↘ FAILED
               STOPPING → STOPPED
```

1. **CREATED**：作业记录已创建，输入文件已复制到staging
2. **QUEUED**：定时作业等待执行时机
3. **IN_PROGRESS**：子进程正在执行
4. **COMPLETED**：执行成功，输出文件已生成
5. **FAILED**：执行失败，记录错误信息
6. **STOPPING→STOPPED**：用户手动停止作业

## 版本信息

- 当前版本：2.11.0
- 支持 JupyterLab 4.x
- 支持 Python 3.9-3.13
- 从 v3.0 起引入多后端架构，Job ID 格式从纯 UUID 改为 `backend_id:uuid`
