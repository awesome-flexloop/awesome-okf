---
type: reference
title: "Python 入口与 nodeenv 管理"
description: "Jupyter Book v2 Python 层源码：__main__.py 入口函数、nodeenv.py Node.js 环境管理"
tags: [jupyter-book, reference, python, nodeenv]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "py/jupyter_book/__main__.py"
    facts: [F-001, F-002, F-003, F-004]
  - path: "py/jupyter_book/nodeenv.py"
    facts: [F-005, F-006, F-007, F-008, F-009, F-010]
---

# Python 入口与 nodeenv 管理

本文档登记 Jupyter Book v2 Python 层的源码，包括 `__main__.py` 入口和 `nodeenv.py` Node.js 环境管理模块。

## 包结构

```
py/jupyter_book/
├── __init__.py    # 空文件
├── __main__.py    # Python 入口，main() 函数
└── nodeenv.py     # Node.js 环境查找/安装/管理
```

编译后的 JS 捆绑包位于 `py/jupyter_book/dist/jupyter-book.cjs`（由 TypeScript 编译产生）。

## __main__.py

- **版本**：`__version__ = "2.1.6"`，`NODEENV_VERSION = "22.17.0"`
- **核心函数**：`main()`
  - Node.js 查找/安装 → 构建环境变量 → 定位 JS 文件 → 子进程/execve 启动
- **Node 版本要求**：18.x、20.x、22.x+（由 `test_node_version()` 检查）
- **平台适配**：
  - Windows：`subprocess.run([node_path, js_path, ...args], env=jb_env)`
  - 非 Windows：`os.execve(node_path, [node_path.name, js_path, ...args], jb_env)`
- **环境变量**：设置 `MYST_LANG=PYTHON`
- **错误处理**：NodeEnvCreationError 和 PermissionDeniedError 转为用户友好的 SystemExit 消息

## nodeenv.py

- **异常类**：PermissionDeniedError、NodeEnvCreationError、NodeVersionError
- **核心函数**：

| 函数 | 说明 |
|------|------|
| `find_installed_node()` | 使用 `shutil.which` 查找系统 node |
| `get_triple_node_version(node_path)` | 执行 `node -v`，正则解析版本号 |
| `find_nodeenv_path(version)` | 使用 platformdirs 获取 nodeenv 用户数据目录 |
| `ask_to_install_node(path)` | 询问用户是否安装（支持 JB_ALLOW_NODEENV 环境变量跳过交互） |
| `create_nodeenv(env_path, version)` | 调用 `python -m nodeenv --node={version} --prebuilt --clean-src` |
| `find_valid_node(binary_path, nodeenv_version, test_version)` | 两阶段查找：系统 Node → nodeenv Node |

- **查找策略**（`find_valid_node`）：
  1. 查找系统已安装 node → 检查版本 → 满足则返回
  2. 系统 node 不可用/版本不符 → 检查 nodeenv 路径是否存在
  3. nodeenv 不存在 → 提示安装 → 创建 nodeenv 环境
  4. 返回 node 可执行文件路径和更新后的 PATH
- **nodeenv 可执行路径**：
  - Windows：`{env_path}/Scripts/node.exe`
  - 非 Windows：`{env_path}/bin/node`

## 相关概念

- [01-python-entry-nodeenv](../concepts/01-python-entry-nodeenv.md)：Python 入口与 nodeenv 详解
- [00-v2-architecture](../concepts/00-v2-architecture.md)：Jupyter Book v2 双层架构
