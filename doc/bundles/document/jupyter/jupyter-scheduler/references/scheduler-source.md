---
source: jupyter_scheduler/scheduler.py
title: Scheduler 调度器源码解析
---

# Scheduler 调度器源码解析

> 信源路径：`jupyter_scheduler/scheduler.py`（934行）

## 类继承体系

```
LoggingConfigurable
└── BaseScheduler (抽象基类)
    └── Scheduler (默认实现，SQLAlchemy持久化)
        ├── ArchivingScheduler (归档输出)
        └── SchedulerWithErrors (测试用，随机抛异常)
```

## BaseScheduler 抽象基类

### 核心配置项

| Trait | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `staging_path` | Unicode | `{jupyter_data_dir()}/scheduler_staging_area` | 作业输出暂存路径（支持fsspec远程路径） |
| `output_directory` | Unicode | `"jobs"` | 本地下载目录名（相对root_dir） |
| `execution_manager_class` | Type | DefaultExecutionManager | 执行管理器类 |
| `root_dir` | Unicode | - | Jupyter server根目录 |
| `environments_manager` | Instance | - | 环境管理器实例 |

### 抽象方法清单

BaseScheduler 定义 14 个抽象方法，涵盖作业和作业定义的完整 CRUD：

- **作业操作**：create_job、update_job、list_jobs、count_jobs、get_job、delete_job、stop_job
- **作业定义操作**：create_job_definition、update_job_definition、delete_job_definition、get_job_definition、list_job_definitions、create_job_from_definition
- **文件操作**：get_staging_paths

### 通用方法实现

BaseScheduler 提供以下通用方法（子类可复用）：

**file_exists(path) / dir_exists(path)**：路径遍历攻击防护
```python
root = os.path.abspath(self.root_dir)
os_path = to_os_path(path, root)
if not (os.path.abspath(os_path) + os.path.sep).startswith(root):
    return False  # 路径逃逸检测
```

**get_job_filenames(model)**：生成输出文件名映射
- 每个output_format：`{basefilename}-{timestamp}.{format}`
- input：原始文件名
- package_input_folder时：files键为附带文件列表

**add_job_files(model)**：填充model.job_files列表
- 检查每个输出文件是否存在于本地输出目录
- input文件始终添加（file_path可能为None）
- 设置downloaded标志（所有job_file.file_path非空且文件存在）

**get_local_output_path(model, root_dir_relative=False)**：返回本地输出目录
- 目录名格式：`{basefilename}-{job_id}`

## Scheduler 默认实现

### 额外配置

| Trait | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `task_runner_class` | Type | TaskRunner | 定时任务运行器类 |
| `db_url` | Unicode | - | 数据库连接URL |
| `task_runner` | Instance | None | TaskRunner实例 |

### 构造函数

接收 `root_dir`、`environments_manager`、`db_url`、`config`、`backend_id` 参数，懒加载 db_session。

### create_job 执行流程

```
1. 验证：input_uri存在（非job_definition触发时）
2. 验证：.ipynb文件必须有kernelspec（execution_manager_class.validate）
3. 幂等性检查：idempotency_token已存在则抛IdempotencyTokenError(409)
4. 生成job_id：backend_id:uuid格式（有backend_id时）或纯uuid
5. 创建Job ORM对象并commit
6. 复制输入文件/文件夹到staging
   - package_input_folder: copy_input_folder() 复制整个目录
   - 否则: copy_input_file() 仅复制输入文件
7. 使用spawn上下文创建子进程执行
   mp_ctx = mp.get_context("spawn")
   p = mp_ctx.Process(target=ExecutionManager(...).process)
   p.start()
8. 记录pid到数据库，commit
9. 返回job_id
```

**为什么使用spawn而非fork**：Python <3.12中fork进程的asyncio事件循环存在bug（cpython#66285），spawn创建全新解释器避免此问题。

### 其他关键方法

**stop_job(job_id)**：通过psutil遍历子进程树查找匹配pid，kill进程，更新状态为STOPPED。

**delete_job(job_id)**：运行中的作业先stop → 删除staging目录 → 删除数据库记录。

**list_jobs(query)**：支持多条件过滤（status/job_definition_id/start_time/name前缀/tags包含）、多字段排序、分页（max_items+next_token偏移量）。

**get_staging_paths(model)**：返回 `{staging_path}/{id}/` 下各格式文件的完整路径。

## ArchivingScheduler

继承Scheduler，重写get_staging_paths添加tar.gz归档路径，配合ArchivingExecutionManager将所有输出打包为tar.gz。

## SchedulerWithErrors

测试用类，所有CRUD方法以50%概率抛出SchedulerError，通过命令行启用：
```bash
jupyter lab --SchedulerApp.scheduler_class=jupyter_scheduler.scheduler.SchedulerWithErrors
```
