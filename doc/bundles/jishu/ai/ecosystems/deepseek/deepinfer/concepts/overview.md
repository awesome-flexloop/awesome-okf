---
type: concept
scope: deepinfer
name: DeepInfer 概述
version: "0.1.0"
source: README.md, examples/README.md, deepinfer/__init__.py
description: DeepInfer 推理框架整体定位、支持矩阵、目录结构与快速开始
sources:
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践
---

# DeepInfer 概述

DeepInfer 是 DeepSeek 内部大规模云服务推理框架的开源版本，提供离线推理能力与大规模服务所需的核心特性。它在 2026-10-20 与 [deepseek-recipe](../../deepseek-recipe/index.md) 编解码组件同步开源，二者共同构成 DeepSeek 公开的生产推理栈。

---

## 一、定位与设计目标

DeepSeek 官方技术报告给出 V4.1 Flash 推理系统的三个设计目标，DeepInfer 正是围绕这些目标组织的：

1. **兼容多种厂商计算芯片**——同一代码树支持 NVIDIA（`DEEPINFER_ACCELERATOR=nvidia`）与华为昇腾（`ascend`），构建期经 `deep_cluster.hardware.accelerator_kind()` 探测后二选一编译。
2. **基于常见硬件组织 Prefill 和 Decode**——用常见 8 卡机器做 Prefill（EP2～8/DP2～8），用 64～128 卡超节点做 Decode（Wide-EP EP64～128），围绕两阶段负载特征设计计算、通信与调度。
3. **支持 KVCache 保留 72 小时以上**——为上下文复用提供更长的时间窗口（生产由 3FS 集群承载，agent 流量 TTL 3 天、chatbot 7 天）。

优化目标一句话：**更大的吞吐，更低的延迟**——在满足延迟要求的前提下提高系统有效吞吐，用更少的算力与能源支撑更多请求。

---

## 二、支持矩阵

| 维度 | 支持项 |
|---|---|
| 模型 | DeepSeek-V4.1-Flash（默认 `deepseek-ai/DeepSeek-V4.1-Flash-1017`） |
| NVIDIA | SM100 GPU；CUDA 13；`torch==2.13.0+cu132` + `flash-attn-4==4.0.0b34` |
| 昇腾 | Ascend 950 NPU；CANN 9.2；`torch==2.13.0+cpu` + `torch-npu==2.13.0rc1` |
| 系统 | Linux、GCC ≥ 13、Python 3.12 |
| 许可证 | Apache License 2.0 |

---

## 三、目录结构

```
DeepInfer/
├── deepinfer/              # 核心 Python 包
│   ├── engine/             # LLMEngine、EngineArgs、三形态引擎（NORMAL/PROMPT/COMPLETION）
│   ├── model_executor/     # layers/（含 tilelang_ops/）、models/（deepseek.py、deepseek_vl.py、mtp/、v4_modules/）、eplb/、parallel_utils/
│   ├── worker/             # worker、model_runner、cache_engine、cuda_graph_runner、dflash_cuda_graph_runner
│   ├── structure_output/   # xgrammar 编译器、matcher、bitmask 掩码
│   ├── ve/                 # Vision Encoder 多模态处理（独立 worker 进程）
│   ├── entrypoints/        # llm.py 离线入口
│   ├── npu_ops/            # 昇腾侧算子适配（deep_select、vit_attn）
│   ├── _C/                 # C++ 扩展 .pyi 存根（真实 .so 构建后入 _so/<accelerator>-<arch>/）
│   └── environ.py          # DEEPINFER_* 环境变量集中定义
├── deep_cluster/           # 独立硬件发现/拓扑库（不依赖 torch，供构建期与运行期共用）
├── csrc/                   # C++ 扩展源码（engine/ 调度器、zos、mtp_varlen、input_metadata 等）
├── vendor/                 # 6 个 DeepSeek 自家 submodule（DeepSelect/FlashMLA/DeepEP/DeepGEMM + 昇腾版）
├── examples/               # offline_inference、benchmark、sweep、structured_output 示例
├── eval/                   # AIME 2026 / HLE / GPQA Diamond 离线评测
└── doc/                    # 部署 Q&A（inference_deployment_qa.md）与性能图
```

---

## 四、构建与快速开始

### 4.1 构建三步

```bash
# 1. 创建并激活空 Python 3.12 环境
# 2. 导出平台变量（保持导出）
export DEEPINFER_ACCELERATOR=nvidia    # 或 ascend
# 3. 一键构建
./build.sh
```

构建要点（源自 `setup.py` 与 `scripts/build_vendor.sh`）：

- **平台二选一**：NPU 走 `torch_npu NpuExtension`（编入 `asc_utils.cpp`、`-DWITH_NPU`）；CUDA 走 `CUDAExtension`（编入 `cuda_utils.cpp`，要求存在 CONDA_PREFIX/VIRTUAL_ENV）。
- **vendor 算子**：nvidia 构建 DeepSelect/FlashMLA/DeepEP/DeepGEMM；ascend 构建对应昇腾版；各子模块 `python setup.py bdist_wheel` 后 `pip install --no-deps` 安装。
- **TileKernels 与 TileLang 不是 submodule**，是 PyPI 依赖（`tilelang==0.1.15`、`tile-kernels==2.1.0`）；自研 TileLang 核在树内 `deepinfer/model_executor/layers/tilelang_ops/`。
- **产物符号链接**：主扩展 `.so` 放入 `deepinfer/_so/<accelerator>-<arch>/`，同一代码树 nvidia/ascend 可共存。

### 4.2 离线推理

```bash
python examples/offline_inference.py --ep 8            # 单机 8 卡
python examples/offline_inference.py --ep 2 --dp 8     # DP8 组
python examples/offline_inference.py --ep 2 --cp 8     # CP8
```

默认模型 `deepseek-ai/DeepSeek-V4.1-Flash-1017`：`--model_name` 为模型 ID 时经 `huggingface_hub.snapshot_download` 下载至本地 HF 缓存；为本地 HF 目录（config.json + safetensors）时直接使用、零网络访问。`DEEPINFER_HF_MODEL_DIR` 把默认模型指向本地副本，但不覆盖显式传入的 `--model_name`。

### 4.3 关键运行开关速查

| 需求 | 配置 |
|---|---|
| 开启 DSpark 变长验证 | `DEEPINFER_ENABLE_MTP_VARLEN=1`（draft 长度由 `DEEPINFER_USE_NEXTN_DECODE` 控制，默认 5，设 0 关闭） |
| Decoder SWA 有界回放 | `DEEPINFER_YOCO_PREFILL_TRUNCATION_MODE=compact` + `DEEPINFER_YOCO_PREFILL_KEEP_TOKENS=140`（V4.1 默认值；保留后缀须 ≥ 窗口 + 回退长度） |
| Batch 不变推理 | `DEEPINFER_BATCH_INVARIANT=1`（NVIDIA only） |
| 确定性采样 | `DEEPINFER_BATCH_INVARIANT=1` + `DEEPINFER_ENABLE_MTP_VARLEN=0` + `SamplingParams` 固定 `seq_seed` |
| 结构化输出 | `SamplingParams(so_args={"schema_type": ..., "schema": ...})`，见[结构化输出](structured-output.md) |

---

## 五、评测体系

`eval/README.md` 提供离线批量评测（Pass@1）：

| 基准 | 规模 | 参考值 |
|---|---|---|
| AIME 2026 | 30 题 × 32 样本 | 99.9% |
| GPQA Diamond | 198 题 × 8 样本 | 93.4% |
| HLE | 2500 题（含 342 图像题） | 42.6%（Full） |

生成与评分两阶段分离（可重复计分）；评分默认走 LLM judge（`EVAL_JUDGE_BASE_URL/KEY/MODEL`），rule 模式全确定；数据集 JSONL 需自备（`DATA_FILE` 指路）。

---

## 六、与生态的关系

- **算子层**：FlashMLA（MLA 注意力）、DeepGEMM（GEMM/MoE）、DeepEP（MoE all-to-all 通信）、DeepSelect、TileKernels（TileLang DSL）——全部 DeepSeek 自家仓库，随 vendor submodule 或 PyPI 引入。
- **协议层**：[deepseek-recipe](../../deepseek-recipe/index.md) 负责 API 协议 ↔ token 序列编解码，生产部署中位于引擎前后两端。
- **基座**：vLLM（主基座）+ SGLang / TensorRT-LLM（设计灵感），DeepInfer 在其上替换调度器为 C++ 实现、加入 DSpark/EPLB/SWA Replay 等自研机制。
