---
type: reference
title: "SH 安装器创建模块 (shar.py)"
description: "Linux/macOS shell 自解压安装程序（.sh）的创建流程与模板机制源码分析。"
tags: [shar, shell-installer, header.sh, 自解压, tarball, Unix]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T00:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: constructor-shar
    resource: "constructor/shar.py"
    title: "constructor/shar.py Shell安装器模块"
  - id: constructor-header
    resource: "constructor/header.sh"
    title: "constructor/header.sh Shell安装脚本头部模板"
---

# SH 安装器创建模块 (shar.py)

shar.py 负责创建 Linux/macOS 平台的 **shell 自解压安装程序**（`.sh` 文件）。生成的 .sh 文件是一个纯 shell 脚本，头部包含安装逻辑，尾部以二进制追加 tarball 数据。

## 核心函数

### `create(info, verbose=False)`

SH 安装器创建入口，执行以下步骤：

1. **准备工作目录**（`TemporaryDirectory`）
2. **调用 `preconda.write_files(info, workdir)`** — 写入预配置文件（urls/repodata/conda-meta/.condarc等）
3. **复制 conda-standalone 二进制** — `utils.copy_conda_exe()` 复制 `_conda` 或 `micromamba`
4. **复制额外文件** — `preconda.copy_extra_files()` 处理 `extra_files` 和 `temp_extra_files`
5. **处理许可证文件** — 读取并编码 license_file 内容
6. **复制 pre/post 安装脚本** — pre_install / post_install（Unix下为.sh）
7. **渲染 header.sh 模板** — `jinja.render_template()` 将 info 字典注入 header.sh
8. **创建 tarball** — 将所有 payload 文件打包为 tar.bz2（使用 `_conda` 或系统 tar）
9. **拼接最终 .sh 文件** — header 脚本 + 二进制 tarball 数据
10. **设置可执行权限** — `os.chmod(outpath, 0o755)`
11. **签名处理** — macOS 下 codesign 签名（如有配置）

## header.sh 模板机制

`constructor/header.sh` 是一个 Jinja2 模板，在安装时由用户的 shell 执行。模板接收 `info` 字典中的所有键值作为模板变量，主要包含：

- 安装路径选择（交互模式 `-b` 批处理模式跳过交互）
- 平台兼容性检查（`__glibc`/`__osx` 虚拟包检测）
- 临时目录解压（`dd` + `tar` 提取二进制 payload）
- 调用 `_conda install` 或 `micromamba install` 执行实际安装
- `conda init` 初始化（classic/condabin 模式）
- 路径空格检查、权限检查
- 清理临时文件、错误处理
- 预定义环境变量：`PREFIX`、`INSTALLER_NAME`、`INSTALLER_VER`、`INSTALLER_PLAT`、`INSTALLER_TYPE=SH`

## 关键设计

- **二进制追加模式**：.sh 文件末尾以标记行（如 `@@END_HEADER@@`）分隔脚本头和二进制数据，安装时用 `dd`/`tail` 提取 tarball。
- **双二进制支持**：同时支持 `conda-standalone`（`_conda`）和 `micromamba`，通过 `info["_conda_exe_type"]` 判断。
- **shebang 尊重**：pre_install/post_install 脚本如有 shebang 行则按其指定的解释器执行，否则默认 `sh`。
- **批处理模式**（`-b`）：跳过交互式向导，自动接受所有默认值，适合 CI/CD 场景。
- **路径长度检查**：通过 `info["_max_relative_path_length"]` 提前计算，避免安装时路径溢出。
- **keep_pkgs 选项**：默认安装后删除 `pkgs/` 缓存，`-k` 选项保留。
