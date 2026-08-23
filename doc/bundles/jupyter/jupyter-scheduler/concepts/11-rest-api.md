# REST API 接口

Jupyter Scheduler 提供 RESTful HTTP API，所有端点前缀为 `/scheduler/`。

## 端点一览

### 作业（Jobs）

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/jobs` | 列出作业（支持过滤、排序、分页） |
| POST | `/jobs` | 创建作业 |
| GET | `/jobs/count` | 统计作业数 |
| GET | `/jobs/{job_id}` | 获取作业详情 |
| PATCH | `/jobs/{job_id}` | 更新作业（仅支持停止） |
| DELETE | `/jobs/{job_id}` | 删除作业 |
| GET | `/jobs/{job_id}/download_files` | 下载作业输出文件 |
| DELETE | `/batch/jobs` | 批量删除作业 |

### 作业定义（Job Definitions）

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/job_definitions` | 列出作业定义 |
| POST | `/job_definitions` | 创建作业定义（定时作业） |
| GET | `/job_definitions/{id}` | 获取定义详情 |
| PATCH | `/job_definitions/{id}` | 更新定义 |
| DELETE | `/job_definitions/{id}` | 删除定义 |
| POST | `/job_definitions/{id}/jobs` | 从定义创建作业实例 |

### 后端与配置

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/backends` | 列出可用后端 |
| GET | `/runtime_environments` | 列出运行时环境 |
| GET | `/config` | 获取功能配置 |

## 作业 API 详解

### POST /scheduler/jobs - 创建作业

请求体（CreateJob）：
```json
{
  "input_uri": "notebooks/my_analysis.ipynb",
  "name": "My Analysis Job",
  "runtime_environment_name": "python3",
  "output_formats": ["ipynb", "html"],
  "parameters": {"n_samples": "1000", "threshold": "0.5"},
  "tags": ["daily", "analysis"],
  "idempotency_token": "unique-token-123",
  "backend_id": "jupyter_server_nb",
  "package_input_folder": false
}
```

响应：
```json
{
  "job_id": "jupyter_server_nb:550e8400-e29b-41d4-a716-446655440000"
}
```

字段说明：
- `input_uri`（必填）：输入文件路径，相对 root_dir
- `name`（必填）：作业名称
- `runtime_environment_name`（必填）：运行时环境名称
- `output_formats`：输出格式列表（默认从后端配置获取）
- `parameters`：Notebook 参数字典（注入到parameters tagged cell）
- `tags`：标签列表
- `idempotency_token`：幂等性令牌，重复提交相同token返回409
- `backend_id`：后端ID（不指定则按文件扩展名自动选择）
- `package_input_folder`：是否打包整个输入文件夹

### GET /scheduler/jobs - 列出作业

查询参数：
- `status`：按状态过滤（CREATED/QUEUED/IN_PROGRESS/COMPLETED/FAILED/STOPPED）
- `job_definition_id`：按作业定义ID过滤
- `name`：按名称前缀过滤
- `start_time`：按开始时间过滤
- `tags`：按标签过滤（包含所有指定标签）
- `sort_by`：排序字段，格式 `field` 或 `asc(field)` / `desc(field)`
- `max_items`：每页条数（默认1000）
- `next_token`：分页偏移量

响应：
```json
{
  "jobs": [
    {
      "job_id": "jupyter_server_nb:xxx",
      "name": "My Job",
      "status": "COMPLETED",
      "input_filename": "analysis.ipynb",
      "create_time": 1703001234000,
      "start_time": 1703001235000,
      "end_time": 1703001300000,
      "job_files": [
        {"display_name": "analysis.ipynb", "file_format": "ipynb", "file_path": "jobs/My Job-xxx/analysis.ipynb"}
      ],
      "downloaded": true,
      "tags": ["daily"],
      "backend_id": "jupyter_server_nb"
    }
  ],
  "total_count": 42,
  "next_token": "1000"
}
```

**多后端状态同步**：列表查询时，对 QUEUED/IN_PROGRESS 状态的作业，会通过对应后端的 get_job() 同步最新状态，支持远程后端的状态更新。

### GET /scheduler/jobs/{job_id} - 获取作业详情

返回单个作业的完整 DescribeJob 对象。

### PATCH /scheduler/jobs/{job_id} - 停止作业

请求体：
```json
{
  "status": "STOPPED"
}
```
仅支持将 status 设为 STOPPED（停止作业），其他状态值返回 500。

### DELETE /scheduler/jobs/{job_id} - 删除作业

删除作业记录和 staging 文件。运行中的作业会先停止再删除。

### GET /scheduler/jobs/{job_id}/download_files - 下载文件

查询参数：
- `redownload`：是否强制重新下载（true/false，默认false）

响应：重定向到 JupyterLab 文件浏览器中的输出目录。

## 作业定义 API

### POST /scheduler/job_definitions - 创建定时作业

请求体（比CreateJob多schedule/timezone/active）：
```json
{
  "input_uri": "notebooks/daily_report.ipynb",
  "name": "Daily Report",
  "runtime_environment_name": "python3",
  "output_formats": ["ipynb", "html"],
  "schedule": "0 9 * * *",
  "timezone": "Asia/Shanghai",
  "active": true,
  "tags": ["daily"]
}
```

- `schedule`：cron 表达式（5字段：分 时 日 月 周）
- `timezone`：IANA 时区名（如 "Asia/Shanghai"、"America/New_York"）
- `active`：是否激活（false 则暂停调度）

### POST /scheduler/job_definitions/{id}/jobs - 手动触发

立即从作业定义创建一个作业实例（不等cron触发）。

请求体可包含 `parameters` 覆盖定义中的参数。

## 其他 API

### GET /scheduler/backends - 列出后端

```json
{
  "backends": [
    {
      "id": "jupyter_server_nb",
      "name": "Jupyter Server Notebook",
      "description": "Execute notebooks locally",
      "file_extensions": ["ipynb"],
      "output_formats": [
        {"id": "ipynb", "label": "Notebook"},
        {"id": "html", "label": "HTML"}
      ],
      "metadata": null
    },
    {
      "id": "jupyter_server_py",
      "name": "Jupyter Server Python",
      "description": "Execute Python scripts locally",
      "file_extensions": ["py"],
      "output_formats": [...]
    }
  ]
}
```

### GET /scheduler/runtime_environments - 列出环境

```json
{
  "environments": [
    {
      "name": "python3",
      "label": "Python 3",
      "description": "Python 3 environment",
      "file_extensions": ["ipynb"],
      "output_formats": [...]
    }
  ],
  "compute_types": []
}
```

### GET /scheduler/config - 功能配置

```json
{
  "supported_features": {...},
  "manage_environments_command": null
}
```

## 错误响应

| 状态码 | 场景 |
|-------|------|
| 400 | 请求参数验证失败、后端不可用、不支持的文件类型 |
| 401 | 未认证（@authenticated装饰器） |
| 404 | 作业/作业定义/后端不存在 |
| 409 | 幂等性冲突（相同idempotency_token已存在） |
| 500 | 服务器内部错误（SchedulerError、InputUriError等） |

错误响应格式：
```json
{
  "message": "Error description",
  "reason": "error_type"
}
```
