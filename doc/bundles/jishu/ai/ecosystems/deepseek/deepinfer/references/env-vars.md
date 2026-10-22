---
type: reference
scope: deepinfer
name: DeepInfer 环境变量总表
version: "0.1.0"
source: deepinfer/environ.py, examples/README.md
description: DEEPINFER_* 环境变量配置体系——平台、投机解码、调度、EPLB、结构化输出与多模态
---

# DEEPINFER_* 环境变量总表

环境变量集中定义于 `deepinfer/environ.py`。按功能域分组：

## 一、平台与构建

| 变量 | 默认 | 含义 |
|---|---|---|
| `DEEPINFER_ACCELERATOR` | nvidia | 平台选择（nvidia/ascend），构建与运行共用 |
| `DEEPINFER_HF_MODEL_DIR` | — | 默认模型本地副本路径（示例层约定，`examples/_config.py` 生效；不覆盖显式 `--model_name`） |

## 二、投机解码（DSpark）

| 变量 | 默认 | 含义 |
|---|---|---|
| `DEEPINFER_USE_NEXTN_DECODE` | 5 | 最大 draft 长度；设 0 关闭投机解码 |
| `DEEPINFER_ENABLE_MTP_VARLEN` | 0 | DSpark 变长验证总开关 |
| `DEEPINFER_MAX_BACKTRACKING_TOKENS` | nextn+1 | 验证回退上限 |
| `DEEPINFER_DFLASH_CONFIDENCE_HEAD_TEMPERATURE` | 1.0 | confidence head 温度（可逗号分隔 per-nextn 元组） |

## 三、调度与执行

| 变量 | 默认 | 含义 |
|---|---|---|
| `DEEPINFER_ZERO_OVERHEAD_SCHEDULING` | 按引擎类型 | ZOS 异步调度；NORMAL/COMPLETION 默认开启 |
| `DEEPINFER_YOCO_PREFILL_TRUNCATION_MODE` | off | Decoder SWA bounded replay 模式：off/mask/compact |
| `DEEPINFER_YOCO_PREFILL_KEEP_TOKENS` | 0 | 截断保留后缀长度；须 ≥ SWA 窗口 + 最大回退（V4.1 默认 140） |
| `DEEPINFER_ENFORCE_EAGER` | 0 | 关闭 CUDA graph（主模型） |
| `DEEPINFER_DFLASH_ENFORCE_EAGER` | 0 | 关闭 DFlash 的 CUDA graph |
| `DEEPINFER_BATCH_INVARIANT` | 0 | Batch 不变推理（NVIDIA only） |

## 四、EPLB 与通信

| 变量 | 默认 | 含义 |
|---|---|---|
| `DEEPINFER_OVERRIDE_NUM_EXTRA_EXPERTS` | 0 | EPLB 冗余专家数下界（实践默认 32；引擎向上取整到 ep_size 整除） |
| `DEEPINFER_MOE_LB_STAT_INTERVAL` | 128 | MoE 负载统计间隔（step） |
| `DEEPINFER_NCCL_NUM_SMS` | 32 | NCCL 通信 SM 预算 |

## 五、采样控制

| 变量 | 默认 | 含义 |
|---|---|---|
| `DEEPINFER_SAMPLER_FORCE_TOPK` | — | 强制采样 top-k |
| `DEEPINFER_DECODE_TOKEN_BLACKLIST` | — | 解码 token 黑名单 |

## 六、结构化输出

| 变量 | 默认 | 含义 |
|---|---|---|
| `DEEPINFER_XGRAMMAR_TIMEOUT` | 20 | SO 编译超时（秒） |
| `DEEPINFER_XGRAMMAR_CACHE_LIMIT_BYTES` | 10 GiB | SO 编译缓存上限（防 CVE-2025-32381 DoS） |
| `DEEPINFER_SO_BUILDER_CPUS` | 4 | SO matcher 构建线程数 |

## 七、多模态与观测

| 变量 | 默认 | 含义 |
|---|---|---|
| `DEEPINFER_MULTIMODAL_POOL_SIZE_GB` | 8 | 多模态共享内存池大小 |
| `DEEPINFER_USE_MULTIMODAL_POOL` | 按引擎类型 | 是否启用多模态内存池 |
| `DEEPINFER_LOGGING_INTERVAL_STEP` | — | 周期日志间隔（设 0 关闭；benchmark 静默段用它） |

## 八、常用组合速查

| 目标 | 组合 |
|---|---|
| 开启 DSpark 变长验证 | `DEEPINFER_ENABLE_MTP_VARLEN=1`（长度看 `DEEPINFER_USE_NEXTN_DECODE`） |
| V4.1 默认 SWA replay | `DEEPINFER_YOCO_PREFILL_TRUNCATION_MODE=compact` + `DEEPINFER_YOCO_PREFILL_KEEP_TOKENS=140` |
| 确定性输出 | `DEEPINFER_BATCH_INVARIANT=1` + `DEEPINFER_ENABLE_MTP_VARLEN=0` + `SamplingParams(seq_seed=固定值)` |
| 昇腾调试 | `ASCEND_LAUNCH_BLOCKING=1` + `ASCEND_SLOG_PRINT_TO_STDOUT=1` |
