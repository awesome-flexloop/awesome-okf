# FPS 源码信源索引

本目录登记 fps 各核心模块的源码位置与 API 清单，供 concepts 文档溯源引用。

| 信源文件 | 对应源码 | 覆盖API |
|---------|---------|---------|
| [module-source.md](module-source.md) | `src/fps/_module.py` | Module类、initialize、生命周期方法 |
| [context-source.md](context-source.md) | `src/fps/_context.py` | Context、SharedValue、Value、put/get/get_nowait |
| [config-source.md](config-source.md) | `src/fps/_config.py` + `src/fps/_importer.py` | get_root_module、merge_config、import_from_string |
| [signal-source.md](signal-source.md) | `src/fps/_signal.py` | Signal类（connect/emit/iterate） |
| [cli-source.md](cli-source.md) | `src/fps/cli/_cli.py` | CLI命令选项与执行流程 |
| [web-source.md](web-source.md) | `src/fps/web/fastapi.py` + `src/fps/web/server.py` | FastAPIModule、ServerModule |

```{toctree}
:hidden:

cli-source
config-source
context-source
module-source
signal-source
web-source
```
