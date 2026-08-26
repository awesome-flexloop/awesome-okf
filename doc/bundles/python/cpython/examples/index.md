# 实战示例

本目录包含 3 个 CPython 实战示例文档。

* [最简 C 扩展模块](minimal-c-extension.md) — 从零编写一个 CPython C 扩展，包含方法定义、参数解析、setup.py 构建。
* [用 C 定义自定义类型](custom-type-c.md) — 在 C 扩展中定义新的 Python 类型，覆盖 tp_new/tp_init/tp_dealloc、方法表、属性访问。
* [字节码剖析](bytecode-dissection.md) — 使用 dis 模块反汇编 Python 函数，理解 LOAD_FAST/CALL/RETURN_VALUE 等字节码指令的执行过程。

```{toctree}
:maxdepth: 7

bytecode-dissection
custom-type-c
minimal-c-extension
```
