---
type: Example
title: "01 最小扩展：Hello World 插件"
description: 从零创建一个最小的 JupyterLab 扩展，注册命令、添加菜单项和 Widget，覆盖项目初始化、代码编写、安装运行全流程
tags: [jupyterlab, extension, hello-world, tutorial, plugin]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T08:19:00Z" }
verified: { by: "process:grep-api-verification", at: "2026-08-22T08:19:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source-map
    resource: /references/source-code-map.md
    title: JupyterLab 源码文件地图
  - id: plugin-system
    resource: /concepts/03-plugin-system.md
    title: 插件系统与依赖注入
---

# 最小扩展：Hello World 插件

本示例演示如何创建一个最小的 JupyterLab 扩展，实现以下功能：

1. 注册一个 "Hello World" 命令
2. 在命令面板中添加入口
3. 在主菜单中添加菜单项
4. 点击后弹出对话框显示 "Hello from JupyterLab Extension!"

> **前置条件**：已安装 Node.js 18+、Python 3.9+、JupyterLab 4.x、`pip install jupyterlab`。

## 步骤 1：使用 cookiecutter 创建项目

JupyterLab 官方提供了扩展模板。使用 `copier` 快速创建：

```bash
pip install copier
copier copy https://github.com/jupyterlab/extension-template .
```

按提示输入：
- `extension_name`: `hello_world`
- `author_name`: 你的名字
- 其他保持默认即可

如果你想手动创建，下面的步骤展示最小项目结构。

## 步骤 2：创建最小项目结构

```
hello-jupyterlab/
├── pyproject.toml
├── package.json
├── tsconfig.json
└── src/
    └── index.ts
```

### package.json

```json
{
  "name": "hello-jupyterlab",
  "version": "0.1.0",
  "description": "My first JupyterLab extension",
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "scripts": {
    "build": "jlpm build:lib && jlpm build:labextension",
    "build:lib": "tsc",
    "build:labextension": "jupyter labextension build .",
    "watch": "tsc -w",
    "clean": "rimraf lib tsconfig.tsbuildinfo"
  },
  "dependencies": {
    "@jupyterlab/application": "^4.0.0",
    "@jupyterlab/apputils": "^4.0.0",
    "@lumino/widgets": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "~5.0.0",
    "rimraf": "~5.0.0",
    "@jupyterlab/builder": "^4.0.0"
  },
  "jupyterlab": {
    "extension": true,
    "outputDir": "hello_jupyterlab/labextension",
    "_buildConfig": {
      "sharedPackages": {
        "@jupyterlab/application": {
          "singleton": true,
          "bundled": false
        },
        "@jupyterlab/apputils": {
          "singleton": true,
          "bundled": false
        }
      }
    }
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2018",
    "module": "ESNext",
    "moduleResolution": "node",
    "lib": ["ES2018", "DOM"],
    "declaration": true,
    "strict": true,
    "esModuleInterop": true,
    "outDir": "lib",
    "rootDir": "src",
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

## 步骤 3：编写插件代码

### src/index.ts

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ICommandPalette, Dialog, showDialog } from '@jupyterlab/apputils';
import { IMainMenu } from '@jupyterlab/mainmenu';

/**
 * Hello World 插件
 * 注册一个命令，在命令面板和主菜单中添加入口
 */
const helloPlugin: JupyterFrontEndPlugin<void> = {
  id: 'hello-jupyterlab:hello',
  autoStart: true,
  // ICommandPalette 是可选依赖：如果没有命令面板（非标准环境）也不报错
  optional: [ICommandPalette, IMainMenu],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette | null,
    mainMenu: IMainMenu | null
  ) => {
    const { commands } = app;
    const commandId = 'hello-jupyterlab:greet';

    // 1. 注册命令
    commands.addCommand(commandId, {
      label: 'Say Hello',
      caption: 'Display a greeting dialog',
      execute: () => {
        showDialog({
          title: 'Hello!',
          body: 'Hello from JupyterLab Extension! 🎉',
          buttons: [Dialog.okButton()]
        });
      }
    });

    // 2. 添加到命令面板
    if (palette) {
      palette.addItem({
        command: commandId,
        category: 'Hello Extension'
      });
    }

    // 3. 添加到主菜单（Help 菜单下）
    if (mainMenu) {
      mainMenu.helpMenu.addGroup(
        [{ command: commandId }],
        100  // 排序权重，越大越靠后
      );
    }

    console.log('hello-jupyterlab 插件已激活！');
  }
};

export default helloPlugin;
```

### 代码解析

| 代码片段 | 作用 |
|---------|------|
| `JupyterFrontEndPlugin<void>` | 插件类型声明，`void` 表示本插件不提供 Token 服务 |
| `id: 'hello-jupyterlab:hello'` | 插件唯一 ID，格式为 `包名:插件名` |
| `autoStart: true` | 应用启动时自动激活 |
| `optional: [ICommandPalette, IMainMenu]` | 声明可选依赖（命令面板和主菜单） |
| `activate(app, palette, mainMenu)` | 激活函数，参数按 requires/optional 顺序注入 |
| `commands.addCommand()` | 注册命令 |
| `palette.addItem()` | 添加命令到命令面板 |
| `mainMenu.helpMenu.addGroup()` | 添加到 Help 菜单 |
| `showDialog()` | 显示 JupyterLab 对话框 |

## 步骤 4：创建 Python 包

### pyproject.toml

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5"]
build-backend = "hatchling.build"

[project]
name = "hello_jupyterlab"
version = "0.1.0"
description = "My first JupyterLab extension"
readme = "README.md"
requires-python = ">=3.9"
license = { text = "BSD-3-Clause" }
dependencies = ["jupyterlab>=4.0.0,<5"]

[tool.hatch.build.targets.wheel]
packages = ["hello_jupyterlab"]

[tool.hatch.build.targets.wheel.shared-data]
"hello_jupyterlab/labextension" = "share/jupyter/labextensions/hello-jupyterlab"
```

### hello_jupyterlab/__init__.py

```python
"""Hello JupyterLab extension."""
import json
from pathlib import Path

HERE = Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open() as fid:
    _package_json = json.load(fid)

def _jupyter_labextension_paths():
    """Called by JupyterLab to discover the extension."""
    return [{
        "src": "labextension",
        "dest": _package_json["name"]
    }]
```

## 步骤 5：构建并安装

```bash
# 安装前端依赖
jlpm install

# 构建 TypeScript 并打包 labextension
jlpm build

# 安装 Python 包（开发模式，修改代码后 jlpm watch 自动重建）
pip install -e .
```

## 步骤 6：运行 JupyterLab

```bash
jupyter lab
```

验证安装：
1. 打开 JupyterLab（浏览器访问 http://localhost:8888）
2. 按 `Ctrl+Shift+C`（或 `Cmd+Shift+C`）打开命令面板
3. 输入 "Say Hello"，看到命令选项
4. 点击执行，弹出 "Hello!" 对话框
5. 打开 Help 菜单，底部应看到 "Say Hello" 菜单项
6. 打开浏览器控制台（F12），应看到 "hello-jupyterlab 插件已激活！" 日志

## 常见问题

### Q: 扩展没有出现在命令面板中？
A: 检查：
1. 运行 `jupyter labextension list` 确认扩展已安装且 enabled
2. 检查浏览器控制台是否有错误
3. 确保 `jlpm build` 成功，`hello_jupyterlab/labextension/` 目录下有文件

### Q: TypeScript 编译报错 "Cannot find module"？
A: 运行 `jlpm install` 确保所有依赖安装。

### Q: 修改代码后不生效？
A: 开发模式下：
1. 在一个终端运行 `jlpm watch`（自动增量编译）
2. 另一个终端运行 `jupyter lab --watch`（自动重新加载扩展）
3. 修改代码后等待编译完成，刷新浏览器

## 扩展练习

在掌握最小扩展后，可以尝试：

1. **添加快捷键**：为命令添加 `Accel Shift H` 快捷键
   ```typescript
   app.commands.addKeyBinding({
     command: commandId,
     keys: ['Accel Shift H'],
     selector: 'body'
   });
   ```

2. **添加 Widget 到左侧栏**：创建一个自定义面板添加到左侧栏（参考 [02 自定义文件类型示例](02-custom-file-type.md)）

3. **添加 Notebook 工具栏按钮**：通过 WidgetExtension 为 Notebook 添加按钮

4. **添加设置项**：创建 JSON Schema 设置文件，允许用户自定义问候语

## 相关概念

- [03 插件系统与依赖注入](/concepts/03-plugin-system.md)
- [07 扩展生态系统](/concepts/07-extension-ecosystem.md)
- [09 关键子系统 - 命令系统](/concepts/09-key-subsystems.md)
- [源码文件地图](/references/source-code-map.md)
