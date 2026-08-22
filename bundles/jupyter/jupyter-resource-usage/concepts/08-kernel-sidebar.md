---
type: Concept
title: 内核使用侧边栏
description: kernelUsagePlugin插件注册、KernelWidgetTracker活动内核跟踪、useInterval自定义Hook、requestUsage API调用、五种空白状态、内存单位格式化
tags: [jupyter-resource-usage, sidebar, kernel-usage, kernel-widget-tracker, use-interval, blank-state]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 内核使用侧边栏

内核使用侧边栏（kernelUsagePlugin）是一个可交互的面板，显示**当前活动Notebook/Console单个内核**的详细资源使用信息。与状态栏的服务器总资源监控不同，它精确到单个内核进程，且包含宿主机资源信息。

## 插件注册

```typescript
const kernelUsagePlugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyter-server/resource-usage:kernel-panel-item',
  autoStart: true,
  requires: [ITranslator],
  optional: [ILabShell, ISettingRegistry, IStatusBar, INotebookTracker, IConsoleTracker],
  activate: (app, translator, labShell, settingRegistry, statusBar, notebookTracker, consoleTracker) => {
    // ...
  }
};
```

- 侧边栏图标位于左侧边栏，使用 `memoryIcon`（内存图标）
- 点击面板后才开始请求数据（懒加载，不影响启动性能）
- 同时兼容 JupyterLab（使用ILabShell）和 Notebook 7（使用INotebookTracker+IConsoleTracker）

## 懒加载机制

面板只有在用户首次点击打开时才开始轮询：

```typescript
panel.shown.connect(() => {
  start();
});
panel.hidden.connect(() => {
  stop();
});
```

- **shown**：面板可见时启动轮询
- **hidden**：面板隐藏时停止轮询，节省API请求
- 这是与状态栏/顶栏的关键区别——状态栏始终轮询，侧边栏按需轮询

## KernelWidgetTracker：活动内核跟踪

内核侧边栏通过 `KernelWidgetTracker` 跟踪当前活动的Notebook或Console widget：

### 信号连接

```typescript
const tracker = new KernelWidgetTracker({ labShell, notebookTracker, consoleTracker });
widgets.push(tracker);
tracker.currentChanged.connect((_, widget) => {
  // 用户切换了活动widget，更新sessionContext
  if (widget) {
    setSessionContext(widget.sessionContext);
    setKernel(widget.sessionContext.session?.kernel);
  } else {
    setSessionContext(null);
    setKernel(null);
  }
});
```

### JupyterLab vs Notebook 7兼容

```typescript
if (labShell) {
  labShell.currentChanged.connect((_, update) => {
    const widget = update.newValue;
    if (widget && hasKernelSession(widget)) {
      this._currentChanged.emit(widget as KernelSessionWidget);
    } else {
      this._currentChanged.emit(null);
    }
  });
} else {
  // Notebook 7: 使用notebookTracker和consoleTracker
  if (notebookTracker) {
    notebookTracker.currentChanged.connect((_, widget) => {
      this._currentChanged.emit(widget as KernelSessionWidget);
    });
  }
  if (consoleTracker) {
    consoleTracker.currentChanged.connect((_, widget) => {
      this._currentChanged.emit(widget as KernelSessionWidget);
    });
  }
}
```

`hasKernelSession()` 通过instanceof判断是ConsolePanel还是NotebookPanel，两者都有 `sessionContext.kernel` 属性。

### 内核变更监听

当用户在同一个Notebook中切换/重启内核时：

```typescript
useEffect(() => {
  const updateKernel = () => {
    setKernel(sessionContext.session?.kernel);
  };
  if (sessionContext) {
    sessionContext.kernelChanged.connect(updateKernel);
    return () => {
      sessionContext.kernelChanged.disconnect(updateKernel);
    };
  } else {
    setKernel(null);
  }
}, [sessionContext]);
```

监听 `kernelChanged` 信号，内核重启/切换时自动更新。

## 轮询机制：useInterval自定义Hook

侧边栏使用自定义的 `useInterval` React Hook，而非Lumino Poll：

```typescript
useInterval(
  async () => {
    if (kernelId && panel.isVisible) {
      requestUsage(kernelId).catch(() => {
        console.warn(`Request failed for ${kernelId}. Kernel restarting?`);
      });
    }
  },
  POLL_INTERVAL_SEC * 1000,  // 5000ms
);
```

- 轮询间隔固定5秒（POLL_INTERVAL_SEC=5）
- 只有当kernelId存在**且**面板可见时才请求
- 面板隐藏时useInterval通过start/stop控制暂停

### 竞态防护

使用useRef保存最新kernelId，丢弃过期响应：

```typescript
const kernelIdRef = useRef<string | undefined>(kernelId);
kernelIdRef.current = kernelId;

const requestUsage = (kid: string) => {
  return requestAPI<any>(`get_usage/${kid}`, {}, serverSettings)
    .then((data) => {
      if (kid !== kernelIdRef.current) {
        return; // 丢弃过期响应（用户切换了内核）
      }
      setUsage(data);
      setBlankState(null); // 清除空白状态
      if (data.content.reason === 'timeout') {
        setBlankState({ reason: 'timeout', timeoutMs: data.content.timeout_ms });
        panel.node.classList.add('jp-mod-timeout');
      } else {
        panel.node.classList.remove('jp-mod-timeout');
      }
    })
    .catch((e) => {
      console.error(e);
    });
};
```

这是必要的，因为用户可能在请求进行中切换到另一个Notebook，旧请求返回时不应覆盖新内核的数据。

## 显示内容

侧边栏面板显示以下字段：

| 字段 | 来源 | 条件 |
|------|------|------|
| Notebook路径 | sessionContext.path | 始终 |
| Kernel ID | content.kernel_id或kernel.id | kernel存在时 |
| Kernel Host | content.hostname | reason !== timeout |
| Timestamp | content.last_activity | 始终 |
| Process ID | content.pid | reason !== timeout |
| CPU | content.kernel_cpu + "%" | reason !== timeout |
| Memory | formatForDisplay(content.kernel_memory) | reason !== timeout |
| Host CPU | host_cpu_percent% + cores | host_usage_flag && reason !== timeout |
| Host Virtual Memory | active/available/free/inactive/percent/total/used/wired | host_usage_flag && reason !== timeout |

### 内存格式化

使用 `format.ts` 中定义的 `formatForDisplay` 函数（widget.tsx中import使用）将字节转为人类可读格式：

```typescript
function formatForDisplay(nBytes: number): string {
  const kB = nBytes / 1024.0;
  if (kB < 1024.0) {
    return `${kB.toFixed(1)} kB`;
  }
  const MB = kB / 1024.0;
  if (MB < 1024.0) {
    return `${MB.toFixed(1)} MB`;
  }
  const GB = MB / 1024.0;
  return `${GB.toFixed(2)} GB`;
}
```

精度规则：kB和MB显示1位小数，GB显示2位小数。这与状态栏的`convertToLargestUnit`（统一2位小数）不同。

## 五种空白状态（Blank State）

当内核数据不可用时，面板显示对应的提示信息而非空白：

| reason | 触发条件 | 显示内容 |
|--------|---------|---------|
| `not_supported` | ipykernel版本<6.9.0 | "Kernel usage is not supported for this kernel: requires ipykernel >= 6.10.0. Found ipykernel version X.X.X." |
| `no_kernel_widget` | 没有活动的Notebook/Console | "Please open a notebook or console in JupyterLab to see kernel usage. You may need to change the active tab." |
| `no_kernel` | widget存在但无活跃内核 | "No active kernel found. Execute a cell to start a kernel." |
| `timeout` | ZMQ请求超时10秒 | "Timed out waiting for kernel usage. Waited XXXXX ms." |
| `loading` | 首次请求中 | "Loading…"（Spinner图标） |

### 空白状态判定逻辑

```typescript
let displayBlankState: BlankStateType = blankState;
if (!kernel) {
  if (!sessionContext) {
    displayBlankState = { reason: 'no_kernel_widget' };
  } else {
    displayBlankState = { reason: 'no_kernel' };
  }
}
if (displayBlankState.reason === null) {
  displayBlankState = { reason: 'loading' };
}
```

优先级：已有blankState（如timeout）> 无内核 > 无widget > 加载中。

### 版本不支持的检测

初始加载时尝试请求一次，检测内核版本：

```typescript
useEffect(() => {
  if (kernelId) {
    requestAPI<any>(`get_usage/${kernelId}`, {}, serverSettings)
      .then((data) => {
        if (data.content.reason === 'not_supported') {
          setBlankState({ reason: 'not_supported', kernelVersion: data.content.kernel_version });
        }
      })
      .catch((e) => console.error(e));
  }
}, [kernelId]);
```

### 超时样式

超时状态下给面板添加 `jp-mod-timeout` CSS类，可通过CSS自定义样式。

## 组件结构

面板使用React函数组件+hooks实现：

```tsx
const KernelView: React.FC<{...}> = (props) => {
  const [kernel, setKernel] = useState<Kernel.IKernelConnection | null | undefined>();
  const [sessionContext, setSessionContext] = useState<ISessionContext | null>();
  const [usage, setUsage] = useState<any>(null);
  const [blankState, setBlankState] = useState<BlankStateType>({ reason: null });
  
  const kernelId = kernel?.id;
  
  // 1. 监听tracker切换
  // 2. 监听kernelChanged
  // 3. 版本检测
  // 4. 定时轮询useInterval
  // 5. 竞态防护requestUsage
  
  return (
    <Widget>
      {/* 根据状态显示blankState或数据面板 */}
    </Widget>
  );
};
```

最后通过 `ReactWidget.create(<KernelView .../>)` 包装为Lumino Widget。

## 相关概念

- [内核资源监控](04-kernel-usage.md) — 后端KernelUsageHandler与ZMQ通信
- [架构总览](02-architecture.md) — 侧边栏数据流
- [状态栏显示](06-statusbar.md) — 与侧边栏的区别
