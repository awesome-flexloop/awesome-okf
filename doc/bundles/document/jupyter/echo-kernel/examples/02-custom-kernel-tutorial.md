---
type: Example
title: 自定义 JupyterLite 内核开发教程
description: 以Echo Kernel为模板，从零开始开发一个自定义JupyterLite内核，包括项目搭建、内核实现、构建配置和测试
tags: [custom-kernel, tutorial, development, jupyterlite, typescript, extension]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-src
    resource: /references/kernel-source.md
    title: EchoKernel类源码信源
  - id: plugin-src
    resource: /references/plugin-source.md
    title: 插件注册源码信源
  - id: python-src
    resource: /references/python-source.md
    title: Python包与构建配置信源
---

## 教程概述

本教程以Echo Kernel为模板，演示如何开发一个自定义JupyterLite内核。我们将创建一个"大写转换内核"（Uppercase Kernel），它将用户输入的文本转换为大写后输出。

通过本教程，你将学会：
1. 搭建JupyterLite内核项目结构
2. 实现BaseKernel抽象方法
3. 配置TypeScript和Python构建系统
4. 本地测试和调试自定义内核

## 步骤1：项目搭建

### 1.1 初始化项目

```bash
# 创建项目目录
mkdir jupyterlite-uppercase-kernel
cd jupyterlite-uppercase-kernel

# 初始化npm包
jlpm init
# 或使用yarn/npm
yarn init
```

### 1.2 安装依赖

```bash
# 核心依赖
jlpm add @jupyterlab/application @jupyterlite/services

# 开发依赖
jlpm add -D @jupyterlab/builder typescript ~5.0.2
jlpm add -D eslint prettier rimraf npm-run-all2
```

### 1.3 项目目录结构

```
jupyterlite-uppercase-kernel/
├── src/
│   ├── index.ts          # 插件入口
│   └── kernel.ts         # 内核实现
├── style/
│   ├── base.css          # 基础样式（可选）
│   ├── index.css         # 样式入口
│   └── index.js          # 样式导入
├── jupyterlite_uppercase_kernel/
│   └── __init__.py       # Python包入口
├── package.json          # npm配置
├── tsconfig.json         # TypeScript配置
├── pyproject.toml        # Python构建配置
├── install.json          # JupyterLab扩展安装配置
└── README.md
```

## 步骤2：实现内核类

创建 `src/kernel.ts`：

```typescript
// Copyright (c) Your Name
// Distributed under the terms of the Modified BSD License.

import type { KernelMessage } from '@jupyterlab/services';
import { BaseKernel } from '@jupyterlite/services';

/**
 * 一个将输入文本转换为大写的内核
 */
export class UppercaseKernel extends BaseKernel {
  /**
   * 处理 kernel_info_request 消息
   */
  async kernelInfoRequest(): Promise<KernelMessage.IInfoReplyMsg['content']> {
    const content: KernelMessage.IInfoReply = {
      implementation: 'Uppercase',
      implementation_version: '0.1.0',
      language_info: {
        codemirror_mode: {
          name: 'text/plain'
        },
        file_extension: '.txt',
        mimetype: 'text/plain',
        name: 'uppercase',
        nbconvert_exporter: 'text',
        pygments_lexer: 'text',
        version: 'es2017'
      },
      protocol_version: '5.3',
      status: 'ok',
      banner: 'An uppercase kernel running in the browser',
      help_links: []
    };
    return content;
  }

  /**
   * 处理 execute_request 消息 —— 核心逻辑
   */
  async executeRequest(
    content: KernelMessage.IExecuteRequestMsg['content']
  ): Promise<KernelMessage.IExecuteReplyMsg['content']> {
    const { code } = content;

    // 自定义逻辑：将输入转换为大写
    const result = code.toUpperCase();

    // 发布标准输出流（可选，显示处理过程信息）
    this.stream({
      name: 'stdout',
      text: `Converting ${code.length} characters to uppercase...\n`
    });

    // 发布执行结果
    this.publishExecuteResult({
      execution_count: this.executionCount,
      data: {
        'text/plain': result
      },
      metadata: {}
    });

    return {
      status: 'ok',
      execution_count: this.executionCount,
      user_expressions: {}
    };
  }

  /**
   * 以下方法为可选实现，最简单的内核可以stub它们
   */
  async completeRequest(
    content: KernelMessage.ICompleteRequestMsg['content']
  ): Promise<KernelMessage.ICompleteReplyMsg['content']> {
    throw new Error('Not implemented');
  }

  async inspectRequest(
    content: KernelMessage.IInspectRequestMsg['content']
  ): Promise<KernelMessage.IInspectReplyMsg['content']> {
    throw new Error('Not implemented');
  }

  async isCompleteRequest(
    content: KernelMessage.IIsCompleteRequestMsg['content']
  ): Promise<KernelMessage.IIsCompleteReplyMsg['content']> {
    throw new Error('Not implemented');
  }

  async commInfoRequest(
    content: KernelMessage.ICommInfoRequestMsg['content']
  ): Promise<KernelMessage.ICommInfoReplyMsg['content']> {
    throw new Error('Not implemented');
  }

  inputReply(content: KernelMessage.IInputReplyMsg['content']): void {
    throw new Error('Not implemented');
  }

  async commOpen(msg: KernelMessage.ICommOpenMsg): Promise<void> {
    throw new Error('Not implemented');
  }

  async commMsg(msg: KernelMessage.ICommMsgMsg): Promise<void> {
    throw new Error('Not implemented');
  }

  async commClose(msg: KernelMessage.ICommCloseMsg): Promise<void> {
    throw new Error('Not implemented');
  }
}
```

## 步骤3：实现插件入口

创建 `src/index.ts`：

```typescript
// Copyright (c) Your Name
// Distributed under the terms of the Modified BSD License.

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import type { IKernel } from '@jupyterlite/services';
import { IKernelSpecs } from '@jupyterlite/services';

import { UppercaseKernel } from './kernel';

/**
 * 注册Uppercase内核的插件
 */
const kernel: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlite/uppercase-kernel:kernel',
  autoStart: true,
  requires: [IKernelSpecs],
  activate: (app: JupyterFrontEnd, kernelspecs: IKernelSpecs) => {
    kernelspecs.register({
      spec: {
        name: 'uppercase',
        display_name: 'Uppercase',
        language: 'text',
        argv: [],
        resources: {
          'logo-32x32': '',
          'logo-64x64': ''
        }
      },
      create: async (options: IKernel.IOptions): Promise<IKernel> => {
        return new UppercaseKernel(options);
      }
    });
  }
};

const plugins: JupyterFrontEndPlugin<any>[] = [kernel];
export default plugins;
```

## 步骤4：配置文件

### 4.1 package.json

```json
{
  "name": "@jupyterlite/uppercase-kernel",
  "version": "0.1.0",
  "description": "Uppercase kernel for JupyterLite",
  "keywords": ["jupyter", "jupyterlab", "jupyterlab-extension"],
  "license": "BSD-3-Clause",
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "style": "style/index.css",
  "files": [
    "lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,woff2,ttf}",
    "style/**/*.{css,js,eot,gif,html,jpg,json,png,svg,woff2,ttf}",
    "src/**/*.{ts,tsx}"
  ],
  "scripts": {
    "build": "jlpm build:lib && jlpm build:labextension:dev",
    "build:prod": "jlpm clean && jlpm build:lib:prod && jlpm build:labextension",
    "build:labextension": "jupyter labextension build .",
    "build:labextension:dev": "jupyter labextension build --development True .",
    "build:lib": "tsc --sourceMap",
    "build:lib:prod": "tsc",
    "clean": "jlpm clean:lib",
    "clean:lib": "rimraf lib tsconfig.tsbuildinfo",
    "clean:labextension": "rimraf jupyterlite_uppercase_kernel/labextension",
    "clean:all": "jlpm clean:lib && jlpm clean:labextension",
    "install:extension": "jlpm build",
    "watch": "run-p watch:src watch:labextension",
    "watch:src": "tsc -w --sourceMap",
    "watch:labextension": "jupyter labextension watch ."
  },
  "dependencies": {
    "@jupyterlab/application": "^4.5.0",
    "@jupyterlite/services": "^0.7.0"
  },
  "devDependencies": {
    "@jupyterlab/builder": "^4.5.0",
    "rimraf": "^5.0.1",
    "npm-run-all2": "^7.0.1",
    "typescript": "~5.0.2"
  },
  "sideEffects": ["style/*.css", "style/index.js"],
  "styleModule": "style/index.js",
  "publishConfig": { "access": "public" },
  "jupyterlab": {
    "extension": true,
    "outputDir": "jupyterlite_uppercase_kernel/labextension",
    "sharedPackages": {
      "@jupyterlite/services": {
        "bundled": false,
        "singleton": true
      }
    }
  }
}
```

### 4.2 tsconfig.json

```json
{
  "compilerOptions": {
    "allowSyntheticDefaultImports": true,
    "composite": true,
    "declaration": true,
    "esModuleInterop": true,
    "incremental": true,
    "jsx": "react",
    "lib": ["DOM", "ES2018", "ES2020.Intl"],
    "module": "esnext",
    "moduleResolution": "node",
    "noEmitOnError": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "preserveWatchOutput": true,
    "resolveJsonModule": true,
    "outDir": "lib",
    "rootDir": "src",
    "strict": true,
    "strictNullChecks": true,
    "target": "ES2018"
  },
  "include": ["src/*"]
}
```

### 4.3 pyproject.toml

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version>=0.3.2"]
build-backend = "hatchling.build"

[project]
name = "jupyterlite_uppercase_kernel"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.9"
dependencies = []
dynamic = ["version", "description", "authors", "urls", "keywords"]

[tool.hatch.version]
source = "nodejs"

[tool.hatch.build.targets.wheel.shared-data]
"jupyterlite_uppercase_kernel/labextension" = "share/jupyter/labextensions/@jupyterlite/uppercase-kernel"
"install.json" = "share/jupyter/labextensions/@jupyterlite/uppercase-kernel/install.json"

[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlite_uppercase_kernel/labextension/static/style.js",
    "jupyterlite_uppercase_kernel/labextension/package.json",
]
skip-if-exists = ["jupyterlite_uppercase_kernel/labextension/static/style.js"]

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlite_uppercase_kernel/labextension"
```

### 4.4 install.json

```json
{
  "packageManager": "python",
  "packageName": "jupyterlite_uppercase_kernel",
  "uninstallInstructions": "Use your Python package manager to uninstall the package jupyterlite_uppercase_kernel"
}
```

### 4.5 Python包入口

创建 `jupyterlite_uppercase_kernel/__init__.py`：

```python
try:
    from ._version import __version__
except ImportError:
    __version__ = "dev"


def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "@jupyterlite/uppercase-kernel"
    }]
```

### 4.6 样式文件（最小）

`style/index.js`：
```javascript
import './base.css';
```

`style/base.css`：
```css
/* 自定义样式 */
```

`style/index.css`：
```css
@import url('base.css');
```

## 步骤5：测试

### 5.1 开发模式安装

```bash
# 安装Python包（开发模式）
python -m pip install -e .

# 链接JupyterLab扩展
jupyter labextension develop . --overwrite

# 安装npm依赖
jlpm install

# 启动watch模式
jlpm run watch
```

### 5.2 运行JupyterLab

另一个终端运行：

```bash
jupyter lab
```

打开浏览器访问JupyterLab，在Launcher中应该能看到"Uppercase"内核。

### 5.3 测试内核

创建一个Uppercase Notebook，输入：

```
hello world
```

预期输出：
```
Converting 11 characters to uppercase...
HELLO WORLD
```

## 步骤6：打包发布

```bash
# 清理并构建生产版本
jlpm clean:all
python -m build

# 上传到PyPI
twine upload dist/*

# 发布npm包
npm publish --access public
```

## 进阶功能建议

基于Echo Kernel模板，你可以实现更复杂的内核：

| 功能 | 需要实现的方法/API |
|------|-------------------|
| 流式输出 | 使用 `this.stream({name: 'stdout', text: '...'})` |
| 富媒体输出（HTML/图片） | 在publishExecuteResult的data中添加MIME类型 |
| 错误处理 | 使用 `this.publishExecuteError()` |
| 代码补全 | 实现 `completeRequest()` |
| 多行输入 | 实现 `isCompleteRequest()` |
| Widgets支持 | 实现 `commOpen/commMsg/commClose` |
| 清除输出 | 使用 `this.clearOutput()` |
| 更新显示 | 使用 `this.updateDisplayData()` |

## 内核开发关键要点

1. **必须实现** `kernelInfoRequest()` 和 `executeRequest()` —— 这两个是最小可用内核
2. **可以stub** 其余方法（抛出Not implemented）—— 基础功能不受影响
3. **language_info** 决定了编辑器语法高亮和文件关联
4. **argv为空数组** —— 浏览器内核不需要命令行启动参数
5. **sharedPackages配置** —— `@jupyterlite/services` 必须设为singleton，避免多实例问题
6. **build:prod用于发布** —— 生产构建禁用sourceMap，减小体积

## 相关示例

- [安装与使用](01-install-and-use.md) — 安装Echo Kernel并体验

## 相关概念

- [JupyterLite内核架构](../concepts/01-kernel-architecture.md)
- [插件注册机制](../concepts/02-plugin-registration.md)
- [EchoKernel实现详解](../concepts/03-echokernel-implementation.md)
- [构建与打包](../concepts/04-build-and-packaging.md)
