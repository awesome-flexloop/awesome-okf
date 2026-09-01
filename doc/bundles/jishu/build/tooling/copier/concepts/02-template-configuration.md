---
type: Concept
title: 模板配置文件 copier.yml
description: copier.yml 配置详解——配置项、问题定义、任务、迁移、排除规则、子目录、外部数据
tags: [copier, template-configuration, copier.yml, yaml, settings]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# 模板配置文件 copier.yml

`copier.yml`（或 `copier.yaml`）是 Copier 模板的核心配置文件，放置在模板根目录。它同时定义了**模板配置项**（以 `_` 开头）和**交互式问题**（其余键）。[^copier-source]

## 配置文件查找规则

Copier 在模板根目录查找 `copier.*` 文件：

- 查找 `copier.yml` 和 `copier.yaml`
- 如果同时存在两个文件，抛出 `MultipleConfigFilesError`
- 如果都不存在，使用空配置（无问题，纯文件复制模式）
- 支持 `!include` 标签引入其他 YAML 文件（glob 模式）

```yaml
# 使用 !include 引入其他配置文件
!include shared/common.yml
!include questions/*.yml
```

`!include` 的安全约束：
- 路径必须是相对路径（不能以 `/` 开头）
- 包含的文件必须在模板目录内（路径越界抛出 `ForbiddenPathError`）
- 支持 glob 模式匹配多个文件

## 配置项（以下划线 `_` 开头）

配置项控制模板的行为，不会作为问题向用户提问。

### 基础配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `_templates_suffix` | str | `.jinja` | 模板文件后缀，空字符串表示所有文件都作为模板渲染 |
| `_min_copier_version` | str | 无 | 要求的最低 Copier 版本（PEP440），如 `"9.0.0"` |
| `_answers_file` | str | `.copier-answers.yml` | 答案文件名（相对路径） |
| `_subdirectory` | str | `""` | 模板子目录，实际模板内容在该子目录下 |
| `_preserve_symlinks` | bool | `false` | 是否保留符号链接而非复制其内容 |

### 文件控制

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `_exclude` | list[str] | 见下方 | 排除的文件模式（gitignore 语法） |
| `_skip_if_exists` | list[str] | `[]` | 存在时跳过覆盖的文件模式（不询问） |
| `_secret_questions` | list[str] | `[]` | 标记为秘密的问题名（不存入答案文件） |

默认排除模式（`DEFAULT_EXCLUDE`）：
```yaml
_exclude:
  - "copier.yaml"
  - "copier.yml"
  - "~*"           # 备份文件
  - "*.py[co]"     # Python 编译文件
  - "__pycache__"
  - ".git"
  - ".DS_Store"
  - ".svn"
```

使用 `_subdirectory` 时，默认排除列表为空，需手动指定需要排除的文件。

### Jinja2 环境配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `_jinja_extensions` | list[str] | `[]` | Jinja2 扩展的 Python 导入路径 |
| `_envops` | dict | 见下方 | Jinja2 Environment 选项 |

`_envops` 默认值：
```yaml
_envops:
  keep_trailing_newline: true  # 保留模板文件末尾换行符
```

支持的 `_envops` 选项：
- `keep_trailing_newline`：保留末尾换行（默认 true）
- `undefined`：`"jinja2.Undefined"`（默认，静默忽略未定义变量）或 `"jinja2.StrictUndefined"`（严格模式，未定义变量抛错）
- 其他 Jinja2 Environment 构造参数（如 `block_start_string`、`variable_start_string` 等自定义分隔符）

### 消息提示

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `_message_before_copy` | str | `""` | 复制前显示的消息 |
| `_message_after_copy` | str | `""` | 复制后显示的消息 |
| `_message_before_update` | str | `""` | 更新前显示的消息 |
| `_message_after_update` | str | `""` | 更新后显示的消息 |

消息字符串本身也会被 Jinja2 渲染，可以引用模板变量。

### 任务与迁移

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `_tasks` | list | `[]` | 生成后执行的任务列表 |
| `_migrations` | list | `[]` | 跨版本迁移任务列表 |

详见 [任务与迁移](07-tasks-and-migrations.md)。

### 外部数据

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `_external_data` | dict | `{}` | 外部 YAML 数据文件映射，延迟加载 |

```yaml
_external_data:
  presets: "data/presets.yml"
```

外部数据通过 LazyDict 延迟加载，首次访问时才读取文件。数据文件路径也支持 Jinja2 模板渲染。安全约束：路径必须在目标项目目录内，除非使用 `--trust`。

## 问题定义

非下划线开头的键定义交互式问题。Copier 支持**简化格式**和**完整格式**。

### 简化格式

```yaml
project_name: my-project          # 等同于 {default: "my-project", type: "str"}
author_name: "Zhang San"          # 默认字符串
python_version: "3.12"            # 默认值
use_docker: false                 # 默认布尔值
```

### 完整格式

```yaml
project_name:
  type: str
  help: "项目名称"
  default: "my-project"
  placeholder: "my-awesome-project"
```

### 问题属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | str | 数据类型：`str`/`int`/`float`/`bool`/`json`/`yaml`/`secret` |
| `help` | str | 帮助文本，显示在问卷提示中 |
| `default` | any | 默认值，支持 Jinja2 模板字符串（可引用之前问题的答案） |
| `placeholder` | str | 输入框占位文本 |
| `choices` | list/dict | 选项列表（单选/多选） |
| `multiselect` | bool | 是否允许多选（配合 choices 使用） |
| `when` | str/bool | 条件表达式，决定是否显示该问题 |
| `validator` | str | 验证器 Jinja2 表达式，返回 true/错误消息 |
| `secret` | bool | 是否为密码输入（不回显），默认 false |

### 问题类型详解

**str（默认类型）**：文本输入
```yaml
project_name:
  type: str
  help: "项目名称"
```

**int/float**：数值输入，自动类型转换
```yaml
port:
  type: int
  default: 8080
  help: "服务端口"
```

**bool**：是/否确认
```yaml
use_docker:
  type: bool
  default: false
  help: "是否包含 Dockerfile？"
```

**json/yaml**：接受 JSON/YAML 格式输入，解析为对应 Python 对象
```yaml
extra_config:
  type: json
  help: "额外配置（JSON 格式）"
```

**secret**：密码输入（不回显），不存入答案文件
```yaml
db_password:
  type: secret
  secret: true    # 也可以通过 _secret_questions 列表标记
  help: "数据库密码"
```

### 选项选择（choices）

```yaml
license:
  type: str
  choices:
    - MIT
    - Apache-2.0
    - GPL-3.0
    - BSD-3-Clause
  default: MIT
```

多选模式：
```yaml
features:
  type: str
  choices:
    - authentication
    - database
    - caching
    - logging
  multiselect: true
  default: [authentication, logging]
```

字典形式的 choices（支持值与显示名分离）：
```yaml
python_version:
  choices:
    "Python 3.10": "3.10"
    "Python 3.11": "3.11"
    "Python 3.12": "3.12"
  default: "3.12"
```

### 条件问题（when）

`when` 属性使用 Jinja2 表达式，可引用之前问题的答案：

```yaml
use_docker:
  type: bool
  default: false

docker_base_image:
  type: str
  default: "python:3.12-slim"
  when: "{{ use_docker }}"    # 仅当 use_docker 为 true 时询问
```

### 动态默认值

`default` 值支持 Jinja2 模板，可以引用之前问题的答案：

```yaml
project_name:
  type: str
  default: "my-project"

package_name:
  type: str
  default: "{{ project_name|lower|replace('-', '_') }}"
  # 根据 project_name 自动生成包名
```

### 配置与问题的分离机制

Copier 内部通过 `filter_config()` 函数分离配置和问题：
- 以 `_` 开头的键 → `config_data`（配置）
- 其余键 → `questions_data`（问题），简化格式自动转为 `{default: value}`

多文档 YAML（`---` 分隔）中，列表类型的配置项（`_exclude`/`_jinja_extensions`/`_secret_questions`/`_skip_if_exists`）会自动合并（extend），其他键后面的文档覆盖前面的。

## 最小配置示例

一个最简单的模板只需一个空的 `copier.yml`（甚至可以没有），此时 Copier 会直接复制所有文件（排除默认模式），不询问任何问题。

一个功能较完整的 `copier.yml` 示例：

```yaml
_templates_suffix: ".jinja"
_min_copier_version: "9.0.0"
_exclude:
  - "*.egg-info"
  - ".pytest_cache"
_skip_if_exists:
  - ".env"

project_name:
  type: str
  help: "项目名称"
  default: "my-project"

author_name:
  type: str
  help: "作者姓名"

use_docker:
  type: bool
  default: false
  help: "包含 Dockerfile？"

_tasks:
  - "git init"
  - command: "pip install -e '.[dev]'"
    working_directory: "{{ _copier_conf.dst_path }}"
```

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [问题与答案系统](03-questions-and-answers.md)
- [Jinja2 模板渲染](04-jinja2-templating.md)
- [Worker 与生命周期](05-worker-and-lifecycle.md)
- [任务与迁移](07-tasks-and-migrations.md)
- [Copier 源码信源登记](../references/copier-source.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](../references/copier-source.md)。
