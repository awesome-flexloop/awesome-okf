---
type: "concept"
title: "环境加载与文件收集"
description: load_environment() 如何扫描 conda-meta 元数据、区分托管文件与非托管文件、处理 noarch 包路径重定向、检测可编辑包和缺失文件。
tags: [conda-pack, environment-loading, conda-meta, noarch, file-collection]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
---

# 环境加载与文件收集

环境加载是打包的第一步，由 `load_environment()` 函数完成。它负责扫描 conda 环境目录，识别所有文件并创建对应的 `File` 对象列表。

## 加载流程概览

```
load_environment(prefix)
    │
    ├─ 1. 验证环境路径有效性
    ├─ 2. 查找 Python site-packages
    ├─ 3. 检查可编辑包（editable packages）
    ├─ 4. 扫描目录获取全部文件（all_files）
    ├─ 5. 遍历 conda-meta/*.json 加载托管包文件
    │     ├─ 包缓存命中 → load_managed_package()
    │     └─ 包缓存缺失 → file_mode='unknown'
    ├─ 6. 检测缺失文件
    ├─ 7. 添加 conda-meta/history
    └─ 8. 添加非托管文件（pip/手动放置）
```

## 1. 环境验证

`load_environment()` 首先验证路径有效性 [F-026]：

```python
if not os.path.exists(prefix):
    raise CondaPackException("Environment path %r doesn't exist" % prefix)
conda_meta = os.path.join(prefix, 'conda-meta')
if not os.path.exists(conda_meta):
    raise CondaPackException("Path %r is not a conda environment" % prefix)
```

一个有效的 conda 环境必须包含 `conda-meta/` 目录。

## 2. 查找 site-packages

`find_site_packages(prefix)` 函数通过 glob `conda-meta/python-*.json` 文件确定环境中安装的 Python 版本 [F-033]：

- 无 Python 包 → 返回 `None`（纯非 Python 环境）
- 多个 Python → 抛出异常（异常情况）
- 一个 Python → 返回对应 site-packages 路径：
  - Windows: `Lib/site-packages`
  - POSIX: `lib/python{major}.{minor}/site-packages`

## 3. 可编辑包检测

`check_no_editable_packages()` 检查现代 pip（≥20.0）的可编辑安装 [F-032]：

- 扫描 `site-packages/*.dist-info/direct_url.json` 文件
- 解析 JSON，检查 `dir_info.editable == True`
- 如果发现可编辑包，抛出异常列出所有违规包名
- 可通过 `ignore_editable_packages=True` 跳过此检查

> **为什么要禁止可编辑包？** 可编辑安装（`pip install -e`）的包通过符号链接或 `.pth` 文件指向源码目录，其文件不在 conda 环境的标准目录结构中，打包无法包含实际源码。

## 4. 全目录扫描

`load_files(prefix)` 遍历环境目录，收集所有文件和目录 [F-027]：

```python
ignore = {
    "pkgs", "envs", "conda-bld", ".conda_lock", "users",
    "conda-recipes", ".index", ".unionfs", ".nonadmin",
    "python.app", "Launcher.app",
}
```

**忽略规则**：
- 忽略上述特殊目录（pkgs/ 是包缓存，envs/ 是嵌套环境等）
- 忽略以 `~` 结尾的文件（编辑器备份）和 `.DS_STORE`（macOS）
- 普通文件和符号链接直接加入结果集
- 子目录递归遍历，空目录也加入结果集

返回的是环境中所有文件的相对路径集合，用于后续区分托管文件和非托管文件。

## 5. 托管包文件加载

核心逻辑：遍历 `conda-meta/*.json`，每个 JSON 文件对应一个已安装的包 [F-026]。

### conda-meta JSON 结构

每个 `<package>-<version>-<build>.json` 文件包含：

```json
{
  "name": "numpy",
  "version": "1.24.0",
  "url": "https://conda.anaconda.org/...",
  "files": ["lib/python3.10/site-packages/numpy/__init__.py", ...],
  "link": {"source": "/path/to/pkgs/numpy-1.24.0-py310_0"}
}
```

### 包缓存命中路径

如果 `info['link']['source']` 指向的包缓存目录存在，调用 `load_managed_package()` [F-029]：

1. **读取 noarch 类型**：通过 `read_noarch_type()` 检查 `info/link.json` 或 `info/package_metadata.json` 中的 `noarch.type` 字段 [F-030]
   - `'python'`：noarch:python 包，需要路径重定向
   - `None` 或其他：普通包

2. **读取文件列表**：
   - 优先使用 `info/paths.json`（新版格式），包含路径和前缀替换信息
   - 回退到 `info/files`（旧版格式）+ `info/has_prefix`（前缀信息）[F-031]

3. **路径重定向**（noarch:python 包）：
   - `site-packages/xxx` → `{actual site-packages}/xxx`
   - `python-scripts/xxx` → `{BIN_DIR}/xxx`
   - 其他路径不变 [F-028]

4. **补充文件**：对于 noarch 包，还从 `info['files']` 补充包缓存中未列出但环境中存在的文件（如编译后的 .pyc）

### 包缓存缺失路径

如果包缓存目录不存在（通常是 `conda clean -p` 清理了缓存），则 [F-026]：
- 将该包所有文件标记为 `file_mode='unknown'`、`prefix_placeholder=None`
- 记录包信息到 `uncached` 列表
- 默认发出警告（`on_missing_cache='warn'`），可设置为 `'raise'` 报错

### paths.json 格式

新版 paths.json 为每个文件提供更详细的元数据：

```json
{
  "paths": [
    {
      "_path": "bin/numpy",
      "prefix_placeholder": "/opt/conda",
      "file_mode": "text"
    },
    ...
  ]
}
```

### has_prefix 格式（旧版）

旧版 has_prefix 文件使用类 shell 语法，每行记录一个需要前缀替换的文件 [F-031]：

```
<placeholder> <mode> <path>    # 三字段：占位符、模式、路径
<path>                         # 单字段：使用默认占位符和 text 模式
```

## 6. 缺失文件检测

通过集合差运算检测包记录中存在但实际文件系统中不存在的文件 [F-026]：

```python
targets = {os.path.normcase(f.target) for f in new_files}
new_missing = targets.difference(all_files)
```

如果发现缺失文件：
- 默认：收集所有缺失包信息后抛出异常，提示可能是 pip 卸载/覆盖了 conda 托管文件
- `ignore_missing_files=True`：过滤掉缺失文件，继续打包

## 7. conda-meta 元数据

- 每个 `conda-meta/*.json` 文件本身也被加入归档 [F-026]
- `conda-meta/history` 文件也被加入（如果存在）
- 这些文件在打包时会通过 `rewrite_conda_meta()` 清除绝对路径字段：
  - `extracted_package_dir` → `""`
  - `package_tarball_full_path` → `""`
  - `link.source` → `""` [F-034]

## 8. 非托管文件

`all_files` 中不属于任何 conda 托管包的文件被视为非托管文件（is_conda=False）[F-026]：

- 包括 pip install 安装的文件、用户手动放置的文件等
- 统一标记为 `file_mode='unknown'`，由 Packer 自动检测类型
- 排除旧版 conda 自动插入的 activate/conda/deactivate 脚本（POSIX 和 Windows 版本）
- 通过 `find_py_source()` 排除 .pyc 对应的 .py 源文件已在托管列表中的情况（避免重复）

## 特殊目录与文件

| 名称 | 处理方式 |
|------|---------|
| `pkgs/` | 忽略（包缓存，不应打包） |
| `envs/` | 忽略（嵌套环境） |
| `conda-bld/` | 忽略（conda-build 工作目录） |
| `.conda_lock` | 忽略 |
| `conda-meta/*.json` | 重写绝对路径后添加 |
| `conda-meta/history` | 直接添加 |
| `bin/activate` 等 | 排除旧版，使用 conda-pack 自带脚本 |
