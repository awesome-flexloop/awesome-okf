---
type: Concept
title: 创作原则与最佳实践：上下文经济学与指令设计模式
description: 技能创作的核心方法论——add-what-agent-lacks 上下文经济学、两类创建路径、划界与控制校准、gotchas/模板/checklist/验证循环/plan-validate-execute 模式，以及 uvx/PEP 723/stderr 分离等脚本工程要点。
tags: [agent-skills, skill-format, authoring, best-practices, prompt-engineering, scripts]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: best-practices-mdx
    resource: /references/spec-sources.md
    title: docs/skill-creation/best-practices.mdx 创作指南
  - id: using-scripts-mdx
    resource: /references/spec-sources.md
    title: docs/skill-creation/using-scripts.mdx 脚本工程指南
---

# 创作原则与最佳实践：上下文经济学与指令设计模式

有效的技能不是 LLM 凭空生成的通用流程，而是**扎根于真实专业知识**的浓缩物。创作指南（best-practices.mdx）给出一条主线判断：在不提供领域上下文的情况下让 LLM 生成技能，产出是模糊的通用流程（"handle errors appropriately" 类）；有效技能来自两类真实来源（F-018）。本文整合创作指南与脚本工程指南（using-scripts.mdx）的全部要点。

## 两条创建路径

从哪里获得"真实专业知识"（F-018）：

1. **从亲自动手的任务中提取**——关注四类信息：有效的步骤、你做出的纠正、输入/输出格式、你提供的上下文。
2. **从既有项目产物合成**——好的源材料包括：内部文档/runbook/风格指南、API 规范/schema/配置文件、代码评审评论与 issue 追踪、版本控制历史（尤其补丁与修复）、真实失败案例及其解决过程。

**用真实执行打磨**（F-019）：对真实任务运行技能，把全部结果（不只是失败）回灌到创建过程；一轮 execute-then-revise 就能明显提升质量。执行痕迹中无产出步骤的常见原因有三——指令太模糊、指令不适用于当前任务、选项太多而无明确默认值。

## 上下文经济学

核心原则（F-020）：

> "Add what the agent lacks, omit what it knows."（补智能体所缺，略智能体已知。）

每段内容的自检问题："Would the agent get this wrong without this instruction?"（没有这条指令智能体会做错吗？）若没有该技能智能体已能完成整个任务，则技能可能没有增加价值。

## 划界与细节度

技能划界类比"决定一个函数该做什么"（F-021）：

- **封装连贯工作单元**，可与其他技能组合。
- **过窄**：迫使单个任务加载多个技能（开销与指令冲突风险）。
- **过宽**：难以精确激活。示例："查询数据库并格式化结果"是连贯单元；再涵盖数据库管理就是管得太多。
- **细节度**：简洁的逐步指引加一个可运行的示例，优于穷举式文档——过度全面的技能反而有害，智能体难以提取相关内容并可能被不适用的指令引上无产出路径。

## 控制校准：自由度 vs 规定性

指令的具体度应与任务的脆弱性匹配（F-023）：

| 场景 | 策略 | 理由 |
|---|---|---|
| 多种路径皆可行 | 给智能体自由度；解释 **why** 比刚性指令更有效 | 理解目的的智能体能做出更好的上下文相关决策 |
| 操作脆弱、要求一致或必须按特定顺序 | 保持**规定性**（prescriptive） | 示例："Run exactly this sequence: `python scripts/migrate.py --verify --backup`… Do not modify the command or add additional flags." |

多数技能是混合体，应**逐段独立校准**。

另两条指令设计原则（F-024）：

- **提供默认值而非菜单**：选定默认工具、简要提及替代项。示例："Use pdfplumber for text extraction… For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
- **倾向过程而非声明**：教智能体如何处理**一类问题**而非某个实例的产出。示例方法："读 schema → 按 `_id` 外键约定 join → 按请求加 WHERE → 聚合并格式化为 markdown 表格"。

## 五种高价值内容模式

### 1. Gotchas（环境陷阱清单）

许多技能中价值最高的内容是"违背合理假设的环境特定事实"清单（F-025）：

- 软删除表必须带 `WHERE deleted_at IS NULL`；
- 同一 ID 在三个系统中字段名分别为 `user_id`/`uid`/`accountId`；
- `/health` 与 `/ready` 语义差异。

放置纪律：gotchas 应放在 `SKILL.md` 正文中，让智能体在遇到情况**之前**读到。当你不得不纠正智能体的错误时，把该纠正加入 gotchas 段——文中称这是迭代改进技能最直接的方式之一。

### 2. 输出格式模板

短模板内联于 SKILL.md；长模板或偶用模板存 `assets/` 并引用（F-026）。理由：智能体对具体结构的模式匹配优于散文描述。

### 3. 多步工作流 checklist

带 `- [ ]` 复选项与脚本路径（F-026）。

### 4. 验证循环

完成 → 运行验证脚本 → 失败则修复重跑 → 通过才继续（F-026）。参考文档也可充当验证器。

### 5. plan-validate-execute

批量或破坏性操作先产出**结构化中间计划**，用验证脚本对照事实源校验后再执行（F-026）。文中以 PDF 表单填充五步流程为例，并强调校验步骤的错误信息要让智能体能**自我纠正**。

### 脚本打包信号

当智能体每轮独立重造相同逻辑（画图、解析特定格式、验证输出）时，信号是把该逻辑写成**经过测试的脚本**放入 `scripts/`（F-026）。

## 附录：脚本工程要点

以下要点来自 using-scripts.mdx（与 F-026、F-043 互补的直接引用信源）。

### 一次性命令 vs 打包脚本

已有包能完成任务时，可直接在 SKILL.md 引用一次性命令；六个常用运行器：

| 运行器 | 生态 | 特点 |
|---|---|---|
| `uvx` | Python（随 uv 分发） | 隔离环境运行包，激进缓存，重复运行近瞬时 |
| `pipx run` | Python | uvx 的成熟替代，OS 包管理器可得 |
| `npx` | Node.js（随 npm 分发） | 按需下载并缓存；用 `npx package@version` 钉版本 |
| `bunx` | Bun | npx 的 Bun 等价物 |
| `deno run` | Deno | 文件系统/网络访问需权限标志；`--` 分隔 Deno 标志与工具标志 |
| `go run` | Go（内置） | 直接编译运行 Go 包 |

建议：钉住版本使行为可复现；在 SKILL.md 声明前置条件（如 "Requires Node.js 18+"）；命令复杂到难以一次写对时，移入 `scripts/` 成为经过测试的脚本。

### PEP 723 内联依赖

Python 脚本可用 PEP 723 内联元数据声明依赖，配 `uv run` 单命令执行（无独立 manifest 与安装步骤）：

```python
# /// script
# dependencies = [
#   "beautifulsoup4",
# ]
# ///

from bs4 import BeautifulSoup
```

```bash
uv run scripts/extract.py
```

配套建议：用 PEP 508 说明符钉版本（`"beautifulsoup4>=4.12,<5"`）；用 `requires-python` 约束 Python 版本；`uv lock --script` 生成锁文件保证完全可复现。Deno（`npm:`/`jsr:` 导入说明符）、Bun（无 node_modules 时自动安装）、Ruby（`bundler/inline`）均有各自的内联依赖机制。

### 面向智能体的脚本接口设计

智能体会读 stdout 和 stderr 决定下一步，几条设计纪律：

1. **禁止交互式提示**（硬性要求）：智能体运行在非交互 shell，无法响应 TTY 提示/密码框/确认菜单，阻塞等待输入的脚本会永久挂起。所有输入走命令行标志、环境变量或 stdin。
2. **用 `--help` 文档化接口**：这是智能体学习脚本接口的首要途径；保持简洁——输出会进入智能体的上下文窗口。
3. **有帮助的错误消息**：说清错了什么、期望什么、下一步试什么。反例 "Error: invalid input" 浪费一轮；正例 "Error: --format must be one of: json, csv, table. Received: \"xml\""。
4. **结构化输出 + 通道分离**：优先 JSON/CSV/TSV；**数据走 stdout、诊断（进度/警告）走 stderr**——智能体既能拿到干净可解析的输出，又保留诊断信息。
5. **幂等性**：智能体可能重试命令，"create if not exists" 比 "create and fail on duplicate" 安全。
6. **`--dry-run` 支持**：破坏性或有状态操作提供预览标志。
7. **有区分的退出码**：不同失败类型用不同退出码，并在 `--help` 中说明含义。
8. **安全默认值**：破坏性操作考虑 `--confirm`/`--force` 等显式确认标志。
9. **可预测的输出规模**：许多 harness 在约 10-30K 字符阈值截断工具输出，可能丢失关键信息；大输出应默认给摘要或合理上限，支持 `--offset` 或 `--output` 标志。

## 相关概念

- [/concepts/00-skill-anatomy.md](/concepts/00-skill-anatomy.md) —— 模式落点的物理结构
- [/concepts/01-progressive-disclosure.md](/concepts/01-progressive-disclosure.md) —— 上下文经济学背后的预算约束
- [/concepts/04-eval-driven-iteration.md](/concepts/04-eval-driven-iteration.md) —— 用真实执行打磨的系统化版本
- [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md) —— skills-ref 自身的 CLI 就是本附录设计纪律的示范
- [/examples/01-first-skill-roll-dice.md](/examples/01-first-skill-roll-dice.md) —— 最小技能的实战创作
