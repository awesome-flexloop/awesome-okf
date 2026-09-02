---
type: example
title: Python API 实战——Pipeline、Informed 与 Steering Vectors
description: >-
  OBLITERATUS Python API 实战：AbliterationPipeline 标准六阶段调用与产物
  属性读取、InformedAbliterationPipeline 七阶段闭环与报告字段、steering
  vectors 可逆干预四步代码、YAML study 配置文件结构。API 签名与 README
  代码示例经源码逐项核验并标注 F-OB 编号。
tags:
  - python-api
  - abliterationpipeline
  - informed-pipeline
  - steering-vectors
  - yaml-config
sources:
  - https://github.com/elder-plinius/OBLITERATUS
  - .trae/specs/create-ai-security-okf-wiki/facts-obliteratus.md
---

# Python API 实战：Pipeline、Informed 与 Steering Vectors

本篇代码与 README 中 Python 示例一致的 API 签名均经源码逐项核验（F-OB-043/044/048），以【已核验】标注。包级导出经 `obliteratus/__init__.py` 的 `__all__`（20 项，懒加载，F-OB-053）。

## 1. AbliterationPipeline：标准六阶段

```python
from obliteratus.abliterate import AbliterationPipeline

pipeline = AbliterationPipeline(
    model_name="meta-llama/Llama-3.1-8B-Instruct",
    method="advanced",          # 默认即 advanced
    output_dir="abliterated",
    device="auto",
    dtype="float16",
)

output_path = pipeline.run()    # -> Path，驱动 SUMMON→PROBE→DISTILL→EXCISE→VERIFY→REBIRTH

# 三个核心产物属性【已核验 F-OB-043】
print(pipeline.refusal_directions)   # dict[int, torch.Tensor]：层号 -> 拒绝方向（L1227）
print(pipeline._strong_layers)       # list[int]：拒绝信号最强的层（L1229）
print(pipeline._quality_metrics)     # dict[str, float]：质量指标（L1235）
```

质量指标键【已核验 F-OB-043】：

| 键 | 含义 | 行号 |
|----|------|------|
| `baseline_perplexity` | 修改前困惑度 | L1716 |
| `baseline_coherence` | 修改前连贯性 | L1717 |
| `perplexity_increase` | 消融后困惑度增幅（VERIFY 门禁：默认上限 3.0） | L1760 |
| `degenerate_fraction` | 退化生成占比（门禁：默认上限 0.2） | L1774 |
| `coherence_retention` | 连贯性保持率（门禁：默认下限 0.5） | L1787 |

门禁阈值经 `max_perplexity_increase`/`min_coherence_retention`/`max_degenerate_fraction` 构造参数传入（informed 构造函数签名核验，F-OB-044）。VERIFY 失败抛 `PipelineValidationError`，用户取消抛 `PipelineCancelledError`，统一基类 `PipelineFailure`（F-OB-056）。

进阶构造参数：`harmful_prompts`/`harmless_prompts`（自定义提示词集）、`on_stage`/`on_log` 回调、`cancellation_event`（协作式取消）、`push_to_hub`/`hub_token`/`hub_community_org`（发布）、`quantization`（informed 构造函数转发清单 L176-232，F-OB-044）。

## 2. InformedAbliterationPipeline：七阶段闭环

```python
from obliteratus.informed_pipeline import InformedAbliterationPipeline

pipeline = InformedAbliterationPipeline(
    model_name="meta-llama/Llama-3.1-8B-Instruct",
    output_dir="abliterated_informed",
    ouroboros_threshold=0.5,     # 自修复检出阈值
    max_ouroboros_passes=3,      # 补偿循环上限（默认 3）
    entanglement_gate=0.8,       # 纠缠门控：超过则跳层
)

output_path, report = pipeline.run_informed()
# -> tuple[Path, InformedPipelineReport]

# 报告三字段【已核验 F-OB-044，与 README L246-257 示例一致】
print(report.insights.detected_alignment_method)   # 对齐指纹：DPO/RLHF/CAI/SFT/unknown（L103）
print(report.insights.recommended_n_directions)    # 分析推导的方向数（L133，默认 1）
print(report.ouroboros_passes)                     # 实际执行的补偿 pass 数（L149，默认 0）
```

`run_informed()`（L270）失败时自动执行 `cleanup_failed_run()` 再抛出（L277-281）——事务性语义：失败的运行不留下半成品 checkpoint。

报告对象 `InformedPipelineReport`（L142-150）完整字段：`insights`（AnalysisInsights）、`stages`（StageResult 列表）、`analysis_duration`、`total_duration`、`ouroboros_passes`、`final_refusal_rate`。`AnalysisInsights` 全字段见[分析模块篇](../concepts/analysis-modules.md)；序列化含 detected_alignment_method/n_directions/ouroboros_passes（L1241/L1258/L1271，F-OB-057）。

ANALYZE 阶段可独立开关五个分析：`run_cone_analysis`/`run_alignment_detection`/`run_cross_layer_analysis`/`run_sparse_analysis`/`run_defense_analysis`（L197-201）；旧参数别名 `hydra_threshold`/`max_hydra_passes` 向后兼容（L206-207）。

## 3. Steering Vectors：可逆干预四步

权重不动的推理时干预，基于 Turner 2023 / Rimsky 2024（F-OB-019/020）。以下代码与 README L390-410 示例一致，API 签名经 steering_vectors.py 核验【F-OB-048】：

```python
from obliteratus.analysis import SteeringVectorFactory, SteeringHookManager
from obliteratus.analysis.steering_vectors import SteeringConfig

# 第 1 步：构造 steering 向量（二选一）
#   来源 A：从已提取的拒绝方向（alpha=-1.0 远离拒绝 = 消融效果；+1.0 反向强化）
vec = SteeringVectorFactory.from_refusal_direction(refusal_dir, alpha=-1.0)     # L90
#   来源 B：从对比激活对（mean(positive) - mean(negative)，L118）
vec = SteeringVectorFactory.from_contrastive_pairs(harmful_acts, harmless_acts)

# 第 2 步：配置目标层与强度
config = SteeringConfig(
    vectors=[vec],
    target_layers=[10, 11, 12, 13, 14, 15],   # 在哪些层注入
    alpha=1.0,                                 # 全局缩放（L71）
    # per_layer_alpha={12: 0.5},               # 逐层覆盖（L72）
    # position="all",                          # all | last | first（L73）
    # normalize=True,                          # 注入前归一化（L74）
)

# 第 3 步：挂载 hook（注册 forward hook，向残差流加 alpha * default_alpha * d）
manager = SteeringHookManager()
manager.install(model, config)      # -> SteeringResult（hooks_installed / total_steered_layers）

# 生成——steering 生效
output = model.generate(input_ids)

# 第 4 步：卸载——模型恢复原状，零残留
manager.remove()
```

源码细节：hook 实现支持 3D（batch, seq_len, hidden）与 2D 隐藏态及 `position` 三种注入位置（L255-299）；`SteeringVectorFactory.combine(vectors, weights)` 可把多向量加权合并（L155-187）；辅助函数 `compute_steering_effectiveness`（L321）与 `format_steering_report`（L346）量化 steering 效果。

**与权重投影的取舍**：steering 是 informed 流水线 VERIFY 阶段的预筛手段（永久修改前先可逆验证），也是 A/B 实验的快捷通道；要产出"消融后模型文件"则必须走权重投影。对比表见[方法预设篇](../concepts/methods-presets.md)。

## 4. 贡献与聚合三 API

```python
from obliteratus import save_contribution, load_contributions, aggregate_results

output_path = pipeline.run()
save_contribution(pipeline, model_name="meta-llama/Llama-3.1-8B-Instruct",
                  notes="A100, default prompts")       # 存本地贡献 JSON（community.py L83）
records = load_contributions("community_results")       # 读入（L196）
aggregated = aggregate_results(records)                 # 聚合成论文表（L225）
```

【已核验 F-OB-053，与 README L819-831 用法一致。】这是不走遥测的 PR 式贡献路径（见[研究生态篇](../concepts/research-ecosystem.md)）。

## 5. YAML study 配置文件结构

`obliteratus run config.yaml` 的配置结构（`run_study(config: StudyConfig) -> AblationReport`，runner.py L19，F-OB-058；remote 段与 README L703-715 示例一致）：

```yaml
model:
  name: meta-llama/Llama-3.1-70B-Instruct
  dtype: float16

study:                  # 研究配置：策略组合与样本量（StudyPreset 字段，F-OB-047）
  preset: jailbreak     # CLI --preset 覆盖此值
  strategies:
    - layer_removal
    - head_pruning
    - ffn_ablation
  max_samples: 400
  batch_size: 8
  max_length: 512

output:
  dir: results/jailbreak-study

remote:                 # 远程执行段（可选；本地跑则省略）
  host: gpu-node
  user: obliteratus
  ssh_key: ~/.ssh/id_rsa
  remote_dir: /tmp/obliteratus_run
  gpus: "0,1,2,3"       # 远端 GPU 选择
  sync_results: true    # 完成后回拷结果
```

八个官方示例 YAML（examples/ 目录清单核验，F-OB-058）：full_study.yaml、gpt2_gpu_quick.yaml、gpt2_head_ablation.yaml、gpt2_layer_ablation.yaml、preset_attention.yaml、preset_knowledge.yaml、preset_quick.yaml、remote_gpu_node.yaml。10 个 study 预设的 strategies/metrics/max_samples/batch_size/max_length/tags 字段结构经 StudyPreset dataclass 核验（study_presets.py L14-26）；layers 与 pruning 的样本数勘误见[新技术谱系篇](../concepts/novel-techniques.md)勘误表 #4。

## 6. 包级导出速查

`obliteratus/__init__.py` 的 20 个导出（懒加载，F-OB-053）：

| 类别 | 导出名 |
|------|--------|
| 流水线 | AbliterationPipeline、InformedAbliterationPipeline |
| 扫描 | set_seed、run_sweep、SweepConfig、SweepResult |
| 社区 | save_contribution、load_contributions、aggregate_results |
| 锦标赛 | TourneyRunner、TourneyResult |
| 自适应 | get_adaptive_recommendation、AdaptiveRecommendation |
| 远程 | RemoteRunner、RemoteConfig |
| 守护 | Watchtower、get_watchtower |
| 自动化 | AutoObliterator、RunArchive |

`__version__ = "0.1.3"`。

## 延伸阅读

- 各阶段内部发生了什么：[pipeline-six-stages.md](../concepts/pipeline-six-stages.md)
- 报告字段的检测来源：[analysis-modules.md](../concepts/analysis-modules.md)
- CLI 等价命令：[cli-quickstart.md](cli-quickstart.md)
