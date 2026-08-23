---
type: concept
title: "CLI 命令行入口"
description: "constructor 命令行工具的完整参数参考、环境变量、退出码、以及 main()/main_build() 函数的执行流程分析。"
tags: [CLI, 命令行, argparse, 参数, main, 构建流程]
status: stable
stale_after: 2027-12-31
level: intermediate
prerequisites: ["01-getting-started", "04-installer-types"]
reading_time: 10
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-main
    resource: "constructor/main.py"
---

# CLI 命令行入口

constructor 的命令行接口由 [`constructor/main.py`](../references/main-cli.md) 中的 `main()` 函数提供，使用 Python 标准库 `argparse` 解析参数。

## 基本用法

```bash
constructor [DIR_PATH] [OPTIONS]
```

`DIR_PATH` 是包含 `construct.yaml` 的目录，默认为当前工作目录（`.`）。

## 完整参数参考

### 位置参数

| 参数 | 说明 |
|------|------|
| `dir_path` | construct.yaml 所在目录，默认 `.` |

### 输出与缓存

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--output-dir`, `-o` | 安装程序输出目录 | 当前目录 |
| `--cache-dir` | 包下载缓存目录 | `~/.conda/constructor` |
| `--clean` | 清理缓存目录并退出 | — |

### 平台与类型控制

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--platform` | 目标平台（如 `win-64`, `linux-64`, `osx-arm64`） | 当前平台 |
| `--installer-type`, `-t` | 安装程序类型：`sh`, `pkg`, `exe`, `msi`, `all` | 平台默认 |
| `--conda-exe` | conda-standalone/micromamba 可执行文件路径 | 自动查找 |

### 调试与测试

| 参数 | 说明 |
|------|------|
| `--dry-run`, `--dry-run-conda` | 仅求解依赖，不生成安装程序 |
| `--render` | 渲染 construct.yaml（处理 selectors 和 Jinja2）并输出，不构建 |
| `--help-construct` | 输出所有 construct.yaml 可用配置键并退出 |
| `-v`, `--verbose` | 详细输出模式 |
| `-V`, `--version` | 输出版本号并退出 |
| `-h`, `--help` | 显示帮助信息 |

### 环境变量

| 变量 | 说明 |
|------|------|
| `CONSTRUCTOR_CACHE` | 缓存目录（等同 `--cache-dir`） |
| `CONDA_CHANNEL_URLS` | 通道 URL（可在 Jinja2 模板中引用） |
| `CONDA_CHANNEL_ALIASES` | 通道别名映射 |
| `CONDA_SOLVER` | 指定 conda solver 插件（如 `libmamba`） |

## conda-standalone 查找逻辑

constructor 需要一个独立的 conda 二进制文件（conda-standalone 或 micromamba）来执行依赖求解和包下载。查找顺序：

1. **`--conda-exe` 参数**：如用户显式指定，直接使用
2. **默认路径**：`sys.prefix/standalone_conda/conda.exe`（Windows）或 `sys.prefix/standalone_conda/conda`（Unix）
3. **错误提示**：都未找到时，报错提示运行 `conda install conda-standalone`

`identify_conda_exe()` 函数通过检查可执行文件是否能成功运行 `--version` 来验证其有效性。识别结果存储在：
- `info["_conda_exe"]`：可执行文件路径
- `info["_conda_exe_type"]`：`StandaloneExe.CONDA` 或 `StandaloneExe.MAMBA`

> **Windows 注意**：micromamba 在 Windows 上不受支持，使用时会 `sys.exit` 报错。

## 核心执行流程（main_build）

`main_build(info, verbose=False)` 是实际的构建编排函数，执行以下步骤：

### Step 1: 确定安装程序类型

```python
itypes = get_installer_type(info)
```

- 如用户通过 `--installer-type` 指定，使用指定类型
- 否则从 `info["installer_type"]`（YAML配置）读取
- 都没有时使用平台默认类型
- 验证指定类型是否允许在当前平台构建

### Step 2: 查找 conda-standalone

```python
if "--conda-exe" not in sys.argv:
    # 查找默认路径
    check_version(...)  # 验证版本 >=24.1
```

### Step 3: 验证 frozen 配置

```python
validate_frozen_envs(info)
```

检查 `freeze_base` 和 `extra_envs` 中的 `freeze_env` 是否有 conda-standalone 版本冲突（25.5.x 有已知 bug）。

### Step 4: 路径规范化

将 `license_file`、`welcome_image`、`header_image`、`icon_image`、`pre_install`、`post_install`、`pre_uninstall`、`nsis_template`、`welcome_file`、`readme_file`、`conclusion_file`、`post_install_pages`、`extra_files`、`temp_extra_files` 等路径字段转为绝对路径。

### Step 5: 调用 FCP（求解+下载）

```python
fcp_main(info, verbose=verbose, dry_run=dry_run, conda_exe=conda_exe)
```

这一步完成依赖求解和包下载，写入 `info["_urls"]`、`info["_records"]`、`info["_all_pkg_records"]` 等字段。详见 [06-FCP依赖求解与包下载](./06-fcp-fetch-and-solve.md)。

若为 `--dry-run`，在此步之后退出。

### Step 6: 循环构建各安装程序类型

```python
for itype in itypes:
    if itype == "sh":
        shar_create(info, verbose=verbose)
    elif itype == "pkg":
        osxpkg_create(info, verbose=verbose)
    elif itype == "exe":
        winexe_create(info, verbose=verbose)
    elif itype == "msi":
        briefcase_create(info, verbose=verbose)
```

每个平台模块都实现统一的 `create(info, verbose=False)` 接口。Docker 类型单独处理。

### Step 7: 处理构建产物

```python
if build_outputs:
    process_build_outputs(info, build_outputs_keys)
```

根据 `build_outputs` 配置生成额外产物（hash/info.json/licenses/lockfile/pkgs_list）。

## _HelpConstructAction 自定义帮助

`--help-construct` 使用自定义 argparse Action 从 JSON Schema 动态生成配置键参考：

1. 加载 `construct.schema.json`
2. 提取所有属性及其描述
3. 格式化输出（支持 deprecated 标记）
4. 列出当前平台可用的 selectors
5. 立即退出（不执行构建）

这确保文档始终与 Schema 保持同步——无需手动维护配置参考。

## 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 非0 | 错误（YAML解析失败、Schema校验失败、依赖求解失败、包下载失败、安装程序生成失败等） |

错误通过 `conda_exception_handler` 捕获，格式化输出错误信息和堆栈跟踪。

## Python API 调用

constructor 也可以作为 Python 库调用：

```python
from constructor.main import main as constructor_main

# 等同于命令行 constructor . -o ./dist --platform win-64
constructor_main([".", "-o", "./dist", "--platform", "win-64",
                 "--conda-exe", "/path/to/conda.exe"])
```

主要可导入函数：

| 函数 | 用途 |
|------|------|
| `main(argv=None)` | CLI 入口，处理命令行参数 |
| `main_build(info, verbose=False)` | 核心构建流程（传入 info 字典） |
| `main_subshell(*args, **kwargs)` | 非 shell 命令模式入口 |
| `main_sourced(*args, **kwargs)` | shell.xxx 命令模式入口（如 `shell.bash`） |
| `get_installer_type(info)` | 确定安装程序类型列表 |
| `construct_parse(path, platform)` | 解析 construct.yaml（返回 info dict） |
| `construct_render(path, platform)` | 渲染 construct.yaml 为文本 |
| `construct_verify(info)` | Schema 校验 |

## 下一步

- [06-FCP依赖求解与包下载](./06-fcp-fetch-and-solve.md)：了解构建流程中最核心的求解下载管线
- [07-conda_interface防腐层](./07-conda-interface.md)：理解 constructor 如何隔离 conda 内部 API 的变化
