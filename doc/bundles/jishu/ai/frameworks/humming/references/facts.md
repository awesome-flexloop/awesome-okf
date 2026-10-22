---
type: Reference
title: "事实清单 F-001~F-106（Humming v0.1.18）"
description: "Humming 知识包编号事实清单——106 条事实采自本地源码检出 v0.1.18-1-g5b500b4（2026-10-21）、vLLM v0.32.1rc0-283 集成侧源码、vllm.ai 官方博客（2026-10-21）与知乎作者自述文章；每条标注来源，官网数字标注测试条件与时点"
tags: [humming, facts, fact-list, evidence, source-cited, quantization, gemm]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /source-map.md
    title: 本地源码检出登记（vllm-project/humming @ 5b500b4）
  - id: blog
    url: https://vllm.ai/blog/2026-10-21-humming
    title: Announcing Humming: Fast, Flexible Kernels for Quantized Inference（2026-10-21）
  - id: vllm-local
    resource: vllm-project/vllm @ 7d5335936c40306063a29fc4e2ccbe71b280e40c
    title: vLLM 本地源码检出（v0.32.1rc0-283，2026-10-22）
  - id: zhihu-author
    url: https://zhuanlan.zhihu.com/p/2021951434141222000
    title: 通用高性能量化推理算子库 Humming（作者 Jinzhen 自述，知乎专栏）
---

# 事实清单 F-001~F-106

采集口径：**本地源码（一手）+ 官方博客（一手）+ vLLM 集成侧源码（一手）+ 作者知乎自述（一手）**。每条事实给出来源（源码相对路径、commit 或 URL）。标注「推导」的为基于事实的工程结论，非原文陈述。性能数字一律附带测试条件与硬件上下文，不作为通用结论。

---

## 一、项目身份与版本（F-001~F-012）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-001 | 官方定位："Humming is a high-performance, lightweight, and highly flexible JIT (Just-In-Time) compiled GEMM kernel library specifically designed for quantized inference."（面向量化推理的高性能、轻量、高灵活 JIT 编译 GEMM 内核库） | README.md:4 |
| F-002 | 仓库地址 `https://github.com/vllm-project/humming`；归属 vLLM 生态组织 | README.md:54；官方博客 |
| F-003 | 本地检出版本 `v0.1.18-1-g5b500b4`，commit `5b500b407a716e9dfcede04a5eba97a6eece0508`，提交时间 2026-10-21 13:54:07 +0800，作者 Chao Zhang | 本地 git describe / git log |
| F-004 | 许可证 Apache-2.0 | 仓库根 `LICENSE` |
| F-005 | PyPI 包名 `humming-kernels`；`requires-python = ">=3.10"`；运行期依赖共 8 项：`torch>=2.7`、`triton`（非 win32）/ `triton-windows>=3.8.0.post29`（win32）、`numpy`、`safetensors`、`jinja2`、`cuda-bindings`、`tqdm`、`tabulate`；CUDA 编译依赖走 extras | `pyproject.toml:6,10,23-33` |
| F-006 | 版本号由 setuptools_scm 动态生成（`version_scheme = "post-release"`，`version_file = "humming/_version.py"`，`fallback_version = "0.0.0"`） | `pyproject.toml:56-59` |
| F-007 | 顶层包 `humming/__init__.py` 仅 13 行，导出面收敛为 `import humming.ops` 与 `import humming.dtypes`；**不导出** `HummingLayer`——正确入口是 `from humming.layer import HummingLayer` | `humming/__init__.py:1-13` |
| F-008 | 顶层 `__version__` 三级回退：`humming._version` → `importlib.metadata.version("humming-kernels")` → `"0.0.0+unknown"` | `humming/__init__.py:2-9` |
| F-009 | 项目由 **Ant Group 与 vLLM community** 联合开源；博客致谢点名 Jinzhen Lin、Zekai Gu、Zhilin Huang（Ant Group）与 Michael Goin、Roberto L. Castro、Chauncey Jiang（vLLM community） | 官方博客「Acknowledgement」节 |
| F-010 | 项目名取自**蜂鸟（hummingbird）**，与「轻量化 + 高性能」定位相称 | 作者知乎自述「Humming算子」节 |
| F-011 | 源码规模：`humming/` 下 76 个 Python 文件（约 21103 行）+ 74 个 CUDA/C++/头文件 | 本地 find 统计（2026-10-22） |
| F-012 | 打包体积：README 称「The package size is only **100+KB**」（包体积 100+KB）；官方博客称「wheel package 约为 **500 KB**」——**两处口径不一致**，见 [verification.md](verification.md) 差异 #2 | README.md:19；官方博客「Usage / Installation」节 |

---

## 二、量化格式与支持矩阵（F-013~F-030）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-013 | 激活类型与权重类型的支持关系由 `check_dtype()` 的 `dtype_map` 判定：int4/int8/float16 门槛 SM75，bfloat16 门槛 SM80，float8e4m3/float8e5m2 门槛 SM89，float4e0m3/float4e2m1/float8e3m4 门槛 SM100（当 `mma_type == UMMA`）否则 SM120 | `humming/kernel/humming.py:427-440` |
| F-014 | 权重侧额外允许 float6e3m2 / float6e2m3，门槛同上（SM100 UMMA 或 SM120） | `humming/kernel/humming.py:442-448` |
| F-015 | 硬约束：权重位宽 `b_dtype.num_bits <= 8`，且 `b_dtype.num_bits <= a_dtype.num_bits`（权重位宽不得超过激活位宽） | `humming/kernel/humming.py:455-456` |
| F-016 | 整数权重 + 浮点激活时：权重必须为**无符号**（`not self.b_dtype.is_signed`），且位宽严格小于激活；带零点时 `b_bits <= mma_b_dtype.mantissa_bits + 1`，不带零点时 `b_bits <= mantissa_bits + 2` | `humming/kernel/humming.py:462-467` |
| F-017 | 浮点权重 + 浮点激活时：权重必须**带符号**（`assert self.b_dtype.is_signed`）；非原生权重时按 mantissa/exponent 位数逐项校验 | `humming/kernel/humming.py:468-470` |
| F-018 | README 支持矩阵给出 7 种激活类型：FP16(SM75+)、BF16(SM80+)、FP8 e4m3(SM89+)、FP8 e5m2(SM89+)、FP4 e2m1(SM120+)、INT8(SM75+)、INT4(SM80+) | README.md:24-32 |
| F-019 | 权重粒度类型枚举 `WeightScaleType`：`GROUP` / `BLOCK` / `CHANNEL` / `TENSOR` | `humming/config/enum.py:56-60` |
| F-020 | 二级 scale 类型枚举 `WeightScale2Type`：`NONE` / `CHANNEL` / `TENSOR` | `humming/config/enum.py:63-66` |
| F-021 | 输入量化模式枚举 `InputQuantizationMode` 六态：`none` / `static_tensor` / `dynamic_token` / `dynamic_group` / `static_tensor_dynamic_group` / `dynamic_group_token` | `humming/config/enum.py:4-10` |
| F-022 | 支持的 scale 数据类型含 BF16、FP16、E4M3、E5M2 与 UE8M0（源码中为 `float8e8m0`，映射 `torch.float8_e8m0fnu`） | README.md:12；`humming/dtypes.py:213,222` |
| F-023 | 权重 schema 注册表 `WEIGHT_SCHEMA_MAP` 收录 12 个条目：auto-round、auto_round、awq、bitnet、compressed-tensors、fp8、gptq、humming、modelopt、mxfp4、gpt_oss_mxfp4、quark | `humming/schema/__init__.py:17-30` |
| F-024 | 输入 schema 注册表 `INPUT_SCHEMA_MAP` 收录 5 个条目：compressed-tensors、fp8、humming、modelopt、quark | `humming/schema/__init__.py:32-38` |
| F-025 | 特殊浮点格式（指数位为 0）可表示的数值范围与同位宽对称整数相同：INT8 排除 -128、float8e0m7 排除 -128，两者均可表示 -127~127 | 官方博客「Quantization Support」节 |
| F-026 | Humming 会**自动**把符合条件的对称整数权重转换到指数位为 0 的浮点格式：转换在 `convert_symmetric_integer_weight()`，条件为整型、位宽 2–8、无整数零点、且权重中不含 0 值；转换后 `b_dtype` 变为 `FloatingPointType(num_bits, exponent_bits=0, mantissa_bits=num_bits-1)` | `humming/schema/humming.py:290-319` |
| F-027 | 源码内「未文档化」浮点格式为 `float8e3m4` 与 `float4e0m3`（`UNDOCUMENTED_FP_DTYPES`）；已验证可执行的架构白名单为 SM100、SM103、SM120、SM121（`UNDOCUMENTED_FP_SM_VERSIONS`） | `humming/config/mma.py:43-47` |
| F-028 | 使用未文档化格式需同时满足两个条件：CUBIN 补丁已启用（`is_cubin_patch_enabled()`）**且**架构在白名单内 | `humming/config/mma.py:49-51` |
| F-029 | 源码注释明确警告：新增架构必须在真机测试后才可加入白名单——**SM107 执行这两种编码会抛 illegal instruction** | `humming/config/mma.py:44-45` |
| F-030 | 权重 schema 转换时会执行 `pack_weight` / `unpack_weight`；Humming 内部整数权重统一使用 **offset-binary 编码**（即使源格式为有符号） | `humming/schema/humming.py:298` 注释；`humming/schema/humming.py:299,314` |

---

## 三、配置体系（F-031~F-040）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-031 | 三层配置：**LayerConfig**（形状/数据类型/量化参数/目标架构）、**ComputeConfig**（GEMM 类型/计算选项/batch invariance/input scale layout）、**TuningConfig**（tile 形状/流水级数/warp 特化/访存/MMA 指令/并发/调度/TMA） | 官方博客「Tuning Config」节；`humming/config/config.py` |
| F-032 | `LayerConfig` 关键字段：`sm_version`、`shape_n`/`shape_k`/`pad_shape_n`/`pad_shape_k`/`num_experts`、`b_dtype`/`a_dtype`/`c_dtype`/`bs_dtype`/`as_dtype`、`input_quant_mode`、`input_scale_group_size`、`weight_scale_group_size`/`weight_scale_group_size_n`、`weight_scale_type`/`weight_scale_2_type`、`use_int_weight_scale`/`use_fused_e8m0_scale`、`has_zero_point`/`is_fp_zero_point`、`has_bias`、`use_packed_k_layout` | `humming/config/config.py:31-70` |
| F-033 | `ComputeConfig` 字段：`use_f16_accum`、`use_batch_invariant`、`use_m_major_input_scale`、`gemm_type`；派生属性 `is_indexed_gemm`/`is_grouped_contiguous_gemm`/`is_grouped_masked_gemm`/`is_grouped_gemm` 由 `gemm_type` 自动推导 | `humming/config/config.py:491-520` |
| F-034 | 约束：indexed GEMM **不支持** m-major input scale（`assert not self.use_m_major_input_scale`） | `humming/config/config.py:513-514` |
| F-035 | `TuningConfig` 字段含 `mma_type`、`block_shape`/`warp_shape`、`use_stream_k`（默认 True）、`num_stages`（默认 2）、`num_ctas_per_sm`（默认 1）、`use_warp_spec`、逐张量的 `use_tma*` 开关、`smem_reuse_mode`、`multi_cast_size_a`/`_b`、`use_pdl`、`raster_group_m`、`evict_weights_first`，以及 UMMA 专有的 `umma_num_dequant_warpgroups`/`umma_cta_group_size` | `humming/config/config.py:523-565` |
| F-036 | GEMM 类型枚举 `GemmType` 四态：`DENSE` / `INDEXED` / `GROUPED_CONTIGUOUS` / `GROUPED_MASKED` | `humming/config/enum.py:69-73` |
| F-037 | MMA 指令类型枚举 `MmaType` 四态：`MMA` / `WGMMA` / `UMMA` / `MXMMA` | `humming/config/enum.py:49-53` |
| F-038 | 权重 scale 类型缺省推断规则：仅依据 `weight_scale_group_size_n` 与 `weight_scale_group_size`——`weight_scale_group_size_n > 1` → `BLOCK`；`weight_scale_group_size == 0` → `CHANNEL`；否则 → `GROUP`。**与权重数据类型无关** | `humming/config/config.py:270-276`；`humming/schema/humming.py:47-54` |
| F-039 | `MXMMA` 原生混合精度仅在「激活为 float8e4m3/float8e5m2 **且** 权重为 float4e2m1/float6e3m2/float6e2m3」时成立 | `humming/config/config.py:592-599` |
| F-040 | 官方提供完整配置参考文档 `docs/config.md`（共 442 行，逐字段说明 LayerConfig / ComputeConfig / TuningConfig） | `docs/config.md:1-442` |

---

## 四、JIT 编译与运行时（F-041~F-050）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-041 | 编译器选择顺序：环境变量 `HUMMING_COMPILER`（`nvcc`/`nvrtc`）> PPU 设备强制 NVCC > 尝试导入 `cuda.bindings.nvrtc` 成功则用 NVRTC > 失败回退 NVCC | `humming/jit/runtime.py:64-80` |
| F-042 | 编译缓存目录 `~/.humming/cache/<hash>/`，临时目录 `~/.humming/tmp/`，模块目录 `~/.humming/tmp/module/`，锁目录 `~/.humming/tmp/lock/`；可用 `HUMMING_CACHE_DIR` / `HUMMING_TMP_DIR` 覆盖 | `humming/utils/jit.py:176-210` |
| F-043 | 编译签名 = 编译器类名 + 类级签名 + 编译 flags + kernel 表达式 + kernel 源码 + `cuh_last_update_time()`；后者是 `include/**/*.cuh` 的「**绝对路径 → mtime**」JSON 字典（**含路径，故缓存不跨安装路径可移植**）；`patch_cubin.cpp` 的内容哈希**总是**拼入签名（判据是 `postprocess_cubin` 参数非 None，与 CUBIN 补丁开关无关） | `humming/jit/compiler.py:48-54,56-71`；`humming/jit/runtime.py:101` |
| F-044 | 缓存命中直接返回 `kernel.cubin`；编译产物在缓存目录留下 `kernel.cu`（源码）、`signature.txt`（签名）、`stdout.log` / `stderr.log`（编译日志） | `humming/jit/compiler.py:73-108` |
| F-045 | 并发编译用文件锁（`FileLock`）保护，避免多进程同时写同一缓存目录；**锁在缓存命中检查之前获取**——即使缓存已命中，进程也需先串行取得该锁 | `humming/jit/compiler.py:78-84` |
| F-046 | 编译失败抛 `RuntimeError` 并在消息中给出缓存目录路径（便于排查源码与编译日志） | `humming/jit/compiler.py:100-107` |
| F-047 | 算子出口 `humming.ops` 的 `__all__` 共 13 项：register_kernel、register_process_input_kernel、get_kernel_smem_size、launch_kernel、process_input、quant_weight、dequant_weight、repack_weight、pack_weight、unpack_weight、humming_gemm、process_mxfp4_w4a8_weight、tops_bench | `humming/ops/__init__.py:19-33` |
| F-048 | `register_kernel(cubin_path)` 通过 `torch.ops.humming.register_kernel` 向 C++ launcher 注册，返回 `(kernel_id, kernel_name)` | `humming/ops/launcher.py:6-8` |
| F-049 | `humming_gemm()` 全部参数为 keyword-only；核心入参含 `layer_config`（序列化字符串）、`inputs`、`weight`、`weight_scale`、`weight_scale_2`、`compute_config`、`tuning_config`、`input_scale`/`input_scale_2`、`zero_point`、`bias`，MoE 相关含 `sorted_ids`/`expert_ids`/`num_tokens_padded`/`expert_layout`/`locks` | `humming/ops/gemm.py:45-63` |
| F-050 | `process_input()` 负责输入侧处理：量化、激活融合、scatter；参数含 `quant_mode`/`quant_dtype`/`quant_group_size`、`group_scales`/`token_scales`、`activation_type`/`activation_impl`、`hadamard_block_size`、`layout`、`expert_tokens`/`scatter_idx` | `humming/ops/input.py:118-138` |

---

## 五、内核实现与流水线（F-051~F-062）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-051 | 三条 GEMM 流水线并存：**标准流水线** `humming.cuh`（同一 kernel 内所有线程兼具 producer/consumer 角色）、**warp specialization 流水线** `humming_ws.cuh`（独立 load 线程 + math 线程，用 `setmaxnreg` 分配寄存器预算）、**UMMA 流水线** `humming_umma.cuh`（SM100+ tcgen05 指令，累加器落在 TMEM） | `humming/include/humming/kernel/humming.cuh`、`humming_ws.cuh`、`humming_umma.cuh` |
| F-052 | CUDA 组件按职责分层：`arith/`（mainloop_arith、epilogue_arith、exp_offset）、`datatype/`（dtypes、dequant、dequant_fused、dequant_native、dequant_prepare、dequant_single、base_conversion）、`mma/`（all、mxmma、umma、wgmma、wmma）、`memory/`（g2s_loader、s2r_loader 及对应 pipeline）、`epilogue/`（gmem_writer、pipeline、smem_reducer、smem_writer）、`utils/ptx/`（barrier、legacy_load、math、shared、tcgen05、tma、warp、wgmma） | `humming/include/humming/` 目录树 |
| F-053 | 权重 repack 内核 `weight_repack_nk` 把任意位宽权重重排成 MMA 需要的 (n,k) 分块 packing | `humming/include/humming/kernel/process.cuh:130` |
| F-054 | packing 层级注释：4bit 为 `[1][4][1][2][2][8]`、8bit 为 `[2][2][2][2][2][4]`、16bit 为 `[4][1][4][2][2][2]`；以 16bit 激活为例，packing block 为 (n,k)=(64,16)，块内再按 16x16 → 8x8 → 2 元素/线程逐级切分 | `humming/include/humming/kernel/process.cuh:190-203` |
| F-055 | 反量化有三条路径：`dequant_native.cuh`（原生格式）、`dequant_fused.cuh`（融合进 GEMM 计算）、`dequant_single.cuh`（独立 kernel），另有 `dequant_prepare.cuh` 预处理 | `humming/include/humming/datatype/` |
| F-056 | 调优启发式按 SM 版本分派：`heuristics_map` 覆盖 75/80/86/87/89/90/100/103/110/120/121，另有 PPU 专用 `PPUSm80Heuristics`；实现分文件于 `tune/sm75.py`、`sm8x.py`（`Sm80Heuristics`/`Sm86Heuristics`/`Sm87Heuristics`/`Sm89Heuristics` 四个类同文件）、`sm90.py`、`sm90_h20.py`、`sm100.py`、`sm120.py`、`sm121.py`、`ppu_sm80.py`。**每个 SM 版本一个独立类**，新增硬件需新增/修改类 | `humming/tune/__init__.py:11-43` |
| F-057 | M 维候选集合：基础档 `1,2,4,8`，SM90 追加步长 8、其余追加步长 16；dense 上限 8192，MoE 上限 65536；超过 1024/2048/4096/16384 时分别要求按 16/32/64/128 对齐 | `humming/tune/base.py:546-560` |
| F-058 | 计算/访存瓶颈判定：`_estimate_compute_bound_threshold` 依据设备 Tensor Core 峰值（`tensorcore_tops`）与显存带宽（`memory_bandwidth_gbps`）估算阈值；SM75/86/89 且为浮点 dtype 并启用 f16 累加时峰值翻倍 | `humming/tune/base.py:15-32` |
| F-059 | 设备启发式基类 `DeviceHeuristics` 携带 `max_smem_size`、按位宽分档的 `b16/b8/b4_allowed_dtypes`、以及 `expert_probability_cv`（MoE 专家负载波动指标） | `humming/tune/base.py:35-41` |
| F-060 | MoE 栅格化调度：`tune/raster.py` 提供 `raster_group_m_for_config` / `get_moe_raster_group_m`，配合 `TuningConfig.raster_group_m` | `humming/tune/raster.py`；`humming/config/config.py:558` |
| F-061 | 进程输入（process_input）内核分五个职责文件：`activation.cuh`、`context.cuh`、`hadamard.cuh`、`quantization.cuh`、`thread_task.cuh` | `humming/include/humming/kernel/process_input/` |
| F-062 | 源码树中的配套工具：`humming/testing/`（benchmark、data、device、process_input、runner、tuning）、`humming/utils/`（cubin、cuda、device、jit、math、nvrtc、smem、weight 等） | `humming/testing/`、`humming/utils/` 目录清单 |

---

## 六、Python API 与生命周期（F-063~F-070）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-063 | `HummingLayer` 是 `torch.nn.Module` 子类的 dataclass，字段：`shape_n`、`shape_k`、`weight_config`、`input_config`、`pad_n_to_multiple`（默认 1）、`pad_k_to_multiple`（默认 1）、`num_experts`、`has_bias`、`torch_dtype` | `humming/layer.py:312-322` |
| F-064 | `torch_dtype` 缺省推断：取 `torch.get_default_dtype()`；若不在 `[float16, bfloat16]` 内，则 SM≥80 选 bfloat16、否则选 float16 | `humming/layer.py:330-334` |
| F-065 | 生命周期三步：`load_from_unquantized()` 装载未量化权重并现场量化 → `transform()` 转成 humming 格式并准备内核 → `__call__` 执行量化 GEMM | README.md:75-81；`humming/layer.py:574` |
| F-066 | `load_from_unquantized()` 断言：输入 dtype 属 `[float16, bfloat16, float32]`；形状等于 `(shape_n, shape_k)`（MoE 时为 `(num_experts, shape_n, shape_k)`） | `humming/layer.py:405-411` |
| F-067 | `transform()` 负责把 weight/input schema 统一到 humming 标准格式；`forward` 首行断言 `self.humming_config is not None`，即**必须先 transform 才能 forward** | `humming/layer.py:574-586,682` |
| F-068 | `transform()` 内部会先执行 `prepare_fp16_e8m0_scale` 处理 FP16 权重配 E8M0 scale 的组合 | `humming/layer.py:184` |
| F-069 | README 的最小可用示例：构造 `HummingLayer(shape_n=8192, shape_k=8192, weight_config={"dtype": "int6"}, torch_dtype=torch.float16)` → `load_from_unquantized` → `transform` → `layer(inputs)`，并与 `inputs.matmul(weight.T)` 对拍 | README.md:61-87 |
| F-070 | `weight_config` 支持 `int6` 这类非 8 的倍数量化位宽——README 示例即以 int6 演示 | README.md:68；`humming/schema/humming.py` 整数类型枚举 |

---

## 七、vLLM 集成（F-071~F-078）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-071 | vLLM CUDA 依赖清单中固定 `humming-kernels[cu13]==0.1.17`（注释「Humming kernels for quantization gemm」） | vLLM `requirements/cuda.txt:32-33` |
| F-072 | **依赖引入历史**：2026-05-19 由 PR #42540 引入 → 2026-05-23 由 PR #43492 revert → 2026-05-26 由 PR #43530 恢复；自 **v0.22.0 起**各正式版本 `requirements/cuda.txt` 均含该行（版本钉随发布滚动：v0.22.0→0.1.2、v0.24.0→0.1.6、v0.26.0→0.1.10、v0.29.0→0.1.12、v0.32.0→0.1.17） | vLLM git log -S "humming-kernels" -- requirements/cuda.txt；各 tag 文件内容 |
| F-073 | **博客口径与源码口径不一致**：博客称「从 vLLM 0.29.0 起 CUDA 安装默认包含 Humming 依赖」，但源码显示该依赖自 v0.22.0（2026-05-29）即已存在；v0.29.0（2026-09-08）只是当时的版本钉为 0.1.12。差异见 [verification.md](verification.md) 差异 #1 | 官方博客「Using Humming in vLLM」节 vs vLLM git 历史 |
| F-074 | vLLM 侧 `MoEBackend` 与 `LinearBackend` 两个 Literal 枚举均含 `"humming"` 取值；文档串释义为「Use Humming Mixed Precision kernels」 | vLLM `vllm/config/kernel.py:137,255,326` |
| F-075 | vLLM 侧存在独立量化方法注册项 `"humming"` → `HummingConfig`；该类实现 `get_min_capability() → 75`、`get_supported_act_dtypes() → [bfloat16, half]` | vLLM `vllm/model_executor/layers/quantization/__init__.py:29,179`；`quantization/humming.py:152-165` |
| F-076 | vLLM 侧 humming 集成代码分布在五处：`quantization/humming.py`（`HummingConfig` / `HummingLinearMethod` / `HummingMoEMethod`）、`quantization/utils/humming/`（`activation.py`/`linear.py`/`moe.py`/`priority.py`/`schema.py`）、`fused_moe/experts/fused_humming_moe.py`、`utils/humming.py`、以及 `model_executor/kernels/linear/*/humming.py`（`mixed_precision`/`mxfp4`/`mxfp6`/`mxfp8`/`nvfp4`/`scaled_mm` 六个——`--linear-backend humming` 的实际落点） | vLLM 全仓 grep `import humming`；`vllm/model_executor/kernels/linear/` |
| F-077 | `--quantization humming` 是**兼容路径**：用于「Humming 支持、但 vLLM 不再原生支持或尚未原生支持」的格式（官方举例 GPTQ INT3）；对 gpt-oss + mxfp4 组合，vLLM 会显式报错并引导改用 `--moe-backend humming` | 官方博客「Using Humming in vLLM」节；vLLM `quantization/humming.py:174-188` |
| F-078 | vLLM 侧已实现「Humming kernel 选择优先级」与「MoE 激活表达式」两套专用逻辑：`utils/humming/priority.py` 提供 `prefers_humming()` / `prioritize_humming()`——**自动优先仅在 compute capability == 90 时生效**（`_HUMMING_PREFERRED_CAPABILITIES = frozenset({90})`）；`utils/humming/activation.py` 把 12 种 MoE 激活（SILU / GELU / GELU_TANH / RELU2 / SWIGLUOAI / SITU / SWIGLUOAI_UNINTERLEAVE / SWIGLUSTEP，以及 SILU_NO_MUL / GELU_NO_MUL / GELU_TANH_NO_MUL / RELU2_NO_MUL）翻译为 humming 可执行表达式 | vLLM `utils/humming/priority.py:11,14-23,26-48`；`utils/humming/activation.py:28-87` |

---

## 八、官方博客性能与路线图（F-079~F-090）

> ⚠️ 本节全部数字均来自官方博客的**特定测试条件**，不代表通用结论。

| 编号 | 事实 | 来源 |
|------|------|------|
| F-079 | 基准方法：由 vLLM community 运行；M 覆盖 1 到 8192 的**每一个 2 的幂**；充分 warmup；逐 kernel 计时；使用 **cold L2 cache**；样本间短暂 pause；MoE speedup 定义为「Gateup GEMM 延迟 + Down GEMM 延迟」之和 | 官方博客「Results / Benchmark 方法」节 |
| F-080 | 编译耗时对比（单次 W4A16 kernel 编译，环境：H200 server + CUDA 13.4 + **关闭编译缓存**）：CUTLASS+NVCC **23.35 秒**；Humming+NVCC **1.82 秒**；Humming+NVRTC **1.88 秒** | 官方博客「Lightweight design」节 |
| F-081 | 编译并加载覆盖单层 GEMM 全部受支持 M size 的内核，**约 2–4 秒**；Humming 可在模型 warmup 期间并行编译内核 | 官方博客「Lightweight design」节 |
| F-082 | Dense W4A16：多数配置与 vLLM Marlin 持平或更快；**小 batch 多个设备约 3–4×**；大 batch 下 H200 约 **2× Marlin**，部分 B300 场景超 **3× Marlin** | 官方博客「WnA16」节 |
| F-083 | MoE W4A16：H20/H200 上 MXFP4 多个中大 batch 约 **2× Marlin**；B300 上 MXINT4/NVFP4 的 grouped 路径约 **5×**；SM120/SM121 上一系列 workload 优于 Marlin 与对应 FlashInfer 实现 | 官方博客「MoE W4A16」节 |
| F-084 | Hopper W8A8（对标 DeepGEMM Contiguous）：小 batch 约 **2.6×**、中 batch 约 **2.5×** | 官方博客「Hopper W8A8」节 |
| F-085 | Hopper W4A8（对标 DeepGEMM W8A8）：H20 约 **4.2×**、H200 约 **4.5×** | 官方博客「Hopper W4A8」节 |
| F-086 | Blackwell B300（对标同精度 DeepGEMM Contiguous）：W8A8 约 **1.25×**、W4A8 约 **1.6×**、W4A4 约 **1.4×** | 官方博客「Blackwell B300」节 |
| F-087 | SM120/SM121（对标 FlashInfer CUTLASS）：多数测试点更优；SM121 小 batch W4A8 约 **+19%**、W4A4 约 **+9%** | 官方博客「SM120 / SM121」节 |
| F-088 | SM120 上最低位配置超过 BF16 cuBLAS 的 **5×**；大 batch 下 H20 上多个位宽维持接近 BF16 cuBLAS 的计算效率 | 官方博客「Other WnA16 formats」节 |
| F-089 | 端到端实测：模型 **DeepSeek-V4.1-Flash**，硬件 **8×H20，TP=8**；保持模型原有 MXFP4 权重不变，把 MoE 执行从 **vLLM Marlin W4A16（BF16 激活）** 切到 **Humming W4A8（tokenwise FP8 激活）**；吞吐提升 **14%–43%**，TTFT 降低 **25%–32%**；并发 64 时输出吞吐 **442.37 → 633.94 tokens/s**，TPOT 约降 **31%** | 官方博客「End-to-end」节及其结果表 |
| F-090 | 路线图：① 扩大设备支持（Rubin 特性含 Locality Domains、更多 T-Head PPU 如 Zhenwu M890、更多 CUDA 兼容设备）；② **引入 autotune**（当前靠针对性调优，尚未有自动搜索，预期与现有启发式互补）；③ 深化与推理框架的集成（量化模型加载、后端选择、并行推理、运行时调度、设备适配），目标之一是让 EP 下的量化 All-to-All 通信可用 | 官方博客「Future Plans」节 |

---

## 九、社区视角与作者自述（F-091~F-094）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-091 | 作者在知乎自述项目的起点：2025 年主要在做 vLLM 仓库 Marlin 算子的开发与优化，为 Marlin 增加 MoE 支持与更多量化类型（FP8、MXFP4、NVFP4）及更多激活类型（FP8、INT8）；判断「开源量化算子支持不完善」——通用 Marlin 只支持 4 位或 8 位，其他位数难加；且不少算子性能不佳（Marlin 在大 batch 下表现差，从 Hopper 起必须用架构专属指令才能发挥硬件性能） | 作者知乎自述「通用高性能量化推理算子库Humming」节 |
| F-092 | 作者自述 vLLM 集成 PR 编号为 **#34556**（已合并），并给出早期仓库地址 `github.com/inclusionAI/humming`（后迁至 `vllm-project/humming`） | 作者知乎自述 |
| F-093 | 作者自述的支持范围（写作时点，早于本包源码快照）：激活类型 FP16/BF16/FP8/INT8/INT4，权重 1–8 位全部整数与浮点类型，量化方法 groupwise/blockwise/channelwise/tensorwise，scale 类型 FP16/BF16/E4M3/E5M2/E8M0；当时「已支持 SM75–SM90 高级特性，SM100/SM120 特性未来支持」 | 作者知乎自述 |
| F-094 | 作者自述编译与体积：单个算子编译时间约 1–2 秒（与算子复杂度相关、与 CPU 性能强相关）；无复杂依赖，仅需 torch 和 nvcc；打包后 wheel 仅 100+KB | 作者知乎自述 |

---

## 十、测试与基准设施（F-095~F-098）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-095 | 基准脚本：`benchmarks/bench_humming.py`（Humming 自身）、`bench_marlin.py`、`bench_cutlass_w8a8.py`、`bench_torch.py`、`bench_triton_moe.py`（五套可横向对比的 harness） | `benchmarks/` 目录清单 |
| F-096 | 已归档基准结果按设备分目录：`4090/`、`a800/`、`h20/`、`h200/`；用例目录名编码 shape 与分组参数，如 `dense_n8192_k8192_g0`、`dense_n8192_k8192_g0_f16accum`、`moe_e256_k8_n512_k7168_g128x128` | `benchmarks/results/` 目录树 |
| F-097 | 结果文件名规则：`{实现}_w{权重位宽}a{激活位宽}_{权重类型}_{激活类型}.json`，同一目录下并存 `humming_*`、`marlin_*`、`cutlass_*`、`torch_*` 四类实现，便于直接对拍 | `benchmarks/results/h200/dense_n8192_k8192_g0/` 文件名清单 |
| F-098 | 测试布局：`tests/kernels/humming/`（9 个 kernel 级测试文件：accumulation / block_scaled / datatype / moe / mxfp4 / scale / shape / special_paths / zero_point）、`tests/kernels/process_input/`（3 个：layout / matrix / scale）、`tests/native/`（仅 `device_info_mock.cpp` 一个 C++ mock）；另有 5 个 Python 级测试位于 `tests/` 根目录（`test_jit_infrastructure.py`、`test_sm8x_heuristics.py`、`test_sm90_heuristics.py`、`test_sm90_h20_heuristics.py`、`test_tuning_candidates.py`） | `tests/` 目录树 |

## 十一、V 门对抗审查新增事实（F-099~F-106）

> 本节为 V 门对抗审查后补充的事实，均已回到源码逐条复核。

| 编号 | 事实 | 来源 |
|------|------|------|
| F-099 | UMMA 支持判定：`LayerConfig.is_umma_supported` 要求 `sm_version // 10 in (10, 11)`——即 **SM100/101/110/111 可用；SM120/121（`//10 == 12`）不支持 UMMA** | `humming/config/config.py:91-95` |
| F-100 | SM120/121 的主用 MMA 为 **MXMMA**（块缩放 MMA），但**有前提**：`get_default_mma_type()` 要求 `use_block_scaled_mma and sm_version // 10 == 12`；`use_block_scaled_mma` 依赖 `mxmma_supported`（MX 系浮点激活 + scale 粒度匹配）。**条件不满足时回落标准 `MMA`** | `humming/config/mma.py:97-105`；`humming/config/config.py:175-184,223-259` |
| F-101 | `locks` 参数是 **stream-k 累加锁**（非专家级锁）：容量**至少**为 `max_stream_k_tiles * num_stream_k_locks_per_tile`（源码断言 `numel() >= required_locks`），仅在 `use_stream_k` 开启时必需；batch-invariant 模式强制 `use_stream_k=False`，此时不需要 locks。vLLM 侧 `create_humming_locks` 按 `num_compute_units * 8` 分配，与 Humming 侧的公式是**两套口径** | `humming/csrc/launcher/tensor.h:255-263`；`humming/include/humming/kernel/humming.cuh:109`；`humming/tune/base.py:334-338`；vLLM `vllm/utils/humming.py:100-109` |
| F-102 | 官方博客明确：B300（SM103）的 **UMMA 指令不再支持 INT8 计算**，但更早的 MMA 指令仍可执行 INT8 GEMM，性能显著降低 | 官方博客「Broad Device Support」节 |
| F-103 | 官方博客明确：**Rubin 不支持 float4e0m3 / float8e3m4 这两种隐藏 Tensor Core 格式**，相关原生计算路径不延伸到 Rubin | 官方博客「Quantization Support」节 |
| F-104 | 官方博客明确：Humming **已完整支持 T-Head 玄武 810E**（CUDA 兼容设备） | 官方博客首段与「Broad Device Support」节 |
| F-105 | 激活类型选择：默认使用 checkpoint 指定的激活类型，设备不支持时**自动回退到更高精度**（无原生 MXFP4 的设备可自动走 FP8 / BF16 / FP16 路径）；用户可通过 vLLM 显式覆盖：`--quantization-config.moe.activation mxfp8` | 官方博客「Selecting Activation Types」节 |
| F-106 | vLLM 侧存在激活类型过时判定：`utils/humming/schema.py` 的 `is_deprecated(a_dtype)` 对 int4@sm≥90、int8@103≤sm<110、以及**任意 <16bit 激活**@100≤sm<120 判为过时。**告警与回退是互斥分支**：`allow_fallback=False` 时打印「Humming {a_dtype} activation is slow on SM{sm_version} now.」但**保留原激活不回退**；`allow_fallback=True` 时静默回退到更高精度激活、**不打印该告警** | vLLM `utils/humming/schema.py:325-334,337-341,361-394` |

---

