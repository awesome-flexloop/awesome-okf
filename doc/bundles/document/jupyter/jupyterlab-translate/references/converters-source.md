---
type: Reference
title: 格式转换模块源码映射
description: jupyterlab-translate converters模块（converters.py）的PO到JSON转换逻辑
tags: [converters, jed, json, po, mo, format]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: converters-source
    resource: /references/converters-source.md
    title: converters.py 源码
---

# 格式转换模块源码映射

本文档记录 `jupyterlab_translate/converters.py` 模块的函数和转换逻辑。

## 模块信息

- **源文件**：`jupyterlab_translate/converters.py`
- **角色**：PO→Jed JSON格式转换
- **外部依赖**：polib, json

## 函数清单

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `convert_catalog_to_json` | `(po_path: Path, output_dir: Path, project: str) -> Path` | 第9-68行 | 将PO文件转换为JupyterLab前端使用的Jed JSON格式 |

## Jed JSON格式结构

```json
{
    "": {
        "domain": "<project>",
        "version": "<version>",
        "language": "<locale-with-dash>",
        "plural_forms": "<plural-forms-expression>"
    },
    "<msgid>": ["<translation>"],
    "<msgctxt>\u0004<msgid>": ["<translation>"],
    "<msgid-plural>": ["<translation-singular>", "<translation-plural>", ...]
}
```

### 转换规则

1. **元数据**：顶层key为空字符串`""`，包含domain、version、language、plural_forms
2. **无上下文条目**：key为msgid本身，value为单元素数组`[msgstr]`
3. **有上下文条目**：key为`{msgctxt}\x04{msgid}`（\x04是EOT控制字符，ASCII 0x04）
4. **复数条目**：value为所有msgstr_plural值的有序数组
5. **特殊处理**：nplurals=1的语言（如韩语）复数列表追加空字符串，以满足JupyterLab前端校验
6. **合并策略**：如果JSON文件已存在，保留旧条目中不在新PO中的翻译
7. **过滤**：obsolete条目不写入JSON；无翻译的条目（msgstr为空）跳过
8. **输出**：JSON以sort_keys=True、indent=4格式化输出

## 相关概念

- [Jed JSON翻译格式](../concepts/06-json-jed-format.md)
- [翻译目录管理](../concepts/05-catalog-management.md)
- [核心工具源码映射](utils-source.md)
