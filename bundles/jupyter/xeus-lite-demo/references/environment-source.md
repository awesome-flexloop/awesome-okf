---
type: Reference
title: 运行时环境配置信源
description: environment.yml 完整内容登记，定义浏览器内 WASM 运行时的 conda 包环境
tags: [environment, conda, wasm, emscripten-forge, xeus-python, reference]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: env-yml
    resource: https://github.com/jupyterlite/xeus-lite-demo/blob/main/environment.yml
    title: xeus-lite-demo environment.yml
---

## 源文件路径

`environment.yml`（仓库根目录）

## 完整内容

```yml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-python
  - ipycanvas
```

## 字段解析

| 字段 | 值 | 说明 |
|------|-----|------|
| `name` | `xeus-kernel` | 环境名称，标识这是 xeus 内核环境 |
| `channels[0]` | `https://repo.prefix.dev/emscripten-forge-dev` | WASM 编译包通道，提供 xeus 内核和已编译为 WebAssembly 的 conda 包 |
| `channels[1]` | `https://repo.prefix.dev/conda-forge` | prefix.dev 镜像的 conda-forge 通道，提供通用 WASM 包 |
| `dependencies[0]` | `xeus-python` | Python 内核（基于 xeus 的 WASM Python 实现） |
| `dependencies[1]` | `ipycanvas` | Interactive Canvas 组件，用于在 Notebook 中绘制图形 |

## 关键说明

- 此文件定义的是**浏览器内运行时**的包环境，所有包必须是 emscripten-forge 编译的 WASM 版本
- channels 顺序重要：emscripten-forge-dev 优先，确保获取 WASM 特化包
- prefix.dev 是 conda 包的托管平台，emscripten-forge 使用其分发 WASM 包
- 修改此文件后 push 到 main 分支，GitHub Actions 自动重建部署
