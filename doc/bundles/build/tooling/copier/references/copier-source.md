---
type: Reference
title: Copier 源码信源登记
description: Copier v9.17.2 源码路径、版本信息、核心模块清单与公开 API
tags: [copier, source, reference, v9.17.2]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-github
    resource: https://github.com/copier-org/copier
    title: Copier GitHub 仓库
    author: organization:copier-org
  - id: copier-docs
    resource: https://copier.readthedocs.io/
    title: Copier 官方文档
---

# Copier 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | copier |
| 版本 | **9.17.2** |
| 描述 | A library for rendering project templates（项目模板渲染库与 CLI 工具） |
| 作者 | Copier Org 社区 |
| 许可证 | MIT |
| Python 要求 | ≥ 3.10 |
| 官方文档 | <https://copier.readthedocs.io/> |
| 源码仓库 | <https://github.com/copier-org/copier> |

## 源码位置

Copier 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/copier/copier/copier/
```

该目录通过 git submodule 引入（external 区域），本地不做修改。

## CLI 入口点

`pyproject.toml` 定义了一个命令行入口点 `copier`，指向 `copier.cli:CopierApp.run`。

- `copier` — 主命令，自动判断是执行 `copy` 还是 `update`
  - 目标目录存在且有 answers 文件 → 执行 `copier update`
  - 否则 → 执行 `copier copy`

子命令包括：
- `copier copy <template_src> <destination_path>` — 从模板引导新项目
- `copier recopy [destination_path]` — 重新复制（保留答案，丢弃项目演化）
- `copier update [destination_path]` — 更新已有项目（尊重项目演化）
- `copier check-update [destination_path]` — 检查是否有新版本模板可用

入口模块为 `copier/cli.py`（公开 API 门面），实际实现在 `copier/_cli.py`。`copier/__main__.py` 支持 `python -m copier` 方式调用。

## 核心模块清单

| 模块 | 说明 |
|------|------|
| `__init__.py` | 包入口，导出公开 API：`run_copy`、`run_recopy`、`run_update`、`Phase`、`VcsRef`、`Settings`、`load_settings`；通过 `__getattr__` 延迟代理到 `_main` 模块，对非公开成员触发弃用警告 |
| `__main__.py` | 支持 `python -m copier` 调用，委托给 CLI 入口 |
| `cli.py` | CLI 公开 API 门面，重导出 `_cli` 模块的 CopierApp 等类 |
| `_cli.py` | CLI 实现模块，基于 plumbum.cli 构建：定义 `CopierApp`（主应用）、`_Subcommand`（子命令基类，含公共开关：`-a`/`-x`/`-r`/`-n`/`-s`/`-q`/`-g`/`--UNSAFE`/`-T`/`-d`/`--data-file`）、`CopierCopySubApp`（copy 子命令，含 `-C`/`-l`/`-f`/`-w`/`--ask`）、`CopierRecopySubApp`（recopy 子命令，含 `-l`/`-f`/`-w`/`-A`/`--ask`）、`CopierUpdateSubApp`（update 子命令，含 `-o`/`-c`/`-l`/`-A`/`--ask`）、`CopierCheckUpdateSubApp`（check-update 子命令，含 `--output-format`）；异常处理通过 `_handle_exceptions()` 统一捕获 `UserMessageError`/`UnsafeTemplateError`/`KeyboardInterrupt` |
| `main.py` | 公开 API 门面，重导出 `_main` 模块的核心函数 |
| `_main.py` | 核心执行引擎，定义 `Worker` 类（pydantic dataclass，23 个配置字段：`src_path`/`dst_path`/`answers_file`/`vcs_ref`/`data`/`exclude`/`use_prereleases`/`skip_if_exists`/`cleanup_on_error`/`defaults`/`user_defaults`/`overwrite`/`pretend`/`quiet`/`conflict`/`context_lines`/`unsafe`/`skip_answered`/`skip_tasks`/`ask`/`settings`/`answers`/`_cleanup_hooks`）；支持上下文管理器协议（`__enter__`/`__exit__`）；核心方法：`run_copy()`（全新生成）、`run_recopy()`（重新复制）、`run_update()`（智能更新，含冲突解决）；内部方法：`_ask()`（交互式问卷）、`_render_template()`（模板渲染主循环）、`_render_file()`（单文件渲染，处理 `.jinja` 后缀、可执行位保留）、`_render_folder()`（目录创建）、`_render_symlink()`（符号链接渲染）、`_render_path()`（路径渲染，支持 yield 标签生成多路径）、`_render_string()`（字符串渲染）、`_render_value()`（值渲染，非字符串跳过）、`_render_context()`（生成 Jinja 渲染上下文，含 `_copier_answers`/`_copier_conf`/`_folder_name`/`_copier_python`/`_copier_phase` 等特殊变量）、`_execute_tasks()`（任务执行，支持条件判断、shell/argv 两种模式、工作目录、环境变量注入）、`_check_unsafe()`（安全检查：jinja_extensions/tasks/migrations 触发 UnsafeTemplateError）、`_solve_render_conflict()`（冲突解决：skip→overwrite→交互确认）、`_render_allowed()`（判断是否需要渲染：identical/create/conflict 三态）、`_sync_git_index_executable_bit()`（Windows 下通过 `git update-index --cacheinfo` 同步可执行位）、`_external_data()`（延迟加载外部数据文件，含路径越界检查） |
| `template.py` | 公开 API 门面，重导出 `_template` 模块 |
| `_template.py` | 模板管理模块，定义 `Template` 类（pydantic dataclass，字段：`url`/`ref`/`use_prereleases`/`_temp_clone_path`）；核心属性：`local_abspath`（本地路径，远程模板自动克隆到临时目录）、`_raw_config`（原始 YAML 配置加载）、`config_data`（过滤后的配置，以 `_` 开头的键为配置项）、`questions_data`（问卷问题定义，简化格式自动转复杂格式）、`tasks`（任务列表）、`migration_tasks()`（版本迁移任务，支持新旧两种配置格式）、`commit`/`commit_hash`（Git 提交描述/完整哈希）、`version`（PEP440 版本对象，通过 dunamai 从 Git 标签生成）、`exclude`（排除模式）、`jinja_extensions`（Jinja2 扩展列表）、`envops`（Jinja2 环境配置）、`templates_suffix`（模板文件后缀，默认 `.jinja`）、`answers_relpath`（答案文件相对路径，默认 `.copier-answers.yml`）、`secret_questions`（密码问题集合）、`subdirectory`（模板子目录）、`git_index_modes`（从 Git index 读取的文件模式，用于跨平台保留可执行位）、`preserve_symlinks`（是否保留符号链接）；重要常量：`DEFAULT_EXCLUDE`（默认排除模式：`copier.yaml`/`copier.yml`/`~*`/`*.py[co]`/`__pycache__`/`.git`/`.DS_Store`/`.svn`）、`DEFAULT_TEMPLATES_SUFFIX = ".jinja"`；工具函数：`filter_config()`（分离配置与问题，`_` 前缀为配置，其余为问题）、`load_template_config()`（加载 copier.yml，支持 `!include` 标签 glob 包含、多文档合并）、`verify_copier_version()`（验证最低 Copier 版本要求）；`Task` dataclass：`cmd`（命令字符串或列表）、`extra_vars`（额外变量）、`condition`（执行条件，默认 `True`）、`working_directory`（工作目录，默认 `.`） |
| `subproject.py` | 公开 API 门面 |
| `_subproject.py` | 子项目管理模块，定义 `Subproject` 类（pydantic dataclass，字段：`local_abspath`/`answers_relpath`/`_cleanup_hooks`）；核心属性：`last_answers`（上次答案，排除私有键但保留 `_src_path`/`_commit`）、`template`（上次使用的模板对象，从 answers 文件重建）、`vcs`（VCS 类型检测）；方法：`is_dirty()`（检查工作区是否有未提交更改） |
| `vcs.py` | 公开 API 门面 |
| `_vcs.py` | VCS（版本控制系统）集成模块，目前仅支持 Git；核心函数：`get_git()`（获取配置了 Copier 身份的 git 命令对象，GIT_USER_NAME="Copier", GIT_USER_EMAIL="copier@copier"）、`is_git_available()`（检测 git 是否可用）、`get_repo()`（URL 扩展：`gh:`→GitHub、`gl:`→GitLab、本地路径检测、git bundle 检测）、`clone()`（克隆仓库，远程仓库使用镜像缓存+worktree 机制，本地仓库支持 dirty changes 自动提交、submodule 递归更新）、`get_latest_tag()`（获取最新 PEP440 版本标签，支持 prerelease 过滤，无标签返回 HEAD）、`_get_or_create_mirror()`（基于 SHA256 的镜像缓存，原子创建+remote update 刷新+worktree prune）、`_clone_via_cache()`（通过 git worktree 从镜像创建临时工作树）；URL 快捷方式：`gh:owner/repo` → `https://github.com/owner/repo.git`、`gl:owner/repo` → `https://gitlab.com/owner/repo.git`；缓存目录可通过 `COPIER_CACHE_DIR` 环境变量覆盖 |
| `user_data.py` | 公开 API 门面 |
| `_user_data.py` | 用户数据与问卷模块，定义 `AnswersMap` 类（多源答案合并：user/init/metadata/last/user_defaults/external/system，通过 ChainMap 优先级合并）、`Question` 类（问题对象，支持类型：str/int/float/bool/json/yaml/secret，支持 choices/multiselect，含条件 `when`、验证器 `validator`、默认值渲染、`get_questionary_structure()` 生成 questionary 提示结构）、`load_answersfile_data()`（从 YAML 加载答案文件）；已弃用：`DEFAULT_DATA` 中的 `now()` 和 `make_secret()`（引导用户使用 Jinja2 过滤器替代） |
| `_jinja_ext.py` | Jinja2 扩展模块，定义 `SandboxedEnvironment`（继承 Jinja2 SandboxedEnvironment，添加自定义过滤器和全局函数）、`CopierTemplateLoader`（自定义模板加载器，支持模板后缀处理）、`YieldExtension`（yield 标签扩展，支持路径名中 `{% yield %}` 生成多个文件）、`get_yield_context()`（获取当前 yield 上下文）；内置 Ansible 过滤器扩展（`jinja2_ansible_filters.AnsibleCoreFiltersExtension`）；自定义全局函数：`pathjoin()`（跨平台路径拼接，支持 posix/windows/native 模式）；`to_json` 过滤器补丁以支持 Pydantic dataclass 和 LazyDict/PurePath 序列化 |
| `errors.py` | 异常体系模块，定义完整的异常和警告类层次；错误类：`CopierError`（基类）→`UserMessageError`（用户消息，退出码 1）→`UnsupportedVersionError`/`ExtensionNotFoundError`/`InteractiveSessionError`；`ConfigFileError`→`InvalidConfigFileError`/`MultipleConfigFilesError`；`PathError`→`PathNotAbsoluteError`/`PathNotRelativeError`/`ForbiddenPathError`；`TaskError`（继承 CalledProcessError 和 UserMessageError）、`CopierAnswersInterrupt`（Ctrl+C 中断，保留部分答案）、`UnsafeTemplateError`（不安全模板，退出码 4）、`YieldTagInFileError`/`MultipleYieldTagsError`；警告类：`CopierWarning`（基类）→`UnknownCopierVersionWarning`/`OldTemplateWarning`/`DirtyLocalWarning`/`ShallowCloneWarning`/`MissingSettingsWarning`/`MissingFileWarning` |
| `_types.py` | 类型定义模块，定义核心类型别名和工具类：`StrOrPath`、`AnyByStrDict`、`JSONSerializable`、`VCSTypes = Literal["git"]`、`Operation = Literal["copy", "update"]`、`MISSING`（缺失值哨兵）；`LazyDict`（延迟求值字典，值为零参数函数，首次访问时求值并缓存）；`Phase` 枚举（PROMPT/TASKS/MIGRATE/RENDER/UNDEFINED，支持 `Phase.use()` 上下文管理器和 `Phase.current()` 类方法，基于 ContextVar 实现）；`VcsRef` 枚举（`CURRENT = ":current:"` 特殊值，表示使用已有模板的当前引用）；路径验证器：`path_is_absolute()`/`path_is_relative()`，对应 `AbsolutePath`/`RelativePath` 注解类型 |
| `settings.py` | 公开 API 门面 |
| `_settings.py` | 设置管理模块，定义 `Settings`/`SettingsModel`（pydantic 模型）、`load_settings()`（加载用户配置）、`is_trusted_repository()`（判断仓库是否在信任列表中） |
| `tools.py` | 公开 API 门面 |
| `_tools.py` | 工具函数模块，包含：`copier_version()`（获取版本号）、`OS`（操作系统信息命名空间）、`Style`（输出样式枚举：OK/WARNING/DANGER/IGNORE）、`printf()`（格式化状态输出）、`cast_to_bool()`（字符串转布尔）、`cast_to_str()`/`force_str_end()`（字符串处理）、`normalize_git_path()`/`escape_git_path()`（Git 路径处理）、`scantree()`（目录树递归扫描）、`set_git_alternates()`（Git alternates 设置）、`handle_remove_readonly()`（Windows 只读文件删除处理）、`try_enum()`（字符串转枚举值）、`printf_exception()`（异常格式化输出） |
| `types.py` | 公开 API 门面，重导出 `_types` |
| `_deprecation.py` | 弃用机制模块，定义 `deprecate_member_as_internal()`（成员访问弃用警告）、`deprecate_answers_file_template_path()`（答案文件路径弃用警告） |
| `py.typed` | PEP 561 类型标记文件，表明包含类型注解 |

## 公开 API 导出

`copier/__init__.py` 显式导出以下核心符号：

- **核心函数**：`run_copy()`、`run_recopy()`、`run_update()`（通过 `__getattr__` 延迟代理到 `_main` 模块）
- **枚举类型**：`Phase`（执行阶段）、`VcsRef`（VCS 引用特殊值）
- **配置类**：`Settings`、`load_settings()`
- **延迟访问**：非下划线开头且不在 `{run_copy, run_recopy, run_update}` 中的属性，会触发弃用警告后从 `_main` 获取

CLI 层公开：`CopierApp`（主应用类），以及各子命令类。

## 核心依赖

| 依赖 | 用途 |
|------|------|
| Jinja2 | 模板渲染引擎（SandboxedEnvironment 沙箱模式） |
| plumbum | Shell 命令封装与 CLI 框架（cli.Application、local 命令、colors） |
| pydantic | 数据验证与 dataclass 增强（ConfigDict、field_validator） |
| pyyaml | YAML 配置文件解析 |
| questionary | 交互式终端问卷（confirm、unsafe_prompt、Choice） |
| packaging | PEP440 版本解析与比较 |
| pathspec | gitignore/gitwildmatch 模式匹配（文件排除） |
| funcy | 函数式工具（lflatten 列表扁平化） |
| dunamai | 从 Git 标签动态生成 PEP440 版本号 |
| prompt_toolkit | 终端交互底层（PygmentsLexer 语法高亮） |
| pygments | 语法高亮（JsonLexer、YamlLexer） |
| platformdirs | 跨平台用户缓存目录定位 |
| jinja2-ansible-filters | Ansible 兼容的 Jinja2 过滤器集 |

[^copier-github]: Copier 源码仓库：<https://github.com/copier-org/copier>
[^copier-docs]: Copier 官方文档：<https://copier.readthedocs.io/>
