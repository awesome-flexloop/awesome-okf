---
type: concept
title: "FCP 依赖求解与包下载"
description: "fcp.py 模块的核心机制：conda Solver API 依赖求解、ProgressiveFetchExtract 并行下载、跨包重复文件检测、路径长度检查和多环境处理。"
tags: [FCP, Solver, 依赖求解, ProgressiveFetchExtract, 包下载, 重复检测]
status: stable
stale_after: 2027-12-31
level: advanced
prerequisites: ["02-architecture-overview", "07-conda-interface"]
reading_time: 14
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-fcp
    resource: "constructor/fcp.py"
---

# FCP 依赖求解与包下载

fcp（Fetch Conda Packages）是 constructor 的核心业务模块，负责**依赖求解 → 包下载 → 去重校验 → 大小估算**的完整管线。所有包在构建时下载并打包到安装程序中，安装时无需网络。

## FCP 在整体流程中的位置

```mermaid
flowchart LR
    A[construct.yaml] --> B[Schema校验]
    B --> C[FCP 求解+下载]
    C --> D[Payload准备 preconda]
    D --> E[平台安装器生成]
```

FCP 的入口是 `fcp.main(info, verbose, dry_run, conda_exe)`（在 main.py 中别名为 `fcp_main`）。

## 核心函数调用链

```
fcp_main(info)
  └─ _main(info, ...)
       ├─ _solve_precs(specs/channels, platform, ...)  # base 环境求解
       ├─ for env in extra_envs:
       │    └─ _solve_precs(..., extra_env=True)       # 额外环境求解
       ├─ _fetch_precs(base_precs, download_dir)       # 下载 base 包
       ├─ for env in extra_envs:
       │    └─ _fetch_precs(env_precs, download_dir)   # 下载额外环境包
       ├─ all_pc_recs = list(unique(base+extra))       # 去重
       └─ check_duplicates_files(all_pc_recs)          # 重复检测+大小估算
```

## _solve_precs：依赖求解

### 三种输入模式

| 模式 | 触发条件 | 行为 |
|------|---------|------|
| **specs 模式** | `specs` 非空 | 直接用 Solver 求解 specs 列表 |
| **environment 模式** | `environment` 指定环境名 | 从已有 conda 环境读取历史记录重建 |
| **environment_file 模式** | `environment_file` 指定文件 | 用子进程 `conda env create` 创建临时环境，读取其记录后删除 |

### Solver 调用

```python
from .conda_interface import Solver

solver = Solver(
    prefix="/constructor/no-environment",  # 虚拟前缀，不实际创建环境
    channels=channel_urls,
    subdirs=(platform, "noarch"),         # 目标平台 + noarch
    specs_to_add=specs,
)
precs = list(solver.solve_final_state())  # 返回拓扑排序的 PackageRecord 列表
```

关键点：
- **prefix 是虚拟路径**：Solver 不需要实际安装环境，仅用于计算依赖关系
- **subdirs 参数**：实现交叉构建——在 Linux 上求解 win-64 平台的包
- **返回值拓扑排序**：`solve_final_state()` 返回的记录已按安装顺序排列（依赖先于依赖者）
- **base 环境自动添加 python**：除非 `base_needs_python=False`（docker模式），否则自动追加 `"python"` 到 specs

### 求解后处理

1. **warn_menu_packages_missing()**：检查 menu_packages 指定的包是否真的在结果中
2. **check_duplicates(precs, duplicate_filenames)**：检测同名包被多次求解的情况
3. **exclude_packages(precs, exclude)**：从结果中移除 exclude 列表中的包
4. **Python优先排序**：将 python 包移到列表最前面，确保安装顺序正确

## _fetch / _fetch_precs：包下载

### ProgressiveFetchExtract

```python
from .conda_interface import ProgressiveFetchExtract

ProgressiveFetchExtract(precs).execute()
```

`ProgressiveFetchExtract` 是 conda 的内置并行下载器：
- 从配置的通道并行下载包
- 提取到 `CONDA_PKGS_DIRS` 缓存目录
- 自动验证 MD5/SHA256 校验和
- 返回 `PrefixGraph` 排序后的记录列表（安装顺序）

### 下载后处理（_fetch_precs）

```python
def _fetch_precs(precs, download_dir, transmute_file_type):
    pc_recs = _fetch(precs, download_dir)      # 下载
    dists, _urls = [], []
    has_conda = False
    for prec in pc_recs:
        # 过滤出 solver 选中的包（排除缓存中无关的包）
        # 处理 transmute_file_type=".conda" 格式转换
        dists.append(prec.fn)
        _urls.append((prec.url, prec.md5))
        if prec.name in ("conda", "mamba"):
            has_conda = True
    return pc_recs, _urls, dists, has_conda
```

格式转换（transmute）使用 `conda_package_handling.api.transmute()` 将 `.tar.bz2` 包转换为更紧凑的 `.conda` 格式。

## check_duplicates_files：重复文件检测

这是 constructor 的一个重要质量保障步骤，在所有包下载完成后执行。

### 检测内容

遍历所有包的 `paths.json`，检测三类问题：

#### 1. 大小写敏感重复（同包路径）

同一个文件路径（大小写完全相同）出现在多个包中。这通常是包打包错误，可能导致安装时文件被覆盖：

```python
for pc_rec in pc_recs:
    paths_data = read_paths_json(pc_rec.extracted_package_dir)
    for path in paths_data["paths"]:
        short_path = path["_path"]
        if short_path in files:
            # 重复文件冲突
```

- 默认 `ignore_duplicate_files=True`：仅打印警告
- `ignore_duplicate_files=False`：直接 `sys.exit` 报错

#### 2. 大小写不敏感重复（大小写冲突）

在 macOS/Windows（大小写不敏感文件系统）上，`File.txt` 和 `file.txt` 是同一个文件。Linux 默认大小写敏感，仅警告：

```python
if sys.platform in ("darwin", "win32"):
    if path_lower in files_lower:
        # 大小写冲突，报错
```

#### 3. 路径长度计算（Windows MAX_PATH 检查）

Windows 传统 API 限制路径长度为 260 字符（MAX_PATH）。constructor 计算两个关键路径长度：

- **中间路径**：`pkgs/<dist>/<short_path>`（解压缓存时）
- **最终路径**：`envs/<env>/<short_path>`（链接到环境时）

```python
path_lengths = [
    len(f"pkgs/{pc_rec['fn']}/{short_path}"),
    len(f"envs/{env_name}/{short_path}"),
]
current_max = max(path_lengths)
```

取所有包的最大值存入 `info["_max_relative_path_length"]`，供安装脚本检查。

#### 4. 大小估算

同时累加压缩包大小和解压后文件大小：

```python
approx_tarballs_size += pc_rec["size"]           # 压缩后
approx_pkgs_size += path.get("size_in_bytes", 0) # 解压后
info["_approx_pkgs_size"] = approx_pkgs_size + 50*1024*1024  # 50MB缓冲区
info["_approx_tarballs_size"] = approx_tarballs_size
```

50MB 缓冲区用于容纳 conda-standalone 二进制和元数据文件。

## 多环境处理

当配置了 `extra_envs` 时，FCP 为每个环境独立求解和下载：

```python
for env_name, env_config in extra_envs.items():
    env_precs = _solve_precs(..., extra_env=True)  # 额外环境不强制python
    env_pc_recs, env_urls, env_dists, env_has_conda = _fetch_precs(env_precs, ...)
    info["_extra_envs_info"][env_name] = {
        "_urls": env_urls,
        "_dists": env_dists,
        "_records": env_pc_recs,
        "_specs": env_specs,
    }
```

多环境注意事项：
- `ignore_duplicate_files` 强制为 `True`（跨环境共享包是预期行为）
- 全局 `exclude` 对所有环境生效（空列表 `[]` 可覆盖为空）
- base 环境必须包含 `conda`（负责管理额外环境）
- 重复文件检测仍运行以计算路径长度和大小估算，但 `duplicate_files="skip"`

## conda 上下文管理

fcp.main() 入口处有重要的上下文保留逻辑：

```python
from .conda_interface import conda_replace_context_default, conda_context

# 保存用户代理/SSL配置（防止被 conda-standalone 环境覆盖）
saved_proxy_servers = deepcopy(conda_context.proxy_servers)
saved_ssl_verify = conda_context.ssl_verify

conda_replace_context_default(
    CONDA_CACHE_DIR=cache_dir,
    CONDA_CHANNELS=channels,
    ...
)

# ... 执行求解和下载 ...

# 恢复代理配置
if saved_proxy_servers:
    conda_context.proxy_servers = saved_proxy_servers
if saved_ssl_verify is not None:
    conda_context.ssl_verify = saved_ssl_verify
```

这确保企业代理和自定义 SSL 证书在构建过程中正常工作。

## dry-run 模式

`--dry-run` 参数跳过下载和安装程序生成，仅执行求解。这对于验证 construct.yaml 配置正确性很有用：

```bash
constructor . --dry-run
```

dry-run 模式在求解完成后返回，输出：
- 每个环境将包含的包列表
- 估算大小
- 重复文件警告
- 路径长度警告

## 写入 info 的字段

FCP 完成后，info 字典中写入以下关键数据供后续模块使用：

| 字段 | 类型 | 使用者 |
|------|------|--------|
| `_urls` | list[tuple[url, md5]] | preconda（写入urls文件） |
| `_dists` | list[str] | 平台安装器 |
| `_records` | list[PackageRecord] | build_outputs（lockfile等） |
| `_all_pkg_records` | list[PackageCacheRecord] | check_duplicates_files、preconda |
| `_approx_pkgs_size` | int | 安装脚本（磁盘空间检查） |
| `_approx_tarballs_size` | int | 安装脚本 |
| `_max_relative_path_length` | int | 安装脚本（MAX_PATH检查） |
| `_has_conda` | bool | 平台安装器（决定初始化选项） |
| `_extra_envs_info` | dict | preconda、平台安装器 |

## 下一步

- [07-conda_interface 防腐层](07-conda-interface.md)：了解 FCP 使用的 conda API 如何被封装
- [08-Preconda Payload 准备](08-preconda-payload.md)：了解下载后的包如何被打包进安装程序
