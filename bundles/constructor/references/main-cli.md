---
type: reference
title: "CLI 入口点 (main.py)"
description: "constructor CLI 入口 main() 函数与 main_build() 核心构建流程源码分析。"
tags: [CLI, argparse, 入口点, main_build]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T00:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: constructor-main
    resource: "constructor/main.py"
    title: "constructor/main.py CLI入口"
---

# CLI 入口点 (main.py)

constructor 的 CLI 入口位于 `constructor/main.py`，采用 **argparse** 解析命令行参数，核心分发函数为 `main()`，实际构建逻辑在 `main_build()` 中。

## 核心流程

```python
# constructor/main.py 核心调用链
main()                           # argparse 入口
  ├─ args = p.parse_args()      # 解析命令行参数
  ├─ --clean → 清理缓存退出
  ├─ --render → construct_render() 并退出
  └─ main_build()               # 核心构建流程
       ├─ construct_parse()     # 解析 construct.yaml
       ├─ construct_verify()    # JSON Schema 校验
       ├─ get_installer_type()  # 确定安装程序类型
       ├─ identify_conda_exe()  # 识别 conda-standalone/micromamba
       ├─ validate_frozen_envs() # 验证 frozen 环境配置
       ├─ 路径规范化（license_file/welcome_image等）
       ├─ fcp_main()            # FCP：求解+下载包（F-001）
       └─ 循环 itypes:
            ├─ shar_create / osxpkg_create / winexe_create / briefcase_create / docker_create
            └─ process_build_outputs()
```

## `main()` 函数关键参数

| 参数 | 说明 |
|------|------|
| `dir_path` | construct.yaml 所在目录（位置参数，默认 CWD） |
| `--output-dir` | 输出目录，默认 CWD |
| `--cache-dir` | 包下载缓存，默认 `~/.conda/constructor` |
| `--platform` | 目标平台，如 `linux-64`, `win-64`, `osx-arm64` |
| `--conda-exe` | conda-standalone/micromamba 可执行文件路径 |
| `--installer-type` | 强制指定安装程序类型（sh/pkg/exe/msi） |
| `--dry-run` | 仅求解不生成安装程序 |
| `--render` | 解析并渲染 construct.yaml（含 selectors/Jinja2） |
| `--help-construct` | 输出 construct.yaml 可用配置键并退出 |
| `-V/--version` | 输出版本号 |

## `get_installer_type()` 平台-类型映射

```python
os_allowed = {
    "linux": (InstallerTypes.SH,),                                    # 仅 .sh
    "osx":   (InstallerTypes.SH, InstallerTypes.PKG),                # .sh + .pkg
    "win":   (InstallerTypes.EXE, InstallerTypes.MSI),               # .exe + .msi
}
# InstallerTypes.ALL     → 构建该平台所有类型
# InstallerTypes.DOCKER  → Linux: .sh + Dockerfile/image
```

## `_HelpConstructAction` 自定义 Action

`--help-construct` 通过自定义 `argparse.Action` 从 JSON Schema 动态读取所有可用配置键并格式化输出，同时列出可用 selectors（通过 `ns_platform()` 生成）。

**关键设计**：
- **两阶段 conda_exe 查找**：先检查 `--conda-exe` 参数，再找 `sys.prefix/standalone_conda/conda.exe` 默认路径，都不存在则报错提示安装 `conda-standalone` 包。
- **跨平台构建保护**：非原生平台构建必须显式指定 `--conda-exe`；macOS pkg 不能在非 macOS 上构建。
- **多安装程序类型合并**：当构建多种类型时（如 all），`process_build_outputs()` 会合并 info 字典中各类型不同的键值为列表。
