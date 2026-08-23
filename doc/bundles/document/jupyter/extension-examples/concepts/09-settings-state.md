---
type: Concept
title: 设置与状态持久化
description: 使用ISettingRegistry实现可配置扩展设置，使用IStateDB实现轻量级状态持久化
tags: [jupyterlab, settings, statedb, ISettingRegistry, IStateDB, persistence, schema]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: settings-src
    resource: /references/core-api-tokens.md
    title: settings/src/index.ts 设置示例
  - id: state-src
    resource: /references/core-api-tokens.md
    title: state/src/index.ts 状态持久化示例
---

## 设置系统（ISettingRegistry）

设置系统允许扩展定义用户可配置的参数，通过 Settings Editor（Settings→Settings Editor）或JSON编辑器修改。设置基于JSON Schema定义，支持类型校验和默认值。

### 三步实现设置系统

**步骤1：创建Schema文件**

在 `schema/plugin.json` 中定义设置的JSON Schema：

```json
{
  "title": "My Extension Settings",
  "description": "Settings for my extension.",
  "type": "object",
  "properties": {
    "limit": {
      "type": "number",
      "title": "Limit",
      "description": "Maximum number of items.",
      "default": 25
    },
    "flag": {
      "type": "boolean",
      "title": "Enable Flag",
      "description": "Whether to enable the flag.",
      "default": false
    }
  },
  "additionalProperties": false
}
```

**步骤2：在插件中加载设置**

```typescript
import { ISettingRegistry } from '@jupyterlab/settingregistry';

const PLUGIN_ID = '@jupyterlab-examples/settings:settings-example';

const extension: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  requires: [ISettingRegistry],
  activate: (app, settings: ISettingRegistry) => {
    const { commands } = app;
    let limit = 25;
    let flag = false;

    function loadSetting(setting: ISettingRegistry.ISettings): void {
      // 读取composite值（用户值覆盖默认值）
      limit = setting.get('limit').composite as number;
      flag = setting.get('flag').composite as boolean;
      console.log(`Limit: ${limit}, flag: ${flag}`);
    }

    // 等待应用恢复和设置加载完成
    Promise.all([app.restored, settings.load(PLUGIN_ID)])
      .then(([, setting]) => {
        loadSetting(setting);

        // 监听设置变化
        setting.changed.connect(loadSetting);

        // 注册切换命令
        commands.addCommand(COMMAND_ID, {
          label: 'Toggle Flag and Increment Limit',
          isToggled: () => flag,
          execute: () => {
            // 编程方式修改设置
            Promise.all([
              setting.set('flag', !flag),
              setting.set('limit', limit + 1)
            ]).then(() => {
              const newLimit = setting.get('limit').composite as number;
              const newFlag = setting.get('flag').composite as boolean;
              window.alert(`Limit: ${newLimit}, flag: ${newFlag}`);
            }).catch(reason => console.error(reason));
          }
        });
      })
      .catch(reason => console.error(reason));
  }
};
```

**步骤3：package.json中声明schema路径**

确保package.json中包含schema文件（在files数组中）。JupyterLab自动发现 `schema/` 目录下的JSON文件。

### ISettingRegistry API

| 方法/属性 | 说明 |
|----------|------|
| `settings.load(pluginId)` | 加载指定插件的设置，返回Promise<ISettings> |
| `setting.get(key)` | 获取设置项，返回 `{ composite, user, default }` |
| `setting.set(key, value)` | 编程方式修改用户设置 |
| `setting.changed` | Signal，设置变化时触发 |
| `setting.composite` | 获取所有组合设置值的对象 |

### 值优先级

每个设置项有三个值层级：

- **default**：schema中定义的默认值
- **user**：用户在Settings Editor中设置的值
- **composite**：用户值优先，无用户值则使用默认值（实际生效值）

```typescript
const limitValue = setting.get('limit');
console.log(limitValue.default);   // 25
console.log(limitValue.user);      // undefined（或用户设置的值）
console.log(limitValue.composite); // 25（或用户覆盖后的值）
```

### Schema中的菜单/工具栏声明

schema/plugin.json 不仅可以定义设置属性，还可以声明菜单和工具栏项（在 `"jupyter.lab.menus"` 和 `"jupyter.lab.toolbars"` 字段），toolbar-button和context-menu示例使用此模式。详见[菜单与工具栏](/concepts/08-menus-toolbars.md)。

## 状态数据库（IStateDB）

状态数据库提供轻量级的JSON持久化存储，适合保存UI状态（如上次选择的选项、面板位置等）。与设置系统的区别：

| 特性 | ISettingRegistry | IStateDB |
|------|-----------------|----------|
| 用户可编辑 | ✅ Settings Editor | ❌ 编程访问 |
| 数据范围 | 插件设置值 | 任意JSON数据 |
| 适用场景 | 用户偏好配置 | UI状态恢复、临时数据持久化 |
| Schema验证 | ✅ JSON Schema | ❌ 无 |

### 使用IStateDB

```typescript
import { IStateDB } from '@jupyterlab/statedb';
import { ReadonlyJSONObject } from '@lumino/coreutils';

const PLUGIN_ID = '@jupyterlab-examples/state:state-example';

const extension: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  requires: [IStateDB],
  activate: (app, state: IStateDB) => {
    const options = ['one', 'two', 'three'];
    let option = options[0];

    app.restored
      .then(() => state.fetch(PLUGIN_ID))  // 读取保存的状态
      .then(value => {
        if (value) {
          option = (value as ReadonlyJSONObject)['option'] as string;
          console.log(`Option ${option} read from state.`);
        }
        return InputDialog.getItem({
          title: 'Pick an option',
          items: options,
          current: Math.max(0, options.indexOf(option))
        });
      })
      .then(result => {
        if (result.button.accept) {
          option = result.value || '';
          return state.save(PLUGIN_ID, { option });  // 保存状态
        }
      })
      .catch(reason => console.error(reason));
  }
};
```

### IStateDB API

| 方法 | 返回 | 说明 |
|------|------|------|
| `fetch(id)` | `Promise<ReadonlyJSONValue \| null>` | 读取指定id的值 |
| `save(id, value)` | `Promise<void>` | 保存值（合并） |
| `remove(id)` | `Promise<void>` | 删除值 |
| `list(namespace?)` | `Promise<IItem[]>` | 列出指定命名空间下的所有项 |

### 命名空间约定

使用插件ID作为state的key前缀，避免与其他扩展冲突：

```typescript
const PLUGIN_ID = '@jupyterlab-examples/state:state-example';
state.save(PLUGIN_ID, { option: 'two' });  // 使用插件ID作为key
```

## 选择设置还是状态？

| 场景 | 使用 |
|------|------|
| 用户需要配置的参数（API Key、主题偏好、功能开关） | ISettingRegistry |
| 记住上次的选择、面板尺寸、展开/折叠状态 | IStateDB |
| 需要Schema验证和类型检查 | ISettingRegistry |
| 内部使用的简单键值存储 | IStateDB |
| 需要在Settings Editor中可见 | ISettingRegistry |

## 布局恢复（ILayoutRestorer）

文档Widget的打开状态恢复通常使用 `WidgetTracker` + `ILayoutRestorer`，而非直接使用IStateDB：

```typescript
restorer.restore(tracker, {
  command: 'docmanager:open',
  args: widget => ({ path: widget.context.path, factory: FACTORY }),
  name: widget => widget.context.path
});
```

这种方式与Document Registry集成，能正确恢复文件类型对应的Widget。

## 相关概念

- [插件基础与依赖注入](/concepts/03-plugin-basics.md)
- [Widget与Shell布局](/concepts/05-widgets-shell.md)
- [通知系统与日志](/concepts/10-notifications-logging.md)
- [核心API与Token参考](/references/core-api-tokens.md)
