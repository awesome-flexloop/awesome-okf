# 实战示例

本目录包含 rust/cargo bundle 的 2 个示例文档，均为源码纵贯走读，其引用的事实编号全部来自概念文档已主覆盖的编号集合。

* [cargo new 源码路径追踪](cargo-new-source-trace.md) — 从进程入口到 ops::cargo_new 的五站实走：CLI 分发决策树、薄壳模式验证与 Workspace 缺席的特例。
* [Cargo.toml 解析流程](cargo-toml-parsing-flow.md) — 从磁盘清单到 Workspace 数据模型的逐站拆解：parser、EitherManifest、继承字段与 config.toml 管线对照。

```{toctree}
:hidden:
:maxdepth: 7

cargo-new-source-trace
cargo-toml-parsing-flow
```
