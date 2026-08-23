---
type: Example
title: 启用和配置 jupyter-collaboration
description: 从零开始安装、启用和配置 Jupyter 实时协作，包括最小配置、常用配置项和验证步骤
tags: [configuration, installation, setup]
concepts: [/concepts/00-introduction.md, /concepts/02-ydoc-extension.md]
generated: { by: source-code-to-okf-wiki/agent, at: "2026-04-21T00:00:00Z" }
status: stable
---

# 启用和配置 jupyter-collaboration

## 前置条件

- Python 3.8+
- JupyterLab 4.0+
- jupyter-server 2.0+

## 安装

```bash
pip install jupyter-collaboration
```

安装后会自动安装以下依赖：
- `jupyter-server-ydoc`：后端服务端
- `jupyter-collaboration`：前端UI扩展（包括协作者面板、共享链接等）
- `jupyter-docprovider`：前端Yjs文档提供者
- `jupyter-collaborative-drive`：协作内容驱动接口
- `pycrdt`：Python CRDT实现

## 最小启动

安装完成后，Jupyter Server 扩展会自动启用。启动 JupyterLab 即可：

```bash
jupyter lab
```

打开两个浏览器窗口访问同一URL并打开同一notebook，即可看到实时协作效果。

## 验证安装

验证扩展是否正确安装：

```bash
# 检查server扩展
jupyter server extension list
# 应该看到:
# jupyter_server_ydoc enabled

# 检查lab扩展
jupyter labextension list
# 应该看到:
# @jupyter/collaboration-extension enabled
# @jupyter/docprovider-extension enabled
```

## 常用配置

### 通过配置文件配置

创建或编辑 `~/.jupyter/jupyter_server_config.py`：

```python
c.YDocExtension.disable_rtc = False           # 全局启用RTC（默认True）
c.YDocExtension.document_cleanup_delay = 60   # 房间空闲清理延迟（秒）
c.YDocExtension.document_save_delay = 1.0     # 保存防抖延迟（秒）

# YStore 配置
c.YDocExtension.store_class = "SQLiteYStore"  # 使用SQLite持久化
c.YDocExtension.ystore_kwargs = {
    "path": ".jupyter_ystore.db"              # SQLite数据库路径
}

# 外带变更检测
c.YDocExtension.file_poll_interval = 1.0      # 文件轮询间隔（秒），0=禁用
c.YDocExtension.outdated_ybuffer_timeout = 1.0  # 过时YBuffer超时
c.YDocExtension.stop_poll_on_errors_after = 24*60*60  # 错误后停止轮询等待时间
```

### 通过命令行参数配置

```bash
jupyter lab --YDocExtension.disable_rtc=False \
            --YDocExtension.document_save_delay=2.0 \
            --YDocExtension.file_poll_interval=5.0
```

### 禁用实时协作

```bash
# 方法1：命令行
jupyter lab --YDocExtension.disable_rtc=True

# 方法2：配置文件
c.YDocExtension.disable_rtc = True
```

禁用后，JupyterLab使用传统的REST API文件操作，不启用CRDT同步。

## 前端配置

前端配置通过 Jupyter Server 的PageConfig传递，通常不需要手动配置：

- `disableRTC`：由后端 `disable_rtc` 配置自动设置
- `collaborative`：由DocumentRegistry默认设置

## 验证协作功能

1. 启动JupyterLab
2. 在浏览器中打开notebook
3. 复制URL到另一个浏览器窗口（或隐身模式）
4. 在两个窗口中同时编辑
5. 应该看到：
   - 彩色的协作光标
   - 协作者头像/名字
   - 实时编辑同步
   - 左下角"协作"面板显示在线用户

## 部署场景配置

### 单用户本地开发

最小配置，无需额外设置：
```python
c.YDocExtension.disable_rtc = False
c.YDocExtension.file_poll_interval = 1.0
```

### 多用户JupyterHub

在JupyterHub上部署时，建议：
```python
c.YDocExtension.disable_rtc = False
c.YDocExtension.document_cleanup_delay = 300  # 5分钟清理空闲房间
c.YDocExtension.file_poll_interval = 5.0      # 降低轮询频率减少I/O
c.YDocExtension.ystore_kwargs = {"path": "/data/jupyter_ystore.db"}
```

### 容器化部署

容器化部署时注意：
```python
c.YDocExtension.disable_rtc = False
c.YDocExtension.file_poll_interval = 0  # 容器内文件不被外部修改，可禁用轮询
c.YDocExtension.ystore_kwargs = {"path": "/tmp/jupyter_ystore.db"}  # 使用临时存储
```

如果需要持久化YStore，将SQLite文件挂载到持久化卷。

## 环境变量

某些配置可以通过环境变量设置：

```bash
# YStore路径（默认SQLiteYStore使用）
JUPYTER_COLLABORATION_YSTORE_PATH=/path/to/ystore.db
```

## 故障排查

### 看不到协作者光标

1. 确认两个窗口使用同一URL（含token）
2. 确认WebSocket连接未被防火墙阻止
3. 检查浏览器控制台是否有WebSocket连接错误
4. 确认 `disable_rtc` 为False

### 编辑内容不同步

1. 检查浏览器网络面板，确认WebSocket消息正常收发
2. 查看服务器日志是否有CRDT错误
3. 尝试刷新页面重新同步

### 文件保存冲突

如果频繁出现"Document Conflict"对话框：
1. 检查文件是否被外部进程修改（如git checkout）
2. 考虑增大 `file_poll_interval` 减少误检
3. 使用协作期间避免外部修改文件
