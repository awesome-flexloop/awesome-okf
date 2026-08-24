---
type: Concept
title: 5分钟快速上手
description: 创建第一个 Copier 模板、使用 copier copy 生成项目、理解 answers 文件
tags: [copier, getting-started, quickstart, template, first-project]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# 5分钟快速上手

本教程带你在 5 分钟内创建第一个 Copier 模板并生成项目。[^copier-source]

## 前置条件

- Python ≥ 3.10
- Git（用于模板版本管理，非必须但推荐）
- 已安装 copier：`pip install copier`

## 第一步：创建模板目录

创建一个模板目录结构。Copier 模板就是一个普通目录，包含 `copier.yml` 配置文件和模板文件：

```
my-template/
├── copier.yml          # 模板配置文件
├── README.md.jinja     # 模板文件（.jinja 后缀表示需要渲染）
├── {{project_name}}/   # 模板目录名也可以使用变量
│   └── main.py.jinja
```

## 第二步：编写 copier.yml

`copier.yml` 是模板的核心配置文件，定义交互式问题和模板设置：

```yaml
# copier.yml
_templates_suffix: ".jinja"
_min_copier_version: "9.0.0"

project_name:
  type: str
  help: "你的项目名称是什么？"
  default: "my-project"

project_description:
  type: str
  help: "项目简短描述"
  default: "A great project built with Copier"

author_name:
  type: str
  help: "作者姓名"

python_version:
  type: str
  help: "Python 版本"
  default: "3.12"
  choices:
    - "3.10"
    - "3.11"
    - "3.12"
    - "3.13"

use_docker:
  type: bool
  help: "是否包含 Dockerfile？"
  default: false
```

配置说明：
- 以 `_` 开头的键是**配置项**（如 `_templates_suffix`、`_min_copier_version`）
- 其他键是**问题定义**，用户将被交互式询问这些变量的值
- 简化格式 `key: default_value` 等价于 `key: {default: default_value}`

## 第三步：编写模板文件

模板文件使用标准 Jinja2 语法。以 `.jinja` 结尾的文件会被渲染（后缀在输出中被去除）。

**README.md.jinja**：
```jinja
# {{ project_name }}

{{ project_description }}

## 环境要求

- Python {{ python_version }}+
{% if use_docker %}
- Docker
{% endif %}

## 安装

```bash
pip install -e .
```

## 作者

\{{ author_name }}
```

**{{project_name}}/main.py.jinja**：
```jinja
"""{{ project_description }}"""

def main():
    print("Hello from {{ project_name }}!")

if __name__ == "__main__":
    main()
```

注意目录名 `\{{project_name}}/` 也是模板——它会被渲染为用户输入的项目名。

## 第四步：生成项目

使用 `copier copy` 命令从模板生成新项目：

```bash
# 语法：copier copy <模板路径> <目标路径>
copier copy ./my-template ./my-new-project
```

Copier 会启动交互式问卷，依次询问 `copier.yml` 中定义的问题：

```
🎤 你的项目名称是什么？
   my-project

🎤 项目简短描述
   A great project built with Copier

🎤 作者姓名
   Zhang San

🎤 Python 版本
   3.12

🎤 是否包含 Dockerfile？ (y/N)
   No
```

回答完毕后，Copier 将渲染所有模板文件到 `./my-new-project/` 目录。

## 第五步：查看生成结果

生成的项目结构：

```
my-new-project/
├── .copier-answers.yml   # 答案文件（自动生成）
├── README.md             # 渲染后的 README
└── my-project/           # 渲染后的目录名
    └── main.py          # 渲染后的 Python 文件
```

**生成的 README.md**（示例）：
```markdown
# my-project

A great project built with Copier

## 环境要求

- Python 3.12+

## 安装

pip install -e .

## 作者

Zhang San
```

### answers 文件

`.copier-answers.yml` 是 Copier 自动生成的答案记录文件，用于后续更新：

```yaml
_commit: v1.0.0
_src_path: /path/to/my-template
project_name: my-project
project_description: A great project built with Copier
author_name: Zhang San
python_version: "3.12"
use_docker: false
```

关键字段：
- `_src_path`：原始模板路径/URL
- `_commit`：使用的模板版本（Git commit 或标签）
- 其余为用户回答的变量值

## 非交互式模式

在 CI/CD 环境中可以使用非交互式模式：

```bash
# 使用默认值，不询问任何问题
copier copy --defaults ./my-template ./my-project

# 通过 --data 传递变量值
copier copy --data project_name=demo --data author_name=Bot ./my-template ./my-project

# 通过 YAML 文件传递数据
copier copy --data-file answers.yml ./my-template ./my-project

# 覆盖已存在的文件（不询问确认）
copier copy --overwrite ./my-template ./my-project
```

## 使用远程 Git 模板

Copier 支持直接从 Git 仓库使用模板：

```bash
# GitHub 快捷方式
copier copy gh:copier-org/autopretty my-project

# GitLab 快捷方式
copier copy gl:user/template my-project

# 完整 Git URL
copier copy https://github.com/user/template.git my-project

# 指定版本标签
copier copy -r v2.0.0 gh:user/template my-project
```

URL 快捷方式映射：
- `gh:owner/repo` → `https://github.com/owner/repo.git`
- `gl:owner/repo` → `https://gitlab.com/owner/repo.git`
- `git+https://...` → 去除 `git+` 前缀使用

## 更新已有项目

当模板更新后，可以使用 `copier update` 更新已有项目：

```bash
cd my-new-project
copier update
```

Copier 会读取 `.copier-answers.yml` 获取原始模板信息，对比新旧版本，智能应用变更。

## 常用 CLI 选项速查

| 选项 | 说明 |
|------|------|
| `-r, --vcs-ref REF` | 指定模板版本（标签/commit/HEAD） |
| `-d, --data K=V` | 通过命令行传递变量值 |
| `--data-file FILE` | 从 YAML 文件加载变量值 |
| `-l, --defaults` | 使用默认答案，不询问 |
| `-f, --force` | 等同于 `--defaults --overwrite` |
| `-w, --overwrite` | 覆盖已存在文件，不询问确认 |
| `-n, --pretend` | 模拟运行，不做实际修改 |
| `-q, --quiet` | 静默模式，抑制状态输出 |
| `-x, --exclude PATTERN` | 额外排除的文件模式 |
| `-T, --skip-tasks` | 跳过模板任务执行 |
| `--trust/--UNSAFE` | 信任模板，允许不安全特性 |
| `-A, --skip-answered` | 跳过已回答的问题 |

## 相关概念

- [Copier 简介](00-introduction.md)
- [模板配置文件](02-template-configuration.md)
- [问题与答案系统](03-questions-and-answers.md)
- [Jinja2 模板渲染](04-jinja2-templating.md)
- [CLI 命令参考](08-cli-reference.md)
- [基础模板创建与使用示例](/examples/basic-template.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](/references/copier-source.md)。
