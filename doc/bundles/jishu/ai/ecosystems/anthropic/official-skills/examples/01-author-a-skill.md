---
type: example
title: "从零造一个 Skill：完整实操"
description: "以一个真实可跑的最小 Skill 为例，演示 frontmatter 编写、quick_validate 校验、package_skill 打包、目录组织与 description 触发设计的完整流程，命令可直接复制。"
tags: [skills, tutorial, authoring, workflow, official-skills]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# 从零造一个 Skill：完整实操

本篇以一个最小但真实的 Skill 为例，演示完整流程。所有命令基于本地镜像 `external/libs/anthropics/skills`，**可直接复制执行**。

---

## 场景设定

要做一个 skill：`meeting-note-formatter`，把会议流水账整理成结构化会议纪要。

**先做取舍判断**：这个 skill 需要脚本吗？

- 不需要——整理格式是判断题，不是确定性计算题
- 需要的只有一份**格式规范**（记纪要怎么写）

因此按 [04-authoring-patterns.md](../concepts/04-authoring-patterns.md) 的模式 1（纯指令流程型）来做，SKILL.md 承担全部规范。

---

## 第 1 步：定 frontmatter

### 1.1 name

```yaml
name: meeting-note-formatter
```

约束（F-014）：kebab-case（`^[a-z0-9-]+$`）、≤64 字符、不以 `-` 开头/结尾、无连续 `--`。"meeting-note-formatter" 全部满足。

### 1.2 description —— 最需要打磨的一行

先用强度 A（场景枚举型）写法：

```yaml
description: >
  Format raw meeting transcripts into structured meeting notes with sections
  for attendees, decisions, action items, and open questions. Use this when
  the user mentions meeting notes, meeting minutes, 会议纪要, 会议记录,
  action items, or asks to tidy up / summarize / format a transcript,
  notes, or discussion. Trigger on: "整理纪要", "会议记录", "转成纪要",
  "format these notes", "turn this transcript into notes". Skip when the
  user only wants a plain summary of a document that is not a meeting, or
  when they asked for verbatim quotes rather than structured notes.
```

逐项自查：

| 检查项 | 结果 |
|--------|------|
| 长度 ≤1024 | ✅ 约 420 字符 |
| 不含 `<` `>` | ✅ |
| 说清"做什么" | ✅ 首句 |
| 说清"何时用" | ✅ Trigger 枚举中英双语 |
| 说清"何时不用" | ✅ Skip 句 |

> 💡 中英双语触发词是有意为之——用户可能说"整理纪要"也可能说"format these notes"，两者都要覆盖。

### 1.3 license

```yaml
license: Complete terms in LICENSE.txt
```

若你的 skill 随仓库分发且是 Apache-2.0，用这一行；若走专有授权，写 `Proprietary. LICENSE.txt has complete terms`——**与 LICENSE.txt 的实际内容保持一致**，不要笼统写 MIT。

### 1.4 allowed-tools / metadata / compatibility

官方 19 个 skill **一个都没用**这三个字段（F-019 实测）。建议：

- `allowed-tools`：先不用。若确实要限制，确认目标运行环境对该字段的实际支持再写。
- `metadata`：官方未用。自建评测体系时可放 `version`、`author`（`metadata` 下的嵌套键在校验时被豁免）。
- `compatibility`：**必须是字符串**、≤500 字符（F-016）。写成嵌套 map 会报 `Compatibility must be a string, got dict`。

```yaml
compatibility: Requires a transcript or bullet notes as input; no external scripts or network access needed.
```

---

## 第 2 步：写正文

### 2.1 骨架选择

参照 `doc-coauthoring` 的三段式，但简化为两段（无读者测试阶段）：

```markdown
# Meeting Note Formatter

## When this applies
（适用/不适用，5 行以内）

## Output structure
（固定五段式骨架 + 每段的填充规则）

## Rules
（条目式硬规则：保留原文用词、不编造、责任人必须明确、日期用绝对日期）

## Example
（一个 before/after 对照）
```

### 2.2 输出模板写成字面骨架

官方惯例是 `ALWAYS use this exact template:` + 具体模板块（F-091 的"模板即字面起点"）。例如：

```markdown
## Output structure

ALWAYS use this exact template:

# <会议主题> — <YYYY-MM-DD>

## 参会人
- <姓名>（<角色>）

## 决策
- <决策内容>（决策人：<姓名>，日期：<YYYY-MM-DD>）

## 待办
- [ ] <任务> — 负责人：<姓名>，截止：<YYYY-MM-DD>

## 悬而未决
- <问题>（阻塞点：<是什么>）

## 其他信息
<不归入以上四类的内容；没有则写"无">
```

### 2.3 写规则时解释"为什么"

不要写 `NEVER add attendees that are not in the transcript.`，改为：

> **只写转录中出现的参会人**——补全名单等于编造事实，纪要的读者会据此行动。

### 2.4 区分 FIXED 与 VARIABLE

参照 `algorithmic-art`（F-092）——本 skill 中：

- **FIXED**：五段标题名称与顺序、待办的 `- [ ]` 格式、日期用 `YYYY-MM-DD`
- **VARIABLE**：具体条目内容、参与人数量、是否有悬而未决段

在正文中显式声明这两块，避免每次输出结构漂移。

---

## 第 3 步：目录组织

```
meeting-note-formatter/
├── SKILL.md              # 必需
├── LICENSE.txt           # 分发时必需
└── references/
    └── edge-cases.md     # 可选：边界案例（跨时区、无人发言、纯闲聊）
```

**放什么、不放什么**：

| 内容 | 位置 | 理由 |
|------|------|------|
| 主流程与模板 | `SKILL.md` | 每次触发都要用 |
| 边界案例 | `references/edge-cases.md` | 少见情况，按需加载 |
| 输出样例 | `SKILL.md` 末尾 | 帮助对齐格式 |
| 输出模板文件 | `assets/` | 若模板要**原样复用**（而非供人读懂），放 `assets/` |

> 🔴 `references/` 文件必须在 SKILL.md 里**标注加载时机**，例如"当转录中出现跨时区时间时读 `references/edge-cases.md`"。否则模型会一次性全读。

---

## 第 4 步：校验

```bash
cd D:/spaces/SpecWeave/external/libs/anthropics/skills/skills/skill-creator
python scripts/quick_validate.py D:/path/to/meeting-note-formatter
```

预期输出：`Skill is valid!`（退出码 0）

失败信息对照：

| 报错 | 原因 | 修法 |
|------|------|------|
| `Unexpected key(s) in SKILL.md frontmatter: xxx` | 用了表外字段 | 只留 6 个允许键 |
| `Name 'xxx' should be kebab-case` | name 含大写/下划线 | 改 kebab-case |
| `Name 'xxx' cannot start/end with hyphen or contain consecutive hyphens` | 首尾 `-` 或 `--` | 改名 |
| `Name 'xxx' is too long (N characters). Maximum is 64 characters.` | 超 64 | 缩短 |
| `Description is too long (N characters). Maximum is 1024 characters.` | 超 1024 | 精简触发词 |
| `Description cannot contain angle brackets (< or>)` | 含尖括号 | 删尖括号（写 "小于号"而非 `<`） |
| `Compatibility must be a string, got dict` | compatibility 写成 map | 改成字符串 |

> ⚠️ **注意**：`quick_validate.py` **不检查行数**（F-017）。它只有一条 500 相关的检查，是 `len(compatibility) > 500`。SKILL.md 超过 500 行不会导致校验失败——但仍建议控制在 500 行内，超出部分拆到 `references/`。

---

## 第 5 步：打包

```bash
cd D:/spaces/SpecWeave/external/libs/anthropics/skills/skills/skill-creator
python scripts/package_skill.py D:/path/to/meeting-note-formatter ./dist
```

产出 `dist/meeting-note-formatter.skill`。

打包规则（实测 `package_skill.py`）：

| 类别 | 规则 |
|------|------|
| 压缩方式 | ZIP_DEFLATED |
| 输出名 | `<目录名>.skill`（用**目录名**，不是 frontmatter 的 `name`） |
| 前置动作 | 自动调用 `validate_skill()`，校验不过直接中止 |
| 排除目录 | `__pycache__`、`node_modules` |
| 排除文件 | `.DS_Store`、`*.pyc` |
| root 级排除 | `evals/`（**仅在 skill 根目录这一层排除**，嵌套更深的不排除） |

> 💡 `evals/` 只在根级排除这一点很关键——你可以在 `evals/` 下放测试用例不被打包，但 `references/evals/` 会被打进包里。

---

## 第 6 步：评估（可选但推荐）

用 `skill-creator` 的双跑机制确认这个 skill 真的有用：

```bash
cd D:/spaces/SpecWeave/external/libs/anthropics/skills/skills/skill-creator
python scripts/run_eval.py --skill-path D:/path/to/meeting-note-formatter --eval-set D:/path/to/evals/evals.json
```

`run_eval.py` 的参数（实测）：

| 参数 | 默认 | 说明 |
|------|------|------|
| `--eval-set` | 必填 | 评估集 JSON 路径 |
| `--skill-path` | 必填 | 被测 skill 目录 |
| `--description` | 无 | 覆盖被测 description（测试不同触发文案） |
| `--num-workers` | 10 | 并行 worker 数 |
| `--timeout` | 30 | 单次查询超时（秒） |
| `--runs-per-query` | 3 | 每条查询跑几次 |
| `--trigger-threshold` | 0.5 | 触发率阈值 |
| `--model` | 用户配置 | 评测用模型 |
| `--verbose` | 关 | 向 stderr 打进度 |

流程（F-095）：

```
1. 同批次发起 with_skill 与 without_skill 两组运行
2. 运行期间并行起草断言（expectations）
3. 运行完成抓取耗时
4. 评分 + 聚合 + 生成报告（benchmark.json）
5. 打开 eval-viewer 人工审阅
```

**双跑是最低成本的确证方式**——它回答"加了这段指令，输出真的变好了吗"，比任何主观判断可靠。

若触发不准，用 `scripts/improve_description.py` 迭代 description。

---

## 第 7 步：装到 Claude Code

作为本地 skill：

```
# 放到 ~/.claude/skills/meeting-note-formatter/
```

或走插件市场（`marketplace.json` 里注册路径）：

```json
{
  "name": "my-plugins",
  "source": "./",
  "skills": ["./skills/meeting-note-formatter"]
}
```

---

## 完整命令速查

```bash
SKILLS=D:/spaces/SpecWeave/external/libs/anthropics/skills/skills

# ① 校验
cd $SKILLS/skill-creator && python scripts/quick_validate.py D:/path/to/my-skill

# ② 打包
cd $SKILLS/skill-creator && python scripts/package_skill.py D:/path/to/my-skill ./dist

# ③ 评估
cd $SKILLS/skill-creator && python scripts/run_eval.py --skill-path D:/path/to/my-skill --eval-set D:/path/to/evals/evals.json

# ④ 打包产物解包查看（验证排除规则）
python -c "import zipfile;print('\n'.join(zipfile.ZipFile('dist/my-skill.skill').namelist()))"
```

---

## 常见坑速查

| 坑 | 症状 | 解法 |
|----|------|------|
| description 写成了"这是什么"而非"何时用" | skill 永远不触发 | 补 Trigger 枚举 + Skip 句 |
| description 触发面过宽 | 频繁误触发 | 补反触发条件，必要时加可执行排除探测 |
| 规范全塞 SKILL.md | 上下文成本高 | 拆 `references/`，并标注加载时机 |
| references 未标加载时机 | 模型全读，等于没拆 | 每篇写清"何时读" |
| 模板写成"参考风格" | 输出每次不一样 | 写成字面骨架，标 `ALWAYS use this exact template:` |
| 用 MUST/NEVER 堆砌 | 遇到边界就崩 | 改写为解释"为什么" |
| 只规定产出、不规定验收 | 产出无法自动检查 | 补 QA 段（内容/文件/视觉） |
| 假设了用户会给全上下文 | 半截输入就崩 | 补缺失信息的处理路径 |

---

## 相关文档

- [SKILL.md格式规范](../concepts/01-skill-format.md) — 字段与目录解剖
- [Skill 编写规范与可复用模式](../concepts/04-authoring-patterns.md) — 骨架选择决策表
- [Skill Creator工具详解](../concepts/02-skill-creator.md) — 元技能完整流程
- [事实登记表](../references/facts.md) — 校验规则实测底账
