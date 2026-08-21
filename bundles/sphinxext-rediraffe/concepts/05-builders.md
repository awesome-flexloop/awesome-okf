---
type: Concept
title: Builder体系详解
description: rediraffe的三个构建器角色：html/dirhtml自动重定向生成、rediraffecheckdiff变更检查、rediraffewritediff自动写入
tags: [sphinxext-rediraffe, builder, rediraffecheckdiff, rediraffewritediff, git-diff, ci]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# Builder体系详解

rediraffe 的功能通过 Sphinx 的 Builder 体系实现。除了在标准的 `html` 和 `dirhtml` 构建器上自动工作外，rediraffe 还注册了两个专用 Builder 用于 CI/CD 场景。

## Builder 总览

| Builder名称 | 类 | 用途 | 触发方式 |
|------------|-----|------|---------|
| `html` | `StandaloneHTMLBuilder` | 正常HTML构建，自动生成重定向文件 | `sphinx-build -b html` |
| `dirhtml` | `DirectoryHTMLBuilder` | 目录URL构建，自动生成重定向文件 | `sphinx-build -b dirhtml` |
| `readthedocs` | — | ReadTheDocs HTML构建 | RTD自动使用 |
| `readthedocsdirhtml` | — | ReadTheDocs目录HTML构建 | RTD自动使用 |
| `rediraffecheckdiff` | `CheckRedirectsDiffBuilder` | Git diff检查：验证删除/重命名文件都有重定向 | `sphinx-build -b rediraffecheckdiff` |
| `rediraffewritediff` | `WriteRedirectsDiffBuilder` | 自动写入：基于Git diff自动追加重定向到文件 | `sphinx-build -b rediraffewritediff` |

> `html`、`dirhtml`、`readthedocs`、`readthedocsdirhtml` 不是 rediraffe 自定义的 Builder，而是通过 `build-finished` 事件钩子在这些 Builder 构建完成后生成重定向文件。`rediraffecheckdiff` 和 `rediraffewritediff` 才是 rediraffe 注册的自定义 Builder。

## 标准构建器的重定向生成

当使用 `html` 或 `dirhtml` 构建器时，rediraffe 的 `build_redirects` 函数在 `build-finished` 事件触发时自动执行。

### 构建器类型检查

`build_redirects` 中对构建器类型做了显式检查：

```python
if isinstance(app.builder, CheckExternalLinksBuilder):
    logger.info('rediraffe: Redirect generation skipped for linkcheck builders.')
    return

if (type(app.builder) not in (StandaloneHTMLBuilder, DirectoryHTMLBuilder)
    and app.builder.name not in READTHEDOCS_BUILDERS):
    logger.info('rediraffe: Redirect generation skipped for unsupported builders.')
    return
```

- **linkcheck 构建器**：跳过（链接检查时不需要重定向文件）
- **非HTML构建器**（如latex、text、man等）：跳过并输出info日志
- **HTML/DirHTML/ReadTheDocs构建器**：正常生成重定向

### html vs dirhtml 的路径差异

两种构建器生成的URL结构不同，rediraffe 会自动适配：

**html 构建器（StandaloneHTMLBuilder）**：
- 每个 `.rst` 文件生成一个独立的 `.html` 文件
- `page.rst` → `page.html`
- 重定向文件直接生成 `.html` 文件

**dirhtml 构建器（DirectoryHTMLBuilder）**：
- 每个非index页面生成一个目录，内含 `index.html`
- `page.rst` → `page/index.html`
- index文件例外：`index.rst` → `index.html`（不嵌套目录）

代码中的特殊处理：

```python
if type(app.builder) is DirectoryHTMLBuilder:
    if redirect_from_name != 'index':
        redirect_from = src_redirect_from.parent / redirect_from_name / 'index.html'
    if redirect_to_name != 'index':
        redirect_to = src_redirect_to.parent / redirect_to_name / 'index.html'
```

## CheckRedirectsDiffBuilder：变更检查器

`rediraffecheckdiff` 是一个"伪构建器"——它不生成任何输出文件，而是利用 Builder 的生命周期执行 Git diff 检查。

### 设计理念

在文档项目中，当开发者删除或重命名文件时，经常忘记添加对应的重定向配置。这会导致线上文档出现404错误。`rediraffecheckdiff` 通过 Git diff 自动检测这些"漏网之鱼"，适合集成到 CI 流水线中。

### 执行流程

```
sphinx-build -b rediraffecheckdiff -D rediraffe_branch=main . _build/check
    │
    └─ CheckRedirectsDiffBuilder.init()
         │
         ├─ 1. 解析 rediraffe_redirects 配置
         │      ├─ dict → 直接使用
         │      └─ str → 调用 create_graph() 解析文件
         │
         ├─ 2. 获取Git仓库根目录
         │      git rev-parse --show-toplevel
         │
         ├─ 3. 检测重命名文件
         │      git diff --name-status --diff-filter=R <branch>
         │      输出格式: R<相似度>	<旧路径>	<新路径>
         │      解析为 {旧路径: (新路径, 相似度%)}
         │
         ├─ 4. 检测删除文件
         │      git diff --diff-filter=D --name-only <branch>
         │      输出为删除文件列表
         │
         ├─ 5. 过滤非源目录、非源后缀文件
         │      abs_path_in_src_dir_w_src_suffix()
         │
         └─ 6. 验证每个变更文件
                ├─ 删除文件在重定向配置中 → info日志 "deleted file ... redirects to ..."
                ├─ 删除文件不在配置中 → error日志 "(broken) ... was deleted but is not redirected!"
                ├─ 重命名文件在配置中 → info日志 "renamed file ... redirects to ..."
                └─ 重命名文件不在配置中 → error日志 "(broken) ... was renamed to ... with similarity of N%!"
```

### 路径过滤

`abs_path_in_src_dir_w_src_suffix` 函数确保只检查源目录内的文档文件：

```python
def abs_path_in_src_dir_w_src_suffix(filename: str) -> Path | None:
    abs_path = (repo_root / filename.strip()).resolve()
    if not str(abs_path).startswith(str(src_path)):
        return None  # 不在源目录内
    if abs_path.suffix not in source_suffixes:
        return None  # 不是源文件（.rst/.md等）
    return abs_path
```

这会自动过滤掉：
- 源目录外的文件（如配置文件、CI脚本）
- 非文档文件（如图片、CSS等静态资源）

### 使用方式

```bash
# 检查相对于main分支的变更
sphinx-build -b rediraffecheckdiff -D rediraffe_branch=origin/main . _build/check

# 检查最近1个提交的变更
sphinx-build -b rediraffecheckdiff -D rediraffe_branch=HEAD~1 . _build/check

# 退出码0表示所有变更都有重定向，非0表示有遗漏
echo $?
```

CI 中可以用退出码判断是否通过检查。

### Builder 抽象方法实现

`CheckRedirectsDiffBuilder` 继承自 `sphinx.builders.Builder`，必须实现以下抽象方法：

| 方法 | 实现 | 说明 |
|------|------|------|
| `init()` | 完整实现（执行diff检查） | Builder初始化时调用 |
| `get_outdated_docs()` | 返回 `[]` | 不触发任何文档重建 |
| `prepare_writing(docnames)` | `pass` | 不需要写文档准备 |
| `write_doc(docname, doctree)` | `pass` | 不需要写单个文档 |
| `get_target_uri(docname, typ)` | 返回 `''` | 不需要URI映射 |
| `read()` | 返回 `[]` | 不需要读取源文件 |

这些空实现使得 rediraffecheckdiff 成为一个"只读检查器"，不产生任何输出文件。

## WriteRedirectsDiffBuilder：自动写入器

`rediraffewritediff` 继承自 `CheckRedirectsDiffBuilder`，在检查的基础上增加了自动写入功能。

### 与 CheckRedirectsDiffBuilder 的区别

| 特性 | CheckRedirectsDiffBuilder | WriteRedirectsDiffBuilder |
|------|--------------------------|--------------------------|
| 检查重定向覆盖 | ✅ | ✅ |
| 自动追加到redirects文件 | ❌ | ✅ |
| 要求redirects为文件 | ❌（dict也可以） | ✅（必须是str文件路径） |
| 使用相似度阈值 | ❌ | ✅（`rediraffe_auto_redirect_perc`） |

### 自动写入逻辑

```python
if self.name == 'rediraffewritediff':
    if perc >= self.app.config.rediraffe_auto_redirect_perc:
        # 构造引号包裹的路径
        rel_rename_from = f'"{PurePosixPath(renamed_file.relative_to(src_path))}"'
        rel_rename_to = f'"{PurePosixPath(hint_to.relative_to(src_path))}"'
        # 追加到redirects文件
        with redirects_path.open('a', encoding='utf-8') as redirects_file:
            redirects_file.write(f'{rel_rename_from} {rel_rename_to}\n')
```

关键细节：
- 自动写入的条目使用**双引号包裹路径**，即使路径不含空格也会包裹
- 使用 `PurePosixPath` 确保路径使用正斜杠（跨平台兼容）
- 以**追加模式**（`'a'`）打开文件，不覆盖已有内容
- 仅当相似度 ≥ `rediraffe_auto_redirect_perc` 阈值时才自动写入

### 前置条件检查

`WriteRedirectsDiffBuilder.init()` 在调用父类 `init()` 之前，先验证配置：

```python
rediraffe_redirects = self.app.config.rediraffe_redirects
if not isinstance(rediraffe_redirects, str):
    logger.error('(broken) Automatic redirects is only available with a redirects file.')
    self.app.statuscode = 1
    return
```

如果使用 dict 方式配置重定向，自动写入会报错（因为无法自动追加到dict中）。

### 使用场景

`rediraffewritediff` 适合在**本地开发**时使用，自动补全重定向配置后开发者再审查和提交：

```bash
# 自动将高相似度重命名追加到redirects.txt
sphinx-build -b rediraffewritediff -D rediraffe_branch=HEAD~1 -D rediraffe_auto_redirect_perc=90 . _build/write

# 审查自动添加的条目
cat redirects.txt

# 确认无误后提交
git add redirects.txt
```

不建议在 CI 中使用 writediff 自动写入（CI应该是只读检查），CI 应使用 checkdiff。

## 构建器在CI/CD中的典型用法

### Pull Request 检查

```yaml
# GitHub Actions 示例
- name: Check redirects
  run: |
    sphinx-build -b rediraffecheckdiff \
      -D rediraffe_branch=origin/${{ github.base_ref }} \
      docs docs/_build/check
```

### 本地开发工作流

```bash
# 1. 重命名或删除一些文件
git mv docs/old-page.rst docs/new-page.rst

# 2. 自动生成重定向
sphinx-build -b rediraffewritediff -D rediraffe_branch=HEAD~1 . _build/write

# 3. 正常构建，验证重定向生效
sphinx-build -b html . _build/html

# 4. 提交重定向配置
git add redirects.txt
```

## 相关概念

- [架构概览](/concepts/02-architecture-overview.md)
- [配置项详解](/concepts/04-configuration.md)
- [路径处理与跨平台兼容](/concepts/07-path-and-cross-platform.md)
- [CI Diff检查集成示例](/examples/diff-checker-ci.md)
- [自动重定向写入示例](/examples/auto-redirect-writer.md)
