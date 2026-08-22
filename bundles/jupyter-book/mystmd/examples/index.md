---
type: Index
title: MySTmd 示例索引
description: MySTmd 核心引擎的可运行示例代码索引，涵盖基本解析、自定义 Transform、参考文献引用、自定义角色和自定义指令。
tags: [mystmd, examples, index]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "00-basic-parsing.md"
  - path: "02-custom-transform.md"
  - path: "03-citations-example.md"
  - path: "04-custom-role.md"
  - path: "05-custom-directive.md"
---

## 示例列表

| 编号 | 示例 | 说明 | 相关概念 |
|------|------|------|---------|
| 00 | [使用 mystParse 解析 MyST Markdown](00-basic-parsing.md) | 基本解析、VFile 错误收集、自定义指令/角色注册、AST 遍历查询 | [MyST 解析器](/concepts/02-myst-parser.md) |
| 02 | [编写自定义 Transform 插件](02-custom-transform.md) | 函数式/Plugin 式 Transform、AST 遍历修改、MystPlugin 打包 | [MDAST 转换管线](/concepts/03-myst-transforms.md) |
| 03 | [参考文献引用处理](03-citations-example.md) | BibTeX 解析、引用渲染器、内联引用格式化、HTML 清理 | [参考文献处理](/concepts/12-citation-js-utils.md) |
| 04 | [编写自定义 Role](04-custom-role.md) | RoleSpec 定义、body/options 类型、验证逻辑、HTML 渲染属性 | [指令与角色系统](/concepts/06-directives-and-roles.md) |
| 05 | [编写自定义 Directive](05-custom-directive.md) | DirectiveSpec 定义、arg/options/body、ctx.parseMyst 递归解析、alias、MystPlugin 打包 | [指令与角色系统](/concepts/06-directives-and-roles.md) |

## 示例难度递进

```
入门级
 ├── 00-basic-parsing — 理解解析流程和 AST 结构
 │
进阶级
 ├── 04-custom-role — 行内扩展
 ├── 03-citations-example — 引用工具使用
 │
高级
 ├── 05-custom-directive — 块级扩展 + 递归解析
 └── 02-custom-transform — AST 后处理
```

## 前置知识

| 示例 | 需要阅读的概念文档 |
|------|-----------------|
| 00-basic-parsing | [MyST 解析器](/concepts/02-myst-parser.md)、[公共类型系统](/concepts/04-myst-common-types.md) |
| 02-custom-transform | [MDAST 转换管线](/concepts/03-myst-transforms.md)、[统一插件架构](/concepts/01-unified-plugin-architecture.md) |
| 03-citations-example | [参考文献处理](/concepts/12-citation-js-utils.md)、[目标与引用系统](/concepts/07-targets-references.md) |
| 04-custom-role | [指令与角色系统](/concepts/06-directives-and-roles.md)、[错误处理](/concepts/05-error-handling.md) |
| 05-custom-directive | [指令与角色系统](/concepts/06-directives-and-roles.md)、[MyST 解析器](/concepts/02-myst-parser.md) |
