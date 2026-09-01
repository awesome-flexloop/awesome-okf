---
okf_version: "0.2"
type: reference
title: CLI 入口点 (main.py)
sources:
  - conda/cli/main.py
---

# CLI 入口点 (main.py)

Conda CLI 采用**双入口模型**：`main()` 作为顶层分发函数，根据命令行首参数判断调用路径——以 `shell.` 开头的命令（如 `conda shell.bash activate`）走 `main_sourced()` 路径，其余子命令走 `main_subshell()` 路径。`main_subshell()` 负责参数预解析、插件加载、上下文初始化和子命令调度；`main_sourced()` 负责 shell 激活脚本的生成与输出。

```python
# conda/cli/main.py

def init_loggers():
    from ..base.context import context
    from ..gateways.logging import initialize_logging, set_log_level
    initialize_logging()
    set_log_level(context.log_level)


def main_subshell(*args, post_parse_hook=None, **kwargs):
    """Entrypoint for the "subshell" invocation of CLI interface. E.g. `conda create`."""
    from ..base.context import context
    from .conda_argparse import do_call, generate_parser, generate_pre_parser

    args = args or ["--help"]

    pre_parser = generate_pre_parser(add_help=False)
    args_subset = args[: args.index("--")] if "--" in args else args
    pre_args, _ = pre_parser.parse_known_args(args_subset)

    override_args = {
        "json": pre_args.json,
        "debug": pre_args.debug,
        "trace": pre_args.trace,
        "verbosity": pre_args.verbosity,
    }

    context.__init__(argparse_args=pre_args)
    if context.no_plugins:
        context.plugin_manager.disable_external_plugins()

    parser = generate_parser(add_help=True)
    args = parser.parse_args(args, override_args=override_args, namespace=pre_args)

    context.__init__(argparse_args=args)
    init_loggers()

    if post_parse_hook:
        post_parse_hook(args, parser)

    exit_code = do_call(args, parser)
    if isinstance(exit_code, int):
        return exit_code
    elif hasattr(exit_code, "rc"):
        return exit_code.rc


def main_sourced(shell, *args, **kwargs):
    """Entrypoint for the "sourced" invocation of CLI interface. E.g. `conda activate`."""
    shell = shell.replace("shell.", "", 1)

    from ..base.context import context
    from ..common.compat import on_win

    context.__init__()

    from ..activate import _build_activator_cls

    try:
        activator_cls = _build_activator_cls(shell)
    except KeyError:
        from ..exceptions import CondaError
        raise CondaError(f"{shell} is not a supported shell.")

    activator = activator_cls(args)
    result = activator.execute()

    if on_win and activator.needs_line_ending_fix:
        result = result.replace("\r", "")
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")

    print(result, end="")
    return 0


def main(*args, **kwargs):
    from ..common.compat import ensure_text_type
    from ..exception_handler import conda_exception_handler

    args = args or sys.argv[1:]
    args = tuple(ensure_text_type(s) for s in args)

    if args and args[0] in ("-V", "--version"):
        from .. import __version__
        print(f"conda {__version__}")
        return 0

    if args and args[0].strip().startswith("shell."):
        main = main_sourced
    else:
        main = main_subshell

    return conda_exception_handler(main, *args, **kwargs)
```

**关键设计**：
- **两阶段解析**：`main_subshell()` 先用 `generate_pre_parser()` 预解析提取全局标志（`--json`/`--debug`/`--trace`/`--verbosity`），再用完整 parser 解析全部参数，确保日志和插件系统在初始化时就能感知这些标志
- **插件可禁用**：`--no-plugins` 标志在预解析阶段即可生效，调用 `disable_external_plugins()` 阻止外部插件加载
- **shell 激活分离**：`main_sourced()` 绕过完整参数解析器，直接通过 `_build_activator_cls()` 构建对应 shell 的激活器并输出脚本内容，因为 `conda activate` 需要输出 shell 代码被 `eval` 执行而非普通子进程
- **异常统一处理**：所有路径最终通过 `conda_exception_handler()` 包装，提供统一的错误报告和退出码处理
