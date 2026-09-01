---
okf_version: "0.2"
type: "concept"
title: "Shell激活机制"
sources:
  - "conda/activate.py"
  - "conda/cli/main.py"
---

# Shell激活机制

conda 的环境激活（activate/deactivate）是 CLI 中最特殊的操作——它不直接修改当前进程的环境变量，而是通过**输出 shell 脚本**由调用方 shell eval 执行。这种"生成代码→shell执行"的模型是理解 conda 激活机制的核心。

## 为什么需要 shell hook？

conda 作为子进程运行时无法修改父 shell 的环境变量。因此 `conda activate` 的实际执行流程是：

1. shell 函数（由 `conda init` 安装的 hook）拦截 `conda activate` 命令
2. shell 函数调用 `conda shell.posix activate <env>` 子进程
3. 子进程生成 shell 脚本（如 `export PATH=...`）输出到 stdout
4. shell 函数对输出做 `eval`，在当前 shell 中执行环境修改

这就是为什么必须运行 `conda init` 才能使用 `conda activate`——没有 shell hook，环境变量修改无法生效。

## main_sourced 入口

当 `main()` 检测到参数以 `"shell."` 开头时（如 `shell.posix`、`shell.bash`、`shell.cmd.exe`），路由到 `main_sourced(shell, *args)` [F-018]：

```python
def main_sourced(shell, *args, **kwargs):
    shell = shell.replace("shell.", "", 1)
    context.__init__()
    activator_cls = _build_activator_cls(shell)
    activator = activator_cls(args)
    result = activator.execute()
    # Windows行尾修复
    if on_win and activator.needs_line_ending_fix:
        result = result.replace("\r", "")
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    print(result, end="")
    return 0
```

关键设计：Windows 下对需要行尾修复的 shell（如 PosixActivator），将 stdout 重配置为 UTF-8 编码并使用 `\n` 换行符，避免 CRLF 导致 shell 脚本语法错误 `cli/main.py#L82-L87`。

## _Activator 抽象基类

`_Activator` 是所有 shell 激活器的抽象基类（metaclass=ABCMeta），定义了激活/反激活的三大职责 [F-079]：

1. **设置/取消环境变量**：`CONDA_PREFIX`、`CONDA_SHLVL`、`CONDA_DEFAULT_ENV`、`CONDA_PROMPT_MODIFIER` 以及包定义的环境变量
2. **执行 activate.d/deactivate.d 脚本**：遍历环境目录下 `etc/conda/activate.d/` 和 `deactivate.d/` 中的脚本
3. **更新 PATH 和命令提示符**：将环境的 `bin/`（Windows 下多个目录）加入 PATH，修改 PS1/prompt 显示当前环境名

所有核心逻辑在 `build_activate()` 和 `build_deactivate()` 中实现，与 shell 类型无关。子类只需定义模板字符串（`export_var_tmpl`、`unset_var_tmpl` 等）和路径转换函数，即可支持新 shell。

### Shell 特定模板

每个子类定义 shell 语法模板：

| 属性 | PosixActivator (bash/zsh) | CmdExeActivator (cmd.exe) | PowerShellActivator | FishActivator |
|---|---|---|---|---|
| `pathsep_join` | `":".join` | `";".join` | `";".join`/`":".join` | `'" "'.join` |
| `export_var_tmpl` | `"export %s='%s'"` | `"%s=%s"` | `'$Env:%s = "%s"'` | `'set -gx %s "%s"'` |
| `unset_var_tmpl` | `"export %s=''"` | `"%s="` | `"$Env:%s = $null"` | `"set -e %s \|\| true"` |
| `script_extension` | `.sh` | `.bat` | `.ps1` | `.fish` |
| `run_script_tmpl` | `'. "%s"'` | `"_CONDA_SCRIPT=%s"` | `'. "%s"'` | `'source "%s"'` |
| `tempfile_extension` | None（stdout） | `.env`（临时文件） | None（stdout） | None（stdout） |

cmd.exe 使用临时文件（`.env` INI 格式）而非 stdout 输出，因为 cmd.exe 无法方便地 eval 多行脚本。

### 支持的 Shell

`activator_map` 注册了7种激活器类 `activate.py#L1156-L1168`：

- **PosixActivator**：posix/bash/zsh/dash/ash（共享bash语法）
- **CshActivator**：csh/tcsh
- **XonshActivator**：xonsh
- **CmdExeActivator**：Windows cmd.exe
- **FishActivator**：fish shell
- **PowerShellActivator**：PowerShell

此外还有 `JSONFormatMixin`，可通过 `+json` 后缀组合（如 `conda shell.posix+json activate`），将激活信息以 JSON 格式返回，供 IDE 和工具集成使用。

## _build_activator_cls：动态类构造

`_build_activator_cls(shell)` 支持 `+` 分隔的混合格式 `activate.py#L1175-L1190`：

```python
def _build_activator_cls(shell):
    shell_etc = shell.split("+")
    activator, formatters = shell_etc[0], shell_etc[1:]
    bases = [activator_map[activator]]
    for f in formatters:
        bases.append(formatter_map[f])
    cls = type("Activator", tuple(reversed(bases)), {})
    return cls
```

例如 `shell.posix+json` 动态生成继承自 `JSONFormatMixin` 和 `PosixActivator` 的类，MRO 中 mixin 在前以覆盖方法。

## activate 工作原理

`activate()` 方法根据 `self.stack` 标志选择 `build_stack()` 或 `build_activate()`，核心逻辑在 `_build_activate_stack()` 中 `activate.py#L360-L451`：

1. **解析前缀**：`_resolve_prefix()` 将环境名或路径转换为绝对路径
2. **栈管理**：通过 `CONDA_SHLVL` 跟踪激活层级，`CONDA_PREFIX_<n>` 保存历史前缀
3. **非首次激活（shlvl > 0 且非 stack）**：先执行旧环境的 deactivate.d 脚本，再替换 PATH 中的旧前缀目录为新前缀目录
4. **stack 模式**：不执行 deactivate.d 脚本，将新前缀的 PATH 目录添加到前面，保留旧环境变量
5. **环境变量管理**：读取 `conda-meta/state`（环境规范变量）和 `etc/conda/activate.d/env_vars.d/`（包变量），被覆盖的旧值保存在 `__CONDA_SHLVL_<n>_<VARNAME>` 中
6. **脚本收集**：按字母序排列 activate.d 脚本

PATH 处理在 Windows 上特别复杂——需要添加前缀目录、`Library/bin`、`Library/usr/bin`、`Scripts`、`Library/<variant>/bin`（ucrt64/clang64/mingw64 等 MSYS2 变体）等多个路径 `activate.py#L619-L658`。

## deactivate 工作原理

`build_deactivate()` `activate.py#L453-L555`：

1. 若 `CONDA_SHLVL == 1`：从 PATH 移除前缀目录，unset `CONDA_PREFIX`/`CONDA_DEFAULT_ENV`/`CONDA_PROMPT_MODIFIER`，执行 deactivate.d 脚本
2. 若 `CONDA_SHLVL > 1`：恢复上一级 `CONDA_PREFIX_<n>` 的环境，执行当前环境 deactivate.d 和上一级 activate.d 脚本
3. stack 环境 deactivate 时只移除 PATH 中的前缀目录，不执行 deactivate.d 脚本
4. 恢复之前被覆盖的环境变量（从 `__CONDA_SHLVL_<n>_<VARNAME>` 取回）

## BUILTIN_COMMANDS（shell层）

`activate.py` 定义了自己的 `BUILTIN_COMMANDS` 字典 [F-080]，包含5个 shell 层命令：

```python
BUILTIN_COMMANDS = {
    "activate": ActivateHelp(),
    "deactivate": DeactivateHelp(),
    "hook": GenericHelp("hook"),
    "commands": GenericHelp("commands"),
    "reactivate": GenericHelp("reactivate"),
}
```

这与 CLI 层的 `BUILTIN_COMMANDS`（24个命令）不同——CLI 层的 activate/deactivate 是 mock 入口（提示用户需要 shell init），真正的激活逻辑在 shell 层的 BUILTIN_COMMANDS 中。

- **hook**：输出 shell 初始化脚本（由 `conda init` 写入 rc 文件），包含 `conda()` shell 函数定义和元变量设置
- **commands**：列出可用的 shell 命令
- **reactivate**：重新激活当前环境（在 install/update/remove 后使用，刷新 PATH 和脚本）

## conda init 与 shell rc 文件

`conda init` 命令（属于 CLI 层内置命令）调用激活器的 `hook()` 方法生成 shell 初始化代码，写入用户的 shell rc 文件（如 `.bashrc`、`.zshrc`、`config.fish`、PowerShell `profile.ps1`）。`hook()` 方法的输出包含：

1. **_hook_preamble**：设置 `CONDA_EXE`、`_CE_M`、`_CE_CONDA` 等元变量
2. **hook_source_path**：内联或 source 对应的 shell 脚本（`conda.sh`、`conda.csh`、`conda.fish`、`conda-hook.ps1` 等）
3. **auto_activate**：若配置了 `auto_activate_base`，自动执行 `conda activate base`
4. **_hook_postamble**：清理临时变量（如 PowerShell 的 `$CondaModuleArgs`）

## Windows 特殊处理

Windows 平台有多处特殊处理：
- cmd.exe 使用临时 `.env` 文件而非 stdout 输出（因为 cmd.exe 没有方便的 eval 机制）
- PowerShell 和 cmd.exe 的路径分隔符为反斜杠
- MSYS2/Cygwin 路径前缀检测（`/c/`、`/cygdrive/c/`）需要特殊路径转换
- Unix shell 在 Windows 上运行时（如 Git Bash）需要行尾修复和 UTF-8 重配置
- 路径中包含 `^` 字符时 cmd.exe 会报错（`_resolve_prefix` 中检测）
