---
type: Example
title: "01 最小扩展：Hello World 插件"
description: 从零创建一个 prebuilt JupyterLab 扩展，注册命令、加入命令面板并弹出对话框，覆盖项目结构、package.json 字段、TypeScript 代码与开发调试全流程
tags: [jupyterlab, extension, hello-world, tutorial, plugin]
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: source-map
    resource: /references/source-code-map.md
    title: JupyterLab 源码文件地图
---

# 01 最小扩展：Hello World 插件

本示例带你从零创建一个最小可用的 JupyterLab 4.x prebuilt 扩展。它只做一件事：注册一条 `my-extension:hello` 命令，在命令面板中可搜索，执行后弹出一个显示 "Hello World!" 的对话框。麻雀虽小，五脏俱全——你将看到插件 id、`autoStart`、`requires` 依赖注入、`activate` 函数、命令注册、命令面板挂载这些贯穿所有 JupyterLab 扩展的核心模式。

> **前置条件**：Node.js 20+（F-018）、Python 3.10+（F-003）、已安装 `pip install jupyterlab>=4.0`。本示例基于 JupyterLab 4.7 的 API。

## 步骤 1：项目结构

一个最小 prebuilt 扩展只需要三个文件：

```
my-extension/
├── package.json
├── tsconfig.json
└── src/
    └── index.ts
```

如果需要通过 `pip install` 分发，再加上 Python 打包文件（`pyproject.toml`），但本地开发可以先用 `jupyter labextension develop` 链接，无需 Python 包。

## 步骤 2：package.json 关键字段

```json
{
  "name": "@my-org/my-extension",
  "version": "0.1.0",
  "description": "A minimal Hello World JupyterLab extension",
  "keywords": ["jupyter", "jupyterlab", "jupyterlab-extension"],
  "license": "BSD-3-Clause",
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "type": "module",
  "exports": {
    ".": "./lib/index.js"
  },
  "files": ["lib/**/*.{js,d.ts,map}"],
  "scripts": {
    "build": "tsc",
    "watch": "tsc -w",
    "clean": "rimraf lib"
  },
  "dependencies": {
    "@jupyterlab/application": "^4.7.0-alpha.1",
    "@jupyterlab/apputils": "^4.7.0-alpha.1"
  },
  "devDependencies": {
    "typescript": "~5.5.0",
    "rimraf": "^5.0.0"
  },
  "jupyterlab": {
    "extension": true
  }
}
```

字段说明：

- **`name`**：npm 包名，也是插件的默认扩展名。JupyterFrontEndPlugin 的 id 通常以包名为前缀（`@my-org/my-extension:plugin`）。
- **`version`**：语义化版本，JupyterLab 用它判断扩展兼容性。
- **`main` / `exports`**：指向编译后的入口 `lib/index.js`。prebuilt 扩展被 Rspack 以模块联邦方式加载，`exports` 字段必须存在。
- **`type: "module"`**：JupyterLab 4 的扩展使用 ESM 模块。
- **`jupyterlab.extension: true`**：声明这是一个 JupyterLab 前端扩展（而非 mime extension 或主题）。构建工具据此把它打入 federated bundle。若为 MIME 渲染器则使用 `"mimeExtension": true`。
- **`jupyterlab.schemaDir`**（可选）：JSON Schema 设置文件目录，插件有可配置设置时使用。
- **`nohoist`**（monorepo 中使用）：如果你的扩展在 Yarn workspace monorepo 中开发，需要在根 package.json 的 `nohoist` 中列出该包，避免 `@jupyterlab/*` 依赖被提升导致多实例冲突。独立项目不需要。

> **版本兼容提示**：`@jupyterlab/application`、`@jupyterlab/apputils` 等核心包属于 singletonPackages（F-139），扩展中声明的版本范围必须与目标 JupyterLab 版本兼容。使用 `^4.7.0` 而非固定版本，让包管理器解析到与宿主一致的版本。prebuilt 扩展不打包这些 singleton 包，运行时由宿主提供。

## 步骤 3：tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2022", "DOM"],
    "declaration": true,
    "outDir": "lib",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"]
}
```

关键点：`moduleResolution: "Bundler"` 配合 ESM 输出；`strict: true` 保证类型安全；`lib` 必须包含 `DOM`，因为 JupyterLab 前端运行在浏览器中。

## 步骤 4：编写插件代码（src/index.ts）

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ICommandPalette, showDialog, Dialog } from '@jupyterlab/apputils';

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@my-org/my-extension:plugin',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    const { commands } = app;

    const command = 'my-extension:hello';

    commands.addCommand(command, {
      label: 'My Extension: Hello',
      caption: 'Say Hello World',
      execute: () => {
        void showDialog({
          title: 'Greeting',
          body: 'Hello World!',
          buttons: [Dialog.okButton()]
        });
      }
    });

    palette.addItem({
      command,
      category: 'My Extension'
    });

    console.log('Hello World extension activated!');
  }
};

export default plugin;
```

### 代码逐行解读

- **`JupyterFrontEndPlugin<void>`**：这是所有 JupyterLab 前端插件的类型别名，定义在 `@jupyterlab/application`（`packages/application/src/frontend.ts:25`），泛型参数 `void` 表示此插件不 provide 任何服务 Token。它本质是 Lumino `IPlugin<JupyterFrontEnd, T>`。
- **`id`**：插件唯一标识，格式 `扩展名:插件名`。同一个 npm 包可以导出多个插件，每个插件 id 不同。
- **`autoStart: true`**：应用启动后自动激活。设为 `false` 则只在被其他插件 `requires` 时才激活（延迟激活）。
- **`requires: [ICommandPalette]`**：声明此插件依赖命令面板服务。`ICommandPalette` 是来自 `@jupyterlab/apputils` 的 Token（`packages/apputils/src/tokens.ts:17`），**不是**来自 `@jupyterlab/application`。JupyterLab 的依赖注入容器根据 Token 自动将对应服务实例传入 `activate` 函数。
- **`activate(app, palette)`**：插件激活入口。第一个参数始终是 `JupyterFrontEnd` 实例，后续参数按 `requires`/`optional` 数组顺序注入。
- **`commands.addCommand`**：`app.commands` 是 Lumino `CommandRegistry`。命令 id `my-extension:hello` 遵循 `namespace:action` 约定。`execute` 返回 Promise，这里用 `void` 显式忽略。
- **`showDialog`**：来自 `@jupyterlab/apputils`（`packages/apputils/src/dialog.tsx:29`），返回 Promise，在对话框关闭时 resolve。`Dialog.okButton()` 创建一个确认按钮。
- **`palette.addItem`**：把命令加入命令面板，`category` 是面板中的分组标题。返回一个 `IDisposable`，插件停用时可反注册（本例 autoStart 且无停用逻辑，故忽略返回值）。
- **`export default plugin`**：prebuilt 扩展的默认导出必须是插件对象（或插件数组），构建工具和 `registerPluginModules` 据此加载（参见 `examples/app/index.js:70` 的 `lab.registerPluginModules(...)`）。

### 更简单的版本：零依赖

如果不需要命令面板入口（例如只想在启动时执行逻辑），`requires` 可以是空数组：

```typescript
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@my-org/my-extension:plugin',
  autoStart: true,
  requires: [],
  activate: (app: JupyterFrontEnd) => {
    app.commands.addCommand('my-extension:hello', {
      label: 'Hello',
      execute: () => {
        void showDialog({ body: 'Hello World!' });
      }
    });
  }
};
```

## 步骤 5：安装依赖与构建

在项目目录下：

```bash
# 安装 npm 依赖
npm install

# 编译 TypeScript
npm run build
```

## 步骤 6：开发模式安装（链接到 JupyterLab）

有两种方式将扩展接入本地 JupyterLab：

### 方式 A：`jupyter labextension develop`（推荐，纯前端开发）

```bash
jupyter labextension develop --overwrite .
```

这条命令把当前目录的 `labextension` 产物（由构建工具生成到 `outputDir`）以符号链接方式注册到 JupyterLab 的用户扩展目录，之后重新构建 JupyterLab 即可识别。`--overwrite` 覆盖已有同名链接。

对于 prebuilt 扩展，**不需要运行 `jupyter lab build`**。这是 prebuilt/federated 模式与旧式 source 扩展的关键区别（F-029、F-138）：扩展预编译为独立 bundle，宿主启动时通过模块联邦动态加载。

### 方式 B：`pip install -e .`（需要 Python 包时）

如果扩展附带 Python 代码（如 server extension），用可编辑安装：

```bash
pip install -e .
```

这要求项目根目录有 `pyproject.toml`，配置 `hatch-jupyter-builder` 作为构建后端，自动执行前端构建并安装 labextension。纯前端扩展不必走这条路。

## 步骤 7：启动与验证

```bash
jupyter lab
```

浏览器打开 JupyterLab 后：

1. 按 `Ctrl+Shift+C`（macOS 为 `Cmd+Shift+C`）打开命令面板。
2. 输入 "Hello" 或 "My Extension"，应能看到 "My Extension: Hello" 命令。
3. 回车执行，弹出标题为 "Greeting"、内容为 "Hello World!" 的对话框。
4. 打开浏览器 DevTools 控制台，应看到 "Hello World extension activated!"。

## 调试技巧

### Watch 模式

开发时运行：

```bash
npm run watch
```

`tsc -w` 会监听 `src/` 变化并增量编译。JupyterLab 页面刷新后即加载新代码。若配合 `jupyter lab --watch`（dev mode），还能获得 Rspack 热重载，但普通 prebuilt 扩展开发只需刷新浏览器即可。

### 浏览器 DevTools

- **Console**：`activate` 中的 `console.log` 和命令执行时的错误都在这里。
- **Sources**：因为编译产生了 `.js.map` source map，可以在 DevTools 的 Sources 面板直接断点调试 TypeScript 源码。
- **Application → Local Storage**：可以看到 JupyterLab 通过 StateDB 存储的键值（F-067），调试状态相关问题时有用。
- **Network**：观察扩展 bundle 是否成功加载（federated 扩展会有独立的 chunk 请求）。

### 常见问题排查

- **命令面板搜不到命令**：检查插件是否成功激活（看控制台日志）、`id` 是否与其他插件冲突、`requires` 中的 Token 是否都存在（Token 缺失会导致插件激活失败，控制台有报错）。
- **报错 "No provider for Token"**：说明 `requires` 中声明的 Token 没有被任何插件 provide。确认 Token 导入路径正确（如 `ICommandPalette` 必须从 `@jupyterlab/apputils` 导入）。
- **扩展未出现在已安装扩展列表**：确认 `jupyter labextension list` 输出中包含你的扩展；检查 `package.json` 的 `jupyterlab.extension` 字段是否为 `true`。
- **多实例错误（React/Lumino）**：确保 `@jupyterlab/*` 和 `@lumino/*` 依赖未被重复打包。prebuilt 扩展应把这些声明为 `dependencies`（而非 `devDependencies`），由宿主提供 singleton 实例（F-139）。

## 注意事项总结

1. **Prebuilt 扩展不需要 `jupyter lab build`**：这是 4.x 的主流方式，安装后刷新即可用。只有旧式 source 扩展才需要重新构建宿主。
2. **singletonPackages 版本兼容**：React、Lumino、CodeMirror、Yjs 等包在宿主中是单例（F-139、F-148），扩展中的版本范围必须兼容，否则运行时可能出现多实例或 API 不匹配。
3. **API 导入路径**：`JupyterFrontEnd`/`JupyterFrontEndPlugin` 来自 `@jupyterlab/application`；`ICommandPalette`、`showDialog`、`Dialog` 来自 `@jupyterlab/apputils`。不要凭包名猜测，对照源码或 `@jupyterlab/metapackage` 的导出确认（F-152）。
4. **默认导出**：prebuilt 扩展必须 `export default` 一个插件或插件数组，这是模块联邦加载的约定。
5. **命令 id 命名空间**：始终用 `组织/扩展名:动作` 格式（如 `my-extension:hello`），避免与核心命令冲突。

## 相关概念

- [03 插件系统与依赖注入](../concepts/03-plugin-system.md)
- [09 关键子系统](../concepts/09-key-subsystems.md)
- [07 扩展生态系统](../concepts/07-extension-ecosystem.md)

## 相关示例

- [02 自定义文件类型查看器](02-custom-file-type.md)
