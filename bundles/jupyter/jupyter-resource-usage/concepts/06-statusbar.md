---
type: Concept
title: 状态栏显示
description: ResourceUsageStatus状态栏组件、VDomRenderer渲染、文本格式化、警告样式、Poll轮询机制、standby暂停策略
tags: [jupyter-resource-usage, statusbar, vdom, resourceusagestatus, text-display, warning]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 状态栏显示

状态栏是 jupyter-resource-usage 默认启用的UI入口，位于 JupyterLab 底部状态栏左侧，以纯文本形式实时显示资源使用情况。

## 插件注册

```typescript
const resourceStatusPlugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyter-server/resource-usage:status-item',
  autoStart: true,
  requires: [ITranslator],
  optional: [IStatusBar, JupyterLab.IInfo],
  activate: (app, translator, statusBar, info) => {
    const item = new ResourceUsageStatus(trans, {
      refreshRate: 5000,
      serverSettings: app.serviceManager.serverSettings,
      refreshStandby: () => {
        if (info) {
          return !info.isConnected || 'when-hidden';
        }
        return 'when-hidden';
      },
    });
    if (statusBar) {
      statusBar.registerStatusItem(resourceStatusPlugin.id, {
        item,
        align: 'left',
        rank: 2,
        isActive: () => item.model.metricsAvailable,
        activeStateChanged: item.model.stateChanged,
      });
    }
  },
};
```

- **对齐**：左侧（`align: 'left'`）
- **排序**：rank=2（很靠左侧的位置）
- **激活条件**：`item.model.metricsAvailable` 为 true（即至少有内存或CPU数据可用）
- **standby策略**：页面隐藏时暂停轮询，断开连接时也暂停

## ResourceUsageStatus 类

```typescript
export class ResourceUsageStatus extends VDomRenderer<ResourceUsage.Model> {
  constructor(trans: TranslationBundle, options: ResourceUsage.Model.IOptions) {
    super(new ResourceUsage.Model(options));
    this._trans = trans;
  }
}
```

继承自 `@jupyterlab/apputils` 的 `VDomRenderer<ResourceUsage.Model>`，使用 Virtual DOM 渲染。构造时创建 `ResourceUsage.Model` 实例作为数据模型。

## 文本渲染逻辑

`render()` 方法根据可用指标组合显示文本：

### 仅内存（默认）

```typescript
if (this.model.memoryLimit === null) {
  text = this._trans.__(
    '%1 %2 %3',
    this.model.memLabel,
    this.model.currentMemory.toFixed(2),
    this.model.memUnits
  );
}
// 输出: "Mem: 256.00 MB"
```

### 内存 + 限制值

```typescript
text = this._trans.__(
  '%1 %2 / %3 %4',
  this.model.memLabel,
  this.model.currentMemory.toFixed(2),
  this.model.memoryLimit.toFixed(2),
  this.model.memUnits
);
// 输出: "Mem: 256.00 / 1024.00 MB"
```

### 内存 + CPU

当 `cpuAvailable` 为 true 时，CPU信息前缀：

```typescript
if (this.model.cpuAvailable) {
  text = `${this.model.cpuLabel} ${(this.model.currentCpuPercent * 100).toFixed(2)} % | ${text}`;
}
// 输出: "CPU: 12.00 % | Mem: 256.00 / 1024.00 MB"
```

### 内存 + CPU + 磁盘

```typescript
if (this.model.diskAvailable) {
  text = `${this.model.diskLabel} ${this.model.currentDisk.toFixed(2)} / ${this.model.maxDisk.toFixed(2)} ${this.model.diskUnits} | ${text}`;
}
// 输出: "| Disk: 1.50 / 10.00 GB | CPU: 12.00 % | Mem: 256.00 / 1024.00 MB"
```

- 显示精度固定为2位小数（`Private.DECIMAL_PLACES = 2`）
- 各指标用 `|` 分隔符连接
- 磁盘信息在最前面，然后是CPU，最后是内存

## 警告样式

当任何资源（内存/CPU/磁盘）的warn状态为true时，应用红底红字警告样式：

```typescript
if (!this.model.usageWarnings.hasWarning) {
  return <TextItem title="Current resource usage" source={text} />;
} else {
  return <TextItem title="Current resource usage" source={text} className={resourceItem} />;
}
```

警告CSS类定义在 `text.ts` 中（使用 typestyle）：

```typescript
export const resourceItem = style(
  {
    fontSize: 'var(--jp-ui-font-size1)',
    fontFamily: 'var(--jp-ui-font-family)',
  },
  {
    backgroundColor: '#FFD2D2',  // 浅红背景
    color: '#D8000C',          // 深红文字
  }
);
```

## 数据模型（ResourceUsage.Model）

状态栏和顶栏共享同一个 `ResourceUsage.Model` 类（在model.ts中定义）：

### Poll轮询

```typescript
this._poll = new Poll({
  factory: () => Private.factory(this._serverSettings),
  frequency: {
    interval: options.refreshRate,  // 默认5000ms
    backoff: true,                   // 失败时指数退避
    max: 300 * 1000,                // 最大退避到300秒
  },
  name: '@jupyterlab/statusbar:ResourceUsage#metrics',
  standby: options.refreshStandby || 'when-hidden',
});
```

- **factory**：调用 `/api/metrics/v1` 获取指标数据
- **backoff**：请求失败时自动增加轮询间隔（指数退避），最大300秒，避免服务不可达时持续轰炸
- **standby**：页面隐藏时停止轮询，节省资源

### 状态更新

Poll的ticked信号触发 `_updateMetricsValues()`：

```typescript
this._poll.ticked.connect((poll) => {
  const { payload, phase } = poll.state;
  if (phase === 'resolved') {
    this._updateMetricsValues(payload);
    return;
  }
  if (phase === 'rejected') {
    // 重置所有指标为不可用
    this._memoryAvailable = false;
    this._cpuAvailable = false;
    this._diskAvailable = false;
    // ...重置值
    this.stateChanged.emit();
    return;
  }
});
```

### 环形缓冲区

模型维护最近20个指标值（N_BUFFER=20），用于趋势图：

```typescript
for (let i = 0; i < N_BUFFER; i++) {
  this._values.push({ memoryPercent: 0, cpuPercent: 0, diskPercent: 0 });
}
// 更新时：
this._values.push({ memoryPercent, cpuPercent: this._currentCpuPercent, diskPercent: currentDiskPercent });
this._values.shift();  // 保持20个值
```

### 单位自动转换

接收数据后自动将字节转换为最合适的单位：

```typescript
const numBytes = value.pss ?? value.rss;
const [currentMemory, memUnits] = convertToLargestUnit(numBytes);
```

PSS优先于RSS。`convertToLargestUnit()` 按1024进制自动选择B/KB/MB/GB/TB/PB。

## isActive 控制

注册状态栏时使用 `isActive` 回调控制显示/隐藏：

```typescript
isActive: () => item.model.metricsAvailable,
activeStateChanged: item.model.stateChanged,
```

当metricsAvailable为false（API不可达或扩展未启用）时，状态栏项自动隐藏。

## 相关概念

- [架构总览](02-architecture.md) — Poll轮询与数据流
- [后端API与指标采集](03-backend-api.md) — API响应格式
- [顶栏监控面板](07-topbar-monitor.md) — 共享Model的进度条UI
- [单位格式化](11-custom-metrics.md) — convertToLargestUnit详解
