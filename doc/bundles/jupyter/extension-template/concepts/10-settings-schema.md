---
type: Concept
title: 设置系统与 JSON Schema
description: 理解 JupyterLab 设置系统的工作原理、plugin.json Schema 编写方法、设置类型定义、快捷键绑定和运行时设置监听。
tags: [settings, json-schema, isettingregistry, plugin.json, shortcuts, user-preferences]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: plugin-json
    location: template/{% if has_settings %}schema{% endif %}/plugin.json.jinja
    lines: "1-8"
  - id: index-ts
    location: template/src/index.ts.jinja
    lines: "31-41"
---

## 设置系统与 JSON Schema

JupyterLab 提供了统一的用户设置系统，允许用户通过图形界面（Settings Editor）配置扩展的行为。启用 `has_settings` 参数后，模板会生成 `schema/plugin.json` 文件，并在前端入口中集成设置加载和变更监听逻辑。

## 设置系统工作原理

```
┌─────────────────────────────────────────────────────────┐
│ schema/plugin.json (JSON Schema)                        │
│  - 定义可用设置项、类型、默认值、描述                    │
│  - 定义快捷键绑定                                       │
└────────────────────┬────────────────────────────────────┘
                     │ 构建时打包到 labextension
                     ▼
┌─────────────────────────────────────────────────────────┐
│ JupyterLab Settings Editor                              │
│  - 自动生成配置 UI（根据 Schema 类型渲染控件）           │
│  - 用户修改后保存到用户配置目录                         │
│  - 合并默认值 + 用户覆盖 → settings.composite          │
└────────────────────┬────────────────────────────────────┘
                     │ ISettingRegistry.load(pluginId)
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Extension activate()                                    │
│  - 加载初始设置                                         │
│  - 监听 settings.changed 事件响应配置变更               │
└─────────────────────────────────────────────────────────┘
```

## plugin.json 基础结构

模板生成的初始 Schema：

```json
{
  "jupyter.lab.shortcuts": [],
  "title": "myextension",
  "description": "myextension settings.",
  "type": "object",
  "properties": {},
  "additionalProperties": false
}
```

### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 设置面板中显示的标题 |
| `description` | string | 设置描述，显示在面板顶部 |
| `type` | string | 始终为 `"object"` |
| `properties` | object | 定义所有设置项 |
| `additionalProperties` | boolean | 是否允许未定义的属性（建议设为 false） |
| `jupyter.lab.shortcuts` | array | 快捷键绑定定义 |
| `jupyter.lab.transform` | array | 高级：设置值转换器 |
| `jupyter.lab.menus` | object | 高级：菜单定义 |
| `jupyter.lab.toolbars` | object | 高级：工具栏定义 |

## 定义设置项

在 `properties` 中定义设置项，每个设置项是一个 JSON Schema 属性：

### 布尔类型

```json
{
  "properties": {
    "autoStart": {
      "type": "boolean",
      "title": "Auto Start",
      "description": "Whether the extension should start automatically.",
      "default": true
    }
  }
}
```

渲染为开关/复选框。

### 字符串类型

```json
{
  "properties": {
    "apiEndpoint": {
      "type": "string",
      "title": "API Endpoint",
      "description": "The URL of the backend API endpoint.",
      "default": "https://api.example.com"
    },
    "theme": {
      "type": "string",
      "title": "Color Theme",
      "description": "Choose the color theme.",
      "enum": ["light", "dark", "auto"],
      "default": "auto"
    }
  }
}
```

- 普通 string 渲染为文本输入框
- 带 `enum` 的 string 渲染为下拉选择框

### 数值类型

```json
{
  "properties": {
    "refreshInterval": {
      "type": "number",
      "title": "Refresh Interval (seconds)",
      "description": "How often to refresh data.",
      "minimum": 1,
      "maximum": 3600,
      "default": 30
    },
    "maxItems": {
      "type": "integer",
      "title": "Maximum Items",
      "description": "Maximum number of items to display.",
      "minimum": 1,
      "default": 100
    }
  }
}
```

- `number` 渲染为数字输入框（可输入小数）
- `integer` 渲染为整数输入框
- `minimum`/`maximum` 提供滑块范围

### 数组类型

```json
{
  "properties": {
    "excludePatterns": {
      "type": "array",
      "title": "Exclude Patterns",
      "description": "File patterns to exclude.",
      "items": { "type": "string" },
      "default": [".git", "node_modules"]
    }
  }
}
```

### 对象类型

```json
{
  "properties": {
    "renderOptions": {
      "type": "object",
      "title": "Render Options",
      "description": "Visual rendering configuration.",
      "properties": {
        "fontSize": { "type": "number", "default": 14 },
        "showLineNumbers": { "type": "boolean", "default": true }
      },
      "default": {}
    }
  }
}
```

## 快捷键绑定

`jupyter.lab.shortcuts` 数组定义默认快捷键：

```json
{
  "jupyter.lab.shortcuts": [
    {
      "command": "myextension:toggle-panel",
      "keys": ["Accel Shift M"],
      "selector": "body"
    },
    {
      "command": "myextension:run-code",
      "keys": ["Shift Enter"],
      "selector": ".jp-CodeCell"
    }
  ]
}
```

### 快捷键字段

| 字段 | 说明 |
|------|------|
| `command` | 要执行的命令 ID（在 `app.commands.addCommand()` 中注册） |
| `keys` | 按键组合数组 |
| `selector` | CSS 选择器，快捷键仅在焦点匹配元素时生效 |

### 修饰键

- `Accel`：在 macOS 上是 `Cmd`，在 Windows/Linux 上是 `Ctrl`（**推荐使用 Accel** 而非硬编码 Ctrl）
- `Shift`、`Alt`、`Ctrl`、`Cmd`：直接修饰键

### 常用 selector

| selector | 作用范围 |
|----------|---------|
| `"body"` | 全局 |
| `".jp-Notebook"` | Notebook 面板中 |
| `".jp-FileEditor"` | 文件编辑器中 |
| `".jp-CodeCell"` | 代码单元格中 |
| `".jp-CommandPalette"` | 命令面板中 |

## 前端加载设置

在插件的 `activate` 函数中通过 `ISettingRegistry` 加载设置：

```typescript
import { ISettingRegistry } from '@jupyterlab/settingregistry';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'myextension:plugin',
  autoStart: true,
  optional: [ISettingRegistry],  // 注意：ISettingRegistry 是 optional 依赖
  activate: (app: JupyterFrontEnd, settingRegistry: ISettingRegistry | null) => {
    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('Settings loaded:', settings.composite);
          // 使用初始设置
          updateFromSettings(settings);

          // 监听设置变更
          settings.changed.connect(() => {
            console.log('Settings changed:', settings.composite);
            updateFromSettings(settings);
          });
        })
        .catch(reason => {
          console.error('Failed to load settings.', reason);
        });
    }
  }
};
```

### 注意事项

1. **ISettingRegistry 是 optional 依赖**：设置注册表可能不可用（如某些测试环境），因此放在 `optional` 而非 `requires` 中，并做 null 检查
2. **使用 `plugin.id`** 而非硬编码字符串，避免重构时遗漏
3. **`settings.composite`** 是默认值与用户覆盖值合并后的结果，应该始终使用它而非 `settings.default` 或 `settings.user`
4. **`settings.changed`** 信号在用户修改设置后触发，必须连接以实现动态响应

### 设置对象的属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `settings.composite` | `{ [key: string]: any }` | 合并后的设置值（默认+用户覆盖），**应该使用的主要值** |
| `settings.default` | `{ [key: string]: any }` | Schema 中定义的默认值 |
| `settings.user` | `{ [key: string]: any }` | 用户自定义覆盖值 |
| `settings.schema` | `ISchema` | 原始 JSON Schema |
| `settings.changed` | `ISignal<ISettings, void>` | 设置变更信号 |
| `settings.id` | `string` | 插件 ID |
| `settings.plugin` | `string` | 插件名称 |

### 类型安全地读取设置

```typescript
function updateFromSettings(settings: ISettingRegistry.ISettings) {
  const autoStart = settings.get('autoStart').composite as boolean;
  const endpoint = settings.get('apiEndpoint').composite as string;
  const interval = settings.get('refreshInterval').composite as number;

  // 使用设置值...
}
```

`settings.get(key)` 返回 `{ composite, default, user }` 对象，相比直接访问 `settings.composite.key` 更安全。

## 用户设置存储位置

用户修改后的设置存储在 JupyterLab 用户配置目录中：

- Linux: `~/.jupyter/lab/user-settings/@jupyterlab/extension-name/plugin.jupyterlab-settings`
- macOS: `~/Library/Jupyter/lab/user-settings/...`
- Windows: `%APPDATA%\jupyter\lab\user-settings\...`

文件格式为 JSON（使用 JSON5 语法，允许注释和尾逗号）：

```json
{
  // User settings for myextension
  "autoStart": false,
  "refreshInterval": 60
}
```

用户也可以直接编辑这个文件，Settings Editor 会自动检测变化。

## 常见模式

### 动态调整行为

```typescript
let refreshTimer: number | null = null;

function updateFromSettings(settings: ISettingRegistry.ISettings) {
  if (refreshTimer) { clearInterval(refreshTimer); }
  const interval = (settings.get('refreshInterval').composite as number) * 1000;
  if (settings.get('autoStart').composite as boolean) {
    refreshTimer = window.setInterval(refreshData, interval);
  }
}
```

### 从设置更新 CSS 变量

```typescript
function updateFromSettings(settings: ISettingRegistry.ISettings) {
  const fontSize = settings.get('fontSize').composite as number;
  document.documentElement.style.setProperty('--myextension-font-size', `${fontSize}px`);
}
```

## 相关概念

- [前端扩展开发](/concepts/06-frontend-extension.md)
- [生成项目结构详解](/concepts/04-project-structure.md)
- [四种扩展类型对比](/concepts/03-four-extension-types.md)
