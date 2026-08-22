---
type: Concept
title: 内核资源监控
description: KernelUsageHandler实现、ZMQ control channel通信、usage_request消息协议、ipykernel版本要求、轮询机制、空白状态处理
tags: [jupyter-resource-usage, kernel, zmq, ipykernel, usage-request, control-channel]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 内核资源监控

内核资源监控是 jupyter-resource-usage 的高级功能，通过 ZMQ 消息通道向**单个 ipykernel** 查询其资源使用情况，与 `/api/metrics/v1` 的进程树psutil采集形成互补。

## 与服务器指标的区别

| 维度 | 服务器指标（ApiHandler） | 内核指标（KernelUsageHandler） |
|------|------------------------|-------------------------------|
| API端点 | `/api/metrics/v1` | `/api/metrics/v1/kernel_usage/get_usage/{kernel_id}` |
| 采集方式 | psutil遍历Server进程+所有子进程 | ZMQ control channel发消息给单个kernel |
| 数据范围 | 所有Kernel+Terminal的总资源 | 单个Kernel进程的精确资源 |
| ipykernel版本 | 无要求 | >= 6.9.0 |
| 包含宿主机信息 | 否 | 是（host_cpu_percent、host_virtual_memory） |
| 响应速度 | 快（本地psutil调用） | 取决于kernel响应（10秒超时） |

## ipykernel 版本检查

```python
try:
    import ipykernel
    IPYKERNEL_VERSION = ipykernel.__version__
    USAGE_IS_SUPPORTED = version.parse("6.9.0") <= version.parse(IPYKERNEL_VERSION)
except ImportError:
    USAGE_IS_SUPPORTED = False
    IPYKERNEL_VERSION = None
```

- 如果未安装ipykernel或版本低于6.9.0，`USAGE_IS_SUPPORTED = False`
- 此时API返回 `"reason": "not_supported"` 及检测到的内核版本
- README中要求 >= 6.11.0（可能文档更新滞后于代码），代码中硬编码检查6.9.0

## KernelUsageHandler 处理流程

### 1. 版本检查（不支持时）

```python
if not USAGE_IS_SUPPORTED:
    self.write(json.dumps({
        "content": {
            "reason": "not_supported",
            "kernel_version": IPYKERNEL_VERSION,
        }
    }))
    return
```

### 2. 获取Kernel连接

```python
kernel_id = matched_part
km = self.kernel_manager
lkm = km.pinned_superclass.get_kernel(km, kernel_id)
session = lkm.session
client = lkm.client()
```

- 从URL路径中提取kernel_id
- 通过kernel_manager获取对应的kernel实例
- 创建client用于ZMQ通信

### 3. 发送usage_request消息

```python
control_channel = client.control_channel
usage_request = session.msg("usage_request", {})
control_channel.send(usage_request)
```

- 使用 **control channel**（而非shell channel）发送消息，避免与代码执行竞争
- 消息类型为 `"usage_request"`，内容为空字典 `{}`
- 这是ipykernel >= 6.9.0 内置支持的消息类型

### 4. ZMQ Poller等待响应

```python
poller = zmq.asyncio.Poller()
control_socket = control_channel.socket
poller.register(control_socket, zmq.POLLIN)
timeout_ms = 10_000
events = dict(await poller.poll(timeout_ms))
```

- 使用 `zmq.asyncio.Poller()` 异步等待响应
- **超时时间10秒**（10000ms）
- 如果超时，返回 `"reason": "timeout"` 错误

### 5. 解析响应

```python
if control_socket not in events:
    out = json.dumps({"content": {"reason": "timeout", "timeout_ms": timeout_ms}, "kernel_id": kernel_id})
else:
    res = client.control_channel.get_msg(timeout=0)
    if isawaitable(res):
        res = await res
    if res:
        res["kernel_id"] = kernel_id
    res["content"].update({"host_usage_flag": config.show_host_usage})
    out = json.dumps(res, default=date_default)
client.stop_channels()
self.write(out)
```

- 响应中注入 `kernel_id` 字段
- 添加 `host_usage_flag`（由 `show_host_usage` 配置控制），前端据此决定是否显示宿主机信息
- 使用 `jupyter_client.jsonutil.date_default` 序列化日期对象
- 完成后调用 `client.stop_channels()` 清理ZMQ连接

## API响应格式

### 正常响应

```json
{
  "header": {...},
  "parent_header": {},
  "metadata": {},
  "content": {
    "hostname": "jupyter-server",
    "pid": 12345,
    "kernel_cpu": 12.5,
    "kernel_memory": 268435456,
    "host_cpu_percent": 25.3,
    "cpu_count": 4,
    "host_virtual_memory": {
      "total": 8589934592,
      "available": 4294967296,
      "percent": 50.0,
      "used": 4294967296,
      "free": 2147483648,
      "active": 3221225472,
      "inactive": 1073741824,
      "wired": 536870912
    },
    "host_usage_flag": true
  },
  "kernel_id": "a1b2c3d4-..."
}
```

### 错误响应：版本不支持

```json
{
  "content": {
    "reason": "not_supported",
    "kernel_version": "6.8.0"
  }
}
```

### 错误响应：超时

```json
{
  "content": {
    "reason": "timeout",
    "timeout_ms": 10000
  },
  "kernel_id": "a1b2c3d4-..."
}
```

## 前端Kernel Usage面板

前端侧边栏面板由以下组件构成：

### KernelWidgetTracker

跟踪当前活动的Notebook/Console widget，在用户切换标签页时自动切换监控的内核：

```typescript
export class KernelWidgetTracker {
    constructor(options: KernelWidgetTracker.IOptions) {
        const { labShell, notebookTracker, consoleTracker } = options;
        this._currentChanged = new Signal(this);
        if (labShell) {
            // JupyterLab环境：使用ILabShell.currentChanged
            labShell.currentChanged.connect((_, update) => {
                const widget = update.newValue;
                if (widget && hasKernelSession(widget)) {
                    this._currentChanged.emit(widget);
                    this._currentWidget = widget;
                } else {
                    this._currentChanged.emit(null);
                    this._currentWidget = null;
                }
            });
        } else {
            // Notebook 7兼容：使用INotebookTracker + IConsoleTracker
            notebookTracker.currentChanged.connect(/* ... */);
            consoleTracker?.currentChanged.connect(/* ... */);
        }
    }
}
```

- 优先使用 `ILabShell`（JupyterLab环境），回退到 `INotebookTracker` + `IConsoleTracker`（Notebook 7）
- `hasKernelSession()` 通过 `instanceof` 判断是 ConsolePanel 还是 NotebookPanel

### 轮询机制

使用自定义 `useInterval` Hook（5秒间隔），且仅在面板可见时请求：

```typescript
useInterval(async () => {
    if (kernelId && panel.isVisible) {
        requestUsage(kernelId).catch(() => {
            console.warn(`Request failed for ${kernelId}. Kernel restarting?`);
        });
    }
}, POLL_INTERVAL_SEC * 1000);
```

### 竞态防护

使用 `useRef` 保存最新kernelId，丢弃过期响应：

```typescript
const kernelIdRef = useRef<string | undefined>(kernelId);
kernelIdRef.current = kernelId;

const requestUsage = (kid: string) => {
    return requestAPI<any>(`get_usage/${kid}`, {}, serverSettings).then((data) => {
        if (kid !== kernelIdRef.current) {
            return; // 忽略过期响应
        }
        // 处理响应...
    });
};
```

### 五种空白状态

| 状态 | reason值 | 显示内容 |
|------|---------|---------|
| 版本不支持 | `not_supported` | 提示需要ipykernel >= 6.10.0，显示检测到的版本 |
| 无内核widget | `no_kernel_widget` | 提示切换到Notebook或Console |
| 无内核 | `no_kernel` | 显示"No active kernel found" |
| 超时 | `timeout` | 显示超时时间（毫秒），面板添加超时CSS类 |
| 加载中 | `loading` | 显示"Loading…" |

## 显示内容

内核侧边栏显示以下信息：

1. **Notebook路径**
2. **Kernel ID**
3. **Kernel Host**（主机名）
4. **Timestamp**（数据采集时间）
5. **Process ID**
6. **CPU**（内核CPU使用率）
7. **Memory**（内核内存使用量，格式化显示）
8. **Host CPU**（当show_host_usage=True时）：CPU核心数和使用率
9. **Host Virtual Memory**（当show_host_usage=True时）：active/available/free/inactive/percent/total/used/wired

## host_usage_flag 配置

通过 `--ResourceUseDisplay.show_host_usage=False` 可隐藏宿主机CPU和虚拟内存信息。默认为 `True`（显示全部信息）。在多租户环境中，管理员可能不希望用户看到宿主机资源信息。

## 相关概念

- [后端API与指标采集](03-backend-api.md) — ApiHandler服务器指标采集
- [配置系统详解](05-configuration.md) — show_host_usage等配置项
- [内核使用侧边栏](08-kernel-sidebar.md) — 前端面板详解
