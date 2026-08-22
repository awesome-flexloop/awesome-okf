---
type: Concept
title: Cookiecutter 模板引擎基础
description: 理解 Cookiecutter 的核心概念——模板变量、Jinja2 渲染、hooks 脚本、目录名渲染，以及 extension-cookiecutter 中如何运用这些机制。
tags: [cookiecutter, jinja2, template-engine, hooks, rendering]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cookiecutter-json
    resource: /references/cookiecutter-json.md
    title: cookiecutter.json 参数全参考
  - id: post-gen-hook
    resource: /references/post-gen-hook-source.md
    title: post_gen_project.py 生成后钩子解析
---

## Cookiecutter 是什么

[Cookiecutter](https://github.com/audreyr/cookiecutter) 是一个命令行工具，从项目模板（cookiecutter template）创建项目。模板是一个包含特殊语法的目录，Cookiecutter 渲染模板后生成一个新的项目目录。

与其他脚手架工具（如 Copier、Yeoman、django-admin startproject）相比，Cookiecutter 的特点是：

- **语言无关**：可以生成任意语言的项目（Python、JS、Go、Rust...）
- **基于 Jinja2**：文件内容和文件名/目录名都支持 Jinja2 模板语法
- **简单**：核心机制只有"变量 + 渲染 + 钩子"，学习曲线平缓
- **广泛使用**：Jupyter、Django、FastAPI 等生态都使用 Cookiecutter

## 核心概念

### 1. cookiecutter.json——变量定义

模板根目录的 `cookiecutter.json` 定义了所有模板变量及其默认值：

```json
{
  "author_name": "My Name",
  "package_name": "my_server_extension",
  "has_binder": "n"
}
```

执行 `cookiecutter <template-path>` 时，Cookiecutter 逐个提示用户输入每个变量的值，方括号中显示默认值。用户也可以通过命令行参数传入值：

```bash
cookiecutter <template-path> author_name="Jane" package_name="jane_ext" --no-input
```

### 2. Jinja2 变量渲染

在模板文件中，使用 `{{ cookiecutter.<variable_name> }}` 引用变量值。文件内容、文件名、目录名都支持 Jinja2 渲染。

**文件内容中的渲染**（以 extension.py 为例）：

```python
name = "{{ cookiecutter.package_name | replace('-', '_') }}"
```

渲染后（假设 package_name 输入为 `my-extension`）：

```python
name = "my_extension"
```

**文件名中的渲染**（模板目录结构）：

```
{{cookiecutter.package_name}}/
├── {{cookiecutter.package_name}}/
│   └── __init__.py
```

渲染后：

```
my_extension/
├── my_extension/
│   └── __init__.py
```

### 3. Jinja2 过滤器

Cookiecutter 支持所有 Jinja2 内置过滤器，模板中常用的有：

| 过滤器 | 作用 | 模板中用途 |
|--------|------|-----------|
| `replace('-', '_')` | 字符串替换 | 将包名中的连字符转为下划线（Python 模块名） |
| `replace('_', '-')` | 字符串替换 | 将包名中的下划线转为连字符（URL 路径） |
| `lower()` | 转小写 | Binder 选项大小写不敏感判断 |
| `startswith('y')` | 判断前缀 | 判断是否选择 Binder |

### 4. Jinja2 控制块

条件渲染使用 `{% if %}...{% endif %}` 块：

```jinja2
{%- if cookiecutter.has_binder.lower().startswith('y') -%}
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/...)
{%- endif %}
```

`{%- ` 和 `-%}` 控制空白符，避免渲染后留下多余空行。

### 5. raw/endraw 块

当文件内容本身包含 `{{ }}` 语法（如 GitHub Actions 表达式）时，使用 `{% raw %}...{% endraw %}` 避免 Jinja2 解析：

```jinja2
{% raw %}
  token: ${{ secrets.GITHUB_TOKEN }}
{% endraw %}
```

渲染后保留原始的 `${{ secrets.GITHUB_TOKEN }}`。

### 6. Hooks——钩子脚本

模板根目录下的 `hooks/` 目录可以包含 Python 或 Shell 脚本，在生成前后执行：

| 钩子文件名 | 执行时机 |
|-----------|---------|
| `pre_gen_project.py` | 模板渲染**之前**执行 |
| `post_gen_project.py` | 模板渲染**之后**执行 |
| `pre_gen_project.sh` | Shell 版本的 pre 钩子 |

本模板使用 `post_gen_project.py` 实现条件文件删除——当用户选择不需要 Binder 时，删除 `binder/` 目录和相关 CI 文件。这是因为 Jinja2 只能控制文件内容，不能控制文件本身是否存在。

钩子脚本执行时：
- 工作目录（cwd）是新生成的项目根目录
- 标准输出/错误会显示给用户
- 非零退出码会终止生成过程

## 目录结构约定

一个 Cookiecutter 模板的标准结构：

```
my-template/                  # 模板根目录
├── cookiecutter.json         # 变量定义（必填）
├── hooks/                    # 钩子脚本（可选）
│   ├── pre_gen_project.py
│   └── post_gen_project.py
├── {{cookiecutter.project_slug}}/   # 项目模板目录（目录名被渲染）
│   ├── README.md
│   ├── pyproject.toml
│   └── {{cookiecutter.project_slug}}/
│       ├── __init__.py
│       └── ...
└── README.md                 # 模板自身的说明文档
```

关键规则：
- 模板目录名**必须**使用 `{{cookiecutter.xxx}}` 格式，这样生成的项目目录名才是用户输入的名字
- 模板目录外的文件（如 README.md、LICENSE）不会被渲染到新项目中
- hooks/ 目录不会被复制到新项目中

## 常用 Cookiecutter 命令

```bash
# 从 GitHub 模板生成项目
cookiecutter https://github.com/jupyter-server/extension-cookiecutter

# 从本地模板目录生成
cookiecutter /path/to/template

# 使用默认值，不交互提问
cookiecutter <template> --no-input

# 传入变量值，不交互
cookiecutter <template> package_name=my_ext author_name="Jane" --no-input

# 指定输出目录
cookiecutter <template> -o ./projects

# 覆盖已存在的目录
cookiecutter <template> --overwrite-if-exists
```

## Cookiecutter vs Copier

Jupyter 生态正在从 Cookiecutter 向 Copier 迁移（如 JupyterLab Extension Template 已改用 Copier）。两者核心区别：

| 特性 | Cookiecutter | Copier |
|------|-------------|--------|
| **模板更新** | ❌ 不支持（生成后无法合并模板更新） | ✅ 支持 `copier update` |
| **答案文件** | 无 | `.copier-answers.yml` 记录选择 |
| **任务执行** | 只有 pre/post 钩子 | 更丰富的任务系统 |
| **学习曲线** | 简单 | 略复杂 |
| **Jupyter Server 扩展** | ✅ 本模板使用 | 暂未迁移 |

对于 Jupyter Server 后端扩展（纯 Python），Cookiecutter 的简单性是优势——项目生成后不需要"更新模板"，因为模板生成的主要是静态配置文件。

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [项目结构详解](/concepts/03-project-structure.md)
- [post_gen_project 钩子解析](/references/post-gen-hook-source.md)
