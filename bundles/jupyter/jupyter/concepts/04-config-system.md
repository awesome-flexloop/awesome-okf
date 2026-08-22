---
type: Concept
title: Jupyter 通用配置系统
description: traitlets 配置框架、配置文件生成与编辑、配置类属性语法、命令行覆盖配置、集合类型配置方法
tags: [jupyter, config, traitlets, configuration, jupyter-config]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T10:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T10:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-metasource
    resource: /references/jupyter-metasource.md
---

# Jupyter 通用配置系统

Jupyter 生态中的所有应用（Notebook、JupyterLab、nbconvert、JupyterHub 等）共享一套统一的配置系统，基于 [traitlets](https://traitlets.readthedocs.io/) 库构建。理解这套配置系统是定制 Jupyter 行为的基础。

## 配置系统核心概念

Jupyter 的配置系统有几个核心特性：

1. **统一配置目录**：所有 Jupyter 应用共享 `~/.jupyter` 配置目录（可通过环境变量覆盖）
2. **Python 配置文件**：配置文件是 Python 脚本，使用 `c.ClassName.attribute = value` 语法
3. **配置文件自动发现**：应用启动时自动从搜索路径加载配置文件
4. **命令行覆盖**：命令行参数优先级高于配置文件
5. **Traitlets 类型系统**：配置项有类型校验和默认值

## 配置文件类型

### 内核配置 vs 应用配置

需要区分两类配置：

| 配置类型 | 位置 | 说明 |
|---------|------|------|
| **Jupyter 应用配置** | `~/.jupyter/` 等 | 适用于 Notebook、JupyterLab、nbconvert 等 Jupyter 应用 |
| **Kernel 配置** | 各 Kernel 自己的目录 | 例如 IPython 内核使用 `~/.ipython/` 而非 `~/.jupyter/` |

IPython 内核有自己的配置目录（`~/.ipython/`），不使用 Jupyter 的通用配置目录。其他语言的 Kernel 也通常有各自的配置位置。

## 生成配置文件

使用 `--generate-config` 选项为特定应用生成默认配置文件：

```bash
# 生成 Jupyter Notebook 配置文件
jupyter notebook --generate-config

# 生成 JupyterLab 配置文件（如果支持）
jupyter lab --generate-config
```

生成的文件命名为 `jupyter_{application}_config.py`，例如：

- `jupyter_notebook_config.py` — Notebook 配置
- `jupyter_server_config.py` — Jupyter Server 配置
- `jupyter_nbconvert_config.py` — nbconvert 配置

配置文件会被写入 Jupyter 配置目录（默认为 `~/.jupyter/`）。

## 配置语法

配置文件是标准的 Python 脚本，通过全局变量 `c`（Config 对象）来设置配置项：

```python
# 设置 Notebook 监听端口
c.NotebookApp.port = 8754

# 设置不自动打开浏览器
c.NotebookApp.open_browser = False

# 设置 Notebook 启动目录
c.NotebookApp.notebook_dir = '/home/user/notebooks'

# 设置允许的来源（CORS）
c.ServerApp.allow_origin = '*'
```

### 配置类命名

配置类名通常与应用/组件名对应：

| 配置类 | 所属组件 |
|--------|---------|
| `NotebookApp` | Jupyter Notebook（经典） |
| `ServerApp` | Jupyter Server（Notebook v7 和 JupyterLab 使用） |
| `LabServerApp` | JupyterLab 特定配置 |
| `TemplateExporter` | nbconvert 模板导出器 |

> **注意**：Notebook v7 和 JupyterLab 使用 Jupyter Server 作为后端，因此很多配置项在 `ServerApp` 而非 `NotebookApp` 下。

### 拼写错误静默忽略

配置文件中的**拼写错误会被静默忽略**，不会报错。如果发现配置项不生效，第一检查项就是拼写是否正确（包括大小写）。

## 命令行覆盖配置

每个配置值都可以通过命令行参数覆盖，使用 `--ClassName.attribute=value` 语法：

```bash
# 等价于 c.NotebookApp.port = 8754
jupyter notebook --NotebookApp.port=8754

# 常用选项有短别名
jupyter notebook --port 8754
jupyter notebook --no-browser
```

**命令行选项的优先级高于配置文件**——配置文件中设置的值会被命令行参数覆盖。

### 查看可用选项

```bash
# 查看常用选项（短选项和帮助）
jupyter notebook --help

# 查看所有可配置项（包括完整类名和属性名）
jupyter notebook --help-all
```

`--help-all` 输出非常详细，包含每个配置项的类型、默认值和说明，是编写配置文件的最佳参考。

## 集合类型配置

对于列表、字典、集合等集合类型的配置项，可以使用 Python 方法来修改：

```python
# 追加到列表末尾
c.TemplateExporter.template_path.append('./templates')

# 插入到列表开头（prepend）
c.TemplateExporter.template_path.prepend('./my-templates')

# 扩展列表
c.InteractiveShellApp.extensions.extend(['my_extension'])

# 添加到集合
c.ServerApp.allow_origin_pat.add('https://example.com')

# 更新字典
c.Exporter.preprocessors.update({'my_preprocessor': True})
```

常用方法总结：

| 方法 | 适用类型 | 效果 |
|------|---------|------|
| `.append(x)` | list | 在末尾添加元素 |
| `.prepend(x)` | list（LazyConfigValue） | 在开头添加元素 |
| `.extend([...])` | list | 批量添加元素 |
| `.add(x)` | set | 添加元素（去重） |
| `.update({...})` | dict/set | 批量更新 |

> **提示**：使用 `.prepend()` 而非 `.insert(0, x)`，因为配置值在加载时可能是 `LazyConfigValue`（延迟配置值），`prepend` 是专门为 Jupyter 配置提供的方法。

## 配置文件搜索路径

Jupyter 配置文件不是只从一个位置加载，而是从一个搜索路径列表中依次加载，后加载的配置会覆盖先加载的。搜索路径顺序：

| 优先级 | Unix/Linux | Windows |
|--------|-----------|---------|
| 1（最高） | `$JUPYTER_CONFIG_DIR`（默认 `~/.jupyter/`） | `%JUPYTER_CONFIG_DIR%`（默认 `%USERPROFILE%\.jupyter`） |
| 2 | `$JUPYTER_CONFIG_PATH` 中的各目录 | `%JUPYTER_CONFIG_PATH%` 中的各目录 |
| 3 | `{sys.prefix}/etc/jupyter/` | `{sys.prefix}\etc\jupyter\` |
| 4（系统级） | `/usr/local/etc/jupyter/`、`/etc/jupyter/` | `%PROGRAMDATA%\jupyter\` |

这意味着：

- **用户配置**（~/.jupyter/）优先级最高，覆盖系统级配置
- **环境级配置**（sys.prefix/etc/jupyter/）适用于 conda/venv 环境
- **系统级配置**（/etc/jupyter/）适用于所有用户
- `JUPYTER_CONFIG_PATH` 可以追加额外的配置搜索目录（用 `:` 分隔，Windows 用 `;`）

### JUPYTER_CONFIG_PATH 的典型用途

当在自定义 prefix（如 conda 环境）安装了 notebook/server 扩展时，扩展的自动启用配置文件位于 `{prefix}/etc/jupyter/`。要让 Jupyter 发现这些配置，需要将该目录加入 `JUPYTER_CONFIG_PATH`：

```bash
# 添加自定义 prefix 的配置目录
export JUPYTER_CONFIG_PATH="/opt/my-jupyter/etc/jupyter:$JUPYTER_CONFIG_PATH"
```

## 配置示例

### 常用 Notebook 配置

```python
# jupyter_notebook_config.py 或 jupyter_server_config.py

# 端口和网络
c.ServerApp.ip = '0.0.0.0'          # 监听所有网络接口（允许远程访问）
c.ServerApp.port = 8888             # 端口
c.ServerApp.open_browser = False    # 不自动打开浏览器

# 文件目录
c.ServerApp.root_dir = '/home/user/projects'  # 启动时的根目录

# 安全
c.ServerApp.password = 'sha1:...'   # 设置密码（使用 jupyter server password 生成）
c.ServerApp.token = ''              # 禁用 token（仅限开发环境！）
c.ServerApp.allow_origin = '*'      # CORS 设置

# 内核
c.MappingKernelManager.default_kernel_name = 'python3'
```

### nbconvert 配置

```python
# jupyter_nbconvert_config.py

# 自定义模板路径
c.TemplateExporter.template_path.append('./my-templates')

# 默认导出格式
c.NbConvertApp.export_format = 'html'

# 执行配置
c.ExecutePreprocessor.timeout = 60  # 单元格执行超时（秒）
```

## 密码设置

Jupyter Notebook/Lab 支持密码认证（替代 URL token）：

```bash
# 设置密码（会提示输入密码，哈希值写入配置）
jupyter server password
```

这会在配置文件中写入 `c.ServerApp.password` 字段。

## 反直觉要点

1. **配置文件是 Python 代码**：你可以在配置文件中写任意 Python 代码（导入模块、计算值等），不只是键值赋值
2. **拼写错误不报**：配置属性名写错了不会有任何错误提示，只是不生效
3. **配置类名可能变化**：从 Notebook classic 切换到 Notebook v7/JupyterLab 时，很多配置从 `NotebookApp` 迁移到了 `ServerApp`
4. **Kernel 配置独立**：IPython 的配置在 `~/.ipython/`，不是 `~/.jupyter/`
5. **配置文件可以不存在**：没有配置文件时使用全部默认值，不需要强制生成
6. **环境变量优先于配置文件**：某些配置可以通过环境变量设置（如 `JUPYTER_PORT`），环境变量通常优先级最高

## 相关概念

- [目录结构与文件位置](05-directories.md) — 配置/数据/运行时目录的详细路径与环境变量
- [jupyter 命令与子命令发现](03-jupyter-command.md) --config-dir/--paths 选项
- [配置基础操作](../examples/02-config-basics.md) — 实战：生成和修改配置
