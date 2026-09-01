---
type: concept
title: "平台安装器实现"
description: "shar.py（Shell .sh）、winexe.py（NSIS .exe）、osxpkg.py（pkgbuild .pkg）和briefcase.py（MSI）四个平台安装器模块的统一接口和平台特定实现。"
tags: [平台安装器, shar, winexe, osxpkg, briefcase, create, NSIS, pkgbuild]
status: stable
stale_after: 2027-12-31
level: advanced
prerequisites: ["02-architecture-overview", "08-preconda-payload"]
reading_time: 12
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-shar
    resource: "constructor/shar.py"
  - id: constructor-winexe
    resource: "constructor/winexe.py"
  - id: constructor-osxpkg
    resource: "constructor/osxpkg.py"
  - id: constructor-briefcase
    resource: "constructor/briefcase.py"
---

# 平台安装器实现

constructor 为每个支持的安装程序类型提供一个独立模块，所有模块实现统一的 `create(info, verbose=False)` 接口。这种**策略模式**设计使得新增平台类型非常简单。

## 统一接口

所有平台安装器模块导出同一个入口函数：

```python
def create(info: dict, verbose: bool = False) -> None:
    """根据 info 字典创建平台特定的安装程序。"""
```

`main_build()` 中的分发逻辑（延迟导入）：

```python
# 按 installer_type 延迟导入并调用
if "sh" in itypes:
    from .shar import create as shar_create
    shar_create(info, verbose=verbose)
if "pkg" in itypes:
    from .osxpkg import create as osxpkg_create
    osxpkg_create(info, verbose=verbose)
if "exe" in itypes:
    from .winexe import create as winexe_create
    winexe_create(info, verbose=verbose)
if "msi" in itypes:
    from .briefcase import create as briefcase_create
    briefcase_create(info, verbose=verbose)
```

延迟导入的好处：在 Windows 上构建不需要 macOS 的 pkgbuild 相关依赖，在 Linux 上构建不需要 NSIS。

## shar.py — Shell 自解压安装程序（Linux/macOS）

### 构建流程

```python
def create(info, verbose=False):
    with TemporaryDirectory() as workdir:
        preconda.write_files(info, workdir)       # 1. 写入payload文件
        utils.copy_conda_exe(info, workdir, "_conda")  # 2. 复制conda-standalone
        preconda.copy_extra_files(info, workdir)  # 3. 复制extra_files
        # 4. 处理许可证、pre/post脚本
        # 5. 渲染 header.sh 模板（Jinja2）
        # 6. 创建 tarball（使用 _conda 或系统 tar）
        # 7. 拼接 header + tarball → .sh 文件
        # 8. chmod 755
```

### 关键技术：二进制追加

.sh 文件是一个纯文本 shell 脚本，二进制数据附加在脚本末尾：

```
#!/bin/bash
...（shell 脚本代码，来自 header.sh 模板）...
echo "Installing..."
dd if="$THIS_FILE" bs=<skip> skip=1 | tar xj -C "$PREFIX/pkgs"
...
exit 0
@@BINARY_MARKER@@
<BINARY TARBALL DATA HERE>
```

安装时，脚本使用 `dd` 或 `tail` 跳过脚本头部，提取 tarball 数据：
- `tail -n +<line_number> "$0" | tar xjf - -C "$PREFIX/pkgs"`
- 或 `dd if="$0" bs=<offset> skip=1 | tar ...`

### header.sh 模板

[`constructor/header.sh`](../references/shar-installer.md) 是一个 Jinja2 模板（约2000行），提供：
- 命令行参数解析（-b、-p、-u、-k、-h）
- 平台兼容性检查（`__glibc`/`__osx` 虚拟包检测）
- 磁盘空间检查（使用 `_approx_pkgs_size`）
- 路径长度检查（使用 `_max_relative_path_length`）
- 临时目录解压和包安装（调用 `_conda install` 或 `micromamba install`）
- conda init（classic/condabin 模式）
- pre/post 脚本执行
- 错误处理和清理

### 双二进制支持

shar 同时支持 conda-standalone 和 micromamba：

```python
if info["_conda_exe_type"] == StandaloneExe.CONDA:
    exe_name = "_conda"
else:  # StandaloneExe.MAMBA
    exe_name = "micromamba"
```

header.sh 模板通过 `INSTALLER_TYPE` 和 conda 命令差异来适配两种二进制。

## winexe.py — NSIS GUI 安装程序（Windows）

### 构建流程

```python
def create(info, verbose=False):
    # 1. 查找 makensis.exe（NSIS编译器）
    # 2. 调用 imaging.mknsis() 处理图片
    with TemporaryDirectory() as workdir:
        preconda.write_files(info, workdir)
        utils.copy_conda_exe(info, workdir, "_conda.exe")
        preconda.copy_extra_files(info, workdir)
        # 3. 复制 .bat 脚本（pre_install/post_install/pre_uninstall）
        # 4. 复制 VCRT 运行时（如需要）
        # 5. 渲染 main.nsi.tmpl → main.nsi
        # 6. 处理自定义 NSIS 页面（welcome_file/post_install_pages）
        # 7. 执行 makensis.exe 编译 .nsi → .exe
        # 8. 代码签名（signtool/azuresigntool）
```

### NSIS 模板系统

模板位于 `constructor/nsis/` 目录：

| 文件 | 用途 |
|------|------|
| `main.nsi.tmpl` | 主安装脚本 Jinja2 模板（约3000行NSIS脚本） |
| `Utils.nsh` | 工具宏（字符串、路径、注册表） |
| `UAC.nsh` | UAC 权限提升宏 |
| `OptionsDialog.nsh` | 高级选项对话框（PATH/Python注册/快捷方式复选框） |
| `StandaloneUninstallerOptions.nsh` | 卸载选项（删除配置/缓存/用户数据） |
| `_nsis.py` | Python 辅助脚本 |
| `_system_path.py` | Windows PATH 环境变量操作 |

main.nsi.tmpl 定义的安装流程：
1. **欢迎页面** → 许可协议页面 → 安装类型选择（Just Me/All Users）
2. **安装路径页面** → 高级选项页面（PATH/注册Python/快捷方式/清理缓存）
3. **安装进度页面**（调用 `_conda.exe install`）
4. **完成页面**（conclusion_file 自定义内容）
5. **卸载程序**：生成 `Uninstall-<Name>.exe`，支持控制面板卸载

### 双模式安装

- **Just Me**：安装到 `%USERPROFILE%\<name>`（或 `%LOCALAPPDATA%` 域用户），不需要管理员权限
- **All Users**：安装到 `%ALLUSERSPROFILE%\<name>`，需要 UAC 提升，PATH 写入系统环境变量

### 自定义 NSIS 页面

用户可通过 `.nsi` 文件插入自定义页面：

```yaml
welcome_file: pages/custom_welcome.nsi    # 许可页面前插入
post_install_pages:                        # 安装完成后插入
  - pages/config_page.nsi
conclusion_file: pages/custom_finish.nsi   # 替换完成页面
```

## osxpkg.py — macOS pkgbuild 安装程序

### 构建流程

```python
def create(info, verbose=False):
    with TemporaryDirectory() as workdir:
        preconda.write_files(info, workdir)
        utils.copy_conda_exe(info, workdir, "conda.exe")
        preconda.copy_extra_files(info, workdir)
        # 1. 处理 macOS 特定资源（welcome/readme/conclusion/许可证/图片）
        # 2. 处理 pre/post 安装脚本（bash）
        # 3. 调用 imaging.mkosx() 处理背景图
        # 4. 使用 pkgbuild 创建组件包
        # 5. 使用 productbuild 合成产品安装包（含 Distribution XML）
        # 6. codesign 签名（如有 signing_identity_name）
        # 7. 公证签名（如有 notarization_identity_name）
```

### macOS 安装域

通过 `pkg_domains` 配置安装位置：

| 域 | 默认 | 路径 |
|---|------|------|
| `enable_currentUserHome` | ✅ | `~/<name>`（或 `~/<default_location_pkg>/<name>`） |
| `enable_anywhere` | ✅ | 用户选择的卷上 `<name>` |
| `enable_localSystem` | ❌ | `/<name>`（需要 root） |

### 资源文件

osxpkg 模块使用 `constructor/osxpkg/` 目录中的模板：

| 文件 | 用途 |
|------|------|
| `preinstall` | pre-install 脚本模板（bash） |
| `postinstall` | post-install 脚本模板（bash） |
| `Distribution` | productbuild Distribution XML 模板（控制安装向导界面） |
| `Licenses.rtf` | 默认许可证 RTF 模板 |
| `Uninstall_commands` | 卸载命令 |
| `com.constructor.constructor.plist` | 包属性列表 |

### Distribution XML

`Distribution` 文件定义 macOS 安装向导的页面布局和选项，包括：
- 安装域选择（个人/所有用户/自定义卷）
- 欢迎/自述/许可/完成页面的自定义内容
- 安装体积计算
- 系统要求（OS X 最低版本）

## briefcase.py — Windows MSI 安装程序（实验性）

### 构建流程

```python
def create(info, verbose=False):
    # 使用 Briefcase + WiX Toolset 构建 MSI
    with TemporaryDirectory() as workdir:
        preconda.write_files(info, workdir)
        utils.copy_conda_exe(info, workdir, "_conda.exe")
        # 1. 准备 Payload 类（打包所有文件）
        # 2. 调用 briefcase 命令行生成 WiX 项目
        # 3. WiX 编译为 .msi
```

`briefcase.py` 定义了 `Payload` 类来管理所有要打包的文件，使用 briefcase 的 WiX backend 生成 Windows Installer 数据库。

> ⚠️ MSI 支持是实验性的，不如 NSIS 成熟。不支持自定义 NSIS 模板，功能相对有限。

## 平台模块共性与差异

| 方面 | shar (.sh) | winexe (.exe) | osxpkg (.pkg) | briefcase (.msi) |
|------|-----------|---------------|---------------|-----------------|
| 安装模式 | CLI 交互/批处理 | GUI 向导 | GUI 向导 | GUI 向导 |
| 脚本类型 | shell | .bat | bash | .bat |
| 自定义页面 | ❌ | ✅ .nsi | ✅ .plugin/.html | ❌ |
| 签名 | ❌ | ✅ signtool/azuresigntool | ✅ codesign | ✅ |
| UAC/权限 | 不需要 | 自动UAC | 需要root安装域 | Windows Installer |
| 静默安装 | `-b` | `/S` | `installer -pkg` | `msiexec /qn` |
| 卸载 | 手动删除/`rm -rf` | 控制面板/Uninstall.exe | 手动/Uninstall_commands | 控制面板 |
| 编译器 | 无（纯shell） | makensis (NSIS) | pkgbuild+productbuild | briefcase+WiX |
| 成熟度 | ✅ 稳定 | ✅ 稳定 | ✅ 稳定 | ⚠️ 实验性 |

## 新增平台类型的步骤

如果要添加新的安装程序类型（如 `.deb`、`.rpm`、AppImage），需要：

1. 创建 `constructor/xxx.py` 模块
2. 实现 `create(info, verbose=False)` 函数
3. 在 `_schema.py` 的 `InstallerTypes` 枚举中添加新类型
4. 在 `main.py` 的 `os_allowed` 映射中注册平台支持
5. 在 `main_build()` 中添加延迟导入和调用
6. 更新 `build_outputs.py` 中 `OUTPUT_HANDLERS` 如有需要
7. 在 `constructor/header.sh` 或新增模板中添加 `INSTALLER_TYPE=XXX` 支持

这就是策略模式的优势——改动局限于明确的扩展点。

## 下一步

- [10-Docker 构建支持](10-docker-build.md)：了解第五种安装类型 Docker
- [11-多环境与通道配置](11-multi-env-and-channels.md)：了解 extra_envs 和 channels_remap 的深入用法
