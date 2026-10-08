---
type: Concept
title: Eval 驱动迭代：把 ML 实验方法用于技能治理
description: 评估技能的完整实验方法学——evals.json 测试用例 schema、带技能/不带技能双臂对照、断言分级与 grading.json、benchmark.json delta 分析、五条模式分析规则与 feedback.json 迭代闭环。
tags: [agent-skills, skill-format, evaluation, benchmark, iteration, assertions]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: evaluating-mdx
    resource: /references/spec-sources.md
    title: docs/skill-creation/evaluating-skills.mdx 评估指南
---

# Eval 驱动迭代：把 ML 实验方法用于技能治理

官方评估指南的篇幅超过规范本体，其方法论直接移植自 ML 实验：双臂对照运行、断言分级（PASS 必须附证据）、benchmark delta 分析、盲比较、训练反馈闭环。它把"技能"当作需要 eval 驱动迭代的软件资产来治理——单次"看起来能用"的验证不可信，因为技能效果与会话历史强耦合，评估要求每次运行从干净上下文开始（F-029）。

## 测试用例与存储

每个测试用例三部分（F-027）：**Prompt**（真实用户消息）、**Expected output**（成功样貌的人类可读描述）、**Input files**（可选）。存放在技能目录内 `evals/evals.json`：

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": "eval-1",
      "prompt": "Analyze sales.csv and report trends",
      "expected_output": "A markdown report with at least 3 insights and a bar chart",
      "files": ["sales.csv"],
      "assertions": ["The output file is valid JSON"]
    }
  ]
}
```

`evals.json` 是唯一手工编写的文件，其余 JSON（`grading.json`、`benchmark.json`、`feedback.json`、`timing.json`）在评估过程中产生（F-028）。

## 双臂对照运行

核心运行模式（F-028）：每个用例跑两次——**带技能**与**不带技能**（或带上一版本）作基线对照。工作区结构：

```text
csv-analyzer-workspace/
├── iteration-1/
│   ├── eval-1/
│   │   ├── with_skill/       # 带技能运行
│   │   │   ├── outputs/
│   │   │   ├── timing.json
│   │   │   └── grading.json
│   │   └── without_skill/    # 基线运行
│   │       ├── outputs/
│   │       ├── timing.json
│   │       └── grading.json
│   └── benchmark.json        # 同层聚合统计
└── skill-snapshot/           # 旧版快照
```

运行纪律（F-029）：每轮从**干净上下文**开始（支持 subagent 的环境天然隔离；否则每个运行用独立会话）；改进既有技能时先快照旧版 `cp -r <skill-path> <workspace>/skill-snapshot/`，基线运行指向快照并保存到 `old_skill/outputs/`。

**timing.json**（F-030）：字段为 `total_tokens` 与 `duration_ms`；Claude Code 的 subagent 任务完成通知携带这两个值，"Save these values immediately — they aren't persisted anywhere else"（立即保存——它们不会被持久化到别处）。

## 断言写作

断言（assertions）在**看到第一轮输出后**再添加（F-031）。好断言三标准：可编程验证、具体可观察、可数：

- ✅ "The output file is valid JSON"
- ✅ "The bar chart has labeled axes"
- ✅ "The report includes at least 3 recommendations"
- ❌ "The output is good"（太模糊）
- ❌ 精确匹配措辞（太脆弱）

写作风格、视觉设计等难以分解为 pass/fail 的品质留给**人工评审**（F-031）。

## 评分与聚合

**grading.json**（F-032）：`assertion_results` 数组（每项 `text`/`passed`/`evidence`）+ `summary`（`passed`/`failed`/`total`/`pass_rate`）。评分原则：PASS 必须有具体证据（引用或指向输出）；同时复审断言本身（太容易/太难/不可验证的要修）。

**benchmark.json**（F-032）：`run_summary` 下 `with_skill`/`without_skill`/`delta` 三块，各含 `pass_rate`/`time_seconds`/`tokens` 的 `mean`+`stddev`（stddev 仅在多次运行时有意义）。delta 同时呈现技能的**代价与收益**——文中示例：+13 秒换 +50 个百分点通过率大概率值得；token 翻倍换 2 个百分点提升可能不值。

补充手段：双版本盲比较（blind comparison）作为断言评分的补充（F-032）。

## 模式分析五条规则

读完聚合数据后按此排查（F-033）：

1. **删除或替换在两种配置下都恒通过的断言**——它们夸大带技能通过率、不反映技能价值（恒通过 ≠ 安全，是噪音）。
2. **排查两种配置下都恒失败的断言**——断言坏了/用例太难/查错了对象。
3. **研究"带技能过、不带技能不过"的断言**——技能价值的直接证据，追问是哪条指令或脚本起效。
4. **结果跨轮不一致（高 stddev）**——收紧指令或补示例降低歧义。
5. **检查时间与 token 离群值**——读执行 transcript 找瓶颈。

## 人工反馈与迭代闭环

为每个用例记录具体可操作的反馈存入 `feedback.json`（F-034）：空字符串表示通过人工评审；"The chart is missing axis labels" 可操作而 "looks bad" 不可操作。

**三类迭代信号**（F-034）：

1. 失败断言——具体缺口；
2. 人工反馈——更广泛的质量问题；
3. 执行 transcript——为什么出错（被忽略的指令可能含糊；无产出步骤应简化或删除）。

**最有效的改法**：把三类信号连同当前 SKILL.md 交给 LLM 提改进提案，附四条准则：

1. **从反馈泛化**——修底层问题而非打窄补丁；
2. **保持精简**——过约束时尝试**删**指令（与"堆更多规则"的直觉相反）；
3. **解释 why**——"Do X because Y tends to cause Z" 优于 "ALWAYS do X, NEVER do Y"；
4. **打包重复工作**。

**循环五步**：提案 → 应用 → 在新 `iteration-<N+1>/` 重跑 → 评分聚合 → 人工复审。**停止条件**：满意、反馈持续为空、或迭代间不再有有意义提升（F-034）。

文末 Tip：`skill-creator` Skill（github.com/anthropics/skills/tree/main/skills/skill-creator）自动运行该工作流的大部分环节——方法与工具的衔接点，另见既有知识束 anthropics-skills。

## 相关概念

- [/concepts/03-authoring-principles.md](/concepts/03-authoring-principles.md) —— 评估发现问题的三个落点（gotchas/指令/脚本）
- [/concepts/05-description-optimization.md](/concepts/05-description-optimization.md) —— 同族方法学：触发维度的 60/40 切分实验
- [/concepts/01-progressive-disclosure.md](/concepts/01-progressive-disclosure.md) —— timing.json 反映三层加载的成本
- [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md) —— 评估前的格式门禁
