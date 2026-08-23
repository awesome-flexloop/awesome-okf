---
type: Concept
title: 配置系统
description: Papyri TOML 配置文件格式、Config 数据类、文件路径常量、环境变量与用户配置
tags: [papyri, config, toml, environment, setup]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: config-src
    resource: /references/config-source.md
    title: Papyri 配置系统源码信源
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
---

## 文件路径配置

Papyri 的本地数据路径在 `config.py` 中定义为常量：

```python
from os.path import expanduser
from pathlib import Path

base_dir = Path(expanduser("~/.papyri/"))
ingest_dir = base_dir / "ingest"
data_dir = base_dir / "data"
user_config_path = base_dir / "config.toml"
```

| 路径 | 默认值 | 用途 |
|------|--------|------|
| `base_dir` | `~/.papyri/` | Papyri 用户数据根目录 |
| `data_dir` | `~/.papyri/data/` | `papyri gen` 输出的 DocBundle 目录 |
| `ingest_dir` | `~/.papyri/ingest/` | Viewer 摄取数据（SQLite + CBOR blobs） |
| `user_config_path` | `~/.papyri/config.toml` | 用户配置文件 |

`ensure_dirs()` 函数创建上述目录。导入 config.py 时不自动创建目录（避免测试/只读 CLI 命令产生副作用），由写操作（GraphStore、gen）显式调用。

## TOML 配置文件

`papyri gen` 接受一个 TOML 配置文件作为参数，指定要文档化的模块和生成选项。

### [global] 节

```toml
[global]
module = 'papyri'                     # 必填：要文档化的根模块名
submodules = ['examples']             # 额外需要分析的子模块列表
examples_folder = '~/path/to/examples/'  # 示例文件目录
logo = "../papyri-logo.png"           # Logo 图片路径
docs_path = "~/path/to/docs"          # 叙述文档（RST文件）目录
execute_doctests = true               # 是否执行 doctest 代码示例
exec_failure = 'raise'               # 执行失败策略：'raise' 或其他
exclude = ["papyri.utils:FullQual"]   # 排除的限定名列表
```

### [global.directives] 节

自定义 RST 指令处理器映射。当 docstring 中使用了 papyri 不认识的 RST 指令时，必须在此注册处理器，否则序列化时会报错。

```toml
[global.directives]
# 格式：指令名 = '模块路径:处理函数'
mydirective = 'papyri.examples:_mydirective_handler'
directive = 'papyri.directives:code_handler'
# testsetup = 'papyri.directives:drop'  # 丢弃指令及其内容
```

**内置处理器**：

| 处理器 | 功能 |
|--------|------|
| `papyri.directives:drop` | 丢弃指令及其内容（静默忽略） |
| `papyri.directives:code_handler` | 将指令体保留为代码块 |

处理器函数的签名应接受指令参数并返回 IR 节点。

### [meta] 节

```toml
[meta]
github_slug = 'jupyter/papyri'  # GitHub 仓库 slug（owner/repo）
tag = '{{version}}'             # Git 标签模板，{{version}} 替换为实际版本
pypi = 'papyri'                 # PyPI 包名
```

## 示例配置

`examples/` 目录提供了多个真实库的配置示例：

| 文件 | 目标库 |
|------|--------|
| `papyri.toml` | papyri 自身 |
| `numpy.toml` | NumPy |
| `scipy.toml` | SciPy |
| `IPython.toml` | IPython |
| `matplotlib.toml` | Matplotlib |
| `pandas.toml` | Pandas |
| `astropy.toml` | Astropy |
| `dask.toml` | Dask |
| `scikit-image.toml` (skimage.toml) | scikit-image |
| `networkx.toml` | NetworkX |
| `xarray.toml` | xarray |
| `traitlets.toml` | Traitlets |
| `ipykernel.toml` | ipykernel |
| `distributed.toml` | Dask Distributed |

## 环境变量

### Python CLI 端

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PAPYRI_UPLOAD_URL` | `http://localhost:4321/api/bundle` | Viewer 上传端点 URL |
| `PAPYRI_UPLOAD_TOKEN` | （无） | Bearer 上传认证令牌 |
| `PAPYRI_VERSION` | 包版本 | 覆盖 User-Agent 中的版本字符串 |

### Viewer 端

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PAPYRI_INGEST_DIR` | `~/.papyri/ingest` | 摄取数据根目录 |
| `PAPYRI_INGEST_DB` | `~/.papyri/ingest/papyri.db` | SQLite 图数据库路径 |
| `PAPYRI_AUTH_DB` | `~/.papyri/auth.db` | SQLite 认证数据库路径 |
| `PAPYRI_SITE` | （无） | 反向代理后的规范外部 URL |
| `PAPYRI_USERNAME` / `PAPYRI_PASSWORD` | （无） | 初始管理员用户种子（首次运行且无用户时） |
| `PAPYRI_DEV_SEED` | （pnpm dev 时为 1） | 开发模式种子（admin/password） |
| `PAPYRI_BUILD_COMMIT` | （无） | 管理面板显示的 Git commit |
| `PAPYRI_BUILD_ADAPTER` | （无） | 管理面板显示的构建适配器名 |

## 用户配置

`user_config.py` 和 `config_loader.py` 管理用户级别的配置加载。用户配置文件 `~/.papyri/config.toml` 可以存储全局默认设置。

`Config` 数据类在 `config_loader.py` 中定义，`load_configuration()` 函数负责从 TOML 文件加载并返回 Config 对象。

## 相关概念

- [快速开始](01-getting-started.md)
- [gen 管线](05-gen-pipeline.md)
- [指令处理器扩展](11-directive-handlers.md)
- [pack 与 upload](08-pack-and-upload.md)
