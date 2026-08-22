---
type: Reference
title: Papyri 配置系统源码信源
description: Papyri TOML 配置文件格式、Config 数据类、配置加载与用户配置源码索引
tags: [papyri, config, toml, setup]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-repo
    resource: https://github.com/carreau/papyri
    title: Papyri GitHub Repository
---

## 配置系统源码索引

### 文件位置常量（config.py）

源码路径：`papyri/config.py`

| 常量 | 值 | 说明 |
|------|-----|------|
| `base_dir` | `~/.papyri/` | Papyri 用户数据根目录 |
| `data_dir` | `~/.papyri/data/` | DocBundle 输出目录（gen 产物） |
| `ingest_dir` | `~/.papyri/ingest/` | Viewer 摄取数据目录（SQLite + blobs） |
| `user_config_path` | `~/.papyri/config.toml` | 用户配置文件路径 |
| `ensure_dirs()` | - | 创建上述目录（导入时不自动调用，由写操作显式调用） |

### TOML 配置文件格式

示例：`examples/papyri.toml`

```toml
[global]
module = 'papyri'                    # 要文档化的根模块名
submodules = ['examples']            # 需要额外分析的子模块
examples_folder = '~/path/to/examples/'  # 示例文件夹
logo = "../papyri-logo.png"          # Logo 路径
docs_path = "~/path/to/docs"         # 叙述文档路径（RST 文件）
execute_doctests = true              # 是否执行 doctest
exec_failure = 'raise'               # 执行失败策略
exclude = ["papyri.utils:FullQual"]  # 排除的限定名列表

[global.directives]                  # 自定义 RST 指令处理器
mydirective = 'papyri.examples:_mydirective_handler'
directive = 'papyri.directives:code_handler'

[meta]
github_slug = 'jupyter/papyri'       # GitHub 仓库 slug
tag = '{{version}}'                  # 版本标签模板
pypi = 'papyri'                      # PyPI 包名
```

### 内置指令处理器（directives.py）

| 处理器 | 功能 |
|--------|------|
| `papyri.directives:drop` | 丢弃指令及其内容 |
| `papyri.directives:code_handler` | 将指令内容保留为代码块 |

### 环境变量

| 变量 | 使用方 | 说明 |
|------|--------|------|
| `PAPYRI_UPLOAD_URL` | upload CLI, viewer | Viewer 端点（默认 `http://localhost:4321/api/bundle`） |
| `PAPYRI_UPLOAD_TOKEN` | upload CLI, viewer | Bearer 上传令牌 |
| `PAPYRI_INGEST_DIR` | viewer | 数据根目录（默认 `~/.papyri/ingest`） |
| `PAPYRI_INGEST_DB` | viewer | SQLite 图数据库路径 |
| `PAPYRI_AUTH_DB` | viewer | SQLite 认证数据库路径 |
| `PAPYRI_SITE` | viewer build | 反向代理后的规范外部 URL |
| `PAPYRI_USERNAME`/`PAPYRI_PASSWORD` | viewer | 初始管理员用户种子 |
| `PAPYRI_DEV_SEED` | viewer | 开发模式种子（admin/password） |
| `PAPYRI_VERSION` | upload CLI | 覆盖 User-Agent 版本字符串 |
| `PAPYRI_BUILD_COMMIT` | viewer build | 管理面板显示的 Git commit |
| `PAPYRI_BUILD_ADAPTER` | viewer build | 管理面板显示的构建适配器名 |
