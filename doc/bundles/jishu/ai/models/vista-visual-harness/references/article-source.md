---
type: reference
title: "VISTA 博文事实清单（F 编号登记）"
description: "量子位《何恺明团队发布多模态Harness框架》事实登记表——F-001~F-044 为博文事实，F-045~F-076 为权威核验补充事实。"
tags: [vista, fact-registry, wechat, arxiv, harness, multimodal]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-04-20
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/3S5OW6ytgz27zrq4UgCkgQ"
    title: "何恺明团队发布多模态Harness框架"
  - id: arxiv
    url: "https://arxiv.org/abs/2610.02200"
    title: "VISTA: A Visual Harness for Reasoning in an Interactive World"
  - id: arxiv-html
    url: "https://arxiv.org/html/2610.02200v1"
    title: "VISTA 论文全文（HTML）"
  - id: project
    url: "https://vista-research.github.io/"
    title: "VISTA 项目页（2026-08-05 blogpost 版本）"
  - id: github
    url: "https://github.com/joshhhhhan/VISTA"
    title: "VISTA 代码仓库（MIT License）"
  - id: arc-methodology
    url: "https://docs.arcprize.org/methodology"
    title: "ARC Prize 官方评测方法学（RHAE 定义）"
  - id: arc-agi3-paper
    url: "https://arxiv.org/abs/2603.24621"
    title: "ARC-AGI-3 技术报告（数据集构成）"
  - id: anthropic-harness
    url: "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"
    title: "Effective harnesses for long-running agents（2025-11-26）"
---

# VISTA 博文事实清单（F 编号登记）

> 本表与 Spec `facts.md` 的 F 编号集合**逐条对应**（V 阶段机械比对项）。F-001~F-044 为博文事实，F-045~F-076 为权威核验补充事实。
> 核验级别：P0=必核验；P1=选核验；P2=可单源（作者观点）。标注"作者观点"者仅代表博文叙述者的判断，不作事实结论使用。

## 一、博文客观事实（F-001 ~ F-044）

| F | 类别 | 声明 | 核验 | 状态 |
|---|------|------|------|------|
| F-001 | 事件 | 何恺明团队在论文《VISTA: A Visual Harness for Reasoning in an Interactive World》中提出一套视觉原生的 Harness——VISTA | P0 | ✅ 与 F-045/F-046 一致 |
| F-002 | 能力 | VISTA 让现有多模态模型直接观察环境、保存原始画面，并在推理时随时回看、放大和检查细节，无需从头训练 | P0 | ✅ 与 F-060/F-054 一致 |
| F-003 | 对比 | 相比传统将环境抽象成文字或代码的做法，VISTA 保留原始的视觉信息 | P0 | ✅ 对应 F-061/F-003 的对比面 |
| F-004 | 机制 | 模型可根据眼下的问题，将过去看过的画面重新调入上下文，参与当前的判断与推理 | P0 | ✅ 对应 F-051/F-052 |
| F-005 | 概念 | 视觉经验成为模型随时调用、反复检查的上下文，多模态模型有了围绕视觉记忆搭建的原生脚手架 | P1 | ✅ 对应 F-059 |
| F-006 | 数字 | 搭配 VISTA，Claude Opus 5.0 完成 ARC-AGI-3 全部 25 个公开游戏，相对人类动作效率得分达到满分 100 | P0 | ✅ 对应 F-047/F-074 |
| F-007 | 数字 | 所用游戏动作数比首次游玩的人类基线少 57.4% | P0 | ✅ 对应 F-048 |
| F-008 | 数字 | 换成 GPT-5.6 Sol，同样全部通关，得分达到 99 | P0 | ✅ 对应 F-049 |
| F-009 | 事件 | 团队还在浏览器游戏、迷宫和连线题中验证了这套方法 | P0 | ✅ 对应 F-056/F-057/F-058 |
| F-010 | 计划 | 团队将更接近物理世界的具身任务列为后续研究方向 | P0 | ✅ 对应 F-069 |
| F-011 | 背景 | 去年 11 月，Anthropic 曾以长时间编程任务为例，介绍 Harness 如何帮助模型跨越多个上下文窗口、持续推进任务 | P0 | ⚠️ 对应 F-072（事实成立），但论文未引用（E-2） |
| F-012 | 机制 | 该 Harness 通过任务清单记录尚未完成的事项，通过进度文件和代码记录保存已经完成的工作 | P0 | ✅ 对应 F-072 |
| F-013 | 观点 | 主要通过文字和代码保存任务状态的 Harness，在一定程度上推动了这一波 Agent 能力的爆发（作者观点） | P2 | 单源（博主判断） |
| F-014 | 问题 | 在真实环境里光有文字记忆不够——模型不仅要记住物体的位置、朝向，还要理解每次动作前后环境究竟发生了哪些变化 | P1 | ✅ 与 F-061/F-062 呼应 |
| F-015 | 问题 | 模型第一次看到一张图时，未必知道哪个细节会在后面变得重要 | P1 | ✅ 与 F-062 呼应 |
| F-016 | 问题 | 视觉信息很难提前用一份文字笔记完整记录下来，更难保证后续执行任务时记录的信息依然够用 | P1 | ✅ 与 F-061/F-062 呼应 |
| F-017 | 做法 | 在 ARC-AGI-3 这类基准中，已有思路是先把画面转换成由数字组成的文本网格，再让模型编写程序模拟环境规则、验证行动方案 | P0 | ✅ 对应 F-061 |
| F-018 | 问题 | 环境越复杂越难被完整转化成文字和代码；交互历史变长后早期画面会被逐渐移出上下文或被文字摘要替代 | P0 | ✅ 对应 F-062 |
| F-019 | 问题 | 研究问题：如何在不额外训练基础模型的情况下，让智能体在推理需要时重新检查过去看到的视觉信息 | P0 | ✅ 对应 F-060/F-054 |
| F-020 | 机制 | VISTA 把环境返回的每一帧原样存到上下文之外，包括动作过程中的动画中间帧，模型需要时再取回来 | P0 | ✅ 对应 F-051 |
| F-021 | 机制 | 在 ARC-AGI-3 评测中，它既能比较不同时刻的画面，也能放大局部，检查小方块上的朝向标记 | P0 | ✅ 对应 F-052 |
| F-022 | 概念 | 文字笔记记录模型当前的理解，原始画面保留供它重新判断的证据 | P0 | ✅ 对应 F-051/F-053 |
| F-023 | 概念 | 研究将这种机制称为对交互历史的显式注意力——模型根据正在思考的问题，选择哪些视觉信息重新进入上下文 | P0 | ✅ 对应 F-059 |
| F-024 | 组件 | VISTA 设计三个核心组件：视觉观测、无损视觉记忆、主动视觉检查 | P0 | ⚠️ 对应 F-050（第三组件论文原词为 visual inspection，见 E-1） |
| F-025 | 数字 | 视觉观测：在 ARC-AGI-3 实验中，VISTA 会将官方提供的 64×64 画面放大为 512×512 的 PNG 图像，保留颜色、外观和空间关系 | P0 | ✅ 对应 F-055 |
| F-026 | 机制 | 无损视觉记忆：每次执行动作后完整保存所有画面（含动画中间帧），按回合号和帧号建立索引 | P0 | ✅ 对应 F-051 |
| F-027 | 能力 | 主动视觉检查：通过 inspect 工具指定历史回合调出画面、裁剪放大局部检查细节；可一次调出多帧对比动作前后变化 | P0 | ✅ 对应 F-052 |
| F-028 | 机制 | 每回合先观察当前画面和可用动作，结合经验判断状态并提出行动假设；信息不足则调用工具回看历史、放大局部、甚至读取具体像素 | P0 | ✅ 对应 F-052 |
| F-029 | 机制 | 找到证据后不直接行动，而是先预测操作可能带来的变化；动作执行后对比实际结果与预测，修正对游戏规则的理解 | P0 | ✅ 与论文执行流程一致 |
| F-030 | 机制 | 两份文字笔记：GUIDE.md 记录跨关卡可复用的规则和经验；WORKING.md 记录当前关卡的状态、进度和后续计划 | P0 | ✅ 对应 F-053 |
| F-031 | 机制 | 上下文接近上限时先整理交接摘要再进入新窗口；此前文字笔记、动作历史和视觉档案都会保留 | P0 | ✅ 与 F-070 一致 |
| F-032 | 机制 | 完整方案中每次动作后默认只展示最后一帧；中间画面统一存入视觉档案，按需主动调取 | P0 | ✅ 对应 F-070 |
| F-033 | 观点 | 既保留完整视觉信息，又避免大量历史图片持续占用上下文空间（作者观点） | P2 | 单源（博主判断） |
| F-034 | 观点 | VISTA 没有为此额外训练新模型：环境理解、行动规划与推理仍由现成多模态模型完成，Harness 负责执行工具调用、保存视觉历史、按需提供证据 | P1 | ✅ 对应 F-054 |
| F-035 | 观点 | VISTA 改变的不是模型本身，而是模型获取、保存和使用视觉信息的方式 | P1 | ✅ 与 F-054 一致 |
| F-036 | 数字 | GameWorld：相同 GPT-5.6 Sol 模型，相比官方基础框架，170 项任务成功率从 40.0% 提高到 63.3% | P0 | ✅ 对应 F-056 |
| F-037 | 数字 | AI GameStore：10 个游戏中综合得分从 47.3 升至 140.3，人类中位数归一化为 100 | P0 | ✅ 对应 F-057 |
| F-038 | 数字 | BabyVision：选取的 39 道迷宫与连线题上，准确率从 41.0% 提高到 63.2% | P0 | ⚠️ 对应 F-058（39 为评估子集，全集 388 项，见 E-6） |
| F-039 | 观点 | BabyVision 只有静态图片，模型也能通过放大局部、检查像素改善判断 | P1 | ✅ 对应 F-052/F-058 |
| F-040 | 观点 | 同一套 VISTA 框架只需少量适配，就能用于不同的游戏与谜题 | P1 | ⚠️ 证据强度见洞察 5 |
| F-041 | 观点 | 保存原始画面、让模型按需回看，可以进一步发挥现有多模态模型的能力 | P2 | 单源（博主判断） |
| F-042 | 名单 | 论文三位共同第一作者为 Qiushi Han、胡珂雅（Keya Hu）、Linlu Qiu，另两位为 Cathy Wu 和何恺明 | P0 | ✅ 对应 F-046 |
| F-043 | 名单 | Qiushi Han（Josh Han）现为 MIT 运筹研究中心博士生，导师为 Cathy Wu | P1 | ✅ MIT ORC 名录（登记名 Josh Han） |
| F-044 | 名单 | Keya Hu 现为 MIT 电气工程与计算机科学系博士生，由何恺明和 Jacob Andreas 联合指导，本科毕业于上海交通大学 ACM 班 | P1 | ✅ 作者个人主页 + MIT CSAIL 名录 |

## 二、权威核验补充事实（F-045 ~ F-076）

| F | 类别 | 声明 | 来源 | 核验 |
|---|------|------|------|------|
| F-045 | 事实 | 论文 arXiv:2610.02200 于 2026-10-01 17:59:45 UTC 提交（v1），分类 cs.AI / cs.CV，类型 Tech report，许可 CC BY 4.0 | arXiv abs 页 | ✅ |
| F-046 | 名单 | 作者为 Qiushi Han、Keya Hu、Linlu Qiu、Cathy Wu、Kaiming He，机构 MIT；论文脚注标注前三位为共同第一作者（*Co-first authors*），项目页渲染为 *co-leads* | arXiv abs + 项目页 | ✅ |
| F-047 | 数字 | 论文摘要给出 ARC-AGI-3 结果：Claude Opus 5.0 的 RHAE 从 40.68 提升到 100.00，完成全部 25 个公开游戏，动作数比首次游玩的人类参与者少 57.4% | arXiv 摘要 + §4.2 + 表1/表2 | ✅ |
| F-048 | 数字 | §4.2 动作数口径：VISTA 共用 7,302 个动作，比人类参考的 17,135 个动作少 57.4% | arXiv §4.2 + 表2 | ✅ |
| F-049 | 数字 | GPT-5.6 Sol 同样完成全部 25 个游戏，RHAE 得分 99.00（最大推理强度） | arXiv §1 + 表1 + 表2 题注 | ✅ |
| F-050 | 组件 | §3.1 三组件官方名称：visual observations、lossless visual memory、visual inspection；图 3c 标注 model-directed visual inspection | arXiv §3.1 + 图3 | ✅ |
| F-051 | 机制 | 无损视觉记忆保存环境返回的每一帧（含中间动画帧）原始形式，每帧按回合号与帧号索引，独立于当前上下文保留而始终可用 | arXiv §3.1 + §1 | ✅ |
| F-052 | 机制 | 视觉检查：时间维度可取任意早期回合多帧以比较状态、重放动作中间动画帧；空间维度可请求任意矩形区域放大视图；另有 read_pixels 返回精确 RGB 值 | arXiv §3.1 + 附录 A.4 算法1 | ✅ |
| F-053 | 机制 | §3.2：GUIDE.md 记录对游戏的理解及跨关卡仍有用的信息，WORKING.md 为当前状态草稿本；A.2 补充 GUIDE.md 存跨关卡与跨会话可复用知识，WORKING.md 存当前关卡临时状态与计划 | arXiv §3.2 + 附录 A.2 | ✅ |
| F-054 | 机制 | §3.2：Harness 是纯机械的，不涉及任何被训练的模型——只执行模型请求的工具调用、返回图像或像素值、对无效请求报错 | arXiv §3.2 | ✅ |
| F-055 | 数字 | §4.3 消融默认值：Agent 接收 512×512 PNG 图像，由官方 64×64 帧 8× 最近邻放大得到 | arXiv §4.3 + 图7b | ✅ |
| F-056 | 数字 | GameWorld 含 34 个浏览器游戏、跨 5 类题材共 170 项任务；VISTA 成功率 63.3%，官方实现 40.0%，新玩家 55.3%，此前最好 20.0% | arXiv §5.1 + §5.2 + 图11 | ✅ |
| F-057 | 数字 | AI GameStore 含 10 个公开浏览器游戏；逐游戏按公开人类中位数归一化为 100 后取几何平均，VISTA 140.3，官方实现 47.3，此前最好 9.0 | arXiv §5.1 + 附录 A.3 + 图11 | ✅ |
| F-058 | 数字 | BabyVision 中评估 39 题（20 迷宫 + 19 连线），准确率 41.0%→63.2%，新玩家 92.3%，此前最好 25.7%；全集为 388 项任务、22 个子类 | arXiv §5.1 + §5.2 + 附录 A.6 + 图11 | ✅ |
| F-059 | 概念 | §3.1/§4.4 使用 "explicit attention mechanism over the interaction history"，§4.4 称其为 re-attention mechanism | arXiv §3.1 + §4.4 | ✅ |
| F-060 | 概念 | 摘要称 VISTA "gives a general-purpose multimodal model long-horizon vision" | arXiv 摘要 | ✅ |
| F-061 | 问题 | §4.2/§4.3：ARC-AGI-3 既有做法通常把每帧表示为文本网格、以整数颜色索引逐行编码，并常用基于代码的世界模型 | arXiv §4.2 + §4.3 | ✅ |
| F-062 | 问题 | §1/§3：随上下文填满，早期观察可能被移出上下文或被文字摘要替代 | arXiv §1 + §3 | ✅ |
| F-063 | 数字 | §4.1 两个闭源多模态后端：Claude Opus 5.0（Claude Code CLI，extra-high 推理强度）与 GPT-5.6 Sol（Codex CLI，max 推理强度）；§4.3 另用开源权重 GLM-5.3 Flash 320B（RHAE 66.93） | arXiv §4.1 + §4.3 + 附录 A.1 | ✅ |
| F-064 | 数字 | §4.2：VISTA 7,302 动作 vs 人类参考 17,135；官方实现（GPT-5.6 Sol）RHAE 13.33、共 10,619 个动作 | arXiv §4.2 + 附录 A.1 | ✅ |
| F-065 | 数字 | §4.3 消融阶梯（累积组件后 RHAE）：13.33 → 47.32 → 51.66 → 65.82 → 70.05 → 94.10 → 99.00 | arXiv §4.3 | ✅ |
| F-066 | 数字 | 另有 3D 重渲染变体：ARC-AGI-3 上 RHAE 84.12，用 20,640 个动作 | arXiv §4.3/§4.4 | ✅ |
| F-067 | 数字 | 附录 B.1 多次运行波动：ARC-AGI-3 Sol 99.00/98.90/99.23（99.04±0.17）；GameWorld 成功率 63.33±2.37%、进度 79.30±2.14%；BabyVision 准确率 63.23±3.00% | arXiv 附录 B.1 | ✅ |
| F-068 | 观点 | §6 局限：所用模型在公开基准之后发布，无法排除游戏已被纳入训练数据；需在私有集等新游戏上评估才是更强泛化检验 | arXiv §6 | ✅ |
| F-069 | 计划 | §7：未来工作可在更逼真的任务上评估，例如更接近物理世界的具身任务 | arXiv §7 | ✅ |
| F-070 | 事实 | §3.1 明确只有三组件，无独立的"显式注意力"组件；§3.2 默认每次动作后只呈现最后一帧，中间帧全部归档 | arXiv §3.1 + §3.2 + 附录 A.2/A.4 | ✅ |
| F-071 | 事实 | 论文 64 条参考文献中唯一 Anthropic 出处是「Introducing Claude Opus 5」模型公告，未引用任何 Anthropic harness 博文 | arXiv 参考文献列表 | ✅ |
| F-072 | 事实 | Anthropic《Effective harnesses for long-running agents》发布于 2025-11-26，含 feature_list.json 特性清单、claude-progress.txt 进度文件与 git 提交保存已完成工作 | anthropic.com/engineering | ✅ |
| F-073 | 事实 | RHAE 是 ARC-AGI-3 官方指标：单关得分 =（人类基线动作数 / AI 动作数）²，单关上限为人类基线的 1.15 倍，未通关关卡计 0；游戏分为各关得分的加权平均（以关卡序号为权重），总分为各游戏分平均 | docs.arcprize.org/methodology | ✅ |
| F-074 | 数字 | ARC-AGI-3 数据集构成：公开演示集 25、半私有集 55、完全私有集 55；私有集刻意与公开集分布外 | arXiv:2603.24621 表1 + §3.6 | ✅ |
| F-075 | 事实 | 代码已开源：github.com/joshhhhhan/VISTA，MIT License；运行需 Linux x86_64 + Python 3.12 + Docker Engine + Codex CLI 0.145.0 或 Claude Code 2.1.220，批量运行另需 tmux；提供 online / competition / offline 三种操作模式 | GitHub README + pyproject.toml | ✅ |
| F-076 | 事实 | ARC Prize 官方记分卡可独立核验：Opus 5.0 对应 RHAE 100，GPT-5.6 Sol 对应 RHAE 99；三基准出处为 GameWorld(ECCV 2026)、AI GameStore(arXiv:2602.17594)、BabyVision(ICML 2026) | arcprize.org/scorecards + 基准论文 | ✅ |

## 三、关联

- 核验报告与勘误：[verification.md](verification.md)
- 知识地图（机制层与迁移层）：[knowledge-map.md](knowledge-map.md)
- 信源登记与边界：[source-manifest.md](source-manifest.md)
