---
okf_version: "0.2"
type: concept
title: "配置迁移与环境诊断"
description: "了解 jupyter_core 的 IPython 配置迁移工具（migrate.py）和环境诊断工具（troubleshoot.py）的功能、实现与使用。"
tags: [jupyter, core, migration, troubleshoot, ipython, diagnostic]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: migrate-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/migrate.py"
    title: "jupyter_core/migrate.py"
  - id: troubleshoot-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/troubleshoot.py"
    title: "jupyter_core/troubleshoot.py"
---

# 配置迁移与环境诊断

jupyter_core 包含两个实用的 CLI 工具：配置迁移工具（`migrate.py`）和环境诊断工具（`troubleshoot.py`）。前者帮助用户从旧版 IPython 平滑过渡到 Jupyter，后者在遇到安装或运行问题时快速收集环境信息。

## 配置迁移（migrate.py）

`jupyter-migrate` 命令负责将 IPython 3.x（及更早版本）的配置和数据文件迁移到 Jupyter 4.x 的目录结构。

### 迁移原则

- **复制而非移动**：所有文件使用 `shutil.copy`/`shutil.copytree` 复制到新位置，原始文件保留不动，确保安全可回滚。
- **幂等性**：如果目标位置已存在文件，则跳过不覆盖。迁移完成后写入标记文件，避免重复执行。
- **空目录/空文件跳过**：源目录为空或配置文件无有效配置时不迁移。

### 迁移映射表

迁移操作在 `migrations` 字典中定义，使用模板路径（`{ipython_dir}`、`{jupyter_data}` 等）：

| 源位置（IPython 3.x） | 目标位置（Jupyter 4.x） | 类型 |
|----------------------|------------------------|------|
| `{ipython_dir}/nbextensions` | `{jupyter_data}/nbextensions` | 目录 |
| `{ipython_dir}/kernels` | `{jupyter_data}/kernels` | 目录 |
| `{profile}/nbconfig` | `{jupyter_config}/nbconfig` | 目录 |
| `{profile}/static/custom/custom.js` | `{jupyter_config}/custom/custom.js` | 文件（非空才迁移） |
| `{profile}/static/custom/custom.css` | `{jupyter_config}/custom/custom.css` | 文件（非空才迁移） |
| `{profile}/security/notebook_secret` | `{jupyter_data}/notebook_secret` | 文件 |
| `{profile}/security/notebook_cookie_secret` | `{jupyter_data}/notebook_cookie_secret` | 文件 |
| `{profile}/security/nbsignatures.db` | `{jupyter_data}/nbsignatures.db` | 文件 |
| `{profile}/ipython_notebook_config.py/.json` | `{jupyter_config}/jupyter_notebook_config.py/.json` | 配置文件（含类名替换） |
| `{profile}/ipython_nbconvert_config.py/.json` | `{jupyter_config}/jupyter_nbconvert_config.py/.json` | 配置文件（含类名替换） |
| `{profile}/ipython_qtconsole_config.py/.json` | `{jupyter_config}/jupyter_qtconsole_config.py/.json` | 配置文件（含类名替换） |

其中：
- `{ipython_dir}` = `get_ipython_dir()`，默认为 `~/.ipython`（可通过 `IPYTHONDIR` 环境变量覆盖）
- `{profile}` = `{ipython_dir}/profile_default`
- `{jupyter_data}` = `jupyter_data_dir()`
- `{jupyter_config}` = `jupyter_config_dir()`

### config_substitutions 类名替换

迁移配置文件时，会自动执行以下正则替换，更新已更名的类名和模块引用：

| 正则模式 | 替换为 | 说明 |
|---------|--------|------|
| `\bIPythonQtConsoleApp\b` | `JupyterQtConsoleApp` | QtConsole 应用类更名 |
| `\bIPythonWidget\b` | `JupyterWidget` | Widget 基类更名 |
| `\bRichIPythonWidget\b` | `RichJupyterWidget` | Rich Widget 更名 |
| `\bIPython\.html\b` | `notebook` | 模块路径变更 |
| `\bIPython\.nbconvert\b` | `nbconvert` | 模块路径变更 |

### 核心函数

| 函数 | 签名 | 说明 |
|------|------|------|
| `get_ipython_dir()` | `() -> str` | 获取 IPython 目录路径。优先读取 `IPYTHONDIR` 环境变量，默认为 `~/.ipython`。不从 IPython 导入以避免触发目录创建。 |
| `migrate_dir(src, dst)` | `(str, str) -> bool` | 迁移目录。源目录为空跳过；目标已存在且非空跳过；否则 `copytree` 复制。返回是否执行了迁移。 |
| `migrate_file(src, dst, substitutions=None)` | `(str, str, dict?) -> bool` | 迁移单个文件。目标存在则跳过；复制后如提供 substitutions 正则字典，则执行文本替换。 |
| `migrate_one(src, dst)` | `(str, str) -> bool` | 自动判断 src 是文件还是目录，分发到 `migrate_file` 或 `migrate_dir`。 |
| `migrate_static_custom(src, dst)` | `(str, str) -> bool` | 迁移 custom.js/css。检查文件是否为非空（非纯注释），空文件跳过。 |
| `migrate_config(name, env)` | `(str, dict) -> list` | 迁移指定名称的配置文件（同时尝试 `.py` 和 `.json` 扩展名），空配置不迁移，执行 `config_substitutions` 替换。返回已迁移文件列表。 |
| `migrate()` | `() -> bool` | 主迁移函数。构建路径映射字典，依次迁移目录、配置文件、custom 文件，最后写入 `migrated` 标记文件。 |

### 迁移标记文件

迁移成功后，在 `jupyter_config_dir()` 下创建一个名为 `migrated` 的文件，内容为迁移时间的 ISO 格式 UTC 时间戳：

```python
with open(Path(env["jupyter_config"], "migrated"), "w") as f:
    f.write(datetime.now(tz=timezone.utc).isoformat())
```

`JupyterApp.migrate_config()` 在初始化时检查此文件是否存在且可写，如果存在则跳过迁移。

### JupyterMigrate 应用类

`JupyterMigrate` 继承自 `JupyterApp`，是 `jupyter-migrate` CLI 命令的实现：

```python
class JupyterMigrate(JupyterApp):
    name = "jupyter-migrate"
    description = """Migrate configuration and data from .ipython prior to 4.0..."""
    
    def start(self):
        if not migrate():
            self.log.info("Found nothing to migrate.")
```

入口点为 `main = JupyterMigrate.launch_instance`。

### 使用方式

```bash
# 命令行执行
jupyter-migrate

# Python 中执行
from jupyter_core.migrate import migrate
migrate()
```

## 环境诊断（troubleshoot.py）

`jupyter-troubleshoot` 是一个极简设计的诊断工具，**仅依赖 Python 标准库**（不依赖 traitlets、platformdirs 等），确保即使在 jupyter_core 安装不完整的情况下也能运行。整个模块只有 3 个函数，约 111 行代码。

### 设计理念

- **外部命令优先**：通过调用外部命令（`pip list`、`conda list`、`which` 等）收集信息，而非 Python API，因为环境问题往往涉及 Python 之外的 PATH、多环境等问题。
- **容错优先**：外部命令执行失败时返回 `None` 而非抛出异常，保证即使某个命令不可用，其他信息仍能正常输出。
- **argcomplete 早退**：如果检测到 `_ARGCOMPLETE` 环境变量（Tab 补全时），立即返回不执行任何操作，避免补全卡顿。

### subs 函数

```python
def subs(cmd: Union[list[str], str]) -> str | None:
```

执行外部命令并返回 stdout 输出：

1. 使用 `subprocess.check_output(cmd)` 执行命令
2. 成功时：以 UTF-8 解码（错误用 `replace` 模式），去除首尾空白后返回
3. 失败时（`OSError` 或 `CalledProcessError`）：返回 `None`

这是一个安全的命令执行包装器，永远不会抛出异常。

### get_data 函数

```python
def get_data() -> dict[str, Any]:
```

返回包含环境信息的字典，字段如下：

| 字段 | 类型 | 说明 |
|------|------|------|
| `path` | `str` | 系统 `PATH` 环境变量（`os.environ["PATH"]`） |
| `sys_path` | `list[str]` | Python 模块搜索路径（`sys.path`） |
| `sys_exe` | `str` | Python 可执行文件路径（`sys.executable`） |
| `sys_version` | `str` | Python 版本字符串（`sys.version`） |
| `platform` | `str` | 平台信息（`platform.platform()`） |
| `which` | `str \| None` | Unix 下 `which -a jupyter` 的输出；Windows 下为 `None` |
| `where` | `str \| None` | Windows 下 `where jupyter` 的输出；Unix 下为 `None` |
| `pip` | `str \| None` | `pip list` 的输出（使用当前 Python：`{sys.executable} -m pip list`） |
| `conda` | `str \| None` | `conda list` 的输出（如果 conda 可用） |
| `conda-env` | `str \| None` | `conda env export` 的输出（如果 conda 可用） |

### main 函数

`main()` 函数按固定顺序输出诊断信息到 stdout：

1. **argcomplete 早退检查**：如果 `_ARGCOMPLETE` 在环境变量中，直接返回
2. **$PATH**：逐行打印 PATH 中的每个目录
3. **sys.path**：逐行打印 Python 模块搜索路径
4. **sys.executable**：打印 Python 可执行文件路径
5. **sys.version**：打印 Python 版本（多行版本逐行缩进）
6. **platform.platform()**：打印平台信息
7. **which -a jupyter**（Unix）或 **where jupyter**（Windows）：打印 jupyter 命令位置
8. **pip list**：打印已安装的 pip 包列表
9. **conda list**：打印已安装的 conda 包列表（如果可用）
10. **conda env export**：打印 conda 环境导出（如果可用）

### 使用方式

```bash
# 命令行执行（输出所有诊断信息）
jupyter-troubleshoot

# 将输出保存到文件用于 issue 报告
jupyter-troubleshoot > troubleshoot.txt

# Python 中获取结构化数据
from jupyter_core.troubleshoot import get_data, subs

data = get_data()
print(f"Python: {data['sys_exe']}")
print(f"版本: {data['sys_version']}")

# 执行任意外部命令（容错）
git_version = subs(["git", "--version"])
if git_version:
    print(f"Git: {git_version}")
```

---

**下一步阅读：**
- [环境变量参考](08-environment-variables.md) — 所有环境变量的完整参考
- [基础使用示例](../examples/01-basic-usage.md) — 使用 get_data() 编程式收集环境信息
