---
type: Concept
title: Prometheus指标集成
description: PSUtilMetricsLoader与PSUtilMetricsLoaderMixin、Prometheus指标注册、process/process_cpu/process_memory/process_disk/system_cpu/system_memory/system_disk指标、已知卡顿bug
tags: [jupyter-resource-usage, prometheus, metrics-loader, psutil-metric, resource-metric, bug]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# Prometheus指标集成

jupyter-resource-usage 内置了 Prometheus 指标导出功能，通过 `PSUtilMetricsLoader` 类将 psutil 采集的资源数据注册为 Prometheus 指标，供监控系统抓取。

## 启用与禁用

Prometheus指标**默认启用**（`enable_prometheus_metrics=True`）。可通过配置禁用：

```python
c.ResourceUseDisplay.enable_prometheus_metrics = False
```

或命令行：

```bash
jupyter lab --ResourceUseDisplay.enable_prometheus_metrics=False
```

### 已知Bug（UI卡顿）

存在已知的UI卡顿问题（[issue #123](https://github.com/jupyter-server/jupyter-resource-usage/issues/123)），启用Prometheus指标后在某些环境下会导致前端界面卡顿。临时解决方法是设置 `enable_prometheus_metrics=False`。

## PSUtilMetricsLoaderMixin

Prometheus集成通过 `PSUtilMetricsLoaderMixin` mixin类实现，在 `load_jupyter_server_extension()` 中混入到ServerApp：

```python
from .prometheus import PSUtilMetricsLoaderMixin, PSUtilMetricsLoader

if "prometheus" in sys.modules:
    parent_logger = server_app.log
    
    class ResUseConfigurable(Configurable):
        cfg = Instance(ResourceUseDisplay)
    
    class ResUsePSUtilMetricsLoader(
        PSUtilMetricsLoaderMixin, server_app.__class__, ResUseConfigurable
    ):
        pass
    
    server_app.__class__ = ResUsePSUtilMetricsLoader
    server_app._jupyter_resuse_config = ResUseConfigurable(cfg=resuseconfig)
else:
    nbapp.log.debug("Prometheus metrics unavailable for Resource Usage Display")
```

关键设计：
1. 检查 `prometheus` 模块是否已加载（jupyter-server依赖prometheus_client）
2. 创建继承自 `PSUtilMetricsLoaderMixin` 和 `server_app.__class__` 的新类
3. 动态替换server_app的类，混入Prometheus指标加载能力
4. 如果prometheus不可用则静默跳过

## PSUtilMetricsLoader 核心类

`metrics.py` 中的 `PSUtilMetricsLoader` 是通用的psutil指标采集引擎：

### 初始化

```python
class PSUtilMetricsLoader:
    def __init__(self, server_app: ServerApp):
        self.config = server_app.config.ResourceUseDisplay if hasattr(server_app, "config") else server_app._jupyter_resuse_config.cfg
        self.server_app = server_app
        self.application = self.server_app.web_app
        self.process = psutil.Process()
        self.cpu_percent_metric = None
        self.thread_metrics_initialized = False
```

- 保存对ServerApp的引用
- 缓存psutil.Process实例（用于CPU百分比计算）
- 配置从ResourceUseDisplay读取

### 指标类型分类

指标分为三类，对应三个标签维度：
- `process`：单个Jupyter Server进程的指标
- `system`：整个系统（宿主机）的指标

### 指标注册

```python
def initialize_thread_metrics(self):
    p = self.process
    try:
        self.application.settings["cpu_gauge"] = Gauge(
            "process_cpu", "The current CPU percent (0.0 to 1.0) of the server process."
        )
        # ...注册其他Gauge指标
    finally:
        self.thread_metrics_initialized = True
```

### 指标采集方法

#### process_metric：进程级指标

```python
def process_metric(self, name: str, args: List[str] = [], kwargs: Dict[str,str] = {}, attribute: Union[str,None] = None):
    if name == "oneshot":
        # 特殊：使用psutil oneshot上下文批量采集
        with self.process.oneshot():
            return {name: self.process_metric(n, a, kw, attr) for name, (n, a, kw, attr) in kwargs.items()}
    res = getattr(self.process, name)(*args, **kwargs)
    if attribute is not None:
        res = getattr(res, attribute)
    return {name: res}
```

支持psutil的 `oneshot()` 上下文管理器，可在一次系统调用中采集多个指标，提升效率。

#### system_metric：系统级指标

```python
def system_metric(self, name: str, args: List[str] = [], kwargs: Dict[str,str] = {}, attribute: Union[str,None] = None):
    res = getattr(psutil, name)(*args, **kwargs)
    if attribute is not None:
        res = getattr(res, attribute)
    return {name: res}
```

直接调用psutil模块级函数（如 `psutil.cpu_count()`、`psutil.virtual_memory()`）。

#### metrics：批量采集

```python
def metrics(self, process_metrics: List[PSUtilMetric], system_metrics: List[PSUtilMetric]):
    # 进程指标（添加process_type="process"标签）
    for metric in process_metrics:
        for key, value in self.process_metric(**metric).items():
            yield [key, value, {"process_type": "process"}]
    
    # 系统指标（添加process_type="system"标签）
    for metric in system_metrics:
        for key, value in self.system_metric(**metric).items():
            yield [key, value, {"process_type": "system"}]
```

返回格式：`[key, value, labels_dict]` 三元组列表。

#### 便捷方法

```python
def memory_metrics(self):
    return self.metrics(self.config.process_memory_metrics, self.config.system_memory_metrics)

def cpu_metrics(self):
    return self.metrics(self.config.process_cpu_metrics, self.config.system_cpu_metrics)

def disk_metrics(self):
    return self.metrics(self.config.process_disk_metrics, self.config.system_disk_metrics)
```

### openmetrics：注册到Prometheus

```python
def openmetrics(self, parser, metrics, registry=REGISTRY):
    for v in metrics:
        # ...获取或创建Gauge
        gauge.labels(**v[2]).set(v[1])
```

将采集到的指标值设置到对应的Prometheus Gauge上。

## 默认Prometheus指标

### CPU指标

| 指标名 | 类型 | 来源 | 标签 |
|--------|------|------|------|
| `process_cpu` | Gauge | process.cpu_percent() | process_type="process" |
| `system_cpu` | Gauge | psutil.cpu_count() | process_type="system" |

### 内存指标

| 指标名 | 类型 | 来源 | 标签 |
|--------|------|------|------|
| `process_memory` | Gauge | process.memory_info().rss | process_type="process" |
| `system_memory` | Gauge | psutil.virtual_memory().total | process_type="system" |

### 磁盘指标

| 指标名 | 类型 | 来源 | 标签 |
|--------|------|------|------|
| `process_disk` | Gauge | （默认空列表） | process_type="process" |
| `system_disk_total` | Gauge | psutil.disk_usage(path).total | process_type="system" |
| `system_disk_used` | Gauge | psutil.disk_usage(path).used | process_type="system" |

## PSUtilMetric配置格式

自定义指标通过配置文件添加到对应的List配置项中：

```python
# 添加进程级磁盘IO指标
c.ResourceUseDisplay.process_disk_metrics = [
    {"name": "io_counters", "attribute": "read_bytes"},
    {"name": "io_counters", "attribute": "write_bytes"},
]

# 添加系统级内存可用量指标
c.ResourceUseDisplay.system_memory_metrics.append(
    {"name": "virtual_memory", "attribute": "available"}
)
```

### 支持的配置键

| 键 | 类型 | 必填 | 说明 |
|----|------|------|------|
| `name` | string | ✅ | psutil方法/函数名 |
| `args` | list | ❌ | 位置参数列表 |
| `kwargs` | dict | ❌ | 关键字参数字典 |
| `attribute` | string | ❌ | 从返回的named tuple中提取指定属性 |

### oneshot批量采集

特殊 `name="oneshot"` 支持在psutil oneshot上下文中一次性采集多个指标：

```python
{"name": "oneshot", "kwargs": {
    "memory": ("memory_info", [], {}, "rss"),
    "cpu_times": ("cpu_times", [], {}, "user"),
}}
```

这会减少系统调用次数，提升效率。

## 指标抓取端点

Prometheus指标通过 jupyter-server 内置的 `/metrics` 端点暴露，在标准的Prometheus metrics端口（通常是8888端口的 `/metrics` 路径）可抓取到以下资源指标：

```
# HELP process_cpu The current CPU percent (0.0 to 1.0) of the server process.
# TYPE process_cpu gauge
process_cpu{process_type="process"} 0.125
# HELP system_cpu ...
system_cpu{process_type="system"} 4
# HELP process_memory ...
process_memory{process_type="process"} 268435456
# HELP system_memory ...
system_memory{process_type="system"} 8589934592
```

## 相关概念

- [配置系统详解](05-configuration.md) — enable_prometheus_metrics等配置
- [后端API与指标采集](03-backend-api.md) — PSUtilMetricsLoader用于自定义指标
