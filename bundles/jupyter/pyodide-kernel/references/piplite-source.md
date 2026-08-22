---
type: Reference
title: piplite 源码参考
description: piplite 包的源码结构和核心 API——Pyodide 环境下的包管理器，包装 micropip 提供 wheel 索引和 PyPI 回退
tags: [piplite, micropip, package, wheel, install]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: piplite-init
    resource: /references/piplite-source.md
    title: "py/piplite/piplite/__init__.py"
---

## 源码文件位置

piplite 包位于 `packages/pyodide-kernel/py/piplite/piplite/`，源码路径：
`external/libs/jupyter/pyodide-kernel/packages/pyodide-kernel/py/piplite/piplite/`

## 核心模块

| 文件 | 说明 |
|------|------|
| `__init__.py` | 主入口，定义 install()、__all__ |
| `constants.py` | 常量定义（ALL_JSON、PIPLITE_URLS、DISABLE_PYPI_FALLBACK） |
| `piplite.py` | 核心包管理器实现 |

## 配置常量

```python
ALL_JSON = "all.json"                         # wheel 索引文件名
PIPLITE_URLS = None                           # 默认 piplite URLs（None = 使用 JS API）
DISABLE_PYPI_FALLBACK = False                 # 默认不禁用 PyPI 回退
PYPI_MAX_RETRIES = 5                          # PyPI 下载最大重试次数
CONTENT_TYPE_WHEEL = "application/zip"        # wheel MIME 类型
CHARSET = "utf-8"                             # 编码
PDPY_MAJOR_WARNING_DONE = False               # pydantic 版本警告标记
```

## install() 函数签名

```python
async def install(
    requirements: _AllPackages,    # str 或 str 列表，包名或 URL
    keep_going: bool = False,      # 出错时继续安装其他包
    deps: bool = True,             # 安装依赖
    credentials: str = "same-origin",
    pre: bool = False,             # 允许预发布版本
    index_urls: _AllPackages | None = None,  # 自定义索引 URL
    *,
    quiet: bool | None = None,
    verbose: bool | int | None = None,
    **kwargs,
) -> None:
```

requirements 可以是：
- 单个包名字符串：`"numpy"`
- 多个包名字符串：`["numpy", "pandas"]`
- wheel URL：直接下载安装

## 核心类

### PiplitePyPIManager

通过 `_micropip.PyPIManager` 子类化实现，扩展 micropip 的包管理器以支持：
1. 自定义 wheel 索引（ALL_JSON）
2. PyPI 回退功能
3. 本地 wheel 安装（emfs:// 协议）

关键方法：
- `_query_package()`: 三级查找策略（见概念文档）
- `add_package_url()`: 添加自定义 wheel URL
- `_extract_package()`: 从 URL 下载并安装 wheel
- `set_index_urls()`: 设置索引 URL 列表
- `get_package_indexes()`: 获取索引 URL 列表（含 pyodide-lock 内置索引）

### 辅助函数

```python
def parse_version(v: str) -> tuple[int, ...]: ...   # 语义化版本解析
def to_module_name(name: str) -> str: ...          # 包名→import名（替换连字符为下划线）
def get_package_max_version_index(versions: dict, target_v: tuple) -> int: ...  # 最大版本选择
```

## 三级包查找策略

```
1. pyodide-lock.json 预加载的内置包
2. PIPLITE_URLS 中的 all.json 本地索引（含本地 wheels + federated wheels）
3. pypi.org（DISABLE_PYPI_FALLBACK=False 时）
```

查找时按版本号选择最新兼容版本，支持比较运算符（`>=`, `==`, `<=`）。

## 相关概念

- [浏览器端包管理](/concepts/05-package-management.md)
- [构建时 Addon 系统](/concepts/04-build-addons.md)
