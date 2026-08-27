---
type: Example
title: 条件渲染与动态文件
description: 使用 when 条件、Jinja2 控制流、yield 标签实现动态文件生成
tags: [copier, conditional, dynamic, yield, jinja2, when, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-src
    resource: /references/copier-source.md
    title: "Copier 源码"
---

# 条件渲染与动态文件

本示例展示 Copier 的条件渲染能力：条件问题、条件文件内容、动态目录结构、以及使用 yield 标签从一个模板生成多个文件。[^copier-src]

## 1. 条件问题（when）

使用 `when` 属性让问题的显示依赖于前序问题的答案：

```yaml
# copier.yml
use_database:
  type: bool
  default: false
  help: "是否使用数据库？"

database_type:
  type: str
  choices: [postgresql, mysql, sqlite]
  default: postgresql
  when: "{{ use_database }}"  # 仅当 use_database=true 时询问

database_host:
  type: str
  default: "localhost"
  when: "{{ use_database and database_type != 'sqlite' }}"

database_port:
  type: int
  default: 5432
  when: "{{ use_database and database_type == 'postgresql' }}"

use_api:
  type: bool
  default: true
  help: "是否包含 REST API？"

api_framework:
  type: str
  choices: [fastapi, flask, django]
  default: fastapi
  when: "{{ use_api }}"
```

条件表达式中可以引用之前所有问题的答案，支持 Jinja2 的完整表达式语法。

## 2. 条件文件内容

在模板文件中使用 Jinja2 的 `{% if %}`/`{% endif %}` 控制内容块：

**requirements.txt.jinja**：
```jinja
{% if use_api %}
{% if api_framework == 'fastapi' %}
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
{% elif api_framework == 'flask' %}
flask>=3.0.0
{% elif api_framework == 'django' %}
django>=5.0.0
{% endif %}
{% endif %}
{% if use_database %}
{% if database_type == 'postgresql' %}
psycopg2-binary>=2.9.0
{% elif database_type == 'mysql' %}
pymysql>=1.1.0
{% endif %}
sqlalchemy>=2.0.0
alembic>=1.12.0
{% endif %}
pydantic>=2.0.0
pyyaml>=6.0
click>=8.0.0
```

**config.py.jinja**：
```jinja
"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "{{ project_name }}"
    debug: bool = False
{% if use_database %}
{% if database_type == 'sqlite' %}
    database_url: str = "sqlite:///./app.db"
{% else %}
    database_url: str = "{{ database_type }}+psycopg://app:app@{{ database_host }}:{{ database_port }}/app"
{% endif %}
{% endif %}
{% if use_api %}
    api_host: str = "0.0.0.0"
    api_port: int = 8000
{% endif %}
```

## 3. 条件文件（通过文件名/目录名中的空字符串渲染）

Copier 支持通过将路径部分渲染为空字符串来条件性地创建文件/目录。

**方法一：使用 yield 跳过空部分**（不直接支持，需用 yield 替代）

**方法二：将条件逻辑放在目录结构中，使用 when 无法直接控制文件存在性**

文件存在性主要通过两种方式控制：
1. `_exclude` 模式（但不能基于答案条件排除）
2. 在文件名中使用条件渲染的 Jinja2 表达式（如果某部分渲染为空字符串，Copier 会跳过该路径）

**示例：条件性 Docker 文件**

创建模板文件 `{% if use_docker %}Dockerfile{% endif %}.jinja`——但这种方式实际会生成名为 `.jinja` 的文件（因为条件为 false 时 Dockerfile 部分为空），不推荐。

更实用的方法是将条件文件放在以 Jinja2 变量命名的目录中：

```
template/
├── copier.yml
└── {{ 'docker' if use_docker else '' }}/
    └── Dockerfile.jinja
```

当 `use_docker=false` 时，目录名渲染为空字符串，但 Copier 会跳过空路径部分（`_render_parts` 中 `if not rendered_part: return`）。

> **注意**：条件文件存在性的推荐做法是在所有文件中使用条件内容，或通过任务脚本在生成后删除不需要的文件。

## 4. Yield 标签：一个模板生成多个文件

使用 `{% yield %}` 标签可以从单个模板文件生成多个输出文件。

### 示例：为多个模块生成配置文件

**copier.yml**：
```yaml
_templates_suffix: ".jinja"

services:
  type: json
  default: '["web", "api", "worker"]'
  help: "要生成的服务列表（JSON 数组）"
```

**模板路径**：`config/{{ service }}.yaml.jinja`

在路径名中使用 yield 迭代：

路径 `config/{% for service in services %}{% yield service %}{% endfor %}.yaml.jinja` 中，`{% yield %}` 会让 Copier 为 `services` 列表中的每个值生成一个文件。

模板文件内容（`config/{service}.yaml.jinja`，注意路径中的 `{service}` 只是示意，实际使用 yield）：

```jinja
{# 使用 yield 的正确方式：路径名中包含 {% yield variable %} #}
apiVersion: v1
kind: Service
metadata:
  name: {{ service }}
spec:
  selector:
    app: {{ project_name }}
    service: {{ service }}
{% if service == 'web' %}
  ports:
    - port: 80
      targetPort: 8080
{% elif service == 'api' %}
  ports:
    - port: 8000
      targetPort: 8000
{% endif %}
```

如果 `services = ["web", "api", "worker"]`，会生成三个文件：
- `config/web.yaml`
- `config/api.yaml`
- `config/worker.yaml`

每个文件中 `{{ service }}` 变量分别对应 `"web"`、`"api"`、`"worker"`。

### yield 工作原理

`_render_parts()` 方法递归处理路径的每个部分：
1. 渲染路径部分
2. 如果检测到 yield 上下文（`get_yield_context()` 返回 `yield_name`），遍历 `yield_iterable`
3. 为每个迭代值创建新的上下文（`{**extra_context, yield_name: value}`）
4. 递归渲染剩余路径部分
5. 空字符串部分跳过（不生成路径）

### yield 限制

- 只能在路径名中使用 yield（文件内容中使用会抛 `YieldTagInFileError`）
- 一个路径名中不允许多个 yield 标签（抛 `MultipleYieldTagsError`）

## 5. 动态默认值

默认值可以引用其他变量，实现联动效果：

```yaml
project_name:
  type: str
  default: "my-app"

package_name:
  type: str
  default: "{{ project_name|lower|replace('-', '_')|replace(' ', '_') }}"

module_name:
  type: str
  default: "{{ package_name }}"

docker_image:
  type: str
  default: "{{ project_name }}:latest"
```

Jinja2 过滤器可以链式调用：
- `|lower`：转小写
- `|replace('-', '_')`：替换字符
- `|trim`：去除空白
- Ansible 过滤器：`|basename`、`|hash('sha256')`、`|to_json`、`|to_yaml`、`|regex_replace`、`|random` 等

## 6. 动态默认值 + 条件组合示例

一个更实际的多层条件配置：

```yaml
# copier.yml
deployment_target:
  type: str
  choices: [local, docker, kubernetes]
  default: local
  help: "部署目标"

docker_base_image:
  type: str
  default: "python:{{ python_version }}-slim"
  when: "{{ deployment_target in ['docker', 'kubernetes'] }}"

kubernetes_namespace:
  type: str
  default: "{{ project_name|lower|replace(' ', '-') }}"
  when: "{{ deployment_target == 'kubernetes' }}"

replicas:
  type: int
  default: 2
  when: "{{ deployment_target == 'kubernetes' }}"

health_check_path:
  type: str
  default: "/health"
  when: "{{ deployment_target != 'local' and use_api }}"
```

## 相关概念

* [问题与答案系统](../concepts/03-questions-and-answers.md)
* [Jinja2 模板渲染](../concepts/04-jinja2-templating.md)
* [模板配置文件](../concepts/02-template-configuration.md)
* [Worker 与生命周期](../concepts/05-worker-and-lifecycle.md)

[^copier-src]: Copier 源码，见本 bundle 信源登记 [references/copier-source.md](../references/copier-source.md)。
