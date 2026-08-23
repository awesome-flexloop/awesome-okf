---
type: "concept"
title: "Shell 激活与环境执行"
sources:
  - id: rattler-shell
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_shell"
---

# Shell 激活与环境执行

`rattler_shell` crate 负责 conda 环境的激活脚本生成和在环境中执行命令。conda 环境"激活"的本质是修改当前 shell 的环境变量（PATH、CONDA_PREFIX、CONDA_DEFAULT_ENV 等），使得 shell 在查找可执行文件、Python 模块等资源时优先使用环境中的版本。

## 为什么需要 Shell 激活

一个 conda 环境前缀目录（如 `~/miniconda3/envs/myenv/`）包含：
- `bin/`（Unix）或 `Scripts/`（Windows）：可执行文件
- `lib/`：库文件
- `lib/pythonX.Y/site-packages/`：Python 包
- `conda-meta/`：已安装包的元数据

要让 shell 使用这些文件，需要：
1. 将 `<prefix>/bin` 添加到 PATH 最前面
2. 设置 `CONDA_PREFIX` 环境变量指向前缀
3. 设置 `CONDA_DEFAULT_ENV` 为环境名
4. 可能需要设置 `CONDA_SHLVL`（嵌套激活层级）
5. 处理 PS1（提示符）修改
6. 运行包的激活/停用脚本（`etc/conda/activate.d/`、`etc/conda/deactivate.d/`）

## Shell 抽象

`rattler_shell::shell` 模块为不同 shell 提供统一抽象：

| Shell 类型 | 模块 | 平台 |
|-----------|------|------|
| Bash | `Bash` | Linux/macOS/WSL |
| Zsh | `Zsh` | macOS/Linux（默认 shell） |
| Fish | `Fish` | 跨平台 |
| Xonsh | `Xonsh` | 跨平台 |
| CmdExe | `CmdExe` | Windows |
| PowerShell | `PowerShell` | Windows/macOS/Linux（Core） |

所有 shell 类型实现 `Shell` trait：

```rust
pub trait Shell {
    /// 设置环境变量的 shell 命令
    fn set_env_var(&self, f: &mut dyn Write, env_var: &str, value: &str) -> io::Result<()>;

    /// 取消设置环境变量
    fn unset_env_var(&self, f: &mut dyn Write, env_var: &str) -> io::Result<()>;

    /// 将路径添加到 PATH 前面
    fn prepend_path(&self, f: &mut dyn Write, path: &Path) -> io::Result<()>;

    /// 运行脚本文件
    fn run_script(&self, f: &mut dyn Write, path: &Path) -> io::Result<()>;

    /// 设置提示符
    fn set_prompt(&self, f: &mut dyn Write, prompt: &str) -> io::Result<()>;

    /// 获取 shell 的扩展名（如 ".sh"、".bat"、".ps1"）
    fn extension(&self) -> &str;
}
```

## 激活脚本生成

`activation` 模块负责生成激活脚本：

```rust
use rattler_shell::{
    activation::{ActivationVariables, Activator, PathModificationBehavior},
    shell::{Bash, PowerShell, ShellEnum},
};
use rattler_conda_types::Platform;
use std::path::Path;

// 创建激活器（以 bash 为例）
let activator = Activator::from_path(
    Path::new("/home/user/myenv"),   // 环境前缀路径
    Bash::default(),                  // shell 类型
    Platform::current(),
)?;

// 生成激活脚本
let activation_script = activator.activation(
    ActivationVariables {
        conda_prefix: None,          // 当前 CONDA_PREFIX（嵌套激活）
        path: None,                  // 当前 PATH（从系统获取）
        path_modification_behavior: PathModificationBehavior::Prepend,  // 前置 PATH
    },
    &Default::default(),
)?;

// activation_script.script: 要 source/执行的脚本内容
// activation_script.env_vars: 设置的环境变量映射
println!("{}", activation_script.script);
```

### 生成的脚本示例（Bash）

```bash
# 取消旧的 PYTHONHOME（如果有）
unset PYTHONHOME

# 记录旧的 PATH（用于 deactivate 时恢复）
export CONDA_PREFIX_1=/home/user/myenv
export PATH=/home/user/myenv/bin:$PATH

# 设置 CONDA 变量
export CONDA_PREFIX=/home/user/myenv
export CONDA_DEFAULT_ENV=myenv
export CONDA_SHLVL=1

# 运行包的激活脚本
if [ -f "/home/user/myenv/etc/conda/activate.d/xxx.sh" ]; then
    . "/home/user/myenv/etc/conda/activate.d/xxx.sh"
fi

# 修改提示符
export PS1="(myenv) $PS1"
```

### 生成的脚本示例（PowerShell）

```powershell
$env:CONDA_PREFIX_1 = $env:CONDA_PREFIX
$env:PATH = "C:\Users\user\myenv;C:\Users\user\myenv\Scripts;C:\Users\user\myenv\Library\bin;" + $env:PATH
$env:CONDA_PREFIX = "C:\Users\user\myenv"
$env:CONDA_DEFAULT_ENV = "myenv"
$env:CONDA_SHLVL = 1
```

## 停用脚本

停用脚本的生成逻辑类似，恢复之前的环境变量：

```rust
let deactivation_script = activator.deactivation(
    ActivationVariables {
        conda_prefix: Some("/home/user/myenv".into()),
        path: Some(current_path),
        path_modification_behavior: PathModificationBehavior::Prepend,
    },
)?;
```

## 在环境中执行命令

`run` 模块提供在激活环境中执行命令的能力：

### run_in_environment

在指定环境前缀中执行命令（自动处理激活）：

```rust
use rattler_shell::run::run_in_environment;
use std::path::Path;
use std::process::Stdio;

let status = run_in_environment(
    Path::new("/home/user/myenv"),     // 环境前缀
    "python",                          // 命令
    &["--version"],                    // 参数
    Path::new("/workspace"),           // 工作目录
    Stdio::inherit(),                  // stdout
    Stdio::inherit(),                  // stderr
    Stdio::inherit(),                  // stdin
    None,                              // 额外环境变量
).await?;

if !status.success() {
    eprintln!("命令执行失败");
}
```

`run_in_environment` 内部会：
1. 检测当前 shell 类型
2. 生成激活脚本
3. 构造复合命令（激活 + 执行用户命令）
4. 以子进程执行
5. 等待完成并返回退出状态

### run_command_in_environment

返回 `std::process::Command`（或 `tokio::process::Command`），允许进一步自定义：

```rust
use rattler_shell::run::run_command_in_environment;

let mut cmd = run_command_in_environment(
    Path::new("/home/user/myenv"),
    "python",
)?;
cmd.current_dir("/workspace");
cmd.env("MY_VAR", "value");
cmd.arg("-c").arg("print('hello')");
let output = cmd.output()?;
```

## 环境变量映射

`ActivationResult` 包含所有被修改的环境变量，这对于不使用 shell 脚本的场景（如直接启动进程）很有用：

```rust
let result = activator.activation(vars, &Default::default())?;

// result.env_vars 是 HashMap<String, String>
// 包含所有应设置的环境变量（PATH, CONDA_PREFIX 等）
for (key, value) in &result.env_vars {
    println!("{}={}", key, value);
}
```

可以直接使用这些环境变量启动子进程，不必通过 shell：

```rust
let mut cmd = std::process::Command::new("/home/user/myenv/bin/python");
cmd.envs(&activation_result.env_vars);
cmd.arg("script.py");
cmd.status()?;
```

## 嵌套激活

当用户在已激活的环境中再次激活另一个环境时（`conda activate env2`），rattler_shell 支持嵌套激活：

1. 保存当前 `CONDA_PREFIX` 到 `CONDA_PREFIX_N`（N 是当前 SHLVL）
2. 更新 `CONDA_PREFIX`、`CONDA_DEFAULT_ENV`、`CONDA_SHLVL`
3. 修改 PATH（新环境的 bin 目录前置）
4. 保存旧的 PATH 和 PS1 以便恢复

停用后逐层恢复。

## PathModificationBehavior

控制 PATH 修改方式：

```rust
pub enum PathModificationBehavior {
    Prepend,    // 将环境 bin 目录前置到 PATH（默认，conda 的标准行为）
    Append,     // 追加到 PATH（不推荐，会导致系统命令优先）
    Replace,    // 完全替换 PATH（极端隔离）
}
```

## CLI 中的 shell-hook

rattler-bin CLI 提供 `shell-hook` 子命令，输出当前 shell 的激活脚本：

```bash
# Bash/Zsh
eval "$(rattler shell-hook -p .prefix/)"

# Fish
rattler shell-hook -p .prefix/ | source

# PowerShell
Invoke-Expression (rattler shell-hook -p .prefix/ --shell powershell)
```

## Python 绑定

py-rattler 提供了 `Activator` 类：

```python
from rattler import ActivationVariables, Activator
from pathlib import Path

activator = Activator(
    prefix_path=Path("/home/user/myenv"),
    shell_type="bash",
)
result = activator.activation(ActivationVariables.default())
print(result.script)
```

## 相关概念

- [安装事务](09-install-and-transaction.md)
- [5分钟快速上手](01-getting-started.md)
