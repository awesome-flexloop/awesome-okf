---
type: Concept
title: 顶栏监控面板
description: systemMonitorPlugin启用与配置、CpuView/MemoryView/DiskView进度条组件、IndicatorComponent与Sparklines趋势图、Settings Editor配置
tags: [jupyter-resource-usage, topbar, sparklines, indicator, cpuview, memoryview, diskview, settings]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 顶栏监控面板

顶栏监控面板（systemMonitorPlugin）提供比状态栏更丰富的可视化资源监控——彩色进度条指示器，点击可切换为迷你趋势图（Sparklines）。此功能**默认禁用**，需用户在设置中手动开启。

## 启用方式

通过 JupyterLab 设置编辑器启用：

1. 菜单：**Settings → Settings Editor**
2. 选择 **Resource Usage Indicator**
3. 勾选 **"Enable resource usage indicators"**
4. 刷新浏览器标签页

顶栏会在工具栏右侧显示CPU、内存、磁盘三个进度条指示器。

## 插件注册

```typescript
const systemMonitorPlugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyter-server/resource-usage:topbar-item',
  autoStart: true,
  requires: [IToolbarWidgetRegistry],
  optional: [ISettingRegistry, JupyterLab.IInfo],
  activate: async (app, toolbarRegistry, settingRegistry, info) => {
    // 加载设置
    let enablePlugin = false;  // 默认禁用
    let refreshRate = 5000;
    let cpuLabel = DEFAULT_CPU_LABEL;      // "CPU: "
    let memoryLabel = DEFAULT_MEMORY_LABEL; // "Mem: "
    let diskLabel = DEFAULT_DISK_LABEL;    // "Disk: "

    if (settingRegistry) {
      const settings = await settingRegistry.load(systemMonitorPlugin.id);
      enablePlugin = settings.get('enable').composite as boolean;
      refreshRate = settings.get('refreshRate').composite as number;
      // ...加载cpu/memory/disk标签设置
    }

    const model = new ResourceUsage.Model({ refreshRate, serverSettings, refreshStandby: ... });
    await model.refresh();

    // 有数据且启用时注册到TopBar
    if (enablePlugin && model.cpuAvailable) {
      toolbarRegistry.addFactory('TopBar', 'cpu', () => CpuView.createCpuView(model, cpuLabel));
    }
    if (enablePlugin && model.memoryAvailable) {
      toolbarRegistry.addFactory('TopBar', 'memory', () => MemoryView.createMemoryView(model, memoryLabel));
    }
    if (enablePlugin && model.diskAvailable) {
      toolbarRegistry.addFactory('TopBar', 'disk', () => DiskView.createDiskView(model, diskLabel));
    }
  },
};
```

- 使用 `IToolbarWidgetRegistry` 注册TopBar工厂
- 各资源的可用性由后端配置决定（track_cpu_percent、track_disk_usage）
- CPU/memory/disk在TopBar中的rank分别为120/130/140

## 三个资源视图组件

### MemoryView（内存）

- **颜色**：绿色 `#00B35B`
- **默认标签**：`"Mem: "`
- **文本格式**：`"256.00 / 1024 MB"`（无限制时只显示当前值）

```typescript
const MemoryViewComponent = ({ model, label }) => {
  const [text, setText] = useState('');
  const [values, setValues] = useState<number[]>([]);
  const update = () => {
    const { memoryLimit, currentMemory, memUnits } = model;
    const precision = ['B', 'KB', 'MB', 'GB'].indexOf(memUnits) > 0 ? 0 : 3;
    const newText = `${currentMemory.toFixed(precision)} ${
      memoryLimit ? '/ ' + memoryLimit.toFixed(precision) : ''
    } ${memUnits}`;
    const newValues = model.values.map(v => v.memoryPercent);
    setText(newText);
    setValues(newValues);
  };
  useEffect(() => {
    model.stateChanged.connect(update);
    return () => { model.stateChanged.disconnect(update); };
  }, [model]);
  return <IndicatorComponent enabled={model.memoryAvailable} values={values} label={label} color={'#00B35B'} text={text} />;
};
```

精度规则：B/KB/MB/GB 单位显示0位小数，TB/PB显示3位小数。

### CpuView（CPU）

- **颜色**：蓝色 `#0072B3`
- **默认标签**：`"CPU: "`
- **文本格式**：`"12%"`（百分比整数）

```typescript
const CpuViewComponent = ({ model, label }) => {
  const update = () => {
    const { cpuLimit, currentCpuPercent } = model;
    const newValues = model.values.map(v => Math.min(1, v.cpuPercent / (cpuLimit || 1)));
    const newText = `${(currentCpuPercent * 100).toFixed(0)}%`;
    // ...
  };
  return <IndicatorComponent enabled={model.cpuAvailable} values={values} label={label} color={'#0072B3'} text={text} />;
};
```

CPU百分比归一化到0-1范围（除以cpuLimit或1），用于进度条显示。

### DiskView（磁盘）

- **颜色**：紫色 `#c27ba0`
- **默认标签**：`"Disk: "`
- **文本格式**：`"1.50 / 10.00 GB"`

```typescript
const DiskViewComponent = ({ model, label }) => {
  const update = () => {
    const { maxDisk, currentDisk, diskUnits } = model;
    const precision = ['B', 'KB', 'MB'].indexOf(diskUnits) > 0 ? 0 : 2;
    const newText = `${currentDisk.toFixed(precision)} / ${maxDisk.toFixed(precision)} ${diskUnits}`;
    // ...
  };
  return <IndicatorComponent enabled={model.diskAvailable} values={values} label={label} color={'#c27ba0'} text={text} />;
};
```

精度规则：B/KB/MB显示0位小数，GB及以上显示2位小数。

## IndicatorComponent：通用指示器

三个视图共用 `IndicatorComponent` 组件：

```tsx
export const IndicatorComponent = ({ enabled, values, label, color, text }) => {
  const percentage = values[values.length - 1];
  return (
    <>
      {enabled && (
        <div className="jp-IndicatorContainer">
          <div className="jp-IndicatorText">{label}</div>
          {percentage !== null && (
            <div className="jp-IndicatorWrapper">
              <IndicatorBar values={values} percentage={percentage} baseColor={color} />
            </div>
          )}
          <div className="jp-IndicatorText">{text}</div>
        </div>
      )}
    </>
  );
};
```

### IndicatorBar：进度条/趋势图切换

```tsx
const IndicatorBar = ({ values, percentage, baseColor }) => {
  const [isSparklines, setIsSparklines] = useState(false);
  const toggleSparklines = () => setIsSparklines(!isSparklines);

  const color = percentage > 0.5 ? (percentage > 0.8 ? 'red' : 'orange') : baseColor;

  return (
    <div className="jp-IndicatorBar" onClick={toggleSparklines}>
      {isSparklines && (
        <Sparklines data={values} min={0.0} max={1.0} limit={values.length} margin={0}>
          <SparklinesLine style={{ stroke: color, strokeWidth: 4, fill: color, fillOpacity: 1 }} />
          <SparklinesSpots />
        </Sparklines>
      )}
      {!isSparklines && <IndicatorFiller percentage={percentage} color={color} />}
    </div>
  );
};
```

**交互**：点击进度条可在进度条模式和Sparklines趋势图模式之间切换。

**颜色规则**：
- < 50%：基础颜色（绿/蓝/紫）
- 50%-80%：橙色（`orange`）
- > 80%：红色（`red`）

### IndicatorFiller：填充进度条

```tsx
const IndicatorFiller = ({ percentage, color }) => (
  <div className="jp-IndicatorFiller" style={{ width: `${percentage * 100}%`, background: color }} />
);
```

宽度按百分比设置，纯CSS实现。

## React Widget 包装

三个视图都通过 `ReactWidget.create()` 将React组件包装为Lumino Widget：

```typescript
export namespace MemoryView {
  export const createMemoryView = (model, label): ReactWidget => {
    return ReactWidget.create(<MemoryViewComponent model={model} label={label} />);
  };
}
```

## 设置Schema

设置项定义在 `schema/topbar-item.json`：

| 设置路径 | 类型 | 默认值 | 说明 |
|---------|------|--------|------|
| `enable` | boolean | false | 是否启用顶栏指示器 |
| `refreshRate` | number | 5000 | 刷新间隔（毫秒） |
| `memory.label` | string | "\| Mem: " | 内存标签文本 |
| `cpu.label` | string | "CPU: " | CPU标签文本 |
| `disk.label` | string | "\| Disk: " | 磁盘标签文本 |

Schema中还定义了TopBar工具栏项的排序：
- cpu: rank 120
- memory: rank 130
- disk: rank 140

## 与状态栏的区别

| 特性 | 状态栏 | 顶栏监控 |
|------|--------|---------|
| 默认启用 | ✅ | ❌ |
| 显示形式 | 纯文本 | 彩色进度条+Sparklines |
| 位置 | 底部状态栏 | 顶部工具栏 |
| 交互 | 无 | 点击切换趋势图 |
| 颜色变化 | 仅警告时红底红字 | 50%橙色/80%红色渐变 |
| 刷新间隔 | 5秒（固定） | 可配置（默认5秒） |
| 自定义标签 | 不支持 | 通过Settings Editor支持 |

## 相关概念

- [状态栏显示](06-statusbar.md) — 默认文本显示，共享Model
- [后端API与指标采集](03-backend-api.md) — 指标数据来源
- [单位格式化](11-custom-metrics.md) — 内存/磁盘单位转换
