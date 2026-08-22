# Echo Kernel 信源参考

本文档目录包含 JupyterLite Echo Kernel 源码学习的信源登记文件，每个文件对应源码中一个核心模块的API清单。

## 信源文档列表

| 文档 | 对应源码 | 核心内容 |
|------|----------|----------|
| [插件注册信源](plugin-source.md) | `src/index.ts` | JupyterFrontEndPlugin定义、IKernelSpecs注册、EchoKernel工厂函数 |
| [内核类信源](kernel-source.md) | `src/kernel.ts` | EchoKernel类、BaseKernel继承、10个抽象方法实现、消息处理 |
| [Python包信源](python-source.md) | `jupyterlite_echo_kernel/__init__.py`, `pyproject.toml`, `install.json` | Python包入口、hatchling构建配置、JupyterLab扩展路径、hatch-jupyter-builder钩子 |

## 信源版本

所有信源基于 echo-kernel v0.4.0（JupyterLite 0.7.0 兼容版本）。
