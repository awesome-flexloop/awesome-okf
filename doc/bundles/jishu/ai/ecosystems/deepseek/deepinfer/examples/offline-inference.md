---
type: example
scope: deepinfer
name: DeepInfer 离线推理示例
version: "0.1.0"
source: examples/offline_inference.py, examples/README.md, examples/_config.py
description: offline_inference.py 完整用法——并行参数、长上下文、VL 回归、decode PPL 基线与结构化输出校验
---

# 离线推理示例

`examples/offline_inference.py` 是 DeepInfer 的入口示例：构造引擎 → 准备 prompts → 生成 → 输出接受率与 decode PPL，可选触发结构化输出校验。

---

## 一、命令行参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--model_name` | `deepseek-ai/DeepSeek-V4.1-Flash-1017` | HF 模型 ID 或本地 HF checkpoint 目录 |
| `--ep` | 8 | 专家并行规模 |
| `--dp` | `max(ep // cp, 1)` | 数据并行规模 |
| `--cp` | 1 | 上下文并行规模（须整除 ep_size） |
| `--disable_eplb` | 关 | 关闭 EPLB 专家负载均衡 |
| `--sampler_force_topk` | 4096 | 采样强制 top-k |
| `--long_context` | 关 | 每样本 16389 输入 token + 4096 输出 token |
| `--check_structured_output` | 关 | 生成后复用同一 LLM 校验 regex/JSON/EBNF 结构化输出 |

## 二、典型运行

```bash
python examples/offline_inference.py --ep 8
python examples/offline_inference.py --ep 2 --dp 8
python examples/offline_inference.py --ep 2 --cp 8
```

多机环境：

```bash
export WORLD_SIZE=1 RANK=0
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
```

引擎构造关键参数（`_config.py` 的 `create_llm`）：`max_num_batched_tokens=32768`、`max_model_len=32768`、`max_num_seqs=4`、`gpu_memory_utilization=0.85`、`lookahead_tokens=min(1, DEEPINFER_USE_NEXTN_DECODE)`。NVIDIA 平台默认注入 `DEEPINFER_BATCH_INVARIANT=1`。

## 三、输出解读

每个样本输出一行（格式被 `tests/models/test_offline_inference.py` 正则解析，**不可改动**）：

```
DP 0; INPUT: '...'; OUTPUT: '...'; output_tokens=N; accept_rate=XX%; decode_ppl=X.XX
```

- **accept_rate**：投机解码 draft 接受率（`num_accepted_draft_tokens / num_draft_tokens`；未开投机时为 N/A）；
- **decode_ppl**：`exp(−Σlogp / N)`——所有 token logprob 必须有限，非有限即断言失败。

## 四、模型加载策略

- `--model_name` 为模型 ID → `huggingface_hub.snapshot_download` 下载到本地 HF 缓存后使用；
- 为本地 HF 目录（config.json + safetensors）→ 直接使用，零网络访问；
- `DEEPINFER_HF_MODEL_DIR` 把**默认模型**指向本地副本，但不覆盖显式传入的 `--model_name`（`examples/_config.py` 生效）。

## 五、VL 离线回归样本

五个输入依次为：两个纯文本样本、一个单图样本、一个三图样本、一个五图 4-shot 样本。所有图片输入只用仓库 `images/` 下的 `carrots.jpeg` 与 `ribs.jpeg`；问答文本（含 `Answer: ` 尾随空格）内联在 `examples/_prompts.py`，无需外部 VL 缓存。修改图片或问题后，需在 NVIDIA 与昇腾上分别重测短/长 PPL 基线。

## 六、decode PPL 基线机制

- 基线存于 `tests/models/offline_decode_ppl.json`，按平台/负载（与传入模型目录无关）索引，每个 DP rank 一组样本，验证时逐样本精确比对；
- 数值变化确认符合预期后，`python examples/refresh_offline_decode_ppl.py` 更新短基线，加 `--long_context` 更新长基线；
- 多机运行（`_launch.run_dp` 跨节点拆分 DP ranks，本地 stdout 只带本地 rank）时，刷新与验证都按节点拆分：各节点只更新/比较自己拥有的 ranks；golden 基线在跨节点文件锁（`tests/models/offline_decode_ppl.json.lock`）保护下写入；
- `--output <path>`（保存候选基线）**仅支持单节点**——多节点下候选文件必然缺失其他节点的 ranks，脚本会直接报错并提示使用默认路径；
- 长 PPL（16389 输入 / 4096 输出 / nextn=5）包含在完整 pytest 运行（`python -m pytest -v -s tests`）中，单独跑用 `python -m pytest -v -s tests/models/test_offline_inference_long.py`。

## 七、结构化输出校验

加 `--check_structured_output` 后，离线推理在样例输出与 decode PPL 之后复用同一 LLM 实例运行 regex / JSON / EBNF 三类结构化检查并验证正常 EOS 终止，任一失败即整个运行失败。三类 `so_args` 用法见[结构化输出概念](../concepts/structured-output.md)。

## 八、昇腾调试提示

```bash
export ASCEND_LAUNCH_BLOCKING=1        # 同步执行算子，栈追踪易读
export ASCEND_SLOG_PRINT_TO_STDOUT=1   # CANN 日志打到 stdout
```
