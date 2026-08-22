---
source: jupyter_scheduler/executors.py
title: ExecutionManager 执行管理器源码解析
---

# ExecutionManager 执行管理器源码解析

> 信源路径：`jupyter_scheduler/executors.py`（265行）

## 类继承体系

```
ExecutionManager (ABC)
├── DefaultExecutionManager        (Notebook执行)
│   └── ArchivingExecutionManager  (归档执行)
└── PythonScriptExecutionManager   (Python脚本执行，定义于python_executor.py)
```

## ExecutionManager 抽象基类

### 模板方法设计模式

`process()` 是不可重写的模板方法，定义执行骨架：

```python
def process(self):
    self.before_start()        # 1. 标记开始
    try:
        self.execute()         # 2. 子类实现具体执行
    except CellExecutionError:
        self.on_failure(e)     # 3a. 失败处理
    except Exception:
        self.on_failure(e)
    else:
        self.on_complete()     # 3b. 成功处理
```

### 生命周期钩子

| 方法 | 作用 | 数据库更新 |
|-----|------|----------|
| `before_start()` | 执行前准备 | status=IN_PROGRESS, start_time=now |
| `execute()` | 具体执行逻辑（抽象） | - |
| `on_failure(e)` | 异常处理 | status=FAILED, status_message=str(e) |
| `on_complete()` | 成功处理 | status=COMPLETED, end_time=now |

### 构造参数

```python
def __init__(self, job_id: str, root_dir: str, db_url: str, staging_paths: Dict[str, str]):
```

- job_id：作业标识符
- root_dir：Jupyter服务器根目录
- db_url：数据库连接URL（子进程独立连接数据库）
- staging_paths：输出文件staging路径字典

### 懒加载属性

- `model`：从数据库查询Job构造DescribeJob（首次访问时加载）
- `db_session`：创建SQLAlchemy session工厂

## DefaultExecutionManager

使用nbconvert的ExecutePreprocessor执行Jupyter Notebook。

### execute() 流程

```
1. 读取staging中的input notebook（nbformat.read, as_version=4）
2. 若有parameters，调用add_parameters()注入参数cell
3. 创建ExecutePreprocessor
   - kernel_name: 从nb.metadata.kernelspec["name"]获取
   - store_widget_state: True
   - cwd: staging目录
4. ep.preprocess(nb, {"metadata": {"path": staging_dir}})
5. finally:
   a. add_side_effects_files(staging_dir)  # 捕获副作用文件
   b. create_output_files(job, nb)        # 生成各格式输出
```

### add_side_effects_files(staging_dir)

递归扫描staging目录，将输入notebook以外的所有新文件路径记录到packaged_files字段。用于捕获notebook执行过程中创建的数据文件、图表等。

### create_output_files(job, notebook_node)

对每个output_format使用 `nbconvert.get_exporter(output_format)` 获取导出器，导出后通过fsspec写入staging路径。支持nbconvert支持的所有格式（ipynb、html、pdf、markdown等）。

### supported_features()

```python
{
    job_name: True,
    output_formats: True,
    job_definition: False,
    idempotency_token: False,
    tags: False,
    email_notifications: False,
    timeout_seconds: False,
    retry_on_timeout: False,
    max_retries: False,
    min_retry_interval_millis: False,
    output_filename_template: False,
    stop_job: True,
    delete_job: True,
}
```

### validate(input_path)

检查notebook是否有kernelspec.name元数据，没有返回False。

## ArchivingExecutionManager

继承DefaultExecutionManager，将所有输出打包为tar.gz归档：

1. 在staging下创建 `files/` 子目录作为执行工作目录
2. 执行notebook（cwd=files/）
3. 生成各格式输出文件
4. 将staging目录下所有文件打包为tar.gz（扁平化目录结构）
5. 清理files/子目录

需配合 ArchivingScheduler 使用。
