---
type: example
scope: deepinfer
name: DeepInfer 性能基准示例
version: "0.1.0"
source: examples/benchmark.py, examples/README.md, examples/sweep/
description: benchmark.py 稳态指标口径、预填充/解码解耦、sweep 扫参与 Pareto 曲线绘制
---

# 性能基准示例

`examples/benchmark.py` 提供 prefill 与 decode 解耦的性能基准；`examples/sweep/` 提供单维扫参并连成吞吐-延迟 Pareto 曲线。

---

## 一、阶段解耦与指标口径

### 1.1 阶段解耦

- `--prefill_batch_size` 与 `--non_cached_tokens` 只影响 prefill 阶段的 chunk 大小与后缀长度；
- `--decode_num_requests` 只控制 decode 批大小；
- prefill 所需请求数 `N = prefill_num_requests` 由 profiling 所需 chunk 数**反推**（与 decode 批 K 无关），上限 512；命中上限导致总 prefill 工作量填不满稳态计划时打印 WARNING（此时 prefill 指标无意义）；连 warmup + profiling 收集窗口都完不成则启动即失败；
- 唯一耦合点：decode 复用 prefill 产出的共享前缀 KV，整批用 `max(N, K)` 个请求创建（`--cp > 1` 时向上取整使批能被 CP 单元均分）——`N > K` 时序号 ≥ K 的请求 `max_tokens=1`、产首 token 即淘汰、不进 decode 批；`N ≤ K` 时多余 prefill chunk 变成更长 warmup；
- 每个请求由一个源请求 fork：先算 `context_length − non_cached_tokens` 个缓存 token（`--non_cached_tokens` 不得超过 `--context_length`），再各自算非缓存后缀；缓存长度为 0 时直接创建。VL prompt 保持图片总数不变且整图分布在缓存前缀与非缓存后缀（无图片跨缓存边界）。

### 1.2 默认值

`decode_num_requests=64`、`context_length=32768`、`non_cached_tokens=4096`、`prefill_batch_size=32768`；nextn 默认 5（全接受口径下 64 请求一步共 384 token）。`DEEPINFER_USE_NEXTN_DECODE=0` 显式关闭投机解码。

### 1.3 三大稳态指标（dp_rank == 0 打印）

| 指标 | 口径 |
|---|---|
| **prefill throughput**（tokens/s/GPU） | 跳过 5 个 warmup chunk 后，最后 11 个 prefill 样本取 10 个稳态区间；10 步处理 token 数 ÷ 总时长 ÷ 设备数（首个样本只提供起始时间戳、token 不计）。供给不足两个采样点时打 N/A；与 LB 统计 flush 撞上的区间剔除（最多丢一个区间） |
| **decode avg_SPS**（steps/s） | 跳过 50 warmup 步与 60 logged 步、decode profiler 挂载前，最后 61 个满批样本取 60 个稳态区间；与 MoE LB 统计 flush（EP all_gather、抖动十几 ms）撞上的区间剔除后再平均；同时打印干净区间内最慢单步 `max_step`（正常应接近 `1000 / avg_SPS`） |
| **decode throughput**（tokens/s/GPU） | `avg_SPS × decode_num_requests × (1 + nextn) / --cp`，全接受口径——每请求每步 `1 + nextn` 个 token，与真实接受率无关 |

`--result_jsonl <FILE>` 把完整配置与三指标背后的原始量（窗口步数、token 数、耗时、avg_SPS）追加为一行 JSON。

### 1.4 Profiler 与日志纪律

- `PROFILE=1` 时 prefill 与 decode 各跑独立 profiler 段，导出时首尾拼接为一条 trace（恒含 2 个完整 chunk 的 prefill 步 + 3 个稳态 decode 步；尾部部分 prefill chunk、decode warmup 与测量窗口跑在两个 profiler 段之间，不入 trace 也不吃 profiler 开销）；
- decode profiler 必须在测量流**最末**：退出后仍有约 7-11% 残余减速（bsz=1 实测），其后不得再排任何测量；trace 内步时含 profiler 即时开销（bsz=1 最多膨胀近 50%），只用于观察 kernel 构成，**不得**据此推导 SPS；
- 测量段加倍：前半开日志（prefill 每 5 步、decode 每 20 步，moe_lb 等在此读取），后半静默出数；批构建、warmup、profile 窗口与 profiler 退出期间日志关闭（`DEEPINFER_LOGGING_INTERVAL_STEP=0`）。

## 二、典型场景

```bash
python examples/benchmark.py                                      # 默认
python examples/benchmark.py --cp 8 --prefill_batch_size 65536    # CP8 + 大 chunk
python examples/benchmark.py --decode_num_requests 1             # 低延迟单请求
python examples/benchmark.py --decode_num_requests 64 \
       --context_length 131072 --yoco_clip                        # 128k + YoCo 截断

python examples/benchmark.py --prompt_mode text                  # 纯文本
python examples/benchmark.py --prompt_mode image                 # ViT 与 LLM 同引擎
```

- 并行规模由环境决定：`ep_size = WORLD_SIZE × len(CUDA_VISIBLE_DEVICES)`（未设时用 `ASCEND_RT_VISIBLE_DEVICES`），`--cp` 须整除 `ep_size`；
- 冗余专家数经 `DEEPINFER_OVERRIDE_NUM_EXTRA_EXPERTS` 传入（实践默认 32）；该值只是**下界**，引擎把 `num_routed_experts + num_extra_experts` 向上取整到 `ep_size` 整除（backbone 与 DFlash 分别取整），落盘记录与绘图都用实际生效的取整值；
- nextn 只经 `DEEPINFER_USE_NEXTN_DECODE` 显式覆盖（设 0 关闭），从不从模型名推断。

## 三、Sweep 与 Pareto 曲线

```bash
# decode：扫 decode_num_requests（8…256），nextn=3，按 0.75 接受率缩放绘图
bash examples/sweep/run_sweep.sh decode ce-128k 131072 3 0.75

# prefill：扫 prefill_batch_size（4096…65536）
bash examples/sweep/run_sweep.sh prefill pe-128k 131072

# encoder：固定图片尺寸，扫每批图片数（1…32）
bash examples/sweep/run_sweep.sh encoder ve-800
```

- 每个 sweep 点启动一次 `benchmark.py`，恒以 `PROFILE=0` 运行（profiler 扰动稳态读数）；日志不落盘，输出直达 stdout，以 `--- point ... ---` 分段；
- 产物为 `sweeps/<tag>/results.jsonl` 与 `sweeps/<tag>/<mode>_pareto.png`（绘图需 matplotlib）；多机时只有持有 dp_rank 0 的节点写 jsonl，其余节点正常退出；
- 一个 tag 一条曲线：改模式或任一固定配置即开新 tag；并行规模在命令中不可见（来自环境），惯例把规模写进 tag 名（如 `ep64-decode-128k`）；同 jsonl 出现不一致点会被一致性断言拦截（model、`ep_size`、`--cp`、`context_length`、`nextn`、冗余专家数、prefill 的 `yoco_clip`）；
- encoder 扫参走 `sweep/ve_sweep.py`：只加载 VE 侧权重不加载 LLM，同进程内逐点计时；图像编码是纯单设备计算，默认 `--dp 1` 即得完整曲线；计时窗口只覆盖 GPU 侧 pad → ViT → downsample → aligner（CPU 预处理由 `MultimodalProcessor` worker 进程在 step 关键路径外异步完成、H2D 随 `InputMetadata` 走通用传输，两者均不计）；吞吐按每图折算的 LLM token 数缩放，与 prefill 曲线同单位；`--image_size W H` / `--num_images N...` 改图片尺寸与扫参点。

## 四、YoCo 等价性验证

`examples/yoco/README.md` 提供 YoCo mask/compact 截断模式的等价性验证（对应 SWA Bounded Replay 的两种模式，见[部署实践](../concepts/deployment-practice.md)）。
