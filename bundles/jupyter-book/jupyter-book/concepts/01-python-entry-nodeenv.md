---
type: concept
title: "Python 入口与 nodeenv 管理"
description: "Jupyter Book v2 Python 层的 main() 函数执行流程、Node.js 环境查找策略和 nodeenv 自动安装机制"
tags: [jupyter-book, python, nodeenv, entrypoint, subprocess]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "py/jupyter_book/__main__.py"
    facts: [F-001, F-002, F-003, F-004]
  - path: "py/jupyter_book/nodeenv.py"
    facts: [F-005, F-006, F-007, F-008, F-009, F-010]
---

# Python 入口与 nodeenv 管理

Jupyter Book v2 的 Python 层非常精简，核心是 `__main__.py` 中的 `main()` 函数和 `nodeenv.py` 中的 Node.js 环境管理。理解这两个文件就理解了 Python 层的全部职责。

## __main__.py 入口

### 版本常量

```python
__version__ = "2.1.6"
NODEENV_VERSION = "22.17.0"
```

- `__version__`：Jupyter Book 版本号
- `NODEENV_VERSION`：自动安装时使用的 Node.js 版本（LTS 版本）

### main() 函数执行流程

```
main()
  │
  ├── 1. binary_path = find_executable_path()
  │      确定 nodeenv 创建的 node 可执行文件名
  │
  ├── 2. node_path, os_path = find_valid_node(
  │      binary_path=binary_path,
  │      test_version=test_node_version,
  │      nodeenv_version=NODEENV_VERSION
  │    )
  │      两阶段查找：系统 Node → nodeenv Node
  │
  ├── 3. js_path = pathlib.Path(__file__).parent / "dist" / "jupyter-book.cjs"
  │      定位编译好的 TS bundle
  │
  ├── 4. jb_node_args = [str(js_path), *sys.argv[1:]]
  │      构建命令行参数（JS 文件路径 + 用户参数）
  │
  ├── 5. node_env = {**os.environ, "PATH": os_path, "MYST_LANG": "PYTHON"}
  │      构建环境变量（合并当前环境 + 更新 PATH + 标记 Python 调用）
  │
  └── 6. 平台分发启动 Node.js
         ├── Windows: subprocess.run([node_path, *jb_node_args], env=jb_env)
         └── Unix:    os.execve(node_path, [node_path.name, *jb_node_args], jb_env)
```

### 平台差异：subprocess vs execve

- **Windows** 使用 `subprocess.run()`：
  - Windows 上 `os.execve` 行为不稳定
  - `subprocess.run` 等待子进程完成，传递退出码
  - 是"父进程+子进程"模型

- **Unix/macOS/Linux** 使用 `os.execve()`：
  - `execve` 替换当前进程（不创建新进程），更高效
  - PID 不变，信号直接传递给 Node.js 进程
  - 没有额外的 Python 进程残留

### test_node_version：版本检查

```python
def test_node_version(raw_version: str) -> tuple[int, int, int] | None:
```

- 执行 `node -v`，输出如 `v22.17.0`
- 使用正则表达式提取 major.minor.patch
- 版本要求：**18.x、20.x、或 22.x+**（Node.js 的 LTS 版本线）
- 不符合要求返回 None，触发 nodeenv 安装流程

### 错误处理

Python 层捕获两种异常：

1. **NodeEnvCreationError**：nodeenv 安装失败
   - 提示用户手动安装 Node.js
   - 给出 nodejs.org 下载链接

2. **PermissionDeniedError**：权限不足无法创建 nodeenv 目录
   - 提示目录路径
   - 建议检查权限或手动安装 Node.js

两种异常都以友好消息退出（`sys.exit(1)`），不显示 Python 栈跟踪。

## nodeenv.py：Node.js 环境管理

nodeenv.py 实现了"查找或安装 Node.js"的两阶段策略。

### 查找策略：find_valid_node

```python
def find_valid_node(
    binary_path: str,
    nodeenv_version: str,
    test_version: Callable[[str], tuple | None]
) -> tuple[Path, str]:
```

执行步骤：

```
1. 查找系统 Node
   node_path = find_installed_node()  # shutil.which("node")
   if node_path 存在:
       version = get_triple_node_version(node_path)  # node -v
       if test_version(version) 符合要求:
           return (node_path, os.environ["PATH"])

2. 检查 nodeenv
   env_path = find_nodeenv_path(NODEENV_VERSION)  # platformdirs 用户数据目录
   if env_path 存在:
       node_path = env_path / binary_path  # Scripts/node.exe 或 bin/node
       if node_path 存在:
           构建新 PATH（nodeenv 路径 + 原 PATH）
           return (node_path, new_path)

3. 安装 nodeenv（如需要）
   if ask_to_install_node(env_path):
       create_nodeenv(env_path, NODEENV_VERSION)
       return (env_path / binary_path, new_path)

4. 失败退出
   raise NodeEnvCreationError("未找到可用的 Node.js")
```

### 关键函数详解

#### find_installed_node

```python
def find_installed_node() -> Path | None:
```

使用 `shutil.which("node")` 在系统 PATH 中查找 node 可执行文件。返回 Path 对象或 None。

#### get_triple_node_version

```python
def get_triple_node_version(node_path: Path) -> str:
```

执行 `node_path -v`，捕获 stdout，返回版本字符串（如 `"v22.17.0"`）。

#### find_nodeenv_path

```python
def find_nodeenv_path(version: str) -> Path:
```

使用 `platformdirs.user_data_dir("jupyter-book", "jupyter-book")` 获取用户数据目录，然后拼接 `nodeenv-{version}`。

典型路径：
- **Windows**: `C:\Users\<user>\AppData\Local\jupyter-book\jupyter-book\nodeenv-22.17.0`
- **macOS**: `~/Library/Application Support/jupyter-book/nodeenv-22.17.0`
- **Linux**: `~/.local/share/jupyter-book/nodeenv-22.17.0`

#### ask_to_install_node

```python
def ask_to_install_node(path: Path) -> bool:
```

交互式询问用户是否安装 Node.js：

1. 打印提示消息，说明将在 `path` 创建 nodeenv 环境
2. 检查 `JB_ALLOW_NODEENV` 环境变量（CI 环境设为 `"1"` 或 `"true"` 自动同意）
3. 等待用户输入 y/n
4. 输入 y 返回 True，输入 n 返回 False

#### create_nodeenv

```python
def create_nodeenv(env_path: Path, version: str) -> None:
```

执行实际安装：

1. 确保 nodeenv Python 包可用（`pip install nodeenv`）
2. 执行命令：
   ```bash
   python -m nodeenv --node=22.17.0 --prebuilt --clean-src <env_path>
   ```
   - `--node=<version>`：指定 Node.js 版本
   - `--prebuilt`：下载预编译二进制（比编译源码快得多）
   - `--clean-src`：安装后清理源码

3. nodeenv 会下载 Node.js 预编译包，解压到 `env_path` 目录

#### nodeenv 可执行路径

创建后的 node 可执行文件位置：

| 平台 | 路径 |
|------|------|
| Windows | `<env_path>\Scripts\node.exe` |
| macOS/Linux | `<env_path>/bin/node` |

`binary_path` 在 `__main__.py` 中根据平台确定：
```python
if platform.system() == "Windows":
    binary_path = Path("Scripts/node.exe")
else:
    binary_path = Path("bin/node")
```

### PATH 环境变量构建

当使用 nodeenv 安装的 Node.js 时，需要将 nodeenv 路径添加到 PATH 最前面：

```python
# Windows
new_path = f"{env_path / 'Scripts'}{os.pathsep}{os.environ['PATH']}"
# Unix
new_path = f"{env_path / 'bin'}{os.pathsep}{os.environ['PATH']}"
```

这确保：
- nodeenv 中的 node/npm 优先被找到
- nodeenv 中的全局安装包可用
- 系统 PATH 作为 fallback

### 异常类

| 异常 | 触发条件 |
|------|---------|
| `PermissionDeniedError` | 无法写入 nodeenv 目录（权限不足） |
| `NodeEnvCreationError` | nodeenv 创建失败（下载失败、磁盘空间不足等） |
| `NodeVersionError` | Node.js 版本不符合要求 |

## 首次运行体验

用户首次运行 `jupyter-book build mybook/` 时：

1. Python 启动，检查系统 Node.js
2. 系统没有 Node.js 或版本不满足要求
3. 提示："Would you like to download and install Node.js v22.17.0?"
4. 用户输入 y
5. 自动下载安装 Node.js 到用户数据目录
6. 启动 Node.js 运行 TS bundle
7. 执行 build 命令

后续运行直接使用 nodeenv 中的 Node.js，不再询问。

## 手动跳过 nodeenv

如果用户已有可用的 Node.js（但不在 PATH 中，或版本满足要求但 shutil.which 没找到），可以：

1. 将 Node.js 添加到 PATH
2. 设置 `JB_ALLOW_NODEENV=0` 禁止自动安装
3. 直接使用 `npx mystmd` 绕过 Python 层

## 相关概念

- [00-v2-architecture](/concepts/00-v2-architecture.md)：v2 双层架构
- [02-ts-cli-commands](/concepts/02-ts-cli-commands.md)：TS CLI 命令
- [01-create-book](/examples/01-create-book.md)：创建 Jupyter Book 示例
