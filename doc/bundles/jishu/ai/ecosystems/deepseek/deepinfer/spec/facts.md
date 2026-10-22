---
type: spec
title: "DeepInfer 源码事实清单（R-Phase）"
---

# DeepInfer 源码事实清单（R-Phase）

> 源码路径：SpecWeave 工作树内镜像 `external/libs/ai/deepseek-ai/DeepInfer`（上游 https://github.com/deepseek-ai/DeepInfer ）
> 收集日期：2026-10-22
> 引擎版本：`0.1.0`（`deepinfer/__init__.py`），Apache-2.0，源自 vLLM 改造

---

## F-001：版本与模型支持

- 文件：README.md、deepinfer/__init__.py
- 版本 `0.1.0`；唯一支持模型 DeepSeek-V4.1-Flash，默认 checkpoint `deepseek-ai/DeepSeek-V4.1-Flash-1017`
- 硬件：NVIDIA SM100（CUDA 13）与 Huawei Ascend 950（CANN 9.2）；前置 Linux、GCC≥13、Python 3.12
- 构建入口 `build.sh`：`export DEEPINFER_ACCELERATOR=nvidia|ascend` → `pip install -r requirements-<平台>.txt` → nvidia 强制 NCCL 2.32.3 → `scripts/build_vendor.sh` → 主扩展产物符号链接入 `deepinfer/_so/<accelerator>-<arch>/`

## F-002：引擎核心在 C++

- 文件：deepinfer/engine/llm_engine.py（1029 行）、csrc/engine/scheduler.hpp、pybind_scheduler.cpp
- `LLMEngine` 直接 `from deepinfer._C.engine import Scheduler, BlockManager, RequestOutputPool, ...`（llm_engine.py:19-31）
- 调度器接口契约见 `deepinfer/_C/engine.pyi`（735 行；schedule/process_outputs/update_mtp_runtime 等，返回值多为零拷贝借用缓冲）
- `_C/` 只含 4 个 .pyi 存根；真实 .so 构建后按平台放入 `deepinfer/_so/<accelerator>-<arch>/`，同代码树双平台可共存（__init__.py:9-32）

## F-003：ZOS 零开销调度

- 文件：csrc/engine/zos.cpp/zos.hpp、deepinfer/engine/arg_utils.py:51-55、deepinfer/engine/engine_type.py:16-17
- 开关 `DEEPINFER_ZERO_OVERHEAD_SCHEDULING` 由 arg_utils 按引擎类型 `os.environ.setdefault` 注入——NORMAL/COMPLETION 默认 "1"
- 生效路径：model_metadata_utils.py:143 选 `prepare_decode_v4_zos` → worker/worker.py:183 → config.py:14（`scheduler_overhead = nextn + (nextn + 1)` token 预算）
- 流水线：GPU 执行 forward(N)→sample(N) 时，CPU 同步执行 schedule(N+1)→launch_forward(N+1)→post-process(N-1)→launch_sample(N+1)

## F-004：并行与 EPLB

- 文件：deepinfer/model_executor/parallel_utils/（parallel_state.py、cp.py、communication_op.py、userbuffer.py、nccl_memory.py）、deepinfer/model_executor/eplb/（policy.py、shuffle.py）
- eplb/__init__.py:42 设置 `TORCH_SYMMEM_ALLOW_OVERLAPPING_DEVICES=1` 支持对称内存 shuffle
- doc/inference_deployment_qa.md:45-53 生产并行：prefill EP2–8/DP2–8、decode Wide-EP EP64–128、attention DP=EP、TP/CP 生产暂不使用
- 冗余专家下界 `DEEPINFER_OVERRIDE_NUM_EXTRA_EXPERTS`（实践默认 32），向上取整到 ep_size 整除（examples/README.md:63）；统计间隔 `DEEPINFER_MOE_LB_STAT_INTERVAL` 默认 128

## F-005：DSpark 推测解码

- 文件：deepinfer/model_executor/models/mtp/dflash.py（392 行，mtp/ 下唯一实现）、v4_modules/heads.py（DFlashNextPredictHeadHC）、v4_modules/hc.py、layers/tilelang_ops/dflash.py（confidence_head_fused）、csrc/engine/mtp_varlen.hpp、layers/mtp_info_pool.py
- ConfidenceHead（dflash.py:46-60）输入 `n_embed + markov_rank`、输出 1 维接受概率
- 变长验证：`DEEPINFER_ENABLE_MTP_VARLEN`；draft 长度 `DEEPINFER_USE_NEXTN_DECODE`（默认 5，0 关闭）
- 与 ZOS 配合：CPU 只定总预算，逐请求长度由 GPU 上 TileLang kernel 重算（累乘、全局排序 top-k、融合 remap scatter），回写 pinned buffer
- 验证结果经 RequestOutput.confidence_score/draft_tok/accept_tok 暴露（_C/engine.pyi:185-232）

## F-006：结构化输出

- 文件：deepinfer/structure_output/{compiler.py, matcher.py, mask.py, so_matcher_builder.py}
- compiler.py:54-63 dispatch 三种 schema_type：json（strict）/regex/ebnf；默认 10 GiB 编译缓存上限（防 CVE-2025-32381）
- matcher.py:20 `MAX_ROLLBACK_TOKENS = DEEPINFER_USE_NEXTN_DECODE + 2`
- mask 经 `tilelang_ops/structure_output.apply_token_bitmask_by_step_inplace` 就地施加
- so_matcher_builder 默认 4 线程（`DEEPINFER_SO_BUILDER_CPUS`）+ CPU 亲和性
- 用法（examples/_structured_output.py:23-36）：`SamplingParams(so_args={"schema_type": ..., "schema": ...})`；JSON schema 必须 json.dumps 序列化为字符串

## F-007：Vision Encoder

- 文件：deepinfer/ve/（multimodal_processor.py、processor/、prepare_tensor_input_vl.py、schema.py）、model_executor/models/vision_encoder/（vit.py、mlp_projector.py、vl_aligner.py）、deepseek_vl.py
- MultimodalProcessor 以独立 worker 进程异步做图像预处理，不在 step 关键路径（examples/README.md:120）
- 多模态共享内存池 `SharedTorchMemoryPool`：`DEEPINFER_MULTIMODAL_POOL_SIZE_GB` 默认 8

## F-008：deep_cluster 独立硬件库

- 文件：deep_cluster/hardware/（nvidia.py/ascend.py/cpu.py，14 个硬件中立函数）、deep_cluster/topology/bind.py
- 刻意不依赖 torch，供 import torch 前的平台探测；setup.py:12 构建期与 deepinfer/__init__.py:18 运行期共用

## F-009：vendor 与依赖

- .gitmodules 6 个 submodule 全部 github.com/deepseek-ai/*：DeepSelect、FlashMLA、DeepEP、DeepGEMM + DeepEP-Ascend、DeepGEMM-Ascend
- scripts/build_vendor.sh:7-22：按平台构建对应 4 个算子轮子并 `pip install --no-deps`
- TileLang/TileKernels 不是 submodule：requirements.txt `tilelang==0.1.15`、`tile-kernels==2.1.0`；自研 TileLang 核在 `deepinfer/model_executor/layers/tilelang_ops/`

## F-010：构建细节

- pyproject.toml：setuptools.build_meta，requires ninja + setuptools>=77.0.3 + torch>=2.7，requires-python >= 3.12
- setup.py：`IS_NPU = accelerator_kind() == "ascend"` 二选一——NPU 走 torch_npu NpuExtension（asc_utils.cpp、-DWITH_NPU）；CUDA 走 CUDAExtension（cuda_utils.cpp，要求 CONDA_PREFIX/VIRTUAL_ENV）；编译统一 -O2 -std=c++20 CXX11 ABI（setup.py:17-21）
- 平台 torch：nvidia `torch==2.13.0+cu132` + `flash-attn-4==4.0.0b34`；ascend `torch==2.13.0+cpu` + `torch-npu==2.13.0rc1`

## F-011：评测

- 文件：eval/README.md（221 行）
- AIME 2026（30 题×32 样本）、HLE（2500 题含 342 图像题）、GPQA Diamond（198 题×8 样本），指标 Pass@1；参考值 AIME 99.9%、GPQA 93.4%、HLE-Full 42.6%
- 生成/评分两阶段分离；评分默认 LLM judge（EVAL_JUDGE_BASE_URL/KEY/MODEL），rule 模式全确定；数据集 JSONL 自备（DATA_FILE）

## F-012：部署 Q&A 文档

- 文件：doc/inference_deployment_qa.md（312 行）
- 记录：EPD 分离架构、KV cache 72h+ 保留、单集群日服务 155T tokens、$38/GPU-hour 收入（谷价）、配套开源 deepseek-recipe 编解码组件

## F-013：示例体系

- 文件：examples/（README.md、offline_inference.py、benchmark.py、_structured_output.py、_config.py、_launch.py、_prompts.py、sweep/、yoco/）
- offline_inference 输出格式被 tests/models/test_offline_inference.py 正则解析，不可改动
- PPL 基线 `tests/models/offline_decode_ppl.json` 按平台/负载索引、逐样本精确比对；多机刷新/验证按节点拆分 + 跨节点文件锁（.lock）
- benchmark 三指标：prefill throughput（跳 5 warmup chunk 取 10 稳态区间）、decode avg_SPS（跳 50 warmup + 60 logged 步取 60 区间，剔除 MoE LB flush 撞击区间）、decode throughput = avg_SPS × decode_num_requests × (1+nextn) / cp（全接受口径）
