---
type: Concept
title: Copier 模板引擎基础
description: 理解 Copier 模板引擎的工作原理、extension-template 中的 Jinja2 条件渲染机制、参数类型系统和后处理任务。
tags: [copier, jinja2, template-engine, conditional-rendering, parameters, _tasks]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: copier-config
    resource: /references/copier-config.md
    title: Copier 配置参数全参考
---

## Copier 模板引擎基础

[Copier](https://copier.readthedocs.io) 是一个现代化的项目模板引擎，通过复制模板目录并渲染其中的 Jinja2 模板文件来生成新项目。extension-template 充分利用了 Copier 的条件渲染、参数验证、后处理任务和项目更新功能。

## 模板目录结构

extension-template 的仓库结构：

```
extension-template/
├── copier.yml              # Copier 配置文件（参数定义、任务、元配置）
├── README.md               # 模板使用说明（非渲染文件）
├── LICENSE                 # 许可证（非渲染文件）
├── .github/                # 模板自身的 CI/CD（非 template/ 子目录）
│   └── workflows/
└── template/               # 模板内容根目录（_subdirectory 指定）
    ├── {{python_name}}/    # Python 包目录（目录名也是模板！）
    │   ├── __init__.py.jinja
    │   └── routes.py.jinja
    ├── src/                # TypeScript 源码
    │   ├── index.ts.jinja
    │   └── request.ts.jinja
    ├── style/              # 样式文件
    ├── schema/             # 设置 schema（条件目录）
    ├── binder/             # Binder 配置（条件目录）
    ├── ui-tests/           # 集成测试（条件目录）
    ├── package.json.jinja
    ├── pyproject.toml.jinja
    ├── tsconfig.json.jinja
    └── ...
```

关键点：
- `_subdirectory: template` 告诉 Copier 只复制 `template/` 子目录
- 以 `.jinja` 后缀结尾的文件会被 Jinja2 渲染
- 不含 `.jinja` 后缀的文件（如 `CHANGELOG.md`、`babel.config.js`）会原样复制
- **目录名也可以是模板**：`{{python_name}}/` 目录会被重命名为用户提供的 Python 包名
- **条件目录/文件**：通过特殊的文件名模式 `{% if condition %}dirname{% endif %}` 实现条件包含

## 元配置字段

`copier.yml` 开头以下划线开头的字段是元配置：

| 字段 | 作用 |
|------|------|
| `_min_copier_version` | 最低 Copier 版本要求（"7.1.0"） |
| `_subdirectory` | 模板内容子目录（"template"） |
| `_jinja_extensions` | 启用的 Jinja2 扩展（`jinja2_time.TimeExtension` 提供 `{% now %}`） |
| `_tasks` | 文件生成后执行的命令列表 |

## 参数类型系统

Copier 支持多种参数类型：

### str 类型

```yaml
author_name:
  type: str
  help: Extension author name
  placeholder: "My Name"
  validator: >-
    {% if not (author_name | regex_search('^[^\s].*$')) %}
    author_name cannot be empty nor start with a blank character.
    {% endif %}
```

- `help`：交互式提示文本
- `placeholder`：输入框占位符
- `default`：默认值（可以是 Jinja2 模板表达式）
- `validator`：使用 Jinja2 模板编写验证逻辑，输出非空字符串时表示验证失败

### bool 类型

```yaml
has_settings:
  when: "{{ kind != 'mimerenderer' }}"
  type: bool
  help: Does the extension have user settings?
  default: no
```

- `when`：条件表达式，决定该参数是否出现
- yes/no 回答会被转换为 Python 的 True/False

### 选项类型（choices）

```yaml
kind:
  type: str
  choices:
    - frontend
    - mimerenderer
    - frontend-and-server
    - theme
  default: frontend
```

用户通过上下箭头选择，而非自由输入。

### 条件显示（when）

`when` 字段控制参数是否在交互中出现。例如：
- `has_settings` 仅在 `kind != 'mimerenderer'` 时出现
- `viewer_name`、`mimetype` 等仅在 `kind == 'mimerenderer'` 时出现
- `yarn_linker` 仅在 `advanced == true` 时出现
- `create_claude_symlink` 仅在 `has_ai_rules == true` 时出现

### 动态默认值

默认值可以引用其他参数的值，使用 Jinja2 模板语法：

```yaml
labextension_name:
  default: "{% if kind == 'theme' %}mytheme{% else %}myextension{% endif %}"

python_name:
  default: "{{ labextension_name | replace('-', '_') | replace('/', '_') | trim('@') }}"
```

`python_name` 的默认值通过 Jinja2 过滤器自动从 `labextension_name` 转换：连字符和斜杠转下划线，去除 `@` 前缀。

## Jinja2 条件渲染

模板文件中使用 `{% if %}` / `{% elif %}` / `{% else %}` / `{% endif %}` 控制代码块的生成。这是 extension-template 实现"一套模板四种类型"的核心机制。

### 条件文件包含

文件名中包含 `{% if condition %}` 模式的文件是条件文件，只有条件满足时才会生成：

```
src/{% if kind == 'frontend-and-server' %}request.ts{% endif %}.jinja
```

这个文件只有在 `kind == 'frontend-and-server'` 时才会被生成。

### 条件目录包含

同理，目录名也可以包含条件：

```
{% if kind == 'frontend-and-server' %}jupyter-config{% endif %}/
{% if has_binder %}binder{% endif %}/
{% if test %}ui-tests{% endif %}/
```

### 条件代码块

在 `.jinja` 文件内部，使用条件块控制代码生成：

```jinja
{# package.json.jinja 中的依赖条件 #}
"dependencies": {
  {% if kind.lower() != 'mimerenderer' %}"@jupyterlab/application": "^4.0.0"
    {% if kind.lower() == 'theme' %},
    "@jupyterlab/apputils": "^4.0.0"{% endif %}
  {% else %}"@jupyterlab/rendermime-interfaces": "^3.8.0",
  "@lumino/widgets": "^2.1.0"{% endif %}
}
```

注意逗号处理：JSON 语法要求最后一个元素后不能有逗号，模板通过嵌套 if 仔细控制逗号位置。

### 常见 Jinja2 过滤器

模板中使用的过滤器：

| 过滤器 | 作用 | 示例 |
|--------|------|------|
| `replace` | 字符串替换 | `labextension_name \| replace('-', '_')` |
| `trim` | 去除字符 | `labextension_name \| trim('@')` |
| `regex_search` | 正则匹配 | 用于 validator 中 |
| `lower` | 转小写 | `kind.lower() == 'theme'` |

## 后处理任务（_tasks）

文件生成后，Copier 可以执行额外命令：

```yaml
_tasks:
  - command: python -c "import os; os.symlink('AGENTS.md', 'CLAUDE.md') ..."
    when: "{{ has_ai_rules and create_claude_symlink }}"
  - command: python -c "import os; os.symlink('AGENTS.md', 'GEMINI.md') ..."
    when: "{{ has_ai_rules and create_gemini_symlink }}"
```

每个任务包含：
- `command`：要执行的 shell 命令
- `when`：执行条件（可选）

extension-template 使用任务创建 AI 工具的符号链接文件。

## 项目更新

Copier 的一个重要特性是支持更新已生成的项目。当模板发布新版本时，在项目目录中运行：

```bash
copier update --trust
```

Copier 会：
1. 比较当前项目与最新模板的差异
2. 交互式地让你审核每个变更（3-way merge）
3. 保留你的自定义代码，同时应用模板更新
4. 更新 `.copier-answers.yml` 记录使用的模板版本

这比 cookiecutter 的"一次生成，永不更新"模式有显著优势。

## answers 文件

Copier 生成项目时会创建 `.copier-answers.yml`（在 `{{_copier_conf.answers_file}}.jinja` 模板中定义），记录用户的回答和模板版本。这个文件应该被提交到 Git，用于后续 `copier update` 时恢复上下文。

## 相关概念

- [快速开始](01-getting-started.md)
- [四种扩展类型对比](03-four-extension-types.md)
- [生成项目结构详解](04-project-structure.md)
- [Copier 配置参数参考](../references/copier-config.md)
