---
type: Concept
title: Frontmatter 全字段规范：规范约束与校验器实现对照
description: SKILL.md 六个 YAML frontmatter 字段的逐项规范约束，与 skills-ref 校验器实现规则的双栏对照——name 五条规则、description ≤1024、compatibility ≤500、metadata 白名单、allowed-tools 实验性。
tags: [agent-skills, skill-format, frontmatter, yaml, validation, specification]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: spec-mdx
    resource: /references/spec-sources.md
    title: docs/specification.mdx Frontmatter 字段表
  - id: skills-ref-validator
    resource: /references/skills-ref-sources.md
    title: skills-ref/src/skills_ref/validator.py 校验规则
---

# Frontmatter 全字段规范：规范约束与校验器实现对照

`SKILL.md` 必须以 YAML frontmatter 开头（F-003）。规范定义了**恰好六个**允许的字段（F-004）：两个必填（`name`、`description`），四个可选（`license`、`compatibility`、`metadata`、`allowed-tools`）。本文逐字段给出规范约束，并与 skills-ref 校验器的实现规则双栏对照——两者基本一致，但在 name 的字符集上存在一个值得注意的差异（规范文本写 "a-z, 0-9"，实现用 `isalnum()` 接受全 Unicode 小写字母，F-059/F-068）。

## 字段总表

| 字段 | 必填 | 规范约束 | skills-ref 校验器规则 |
|---|---|---|---|
| `name` | ✅ | 1-64 字符；unicode 小写字母数字与连字符；不以连字符开头/结尾；无连续连字符；必须与父目录名一致（F-004、F-005） | `MAX_SKILL_NAME_LENGTH = 64`；NFKC 归一化后检查六类失败 + 目录名匹配；`isalnum()` 字符集（F-059） |
| `description` | ✅ | 1-1024 字符；同时描述 what 与 when；含触发关键词（F-004、F-007） | `MAX_DESCRIPTION_LENGTH = 1024`；非空 str + 长度上限，消息 "Description exceeds 1024 character limit (N chars)"（F-060） |
| `license` | 可选 | 许可证名称或捆绑许可证文件名；建议简短（F-008） | 不做内容校验（仅在字段白名单内即可） |
| `compatibility` | 可选 | 1-500 字符；环境要求（product、system packages、network access）（F-004、F-008） | `MAX_COMPATIBILITY_LENGTH = 500`；非 str → "Field 'compatibility' must be a string"，超长 → "Compatibility exceeds 500 character limit (N chars)"（F-060） |
| `metadata` | 可选 | 字符串键到字符串值的映射；键名建议 reasonably unique（F-009） | 值经 parser 强制 `str()` 化；白名单外的顶层字段报 "Unexpected fields in frontmatter: ..."（F-057、F-060） |
| `allowed-tools` | 可选（Experimental） | 空格分隔的预批准工具列表；"Support for this field may vary between agent implementations"（F-009） | 不做内容校验，仅要求在白名单内（F-060） |

白名单定义于校验器常量 `ALLOWED_FIELDS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}`，注释标注 "Allowed frontmatter fields per Agent Skills Spec"（F-059）。任何白名单外字段报错 "Unexpected fields in frontmatter: X, Y. Only [...] are allowed."（字段名排序输出，F-060）。

## name：五条规则与实现细节

规范约束（F-005、F-006）：

1. 长度 1-64 字符。
2. 只允许 unicode 小写字母数字（`a-z`、`0-9`）和连字符（`-`）。
3. 不得以连字符开头或结尾。
4. 不得包含连续连字符（`--`）。
5. 必须与父目录名一致（must match the parent directory name）。

合法示例：`pdf-processing`、`data-analysis`、`code-review`；非法示例：`PDF-Processing`（大写）、`-pdf`（连字符开头）、`pdf--processing`（连续连字符）（F-006）。

skills-ref 校验器的实现序列（F-059）：先做空/非 str/strip 后为空的短路检查（"Field 'name' must be a non-empty string"），随后 `unicodedata.normalize("NFKC", name.strip())` 归一化，再依次检查长度、小写、连字符两端、连续连字符、非法字符，最后将同样 NFKC 归一化的目录名与 name 比较（不等 → "Directory name 'X' must match skill name 'Y'"）。

**i18n 差异点**：校验器 docstring 写 "Skill names support i18n characters (Unicode letters) plus hyphens"，`isalnum()` 使中文（`技能`）、俄文（`мой-навык`）名称可通过校验（F-068 锁定的测试行为）；但大写仍被拒绝。规范文本的 "a-z, 0-9" 与实现的三方差异以测试目录为最精确的行为记录（F-059、F-068）——写技能时建议仍按规范的 ASCII kebab-case 保守行事，跨客户端兼容性最好。

## description：1024 字符内的路由函数

- 约束：1-1024 字符（F-007）。
- 应同时描述技能做什么（what）与何时使用（when）。
- 应包含帮助智能体识别相关任务的具体关键词。
- 规范差例："Helps with PDFs."（过于模糊）；好例："Extracts text and tables from PDF files... Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction."（F-007）。

description 是渐进式披露第一层唯一的内容，触发优化的完整方法论见 [/concepts/05-description-optimization.md](/concepts/05-description-optimization.md)。

## 三个低频字段

**license**（F-008）：可选；指定技能适用的许可证；规范建议保持简短（许可证名称或捆绑许可证文件的名称），示例 `license: Proprietary. LICENSE.txt has complete terms`。

**compatibility**（F-008）：可选；1-500 字符；内容为环境要求（intended product、system packages、network access 等），示例 `Requires git, docker, jq, and access to the internet`、`Requires Python 3.14+ and uv`。规范附 Note："Most skills do not need the `compatibility` field."（大多数技能不需要此字段）。

**metadata**（F-009）：可选；字符串键到字符串值的映射；客户端可在此存放规范未定义的附加属性；键名建议取得 reasonably unique 以避免意外冲突；示例 `metadata: {author: example-org, version: "1.0"}`。skills-ref 的 parser 会把 metadata 的值强制转为字符串——YAML 数值 `1.0` 读出后是字符串 `"1.0"`（F-057、F-065 锁定的行为）。

## allowed-tools：唯一的实验性字段

以空格分隔的字符串列出预先批准（pre-approved）运行的工具（F-009）：

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

规范明确标注其为 Experimental（实验性）："Support for this field may vary between agent implementations"——各实现的支持度不一，使用前应确认目标客户端行为。

## 校验的两种严格度

同一份 frontmatter，在两个场景下会遇到不同严格度（这是有意设计的两极，详见 [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md)）：

- **严格校验（CI 门禁）**：`skills-ref validate` 拒绝一切白名单外字段、强制 name 与目录名 NFKC 一致（F-059 ~ F-061）。
- **宽松校验（客户端加载）**：name 不匹配/超长 → 警告但加载；仅 description 缺失或 YAML 完全不可解析 → 跳过（F-047）。

## 相关概念

- [/concepts/00-skill-anatomy.md](/concepts/00-skill-anatomy.md) —— 字段所在的文件骨架
- [/concepts/05-description-optimization.md](/concepts/05-description-optimization.md) —— description 字段的深度优化
- [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md) —— 校验器完整 API 与错误消息
- [/references/spec-sources.md](/references/spec-sources.md) —— 字段表的原始信源
