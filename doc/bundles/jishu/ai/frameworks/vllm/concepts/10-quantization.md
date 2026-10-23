---
type: Concept
title: "量化：方法矩阵、硬件兼容与插件机制"
description: "vLLM 量化全景——FP8/MXFP4/NVFP4/INT8/INT4/GPTQ/AWQ/GGUF/bitsandbytes 等方法矩阵与 GPU 架构兼容表、--quantization 与外挂权重路径、量化 KV cache、MoE 专家量化（moe_wna16/experts_int8）、out-of-tree 量化插件与注册 API"
tags: [vllm, quantization, fp8, int4, gptq, awq, gguf, moe-quantization, quantized-kv-cache, quantization-plugin]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-quant
    resource: /references/source-map.md
    title: vllm/model_executor/layers/quantization/（本地检出）
  - id: website-quant
    url: https://docs.vllm.ai/en/latest/features/quantization/
    title: Quantization（官网文档）
---

# 量化：方法矩阵、硬件兼容与插件机制

量化是 vLLM 显存效率的第二根支柱（第一根是 [05 KV 缓存](05-kv-cache.md) 的 PagedAttention）。vLLM 本身不做训练侧量化——它消费外部工具（llm-compressor、AutoAWQ、GPTQModel、NVIDIA Model Optimizer、AMD Quark、TorchAO、Intel INC 等）产出的量化权重，运行时提供对应 kernel（F-096）。

## 方法与硬件兼容矩阵

官方兼容表（docs/features/quantization，2026-10 时点；✅=支持）：

| 实现 | Volta | Turing | Ampere | Ada | Hopper | AMD GPU | Intel GPU | x86 CPU | Arm CPU |
|------|-------|--------|--------|-----|--------|---------|-----------|---------|---------|
| AWQ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| GPTQ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| Marlin（GPTQ/AWQ/FP8/FP4） | ❌ | ✅* | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| llm-compressor INT8 (W8A8) | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| llm-compressor INT8 (W4A8) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| llm-compressor FP8 (W8A8) | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| bitsandbytes | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| DeepSpeedFP | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| GGUF | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

架构缩写：Volta=SM 7.0、Turing=7.5、Ampere=8.0/8.6、Ada=8.9、Hopper=9.0；*Turing 不支持 Marlin MXFP4（F-097）。要点：

- **FP8 W8A8** 是 Ada/Hopper/AMD 的甜点——官方 quickstart 的 FP8 案例即在 Hopper 上跑（F-098）。
- **INT4（W4A16）** 家族（GPTQ/AWQ）跨代兼容最广，适合显存紧张的 Ampere 卡（F-099）。
- **GGUF** 保持 llama.cpp 生态兼容，Volta 起全系 NVIDIA 可用（F-100）。

## 源码侧实现清单

`vllm/model_executor/layers/quantization/` 下的实现（本地检出）：

| 模块 | 方法 |
|------|------|
| `fp8.py` / `fbgemm_fp8.py` | FP8 W8A8、FP8 E4M3/E5M2 |
| `mxfp4.py` / `modelopt.py` / `modelopt_block_quant.py` | MXFP4/MXFP8、NVFP4（NVIDIA Model Optimizer 系） |
| `auto_awq.py` / `awq_triton.py` | AWQ（Marlin/Triton 后端） |
| `auto_gptq.py` | GPTQ（Marlin 后端） |
| `compressed_tensors/` | llm-compressor 统一格式 |
| `moe_wna16.py` / `experts_int8.py` | MoE 专家专用：WNA16 与 INT8 专家量化 |
| `kv_cache.py` | 量化 KV cache（与 [05 KV 缓存](05-kv-cache.md) 联动） |
| `humming.py` / `turboquant` / `quark` / `torchao.py` / `inc` | 硬件厂商与社区后端 |

MoE 模型的量化要特别对待：线性层与专家层可分别配置，`FusedMoE` 走 `FusedMoEMethodBase` 子类（如 `Fp8MoEMethod`），未量化专家可用 `UnquantizedFusedMoEMethod` 跳过（F-101）。

## 使用方式

```bash
# 方式一：模型目录 quantization_config 自动识别（主流）
vllm serve <model> --dtype auto

# 方式二：命令行显式指定
vllm serve <model> --quantization fp8

# KV cache 量化（在量化配置之外单独控制）
vllm serve <model> --kv-cache-dtype fp8
```

`--quantization` 缺省时从模型 config 的 `quantization_config` 读取；llm-compressor 格式同时携带权重量化与忽略层清单（F-102）。

## Out-of-Tree 量化插件

自定义量化方法不改 vLLM 源码：用 `@register_quantization_config` 装饰器注册，实现 `QuantizationConfig` 的 `get_quant_method`（对 `FusedMoE` 返回 `FusedMoEMethodBase` 子类）与量化 `LinearMethodBase`/MoE method（F-103）。GPU 架构过滤用 `get_quant_method` 里的 capability 检查，插件在 `vllm/plugins/` 机制下被发现（F-104）。硬件厂商（AMD Quark、Intel INC、NVIDIA ModelOpt）均以此模式集成。

## 选型速查

| 场景 | 推荐 | 理由 |
|------|------|------|
| Hopper/Ada 新卡、追求速度 | FP8 W8A8 | 硬件原生 Tensor Core 支持，几乎无精度损失 |
| Ampere/显存吃紧 | GPTQ/AWQ INT4 | 跨代兼容，显存减半以上 |
| 消费级/ llama.cpp 生态迁移 | GGUF | 权重格式通用 |
| MoE 大模型 | FP8 + `moe_wna16`/`experts_int8` | 专家层是显存大头 |
| CPU 部署 | llm-compressor INT8 (W8A8/W4A8) | x86/Arm 均有支持 |

## 相关阅读

- [05 KV 缓存与 PagedAttention](05-kv-cache.md)：KV 量化、卸载与块管理
- [07 配置体系](07-configuration.md)：`--quantization` 等参数族
- [09 模型支持](09-model-support.md)：量化实现与模型实现的耦合
