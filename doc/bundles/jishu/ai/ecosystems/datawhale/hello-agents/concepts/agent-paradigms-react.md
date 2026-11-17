---
title: 智能体范式与ReAct
type: concept
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/multi-agent-collaboration
  - /datawhale/hello-agents/concepts/agent-framework-development
  - /datawhale/hello-agents/references/chapter04-classic-paradigms
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/第四章%20智能体经典范式构建.md
  - https://arxiv.org/abs/2210.03629
  - https://react-lm.github.io/
---

# 智能体范式与ReAct

智能体范式（Agent Paradigm）是组织 LLM「思考」与「行动」过程的架构模式。Hello-Agents 教程重点实现了三种最具代表性的经典范式：**ReAct**、**Plan-and-Solve** 和 **Reflection**。这一篇以 ReAct 为主，先把论文里的原始定义、实验与失败模式讲清，再看它如何落到今天的工程实现。

## ReAct：推理与行动协同

ReAct（Reasoning and Acting）由 Shunyu Yao 等七位作者提出，论文 [arXiv:2210.03629](https://arxiv.org/abs/2210.03629) 于 2022 年 10 月首次提交，2023 年 3 月以 ICLR 相机就绪版更新。它的核心主张是：**让语言模型把推理轨迹（reasoning traces）与任务动作（task-specific actions）交错生成**，而不是把「推理」和「行动」当成两条互不相干的研究线（Yao et al., 2023）。

### 它要解决的两个极端

| 路线 | 代表方法 | 强项 | 结构性缺陷 |
|------|----------|------|------------|
| 纯推理 | Chain-of-Thought（CoT） | 多步分解、逻辑连贯 | 不接触外部世界，事实容易编造，错误会沿推理链传播 |
| 纯行动 | Act-only、WebGPT、SayCan | 能调用工具、能改变环境 | 缺少显式规划，遇到异常不会调整，难以解释为什么点这一步 |

ReAct 的判断是：**推理让行动有目的，行动让推理有事实依据**。两者交错，才同时拿到「可解释」与「可纠错」。

### 轨迹长什么样

一条 ReAct 轨迹由三类片段交替组成：

```text
Thought 1: 我需要先查这两个人物的出生地
Action 1: search[周杰伦]
Observation 1: 周杰伦，1979 年 1 月 18 日出生于台湾省新北市
Thought 2: 还需要另一个人的信息
Action 2: search[费玉清]
Observation 2: 费玉清，1955 年 7 月 17 日出生于台湾省台北市
Thought 3: 两人的出生地都查到了，可以回答
Action 3: finish[周杰伦出生于新北市，费玉清出生于台北市]
```

三个要点：

1. **Thought 不是装饰**：它承担拆解目标、决定下一步查什么、判断观察是否足够、发现异常并换策略。
2. **Action 是任务特定的**：问答任务的动作空间通常是 `search[entity]`、`lookup[string]`、`finish[answer]`；ALFWorld 是文本家务动作；WebShop 是 `search[...]` 与 `click[...]`。动作空间由环境定义，不是模型自由发挥。
3. **Observation 来自环境**：它不是模型生成的，而是工具或环境返回的真实结果；这一条是 ReAct 与 CoT 的分水岭。

### 形式化与算法

把环境记为 $\mathcal{E}$，动作空间记为 $\mathcal{A}$，模型策略记为 $\pi$。在第 $t$ 步：

```text
a_t, thought_t ~ π(· | 问题, 示例轨迹, thought_1, a_1, o_1, ..., o_{t-1})
o_t = E(a_t)
```

当 $a_t = \text{finish}$ 或达到步数上限时停止。论文用**少样本提示**实现 $\pi$：提示里放若干条人工写的完整轨迹（含 Thought/Action/Observation），模型照格式续写；解码用贪心。决策任务只给 1–2 个示例，问答任务给更多示例。

```python
# 最小骨架：论文式文本协议
context = few_shot_examples + [f"Question: {question}"]
for step in range(max_steps):
    text = llm(context)                 # 生成 "Thought: ...\nAction: ..."
    thought, action = parse(text)
    if action.name == "finish":
        return action.arg
    observation = environment.step(action)   # 真实工具返回
    context += [text, f"Observation: {observation}"]
return fallback_or_give_up()
```

这段骨架只有二十来行，但已经包含 ReAct 的四个关键部件：**提示格式、动作解析、环境执行、轨迹回填**。工程实现的大部分复杂度，都在「解析失败怎么办、动作不合法怎么办、循环停不下来怎么办」。

## 论文实验：ReAct 到底赢在哪

论文在四类任务上做少样本实验，主干模型为 PaLM-540B。下表是问答与事实验证的结果（HotpotQA 用 EM，FEVER 用准确率）：

| 方法 | HotpotQA EM | FEVER Acc |
|------|-------------|-----------|
| Standard prompting | 28.7 | 57.1 |
| CoT（纯推理） | 29.4 | 56.3 |
| CoT-SC（21 采样多数投票） | 33.4 | 60.4 |
| Act（纯行动） | 25.7 | 58.9 |
| **ReAct** | **27.4** | **60.9** |
| CoT-SC → ReAct（先投票再行动） | 34.2 | **64.6** |
| ReAct → CoT-SC（先行动再投票） | **35.1** | 62.0 |
| 监督学习 SOTA | 67.5 | 89.5 |

两个容易误读的点：

- **ReAct 单独使用并不全面碾压 CoT-SC**：HotpotQA 上 27.4 低于 CoT-SC 的 33.4；它的优势在 FEVER 与「可解释、可纠错」。
- **组合往往比单用更好**：先让 CoT-SC 投票、失败再退回 ReAct，或先 ReAct 再 CoT-SC 兜底，两个方向都能把数字往上推。这说明 ReAct 不是替代品，而是**可与推理集成互补的一种执行结构**。

在交互决策任务上，论文报告的优势更明显：

| 任务 | 指标 | Act | ReAct | 说明 |
|------|------|-----|-------|------|
| ALFWorld | 成功率 | 45%（最佳 trial） | **71%（最佳 trial）** | ReAct 最差 trial 也有 48%，仍高于 Act 最佳 |
| WebShop | 分数 / 成功率 | 62.3 / 30.1 | **66.6 / 40.0** | 相对 IL、IL+RL 也有提升；人类为 82.1 / 59.6 |

论文摘要给出的概括是：在 ALFWorld 与 WebShop 上，ReAct 相对模仿学习与强化学习方法分别取得 **34% 与 10% 的绝对成功率提升**，而提示里只有一两个示例。

> **数字使用警告**：以上是 PaLM-540B、特定提示与贪心解码下的少样本结果，换模型、换示例、换工具都会变。它们适合用来说明「机制为什么有效」，不适合当作你手上模型的效果承诺。

### 消融：去掉任何一半都会退化

论文的消融给出三条稳定结论：

1. **去掉 Thought，只剩 Action**：模型仍能调用工具，但不会拆解、不会纠错，复杂任务成功率明显下降。
2. **去掉 Action，只剩 Thought**：退化为 CoT，事实幻觉与错误传播回来；FEVER 上的假阳性率明显更高。
3. **两者都在，但组合方式不同**：CoT-SC 与 ReAct 的两种串接都能提升，说明「内部推理」与「外部取证」是互补信息源，而不是谁替代谁。

## 失败模式：ReAct 不是万能药

论文对 HotpotQA 的轨迹做了人工归因。下表是 ReAct 与 CoT 的成功/失败构成（百分比为被分析轨迹中的占比）：

| 类型 | 定义 | ReAct | CoT |
|------|------|-------|-----|
| 真阳性 | 推理与事实都正确 | 94% | 86% |
| 假阳性 | 推理或事实被编造 | **6%** | **14%** |
| 推理错误 | 推理链错，含陷入重复步骤 | **47%** | 16% |
| 搜索结果错误 | 检索为空或不含有用信息 | 23% | — |
| 幻觉 | 编造推理或事实 | **0%** | **56%** |
| 标签歧义 | 预测对但未精确匹配标签 | 29% | 28% |

读法：

- ReAct 把「幻觉」压到 0%（在这批样本里），代价是**推理错误升到 47%**，其中大量是重复同一 Thought/Action 的循环。论文怀疑与贪心解码有关，并提出更好的解码（如束搜索）可能缓解。
- **23% 的失败来自检索结果无用**。这提醒工程实现：工具返回质量与模型推理同样重要；「搜不到」不是模型能靠多想几步解决的。
- CoT 的 56% 幻觉与 14% 假阳性，正是「不接地」的代价。

其他论文明确写出的限制：

- **上下文增长**：每一步都要把完整轨迹放回提示，长任务很快吃满窗口。
- **动作空间大时示例不够**：复杂环境需要更多演示，容易超过上下文上限。
- **微调只是初步结果**：论文报告 HotpotQA 上的初步微调实验，ReAct 格式在各模型规模上表现最好，微调后的小模型可通过提示的大模型；但更大规模、多任务与强化学习结合仍是开放问题。

## 五条设计启示

1. **先设计动作空间，再写提示词**。动作名、参数、返回格式决定模型能不能学会；动作空间混乱，Thought 写得再漂亮也没用。
2. **Thought 要产生决策差异**。如果每一步的 Thought 都是「我需要继续」，它只是 token 开销；好的 Thought 会改变下一步动作或终止判断。
3. **Observation 必须真实且可解析**。工具报错要作为观察返回，而不是被吞掉；否则模型会在错误前提上继续推理。
4. **终止条件要显式**。论文用 `finish[answer]`；工程里还要有步数上限、重复检测、人工接管三条兜底。
5. **把「检索失败」当一等公民**。搜索为空、结果不含答案、页面打不开，都应该进入策略分支，而不是指望模型自己醒悟。

## 从论文协议到工程实现

论文用纯文本协议（`Thought:` / `Action:` / `Observation:`），今天的工程实现通常换成函数调用或 JSON。两者不是替代关系，而是同一循环的不同编码方式：

| 维度 | 论文 ReAct（2022） | 现代工程实现 |
|------|--------------------|--------------|
| 动作表示 | 文本 `Action: search[...]` | 函数调用 / JSON `{"tool":"search","args":{...}}` |
| 解析方式 | 正则或字符串匹配 | 结构化解析 + schema 校验 |
| 工具选择 | 提示里写死动作空间 | 工具注册表 + 动态下发 |
| 错误处理 | 观察里返回错误文本 | 错误码 + 重试/降级/人工接管 |
| 终止 | `finish[answer]` | 显式 finish 工具 + 步数/重复/超时 |
| 安全 | 论文未展开 | 权限、确认闸门、审计日志 |

这也解释了为什么很多「Agent 框架」看起来不像论文：它们保留的是**交错循环**，换掉的是**文本协议与提示拼接**。

## 小满的 ReAct：一个手机上的工程化样本

TRAE 训练营里的小满 App 是一个可直接观察的工程化 ReAct 样本。它没有照搬论文的文本格式，而是把循环拆成两条模型链：

| 维度 | 论文 ReAct | 小满的实现 |
|------|------------|------------|
| 推理输出 | 自然语言 Thought | 聊天模型规划 + 操作模型输出 JSON 动作 |
| 动作空间 | 任务特定文本动作 | 点击、长按、输入、滑动、返回、等待、打开 App 等设备动作 |
| 观察 | 工具返回文本 | 屏幕截图 + 无障碍节点树（≤120 节点） |
| 循环上限 | 论文按任务设步数 | `maxSteps=30`、连续 3 次屏幕不变判卡住 |
| 安全 | 未展开 | `core-sentinel` 拒绝/询问/允许，付款发送删除前确认 |
| 经验 | 无 | 成功后写入 `howto` 笔记，下次任务检索注入 |

对应细节见 [小满 Agent 解剖](../../../trae/trae-agent-camp-01/concepts/02-agent-anatomy-react.md) 与 [源码地图](../../../trae/trae-agent-camp-01/concepts/08-source-map.md)。这张对照表的价值是：**论文给你机制，工程给你约束**；只读论文容易写出「能演示、停不下来」的循环。

## 与 Plan-and-Solve、Reflection 的关系

ReAct 不是唯一的范式。把三者放在一起看，差异在「思考与行动的时间关系」：

| 维度 | ReAct | Plan-and-Solve | Reflection |
|------|-------|----------------|------------|
| 思考-行动关系 | 交错进行 | 先规划后执行 | 先生成后反思 |
| 灵活性 | 高，可动态调整 | 中，按计划执行 | 中高，迭代修正 |
| 适用场景 | 信息检索、动态决策 | 流程固定的复杂任务 | 高质量内容生成 |
| 成本 | 中等（多轮工具调用） | 较低（一次规划） | 较高（多轮自我评估） |
| 主要风险 | 循环、上下文膨胀 | 计划过期、环境变化 | 过度自我批评、收敛慢 |

工程上常见的组合是：**Plan-and-Solve 出骨架 → ReAct 执行每一步 → Reflection 在关键节点复盘**。三者不是互斥选项，而是不同粒度的控制结构。

## 从零实现的价值

教程强调亲手实现范式的重要性：

1. **理解设计机制**：直接使用高度抽象的框架，容易把「循环」当成黑盒。
2. **暴露工程挑战**：解析失败、工具报错、死循环、上下文超限，这些才是 Agent 从演示到可用的分水岭。
3. **从使用者到创造者**：掌握循环与动作空间的设计后，才能为具体场景做取舍，而不是在框架参数里碰运气。

## 常见误区

- **「ReAct 就是 CoT 加工具」**：不准确。CoT 的推理不改变外部状态；ReAct 的 Action 会改变环境，Observation 会反过来改写推理前提。
- **「Thought 越多越好」**：不对。Thought 的价值在决策差异；重复同一句思考只会推高成本与循环风险。
- **「ReAct 一定比 CoT 准」**：论文里 HotpotQA 单用 ReAct 低于 CoT-SC；它的优势是接地、可解释、可纠错，以及和 CoT-SC 组合后的上限。
- **「有了函数调用就不需要 ReAct」**：函数调用只是动作编码方式；没有「观察—再推理」的闭环，仍只是单轮工具调用。
- **「失败就是模型不行」**：论文的失败归因里，47% 是推理/循环、23% 是检索质量；先分链定位，再谈换模型。

## 参考与延伸

- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models.* ICLR 2023. [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)
- 项目页与代码：[react-lm.github.io](https://react-lm.github.io/)、[ysymyth/ReAct](https://github.com/ysymyth/ReAct)
- Hello-Agents 第四章：智能体经典范式构建
- 相关：[Agent 框架开发](agent-framework-development.md)、[多 Agent 协作](multi-agent-collaboration.md)
