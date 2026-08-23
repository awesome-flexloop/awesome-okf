---
type: Reference
title: 项目元数据与依赖版本
description: jupyterlite-xeus v5.0.0 的包信息、依赖版本、构建配置和支持平台
tags: [metadata, dependencies, version, build]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pkg-json
    resource: /references/metasource.md
    title: package.json and pyproject.toml
---

## 项目元数据

| 属性 | 值 |
|------|---|
| npm 根包名 | `@jupyterlite/xeus-root` |
| Python 包名 | `jupyterlite_xeus` |
| 版本 | 5.0.0 |
| License | BSD-3-Clause |
| 仓库 | https://github.com/jupyterlite/xeus |
| 文档 | https://jupyterlite-xeus.readthedocs.io |
| JupyterLab 要求 | >= 4.0.0 |
| Python 要求 | >= 3.10（支持 3.10-3.14） |

## Monorepo 包结构

| 包名 | 路径 | 职责 |
|------|------|------|
| `@jupyterlite/xeus-core` | packages/xeus-core/ | 抽象基类与接口定义 |
| `@jupyterlite/xeus` | packages/xeus/ | empack具体实现、双Worker模式 |
| `@jupyterlite/xeus-extension` | packages/xeus-extension/ | JupyterLab扩展注册入口 |

## Python 依赖

```
empack>=5.1.1,<7
traitlets
jupyterlite-core>=0.7.0,<0.9.0
pyyaml
requests
```

## 构建系统

- **Python**: hatchling + hatch-nodejs-version + jupyter-builder
- **JavaScript/TypeScript**: lerna monorepo + tsc + webpack
- **内核打包**: empack（conda环境→WASM可用tar.gz）
- **环境创建**: micromamba（emscripten-wasm32平台）

## 默认 Channels

```python
DEFAULT_CHANNELS = [
    "https://prefix.dev/emscripten-forge-4x",
    "https://prefix.dev/conda-forge"
]
```

## 支持的内核

- xeus-python（Python内核）
- xeus-lua（Lua内核）
- xeus-r（R内核）
- xeus-cpp（C++内核）
- xeus-nelson（Nelson内核）
- xeus-javascript（JavaScript内核）

## 相关概念

- [项目架构](../concepts/02-architecture.md)
- [构建系统](../concepts/05-build-system.md)
