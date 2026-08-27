---
type: Concept
title: 快速开始
description: 通过3条命令完成JupyterLab扩展的国际化工作流：extract提取字符串、update更新翻译、compile编译产物
tags: [getting-started, quickstart, cli, workflow, extract, update, compile]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/cli-source.md
    title: README使用说明
  - id: api
    resource: /references/api-source.md
    title: API层函数映射
---

# 快速开始

本节展示如何使用 jupyterlab-translate 为一个JupyterLab扩展添加国际化支持。整个工作流由三条核心命令组成：extract → update → compile。

## 前置条件

- Python >= 3.7
- Node.js >= 14
- 已安装jupyterlab-translate：`pip install jupyterlab-translate`

## 基本工作流（独立扩展包模式）

假设你的JupyterLab扩展位于 `my-extension/` 目录，项目名为 `my_extension`。

### 第一步：提取字符串

```bash
jupyterlab-translate extract <JLAB-EXTENSION-DIR> <JLAB-EXTENSION-NAME>
```

示例：

```bash
jupyterlab-translate extract ./my-extension my_extension
```

此命令会：
1. 扫描扩展目录中的 `*.py`、`*.ts`、`*.tsx` 源文件
2. 查找JSON Schema文件并提取可翻译字段
3. 生成POT模板文件到 `my-extension/my_extension/locale/my_extension.pot`
4. 自动合并和去重字符串条目

### 第二步：更新翻译目录

```bash
jupyterlab-translate update <JLAB-EXTENSION-DIR> <JLAB-EXTENSION-NAME> -l <LOCALE>
```

示例：

```bash
jupyterlab-translate update ./my-extension my_extension -l es_ES -l zh_CN
```

此命令会：
1. 读取POT模板文件
2. 为每个指定语言创建或更新PO文件
3. PO文件位于 `my-extension/my_extension/locale/<LOCALE>/LC_MESSAGES/my_extension.po`
4. 如果PO文件已存在，保留已有翻译并合并新字符串

如果不指定 `-l` 参数，将自动发现 `locale/` 目录下已有的所有语言并更新。

### 第三步：编译翻译文件

```bash
jupyterlab-translate compile <JLAB-EXTENSION-DIR> <JLAB-EXTENSION-NAME> -l <LOCALE>
```

示例：

```bash
jupyterlab-translate compile ./my-extension my_extension -l es_ES
```

此命令会：
1. 将PO文件编译为MO二进制文件（`*.mo`）供Python后端使用
2. 将PO文件转换为Jed JSON格式（`*.json`）供JupyterLab前端使用
3. 两种格式文件位于PO文件同目录下

## 生成的目录结构

执行完三步后，你的扩展目录中会生成以下结构：

```
my-extension/
└── my_extension/           # 项目名（normalize后，-替换为_）
    └── locale/
        ├── my_extension.pot          # 翻译模板
        ├── es_ES/
        │   └── LC_MESSAGES/
        │       ├── my_extension.po   # 西班牙语翻译源文件
        │       ├── my_extension.mo   # 编译后的MO文件
        │       └── my_extension.json # Jed JSON格式（前端用）
        └── zh_CN/
            └── LC_MESSAGES/
                ├── my_extension.po
                ├── my_extension.mo
                └── my_extension.json
```

## 语言包仓库模式

如果你在维护[jupyterlab/language-packs](https://github.com/jupyterlab/language-packs)集中式语言包仓库，使用 `_pack` 后缀的命令：

```bash
# 从JupyterLab核心提取字符串
jupyterlab-translate extract-pack <package-dir> <language-packs-dir> jupyterlab

# 从第三方扩展提取字符串
jupyterlab-translate extract-pack <package-dir> <language-packs-dir> <extension-name>

# 更新翻译
jupyterlab-translate update-pack <package-dir> <language-packs-dir> jupyterlab -l zh_CN

# 编译（会自动将产物移动到语言包目录）
jupyterlab-translate compile-pack <language-packs-dir> jupyterlab -l zh_CN
```

## 注意事项

- 项目名参数会被规范化：转为小写、`-` 替换为 `_`（如 `My-Extension` → `my_extension`）
- locale格式使用下划线分隔（如 `zh_CN`、`es_ES`、`ko_KR`），JSON输出时自动转为短横线格式（`zh-CN`）
- 首次执行update时会创建新的PO文件，之后执行会合并更新

## 相关概念

- [JupyterLab Translate 简介](00-introduction.md)
- [CLI命令参考](03-cli-commands.md)
- [架构总览](02-architecture-overview.md)
- [双模式分发机制](11-dual-mode-distribution.md)
- [基础扩展示例](../examples/01-basic-extension-i18n.md)
