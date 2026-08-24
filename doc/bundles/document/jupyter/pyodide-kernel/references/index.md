# Pyodide Kernel 源码信源索引

本目录登记 jupyterlite-pyodide-kernel 各核心模块的源码位置与 API 清单，供 concepts 文档溯源引用。

| 信源文件 | 对应源码路径 | 覆盖范围 |
|---------|------------|---------|
| [addon-source.md](addon-source.md) | `jupyterlite_pyodide_kernel/addons/` | 构建端三个Addon（PyodideAddon/PipliteAddon/PyodideLockAddon）API、BaseAddon基类、常量定义 |
| [kernel-ts-source.md](kernel-ts-source.md) | `packages/pyodide-kernel/src/` | 主线程PyodideKernel类、Worker抽象基类、Comlink/Coincident两种实现、IOptions接口 |
| [kernel-py-source.md](kernel-py-source.md) | `packages/pyodide-kernel/py/pyodide-kernel/pyodide_kernel/` | 浏览器端Python Kernel（PyodideKernel/Interpreter/LiteStream/LiteDisplay/Comm/Mocks/Patches） |
| [piplite-source.md](piplite-source.md) | `packages/pyodide-kernel/py/piplite/piplite/` | piplite包管理器（install函数、三级查找、常量、PiplitePyPIManager） |
| [extension-source.md](extension-source.md) | `packages/pyodide-kernel-extension/src/` | JupyterLab扩展插件注册、Kernel Spec定义、插件设置Schema |

```{toctree}
:hidden:

addon-source
extension-source
kernel-py-source
kernel-ts-source
piplite-source
```
