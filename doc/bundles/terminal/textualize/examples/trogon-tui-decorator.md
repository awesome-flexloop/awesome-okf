---
type: Example
title: 卫星示例：@tui 装饰器为 Click CLI 生成 TUI
description: 演示 Trogon 的 @tui 装饰器与 typer.init_tui 两种接入方式，讲清「内省 CLI 结构 → 生成 Textual 表单 → execvp 执行回原命令」的完整流程，让任意 Click CLI 一键获得 TUI。
tags: [textualize, trogon, click, typer, tui, introspect]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "trogon", resource: "/references/trogon.md", title: "Trogon 仓库信源登记" }]
---

# 卫星示例：@tui 装饰器为 Click CLI 生成 TUI

## 概述

Trogon 是 Textualize 生态中「为 CLI 自动生成友好 TUI」的卫星组件：它内省 Click/Typer 命令的参数结构，构建一个 Textual 表单应用，用户填单后由进程 `execvp` 把组装好的命令原样交回 CLI 执行。本文展示两种接入方式：

- **Click 命令函数**：用 `@tui` 装饰器（F-TG-05）包裹命令函数，为命令组注入 `tui` 子命令。
- **Typer 应用**：调用 `typer.init_tui(app)`（F-TG-17）注入 `tui` 子命令。

借此说明「内省 → 表单 → execvp」三步流程（F-TG-03..04）。

## 可运行示例

### 方式一：Click 命令函数加 `@tui`

```python
import click
from trogon import tui  # F-TG-02: __init__ 导出 tui 与 Trogon


@click.group()
def greet():
    """示例命令组：生成 TUI 后填入参数即可运行。"""


@greet.command()
@click.option("--name", default="world", help="打招呼对象")
@click.option("-n", "--times", default=1, help="重复次数")
def hello(name, times):
    """说 hello。"""
    for _ in range(times):
        click.echo(f"Hello, {name}!")


# 关键：无论传入的是 Command 还是 Group，@tui 都会保证返回一个挂有
# "tui" 子命令的命令对象（F-TG-05）。
greet = tui(name="greet")(greet)

if __name__ == "__main__":
    greet()
```

保存为 `greet_demo.py` 运行 `python greet_demo.py tui` 即打开 Trogon 表单；填好参数后执行，Trogon 会把组装好的命令经 `os.execvp` 交回真实运行（F-TG-04）。

### 方式二：Typer 应用用 `init_tui`

```python
import typer

try:
    import typer
except ImportError:  # F-TG-17 依赖守卫
    raise ImportError(
        "The extra `trogon[typer]` is required to enable tui generation from Typer apps."
    )

from trogon.typer import init_tui  # F-TG-17

app = typer.Typer(help="Typer 示例：用 init_tui 注入 TUI。")


@app.command()
def main(name: str = typer.Option("world", help="打招呼对象"),
         times: int = typer.Option(1, help="重复次数")):
    """说 hello。"""
    for _ in range(times):
        typer.echo(f"Hello, {name}!")


if __name__ == "__main__":
    init_tui(app)  # 注册 "tui" 子命令并返回 app（F-TG-17）
    app()
```

保存为 `typer_demo.py` 运行 `python typer_demo.py tui`，同样进入 Trogon 表单，填单确认后由 Trogon 重新执行。

## 讲解

### 1. 接入层做了什么

- **`@tui` 装饰器**（F-TG-05）：返回一个 with `@click.pass_context` 的闭包 `wrapped_tui`，其函数体为 `Trogon(app, app_name=name, command_name=command, click_context=ctx).run()`。若被装饰的是 `click.Group`，直接给它追加 `tui` 子命令并返回原组；否则新建一个 `click.Group`，把命令函数挂进去，再注册 `tui` 子命令并返回这个新组。
- **`typer.init_tui`**（F-TG-17）：`wrapped_tui()` 内部以 `Trogon(typer.main.get_group(app), app_name=name, click_context=click.get_current_context()).run()` 构造 Trogon，并用 `app.command("tui", help="Open Textual TUI.")` 注册子命令后返回原 `app`。它需要安装 `trogon[typer]` 额外依赖。

### 2. 内省 → 表单 → execvp 三流程

- **内省**：`Trogon` 构造保存 `self.cli`，`is_grouped_cli = isinstance(cli, click.Group)`；`app_name` 缺省时经 `detect_run_string()` 探测运行串，否则回退为 `"cli"`（F-TG-03）。默认屏幕 `CommandBuilder` 会 `introspect_click_app(cli)` 递归扫描命令/选项/参数/子命令（F-TG-06、F-TG-12）。
- **表单**：`CommandForm` 由内省出的 `CommandSchema` 构建参数控件，用户每次改动都会 post `CommandForm.Changed`；`@on(CommandForm.Changed) update_command_to_run` 把 `event.command_data.to_cli_args(include_root_command=...)` 写入 `self.post_run_command`（F-TG-04）。
- **execvp**：用户确认后 `run()` 在 `try: super().run(...) finally:` 中，对非空 `post_run_command` 创建 `Console()`，若 `execute_on_exit` 则打印待执行命令，最后 `arguments = [*shlex.split(app_name), *post_run_command]` 并 `os.execvp(program_name, arguments)` 进程替换为原 CLI（F-TG-04）。

### 3. 使用提示

- 直接在 install 了 trogon 的环境运行 `python greet_demo.py tui` 即可在终端看到表单；`ctrl+r`（Close & Run）或绿色按钮触发关闭并执行。
- Trogon 本身就是 Textual App，因此运行环境需要支持 Textual 的终端驱动。

## 相关概念

- [23 · Trogon](/concepts/23-trogon.md)
- [00 · Textualize 生态总览](/concepts/00-ecosystem-overview.md)