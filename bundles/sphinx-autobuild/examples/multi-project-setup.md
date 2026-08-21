---
type: Example
title: 多项目并行开发
description: 同时运行多个 sphinx-autobuild 实例——自动端口分配、浏览器自动打开、后台运行
tags: [sphinx-autobuild, multi-project, --port=0, --open-browser, parallel, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-autobuild-source
    resource: /references/sphinx-autobuild-source.md
    title: sphinx-autobuild 源码信源登记
---

# 多项目并行开发

## 场景

你同时开发多个 Sphinx 文档项目（例如一个主项目文档和多个子项目文档），需要同时预览多个文档站点，手动管理端口和浏览器窗口非常繁琐。

## 核心技巧：--port=0 和 --open-browser

sphinx-autobuild 的 `--port=0` 选项让操作系统自动分配空闲端口，`--open-browser` 自动打开浏览器。两者结合可以轻松实现多项目并行。

## 并行运行多个实例

### Linux/macOS（使用 & 后台运行）

```bash
sphinx-autobuild --port=0 --open-browser project-a/docs project-a/docs/_build/html &
sphinx-autobuild --port=0 --open-browser project-b/docs project-b/docs/_build/html &
sphinx-autobuild --port=0 --open-browser project-c/docs project-c/docs/_build/html &
```

每个实例会：
1. 自动获取一个空闲端口
2. 启动服务器
3. 完成首次构建后自动打开浏览器标签页
4. 在后台运行

终端会显示每个实例实际使用的端口：

```
[sphinx-autobuild] Serving on http://127.0.0.1:8000
[sphinx-autobuild] Serving on http://127.0.0.1:8001
[sphinx-autobuild] Serving on http://127.0.0.1:8002
```

### Windows PowerShell（使用 Start-Process）

```powershell
Start-Process sphinx-autobuild -ArgumentList "--port=0","--open-browser","project-a/docs","project-a/docs/_build/html"
Start-Process sphinx-autobuild -ArgumentList "--port=0","--open-browser","project-b/docs","project-b/docs/_build/html"
Start-Process sphinx-autobuild -ArgumentList "--port=0","--open-browser","project-c/docs","project-c/docs/_build/html"
```

或者在新窗口中运行：

```powershell
Start-Process powershell -ArgumentList "-NoExit","-Command","sphinx-autobuild --port=0 --open-browser project-a/docs project-a/docs/_build/html"
```

## 使用不同输出目录

**重要**：多个项目必须使用**不同的输出目录**，否则构建输出会互相覆盖。推荐的目录结构：

```
workspace/
├── project-a/
│   ├── docs/
│   │   ├── conf.py
│   │   └── index.rst
│   └── docs/_build/html/    # 项目 A 的独立输出目录
├── project-b/
│   ├── docs/
│   │   ├── conf.py
│   │   └── index.rst
│   └── docs/_build/html/    # 项目 B 的独立输出目录
└── project-c/
    ├── docs/
    └── docs/_build/html/   # 项目 C 的独立输出目录
```

## 创建启动脚本

### Bash 脚本（start-docs.sh）

```bash
#!/bin/bash
# 同时启动所有文档预览服务

echo "Starting documentation preview servers..."

# 启动项目 A
sphinx-autobuild --port=0 --open-browser \
  project-a/docs project-a/docs/_build/html &
PID_A=$!

# 启动项目 B
sphinx-autobuild --port=0 --open-browser \
  project-b/docs project-b/docs/_build/html &
PID_B=$!

# 启动项目 C
sphinx-autobuild --port=0 --open-browser \
  project-c/docs project-c/docs/_build/html &
PID_C=$!

echo "Servers started (PIDs: $PID_A, $PID_B, $PID_C)"
echo "Press Ctrl+C to stop all servers"

# 等待所有后台进程
wait
```

使用：

```bash
chmod +x start-docs.sh
./start-docs.sh
```

### PowerShell 脚本（start-docs.ps1）

```powershell
# start-docs.ps1
# 同时启动所有文档预览服务

Write-Host "Starting documentation preview servers..." -ForegroundColor Green

$jobs = @()

# 启动每个项目
$projects = @(
    @{ Name = "project-a"; Docs = "project-a/docs"; Build = "project-a/docs/_build/html" },
    @{ Name = "project-b"; Docs = "project-b/docs"; Build = "project-b/docs/_build/html" },
    @{ Name = "project-c"; Docs = "project-c/docs"; Build = "project-c/docs/_build/html" }
)

foreach ($proj in $projects) {
    Write-Host "Starting $($proj.Name)..." -ForegroundColor Cyan
    $job = Start-Process -FilePath "sphinx-autobuild" `
        -ArgumentList "--port=0","--open-browser",$proj.Docs,$proj.Build `
        -PassThru -NoNewWindow
    $jobs += $job
}

Write-Host "`nAll servers started. Press Ctrl+C to stop all." -ForegroundColor Green

try {
    # 等待用户按 Ctrl+C
    $jobs | Wait-Process
} finally {
    # 清理：停止所有子进程
    Write-Host "`nStopping all servers..." -ForegroundColor Yellow
    $jobs | Stop-Process -Force -ErrorAction SilentlyContinue
}
```

## monorepo 场景

在 monorepo 中，多个子项目的文档可能需要共享配置：

```
monorepo/
├── docs/                    # 主文档
│   ├── conf.py
│   └── index.rst
├── packages/
│   ├── core/
│   │   └── docs/
│   │       ├── conf.py
│   │       └── index.rst
│   └── plugins/
│       └── docs/
│           ├── conf.py
│           └── index.rst
└── Makefile
```

Makefile 启动所有文档：

```makefile
.PHONY: docs-live
docs-live:
	sphinx-autobuild --port=0 --open-browser docs docs/_build/html &
	sphinx-autobuild --port=0 packages/core/docs packages/core/docs/_build/html &
	sphinx-autobuild --port=0 packages/plugins/docs packages/plugins/docs/_build/html &
	wait
```

## 查找运行中的实例

如果你忘记了哪个端口对应哪个项目，可以查看终端输出或使用系统工具：

**Linux/macOS：**

```bash
# 查看所有监听端口的 sphinx-autobuild 进程
ps aux | grep sphinx-autobuild

# 查看端口占用
lsof -i -P | grep sphinx-auto
```

**Windows：**

```powershell
# 查看 Python 进程的命令行
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like "*sphinx-autobuild*" } |
  Select-Object ProcessId, CommandLine
```

## 停止所有实例

### 前台启动的实例

直接在每个终端按 `Ctrl+C`。

### 后台启动的实例（Bash）

```bash
# 停止所有 sphinx-autobuild 进程
pkill -f sphinx-autobuild

# 或者使用 jobs 命令管理
jobs        # 列出后台任务
kill %1     # 停止第1个后台任务
kill %2     # 停止第2个
kill %1 %2  # 同时停止多个
```

### PowerShell

```powershell
# 停止所有 sphinx-autobuild 进程
Get-Process python | Where-Object {
    $_.MainModule.FileVersionInfo.FileDescription -like "*sphinx*"
} | Stop-Process

# 或者根据命令行停止
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like "*sphinx-autobuild*" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

## 端口管理最佳实践

1. **始终使用 `--port=0`**：避免端口冲突，让操作系统自动分配
2. **始终使用 `--open-browser`**：不用手动输入端口号和地址
3. **使用独立输出目录**：不同项目不能共享同一个 `_build/html` 目录
4. **配合 Makefile 或脚本**：将启动命令写入脚本，一键启动所有项目
5. **记录 PID**：脚本启动时记录进程 ID，方便统一停止

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [CLI 入口与参数解析](/concepts/03-cli-and-entrypoint.md)
- [服务器与热重载](/concepts/06-server-and-hotreload.md)
- [基础使用](/examples/basic-usage.md)
