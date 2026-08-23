---
type: Concept
title: 后端API与指标采集
description: ApiHandler实现、psutil进程树遍历、内存RSS/PSS采集、CPU百分比计算、磁盘用量获取、API响应格式、线程池设计
tags: [jupyter-resource-usage, api, psutil, metrics, backend, tornado, rss, pss]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 后端API与指标采集

后端API的核心是 `api.py` 中的 `ApiHandler` 类，它继承自 `jupyter_server.base.handlers.APIHandler`，处理 `/api/metrics/v1` 端点的GET请求。

## ApiHandler 类结构

```python
class ApiHandler(APIHandler):
    executor = ThreadPoolExecutor(max_workers=5)
    _cached_processes = {}  # 类变量，缓存Process实例
```

关键设计：
- **线程池**：`ThreadPoolExecutor(max_workers=5)` 用于CPU百分比的阻塞计算
- **进程缓存**：`_cached_processes` 是类级字典，缓存 psutil.Process 实例。这是因为 `cpu_percent()` 方法需要比较两次调用之间的CPU时间差，首次调用总是返回0

## GET 请求处理流程

`get()` 方法是 `@web.authenticated` 装饰的异步方法，执行以下步骤：

### 步骤1：获取配置与进程列表

```python
config = self.settings["jupyter_resource_usage_display_config"]
cur_process = psutil.Process()
all_processes = [cur_process] + cur_process.children(recursive=True)
```

- `cur_process` 是 Jupyter Server 主进程
- `children(recursive=True)` 递归获取所有子进程（包括各个Kernel进程、Terminal进程等）
- `all_processes` 是完整的进程树列表

### 步骤2：更新Process缓存

```python
cached = [ApiHandler._cached_processes.get(p.pid, p) for p in all_processes]
ApiHandler._cached_processes = {p.pid: p for p in cached}
```

对每个进程，如果缓存中已有对应PID的Process实例则复用，否则使用新创建的实例。缓存机制确保 `cpu_percent()` 有历史数据可比。

### 步骤3：采集内存信息

```python
rss = 0
pss = None
for p in all_processes:
    try:
        info = p.memory_full_info()
        if hasattr(info, "pss"):
            pss = (pss or 0) + info.pss
        rss += info.rss
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        pass
```

- 遍历所有进程，调用 `memory_full_info()` 获取详细内存信息
- **RSS**（Resident Set Size）：进程在RAM中实际占用的内存，所有平台支持
- **PSS**（Proportional Set Size）：Linux特有，按比例分摊共享库内存，比RSS更准确
- PSS通过 `hasattr(info, "pss")` 检测可用性（Linux上才有）
- 异常处理：进程可能在遍历期间退出（NoSuchProcess）或无权限访问（AccessDenied），静默跳过

### 步骤4：确定内存限制

```python
if callable(config.mem_limit):
    mem_limit = config.mem_limit(rss=rss, pss=pss)
else:
    mem_limit = config.mem_limit
```

`mem_limit` 支持两种模式：
- **整数**：固定的字节数限制
- **可调用对象**：接收 `rss` 和 `pss` 参数，动态计算限制值

### 步骤5：构建内存limits与warning

```python
limits = {"memory": {"rss": mem_limit, "pss": mem_limit}}
if config.mem_limit and config.mem_warning_threshold != 0:
    limits["memory"]["warn"] = (mem_limit - rss) < (mem_limit * config.mem_warning_threshold)
```

Warning 逻辑：当剩余内存 `(mem_limit - rss)` 小于 `mem_limit * threshold` 时触发警告。例如mem_limit=1GB，threshold=0.1，当使用超过900MB时警告。

### 步骤6：可选采集CPU信息

```python
if config.track_cpu_percent:
    cpu_count = psutil.cpu_count()
    cpu_percent = await self._get_cpu_percent(cached)
    # ... 设置limits["cpu"]和warning
    metrics.update(cpu_percent=cpu_percent, cpu_count=cpu_count)
```

CPU采集默认**关闭**，需 `track_cpu_percent=True` 启用。

`_get_cpu_percent()` 使用 `@run_on_executor` 装饰器在ThreadPoolExecutor中运行：

```python
@run_on_executor
def _get_cpu_percent(self, all_processes):
    def get_cpu_percent(p):
        try:
            return p.cpu_percent()
        except:
            return 0
    return sum([get_cpu_percent(p) for p in all_processes])
```

- 对每个进程调用 `cpu_percent()`（利用缓存的Process实例），求和
- 异常时返回0（进程可能已死亡）

### 步骤7：可选采集磁盘信息

```python
if config.track_disk_usage:
    try:
        disk_info = psutil.disk_usage(config.disk_path)
    except Exception:
        pass
    else:
        metrics.update(disk_used=disk_info.used, disk_total=disk_info.total)
        limits["disk"] = {"disk": disk_info.total}
        # ... warning逻辑
```

磁盘采集默认**关闭**，需 `track_disk_usage=True` 启用。监控 `disk_path`（默认 `/home/jovyan`，可从HOME环境变量读取）所在分区。

### 步骤8：返回JSON响应

```python
self.write(json.dumps(metrics))
```

## API响应格式

### 基础响应（仅内存，默认配置）

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

### 启用CPU后的响应

```json
{
  "rss": 268435456,
  "pss": 256000000,
  "limits": {
    "memory": {"rss": 1073741824, "pss": 1073741824, "warn": false},
    "cpu": {"cpu": 400, "warn": false}
  },
  "cpu_percent": 25.6,
  "cpu_count": 4
}
```

### 完整响应（内存+CPU+磁盘）

```json
{
  "rss": 268435456,
  "pss": 256000000,
  "limits": {
    "memory": {"rss": 1073741824, "pss": 1073741824, "warn": false},
    "cpu": {"cpu": 400, "warn": false},
    "disk": {"disk": 10737418240, "warn": true}
  },
  "cpu_percent": 25.6,
  "cpu_count": 4,
  "disk_used": 9663676416,
  "disk_total": 10737418240
}
```

## 字段说明

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `rss` | number | bytes | 进程树常驻内存总和（所有平台） |
| `pss` | number | bytes | 进程树比例共享内存总和（仅Linux，可选） |
| `cpu_percent` | number | percent | CPU使用率百分比（占一个核心的百分比，可>100%） |
| `cpu_count` | number | count | 系统CPU核心数 |
| `disk_used` | number | bytes | 磁盘已用空间 |
| `disk_total` | number | bytes | 磁盘总空间 |
| `limits.memory.rss/pss` | number | bytes | 内存显示限制（非强制限制） |
| `limits.memory.warn` | boolean | - | 内存警告状态 |
| `limits.cpu.cpu` | number | percent | CPU显示限制（默认100*cpu_count） |
| `limits.cpu.warn` | boolean | - | CPU警告状态 |
| `limits.disk.disk` | number | bytes | 磁盘总容量 |
| `limits.disk.warn` | boolean | - | 磁盘警告状态 |

## PSUtilMetricsLoader：通用指标采集引擎

`metrics.py` 中的 `PSUtilMetricsLoader` 是 Prometheus 集成和自定义指标的底层引擎：

```python
class PSUtilMetricsLoader:
    def __init__(self, server_app: ServerApp): ...
    def process_metric(self, name, args=[], kwargs={}, attribute=None): ...
    def system_metric(self, name, args=[], kwargs={}, attribute=None): ...
    def get_metric_values(self, metrics, metric_type): ...
    def metrics(self, process_metrics, system_metrics): ...
    def memory_metrics(self): ...
    def cpu_metrics(self): ...
    def disk_metrics(self): ...
```

### PSUtilMetric 自定义TraitType

`config.py` 中定义的 `PSUtilMetric` 允许通过配置灵活指定要采集的psutil指标：

```python
class PSUtilMetric(TraitType):
    """A trait describing the format to specify a metric from the psutil package"""
    def validate(self, obj, value):
        if isinstance(value, dict):
            keys = list(value.keys())
            if "name" in keys:
                keys.remove("name")
                if all(key in ["args", "kwargs", "attribute"] for key in keys):
                    return value
        self.error(obj, value)
```

每个PSUtilMetric是一个字典，支持以下键：
- `name`（必填）：psutil函数/方法名
- `args`：位置参数列表
- `kwargs`：关键字参数字典
- `attribute`：如果返回named tuple，指定要提取的属性名

### 默认指标配置

```python
process_memory_metrics = [{"name": "memory_info", "attribute": "rss"}]
system_memory_metrics = [{"name": "virtual_memory", "attribute": "total"}]
process_cpu_metrics = [{"name": "cpu_percent", "kwargs": {"interval": 0.05}}]
system_cpu_metrics = [{"name": "cpu_count"}]
system_disk_metrics = [
    {"name": "disk_usage", "args": [disk_path], "attribute": "total"},
    {"name": "disk_usage", "args": [disk_path], "attribute": "used"},
]
```

## 内存单位：RSS vs PSS

| 指标 | 全称 | 平台支持 | 含义 |
|------|------|---------|------|
| RSS | Resident Set Size | 所有平台 | 进程占用的物理内存总和，包含共享库的全部大小 |
| PSS | Proportional Set Size | 仅Linux | 按比例分摊共享内存后的实际占用，更准确但获取较慢 |

前端优先使用PSS：`const numBytes = value.pss ?? value.rss;`

## 相关概念

- [架构总览](02-architecture.md) — 整体架构与数据流
- [内核资源监控](04-kernel-usage.md) — KernelUsageHandler与ZMQ通信
- [配置系统详解](05-configuration.md) — 配置指标采集选项
- [Prometheus指标集成](10-prometheus.md) — PSUtilMetricsLoader在Prometheus中的应用
