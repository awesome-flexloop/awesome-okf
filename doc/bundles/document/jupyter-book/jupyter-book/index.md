---
type: bundle
title: "Jupyter Book CLI"
okf_version: "0.2"
---

# Jupyter Book CLI

Jupyter Book v2 是基于 MyST 引擎的下一代科学文档出版工具，采用 **Python + TypeScript 双层架构**——Python 层管理 Node.js 环境，TypeScript 层委托 myst-cli 实现文档构建、多格式导出和预览。

## 架构核心

Jupyter Book v2 的本质是 **myst-cli 的白标发行版**：核心文档解析、转换、导出逻辑由 myst-cli 提供，Jupyter Book 通过环境变量定制品牌（名称、URL、默认配置），Python 层封装让用户无需感知 Node.js 的存在。

## 知识地图

```
Jupyter Book v2 CLI
├── 双层架构 ────────────────── Python 层（nodeenv）+ TypeScript 层（commander）
│   ├── Python 入口 ─────────── __main__.py: main() 函数、Node.js 查找/安装
│   └── TS CLI 命令 ─────────── commander 注册、clirun 执行器、命令委托
├── 与 myst-cli 的关系 ──────── 白标环境变量、代码复用、功能等价性
├── 模板系统 ────────────────── myst-templates 仓库、jtex 渲染
└── v1 迁移 ─────────────────── Sphinx→myst-cli 配置迁移、指令兼容
```

## 文档导航

### 入门示例
- [创建你的第一本书](examples/01-create-book.md) — 安装、初始化、预览、构建
- [构建与发布](examples/02-build-publish.md) — 多格式导出、GitHub Pages、出版级 PDF

### 核心概念（按学习路径）
1. [Jupyter Book v2 双层架构](concepts/00-v2-architecture.md) — Python+TS 双层、白标设计
2. [Python 入口与 nodeenv 管理](concepts/01-python-entry-nodeenv.md) — main() 流程、Node.js 查找策略
3. [TypeScript CLI 命令体系](concepts/02-ts-cli-commands.md) — commander、clirun、各子命令
4. [与 myst-cli 的关系](concepts/03-myst-cli-relationship.md) — 白标机制、功能等价、依赖关系
5. [模板系统](concepts/04-template-system.md) — myst-templates、template.yml、jtex 渲染
6. [从 v1 迁移](concepts/05-migration-from-v1.md) — _config.yml→myst.yml、Sphinx→myst-cli

### 信源参考
- [Python 入口与 nodeenv](references/python-entry.md) — __main__.py、nodeenv.py 源码
- [TS CLI 入口与命令委托](references/ts-cli-entry.md) — index.ts、clirun.ts、各命令文件

### 规格说明
- [事实清单](spec/facts.md) — 从源码提取的编号事实
- [架构洞察](spec/insights.md) — 核心架构洞察与知识地图

## 相关知识束
- [myst-exporters](../myst-exporters/index.md) — 底层多格式导出引擎

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
