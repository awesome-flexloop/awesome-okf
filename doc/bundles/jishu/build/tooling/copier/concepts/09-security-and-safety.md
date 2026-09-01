---
type: Concept
title: 安全与信任机制
description: 沙箱环境、不安全特性检测、信任机制、ForbiddenPathError、符号链接安全、外部数据路径限制、secret 问题
tags: [copier, security, safety, sandbox, trust, unsafe, forbidden-path]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# 安全与信任机制

Copier 采用"默认安全"（secure by default）设计：模板运行在 Jinja2 沙箱中，危险特性需要用户显式授权。这确保了使用第三方模板时不会在不知情的情况下执行任意代码。[^copier-source]

## 威胁模型

Copier 模板可能来自不受信任的第三方（如公开的 GitHub 仓库），可能包含恶意代码。Copier 的安全机制旨在防止以下威胁：

1. **任意代码执行**：通过 Jinja2 扩展或任务执行 shell 命令
2. **路径遍历**：通过模板路径渲染访问项目目录外的文件
3. **敏感信息泄露**：通过模板变量读取系统文件或环境变量
4. **符号链接攻击**：通过符号链接指向模板外的敏感文件
5. **数据外泄**：通过外部数据功能读取项目外的配置文件

## SandboxedEnvironment：沙箱渲染

所有 Jinja2 模板渲染在 `SandboxedEnvironment` 中执行，这是 Jinja2 提供的安全环境：

- **禁止访问私有属性**：无法访问以下划线开头的属性/方法
- **限制内置函数**：无法直接调用 `eval()`、`exec()`、`open()` 等危险函数
- **禁止模块导入**：无法通过模板直接 import Python 模块
- **运算符重载保护**：对算术运算、属性访问等操作进行安全检查

沙箱环境通过 `_jinja_ext.py` 中的 `SandboxedEnvironment` 类实现，基于 Jinja2 原生的 `jinja2.sandbox.SandboxedEnvironment`。

## 不安全特性检测

`Worker._check_unsafe(mode)` 在执行 copy/update 前检测以下不安全特性：

| 不安全特性 | 检测条件 | 风险 |
|-----------|---------|------|
| `jinja_extensions` | 模板定义了自定义 Jinja2 扩展 | 扩展可绕过沙箱限制，执行任意 Python 代码 |
| `tasks` | 模板定义了任务且未 `--skip-tasks` | 任务在 shell 中执行任意命令 |
| `migrations` | update 时新旧版本间有迁移任务 | 迁移脚本在 shell 中执行任意命令 |

检测逻辑：
1. 如果用户指定了 `--trust`/`--UNSAFE`（即 `unsafe=True`），跳过检查
2. 如果模板 URL 在用户信任列表中（`is_trusted_repository()`），跳过检查
3. 否则收集所有检测到的不安全特性
4. 如果有不安全特性，抛出 `UnsafeTemplateError`

### UnsafeTemplateError

```
Template uses potentially unsafe features: jinja_extensions, tasks.
If you trust this template, consider adding the `--trust` option when running `copier copy/update`.
```

退出码为 4（二进制 `100`），与普通错误（退出码 1）区分。

## 信任机制

### --trust / --UNSAFE 标志

用户通过 CLI 标志显式信任模板：

```bash
copier copy --trust gh:user/template my-project
copier copy --UNSAFE ./local-template output/
copier update --trust
```

API 中对应 `unsafe=True` 参数：

```python
run_copy("template/path", "output", unsafe=True)
```

### 信任列表配置

通过 `Settings` 配置文件可以配置仓库信任列表，`is_trusted_repository()` 检查 URL 是否匹配信任规则。信任配置位于用户设置文件中，避免每次都需要手动指定 `--trust`。

CLI 启动时也会显示黄色安全警告：
```
WARNING! Use only trusted project templates, as they might
execute code with the same level of access as your user.
```

## ForbiddenPathError：路径越界保护

Copier 在多处实施路径安全检查，防止路径遍历攻击：

### 模板路径检查

在 `_render_template()` 中：
- 符号链接如果指向模板目录外，且不保留符号链接模式，抛出 `ForbiddenPathError`
- 渲染后的目标路径必须在 `dst_root` 内（`is_relative_to(dst_root)`），否则抛出 `ForbiddenPathError`

```python
if not dst_realpath.is_relative_to(dst_root):
    raise ForbiddenPathError(path=dst_relpath)
```

### Subdirectory 路径检查

`template_copy_root` 计算模板子目录后检查其是否在模板目录内：
```python
if not path.is_relative_to(self.template.local_abspath):
    raise ForbiddenPathError(path=Path(subdir))
```

### 外部数据路径检查

外部数据文件（`_external_data`）路径必须在目标项目目录内：
```python
if not (dst_path / rendered_path).resolve().is_relative_to(subproject.local_abspath):
    if not self.unsafe:
        raise ForbiddenPathError(path=Path(path), hint="...")
```

错误消息包含提示信息，指导用户使用 `--trust` 覆盖检查。

### !include 路径检查

`copier.yml` 中的 `!include` 标签：
- 不允许绝对路径
- 包含的文件必须在模板根目录内
- 违反时抛出 `ForbiddenPathError`

## 符号链接安全

符号链接处理有两种模式：

### 默认模式（preserve_symlinks=False）

不保留符号链接，而是复制链接指向的内容。安全检查：
- 如果符号链接指向模板目录外，抛出 `ForbiddenPathError`（防止链接到 /etc/passwd 等敏感文件）
- 写入前如果目标是符号链接，先 `unlink()` 再创建文件/目录

### 保留模式（_preserve_symlinks: true）

保留符号链接，在目标目录创建对应的符号链接：
- 允许符号链接指向项目目录外（因为链接本身在项目内）
- 但渲染时不跟随到项目外的目录内容

macOS 上额外复制符号链接的权限位（`lchmod`）。

## Secret 问题与答案文件

标记为 `secret: true` 的问题（或在 `_secret_questions` 列表中的问题）：
- 在交互式输入时使用密码提示（不回显）
- **不会写入 `.copier-answers.yml`** 文件，防止敏感信息泄露到磁盘

```yaml
_secret_questions:
  - db_password
  - api_key

db_password:
  type: secret
  help: "数据库密码"
```

## Settings 配置

`_settings.py` 定义 `SettingsModel` 和用户配置管理：
- `load_settings()` 加载用户配置文件
- `is_trusted_repository(trust_list, url)` 判断仓库是否在信任列表中
- 缺失设置文件时发出 `MissingSettingsWarning`

## 错误类型与安全边界

| 异常 | 触发场景 | 用户可覆盖？ |
|------|---------|------------|
| `UnsafeTemplateError` | 使用了 jinja_extensions/tasks/migrations 但未 trust | ✅ `--trust` |
| `ForbiddenPathError` | 路径越界（目录遍历、外部数据越界、include 越界） | ⚠️ 仅外部数据可 `--trust`，模板路径/symlink 越界不可覆盖 |
| `ExtensionNotFoundError` | Jinja2 扩展加载失败（安装缺失） | ❌ 需要安装依赖 |
| `YieldTagInFileError` | 文件内容中使用了 yield 标签 | ❌ 设计限制 |
| `MultipleYieldTagsError` | 单路径中使用多个 yield 标签 | ❌ 设计限制 |

设计上，模板路径和符号链接的越界检查**不可通过 `--trust` 覆盖**，这些是硬性安全边界。只有 jinja_extensions/tasks/migrations 这类"功能需要"的不安全性才允许通过信任机制授权。

## 安全最佳实践

1. **审查模板来源**：只使用来自可信来源的模板，审查其 `copier.yml` 和任务定义
2. **首次使用前检查**：在不安全环境（如容器中）首次运行模板，观察其行为
3. **使用 --pretend 预演**：`-n/--pretend` 可以查看将要做什么而不做实际修改
4. **最小权限原则**：以普通用户而非 root 运行 copier
5. **标记敏感信息为 secret**：密码、API key 等始终使用 `type: secret`
6. **CI/CD 中固定版本**：使用 `-r` 指定具体标签/commit，避免模板更新引入风险
7. **审查 tasks 和 migrations**：这些是 shell 命令执行点，仔细审查其内容

```bash
# 安全预演：查看将要执行的操作
copier copy -n template/ output/

# 非交互模式不使用 --trust 会在不安全模板时失败
copier copy -l template/ output/
# 报错退出码 4，不会执行危险操作
```

## 相关概念

- [Jinja2 模板渲染](04-jinja2-templating.md)
- [Worker 与生命周期](05-worker-and-lifecycle.md)
- [任务与迁移](07-tasks-and-migrations.md)
- [模板配置文件](02-template-configuration.md)
- [Copier 源码信源登记](../references/copier-source.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](../references/copier-source.md)。
