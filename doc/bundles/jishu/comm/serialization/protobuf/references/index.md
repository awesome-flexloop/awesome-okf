# protobuf 信源登记簿

* [仓库结构与构建系统信源登记](repo-structure.md) — 主仓 v37.0-dev 根目录结构、版本常量与 Bazel/CMake 双构建系统的源码路径，支撑 F-REPO-001~067。
* [C++ 运行时核心信源登记](cpp-core.md) — src/google/protobuf/ 下消息模型、descriptor、wire format、IO 流、JSON 与 WKT 源码路径，支撑 F-CPP-001~144。
* [protoc 编译器信源登记](compiler.md) — compiler/ 下命令行框架、解析导入、九语言生成器与插件协议源码路径，支撑 F-CMP-001~090。
* [多语言运行时信源登记](runtimes.md) — Python、Rust、hpb、Java、C#、ObjC、PHP、Ruby、Lua 九大运行时源码路径，支撑 F-RT-001~105。
* [测试与规范体系信源登记](testing.md) — conformance、benchmarks、examples、editions 测试与 CI 辅助源码路径，支撑 F-TST-001~080。

```{toctree}
:hidden:
:maxdepth: 7

repo-structure
cpp-core
compiler
runtimes
testing
```
