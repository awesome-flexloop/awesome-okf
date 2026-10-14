# 实战走读（Examples）

三篇走读均基于固定快照 `4df6562` 的 `examples/` 与 `libkywc/` 源码；文中构建/运行命令均标注「本次未执行」。

| 文档 | 走读对象 | 学到什么 |
|---|---|---|
| [跟写一个特效插件](01-effect-plugin-walkthrough.md) | `examples/simple_plugin.c`（simple.so）、alpha_modifier、kde_keystate | 插件数据结构填充、钩子注册、meson 目标声明与最小插件骨架 |
| [wlu 工具库与协议客户端](02-wlu-utilities-walkthrough.md) | `examples/lib/`（wlu）、monitor、output_doctor、virtual_desktop | Wayland 连接/registry 轮询、SHM 缓冲、输入监听与裸协议客户端写法 |
| [libkywc + QML 缩略图客户端](03-libkywc-qml-thumbnail.md) | `libkywc/` 67 API 与 `examples/gui/` | 稳定客户端库 API、C++/QML 数据桥、缩略图双路径与能力协商 |

```{toctree}
:hidden:
:maxdepth: 2

01-effect-plugin-walkthrough
02-wlu-utilities-walkthrough
03-libkywc-qml-thumbnail
```
