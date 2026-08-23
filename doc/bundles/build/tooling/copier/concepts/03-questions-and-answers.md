---
type: Concept
title: 问题与答案系统
description: Question 类、问题类型、条件显示、答案合并优先级、answers 文件、交互式问卷流程
tags: [copier, questions, answers, interactive, questionnaire, answers-map]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# 问题与答案系统

Copier 的问卷系统负责收集模板变量值，支持交互式 TUI（终端用户界面）和非交互式数据传递两种模式。答案来自多个数据源，按优先级合并。[^copier-source]

## AnswersMap：多源答案合并

`AnswersMap` 类（定义在 `_user_data.py`）管理来自不同来源的答案，通过 `ChainMap` 实现优先级合并：[^copier-source]

| 来源 | 属性 | 说明 | 优先级 |
|------|------|------|--------|
| 用户交互 | `user` | 通过 TUI 交互式输入的答案 | 最高 |
| 初始化数据 | `init` | `--data`/`--data-file` 传递的数据 | 高 |
| 用户默认 | `user_defaults` | 用户自定义默认值（覆盖模板默认） | 中高 |
| 上次答案 | `last` | 从 `.copier-answers.yml` 读取的上次答案 | 中 |
| 外部数据 | `external` | `_external_data` 定义的 YAML 文件（LazyDict） | 中低 |
| 元数据 | `metadata` | 模板元数据（`_src_path`/`_commit`） | 低 |
| 系统/初始化 | `system` | Worker 自动生成的上下文 | 最低 |

答案合并通过 `combined` 属性实现，高优先级覆盖低优先级。

### hidden 答案

标记为 `secret: true` 的问题或通过 `answers.hide(var_name)` 隐藏的变量，不会出现在最终的 answers 文件中。密钥类问题应始终标记为 secret。

## Question 类

每个问题在内部表示为 `Question` 对象（pydantic dataclass），包含以下核心能力：

- **答案解析**：`parse_answer(value)` 将用户输入转换为目标类型
- **答案验证**：`validate_answer(answer)` 运行验证器检查合法性
- **条件判断**：`get_when()` 判断当前问题是否应显示
- **默认值获取**：`get_default()` 获取渲染后的默认值（支持 MISSING 哨兵表示无默认值）
- **TUI 结构生成**：`get_questionary_structure()` 生成 questionary 库所需的提示结构

### 问题类型与解析

| 类型 | Python 类型 | 输入方式 | 说明 |
|------|------------|----------|------|
| `str` | `str` | 文本输入 | 默认类型 |
| `int` | `int` | 文本输入→自动转换 | 输入非整数会重新提示 |
| `float` | `float` | 文本输入→自动转换 | 同上 |
| `bool` | `bool` | Yes/No 确认 | y/N 选择 |
| `json` | `dict/list` | 多行文本→json.loads | 支持 Pygments 语法高亮 |
| `yaml` | `dict/list` | 多行文本→yaml.safe_load | 支持 Pygments 语法高亮 |
| `secret` | `str` | 密码输入（不回显） | 标记为 hidden，不存入答案文件 |

JSON/YAML 类型使用 prompt_toolkit 的 PygmentsLexer 提供实时语法高亮（JsonLexer/YamlLexer）。

## 交互式问卷流程

问卷流程在 `Worker._ask()` 方法中实现，执行以下步骤：

1. **初始化 AnswersMap**：合并 init/user_defaults/last/metadata/external 数据源
2. **遍历问题**：按 `copier.yml` 中的定义顺序逐个处理
3. **验证上次答案**：如果问题有 last 答案，尝试 parse+validate；失败则删除 last 答案
4. **条件判断**：调用 `question.get_when()` 判断是否跳过该问题
   - 跳过 → 调用 `answers.hide(var_name)` 隐藏，删除 last 答案
   - 无默认值（MISSING）→ 直接跳到下一个问题
5. **非交互路径检查**（按优先级）：
   - 用户通过 `--ask` 显式要求询问 → 进入交互模式
   - 答案在 `init` 数据中（`--data`/`--data-file`）→ parse+validate 后存入 user
   - `--skip-answered` 且有 last 答案 → 跳过
   - `--defaults` 模式 → 使用默认值（无默认值则抛 ValueError）
6. **交互询问**：通过 questionary 的 `unsafe_prompt()` 显示 TUI 提示
7. **重新加载外部数据**：外部数据可能依赖前面的答案，问卷结束后重新加载

### 跳过逻辑详解

问题是否被询问由以下条件决定（按优先级）：

```
1. --ask 匹配 glob 模式 → 强制询问
2. --data/--data-file 提供了值 → 使用该值，不询问
3. --skip-answered 且已有上次答案 → 跳过
4. --defaults → 使用默认值，不询问
5. when 条件为 false → 跳过（隐藏）
6. 以上都不满足 → 交互式询问
```

### Ctrl+C 中断处理

用户按 Ctrl+C 时，抛出 `CopierAnswersInterrupt` 异常，携带：
- `answers`：已收集的部分答案
- `last_question`：中断时正在回答的问题
- `template`：当前模板对象

调用方可以捕获此异常进行清理（如保存部分答案）。

## 答案文件（.copier-answers.yml）

答案文件记录了生成项目时使用的所有模板变量值和元数据，是 Copier 实现更新功能的关键。

### 自动生成的元数据字段

| 字段 | 说明 |
|------|------|
| `_src_path` | 模板源路径/URL |
| `_commit` | 使用的模板 commit（标签或 hash） |

这两个字段由 `_answers_to_remember()` 方法自动添加，是更新时定位原始模板的依据。

### 排除规则

以下答案**不会**写入答案文件：
- 以 `_` 开头的内部变量（除 `_commit`/`_src_path` 外）
- 被标记为 `hidden` 的问题（secret 问题、when 条件为 false 的问题）
- 不在 `template.questions_data` 中的键
- 非 JSON 可序列化的值（JSONSerializable = dict/list/str/int/float/bool/None）

### 自定义答案文件路径

通过以下方式自定义答案文件位置：
- CLI：`-a/--answers-file PATH`（相对 dst_path）
- API：`Worker(answers_file=...)`
- 模板配置：`_answers_file` 选项

答案文件路径本身也支持 Jinja2 模板渲染。

## 默认值渲染与模板上下文

问题的 `default` 值是 Jinja2 模板字符串，可以引用之前问题的答案。渲染时使用的上下文包含：

- 之前所有已回答问题的变量
- `_copier_conf`：Worker 配置对象（LazyDict）
- `_copier_phase`：当前执行阶段（Phase 枚举值）
- `_copier_python`：当前 Python 解释器路径
- `_folder_name`：目标目录名

### 条件渲染示例

```yaml
use_database:
  type: bool
  default: false
  help: "使用数据库？"

database_type:
  type: str
  choices: [postgresql, mysql, sqlite]
  default: postgresql
  when: "{{ use_database }}"

database_url:
  type: str
  default: "postgres://localhost/{{ project_name }}"
  when: "{{ use_database and database_type == 'postgresql' }}"
```

## 非交互式数据传递

### --data 选项

```bash
copier copy -d project_name=demo -d author_name=Bot template/ output/
```

`-d` 可多次指定，格式为 `KEY=VALUE`。注意：值始终作为字符串传递，由 Question 的类型解析器转换。

### --data-file 选项

```yaml
# answers.yml
project_name: demo
author_name: Bot
python_version: "3.12"
use_docker: true
```

```bash
copier copy --data-file answers.yml template/ output/
```

`--data-file` 的值会被 `--data` 覆盖（CLI 选项优先级更高）。

### --defaults 模式

使用模板定义的所有默认值，完全跳过交互式询问。适用于 CI/CD 场景。

```bash
copier copy --defaults --overwrite template/ output/
```

如果任何必填问题没有默认值，`--defaults` 会抛出 `ValueError: Question "xxx" is required`。

### --skip-answered

更新时跳过已有答案的问题，只询问新增的或上次未回答的问题：

```bash
copier update --skip-answered
```

### --ask 选项

强制询问匹配 glob 模式的问题，即使其他选项会跳过它们：

```bash
# 强制询问所有以 "db_" 开头的问题
copier update --ask "db_*"
```

## 相关概念

- [模板配置文件](02-template-configuration.md)
- [Worker 与生命周期](05-worker-and-lifecycle.md)
- [CLI 命令参考](08-cli-reference.md)
- [VCS 集成与版本管理](06-vcs-integration.md)
- [Copier 源码信源登记](/references/copier-source.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](/references/copier-source.md)。
