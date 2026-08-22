# 自定义后端开发指南

通过扩展 BaseBackend 类，可以为 Jupyter Scheduler 添加自定义执行后端，将作业调度到远程集群、云服务或其他计算平台。

## 开发步骤总览

```
1. 定义 Backend 类（继承 BaseBackend）
2. （可选）定义自定义 Scheduler 类（继承 BaseScheduler）
3. （可选）定义自定义 ExecutionManager 类（继承 ExecutionManager）
4. 注册 entry point
5. 安装并测试
```

## Step 1: 定义 Backend 类

创建后端声明类，通过 ClassVar 声明能力：

```python
# my_package/backends.py
from jupyter_scheduler.base_backend import BaseBackend

class MyRemoteBackend(BaseBackend):
    id = "my_remote"
    name = "My Remote Compute"
    description = "Execute jobs on my remote cluster"
    scheduler_class = "my_package.scheduler.MyRemoteScheduler"
    execution_manager_class = "my_package.executors.MyRemoteExecutor"
    database_manager_class = None  # 使用默认SQLAlchemy
    file_extensions = ["ipynb", "py"]
    output_formats = [
        {"id": "ipynb", "label": "Notebook"},
        {"id": "html", "label": "HTML"},
        {"id": "pdf", "label": "PDF"},
    ]
```

### 关键约束

- `id` 必须全局唯一，不能包含冒号（`:`）
- `scheduler_class` 和 `execution_manager_class` 使用完全限定路径（字符串）
- 如果不需要自定义 Scheduler，可复用 `"jupyter_scheduler.scheduler.Scheduler"`

## Step 2: 定义自定义 Scheduler（可选）

如果需要自定义作业调度逻辑（如提交到远程API、轮询远程状态等），继承 BaseScheduler：

```python
# my_package/scheduler.py
from jupyter_scheduler.scheduler import BaseScheduler, Scheduler
from jupyter_scheduler.models import CreateJob, DescribeJob, Status
from jupyter_scheduler.utils import get_utc_timestamp

class MyRemoteScheduler(Scheduler):
    """远程调度器，提交作业到远程计算平台"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.remote_client = None  # 初始化远程客户端
        # 远程后端通常不需要本地TaskRunner（远程平台自己调度）
        self.task_runner = None
    
    def create_job(self, job):
        """提交作业到远程平台"""
        # 1. 生成job_id（自动带backend_id前缀）
        job_id = self._generate_job_id()
        
        # 2. 创建数据库记录
        db_job = Job(
            job_id=job_id,
            input_filename=job.input_filename,
            name=job.name,
            status=Status.QUEUED,  # 等待远程执行
            backend_id=self.backend_id,
            # ... 其他字段
        )
        self._session.add(db_job)
        self._session.commit()
        
        # 3. 上传输入文件到远程存储（如S3）
        self._upload_input(job_id, job.input_uri)
        
        # 4. 提交作业到远程API
        remote_job_id = self.remote_client.submit(job_id, ...)
        
        # 5. 存储远程作业ID映射
        db_job.remote_job_id = remote_job_id
        self._session.commit()
        
        return job_id
    
    def get_job(self, job_id):
        """查询作业状态，从远程平台同步"""
        db_job = self._get_db_job(job_id)
        
        # 同步远程状态
        if db_job.status in (Status.QUEUED, Status.IN_PROGRESS):
            remote_status = self.remote_client.get_status(db_job.remote_job_id)
            new_status = self._map_remote_status(remote_status)
            if new_status != db_job.status:
                db_job.status = new_status
                if new_status == Status.COMPLETED:
                    # 下载输出文件到staging
                    self._download_outputs(job_id)
                self._session.commit()
        
        return self._to_describe_job(db_job)
    
    def stop_job(self, job_id):
        """取消远程作业"""
        db_job = self._get_db_job(job_id)
        self.remote_client.cancel(db_job.remote_job_id)
        db_job.status = Status.STOPPED
        db_job.end_time = get_utc_timestamp()
        self._session.commit()
    
    def list_jobs(self, query=None):
        """列出作业，支持分页"""
        # 实现本地数据库查询+远程状态同步
        ...
    
    def delete_job(self, job_id):
        """删除作业（停止+清理staging+删除记录）"""
        if self._is_running(job_id):
            self.stop_job(job_id)
        self._cleanup_staging(job_id)
        # 删除数据库记录
        ...
    
    # 必须实现的抽象方法
    def update_job(self, job_id, job): ...
    def count_jobs(self, query=None): ...
    def create_job_definition(self, job_definition): ...
    def update_job_definition(self, job_definition_id, job_definition): ...
    def delete_job_definition(self, job_definition_id): ...
    def get_job_definition(self, job_definition_id): ...
    def list_job_definitions(self, query=None): ...
    def create_job_from_definition(self, job_definition_id, parameters=None): ...
    def get_staging_paths(self, model): ...
```

### 复用默认 Scheduler

如果只是自定义执行逻辑（如在同一机器上用不同方式执行），可以直接使用默认 Scheduler 类，只需自定义 ExecutionManager：

```python
class MyBackend(BaseBackend):
    id = "my_backend"
    scheduler_class = "jupyter_scheduler.scheduler.Scheduler"  # 复用默认
    execution_manager_class = "my_package.executors.MyExecutor"
```

## Step 3: 定义自定义 ExecutionManager

继承 ExecutionManager 或其子类，实现 execute() 方法：

```python
# my_package/executors.py
from jupyter_scheduler.executors import ExecutionManager, DefaultExecutionManager

class MyRemoteExecutor(ExecutionManager):
    """远程执行管理器（子进程中运行）"""
    
    def execute(self):
        """提交到远程并等待完成"""
        # 子进程中可以使用长时间运行的轮询
        job = self.model
        
        # 1. 上传输入到远程（如需要）
        # 2. 提交执行
        # 3. 轮询状态
        # 4. 下载输出到staging_paths
        
        # 注意：子进程独立连接数据库
        # self.db_session 可用于更新状态
        # self.staging_paths 包含各输出格式的staging路径
```

或者更简单地继承 DefaultExecutionManager 复用 nbconvert 执行：

```python
class MyCustomExecutor(DefaultExecutionManager):
    def execute(self):
        # 自定义前置处理
        self._setup_environment()
        super().execute()  # 使用默认nbconvert执行
        # 自定义后置处理
        self._post_process()
```

### supported_features

每个 ExecutionManager 必须声明支持的功能特性：

```python
@staticmethod
def supported_features():
    return {
        "job_name": True,
        "parameters": True,
        "output_formats": True,
        "job_definition": True,
        "idempotency_token": False,
        "tags": True,
        "email_notifications": False,
        "timeout_seconds": True,
        "retry_on_timeout": False,
        "max_retries": False,
        "min_retry_interval_millis": False,
        "output_filename_template": True,
        "stop_job": True,
        "delete_job": True,
    }
```

前端根据此字典决定显示哪些UI控件。

### validate 静态方法

```python
@staticmethod
def validate(input_path):
    """检查输入文件是否可被此后端执行"""
    # 检查文件格式、内核等
    return True  # 或 False
```

## Step 4: 注册 Entry Point

在 `pyproject.toml` 中注册 entry point：

```toml
[project.entry-points."jupyter_scheduler.backends"]
my_remote = "my_package.backends:MyRemoteBackend"
```

多个后端可注册多个 entry point：

```toml
[project.entry-points."jupyter_scheduler.backends"]
my_remote = "my_package.backends:MyRemoteBackend"
my_local = "my_package.backends:MyLocalBackend"
```

## Step 5: 安装并测试

```bash
pip install -e my_package/
jupyter lab  # 启动JupyterLab
```

启动日志应显示后端已加载：
```
Initialized 3 backend(s): ['jupyter_server_nb', 'jupyter_server_py', 'my_remote']
```

## 前端集成

自定义后端在前端自动可用：
- 创建作业对话框的"Environment"下拉框中显示后端名称
- BackendsHandler API 返回后端描述
- 前端通过 `@jupyterlab/scheduler` 包的 token（`IAdvancedOptions`、`TelemetryHandler`）可扩展高级选项面板

### 前端 Token 扩展

前端通过 Lumino Token 注入依赖：

```typescript
// 自定义高级选项组件
const advancedOptionsPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension/advanced-options',
  autoStart: true,
  requires: [IAdvancedOptions],
  activate: (app: JupyterFrontEnd, advancedOptions: IAdvancedOptions) => {
    // 注册自定义选项组件
    advancedOptions.addComponent({
      component: MyOptionsComponent,
      isEnabled: (jobdef) => jobdef.backendId === 'my_remote'
    });
  }
};
```

## 配置自定义后端

安装后可通过 Jupyter 配置系统配置后端：

```python
# jupyter_server_config.py
c.SchedulerApp.preferred_backends = {
    "ipynb": "my_remote",  # .ipynb文件默认使用远程后端
}
c.SchedulerApp.backend_config = {
    "my_remote": {
        "db_url": "postgresql://user:pass@dbhost/scheduler",  # 独立数据库
        "metadata": {"api_endpoint": "https://my-cluster.example.com"}
    }
}
```

## 参考实现

Jupyter Scheduler 官方维护了一个参考实现：[jupyter-scheduler-remote](https://github.com/jupyter-server/jupyter-scheduler)（在同一仓库的示例中），展示了如何将作业提交到远程执行环境。

内置后端也是很好的参考：
- [JupyterServerNotebookBackend](../references/backend-registry-source.md) - 最简实现，直接复用默认Scheduler和DefaultExecutionManager
- [ArchivingScheduler](../references/scheduler-source.md) - 继承Scheduler扩展功能
