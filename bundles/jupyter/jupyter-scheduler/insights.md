# Jupyter Scheduler 架构洞察

> I阶段产出：核心洞察四元组（概念→问题→方案→证据）+ 知识地图 + 文档结构规划

## 核心洞察四元组

### I-01: 后端插件化架构（Backend Plugin Architecture）

**概念**：基于 entry_points 的可插拔后端注册机制

**问题**：Notebook 执行和 Python 脚本执行有完全不同的执行模型（nbconvert vs subprocess），未来还需支持远程执行后端（如 AWS Braket、Kubernetes 等），如何在不修改核心代码的情况下扩展执行后端？

**方案**：
1. 通过 `jupyter_scheduler.backends` entry point group 声明式注册后端类
2. `BaseBackend` 使用 ClassVar 定义后端能力声明（id、name、支持的文件扩展名、输出格式、scheduler_class、execution_manager_class）
3. `BackendRegistry` 在启动时自动发现并初始化所有后端，建立扩展名→后端的路由映射
4. Job ID 使用 `backend_id:uuid` 命名空间格式，任何操作都能通过 ID 路由到正确后端
5. 每个后端可独立配置数据库连接（db_url 覆盖）、自定义调度器和执行管理器

**证据**：F-005、F-034~F-053

### I-02: Job ID 命名空间路由（Namespaced Job Routing）

**概念**：`backend_id:uuid` 格式的复合作业标识符实现多后端统一路由

**问题**：多后端场景下，HTTP API 需要知道每个作业属于哪个后端才能正确路由，但前端不应需要感知后端路由逻辑；同时需要兼容 v3.0 之前纯 UUID 的 legacy 作业。

**方案**：
1. 新作业 ID 格式为 `{backend_id}:{uuid}`，冒号作为分隔符
2. `parse_job_id()` 解析 ID 为 (backend_id, uuid) 元组，无冒号时 backend_id=None 表示 legacy
3. `resolve_scheduler()` 根据 ID 路由：legacy 走 legacy_job_backend，新式 ID 查找对应后端
4. Handler 层的 `get_scheduler(job_id)` 和 `resolve_backend_for_job(payload)` 封装路由逻辑
5. 后端 ID 禁止包含冒号（F-053），保证分隔符唯一性
6. 列表查询统一从 legacy 后端（共享数据库）获取，但对运行中的作业通过各自后端同步状态

**证据**：F-016、F-023、F-029、F-053、F-118~F-120、F-127、F-183~F-184

### I-03: 多进程执行隔离（Multi-process Execution Isolation）

**概念**：使用 `multiprocessing.get_context("spawn")` 创建独立子进程执行作业

**问题**：nbconvert 执行 notebook 会在当前进程运行任意用户代码，可能导致内存泄漏、事件循环污染、GIL 竞争，甚至崩溃服务器进程。Python <3.12 中 fork 模式的 asyncio 事件循环存在已知 bug。

**方案**：
1. `Scheduler.create_job()` 使用 `mp.get_context("spawn")` 创建全新子进程（非 fork）
2. 子进程入口为 `ExecutionManager.process()` 模板方法
3. 父进程记录子进程 PID 到数据库，用于 stop_job 时通过 psutil 查找并 kill
4. 子进程通过 db_url 独立连接数据库更新状态，不依赖父进程内存
5. spawn 模式确保子进程有干净的 Python 解释器状态，避免 fork 带来的 asyncio/锁状态问题

**证据**：F-067~F-069、F-077、F-014

### I-04: 模板方法执行生命周期（Template Method Execution Lifecycle）

**概念**：ExecutionManager.process() 定义固定执行骨架，子类填充具体执行逻辑

**问题**：不同执行后端（Notebook、Python脚本、远程执行）有不同的执行逻辑，但状态管理（开始→执行→成功/失败→状态更新）是通用的。如何避免重复代码同时保证状态一致性？

**方案**：
1. `process()` 是 final 模板方法：before_start() → execute() → on_failure(e)/on_complete()
2. before_start() 更新状态为 IN_PROGRESS + start_time
3. on_failure(e) 更新状态为 FAILED + status_message
4. on_complete() 更新状态为 COMPLETED + end_time
5. 子类只需实现 execute() 抽象方法和 supported_features() 类方法
6. DefaultExecutionManager 和 PythonScriptExecutionManager 分别实现 Notebook 和 Python 脚本的执行逻辑

**证据**：F-138~F-157

### I-05: Staging Area 两阶段文件管理（Two-Phase File Management）

**概念**：staging 区域（执行输出）→ 本地输出目录（下载）的两阶段文件生命周期

**问题**：作业在服务器后台异步执行，输出文件可能很大（支持远程存储 fsspec）；用户可能多次查看作业列表但不下载文件；执行中产生的副作用文件需要被捕获；归档模式需要打包所有文件。

**方案**：
1. **Staging 阶段**：作业执行时输出写入 staging_path（默认 jupyter_data_dir/scheduler_staging_area/{job_id}/），支持本地和远程文件系统（fsspec）
2. **本地输出阶段**：用户显式触发下载时，JobFilesManager 通过子进程将 staging 文件复制到 root_dir/jobs/{basefilename}-{job_id}/
3. get_job/list_jobs 只检查本地文件是否存在来设置 downloaded 标志和 job_files 列表
4. Downloader 支持三种模式：tar/tar.gz 归档解压、逐文件复制、附带副作用文件
5. 每个作业有独立目录，删除作业时清理 staging 和本地输出

**证据**：F-010~F-011、F-060~F-062、F-076、F-082、F-177~F-181

### I-06: 基于优先队列的定时调度（Priority Queue Cron Scheduling）

**概念**：heapq 优先队列 + 内存 SQLite 缓存实现轻量级 cron 调度

**问题**：需要根据 cron 表达式和时区定时创建作业实例，但不应引入重型调度器（如 Celery/Airflow）；需要支持作业定义的增删改和暂停/恢复；进程重启后需要恢复调度状态。

**方案**：
1. `PriorityQueue` 基于 heapq 实现最小堆，按 next_run_time 排序，peek 获取最早待执行任务
2. `Cache` 使用内存 SQLite（`"sqlite://"`）持久化调度状态（job_definition_id、next_run_time、active、timezone、schedule）
3. TaskRunner 按 poll_interval（默认10秒）轮询队列：到期任务执行 create_job 后计算下次时间重新入队
4. 启动时 populate_cache() 从数据库加载所有带 schedule 的活跃作业定义
5. 更新/删除作业定义时同步更新 Cache 和 Queue（Queue 中过期任务在 process_queue 时通过 Cache 校验跳过）

**证据**：F-158~F-171

### I-07: 参数注入机制（Parameter Injection）

**概念**：通过 tagged cell 注入参数实现 notebook 参数化执行

**问题**：同一 notebook 需要以不同参数重复执行（如每日报告不同日期），如何在不修改原始 notebook 的情况下注入参数值？

**方案**：
1. `add_parameters(nb, parameters)` 创建新代码 cell，内容为 `key = value` 赋值语句
2. 新 cell 标记为 `"injected-parameters"` tag
3. 插入位置优先级：替换已有 injected-parameters cell → 插入到 parameters-tagged cell 之后 → 插入到最前面
4. 这与 papermill 的参数化约定一致，兼容已使用 `parameters` tag 的 notebook
5. Python 脚本执行器通过环境变量 `JUPYTER_PARAM_{key}` 传递参数

**证据**：F-182、F-155

### I-08: 轻量级自动数据库迁移（Lightweight Auto-Migration）

**概念**：基于 inspect + ALTER TABLE ADD COLUMN 的零框架自动迁移

**问题**：版本升级可能新增数据库列，但不应要求用户手动执行迁移脚本；SQLite 对 ALTER TABLE 支持有限。

**方案**：
1. `update_db_schema()` 在每次 create_tables 时检查现有表结构
2. 对比模型定义的列与数据库现有列，为缺少的列生成 `ALTER TABLE ADD COLUMN ... NULL`
3. 新列必须 nullable 且不依赖默认值（迁移时默认值被忽略）
4. 不支持列删除或类型变更（仅 additive 迁移）
5. 代码注释强制约束："All new columns added to this table must be nullable"

**证据**：F-112~F-114

### I-09: 前端 Token 依赖注入（Frontend Token DI）

**概念**：基于 Lumino Token 的依赖注入实现前端可扩展性

**问题**：高级选项面板和遥测日志需要支持第三方扩展自定义，但不应硬编码依赖。

**方案**：
1. 定义 `Scheduler.IAdvancedOptions` 和 `Scheduler.TelemetryHandler` 两个 Token
2. 独立插件提供这些 Token 的默认实现（AdvancedOptions 组件、noop 遥测器）
3. 主插件通过 requires 声明依赖这些 Token，第三方可替换实现
4. 上下文菜单基于后端列表动态注册，支持多文件类型

**证据**：F-188~F-190

### I-10: 扩展点分层设计（Layered Extension Points）

**概念**：三层扩展点设计：Backend（执行后端）→ Scheduler（调度逻辑）→ ExecutionManager（执行逻辑）

**问题**：不同场景需要不同粒度的定制：有些只需要自定义执行逻辑（如远程执行），有些需要替换整个调度逻辑（如外部任务队列），有些只需要添加新的文件类型支持。

**方案**：
1. **Backend 层**（最大粒度）：继承 BaseBackend，通过 entry_points 注册，完全自定义 scheduler_class + execution_manager_class + database_manager_class + file_extensions + output_formats
2. **Scheduler 层**（中粒度）：继承 BaseScheduler 或 Scheduler，通过 `SchedulerApp.scheduler_class` 配置替换，可自定义持久化和作业生命周期
3. **ExecutionManager 层**（最小粒度）：继承 ExecutionManager，通过后端配置或 `scheduler_class` 指定，仅自定义执行逻辑
4. 内置测试类 SchedulerWithErrors/JobFilesManagerWithErrors 演示了如何通过替换类来注入测试行为

**证据**：F-012~F-013、F-055、F-084、F-089、F-090

---

## 知识地图

```
jupyter-scheduler/
├── 00-introduction.md          # 项目概述与核心概念
├── 01-architecture-overview.md # 整体架构（后端注册→路由→调度→执行→文件）
├── 02-extension-app.md         # SchedulerApp 扩展应用与启动流程
├── 03-backend-system.md        # 后端注册体系（BaseBackend/BackendRegistry/entry_points）
├── 04-job-routing.md           # Job ID 命名空间路由与多后端调度
├── 05-scheduler-lifecycle.md   # 作业生命周期（创建→调度→执行→状态更新→清理）
├── 06-execution-managers.md    # 执行管理器（Notebook/Python脚本/自定义）
├── 07-task-runner.md           # 定时调度（优先队列/cron/时区/缓存）
├── 08-data-models.md           # 数据模型与ORM（pydantic模型/SQLAlchemy/自动迁移）
├── 09-http-api-handlers.md     # REST API 与 Handler 体系
├── 10-file-management.md       # 文件管理（staging/下载/副作用/归档）
├── 11-frontend-extension.md    # 前端扩展架构（插件/命令/Token DI/上下文菜单）
├── 12-custom-backend.md        # 自定义后端开发指南
└── index.md                    # 概念索引
```

```
examples/
├── 01-create-first-job.md      # 创建第一个Notebook作业
├── 02-schedule-recurring-job.md# 创建定时作业
├── 03-run-python-script.md     # 执行Python脚本作业
├── 04-parameterized-notebook.md# 参数化Notebook执行
├── 05-custom-backend.md        # 开发自定义后端
└── index.md                    # 示例索引
```

```
references/
├── app-entry-source.md         # SchedulerApp 源码解析
├── scheduler-source.md         # Scheduler/BaseScheduler 源码解析
├── handlers-source.md          # HTTP Handlers 源码解析
├── executor-source.md          # ExecutionManager 源码解析
├── task-runner-source.md       # TaskRunner 源码解析
├── models-source.md            # 数据模型源码解析
├── orm-source.md               # ORM 数据库层源码解析
├── backend-registry-source.md  # BackendRegistry 源码解析
├── index.md                    # 信源索引
```

---

## 文档结构设计原则

1. **概念先行**：先讲"是什么"和"为什么"，再讲"怎么用"
2. **数据流驱动**：按作业生命周期（创建→排队→执行→完成→下载）组织概念文档
3. **信源可溯**：每个概念文档引用 references/ 中的源码解析文档，每个事实标注 F-xxx 编号
4. **示例最小化**：examples 提供端到端可操作步骤，concepts 专注于原理和设计
5. **扩展导向**：重点覆盖自定义后端开发，这是 jupyter-scheduler 最有价值的扩展点
