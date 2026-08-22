---
type: concept
title: "Jupyter Book v2 双层架构"
description: "Jupyter Book v2 的 Python + TypeScript 双层架构设计：Python 层管理 Node.js 环境，TypeScript 层委托 myst-cli 实现核心 CLI 逻辑"
tags: [jupyter-book, architecture, python, typescript, myst-cli, white-label]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "py/jupyter_book/__main__.py"
    facts: [F-001, F-002, F-003, F-004]
  - path: "py/jupyter_book/nodeenv.py"
    facts: [F-005, F-006, F-007]
  - path: "ts/index.ts"
    facts: [F-011, F-012, F-013]
  - path: "ts/clirun.ts"
    facts: [F-014, F-015]
---

# Jupyter Book v2 双层架构

Jupyter Book v2 是对 v1 的彻底重构，采用 **Python + TypeScript 双层架构**。Python 层负责 Node.js 运行时环境管理和进程启动，TypeScript 层负责实际的 CLI 命令逻辑（通过委托 myst-cli 实现）。

## 为什么采用双层架构

Jupyter Book v1 是纯 Python 实现，但 v2 转向 Python + TypeScript 双层，核心原因：

1. **复用 MyST 生态**：MyST 工具链（myst-parser、myst-transforms、myst-exporters 等）全部是 TypeScript 实现，在 JS 生态中维护最活跃
2. **性能**：TypeScript 上的 unified 生态（micromark、mdast、hast、rehype）处理文档解析和转换非常快
3. **统一工具链**：myst-cli 已经实现了完整的文档构建/导出/预览能力，Jupyter Book v2 本质上是 myst-cli 的白标发行版
4. **Python 用户体验**：用户仍然通过 `pip install jupyter-book` 安装、`jupyter-book` 命令使用，不需要感知 Node.js 的存在
5. **跨平台**：nodeenv 保证各平台（Windows/macOS/Linux）都有可用的 Node.js 运行时

## 架构概览

```
用户命令行
    │
    ▼
jupyter-book (Python CLI 入口)
    │
    ├── py/jupyter_book/__main__.py     # Python 入口 main()
    │       │
    │       ├── nodeenv.py              # Node.js 环境查找/安装
    │       │     ├── 查找系统 Node.js (shutil.which)
    │       │     ├── 版本检查 (>=18.x, 推荐 20/22)
    │       │     └── 如不满足，自动创建 nodeenv 环境
    │       │
    │       ├── 定位 dist/jupyter-book.cjs (编译后的 TS bundle)
    │       │
    │       └── subprocess.run / os.execve 启动 Node.js
    │             │ 设置 MYST_LANG=PYTHON 环境变量
    │             │
    ▼             ▼
            Node.js 进程
              │
              ├── ts/index.ts           # TS CLI 入口
              │       │
              │       ├── 设置白标环境变量（MYSTMD_READABLE_NAME 等）
              │       │
              │       ├── 创建 commander Program
              │       │
              │       └── 注册命令（init/build/start/clean/templates）
              │             │
              │             └── ts/clirun.ts  # 统一执行器
              │                   │
              │                   ├── chalkLogger 创建
              │                   ├── Session 创建
              │                   └── 委托到 myst-cli 函数
              │                         │
              ▼                         ▼
                                  myst-cli 核心逻辑
                                    ├── init      → 项目初始化
                                    ├── build     → 文档构建/导出
                                    ├── start     → 开发服务器
                                    ├── clean     → 清理构建产物
                                    └── templates → 模板管理
                                          │
                                          ▼
                                    myst-exporters（多格式导出）
                                    myst-transforms（文档转换）
                                    myst-templates（模板系统）
```

## Python 层职责

Python 层非常薄（约 100 行代码），只做三件事：

1. **Node.js 环境管理**（nodeenv.py）：
   - 查找系统已安装的 Node.js
   - 检查版本（18.x、20.x、22.x+）
   - 如果系统没有合适版本，自动通过 nodeenv 包创建隔离环境
   - 支持 `JB_ALLOW_NODEENV` 环境变量跳过交互确认

2. **JS bundle 定位**：
   - 找到 `py/jupyter_book/dist/jupyter-book.cjs`（TypeScript 编译后的单文件 bundle）
   - 这个 bundle 在 pip 安装时已经打包好，不需要用户单独安装

3. **进程启动**：
   - Windows：`subprocess.run([node_path, js_path, ...args], env)`
   - Unix：`os.execve(node_path, [node_name, js_path, ...args], env)`（替换当前进程，更高效）
   - 设置 `MYST_LANG=PYTHON` 环境变量告诉 TS 层是从 Python 调用的

Python 层不包含任何文档解析、构建、导出逻辑——全部委托给 TypeScript 层。

## TypeScript 层职责

TypeScript 层也很薄（主要是配置和委托），核心是白标（white-label）定制：

### 白标环境变量

在 commander 解析命令行参数之前，TS 层设置一系列环境变量来定制 myst-cli 的行为：

```typescript
process.env.MYSTMD_READABLE_NAME = "Jupyter Book";   // 用户可读名称
process.env.MYSTMD_BINARY_NAME = "jupyter book";     // 二进制名称
process.env.MYSTMD_HOME_URL = "https://jupyterbook.org/stable"; // 官网链接
process.env.MYSTMD_NPM_BINARY_NAME = "jupyter-book"; // npm 包名
process.env.MYSTMD_NPM_PACKAGE_NAME = "jupyter-book"; // npm 包全名
```

这些环境变量让 myst-cli 在帮助信息、升级提示、错误消息中显示 "Jupyter Book" 而非 "mystmd"，实现白标效果。

### 命令注册与委托

TS 层使用 commander 创建 CLI 程序，注册子命令。但每个命令的实际实现都委托给从 myst-cli 导入的函数：

| TS 命令文件 | 委托目标（myst-cli） | 说明 |
|-----------|-------------------|------|
| ts/build.ts | `build` (from myst-cli) | 1行委托 |
| ts/clean.ts | `clean` (from myst-cli) | 1行委托 |
| ts/site.ts | `startServer` (from myst-cli) | 1行委托（start 命令）|
| ts/init.ts | `init` (from myst-cli) | 少量自定义选项，委托 |
| ts/templates.ts | listPublicTemplates 等 (from myst-templates) | 最复杂，有自定义列表/下载逻辑 |

### clirun 统一执行器

每个命令的 action 都通过 `clirun(sessionClass, func, program)` 包装，提供统一的：
- 日志初始化（chalkLogger，支持 --debug）
- Session 创建和 reload
- Node.js 版本检查（logVersions + checkNodeVersion）
- 错误捕获和友好的错误消息
- 升级通知（session.showUpgradeNotice）

## 与 v1 的关系

Jupyter Book v1（`jupyter-book` PyPI 包）是基于 Sphinx 的纯 Python 实现：
- 使用 Sphinx 作为构建引擎
- 使用 MyST-Parser（Python 版）解析 MyST Markdown
- 自定义 Sphinx 扩展实现各种功能
- CLI 通过 click 实现

Jupyter Book v2：
- 抛弃 Sphinx，直接使用 myst-cli 作为构建引擎
- 解析器使用 myst-parser（TypeScript 版，即 micromark 扩展）
- 导出使用 myst-exporters
- Python 层仅作为 Node.js 环境管理器
- CLI 通过 commander 实现（TS 层）

v2 的代码量远小于 v1，因为核心能力由 myst-cli 提供。这也意味着 Jupyter Book v2 和 mystmd 命令行工具功能等价，只是品牌和默认配置不同。

## 关键设计决策

### 为什么不直接用 mystmd？

用户可以直接使用 `npx mystmd` 或 `pip install mystmd`（mystmd 也有 Python 入口），Jupyter Book v2 存在的意义是：
1. **品牌延续**：Jupyter Book 用户群体庞大，保持 pip 包名和命令名
2. **Jupyter 生态集成**：与 Jupyter Notebook/Lab 生态更紧密
3. **默认配置**：为 Jupyter 笔记本用户提供更好的默认值
4. **模板预设**：默认使用适合 Jupyter Book 的模板
5. **迁移路径**：为 v1 用户提供平滑迁移到 MyST 引擎的路径

### 为什么使用 nodeenv 而非捆绑 Node.js？

- **包体积**：捆绑 Node.js 会让 pip 包体积增大到 50MB+
- **灵活性**：系统已有 Node.js 时复用，不重复安装
- **隔离性**：nodeenv 创建独立环境，不污染系统 Node.js
- **版本管理**：固定使用经过测试的 Node.js 版本（NODEENV_VERSION）

### 为什么用 CJS bundle？

TypeScript 编译为单个 CommonJS 文件（`dist/jupyter-book.cjs`），原因：
- 不需要 node_modules 依赖（全部打包进 bundle）
- 启动速度快（不需要解析 ESM 模块依赖）
- pip 安装时只需复制一个文件
- 兼容性好（CJS 在所有 Node.js 版本上都支持）

## 相关概念

- [01-python-entry-nodeenv](/concepts/01-python-entry-nodeenv.md)：Python 入口与 nodeenv 详解
- [02-ts-cli-commands](/concepts/02-ts-cli-commands.md)：TS CLI 命令详解
- [03-myst-cli-relationship](/concepts/03-myst-cli-relationship.md)：与 myst-cli 的关系
- [04-template-system](/concepts/04-template-system.md)：模板系统
- [05-migration-from-v1](/concepts/05-migration-from-v1.md)：从 v1 迁移
