---
type: Reference
title: cookiecutter.json 参数全参考
description: Jupyter Server Extension CookieCutter 模板的所有交互参数定义、默认值和 Jinja2 渲染规则。
tags: [reference, cookiecutter, parameters, configuration]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cookiecutter-json
    resource: https://github.com/jupyter-server/extension-cookiecutter/blob/main/cookiecutter.json
    title: cookiecutter.json 源码
---

## 参数清单

`cookiecutter.json` 文件定义了模板生成时需要用户填写的所有参数。执行 `cookiecutter <template-path>` 时，引擎会逐一向用户提问，使用默认值或用户输入填充模板变量。

| 参数键 | 默认值 | 类型 | 说明 |
|--------|--------|------|------|
| `author_name` | `"My Name"` | 字符串 | 扩展作者姓名，写入 pyproject.toml 的 authors 字段和 LICENSE 版权行 |
| `author_email` | `"me@me.com"` | 字符串 | 作者邮箱，写入 pyproject.toml 的 authors 字段 |
| `package_name` | `"my_server_extension"` | 字符串 | Python 包名，作为目录名、模块名和分发名的基础。支持连字符（`-`）和下划线（`_`） |
| `project_short_description` | `"A Jupyter Server extension."` | 字符串 | 项目一句话简介，写入 `__init__.py` 文档字符串和 README.md |
| `has_binder` | `"n"` | 字符串（y/n） | 是否包含 Binder 集成配置。值以 `y` 开头（不区分大小写）时保留 `binder/` 目录和 Binder CI 工作流 |
| `repository` | `"https://github.com/github_username/{{ cookiecutter.package_name }}"` | 字符串（含模板变量） | 项目仓库 URL，写入 pyproject.toml 的 `[project.urls] Home` 字段和 README badge 链接 |

## Jinja2 变量使用规则

模板中通过 `{{ cookiecutter.<param_name> }}` 引用参数值。此外，模板广泛使用两个字符串替换过滤器来处理命名约定：

### 连字符→下划线（Python 模块名）

```jinja2
{{ cookiecutter.package_name | replace('-', '_') }}
```

用于 Python 模块路径、ExtensionApp name 属性、`_jupyter_server_extension_points()` 返回值。因为 Python 模块名不允许连字符，当用户输入 `my-extension` 时，此过滤器将其转换为 `my_extension`。

出现位置：
- `__init__.py` 中的 `_jupyter_server_extension_points()` 函数
- `extension.py` 中的 `Extension.name` 属性
- `conftest.py` 中的 jp_server_config fixture
- `jupyter-config/*.json` 中的扩展启用配置

### 下划线→连字符（URL 路由）

```jinja2
{{ cookiecutter.package_name | replace('_', '-') }}
```

用于 HTTP 路由路径。Jupyter Server 扩展的 URL 约定使用连字符，当包名含下划线时转换为连字符。

出现位置：
- `extension.py` 中的 handlers URL 模式：`("<package-dash>/ping", PingHandler)`
- `test_handlers.py` 中的 jp_fetch 路径参数

### 条件渲染

Binder 相关内容通过条件块控制：

```jinja2
{%- if cookiecutter.has_binder.lower().startswith('y') -%}
  <!-- Binder badge 和工作流内容 -->
{%- endif %}
```

`lower()` 确保大小写不敏感（`Y`/`y`/`Yes`/`yes` 均识别），`startswith('y')` 比精确比较更宽松。

README.md 中的 Binder badge 使用 `{% raw %}{% endraw %}` 注释语法 `{# ... #}` 来避免 Jinja2 解析干扰。

### 原始块（raw/endraw）

GitHub Actions 工作流文件中包含 `${{ }}` 语法，这与 Jinja2 的变量语法冲突。模板使用 `{% raw %}...{% endraw %}` 块来转义：

```jinja2
{% raw %}
  token: ${{ secrets.GITHUB_TOKEN }}
{% endraw %}
```

出现位置：`build.yml` 中的 check_release job。

## 参数流向图

```
cookiecutter.json (用户输入)
    │
    ├── author_name, author_email ──→ pyproject.toml [project.authors]
    │                               ──→ LICENSE (版权行)
    │
    ├── package_name ──→ 目录名: {{cookiecutter.package_name}}/
    │                  ──→ 模块名: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/
    │                  ──→ pyproject.toml [project.name]
    │                  ──→ replace('-','_') → Python 导入路径、Extension.name
    │                  ──→ replace('_','-') → URL 路由
    │                  ──→ jupyter-config 文件名
    │
    ├── project_short_description ──→ __init__.py docstring
    │                              ──→ README.md
    │
    ├── has_binder ──→ post_gen_project.py 条件删除
    │              ──→ README.md 条件渲染 Binder badge
    │              ──→ binder-on-pr.yml 条件保留
    │
    └── repository ──→ pyproject.toml [project.urls]
                   ──→ README.md badge 链接
                   ──→ Binder URL 构造
```

## 相关概念

- [Cookiecutter 模板引擎基础](../concepts/02-cookiecutter-basics.md)
- [项目结构详解](../concepts/03-project-structure.md)
- [post_gen_project 钩子解析](post-gen-hook-source.md)
