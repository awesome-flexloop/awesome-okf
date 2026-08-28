# 实战示例

本目录包含 2 个 rust-lang/rust 实战走读文档。

* [x.py 构建流程剖析](x-py-build-walkthrough.md) — 沿一次 ./x 调用逐层走读：入口解释器选择、bootstrap 自我编译、Kind 分发、三阶段自举展开与 build/ 产物观察。
* [std 模块结构剖析](std-module-anatomy.md) — 以 library/std 为标本的逐层走读：门面组织、sys/os 平台分发、env/fs 代表模块 API 表面、启动链与 sysroot 收口。

```{toctree}
:hidden:
:maxdepth: 7

x-py-build-walkthrough
std-module-anatomy
```
