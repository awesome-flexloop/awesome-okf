---
type: Pattern
title: 条件渲染模板模式
description: 使用 Jinja2 条件块在单一模板中生成多种变体代码，减少模板维护成本，适用于项目脚手架和代码生成器。
tags: [jinja2, copier, conditional-rendering, template-pattern, scaffolding]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:36:00Z" }
status: stable
source: extension-template
applicability: 项目模板、代码生成器、配置模板
---

# 条件渲染模板模式

## 问题

项目模板需要支持多种配置变体（如多种扩展类型、功能开关），但为每个变体维护独立模板会导致代码重复和维护负担。

## 解决方案

使用 Jinja2 条件块（`{% if %}`/`{% elif %}`/`{% else %}`/`{% endif %}`）在单一模板文件中嵌入变体逻辑，通过参数控制代码生成。

## 模板中的应用

### 1. 条件代码块

在 `.jinja` 文件中使用条件块控制代码片段的生成：

```jinja
{# 根据扩展类型导入不同依赖 #}
{% if kind.lower() != 'mimerenderer' %}
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
  {% if kind.lower() == 'theme' %}
import { IThemeManager } from '@jupyterlab/apputils';
  {% endif %}
{% else %}
import { IRenderMime } from '@jupyterlab/rendermime-interfaces';
import { Widget } from '@lumino/widgets';
{% endif %}
```

### 2. 条件文件

使用 `{% if condition %}filename{% endif %}.jinja` 命名模式实现条件文件：

```
src/{% if kind == 'frontend-and-server' %}request.ts{% endif %}.jinja
```

文件只有在条件满足时才会被生成。

### 3. 条件目录

同理，目录名也可以包含条件：

```
{% if has_binder %}binder{% endif %}/
{% if test %}ui-tests{% endif %}/
{% if has_settings %}schema{% endif %}/
```

### 4. 条件依赖

在 package.json.jinja 中根据类型动态添加依赖：

```jinja
"dependencies": {
  {% if kind.lower() != 'mimerenderer' %}"@jupyterlab/application": "^4.0.0"
    {% if kind.lower() == 'theme' %},
    "@jupyterlab/apputils": "^4.0.0"{% endif %}
  {% else %}"@jupyterlab/rendermime-interfaces": "^3.8.0",
  "@lumino/widgets": "^2.1.0"{% endif %}
}
```

### 5. 动态默认值

参数默认值可以引用其他参数：

```yaml
python_name:
  default: "{{ labextension_name | replace('-', '_') | replace('/', '_') | trim('@') }}"
```

## 关键原则

1. **逗号管理**：JSON/JS 中条件添加属性时必须小心处理逗号位置，避免生成无效语法
2. **参数验证**：使用 `validator` 字段（Jinja2 模板）验证用户输入
3. **条件显示**：使用 `when` 字段控制参数在交互中是否出现
4. **嵌套条件**：条件可以嵌套，但避免超过三层，否则可读性下降
5. **文件命名约定**：条件文件使用 `{% if %}name{% endif %}.ext.jinja` 模式

## 反模式

- ❌ 在条件块中大量复制粘贴相同代码（应提取为共享片段）
- ❌ 条件逻辑过于复杂导致模板不可读（超过 5 层嵌套）
- ❌ 在条件块中遗漏逗号或括号导致生成的代码有语法错误
- ❌ 不验证用户输入直接拼接到模板中（可能导致生成错误）

## 适用场景

- 项目脚手架生成器（如 Copier、Cookiecutter）
- 代码生成器（根据配置生成不同代码）
- 配置文件模板（根据环境变量生成不同配置）
- 多平台/多框架适配模板
