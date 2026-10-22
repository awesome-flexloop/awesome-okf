---
type: Reference
title: "信源登记簿：本地源码检出与官方博客"
description: "Humming 知识包信源登记——本地源码检出元信息（v0.1.18-1-g5b500b4）、源码树结构与关键文件清单、官方博客与作者自述入口、vLLM 集成侧文件清单"
tags: [humming, source-map, source-registry, repo-structure, provenance]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /source-map.md
    title: 本地源码检出登记（vllm-project/humming @ 5b500b4）
---

# 信源登记簿：本地源码检出与官方博客

## 一、本地源码检出登记

| 项 | 值 | 出处 |
|----|-----|------|
| 仓库 | `https://github.com/vllm-project/humming` | F-002 |
| 本地路径 | `D:\spaces\SpecWeave\external\libs\ai\vllm-project\humming` | — |
| commit | `5b500b407a716e9dfcede04a5eba97a6eece0508` | F-003 |
| git describe | `v0.1.18-1-g5b500b4` | F-003 |
| 提交时间 | 2026-10-21 13:54:07 +0800 | F-003 |
| 提交作者 | Chao Zhang | F-003 |
| 许可证 | Apache-2.0（仓库根 `LICENSE`） | F-004 |
| Python 要求 | `>=3.10` | F-005 |
| 运行期依赖 | 共 8 项（`torch>=2.7`、`triton`/`triton-windows`、`numpy`、`safetensors`、`jinja2`、`cuda-bindings`、`tqdm`、`tabulate`）；CUDA 编译依赖走 extras | F-005 |
| 版本号生成 | setuptools_scm（`post-release` 方案，写入 `humming/_version.py`，`fallback_version = "0.0.0"`） | F-006 |
| 运行时版本读取 | `humming.__version__` 三级回退：`humming._version` → `importlib.metadata.version("humming-kernels")` → `"0.0.0+unknown"` | F-008 |
| 抓取时点 | 2026-10-22 | — |

> **快照边界**：本束基于上述 commit。Humming 处于 0.1.x 快速迭代期（版本号三位数滚动），引用具体行号时须带版本口径；`stale_after: 2027-04-22` 前应复核。

## 二、源码树结构

```
humming/                          # 顶层：76 个 Python 文件（约 21103 行）
├── __init__.py                   # 13 行门面，仅导出 humming.ops / humming.dtypes（F-007）
├── _version.py                   # setuptools_scm 生成，勿手改
├── dtypes.py                     # 浮点/整型 dtype 定义与 scale 类型映射
├── layer.py                      # HummingLayer：nn.Module + dataclass（F-063）
├── forward.py                    # 前向计算路径
├── transform.py                  # 权重/输入 schema → humming 标准格式转换
├── build.py                      # 构建期辅助
├── device.py                     # 设备信息查询（SM 版本、峰值算力、带宽）
├── config/                       # 配置体系
│   ├── config.py                 # LayerConfig / ComputeConfig / TuningConfig（F-031~F-035）
│   ├── enum.py                   # GemmType / MmaType / WeightScaleType 等枚举（F-019~F-021、F-036~F-037）
│   ├── mma.py                    # MMA 能力表与未文档化格式白名单（F-027~F-029）
│   └── base.py                   # 配置基类
├── ops/                          # Python 算子出口（13 项 __all__，F-047）
│   ├── gemm.py                   # humming_gemm()：量化 GEMM 入口（F-049）
│   ├── input.py                  # process_input()：输入侧量化/融合/scatter（F-050）
│   ├── weight.py                 # quant/dequant/pack/unpack/repack 权重工具
│   ├── launcher.py               # register_kernel → torch.ops.humming.register_kernel（F-048）
│   ├── bench.py                  # tops_bench 基准入口
│   └── utils.py
├── schema/                       # 权重/输入 schema 注册表
│   ├── __init__.py               # WEIGHT_SCHEMA_MAP(12) / INPUT_SCHEMA_MAP(5)（F-023~F-024）
│   └── humming.py                # humming 标准格式转换与整数→浮点自动转换（F-026、F-030）
├── kernel/                       # Python 侧内核实现
│   ├── humming.py                # check_dtype()：类型与位宽硬约束（F-013~F-017）
│   └── ...                       # 内核调度与 launch 逻辑
├── jit/                          # JIT 编译栈
│   ├── compiler.py               # 编译签名、缓存、FileLock、错误处理（F-043~F-046）
│   ├── runtime.py                # 编译器选择优先级（F-041）
│   └── ...                       # NVRTC/NVCC 后端封装
├── tune/                         # 自动调优启发式
│   ├── __init__.py               # heuristics_map 按 SM 版本分派（F-056）
│   ├── base.py                   # 瓶颈判定、M 候选生成（F-057~F-059）
│   ├── candidate.py              # 候选 tile/warp 配置枚举
│   ├── raster.py                 # MoE 栅格化调度（F-060）
│   ├── sm75.py / sm8x.py / sm90.py / sm90_h20.py / sm100.py / sm120.py / sm121.py
│   └── ppu_sm80.py               # PPU 设备专用启发式
├── testing/                      # 测试与基准支撑设施（F-062）
├── utils/                        # cubin / cuda / device / jit / math / nvrtc / smem / weight
├── csrc/                         # C++ 侧
│   ├── launcher/                 # launcher.cpp、elf.h、mapped_file.h、tensor.h、tma.h…
│   ├── nvrtc_compile.cpp         # NVRTC 编译后端
│   ├── patch_cubin.cpp           # CUBIN 补丁（未文档化 FP 格式必需，F-028）
│   └── device_info.cpp
└── include/humming/              # CUDA 头文件（63 个 .cuh）+ csrc/ 下的 7 个 .h + 4 个 .cpp
    ├── scheduler.cuh
    ├── arith/                    # mainloop_arith、epilogue_arith、exp_offset
    ├── datatype/                 # dtypes、dequant{,_fused,_native,_prepare,_single}、base_conversion
    ├── epilogue/                 # gmem_writer、pipeline、smem_reducer、smem_writer
    ├── kernel/                   # humming.cuh / humming_ws.cuh / humming_umma.cuh、process.cuh
    │   └── process_input/        # activation / context / hadamard / quantization / thread_task（F-061）
    ├── memory/                   # g2s_loader、s2r_loader 及对应 pipeline
    ├── mma/                      # all / mxmma / umma / wgmma / wmma
    └── utils/ptx/                # barrier、tma、tcgen05、wgmma、warp、shared、math、legacy_load
```

其余顶层目录：

| 目录 | 内容 | 出处 |
|------|------|------|
| `docs/` | `config.md`（442 行配置参考） | F-040 |
| `tests/` | `kernels/humming/`(9)、`kernels/process_input/`(3)、`native/`、5 个 Python 级测试 | F-098 |
| `benchmarks/` | `bench_humming.py`、`bench_marlin.py`、`bench_cutlass_w8a8.py`、`bench_torch.py`、`bench_triton_moe.py` | F-095 |
| `benchmarks/results/` | 按设备分目录 `4090/`、`a800/`、`h20/`、`h200/` | F-096 |
| `tools/` | `build_native.py`（原生构建辅助） | — |
| `AGENTS.md` | 代码风格指南 | — |

## 三、关键文件清单

| 关注点 | 文件 | 行号锚点 |
|--------|------|----------|
| 官方定位与支持矩阵 | `README.md` | 4（定位）、12（scale 类型）、14（SM75+）、19（体积）、24-32（支持矩阵） |
| 最小可用示例 | `README.md` | 61-87 |
| 顶层导出面 | `humming/__init__.py` | 1-13 |
| 三层配置定义 | `humming/config/config.py` | 31-70、491-520、523-565 |
| 类型/位宽硬约束 | `humming/kernel/humming.py` | 427-470 |
| 枚举定义 | `humming/config/enum.py` | 4-10、49-73 |
| 未文档化 FP 白名单 | `humming/config/mma.py` | 43-51 |
| schema 注册表 | `humming/schema/__init__.py` | 17-38 |
| 整数→浮点自动转换 | `humming/schema/humming.py` | 290-319 |
| JIT 编译与缓存 | `humming/jit/compiler.py` | 56-108 |
| 编译器选择 | `humming/jit/runtime.py` | 64-80 |
| 缓存目录布局 | `humming/utils/jit.py` | 176-210 |
| 层生命周期 | `humming/layer.py` | 312-322、330-334、405-411、574-586、682 |
| 算子签名 | `humming/ops/gemm.py` / `input.py` | 45-63 / 118-138 |
| 调优启发式分派 | `humming/tune/__init__.py` | 29-43 |
| M 维候选生成 | `humming/tune/base.py` | 546-560 |
| 瓶颈判定 | `humming/tune/base.py` | 15-32 |
| 权重 repack 与 packing | `humming/include/humming/kernel/process.cuh` | 130、185-210 |

## 四、官方博客与外部信源

| 信源 | URL / 入口 | 采信内容 | 性质 |
|------|------------|---------|------|
| 官方博客发布公告 | https://vllm.ai/blog/2026-10-21-humming | 定位、致谢、量化支持说明、三层配置、性能数字与测试条件、路线图 | 一手（官方口径） |
| 官方仓库 | https://github.com/vllm-project/humming | README、AGENTS、代码 | 一手（源码） |
| 早期仓库地址 | `github.com/inclusionAI/humming`（后迁至 vllm-project） | 溯源线索 | 二手（作者自述） |
| vLLM 官方仓库 | https://github.com/vllm-project/vllm | 集成侧源码、依赖版本钉 | 一手（源码） |
| 作者知乎自述 | https://zhuanlan.zhihu.com/p/2021951434141222000 | 项目缘起（2025 年 Marlin 算子开发）、集成 PR #34556、支持范围与体积自述 | 一手（作者自述，早于本包快照） |
| vLLM 博客索引 | https://vllm.ai/blog | 定位本篇在博客序列中的位置 | 一手 |

## 五、vLLM 集成侧源码登记

| 文件 | 内容 | 出处 |
|------|------|------|
| `requirements/cuda.txt:32-33` | `humming-kernels[cu13]==0.1.17` 版本钉 | F-071 |
| `vllm/config/kernel.py:137,255,326` | `MoEBackend` / `LinearBackend` 枚举含 `"humming"` | F-074 |
| `vllm/model_executor/layers/quantization/__init__.py:29,179` | 量化方法注册项 `"humming"` → `HummingConfig` | F-075 |
| `vllm/model_executor/layers/quantization/humming.py:152-188,373+` | `HummingConfig` / `HummingLayerQuantizationConfig` / `HummingLinearMethod` / `HummingMoEMethod` | F-075~F-077 |
| `vllm/model_executor/layers/quantization/utils/humming/` | `activation.py` / `linear.py` / `moe.py` / `priority.py` / `schema.py` | F-076、F-078 |
| `vllm/model_executor/layers/fused_moe/experts/fused_humming_moe.py` | MoE 融合执行路径 | F-076 |
| `vllm/utils/humming.py` | `create_humming_locks` / `_patch_humming` | F-076 |

## 六、检索工具登记

| 工具 | 用途 | 说明 |
|------|------|------|
| `git log -S "humming-kernels" -- requirements/cuda.txt` | 依赖引入历史溯源 | 用于 F-072 的版本引入时点核验 |
| 逐 tag 比对 `requirements/cuda.txt` | 版本钉滚动核验 | 用于 F-072 各版本钉记录 |
| `grep -rn "import humming" vllm/` | 集成侧文件清单 | 用于 F-076 |
| 知乎 CLI `search zhihu --query ...` | 社区视角信源 | 作者自述文章（F-091~F-094） |
