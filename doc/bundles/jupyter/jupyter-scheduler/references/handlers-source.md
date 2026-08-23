---
source: jupyter_scheduler/handlers.py
title: HTTP Handlers 源码解析
---

# HTTP Handlers 源码解析

> 信源路径：`jupyter_scheduler/handlers.py`（531行）

## 类层次结构

```
APIHandler (jupyter_server)
└── ExtensionHandlerMixin + JobHandlersMixin + APIHandler
    ├── JobDefinitionHandler      (GET/POST/PATCH/DELETE)
    ├── JobHandler                (GET/POST/PATCH/DELETE)
    ├── JobFromDefinitionHandler  (POST)
    ├── BatchJobHandler           (DELETE)
    ├── JobsCountHandler          (GET)
    ├── RuntimeEnvironmentsHandler(GET)
    ├── FeaturesHandler           (GET)
    ├── ConfigHandler             (GET)
    ├── FilesDownloadHandler      (GET)
    └── BackendsHandler           (GET)
```

## JobHandlersMixin

所有Handler共享的Mixin，提供：

| 成员 | 说明 |
|-----|------|
| `scheduler` | 从settings懒加载legacy后端scheduler |
| `backend_registry` | 从settings懒加载BackendRegistry |
| `environments_manager` | 从settings懒加载环境管理器 |
| `get_scheduler(job_id)` | 根据job_id路由到正确后端的scheduler |
| `resolve_backend_for_job(payload)` | 根据payload的backend_id或文件扩展名选择后端 |
| `execution_manager_class` | 从scheduler获取执行管理器类 |

**get_scheduler**：调用 `resolve_scheduler(job_id, backend_registry)`，解析job_id中的backend_id，路由到对应后端；backend不可用时抛HTTPError(400)。

**resolve_backend_for_job**：优先使用payload中显式指定的backend_id（404找不到后端），否则按input_uri的文件扩展名自动选择（400无后端支持该扩展名）。

## compute_sort_model

解析sort_by查询参数：
```python
PATTERN = re.compile("^(asc|desc)?\(?([^\)]+)\)?", re.IGNORECASE)
```
支持格式：`name`（默认asc）、`asc(name)`、`desc(create_time)`。

## Handler 详细说明

### JobDefinitionHandler

| 方法 | 路径参数 | 功能 |
|-----|---------|------|
| GET | 无 | 列出作业定义（支持name/create_time/tags/sort_by/max_items/next_token过滤） |
| GET | job_definition_id | 获取单个作业定义详情 |
| POST | - | 创建作业定义（先resolve_backend_for_job选择后端） |
| PATCH | job_definition_id | 更新作业定义 |
| DELETE | job_definition_id | 删除作业定义 |

### JobHandler

| 方法 | 路径参数 | 功能 |
|-----|---------|------|
| GET | 无 | 列出作业（支持status/name/start_time/tags/job_definition_id过滤） |
| GET | job_id | 获取单个作业详情（路由到对应后端的scheduler） |
| POST | - | 创建作业（自动设置默认output_formats，返回job_id和backend_id） |
| PATCH | job_id | 更新作业（仅允许status设为STOPPED，调用stop_job） |
| DELETE | job_id | 删除作业 |

**GET列表特殊逻辑**：
1. 从legacy后端查询所有作业（共享数据库）
2. 为legacy作业填充backend_id
3. 对QUEUED/IN_PROGRESS状态的作业，通过对应后端的get_job同步状态（支持远程后端状态同步）
4. 同步失败仅记录warning，不阻断响应

**POST创建作业**：自动从后端配置填充output_formats（用户未指定时）。

**PATCH更新作业**：status非STOPPED时直接抛500错误。

### 其他Handler

- **JobFromDefinitionHandler**：POST从作业定义创建作业实例
- **BatchJobHandler**：DELETE批量删除（job_id查询参数可重复）
- **JobsCountHandler**：GET统计指定status的作业数（默认IN_PROGRESS）
- **RuntimeEnvironmentsHandler**：GET返回环境列表及输出格式映射
- **ConfigHandler**：GET返回supported_features和manage_environments_command
- **FilesDownloadHandler**：GET触发文件下载（支持redownload参数），通过子进程执行
- **BackendsHandler**：GET返回所有可用后端的描述信息（按名称排序）

## 异常处理映射

| 异常类型 | HTTP状态码 |
|---------|-----------|
| ValidationError (pydantic) | 400 |
| IdempotencyTokenError | 409 |
| InputUriError | 500 |
| SchedulerError | 500 |
| HTTPError | 原样抛出 |
| ValueError (后端不可用) | 400 |
| 其他Exception | 500 |

所有Handler使用 `@authenticated` 装饰器和 `ensure_async()` 包装异步调用。
