---
source: jupyter_scheduler/backend_registry.py, jupyter_scheduler/backends.py, jupyter_scheduler/base_backend.py, jupyter_scheduler/backend_utils.py
title: 后端注册体系源码解析
---

# 后端注册体系源码解析

> 信源路径：`backend_registry.py`（165行）、`backends.py`（72行）、`base_backend.py`（32行）、`backend_utils.py`（70行）

## BaseBackend 基类

定义于 `base_backend.py`，使用 ClassVar 声明后端能力：

```python
class BaseBackend:
    id: ClassVar[str]                           # 唯一标识（不能含冒号）
    name: ClassVar[str]                         # 显示名称
    description: ClassVar[str] = ""             # 描述
    scheduler_class: ClassVar[str]              # 调度器类完全限定路径
    execution_manager_class: ClassVar[str]      # 执行管理器类完全限定路径
    database_manager_class: ClassVar[Optional[str]] = None  # 可选自定义数据库
    file_extensions: ClassVar[List[str]] = []   # 支持的文件扩展名
    output_formats: ClassVar[List[OutputFormat]] = []       # 支持的输出格式
```

`to_dict()` 类方法将属性转为字典，用于创建 BackendConfig。

## 内置后端

### JupyterServerNotebookBackend

| 属性 | 值 |
|-----|---|
| id | `"jupyter_server_nb"` |
| name | `"Jupyter Server Notebook"` |
| scheduler_class | `"jupyter_scheduler.scheduler.Scheduler"` |
| execution_manager_class | `"jupyter_scheduler.executors.DefaultExecutionManager"` |
| file_extensions | `["ipynb"]` |
| output_formats | ipynb(Notebook), html(HTML) |

### JupyterServerPythonBackend

| 属性 | 值 |
|-----|---|
| id | `"jupyter_server_py"` |
| name | `"Jupyter Server Python"` |
| scheduler_class | `"jupyter_scheduler.scheduler.Scheduler"` |
| execution_manager_class | `"jupyter_scheduler.python_executor.PythonScriptExecutionManager"` |
| file_extensions | `["py"]` |
| output_formats | stdout(Output), stderr(Errors), json(JSON) |

## BackendConfig 运行时配置

pydantic模型，字段：id、name、description、scheduler_class、execution_manager_class、database_manager_class（Optional）、db_url（Optional，覆盖全局数据库）、file_extensions、output_formats（List[Dict[str,str]]）、metadata（Optional[Dict]）。

## BackendRegistry 注册中心

### 核心数据结构

```python
_backends: Dict[str, BackendInstance]     # backend_id → 运行实例
_legacy_job_backend: str                  # legacy作业后端ID
_preferred_backends: Dict[str, str]      # 文件扩展名 → 首选后端ID
_extension_map: Dict[str, List[str]]     # 文件扩展名 → 支持该扩展名的后端ID列表
```

### BackendInstance

```python
class BackendInstance(BaseModel):
    config: BackendConfig
    scheduler: Any  # BaseScheduler实例（Any用于测试mock）
```

### 初始化流程 initialize()

```
1. 验证后端ID唯一性（重复抛ValueError）
2. 验证ID不含冒号（抛ValueError）
3. 对每个BackendConfig：
   a. _create_backend(cfg, ...) → BackendInstance
   b. 注册到 _backends
   c. 为每个file_extension建立_extension_map映射
4. _create_backend内部：
   a. import_class(scheduler_class) 动态导入
   b. 确定db_url（cfg.db_url or global_db_url）
   c. 若使用默认SQLAlchemy存储（database_manager_class is None），create_tables
   d. 实例化scheduler
   e. 若有execution_manager_class，动态导入并设置到scheduler
```

### 路由方法

**get_backend(backend_id)**：精确查找，返回BackendInstance或None。

**get_legacy_job_backend()**：返回处理legacy作业的后端，ID不存在抛KeyError。

**get_for_file(input_uri)**：按文件扩展名自动选择：
1. 从input_uri提取扩展名
2. 查找_extension_map获取候选后端列表
3. 无候选抛ValueError
4. 优先返回_preferred_backends中配置的
5. 否则按名称字母序返回第一个

**describe_backends()**：按名称字母序返回所有后端的DescribeBackendResponse列表。

### import_class 工具函数

```python
def import_class(class_path: str) -> Type:
    module_path, class_name = class_path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)
```

## 后端发现 discover_backends()

通过 `importlib.metadata.entry_points()` 发现入口组 `jupyter_scheduler.backends` 中注册的所有后端：

1. 兼容新旧Python API（`eps.select(group=)` vs `eps.get(group, [])`）
2. 对每个entry point尝试ep.load()
3. ImportError时记录warning（缺少依赖），跳过
4. 检查backend_class.id属性，缺少则跳过
5. 返回 `Dict[backend_id, backend_class]`

## Legacy 后端选择 get_legacy_job_backend_id()

优先级：
1. 显式配置的 `legacy_job_backend` 参数
2. `DEFAULT_FALLBACK_BACKEND_ID`（`"jupyter_server_nb"`）
3. 均不可用时抛ValueError

## Job ID 路由工具（job_id.py）

**make_job_id(backend_id, uuid)**：返回 `f"{backend_id}:{uuid}"`

**parse_job_id(job_id)**：返回 `(backend_id, uuid)` 元组，无冒号时backend_id为None（legacy）

**resolve_scheduler(job_id, registry)**：
- legacy ID（无backend_id）→ 返回legacy后端scheduler
- 新式ID → 查找对应后端的scheduler
- 后端不存在 → 抛ValueError
