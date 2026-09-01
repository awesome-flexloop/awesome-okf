---
title: 快速开始
type: example
bundle: jupyter-notebook
chapter: "00"
difficulty: beginner
tags: ["quickstart", "installation", "setup"]
prerequisites: []
sources: ["F-001", "F-003", "F-029"]
related_concepts: ["00-introduction", "08-build-system"]
---

# 00 | 快速开始

本教程带你从零开始安装和启动Jupyter Notebook v7。

## 方式一：pip安装（推荐）

### 前置条件

- Python 3.10+（F-001）
- pip 或 conda

### 安装

```bash
# 使用pip安装
pip install notebook

# 验证安装
jupyter notebook --version
# 输出: 7.x.x
```

### 启动

```bash
# 启动Notebook（自动打开浏览器）
jupyter notebook

# 指定端口启动
jupyter notebook --port=9999

# 不自动打开浏览器
jupyter notebook --no-browser

# 指定工作目录
jupyter notebook --ServerApp.root_dir=/path/to/notebooks

# 允许外部访问
jupyter notebook --ip=0.0.0.0 --ServerApp.token=''
```

启动后终端会显示类似输出：

```
[I 2026-08-21 10:00:00.000 ServerApp] jupyter_server 2.x.x is running at:
[I 2026-08-21 10:00:00.000 ServerApp]     http://localhost:8888/tree?token=xxxxxx
```

在浏览器中打开显示的URL即可访问Notebook。

## 方式二：从源码安装（开发模式）

适用于需要修改Notebook源码或开发扩展的场景。

### 前置条件

- Python 3.10+
- Node.js 18+
- npm 或 yarn
- Git

### 步骤

```bash
# 1. 克隆源码
git clone https://github.com/jupyter/notebook.git
cd notebook

# 2. 安装Python包（可编辑模式）
pip install -e ".[dev,test]"

# 3. 安装前端依赖
npm install

# 4. 构建前端
npm run build

# 5. 启动
jupyter notebook
```

### 开发模式（前端热重载）

在两个终端中分别运行：

```bash
# 终端1：监听前端变化自动构建
npm run watch

# 终端2：启动Notebook
jupyter notebook
```

## 方式三：使用Docker

```bash
# 使用官方镜像
docker run -it -p 8888:8888 quay.io/jupyter/base-notebook:latest

# 挂载本地目录
docker run -it -p 8888:8888 \
    -v /your/local/notebooks:/home/jovyan/work \
    quay.io/jupyter/base-notebook:latest
```

## 验证安装成功

访问 `http://localhost:8888/tree`，你应该看到：

1. **文件浏览器界面**（Tree页面），显示启动目录下的文件
2. **右侧有"New"按钮**，可以创建新的Notebook、Console、Terminal
3. **顶部菜单栏**（File/Edit/View/Run/Kernel等）
4. **左上角有Jupyter Logo**

### 创建第一个Notebook

1. 点击右侧 "New" 下拉按钮
2. 选择一个Kernel（如 "Python 3"）
3. 在新标签页中输入代码：
   ```python
   print("Hello, Jupyter Notebook v7!")
   ```
4. 按 `Shift+Enter` 运行代码
5. 你应该看到输出 "Hello, Jupyter Notebook v7!"

## 常用启动选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--port` | 指定端口 | `--port=9999` |
| `--ip` | 监听IP | `--ip=0.0.0.0` |
| `--no-browser` | 不打开浏览器 | `--no-browser` |
| `--ServerApp.root_dir` | 工作目录 | `--ServerApp.root_dir=/data` |
| `--ServerApp.token` | 认证token | `--ServerApp.token='mytoken'` |
| `--ServerApp.password` | 设置密码 | `--ServerApp.password=''` |
| `--ServerApp.allow_origin` | CORS允许 | `--ServerApp.allow_origin='*'` |
| `--config` | 指定配置文件 | `--config=my_config.py` |
| `--expose-app-in-browser` | 暴露window.jupyterapp | `--expose-app-in-browser` |
| `--custom-css` | 启用自定义CSS | `--custom-css` |

## 配置文件

### 生成配置文件

```bash
jupyter server --generate-config
```

这会创建 `~/.jupyter/jupyter_server_config.py`。

### 常用配置

```python
# ~/.jupyter/jupyter_server_config.py
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = '/home/user/notebooks'
c.ServerApp.token = ''
c.ServerApp.password = ''
c.LabServerApp.open_browser = False
c.JupyterNotebookApp.default_url = '/tree'
```

## 常用快捷键

| 快捷键 | 模式 | 功能 |
|--------|------|------|
| `Shift+Enter` | 编辑模式 | 运行当前cell，移动到下一个 |
| `Ctrl+Enter` | 编辑模式 | 运行当前cell |
| `Alt+Enter` | 编辑模式 | 运行当前cell，在下方插入新cell |
| `Esc` | 编辑模式 | 切换到命令模式 |
| `Enter` | 命令模式 | 切换到编辑模式 |
| `a` | 命令模式 | 在上方插入cell |
| `b` | 命令模式 | 在下方插入cell |
| `dd` | 命令模式 | 删除当前cell |
| `m` | 命令模式 | 将cell转为Markdown |
| `y` | 命令模式 | 将cell转为Code |
| `h` | 命令模式 | 显示快捷键帮助 |

## 故障排查

### 端口被占用

```bash
# 查找占用8888端口的进程
# Linux/Mac:
lsof -i:8888
# Windows:
netstat -ano | findstr :8888

# 使用其他端口启动
jupyter notebook --port=8889
```

### 浏览器不自动打开

手动复制终端中显示的URL（含token）到浏览器中访问。

### Kernel无法启动

```bash
# 重新安装ipykernel
pip install --upgrade ipykernel
python -m ipykernel install --user
```

### 权限错误

```bash
# 使用--allow-root在root下运行（不推荐）
jupyter notebook --allow-root

# 或使用普通用户运行
```

## 下一步

- [开发前端扩展](01-frontend-extension.md) 学习如何创建Notebook插件
- [开发服务端扩展](02-server-extension.md) 学习如何添加自定义API
