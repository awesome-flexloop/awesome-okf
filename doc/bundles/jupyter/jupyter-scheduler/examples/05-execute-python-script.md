# 执行 Python 脚本作业

除了 Notebook，Jupyter Scheduler 也支持直接执行 Python 脚本（`.py` 文件），使用 `jupyter_server_py` 后端。

## 创建 Python 脚本

创建一个示例脚本 `examples/process_data.py`：

```python
#!/usr/bin/env python3
"""数据处理脚本 - 通过jupyter-scheduler执行"""

import sys
import os
import json
import datetime
import argparse

def main():
    parser = argparse.ArgumentParser(description="Process data")
    parser.add_argument("--input", default="data.csv", help="Input file")
    parser.add_argument("--output", default="result.json", help="Output file")
    parser.add_argument("--threshold", type=float, default=0.5, help="Threshold value")
    args = parser.parse_args()
    
    print(f"[{datetime.datetime.now()}] Starting data processing...")
    print(f"  Input: {args.input}")
    print(f"  Output: {args.output}")
    print(f"  Threshold: {args.threshold}")
    
    # 模拟数据处理
    result = {
        "timestamp": datetime.datetime.now().isoformat(),
        "input": args.input,
        "threshold": args.threshold,
        "status": "success",
        "records_processed": 1000,
    }
    
    # 写入输出文件
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[{datetime.datetime.now()}] Processing complete.")
    print(f"  Result written to: {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## 通过 REST API 执行 Python 脚本

```bash
curl -X POST http://localhost:8888/scheduler/jobs \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "examples/process_data.py",
    "name": "Process Data",
    "runtime_environment_name": "python3",
    "output_formats": ["stdout", "stderr"],
    "backend_id": "jupyter_server_py"
  }'
```

**注意**：
- `input_uri` 指向 `.py` 文件
- 不指定 `backend_id` 时，系统会根据 `.py` 扩展名自动路由到 `jupyter_server_py` 后端
- Python 脚本后端支持的 output_formats：`stdout`（标准输出）、`stderr`（错误输出）、`json`（JSON结果）

## 查看执行结果

```bash
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/scheduler/jobs/$JOB_ID"
```

Python 脚本作业的 job_files 包含 stdout 和 stderr：

```json
{
  "job_id": "jupyter_server_py:xxx",
  "name": "Process Data",
  "status": "COMPLETED",
  "job_files": [
    {
      "display_name": "stdout",
      "file_format": "stdout",
      "file_path": null
    },
    {
      "display_name": "stderr",
      "file_format": "stderr",
      "file_path": null
    }
  ]
}
```

下载后查看 stdout 输出：
```
[2024-01-15 09:00:01.123456] Starting data processing...
  Input: data.csv
  Output: result.json
  Threshold: 0.5
[2024-01-15 09:00:02.456789] Processing complete.
  Result written to: result.json
```

## 传参给 Python 脚本

Python 脚本执行器使用 subprocess 运行脚本，可以通过环境变量或命令行参数传递参数。

### 方式一：通过 parameters 环境变量

`jupyter_server_py` 后端会将 parameters 字典作为环境变量传递给子进程：

```bash
curl -X POST http://localhost:8888/scheduler/jobs \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "examples/process_data.py",
    "name": "Process Data with Params",
    "runtime_environment_name": "python3",
    "output_formats": ["stdout"],
    "parameters": {
      "THRESHOLD": "0.8",
      "INPUT_FILE": "large_data.csv"
    },
    "backend_id": "jupyter_server_py"
  }'
```

在脚本中读取环境变量：
```python
import os
threshold = float(os.environ.get("THRESHOLD", "0.5"))
input_file = os.environ.get("INPUT_FILE", "data.csv")
```

### 方式二：自定义后端的命令行参数

如果需要传递命令行参数，需要自定义执行管理器。参见[自定义后端开发指南](../concepts/12-custom-backend.md)。

## 定时执行 Python 脚本

```bash
curl -X POST http://localhost:8888/scheduler/job_definitions \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "scripts/daily_cleanup.py",
    "name": "Daily Cleanup",
    "runtime_environment_name": "python3",
    "output_formats": ["stdout", "stderr"],
    "schedule": "0 2 * * *",
    "timezone": "Asia/Shanghai",
    "active": true,
    "backend_id": "jupyter_server_py"
  }'
```

每天凌晨2点执行清理脚本。

## Python 脚本与 Notebook 的区别

| 特性 | Notebook (.ipynb) | Python脚本 (.py) |
|-----|-------------------|------------------|
| 后端 | jupyter_server_nb | jupyter_server_py |
| 执行方式 | nbconvert ExecutePreprocessor（启动kernel） | subprocess.run（直接执行） |
| 输出格式 | ipynb, html, pdf等nbconvert格式 | stdout, stderr, json |
| 参数注入 | parameters tagged cell | 环境变量 |
| 副作用文件 | 自动捕获staging目录中的文件 | 同Notebook |
| 内核要求 | 需要kernelspec | 不需要（直接用Python解释器） |
| 执行环境 | Jupyter kernel（支持ipywidgets等） | 标准Python进程 |

## 打包输入文件夹

如果脚本依赖同目录下的其他模块或数据文件，使用 `package_input_folder: true`：

```bash
curl -X POST http://localhost:8888/scheduler/jobs \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_uri": "myproject/main.py",
    "name": "Run Project",
    "runtime_environment_name": "python3",
    "output_formats": ["stdout"],
    "package_input_folder": true,
    "backend_id": "jupyter_server_py"
  }'
```

这会将 `myproject/` 目录下的所有文件复制到 staging，脚本可以 import 同目录下的模块。

## 错误处理

脚本以非零退出码退出时，作业状态变为 FAILED，stderr 中包含错误信息：

```python
# 脚本出错示例
import sys
print("Processing...", file=sys.stderr)
raise RuntimeError("Something went wrong")
```

作业状态为 FAILED 时，status_message 和 stderr 文件中会包含 traceback 信息。

## 示例：数据处理流水线

创建一个完整的数据处理流水线：

1. `download_data.py` - 下载数据
2. `clean_data.py` - 清洗数据
3. `analyze.py` - 分析数据
4. `generate_report.py` - 生成报告

可以通过定时作业定义串联，或使用 Notebook 作为编排入口调用这些脚本。
