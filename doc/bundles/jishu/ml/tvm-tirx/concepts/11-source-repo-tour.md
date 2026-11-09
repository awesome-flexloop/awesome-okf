---
type: Concept
title: 源码仓导航——目录、模块职责与构建测试
description: 基于本地 apache/tvm-tirx 检出（commit cdc7a37，2026-11-08）梳理仓库布局、C++/Python/Rust 模块职责、scikit-build-core + uv 构建、CMake 开关、测试与 CI
tags: [tvm-tirx, 源码, 仓库结构, 构建, cmake, 测试, ci, rust]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: local-checkout
    resource: https://github.com/apache/tvm-tirx/tree/cdc7a37793e449917faa2dcaa66df1bb61df2ba5
    title: apache/tvm-tirx 源码快照（commit cdc7a377，2026-11-08）
  - id: repo-agents
    resource: https://github.com/apache/tvm-tirx/blob/cdc7a37793e449917faa2dcaa66df1bb61df2ba5/AGENTS.md
    title: TVM TIRx AGENTS.md
  - id: pyproject
    resource: https://github.com/apache/tvm-tirx/blob/cdc7a37793e449917faa2dcaa66df1bb61df2ba5/pyproject.toml
    title: pyproject.toml
---

# 源码仓导航

> 文中 `[F-xxx]` 为编号事实，来源见 [facts.md](../references/facts.md)。
> **快照**：本地检出 `cdc7a37793e449917faa2dcaa66df1bb61df2ba5`（2026-11-08，工作树干净）[F-100]。所有路径均相对于仓库根。

## 1. 一句话定位（来自仓内 AGENTS.md）

> TIRx is a compiler foundation for development of ML compilers and agentic compiler harnesses. [F-101]

与官网 README 的「minimal, stable, extensible DSL and compiler foundation」相比，仓内表述更强调 **agentic compiler harness**——基础层之上还要能搭分析/实验/验证工具。

## 2. 顶层目录职责

| 目录 | 职责 | 关键内容 |
|------|------|----------|
| `include/tvm/` | C++ 公共头 | `ir/`、`sym/`、`tirx/`、`target/`、`runtime/`、`codegen/`、`backend/` [F-102] |
| `src/` | C++ 实现 | 编译器、运行时、codegen（C/LLVM）、各 backend [F-102] |
| `python/tvm_tirx/` | Python 包与 C++ 反射绑定 | `ir`、`tirx`、`sym`、`script`、`backend`、`codegen`、`runtime`、`target`、`testing`、`support` [F-103] |
| `rust/tvm-tirx/` | Rust crate | IR/分析/Pass/扩展 API；对象定义由 stubgen 生成 [F-104] |
| `tests/cpp/` | GoogleTest | C++ 单元测试 [F-101] |
| `tests/python/` | pytest | 按命名空间与 backend 组织 [F-101] |
| `tests/lint/` | 合规检查 | ASF header、文件类型 [F-101] |
| `docs/` | Sphinx 文档 | RST + autosummary；含 IR/编程/扩展/后端参考 [F-105] |
| `cmake/` | 构建模块 | LLVM/CUDA/Metal/ROCm/Vulkan/OpenCL/Z3/Rust 的 finder 与配置 [F-106] |
| `3rdparty/tvm-ffi/` | TVM-FFI 子模块 | 对象、反射、packed function、ABI [F-107] |
| `ci/jenkins/`、`ci/wheel/` | CI 与 wheel | Linux ARM/GPU/EXTRA 流水线、manylinux/macOS/Windows 修复 [F-108] |

## 3. Python 包模块地图

仓内 AGENTS.md 给出六条职责边界 [F-103]：

| 模块 | 职责 |
|------|------|
| `tvm_tirx.ir` | 共享表达式、类型、语句、函数、模块、源码位置 |
| `tvm_tirx.tirx` | 张量程序构造、layout、分析、lowering pass |
| `tvm_tirx.sym` | 化简与符号推理（含 Z3 集成） |
| `tvm_tirx.script` | 共享解析/打印 + TIRx 方言 builder |
| `tvm_tirx.backend` | 目标相关算子、变换、代码生成、运行时支持 |
| `tvm_tirx.runtime` / TVM-FFI | 对象、反射、packed function、设备感知运行时 |

几个容易忽略的具体模块：

- `python/tvm_tirx/tirx/layout.py`：`Layout`、`TileLayout`、`ComposeLayout`、`Axis`、`S`、`R` [F-109]；
- `python/tvm_tirx/tirx/compilation_pipeline.py`：默认 lowering 流水线 [F-110]；
- `python/tvm_tirx/codegen/executable.py`：`Executable` 的 `jit()` / `export_library()` [F-111]；
- `python/tvm_tirx/backend/_autoload_backends.py`：内置后端与外部后端入口点 [F-112]。

## 4. 构建系统

| 项 | 事实 |
|----|------|
| 包名 / 版本 | `apache-tvm-tirx` / `0.1.0b1` [F-113] |
| 构建后端 | `scikit-build-core>=0.11` [F-114] |
| Python | `>=3.10`；classifier 覆盖 3.10–3.13，Development Status 4 - Beta [F-113] |
| C++ | C++20 编译器 + CMake ≥3.26 + Ninja [F-101] |
| 包管理 | `uv sync` 管理 `.venv`；`uv run --no-sync` 在环境中执行 [F-101] |
| 运行时依赖 | `apache-tvm-ffi>=0.1.15.post1`、`apache-tvm-ffi-orcjit>=0.1.3`、`ml_dtypes`、`numpy` [F-115] |
| 构建期依赖 | `mlc-llvm-static[all]==23.1.1.post0`、`mlc-z3-static==5.3.1.post1` [F-116] |
| wheel 组件 | `tvm_tirx` + `tvm_tirx_llvm_backend` [F-117] |

最小构建命令（官方 AGENTS.md）[F-101]：

```bash
git submodule update --init --recursive
uv sync --no-default-groups
```

Rust 测试单独执行（见第 6 节），不要与 Python 编辑安装混为一步。

C++-only 构建：

```bash
uv sync --only-group build
uv run --no-sync cmake -S . -B build_cpp -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
uv run --no-sync cmake --build build_cpp --parallel --config RelWithDebInfo --target tvm_tirx_compiler
```

## 5. CMake 开关

| 开关 | 默认 | 作用 |
|------|------|------|
| `TVM_TIRX_USE_LLVM` | ON | LLVM 代码生成 [F-118] |
| `TVM_TIRX_USE_Z3` | AUTO | Z3 SMT 求解器支持 [F-118] |
| `TVM_TIRX_USE_CUDA` | AUTO | CUDA 后端 [F-118] |
| `TVM_TIRX_USE_OPENCL` | OFF | OpenCL 后端 [F-118] |
| `TVM_TIRX_USE_VULKAN` | OFF | Vulkan / SPIR-V [F-118] |
| `TVM_TIRX_USE_ROCM` | OFF | ROCm 后端 [F-118] |
| `TVM_TIRX_USE_METAL` | OFF | Metal 后端 [F-118] |
| `TVM_TIRX_USE_RUST` | AUTO | 用 cargo 构建 Rust 算子 [F-118] |
| `TVM_TIRX_BUILD_TESTS` | OFF | 构建 C++ 测试 [F-118] |

> `AUTO` 的含义是「探测到依赖就启用」，不是「默认保证可用」。CI 的 GPU/ARM/EXTRA 分支也说明后端覆盖需要专门构建 [F-108]。

## 6. 测试、lint 与 CI

| 层 | 命令/入口 | 说明 |
|----|-----------|------|
| Python 测试 | `uv run --no-sync pytest -v tests/python -m "not gpu"` | GPU 测试用 `-m gpu` [F-101] |
| C++ 测试 | `cmake ... -DTVM_TIRX_BUILD_TESTS=ON` + `ctest` | GoogleTest [F-101] |
| Rust 测试 | `cargo test --manifest-path rust/Cargo.toml` | crate 依赖 `tvm-tirx-config`/`tvm-ffi-config` [F-104] |
| lint | `pre-commit run --all-files` | ASF header、ruff、clang-format 等 [F-101] |
| CI | GitHub Actions（macOS/Windows/lint）+ Jenkins（ARM/GPU/EXTRA） | GPU 构建一个 CUDA wheel 供 CPU/GPU/文档使用 [F-108] |

## 7. 源码核对后需要修正的三个认知

1. **后端不止 CUDA/LLVM**：源码注册了 10 个内置后端，另有 LLVM 核心 codegen（见 [12-backend-matrix](12-backend-matrix.md)）[F-112]。
2. **`compile` 不是「零 pass」**：它有一条确定的 lowering 流水线（dispatch/layout/flatten/vectorize/unroll/CSE/verify/reduce），只是不做搜索式调优（见 [13-compiler-pipeline](13-compiler-pipeline.md)）[F-110]。
3. **Rust 不只是文档承诺**：仓内有 `rust/tvm-tirx` crate、stubgen 生成的对象定义、`libtvm_tirx_rust` 加载路径；官方仍标 WIP，但工程链路是真实存在的 [F-104]。

## 8. 快速定位表

| 你想看什么 | 去哪里 |
|------------|--------|
| Python API 全貌 | `python/tvm_tirx/` 各模块 `__init__.py` |
| IR 对象定义 | `include/tvm/ir/*.h`、`include/tvm/tirx/*.h` |
| Layout 实现 | `include/tvm/tirx/layout.h`、`python/tvm_tirx/tirx/layout.py` |
| Lowering 顺序 | `python/tvm_tirx/tirx/compilation_pipeline.py` |
| 后端注册 | `python/tvm_tirx/backend/_autoload_backends.py` |
| 编译/导出 | `python/tvm_tirx/codegen/executable.py` |
| C++ 运行时 | `src/runtime/`、`include/tvm/runtime/` |
| CUDA codegen | `src/backend/cuda/`、`python/tvm_tirx/backend/cuda/` |
| 官方示例 | `examples/quick_start/`、`examples/ir_guides/`、`examples/extension_guides/` |
