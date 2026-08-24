# JupyterLite 信源参考

本文档目录包含 JupyterLite 源码学习的信源登记文件，每个文件对应源码中一个核心模块的API清单。

## 信源文档列表

| 文档 | 对应源码 | 核心内容 |
|------|----------|----------|
| [项目元信源](metasource.md) | 整体项目 | 版本信息、目录结构、包清单、架构特征 |
| [内核系统信源](kernel-source.md) | `packages/services/src/kernel/` | BaseKernel、LiteKernelClient、消息路由、WebSocket通信 |
| [内容管理信源](contents-source.md) | `packages/services/src/contents/` | BrowserStorageDrive、DriveFS、ContentsAPI、Emscripten FS桥接 |
| [构建系统信源](build-source.md) | `py/jupyterlite-core/` | LiteManager、Addon插件体系、Doit任务框架 |
| [应用框架信源](app-source.md) | `packages/application/` | JupyterLiteApp、扩展加载、Service Worker |

## 信源版本

所有信源基于 Git commit `cf4958fcd20763a61ce4c7eeb1394f3c60e16cb0`（2026年8月）。

```{toctree}
:hidden:

app-source
build-source
contents-source
kernel-source
metasource
```
