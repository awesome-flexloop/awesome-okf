# 执行管理器

ExecutionManager 负责在子进程中执行具体的作业逻辑（Notebook 或 Python 脚本），采用**模板方法模式**定义执行骨架。

## 类层次

```
ExecutionManager (ABC)
├── DefaultExecutionManager        # Notebook 执行（nbconvert）
│   └── ArchivingExecutionManager  # 归档执行（打包tar.gz）
└── PythonScriptExecutionManager   # Python 脚本执行（subprocess）
```

## 模板方法模式

`process()` 是不可被子类重写的模板方法，定义执行的标准骨架：

```python
def process(self):
    """Execute the notebook and update job status in database."""
    self.before_start()
    try:
        self.execute()
    except Exception as e:
        self.on_failure(e)
    else:
        self.on_complete()
```

子类只需实现 `execute()` 抽象方法，状态更新逻辑由基类统一处理。

## 生命周期钩子

### before_start()

```python
def before_start(self):
    job = self.db_job
    job.status = Status.IN_PROGRESS
    job.start_time = get_utc_timestamp()
    self.db_session.commit()
```

将作业状态设为 IN_PROGRESS 并记录开始时间。在子进程中独立运行，通过数据库连接更新状态。

### execute()（抽象方法）

子类必须实现。DefaultExecutionManager 使用 nbconvert 执行 Notebook，PythonScriptExecutionManager 使用 subprocess 执行 Python 脚本。

### on_failure(e)

```python
def on_failure(self, e):
    job = self.db_job
    job.status = Status.FAILED
    job.status_message = str(e)
    self.db_session.commit()
```

记录异常信息，状态设为 FAILED。CellExecutionError 和其他 Exception 均走此路径。

### on_complete()

```python
def on_complete(self):
    job = self.db_job
    job.status = Status.COMPLETED
    job.end_time = get_utc_timestamp()
    self.db_session.commit()
```

状态设为 COMPLETED 并记录结束时间。

## DefaultExecutionManager（Notebook 执行）

使用 `nbconvert.preprocessors.ExecutePreprocessor` 执行 Jupyter Notebook。

### execute() 流程

```
1. 读取staging中的input notebook
   nb = nbformat.read(input_path, as_version=4)

2. 参数注入（如有parameters）
   if self.model.parameters:
       add_parameters(nb, self.model.runtime_environment_name or "python3", self.model.parameters)

3. 创建ExecutePreprocessor
   ep = ExecutePreprocessor(
       kernel_name=nb.metadata.kernelspec["name"],
       store_widget_state=True,
   )

4. 执行notebook（cwd=staging目录）
   ep.preprocess(nb, {"metadata": {"path": staging_dir}})

5. 捕获副作用文件
   add_side_effects_files(staging_dir)

6. 生成各格式输出
   create_output_files(job, nb)
```

### 参数注入 add_parameters()

当 CreateJob 包含 `parameters` 字典时，向 Notebook 注入一个 tagged cell：

```python
def add_parameters(nb, kernel_name, parameters):
    # 查找已有的"parameters" tagged cell
    # 或在第一个cell后插入新的parameters cell
    # cell内容为: key = value 形式的Python赋值语句
    # 标记 tags=["parameters"]
```

这与 papermill 的参数化机制兼容，使用 cell tag `parameters` 标识注入位置。

### 副作用文件捕获 add_side_effects_files()

递归扫描 staging 目录，收集输入 notebook 以外的所有新创建文件路径：

```python
def add_side_effects_files(staging_dir):
    for root, dirs, files in os.walk(staging_dir):
        for file in files:
            if file != input_filename:
                packaged_files.append(relative_path)
    job.packaged_files = packaged_files
```

这些文件包括 Notebook 执行过程中保存的数据文件、图表、模型文件等。

### 输出文件生成 create_output_files()

对每个 output_format 使用 nbconvert 导出器生成输出：

```python
from nbconvert import get_exporter
for format in output_formats:
    exporter_class = get_exporter(format)
    exporter = exporter_class()
    output, _ = exporter.from_notebook_node(nb)
    with fsspec.open(staging_paths[format], "w") as f:
        f.write(output)
```

支持的格式取决于 nbconvert 安装的导出器（ipynb、html、pdf、markdown、latex 等）。

### supported_features()

返回后端支持的功能特性字典：

```python
{
    "job_name": True,
    "output_formats": True,
    "stop_job": True,
    "delete_job": True,
    # 其他均为False
}
```

前端据此显示/隐藏对应UI控件。

### validate(input_path)

静态检查 Notebook 是否包含 kernelspec.name 元数据：

```python
@staticmethod
def validate(input_path):
    nb = nbformat.read(input_path, as_version=4)
    return "kernelspec" in nb.metadata and "name" in nb.metadata.kernelspec
```

缺少 kernelspec 的 Notebook 在创建作业时被拒绝。

## PythonScriptExecutionManager

定义于 `python_executor.py`，使用 subprocess 执行 Python 脚本。

- 将 stdout/stderr 分别重定向到输出文件
- 支持 JSON 结果输出
- 输出格式：stdout、stderr、json

## ArchivingExecutionManager

继承 DefaultExecutionManager，将所有输出打包为 tar.gz：

1. 在 staging 下创建 `files/` 子目录作为执行 cwd
2. 执行 Notebook（输出在 files/ 中）
3. 生成各格式输出文件
4. 将 staging 目录所有内容打包为 tar.gz（扁平化目录）
5. 清理 files/ 子目录

需配合 ArchivingScheduler 使用（Scheduler 的子类，重写 get_staging_paths 添加 tar 路径）。

## 构造参数

```python
def __init__(self, job_id: str, root_dir: str, db_url: str, staging_paths: Dict[str, str]):
```

- **job_id**：作业ID（含 backend_id 前缀的格式）
- **root_dir**：Jupyter Server 根目录（用于路径解析）
- **db_url**：数据库连接URL（子进程独立创建数据库连接）
- **staging_paths**：各输出格式对应的staging文件路径字典

## 懒加载属性

- `model`：从数据库查询 Job 记录，构造 DescribeJob pydantic 模型
- `db_session`：创建 SQLAlchemy sessionmaker（每个子进程独立的session工厂）
- `db_job`：从数据库查询 ORM Job 对象（用于状态更新）
- `execution_dir_path`：staging 目录路径（输入文件所在目录）
