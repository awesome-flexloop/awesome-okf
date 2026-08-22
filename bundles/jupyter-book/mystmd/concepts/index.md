---
type: Index
title: MySTmd 核心引擎概念索引
description: MySTmd 核心引擎知识束的概念文档索引，涵盖整体架构、解析器、转换管线、类型系统、错误处理、指令/角色、目标引用、Frontmatter、节点规范、配置系统、CLI和参考文献处理。
tags: [mystmd, concepts, index]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "00-overview.md"
  - path: "01-unified-plugin-architecture.md"
  - path: "02-myst-parser.md"
  - path: "03-myst-transforms.md"
  - path: "04-myst-common-types.md"
  - path: "05-error-handling.md"
  - path: "06-directives-and-roles.md"
  - path: "07-targets-references.md"
  - path: "08-frontmatter.md"
  - path: "09-myst-spec-node-types.md"
  - path: "10-configuration-system.md"
  - path: "11-cli-toolchain.md"
  - path: "12-citation-js-utils.md"
---

## 概念文档列表

### 架构总览

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [MySTmd 整体架构](00-overview.md) | 包架构、核心数据流、插件体系、技术栈 |
| 01 | [统一插件架构](01-unified-plugin-architecture.md) | unified Plugin 接口、DirectiveSpec/RoleSpec/TransformSpec/MystPlugin、markdown-it 插件层 |

### 解析与转换

| 编号 | 文档 | 说明 |
|------|------|------|
| 02 | [MyST 解析器](02-myst-parser.md) | mystParse、createTokenizer、MarkdownParseState、Token→MDAST 映射、指令/角色后处理 |
| 03 | [MDAST 转换管线](03-myst-transforms.md) | basicTransformations 22 个有序 transform、document/project 两阶段、compositePlugin |

### 类型与工具

| 编号 | 文档 | 说明 |
|------|------|------|
| 04 | [公共类型系统](04-myst-common-types.md) | GenericNode/GenericParent、RuleId 枚举、工具函数、TargetKind/AdmonitionKind |
| 05 | [错误处理与 VFile 消息系统](05-error-handling.md) | VFile messages、fileError/fileWarn/fileInfo、ErrorRule 级别覆盖、RuleId 分类 |
| 09 | [MDAST 节点类型规范](09-myst-spec-node-types.md) | 50+ 节点类型定义、SourceFileKind/CiteKind 枚举、myst-spec-ext 兼容层 |

### MyST 语法特性

| 编号 | 文档 | 说明 |
|------|------|------|
| 06 | [指令与角色系统](06-directives-and-roles.md) | DirectiveSpec/RoleSpec 定义、参数类型系统、选项解析、ctx.parseMyst 递归解析 |
| 07 | [目标与引用系统](07-targets-references.md) | (label)= 目标标记、enumerateTargets 全局编号、resolveReferences 交叉引用、cite 角色 |
| 08 | [Frontmatter 元数据系统](08-frontmatter.md) | Page/Project/Site 三级 frontmatter、20+ 子模块、YAML 解析与合并 |
| 12 | [参考文献处理](12-citation-js-utils.md) | citation-js-utils、BibTeX 解析、CSL、APA/Vancouver/Harvard 样式、inline citation 格式化 |

### 配置与工具链

| 编号 | 文档 | 说明 |
|------|------|------|
| 10 | [配置系统](10-configuration-system.md) | myst.yml、ProjectConfig/SiteConfig/ErrorRule、插件注册、nav/actions 配置 |
| 11 | [CLI 工具链](11-cli-toolchain.md) | myst init/build/start/clean/templates、commander、Session、构建流程 |

## 概念依赖图

```
00 整体架构
 ├─ 01 统一插件架构
 │    ├─ 06 指令与角色系统
 │    └─ 03 MDAST 转换管线
 ├─ 02 MyST 解析器
 │    ├─ 06 指令与角色系统
 │    ├─ 09 MDAST 节点类型规范
 │    └─ 05 错误处理
 ├─ 03 MDAST 转换管线
 │    ├─ 07 目标与引用系统
 │    ├─ 12 参考文献处理
 │    └─ 05 错误处理
 ├─ 04 公共类型系统
 │    ├─ 01 统一插件架构
 │    ├─ 05 错误处理
 │    └─ 09 MDAST 节点类型规范
 ├─ 08 Frontmatter 元数据
 ├─ 10 配置系统
 │    ├─ 08 Frontmatter
 │    └─ 05 错误处理
 └─ 11 CLI 工具链
      ├─ 10 配置系统
      ├─ 02 MyST 解析器
      └─ 03 MDAST 转换管线
```
