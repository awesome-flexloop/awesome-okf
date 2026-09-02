---
type: concept
title: 扩展与部署——多 GPU、量化、SSH 远程与部署形态
description: >-
  OBLITERATUS 的横向扩展与部署全景：device_map=auto 朴素流水线并行的本质
  （内存方案而非速度方案）、双大模型基准表与最少 GPU 原则、--gpus 选择、
  精度与量化（dtype 显存表、bitsandbytes、FP8/NVFP4 自动去量化）、
  gpu-calc 估算器、SSH 远程六步流程、130 模型预设 5 层级、数据并行分支
  与四种部署形态。
tags:
  - multi-gpu
  - pipeline-parallelism
  - quantization
  - fp8
  - nvfp4
  - ssh
  - gpu-calc
  - deployment
sources:
  - https://github.com/elder-plinius/OBLITERATUS
  - .trae/specs/create-ai-security-okf-wiki/facts-obliteratus.md
---

# 扩展与部署：多 GPU、量化、SSH 远程与部署形态

## 一、多 GPU 的本质：内存方案，不是速度方案

模型放不进单卡时，OBLITERATUS 用 accelerate 的 `device_map="auto"` 把模型各层切片分布到所有可见 GPU（F-OB-021）。这是**朴素流水线并行**：层均匀分布，但激活逐层流过，**同一时刻只有一张 GPU 在计算**，其他 GPU 只是"存着自己那几层等轮到自己"。

三个工程推论（F-OB-021/022）：

1. 加 GPU 只解决"放得下"，不解决"跑得快"；
2. GPU 越多可能**越慢**——层边界的跨卡传输开销增加；
3. 流水线并行对计算密集阶段（PROBE/VERIFY）无加速——每次仍是一个 prompt 穿过整个层栈。

### 基准表（README 数据，[README-only] 无源码内基准文件可核验，F-OB-022）

GPT-OSS-120B（117B MoE，bf16 约 234 GB）：

| GPU 数 | 总耗时 | 每卡显存 | 备注 |
|--------|--------|---------|------|
| 3 | 失败 | 约 78 GB | 激活余量不足，部分层以 meta tensor 卸载到 CPU，EXCISE 阶段崩溃 |
| 4 | **615s**（最快） | 约 58 GB | 跨卡传输最少 |
| 5 | 763s | 约 47 GB | 比 4 卡慢 24% |
| 6 | 766s | 约 39 GB | 比 4 卡慢 25% |
| 8 | 633s | 约 29 GB | 比 4 卡慢 3%，额外跑了 CPU 侧快照约 20s |

DeepSeek-R1-Distill-Llama-70B（70B dense，bf16 约 149 GB，80 层）：

| GPU 数 | 总耗时 | 每卡显存 | 备注 |
|--------|--------|---------|------|
| 2 | 失败 | 约 75 GB | 149 GB 模型在 160 GB 总显存上无激活余量，meta tensor 崩溃 |
| 3 | **536s**（最快） | 约 50 GB | 该模型最少可行 GPU 数 |
| 4 | 626s | 约 37 GB | 比 3 卡慢 17% |
| 8 | 627s | 约 19 GB | 与 4 卡持平，无收益 |

阶段耗时分布（跨 GPU 数近似恒定）：VERIFY 约 210-270s、REBIRTH 约 194-350s——**VERIFY+REBIRTH 合计约占 90% 墙钟时间**，实际计算（PROBE/DISTILL/EXCISE）仅约 50-80s。

### 最少 GPU 原则

- 用**恰好放得下的最少 GPU**：4 卡快于 8 卡（GPT-OSS-120B）、3 卡最快（DeepSeek-70B）；
- 留足余量：参数显存之外还要容纳激活、KV cache 与中间量——234 GB 模型在 240 GB 总显存上失败、149 GB 模型在 160 GB 上失败；
- 大模型流水线运行是 I/O 主导的，先考虑量化再考虑加卡。

## 二、--gpus 选择与精度量化

### GPU 选择

`--gpus` 接受逗号分隔 GPU ID 或 `all`（默认），在 CUDA 初始化前设置 `CUDA_VISIBLE_DEVICES`（F-OB-023；cli.py L86-96 `_add_gpu_args`、L128-147 `_apply_gpu_selection`，remote 运行时跳过本地设置交给 remote runner）：

```bash
obliteratus obliterate bigmodel/200B --gpus all          # 全部
obliteratus obliterate bigmodel/200B --gpus 0,1,2,3      # 指定 0-3
obliteratus obliterate meta-llama/Llama-3.1-70B-Instruct --gpus 2,5
```

### dtype 显存表（F-OB-025，[README-only]）

| Dtype | 字节/参数 | 7B | 70B | 405B |
|-------|----------|-----|-----|------|
| float32 | 4 | 28 GB | 280 GB | 1620 GB |
| float16 / bfloat16 | 2 | 14 GB | 140 GB | 810 GB |
| int8（bitsandbytes） | 1 | 7 GB | 70 GB | 405 GB |
| int4（bitsandbytes） | 0.5 | 3.5 GB | 35 GB | 203 GB |

- `--dtype` 控制权重精度（cli.py L235 实测默认 `float16`；README 正文示例中另有 "Default: bfloat16" 的表述，以 CLI 默认值 float16 为准）；
- `--quantization` CLI choices 实测为 `["4bit","8bit"]`（cli.py L290，F-OB-024），依赖 extra `quantization`（bitsandbytes>=0.46.1，F-OB-051）；每降一档精度约省一半 GPU；
- 注意权衡：**修改权重时原生浮点权重数值保真更好**，量化加载只在"塞下模型"是首要约束时使用（F-OB-024 README 表述）。

### FP8 / NVFP4 checkpoint 自动支持

loader 从 checkpoint 的 `quantization_config` 检测格式，逐 shard 去量化为 float（默认 BF16），跑完流水线后输出保存为 BF16（F-OB-026）。检测的 scheme（models/quant_dequant.py L88-93 `QuantScheme` 枚举，模块 docstring 列四种）：

| 格式 | 覆盖 scheme |
|------|------------|
| FP8 | DeepSeek 式 block-wise（weight_scale_inv + weight_block_size）、compressed-tensors per-channel、ModelOpt FP8 |
| NVFP4 | ModelOpt（weight + weight_scale + weight_scale_2）、compressed-tensors NVFP4 |

两个关键限制：**峰值显存按模型的 BF16 尺寸计**（不是量化后尺寸），输出恒为 BF16（要量化服务工件需事后用 llm-compressor/modelopt 重压）；不支持的布局会明确报错并指名 scheme。

### 特例：Qwen3.8 hybrid 运行时契约

hybrid Gated DeltaNet 架构需要 FLA 与 causal-conv1d CUDA 内核，**拒绝**通用 PyTorch fallback 与多 GPU `device_map="auto"` 切片；完整文本模型必须置于单 CUDA 设备并留 15% headroom，不满足则停止分配；pristine 质量门失败则不修改 checkpoint；安装 `pip install -e ".[qwen-hybrid]"`（F-OB-037）。

## 三、gpu-calc 估算器

不确定需要几张卡时，`gpu-calc` 按 HF 模型名自动取配置估算最少 GPU 数，综合权重显存、激活开销与 CUDA context，输出带余量估算的配置表；MoE 模型的激活开销按**激活参数**而非总参数计算（F-OB-028；cli.py L537-561 核验，支持 `--params`/`--active-params`/`--dtype`/`--gpu-mem`）：

```bash
obliteratus gpu-calc meta-llama/Llama-3.1-70B-Instruct --gpu-mem 24
obliteratus gpu-calc --params 117 --active-params 13 --dtype bfloat16 --gpu-mem 80   # MoE 双参数
```

## 四、SSH 远程执行

从本地笔记本驱动远程 GPU 节点跑完整流水线。CLI 六参数（cli.py L99-125 `_add_remote_args`，F-OB-027）：`--remote [USER@]HOST`、`--ssh-key`、`--ssh-port`（默认 22）、`--remote-dir`（默认 /tmp/obliteratus_run）、`--remote-python`（默认 python3）、`--no-sync`（结果留在远端不回拷）。

remote runner 六步流程（细节 [README-only]，F-OB-027）：

```mermaid
flowchart LR
    A[1 连通性测试] --> B[2 nvidia-smi 探测 GPU]
    B --> C[3 远端自动安装]
    C --> D[4 上传配置文件]
    D --> E[5 实时日志流运行]
    E --> F[6 SCP 回拷结果]
```

安全要求（README 明文，F-OB-027）：**严格 host-key 验证**——通过独立渠道核实提供商指纹并先写入 `known_hosts` 再运行；使用最小权限非 root 账户，限定在目标计算目录与命令。`obliteratus run`（YAML）与 `obliteratus tourney` 同样支持 remote，YAML 内可写 `remote:` 段（host/user/ssh_key/remote_dir/gpus/sync_results）。

## 五、130 个模型预设的 5 层级

**勘误**：README 称 116 个模型，源码 presets.py 实际登记 130 个 `ModelPreset`（F-OB-013），层级划分一致。每条预设携带 `name`/`hf_id`/`description`/`tier`/`params`/`recommended_dtype`/`recommended_quantization`/`gated` 字段（presets.py L16-25 源码核验）。

| 层级 | 显存 | 示例模型 |
|------|------|---------|
| tiny | CPU / <1 GB | GPT-2、TinyLlama 1.1B、Qwen2.5-0.5B、SmolLM2 |
| small | 4-8 GB | Phi-2 2.7B、Gemma-2 2B、StableLM-2 1.6B |
| medium | 8-16 GB | Mistral 7B、Qwen2.5-7B、Gemma-2 9B、Phi-3.5 |
| large | 24+ GB | LLaMA-3.1 8B、Qwen2.5-14B、Mistral 24B、DeepSeek-R1 distills |
| frontier | 多 GPU | DeepSeek-V3.2 685B、Qwen3-235B、GLM-4.7 355B |

含预消融变体（Dolphin、Hermes、WhiteRabbitNeo）供与原版链式对照 A/B。浏览：`obliteratus models [--tier tiny|small|medium|large|frontier]`（cli.py L190-197 核验）。

## 六、数据并行分支

PROBE 阶段约 1024 次前向传播是"单卡放得下"场景的主要瓶颈，而流水线并行帮不上忙。真数据并行（复制模型到各卡 + 分发 prompt batch）位于实验分支 `data-parallel-prereplication`（`--data-parallel`，main 分支 cli.py 中无此参数，F-OB-038）：深拷贝模型到每张 GPU，线程池分发 batch。基准（Pythia 12B、8x A100）：单卡 PROBE 7.1s vs 8 卡数据并行 7.7s——该规模下并行开销已超收益，仅当 prompt 数或模型规模相对单次前向成本继续增大时才划算。

## 七、部署形态

| 形态 | 入口 | 要点 | F 编号 |
|------|------|------|--------|
| 本地 Gradio UI | `obliteratus ui`（--port 7860/--host 0.0.0.0/--share/--no-browser/--auth/--quiet，cli.py L210-228） | 与 HF Space 同一份 app.py（约 6,100+ 行、10 个顶级 tab），pyproject `py-modules = ["app"]` 使 wheel 内置 | F-OB-034/061 |
| HF Spaces ZeroGPU | hf-spaces/README.md frontmatter：sdk gradio 5.29.0、hardware zero-a10g、persistent_storage large | ZeroGPU 模式访客自带 GPU 配额——Space owner 零 GPU 成本、多用户并发互不干扰；Space 上遥测自动开启 | F-OB-062/030 |
| Colab | notebooks/abliterate.ipynb | 零命令路径：Run All 即跑 | F-OB-040 |
| YAML study 配置 | `obliteratus run <config.yaml> [--preset quick|full|attention|jailbreak|guardrail...]` | examples/ 含 8 个示例 YAML；10 个 study 预设经 study_presets.py 注册（layers/pruning 样本数 README 有误，F-OB-032） | F-OB-058/047 |

另有共享 GPU 主机部署契约（docs/deployment/shared-gpu-host.md：per-user workspace 0700、GPU 经调度器租约、UI 仅 loopback、`OBLITERATUS_GPU_LIFECYCLE_DIR` 生命周期协议）与 systemd 单元（F-OB-064/065），详见[架构地图](../references/architecture-map.md)。

## 选型决策表

| 场景 | 推荐 |
|------|------|
| 模型单卡放得下 | 就用 1 张，加卡无益甚至更慢 |
| 差一点放不下 | 先 `--quantization 8bit`/`4bit`，减半精度约减半显存 |
| 单卡放得下但 PROBE 慢 | data-parallel 分支（仅当每卡放得下且有激活余量） |
| 单卡放不下 | `--gpus` 用最少可行数；`gpu-calc` 先算 |
| 需要 4+ 卡 | 流水线并行是唯一选项，预期 I/O 主导；优先考虑 int4 降 4 倍卡数 |
| 本地无 GPU | `--remote user@gpu-node`，或 HF Spaces / Colab |

## 延伸阅读

- 远程/本地命令行全参数实操：[cli-quickstart.md](../examples/cli-quickstart.md)
- 凭据六级解析与部署资产：[architecture-map.md](../references/architecture-map.md)
- HF Spaces 上的遥测行为：[research-ecosystem.md](research-ecosystem.md)
