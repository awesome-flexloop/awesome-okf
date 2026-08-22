---
type: concept
title: "与 myst-cli 的关系"
description: "Jupyter Book v2 作为 myst-cli 的白标发行版，理解两者的代码复用关系、白标机制和功能差异"
tags: [jupyter-book, myst-cli, white-label, relationship, delegation]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "ts/index.ts"
    facts: [F-011, F-012, F-013]
  - path: "ts/clirun.ts"
    facts: [F-014, F-015]
  - path: "ts/build.ts"
    facts: [F-016]
  - path: "ts/init.ts"
    facts: [F-017]
  - path: "ts/clean.ts"
    facts: [F-019]
  - path: "ts/site.ts"
    facts: [F-020]
---

# 与 myst-cli 的关系

Jupyter Book v2 和 myst-cli 的关系是理解 v2 架构的关键。简单来说：**Jupyter Book v2 是 myst-cli 的白标（white-label）发行版**。

## 什么是白标发行版

白标（white-label）是指一个产品以不同的品牌名重新打包发布。在软件领域，白标发行版通常：
- 复用上游产品的全部核心代码
- 更换品牌标识（名称、Logo、URL、帮助文本）
- 可能添加少量定制功能或默认配置
- 保持与上游的功能同步

Jupyter Book v2 对 myst-cli 做的就是这件事：核心逻辑 100% 来自 myst-cli，只做了品牌替换和少量 Jupyter 生态定制。

## 代码复用比例

从代码量角度看 Jupyter Book v2 的 TS 层：

| 文件 | 代码行数 | 功能 | 来源 |
|------|---------|------|------|
| ts/index.ts | ~50 行 | 白标设置 + 命令注册 | Jupyter Book 自定义 |
| ts/clirun.ts | ~40 行 | 统一执行器 | Jupyter Book 自定义 |
| ts/build.ts | ~5 行 | 委托到 myst-cli | 全部委托 |
| ts/clean.ts | ~5 行 | 委托到 myst-cli | 全部委托 |
| ts/site.ts | ~5 行 | 委托到 myst-cli | 全部委托 |
| ts/init.ts | ~30 行 | 委托 + 自定义选项 | 大部分委托 |
| ts/templates.ts | ~120 行 | 模板列表/下载 | 调用 myst-templates |
| ts/options.ts | ~20 行 | Jupyter 专属选项 | Jupyter Book 自定义 |
| ts/version.ts | ~1 行 | 版本号 | Jupyter Book 自定义 |
| **合计** | **~276 行** | | |

相比之下，myst-cli 有数千行代码实现核心的文档构建、转换、导出、预览功能。Jupyter Book v2 的 TS 层本质上是一个薄包装。

## 白标机制的实现

### 环境变量方式

Jupyter Book 选择了**环境变量**而非配置对象/继承/子类化来实现白标，原因：

1. **导入顺序**：白标设置必须在 import myst-cli 之前生效
2. **无侵入**：不需要修改 myst-cli 的 API 或引入额外的抽象层
3. **简单**：`process.env.XXX = value` 是最简单的全局配置
4. **跨进程**：环境变量会自动传递给 myst-cli 启动的子进程（如 latexmk、dev server）

myst-cli 在初始化时检查这些环境变量，如果存在就使用它们替代默认值：

```typescript
// myst-cli 内部（示意代码）
const READABLE_NAME = process.env.MYSTMD_READABLE_NAME ?? "MyST Markdown";
const BINARY_NAME = process.env.MYSTMD_BINARY_NAME ?? "myst";
const HOME_URL = process.env.MYSTMD_HOME_URL ?? "https://mystmd.org";
```

### Python 层也有环境变量标记

Python 层在启动 Node.js 时设置 `MYST_LANG=PYTHON`，这个环境变量告诉 myst-cli：
- 当前是从 Python 包启动的（而非 npm/npx）
- 升级建议应该提示 `pip install -U jupyter-book` 而非 `npm install -g mystmd`
- 某些路径解析使用 pip 包的位置而非 npm 全局位置

## 功能等价性

以下命令在功能上等价（产出相同的结果）：

| Jupyter Book v2 | myst-cli | 说明 |
|----------------|----------|------|
| `jupyter-book init` | `myst init` | 项目初始化 |
| `jupyter-book build` | `myst build` | 文档构建 |
| `jupyter-book start` | `myst start` | 开发服务器 |
| `jupyter-book clean` | `myst clean` | 清理构建 |
| `jupyter-book templates list` | `myst templates list` | 模板列表 |
| `jupyter-book templates download` | `myst templates download` | 模板下载 |

差异点：
1. **品牌**：所有输出信息显示 "Jupyter Book" 而非 "MyST"
2. **默认模板**：Jupyter Book 可能配置不同的默认模板
3. **安装方式**：pip vs npm
4. **额外选项**：init 命令有 `--gh-pages`/`--gh-curvenote` 选项

## 依赖关系图

```
jupyter-book (Python 包)
  │
  ├── Python 层（薄）
  │   └── __main__.py + nodeenv.py (~200 行)
  │
  └── TypeScript 层（薄）
      └── dist/jupyter-book.cjs (webpack/rollup bundle)
            │
            ├── 直接依赖：
            │   ├── myst-cli（核心构建逻辑）
            │   ├── myst-templates（模板管理）
            │   ├── myst-common（共享工具）
            │   ├── commander（CLI 框架）
            │   ├── chalk（终端颜色）
            │   └── core-js（polyfill）
            │
            └── 间接依赖（通过 myst-cli）：
                ├── myst-parser（MyST 解析）
                ├── myst-transforms（AST 转换）
                ├── myst-to-html/tex/docx/jats/md/typst（导出器）
                ├── jtex（模板引擎）
                ├── simple-validators（验证）
                ├── unified/remark/rehype（AST 生态）
                └── ...更多
```

## 为什么这样设计

### 对用户的好处

1. **零 Node.js 门槛**：用户通过 pip 安装，不需要知道 Node.js 存在
2. **Jupyter 品牌体验**：命令名、帮助文本、文档链接都指向 jupyterbook.org
3. **一个工具**：`pip install jupyter-book` 一条命令搞定
4. **快速获得新功能**：myst-cli 上游改进自动惠及 Jupyter Book 用户

### 对开发者的好处

1. **极小维护成本**：Jupyter Book v2 的核心代码不到 500 行（Python+TS）
2. **不重复造轮子**：文档解析/构建/导出是 hard problem，myst-cli 团队专门解决
3. **关注点分离**：Jupyter Book 可以专注于 Jupyter 生态集成（笔记本执行、Binder 等）
4. **快速迭代**：上游 myst-cli 更新后，Jupyter Book 只需更新依赖版本

### 对 MyST 生态的好处

1. **用户增长**：Jupyter Book 的庞大用户群为 MyST 生态带来用户
2. **反馈循环**：更多用户 → 更多 bug report → 更好的 myst-cli
3. **标准化**：Jupyter Book 使用 MyST 作为源格式，推动 MyST 成为学术写作标准

## 与 mystmd Python 包的关系

除了 jupyter-book，mystmd 自己也提供 Python 包：

- **jupyter-book**（Jupyter 官方）：白标 + Jupyter 生态定制
- **mystmd**（MyST 官方）：直接 Python 包装，无白标定制

两者都包含相同的 Python 层逻辑（nodeenv 管理 + 启动 TS bundle），区别只在于：
- 品牌环境变量不同
- 默认模板/配置可能不同
- PyPI 包名不同
- 文档链接不同

## 版本同步

Jupyter Book v2 的版本号与 myst-cli 的版本号不是一一对应的：
- Jupyter Book v2.x.y 可能依赖 myst-cli a.b.c
- myst-cli 的更新需要 Jupyter Book 团队测试后才会发布新版本
- 但由于 Jupyter Book 层极薄，版本同步成本很低

用户可以在两个工具间自由切换：用 jupyter-book 创建的项目可以用 myst 命令操作，反之亦然（因为底层是同一个 myst.yml 配置和相同的 _build 目录结构）。

## 相关概念

- [00-v2-architecture](/concepts/00-v2-architecture.md)：v2 双层架构
- [02-ts-cli-commands](/concepts/02-ts-cli-commands.md)：TS CLI 命令
- [04-template-system](/concepts/04-template-system.md)：模板系统
- [05-migration-from-v1](/concepts/05-migration-from-v1.md)：从 v1 迁移
