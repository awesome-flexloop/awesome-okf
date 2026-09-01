---
type: concept
title: "Preconda Payload 准备"
description: "preconda.py 如何准备安装程序的 payload 文件：urls列表、repodata缓存、conda-meta历史、.condarc配置、extra_files注入和frozen标记。"
tags: [preconda, payload, urls, repodata, conda-meta, condarc, frozen]
status: stable
stale_after: 2027-12-31
level: advanced
prerequisites: ["06-fcp-fetch-and-solve", "07-conda-interface"]
reading_time: 10
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-preconda
    resource: "constructor/preconda.py"
---

# Preconda Payload 准备

FCP 完成包下载后，`preconda.py` 负责将包的元数据和配置文件写入工作目录，这些文件将被打包进安装程序的 payload tarball，在安装时由 conda-standalone 使用。

## Payload 文件清单

preconda 写入的文件构成了安装程序的"自举数据"，使得目标机器上的 conda-standalone 可以完全离线工作：

```
workdir/
├── channelmirrors.yaml       # 通道镜像配置（mirrored_channels）
├── .condarc                   # conda 配置（write_condarc/condarc选项）
├── extra_files/               # 用户注入的额外文件
│   ├── script.sh
│   └── config.yaml
├── pkgs/                     # 包缓存目录
│   ├── cache/                 # 精简后的 repodata 缓存
│   │   ├── <hash>.json       # 每个通道的精简repodata
│   │   └── cache.json        # 缓存索引
│   ├── urls                   # 包下载URL列表（conda create --file格式）
│   ├── urls.conda-meta        # 额外环境的URL列表
│   └── <package-files>        # 下载的包文件（.tar.bz2/.conda）
├── conda-meta/               # base环境元数据
│   ├── history               # conda历史记录（含user_requested_specs）
│   ├── frozen                # CEP-22 frozen标记（freeze_base选项）
│   └── initial-state.explicit.txt  # 初始显式安装列表
├── envs/                     # 额外环境元数据
│   └── <env_name>/
│       ├── conda-meta/
│       │   ├── history
│       │   └── frozen
│       ├── channels.txt      # 该环境的通道列表
│       └── shortcuts.txt     # 该环境的快捷方式配置
└── licenses/                 # 许可证文件（build_outputs: licenses）
```

## 核心函数

### write_files(info, workspace)

Payload 准备的主入口函数，按以下顺序执行：

```python
def write_files(info, workspace):
    # 1. 写入 frozen 标记
    write_frozen(info.get("freeze_base"), join(workspace, "conda-meta"))

    # 2. 写入 .condarc
    write_condarc(info, workspace)

    # 3. 为每个环境写入文件
    for env_name, env_config in env_data:
        env_dir = base_env_dir if env_name == "base" else join(workspace, "envs", env_name)
        mkdir_p(join(env_dir, "conda-meta"))

        # 写入 channels.txt 和 shortcuts.txt
        write_channels_txt(info, env_dir, env_config)
        write_shortcuts_txt(info, env_dir, env_config)

        # 写入环境 frozen 标记
        write_frozen(env_config.get("freeze_env"), join(env_dir, "conda-meta"))

        # 写入 repodata 缓存
        write_index_cache(info, used_packages_repodata_records_tuples)

    # 4. 写入 conda-meta/history
    write_conda_meta(info, join(workspace, "conda-meta"), "base")

    # 5. 写入额外环境的 conda-meta/history
    for env_name, env_config in extra_envs_info.items():
        write_conda_meta(info, join(workspace, "envs", env_name, "conda-meta"), env_name)

    # 6. 写入 initial-state.explicit.txt
    write_initial_state_explicit_txt(info, ...)

    # 7. 复制 extra_files
    copy_extra_files(...)
```

### write_index_cache(info, dst_dir, used_packages)

为每个通道下载完整 repodata，然后调用 `conda_interface.write_repodata()` 精简并写入缓存目录。这是离线安装的核心——安装程序内置了"缩小版"的 repodata：

```python
def write_index_cache(info, dst_dir, used_packages):
    from .conda_interface import write_repodata, get_repodata

    for url, used_in_url in used_packages.items():
        full_repodata = get_repodata(url)
        write_repodata(cache_dir, url, full_repodata, used_in_url, info)
```

`used_packages` 是一个字典 `{channel_url: [package_filename, ...]}`，记录每个通道中实际使用的包。

### write_conda_meta(info, dst_dir, env_name)

写入 conda 环境的 `history` 文件。这个文件是 conda 的操作日志，constructor 写入以下内容：

```python
def write_conda_meta(info, dst_dir, env_name):
    # ==> cmd: <specs列表>
    # 更新时间戳
    # +python-3.14.6-h...
    # +pip-25.3-h...
    # ...
```

history 文件格式对 conda 很重要：
- `# ==> cmd:` 行记录创建环境的命令
- `# update specs:` 行记录 `user_requested_specs`
- `+dist-name` 行记录显式安装的包
- 这使得安装后用户执行 `conda install` 时，conda 能正确理解环境的初始状态

### write_frozen(freeze_info, dst_dir)

写入 CEP-22 规范的 `frozen` 标记文件：

```python
def write_frozen(freeze_info, dst_dir):
    if freeze_info:
        frozen_path = join(dst_dir, "frozen")
        frozen_data = {}
        if "conda" in freeze_info:
            frozen_data["conda"] = freeze_info["conda"]
        frozen_path.write_text(json.dumps(frozen_data))
```

frozen 文件存在时，conda 会拒绝在该环境中执行 install/update/remove 操作，保护 base 环境不被用户修改。

### write_initial_state_explicit_txt(info, dst_dir, urls)

写入 `initial-state.explicit.txt`，记录初始安装的包的精确 URL 和 MD5。这用于 `conda list --explicit` 和环境复制：

```
# This file may be used to create an environment using:
# $ conda create --name <env> --file <this file>
# platform: win-64
@EXPLICIT
https://repo.anaconda.com/pkgs/main/win-64/python-3.14.6-h...#<md5>
https://repo.anaconda.com/pkgs/main/win-64/pip-25.3-h...#<md5>
```

### write_channels_txt(info, dst_dir, env_config)

写入每个环境的 `channels.txt`，列出该环境使用的通道 URL。安装后 conda 使用这个文件来配置通道。

### write_shortcuts_txt(info, dst_dir, env_config)

写入 `shortcuts.txt`，列出哪些包应该创建开始菜单快捷方式（Windows）。空文件表示不创建任何快捷方式。

### write_condarc(info, dst_dir)

写入 `.condarc` 文件。优先级：
1. 如果 `condarc` 选项直接提供了内容（字符串或dict），使用该内容
2. 否则，如果 `write_condarc=True`，从 channels 和 conda_default_channels 生成
3. 如果有 `channels_remap`，使用 dest 通道
4. 如果有 `mirrored_channels`，包含镜像配置

### copy_extra_files(extra_files, workspace, ...)

将用户通过 `extra_files` 和 `temp_extra_files` 指定的文件复制到工作目录。支持两种格式：

```yaml
extra_files:
  - ./my-script.sh                              # 字符串：复制到根目录
  - {src: ./config.yaml, dst: etc/config.yaml}  # 字典：指定相对路径
```

## 关键数据来源

preconda 使用的数据来自 FCP 阶段写入 info 字典的字段：

| info 字段 | 来源模块 | 用于生成 |
|-----------|---------|---------|
| `_urls` | fcp.py | `pkgs/urls`、`initial-state.explicit.txt` |
| `_extra_envs_info[env]["_urls"]` | fcp.py | `pkgs/urls.conda-meta` |
| `_all_pkg_records` | fcp.py | repodata 精简（used_packages） |
| `channels` | construct.py | `channels.txt`、`.condarc` |
| `channels_remap` | construct.py | `.condarc`（使用dest通道） |
| `extra_files` | construct.py | `copy_extra_files()` |
| `write_condarc`/`condarc` | construct.py | `.condarc` |
| `menu_packages` | construct.py | `shortcuts.txt` |
| `user_requested_specs` | construct.py | `conda-meta/history` |
| `freeze_base`/`freeze_env` | construct.py | `conda-meta/frozen` |
| `mirrored_channels` | construct.py | `channelmirrors.yaml` |

## 与平台安装器的协作

preconda 完成 write_files 后，各平台模块（shar/winexe/osxpkg/briefcase）在工作目录基础上：
1. 复制 conda-standalone 二进制（`_conda` 或 `micromamba`）
2. 复制 pre/post 安装脚本
3. 渲染平台特定的安装脚本模板（header.sh/main.nsi.tmpl等）
4. 将整个工作目录打包为 tarball（shar）或编译为安装程序（winexe/osxpkg）

## 下一步

- [09-平台安装器实现](09-platform-installers.md)：了解各平台模块如何将 payload 打包为最终安装程序
- [12-构建输出产物](12-build-outputs.md)：了解 build_outputs 生成的 hash/licenses/lockfile 等附属产物
