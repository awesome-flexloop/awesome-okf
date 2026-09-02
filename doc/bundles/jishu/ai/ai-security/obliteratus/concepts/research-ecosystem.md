---
type: concept
title: 研究生态与治理——遥测、贡献、学术谱系与双许可
description: >-
  OBLITERATUS 的社区与研究治理全景：遥测数据边界（收集与不收集字段逐项
  telemetry.py 核对）、排行榜与 aggregate 命令、PR 式本地贡献三 API、
  学术引用网络与基准工件、AGPL-3.0 + 商业双许可治理、CI 风险映射与
  条件测试发布门禁，以及上游免责声明要点。
tags:
  - telemetry
  - community
  - leaderboard
  - dual-license
  - agpl
  - supply-chain
  - governance
sources:
  - https://github.com/elder-plinius/OBLITERATUS
  - .trae/specs/create-ai-security-okf-wiki/facts-obliteratus.md
---

# 研究生态与治理：遥测、贡献、学术谱系与双许可

OBLITERATUS 不只是一个工具，上游将其定位为"分布式研究实验"：遥测开启时每次运行向社区数据集贡献匿名基准数据（F-OB-002）。从生态视角看，elder-plinius 系列仓库构成了"数据-工具-社区"三层结构（洞察 5）：档案仓库提供数据层，OBLITERATUS 提供工具层，遥测机制与社区渠道构成社区层——单人研究者已在机构外复制了准学术研究基础设施（引用规范、基准数据集、可复现流水线、许可治理俱全）。

## 一、社区遥测平台

### 数据边界（telemetry.py 逐项源码核对，F-OB-029/030）

**收集的字段**（BenchmarkRecord dataclass，telemetry.py L326-364）：

| 字段 | 内容 |
|------|------|
| schema_version / timestamp | 遥测 schema 版本 2（L51）、时间戳 |
| session_id | **每次会话随机生成，非按用户**（源码注释 "Random per-session, not per-user"） |
| model_id / model_family / model_size_b / is_moe | 模型名、家族、参数规模、是否 MoE |
| method / n_directions | 方法名与方向数 |
| metrics | 聚合基准分数：refusal_rate、perplexity、coherence、kl_divergence |
| gpu_name / gpu_vram_gb | 硬件信息 |

**明确不收集**：prompts、outputs、IP 地址、用户身份——模块 docstring 原文 "No user identity, IP addresses, or prompt content is stored"（L1-26）。

### 机制与防护

- **默认关闭**：本地需 `OBLITERATUS_TELEMETRY=1` 环境变量或 `enable_telemetry()` 开启；**HF Spaces 上自动开启**（F-OB-030）。
- **双落点**：本地 JSONL（`~/.obliteratus/telemetry.jsonl`）+ 中心 HF Dataset（默认 `pliny-the-prompter/OBLITERATUS-TELEMETRY`，`OBLITERATUS_TELEMETRY_REPO` 可改）。
- **内置脱敏**（源码核验）：token 替换——hf_/ghp_/github_pat_/sk- 前缀令牌替换为占位符（`_sanitize_public_text` L68-79）；敏感键名过滤正则 `authorization|credential|password|secret|token|api_key`（L52-54）；九个公共指标的值域校验（`_PUBLIC_METRIC_RANGES` L55-65，含 refusal_rate/perplexity/coherence/kl_divergence/capability_score 等）——超出公共值域的数值不外发。

**防御视角的提示**（洞察 5 行动项）：OBLITERATUS-TELEMETRY 类社区遥测数据集是潜在的低成本观测源，但存在抽样偏差——自选用户、本地默认关闭、仅 Spaces 自动开启，不能视为无偏样本。

## 二、排行榜与 aggregate

社区运行汇入 HF Space 的 **Leaderboard tab**（app.py L5762，10 个顶级 tab 之一——README 只列 8 个 tab 为勘误项，F-OB-034）：社区聚合的模型/方法/配置排名，可在开工前查最优方法。命令行消费（F-OB-029 相关 README 用法）：

```bash
obliteratus aggregate --format summary                              # 社区发现概览
obliteratus aggregate --format latex --metric refusal_rate --min-runs 3   # 论文级 LaTeX 表
```

## 三、PR 式本地贡献

完全不走遥测的替代路径：结果存 JSON，经 pull request 提交。三个 API 均在 `obliteratus/__init__.py` `__all__` 中导出（F-OB-053），实现于 community.py（save_contribution L83、load_contributions L196、aggregate_results L225）：

```python
from obliteratus import save_contribution, load_contributions, aggregate_results

save_contribution(pipeline, model_name=..., notes="A100, default prompts")
records = load_contributions("community_results")
aggregated = aggregate_results(records)
```

## 四、学术引用网络

README References 章节列出的学术谱系（F-OB-009）：

| 工作 | 内容 | 在 OBLITERATUS 中的体现 |
|------|------|------------------------|
| Arditi et al. 2024（arXiv:2406.11717） | 拒绝由单一方向介导 | basic 预设、ActivationProbe、方向理论基石 |
| Gülmez 2026 Gabliteration（arXiv:2512.18901） | 自适应多方向神经权重修改 | aggressive 预设（Full Gabliteration）、gabliteration 方法 |
| grimjim 2025 | norm-preserving biprojection | advanced 及以上的范数保持双投影 |
| Turner et al. 2023（arXiv:2308.10248） | Activation Addition | steering vectors 工厂 |
| Rimsky et al. 2024（arXiv:2312.06681） | CAA 对比激活加法 | 对比对 steering 构造 |
| Meng et al. 2022（arXiv:2202.05262） | 因果追踪（ROME） | CausalRefusalTracer（近似实现） |
| Alain & Bengio 2017 | 线性探针 | LinearRefusalProbe |
| Elhage et al. 2021 | Transformer Circuits 框架 | ResidualStreamDecomposer |
| Wollschlager et al. 2025（arXiv:2502.17420） | 概念几何 | ConceptConeAnalyzer；其 ICML 2025 工作对应 RDO |

引用的同类研究工件（F-OB-010）：HarmBench（arXiv:2402.04249）、AdvBench（arXiv:2307.15043）、JailbreakBench、Anthropic hh-rlhf、FailSpy/abliterator。官方引用 bibtex（obliteratus2026）的 note 字段写 "15 analysis modules, 1,130 mandatory CPU tests"——后者是勘误项（三说之一，实测 1,949 函数，F-OB-011/012）。项目还自带学术手稿目录 paper/（main.tex、appendix.tex、references.bib）与 Colab notebook（F-OB-040）。

## 五、双许可治理

- **开源侧**：AGPL-3.0-or-later（pyproject.toml L11 源码核验，F-OB-005）。以网络服务（SaaS）运行修改版必须向用户开源同许可。
- **商业侧**：无法满足 AGPL 义务的组织（专有 SaaS、闭源产品、无法披露源码的内部工具）可购买商业许可，经 GitHub Issues 联系。
- 自述与 MongoDB、Qt、Grafana 同类双许可模式（F-OB-005）。
- 治理含义：SaaS 闭源部署路径被 AGPL 条款阻断（这正是 AGPL 的设计目的），商业许可是唯一合规闭源通道；研究使用不受影响。

## 六、供应链与测试治理

F-OB-052/054 源码核验的治理体系：

- **测试规模**：tests/ 实测 116 个 test_*.py 文件、1,949 个 `def test_` 函数（README 三说 1,001/1,130/1,500+ 均为勘误，F-OB-012）；仓库自带合成离线模型 fixture（tiny_offline_model.py）驱动无网络流水线测试。
- **pytest 配置**：`--cov-fail-under=75` 硬门禁（pyproject.toml L103）；11 种 markers（cpu/integration/slow/gpu/mps/mlx/network/download/remote/operator_ui，L108-119）。
- **CI 分层**：快速 PR 门为 Python 3.12 核心 + 风险映射 lane（50% changed-line floor，README 声称）；tagged release 跑全 Python 矩阵，75% statement / 60% branch 覆盖（README 声称部分 [README-only]）；另有 conditional-tests.yml 工作流。
- **条件测试**：9 个环境绑定测试文件（CUDA/MPS/MLX/Jetson/网络服务/模型下载/operator UI/远程执行/external evaluation runtime）走单独的条件工作流，Jetson lane 为可信人工硬件探针（F-OB-052/066）。
- **策略文件**：ci/ 目录含 conditional-test-policy.json、pr-test-policy.json、supply-chain-policy.json、test-quality-policy.json、test-risk-map.json——**测试按风险映射编排**，而非均一跑全量（F-OB-054）。
- **mutmut 变异测试**：仅对数值契约与持久化契约等关键文件做选择性变异（pyproject.toml [tool.mutmut] L121-164）——数值正确性（投影数学、白化 SVD）被单独加固。
- **发布流程**：PR 接受与发布走独立的 exact-SHA 绑定门禁（docs/RELEASE_PROCESS.md；不可变失败 tag、exact-tag 认证、source-only snapshot 策略）。

## 七、上游免责声明要点

使用/引用本束内容前须知（F-OB-003/004，上游 Research Purpose & Responsible Use 与 Disclaimer 章节）：

1. 上游定位为对齐研究工具，四类目标用户为 alignment researchers、red-teamers、AI safety evaluators、local-first practitioners；明确排除以生成现实伤害内容为目的的使用。
2. 仅限研究、red-teaming、安全评估、机制可解释性、本地实验；产出模型的安全护栏已被外科手术移除，**用户对产出模型及其全部生成内容负全责**。
3. 不得用于骚扰、欺诈、非自愿亲密影像、未成年人剥削等。
4. 软件按"as-is"提供，无保修；作者与贡献者不对修改模型的产出或下游使用负责。
5. 上游自辩逻辑：发布对齐研究工具与对抗评估框架是 AI 安全社区的标准实践，同类公开工件包括 HarmBench、AdvBench、JailbreakBench、Anthropic 红队数据集与 abliterator。

## 延伸阅读

- 三层生态地图与可信度分级的跨仓库视角：见 elder-plinius 系列束总览（cl4r1t4s / l1b3rt4s 束）
- 遥测命令行开关实操：[cli-quickstart.md](../examples/cli-quickstart.md)
- 架构与凭据体系：[architecture-map.md](../references/architecture-map.md)
