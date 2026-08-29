---
type: Concept
title: skills-ref 参考实现：最小完整闭环的架构样本
description: skills-ref 参考库的架构解读——8 个公开 API 签名、validator 校验规则与错误消息、parser 四类 ParseError、CLI 三子命令、to_prompt XML 结构与 html.escape、校验/读取两种错误风格分工。
tags: [agent-skills, skills-ref, python, api, architecture, validation, cli]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: skills-ref-init
    resource: /references/skills-ref-sources.md
    title: skills-ref/src/skills_ref/__init__.py
  - id: skills-ref-parser
    resource: /references/skills-ref-sources.md
    title: skills-ref/src/skills_ref/parser.py
  - id: skills-ref-validator
    resource: /references/skills-ref-sources.md
    title: skills-ref/src/skills_ref/validator.py
---

# skills-ref 参考实现：最小完整闭环的架构样本

skills-ref 是 Agent Skills 开放标准的 Python 参考实现（版本 0.1.0，Apache-2.0，作者 Keith Lazuka / Anthropic；F-053），以 8 个模块合计 536 行（非空 398 行）完整覆盖客户端集成的三个程序化接触点：发现后的元数据读取、Tier 1 目录生成、质量门禁。定位声明："This library is intended for demonstration purposes only. It is not meant to be used in production."（F-054）；仓库 AGENTS.md 进一步声明它是 demonstration artifact，不构成格式需求的来源（F-001）——因此本文档把它当作**自研 Skill 客户端的接口设计模板**来解读，而非规范性 SDK。

## 公开 API 全景

`__init__.py` 的 `__all__` 导出 8 个符号（F-055）：

```python
__all__ = [
    "SkillError",
    "ParseError",
    "ValidationError",
    "SkillProperties",
    "find_skill_md",
    "validate",
    "read_properties",
    "to_prompt",
]
__version__ = "0.1.0"
```

签名总表（均已对照源码验证）：

| 符号 | 签名 | 模块 |
|---|---|---|
| `SkillError` | `class SkillError(Exception)` | errors.py |
| `ParseError` | `class ParseError(SkillError)` | errors.py |
| `ValidationError` | `__init__(self, message: str, errors: list[str] \| None = None)`；`self.errors` 未提供时默认 `[message]` | errors.py |
| `SkillProperties` | dataclass：`name: str`、`description: str`、`license: Optional[str] = None`、`compatibility: Optional[str] = None`、`allowed_tools: Optional[str] = None`、`metadata: dict[str, str] = field(default_factory=dict)` | models.py |
| `find_skill_md` | `(skill_dir: Path) -> Optional[Path]` | parser.py |
| `read_properties` | `(skill_dir: Path) -> SkillProperties` | parser.py |
| `validate` | `(skill_dir: Path) -> list[str]` | validator.py |
| `to_prompt` | `(skill_dirs: list[Path]) -> str` | prompt.py |

另有内部函数 `parse_frontmatter(content: str) -> tuple[dict, str]` 与 `validate_metadata(metadata: dict, skill_dir: Optional[Path] = None) -> list[str]`，以及四个 `_validate_*` 私有校验函数。

## parser：发现与解析

**`find_skill_md(skill_dir)`**（F-057）：依次检查 `SKILL.md` 与 `skill.md`（大写优先），存在返回路径，均不存在返回 `None`；docstring "Prefers SKILL.md (uppercase) but accepts skill.md (lowercase)"。

**`parse_frontmatter(content)`**（F-057）：frontmatter 用 `strictyaml.load` 解析（YAML 子集，无类型注入面）。四类 `ParseError`：

| 触发条件 | 错误消息 |
|---|---|
| 内容不以 `---` 开头 | `SKILL.md must start with YAML frontmatter (---)` |
| `content.split("---", 2)` 少于 3 段 | `SKILL.md frontmatter not properly closed with ---` |
| `strictyaml.YAMLError` | `Invalid YAML in frontmatter: {e}` |
| 解析结果非 dict | `SKILL.md frontmatter must be a YAML mapping` |

若存在键 `metadata` 且为 dict，整体转换为 `{str(k): str(v) for k, v in ...}`（值强制字符串化——YAML 数值 `1.0` 读出后是字符串 `"1.0"`，该行为由测试锁定而非文档记录，F-065）。

**`read_properties(skill_dir)`**（F-058）：职责是"读取"而非"校验"——docstring 明确 "It does NOT perform full validation. Use validate() for that."。失败路径：缺 SKILL.md → `ParseError(f"SKILL.md not found in {skill_dir}")`；缺 `name`/`description` → `ValidationError("Missing required field in frontmatter: name")`；非字符串或 strip 后为空 → `ValidationError("Field 'name' must be a non-empty string")`。返回的 `SkillProperties` 从 metadata 的扁平键取 `license`/`compatibility`/`allowed-tools`，嵌套键取 `metadata`。

**`SkillProperties.to_dict()` 序列化规则**（F-056）：排除 None 值；`allowed_tools` 输出键名为连字符形式 `"allowed-tools"`；`metadata` 为空 dict 时整体省略。

## validator：严格校验

模块级常量（F-059）：`MAX_SKILL_NAME_LENGTH = 64`、`MAX_DESCRIPTION_LENGTH = 1024`、`MAX_COMPATIBILITY_LENGTH = 500`、`ALLOWED_FIELDS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}`。

**`_validate_name(name, skill_dir)` 校验序列**（F-059）：空/非 str/strip 后为空 → "Field 'name' must be a non-empty string"（短路返回）；随后 `unicodedata.normalize("NFKC", name.strip())` 归一化，依次检查——

| 检查 | 错误消息 |
|---|---|
| 长度 >64 | `Skill name '{name}' exceeds 64 character limit (N chars)` |
| `name != name.lower()` | `must be lowercase` |
| 以 `-` 开头或结尾 | `cannot start or end with a hyphen` |
| 含 `--` | `cannot contain consecutive hyphens` |
| 存在字符既非 `isalnum()` 也非 `-` | `contains invalid characters. Only letters, digits, and hyphens are allowed.` |
| 目录名（同样 NFKC 归一化）与 name 不等 | `Directory name 'X' must match skill name 'Y'` |

docstring "Skill names support i18n characters (Unicode letters) plus hyphens."——`isalnum()` 使中文 `技能`、俄文 `мой-навык` 通过校验（F-068 测试锁定），比规范文本的 "a-z, 0-9" 宽半步（三方差异分析见 [/concepts/02-frontmatter-fields.md](/concepts/02-frontmatter-fields.md)）。

**其余校验函数**（F-060）：`_validate_description`（>1024 → "Description exceeds 1024 character limit (N chars)"）；`_validate_compatibility`（非 str → "Field 'compatibility' must be a string"；>500 → "Compatibility exceeds 500 character limit (N chars)"）；`_validate_metadata_fields`（白名单外字段 → "Unexpected fields in frontmatter: X, Y. Only [...] are allowed."，字段名排序输出）。

**`validate_metadata`**：核心校验函数，作用于已解析的 metadata（docstring：避免从 parser 调用时重复文件 I/O），顺序为未知字段 → `name` 缺失 → `description` 缺失 → `compatibility`（存在才校验）。

**`validate(skill_dir)`**（F-061）：四个早退分支——路径不存在 → `["Path does not exist: {skill_dir}"]`；不是目录 → `["Not a directory: {skill_dir}"]`；`find_skill_md` 为 None → `["Missing required file: SKILL.md"]`；`parse_frontmatter` 抛 `ParseError` → `[str(e)]`；全部通过则返回 `validate_metadata(metadata, skill_dir)`。**返回错误消息列表，空列表表示有效**——不抛异常。

## prompt：Tier 1 目录生成

**`to_prompt(skill_dirs)`**（F-062）：空列表返回字面量 `"<available_skills>\n</available_skills>"`；非空时对每个目录 `resolve()` → `read_properties` → 逐行追加：

```xml
<available_skills>
<skill>
<name>pdf-reader</name>
<description>Read and extract text from PDF files</description>
<location>/path/to/pdf-reader/SKILL.md</location>
</skill>
</available_skills>
```

细节：`name` 与 `description` 经 `html.escape` 转义（description 含 `<foo> & <bar>` 时输出 `&lt;foo&gt;`、`&amp;`、`&lt;bar&gt;`，F-066 测试锁定），而 `location` 不转义；`location` 取 `str(find_skill_md(skill_dir))` 即 SKILL.md 的绝对路径。docstring 声明 "This XML format is what Anthropic uses and recommends for Claude models. Skill Clients may format skill information differently to suit their models or preferences."——官方参考实现主动放弃输出格式的规范性。

## cli：三个子命令

click 骨架：`@click.group()` + `@click.version_option()` 的 `main()`；辅助函数 `_is_skill_md_file(path)` 判定"路径直接指向 SKILL.md 或 skill.md 文件"（`path.is_file() and path.name.lower() == "skill.md"`）；三个子命令在参数为 SKILL.md 文件时均先替换为其父目录（F-063）。

| 子命令 | 参数 | 成功输出 | 失败行为 | 退出码 |
|---|---|---|---|---|
| `validate` | `skill_path` | stdout `Valid skill: {path}` | stderr `Validation failed for {path}:` + 每条 `  - {error}` | 0 有效 / 1 校验错误 |
| `read-properties` | `skill_path` | stdout `json.dumps(props.to_dict(), indent=2)` | 捕获 `SkillError` → stderr `Error: {e}` | 0 成功 / 1 解析错误 |
| `to-prompt` | `skill_paths`（`nargs=-1, required=True`） | stdout XML | `SkillError` → stderr | 0 成功 / 1 错误 |

（F-064；CLI 实战见 [/examples/02-skills-ref-cli.md](/examples/02-skills-ref-cli.md)。）

## 错误风格分工与测试锁定

同一库内两种错误风格按用途分工（与"统一抛异常"的常见直觉相反）：

- **校验 API 返回 `list[str]`**（空列表 = 有效）——面向 CI 聚合全部错误后一次性报告；
- **读取 API 抛异常**（`ParseError`/`ValidationError`）——面向快速失败。

40 个测试（parser 15 + prompt 4 + validator 21，F-065 ~ F-068）锁定了上述全部行为，包括 XML 转义、NFKC 归一化、i18n 名称与 metadata 值字符串化——测试目录是这套行为语义最精确的记录。

## 相关概念

- [/concepts/02-frontmatter-fields.md](/concepts/02-frontmatter-fields.md) —— 校验规则对应的规范约束
- [/concepts/06-client-integration.md](/concepts/06-client-integration.md) —— 三个接触点对应的客户端生命周期
- [/references/skills-ref-sources.md](/references/skills-ref-sources.md) —— 本文所有 API 的逐文件信源登记
- [/examples/02-skills-ref-cli.md](/examples/02-skills-ref-cli.md) —— 三个子命令的实战演练
