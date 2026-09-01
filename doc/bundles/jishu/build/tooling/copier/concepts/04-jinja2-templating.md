---
type: Concept
title: Jinja2 模板渲染
description: Jinja2 沙箱环境、模板后缀、文件/路径/字符串渲染、yield 扩展、自定义过滤器、环境配置、渲染上下文
tags: [copier, jinja2, templating, rendering, sandbox, extensions, yield]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# Jinja2 模板渲染

Copier 使用 Jinja2 模板引擎渲染文件内容、文件名和目录名。渲染在沙箱环境中执行，确保模板无法执行任意代码（除非显式信任）。[^copier-source]

## SandboxedEnvironment：安全沙箱

Copier 使用 `SandboxedEnvironment`（继承自 Jinja2 的 `SandboxedEnvironment`）作为模板渲染环境。沙箱环境限制了不安全的属性访问和方法调用，防止恶意模板访问敏感信息或执行危险操作。[^copier-source]

沙箱限制包括：
- 禁止访问以下划线开头的私有属性
- 禁止调用危险的 Python 内置函数
- 限制对 `os`、`sys`、`subprocess` 等模块的直接访问

如果模板需要使用自定义 Jinja2 扩展（可能绕过沙箱），Copier 会检测到并抛出 `UnsafeTemplateError`，要求用户显式使用 `--trust`/`--UNSAFE` 标志。

## 模板后缀（templates_suffix）

默认情况下，以 `.jinja` 结尾的文件会被当作 Jinja2 模板渲染，输出时去除 `.jinja` 后缀：

- `README.md.jinja` → 渲染 → `README.md`
- `main.py.jinja` → 渲染 → `main.py`
- `config.yaml`（无后缀）→ 原样复制，不渲染

通过 `_templates_suffix` 配置项可以自定义后缀：
```yaml
_templates_suffix: ".tmpl"    # 使用 .tmpl 作为模板后缀
_templates_suffix: ""         # 空后缀：所有文件都作为模板渲染
```

空后缀模式下所有文件都会被 Jinja2 渲染。二进制文件遇到解码错误时会回退为原样复制（`UnicodeDecodeError` 时 fallback）。

## 模板加载器（CopierTemplateLoader）

`CopierTemplateLoader` 是自定义的 Jinja2 模板加载器，负责从模板目录加载模板文件。它处理模板后缀逻辑，确保 `get_template()` 能正确找到以 `.jinja` 结尾的模板文件。

## 渲染类型

Copier 支持三种层次的模板渲染：

### 1. 文件内容渲染（_render_file）

最常见的渲染类型。读取模板文件内容，通过 Jinja2 渲染后写入目标路径。

流程：
1. 判断文件是否以 `templates_suffix` 结尾 → 是则渲染，否则直接读取字节
2. 通过 `jinja_env.get_template()` 获取 Jinja2 模板对象
3. 调用 `tpl.render(**context)` 渲染内容
4. 检查是否包含 yield 标签（文件内容中不允许 yield，抛 `YieldTagInFileError`）
5. 确定目标文件权限（优先使用 Git index 中的模式，回退到文件系统 stat）
6. 调用 `_render_allowed()` 判断是否需要写入（identical/create/conflict）
7. 写入文件并设置权限
8. 在 Windows 上通过 `git update-index --cacheinfo` 同步可执行位

### 2. 路径渲染（_render_path）

文件名和目录名也支持 Jinja2 模板语法。路径的每个部分（由 `/` 或 `\` 分隔）都会被独立渲染。

```
{{project_name}}/main.py.jinja
```

如果 `project_name` 的值是 `"my-app"`，则生成路径 `my-app/main.py`。

路径渲染还支持 `{% yield %}` 标签，用于从一个模板路径生成多个输出文件。详见下文 yield 扩展。

特殊处理：如果渲染后的路径是 answers 文件路径（`.copier-answers.yml`），会触发弃用警告（在子目录中使用 answers 文件模板路径已被弃用）。

### 3. 字符串渲染（_render_string）

用于渲染配置值、消息、任务命令、条件表达式等短字符串：

```python
rendered = worker._render_string("Hello, {{ name }}!")
```

内部通过 `jinja_env.from_string(string).render(**context)` 实现。

还有一个 `_render_value()` 方法，对非字符串值直接返回原值（跳过渲染）。

## Yield 扩展：一生多

`YieldExtension` 是 Copier 的自定义 Jinja2 扩展，允许在路径名中使用 `{% yield %}` 标签从一个模板生成多个文件。

典型用例：根据列表变量生成多个配置文件。

```
{# 模板路径：configs/{{ item }}.yaml.jinja #}
{% for item in services %}{% yield item %}{% endfor %}
```

如果 `services = ["web", "api", "worker"]`，则会生成三个文件：
- `configs/web.yaml`
- `configs/api.yaml`
- `configs/worker.yaml`

Yield 上下文通过 `get_yield_context()` 获取，包含 `yield_name`（迭代变量名）和 `yield_iterable`（可迭代对象）。

**限制**：yield 标签只能在路径名中使用，不能在文件内容中使用（否则抛 `YieldTagInFileError`）。一个路径名中不允许多个 yield 标签（`MultipleYieldTagsError`）。

## 内置扩展与过滤器

### 默认启用的扩展

| 扩展 | 说明 |
|------|------|
| `jinja2_ansible_filters.AnsibleCoreFiltersExtension` | Ansible 兼容过滤器集（`to_json`、`to_yaml`、`regex_replace`、`basename`、`dirname`、`hash`、`random` 等） |
| `YieldExtension` | Copier 内置的 yield 标签扩展 |

### 自定义全局函数

| 函数 | 说明 |
|------|------|
| `pathjoin(*parts, mode="posix")` | 跨平台路径拼接。mode 支持 `"posix"`（`/` 分隔）、`"windows"`（`\` 分隔）、`"native"`（系统原生） |

### to_json 过滤器补丁

Copier 补丁了 Jinja2 的 `to_json` 过滤器，使其支持：
- Pydantic dataclass 对象（通过 `pydantic_core.to_jsonable_python` 序列化）
- `LazyDict`（转换为普通 dict）
- `PurePath` 对象（转换为字符串）

## 渲染上下文变量

渲染模板时可用的变量由 `_render_context()` 方法生成，包括：

### 用户答案

所有问题变量直接可用，如 `{{ project_name }}`、`{{ author_name }}`。

### 特殊变量

| 变量 | 说明 |
|------|------|
| `_copier_answers` | 将被记住的答案（写入答案文件的内容） |
| `_copier_conf` | Worker 配置对象（LazyDict），包含 src_path、dst_path、answers_file、vcs_ref、exclude、overwrite 等配置 |
| `_folder_name` | 目标项目目录名 |
| `_copier_python` | 当前 Python 解释器路径（`sys.executable`） |
| `_copier_phase` | 当前执行阶段（prompt/render/tasks/migrate/undefined） |
| `_copier_operation` | 当前操作类型（copy/update） |

### `_copier_conf` 可用属性

通过 `_copier_conf` 可访问 Worker 的配置（均为 LazyDict 延迟求值）：

```jinja
{{ _copier_conf.src_path }}        # 模板源路径
{{ _copier_conf.dst_path }}        # 目标路径
{{ _copier_conf.vcs_ref }}         # VCS 引用
{{ _copier_conf.overwrite }}       # 是否覆盖
{{ _copier_conf.sep }}             # 路径分隔符（os.sep）
{{ _copier_conf.os }}              # OS 信息对象
```

### 任务额外变量

在任务执行时，任务的 `extra_vars` 会以 `_` 前缀注入渲染上下文（如 `_stage`、`_version_from`）。

## Jinja2 环境配置（envops）

通过 `_envops` 配置项自定义 Jinja2 Environment 行为：

```yaml
_envops:
  keep_trailing_newline: true           # 保留末尾换行（默认 true）
  undefined: "jinja2.StrictUndefined"   # 严格模式：未定义变量抛错
  block_start_string: "<%"              # 自定义块开始标记
  block_end_string: "%>"
  variable_start_string: "[["           # 自定义变量开始标记
  variable_end_string: "]]"
```

支持的 undefined 类：
- `"jinja2.Undefined"`（默认）：未定义变量静默渲染为空字符串
- `"jinja2.StrictUndefined"`：未定义变量抛出 `UndefinedError`

自定义分隔符在模板包含与 JavaScript/CSS 等语法冲突时很有用。

## 文件权限处理

Copier 智能处理文件可执行权限：

1. **Git index 模式优先**：从模板的 Git index（`git ls-files --stage`）读取文件模式，这是模板作者意图的权威来源
2. **跨平台可执行位保留**：Windows 上 `os.stat()` 不报告可执行位，但 Git index 中记录的 `100755`/`100644` 模式会被保留
3. **权限合并策略**：Git index 只提供可执行位（0o111），读写位（非 0o111）来自文件系统 stat
4. **Git index 同步**：在 `core.fileMode=false`（Windows 默认）时，通过 `git update-index --cacheinfo` 显式同步可执行位到目标仓库的 Git index

## 渲染冲突解决

当目标文件已存在且内容不同时，`_render_allowed()` 判断如何处理：

1. **identical**：新旧内容完全相同（含权限检查）→ 跳过，输出 `identical` 标记
2. **skip_if_exists 匹配**：文件匹配跳过模式 → 跳过，输出 `skip` 标记
3. **overwrite 模式**：用户指定了 `--overwrite` 或是 answers 文件 → 直接覆盖
4. **交互确认**：运行在 TTY 中 → 通过 questionary 询问用户是否覆盖
5. **非交互模式**：无 TTY 时抛出 `InteractiveSessionError`，提示使用 `--overwrite`

输出颜色标记（Style 枚举）：
- `OK`（绿色）：create/skip
- `WARNING`（黄色）：overwrite
- `DANGER`（红色）：conflict
- `IGNORE`（灰色）：identical

## 相关概念

- [模板配置文件](02-template-configuration.md)
- [Worker 与生命周期](05-worker-and-lifecycle.md)
- [任务与迁移](07-tasks-and-migrations.md)
- [安全与信任机制](09-security-and-safety.md)
- [条件渲染与动态文件示例](../examples/conditional-rendering.md)
- [Copier 源码信源登记](../references/copier-source.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](../references/copier-source.md)。
