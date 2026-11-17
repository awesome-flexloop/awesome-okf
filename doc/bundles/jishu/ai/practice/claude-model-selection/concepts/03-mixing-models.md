---
type: Concept
title: "混合模型编排"
description: "在同一个系统里组合 Fable、Opus、Sonnet、Haiku：切换断点、thinking 兼容、子代理、advisor 与批量委派。"
tags: [claude, multi-model, subagents, advisor, orchestration]
generated: { by: "lobsterai/main", at: "2026-11-10T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T13:30:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: cc-model-config
    resource: https://code.claude.com/docs/en/model-config
---

# 混合模型编排

## 为什么要混合

单一模型只能选一个成本/能力点。混合模型把不同步骤放到不同档位：规划用大模型，执行用中模型，机械劳动用小模型。博文的四个演示场景就是这个思路——Fable 5.2 做 JavaScript→TypeScript 迁移，Opus 5.5 做订阅功能，Sonnet 5.5 写商品页，Haiku 5.5 给客服消息分类（F-047 的延伸应用）。

混合不是免费的：切换有缓存成本，thinking block 有兼容边界，编排本身也消耗 token。下面按“值不值得”逐项拆。

## 切换要选自然断点

提示缓存属于写入它的模型。第一次在新模型上发请求，要为整段对话支付缓存写入价（F-049）。切换越频繁、上下文越长，这笔钱越贵。

降低切换成本的做法（F-050）：

1. Claude Code 里先执行 `/compact`，把上下文压短再换模型。
2. 或者带一份简短书面计划开新会话。
3. API 侧用“工作至今的摘要”开启新模型对话，不要直接灌全量历史。

自然断点通常是：一个 PR 完成、一次调查结束、计划评审通过。不要在任务中途为了省几分钱换模型。

## Thinking block 的兼容边界

每个 thinking block 记录生成它的模型，模型只读部分其他模型的 block（F-051）：

| 读取方 | 可读取的 thinking block |
|---|---|
| Opus 5.5 | Sonnet 5.5、Haiku 5.5 |
| Sonnet 5.5 | Haiku 5.5 |
| Fable 5.2 | Opus 5.5、Sonnet 5.5、Haiku 5.5 |
| Fable 5.1 | Opus 5.5（仅 Claude API） |

规则可以概括为：**向上不读，向下可读**。下移一档会丢失先前推理，因为模型不读更高级模型的 block；无法读取时 API 丢弃 block 但请求仍然成功，新模型就在没有那段推理的情况下继续工作（F-052）。

两个高危切换：

1. 从 Fable 5.2 切到任何其他通用模型，都会丢弃它的推理（F-053）。
2. 把 Opus 5.5 的会话交给 Fable 5.1 以外的更小模型，等于让它重新建立判断。

所以“降档省钱”只适合那些不依赖前序深度推理的步骤；需要延续判断链的任务，要么不换，要么换完补一份显式结论摘要。

## 子代理：把冗长阅读外包

子代理在独立上下文窗口运行，只回传摘要，按它自己运行的模型费率计费（F-054）。这使“便宜模型读大量材料、贵模型做判断”成为标准做法。

Claude Code 里用 `model: haiku` 或 `model: sonnet` 指定子代理模型；`CLAUDE_CODE_SUBAGENT_MODEL` 设未指定时的默认（F-054）。博文给出的 `log-reader` 示例只做一件事：读日志，报告每个失败的文件、测试名和第一行错误，不改任何文件（F-055）。

原则是：小模型只做“错误容易发现”的工作——找文件、跑测试、读日志；改代码与判断留给主模型（F-056）。小模型误读一次搜索结果，主模型就会打开错文件并把 token 花在错误方向上。

一个容易忽略的细节：Claude Code 内置的 Explore 子代理使用会话模型（API 上上限为 Opus），并不总是跑 Haiku。要压低探索成本，可以自建同名 `Explore` 并设 `model: haiku`；`ANTHROPIC_DEFAULT_HAIKU_MODEL` 可以固定 `haiku` 别名的指向（F-057）。

`haiku` 别名的解析还依赖平台：Anthropic API 上解析为 Haiku 5.5（需 Claude Code v2.1.293+），Bedrock、Google Cloud、Microsoft Foundry、Claude Platform on AWS 仍解析为 Haiku 4.5（F-058）。跨平台部署时别假设别名等价。

## opusplan：一个反面教材

`opusplan` 别名在 plan 模式用 Opus，执行阶段切到 Sonnet（F-059）。听起来省钱，但它把代码编辑放在小模型上，正好与博文建议相反——博文主张代码编辑留在主模型，只把小任务交给小模型。采用 `opusplan` 前应在自己的任务上实测，而不是因为它名字好听就设为默认。

## Advisor：只在会咨询时有用

Advisor 工具（beta）把便宜快速的 executor 与更强的 advisor 配对，executor 可以在中途请求指导，多数 token 按 executor 费率计费（F-060）。

但博文对它的态度相当克制：平台成本指南的四组配对里，没有一组明显优于单用 executor；只有 executor 主动咨询时 advisor 才有帮助（F-061）。executor 在低 effort 下咨询得更少，收益也更小。

配对还受兼容性限制：Sonnet 5.5 executor 接受 Fable 5.2、Opus 5.5、Opus 5、Sonnet 5.5 作为 advisor；Fable 5.2 executor 只接受 Fable 5.2 或 Mythos 5.2（F-062）。

一个实测反例：Opus 5.5 `high` 配 Fable 5.1 advisor 在内部编码基准得 90.1%、`$2.92`/次，比单用 Opus 5.5 `high` 高 1.7 分、花费约 2.1 倍（F-063）。1.7 分在运行间噪声范围内，大致等于直接升 effort 能买到的量。

结论：先测 executor 的咨询率。如果它几乎不问，advisor 只是账单上的额外一行。

## 批量委派：大任务拆给便宜 worker

子代理处理“主线程旁边的支线”；批量委派处理“一个上下文装不下的大任务”：顶级模型拆分、分发给大量便宜 worker 并行执行、再合并结果。

博文的内部缺陷搜索基准（约 2200 万 token 源码）显示：Opus 5.5 带队、最多 25 个 Sonnet 5.5 worker，成本比单用 Opus 5.5 默认 effort 低约三分之一，得分接近（F-064）。

Claude Platform 的 Claude Managed Agents 提供 multiagent orchestration：一个 coordinator 加一组 worker（F-065）。但它不适合单链依赖步骤，也不适合一个上下文就能完成的工作——那些场景里规划与合并的成本高于节省。

## 混合系统的四条纪律

1. 切换只在自然断点，先压缩上下文再换模型。
2. 需要延续推理链的步骤不降档；降档后补显式结论摘要。
3. 子代理只做可校验的机械劳动，代码编辑与判断留在主模型。
4. 简单路由用代码写死，不要用模型做路由器（F-074）。

以上编排能力中，advisor、preserved thinking 与部分 API 行为仅有博文单源；platform.claude.com 在核验环境区域受限，采用前请以当前官方文档复核。
