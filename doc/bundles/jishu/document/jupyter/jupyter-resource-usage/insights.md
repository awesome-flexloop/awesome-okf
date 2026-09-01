---
type: Insights
okf_version: "0.2"
title: "jupyter-resource-usage 架构洞察"
generated: "2026-08-22"
tags: [jupyter, resource-usage, monitoring, python, typescript]
sources:
  - facts.md
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter_resource_usage/api.py
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter_resource_usage/config.py
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter_resource_usage/metrics.py
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/jupyter_resource_usage/prometheus.py
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/packages/labextension/src/index.ts
  - ../../../../../external/libs/jupyter/jupyter-resource-usage/packages/labextension/src/model.ts
---
# jupyter-resource-usage 架构洞察

## I-001：双通道指标采集架构——进程级聚合与内核级 ZMQ 会话

**类型**：架构模式
**关联事实**：F-008, F-009, F-010, F-011, F-015, F-016, F-017, F-018, F-019, F-020

**洞察**：该扩展在同一服务端并置了两套相互独立、语义不同的指标通道，由服务器扩展注册的两条路由承载（F-008）：`/api/metrics/v1` 对应进程级 `ApiHandler`，`/api/metrics/v1/kernel_usage/get_usage/<kernel_id>` 对应内核级 `KernelUsageHandler`。进程级通道直接内联 `psutil`：以 `psutil.Process()` 及全部递归子进程 `children(recursive=True)` 为采集对象（F-010），遍历调用 `memory_full_info()` 累加 rss、并在支持时累加 pss（F-011）；`_cached_processes` 类属性缓存 psutil.Process 实例，使 `cpu_percent()` 的"对比上次调用"增量语义能跨请求生效（F-009）。内核级通道则通过 ZMQ 向内核请求数据：先依赖 `ipykernel>=6.9.0` 判定支持性（F-016），经 `pinned_superclass.get_kernel` 获取内核、构造 `usage_request` 消息经 `control_channel` 发出（F-018），再以 `zmq.asyncio.Poller` + 10s 超时等待（F-019）。

两通道的数据来源、协议与失败语义完全不同：进程级是服务端主动读取操作系统进程表，输出 JSON（F-015）；内核级是内核进程内采集后经消息总线回传，超时与不支持分别返回 `timeout`/`not_supported` 两类 reason（F-017, F-019），成功响应附带 `kernel_id` 与 `host_usage_flag` 供前端区分归属与展示策略（F-020）。

```
                     jupyter-resource-usage (Jupyter Server 进程)
┌──────────────────────────────────────────────────────────────────────────┐
│ 通道 A：进程级（ApiHandler）                  通道 B：内核级（KernelUsageHandler）│
│  psutil.Process() + children(recursive=True) │  pinned_superclass.get_kernel(kid)│
│  ├─ memory_full_info() → rss / pss           │  control_channel.send(usage_request)│
│  ├─ cpu_percent()（缓存实例，增量语义）        │  zmq Poller + 10s 超时              │
│  └─ disk_usage(disk_path)                    │  timeout / not_supported 双 reason  │
│        │                                     │        │                           │
│        ▼                                     │        ▼                           │
│  GET /api/metrics/v1 → JSON (F-008, F-015)   │  GET .../get_usage/<kid> (F-008)   │
│        │                                     │  成功附带 kernel_id + host_usage_flag│
│        ▼                                     │        ▼                           │
│  前端 ResourceUsage.Model（Poll 轮询）         │  前端 KernelUsageWidget（5s 轮询）   │
└──────────────────────────────────────────────────────────────────────────┘
```

**复用价值**：当"整体使用量"与"单实例精确用量"语义不同时，可用双通道各自独立采集、前端统一汇聚。注意跨进程聚合时 psutil 实例缓存的增量语义陷阱；异步请求务必显式设置超时并向前端传递可区分的失败原因。

## I-002：配置驱动的声明式指标抽象——PSUtilMetric + PSUtilMetricsLoader

**类型**：设计决策
**关联事实**：F-021, F-022, F-023, F-024, F-031, F-032, F-033, F-034, F-035, F-036

**洞察**：扩展没有把指标采集逻辑硬编码进消费方，而是抽象为"指标描述 + 通用加载器"两层。`PSUtilMetric` trait 将每条指标描述为 `{"name", "args", "kwargs", "attribute"}` 字典（F-021）；指标清单完全声明在 `ResourceUseDisplay` 配置中：进程内存默认 `memory_info.rss`、系统内存默认 `virtual_memory.total`（F-022）、进程 CPU 默认 `cpu_percent(interval=0.05)`、系统 CPU 默认 `cpu_count`（F-023）、磁盘默认两个 `disk_usage` 项取 total/used（F-024）。`PSUtilMetricsLoader` 从 `web_app.settings` 读取这份配置（F-031），用 `getattr(process, name)(*args, **kwargs)` 统一调用 psutil 方法、按 `attribute` 取 named tuple 字段（F-032），`process_metric` 对当前进程与递归子进程求和（F-033），`get_metric_values` 经 `metric_types` 字典分派 process/system 两条路径（F-034），`metrics()` 在任一指标值为 None 时整体返回 None（F-035）。

需要澄清的是：`PrometheusHandler` 构造时接收 `PSUtilMetricsLoader`，并用其输出写 6 个 Gauge（F-036）——只有 Prometheus 通道复用了该加载器；而进程级 `ApiHandler` 是**内联 psutil** 直接采集（对照 F-010~F-015），两者并不共享采集逻辑。这一抽象让新增一种资源类型（如磁盘）只需在配置中补一组指标描述即可被 Prometheus 通道消费，但 REST 通道若也要吃到该能力则需另行接入。

```
配置层 (config.py)                       执行层 (metrics.py)                    消费层
PSUtilMetric dict ──────────►  PSUtilMetricsLoader ──────────► PrometheusHandler (6 Gauge)
{name,args,kwargs,attribute}  ├─ process_metric() 求和         ApiHandler (内联 psutil，独立)
  ↑ 声明式扩展（加磁盘只需加条目） └─ metric_types 字典分派
```

**复用价值**：监控多种资源且指标项经常演进的系统，可采用"指标描述字典 + 通用加载器 + 配置开关"三段式，让新增指标只改配置不碰采集逻辑；但要显式设计指标缺失时的降级语义（全部放弃 or 部分可用），并注意多个消费方可能各自持有独立的采集实现，勿假设它们必然共享同一加载器。

## I-003："显示限额但不强制"——展示型 limit 设计

**类型**：设计决策
**关联事实**：F-012, F-013, F-014, F-025, F-026, F-028, F-029, F-037, F-038

**洞察**：`mem_limit` 与 `cpu_limit` 的 help 文本明确写着"不实际限制用户内存/CPU 使用"（F-026, F-028）——这是一对纯展示型限额：只影响状态栏/指示条与告警阈值的计算，不参与任何 cgroup/ulimit 级资源管控。限额来源支持三重回退：环境变量 `MEM_LIMIT`/`CPU_LIMIT`（JupyterHub spawner 注入）→ traitlets 配置 → callable 动态计算（F-026, F-028, F-037, F-038）；callable 分支以 `rss=`/`cpu_percent=` 关键字传参（F-037, F-038），让宿主可基于实际用量派生限额。`mem_limit` 为 0 时服务端回退系统总量 `virtual_memory_total`，`cpu_limit` 为 0 时回退 `100.0 * cpu_count`（F-037, F-038）。

告警（warn）是同型阈值比较：`(limit - used) < limit * mem_warning_threshold`，内存、CPU、磁盘三处实现数学结构一致（F-012, F-013, F-014），阈值默认 0.1 表示"剩余不足 10% 即告警"、置 0 可关闭（F-025）。磁盘通道默认关闭（`track_disk_usage` 默认 False，F-029），需显式开启才参与采集与告警。

```
MEM_LIMIT / CPU_LIMIT 环境变量 ─┐
--ResourceUseDisplay.mem_limit  ├─► mem_limit / cpu_limit (Union Int|Callable) ──► warn 判定
traitlets 配置文件              ┘        │  (limit-used) < limit*threshold, threshold 默认 0.1
                                         │  仅展示，不执行 cgroup/ulimit 强制
                                         └─ 0 → 回退系统总量 virtual_memory_total / 100*cpu_count
```

**复用价值**：在"监控面板 + 非管控方"场景下，把限额设计为纯展示量并允许 callable 派生，可避免监控组件越权干预运行时；同时保持"配置缺失→回退系统容量"的稳妥默认。告警阈值统一为"剩余比例"的数学形式，多资源复用同一公式。

## I-004：单一数据模型 + 多视图订阅——前端指标分发架构

**类型**：架构模式
**关联事实**：F-039, F-040, F-041, F-042, F-043, F-045, F-046, F-047, F-048, F-052, F-053, F-054

**洞察**：前端由三个各自 `autoStart` 的插件构成入口矩阵：`resourceStatusPlugin`（状态栏，requires `ITranslator`，F-039）、`systemMonitorPlugin`（topbar，requires `IToolbarWidgetRegistry`，F-041）与 `kernelUsagePlugin`（侧栏，F-044）。topbar 插件经 `settingRegistry.load` 读取 `enable`/`refreshRate`/各资源 label 等配置（F-042）；状态栏用 `statusBar.registerStatusItem` 注册（F-040），topbar 用 `toolbarRegistry.addFactory('TopBar', ...)` 分别注册 cpu/memory/disk 工厂（F-043）。

指标数据不随各视图分别拉取，而是收敛为单一 `ResourceUsage.Model`：由 `Poll` 以 `refreshRate` 轮询 `/api/metrics/v1`，带 backoff 与 `when-hidden` standby（F-046），`Private.factory` 负责发请求（F-048）；模型仅保留最近 `N_BUFFER = 20` 条历史值（F-045），`_updateMetricsValues` 完成 pss/rss 优先级换算与 limit 解析（F-047）。视图侧 `ResourceUsageStatus` 继承 `VDomRenderer<ResourceUsage.Model>`（F-052），以 `memoryLimit === null` 区分"只显示当前值 / 显示当前值与上限"两种渲染（F-053），告警时追加告警样式类（F-054）。模型负责原始语义，视图只做文本格式与样式决策，避免重复轮询。

```
                    Poll(refreshRate, standby=when-hidden)
                            │
                     ResourceUsage.Model (单一数据源)
                     ├─ N_BUFFER=20 历史缓冲 / pss→rss 换算 / limit 解析
                     └─ 状态信号 ──► 多订阅者
ResourceUsageStatus(状态栏)   CpuView  MemoryView  DiskView (topbar 工厂)
   (VDomRenderer, F-052)      (addFactory('TopBar', ...), F-043)
```

**复用价值**：多入口 UI（状态栏 + 工具栏 + 侧栏）共用一个实时数据模型是通用模式——单一轮询源降低网络与逻辑重复，VDom 模型 + 信号 + React 工厂让每个视图保持极薄。历史缓冲与百分比换算放在模型层，可使各视图渲染逻辑保持一致的语义。

## I-005：内核级 usage 的空白态驱动渲染与过期响应防护

**类型**：架构约束
**关联事实**：F-016, F-017, F-019, F-020, F-055, F-056, F-057, F-058, F-059, F-060

**洞察**：Kernel Usage 侧栏面对"无内核 widget、内核不支持、请求超时"等多种失败路径，因此被设计成"显式空白态机"。`KernelUsagePanel` 继承 `StackedPanel` 作为容器（F-055），按 `POLL_INTERVAL_SEC = 5` 每 5 秒轮询（F-058）。`hasKernelSession` 以 `instanceof ConsolePanel || NotebookPanel` 硬判定哪个 widget 带内核（F-057）；`KernelWidgetTracker` 监听 `labShell.currentChanged` 或 notebook/console tracker 的 `currentChanged`，把当前带内核 widget 归一化发射（F-056）。

异步时序上，`requestUsage` 用 `kernelIdRef` 比对"响应所属 kernel_id 与当前 kernel_id"，丢弃迟到响应，`data.content.reason` 存在时转入 `not_supported`/`timeout`/`no_kernel` 等空白态（F-059）。`not_supported`/`timeout` 由服务端判定（F-016, F-017, F-019）；host 信息是否展示由后端 `show_host_usage` 注入 `host_usage_flag` 控制（F-020），前端据此决定是否渲染 "Host CPU" 与 "Host Virtual Memory" 区块（F-060）——展示开关在服务端配置，前端只被动响应。

```
              ┌───────────── 失败态机 ─────────────┐
   no_kernel / not_supported / timeout / 其他空白态
              └─────────────┬─────────────┘
                            ▼
   kernelIdRef 比对 → 丢弃迟到响应 → 仅更新当前内核的 usage 面板
   host_usage_flag(服务端) → 决定是否渲染 Host CPU / Host Virtual Memory
```

**复用价值**：对"实时数据可能长期不可用"的 UI，应显式建模空白态集合而非隐式判空；异步响应必须按请求身份（如 kernel_id）校验归属后再应用；"能否展示某信息"这类策略开关放服务端配置、前端被动消费，可避免重复实现策略逻辑。
