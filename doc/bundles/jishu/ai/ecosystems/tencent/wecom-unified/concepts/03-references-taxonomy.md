---
type: concept
title: references 分类学
description: 把 133 篇扁平 reference 的两级命名、逐域分布与四个大系列整理成可检索、可扩写的分类体系。
tags: [wecom, wecom-unified, references]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# references 分类学

`references/` 是这套 Skill 真正的知识库：133 篇 `.md` 全部平铺在一层，没有子目录（F-009、F-045）。这种看似「不讲究」的组织方式，实际上用文件名承担了索引职责——只要掌握命名规则，就能在不打开文件的情况下判断某篇文档属于哪个域、是入口还是细则、属于哪个子系列。

## 一、两级命名：入口与细则

133 篇中，14 篇是域入口，文件名为 `wecomcli-<域>.md`；其余 119 篇是域内文档，文件名为 `wecomcli-<域>-<主题>.md`（F-046）。`README.md` 的项目结构说明也明确标注了这两级命名（F-018）。

| 层级 | 命名模式 | 篇数 | 作用 | 证据 |
|---|---|---|---|---|
| 域入口 | `wecomcli-<域>.md` | 14 | 域适用范围、接口路由表、跨域依赖 | F-046 |
| 域内细则 | `wecomcli-<域>-<主题>.md` | 119 | 单个接口或单类操作的参数契约 | F-046 |
| 合计 | — | 133 | — | F-045、F-063 |

入口文件的职责不是「概述」，而是「分流」：它通常包含适用范围、不适用情形、接口路由表与跨技能依赖，指引读者继续读取哪篇细则。因此正确的使用顺序永远是「先入口、后细则」，跳过入口直接翻细则，容易漏掉不适用条件与跨域依赖。

一个可操作的检索示例：用户说「把这份表格里的合并单元格处理一下」，先由意图路由判定为 sheet 域，读 `wecomcli-sheet.md` 得到主题清单，再定位与合并单元格相关的细则；若用户说的是「智能表格里的视图分组」，则改读 `wecomcli-smartsheet.md`。两次检索的差别只在入口，后续路径由入口的清单决定，并不需要记住 133 个文件名。这也是入口文件必须维护完整主题清单的原因——它是整棵检索树的根。

## 二、逐域分布

| 业务域 | 篇数 | 构成 | 代表文件 | 证据 |
|---|---|---|---|---|
| contact | 1 | 仅入口 | `wecomcli-contact.md` | F-047 |
| disk | 1 | 仅入口 | `wecomcli-disk.md` | F-048 |
| media | 1 | 仅入口 | `wecomcli-media.md` | F-049 |
| message | 1 | 仅入口 | `wecomcli-message.md` | F-050 |
| doc | 4 | 入口 + create / contents-append / contents-overwrite | `wecomcli-doc-create.md` | F-051 |
| doc-manage | 4 | 入口 + members / names / rules update | `wecomcli-doc-manage-doc-rules-update.md` | F-052 |
| calendar | 8 | 入口 + agenda / cancel / create / freebusy / meeting-room / search / update | `wecomcli-calendar-freebusy.md` | F-053 |
| meeting | 7 | 入口 + cancel / create / list / original-get / search / update | `wecomcli-meeting-original-get.md` | F-054 |
| todo | 7 | 入口 + create / delete / finish / get / list / update | `wecomcli-todo-finish.md` | F-055 |
| sheet | 18 | 入口 + 17 篇主题细则 | `wecomcli-sheet-read-data.md` | F-056 |
| smartsheet | 32 | 入口 + 11 篇领域文档 + 20 篇模板文档 | `wecomcli-smartsheet-webhook.md` | F-057、F-058 |
| smartpage | 14 | 入口 + 3 篇领域文档 + 10 篇公式文档 | `wecomcli-smartpage-mdx-syntax.md` | F-060 |
| pptx | 27 | 入口 + 12 篇流程/契约 + 14 篇组件文档 | `wecomcli-pptx-content-contract.md` | F-061 |
| email | 8 | 入口 + 7 篇主题 | `wecomcli-email-send-mail.md` | F-062 |
| 合计 | 133 | 1+1+1+1+4+4+8+7+7+18+32+14+27+8 | — | F-063 |

分布极不均衡：contact、disk、media、message 四个域各只有 1 篇，说明这些域的接口面窄、单篇即可讲完；而 sheet（18）、smartsheet（32）、smartpage（14）、pptx（27）四个域合计 91 篇，占全部的 68%。这四域也是操作复杂度最高、最容易出错的区域，需要按子系列继续拆分。

## 三、四个子系列

大域内部用固定前缀形成子系列，这是分类学的第二层规律：

| 子系列 | 前缀 | 篇数 | 取值示例 | 证据 |
|---|---|---|---|---|
| sheet 主题细则 | `wecomcli-sheet-` | 17 | `workbook`、`read-data`、`write-cells`、`formulas`、`style`、`filter`、`validation`、`xlsx-process` | F-056 |
| smartsheet 模板 | `wecomcli-smartsheet-template-` | 20 | `project_management`、`hr_and_administration`、`sales_and_operations`、`workflow` 类场景 | F-057、F-058 |
| smartpage 公式 | `wecomcli-smartpage-formula-` | 10 | `arraylist`、`datetime`、`logic`、`math`、`operators`、`pageblock`、`reference`、`templates`、`text`、`user` | F-060 |
| pptx 组件 | `wecomcli-pptx-component-` | 14 | `animation`、`box`、`chart`、`codeblock`、`diagram`、`image`、`qrcode`、`slide`、`svg`、`table`、`text` | F-061 |

四个系列的服务对象不同：sheet 主题细则是「按操作类型」拆分，smartsheet 模板是「按行业场景」拆分，smartpage 公式是「按函数类别」拆分，pptx 组件是「按页面元素」拆分。识别系列类型，就能预判文档里大致是什么内容。

## 四、命名变体与例外

规则之外有三处值得注意的变体：

1. **模板名使用下划线**。20 篇 smartsheet 模板文档在模板名部分使用下划线，例如 `wecomcli-smartsheet-template-rd_process_ops.md`，与其余文档的连字符风格不同（F-059）。检索时不能假设「所有分隔符都是连字符」。
2. **pptx 的双前缀**。两篇文档的全名是 `wecomcli-pptx-pptx-api.md` 与 `wecomcli-pptx-pptx-edit.md`，域前缀与主题前缀重复（F-061）。按 `wecomcli-pptx-*.md` 匹配会得到 26 篇，加上入口才是 27 篇。
3. **doc 与 doc-manage 的前缀重叠**。`wecomcli-doc*.md` 会同时命中两个域，统计 doc 域时必须排除 `wecomcli-doc-manage*`（F-051、F-052）。这也是逐域计数容易出错的地方。

## 五、用文件名做检索与扩写

由于目录扁平且命名严格，可以直接把文件名当作索引：先按 `wecomcli-<域>.md` 找入口，再按 `<域>-<主题>` 枚举细则，最后按子系列前缀定位专项文档。`F-063` 的求和校验（15 个域逐域计数合计 133，等于目录实测）提供了一个可复跑的完整性检查：新增文档后若两侧不等，说明有文档落在命名规则之外。

扩写时应遵守三条既有约定：域入口只增加清单与指向，不堆参数细节；域内细则按「一个接口/一类操作一篇」拆分；子系列沿用固定前缀，模板名保持既有下划线风格（F-059）。破坏命名一致性不会导致构建失败，但会让「文件名即索引」的检索方式失效，这是这套扁平结构唯一的隐性成本。

## 延伸阅读

- [意图路由](02-intent-routing.md)：先分域，再按本篇方法定位细则。
- [脚本工具链](04-scripts-toolchain.md)：references 之外的 Python 脚本资产。
- [PPT 模板系统](05-ppt-template-system.md)：pptx 组件文档与本地模板的对应关系。
- [信源登记](../references/sources.md)：133 篇的核对命令与逐域计数方法。