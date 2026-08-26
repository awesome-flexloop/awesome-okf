---
type: Index
title: 信源登记索引
description: jupyterlab-translate源码信源登记索引，记录文档到源码的映射关系
tags: [index, references, source-mapping, traceability]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
status: stable
---

# 信源登记

信源文档记录概念文档和示例文档中的事实与源码的对应关系，确保可溯源。

## 源码模块映射

| 模块文件 | 类/函数数量 | 信源文档 |
|---------|-----------|---------|
| `jupyterlab_translate/cli.py` | 1类7命令 | [CLI命令源码映射](/references/cli-source.md) |
| `jupyterlab_translate/api.py` | 6函数 | [API层源码映射](/references/api-source.md) |
| `jupyterlab_translate/utils.py` | 19函数 | [核心工具源码映射](/references/utils-source.md) |
| `jupyterlab_translate/converters.py` | 3函数 | [格式转换模块源码映射](/references/converters-source.md) |
| `jupyterlab_translate/finder.py` | 4函数 | [运行时发现模块源码映射](/references/finder-source.md) |
| `jupyterlab_translate/plugin.py` | 1类3方法 | [Hatch构建钩子源码映射](/references/plugin-source.md) |
| `jupyterlab_translate/contributors.py` | 4函数1类 | [Crowdin贡献者模块源码映射](/references/contributors-source.md) |
| 常量与配置 | — | [常量与配置映射](/references/constants-config.md) |

## 信源使用规范

1. **每个事实可溯源**：概念文档中的每个技术事实都应追溯到references中对应的源码位置
2. **Grep级验证**：API名称、函数签名、常量值需通过Grep在源码中验证存在
3. **版本绑定**：所有文档绑定到v1.3.7版本，版本升级后需更新信源

```{toctree}
:maxdepth: 7

api-source
cli-source
constants-config
contributors-source
converters-source
finder-source
plugin-source
utils-source
```
