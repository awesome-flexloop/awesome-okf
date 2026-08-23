---
type: reference
title: "Windows EXE 安装器创建模块 (winexe.py)"
description: "Windows NSIS 安装程序（.exe）的创建流程、NSIS模板编译和自定义页面机制源码分析。"
tags: [winexe, NSIS, Windows, exe-installer, makensis, 安装程序]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T00:21:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: constructor-winexe
    resource: "constructor/winexe.py"
    title: "constructor/winexe.py Windows EXE安装器模块"
  - id: constructor-nsis
    resource: "constructor/nsis/main.nsi.tmpl"
    title: "constructor/nsis/main.nsi.tmpl NSIS主模板"
---

# Windows EXE 安装器创建模块 (winexe.py)

winexe.py 负责创建 Windows 平台的 **NSIS（Nullsoft Scriptable Install System）GUI 安装程序**（`.exe` 文件）。生成过程包括：图片处理、NSIS 脚本渲染、编译、签名。

## 核心函数

### `create(info, verbose=False)`

Windows EXE 安装器创建入口，执行以下步骤：

1. **查找 NSIS 编译器**（`makensis.exe`）— 从 conda 环境的 nsis 包或系统 PATH 查找
2. **图片处理** — 调用 `imaging.mknsis()` 生成/调整欢迎图(164x314)、头图(150x57)、图标(256x256)
3. **准备工作目录**（`TemporaryDirectory`）
4. **调用 `preconda.write_files(info, workdir)`** — 写入预配置文件
5. **复制 conda-standalone** — `utils.copy_conda_exe()` 复制 `_conda.exe`
6. **复制 extra_files / temp_extra_files** — 包括自定义 NSIS 页面（.nsi）、许可证等
7. **处理 pre_install / post_install / pre_uninstall 脚本**（.bat 文件）
8. **复制 VCRT 运行时**（如检测到需要）
9. **渲染 NSIS 模板** — 使用 Jinja2 将 `main.nsi.tmpl` 渲染为完整 `.nsi` 脚本
10. **自定义 NSIS 模板** — 如用户提供了 `nsis_template`，追加或替换
11. **执行 makensis 编译** — 子进程调用 `makensis.exe` 生成 .exe
12. **Windows 签名** — 调用 `signing.WindowsSignTool` 或 `AzureSignTool` 签名
13. **清理临时文件**

## NSIS 模板系统

模板文件位于 `constructor/nsis/` 目录：

| 文件 | 用途 |
|------|------|
| `main.nsi.tmpl` | 主安装脚本 Jinja2 模板（欢迎页→许可→安装路径→安装→完成→环境配置） |
| `Utils.nsh` | 工具宏（字符串处理、路径检测、UAC等） |
| `UAC.nsh` | UAC 权限提升宏（Vista+） |
| `OptionsDialog.nsh` | 高级选项对话框（添加PATH、注册Python等复选框） |
| `StandaloneUninstallerOptions.nsh` | 卸载程序选项（删除配置/缓存/用户数据） |
| `_nsis.py` | NSIS 辅助 Python 脚本（在构建时执行） |
| `_system_path.py` | Windows PATH 环境变量操作（添加/移除） |

模板变量通过 `info` 字典传递，包括安装路径选项、快捷方式配置、初始化选项等。

## 自定义页面机制

用户可通过 `welcome_file`（.nsi）、`conclusion_file`（.nsi）、`post_install_pages`（.nsi列表）插入自定义 NSIS 页面：
- `welcome_file`：在许可页面前插入（需为nsi类型）
- `post_install_pages`：在安装完成后、完成页面前插入多个自定义页面
- `conclusion_file`：替换默认完成页面

## 关键设计

- **Just Me / All Users 双模式**：支持当前用户安装（`%USERPROFILE%`）和所有用户安装（`%ALLUSERSPROFILE%`），通过 UAC 提升权限。
- **PATH 管理**：通过 `_system_path.py` 安全地添加/移除 `$INSTDIR`、`$INSTDIR/Scripts`、`$INSTDIR/Library/bin` 到系统 PATH。
- **Python 注册**：`register_python` 选项支持将安装的 Python 注册为系统默认（写入注册表）。
- **conda-standalone 卸载**：`uninstall_with_conda_exe` 选项使用 `_conda.exe` 执行卸载（需要 conda >=24.11.0），支持移除配置文件、用户数据、缓存。
- **签名集成**：支持 `signtool.exe`（Windows SDK）和 `azuresigntool`（Azure Key Vault）两种签名工具。
- **快捷方式**：通过 `menu_packages` 控制哪些包创建开始菜单快捷方式；空列表完全禁用快捷方式。
