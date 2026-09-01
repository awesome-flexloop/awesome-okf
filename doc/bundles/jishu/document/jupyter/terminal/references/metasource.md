---
type: Reference
title: JupyterLite Terminal 项目元信源
description: 项目版本、依赖、构建配置、目录结构等元数据信源
tags: [jupyterlite, terminal, metadata, build, dependencies]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pkg-json
    resource: /../../../../../../external/libs/jupyter/terminal/package.json
    title: package.json
  - id: pyproject
    resource: /../../../../../../external/libs/jupyter/terminal/pyproject.toml
    title: pyproject.toml
---

# 项目元信源

## 基本信息

| 属性 | 值 |
|------|-----|
| npm包名 | `@jupyterlite/terminal` |
| Python包名 | `jupyterlite_terminal` |
| 版本 | `1.7.0-a0` |
| 描述 | A terminal for JupyterLite |
| License | BSD-3-Clause |
| 仓库 | https://github.com/jupyterlite/terminal |
| JupyterLite兼容性 | >= 0.7.0, < 0.9.0 |
| Python要求 | >= 3.10 |

## npm 核心依赖

| 包名 | 版本范围 | 用途 |
|------|---------|------|
| @jupyterlab/apputils | ^4.6.0 | JupyterLab应用工具（主题管理等） |
| @jupyterlab/coreutils | ^6.5.0 | JupyterLab核心工具（PageConfig、URLExt等） |
| @jupyterlab/services | ^7.5.0 | JupyterLab服务（TerminalManager、Terminal API等） |
| @jupyterlab/settingregistry | ^4.5.0 | JupyterLab设置注册表 |
| @jupyterlite/apputils | ^0.7.0 \|\| ^0.8.0 | JupyterLite应用工具（IServiceWorkerManager等） |
| @jupyterlite/cockle | ^1.8.0-a0 | 浏览器内WASM shell实现 |
| @jupyterlite/services | ^0.7.0 \|\| ^0.8.0 | JupyterLite服务（DriveFS、ContentsAPI等） |
| @lumino/coreutils | ^2.2.1 | Lumino核心工具（Token、JSONPrimitive等） |
| @lumino/signaling | ^2.1.4 | Lumino信号系统（Signal、ISignal） |
| coincident | ^4.1.1 | SharedArrayBuffer Worker通信 |
| comlink | ^4.4.2 | Service Worker Worker通信 |
| mock-socket | ^9.3.1 | 浏览器内WebSocket模拟 |

## Python 依赖

| 包名 | 版本范围 |
|------|---------|
| jupyterlite-core | >=0.7.0,<0.9.0,!=0.7.4,!=0.7.5 |
| hatchling | >=1.5.0（构建时） |
| jupyter-builder | >=1.0.0,<2（构建时） |
| hatch-nodejs-version | >=0.3.2（构建时） |

## 构建系统

| 工具 | 用途 |
|------|------|
| TypeScript ~5.7.0 | TS→JS编译，target ES2022 |
| Rspack | Worker打包（coincident.worker.js、comlink.worker.js） |
| jupyter-builder | JupyterLab扩展构建 |
| hatchling + hatch-nodejs-version | Python包构建（版本从package.json同步） |
| hatch-jupyter-builder | 集成npm构建到Python wheel |

## npm scripts

| 命令 | 说明 |
|------|------|
| `build` | 完整构建（lib + worker + dev labextension） |
| `build:prod` | 生产构建（clean + prod lib + prod worker + labextension） |
| `build:lib` | TypeScript编译（带sourceMap） |
| `build:worker` | Rspack打包Worker（development模式） |
| `build:labextension` | JupyterLab扩展构建 |
| `watch` | 监听模式（tsc -w + jupyter-builder watch） |
| `test` | Jest测试 |
| `lint` | stylelint + prettier + eslint |

## 目录结构

```
@jupyterlite/terminal/
├── src/                          # TypeScript源码
│   ├── index.ts                  # 插件入口（6个插件定义+导出）
│   ├── tokens.ts                 # ILiteTerminalAPIClient Token
│   ├── client.ts                 # LiteTerminalAPIClient 核心类
│   ├── shell.ts                  # TerminalShell（继承cockle BaseShell）
│   ├── exec.ts                   # 无头shell命令执行插件
│   ├── coincident.worker.ts      # SharedArrayBuffer模式Worker
│   ├── comlink.worker.ts         # ServiceWorker模式Worker
│   ├── coincident.d.ts           # coincident类型声明
│   └── __tests__/                # 单元测试
├── style/                        # CSS样式
│   ├── index.css                 # 入口（@import base.css）
│   └── base.css                  # 基础样式
├── jupyterlite_terminal/         # Python包
│   ├── __init__.py               # 包入口+labextension路径
│   └── add_on.py                 # JupyterLite构建插件（WASM复制）
├── deploy/                       # 部署示例
│   ├── jupyter-lite.json         # 配置示例（terminalsAvailable: true）
│   └── contents/                 # 示例内容文件
├── ui-tests/                     # Playwright E2E测试
├── package.json                  # npm元数据
├── pyproject.toml                # Python元数据+构建配置
├── tsconfig.json                 # TypeScript配置
├── rspack.config.js              # 主构建配置
├── worker.rspack.config.js       # Worker构建配置
├── install.json                  # JupyterLab扩展安装信息
└── README.md                     # 用户文档
```
