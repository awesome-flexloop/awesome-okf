---
type: Facts
okf_version: "0.2"
title: "jupyter-resource-usage 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, resource-usage, monitoring, python, typescript]
sources:
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter_resource_usage/api.py
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter_resource_usage/config.py
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter_resource_usage/metrics.py
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter_resource_usage/prometheus.py
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter_resource_usage/server_extension.py
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/packages/labextension/src/index.ts
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/packages/labextension/src/model.ts
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/packages/labextension/src/widget.tsx
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/pyproject.toml
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter-config/jupyter_server_config.d/jupyter_resource_usage.json
---
# jupyter-resource-usage 源码事实清单

## 项目元数据

- F-001: pyproject.toml:10-11 — 包名为 `jupyter-resource-usage`，描述为 "Jupyter Extension to show resource usage"
- F-002: pyproject.toml:13 — 要求 Python >= 3.10
- F-003: pyproject.toml:38-43 — 运行时依赖 `jupyter_server>=2.0`、`prometheus_client`、`psutil>=5.6`、`pyzmq>=19`
- F-004: jupyter_resource_usage/_version.py:1 — `__version__ = "1.3.0"`

## Python 后端 - 服务器扩展入口与路由

- F-005: jupyter_resource_usage/__init__.py:7-8 — `_jupyter_labextension_paths()` 返回 `{"src": "labextension", "dest": "@jupyter-server/resource-usage"}`
- F-006: jupyter_resource_usage/__init__.py:11-15 — `_jupyter_server_extension_points()` 返回 `{"module": "jupyter_resource_usage"}`
- F-007: jupyter_resource_usage/server_extension.py:11-16 — `load_jupyter_server_extension()` 实例化 `ResourceUseDisplay(parent=server_app)` 并写入 `web_app.settings["jupyter_resource_usage_display_config"]`
- F-008: jupyter_resource_usage/server_extension.py:19-32 — 注册两条路由：`base_url/api/metrics/v1` → `ApiHandler`，`base_url/api/metrics/v1/kernel_usage/get_usage/(.+)$` → `KernelUsageHandler`（`(.+)` 捕获 kernel_id）

## Python 后端 - ApiHandler 指标采集

- F-009: jupyter_resource_usage/api.py:24-28 — `ApiHandler` 继承 `jupyter_server.base.handlers.APIHandler`，`executor = ThreadPoolExecutor(max_workers=5)`，`_cached_processes` 类属性缓存 psutil.Process 实例使 `cpu_percent()` 能对比上次测量
- F-010: jupyter_resource_usage/api.py:37-38 — 采集对象为当前进程 `psutil.Process()` 及其全部递归子进程 `children(recursive=True)`
- F-011: jupyter_resource_usage/api.py:45-54 — 遍历进程调用 `memory_full_info()` 累加 rss，`hasattr(info, "pss")` 为真时累加 pss；捕获 `psutil.NoSuchProcess`/`psutil.AccessDenied` 并跳过
- F-012: jupyter_resource_usage/api.py:56-65 — `mem_limit` 为 callable 时以 `rss=, pss=` 调用，否则取 Int；`limits["memory"]` 含 rss/pss/warn，warn 判定式 `(mem_limit - rss) < (mem_limit * mem_warning_threshold)`
- F-013: jupyter_resource_usage/api.py:72-83 — `track_cpu_percent` 为 True 时返回 `cpu_percent`/`cpu_count`，`cpu_limit != 0` 时构造 `limits["cpu"]` 及 warn
- F-014: jupyter_resource_usage/api.py:86-97 — `track_disk_usage` 为 True 时调用 `psutil.disk_usage(config.disk_path)`，异常被吞掉；成功时写入 `disk_used`/`disk_total` 与 `limits["disk"]` 及 warn
- F-015: jupyter_resource_usage/api.py:99-111 — `self.write(json.dumps(metrics))` 输出 JSON；`_get_cpu_percent` 带 `@run_on_executor` 在线程池中 `sum` 各进程 `cpu_percent()`

## Python 后端 - KernelUsageHandler

- F-016: jupyter_resource_usage/api.py:14-21 — `USAGE_IS_SUPPORTED` 由 `ipykernel.__version__ >= 6.9.0` 判定，ImportError 时为 False 且 `IPYKERNEL_VERSION = None`
- F-017: jupyter_resource_usage/api.py:117-128 — 不支持时返回 `{"content": {"reason": "not_supported", "kernel_version": IPYKERNEL_VERSION}}`
- F-018: jupyter_resource_usage/api.py:132-140 — 经 `km.pinned_superclass.get_kernel(km, kernel_id)` 获取内核，构造 `session.msg("usage_request", {})` 经 `control_channel.send()` 发出
- F-019: jupyter_resource_usage/api.py:141-152 — 使用 `zmq.asyncio.Poller()` 注册 control_socket，`timeout_ms = 10_000`；超时返回 `{"content": {"reason": "timeout", "timeout_ms": ...}, "kernel_id": ...}`
- F-020: jupyter_resource_usage/api.py:154-164 — 成功时 `control_channel.get_msg(timeout=0)` 读取响应（可返回 Future），附加 `kernel_id` 与 `host_usage_flag=config.show_host_usage`，随后 `client.stop_channels()`

## Python 后端 - 配置项 (ResourceUseDisplay)

- F-021: jupyter_resource_usage/config.py:21-33 — `PSUtilMetric` TraitType 校验 dict 必须含 `name`，其余键仅允许 `args`/`kwargs`/`attribute`
- F-022: jupyter_resource_usage/config.py:50-58 — `process_memory_metrics` 默认 `[{"name": "memory_info", "attribute": "rss"}]`，`system_memory_metrics` 默认 `[{"name": "virtual_memory", "attribute": "total"}]`
- F-023: jupyter_resource_usage/config.py:60-67 — `process_cpu_metrics` 默认 `[{"name": "cpu_percent", "kwargs": {"interval": 0.05}}]`，`system_cpu_metrics` 默认 `[{"name": "cpu_count"}]`
- F-024: jupyter_resource_usage/config.py:74-80 — `system_disk_metrics` 默认两个 disk_usage 项，args 均为 `[disk_path]`，attribute 分别为 total/used
- F-025: jupyter_resource_usage/config.py:82-93 — `mem_warning_threshold` Float 默认 0.1，help 说明置 0 关闭告警
- F-026: jupyter_resource_usage/config.py:95-110 — `mem_limit` 为 `Union(Int, Callable)`，help 说明"不实际限制内存"；默认值读取 `os.environ.get("MEM_LIMIT", 0)`
- F-027: jupyter_resource_usage/config.py:112-117 — `track_cpu_percent` Bool 默认 False
- F-028: jupyter_resource_usage/config.py:132-147 — `cpu_limit` 为 `Union(Float, Callable)` 默认 0，help 说明"不实际限制 CPU"；默认值读取 `os.environ.get("CPU_LIMIT", 0)`
- F-029: jupyter_resource_usage/config.py:149-158 — `track_disk_usage` Bool 默认 False；`disk_path` 默认值读取 `os.environ.get("HOME", "/home/jovyan")`
- F-030: jupyter_resource_usage/config.py:173-185 — `enable_prometheus_metrics` 默认 True；`show_host_usage` 默认 True

## Python 后端 - psutil 指标加载器

- F-031: jupyter_resource_usage/metrics.py:9-14 — `PSUtilMetricsLoader` 从 `server_app.web_app.settings` 读取 display config
- F-032: jupyter_resource_usage/metrics.py:16-27 — `get_process_metric_value` 用 `getattr(process, name)(*args, **kwargs)` 调用方法，`attribute` 非空时取 named tuple 字段，异常返回 0
- F-033: jupyter_resource_usage/metrics.py:29-40 — `process_metric` 对当前进程+递归子进程求和，psutil 为 None 时返回 None
- F-034: jupyter_resource_usage/metrics.py:56-66 — `get_metric_values` 按 `metric_types` 字典分发 process/system，`attribute` 存在时 name 拼接为 `name_attribute`
- F-035: jupyter_resource_usage/metrics.py:68-78 — `metrics()` 组合 process 与 system 指标，任一值为 None 时整体返回 None

## Python 后端 - Prometheus 指标

- F-036: jupyter_resource_usage/prometheus.py:21-32 — 注册 6 个 Gauge：`total_memory_usage`/`max_memory_usage`/`total_cpu_usage`/`max_cpu_usage`/`max_disk_usage`/`current_disk_usage`
- F-037: jupyter_resource_usage/prometheus.py:50-61 — `apply_memory_limit`：callable 以 `rss=` 调用；`mem_limit > 0` 取配置值；否则取 `virtual_memory_total`
- F-038: jupyter_resource_usage/prometheus.py:63-74 — `apply_cpu_limit`：callable 以 `cpu_percent=` 调用；`cpu_limit > 0.0` 取配置值；否则返回 `100.0 * cpu_count`

## TS 前端 - 插件与设置

- F-039: packages/labextension/src/index.ts:70-74 — `resourceStatusPlugin` id 为 `@jupyter-server/resource-usage:status-item`，`autoStart: true`，requires `ITranslator`
- F-040: packages/labextension/src/index.ts:96-103 — `statusBar.registerStatusItem` 注册状态栏项，`align: 'left'`、`rank: 2`、`isActive: () => item.model.metricsAvailable`
- F-041: packages/labextension/src/index.ts:111-114 — `systemMonitorPlugin` id 为 `@jupyter-server/resource-usage:topbar-item`，requires `IToolbarWidgetRegistry`，optional `ISettingRegistry`
- F-042: packages/labextension/src/index.ts:129-143 — 从 `settingRegistry.load(systemMonitorPlugin.id)` 读取 `enable`/`refreshRate`/`cpu.label`/`memory.label`/`disk.label`
- F-043: packages/labextension/src/index.ts:157-175 — 通过 `toolbarRegistry.addFactory('TopBar', ...)` 分别注册 cpu/memory/disk 工厂
- F-044: packages/labextension/src/index.ts:179-183 — `kernelUsagePlugin` id 为 `@jupyter-server/resource-usage:kernel-panel-item`，optional `[ICommandPalette, ILabShell, IConsoleTracker]`，注册命令 `kernel-usage:get`

## TS 前端 - 数据模型与请求

- F-045: packages/labextension/src/model.ts:21 — `N_BUFFER = 20`，模型仅保留最近 20 条历史值
- F-046: packages/labextension/src/model.ts:63-73 — 使用 `Poll` 轮询 `/api/metrics/v1`，`frequency.interval = options.refreshRate`、`backoff: true`、`max: 300 * 1000`、`standby: 'when-hidden'`
- F-047: packages/labextension/src/model.ts:233-247 — `_updateMetricsValues` 中 `numBytes = value.pss ?? value.rss`，内存 limit 取 `memoryLimits?.pss ?? memoryLimits?.rss`
- F-048: packages/labextension/src/model.ts:402-417 — `Private.factory` 请求 `URLExt.join(serverSettings.baseUrl, 'api/metrics/v1')`，非 ok 响应返回 null

## jupyter-config 注册与构建发布

- F-049: jupyter-config/jupyter_server_config.d/jupyter_resource_usage.json:2-5 — `ServerApp.jpserver_extensions` 中 `"jupyter_resource_usage": true` 启用服务器扩展
- F-050: jupyter-config/nbconfig/notebook.d/jupyter_resource_usage.json:2-3 — `load_extensions` 中 `"jupyter_resource_usage/main": true` 启用 nbextension
- F-051: pyproject.toml:62-68 — hatch wheel `shared-data` 将 static→`share/jupyter/nbextensions/`、labextension→`share/jupyter/labextensions/`、install.json→labextensions、jupyter-config 三目录→`etc/jupyter/` 对应位置

## TS 前端 - 指标视图组件

- F-052: packages/labextension/src/resourceUsage.tsx:19 — `ResourceUsageStatus` 继承 `VDomRenderer<ResourceUsage.Model>`
- F-053: packages/labextension/src/resourceUsage.tsx:36-51 — `memoryLimit === null` 时文本为 "标签 当前值 单位"，否则为 "标签 当前值 / 上限 单位"
- F-054: packages/labextension/src/resourceUsage.tsx:64-78 与 text.ts:6-15 — `usageWarnings.hasWarning` 为真时 `TextItem` 追加 `resourceItem` 样式类（`backgroundColor: '#FFD2D2'`、`color: '#D8000C'`）

## TS 前端 - Kernel Usage 侧栏

- F-055: packages/labextension/src/panel.ts:13 — `KernelUsagePanel` 继承 `StackedPanel`，id 为 `kernelusage-panel-id`
- F-056: packages/labextension/src/tracker.ts:10-46 — `KernelWidgetTracker` 监听 `labShell.currentChanged` 或 notebook/console tracker 的 `currentChanged`，对带内核的 widget 发射信号；构造时对已有当前 widget 兜底赋值
- F-057: packages/labextension/src/types.ts:22-26 — `hasKernelSession` 以 `instanceof ConsolePanel || instanceof NotebookPanel` 判定 widget 是否带内核
- F-058: packages/labextension/src/widget.tsx:36 — `POLL_INTERVAL_SEC = 5`，内核侧栏每 5 秒轮询一次
- F-059: packages/labextension/src/widget.tsx:151-178 — `requestUsage` 请求 `get_usage/<kid>`，用 `kernelIdRef` 比对丢弃过期响应；`data.content.reason` 存在时转入 `not_supported`/`timeout`/`no_kernel` 等空白态
- F-060: packages/labextension/src/widget.tsx:310-359 — `host_usage_flag` 为真时渲染 "Host CPU" 与 "Host Virtual Memory" 区块（active/available/free/inactive/percent/total/wired）
