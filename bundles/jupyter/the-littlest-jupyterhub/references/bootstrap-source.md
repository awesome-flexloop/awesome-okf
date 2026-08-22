---
type: Reference
title: bootstrap.py 源码信源
description: bootstrap/bootstrap.py 模块公共 API 信源文档
tags: [reference, source, bootstrap, bootstrapping, installer-entry, api]
sources:
  - id: tljh-bootstrap
    title: bootstrap/bootstrap.py
---

# bootstrap.py 源码信源

> TLJH 安装引导脚本。仅依赖 Python 标准库，负责系统检查、基础工具安装、Hub 环境创建、TLJH 包安装，最后通过 os.execv 切换到 installer。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TLJH_INSTALL_PREFIX` | 安装根目录 | `/opt/tljh` |
| `TLJH_BOOTSTRAP_PIP_SPEC` | TLJH 包 pip 安装路径 | `the-littlest-jupyterhub=={version}` |
| `TLJH_BOOTSTRAP_DEV` | 开发模式（yes/no） | `no` |

## 关键设计

### 零依赖约束

bootstrap.py 仅使用 Python 标准库，不依赖任何第三方包。它包含 `run_subprocess` 函数的独立副本（与 installer.py 中的副本必须保持一致），因为在引导阶段 tljh 包尚未安装。

### Python 版本兼容

- Python ≥3.9：正常执行
- Python 3.8：能解析并打印清晰的升级提示错误
- Python <3.8：语法错误（使用 f-string 等新语法）

## 公共函数

### `ensure_host_system_can_install_tljh()`

系统兼容性检查，不通过则 sys.exit(1)：
1. 读取 `/etc/os-release`，确认 ID 为 ubuntu 或 debian
2. Ubuntu 检查 VERSION_ID ≥22.04
3. Debian 检查 VERSION_ID ≥11
4. Python 版本 ≥3.9
5. systemctl 可用（`shutil.which("systemctl")`）
6. 通过 `_miniforge_arch()` 验证架构支持

### `ProgressPageRequestHandler(http.server.BaseHTTPRequestHandler)`

安装进度页 HTTP 请求处理器：
- `GET /logs`：读取 INSTALL_PREFIX/installer.log 返回
- `GET /` → 302 重定向到 `/index.html`
- `GET /index.html`：返回安装进度 HTML 页面
- `GET /favicon.ico`：返回 favicon

### `_resolve_git_version(version) → str`

通过 `git ls-remote --tags` 解析版本号：
- `latest` → 匹配最新数字版本 tag（排除含 `-` 的预发布）
- 部分版本（如 `1.0`）→ 匹配 `v1.0.*` 中最新的 tag
- 分支名/commit hash → 原样返回

### `get_color_functions() → (color, do_print)`

终端颜色支持检测：TTY 时返回 ANSI 颜色函数，非 TTY 时返回无操作函数。

### `main()`

主入口函数：
1. 检测 Python ≥3.9，否则打印错误退出
2. 从环境变量读取 INSTALL_PREFIX 等设置
3. `ensure_host_system_can_install_tljh()`
4. 解析 CLI 参数：--show-progress-page、--version、其余透传
5. 如果指定 `--show-progress-page`，在端口80启动 HTTP 服务器（子进程）
6. `init_logging(INSTALL_PREFIX)`
7. 新安装时：
   - apt 更新
   - apt install python3/python3-venv/python3-pip/git/sudo（DEBIAN_FRONTEND=noninteractive）
   - 创建 Hub venv：`python3 -m venv {HUB_ENV_PREFIX}`
   - 升级 pip
   - pip install the-littlest-jupyterhub
8. 构造传递给 installer 的参数（透传未知参数、--progress-page-server-pid）
9. `os.execv(hub_env_python, ["-m", "tljh.installer"] + flags)`

## run_subprocess 副本

bootstrap.py 内嵌了 `run_subprocess` 函数副本，与 `tljh/utils.py` 中的实现保持一致。这是引导程序自包含约束的结果。
