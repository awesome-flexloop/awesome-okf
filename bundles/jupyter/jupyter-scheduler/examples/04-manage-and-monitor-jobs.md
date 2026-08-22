# 管理和监控作业

本示例展示如何管理作业的完整生命周期：查看状态、停止运行中的作业、删除作业、批量操作和错误处理。

## 查看作业列表

### 基本列表查询

```bash
# 查看所有作业（默认按创建时间降序，最多1000条）
curl -H "Authorization: token $TOKEN" \
  http://localhost:8888/scheduler/jobs
```

### 按状态过滤

```bash
# 只看正在运行的作业
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs?status=IN_PROGRESS"

# 只看失败的作业
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs?status=FAILED"

# 只看已完成的作业
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs?status=COMPLETED"
```

可用状态值：CREATED、QUEUED、IN_PROGRESS、COMPLETED、FAILED、STOPPING、STOPPED

### 按标签过滤

```bash
# 查看带有 "daily" 标签的作业
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs?tags=daily"
```

### 按作业定义过滤

```bash
# 查看某个定时作业定义产生的所有作业
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs?job_definition_id=$DEF_ID"
```

### 排序和分页

```bash
# 按名称升序排列
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs?sort_by=asc(name)"

# 按开始时间降序
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs?sort_by=desc(start_time)"

# 分页：每页10条，获取第二页
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs?max_items=10&next_token=10"
```

### 统计作业数

```bash
# 统计正在运行的作业数（默认IN_PROGRESS）
curl -H "Authorization: token $TOKEN" \
  http://localhost:8888/scheduler/jobs/count

# 统计失败的作业数
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs/count?status=FAILED"
```

## 监控作业执行进度

### 轮询状态

```python
import requests
import time

def wait_for_job(base_url, token, job_id, poll_interval=5, timeout=3600):
    """等待作业完成，返回最终状态"""
    headers = {"Authorization": f"token {token}"}
    start = time.time()
    
    while time.time() - start < timeout:
        resp = requests.get(f"{base_url}/scheduler/jobs/{job_id}", headers=headers)
        job = resp.json()
        status = job["status"]
        
        elapsed = time.time() - start
        print(f"[{elapsed:.0f}s] Status: {status}")
        
        if status == "COMPLETED":
            print(f"Job completed in {job['end_time'] - job['start_time']}ms")
            return job
        elif status == "FAILED":
            print(f"Job failed: {job.get('status_message', 'Unknown error')}")
            return job
        elif status == "STOPPED":
            print("Job was stopped")
            return job
        
        time.sleep(poll_interval)
    
    print("Timeout waiting for job")
    return None
```

### 查看失败原因

失败作业的 `status_message` 字段包含错误信息：

```bash
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs/$JOB_ID" | python -m json.tool
```

输出示例：
```json
{
  "job_id": "jupyter_server_nb:xxx",
  "status": "FAILED",
  "status_message": "CellExecutionError: An error occurred while executing the following cell:\n--\nprint(undefined_variable)\n--\nNameError: name 'undefined_variable' is not defined",
  "start_time": 1703001235000,
  "end_time": 1703001240000
}
```

### 查看执行时间

```python
job = wait_for_job(BASE_URL, TOKEN, job_id)
if job and job["status"] == "COMPLETED":
    duration_ms = job["end_time"] - job["start_time"]
    print(f"Execution time: {duration_ms/1000:.1f}s")
```

## 停止作业

### 停止单个作业

```bash
curl -X PATCH \
  "http://localhost:8888/scheduler/jobs/$JOB_ID" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "STOPPED"}'
```

停止流程：
1. Scheduler 从数据库查询作业 PID
2. 使用 psutil 递归查找子进程树（包括 kernel 进程）
3. Kill 所有相关进程
4. 更新状态为 STOPPED

**注意**：只能停止 IN_PROGRESS 或 QUEUED 状态的作业。COMPLETED/FAILED/STOPPED 状态的作业无法停止。

### 停止并重新运行

```python
def stop_and_rerun(base_url, token, job_id):
    headers = {"Authorization": f"token {token}"}
    
    # 停止当前作业
    requests.patch(
        f"{base_url}/scheduler/jobs/{job_id}",
        headers=headers,
        json={"status": "STOPPED"},
    )
    
    # 获取原作业配置
    old_job = requests.get(f"{base_url}/scheduler/jobs/{job_id}", headers=headers).json()
    
    # 创建新作业（使用相同配置）
    resp = requests.post(
        f"{base_url}/scheduler/jobs",
        headers=headers,
        json={
            "input_uri": old_job["input_uri"],
            "name": old_job["name"] + " (rerun)",
            "runtime_environment_name": old_job["runtime_environment_name"],
            "output_formats": old_job["output_formats"],
            "parameters": old_job.get("parameters"),
        },
    )
    return resp.json()["job_id"]
```

## 删除作业

### 删除单个作业

```bash
curl -X DELETE \
  "http://localhost:8888/scheduler/jobs/$JOB_ID" \
  -H "Authorization: token $TOKEN"
```

删除操作：
1. 如果作业正在运行，先停止它
2. 删除 staging 目录中的临时文件
3. 删除数据库记录
4. 本地输出目录（jobs/下的已下载文件）不会被删除

### 批量删除作业

```bash
# 批量删除多个作业（job_id参数可重复）
curl -X DELETE \
  "http://localhost:8888/scheduler/batch/jobs?job_id=$ID1&job_id=$ID2&job_id=$ID3" \
  -H "Authorization: token $TOKEN"
```

### 清理已完成的作业

```python
import requests

def cleanup_completed_jobs(base_url, token):
    """删除所有已完成/失败/停止的作业"""
    headers = {"Authorization": f"token {token}"}
    
    # 获取所有终态作业
    deleted = []
    for status in ["COMPLETED", "FAILED", "STOPPED"]:
        resp = requests.get(
            f"{base_url}/scheduler/jobs",
            headers=headers,
            params={"status": status, "max_items": 1000},
        )
        for job in resp.json()["jobs"]:
            requests.delete(
                f"{base_url}/scheduler/jobs/{job['job_id']}",
                headers=headers,
            )
            deleted.append(job["job_id"])
    
    print(f"Deleted {len(deleted)} jobs")
    return deleted
```

## 下载和查看输出

### 触发下载

```bash
# 下载到本地工作区
curl -L -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs/$JOB_ID/download_files"

# 强制重新下载（覆盖已有文件）
curl -L -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs/$JOB_ID/download_files?redownload=true"
```

### 检查下载状态

```python
def is_downloaded(base_url, token, job_id):
    headers = {"Authorization": f"token {token}"}
    resp = requests.get(f"{base_url}/scheduler/jobs/{job_id}", headers=headers)
    job = resp.json()
    return job.get("downloaded", False)
```

### 下载后查看文件列表

下载完成后，`job_files` 中的 `file_path` 字段会填充：

```json
{
  "job_files": [
    {
      "display_name": "analysis.ipynb",
      "file_format": "ipynb",
      "file_path": "jobs/My Analysis-550e8400/analysis.ipynb"
    },
    {
      "display_name": "analysis.html",
      "file_format": "html",
      "file_path": "jobs/My Analysis-550e8400/analysis.html"
    }
  ],
  "downloaded": true
}
```

## 可用后端查询

```bash
# 查看所有可用后端
curl -H "Authorization: token $TOKEN" \
  http://localhost:8888/scheduler/backends

# 查看运行时环境
curl -H "Authorization: token $TOKEN" \
  http://localhost:8888/scheduler/runtime_environments

# 查看功能配置
curl -H "Authorization: token $TOKEN" \
  http://localhost:8888/scheduler/config
```
