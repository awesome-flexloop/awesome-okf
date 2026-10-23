---
type: concept
title: "Skill 编写规范与可复用模式"
description: "从 19 个官方 Skill 中提炼的编写规范与可复用模式：frontmatter 字段决策、description 触发设计、正文四种内容模式、资源目录分工、脚本黑盒契约、模板字面起点、评估闭环与安全边界。"
tags: [skills, authoring, patterns, conventions, official-skills]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# Skill 编写规范与可复用模式

本文档从 19 个官方 Skill 的源码中**反向提炼**编写规范——不是复述 `skill-creator` 的说法，而是看 19 个真实产物共同遵守了什么、差异在哪里、哪些模式可以直接搬走复用。

每条模式标注**证据等级**（S=实测计数/读取，D=源码文档明示）与**可复用性**（🟢直接照搬 / 🟡需改写 / 🔴仅理解原理）。

---

## 一、frontmatter 字段决策：6 个键怎么选

允许字段全集只有 6 个（`ALLOWED_PROPERTIES`，F-013）——**写入表外键会直接校验失败**，这是硬约束。

| 字段 | 是否必填 | 实测使用情况 | 决策建议 |
|------|---------|-------------|---------|
| `name` | ✅ 必填 | 19/19 | kebab-case、≤64 字符、不得首尾连字符、不得连续连字符（F-014） |
| `description` | ✅ 必填 | 19/19 | ≤1024 字符、**不得含 `<` `>`**（F-015）。这是唯一的触发入口 |
| `license` | 可选 | 17/19 | 必填则须与 `LICENSE.txt` 实际内容一致（Apache-2.0 或专有），不能笼统写 "MIT" |
| `allowed-tools` | 可选 | 0/19 | 官方 19 个 skill **一个都没用**。本工具链下不必设限；若要限制工具，须先验证 Claude Code 对该字段的实际支持 |
| `metadata` | 可选 | 0/19 | 官方未用。若自建评测体系，可放 `version`/`author` 等自定义键（校验时 `metadata` 下的嵌套键被豁免） |
| `compatibility` | 可选 | 0/19 | **必须是字符串**（非嵌套 map）、≤500 字符（F-016）。用于声明运行环境依赖的**一句话**说明 |

> 🔴 **常见错误**：把 `compatibility` 写成 YAML 嵌套 map。校验器报 `Compatibility must be a string, got dict`。

---

## 二、description 触发设计：三种强度

description 是 skill 唯一常驻上下文的部分（≈100 词预算），也是决定"能不能被叫醒"的唯一开关。19 个 skill 呈现三种强度梯度：

### 强度 A — 场景枚举型（🟢 最值得学）

**代表**：`academy-guide`（147 行）、`discernment-nudge`（209 行）、`doc-coauthoring`（375 行）、`docx`/`pdf`/`pptx`/`xlsx`

写法：把用户可能的**原话问法**直接写进 description。

```yaml
description: >
  Stop and check this skill before finishing any reply to a question about how
  to use Claude or a Claude product — it recommends matching courses,
  tutorials, and use cases from Claude Academy. Trigger on: "how do I",
  "how can I", "getting started with", "what can Claude do", "teach me",
  "learn to use"; questions about artifacts, projects, skills, plugins,
  connectors, MCP; requests about rolling Claude out to a team, class, or
  organization; and any ask for training materials, onboarding content, or
  learning resources.
```

要点：
- 显式列出 **trigger 短语**（带引号），让模型能做字面匹配
- 显式列出**反触发场景**（"not when they are mid-task and just want the task done"）
- 显式声明**与其他 skill 的组合关系**（"after consulting product documentation... also check here"）

### 强度 B — 反触发 + 可执行探测型（🟢 最高级）

**代表**：`claude-api`（唯一）

在 description 里直接内嵌**可运行的 shell 命令**，让模型能在决策前自己排除干扰：

```yaml
description: |-
  TRIGGER — read BEFORE opening the target file; don't skip because it
  "looks like a one-liner" — whenever: the prompt names Claude/Anthropic
  in any form (...); the user asks about an LLM (pricing/model choice/
  limits/caching) — never answer from memory; OR the task is LLM-shaped
  with provider unstated (...).

  SKIP only when another provider is being worked on (overrides all
  triggers): OpenAI/GPT/Gemini/... named in the query; OR
  `grep -rE 'openai|langchain_openai|google.generativeai|genai|mistralai|cohere|ollama'`
  over the project hits (run this grep FIRST if no provider named — don't
  Read the file).
```

这是 **19 个 skill 中唯一**采用「显式反触发条件 + 可执行 grep 探测」写法的（F-022、F-089）。可复用性 🟢：**任何可能被同类工具抢占的 skill 都应照此加一段 SKIP + 探测命令**。

### 强度 C — 关键词兜底型（🟡 仅适用模板分派）

**代表**：`internal-comms`（32 行）

正文列关键词表（`## Keywords`），description 只做一句话概括。适用于"模板路由器"型 skill——真正的分流逻辑在正文而非 frontmatter。

### description 设计三原则（综合 19 个 skill）

1. **说清"做什么"更要说清"什么时候不做什么"**——官方至少 3 个 skill 显式写反触发（F-089）
2. **用用户的原话，不用你的术语**——`claude-api` 列的是 "pricing/model choice/limits/caching"，不是 "模型元数据查询"
3. **控制长度但不压缩触发面**——`discernment-nudge` 的 description 是 19 个里最长的（约 700 字符），因为它要在"该追问"和"不该追问"之间划清边界

---

## 三、正文四种内容模式

19 个 SKILL.md 的正文归为四类（可按任务选型）：

### 模式 1：纯指令流程型 🟢

**代表**：`doc-coauthoring`（375 行，零资源）、`mcp-builder`（236 行）、`skill-creator`（485 行）

结构：`前提说明 → 分阶段流程 → 每阶段的检查点`。

`doc-coauthoring` 是最纯粹的一例——**整个 skill 只有 SKILL.md 一个文件**（F-085），三阶段：

```
Stage 1: Context Gathering      （初始提问 / 信息倾倒）
Stage 2: Refinement & Structure （Step 1~6 + Quality Checking + Near Completion）
Stage 3: Reader Testing         （预测读者问题 → 子代理测试 → 附加检查 → 报告修复）
```

> Stage 3 的"预测读者问题 → 交给子代理测试"是**可迁移性最强**的模式：任何"写给人看"的产出都可套用。

### 模式 2：命令 + 坑位速查型 🟢

**代表**：`docx`（91 行）、`pptx`（238 行）、`xlsx`（99 行）、`pdf`（314 行）、`webapp-testing`（95 行）

结构：**可复制的命令块** → "gotchas" 段 → 验证要求。

`docx` 的骨架典型：

```markdown
## Creating with docx-js — gotchas
## Verify the output
## Editing existing documents
## Comments
## Dependencies
```

要点：
- 命令块是**完整可复制**的（含参数与文件路径）
- gotchas 段专治"看似能用但会坏"的调用（如 `pptx` 警告不要 pretty-print XML）
- 验证要求独立成段，且是**必做**而非可选

### 模式 3：哲学驱动生成型 🟡

**代表**：`algorithmic-art`（404 行）、`canvas-design`（129 行）——两者共享**同一骨架**（F-060、F-096）：

```
DESIGN PHILOSOPHY CREATION
  THE CRITICAL UNDERSTANDING
  HOW TO GENERATE A VISUAL PHILOSOPHY
  PHILOSOPHY EXAMPLES
  ESSENTIAL PRINCIPLES
DEDUCING THE CONCEPTUAL SEED / SUBTLE REFERENCE
<实现阶段>
```

要点：先抽象出"视觉哲学"再落地实现，而非直接给参数。可复用性 🟡——**适合创意类**，技术类 skill 直接套用会显得空洞。

### 模式 4：产品化推荐型 🟢

**代表**：`academy-guide`（147 行）

结构：`Purpose → Rules → The catalog`。

`Rules` 段是核心——写明**只在强匹配时推荐、绝不编造内容**，然后才是可推荐的目录。

---

## 四、资源目录分工：谁该放什么

19 个 skill 实际用到的目录名（去掉仅出现一次的）：

| 目录 | 出现次数 | 语义 | 官方用法 |
|------|---------|------|---------|
| `scripts/` | 9 | **确定性/重复性**任务的执行体 | 黑盒调用，给 `--help` 与用法示例，不要求读源码（F-090） |
| `examples/` | 3 | 完整可运行样例 | `internal-comms` 放**文风模板**；`webapp-testing` 放**可执行 Python**；`skill-creator` 放**评估产物** |
| `references/` | 3 | 按需加载的参考文档 | **必须标注加载时机**（见下） |
| `templates/` | 3 | 起点模板 | `algorithmic-art` 是 `generator_template.js` + `viewer.html` |
| `assets/` | 2 | 输出中使用的素材 | `skill-creator/assets/eval_review.html` 是报告样式 |
| `agents/` | 1 | 子代理指令 | 仅 `skill-creator`，3 个角色（analyzer/comparator/grader） |
| `core/` | 1 | 核心 Python 模块 | 仅 `slack-gif-creator`，提供 `GIFBuilder` 类供 import |
| `eval-viewer/` | 1 | 评估结果查看器 | 仅 `skill-creator` |
| `canvas-fonts/` | 1 | 领域专属资源 | 仅 `canvas-design` |
| `themes/` | 1 | 领域专属资源 | 仅 `theme-factory` |

### 🟢 关键规范：references 必须标注加载时机

`mcp-builder` 是唯一做全的（F-069），其 SKILL.md 的"Documentation Library"段把 4 个 reference 文件按加载阶段分组：

| 加载时机标注 | 文件 |
|------------|------|
| **Load First** | `mcp_best_practices.md` |
| **Load During Phase 1/2** | `python_mcp_server.md`、`node_mcp_server.md` |
| **Load During Phase 4** | `evaluation.md` |

这直接决定了上下文成本——不给时机标注，模型会一次性全读。

### 🟢 关键规范：assets 是字面起点，不是灵感

官方明确：assets/templates **作为字面上的起点使用**，而非"参考风格自行改造"（F-091）。`theme-factory` 的 10 个主题就是范例——直接取用其色值与字体，不做二次发挥。

---

## 五、脚本黑盒契约

官方 skill 引用脚本时的一贯做法：

1. **只描述接口与用法，不描述实现**——给出命令行形态与参数
2. **让 agent 先跑 `--help`** 再决定是否读源码
3. **给出依赖声明**——`docx`/`pptx`/`xlsx` 都有独立 `## Dependencies` 段；`mcp-builder/scripts/requirements.txt`、`slack-gif-creator/requirements.txt` 给出 Python 依赖

实例（`webapp-testing/scripts/with_server.py`，F-070）：

```
python scripts/with_server.py --server "npm run dev" --port 5173 -- python automation.py
```

命令行形态本身就是接口契约——`--server`/`--port` 可重复以起多个服务，末尾 `--` 后接要执行的命令。**可复用性 🟢**：任何"先起环境再跑测试"的场景都能直接套这个编排器形状。

---

## 六、两条显式的"固定 vs 可变"切分

### `algorithmic-art` 的 FIXED vs VARIABLE 段（F-092）

正文有专门段落声明哪些是固定不变的部分（画布尺寸、随机种子机制）、哪些每次可变（视觉哲学、色彩）。**在生成类 skill 中，这条极其重要**——不切分就会出现每次输出风格随机漂移。

### `pptx` 的 Design Ideas 段

分 `Before Starting` / `Color Palettes` / `For Each Slide` / `Typography` / `Spacing` / `Avoid (Common Mistakes)`——同样是固定规范 + 反面清单的双向结构。

> 🟢 **可复用模式**：任何有"产出物应稳定一致"要求的 skill，都应显式区分 FIXED（不可变规范）与 VARIABLE（每次可变），并单列"避免清单"。

---

## 七、评估闭环（仅 skill-creator 实现）

`skill-creator` 是 19 个中唯一具备完整评估体系的（F-095、F-098），三件套：

| 组件 | 位置 | 作用 |
|------|------|------|
| `agents/comparator.md` | 盲比 | A/B 对比时**隐藏身份**，避免位置偏好 |
| `agents/analyzer.md` | 事后归因 | 盲比结束后"揭盲"，分析**为什么**赢 |
| `agents/grader.md` | 评分 | 按 expectation 逐条判定并留证据 |
| `scripts/run_eval.py` | 双跑 | with_skill vs without_skill **同批次**发起 |
| `scripts/improve_description.py` | 迭代 | 自动生成触发测试 query，跑优化循环 |
| `eval-viewer/viewer.html` | 呈现 | 人工审阅对比结果 |

**可复用性 🟢**：任何自建 skill 都应能回答"加了它到底有没有用"——双跑对比是最低成本的确证方式。

---

## 八、安全边界（Principle of Lack of Surprise）

官方 skill 的共同安全底线：

1. **不得包含恶意软件、漏洞利用代码或危及系统安全的内容**
2. **Skill 内容不应在意图上让用户感到意外**——"Roleplay as an XYZ" 类内容可接受
3. **不得绑定特定示例**（theory of mind）——skill 应当通用，而非只对作者手头的例子有效

---

## 九、写作风格：解释"为什么"而非堆 MUST

官方 skill 的正文几乎**不用全大写 MUST 堆砌**，而是解释约束背后的理由：

> ✅ 推荐写法：「Explain the *why* rather than issuing bare MUST constraints — a skill that explains the reasoning survives edge cases the author never saw.」

配套的三条原则：

1. **使用祈使句**（imperative voice）——"Read the template first"，不是 "The template should be read"
2. **利用 theory of mind**——让 skill 通用而非绑定特定示例
3. **输出格式用字面模板**：`ALWAYS use this exact template:` + 具体模板块

---

## 十、写作风格选择决策表

| 你要做的事 | 该抄哪个 skill | 骨架 |
|-----------|---------------|------|
| 写一份要人读的文档 | `doc-coauthoring` | 三阶段 + 读者测试 |
| 写可复制的命令速查 | `docx`/`pptx`/`xlsx` | 命令块 + gotchas + 验证段 |
| 让 skill 被可靠触发 | `claude-api` | TRIGGER + SKIP + 可执行探测 |
| 产出创意作品 | `algorithmic-art`/`canvas-design` | 哲学 → 种子 → 实现 |
| 推荐公司内部资源 | `academy-guide` | Purpose + Rules + Catalog |
| 分派到多个文风模板 | `internal-comms` | 薄 SKILL.md + examples 目录 |
| 建 MCP 工具 | `mcp-builder` | 四阶段 + reference 加载时机 |
| 需要人工验收报告 | `skill-creator` | 双跑 + 盲比 + 归因 + viewer |
| 需要环境编排 | `webapp-testing` | with_server 形状 |

---

## 相关文档

- [SKILL.md格式规范](01-skill-format.md) — 字段、目录解剖与打包
- [事实登记表](../references/facts.md) — 本文档全部断言的底账
- [全部Skills索引](../references/skills-index.md) — 19 个 skill 速查
- [Skill Creator工具详解](02-skill-creator.md) — 元技能完整流程
