---
type: Example
title: 任务与自动化钩子
description: 使用 _tasks 和 _migrations 在生成后执行命令、条件任务、版本迁移脚本
tags: [copier, tasks, hooks, migrations, automation, post-generation, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-src
    resource: /references/copier-source.md
    title: "Copier 源码"
---

# 任务与自动化钩子

本示例展示如何使用 Copier 的任务系统在模板渲染后自动执行命令，包括初始化 Git 仓库、安装依赖、以及跨版本迁移脚本。任务属于不安全特性，需要 `--trust` 授权。[^copier-src]

## 1. 基本任务：初始化 Git 仓库

最简单的任务是字符串列表，每个字符串作为 shell 命令执行：

```yaml
# copier.yml
_tasks:
  - "git init"
  - "git add ."
  - "git commit -m 'Initial commit from Copier template' --no-verify"
```

执行时，Copier 会在目标项目目录下依次运行这些命令。

**注意**：执行任务需要 `--trust` 标志：
```bash
copier copy --trust ./template ./my-project
```

## 2. 条件任务

使用 `when` 条件让任务仅在特定情况下执行：

```yaml
# copier.yml
use_docker:
  type: bool
  default: false

install_deps:
  type: bool
  default: true
  help: "是否自动安装依赖？"

_tasks:
  - command: "git init"
    when: "true"  # 始终执行

  - command: "pip install -e '.[dev]'"
    when: "{{ install_deps }}"

  - command: "docker build -t {{ project_name }} ."
    when: "{{ use_docker }}"
    working_directory: "{{ _copier_conf.dst_path }}"
```

条件表达式是 Jinja2 模板，渲染后通过 `cast_to_bool()` 转为布尔值。可用变量包括所有答案和特殊变量（`_copier_operation`、`_stage` 等）。

## 3. 任务的两种命令格式

### Shell 字符串模式（简单）

```yaml
_tasks:
  - "echo 'Hello, {{ project_name }}!' && pip install -e ."
```

字符串命令通过 `shell=True` 执行，支持 shell 特性（管道、&&、重定向等），但有 shell 注入风险。

### Argv 列表模式（安全）

```yaml
_tasks:
  - command:
      - "pip"
      - "install"
      - "-e"
      - ".[dev]"
```

列表命令通过 `shell=False` 直接执行，不经过 shell 解析，更安全。列表中的每个元素仍支持 Jinja2 渲染。

## 4. 工作目录

使用 `working_directory` 指定任务的执行目录（相对于项目根目录）：

```yaml
_tasks:
  # 在项目根目录执行
  - command: "npm install"

  # 在前端子目录执行
  - command: "npm run build"
    working_directory: "frontend"

  # 使用动态路径
  - command: "python scripts/setup.py"
    working_directory: "{{ package_name }}"
```

`working_directory` 支持 Jinja2 渲染，可以引用模板变量。

## 5. 带前后消息的完整工作流

```yaml
_message_before_copy: |
  🚀 正在创建项目 {{ project_name }}...
  请回答以下问题：

_message_after_copy: |
  ✅ 项目创建完成！

  快速开始：
    cd {{ project_name }}
  {% if install_deps %}
    # 依赖已自动安装
  {% else %}
    pip install -e '.[dev]'
  {% endif %}
    git add . && git commit -m "Initial commit"

_tasks:
  - command: "git init"
    when: "true"

  - command:
      - "pip"
      - "install"
      - "-e"
      - ".[dev]"
    when: "{{ install_deps }}"

  - command: "pre-commit install"
    when: "{{ use_pre_commit and install_deps }}"

  - command: "git add . && git commit -m 'Initial commit' --no-verify"
    when: "true"
```

## 6. 迁移任务（_migrations）

迁移任务在 `copier update` 时执行，用于处理模板版本间的不兼容变更。迁移分为 before 和 after 两个阶段。

### 新格式（推荐）

```yaml
# copier.yml
_templates_suffix: ".jinja"

_migrations:
  # v1.0.0 → v2.0.0 迁移：重命名配置文件
  - version: "2.0.0"
    when: "{{ _stage == 'before' }}"
    command: "mv config.yaml config.yml"
    working_directory: "."

  # v2.0.0 后：安装新依赖
  - version: "2.0.0"
    when: "{{ _stage == 'after' }}"
    command: "pip install -e '.[dev]'"

  # v3.0.0 迁移：数据格式转换
  - version: "3.0.0"
    when: "{{ _stage == 'before' }}"
    command: ["python", "scripts/migrate_to_v3.py"]
    working_directory: "scripts"

  # 无版本号：每次更新都执行
  - command: "echo 'Migration checks complete'"
    when: "{{ _stage == 'after' }}"
```

迁移任务可用的额外变量：

| 变量 | 说明 |
|------|------|
| `_stage` | `"before"` 或 `"after"` |
| `_version_from` | 旧版本 commit 描述 |
| `_version_to` | 新版本 commit 描述 |
| `_version_pep440_from` | 旧版本 PEP440 Version 对象 |
| `_version_pep440_to` | 新版本 PEP440 Version 对象 |
| `_version_current` | 当前迁移的版本号 |
| `_copier_operation` | 固定为 `"update"` |

对应环境变量（大写，去掉 `_` 前缀）：`STAGE`、`VERSION_FROM`、`VERSION_TO`、`VERSION_PEP440_FROM`、`VERSION_PEP440_TO`、`VERSION_CURRENT`、`COPIER_OPERATION`。

### 迁移版本比较逻辑

```
新版本 >= 迁移版本 > 旧版本 → 执行迁移
```

例如：从 v1.0.0 更新到 v3.0.0，version="2.0.0" 的迁移会执行；version="3.5.0" 的不会执行。

### 迁移执行顺序

1. **before 阶段**：在新模板渲染前执行（用于清理旧文件、数据迁移）
2. **新模板渲染**：应用新模板的文件变更
3. **after 阶段**：在新模板渲染后执行（用于安装新依赖、更新配置）

## 7. 完整模板示例：Python 包模板

```yaml
# copier.yml
_templates_suffix: ".jinja"
_min_copier_version: "9.0.0"

project_name:
  type: str
  help: "项目名称"
  default: "my-package"

package_name:
  type: str
  default: "{{ project_name|replace('-', '_') }}"

author_name:
  type: str
  help: "作者"

python_version:
  type: str
  default: "3.12"
  choices: ["3.10", "3.11", "3.12", "3.13"]

use_docker:
  type: bool
  default: false

install_deps:
  type: bool
  default: true

_message_after_copy: |
  🎉 {{ project_name }} 创建成功！

_tasks:
  # 初始化 Git
  - command: "git init"

  # 安装依赖
  - command: ["pip", "install", "-e", ".[dev]"]
    when: "{{ install_deps }}"

  # Docker 构建
  - command: "docker build -t {{ project_name }} ."
    when: "{{ use_docker }}"

  # 初始提交
  - command:
      - "git"
      - "add"
      - "."

  - command:
      - "git"
      - "commit"
      - "-m"
      - "Initial commit from Copier template"
      - "--no-verify"
```

生成命令：
```bash
copier copy --trust ./my-template ./new-package
```

## 8. 任务执行输出

执行任务时，Copier 会在 stderr 显示进度：

```
 > Running task 1 of 4: git init
 > Running task 2 of 4: ['pip', 'install', '-e', '.[dev]']
 > Running task 3 of 5: docker build -t my-package .
 > Running task 4 of 5: ['git', 'add', '.']
 > Running task 5 of 5: ['git', 'commit', '-m', 'Initial commit from Copier template', '--no-verify']
```

失败的任务会抛出 `TaskError`（继承 `CalledProcessError`），包含命令、返回码、stdout、stderr 信息，中止整个流程。

## 9. --skip-tasks 和 pretend 模式

### 跳过任务

```bash
# 生成项目但不执行任务
copier copy -T ./template ./output
```

`-T/--skip-tasks` 跳过所有任务执行，包括迁移任务。

### 预演模式

```bash
# 查看将要执行的操作（包括任务），但不实际修改文件
copier copy -n --trust ./template ./output
```

`-n/--pretend` 模式下，任务只会打印命令而不会实际执行。

## 相关概念

* [任务与迁移](../concepts/07-tasks-and-migrations.md)
* [Worker 与生命周期](../concepts/05-worker-and-lifecycle.md)
* [安全与信任机制](../concepts/09-security-and-safety.md)
* [CLI 命令参考](../concepts/08-cli-reference.md)
* [项目更新工作流示例](update-workflow.md)

[^copier-src]: Copier 源码，见本 bundle 信源登记 [references/copier-source.md](../references/copier-source.md)。
