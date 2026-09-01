---
type: Reference
title: skills-ref 源码与测试信源登记
description: 登记 skills-ref 参考实现库的 12 个源码/测试/配置信源文件，逐个记录模块职责、公开与私有 API 签名、异常类型及被 40 个测试锁定的行为，标注对应事实编号段。
tags: [agent-skills, skills-ref, python, sources, api, provenance]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: skills-ref-parser
    resource: /references/skills-ref-sources.md
    title: skills-ref/src/skills_ref/parser.py
  - id: skills-ref-validator
    resource: /references/skills-ref-sources.md
    title: skills-ref/src/skills_ref/validator.py
  - id: skills-ref-cli
    resource: /references/skills-ref-sources.md
    title: skills-ref/src/skills_ref/cli.py
---

# skills-ref 源码与测试信源登记

本文件登记 skills-ref 参考实现库的全部信源文件（共 12 个：包配置 1、README 1、源码模块 7、测试文件 3），信源均位于 `external/libs/ai/agentskills/agentskills/skills-ref/`。skills-ref 是 Agent Skills 开放标准的 Python 参考实现（demonstration artifact，非 production SDK，见 F-001 / F-054），以 8 个模块合计 536 行（非空 398 行）Python 代码覆盖客户端集成的三个程序化接触点：元数据读取、Tier 1 目录生成、质量门禁。

API 边界与裁决声明：公开 API 由 `__init__.py` 的 `__all__` 定义（8 个符号，F-055）；`_validate_name` 等下划线前缀函数为内部实现。仓库 AGENTS.md 明确 skills-ref 不构成格式需求的来源（F-001）——本文档登记的 API 行为仅作架构样本参考。

## 信源总表

| # | 信源文件（相对 skills-ref/） | 模块职责 | 支撑事实 |
|---|---|---|---|
| 1 | `pyproject.toml` | 包元数据与构建配置 | F-053 |
| 2 | `README.md` | 安装与定位声明 | F-054 |
| 3 | `src/skills_ref/__init__.py` | 公开 API 出口 | F-055 |
| 4 | `src/skills_ref/errors.py` | 异常层级 | F-056 |
| 5 | `src/skills_ref/models.py` | 数据模型 | F-056 |
| 6 | `src/skills_ref/parser.py` | 发现与解析 | F-057 ~ F-058 |
| 7 | `src/skills_ref/validator.py` | 严格校验 | F-059 ~ F-061 |
| 8 | `src/skills_ref/prompt.py` | XML 目录生成 | F-062 |
| 9 | `src/skills_ref/cli.py` | 命令行接口 | F-063 ~ F-064 |
| 10 | `tests/test_parser.py` | 解析行为锁定（15 测试） | F-065 |
| 11 | `tests/test_prompt.py` | XML 输出锁定（4 测试） | F-066 |
| 12 | `tests/test_validator.py` | 校验行为锁定（21 测试） | F-067 ~ F-068 |

## 逐文件登记

### 1. pyproject.toml

包元数据：`name = "skills-ref"`，`version = "0.1.0"`，description "Reference library for Agent Skills"，license Apache-2.0，作者 Keith Lazuka（Anthropic）；`requires-python = ">=3.11"`；运行依赖 `click>=8.0` 与 `strictyaml>=1.7.3`；`[project.scripts]` 定义 CLI 入口 `skills-ref = "skills_ref.cli:main"`；构建后端 hatchling（wheel 打包 `src/skills_ref`）；dev 依赖组 `pytest>=7.0`、`ruff>=0.8.0`。→ F-053

### 2. README.md

顶部 IMPORTANT 注记："This library is intended for demonstration purposes only. It is not meant to be used in production."；给出 macOS/Linux/Windows 三套安装说明（`pip install -e .` 或 `uv sync`，Windows 含 PowerShell 与 cmd 两种激活命令）；声明安装后 `skills-ref` 可执行文件在激活的虚拟环境 PATH 上可用。→ F-054

### 3. src/skills_ref/__init__.py

公开 API 出口。`__all__` 导出 8 个符号：`SkillError`、`ParseError`、`ValidationError`、`SkillProperties`、`find_skill_md`、`validate`、`read_properties`、`to_prompt`；`__version__ = "0.1.0"`。这 8 个符号构成参考实现的完整公开接口面。→ F-055

### 4. src/skills_ref/errors.py

异常层级：`SkillError(Exception)` 为所有技能相关错误的基类；`ParseError(SkillError)` 在 SKILL.md 解析失败时抛出；`ValidationError(SkillError)` 构造签名为 `__init__(self, message: str, errors: list[str] | None = None)`，属性 `self.errors` 未提供时默认 `[message]`。→ F-056

### 5. src/skills_ref/models.py

数据模型：`SkillProperties` 为 dataclass，字段 `name: str`、`description: str`、`license: Optional[str] = None`、`compatibility: Optional[str] = None`、`allowed_tools: Optional[str] = None`、`metadata: dict[str, str] = field(default_factory=dict)`。`to_dict()` 序列化规则：排除 None 值；`allowed_tools` 输出键名为连字符形式 `"allowed-tools"`；`metadata` 为空 dict 时整体省略。→ F-056

### 6. src/skills_ref/parser.py

发现与解析模块，三个函数：

```python
def find_skill_md(skill_dir: Path) -> Optional[Path]
def parse_frontmatter(content: str) -> tuple[dict, str]
def read_properties(skill_dir: Path) -> SkillProperties
```

- `find_skill_md`：依次检查 `SKILL.md` 与 `skill.md`（大写优先），存在则返回路径，均不存在返回 `None`；docstring "Prefers SKILL.md (uppercase) but accepts skill.md (lowercase)"。→ F-057
- `parse_frontmatter`：四类 `ParseError`——①内容不以 `---` 开头 → "SKILL.md must start with YAML frontmatter (---)"；②`content.split("---", 2)` 少于 3 段 → "SKILL.md frontmatter not properly closed with ---"；③`strictyaml.YAMLError` 包装为 `ParseError(f"Invalid YAML in frontmatter: {e}")`；④解析结果非 dict → "SKILL.md frontmatter must be a YAML mapping"。frontmatter 经 `strictyaml.load` 解析（YAML 子集，无类型注入面）；若存在键 `metadata` 且为 dict，整体转换为 `{str(k): str(v) for k, v in ...}`（值强制字符串化）。→ F-057
- `read_properties`：`find_skill_md` 返回 None → `ParseError(f"SKILL.md not found in {skill_dir}")`；缺 `name`/`description` → `ValidationError("Missing required field in frontmatter: name")`（description 同理）；非字符串或 strip 后为空 → `ValidationError("Field 'name' must be a non-empty string")`（description 同理）；返回 `SkillProperties(name=name.strip(), description=description.strip(), license=metadata.get("license"), compatibility=metadata.get("compatibility"), allowed_tools=metadata.get("allowed-tools"), metadata=metadata.get("metadata"))`；docstring 明确 "It does NOT perform full validation. Use validate() for that."。→ F-058

### 7. src/skills_ref/validator.py

严格校验模块。模块级常量（源码 L10-L15）：`MAX_SKILL_NAME_LENGTH = 64`、`MAX_DESCRIPTION_LENGTH = 1024`、`MAX_COMPATIBILITY_LENGTH = 500`；`ALLOWED_FIELDS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}`。

公开与核心函数：

```python
def validate(skill_dir: Path) -> list[str]                                    # L150
def validate_metadata(metadata: dict, skill_dir: Optional[Path] = None) -> list[str]  # L118
```

内部校验函数：

```python
def _validate_name(name: str, skill_dir: Path) -> list[str]     # L25
def _validate_description(description: str) -> list[str]        # L70
def _validate_compatibility(compatibility: str) -> list[str]    # L87
def _validate_metadata_fields(metadata: dict) -> list[str]      # L104
```

- `_validate_name` 校验序列：空/非 str/strip 后为空 → "Field 'name' must be a non-empty string"（短路返回）；随后 `unicodedata.normalize("NFKC", name.strip())` 归一化，依次检查——长度 >64 → "exceeds 64 character limit (N chars)"；`name != name.lower()` → "must be lowercase"；以 `-` 开头或结尾 → "cannot start or end with a hyphen"；含 `--` → "cannot contain consecutive hyphens"；存在字符既非 `isalnum()` 也非 `-` → "contains invalid characters. Only letters, digits, and hyphens are allowed."；传入 skill_dir 时目录名同样 NFKC 归一化后与 name 比较，不等 → "Directory name 'X' must match skill name 'Y'"；docstring "Skill names support i18n characters (Unicode letters) plus hyphens."（注意：`isalnum()` 接受全 Unicode 小写字母，比规范文本的 "a-z, 0-9" 宽，F-068 测试锁定此行为）。→ F-059
- `_validate_description`：非空 str 检查 + 长度 >1024 → "Description exceeds 1024 character limit (N chars)"。`_validate_compatibility`：非 str → "Field 'compatibility' must be a string"，长度 >500 → "Compatibility exceeds 500 character limit (N chars)"。`_validate_metadata_fields`：`set(metadata.keys()) - ALLOWED_FIELDS` 非空 → "Unexpected fields in frontmatter: X, Y. Only [...] are allowed."（字段名排序输出）。→ F-060
- `validate_metadata`：核心校验函数，作用于已解析的 metadata（docstring：避免从 parser 调用时重复文件 I/O），顺序为未知字段 → `name`（缺失 → "Missing required field in frontmatter: name"）→ `description`（同构）→ `compatibility`（存在才校验）。→ F-060
- `validate` 四个早退分支：路径不存在 → `["Path does not exist: {skill_dir}"]`；不是目录 → `["Not a directory: {skill_dir}"]`；`find_skill_md` 为 None → `["Missing required file: SKILL.md"]`；`parse_frontmatter` 抛 `ParseError` → `[str(e)]`；全部通过则返回 `validate_metadata(metadata, skill_dir)`。返回错误消息列表，空列表表示有效。→ F-061

### 8. src/skills_ref/prompt.py

Tier 1 目录生成模块，单函数：

```python
def to_prompt(skill_dirs: list[Path]) -> str   # L9
```

空列表返回字面量 `"<available_skills>\n</available_skills>"`；非空时对每个目录执行 `Path(skill_dir).resolve()` → `read_properties` → 追加行 `<skill>`、`<name>`、`html.escape(props.name)`、`</name>`、`<description>`、`html.escape(props.description)`、`</description>`、`<location>`、`str(find_skill_md(skill_dir))`、`</location>`、`</skill>`，最后追加 `</available_skills>`，以 `"\n".join` 拼接。docstring 声明 "This XML format is what Anthropic uses and recommends for Claude models. Skill Clients may format skill information differently to suit their models or preferences."。注意：name/description 走 `html.escape` 而 location 不转义。→ F-062

### 9. src/skills_ref/cli.py

click 命令行接口。骨架：`@click.group()` + `@click.version_option()` 的 `main()`（docstring "Reference library for Agent Skills"）；模块级辅助函数 `_is_skill_md_file(path: Path) -> bool`（L15）判定"路径直接指向 SKILL.md 或 skill.md 文件"（`path.is_file() and path.name.lower() == "skill.md"`）；三个子命令在参数为 SKILL.md 文件时均先替换为其父目录。→ F-063

三个子命令（退出码约定见各 docstring）：

| 子命令 | 参数 | 成功输出 | 失败行为 |
|---|---|---|---|
| `validate` | `skill_path`（`click.Path(exists=True, path_type=Path)`） | stdout `Valid skill: {path}` | stderr `Validation failed for {path}:` + 每条 `  - {error}`，`sys.exit(1)`；退出码 0 有效 / 1 校验错误 |
| `read-properties` | `skill_path` | stdout `json.dumps(props.to_dict(), indent=2)` | 捕获 `SkillError` → stderr `Error: {e}` + exit 1；退出码 0 成功 / 1 解析错误 |
| `to-prompt` | `skill_paths`（`nargs=-1, required=True` 多路径） | stdout XML（`click.echo` 输出 `to_prompt` 结果） | `SkillError` → stderr + exit 1 |

→ F-064

### 10. tests/test_parser.py

15 个测试锁定解析行为：合法 frontmatter 解析出 metadata dict 与含 `# My Skill` 的 body；无 frontmatter → `ParseError` 匹配 "must start with YAML frontmatter"；未闭合 → "not properly closed"；`name: [invalid` → "Invalid YAML"；YAML 列表 → "must be a YAML mapping"；`read_properties` 读出 name/description/license、嵌套 metadata、`allowed-tools` 字符串 `"Bash(jq:*) Bash(git:*)"`；缺 SKILL.md → "SKILL.md not found"；缺 name/description → `ValidationError` 匹配 "Missing required field.*name"；`find_skill_md` 大写优先、仅小写时接受、均无返回 `None`；`read_properties` 可用小写 `skill.md` 工作；YAML 数值 `version: 1.0` 经读取后为字符串 `"1.0"`（metadata 值字符串化）；`to_dict()` 输出连字符键 `d["allowed-tools"]`。→ F-065

### 11. tests/test_prompt.py

4 个测试锁定 to_prompt 行为：空列表输出恰好 `"<available_skills>\n</available_skills>"`；单技能输出含 `<name>\nmy-skill\n</name>` 与 `<description>\nA test skill\n</description>` 的换行包裹格式及含 `SKILL.md` 的 `<location>`；双技能时 `result.count("<skill>") == 2`；XML 特殊字符转义——description 含 `<foo> & <bar>` 时输出含 `&lt;foo&gt;`、`&amp;`、`&lt;bar&gt;` 且不含裸 `<foo>`/`<bar>`。→ F-066

### 12. tests/test_validator.py

21 个测试锁定校验行为：合法技能 `errors == []`；不存在路径 → 含 "does not exist"；文件路径 → "Not a directory"；缺 SKILL.md → "Missing required file: SKILL.md"；name 五类失败（大写 → "lowercase"；70 字符 → "exceeds"+"character limit"；`-my-skill` → "cannot start or end with a hyphen"；`my--skill` → "consecutive hyphens"；`my_skill` → "invalid characters"）；目录名不匹配 → "must match skill name"；未知字段 → "Unexpected fields"；license+metadata 齐全 → `[]`；`allowed-tools: Bash(jq:*) Bash(git:*)` 被接受 → `[]`；description 1100 字符 → "exceeds"+"1024"；compatibility 550 字符 → "exceeds"+"500"。i18n 与 NFKC：中文 `技能`、俄文 `мой-навык` 通过 → `[]`；大写 `НАВЫК` → "lowercase"；分解形 `cafe\u0301`（name）与预组合形 `café`（目录名）经 NFKC 归一化后 `errors == []`。→ F-067 ~ F-068

## 相关概念

- [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md) —— 本登记表源码的架构解读
- [/concepts/02-frontmatter-fields.md](/concepts/02-frontmatter-fields.md) —— validator 校验规则与规范约束的双栏对照
- [/references/spec-sources.md](/references/spec-sources.md) —— 规范文档类信源登记
- [/examples/02-skills-ref-cli.md](/examples/02-skills-ref-cli.md) —— 三个 CLI 子命令的实战演练
