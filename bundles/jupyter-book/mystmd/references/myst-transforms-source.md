---
type: Reference
title: myst-transforms 转换插件源码信源
description: myst-transforms 包导出的 30+ 个 MDAST 转换插件、basicTransformations 复合管线以及 getFrontmatter 函数的源码登记。
tags: [mystmd, transforms, mdast, unified, plugin]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-transforms/src/index.ts"
    facts: [F-075, F-076, F-077, F-078]
  - path: "myst-transforms/src/basic.ts"
    facts: [F-079, F-080]
  - path: "myst-transforms/src/liftMystDirectivesAndRoles.ts"
    facts: [F-081]
  - path: "myst-transforms/src/frontmatter.ts"
    facts: [F-082, F-083]
---

## 源码位置

- `myst-transforms/src/index.ts` — 包导出入口
- `myst-transforms/src/basic.ts` — basicTransformations 复合插件
- `myst-transforms/src/liftMystDirectivesAndRoles.ts` — 指令/角色提升转换
- `myst-transforms/src/frontmatter.ts` — getFrontmatter 函数
- 各独立 transform 文件：admonitions, blocks, code, containers, enumerate, footnotes, headings, html, images, include, indices, keys, links/, math, mathSimplifications, removeUnicode, targets, toc, unnest, basic, liftMystDirectivesAndRoles, caption, blockquote, abbreviations, glossary, joinGates, htmlIds

## 导出 API

### 转换插件分类

#### 指令与角色提升
| API | 说明 |
|-----|------|
| `liftMystDirectivesAndRolesTransform` | 提升 mystDirective/mystRole 节点，转移 target 属性 |
| `liftMystDirectivesAndRolesPlugin` | 对应的 unified Plugin |

#### 目标与标签
| API | 说明 |
|-----|------|
| `mystTargetsTransform` | 处理 mystTarget 节点，生成 identifier/label/html_id |
| `mystTargetsPlugin` | 对应的 unified Plugin |
| `headingLabelTransform` | 为标题自动生成标签 |
| `headingLabelPlugin` | 对应的 unified Plugin |

#### 标题
| API | 说明 |
|-----|------|
| `headingDepthTransform` | 调整标题深度 |
| `headingDepthPlugin` | 对应的 unified Plugin |
| `captionParagraphTransform` | 处理 caption 段落 |
| `captionParagraphPlugin` | 对应的 unified Plugin |

#### 代码
| API | 说明 |
|-----|------|
| `codeTransform` | 代码块处理（转换为 code 指令） |
| `codePlugin` | 对应的 unified Plugin |
| `inlineCodeFlattenTransform` | 内联代码展平 |
| `inlineCodeFlattenPlugin` | 对应的 unified Plugin |

#### 数学
| API | 说明 |
|-----|------|
| `mathTransform` / `mathPlugin` | 数学公式处理 |
| `mathLabelTransform` / `mathLabelPlugin` | 数学公式标签 |
| `mathNestingTransform` / `mathNestingPlugin` | 数学公式嵌套 |
| `renderEquation` | 渲染公式 |
| `inlineMathSimplificationTransform` / `inlineMathSimplificationPlugin` | 内联数学简化 |

#### Admonition
| API | 说明 |
|-----|------|
| `admonitionHeadersTransform` / `admonitionHeadersPlugin` | admonition 标题处理 |
| `admonitionBlockquoteTransform` / `admonitionBlockquotePlugin` | blockquote 转 admonition |
| `admonitionQmdTransform` / `admonitionQmdPlugin` | QMD 格式 admonition 处理 |

#### 块与容器
| API | 说明 |
|-----|------|
| `blockNestingTransform` / `blockNestingPlugin` | 块嵌套处理 |
| `blockMetadataTransform` / `blockMetadataPlugin` | 块元数据处理 |
| `containerChildrenTransform` / `containerChildrenPlugin` | 容器子节点处理 |

#### 引用与列举
| API | 说明 |
|-----|------|
| `enumerateTargetsTransform` / `enumerateTargetsPlugin` | 列举目标（编号） |
| `resolveLinksAndCitationsTransform` | 解析链接和引用 |
| `resolveReferencesTransform` / `resolveReferencesPlugin` | 解析交叉引用 |
| `ReferenceState` | 引用状态解析器类 |
| `MultiPageReferenceResolver` | 多页引用解析器 |

#### 脚注
| API | 说明 |
|-----|------|
| `footnotesTransform` / `footnotesPlugin` | 脚注处理 |

#### 链接（links/ 子模块）
| API | 说明 |
|-----|------|
| links 子模块 | myst/sphinx/wiki/github/doi/rrid/ror 链接类型解析 |

#### 其他
| API | 说明 |
|-----|------|
| `htmlTransform` / `htmlPlugin` / `reconstructHtmlTransform` / `reconstructHtmlPlugin` | HTML 处理 |
| `htmlIdsTransform` / `htmlIdsPlugin` | HTML ID 生成 |
| `keysTransform` / `keysPlugin` | 密钥/标识符处理 |
| `imageAltTextTransform` / `imageAltTextPlugin` | 图片 alt 文本 |
| `includeDirectiveTransform` / `includeDirectivePlugin` | include 指令处理 |
| `buildIndexTransform` / `indexIdentifierTransform` / `indexIdentifierPlugin` | 索引条目处理 |
| `buildTocTransform` | 目录生成 |
| `glossaryTransform` / `glossaryPlugin` | 术语表处理 |
| `abbreviationTransform` / `abbreviationPlugin` | 缩写处理 |
| `blockquoteTransform` / `blockquotePlugin` | 引用块处理 |
| `joinGatesTransform` / `joinGatesPlugin` | 条件内容合并 |
| `unnestTransform` | 去嵌套 |
| `removeUnicodeTransform` | Unicode 清理 |
| `getFrontmatter` | Frontmatter 提取 |

### 复合插件

| API | 签名 | 说明 |
|-----|------|------|
| `basicTransformations` | `(tree: GenericParent, file: VFile, opts?: Record<string, any>) => void` | 按序执行 22 个核心 transform |
| `basicTransformationsPlugin` | `Plugin<[Record<string, any>], GenericParent, GenericParent>` | basicTransformations 的 unified Plugin 包装 |

### basicTransformations 执行顺序

1. liftMystDirectivesAndRolesTransform
2. mystTargetsTransform
3. captionParagraphTransform
4. codeBlockToDirectiveTransform (translate: ['math', 'mermaid'])
5. mathNestingTransform
6. mathLabelTransform
7. subequationTransform
8. headingLabelTransform
9. admonitionQmdTransform
10. admonitionBlockquoteTransform（必须在 header transforms 之前）
11. admonitionHeadersTransform
12. joinGatesTransform（必须在 block nesting 之前）
13. blockNestingTransform
14. blockMetadataTransform
15. blockToFigureTransform
16. containerChildrenTransform
17. htmlIdsTransform
18. imageAltTextTransform
19. blockquoteTransform
20. removeUnicodeTransform
21. headingDepthTransform
22. inlineCodeFlattenTransform
