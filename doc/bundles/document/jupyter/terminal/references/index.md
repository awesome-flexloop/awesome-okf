# JupyterLite Terminal 信源参考

本文档目录包含 JupyterLite Terminal 源码学习的信源登记文件，每个文件对应源码中一个核心模块的API清单，作为概念文档和示例文档的事实来源。

## 信源文档列表

| 文档 | 对应源码 | 核心内容 |
|------|----------|----------|
| [项目元信源](metasource.md) | `package.json`, `pyproject.toml` | npm/Python包元数据、依赖版本、构建脚本、目录结构 |
| [插件系统源码信源](plugin-source.md) | `src/index.ts` | 6个JupyterLab/Lite插件定义、依赖注入关系、activate实现、具名导出 |
| [LiteTerminalAPIClient API信源](client-source.md) | `src/client.ts`, `src/tokens.ts` | LiteTerminalAPIClient类完整API、startNew/createHeadlessShell、Private命名空间 |
| [Shell与Worker源码信源](shell-source.md) | `src/shell.ts`, `src/coincident.worker.ts`, `src/comlink.worker.ts` | TerminalShell类、Coincident/Comlink Worker实现、SharedArrayBufferFS、Worker构建配置 |
| [无头命令执行API信源](exec-source.md) | `src/exec.ts` | HeadlessShellPool、4个编程式命令、runOnSession执行流程、输出清理、超时机制 |
| [Python端源码信源](python-source.md) | `jupyterlite_terminal/__init__.py`, `jupyterlite_terminal/add_on.py` | Python包入口、_jupyter_labextension_paths、TerminalAddon post_build钩子、hatch构建配置 |

## 信源版本

所有信源基于 @jupyterlite/terminal v1.7.0-a0（兼容 JupyterLite 0.7.0~0.8.x）。

## 源码入口文件速查

| 文件 | 路径 | 说明 |
|------|------|------|
| 插件入口 | `src/index.ts` | 6个插件定义与导出 |
| Token定义 | `src/tokens.ts` | ILiteTerminalAPIClient接口 |
| API客户端 | `src/client.ts` | LiteTerminalAPIClient核心实现（~260行） |
| Shell实现 | `src/shell.ts` | TerminalShell类（~80行） |
| 无头命令 | `src/exec.ts` | HeadlessShellPool + 4命令（~280行） |
| SAB Worker | `src/coincident.worker.ts` | SharedBufferContentsAPI + CoincidentTerminalShellWorker |
| SW Worker | `src/comlink.worker.ts` | ComlinkTerminalShellWorker |
| Python入口 | `jupyterlite_terminal/__init__.py` | 版本 + labextension路径 |
| 构建插件 | `jupyterlite_terminal/add_on.py` | WASM文件复制post_build钩子 |

```{toctree}
:hidden:

client-source
exec-source
metasource
plugin-source
python-source
shell-source
```
