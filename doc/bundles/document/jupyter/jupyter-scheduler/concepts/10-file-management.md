# 文件管理与输出处理

Jupyter Scheduler 采用**两阶段文件管理**设计：作业输出先写入 staging 暂存区，用户主动下载时才复制到工作区。文件操作通过 fsspec 抽象，支持本地和远程存储。

## 目录结构

### Staging 暂存区

```
{staging_path}/
└── {job_id}/                          # 每个作业一个目录
    ├── {input_filename}               # 输入文件（notebook/script）
    ├── {input_filename}.ipynb         # 执行后的notebook
    ├── {input_filename}.html          # HTML导出（如果output_formats包含）
    ├── data.csv                       # Notebook创建的副作用文件
    ├── plot.png                       # 副作用文件
    └── ...
```

默认 staging 路径：`{jupyter_data_dir()}/scheduler_staging_area`，可配置：
```python
c.SchedulerApp.staging_path = "/path/to/staging"
```

Staging 路径支持 fsspec 协议（如 `s3://bucket/staging`），可对接远程存储。

### 本地输出目录

```
{root_dir}/
└── jobs/                              # 本地下载目录（output_directory配置）
    └── {basefilename}-{job_id}/       # 每个作业一个目录
        ├── {input_filename}           # 输入文件
        ├── {input_filename}.ipynb     # 输出notebook
        └── {input_filename}.html      # HTML导出
```

目录名格式：`{name}-{job_id_short}`（name来自作业名称，去除文件扩展名）。

## 文件流转

```
用户Notebook (root_dir/notebook.ipynb)
        │ create_job
        │ 1. 复制输入文件到staging
        ▼
Staging (scheduler_staging_area/{job_id}/notebook.ipynb)
        │ 2. 子进程执行
        │    nbconvert执行 → 生成输出文件
        ▼
Staging (含输出文件)
        │ 3. 用户触发下载 GET /jobs/{id}/download_files
        │ 4. JobFilesManager复制到工作区
        ▼
Local Output (root_dir/jobs/{name}-{id}/)
        │ 5. JupyterLab文件浏览器可直接访问
        ▼
用户查看
```

## Staging 文件操作

### copy_input_file / copy_input_folder

创建作业时将输入文件/文件夹复制到 staging：

```python
# 单文件复制
fsspec.open(staging_input_path, "wb").write(fsspec.open(input_path, "rb").read())

# 文件夹复制（package_input_folder=True时）
_recursive_copy(input_dir, staging_dir, fs)
```

### get_staging_paths(model)

返回各输出格式对应的 staging 路径字典：

```python
def get_staging_paths(self, model):
    paths = {}
    for format in model.output_formats:
        ext = "ipynb" if format == "ipynb" else format
        paths[format] = f"{staging_dir}/{basefilename}.{ext}"
    paths["input"] = staging_input_path
    return paths
```

### 输出文件写入

执行完成后，ExecutionManager 将各格式输出写入 staging：

```python
# DefaultExecutionManager.create_output_files()
for format in output_formats:
    exporter = get_exporter(format)()
    output, _ = exporter.from_notebook_node(nb)
    with fsspec.open(staging_paths[format], "w") as f:
        f.write(output)
```

### 副作用文件捕获

Notebook 执行过程中可能在 cwd（即 staging 目录）创建数据文件、图表等。`add_side_effects_files()` 递归扫描 staging 目录收集这些文件：

```python
for root, dirs, files in os.walk(staging_dir):
    for f in files:
        if f != input_filename and f not in known_outputs:
            packaged_files.append(os.path.relpath(os.path.join(root, f), staging_dir))
job.packaged_files = packaged_files
```

## 文件下载（JobFilesManager）

`JobFilesManager` 负责将 staging 中的输出文件复制到本地工作区。

### 下载流程

1. 接收 GET `/scheduler/jobs/{job_id}/download_files?redownload=false` 请求
2. 查询作业状态（必须是 COMPLETED/FAILED/STOPPED）
3. 确定本地输出目录路径
4. 检查是否已下载（目录存在且所有文件就位）：
   - 已下载且 redownload=false → 返回路径
   - 未下载或 redownload=true → 执行复制
5. 在子进程中执行下载（避免阻塞服务器）：
   ```python
   downloader = Downloader(...)
   p = mp.get_context("spawn").Process(target=downloader.process)
   p.start()
   ```
6. 下载完成后更新 model.downloaded 标志
7. 重定向到文件浏览器路径

### Downloader 子进程

Downloader 是独立子进程，负责：
1. 创建本地输出目录
2. 从 staging 复制所有输出文件（包括 packaged_files）到本地目录
3. 复制 input 文件
4. 更新数据库中的 job 状态（file_path 字段）

### 重下载

`redownload=true` 参数强制重新从 staging 复制文件到本地目录，覆盖已存在的文件。

## 路径安全

### 路径遍历攻击防护

`file_exists()` 和 `dir_exists()` 方法验证路径是否在 root_dir 内：

```python
def file_exists(self, path):
    root = os.path.abspath(self.root_dir)
    os_path = to_os_path(path, root)
    if not (os.path.abspath(os_path) + os.path.sep).startswith(root):
        return False
    return os.path.isfile(os_path)
```

使用 `os.path.abspath()` 规范化路径后，检查是否以 root_dir 为前缀，防止 `../` 路径逃逸。

## 输出文件名

### 文件名模板

默认模板：`"{{input_filename}}-{{create_time}}"`

可用变量：
- `{{input_filename}}`：输入文件名（不含扩展名）
- `{{create_time}}`：作业创建时间戳

模板使用 `string.Template` 或简单字符串替换生成最终文件名。

### JobFile 记录

每个输出文件在 Job 模型中对应一个 JobFile 条目：

```python
class JobFile(BaseModel):
    display_name: str      # 显示名称
    file_format: str       # 格式（ipynb/html/...）
    file_path: Optional[str]  # 本地路径（下载后填充）
```

### downloaded 标志

DescribeJob 模型包含 `downloaded` 布尔字段，表示所有输出文件是否已下载到本地目录：
- True：所有 job_file 的 file_path 非空且文件存在
- False：文件尚未下载或正在下载中
