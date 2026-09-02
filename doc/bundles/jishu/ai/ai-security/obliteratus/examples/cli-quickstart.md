---
type: example
title: CLI 实战——从安装到 aggregate 的全流程
description: >-
  OBLITERATUS 命令行实战：四种安装方式、info/models/presets/strategies 探索
  命令、obliterate 单命令消融与全参数示例、interactive 引导、run YAML study、
  aggregate 汇总、gpu-calc 估算，附 19 个 CLI 子命令速查表。全部命令与参数
  经 cli.py 源码核验并标注 F-OB 编号。
tags:
  - cli
  - obliterate
  - interactive
  - study
  - aggregate
  - gpu-calc
sources:
  - https://github.com/elder-plinius/OBLITERATUS
  - .trae/specs/create-ai-security-okf-wiki/facts-obliteratus.md
---

# CLI 实战：从安装到 aggregate 的全流程

本篇所有命令与参数均经 `obliteratus/cli.py` 源码核验（版本 0.1.3，F-OB-041/042/051），并以 F-OB 编号标注出处。请先阅读[束根的研究用途限定声明](../index.md)——本篇内容为上游公开文档的如实记录，仅用于对齐研究与安全评估语境。

## 1. 安装

```bash
# 基础安装（源码目录内，可编辑模式；核心依赖 torch/transformers/accelerate 等）
pip install -e .

# Web UI（Gradio，与 HF Space 同一 app.py）
pip install -e ".[spaces]"

# bitsandbytes 量化后端（4bit/8bit 需要）
pip install -e ".[quantization]"

# Qwen3.8 hybrid 运行时（FLA + causal-conv1d CUDA 内核）
pip install -e ".[qwen-hybrid]"

# 开发与测试
pip install -e ".[dev]"
```

依赖组经 pyproject.toml 核验（F-OB-051）：可选组 dev/quantization/qwen-hybrid/spaces；Python >=3.10。安装后入口点为 `obliteratus`（`[project.scripts] obliteratus = "obliteratus.cli:main"`）。

## 2. 探索命令（先看后跑）

```bash
obliteratus --version                      # 版本号（0.1.3）
obliteratus info meta-llama/Llama-3.1-8B-Instruct
#   打印模型架构信息；--task causal_lm|classification、--device cpu、--dtype float32（cli.py L177-181）

obliteratus models                         # 浏览 130 个模型预设（README 称 116 为勘误项）
obliteratus models --tier tiny             # 按 tiny|small|medium|large|frontier 过滤（L190-197）

obliteratus presets                        # 浏览 study 预设（quick/full/attention/jailbreak 等，L200）
obliteratus strategies                     # 列出消融策略（layer_removal/head_pruning/ffn_ablation/embedding_ablation，L203）
```

## 3. obliterate：单命令消融

最小命令（README 示例，`--method` 默认值 `advanced`，F-OB-008/042）：

```bash
obliteratus obliterate meta-llama/Llama-3.1-8B-Instruct --method advanced
```

### 关键参数（cli.py 逐项核验）

| 参数 | 说明 | 锚点 |
|------|------|------|
| `model`（位置参数） | HuggingFace 模型名/路径 | L232 |
| `--output-dir` | 产出模型保存目录 | L233 |
| `--device` | 默认 auto | L234 |
| `--dtype` | 权重精度，默认 float16 | L235 |
| `--method` | 10 choices：basic/advanced/aggressive/spectral_cascade/informed/surgical/optimized/som/inverted/nuclear，默认 advanced | L237-243 |
| `--n-directions` | 覆盖预设的方向数 | L244 |
| `--direction-method` | diff_means/svd/leace/som | L245-249 |
| `--regularization` | 保留比例覆盖（0.0-1.0） | L250 |
| `--refinement-passes` | 迭代精炼轮数覆盖 | L251 |
| `--min-layer-fraction` / `--max-layer-fraction` | 层选择的深度分数下限/上限（如 0.75 只动最后四分之一） | L252-258 |
| `--quantization` | 4bit / 8bit（bitsandbytes） | L290 |
| `--contribute` | 本次运行贡献社区遥测数据集 | L361-364 |
| `--contribute-notes` | 贡献备注 | L365-368 |
| `--gpus` | 逗号分隔 GPU ID 或 all（设 CUDA_VISIBLE_DEVICES） | L89-96 |

### 全参数示例

```bash
# 本地多卡 + 量化 + 贡献遥测
obliteratus obliterate meta-llama/Llama-3.1-70B-Instruct \
    --method surgical \
    --output-dir ./out-70b \
    --gpus 0,1,2,3 \
    --dtype float16 \
    --quantization 8bit \
    --contribute --contribute-notes "4xA100-80GB, surgical"

# 远程执行（六参数组，cli.py L102-125）
obliteratus obliterate meta-llama/Llama-3.1-70B-Instruct \
    --remote obliteratus@10.0.0.5 \
    --ssh-key ~/.ssh/id_rsa \
    --ssh-port 2222 \
    --remote-dir /data/obliteratus \
    --remote-python python3.11
    # 加 --no-sync 则结果留在远端不回拷
```

> 提醒：远程执行要求严格 host-key 验证与最小权限非 root 账户（见[扩展与部署篇](../concepts/scaling-deployment.md)第四节）。

## 4. interactive：引导模式

```bash
obliteratus interactive
```

无参数的引导式向导：交互选择硬件、模型与预设（cli.py L184-187），适合首次接触或不想记参数的场景。

## 5. run：YAML 研究运行

```bash
obliteratus run examples/preset_quick.yaml            # 跑一个 study 配置
obliteratus run full_study.yaml --preset jailbreak    # --preset 覆盖预设（cli.py L164-172）
obliteratus run config.yaml --output-dir ./out2       # 覆盖输出目录
```

YAML 结构与 remote 段示例见 [python-api.md](python-api.md) 第五节的配置文件结构（`run` 与 remote 的 YAML 支持同源，F-OB-058）。10 个 study 预设（quick/full/attention/layers/knowledge/pruning/embeddings/jailbreak/guardrail/robustness）经 study_presets.py 注册核验；其中 layers 与 pruning 的 max_samples 源码实测均为 100（README 写 150/200 为勘误项，F-OB-032）。

## 6. aggregate：汇总社区/本地数据

```bash
obliteratus aggregate --format summary                                  # 概览
obliteratus aggregate --format latex --metric refusal_rate --min-runs 3 # 论文级 LaTeX 表
```

（F-OB-029 语境下的 README 用法；数据来源为遥测数据集或本地贡献 JSON。）

## 7. gpu-calc：最少 GPU 估算

```bash
obliteratus gpu-calc meta-llama/Llama-3.1-70B-Instruct --gpu-mem 24   # 按 HF 名自动取参数量
obliteratus gpu-calc --params 70 --dtype bfloat16 --gpu-mem 80        # 手动指定
obliteratus gpu-calc --params 117 --active-params 13 --dtype bfloat16 --gpu-mem 80   # MoE 双参数
```

四个参数 `--params`/`--active-params`/`--dtype`/`--gpu-mem` 经 cli.py L537-561 核验（F-OB-028）。决策逻辑见[扩展与部署篇](../concepts/scaling-deployment.md)选型决策表。

## 8. 十九个子命令速查表

CLI 顶层子命令共 19 个（含 1 个隐藏别名），全部经 cli.py 行号核验（F-OB-041）：

| 子命令 | 行号 | 用途 |
|--------|------|------|
| run | L164 | 运行 YAML 消融配置（支持 --preset 覆盖与 remote） |
| info | L177 | 打印模型架构信息 |
| interactive | L184 | 引导式向导 |
| models | L190 | 浏览模型预设（--tier 过滤） |
| presets | L200 | 浏览 study 预设 |
| strategies | L203 | 列出消融策略 |
| ui | L206 | 本地启动 Gradio UI（--port 7860/--host 0.0.0.0/--share/--no-browser/--auth/--quiet，L210-228） |
| obliterate | L370 | 主消融命令 |
| abliterate | L378 | obliterate 的向后兼容别名（help=argparse.SUPPRESS 隐藏） |
| self-improve | L384 | 自改进流程 |
| report | L418 | 报告生成 |
| aggregate | L423 | 汇总社区/本地贡献数据 |
| restore-multimodal | L430 | 恢复多模态组件 |
| capability-check | L442 | 能力检查 |
| blend | L456 | 模型混合 |
| tourney | L496 | 方法对比锦标赛（10 方法，tourney.py L41-52，F-OB-015） |
| recommend | L524 | 自适应推荐（get_adaptive_recommendation，F-OB-053） |
| gpu-calc | L537 | GPU 需求估算 |
| runs | L564 | 运行管理，含 6 个子命令：launch(L572)/status/cancel/result(L578-580)/list(L581)/prune-checkpoint(L582-586) |

## 9. 常用组合套路

```bash
# 套路一：零风险冒烟（CPU 可跑的小模型 + 默认 advanced）
obliteratus obliterate Qwen/Qwen2.5-0.5B --output-dir ./smoke

# 套路二：先 steering 预筛再落刀（见 python-api.md steering 段），
#        或直接用 informed 方法让分析模块自动配置
obliteratus obliterate meta-llama/Llama-3.1-8B-Instruct --method informed

# 套路三：大模型全流程（先估算再执行再汇总）
obliteratus gpu-calc Qwen/Qwen3-235B --gpu-mem 80
obliteratus obliterate Qwen/Qwen3-235B --method nuclear --gpus all --contribute
obliteratus aggregate --format summary
```

## 延伸阅读

- 方法选择的原理依据：[methods-presets.md](../concepts/methods-presets.md)
- 六阶段执行过程中各参数生效位置：[pipeline-six-stages.md](../concepts/pipeline-six-stages.md)
- Python API 与 YAML 配置文件结构：[python-api.md](python-api.md)
