---
okf_version: '0.2'
type: index
bundle: obliteratus
version: 0.1.0
description: >-
  OBLITERATUS 是当前最先进的开源 abliteration 研究工具包，对大语言模型实施
  权重级拒绝行为移除。本束覆盖六/七阶段流水线、7 方法预设、15 分析模块、
  19 个 CLI 子命令、130 个模型预设、双干预范式、多 GPU 与 SSH 远程执行、
  遥测生态与双许可治理，全部关键事实经源码核验并标注 F-OB 编号。
concepts:
  - abliteration-primer: abliteration 原理入门（refusal direction、SVD、白化、权重投影）
  - pipeline-six-stages: 六/七阶段流水线与阶段源码映射
  - methods-presets: 7 方法预设与双干预范式
  - analysis-modules: 15 分析模块全景与 informed 闭环
  - novel-techniques: 2025-2026 新技术谱系与 README 勘误表
  - scaling-deployment: 多 GPU、量化、SSH 远程与部署形态
  - research-ecosystem: 遥测生态、学术谱系与许可治理
references:
  - architecture-map: 包结构模块树、凭据体系与部署资产
examples:
  - cli-quickstart: CLI 实战全流程
  - python-api: Python API 实战与 YAML study
---

# OBLITERATUS：分析驱动的 abliteration 研究工具包

OBLITERATUS 自述为"understanding and removing refusal behaviors from large language models"的开源工具包（F-OB-001）：实现 abliteration——在不重训练、不微调的前提下，识别并外科手术式移除大语言模型中负责内容拒绝的内部表征。它同时是一个分布式研究实验：遥测开启时，每次运行向社区数据集贡献匿名基准数据（拒绝方向几何、跨层对齐签名、硬件性能档案、方法有效性评分）（F-OB-002）。

从 AI 安全研究视角看，OBLITERATUS 证明了一个关键事实：**安全边界是分层的**。全部提示级防线（安全段落、防注入枚举、拒绝策略）都作用在对话层，而对权重做拒绝方向投影可以永久移除拒绝行为，且无需任何对话交互（洞察 2）。开源权重一旦发布，提示层对齐对权重修改者不构成约束——防御重心必须前移到权重来源可信与分发审计。这是本束的核心阅读视角。

## 快速导航

### 核心概念
- [abliteration 原理入门](concepts/abliteration-primer.md) — refusal direction、diff-in-means、SVD、白化、权重投影数学直觉
- [六/七阶段流水线](concepts/pipeline-six-stages.md) — SUMMON 到 REBIRTH 逐阶段详解与源码函数映射
- [方法预设与双干预范式](concepts/methods-presets.md) — 7 预设适用场景；永久权重投影 vs 可逆 steering vectors
- [15 分析模块全景](concepts/analysis-modules.md) — 模块表、informed 闭环检测→配置映射
- [新技术谱系与勘误表](concepts/novel-techniques.md) — EGA、COSMIC、RDO 等 11 项；6 处 README 勘误
- [扩展与部署](concepts/scaling-deployment.md) — 多 GPU 本质、量化、SSH 远程、部署形态
- [研究生态与治理](concepts/research-ecosystem.md) — 遥测边界、贡献机制、学术谱系、双许可、测试治理

### 示例
- [CLI 实战](examples/cli-quickstart.md) — 安装、探索、单命令消融、参数全集、YAML study、aggregate
- [Python API 实战](examples/python-api.md) — AbliterationPipeline、InformedAbliterationPipeline、steering vectors

### 参考
- [架构地图](references/architecture-map.md) — 包结构模块树、凭据六级解析、部署资产

## 能力速览

| 维度 | 数值 | 说明 |
|------|------|------|
| 方法预设 | 7 个（README 表） | 源码实际更大：CLI `--method` 10 个 choices，docstring 列 14 方法（F-OB-015） |
| 分析模块 | 15 核心模块 | `analysis/__init__.py` 实际导出 30 个（15 核心 + 15 扩展）（F-OB-017） |
| CLI 子命令 | 19 个（含 1 隐藏别名） | `cli.py` 核验；`abliterate` 为向后兼容别名（F-OB-041） |
| 模型预设 | 130 个（源码实测） | README 称 116——勘误项，见新技术篇勘误表（F-OB-013） |
| 测试规模 | 116 文件 / 1,949 个测试函数（实测） | README 三处声称 1,001/1,130/1,500+ 互异——勘误项（F-OB-012） |
| 流水线阶段 | 6（标准）/ 7（informed） | ANALYZE 插入在 PROBE 与 DISTILL 之间（F-OB-006/007） |
| 版本与语言 | v0.1.3；Python >=3.10 | pyproject.toml 核验（F-OB-051） |
| 许可 | AGPL-3.0-or-later + 商业双许可 | MongoDB/Qt/Grafana 同类模式（F-OB-005） |

## 研究用途限定声明

OBLITERATUS 是公开的 AI 对齐研究工具，上游自带 Research Purpose & Responsible Use 章节（F-OB-003）。本束如实呈现其研究定位，阅读与引用本束时须知：

- **目标用户**（上游定义，F-OB-003）：alignment researchers（研究拒绝表征在 transformer 激活空间的几何结构）、red-teamers（评估后训练安全对权重级干预的鲁棒性）、AI safety evaluators（需要无限制基线做基准测试）、local-first practitioners（在自有硬件上对模型保有完全控制权）。
- **明确的排除项**（上游定义，F-OB-003）：不面向试图生成对真实人群造成现实伤害内容的使用者，不面向缺乏负责任使用无审查模型技术能力的人。
- **免责声明要点**（F-OB-004）：仅限研究、red-teaming、安全评估、机制可解释性、本地实验；用户对产出模型及其生成内容负全责；不得用于骚扰、欺诈、未成年人剥削等；软件无保修；作者不对产出负责。
- **防御视角的正确用法**：本束内容用于理解权重级干预面的威胁模型、评估自有模型与权重的分发风险、设计面向供应链的安全控制，而非用于规避他人部署系统的安全机制。

## 信任声明块

- **源码位置**：`d:\spaces\SpecWeave\external\dao\action\elder-plinius\OBLITERATUS\`（GitHub 公开仓库 elder-plinius/OBLITERATUS 的本地克隆，v0.1.3，快照 git HEAD `e39f908832405ccad89cb2a5111e7c2576741d94`）。
- **生成时间**：2026-09-02。
- **维护者**：OKF Wiki Bot。
- **事实标准**：本束全部数字与行为断言**以源码实测为准**，关键论断标注 F-OB-xxx 编号（对应本地事实清单 `.trae/specs/create-ai-security-okf-wiki/facts-obliteratus.md`，66 条，其中约 50 条含源码路径/行号证据）。README 声称项均经源码二次核验，无法核验者标注 [README-only]，与源码不一致者列为勘误。
- **勘误**：README 与源码存在 6 处已核验不一致（测试规模三说、模型预设 116 vs 130、nuclear 方向数 8 vs 4、study 样本数、UI tab 数、ANALYZE 模块数），完整对照见 [新技术谱系与勘误表](concepts/novel-techniques.md)；ANALYZE 阶段模块数勘误另见 [分析模块全景](concepts/analysis-modules.md)。

## 上游与同域工件

- 上游仓库：<https://github.com/elder-plinius/OBLITERATUS>（HuggingFace Space：<https://huggingface.co/spaces/pliny-the-prompter/obliteratus>）
- 学术引用网络与基准工件：Arditi et al. 2024、HarmBench、JailbreakBench、Anthropic hh-rlhf、FailSpy/abliterator 等（F-OB-009/010），详见[研究生态篇](concepts/research-ecosystem.md)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/abliteration-primer.md
concepts/pipeline-six-stages.md
concepts/methods-presets.md
concepts/analysis-modules.md
concepts/novel-techniques.md
concepts/scaling-deployment.md
concepts/research-ecosystem.md
examples/cli-quickstart.md
examples/python-api.md
references/architecture-map.md
```
