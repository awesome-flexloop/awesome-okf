---
type: Index
title: Xeus 信源参考索引
description: jupyterlite-xeus v5.0.0 各核心模块源码级参考文档索引
tags: [references, index, xeus, source]
status: stable
---

# Xeus 信源参考索引

本目录包含 jupyterlite-xeus v5.0.0 各核心模块的源码级参考文档，为概念文档和示例提供可追溯的代码依据。

## 信源列表

| 信源文件 | 覆盖模块 | 对应事实 |
|---------|---------|---------|
| [kernel-base-source.md](kernel-base-source.md) | xeus-core 基类（WebWorkerKernelBase、XeusRemoteKernelBase、XeusWorkerLoggerBase、接口定义） | F-015~F-052 |
| [kernel-impl-source.md](kernel-impl-source.md) | xeus 包具体实现（WebWorkerKernel、EmpackedXeusRemoteKernel、IEmpackXeusWorkerKernel） | F-053~F-077 |
| [worker-modes-source.md](worker-modes-source.md) | coincident/comlink 双Worker模式实现 | F-078~F-092 |
| [extension-source.md](extension-source.md) | JupyterLab扩展注册（kernelPlugin、empackEnvMetaPlugin、tokens） | F-093~F-107 |
| [python-addon-source.md](python-addon-source.md) | Python构建端XeusAddon（post_build、环境创建、内核复制、empack打包） | F-108~F-130 |
| [conda-env-source.md](conda-env-source.md) | Conda环境创建与pip依赖安装 | F-131~F-137 |
| [metasource.md](metasource.md) | 项目元数据与依赖版本 | F-001~F-014 |

```{toctree}
:hidden:

conda-env-source
extension-source
kernel-base-source
kernel-impl-source
metasource
python-addon-source
worker-modes-source
```
