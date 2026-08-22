---
type: Concept
title: 工具函数与扩展开发
description: convertToLargestUnit单位转换、formatForDisplay内存格式化、Icon资源、VDomRenderer/ReactWidget组件模式、自定义扩展指南
tags: [jupyter-resource-usage, utility, format, icon, vdom, react-widget, extension]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 工具函数与扩展开发

本文档整理 jupyter-resource-usage 中的工具函数、通用模式，以及基于现有代码进行扩展开发的指南。

## 单位格式化函数

### convertToLargestUnit（TypeScript，格式化工具）

位于 `packages/labextension/src/format.ts`，将字节数转换为最合适的单位（model.ts中import使用）：

```typescript
const DEFAULT_UNIT_IMPLEMENTATION = (
  value: number,
  unit: 'B' | 'KB' | 'MB' | 'GB' | 'TB' | 'PB'
): string => {
  const prefix = Private.UnitPrefixes[unit];
  return `${prefix}${unit}`;
};

export function convertToLargestUnit(
  valueInBytes: number,
  unitImplementation = DEFAULT_UNIT_IMPLEMENTATION
): [number, string] {
  if (valueInBytes < 0) {
    console.error(
      `Provided a negative value of ${valueInBytes} to convert to the largest unit`
    );
    return [-1, 'B'];
  }
  let size = valueInBytes;
  for (let unit = 0; unit < Private.UNITS.length; unit++) {
    if (size < Private.KB || unit === Private.UNITS.length - 1) {
      return [size, unitImplementation(size, Private.UNITS[unit])];
    } else {
      size = size / Private.KB;
    }
  }
  return [0, 'B']; // 不应到达
}
```

- **输入**：字节数
- **输出**：`[数值, 单位字符串]` 元组
- **进位基准**：1024（KB/MB/GB/TB/PB）
- **精度**：返回数值本身，由调用方决定小数位数（状态栏固定2位小数）
- **负数处理**：返回 `[-1, 'B']` 并打印console.error

### formatForDisplay（TypeScript，侧边栏）

位于 `packages/labextension/src/format.ts`，为内核侧边栏专用的内存格式化（widget.tsx中import使用）：

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

- **精度规则**：kB/MB 1位小数，GB 2位小数
- **单位范围**：仅到GB（内核内存一般不会超过TB级别）
- **与convertToLargestUnit区别**：固定精度、无TB/PB支持、直接返回格式化字符串

### 单位常量

```typescript
namespace Private {
  export const KB = 1024;
  export const UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'] as const;
  export const UnitPrefixes = {
    B: '',
    KB: 'K',
    MB: 'M',
    GB: 'G',
    TB: 'T',
    PB: 'P',
  } as const;
}
```

## API请求工具

### 状态栏/顶栏使用的requestAPI

```typescript
// 简单GET请求，自动处理json解析
export async function requestAPI<T>(url = '', init: RequestInit = {}, settings: ServerConnection.ISettings = ServerConnection.defaultSettings): Promise<T> {
  const fullUrl = URLExt.join(settings.baseUrl, url);
  const response = await ServerConnection.makeRequest(fullUrl, init, settings);
  if (!response.ok) {
    throw new ServerConnection.ResponseError(response);
  }
  return response.json();
}
```

路径：`/api/metrics/v1`

### 内核侧边栏使用的requestAPI

```typescript
// 路径前缀为 /api/metrics/v1/kernel_usage/
const requestAPI = <T>(
  url: string,
  init: RequestInit = {},
  settings: ServerConnection.ISettings = ServerConnection.defaultSettings
): Promise<T> => {
  const fullUrl = URLExt.join(
    settings.baseUrl,
    'api',
    'metrics',
    'v1',
    'kernel_usage',
    url
  );
  return ServerConnection.makeRequest(fullUrl, init, settings).then((response) => {
    if (response.status !== 200) {
      return response.json().then((data: any) => {
        throw new ServerConnection.ResponseError(response, data.message);
      });
    }
    return response.json();
  });
};
```

路径：`/api/metrics/v1/kernel_usage/get_usage/{kernel_id}`

## Icon资源

### 内存图标

使用JupyterLab内置的 `memoryIcon`（从 `@jupyterlab/ui-components` 导入），用于侧边栏图标：

```typescript
import { memoryIcon } from '@jupyterlab/ui-components';

const kernelPanel = new ReactWidget(...);
kernelPanel.id = 'kernel-resource-usage';
kernelPanel.title.icon = memoryIcon;
kernelPanel.title.caption = trans.__('Kernel Resource Usage');
```

## React组件模式

### useInterval自定义Hook

用于定时轮询，支持启动/暂停控制：

```typescript
const useInterval = (callback: () => void, delay: number) => {
  const savedCallback = useRef(callback);
  const intervalId = useRef<number | null>(null);
  
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
  
  useEffect(() => {
    const tick = () => savedCallback.current();
    intervalId.current = window.setInterval(tick, delay);
    return () => {
      if (intervalId.current) window.clearInterval(intervalId.current);
    };
  }, [delay]);
};
```

- 使用useRef保存最新回调，避免重复setInterval
- 返回清理函数在unmount时清除定时器
- 与Lumino Poll不同，更轻量，但无backoff/standby功能

### VDomRenderer模式（状态栏）

状态栏使用JupyterLab的 `VDomRenderer` 而非React：

```typescript
export class ResourceUsageStatus extends VDomRenderer<ResourceUsage.Model> {
  constructor(trans: TranslationBundle, options: ResourceUsage.Model.IOptions) {
    super(new ResourceUsage.Model(options));
    this._trans = trans;
  }
  
  render(): VNode | VNode[] | null {
    // 返回React JSX（@lumino/virtualdom兼容）
    if (!this.model.metricsAvailable) return null;
    // ...构建文本
    if (this.model.usageWarnings.hasWarning) {
      return <TextItem className={resourceItem} source={text} />;
    }
    return <TextItem source={text} />;
  }
}
```

### ReactWidget模式（顶栏/侧边栏）

新组件统一使用ReactWidget包装React函数组件：

```typescript
// 顶栏
export const createCpuView = (model, label): ReactWidget => {
  return ReactWidget.create(<CpuViewComponent model={model} label={label} />);
};

// 侧边栏
const kernelPanel = ReactWidget.create(
  <KernelView
    tracker={tracker}
    panel={kernelPanel}
    trans={trans}
    settingsProvider={settingsProvider}
    serverSettings={settings}
  />
);
```

## 后端扩展开发模式

### 添加新的API端点

1. 在 `api.py` 中创建新的Handler类，继承 `APIHandler`
2. 在 `_load_jupyter_server_extension()` 中注册路由：

```python
from jupyter_resource_usage.api import MyNewHandler

web_app.add_handlers(
  host_pattern,
  [
    (url_path_join(base_url, 'api/metrics/v1/my-endpoint'), MyNewHandler),
    # ...
  ]
)
```

3. 使用 `@web.authenticated` 装饰器保护端点
4. 在 `server_extension_points` 列表中注册元数据（如需要）

### 添加新的配置项

在 `ResourceUseDisplay` 类中添加traitlets属性：

```python
from traitlets import Float, Bool, Unicode

my_new_option = Bool(
    default_value=False,
    config=True,
    help="Enable my new feature."
)
```

traitlets会自动生成命令行参数 `--ResourceUseDisplay.my_new_option=True` 和配置文件项 `c.ResourceUseDisplay.my_new_option = True`。

### 添加新的前端组件

遵循三插件模式：
1. **状态栏**：继承 `VDomRenderer`，使用 `IStatusBar.registerStatusItem()`
2. **顶栏**：使用React函数组件 + `ReactWidget.create()`，通过 `IToolbarWidgetRegistry.addFactory('TopBar', name, factory)`
3. **侧边栏**：使用React函数组件 + hooks（useInterval, useRef竞态防护），通过 `app.shell.add(widget, 'left', { rank })`

## 构建与发布

### 开发安装

```bash
git clone https://github.com/jupyter-server/jupyter-resource-usage
cd jupyter-resource-usage
pip install -e ".[dev]"

# 安装labextension（开发模式）
jupyter labextension develop . --overwrite

# 链接classic nbextension
jupyter serverextension enable --py jupyter_resource_usage
jupyter nbextension install --py jupyter_resource_usage --symlink
jupyter nbextension enable --py jupyter_resource_usage

# 构建前端
jlpm install
jlpm run build
```

### 前端开发

使用 `jlpm run watch` 启动watch模式，实时编译TypeScript：

```bash
jlpm run watch
# 在另一个终端
jupyter lab --watch
```

### 测试

```bash
# Python测试
pytest jupyter_resource_usage/tests/

# 前端测试
jlpm run test
```

## 相关概念

- [后端API与指标采集](03-backend-api.md) — API端点实现
- [配置系统详解](05-configuration.md) — 添加配置项方法
- [状态栏显示](06-statusbar.md) — VDomRenderer模式详解
- [顶栏监控面板](07-topbar-monitor.md) — ReactWidget模式详解
- [内核使用侧边栏](08-kernel-sidebar.md) — useInterval模式详解
