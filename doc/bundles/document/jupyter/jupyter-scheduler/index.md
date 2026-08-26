# Jupyter Scheduler Wiki

> JupyterLab 作业调度扩展源码学习 Wiki
> 版本：v2.11.0 | OKF v0.2 | 生成日期：2026-04-21

Jupyter Scheduler 是 JupyterLab 的官方作业调度扩展，支持 Notebook 和 Python 脚本的后台执行与定时调度，采用可插拔后端架构。

## 快速开始

| 想做什么 | 去哪里看 |
|---------|---------|
| 了解Jupyter Scheduler是什么 | [概述](concepts/00-introduction.md) |
| 理解整体架构设计 | [架构总览](concepts/01-architecture-overview.md) |
| 创建第一个作业 | [创建第一个Notebook作业](examples/01-create-first-job.md) |
| 设置定时执行 | [创建定时调度作业](examples/02-schedule-recurring-job.md) |
| 执行Python脚本 | [执行Python脚本作业](examples/05-execute-python-script.md) |

## 概念文档（Concepts）

理解架构和核心机制：

| 序号 | 文档 | 说明 |
|-----|------|------|
| 00 | [概述](concepts/00-introduction.md) | 功能介绍、架构总览、作业生命周期 |
| 01 | [整体架构](concepts/01-architecture-overview.md) | 分层架构、设计模式、请求处理流程 |
| 02 | [SchedulerApp扩展应用](concepts/02-extension-app.md) | 扩展注册、启动流程、配置项 |
| 03 | [后端注册体系](concepts/03-backend-system.md) | BaseBackend、BackendRegistry、entry points发现 |
| 04 | [Job ID命名空间路由](concepts/04-job-routing.md) | backend_id:uuid格式、多后端路由、legacy兼容 |
| 05 | [作业生命周期管理](concepts/05-scheduler-lifecycle.md) | 创建→执行→完成/失败/停止全流程、spawn子进程 |
| 06 | [执行管理器](concepts/06-execution-managers.md) | 模板方法模式、Notebook/脚本执行、参数注入 |
| 07 | [TaskRunner定时调度](concepts/07-task-runner.md) | 优先队列、cron调度、惰性过期清理 |
| 08 | [数据模型](concepts/08-data-models.md) | Pydantic API模型、SQLAlchemy ORM、兼容层 |
| 09 | [数据库与自动迁移](concepts/09-database-migration.md) | SQLite持久化、ALTER TABLE迁移、内存缓存 |
| 10 | [文件管理与输出处理](concepts/10-file-management.md) | 两阶段文件管理、staging、fsspec、路径安全 |
| 11 | [REST API接口](concepts/11-rest-api.md) | 端点一览、请求/响应格式、错误码 |
| 12 | [自定义后端开发](concepts/12-custom-backend.md) | 开发步骤、BaseBackend/Scheduler/Executor定制 |

## 示例文档（Examples）

从实践中学习：

| 序号 | 文档 | 说明 |
|-----|------|------|
| 01 | [创建第一个Notebook作业](examples/01-create-first-job.md) | REST API/UI创建作业、查看状态、下载输出 |
| 02 | [创建定时调度作业](examples/02-schedule-recurring-job.md) | cron表达式、暂停/恢复、手动触发、参数 |
| 03 | [参数化Notebook执行](examples/03-parameterized-notebook.md) | parameters tag、参数注入、批量执行、幂等令牌 |
| 04 | [管理和监控作业](examples/04-manage-and-monitor-jobs.md) | 过滤/排序/分页、状态轮询、停止/删除/批量清理 |
| 05 | [执行Python脚本作业](examples/05-execute-python-script.md) | .py文件执行、环境变量传参、打包输入文件夹 |

## 源码信源（References）

基于源码的逐模块解析，作为概念文档的信源支撑：

| 信源文档 | 源码文件 | 行数 |
|---------|---------|------|
| [SchedulerApp扩展应用](references/app-entry-source.md) | `extension.py` | 193 |
| [Scheduler调度器](references/scheduler-source.md) | `scheduler.py` | 934 |
| [HTTP Handlers](references/handlers-source.md) | `handlers.py` | 531 |
| [ExecutionManager执行管理器](references/executor-source.md) | `executors.py` | 265 |
| [TaskRunner定时调度](references/task-runner-source.md) | `task_runner.py` | 344 |
| [数据模型](references/models-source.md) | `models.py` | 314 |
| [ORM数据库层](references/orm-source.md) | `orm.py` | 165 |
| [后端注册体系](references/backend-registry-source.md) | `backend_registry.py`等4个文件 | 434 |
| [信源索引](references/index.md) | 全部源码文件 | - |

## 架构核心洞察

1. **后端插件化**：通过Python entry points声明式注册后端，零修改核心代码即可扩展执行环境
2. **命名空间路由**：`backend_id:uuid`格式的Job ID实现多后端共享API，Handler层自动路由
3. **多进程隔离**：spawn模式子进程执行用户代码，独立数据库连接更新状态，隔离故障
4. **模板方法执行**：ExecutionManager.process()定义标准生命周期钩子，子类只需实现execute()
5. **两阶段文件管理**：staging暂存+显式下载，避免大文件冗余，fsspec支持远程存储
6. **轻量自动迁移**：ORM层内置ALTER TABLE ADD COLUMN迁移，新列nullable兼容SQLite限制
7. **优先队列+cron**：TaskRunner最小堆+croniter，惰性过期清理避免堆修改开销
8. **路径安全防护**：所有文件路径操作验证root_dir边界，防路径遍历攻击
9. **前端Token注入**：Lumino Token机制支持UI组件可扩展（高级选项面板、遥测等）
10. **pydantic兼容层**：v1/v2自动检测兼容，平滑版本过渡

## 知识地图

```
入门
 ├─ 概述 (00)
 └─ 创建第一个作业 (ex01)

核心概念
 ├─ 整体架构 (01)
 ├─ 扩展应用与启动 (02)
 ├─ 后端注册体系 (03)
 ├─ Job ID路由 (04)
 ├─ 作业生命周期 (05)
 ├─ 执行管理器 (06)
 ├─ 定时调度 (07)
 ├─ 数据模型 (08)
 ├─ 数据库迁移 (09)
 ├─ 文件管理 (10)
 └─ REST API (11)

实践指南
 ├─ 定时作业 (ex02)
 ├─ 参数化执行 (ex03)
 ├─ 管理监控 (ex04)
 └─ Python脚本 (ex05)

扩展开发
 └─ 自定义后端 (12)

源码信源
 └─ references/ (9份源码解析)
```

```{toctree}
:hidden:
:maxdepth: 7

references/index
concepts/00-introduction
concepts/01-architecture-overview
concepts/02-extension-app
concepts/03-backend-system
concepts/04-job-routing
concepts/05-scheduler-lifecycle
concepts/06-execution-managers
concepts/07-task-runner
concepts/08-data-models
concepts/09-database-migration
concepts/10-file-management
concepts/11-rest-api
concepts/12-custom-backend
examples/01-create-first-job
examples/02-schedule-recurring-job
examples/03-parameterized-notebook
examples/04-manage-and-monitor-jobs
examples/05-execute-python-script
facts
insights
log
```
