# 后端注册体系

Jupyter Scheduler 的核心设计之一是**可插拔后端架构**。通过 Python entry points 机制，第三方包可以注册自定义执行后端，无需修改核心代码即可扩展支持新的执行环境（如 Kubernetes、AWS Braket、Dask 集群等）。

## BaseBackend 基类

所有后端必须继承 `BaseBackend`，通过类变量（ClassVar）声明能力：

```python
from jupyter_scheduler.base_backend import BaseBackend

class MyBackend(BaseBackend):
    id = "my_backend"                           # 唯一标识（不能含冒号）
    name = "My Custom Backend"                  # 显示名称
    description = "Execute jobs on my platform" # 描述
    scheduler_class = "my_package.scheduler.MyScheduler"      # 调度器类
    execution_manager_class = "my_package.executors.MyExecutor" # 执行器类
    database_manager_class = None               # 可选，自定义数据库管理
    file_extensions = ["ipynb", "py"]           # 支持的文件扩展名
    output_formats = [                          # 支持的输出格式
        {"id": "ipynb", "label": "Notebook"},
        {"id": "html", "label": "HTML"},
    ]
```

### 类属性说明

| 属性 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `id` | str | ✓ | 后端唯一标识符，用于Job ID前缀和路由。不能包含冒号（`:`） |
| `name` | str | ✓ | 用户可见的显示名称，前端下拉选择时展示 |
| `description` | str | - | 后端描述文本 |
| `scheduler_class` | str | ✓ | 调度器类的完全限定路径（如 `"module.ClassName"`） |
| `execution_manager_class` | str | ✓ | 执行管理器类的完全限定路径 |
| `database_manager_class` | str | - | 自定义数据库管理器类路径，None时使用默认SQLAlchemy |
| `file_extensions` | List[str] | - | 支持的输入文件扩展名（如 `["ipynb"]`） |
| `output_formats` | List[Dict] | - | 支持的输出格式，每项含 `id`、`label`、`description` |

## 内置后端

### JupyterServerNotebookBackend

- **ID**：`jupyter_server_nb`
- **文件类型**：`.ipynb`（Jupyter Notebook）
- **调度器**：`jupyter_scheduler.scheduler.Scheduler`
- **执行器**：`jupyter_scheduler.executors.DefaultExecutionManager`
- **输出格式**：Notebook（.ipynb）、HTML（.html）
- **执行方式**：在 Jupyter Server 本地使用 nbconvert ExecutePreprocessor 执行

### JupyterServerPythonBackend

- **ID**：`jupyter_server_py`
- **文件类型**：`.py`（Python 脚本）
- **调度器**：`jupyter_scheduler.scheduler.Scheduler`
- **执行器**：`jupyter_scheduler.python_executor.PythonScriptExecutionManager`
- **输出格式**：标准输出（stdout）、错误输出（stderr）、JSON结果
- **执行方式**：在 Jupyter Server 本地使用 subprocess.run 执行脚本

## BackendRegistry 注册中心

`BackendRegistry` 负责管理所有已发现后端的生命周期和路由：

### 初始化

在 SchedulerApp.initialize_settings() 中创建：

```python
registry = BackendRegistry(backend_configs, default_id, preferred_backends)
registry.initialize(
    root_dir=self.serverapp.root_dir,
    environments_manager=environments_manager,
    db_url=self.db_url,
    config=self.config,
)
```

initialize() 执行以下操作：
1. 验证后端ID唯一性和格式（不含冒号）
2. 对每个 BackendConfig：
   - 动态 import scheduler_class
   - 确定数据库URL（per-backend覆盖或全局db_url）
   - 若使用默认SQLAlchemy存储，调用 `create_tables()` 自动建表/迁移
   - 实例化 Scheduler
   - 设置 execution_manager_class
   - 注册到 `_backends` 字典
   - 建立扩展名→后端ID映射

### 路由方法

| 方法 | 用途 |
|-----|------|
| `get_backend(backend_id)` | 精确查找后端实例 |
| `get_legacy_job_backend()` | 获取处理legacy作业的后端 |
| `get_for_file(input_uri)` | 按文件扩展名自动选择后端 |
| `describe_backends()` | 返回所有后端描述（按名称排序，用于前端展示） |

### 文件扩展名路由

当创建作业时未指定 `backend_id`，系统按以下规则自动选择后端：

1. 从 input_uri 提取文件扩展名（如 `.ipynb`）
2. 查找支持该扩展名的所有后端
3. 若 `preferred_backends` 配置了该扩展名的首选后端，使用它
4. 否则按后端名称字母序选择第一个

```python
# 配置示例：.ipynb 文件优先使用自定义后端
c.SchedulerApp.preferred_backends = {"ipynb": "my_custom_backend"}
```

## 后端发现机制

`discover_backends()` 通过 Python entry points 自动发现后端：

```python
eps = entry_points()
backend_eps = eps.select(group="jupyter_scheduler.backends")
for ep in backend_eps:
    backend_class = ep.load()
    backends[backend_class.id] = backend_class
```

第三方包在 `pyproject.toml` 中注册 entry point：

```toml
[project.entry-points."jupyter_scheduler.backends"]
my_backend = "my_package.backends:MyBackend"
```

后端加载失败时（ImportError等），记录warning并跳过，不影响其他后端和服务器启动。

## 每后端配置覆盖

通过 `SchedulerApp.backend_config` 可为特定后端覆盖配置：

```python
c.SchedulerApp.backend_config = {
    "my_backend": {
        "db_url": "postgresql://user:pass@host/db",  # 独立数据库
        "metadata": {"region": "us-west-2"}          # 自定义元数据
    }
}
```

支持的覆盖键：
- `db_url`：独立的数据库连接URL（默认共享全局db_url）
- `metadata`：自定义元数据字典

## 自定义后端开发

开发自定义后端需要：

1. 创建 `BaseBackend` 子类，声明能力属性
2. 创建自定义 `BaseScheduler` 子类（可选，若默认Scheduler不满足需求）
3. 创建自定义 `ExecutionManager` 子类，实现 `execute()` 方法
4. 在 pyproject.toml 中注册 entry point
5. 安装包后自动发现

参见：[自定义后端开发指南](12-custom-backend.md)
