# 信源登记簿

本目录包含 rust-lang/rust 知识库的信源登记文件。

* [rustc 编译器信源登记](rustc-source-map.md) — 基线 commit 与版本、构建域划分、compiler/ 79 个 crate 清单、流水线各 crate 关键文件与行号坐标、tests 测试套件索引。
* [标准库信源登记](std-source-map.md) — library/ workspace 配置与特殊构建 profile、23 个目录清单、core/alloc/std 关键 lib.rs 与 sys/os 平台分发坐标、sysroot 与 panic 运行时坐标。

```{toctree}
:hidden:
:maxdepth: 7

rustc-source-map
std-source-map
```
