# 数据模型

Jupyter Scheduler 使用 Pydantic v1 兼容层定义请求/响应数据模型，使用 SQLAlchemy ORM 定义数据库表结构。两者分离但字段对齐。

## Pydantic 模型（API层）

定义于 `models.py`，用于 HTTP 请求验证和响应序列化。

### 枚举类型

**Status**：作业状态枚举
- CREATED、QUEUED、IN_PROGRESS、COMPLETED、FAILED、STOPPING、STOPPED

**SortDirection**：排序方向
- asc、desc

### 请求模型

| 模型 | 用途 | 关键字段 |
|-----|------|---------|
| CreateJob | 创建作业请求 | input_uri, output_formats, parameters, idempotency_token, name, tags, runtime_environment_name, backend_id, package_input_folder |
| UpdateJob | 更新作业请求 | status(仅STOPPED)、其他可选字段 |
| CreateJobDefinition | 创建作业定义 | 同CreateJob + schedule, timezone, active（无idempotency_token） |
| UpdateJobDefinition | 更新作业定义 | 所有字段可选 |
| CreateJobFromDefinition | 从定义创建作业 | parameters(覆盖) |
| ListJobsQuery | 查询作业列表 | job_definition_id, status, name, start_time, tags, sort_by, max_items, next_token |
| ListJobDefinitionsQuery | 查询定义列表 | name, create_time, tags, sort_by, max_items, next_token |
| CountJobsQuery | 统计作业数 | status(默认IN_PROGRESS) |

### 响应模型

| 模型 | 用途 | 关键字段 |
|-----|------|---------|
| DescribeJob | 作业详情 | 继承CreateJob字段 + job_id, status, create_time, update_time, start_time, end_time, url, job_files, downloaded, packaged_files, backend_id |
| DescribeJobDefinition | 定义详情 | 继承CreateJob字段 + job_definition_id, schedule, timezone, active, url, backend_id |
| ListJobsResponse | 作业列表 | jobs: List[DescribeJob], total_count, next_token |
| ListJobDefinitionsResponse | 定义列表 | job_definitions: List[DescribeJobDefinition], total_count, next_token |
| JobFile | 文件描述 | display_name, file_format, file_path |
| OutputFormat | 输出格式 | id(小写), label(显示名) |
| RuntimeEnvironment | 运行时环境 | name, label, description, file_extensions, output_formats, metadata |
| EmailNotifications | 邮件通知 | on_start, on_success, on_failure（收件人列表） |
| BackendConfig/DescribeBackend | 后端描述 | id, name, description, file_extensions, output_formats, metadata |

### 自动填充字段

**input_filename**：root_validator 自动从 input_uri 提取文件名

```python
@root_validator(skip_on_failure=True)
def populate(cls, values):
    input_uri = values.get("input_uri")
    if input_uri:
        values["input_filename"] = os.path.basename(input_uri)
    return values
```

### 常量

- `OUTPUT_FILENAME_TEMPLATE = "{{input_filename}}-{{create_time}}"`：默认输出文件名模板
- `DEFAULT_SORT = SortField(name="create_time", direction=SortDirection.desc)`：默认按创建时间降序
- `DEFAULT_MAX_ITEMS = 1000`：默认分页大小

## SQLAlchemy ORM 模型（存储层）

定义于 `orm.py`，映射到数据库表。

### 表结构

**jobs 表**：

| 列 | 类型 | 默认值 | 说明 |
|----|------|-------|------|
| job_id | VARCHAR(128) PK | generate_uuid() | 作业ID |
| job_definition_id | VARCHAR(36) | - | 关联作业定义ID |
| status | VARCHAR(64) | STOPPED | 当前状态 |
| status_message | VARCHAR(1024) | - | 状态/错误消息 |
| start_time | BIGINT | - | 开始时间(ms) |
| end_time | BIGINT | - | 结束时间(ms) |
| url | VARCHAR(256) | generate_jobs_url | 前端路径 |
| pid | INTEGER | - | 子进程ID |
| idempotency_token | VARCHAR(256) | - | 幂等性令牌 |
| backend_id | VARCHAR(64) | - | 后端ID |

**job_definitions 表**：

| 列 | 类型 | 默认值 | 说明 |
|----|------|-------|------|
| job_definition_id | VARCHAR(36) PK | generate_uuid() | 定义ID |
| schedule | VARCHAR(256) | - | cron表达式 |
| timezone | VARCHAR(36) | - | 时区IANA名 |
| url | VARCHAR(256) | generate_job_definitions_url | 前端路径 |
| active | BOOLEAN | True | 是否激活 |
| backend_id | VARCHAR(64) | - | 后端ID |

两表共享 CommonColumns mixin：runtime_environment_name、input_filename、output_formats、name、tags、parameters、email_notifications、timeout_seconds、retry_on_timeout、max_retries、create_time、update_time、package_input_folder、packaged_files等。

### 自定义类型

- **JsonType**：Python对象↔JSON字符串互转，存储为VARCHAR
- **EmailNotificationType**：EmailNotifications pydantic模型↔JSON字符串互转

## Pydantic v1/v2 兼容

`jupyter_scheduler/pydantic_v1/` 目录提供版本兼容层：
- 检测安装的 pydantic 版本
- v1：直接从 pydantic 导出
- v2：从 pydantic.v1 导出
- 同时兼容 dataclasses

这确保了代码在 pydantic v1 和 v2 环境下都能正常运行。
