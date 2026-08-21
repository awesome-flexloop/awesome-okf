---
type: Concept
title: 配置项详解
description: rediraffe 的四个配置项（rediraffe_redirects/branch/template/auto_redirect_perc）的类型、默认值、使用场景与注意事项
tags: [sphinxext-rediraffe, configuration, confval, rediraffe_redirects, rediraffe_branch]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# 配置项详解

sphinxext-rediraffe 通过 Sphinx 的标准配置机制（`conf.py` 中的变量）提供四个配置项。所有配置均通过 `app.add_config_value()` 注册，第三个参数为 `None` 表示配置值可以是任何类型，不做环境 rebuild 触发。

## 配置项总览

| 配置项 | 类型 | 默认值 | 必需 | 说明 |
|--------|------|--------|------|------|
| `rediraffe_redirects` | `dict[str, str] | str | None` | `None` | ✅（重定向功能必需） | 重定向映射或文件路径 |
| `rediraffe_branch` | `str` | `''` | diff检查器必需 | Git diff 基准分支/提交 |
| `rediraffe_template` | `str | None` | `None` | ❌ | 自定义Jinja2模板文件路径 |
| `rediraffe_auto_redirect_perc` | `int` | `100` | ❌ | 自动重定向相似度阈值（0-100） |

## rediraffe_redirects

**类型**：`dict[str, str] | str | None`
**默认值**：`None`

这是最核心的配置项，定义了页面重定向映射。支持三种值：

### 值为 dict

直接在 `conf.py` 中用字典定义重定向：

```python
rediraffe_redirects = {
    'old-page.rst': 'new-page.rst',
    'legacy/intro.rst': 'guide/introduction.rst',
}
```

- key：源文件路径（相对于Sphinx源目录），即被重定向走的旧页面
- value：目标文件路径（相对于Sphinx源目录），即用户最终到达的新页面
- 文件后缀应与源文件格式一致（通常是 `.rst`）

适用场景：重定向数量较少（<20条），或重定向配置需要动态生成。

### 值为 str（文件路径）

指定一个外部文本文件路径（相对于源目录）：

```python
rediraffe_redirects = 'redirects.txt'
```

文件格式为每行一对 `源路径 目标路径`，支持注释和引号：

```text
# 这是注释
old-page.rst new-page.rst
legacy/intro.rst guide/introduction.rst

# 路径含空格时用引号
"old tutorial.rst" "tutorials/first-steps.rst"
```

适用场景：重定向数量较多，或需要被 `rediraffewritediff` 自动追加（dict方式不支持自动写入）。

### 值为 None（默认）

不配置重定向。构建时输出警告：

```
rediraffe: rediraffe was not given redirects to process. Redirects will not be generated.
```

适用于临时禁用重定向或在某些构建环境中不需要重定向的场景。

### 配置错误处理

| 错误场景 | 行为 |
|---------|------|
| 文件路径指定的文件不存在 | 输出error日志，设置 `app.statuscode = 1`，跳过重定向生成 |
| 文件格式错误（无法解析的行） | `create_graph` 抛出 ExtensionError，构建失败 |
| 重复key | `create_graph` 抛出 ExtensionError，构建失败 |
| dict中存在循环引用 | `create_simple_redirects` 抛出 ExtensionError，构建失败 |

## rediraffe_branch

**类型**：`str`
**默认值**：`''`（空字符串）

指定 Git diff 检查时对比的基准分支或提交。仅在使用 `rediraffecheckdiff` 或 `rediraffewritediff` 构建器时需要。

```python
rediraffe_branch = 'main~1'     # 对比上一个提交
rediraffe_branch = 'main'       # 对比main分支
rediraffe_branch = 'HEAD~5'     # 对比5个提交前
rediraffe_branch = 'v1.0.0'     # 对比特定tag
```

### Git diff 命令

rediraffe 内部执行两条 git 命令：

```bash
# 检测重命名文件（R状态）
git diff --name-status --diff-filter=R <branch>

# 检测删除文件（D状态）
git diff --diff-filter=D --name-only <branch>
```

如果 `rediraffe_branch` 为空字符串，git diff 命令不带分支参数，对比工作区与HEAD。

### 使用示例

在 CI 中检查相对于主分支的所有文件变更是否都有重定向：

```python
# conf.py
rediraffe_redirects = 'redirects.txt'
rediraffe_branch = 'origin/main'
```

```bash
# CI 命令
sphinx-build -b rediraffecheckdiff . _build/check
```

## rediraffe_template

**类型**：`str | None`
**默认值**：`None`（使用内置默认模板）

指定自定义 Jinja2 模板文件路径（相对于源目录），用于渲染重定向HTML页面。

```python
rediraffe_template = 'rediraffe_template.html'
```

### 模板加载时机

模板文件在 `build-finished` 事件触发时才加载和读取，这意味着：
- 模板文件可以在构建过程中动态生成（例如由其他扩展生成）
- 模板文件路径不需要在构建开始时就存在
- 如果模板文件不存在，会输出警告并回退到默认模板

### 模板可用变量

模板中可以使用以下 Jinja2 变量：

| 变量 | 类型 | 说明 |
|------|------|------|
| `rel_url` | `str` | 从源页面到目标页面的相对URL（如 `../new-page.html`） |
| `from_file` | `Path` | 源文件路径（重定向前的路径，如 `old-page.rst`） |
| `to_file` | `Path` | 目标文件路径（重定向后的路径，如 `new-page.rst`） |
| `from_url` | `Path` | 源HTML路径（相对于outdir，如 `old-page.html`） |
| `to_url` | `Path` | 目标HTML路径（相对于outdir，如 `new-page.html`） |

### 默认模板

```html
<html>
    <head>
        <noscript>
            <meta http-equiv="refresh" content="0; url={{rel_url}}"/>
        </noscript>
    </head>
    <body>
        <script>
            window.location.href = '{{rel_url}}' + (window.location.search || '') + (window.location.hash || '');
        </script>
        <p>You should have been redirected.</p>
        <a href="{{rel_url}}">If not, click here to continue.</a>
    </body>
</html>
```

默认模板包含三个关键机制：
1. **`<noscript>` + meta refresh**：无JavaScript环境下的降级方案
2. **JavaScript 跳转**：将 `window.location.search`（查询参数）和 `window.location.hash`（片段标识）附加到目标URL
3. **手动链接**：用户可点击的 fallback 链接

### 自定义模板示例

一个简单的SEO友好模板：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Page Moved</title>
    <meta http-equiv="refresh" content="0; url={{rel_url}}">
    <link rel="canonical" href="{{rel_url}}">
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
    </style>
</head>
<body>
    <h1>Page Moved</h1>
    <p>This page has moved to <a href="{{rel_url}}">{{to_url}}</a>.</p>
    <p>You should be redirected automatically.</p>
    <script>
        window.location.replace('{{rel_url}}' + window.location.search + window.location.hash);
    </script>
</body>
</html>
```

## rediraffe_auto_redirect_perc

**类型**：`int`
**默认值**：`100`

设置 `rediraffewritediff` 构建器自动添加重定向时的Git重命名相似度阈值。

Git 的重命名检测基于文件内容相似度（0-100%）。当重命名相似度大于等于此阈值时，rediraffe 自动将重命名对追加到redirects文件。

```python
rediraffe_auto_redirect_perc = 100   # 默认：仅100%相似才自动添加
rediraffe_auto_redirect_perc = 90    # 90%以上相似就自动添加
rediraffe_auto_redirect_perc = 50    # 50%以上就添加（激进）
```

### 阈值选择建议

| 阈值 | 场景 | 风险 |
|------|------|------|
| 100（默认） | 安全优先，只自动处理完全重命名 | 小修改后重命名的文件不会被自动添加 |
| 90-99 | 大多数项目推荐，处理轻微修改后的重命名 | 可能将新文件误判为重命名（但内容高度相似时通常正确） |
| 70-89 | 积极模式，重构时可能有用 | 误判风险增加，建议CI中人工审查自动添加的条目 |
| <70 | 不推荐 | 误判风险很高 |

### 注意事项

- 此配置仅影响 `rediraffewritediff` 构建器，不影响正常HTML构建
- 自动写入仅在重定向配置为**文件方式**（str类型）时可用；dict方式会报错
- 删除文件（D状态）无法自动推断目标，始终需要手动添加

## 配置项组合模式

### 模式1：最小配置（仅重定向生成）

```python
extensions = ['sphinxext.rediraffe']
rediraffe_redirects = {
    'old.rst': 'new.rst',
}
```

### 模式2：文件配置 + CI检查

```python
extensions = ['sphinxext.rediraffe']
rediraffe_redirects = 'redirects.txt'
rediraffe_branch = 'origin/main'
```

### 模式3：全功能配置（自动写入+自定义模板）

```python
extensions = ['sphinxext.rediraffe']
rediraffe_redirects = 'redirects.txt'
rediraffe_branch = 'HEAD~1'
rediraffe_template = '_templates/redirect.html'
rediraffe_auto_redirect_perc = 90
```

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [架构概览](/concepts/02-architecture-overview.md)
- [Builder体系详解](/concepts/05-builders.md)
- [Jinja2模板系统](/concepts/06-jinja-templates.md)
- [基础重定向示例](/examples/basic-redirects.md)
- [CI Diff检查集成示例](/examples/diff-checker-ci.md)
- [自动重定向写入示例](/examples/auto-redirect-writer.md)
