---
type: Example
title: 基本使用示例
description: 安装、启用CPU/磁盘监控、配置内存限制、启用顶栏指示器、查看内核资源、容器化部署配置等完整使用示例
tags: [jupyter-resource-usage, example, basic-usage, configuration, container]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 基本使用示例

本文档提供 jupyter-resource-usage 从安装到高级配置的完整使用示例。

## 示例1：基础安装与使用

### 1.1 pip安装

```bash
pip install jupyter-resource-usage
```

安装后启动JupyterLab，底部状态栏将自动显示内存使用量：

```
Mem: 256.00 MB
```

### 1.2 conda安装

```bash
conda install -c conda-forge jupyter-resource-usage
```

### 1.3 验证安装

```bash
jupyter server extension list
```

应看到：

```
jupyter_resource_usage enabled
    - Validating jupyter_resource_usage...
      jupyter_resource_usage 1.3.0 OK
```

## 示例2：启用CPU和磁盘监控

默认仅监控内存，通过配置文件启用CPU和磁盘：

```python
# ~/.jupyter/jupyter_server_config.py
c = get_config()

# 启用CPU使用率追踪
c.ResourceUseDisplay.track_cpu_percent = True

# 启用磁盘用量追踪
c.ResourceUseDisplay.track_disk_usage = True
```

重启JupyterLab后，状态栏显示：

```
| Disk: 1.50 / 10.00 GB | CPU: 12.00 % | Mem: 256.00 / 1024.00 MB
```

## 示例3：配置资源限制与警告

```python
# ~/.jupyter/jupyter_server_config.py
c = get_config()

# 设置内存限制为4GB（字节单位）
c.ResourceUseDisplay.mem_limit = 4 * 1024 * 1024 * 1024  # 4GB

# 设置CPU限制为2核（200%）
c.ResourceUseDisplay.cpu_limit = 200

# 当剩余资源低于15%时警告（默认10%）
c.ResourceUseDisplay.mem_warning_threshold = 0.15
c.ResourceUseDisplay.cpu_warning_threshold = 0.15
c.ResourceUseDisplay.disk_warning_threshold = 0.15

# 启用CPU和磁盘
c.ResourceUseDisplay.track_cpu_percent = True
c.ResourceUseDisplay.track_disk_usage = True
```

效果：
- 状态栏显示 `Mem: 3.20 / 4.00 GB`
- 内存使用超过3.4GB（85%）时状态栏变为红底红字
- CPU使用超过170%（85%）时同样触发警告

## 示例4：动态内存限制（Callable）

根据系统内存动态计算显示限制：

```python
import psutil

def dynamic_mem_limit(rss, pss):
    """显示限制为系统总内存的80%"""
    total = psutil.virtual_memory().total
    return int(total * 0.8)

c.ResourceUseDisplay.mem_limit = dynamic_mem_limit
```

## 示例5：启用顶栏进度条指示器

1. 打开 **Settings → Settings Editor**
2. 选择 **Resource Usage Indicator**
3. 勾选 **"Enable resource usage indicators"**
4. 可调整刷新间隔（默认5000ms）和标签文本
5. 刷新浏览器页面

顶栏右侧将显示：
- 蓝色CPU进度条（点击可切换Sparklines趋势图）
- 绿色内存进度条
- 紫色磁盘进度条（需启用磁盘监控）

进度条颜色规则：
- <50%：基础颜色
- 50-80%：橙色
- >80%：红色

## 示例6：查看单个内核资源

1. 确认ipykernel版本 >= 6.9.0：
```bash
pip show ipykernel | grep Version
# Version: 6.29.0
```

2. 打开或新建一个Notebook
3. 点击左侧边栏的内存图标（Kernel Resource Usage面板）
4. 面板显示：
   - Notebook路径
   - Kernel ID和Host
   - 该内核的CPU%和Memory使用量
   - 宿主机CPU和内存信息（可通过show_host_usage隐藏）

## 示例7：Docker容器中部署

在Dockerfile中设置内存限制环境变量：

```dockerfile
FROM jupyter/base-notebook:latest

# 安装jupyter-resource-usage
RUN pip install jupyter-resource-usage

# 启用CPU和磁盘监控
RUN echo "c.ResourceUseDisplay.track_cpu_percent = True" >> /etc/jupyter/jupyter_server_config.py && \
    echo "c.ResourceUseDisplay.track_disk_usage = True" >> /etc/jupyter/jupyter_server_config.py

# 容器内存限制（JupyterHub/k8s会自动设置MEM_LIMIT环境变量）
# 手动设置示例：
ENV MEM_LIMIT=2147483648  # 2GB
```

使用docker运行时传递内存限制：

```bash
docker run -m 2g -e MEM_LIMIT=2147483648 -p 8888:8888 my-jupyter-image
```

状态栏将自动显示容器内存限制：`Mem: 512.00 / 2048.00 MB`

## 示例8：命令行参数快速启用

```bash
# 临时启用CPU和磁盘追踪
jupyter lab \
  --ResourceUseDisplay.track_cpu_percent=True \
  --ResourceUseDisplay.track_disk_usage=True \
  --ResourceUseDisplay.mem_limit=2147483648 \
  --ResourceUseDisplay.enable_prometheus_metrics=False
```

## 示例9：调用REST API

### 获取服务器总资源指标

```bash
# 获取内存指标（默认）
curl -s http://localhost:8888/api/metrics/v1 \
  -H "Authorization: token <your-token>" | jq .
```

响应：
```json
{
  "rss": 268435456,
  "limits": {
    "memory": {
      "rss": 1073741824,
      "pss": 1073741824
    }
  }
}
```

### 获取单个内核指标

```bash
# 先获取kernel列表
KERNEL_ID=$(jupyter kernel list --json | jq -r '.[0].id')

# 查询该内核资源
curl -s "http://localhost:8888/api/metrics/v1/kernel_usage/get_usage/$KERNEL_ID" \
  -H "Authorization: token <your-token>" | jq .
```

响应：
```json
{
  "content": {
    "hostname": "jupyter-server",
    "pid": 42,
    "kernel_cpu": 12.5,
    "kernel_memory": 134217728,
    "host_cpu_percent": 25.3,
    "cpu_count": 4,
    "host_virtual_memory": {
      "total": 8589934592,
      "available": 4294967296,
      "percent": 50.0
    }
  },
  "kernel_id": "a1b2c3d4-..."
}
```

## 示例10：禁用Prometheus指标（解决卡顿）

如果遇到UI卡顿问题，禁用Prometheus指标：

```python
# ~/.jupyter/jupyter_server_config.py
c = get_config()
c.ResourceUseDisplay.enable_prometheus_metrics = False
```

或命令行：
```bash
jupyter lab --ResourceUseDisplay.enable_prometheus_metrics=False
```

## 示例11：多租户环境隐藏宿主机信息

```python
c.ResourceUseDisplay.show_host_usage = False
```

此时内核侧边栏只显示该内核自身的资源，不显示宿主机CPU和内存总量。

## 相关概念

- [安装与启用](../concepts/01-installation.md)
- [配置系统详解](../concepts/05-configuration.md)
- [后端API与指标采集](../concepts/03-backend-api.md)
- [内核资源监控](../concepts/04-kernel-usage.md)
- [Prometheus指标集成](../concepts/10-prometheus.md)
