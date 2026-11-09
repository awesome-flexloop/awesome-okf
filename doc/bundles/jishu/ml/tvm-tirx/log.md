# 更新日志

## 2026-11-09（源码核对）

**核对**：基于本地源码检出 `external/dev/libs/TIRx/tvm-tirx`（commit `cdc7a377`，2026-11-08）更新，修正三处文档-only 认知。

- **新增概念**：11 源码仓导航、12 后端矩阵、13 编译流水线。
- **事实台账**：F-001~F-099 → F-001~F-135（新增 36 条源码事实）。
- **关键修正**：
  - 后端不止 CUDA/LLVM：源码注册 10 个内置后端（cuda/metal/rocm/trn/opencl/vulkan/webgpu/hexagon/adreno/rust）；
  - `compile` 不是零 pass：存在固定 lowering 流水线（dispatch/layout/化简/展平/向量化/展开/CSE/校验/allreduce），只是不做搜索式调优；
  - Rust 不只是承诺：crate、stubgen 生成、`#[repr(C)]` ABI 校验、`libtvm_tirx_rust` 加载路径均在源码中。
- **核验**：P0 由 20 项增至 26 项（18 ✅ / 3 ⚠️ / 5 ❌）；洞察 9 条、模式 5 条、审查 6 视角。
- **边界**：源码为静态阅读，未执行构建/测试；非 CUDA 后端未实测。

## 2026-11-09（增补第一代）

**增补**：纳入 2026-06 第一代 TIRx 的两篇官方文章，补齐「两代演进 + layout/dispatch + 性能证据」。

- **新增信源**：Apache 官方博客 *TIRx: An Open Compiler Stack for Evolving Frontier ML Kernels*（2026-06-22）+ 知乎中文版（侯博涵，2026-06-23）+ PyPI `apache-tvm` 0.25.0。
- **新增概念**：08 两代对照、09 storage-first layout 与 tile 派发、10 54 配置 B200 基准解读。
- **新增示例**：layout-mapping（元素 57 的 warp/lane/reg 手算）。
- **事实台账**：F-001~F-064 → F-001~F-099，新增 35 条第一代事实与两代边界观察。
- **关键修订**：
  - 区分第一代（`apache-tvm` 0.25.0，`@T.jit`/`@T.prim_func`、`Tx.*`）与第二代（`apache-tvm-tirx` 0.1.0b1，`@T.function`）；
  - 第一代 1517/1404/2895/5930 TFLOPS 等基准**不得外推**到第二代；
  - 洞察由 5 条增至 7 条、模式由 3 条增至 4 条、对抗审查增至 5 视角。
- **核验**：P0 由 15 项增至 20 项（14 ✅ / 3 ⚠️ / 3 ❌）。

## 2026-11-09（创建）

**创建**：TVM TIRx 知识包（`jishu/ml/tvm-tirx`）首次入库。

- **信源**：知乎专栏《构建 Agent 时代的机器学习编译基础层》（陈天奇，2026-11-05）+ Apache TVM 官方博客（2026-11-03）+ `apache/tvm-tirx` 仓库 + 官方文档站 + PyPI。
- **结构**：8 篇概念文档、3 篇示例、3 篇参考文档（F-001~F-064 编号事实、信源核验、洞察模式）。
- **核验**：15 项 P0 核验（10 ✅ / 3 ⚠️ / 2 ❌），两处两源冲突已记录并给出裁决口径。
- **边界**：未做源码逐行精读、未独立安装运行、未引用性能基准；Rust 成熟度以官方博客「work in progress」为准。
- **方法**：方法论编排（R→I→E→V→C），质量门 G1-G4 自检通过。
