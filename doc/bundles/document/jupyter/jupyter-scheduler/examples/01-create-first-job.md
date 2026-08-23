# 创建并执行第一个 Notebook 作业

本示例展示如何通过 REST API 创建一个简单的 Notebook 后台执行作业。

## 前置条件

- JupyterLab 4.x 已启动，jupyter-scheduler 扩展已安装
- 有一个可执行的 Notebook 文件
- Notebook 包含 kernelspec 元数据（正常在JupyterLab中保存的Notebook都有）

## 准备测试 Notebook

创建一个简单的测试 Notebook `examples/hello.ipynb`，内容：

```python
# 第一个cell
import time
import datetime

print(f"开始执行: {datetime.datetime.now()}")
time.sleep(2)
print(f"执行完成: {datetime.datetime.now()}")
```

确保 Notebook 在 JupyterLab 中可以正常运行（有 kernelspec）。

## 通过 REST API 创建作业

使用 curl 或任何 HTTP 客户端发送请求：

```bash
# 获取Jupyter token（从JupyterLab启动日志或jupyter server list）
TOKEN=$(jupyter server list 2>/dev/null | grep -oP '(?<=token=)[a-f0-9]+' | head -1)

# 创建作业
curl -X POST http://localhost:8888/scheduler/jobs \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "examples/hello.ipynb",
    "name": "Hello Job",
    "runtime_environment_name": "python3",
    "output_formats": ["ipynb", "html"],
    "tags": ["test"]
  }'
```

响应：
```json
{"job_id": "jupyter_server_nb:550e8400-e29b-41d4-a716-446655440000"}
```

## 查看作业状态

```bash
# 查看所有作业
curl -H "Authorization: token $TOKEN" \
  http://localhost:8888/scheduler/jobs

# 查看特定作业
JOB_ID="jupyter_server_nb:550e8400-e29b-41d4-a716-446655440000"
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs/$JOB_ID"
```

等待作业完成（状态从 IN_PROGRESS 变为 COMPLETED）：

```json
{
  "job_id": "jupyter_server_nb:550e8400-...",
  "name": "Hello Job",
  "status": "COMPLETED",
  "input_filename": "hello.ipynb",
  "output_formats": ["ipynb", "html"],
  "job_files": [
    {"display_name": "hello.ipynb", "file_format": "ipynb", "file_path": null},
    {"display_name": "hello.html", "file_format": "html", "file_path": null}
  ],
  "downloaded": false,
  "create_time": 1703001234000,
  "start_time": 1703001235000,
  "end_time": 1703001237000
}
```

注意 `file_path` 为 null，`downloaded` 为 false——输出还在 staging 中，需要下载。

## 下载输出文件

```bash
curl -L -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs/$JOB_ID/download_files"
```

这会将文件复制到 `jobs/Hello Job-{job_id_short}/` 目录下。下载完成后：
- `downloaded` 变为 true
- `file_path` 填充为相对路径
- JupyterLab 文件浏览器中可以在 `jobs/` 目录看到输出文件

## 通过 JupyterLab UI 操作

在 JupyterLab 界面中：

1. **创建作业**：右键点击 Notebook 文件 → "Create Job"，或在 Notebook 工具栏点击创建作业按钮
2. **填写表单**：输入作业名称、选择输出格式
3. **查看作业列表**：点击左侧 "Jobs" 图标（时钟图标）打开 Jobs 面板
4. **下载输出**：作业完成后，点击 "Download" 按钮
5. **查看结果**：下载后点击文件名在 JupyterLab 中打开

## 使用 Python 客户端（requests）

```python
import requests

# 配置
BASE_URL = "http://localhost:8888"
TOKEN = "your-jupyter-token"
headers = {"Authorization": f"token {TOKEN}"}

# 创建作业
resp = requests.post(
    f"{BASE_URL}/scheduler/jobs",
    headers=headers,
    json={
        "input_uri": "examples/hello.ipynb",
        "name": "Python API Job",
        "runtime_environment_name": "python3",
        "output_formats": ["ipynb"],
    },
)
job_id = resp.json()["job_id"]
print(f"Created job: {job_id}")

# 轮询等待完成
import time
while True:
    resp = requests.get(f"{BASE_URL}/scheduler/jobs/{job_id}", headers=headers)
    job = resp.json()
    print(f"Status: {job['status']}")
    if job["status"] in ("COMPLETED", "FAILED", "STOPPED"):
        break
    time.sleep(2)

# 下载输出
if job["status"] == "COMPLETED":
    requests.get(
        f"{BASE_URL}/scheduler/jobs/{job_id}/download_files",
        headers=headers,
        allow_redirects=True,
    )
    print("Output downloaded to jobs/ directory")
```

## 常见问题

**Q: 创建作业时报错 "Kernel not found"？**
A: 确保 Notebook 已保存且包含 `metadata.kernelspec.name`。在 JupyterLab 中打开 Notebook 执行一个 cell 后保存即可。

**Q: 作业一直停留在 IN_PROGRESS？**
A: 可能是 kernel 启动失败或执行卡住。查看 Jupyter Server 日志排查。使用 PATCH /jobs/{id} 将 status 设为 STOPPED 可停止作业。

**Q: 下载后文件在哪里？**
A: 默认在 Jupyter 根目录的 `jobs/{name}-{job_id}/` 目录下。可通过 `c.SchedulerApp.output_directory` 配置修改。
