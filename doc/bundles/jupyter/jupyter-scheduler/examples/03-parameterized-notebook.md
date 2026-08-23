# 参数化 Notebook 执行

Jupyter Scheduler 支持向 Notebook 注入参数，实现同一份 Notebook 代码用不同参数值运行。这与 papermill 的参数化机制兼容。

## 参数 Cell 准备

### 添加 parameters tag

在 JupyterLab 中：

1. 选中要作为参数的 cell
2. 点击左侧边栏的属性检查器（齿轮图标）
3. 在 "Tags" 部分添加 `parameters` tag
4. 在 cell 中定义参数默认值

```python
# 这个cell的tag是"parameters"
# 默认参数值（在本地交互运行时使用）

start_date = "2024-01-01"
end_date = "2024-01-31"
region = "us-east-1"
n_samples = 1000
threshold = 0.5
model_type = "random_forest"
```

### 参数值类型

所有参数通过 cell 注入，以 Python 赋值语句形式传递。值类型支持：
- 字符串：`"value"`（需要加引号）
- 数字：`1000`、`0.5`
- 布尔值：`True`、`False`
- 列表/字典：JSON 格式

## 创建带参数的作业

### 通过 REST API

```bash
curl -X POST http://localhost:8888/scheduler/jobs \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "analysis/parametric_analysis.ipynb",
    "name": "Analysis - Jan 2024",
    "runtime_environment_name": "python3",
    "output_formats": ["ipynb", "html"],
    "parameters": {
      "start_date": "\"2024-01-01\"",
      "end_date": "\"2024-01-31\"",
      "region": "\"eu-west-1\"",
      "n_samples": "5000",
      "threshold": "0.8"
    }
  }'
```

**注意**：字符串参数值需要包含引号，如 `"\"value\""`，因为注入时直接拼接到 Python 赋值语句中。

### 参数注入机制

执行时，ExecutionManager 的 `add_parameters()` 方法：

1. 在 Notebook 中查找 tag 为 `parameters` 的 cell
2. 在该 cell 之后插入一个新 cell（tag 为 `injected-parameters`）
3. 新 cell 内容为：
```python
# Injected parameters
start_date = "2024-01-01"
end_date = "2024-01-31"
region = "eu-west-1"
n_samples = 5000
threshold = 0.8
```
4. 后续 cell 执行时使用注入的参数值（覆盖默认值）

### 输出 Notebook 示例

执行后的 Notebook 中可以看到：

```
Cell 1 (parameters tag):
    start_date = "2024-01-01"  # 默认值
    end_date = "2024-01-31"
    ...

Cell 2 (injected-parameters tag):  <-- 自动注入
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    region = "eu-west-1"          # 覆盖默认值
    n_samples = 5000              # 覆盖默认值
    threshold = 0.8               # 覆盖默认值

Cell 3:
    print(f"分析 {start_date} 到 {end_date} 的 {region} 数据")
    # 使用注入的参数执行...
```

## 批量参数化执行

通过多次调用 API 实现批量运行不同参数组合：

```python
import requests
import time

BASE_URL = "http://localhost:8888"
TOKEN = "your-token"
headers = {"Authorization": f"token {TOKEN}"}

# 参数组合
param_sets = [
    {"region": "\"us-east-1\"", "threshold": "0.5"},
    {"region": "\"eu-west-1\"", "threshold": "0.5"},
    {"region": "\"ap-southeast-1\"", "threshold": "0.7"},
]

job_ids = []
for params in param_sets:
    resp = requests.post(
        f"{BASE_URL}/scheduler/jobs",
        headers=headers,
        json={
            "input_uri": "analysis/model_training.ipynb",
            "name": f"Training {params['region']}",
            "runtime_environment_name": "python3",
            "output_formats": ["ipynb"],
            "parameters": params,
        },
    )
    job_id = resp.json()["job_id"]
    job_ids.append(job_id)
    print(f"Created job: {job_id}")

# 等待所有作业完成
for job_id in job_ids:
    while True:
        resp = requests.get(f"{BASE_URL}/scheduler/jobs/{job_id}", headers=headers)
        status = resp.json()["status"]
        if status in ("COMPLETED", "FAILED", "STOPPED"):
            print(f"Job {job_id}: {status}")
            break
        time.sleep(5)

# 下载所有结果
for job_id in job_ids:
    requests.get(
        f"{BASE_URL}/scheduler/jobs/{job_id}/download_files",
        headers=headers,
        allow_redirects=True,
    )
```

## 定时作业中的参数

定时作业定义时也可以设置参数，所有按 cron 触发的执行都会使用相同的参数：

```bash
curl -X POST http://localhost:8888/scheduler/job_definitions \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "reports/daily_report.ipynb",
    "name": "Daily EU Report",
    "runtime_environment_name": "python3",
    "output_formats": ["ipynb", "html"],
    "schedule": "0 9 * * *",
    "timezone": "Europe/Paris",
    "parameters": {"region": "\"eu-west-1\""},
    "active": true
  }'
```

手动触发时可以覆盖默认参数：

```bash
curl -X POST \
  "http://localhost:8888/scheduler/job_definitions/$DEF_ID/jobs" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"region": "\"us-east-1\""}}'
```

## 使用幂等性令牌

对于参数化作业，建议使用 `idempotency_token` 防止重复提交：

```bash
curl -X POST http://localhost:8888/scheduler/jobs \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "analysis/run.ipynb",
    "name": "Run 001",
    "runtime_environment_name": "python3",
    "output_formats": ["ipynb"],
    "parameters": {"seed": "42"},
    "idempotency_token": "run-001-seed-42"
  }'
```

重复使用相同 token 会返回 409 Conflict，避免网络重试导致重复执行。

## 注意事项

1. **字符串参数要加引号**：`"region": "\"eu-west-1\""` 而非 `"region": "eu-west-1"`
2. **parameters cell必须存在**：如果Notebook没有parameters tagged cell，参数会被忽略
3. **参数覆盖发生在cell级**：注入的cell紧跟在parameters cell之后，Python变量作用域规则决定后面的赋值覆盖前面的
4. **不要在parameters cell之后重新定义参数变量**：否则会覆盖注入的值
5. **参数值是字符串传入**：API中parameters字典的value都是字符串形式，因为注入时直接拼接到Python代码中
