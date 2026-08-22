---
type: Concept
title: 架构总览
description: jupyterlab-translate采用CLI→API→Core三层洋葱架构，支持独立扩展包和集中语言包双模式分发，从Python/TypeScript/Schema三源提取字符串
tags: [architecture, three-layer, onion, dual-mode, extraction-sources, data-flow]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: api-source
    resource: /references/api-source.md
    title: API层源码映射
  - id: utils-source
    resource: /references/utils-source.md
    title: 核心工具源码映射
  - id: cli-source
    resource: /references/cli-source.md
    title: CLI源码映射
---

# 架构总览

jupyterlab-translate 采用**三层洋葱架构**，从外到内分别是CLI层、API编排层和核心功能层。各层职责清晰分离：外层负责参数解析和用户交互，中间层负责流程编排，内层负责具体功能实现。

## 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  CLI层 (cli.py)                                              │
│  Click命令定义、参数解析、输出信息                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  API层 (api.py)                                          ││
│  │  参数校验、路径计算、流程编排、高层API                        ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │  核心层 (utils.py / converters.py / finder.py)       │││
│  │  │  字符串提取、目录操作、格式转换、运行时发现               │││
│  │  │  plugin.py (Hatch Hook)                              │││
│  │  │  contributors.py (Crowdin集成)                        │││
│  │  └─────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### CLI层（cli.py）

CLI层是最外层，使用Click框架定义命令行接口。它的职责非常单一：
- 定义7个子命令（extract, update, compile, extract-pack, update-pack, compile-pack, update-contributors）
- 声明命令参数（位置参数和选项）
- 解析命令行输入
- 调用API层对应函数
- 输出用户友好的提示信息

CLI层不包含任何业务逻辑，所有实际工作都委托给API层完成。

### API层（api.py）

API层是中间编排层，负责：
- **参数校验**：调用 `check_locales()` 验证locale有效性
- **名称规范化**：通过 `normalize_project()` 将项目名统一为小写+下划线格式
- **路径计算**：根据模式（独立包/语言包）计算不同的输出目录路径
- **流程串联**：按顺序调用核心层的函数完成完整工作流
- **文件移动**：在语言包模式下，将编译产物移动到正确的目录位置

API层的6个主要函数对应CLI的6个翻译命令，外加 `compile_po_file()` 供Hatch Hook调用。

### 核心层

核心层包含实际执行功能的模块：

| 模块 | 职责 |
|------|------|
| `utils.py` | 核心工具函数：字符串提取（三源）、POT/PO/MO文件操作、版本获取、locale验证 |
| `converters.py` | PO→Jed JSON格式转换 |
| `finder.py` | 运行时通过entry points发现已安装的语言包和扩展locale数据 |
| `plugin.py` | Hatch Build Hook实现，构建时自动编译翻译 |
| `contributors.py` | Crowdin API集成，下载和格式化贡献者列表 |
| `constants.py` | 常量定义和gettext-extract JS配置 |

## 三源字符串提取

字符串提取是工具的核心能力，来自三个独立的来源：

```
源码文件
├── Python (*.py)     → pybabel extract    → polib处理
├── TypeScript (*.ts) → gettext-extract    → (Node.js/ncc打包)
├── TSX (*.tsx)       → gettext-extract    → (Node.js/ncc打包)
└── JSON Schema (*.json) → 自定义递归遍历  → 正则选择器匹配
```

三路提取的结果在 `create_catalog()` 中合并，经 `fix_location()` 修正路径、`remove_duplicates()` 按(msgctxt, msgid, msgid_plural)三元组去重后，生成最终的POT模板文件。

## 双格式编译输出

翻译编译同时产出两种格式，分别服务于不同的运行时：

```
PO文件 (*.po)
├── pybabel compile / polib.save_as_mofile() → MO文件 (*.mo)  → Python后端/gettext
└── convert_catalog_to_json()                → JSON文件 (*.json) → JupyterLab前端/Jed
```

- **MO文件**：gettext标准二进制格式，被Python的gettext模块加载
- **JSON文件**：Jed格式，被JupyterLab前端的i18n系统加载

## 数据流

以独立扩展包的完整工作流为例，数据流动如下：

```
extract:  源码文件 → extract_strings/extract_tsx_strings/extract_schema_strings
          → fix_location → remove_duplicates → POT文件 (*.pot)

update:   POT文件 → pybabel init/update → PO文件 (*.po)（人工翻译填入msgstr）

compile:  PO文件 → pybabel compile → MO文件 (*.mo)
                  → convert_catalog_to_json → JSON文件 (*.json)
```

## 双模式分发

工具支持两种翻译分发模式，它们共享核心提取和编译逻辑，区别仅在目录结构：

| 特性 | 独立扩展包模式 | 集中语言包模式 |
|------|--------------|--------------|
| CLI命令 | extract/update/compile | extract-pack/update-pack/compile-pack |
| 输出位置 | 扩展包自身的locale/目录 | 语言包仓库的language-packs/目录 |
| 包结构 | 扩展包内含翻译文件 | 独立的jupyterlab-language-pack-xx包 |
| Hatch Hook | 可选配置 | 标准配置 |

## 相关概念

- [JupyterLab Translate 简介](/concepts/00-introduction.md)
- [快速开始](/concepts/01-getting-started.md)
- [CLI命令参考](/concepts/03-cli-commands.md)
- [字符串提取流水线](/concepts/04-extraction-pipeline.md)
- [翻译目录管理](/concepts/05-catalog-management.md)
- [Jed JSON翻译格式](/concepts/06-json-jed-format.md)
- [双模式分发机制](/concepts/11-dual-mode-distribution.md)
