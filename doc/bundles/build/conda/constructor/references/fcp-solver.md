---
type: reference
title: "FCP 求解与下载模块 (fcp.py)"
description: "fcp.py 中 conda 包求解、下载、去重、重复文件检测的核心源码分析。"
tags: [FCP, Solver, ProgressiveFetchExtract, 包下载, 依赖求解]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T00:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: constructor-fcp
    resource: "constructor/fcp.py"
    title: "constructor/fcp.py 包获取模块"
---

# FCP 求解与下载模块 (fcp.py)

fcp（Fetch Conda Packages）模块是 constructor 的核心业务逻辑层，负责 **依赖求解 → 包下载 → 去重校验 → 大小估算** 的完整管线。

## 核心函数

### `main(info, verbose, dry_run, conda_exe)`

FCP 入口函数，从 `info` 字典中提取所有配置参数，设置 conda 上下文环境变量（`CONDA_PKGS_DIRS`），调用 `_main()` 执行求解下载，将结果写回 `info` 字典。

关键写入 `info` 的字段：
- `info["_all_pkg_records"]` — 所有环境的 PackageCacheRecord 列表（去重后）
- `info["_urls"]` — base 环境包的 `(url, md5)` 元组列表
- `info["_dists"]` — base 环境的分发包文件名列表
- `info["_records"]` — base 环境的 PackageRecord 列表（拓扑排序后）
- `info["_approx_tarballs_size"]` / `info["_approx_pkgs_size"]` — 压缩/解压大小估算
- `info["_has_conda"]` — base 环境是否包含 conda
- `info["_extra_envs_info"]` — 额外环境数据：`{env_name: {_urls, _dists, _records}}`
- `info["_max_relative_path_length"]` — 最大相对路径长度（Windows MAX_PATH 检查）

### `_solve_precs(...)` → 依赖求解

```python
solver = Solver(
    prefix="/constructor/no-environment",
    channels=channel_urls,
    subdirs=(platform, "noarch"),
    specs_to_add=specs,
)
precs = list(solver.solve_final_state())  # 返回拓扑排序的 PackageRecord 列表
```

- base 环境自动追加 `"python"` 到 specs（除非 `base_needs_python=False`）。
- 支持三种输入模式：`specs`（直接列包）、`environment`（从已有环境复制）、`environment_file`（从 environment.yml/txt 创建临时环境求解）。
- 环境文件模式：调用子进程 `conda env create --file <file> --prefix <tmpdir>` 创建临时环境后读取其记录。
- 求解后执行：`warn_menu_packages_missing()`（菜单包缺失警告）、`check_duplicates()`（同名包重复检测）、`exclude_packages()`（排除指定包）。

### `_fetch(download_dir, precs)` → 下载包

```python
from conda.core.package_cache_data import ProgressiveFetchExtract
ProgressiveFetchExtract(precs).execute()
```

使用 conda 的 `ProgressiveFetchExtract` 并行下载并提取包到缓存目录，返回 `PrefixGraph` 排序后的记录列表。

### `_fetch_precs(precs, download_dir, transmute_file_type)` → 下载+格式转换

- 下载后过滤出 solver 选中的包记录。
- 若设置 `transmute_file_type=".conda"`，使用 `conda_package_handling.api.transmute()` 将 `.tar.bz2` 转成 `.conda` 格式。
- 返回 `(pc_recs, _urls, dists, has_conda)` 四元组。

### `check_duplicates_files(...)` → 重复文件检测

遍历所有包的 `paths.json`，检测：
1. **大小写敏感重复**：同一路径出现在多个包中 → 默认报错（`ignore_duplicate_files=True` 时警告）。
2. **大小写不敏感重复**：在 macOS/Windows（大小写不敏感文件系统）上，路径小写相同但大小写不同也报错，Linux 仅警告。
3. **路径长度计算**：分别计算 `pkgs/<dist>/<short_path>`（中间路径）和 `envs/<env>/<short_path>`（最终路径）的长度，取最大值用于 Windows MAX_PATH 检查。
4. **大小估算**：累加 tarball 大小和解压后文件大小（初始 50MB 缓冲区）。

## 多环境处理流程

```
_main()
  ├─ _solve_precs()           # 求解 base 环境
  ├─ for env_name in extra_envs:
  │    └─ _solve_precs(extra_env=True)  # 求解每个额外环境（不强制python）
  ├─ _fetch_precs(base_precs) # 下载 base 包
  ├─ for env in extra_envs:
  │    └─ _fetch_precs(env_precs)  # 下载额外环境包
  ├─ all_pc_recs 去重
  └─ check_duplicates_files(all_pc_recs)  # 重复检测+大小估算
```

extra_envs 存在时跳过重复文件检测（`duplicate_files="skip"`），因为跨环境共享包是预期行为，但仍计算大小和路径长度。

## 关键设计

- **代理/SSL保留**：`fcp_main()` 在调用 `conda_replace_context_default` 前保存 `proxy_servers` 和 `ssl_verify`，替换上下文后恢复，确保企业代理环境正常工作（F-002）。
- **conda-standalone 版本检测**：Windows 下 micromamba 不支持（`sys.exit`）；`uninstall_with_conda_exe` 需要 conda >=24.11.0；frozen 环境在 conda-standalone 25.5.x 有已知bug。
- **Python优先排序**：求解后将 `python` 包移到记录列表最前面，确保安装顺序正确。
