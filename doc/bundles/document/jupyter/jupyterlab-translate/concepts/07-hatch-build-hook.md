---
type: Concept
title: Hatch构建钩子集成
description: 通过Hatch Build Hook在wheel构建时自动编译PO翻译文件为MO和JSON格式，实现翻译文件的自动打包
tags: [hatch, build-hook, wheel, sdist, compile, packaging, build-system]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: plugin-source
    resource: /references/plugin-source.md
    title: Hatch构建钩子源码映射
---

# Hatch构建钩子集成

jupyterlab-translate 提供了一个Hatch Build Hook插件，在Python包构建时自动编译翻译文件。这使得语言包维护者无需手动执行compile命令，构建过程会自动处理PO→MO/JSON的转换。

## 插件注册

### Entry Point

在 `pyproject.toml` 中，jupyterlab-translate通过entry point注册Hatch钩子：

```toml
[project.entry-points.hatch]
jupyter-translate = "jupyterlab_translate.hooks"
```

hooks.py中的 `hatch_register_build_hook()` 函数返回 `JupyterLanguageBuildHook` 类。

### 在语言包中启用

在语言包的 `pyproject.toml` 中添加：

```toml
[tool.hatch.build.hooks.jupyter-translate]
dependencies = ["jupyterlab-translate"]
```

## JupyterLanguageBuildHook类

`JupyterLanguageBuildHook` 继承自 `hatchling.builders.hooks.plugin.interface.BuildHookInterface`，实现了三个核心方法。

### 常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `PLUGIN_NAME` | `"jupyter-translate"` | 插件名称 |
| `COMPILATION_THRESHOLD` | `0` | 编译阈值（翻译百分比），默认0表示全部编译 |
| `PACKAGE_PREFIX` | `"jupyterlab_language_pack_"` | 语言包Python包名前缀 |

### _get_locale_name() 方法

这是一个内部辅助方法，用于发现语言包目录和提取locale名称：

1. 在包根目录glob匹配 `jupyterlab_language_pack_??_??`（双字母语言+双字母国家）
2. 如果没找到，再匹配 `jupyterlab_language_pack_???_??`（三字母语言+双字母国家）
3. 从包名中提取locale名称（去掉前缀）
4. 返回 `(messages_folder, locale_name)` 元组

messages_folder路径格式为：
```
<package_folder>/locale/<locale_name>/LC_MESSAGES/
```

### clean() 方法

当执行 `hatch build -c` 或 `hatch clean` 时触发：

1. 调用 `_get_locale_name()` 获取messages_folder
2. 删除messages_folder中所有 `.json` 和 `.mo` 文件（保留 `.po` 源文件）

### initialize() 方法

这是核心方法，在每次构建前执行。行为因构建目标类型而异。

#### Wheel构建（target_name == "wheel"）

1. 发现messages_folder中所有 `.po` 文件
2. 对每个PO文件：
   - 使用polib读取PO文件
   - 调用 `po.percent_translated()` 计算翻译完成百分比
   - 如果百分比 >= COMPILATION_THRESHOLD（默认0），调用 `compile_po_file()`
   - 如果低于阈值，打印信息跳过
3. compile_po_file() 会生成 `.json` 和 `.mo` 文件

Wheel构建产物包含 `.json` 和 `.mo`，不包含 `.po` 文件。

#### 非Wheel构建（如sdist）

1. 检查 `CROWDIN_API_KEY` 环境变量
2. 如果存在，调用 `get_contributors_report()` 更新CONTRIBUTORS.md
3. 如果不存在，打印警告

sdist构建保留 `.po` 源文件，不包含编译产物（`.json`/`.mo`）。

## 构建产物差异

以韩语语言包为例（来自测试验证）：

### sdist（源码分发包）包含：

```
jupyterlab_language_pack_ko_kr-1.0.post2/
├── CONTRIBUTORS.md
├── jupyterlab_language_pack_ko_KR/
│   ├── __init__.py
│   └── locale/ko_KR/LC_MESSAGES/
│       ├── jupyterlab.po      ← PO源文件
│       └── spellchecker.po    ← PO源文件
├── pyproject.toml
└── PKG-INFO
```

### wheel（二进制分发包）包含：

```
jupyterlab_language_pack_ko_KR/
├── __init__.py
└── locale/ko_KR/LC_MESSAGES/
    ├── jupyterlab.json       ← 编译后的JSON
    ├── jupyterlab.mo         ← 编译后的MO
    ├── spellchecker.json    ← 编译后的JSON
    └── spellchecker.mo      ← 编译后的MO
```

## pyproject.toml完整配置示例

以下是一个语言包的典型pyproject.toml配置：

```toml
[build-system]
requires = ["hatchling>=1.4.0", "jupyterlab-translate"]
build-backend = "hatchling.build"

[project]
name = "jupyterlab_language_pack_ko_KR"
dynamic = ["version"]

[project.entry-points."jupyterlab.languagepack"]
ko_KR = "jupyterlab_language_pack_ko_KR"

[tool.hatch.version]
path = "jupyterlab_language_pack_ko_KR/__init__.py"

[tool.hatch.build]
artifacts = [
    "CONTRIBUTORS.md"
]

[tool.hatch.build.hooks.jupyter-translate]
dependencies = ["jupyterlab-translate"]

[tool.hatch.build.targets.wheel]
artifacts = [
    "jupyterlab_language_pack_ko_KR/**/*.json",
    "jupyterlab_language_pack_ko_KR/**/*.mo",
]
exclude = [
    "jupyterlab_language_pack_ko_KR/**/*.po",
]
```

## 编译阈值说明

`COMPILATION_THRESHOLD` 当前设置为0，意味着所有PO文件（即使翻译率很低）都会被编译。语言包维护者可以根据需要修改此值：

- `0`：编译所有PO文件（默认，推荐）
- `50`：只编译翻译率≥50%的语言
- `100`：只编译100%完成的语言

> 注意：当前threshold是模块级常量，不通过pyproject.toml配置。如需自定义，需要fork或monkey-patch。

## 相关概念

- [翻译目录管理](05-catalog-management.md)
- [Jed JSON翻译格式](06-json-jed-format.md)
- [运行时语言包发现](08-runtime-discovery.md)
- [Crowdin贡献者集成](10-contributors-crowdin.md)
- [Hatch构建钩子源码映射](../references/plugin-source.md)
- [Hatch构建钩子配置示例](../examples/04-hatch-hook-integration.md)
