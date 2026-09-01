---
type: Example
title: 添加自定义语言服务器
description: 以一个假设的 Python 语言服务器为例，演示如何为 jupyterlite-lsp 添加新的浏览器端语言服务器
tags: [example, custom-server, plugin, extension, web-worker]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: yaml
    resource: /references/yaml-plugin-source.md
    title: YAML语言服务器包源码引用
  - id: core
    resource: /references/core-plugin-source.md
    title: 核心LSP包源码引用
---

## 概述

本文档演示如何为 jupyterlite-lsp 添加一个新的浏览器端语言服务器。我们以 YAML/JSON 服务器（`@jupyterlite/lsp-yaml`）为参考模板，展示创建新语言服务器包的完整流程。

添加新语言服务器**不需要修改 `@jupyterlite/lsp` 核心包**，只需创建一个新的 npm 包，实现 IJSONRPCLanguageServer 接口，并通过插件注册即可。

## 步骤一：创建 npm 包

在 `packages/` 目录下创建新包目录，例如 `packages/lsp-python/`：

```
packages/lsp-python/
├── package.json
├── tsconfig.json
├── webpack.config.js
└── src/
    ├── index.ts
    ├── plugin.ts
    ├── server.ts
    ├── tokens.ts
    └── worker.ts      (可选，如果使用 Web Worker)
```

## 步骤二：配置 package.json

```json
{
  "name": "@jupyterlite/lsp-python",
  "version": "0.1.0-alpha0",
  "description": "Python language server for JupyterLite",
  "license": "BSD-3-Clause",
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "files": ["{lib}/**/*"],
  "scripts": {
    "dist:npm": "cd ../../dist && npm pack ../packages/lsp-python",
    "labextension:build": "jupyter labextension build .",
    "watch": "jupyter labextension watch ."
  },
  "dependencies": {
    "@jupyterlite/lsp": "^0.1.0a0",
    "@jupyterlite/server": "^0.1.0-beta.15"
  },
  "devDependencies": {
    "@jupyterlab/builder": "^3.4.0"
  },
  "jupyterlab": {
    "extension": "lib/plugin.js",
    "outputDir": "../../src/jupyterlite_lsp/_d/share/jupyter/labextensions/@jupyterlite/lsp-python",
    "webpackConfig": "./webpack.config.js",
    "sharedPackages": {
      "@jupyterlite/lsp": {
        "bundled": false,
        "singleton": true
      }
    }
  },
  "jupyterlite": {
    "liteExtension": true
  }
}
```

关键点：
- `outputDir` 必须指向 Python 包的 `_d/share/jupyter/labextensions/@jupyterlite/<name>` 目录
- `sharedPackages` 中将 `@jupyterlite/lsp` 设为 singleton，确保共享核心包实例
- 在 Python 端的 `constants.py` 的 `EXTENSION_NAMES` 列表中添加新包名

## 步骤三：定义 tokens.ts

```typescript
import type * as SCHEMA from '@krassowski/jupyterlab-lsp/lib/_schema';
import * as _PACKAGE from '../package.json';

export const PACKAGE = _PACKAGE;
export const NS = PACKAGE.name;
export const SERVER_PLUGIN_ID = `${NS}:plugin`;

export const SPEC: SCHEMA.ServerSpecProperties = {
  display_name: 'Python',
  languages: ['python'],
  mime_types: ['text/x-python', 'application/x-python-code'],
  version: 2,
};
```

将 `languages` 和 `mime_types` 替换为目标语言对应的 MIME 类型。

## 步骤四：实现 server.ts

创建实现 IJSONRPCLanguageServer 接口的类。如果语言服务器可以在 Web Worker 中运行（推荐），参考 JSONLanguageServer 的模式：

```typescript
import type WaitQueue from 'wait-queue';
import { DEBUG, IJSONRPCLanguageServer } from '@jupyterlite/lsp';

export class PythonLanguageServer implements IJSONRPCLanguageServer {
  private _worker: Worker | null = null;
  private _readQueue: WaitQueue<any> | null = null;

  async initialize(): Promise<void> {
    const { default: WaitQueue } = await import('wait-queue');
    this._readQueue = new WaitQueue();
    this._worker = new Worker(
      new URL('./worker-language-server', import.meta.url)  // 你的 Worker 入口
    );
    this._worker.onmessage = this.onWorkerMessage;
  }

  onWorkerMessage = (msg: MessageEvent) => {
    this._readQueue?.unshift(msg.data);
  };

  async *read(): AsyncGenerator<string> {
    let msg: any;
    while (this._worker) {
      msg = await this._readQueue?.pop();
      yield msg;
    }
  }

  async write(msg: string | ArrayBuffer | Blob | ArrayBufferView): Promise<void> {
    this._worker?.postMessage(msg);
  }
}
```

如果语言服务器不支持 Web Worker（例如在主线程运行），需要实现不同的消息桥接方式。WaitQueue 仍然可以用于将回调/事件模式转换为 AsyncGenerator。

## 步骤五：定义 worker.ts

```typescript
// 导入语言服务器的 Web Worker 入口
// 例如：import 'some-language-server/lib/webworker/serverMain';
```

具体内容取决于你使用的语言服务器。yaml-language-server 使用 `yaml-language-server/lib/esm/webworker/yamlServerMain`。

## 步骤六：创建 plugin.ts

```typescript
import { DEBUG, ILanguageServers } from '@jupyterlite/lsp';
import { JupyterLiteServer, JupyterLiteServerPlugin } from '@jupyterlite/server';
import { SERVER_PLUGIN_ID, SPEC } from './tokens';

const plugin: JupyterLiteServerPlugin<void> = {
  id: SERVER_PLUGIN_ID,
  autoStart: true,
  requires: [ILanguageServers],
  activate: (app: JupyterLiteServer, lsp: ILanguageServers) => {
    DEBUG && console.info(lsp);
    lsp.addLanguageServer('python', {
      spec: SPEC,
      createNewServer: async () => {
        const { PythonLanguageServer } = await import('./server');
        return new PythonLanguageServer();
      },
    });
  },
};

export default [plugin];
```

注意 `addLanguageServer` 的第一个参数是服务器 ID（如 `'python'`），这会影响 WebSocket URL 路径（`/lsp/ws/python`）。

## 步骤七：创建 index.ts

```typescript
export * from './tokens';
export * from './server';
export * from './plugin';
```

## 步骤八：配置 webpack.config.js

```javascript
module.exports = {
  output: { clean: true },
  devtool: 'source-map',
  module: {
    rules: [{ test: /\.js$/, use: ['source-map-loader'] }],
  },
};
```

## 步骤九：更新 Python 端

在 `src/jupyterlite_lsp/constants.py` 的 `EXTENSION_NAMES` 列表中添加新包名：

```python
EXTENSION_NAMES = [
    "lsp",
    "lsp-yaml",
    "lsp-python",  // 新增
]
```

## 步骤十：更新根配置

1. 在根 `package.json` 的 workspaces 中自动包含（通过 `packages/*` glob）
2. 在 dodo.py 中如果需要特殊构建逻辑，添加对应任务
3. 如果新服务器需要构建时 patch（类似 WebSocket patch），在 dodo.py 中添加

## 构建和测试

```bash
# 安装依赖
jlpm setup:js

# 构建所有 JS 包
jlpm build:lib
jlpm build:ext

# 开发模式安装
jlpm setup:py:pip
jlpm setup:py:ext

# 构建 JupyterLite 示例
jlpm lite:build

# 启动测试
jupyter lab --no-browser --debug
```

## 注意事项

1. **语言服务器必须可在浏览器中运行**：不是所有 LSP 服务器都支持浏览器环境。需要确认目标语言服务器支持 Web Worker 或可以打包为浏览器可用的 JS
2. **动态 import 减少初始加载体积**：使用 `await import('./server')` 延迟加载服务器实现
3. **WaitQueue 桥接模式**：Worker 的 onmessage 是 push 模式，AsyncGenerator 是 pull 模式，WaitQueue 是两者之间的桥梁
4. **sharedPackages singleton**：确保 `@jupyterlite/lsp` 在所有包间共享同一实例，否则 Token 注入会失败
5. **文件大小**：语言服务器（如 Monaco 编辑器的各类语言服务）可能体积较大，注意监控 bundle 大小
6. **构建时 patch**：如果语言服务器内部也创建 WebSocket 连接（需要连接到后端服务），可能需要类似 hacks 的 patch 机制

## 相关概念

- [IJSONRPCLanguageServer 接口](../concepts/04-language-server-interface.md)
- [YAML/JSON 语言服务器](../concepts/06-yaml-server.md)
- [三插件体系](../concepts/03-plugin-system.md)
- [架构总览](../concepts/02-architecture-overview.md)
