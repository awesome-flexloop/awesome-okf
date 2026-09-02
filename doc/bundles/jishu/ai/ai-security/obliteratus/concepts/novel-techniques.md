---
type: concept
title: 2025-2026 新技术谱系与 README 勘误表
description: >-
  OBLITERATUS 实现的 11 项新技术（EGA、CoT-Aware、COSMIC、RDO、KL 共优化、
  组件级缩放、LoRA 可逆消融、激活缩尾、浮点方向插值、多方向范数保持、
  参数化核优化）——每项一句话机制、解决的问题与来源；附 6 处 README
  与源码不一致的完整勘误对照表与源码锚点核验方法示范。
tags:
  - ega
  - cosmic
  - rdo
  - kl-divergence
  - lora
  - winsorization
  - errata
  - documentation-drift
sources:
  - https://github.com/elder-plinius/OBLITERATUS
  - .trae/specs/create-ai-security-okf-wiki/facts-obliteratus.md
---

# 2025-2026 新技术谱系与 README 勘误表

OBLITERATUS 在经典 abliteration（diff-in-means + SVD + 投影）之上实现了 11 项新技术（README L107-124，F-OB-018）。本篇逐项给出"一句话机制 + 解决的问题 + 来源"，全部附源码锚点；随后给出本束最重要的治理产出——**6 处 README 与源码不一致的完整勘误表**（引洞察 4）。

## 十一项新技术

| # | 技术 | 一句话机制 | 解决的问题 | 来源 | 源码锚点 |
|---|------|-----------|-----------|------|---------|
| 1 | 专家粒度消融 EGA | 借 MoE 路由 logits 把拒绝信号分解到 per-expert 分量再分别手术 | dense 式整体投影对 MoE 附带伤害过大——只需要动安全相关的专家 | Novel | `per_expert_directions` 开关，abliterate.py L212/L240/L523 |
| 2 | CoT-Aware 消融 | 对推理关键方向做正交化，只消拒绝方向与推理方向的耦合分量 | 拒绝方向与思维链方向纠缠，朴素消融破坏推理能力 | Novel | `cot_aware`，L538；校正链 L3189-3253 |
| 3 | COSMIC 层选择 | 选取有害/无害表征余弦相似度最低（最可分）的层做手术 | 层选择靠拍脑袋（top-k/middle60）会命中纠缠层 | arXiv:2506.00085，ACL 2025 | COSMIC 融合分支 L2791-2799（日志 "COSMIC="） |
| 4 | 参数化核优化 | 7 个全局参数的钟形层加权曲线，用 Optuna TPE 搜索 | 逐层强度手调不可扩展 | Heretic 启发 | L309/L521（layer_adaptive_strength）与 optimized 预设 |
| 5 | RDO 拒绝方向优化 | 用线性拒绝探针的梯度对 SVD 提取的方向做精炼 | SVD 方向是统计最优不是因果最优 | Wollschlager et al.，ICML 2025 | `rdo_refinement`，L245/L536-537；精炼链 L2928-3012 |
| 6 | 浮点方向插值 | 用高斯形权重对连续 SVD 方向索引插值 | 离散取前 k 个方向在边界处跳变 | Novel | `float_layer_interpolation`，L539；实现 L3057-3084 |
| 7 | KL 散度共优化 | 对照无修改基线测前向序列 token KL，精确回滚破坏性弱信号层直至满足预算 | 消融"过犹不及"缺少自动刹车 | Novel | `use_kl_optimization` + `kl_budget: 0.5`，L216/L244/L489-490 |
| 8 | 组件级缩放 | attention 与 MLP 分别设置投影强度 | MLP 层对消融更敏感，一刀切强度会误伤 | Novel | `layer_adaptive_strength`，L309/L521；强度计算 L3029-3041 |
| 9 | LoRA 可逆消融 | 用 rank-1 LoRA 适配器替代永久权重手术 | 想要"可卸载的消融"——权重投影不可逆 | Novel | lora_ablation.py 文件存在；`use_lora_ablation`，L491 |
| 10 | 激活缩尾 | SVD 前把激活向量截断到分位数区间 | 离群激活主导方向提取 | Heretic 启发 | `winsorize_activations` + `winsorize_percentile: 0.01`，L244-245/L334/L486 |
| 11 | 多方向范数保持 | 投影前一次性捕获全部权重范数，全部方向投影完后统一恢复 | 逐方向恢复范数会反复重引入已删分量 | Novel | 多方向 norm preservation，F-OB-018 |

README "Novel techniques" 表共 11 行（F-OB-018），全部在源码找到开关或文件级锚点。它们与 7 个方法预设的映射关系见[方法预设篇](methods-presets.md)的选型表。

## README 勘误对照表（6 处）

> **方法论警示**（洞察 4）：OBLITERATUS 拥有 1,949 个测试函数与 CI 覆盖率门禁，但 README 仍有 6 处与源码不一致，且漂移方向双向——既有夸大声称也有少报能力。结论：**对安全研究工具，README 不能作为事实来源，逐项源码核验是唯一可信路径**。同一 README 内部自相矛盾（测试数三说）说明这是多入口各自独立衰减，而非整体不可信（15 模块表核验通过即是反例）。

| # | 条目 | README 声称 | 源码实测 | 证据锚点 | F 编号 |
|---|------|------------|---------|---------|--------|
| 1 | 测试规模（三说互异） | 能力对比表 "1,001 tests"（L779）；bibtex note "1,130 mandatory CPU tests"（L873）；Testing 章节 "more than 1,500 tests"（L884） | tests/ 下 **116 个 test_*.py 文件、1,949 个 `def test_` 函数**（2026-09-02 Glob + PowerShell 递归统计） | tests/ 目录；tests/conditional/ 9 个环境绑定文件 | F-OB-012 |
| 2 | 模型预设数 | "116 curated models across 5 tiers"（L494-510） | presets.py 实际登记 **130 个 ModelPreset 条目**（正则 `^    ModelPreset\(` 计数）；5 层级划分与 docstring 一致 | presets.py L3-8、L36 起 | F-OB-013 |
| 3 | nuclear 方法方向数 | 预设表写 "8 (SVD)"（L386） | **n_directions: 4**（L510），描述原文明确写 "Uses 4 SVD directions (not 8) to avoid over-ablation"（L503） | abliterate.py L494-511 | F-OB-014 |
| 4 | study 预设样本数 | layers 150、pruning 200（L742-757） | **layers max_samples=100、pruning max_samples=100**；其余 8 个预设样本数一致 | study_presets.py L35-225 | F-OB-032 |
| 5 | Web UI 顶级 tab 数 | 8 个 tab（L131-142） | app.py 实际 **10 个**：Obliterate、Benchmark（含 Multi-Method/Multi-Model/Quick Presets 三子 tab）、Chat、A/B Compare、Strength Sweep、Tourney、Export、Push to Hub、Leaderboard、About——README 未列 Tourney 与 Push to Hub | app.py Grep `gr.Tab(`（L4806-L5889） | F-OB-034 |
| 6 | ANALYZE 阶段分析模块数 | "The ANALYZE stage runs 4 analysis modules"（L470），AUTO-CONFIG 表列 4 行 | `_analyze()` 实际按序调用 **5 个**（alignment imprint、cone geometry、cross-layer、defense robustness、sparse surgery/RSI）；docstring 映射表亦列 5 行 | informed_pipeline.py L25-29、L326-360 | F-OB-050 |

### 漂移的方向性解读

6 处勘误中：#3 nuclear 方向数是**夸大**（README 称 8 实为 4——把保守设计说成激进配置）；#1 测试数既有夸大也有保守（1,001 < 1,130 < 1,500+ < 实测 1,949，三个数字全部偏低但互不相同）；#2 模型数、#5 tab 数是**保守**（实际能力比声称多）；#4、#6 直接影响复现（study 样本数影响实验规模，ANALYZE 模块数影响闭环配置逻辑的理解）。漂移方向不一致意味着**不存在"往少里信"或"往多里防"的简单修正策略**——唯一可靠的做法是每条关键断言带源码锚点（文件:行号），并区分【已核验】/ [README-only] /【不一致】三档标注。

### 对同类工具评估的核验方法示范

1. **计数类声称**（模块数、模型数、测试数、tab 数）：用结构化枚举代替阅读——`__all__` 长度、正则计数、Grep 匹配数、目录文件数；
2. **配置类声称**（方向数、样本数、默认值）：直接读源码常量定义（`METHODS` 字典、`StudyPreset` 字段、argparse default）；
3. **流程类声称**（阶段数、调用顺序）：读编排函数（`run_informed`、`_analyze`）与 docstring 映射表交叉验证；
4. **基准类声称**（耗时、加速比）：README 基准数据无源码内数据文件可核验的，标注 [README-only] 待复现（本束中 F-OB-022/025/031/036/038 即此档）。

## 延伸阅读

- 技术在方法预设中的开关组合：[methods-presets.md](methods-presets.md)
- ANALYZE 5 模块闭环详解：[analysis-modules.md](analysis-modules.md)
- 层选择策略与后处理链的函数锚点：[pipeline-six-stages.md](pipeline-six-stages.md)
