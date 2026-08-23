---
type: Example
title: 扩展包国际化基础流程
description: 从零开始为一个JupyterLab扩展配置国际化，包括源码标记、字符串提取、翻译和编译完整流程
tags: [example, extension, i18n, workflow, extract, update, compile, basic]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: utils-source
    resource: /references/utils-source.md
    title: 核心工具函数映射
  - id: constants-config
    resource: /references/constants-config.md
    title: 翻译函数配置
---

# 扩展包国际化基础流程

本示例演示如何从零开始为一个JupyterLab扩展添加国际化支持，包括在源码中标记可翻译字符串、提取字符串、创建翻译文件和编译产物。

## 前置条件

- Python >= 3.7，Node.js >= 14
- 已安装jupyterlab-translate：`pip install jupyterlab-translate`
- 已有一个JupyterLab扩展项目

## 步骤一：在源码中标记可翻译字符串

### Python代码

在Python代码中，使用 `trans` 对象的方法标记可翻译字符串：

```python
# my_extension/__init__.py
from some_i18n_module import trans  # 实际使用JupyterLab提供的trans对象

# 简单翻译
text = trans.__("Hello World")

# 带复数
text = trans._n("One file opened", "{count} files opened", count).format(count=count)

# 带上下文（消歧义）
text = trans._p("menu", "Open")

# 带上下文+复数
text = trans._np("toolbar", "One item", "{count} items", count)
```

pybabel会从以下函数中提取字符串：
`trans.gettext`, `trans.pgettext`, `trans.ngettext`, `trans.npgettext`, `trans.__`, `trans._p`, `trans._n`, `trans._np`

### TypeScript/TSX代码

在TypeScript代码中，使用扩展初始化时获得的翻译函数：

```typescript
// src/index.ts
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:plugin',
  autoStart: true,
  requires: [ITranslator],
  activate: (app: JupyterFrontEnd, translator: ITranslator) => {
    const trans = translator.load('my_extension');

    // 简单翻译
    console.log(trans.__("Hello World"));

    // 复数
    const count = 5;
    console.log(trans._n("One file", "{count} files", count).replace('{count}', String(count)));

    // 带上下文
    console.log(trans._p("menu", "File"));

    // 命令标签
    app.commands.addCommand('my-extension:run', {
      label: trans.__("Run My Extension"),
      execute: () => { /* ... */ }
    });
  }
};
```

gettext-extract支持的调用根：`trans`, `this.trans`, `this._trans`, `this.props.trans`, `props.trans`

### JSON Schema设置

在插件的schema文件中，title和description字段会被自动提取：

```json
{
  "title": "My Extension",
  "description": "A demo JupyterLab extension",
  "properties": {
    "enabled": {
      "title": "Enable feature",
      "description": "Whether to enable the feature",
      "type": "boolean",
      "default": true
    }
  },
  "jupyter.lab.menus": [
    {
      "id": "my-menu-item",
      "label": "My Command"
    }
  ]
}
```

在package.json中指定schema目录：

```json
{
  "jupyterlab": {
    "schemaDir": "schema"
  }
}
```

## 步骤二：提取字符串

假设扩展目录结构为：

```
my-extension/
├── my_extension/
│   └── __init__.py
├── src/
│   └── index.ts
├── schema/
│   └── plugin.json
└── pyproject.toml
```

执行extract命令：

```bash
jupyterlab-translate extract ./my-extension my_extension
```

这会在 `my-extension/my_extension/locale/` 下生成 `my_extension.pot` 文件。

## 步骤三：创建翻译文件

为中文和西班牙语创建翻译：

```bash
jupyterlab-translate update ./my-extension my_extension -l zh_CN -l es_ES
```

这会创建以下文件：
- `my_extension/locale/zh_CN/LC_MESSAGES/my_extension.po`
- `my_extension/locale/es_ES/LC_MESSAGES/my_extension.po`

编辑PO文件填入翻译。以中文为例：

```po
#: /my_extension/__init__.py:5
msgid "Hello World"
msgstr "你好，世界"

#: /src/index.ts:15
msgctxt "menu"
msgid "File"
msgstr "文件"

#: /schema/plugin.json:/title
msgctxt "schema"
msgid "My Extension"
msgstr "我的扩展"

#: /src/index.ts:12
msgid "One file"
msgid_plural "{count} files"
msgstr[0] "一个文件"
msgstr[1] "{count}个文件"
```

## 步骤四：编译翻译文件

```bash
jupyterlab-translate compile ./my-extension my_extension -l zh_CN -l es_ES
```

编译后生成MO和JSON文件：

```
my-extension/
└── my_extension/
    └── locale/
        ├── my_extension.pot
        ├── zh_CN/
        │   └── LC_MESSAGES/
        │       ├── my_extension.po
        │       ├── my_extension.mo    ← 新增
        │       └── my_extension.json  ← 新增
        └── es_ES/
            └── LC_MESSAGES/
                ├── my_extension.po
                ├── my_extension.mo
                └── my_extension.json
```

## 步骤五：配置Entry Point

在pyproject.toml中添加entry point，让JupyterLab运行时能发现翻译：

```toml
[project.entry-points."jupyterlab.locale"]
my-extension = "my_extension"
```

## 步骤六：配置打包

确保wheel中包含翻译文件：

```toml
[tool.hatch.build.targets.wheel]
artifacts = [
    "my_extension/**/*.json",
    "my_extension/**/*.mo",
]
exclude = [
    "my_extension/**/*.po",
]
```

## 更新翻译

当源码中的字符串发生变化后，重新执行：

```bash
# 重新提取（合并到已有POT）
jupyterlab-translate extract ./my-extension my_extension

# 更新PO文件（保留已有翻译，添加新字符串）
jupyterlab-translate update ./my-extension my_extension -l zh_CN

# 重新编译
jupyterlab-translate compile ./my-extension my_extension -l zh_CN
```

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [字符串提取流水线](/concepts/04-extraction-pipeline.md)
- [翻译目录管理](/concepts/05-catalog-management.md)
- [Jed JSON翻译格式](/concepts/06-json-jed-format.md)
- [Hatch构建钩子集成](/concepts/07-hatch-build-hook.md)
