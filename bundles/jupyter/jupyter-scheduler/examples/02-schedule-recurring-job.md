# 创建定时调度作业

本示例展示如何创建基于 cron 表达式的定时作业（Job Definition），实现 Notebook 的周期性自动执行。

## cron 表达式格式

Jupyter Scheduler 使用标准的 5 字段 cron 表达式：

```
┌───────── 分钟 (0-59)
│ ┌─────── 小时 (0-23)
│ │ ┌───── 日期 (1-31)
│ │ │ ┌─── 月份 (1-12)
│ │ │ │ ┌─ 星期 (0-7, 0和7都是周日)
│ │ │ │ │
* * * * *
```

常用示例：

| 表达式 | 含义 |
|-------|------|
| `0 9 * * *` | 每天上午9点 |
| `0 9 * * 1-5` | 工作日（周一到周五）上午9点 |
| `0 */6 * * *` | 每6小时 |
| `30 8 1 * *` | 每月1号上午8:30 |
| `0 9 * * 0` | 每周日上午9点 |
| `*/5 * * * *` | 每5分钟 |

时区使用 IANA 时区名（如 `Asia/Shanghai`、`America/New_York`、`UTC`）。

## 创建定时作业

### 通过 REST API

```bash
curl -X POST http://localhost:8888/scheduler/job_definitions \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "reports/daily_report.ipynb",
    "name": "Daily Report",
    "runtime_environment_name": "python3",
    "output_formats": ["ipynb", "html"],
    "schedule": "0 9 * * *",
    "timezone": "Asia/Shanghai",
    "active": true,
    "tags": ["daily", "report"]
  }'
```

响应：
```json
{
  "job_definition_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### 通过 JupyterLab UI

1. 在文件浏览器中右键点击 Notebook → "Create Job Definition"
2. 填写作业名称
3. 在 "Schedule" 部分选择频率和时间
4. 选择时区
5. 勾选 "Active" 启用调度
6. 点击 "Create"

## 管理定时作业

### 列出所有定时作业

```bash
curl -H "Authorization: token $TOKEN" \
  http://localhost:8888/scheduler/job_definitions
```

### 暂停定时作业

```bash
curl -X PATCH \
  "http://localhost:8888/scheduler/job_definitions/$DEF_ID" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active": false}'
```

### 恢复定时作业

```bash
curl -X PATCH \
  "http://localhost:8888/scheduler/job_definitions/$DEF_ID" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active": true}'
```

### 修改调度时间

```bash
curl -X PATCH \
  "http://localhost:8888/scheduler/job_definitions/$DEF_ID" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"schedule": "0 8 * * *", "timezone": "Asia/Shanghai"}'
```

### 手动触发一次执行

不等 cron 触发时间，立即执行一次：

```bash
curl -X POST \
  "http://localhost:8888/scheduler/job_definitions/$DEF_ID/jobs" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

也可以在手动触发时覆盖参数：
```bash
curl -X POST \
  "http://localhost:8888/scheduler/job_definitions/$DEF_ID/jobs" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"date": "2024-01-15"}}'
```

### 删除定时作业

```bash
curl -X DELETE \
  "http://localhost:8888/scheduler/job_definitions/$DEF_ID" \
  -H "Authorization: token $TOKEN"
```

删除定时作业不会删除已经由它创建的历史作业实例。

## 查看定时作业产生的作业

创建的每个作业实例都带有 `job_definition_id` 字段，可以通过过滤查询：

```bash
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs?job_definition_id=$DEF_ID"
```

## 带参数的定时作业

Notebook 中可以定义参数，定时执行时自动注入：

1. 在 Notebook 中添加一个 cell，标记 tag 为 `parameters`
2. 在 cell 中定义参数默认值：
```python
# parameters
date = "2024-01-01"
region = "us-east-1"
```

创建定时作业时指定参数值：
```bash
curl -X POST http://localhost:8888/scheduler/job_definitions \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "reports/daily_report.ipynb",
    "name": "Daily Report",
    "runtime_environment_name": "python3",
    "output_formats": ["ipynb", "html"],
    "schedule": "0 9 * * *",
    "timezone": "Asia/Shanghai",
    "parameters": {"region": "ap-southeast-1"},
    "active": true
  }'
```

执行时，参数 cell 会被新的 cell 覆盖（在其后插入一个包含实际参数值的 cell），Notebook 使用注入的参数值执行。

## 注意事项

1. **Jupyter Server 必须持续运行**：定时调度依赖 TaskRunner 在服务器进程中轮询，服务器关闭时不会触发作业
2. **精度限制**：默认轮询间隔为 10 秒，cron 时间精度为分钟级
3. **错过的作业不补执行**：服务器重启期间错过的执行时间不会被补偿
4. **active 控制**：设置 active=false 暂停调度但保留定义，恢复后继续按 schedule 执行
5. **时区**：务必正确设置 timezone，否则执行时间可能与预期不符
