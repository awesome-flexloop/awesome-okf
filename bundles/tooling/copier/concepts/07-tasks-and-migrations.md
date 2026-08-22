---
type: Concept
title: 任务与迁移
description: 任务执行、条件任务、工作目录、迁移任务（before/after）、新旧迁移格式、任务环境变量
tags: [copier, tasks, migrations, hooks, automation, shell-commands, post-generation]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# 任务与迁移

Copier 支持在模板渲染后自动执行 shell 命令（任务），以及在项目更新时执行跨版本的迁移脚本。任务和迁移属于**不安全特性**，需要用户显式 `--trust` 授权。[^copier-source]

## Task 数据类

`Task` 类（定义在 `_template.py`）表示一个可执行任务：[^copier-source]

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cmd` | str \| Sequence[str] | 必填 | 要执行的命令。字符串 → shell 执行；列表 → argv 方式执行（不经过 shell） |
| `extra_vars` | dict[str, Any] | `{}` | 额外变量，作为 Jinja2 变量（`_` 前缀）和环境变量（大写）可用 |
| `condition` | str \| bool | `True` | 执行条件，Jinja2 表达式渲染后转布尔 |
| `working_directory` | Path | `Path()` | 工作目录（相对子项目根目录），支持 Jinja2 渲染 |

## 模板任务（_tasks）

在 `copier.yml` 中通过 `_tasks` 定义渲染完成后要执行的命令：

### 简单格式（字符串列表）

```yaml
_tasks:
  - "git init"
  - "pip install -e '.[dev]'"
```

每个字符串作为 shell 命令执行，自动在目标项目目录下运行。

### 完整格式（字典列表）

```yaml
_tasks:
  - command: "git init"
    when: "{{ _copier_operation == 'copy' }}"  # 仅在 copy 时执行
    working_directory: "{{ _copier_conf.dst_path }}"

  - command:
      - "pip"
      - "install"
      - "-e"
      - ".[dev]"
    when: "{{ install_deps }}"
```

字典格式支持：
- `command`：命令（字符串或列表）
- `when`：条件表达式（Jinja2），渲染后通过 `cast_to_bool()` 转布尔值
- `working_directory`：工作目录（默认 `.`，即目标项目根目录）

### 任务执行流程

`Worker._execute_tasks()` 的执行步骤：

1. 遍历任务列表，为每个任务构建 `extra_context`
   - 包含任务的 `extra_vars`（前缀 `_`）
   - 始终包含 `_copier_operation`（copy/update）
2. 渲染 `condition`，条件为假值跳过
3. 渲染命令：
   - 字符串命令 → 渲染后使用 `shell=True` 执行
   - 列表命令 → 逐元素渲染后使用 `shell=False` 执行（更安全）
4. 渲染 `working_directory`，解析为绝对路径
5. 构建环境变量：`extra_vars` 的键名去掉前缀 `_` 后大写（如 `_stage` → `STAGE`）
6. 使用 plumbum 的 `local.cwd()` 和 `local.env()` 设置工作目录和环境
7. `subprocess.run()` 执行命令
8. 返回码非零时抛出 `TaskError`（包含命令、返回码、stdout、stderr）

### 任务中的特殊变量

任务执行时可使用以下额外 Jinja2 变量：

| 变量 | 值 | 说明 |
|------|-----|------|
| `_copier_operation` | `"copy"` / `"update"` | 当前操作类型 |
| `_stage` | `"task"` | 固定为 "task"（普通任务） |

环境变量：
- `COPIER_OPERATION`：`copy` 或 `update`
- `STAGE`：`task`

### 任务安全

- 任务属于不安全特性，`_check_unsafe()` 会检测 `template.tasks` 非空且未 `skip_tasks` 时要求 `--trust`
- `--skip-tasks`/`-T` CLI 选项可跳过所有任务执行
- `pretend` 模式下任务不会实际执行（只打印将要执行的命令）

## 迁移任务（_migrations）

迁移任务在 `copier update` 时执行，用于处理模板版本间的不兼容变更。迁移任务分为两个阶段：

| 阶段 | 执行时机 | 用途 |
|------|---------|------|
| `before` | 新模板渲染**之前** | 数据迁移、旧文件清理、格式转换 |
| `after` | 新模板渲染**之后** | 配置更新、依赖安装、后处理 |

### 新格式（推荐）

```yaml
_migrations:
  - version: "2.0.0"
    when: "{{ _stage == 'before' }}"
    command: "python scripts/migrate_v1_to_v2.py"
    working_directory: "scripts"

  - version: "2.0.0"
    when: "{{ _stage == 'after' }}"
    command: "pip install -e '.[dev]'"

  # 无版本号的迁移：始终执行
  - command: "echo 'migration complete'"
    when: "{{ _stage == 'after' }}"
```

迁移任务字段：
- `version`：触发迁移的版本门槛（PEP440），当 `新版本 >= version > 旧版本` 时执行
- `when`：条件表达式，可使用 `_stage` 变量判断是 before 还是 after 阶段
- `command`：要执行的命令（字符串或列表）
- `working_directory`：工作目录

如果迁移是字符串或列表（非字典），使用默认条件 `{{ _stage == "after" }}`：

```yaml
_migrations:
  - "echo 'This runs after update'"
  - ["echo", "This also runs after update"]
```

### 旧格式（已弃用）

旧格式使用 `before`/`after` 键直接指定命令列表，仍被支持但会发出 `DeprecationWarning`：

```yaml
_migrations:
  - version: "1.0.0"
    before:
      - "echo 'Running before migration to v1.0.0'"
    after:
      - "echo 'Running after migration to v1.0.0'"
```

### 迁移额外变量

迁移任务的 `extra_vars` 包含：

| 变量 | 说明 |
|------|------|
| `_stage` | `"before"` 或 `"after"` |
| `_version_from` | 旧版本的 commit 描述 |
| `_version_to` | 新版本的 commit 描述 |
| `_version_pep440_from` | 旧版本的 PEP440 Version 对象 |
| `_version_pep440_to` | 新版本的 PEP440 Version 对象 |
| `_version_current` | 当前迁移的版本号（有 version 字段时） |
| `_version_pep440_current` | 当前迁移的 PEP440 Version 对象 |
| `_copier_operation` | 固定为 `"update"` |

对应的环境变量：`STAGE`、`VERSION_FROM`、`VERSION_TO`、`VERSION_PEP440_FROM`、`VERSION_PEP440_TO`、`VERSION_CURRENT`、`VERSION_PEP440_CURRENT`、`COPIER_OPERATION`。

### 版本比较逻辑

迁移版本比较基于 PEP440：
- 从模板的 `_migrations` 列表中遍历所有迁移
- 对有 `version` 字段的迁移，检查 `new_version >= migration.version > old_version`
- 无 `version` 字段的迁移始终执行
- before 阶段在渲染前执行，after 阶段在渲染后执行

## 消息钩子

除了任务，Copier 还支持简单的消息提示：

```yaml
_message_before_copy: |
  Welcome! Let's create your new project.
  This will take a few moments...

_message_after_copy: |
  Project created successfully!
  Next steps:
    1. cd {{ project_name }}
    2. pip install -e .
    3. git init && git add . && git commit -m "Initial commit"

_message_before_update: "Upgrading {{ project_name }} to latest template..."
_message_after_update: "Update complete! Please review changes."
```

消息字符串在渲染阶段通过 Jinja2 渲染，可以引用所有模板变量。消息输出到 stderr。

## 任务最佳实践

1. **使用列表命令格式**：`command: ["pip", "install", package]` 比字符串更安全（避免 shell 注入）
2. **使用条件控制**：通过 `when` 条件让任务只在特定情况下执行（如仅 copy 时执行 `git init`）
3. **提供幂等性**：任务应设计为可重复执行不产生副作用
4. **注意工作目录**：默认工作目录是目标项目根目录，子目录任务需要显式指定 `working_directory`
5. **优雅处理失败**：任务失败会抛出 `TaskError` 中止整个流程，考虑使用 `|| true`（shell 模式）容忍非关键命令失败
6. **避免交互式命令**：任务在非 TTY 环境（CI/CD）下也可能执行，避免需要人工输入的命令

## 相关概念

- [模板配置文件](02-template-configuration.md)
- [Worker 与生命周期](05-worker-and-lifecycle.md)
- [安全与信任机制](09-security-and-safety.md)
- [项目更新工作流示例](/examples/update-workflow.md)
- [任务与钩子示例](/examples/tasks-and-hooks.md)
- [Copier 源码信源登记](/references/copier-source.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](/references/copier-source.md)。
