---
type: Reference
title: post_gen_project.py 生成后钩子解析
description: 解析 Cookiecutter 的 post_gen_project.py 钩子脚本，理解条件文件删除机制和递归路径删除工具函数。
tags: [reference, cookiecutter, hooks, post-generation, conditional-files]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: post-gen-py
    resource: https://github.com/jupyter-server/extension-cookiecutter/blob/main/hooks/post_gen_project.py
    title: post_gen_project.py 源码
---

## 完整源码

```python
#!/usr/bin/env python
from pathlib import Path

PROJECT_DIRECTORY = Path.cwd()


def remove_path(path: str) -> None:
    """Remove the provided path.

    If the target path is a directory, remove it recursively.
    """
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        for f in path.iterdir():
            remove_path(f)
        path.rmdir()


if __name__ == "__main__":

    if not "{{ cookiecutter.has_binder }}".lower().startswith("y"):
        remove_path(PROJECT_DIRECTORY / "binder")
        remove_path(PROJECT_DIRECTORY / ".github/workflows/binder-on-pr.yml")
```

## 执行时机

`hooks/post_gen_project.py` 是 Cookiecutter 的**生成后钩子**。Cookiecutter 在以下时机执行钩子脚本：

1. 模板文件全部渲染并写入目标目录**之后**
2. 在输出最终成功消息**之前**
3. 工作目录已切换到生成的项目目录（`Path.cwd()` 指向新生成的项目根目录）

钩子脚本放在模板根目录的 `hooks/` 子目录下，文件名固定为 `pre_gen_project.py`（生成前）、`post_gen_project.py`（生成后）等。

## 核心函数：remove_path

```python
def remove_path(path: str) -> None:
    """Remove the provided path.

    If the target path is a directory, remove it recursively.
    """
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        for f in path.iterdir():
            remove_path(f)
        path.rmdir()
```

这是一个递归删除工具函数：

1. **文件检测**：`path.is_file()` 判断是否为文件，是则调用 `path.unlink()` 删除文件
2. **目录检测**：`path.is_dir()` 判断是否为目录
3. **递归遍历**：`path.iterdir()` 遍历目录中所有条目，对每个条目递归调用 `remove_path`
4. **删除空目录**：所有子项删除后，调用 `path.rmdir()` 删除空目录本身（`rmdir()` 只能删除空目录）

这相当于实现了 `shutil.rmtree()` 的功能，但使用 pathlib 面向对象 API。

> **为什么不用 shutil.rmtree？** pathlib 是 Python 3.4+ 标准的面向对象路径 API，类型注解更清晰（`Path` 对象而非字符串），链式调用更优雅。在新代码中使用 pathlib 是 Jupyter 生态的惯例。

## 条件删除逻辑

```python
if __name__ == "__main__":

    if not "{{ cookiecutter.has_binder }}".lower().startswith("y"):
        remove_path(PROJECT_DIRECTORY / "binder")
        remove_path(PROJECT_DIRECTORY / ".github/workflows/binder-on-pr.yml")
```

### 条件判断解析

```python
if not "{{ cookiecutter.has_binder }}".lower().startswith("y"):
```

1. `"{{ cookiecutter.has_binder }}"` 在渲染时被替换为用户输入值（`"y"` 或 `"n"`）
2. `.lower()` 将输入转为小写，实现大小写不敏感匹配
3. `.startswith("y")` 判断是否以 `y` 开头（匹配 `y`、`Y`、`yes`、`Yes`、`YES` 等）
4. `not` 取反：用户未选择 Binder 时执行删除

### 删除的路径

当用户选择不需要 Binder（`has_binder` 不以 `y` 开头）时，删除两个路径：

| 路径 | 类型 | 说明 |
|------|------|------|
| `binder/` | 目录 | Binder 配置目录（包含 environment.yml 和 postBuild） |
| `.github/workflows/binder-on-pr.yml` | 文件 | PR 自动评论 Binder 链接的 GitHub Action |

这两个路径是 Binder 集成的全部内容，删除后项目就不再包含 Binder 相关配置。

### 为什么不用 Jinja2 条件块？

模板中的 `README.md` 使用 Jinja2 条件块控制 Binder badge 的显示：

```jinja2
{%- if cookiecutter.has_binder.lower().startswith('y') -%}
[![Binder](...)
{%- endif %}
```

但整个目录和文件的条件包含/排除无法通过 Jinja2 模板语法实现（Jinja2 只处理文件内容，不处理文件是否存在），因此需要通过 post_gen_project 钩子来删除不需要的文件和目录。

## 钩子执行上下文

```python
PROJECT_DIRECTORY = Path.cwd()
```

Cookiecutter 执行钩子脚本时，工作目录（cwd）已经是生成后的项目目录。例如：
- 用户执行 `cookiecutter https://... -o ~/projects`
- 输入包名 `my_extension`
- 钩子执行时 cwd = `~/projects/my_extension`

因此 `Path.cwd()` 直接指向新项目根目录，`PROJECT_DIRECTORY / "binder"` 解析为 `~/projects/my_extension/binder`。

## 扩展钩子的模式

基于此模板的模式，可以在 post_gen_project 中实现更多条件逻辑：

```python
if __name__ == "__main__":
    # 根据用户选择删除不需要的组件
    if not "{{ cookiecutter.has_cli }}".lower().startswith("y"):
        remove_path(PROJECT_DIRECTORY / "{{ cookiecutter.package_name }}" / "cli.py")

    if "{{ cookiecutter.has_frontend }}".lower().startswith("n"):
        remove_path(PROJECT_DIRECTORY / "src")
        remove_path(PROJECT_DIRECTORY / "package.json")

    # 初始化 git 仓库
    import subprocess
    subprocess.run(["git", "init"], cwd=PROJECT_DIRECTORY)

    # 打印成功消息
    print("🎉 Extension project created successfully!")
```

## 相关概念

- [Cookiecutter 模板引擎基础](/concepts/02-cookiecutter-basics.md)
- [项目结构详解](/concepts/03-project-structure.md)
- [Binder 集成](/concepts/10-binder-integration.md)
