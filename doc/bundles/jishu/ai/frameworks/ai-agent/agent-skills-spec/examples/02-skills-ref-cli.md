---
type: Example
title: skills-ref CLI 实战：validate / read-properties / to-prompt
description: skills-ref 参考实现三子命令全流程实战——validate 校验与退出码、read-properties 的 JSON 序列化规则、to-prompt 多技能 XML 生成与转义行为，附安装步骤与定位说明。
tags: [agent-skills, skills-ref, cli, validation, tutorial]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: skills-ref-cli
    resource: /references/skills-ref-sources.md
    title: skills-ref/src/skills_ref/cli.py
  - id: skills-ref-readme
    resource: /references/skills-ref-sources.md
    title: skills-ref/README.md 安装说明
  - id: skills-ref-tests
    resource: /references/skills-ref-sources.md
    title: skills-ref/tests/ 行为锁定
---

# skills-ref CLI 实战：validate / read-properties / to-prompt

本例走通 skills-ref 参考实现的三个 CLI 子命令：`validate`（质量门禁）、`read-properties`（元数据读取）、`to-prompt`（Tier 1 目录生成）。三者共同覆盖了客户端集成指南中的全部程序化接触点（见 [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md)）。

**定位先声明**：README 顶部 IMPORTANT 注记 "This library is intended for demonstration purposes only. It is not meant to be used in production."——它是架构样本，不是生产 SDK（F-054）。

## 安装

包元数据：`skills-ref` 0.1.0，`requires-python = ">=3.11"`，依赖 `click>=8.0` 与 `strictyaml>=1.7.3`；`[project.scripts]` 定义入口 `skills-ref = "skills_ref.cli:main"`（F-053）。

```bash
# macOS / Linux
pip install -e .
# 或
uv sync

# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .

# Windows cmd
.venv\Scripts\activate.bat
pip install -e .
```

安装后 `skills-ref` 可执行文件在激活的虚拟环境 PATH 上可用（F-054）。验证版本：

```bash
skills-ref --version
skills-ref --help   # docstring: Reference library for Agent Skills
```

准备两个技能目录用于演练（可用 [/examples/01-first-skill-roll-dice.md](/examples/01-first-skill-roll-dice.md) 创建的 `roll-dice`）。

## 子命令 1：validate（质量门禁）

**用法**：`skills-ref validate <skill_path>`；参数可为技能目录，也可直接指向 SKILL.md 文件（内部 `_is_skill_md_file` 判定后替换为其父目录）（F-063、F-064）。

```bash
# 校验通过：stdout 输出，退出码 0
$ skills-ref validate .agents/skills/roll-dice
Valid skill: .agents/skills/roll-dice

# 指向 SKILL.md 文件也可以（自动替换为父目录）
$ skills-ref validate .agents/skills/roll-dice/SKILL.md
Valid skill: .agents/skills/roll-dice
```

校验失败示例（把 name 改成 70 个字符后）：

```bash
$ skills-ref validate .agents/skills/roll-dice
Validation failed for .agents/skills/roll-dice:      # ← 输出到 stderr
  - Skill name 'aaa...' exceeds 64 character limit (70 chars)
$ echo $?
1                                                      # ← 退出码 1
```

**退出码约定**（F-064）：0 = 有效；1 = 存在校验错误。这使其可直接用于 CI 门禁：

```bash
skills-ref validate .agents/skills/roll-dice || echo "skill 格式不合格，阻断合并"
```

校验内容对应 `validate()` 的完整规则链（路径存在 → 是目录 → 有 SKILL.md → frontmatter 可解析 → 六字段白名单 → name 五规则 + 目录匹配 → description/compatibility 上限），错误消息清单见 [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md)。

## 子命令 2：read-properties（读取元数据）

**用法**：`skills-ref read-properties <skill_path>`；输出 `json.dumps(props.to_dict(), indent=2)` 的格式化 JSON（F-064）。

```bash
$ skills-ref read-properties .agents/skills/roll-dice
{
  "name": "roll-dice",
  "description": "Roll a random dice roll. Use when the user asks for a dice roll..."
}
```

序列化规则（F-056）：None 字段被剔除（上例没有 license/compatibility/allowed-tools）；`allowed_tools` 输出键名为连字符形式 `"allowed-tools"`；空 metadata 整体省略。一个带全字段的技能输出：

```json
{
  "name": "pdf-tools",
  "description": "PDF extraction and form filling. Use when working with PDFs.",
  "license": "Proprietary. LICENSE.txt has complete terms",
  "compatibility": "Requires Python 3.11+ and uv",
  "allowed-tools": "Bash(git:*) Bash(jq:*) Read",
  "metadata": {"author": "example-org", "version": "1.0"}
}
```

注意 metadata 的值经 parser 强制字符串化——YAML 数值 `1.0` 读出后是字符串 `"1.0"`（F-065 测试锁定的行为）。

**失败行为**：解析失败（如 frontmatter 不存在）时捕获 `SkillError`，stderr 输出 `Error: {e}`，退出码 1（F-064）：

```bash
$ skills-ref read-properties ./broken-skill
Error: SKILL.md must start with YAML frontmatter (---)
$ echo $?
1
```

**退出码约定**：0 成功 / 1 解析错误。

## 子命令 3：to-prompt（生成技能目录 XML）

**用法**：`skills-ref to-prompt <skill_paths...>`；接受**一个或多个**技能路径（`nargs=-1, required=True`），输出可直接嵌入系统提示词的 `<available_skills>` XML（F-064）：

```bash
$ skills-ref to-prompt .agents/skills/roll-dice .agents/skills/pdf-tools
<available_skills>
<skill>
<name>roll-dice</name>
<description>Roll a random dice roll. Use when the user asks for a dice roll...</description>
<location>/abs/path/to/.agents/skills/roll-dice/SKILL.md</location>
</skill>
<skill>
<name>pdf-tools</name>
<description>PDF extraction and form filling. Use when working with PDFs.</description>
<location>/abs/path/to/.agents/skills/pdf-tools/SKILL.md</location>
</skill>
</available_skills>
```

行为细节（F-062、F-066 测试锁定）：

- 空路径列表理论上输出 `"<available_skills>\n</available_skills>"`（CLI 因 `required=True` 不会收到空列表，该分支由库 API `to_prompt([])` 提供）；
- `location` 是 SKILL.md 的**绝对路径**（内部先 `resolve()`）；
- `name` 与 `description` 经 `html.escape` 转义——description 含 `<foo> & <bar>` 时输出 `&lt;foo&gt;`、`&amp;`、`&lt;bar&gt;`，不含裸 XML 标签；`location` 不转义；
- XML 格式是 "what Anthropic uses and recommends for Claude models"，其他客户端可自行格式化（F-062 docstring 声明）。

`location` 的用途：支撑文件读取式激活 + 给模型解析相对引用提供基路径（F-049）。

## 三子命令速查表

| 子命令 | 参数形态 | stdout | stderr | 退出码 |
|---|---|---|---|---|
| `validate` | 单路径（目录或 SKILL.md 文件） | `Valid skill: {path}` | `Validation failed for {path}:` + 缩进错误列表 | 0 / 1 |
| `read-properties` | 单路径 | 格式化 JSON（`to_dict()`） | `Error: {e}` | 0 / 1 |
| `to-prompt` | 多路径（≥1，必填） | `<available_skills>` XML | `Error: {e}` | 0 / 1 |

三者对"参数直接指向 SKILL.md 文件"均做了容错（替换为其父目录）（F-063）。

## 相关概念

- [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md) —— 三子命令背后的 API 与错误风格
- [/concepts/02-frontmatter-fields.md](/concepts/02-frontmatter-fields.md) —— validate 检查的字段规则
- [/concepts/06-client-integration.md](/concepts/06-client-integration.md) —— to-prompt 输出在披露层的角色
- [/examples/01-first-skill-roll-dice.md](/examples/01-first-skill-roll-dice.md) —— 被校验对象 roll-dice 的创建过程
