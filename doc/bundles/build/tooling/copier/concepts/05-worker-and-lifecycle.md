---
type: Concept
title: Worker 与生命周期
description: Worker 类、copy/recopy/update 三种操作、执行阶段、上下文管理器、冲突解决、外部数据延迟加载
tags: [copier, worker, lifecycle, run-copy, run-update, run-recopy, phases]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# Worker 与生命周期

`Worker` 类是 Copier 的核心执行引擎，管理模板渲染的完整生命周期。它是一个 pydantic dataclass，支持上下文管理器协议，提供 `run_copy()`、`run_recopy()`、`run_update()` 三种主要操作。[^copier-source]

## Worker 类概览

### 配置字段（23 个）

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `src_path` | str \| None | None | 模板路径（本地/远程 URL）；update 时可为 None（从 answers 文件读取） |
| `dst_path` | Path | `Path()` | 目标项目路径 |
| `answers_file` | RelativePath \| None | None | 答案文件相对路径（覆盖模板默认） |
| `vcs_ref` | str \| VcsRef \| None | None | 指定模板版本（标签/commit/HEAD/:current:） |
| `data` | dict | `{}` | 预置答案数据（等价于 `--data`） |
| `exclude` | Sequence[str] | `()` | 额外排除模式 |
| `use_prereleases` | bool | False | 比较最新标签时包含预发布版本 |
| `skip_if_exists` | Sequence[str] | `()` | 存在时跳过的文件模式 |
| `cleanup_on_error` | bool | True | 出错时删除目标目录（仅当目录由 Copier 创建） |
| `defaults` | bool | False | 使用默认答案，不询问 |
| `user_defaults` | dict | `{}` | 用户默认值（覆盖模板默认） |
| `overwrite` | bool | False | 覆盖已有文件不询问 |
| `pretend` | bool | False | 模拟运行，不做实际修改 |
| `quiet` | bool | False | 静默模式，抑制输出 |
| `conflict` | Literal["inline","rej"] | `"inline"` | 冲突解决方式：inline 标记或 .rej 文件 |
| `context_lines` | PositiveInt | 3 | 更新时冲突检测的上下文行数 |
| `unsafe` | bool | False | 允许不安全特性（jinja_extensions/tasks/migrations） |
| `skip_answered` | bool | False | 跳过已有答案的问题 |
| `skip_tasks` | bool | False | 跳过任务执行 |
| `ask` | Sequence[str] | `()` | 强制询问匹配 glob 的问题 |
| `settings` | SettingsModel | 自动加载 | 用户设置 |
| `answers` | AnswersMap | 自动初始化 | 答案映射（内部状态，init=False） |

### 缓存属性（cached_property）

Worker 使用 `@cached_property` 延迟计算昂贵的属性：

| 属性 | 说明 |
|------|------|
| `subproject` | Subproject 对象（目标项目状态） |
| `template` | Template 对象（模板加载、配置解析、Git 克隆） |
| `jinja_env` | 配置好的 SandboxedEnvironment |
| `match_exclude` | 排除模式匹配函数（PathSpec） |
| `match_skip` | skip-if-exists 模式匹配函数 |
| `all_exclusions` | 默认+模板+用户排除的合并列表 |
| `all_skip_if_exists` | skip-if-exists 模式合并列表 |
| `answers_relpath` | 渲染后的答案文件相对路径 |
| `resolved_vcs_ref` | 解析后的 VCS 引用（处理 VcsRef.CURRENT） |
| `template_copy_root` | 模板复制根目录（处理 subdirectory） |

### 上下文管理器协议

Worker 必须作为上下文管理器使用，以确保资源清理：

```python
from copier import run_copy

# 便捷函数（内部创建 Worker 上下文管理器）
run_copy("template/path", "output/path")

# 或者直接使用 Worker
from copier._main import Worker

with Worker(src_path="template/path", dst_path=Path("output")) as worker:
    worker.run_copy()
```

`__exit__` 方法确保在异常发生时调用 `_cleanup()`（清理临时克隆目录等），正常退出时也执行清理。

## 三种核心操作

### run_copy()：全新生成

从模板从零开始生成项目，不考虑目标目录的已有内容。

执行流程：
1. **清除缓存**：删除可能存在的 `match_exclude` 缓存（操作上下文切换）
2. **安全检查**：`_check_unsafe("copy")` 检测不安全特性
3. **前置消息**：打印 `_message_before_copy`
4. **问卷阶段**（Phase.PROMPT）：`_ask()` 交互式收集答案
5. **记录目录状态**：检查目标目录是否已存在（影响出错清理策略）
6. **渲染阶段**（Phase.RENDER）：`_render_template()` 遍历模板树渲染所有文件/目录/符号链接
7. **任务阶段**（Phase.TASKS）：`_execute_tasks(template.tasks)` 执行模板定义的任务
8. **异常处理**：如果目标目录是 Copier 创建的且出错，`rmtree` 清理
9. **后置消息**：打印 `_message_after_copy`

```python
# API 调用
run_copy(
    src_path="gh:user/template",
    dst_path="./my-project",
    data={"project_name": "demo"},
    defaults=True,
    overwrite=True,
    vcs_ref="v2.0.0",
    unsafe=False,
)
```

### run_recopy()：重新复制

更新已有项目，保留答案但丢弃所有项目演化。相当于"忘记本地修改，重新应用模板"。

执行流程：
1. 从 answers 文件读取原始模板 URL（必须存在 `_src_path`）
2. 使用 `replace(self, src_path=original_url)` 创建新 Worker
3. 调用 `run_copy()` 执行全新复制

```python
run_recopy(dst_path="./my-project", defaults=True, overwrite=True)
```

### run_update()：智能更新

更新已有项目到模板新版本，**尊重项目演化**——这是 Copier 区别于一次性脚手架工具的核心能力。

更新流程比 copy 复杂，涉及三向合并：
1. 读取旧模板版本（从 answers 文件的 `_commit`）
2. 获取新模板版本（最新标签或指定 ref）
3. 比较旧模板→新模板的变更
4. 将变更智能应用到已有项目，保留用户在两次 copier 之间所做的修改
5. 处理冲突（inline 标记或 .rej 文件）
6. 执行迁移任务（before/after 阶段）

关键参数：
- `conflict`：`"inline"`（默认，使用 `<<<<<<<`/`=======`/`>>>>>>>` 内联合并标记）或 `"rej"`（生成 `.rej` 补丁文件）
- `context_lines`：冲突检测的上下文行数（越多越精确但冲突越多，越少越宽松）
- `vcs_ref=VcsRef.CURRENT`（`:current:`）：使用上次的模板版本（不升级）

```python
run_update(
    dst_path="./my-project",
    conflict="inline",
    context_lines=3,
    skip_answered=True,
)
```

## 执行阶段（Phase）

Copier 使用 `Phase` 枚举跟踪当前执行阶段，通过 `ContextVar`（`_phase`）在协程/线程上下文中传播：

| 阶段 | 值 | 触发时机 |
|------|-----|---------|
| PROMPT | `"prompt"` | 交互式问卷阶段 |
| TASKS | `"tasks"` | 执行模板任务阶段 |
| MIGRATE | `"migrate"` | 执行版本迁移任务阶段 |
| RENDER | `"render"` | 文件/路径渲染阶段 |
| UNDEFINED | `"undefined"` | 外部数据加载等不确定阶段 |

阶段通过 `Phase.use(phase)` 上下文管理器设置，`Phase.current()` 获取当前阶段。在模板中可通过 `{{ _copier_phase }}` 访问。

操作类型（copy/update）通过 `_operation` ContextVar 和 `@as_operation` 装饰器设置。

## 模板渲染主循环（_render_template）

渲染流程遍历模板目录树（通过 `scantree` 递归扫描），对每个文件/目录/符号链接进行处理：

1. **安全检查**：符号链接如果指向模板外，且不保留符号链接，抛 `ForbiddenPathError`
2. **路径渲染**：`_render_path()` 渲染相对路径（支持 yield 多路径）
3. **目标路径安全**：渲染后的路径必须在 dst_root 内，否则抛 `ForbiddenPathError`
4. **排除匹配**：匹配 exclude 模式的路径跳过
5. **按类型分发**：
   - 符号链接 + preserve_symlinks → `_render_symlink()`
   - 目录 → `_render_folder()`
   - 普通文件 → `_render_file()`

### 外部数据延迟加载

外部数据（`_external_data`）使用 `LazyDict` 实现懒加载：
- 首次访问时才读取 YAML 文件
- 文件路径本身也支持 Jinja2 渲染（使用 UNDEFINED phase）
- 安全检查：数据文件路径必须在目标项目目录内（除非 `--trust`）
- 问卷结束后重新加载（因为路径可能依赖前面问题的答案）

## 任务执行（_execute_tasks）

任务执行流程：
1. 遍历任务列表，为每个任务构建 `extra_context`（含 `_copier_operation`）
2. 渲染 `condition` 条件，条件为假值跳过该任务
3. 渲染命令（字符串→shell 执行，列表→argv 执行）
4. 渲染 `working_directory`（工作目录）
5. 非 pretend 模式下，使用 plumbum `local.cwd()` 和 `local.env()` 设置工作目录和环境变量
6. `subprocess.run()` 执行命令
7. 返回码非零时抛出 `TaskError`

任务执行时，extra_vars 中的变量：
- 作为 Jinja2 变量可用（前缀 `_`，如 `_stage`）
- 作为环境变量可用（大写，去掉 `_` 前缀，如 `STAGE`）

## 安全检查（_check_unsafe）

在执行 copy/update 前检查模板是否使用了不安全特性：

| 特性 | 触发条件 |
|------|---------|
| `jinja_extensions` | 模板定义了自定义 Jinja2 扩展 |
| `tasks` | 模板定义了任务且未 `skip_tasks` |
| `migrations` | update 时新旧模板间存在迁移任务 |

如果检测到不安全特性且用户未指定 `--trust`/`--UNSAFE`，抛出 `UnsafeTemplateError`，列出不安全特性并提示使用 `--trust`。

信任判断也支持通过 `settings.trust` 配置仓库信任列表（`is_trusted_repository()`）。

## 清理机制

Worker 维护 `_cleanup_hooks` 列表，在 `__exit__` 时依次执行。主要清理对象：
- `Template._temp_clone_path`：远程模板的临时克隆目录
- `Subproject._cleanup`：子项目相关临时资源

使用 `contextlib.suppress(Exception)` 确保单个清理方法失败不影响其他清理。

## 便捷函数

Copier 在 `__init__.py` 中导出三个便捷函数，封装了 Worker 的创建和上下文管理：

- `run_copy(src_path, dst_path, **kwargs)`：等价于 `with Worker(...) as w: w.run_copy()`
- `run_recopy(dst_path, **kwargs)`：等价于 `with Worker(...) as w: w.run_recopy()`
- `run_update(dst_path, **kwargs)`：等价于 `with Worker(...) as w: w.run_update()`

这些函数是大多数用户和脚本的主要 API 入口。

## 相关概念

- [Jinja2 模板渲染](04-jinja2-templating.md)
- [问题与答案系统](03-questions-and-answers.md)
- [VCS 集成与版本管理](06-vcs-integration.md)
- [任务与迁移](07-tasks-and-migrations.md)
- [安全与信任机制](09-security-and-safety.md)
- [CLI 命令参考](08-cli-reference.md)
- [Python API 使用示例](/examples/python-api-usage.md)
- [Copier 源码信源登记](/references/copier-source.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](/references/copier-source.md)。
