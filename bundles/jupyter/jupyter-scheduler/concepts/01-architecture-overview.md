# 整体架构

Jupyter Scheduler 采用**分层插件架构**，从上到下分为四层：前端交互层、HTTP API层、调度核心层、执行层。后端注册体系贯穿所有层，实现可插拔扩展。

## 分层架构

```
┌─────────────────────────────────────────────────────────┐
│  前端交互层 (JupyterLab Extension)                       │
│  命令面板 / Notebook工具栏 / 文件浏览器菜单 / Jobs面板     │
│  SchedulerService (REST客户端)                           │
├─────────────────────────────────────────────────────────┤
│  HTTP API层 (Tornado Handlers)                          │
│  JobHandler / JobDefinitionHandler / BackendsHandler    │
│  JobHandlersMixin (后端路由/参数解析/异常处理)            │
├─────────────────────────────────────────────────────────┤
│  调度核心层 (Scheduler + TaskRunner)                     │
│  ┌─────────────────────────────────────────────────┐    │
│  │ BackendRegistry                                 │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │    │
│  │  │ Notebook │ │ Python   │ │ Custom   │ ...    │    │
│  │  │ Backend  │ │ Backend  │ │ Backend  │        │    │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘        │    │
│  │       Scheduler    Scheduler   Scheduler        │    │
│  │       (ORM+staging+process mgmt)                │    │
│  └─────────────────────┬───────────────────────────┘    │
│  TaskRunner (cron定时调度, 优先队列+内存缓存)            │
├─────────────────────────────────────────────────────────┤
│  执行层 (ExecutionManager)                              │
│  DefaultExecutionManager (nbconvert Notebook执行)       │
│  PythonScriptExecutionManager (subprocess脚本执行)      │
│  ArchivingExecutionManager (归档执行)                    │
│  自定义ExecutionManager (远程执行后端)                   │
├─────────────────────────────────────────────────────────┤
│  存储层                                                 │
│  SQLite/SQLAlchemy ORM (作业持久化)                      │
│  文件系统/fsspec (staging + 本地输出目录)                │
└─────────────────────────────────────────────────────────┘
```

## 关键设计模式

### 1. 插件注册模式（Entry Points + BaseBackend）

后端通过 Python entry_points 声明式注册，无需修改核心代码即可添加新的执行后端。每个后端通过 ClassVar 声明其能力（支持的文件类型、输出格式、关联的调度器/执行器类）。

参见：[后端注册体系](../references/backend-registry-source.md)

### 2. 命名空间路由模式（backend_id:uuid）

Job ID 使用 `backend_id:uuid` 复合格式，使得多后端共享同一套 HTTP API 成为可能。Handler 层解析 ID 前缀自动路由到正确的后端调度器。

参见：[Job ID 路由](04-job-routing.md)

### 3. 模板方法模式（ExecutionManager.process）

`process()` 方法定义执行骨架（before_start→execute→on_failure/on_complete），子类只需实现 `execute()` 方法。状态更新（IN_PROGRESS→COMPLETED/FAILED）在基类中统一处理。

参见：[执行管理器](06-execution-managers.md)

### 4. 两阶段文件管理（Staging → Download）

作业输出先写入 staging 暂存区（支持本地/远程存储），用户显式下载时复制到工作区。这避免了大文件在工作区中的冗余存储。

参见：[文件管理](10-file-management.md)

### 5. 多进程隔离模式（spawn 上下文）

每个作业在独立子进程中执行（multiprocessing spawn模式），隔离用户代码对服务器进程的影响。子进程通过数据库连接独立更新状态，不依赖父进程内存。

参见：[作业生命周期](05-scheduler-lifecycle.md)

## 请求处理流程

以创建作业为例：

```
1. 前端 POST /scheduler/jobs
2. JobHandler.post()
   a. resolve_backend_for_job(payload) → 选择后端
   b. 填充默认output_formats
   c. scheduler.create_job(CreateJob(**payload))
3. Scheduler.create_job()
   a. 验证input_uri和kernel
   b. 幂等性检查
   c. 生成job_id（backend_id:uuid）
   d. 创建Job ORM记录
   e. 复制输入文件到staging
   f. spawn子进程执行DefaultExecutionManager.process()
   g. 记录pid，返回job_id
4. 子进程执行：
   a. before_start() → 状态=IN_PROGRESS
   b. execute() → nbconvert执行notebook
   c. on_complete()/on_failure() → 更新状态
5. 前端轮询GET /scheduler/jobs/{job_id}获取状态
6. 用户触发下载 → FilesDownloadHandler → JobFilesManager复制文件到工作区
```

## 数据流

```
用户Notebook/脚本 (root_dir/)
       │ create_job
       ▼
Staging Area (scheduler_staging_area/{job_id}/)
       │ 子进程执行
       ├── 执行后的Notebook (.ipynb)
       ├── HTML导出 (.html)
       └── 副作用文件 (数据/图表等)
       │ download_files
       ▼
Local Output (root_dir/jobs/{name}-{job_id}/)
       │ 用户查看
       ▼
JupyterLab文件浏览器
```
