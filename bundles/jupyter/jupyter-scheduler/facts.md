---
sources:
- ../../../../../external/libs/jupyter/jupyter-scheduler/pyproject.toml
- ../../../../../external/libs/jupyter/jupyter-scheduler/package.json
- ../../../../../external/libs/jupyter/jupyter-scheduler/README.md
- ../../../../../external/libs/jupyter/jupyter-scheduler/setup.py
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/__tests__/backend-utils.spec.ts
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/__tests__/jupyter_scheduler.spec.ts
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/advanced-options.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/advanced-table/advanced-table-header.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/advanced-table/advanced-table.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/advanced-table/index.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/backend-picker.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/box.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/button-bar.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/button.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/cluster.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/collapsible-panel.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/compute-type-picker.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/confirm-buttons.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/confirm-dialog-buttons.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/create-schedule-options.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/environment-picker.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/error-boundary.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/files-directory-link.tsx
- ../../../../../external/libs/jupyter/jupyter-scheduler/src/components/heading.tsx
type: Facts
okf_version: '0.2'
title: jupyter-scheduler 源码事实清单
generated: '2026-08-22'
tags:
- facts
---

# Jupyter Scheduler 源码事实清单

> R阶段产出：零推测事实清单，所有事实均可通过源码路径验证。

## F-001 ~ F-020: 项目基础信息

F-001: 包名 `jupyter_scheduler`，版本号 `2.11.0`，`version_info = (2, 11, 0, "", "")`，定义于 `jupyter_scheduler/_version.py`

F-002: 构建系统使用 hatchling（`hatchling>=1.3.1`），构建后端为 `hatchling.build`，前端构建依赖 `jupyterlab~=4.0`，见 `pyproject.toml`

F-003: 包描述为 "A JupyterLab extension for running jobs"，许可证为 BSD License，作者为 Project Jupyter，Python 版本要求 `>=3.9`，支持 Python 3.9-3.13

F-004: 核心运行时依赖：`jupyter_server>=1.6,<3`、`traitlets~=5.0`、`nbconvert~=7.0`、`pydantic>=1.10,<3`、`sqlalchemy>=2.0,<3`、`croniter~=1.4`、`pytz>=2023.3,<=2024.2`、`fsspec>=2023.6.0,<=2025.3.2,!=2025.3.1`、`psutil~=5.9`

F-005: 通过 entry_points 注册后端，入口组名为 `jupyter_scheduler.backends`，内置注册两个后端：`jupyter_server_nb`（Notebook后端）→ `JupyterServerNotebookBackend`，`jupyter_server_py`（Python后端）→ `JupyterServerPythonBackend`

F-006: 前端扩展 ID 为 `@jupyterlab/scheduler:plugin`，Labextension 静态文件安装到 `share/jupyter/labextensions/@jupyterlab/scheduler`，配置文件安装到 `etc/jupyter/jupyter_server_config.d` 和 `etc/jupyter/jupyter_notebook_config.d`

F-007: 项目仓库地址为 `https://github.com/jupyter-server/jupyter-scheduler`，见 pyproject.toml [project.urls]

F-008: 包含 pydantic v1 兼容层 `jupyter_scheduler/pydantic_v1/`，提供 `__init__.py`、`dataclasses.py`、`main.py`，支持 pydantic v1 和 v2

F-009: 默认数据库为 SQLite，存储路径为 `{jupyter_data_dir()}/scheduler.sqlite`，可通过 `SchedulerApp.db_url` 配置

F-010: 默认 staging 路径为 `{jupyter_data_dir()}/scheduler_staging_area`，可通过 `BaseScheduler.staging_path` 配置

F-011: 本地输出目录默认为 `jobs`（相对于 Jupyter server root_dir），可通过 `BaseScheduler.output_directory` 配置

F-012: 默认执行管理器为 `DefaultExecutionManager`（执行 Notebook），默认任务运行器为 `TaskRunner`（定时调度），默认环境管理器为 `CondaEnvironmentManager`

F-013: 默认调度器类为 `jupyter_scheduler.scheduler.Scheduler`，默认文件管理器类为 `jupyter_scheduler.job_files_manager.JobFilesManager`

F-014: TaskRunner 默认轮询间隔为 10 秒（`poll_interval=10`），可配置

F-015: 输出文件名模板默认为 `"{{input_filename}}-{{create_time}}"`，定义于 `OUTPUT_FILENAME_TEMPLATE` 常量

F-016: Job ID 格式从 v3.0 起为 `backend_id:uuid`（如 `jupyter_server_nb:abc123-def456-...`），v3.0 之前为纯 UUID（legacy 格式）

F-017: 提供 `SchedulerWithErrors` 和 `JobFilesManagerWithErrors` 两个测试用类，随机抛出异常用于 UI 测试

F-018: 提供 `ArchivingScheduler` 和 `ArchivingExecutionManager`，将所有输出文件打包为 tar.gz 归档

F-019: 支持 `drop_tables` 配置项（默认 False），启动时可选择删除数据库表重建

F-020: 支持 `legacy_job_backend` 配置项，用于指定路由 legacy 作业（纯UUID ID）的后端

## F-021 ~ F-050: 扩展应用 SchedulerApp

F-021: `SchedulerApp` 定义于 `jupyter_scheduler/extension.py`，继承自 `jupyter_server.extension.application.ExtensionApp`，`name = "jupyter_scheduler"`

F-022: SchedulerApp 注册 11 个 HTTP 路由：
- `/scheduler/backends` → BackendsHandler（列出可用后端）
- `/scheduler/jobs` → JobHandler（创建/列出作业）
- `/scheduler/jobs/count` → JobsCountHandler（统计作业数）
- `/scheduler/jobs/{job_id}` → JobHandler（查询/更新/删除单个作业）
- `/scheduler/jobs/{job_id}/download_files` → FilesDownloadHandler（下载作业文件）
- `/scheduler/batch/jobs` → BatchJobHandler（批量删除作业）
- `/scheduler/job_definitions` → JobDefinitionHandler（创建/列出作业定义）
- `/scheduler/job_definitions/{job_definition_id}` → JobDefinitionHandler（查询/更新/删除作业定义）
- `/scheduler/job_definitions/{job_definition_id}/jobs` → JobFromDefinitionHandler（从定义创建作业）
- `/scheduler/runtime_environments` → RuntimeEnvironmentsHandler（列出运行时环境）
- `/scheduler/config` → ConfigHandler（返回配置和支持的功能）

F-023: Job ID 正则表达式为 `r"(?P<job_id>[\w:%-]+)"`，支持 `backend_id:uuid` 格式（含冒号和百分号）

F-024: JobDefinition ID 正则表达式为 `r"(?P<job_definition_id>\w+(?:-\w+)+)"`，匹配 UUID 格式（含连字符）

F-025: SchedulerApp 配置项包括：`drop_tables`（Bool）、`db_url`（Unicode，默认SQLite路径）、`legacy_job_backend`（Unicode，可空）、`backend_config`（Dict，每后端配置覆盖）、`preferred_backends`（Dict，文件扩展名→后端ID映射）、`environment_manager_class`（Type，默认CondaEnvironmentManager）、`scheduler_class`（Type，默认Scheduler）、`job_files_manager_class`（Type，默认JobFilesManager）

F-026: `initialize_settings()` 方法执行顺序：`super().initialize_settings()` → `discover_backends()` 发现后端 → `_build_backend_configs()` 构建配置 → `get_legacy_job_backend_id()` 确定legacy后端 → 创建 EnvironmentManager → 创建 BackendRegistry 并 initialize() → 获取legacy后端的scheduler → 创建 JobFilesManager → 更新 settings → 启动各后端的 task_runner

F-027: `_build_backend_configs()` 为每个发现的后端创建 BackendConfig 对象，支持通过 `backend_config` trait 覆盖 `db_url` 和 `metadata`；对默认notebook后端特殊处理 `scheduler_class` 覆盖以保持向后兼容

F-028: settings 中注入的对象：`environments_manager`、`scheduler`（legacy后端的调度器，向后兼容）、`backend_registry`、`job_files_manager`

F-029: 初始化完成后，遍历所有后端，对有 task_runner 的后端通过 `loop.create_task(backend.scheduler.task_runner.start())` 异步启动定时任务

F-030: 启动日志输出格式：`"Initialized {n} backend(s): {ids} (legacy_job_backend: {default_id})"`

F-031: 若 `discover_backends()` 返回空字典，抛出 ValueError：`"No scheduler backends available. The 'jupyter_server_nb' backend should be registered via entry points."`

F-032: `backend_config` 支持的 per-backend 覆盖键为：`db_url`、`metadata`，格式示例 `{'k8s': {'db_url': 'postgresql://...'}}`

F-033: `preferred_backends` 用于控制同一文件扩展名有多个后端支持时的默认选择，格式示例 `{'ipynb': 'jupyter_server_nb', 'py': 'jupyter_server_py'}`

## F-034 ~ F-060: 后端体系 BaseBackend 与 BackendRegistry

F-034: `BaseBackend` 定义于 `jupyter_scheduler/base_backend.py`，是所有后端的基类，通过 ClassVar 定义能力属性

F-035: BaseBackend 的类属性：`id`（str，后端唯一标识）、`name`（str，显示名称）、`description`（str，默认""）、`scheduler_class`（str，调度器类完全限定路径）、`execution_manager_class`（str，执行管理器类完全限定路径）、`database_manager_class`（Optional[str]，默认None）、`file_extensions`（List[str]，支持的文件扩展名）、`output_formats`（List[OutputFormat]，支持的输出格式）

F-036: BaseBackend 提供 `to_dict()` 类方法，将类属性转换为字典用于 BackendConfig 创建

F-037: `JupyterServerNotebookBackend` 定义于 `backends.py`，id=`"jupyter_server_nb"`，name=`"Jupyter Server Notebook"`，scheduler_class=`"jupyter_scheduler.scheduler.Scheduler"`，execution_manager_class=`"jupyter_scheduler.executors.DefaultExecutionManager"`，file_extensions=`["ipynb"]`，输出格式：ipynb（Notebook）、html（HTML）

F-038: `JupyterServerPythonBackend` 定义于 `backends.py`，id=`"jupyter_server_py"`，name=`"Jupyter Server Python"`，scheduler_class=`"jupyter_scheduler.scheduler.Scheduler"`，execution_manager_class=`"jupyter_scheduler.python_executor.PythonScriptExecutionManager"`，file_extensions=`["py"]`，输出格式：stdout（Output）、stderr（Errors）、json（JSON）

F-039: 常量 `JUPYTER_SERVER_NB_BACKEND_ID = "jupyter_server_nb"`、`JUPYTER_SERVER_PY_BACKEND_ID = "jupyter_server_py"`、`DEFAULT_FALLBACK_BACKEND_ID = JUPYTER_SERVER_NB_BACKEND_ID`

F-040: `BackendConfig`（pydantic模型）定义于 `backends.py`，字段：id、name、description、scheduler_class、execution_manager_class、database_manager_class（Optional）、db_url（Optional）、file_extensions、output_formats（List[Dict[str,str]]）、metadata（Optional[Dict]）

F-041: `DescribeBackendResponse` 定义于 `backends.py`，用于 GET /scheduler/backends API 响应，字段：id、name、description、file_extensions、output_formats（List[OutputFormat]）

F-042: `BackendInstance`（pydantic模型）定义于 `backend_registry.py`，包含 config（BackendConfig）和 scheduler（BaseScheduler实例）两个字段

F-043: `BackendRegistry` 定义于 `backend_registry.py`，是后端注册、初始化和路由的核心类，维护 `_configs`、`_backends`（Dict[str, BackendInstance]）、`_legacy_job_backend`（str）、`_preferred_backends`（Dict[str,str]）、`_extension_map`（Dict[str, List[str]]，扩展名→后端ID列表映射）

F-044: BackendRegistry.initialize() 验证后端ID唯一性（重复ID抛ValueError）、ID不含冒号（抛ValueError），然后为每个配置创建 BackendInstance 并建立扩展名映射

F-045: BackendRegistry._create_backend() 通过 `import_class()` 动态导入 scheduler_class，为使用默认SQLAlchemy存储的后端调用 `create_tables()` 创建数据库表，实例化scheduler，若有 execution_manager_class 则动态导入并设置

F-046: `import_class(class_path)` 函数通过 `rsplit(".", 1)` 分割模块路径和类名，使用 `__import__` 动态导入模块，`getattr` 获取类

F-047: BackendRegistry.get_backend(backend_id) 返回匹配ID的 BackendInstance 或 None

F-048: BackendRegistry.get_legacy_job_backend() 返回处理legacy作业的后端，若配置的legacy_job_backend不在已注册后端中抛KeyError

F-049: BackendRegistry.get_for_file(input_uri) 按文件扩展名自动选择后端：先检查 preferred_backends 配置，否则按名称字母序返回第一个；无后端支持该扩展名抛ValueError

F-050: BackendRegistry.describe_backends() 按名称字母序返回所有后端的 DescribeBackendResponse 列表

F-051: `discover_backends()` 定义于 `backend_utils.py`，通过 `importlib.metadata.entry_points()` 发现 `jupyter_scheduler.backends` 入口组中注册的所有后端类，ImportError时记录warning跳过，缺少id属性时跳过

F-052: `get_legacy_job_backend_id()` 定义于 `backend_utils.py`，优先级：显式配置的 legacy_job_backend > DEFAULT_FALLBACK_BACKEND_ID（jupyter_server_nb）> 抛ValueError

F-053: 后端ID中不能包含冒号（`:`），因为冒号用作 job_id 的 backend_id 和 uuid 之间的分隔符

## F-054 ~ F-090: 调度器 BaseScheduler 与 Scheduler

F-054: `BaseScheduler` 定义于 `scheduler.py`，继承 `LoggingConfigurable`，是所有调度器的抽象基类

F-055: BaseScheduler 定义的 traitlets 配置项：`staging_path`（Unicode，默认jupyter_data_dir/scheduler_staging_area）、`output_directory`（Unicode，默认"jobs"）、`execution_manager_class`（Type，默认DefaultExecutionManager）、`root_dir`（Unicode，Jupyter server根目录）、`environments_manager`（Instance，EnvironmentManager实例）

F-056: BaseScheduler 构造函数接收 `root_dir`、`environments_manager`、`config`（可选）、`backend_id`（可选）

F-057: BaseScheduler 定义的抽象方法：create_job、update_job、list_jobs、count_jobs、get_job、delete_job、stop_job、create_job_definition、update_job_definition、delete_job_definition、get_job_definition、list_job_definitions、create_job_from_definition、get_staging_paths

F-058: BaseScheduler.file_exists(path) 检查文件是否存在于root_dir下，路径遍历攻击防护：验证 `os.path.abspath(os_path)` 以 root 开头

F-059: BaseScheduler.dir_exists(path) 检查目录是否存在于root_dir下，同样有路径遍历防护

F-060: BaseScheduler.get_job_filenames(model) 返回输出格式到文件名的映射字典：每个output_format对应 `{basefilename}-{timestamp}.{format}`，input对应原始input_filename，package_input_folder时添加files键

F-061: BaseScheduler.add_job_files(model) 为model填充job_files列表，每个文件检查是否存在后添加JobFile，input文件始终添加（file_path可能为None），package_input_folder时添加Files链接

F-062: BaseScheduler.get_local_output_path(model, root_dir_relative=False) 返回本地输出目录路径，目录名格式为 `{basefilename}-{job_id}`

F-063: `Scheduler` 继承 BaseScheduler，是默认调度器实现，使用 SQLAlchemy ORM 持久化，支持多进程执行

F-064: Scheduler 额外配置项：`task_runner_class`（Type，默认TaskRunner）、`db_url`（Unicode）、`task_runner`（Instance，BaseTaskRunner实例，可空）

F-065: Scheduler 构造函数额外接收 `db_url` 参数，若 task_runner_class 非空则实例化 task_runner

F-066: Scheduler.db_session 属性使用懒加载，首次访问时调用 `create_session(self.db_url)` 创建 SQLAlchemy session 工厂

F-067: Scheduler.create_job(model) 执行流程：验证input_uri存在→验证notebook有kernel（.ipynb文件）→幂等性token检查→生成job_id（backend_id:uuid格式）→创建Job ORM对象并提交→复制输入文件/文件夹到staging→multiprocessing spawn新进程执行→记录pid→返回job_id

F-068: create_job中使用 `mp.get_context("spawn")` 创建子进程（非fork），避免Python<3.12中fork进程的asyncio事件循环bug

F-069: create_job中子进程目标为 `execution_manager_class(job_id, staging_paths, root_dir, db_url).process`

F-070: Scheduler.copy_input_file(input_uri, copy_to_path) 使用fsspec读取源文件并写入staging路径，支持本地和远程文件系统

F-071: Scheduler.copy_input_folder(input_uri, nb_copy_to_path) 复制输入文件所在目录到staging，返回复制的文件相对路径列表（用于packaged_files）

F-072: Scheduler.update_job(job_id, model) 直接使用SQLAlchemy update更新字段

F-073: Scheduler.list_jobs(query) 支持过滤条件：status、job_definition_id、start_time、name（前缀匹配）、tags（包含所有标签）；支持排序（多字段，asc/desc）；支持分页（max_items + next_token偏移量）

F-074: list_jobs返回的每个job调用add_job_files填充文件信息，next_token计算为当前偏移+返回数量，达到total时设为None

F-075: Scheduler.get_job(job_id, job_files=True) 查询单个job，job_files=True时调用add_job_files填充文件信息

F-076: Scheduler.delete_job(job_id) 流程：若job状态为IN_PROGRESS则先stop_job→删除staging目录→删除数据库记录

F-077: Scheduler.stop_job(job_id) 流程：更新状态为STOPPING→查找子进程（通过psutil遍历当前进程的children递归查找匹配pid）→kill进程→更新状态为STOPPED

F-078: Scheduler.create_job_definition(model) 流程：验证input_uri→创建JobDefinition ORM对象→复制输入文件到staging→若有schedule且task_runner存在则调用task_runner.add_job_definition

F-079: Scheduler.update_job_definition(job_definition_id, model) 有短路优化：若input_uri/schedule/timezone/active均未变化则直接返回；否则更新数据库，必要时复制新输入文件，通知task_runner

F-080: Scheduler.delete_job_definition(job_definition_id) 流程：删除关联的所有job（级联删除）→删除job_definition记录→通知task_runner

F-081: Scheduler.create_job_from_definition(job_definition_id, model) 从job_definition创建job：获取definition→从staging读取input路径→合并属性→调用create_job

F-082: Scheduler.get_staging_paths(model) 返回staging路径字典：每个output_format对应 `{staging_path}/{id}/{filename}`，input对应 `{staging_path}/{id}/{input_filename}`

F-083: `ArchivingScheduler` 继承 Scheduler，重写 get_staging_paths 添加 `tar.gz` 归档路径，execution_manager_class 默认 ArchivingExecutionManager

F-084: `SchedulerWithErrors` 继承 Scheduler，所有方法以50%概率抛出 SchedulerError，仅用于UI测试，通过 `--SchedulerApp.scheduler_class=jupyter_scheduler.scheduler.SchedulerWithErrors` 启用

## F-085 ~ F-110: 数据模型 models.py

F-085: `Status` 枚举值：CREATED、QUEUED、IN_PROGRESS、COMPLETED、FAILED、STOPPING、STOPPED，继承 str 和 Enum

F-086: `OutputFormat` 模型：id（格式标识如"ipynb"）、label（显示名如"Notebook"）、description（可选提示文本）

F-087: `RuntimeEnvironment` 模型：name、label、description、file_extensions、output_formats、metadata（Optional[Dict]）、compute_types（Optional[List[str]]）、default_compute_type（Optional[str]）、utc_only（Optional[bool]）

F-088: `CreateJob` 模型字段：input_uri（必填）、input_filename（root_validator自动从input_uri提取）、runtime_environment_name（必填）、runtime_environment_parameters（Optional[Dict]）、output_formats（Optional[List[str]]）、idempotency_token（Optional[str]）、job_definition_id（Optional[str]）、parameters（Optional[Dict[str,str]]）、tags（Optional[Tags]）、name（必填）、output_filename_template（默认OUTPUT_FILENAME_TEMPLATE）、compute_type（Optional[str]）、package_input_folder（Optional[bool]）、backend_id（Optional[str]）

F-089: `DescribeJob` 模型比CreateJob多字段：job_id、job_files（List[JobFile]，默认[]）、url、create_time（int）、update_time（int）、start_time（Optional[int]）、end_time（Optional[int]）、status（默认CREATED）、status_message（Optional[str]）、downloaded（bool，默认False）、packaged_files（Optional[List[str]]），启用orm_mode=True

F-090: `JobFile` 模型：display_name、file_format、file_path（Optional[str]，相对于server root_dir）

F-091: `CreateJobDefinition` 模型比CreateJob多：schedule（Optional[str]，cron表达式）、timezone（Optional[str]），无idempotency_token和job_definition_id

F-092: `DescribeJobDefinition` 模型比CreateJobDefinition多：job_definition_id、create_time、update_time、active（bool，默认True）、url、packaged_files，启用orm_mode=True

F-093: `UpdateJob` 模型：status（Optional，只能设为STOPPED）、name、compute_type、status_message、runtime_environment_parameters

F-094: `UpdateJobDefinition` 模型：runtime_environment_name、runtime_environment_parameters、output_formats、parameters、tags、name、url、schedule、timezone、output_filename_template、active、compute_type、input_uri

F-095: `SortDirection` 枚举：asc、desc；`SortField` 模型：name（str）、direction（SortDirection）；默认排序 `DEFAULT_SORT = SortField(name="create_time", direction=SortDirection.desc)`

F-096: `ListJobsQuery` 模型：job_definition_id、status、name、start_time、tags、sort_by（默认[DEFAULT_SORT]）、max_items（默认1000）、next_token

F-097: `ListJobsResponse` 模型：jobs（List[DescribeJob]）、total_count（int）、next_token（Optional[str]）

F-098: `CountJobsQuery` 模型：status（默认Status.IN_PROGRESS）

F-099: `JobFeature` 枚举：job_name、parameters、output_formats、job_definition、idempotency_token、tags、email_notifications、timeout_seconds、retry_on_timeout、max_retries、min_retry_interval_millis、output_filename_template、stop_job、delete_job

F-100: `EmailNotifications` 模型：on_start（Optional[List[str]]）、on_success（Optional[List[str]]）、on_failure（Optional[List[str]]）、no_alert_for_skipped_runs（bool，默认True）

F-101: `CreateJobFromDefinition` 模型：parameters（Optional[Dict[str,str]]），用于从作业定义手动触发作业时覆盖参数

F-102: `compute_sort_model(query_argument)` 函数解析sort_by查询参数，正则 `^(asc|desc)?\(?([^\)]+)\)?` 支持 `asc(name)` 或 `name` 格式

F-103: Tags 类型别名为 `List[str]`，EnvironmentParameterValues 类型别名为 `Union[int, float, bool, str]`

## F-104 ~ F-125: ORM 数据库层

F-104: ORM 使用 SQLAlchemy 2.0 声明式映射，`Base = declarative_base()`，定义于 `orm.py`

F-105: `JsonType` 是 TypeDecorator，将Python对象序列化为JSON字符串存储（String类型），读取时反序列化，cache_ok=True

F-106: `EmailNotificationType` 是 TypeDecorator，将 EmailNotifications pydantic模型序列化为JSON存储，读取时构造为EmailNotifications对象

F-107: `CommonColumns` 是 declarative_mixin，Job和JobDefinition共用的列：runtime_environment_name（String(256), not null）、runtime_environment_parameters（JsonType(1024)）、compute_type（String(256)）、input_filename（String(256), not null）、output_formats（JsonType(512)）、name（String(256)）、tags（JsonType(1024)）、parameters（JsonType(1024)）、email_notifications（EmailNotificationType(1024)）、timeout_seconds（Integer, 默认600）、retry_on_timeout（Boolean, 默认False）、max_retries（Integer, 默认0）、min_retry_interval_millis（Integer, 默认0）、output_filename_template（String(256)）、update_time（Integer, UTC毫秒时间戳,onupdate自动更新）、create_time（Integer, UTC毫秒时间戳）、package_input_folder（Boolean）、packaged_files（JsonType, 默认[]）

F-108: `Job` 表名 `"jobs"`，额外列：job_id（String(128), 主键, 默认generate_uuid）、job_definition_id（String(36)）、status（String(64), 默认STOPPED）、status_message（String(1024)）、start_time（Integer）、end_time（Integer）、url（String(256), 默认generate_jobs_url）、pid（Integer, 子进程ID）、idempotency_token（String(256)）、backend_id（String(64)）

F-109: `JobDefinition` 表名 `"job_definitions"`，额外列：job_definition_id（String(36), 主键, 默认generate_uuid）、schedule（String(256)）、timezone（String(36)）、url（String(256), 默认generate_job_definitions_url）、active（Boolean, 默认True）、backend_id（String(64)）

F-110: `generate_uuid()` 函数返回 `str(uuid4())`

F-111: `generate_jobs_url(context)` 返回 `f"/jobs/{job_id}"`，`generate_job_definitions_url(context)` 返回 `f"/job_definitions/{job_definition_id}"`

F-112: `create_tables(db_url, drop_tables=False)` 流程：create_engine → update_db_schema（自动迁移新增列）→ 若drop_tables则drop_all → create_all

F-113: `update_db_schema(engine, Base)` 实现轻量级自动迁移：inspect现有表的列，对比模型列，为缺少的列执行 `ALTER TABLE ADD COLUMN ... NULL`（新列必须nullable）

F-114: 数据库迁移注释明确要求："All new columns added to this table must be nullable to ensure compatibility during database migrations. Any default values specified for new columns will be ignored during the migration process."

F-115: `create_session(db_url)` 创建 SQLAlchemy sessionmaker 工厂（非session实例），echo=False

F-116: Job表默认status为STOPPED（非CREATED），这是因为stop_job查询时需要匹配IN_PROGRESS状态

## F-117 ~ F-140: HTTP Handlers

F-117: 所有Handler继承 `ExtensionHandlerMixin`、`JobHandlersMixin`、`APIHandler`，使用 `@authenticated` 装饰器保护

F-118: `JobHandlersMixin` 提供：scheduler属性（从settings懒加载）、backend_registry属性（从settings懒加载）、environments_manager属性、execution_manager_class属性、get_scheduler(job_id)方法（根据job_id路由到正确后端的scheduler）、resolve_backend_for_job(payload)方法（从payload的backend_id或文件扩展名自动选择后端）

F-119: get_scheduler(job_id)调用resolve_scheduler解析，backend不可用时抛HTTPError(400)

F-120: resolve_backend_for_job(payload)优先使用payload中的backend_id（找不到抛404），否则按input_uri的文件扩展名自动选择（找不到抛400）

F-121: `JobDefinitionHandler` 支持GET（列表/单个）、POST（创建）、PATCH（更新）、DELETE（删除）；GET列表支持create_time、name、tags、sort_by、max_items、next_token查询参数

F-122: JobDefinitionHandler POST时先resolve_backend_for_job选择后端，设置payload["backend_id"]，再调用对应scheduler.create_job_definition

F-123: `JobHandler` 支持GET（列表/单个）、POST（创建）、PATCH（更新，仅允许status设为STOPPED）、DELETE（删除）

F-124: JobHandler POST时自动设置默认output_formats（从后端配置获取），成功返回{"job_id": ..., "backend_id": ...}

F-125: JobHandler PATCH时，若status非STOPPED则抛HTTPError(500)，status=STOPPED时调用scheduler.stop_job，否则调用update_job

F-126: JobHandler GET单个job时通过get_scheduler(job_id)路由到正确后端；legacy job（backend_id为空）填充为legacy后端ID

F-127: JobHandler GET列表时从legacy后端查询所有作业（共享数据库），对QUEUED/IN_PROGRESS状态的作业通过对应后端的scheduler.get_job同步状态（支持远程后端如Braket同步状态）

F-128: IdempotencyTokenError返回HTTP 409状态码；ValidationError返回400；InputUriError/SchedulerError返回500

F-129: `JobFromDefinitionHandler` 仅支持POST，从作业定义创建作业实例

F-130: `BatchJobHandler` 支持DELETE批量删除，通过job_id查询参数传递多个ID

F-131: `JobsCountHandler` GET返回指定status的作业计数，默认统计IN_PROGRESS

F-132: `RuntimeEnvironmentsHandler` GET返回可用运行时环境列表及其输出格式映射

F-133: `ConfigHandler` GET返回supported_features和manage_environments_command

F-134: `FilesDownloadHandler` GET触发文件下载，支持redownload查询参数强制重新下载，通过multiprocessing Process启动Downloader

F-135: `BackendsHandler` GET返回所有可用后端的DescribeBackendResponse列表（按名称字母序）

F-136: Handler统一异常处理模式：ValidationError→400、IdempotencyTokenError→409、InputUriError/SchedulerError→500、HTTPError原样抛出、其他Exception→500

F-137: 所有Handler方法使用 `ensure_async()` 包装同步调度器方法调用，兼容异步调度器

## F-138 ~ F-155: 执行管理器 ExecutionManager

F-138: `ExecutionManager`（ABC）定义于 `executors.py`，是执行管理器的抽象基类，模板方法模式

F-139: ExecutionManager构造函数接收 job_id、root_dir、db_url、staging_paths（Dict[str,str]）

F-140: ExecutionManager.process() 是模板方法（不可重写），执行流程：before_start() → execute() → on_failure(e)（异常时）或 on_complete()（成功时）

F-141: ExecutionManager.before_start() 更新job状态为IN_PROGRESS，记录start_time

F-142: ExecutionManager.on_failure(e) 更新job状态为FAILED，记录status_message为异常字符串

F-143: ExecutionManager.on_complete() 更新job状态为COMPLETED，记录end_time

F-144: ExecutionManager 抽象方法：execute()、supported_features()（类方法）；validate()类方法默认返回True

F-145: ExecutionManager.model属性懒加载，从数据库查询Job并构造DescribeJob（from_orm）

F-146: ExecutionManager.db_session属性懒加载，调用create_session创建session工厂

F-147: `DefaultExecutionManager` 继承 ExecutionManager，使用nbconvert ExecutePreprocessor执行notebook

F-148: DefaultExecutionManager.execute() 流程：读取input notebook → 若有parameters则调用add_parameters注入参数 → 创建ExecutePreprocessor（kernel_name从notebook metadata获取，store_widget_state=True，cwd=staging_dir）→ ep.preprocess()执行 → finally中add_side_effects_files和create_output_files

F-149: DefaultExecutionManager.add_side_effects_files(staging_dir) 递归扫描staging目录，将输入notebook以外的新文件添加到packaged_files

F-150: DefaultExecutionManager.create_output_files(job, notebook_node) 对每个output_format使用nbconvert.get_exporter获取导出器，导出后写入staging路径

F-151: DefaultExecutionManager.supported_features() 返回：job_name=True、output_formats=True、stop_job=True、delete_job=True，其余功能False（job_definition/idempotency_token/tags/email_notifications/timeout等均不支持）

F-152: DefaultExecutionManager.validate(input_path) 检查notebook是否有kernelspec.name，没有返回False

F-153: `ArchivingExecutionManager` 继承 DefaultExecutionManager，将side-effect文件放入 `files/` 子目录执行，完成后打包所有输出为tar.gz归档，清理run_dir

F-154: `PythonScriptExecutionManager` 继承 ExecutionManager，通过subprocess.run执行Python脚本

F-155: PythonScriptExecutionManager.execute() 流程：复制当前环境变量 → parameters转为JUPYTER_PARAM_{key}环境变量 → subprocess.run([sys.executable, input_path], capture_output=True, text=True) → 写入stdout/stderr文件 → add_side_effects_files → returncode非0则抛RuntimeError

F-156: PythonScriptExecutionManager.supported_features() 中 output_formats=False（不支持notebook转换），其他同DefaultExecutionManager

F-157: PythonScriptExecutionManager.validate() 始终返回True（Python脚本无需kernel验证）

## F-158 ~ F-175: 任务运行器 TaskRunner（定时调度）

F-158: `BaseTaskRunner` 定义于 `task_runner.py`，继承 LoggingConfigurable，抽象基类

F-159: BaseTaskRunner.poll_interval 配置项默认10秒，控制轮询间隔

F-160: BaseTaskRunner 抽象方法：start()（async）、add_job_definition()、update_job_definition()、delete_job_definition()、pause_jobs()、resume_jobs()

F-161: `TaskRunner` 继承 BaseTaskRunner，默认实现，维护内存SQLite缓存和优先队列

F-162: TaskRunner内部使用 `Cache` 类（内存SQLite `"sqlite://"`）存储 job_definitions_cache 表，字段：job_definition_id（主键）、next_run_time（Integer）、active（Boolean）、timezone（String(36)）、schedule（String(256)）

F-163: TaskRunner内部使用 `PriorityQueue`（基于heapq）管理待执行任务，`JobDefinitionTask` 包含 job_definition_id 和 next_run_time，按 next_run_time 排序（`__lt__` 比较）

F-164: TaskRunner.populate_cache() 从数据库加载所有有schedule的JobDefinition，计算next_run_time，写入Cache，active的加入PriorityQueue

F-165: TaskRunner.compute_next_run_time(schedule, timezone) 使用croniter计算下次运行时间，支持时区（pytz）

F-166: TaskRunner.process_queue() 循环处理队列：peek最早任务 → 检查Cache中的任务是否仍有效（active且next_run_time未变）→ 计算时间差 → 到期则create_job并计算下次运行时间重新入队 → 未到期则break

F-167: TaskRunner.create_job(job_definition_id) 从staging读取input_uri，调用scheduler.create_job创建作业实例

F-168: TaskRunner.start() 是async方法：populate_cache() → 无限循环 process_queue() → await asyncio.sleep(poll_interval)

F-169: TaskRunner.add_job_definition() 在创建新定时作业定义时调用，计算next_run_time并加入Cache和Queue

F-170: TaskRunner.update_job_definition() 在更新作业定义时调用，若next_run_time变化或重新激活则推入新任务到队列

F-171: TaskRunner.delete_job_definition() 仅从Cache删除（Queue中的过期任务在process_queue时自动跳过）

## F-172 ~ F-190: 其他核心模块

F-172: `EnvironmentManager`（ABC）定义于 `environments.py`，抽象方法：list_environments()、manage_environments_command()、output_formats_mapping()

F-173: `CondaEnvironmentManager` 是默认环境管理器，通过 `conda env list --json` 获取Conda环境列表；Conda不可用时返回当前Python环境（sys.prefix/sys.executable）；每个环境file_extensions=["ipynb"]，output_formats=["ipynb","html"]

F-174: CondaEnvironmentManager.output_formats_mapping() 返回：ipynb→Notebook、html→HTML、stdout→Output、stderr→Errors、json→JSON

F-175: `StaticEnvironmentManager` 提供静态环境列表（仅demo用），返回名为"jupyterlab-env"的虚拟环境

F-176: `EnvironmentRetrievalError` 异常类定义于 environments.py

F-177: `JobFilesManager` 定义于 `job_files_manager.py`，管理从staging下载文件到本地输出目录，接收backend_registry用于路由

F-178: JobFilesManager.copy_from_staging(job_id, redownload=False) 通过multiprocessing Process启动Downloader执行下载（避免阻塞事件循环）

F-179: `Downloader` 类执行实际文件复制：支持tar/tar.gz归档解压（优先）或逐文件复制；支持redownload强制覆盖；package_input_folder时复制附带文件

F-180: Downloader.download_tar() 使用fsspec打开归档文件，tarfile解压到output_dir，Python 3.12+使用extraction_filter（no-op lambda）安全过滤

F-181: Downloader.generate_filepaths() 生成需要复制的文件路径对（staging→output），跳过已存在文件（除非redownload=True）

F-182: `add_parameters(nb, parameters)` 定义于 `parameterize.py`，向notebook注入参数代码单元（tag为"injected-parameters"），插入位置：已有injected-parameters单元替换 → 有parameters单元则插入其后 → 否则插入到最前面

F-183: `make_job_id(backend_id, uuid)` 返回 `f"{backend_id}:{uuid}"`；`parse_job_id(job_id)` 返回 (backend_id, uuid) 元组，无冒号时backend_id为None

F-184: `resolve_scheduler(job_id, backend_registry)` 解析job_id获取对应scheduler：无backend_id（legacy格式）返回legacy后端scheduler，否则返回对应后端scheduler，后端不存在抛ValueError

F-185: 工具函数（utils.py）：`get_utc_timestamp()` 返回UTC毫秒时间戳；`compute_next_run_time(schedule, timezone)` 使用croniter计算下次运行时间；`get_localized_timestamp(timezone)` 返回指定时区的毫秒时间戳；`create_output_directory(input_filename, job_id)` 返回 `{basefilename}-{job_id}`；`create_output_filename(input_filename, create_time, output_format)` 返回 `{basefilename}-{timestamp}.{format}`；`find_cell_index_with_tag(nb, tag)` 查找第一个带指定tag的cell索引；`copy_directory(source_dir, dest_dir, exclude_files)` 递归复制目录返回复制文件列表；`UUIDEncoder` 处理UUID JSON序列化

F-186: 时间戳使用毫秒级Unix时间戳（UTC），croniter返回的是秒级float需要×1000

F-187: `exceptions.py` 定义三个异常类：`SchedulerError`、`IdempotencyTokenError`、`InputUriError`

F-188: 前端三个JupyterFrontEndPlugin：主插件`@jupyterlab/scheduler:plugin`（requires: IFileBrowserFactory, INotebookTracker, ITranslator, ILayoutRestorer, IAdvancedOptions, TelemetryHandler; optional: ILauncher）、IAdvancedOptions插件（提供AdvancedOptions React组件）、TelemetryHandler插件（默认noop遥测处理器）

F-189: 前端命令ID：scheduling:delete-job、scheduling:create-from-filebrowser、scheduling:create-from-notebook、scheduling:restore-layout、scheduling:stop-job、scheduling:download-files、scheduling:list-jobs-from-launcher

F-190: 前端动态上下文菜单：启动时立即注册notebook类型的右键菜单（竞态条件保护），然后异步获取backends列表按文件类型更新菜单注册（使用DisposableSet管理菜单生命周期）
