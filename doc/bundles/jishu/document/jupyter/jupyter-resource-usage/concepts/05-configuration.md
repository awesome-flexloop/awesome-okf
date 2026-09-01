---
type: Concept
title: 配置系统详解
description: ResourceUseDisplay所有traitlets配置项、环境变量、命令行参数、配置文件方法、mem_limit/cpu_limit Callable动态限制、PSUtilMetric自定义指标
tags: [jupyter-resource-usage, configuration, traitlets, mem-limit, cpu-limit, environment-variables]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 配置系统详解

jupyter-resource-usage 使用 Jupyter 生态标准的 **traitlets** 配置系统，支持三种配置方式：环境变量、命令行参数、配置文件。

## 配置入口类：ResourceUseDisplay

所有配置项定义在 `config.py` 的 `ResourceUseDisplay` 类中，继承自 `traitlets.config.Configurable`。

### 配置访问方式

在API Handler中通过 settings 获取配置实例：

```python
config = self.settings["jupyter_resource_usage_display_config"]
```

在 `load_jupyter_server_extension()` 中创建并存入settings：

```python
resuseconfig = ResourceUseDisplay(parent=server_app)
server_app.web_app.settings["jupyter_resource_usage_display_config"] = resuseconfig
```

## 完整配置项列表

### 内存相关配置

| 配置项 | 类型 | 默认值 | 环境变量 | 说明 |
|--------|------|--------|---------|------|
| `mem_limit` | Int / Callable | `MEM_LIMIT` 或 0 | `MEM_LIMIT` | 内存显示限制（字节），0表示显示系统最大内存 |
| `mem_warning_threshold` | Float | 0.1 | - | 内存警告阈值（剩余比例），0表示禁用 |

#### mem_limit 详解

`mem_limit` 支持三种模式：

1. **整数（字节数）**：固定的显示限制值
2. **Callable函数**：动态计算限制，接收 `rss` 和 `pss` 关键字参数
3. **0（默认）**：显示系统总内存（`psutil.virtual_memory().total`）

默认值从 `MEM_LIMIT` 环境变量读取，这是 JupyterHub 等平台自动设置的。

> ⚠️ **重要**：`mem_limit` 仅影响**显示**，不会实际限制用户的内存使用！

#### mem_warning_threshold 详解

默认值0.1表示当剩余内存不足10%时触发警告。例如1GB内存限制，使用超过900MB时状态栏变为红底红字。

设置为0可禁用警告。

### CPU相关配置

| 配置项 | 类型 | 默认值 | 环境变量 | 说明 |
|--------|------|--------|---------|------|
| `track_cpu_percent` | Bool | False | - | 是否启用CPU使用率追踪 |
| `cpu_limit` | Float / Callable | `CPU_LIMIT` 或 0 | `CPU_LIMIT` | CPU显示限制（百分比，如400表示4核），0表示100*cpu_count |
| `cpu_warning_threshold` | Float | 0.1 | - | CPU警告阈值，0表示禁用 |

#### cpu_limit 详解

- 单位是"百分比*核心数"，例如4核机器的100%是400
- Callable模式接收 `cpu_percent` 参数
- 默认0时显示为 `100.0 * cpu_count`（即全部核心）

#### 启用CPU追踪

CPU追踪默认关闭，需显式启用：

```python
c = get_config()
c.ResourceUseDisplay.track_cpu_percent = True
```

或命令行：

```bash
jupyter lab --ResourceUseDisplay.track_cpu_percent=True
```

### 磁盘相关配置

| 配置项 | 类型 | 默认值 | 环境变量 | 说明 |
|--------|------|--------|---------|------|
| `track_disk_usage` | Bool | False | - | 是否启用磁盘用量追踪 |
| `disk_path` | Unicode / Callable | `$HOME` 或 `/home/jovyan` | `HOME` | 要监控的分区路径 |
| `disk_warning_threshold` | Float | 0.1 | - | 磁盘警告阈值，0表示禁用 |

磁盘监控默认也关闭，需 `track_disk_usage=True` 启用。默认监控用户主目录所在分区。

### Prometheus相关配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_prometheus_metrics` | Bool | True | 是否启用Prometheus指标推送 |

存在已知UI卡顿bug（issue #123），可设为False禁用：

```bash
jupyter lab --ResourceUseDisplay.enable_prometheus_metrics=False
```

### 宿主机信息配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `show_host_usage` | Bool | True | 内核侧边栏是否显示宿主机CPU和虚拟内存信息 |

在多租户环境中可设为False，隐藏宿主机资源细节。

### 自定义PSUtil指标配置

这些List类型的配置项允许高级用户自定义要采集的psutil指标：

| 配置项 | 默认值 | 用途 |
|--------|--------|------|
| `process_memory_metrics` | `[{"name": "memory_info", "attribute": "rss"}]` | 进程级内存指标 |
| `system_memory_metrics` | `[{"name": "virtual_memory", "attribute": "total"}]` | 系统级内存指标 |
| `process_cpu_metrics` | `[{"name": "cpu_percent", "kwargs": {"interval": 0.05}}]` | 进程级CPU指标 |
| `system_cpu_metrics` | `[{"name": "cpu_count"}]` | 系统级CPU指标 |
| `process_disk_metrics` | `[]` | 进程级磁盘指标 |
| `system_disk_metrics` | disk_usage total + used | 系统级磁盘指标 |

每个指标项是PSUtilMetric字典格式：

```python
{
    "name": "psutil_function_name",  # psutil函数/方法名
    "args": [positional_args],       # 位置参数（可选）
    "kwargs": {"key": "value"},      # 关键字参数（可选）
    "attribute": "attr_name"         # 返回named tuple时选择属性（可选）
}
```

## 配置方式

### 方式1：配置文件（推荐）

生成或编辑 Jupyter 配置文件（`~/.jupyter/jupyter_server_config.py`）：

```python
c = get_config()

# 启用CPU和磁盘追踪
c.ResourceUseDisplay.track_cpu_percent = True
c.ResourceUseDisplay.track_disk_usage = True

# 设置内存限制为2GB
c.ResourceUseDisplay.mem_limit = 2 * 1024 * 1024 * 1024  # 2GB in bytes

# 设置CPU限制为2核
c.ResourceUseDisplay.cpu_limit = 200  # 2 cores * 100%

# 调整警告阈值为15%
c.ResourceUseDisplay.mem_warning_threshold = 0.15
c.ResourceUseDisplay.cpu_warning_threshold = 0.15
c.ResourceUseDisplay.disk_warning_threshold = 0.15

# 禁用Prometheus（避免已知卡顿bug）
c.ResourceUseDisplay.enable_prometheus_metrics = False

# 隐藏宿主机信息
c.ResourceUseDisplay.show_host_usage = False

# 设置磁盘监控路径
c.ResourceUseDisplay.disk_path = "/data"
```

### 方式2：命令行参数

```bash
jupyter lab \
  --ResourceUseDisplay.track_cpu_percent=True \
  --ResourceUseDisplay.track_disk_usage=True \
  --ResourceUseDisplay.mem_limit=2147483648 \
  --ResourceUseDisplay.mem_warning_threshold=0.15 \
  --ResourceUseDisplay.enable_prometheus_metrics=False
```

### 方式3：环境变量

仅 `mem_limit`、`cpu_limit`、`disk_path` 支持环境变量：

```bash
# JupyterHub等平台自动设置
export MEM_LIMIT=2147483648
export CPU_LIMIT=400
export HOME=/home/jovyan

jupyter lab
```

### 方式4：动态mem_limit（Callable）

`mem_limit` 和 `cpu_limit` 支持传入可调用对象实现动态限制：

```python
def dynamic_mem_limit(rss, pss):
    """根据当前使用量动态调整限制显示"""
    import psutil
    total = psutil.virtual_memory().total
    # 显示限制为系统内存的80%
    return int(total * 0.8)

c.ResourceUseDisplay.mem_limit = dynamic_mem_limit
```

## 前端设置（顶栏监控）

顶栏监控插件的设置通过 JupyterLab Settings Editor 配置，存储在用户设置中（非traitlets配置）：

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable` | boolean | false | 是否启用顶栏资源指示器 |
| `refreshRate` | number | 5000 | 刷新间隔（毫秒） |
| `memory.label` | string | "\| Mem: " | 内存指示器标签 |
| `cpu.label` | string | "CPU: " | CPU指示器标签 |
| `disk.label` | string | "\| Disk: " | 磁盘指示器标签 |

Schema定义在 `schema/topbar-item.json`，在Settings Editor中通过 **Settings → Settings Editor → Resource Usage Indicator** 访问。

## 相关概念

- [后端API与指标采集](03-backend-api.md) — 配置如何影响API响应
- [Prometheus指标集成](10-prometheus.md) — enable_prometheus_metrics配置
- [内核资源监控](04-kernel-usage.md) — show_host_usage配置
- [顶栏监控面板](07-topbar-monitor.md) — 前端设置编辑器配置
