---
type: spec
title: github-activity 架构洞察
description: github-activity 源码洞察记录
tags:
- github-activity
- spec
- insights
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: github-activity-source
  resource: /references/activity-source.md
  title: github-activity activity-source
---

# github-activity 架构洞察

> I 阶段产出：基于事实清单提炼的核心洞察四元组。

## 洞察 I-001：双模式标签分类——tags+pre 实现灵活分类

- **陈述**：github-activity 对每个PR分类配置了两种匹配模式：`tags`（匹配PR标签）和`pre`（匹配标题前缀关键字）。PR只需满足任一条件即归入对应分类，分类按优先级排列（api_change最高，ci最低），未匹配的PR归入"其他合并PR"。
- **证据**：F-005~F-014（8种分类的tags/pre配置）、TAGS_METADATA_BASE有序字典定义
- **反常识**：只依赖GitHub标签（labels）做分类是脆弱的——贡献者经常忘记打标签。双模式设计让标题前缀（如"BREAK:"、"FIX:"、"ENH:"、"DOC:"）成为可靠的后备分类方式。这种"标签+前缀约定"的双模式比纯标签分类容错率高得多，也符合conventional commits的思想。
- **行动**：自动化PR分类系统应同时利用标签和标题约定（前缀/正则），不要只依赖单一信号；按优先级排列分类，确保破坏性变更等重要类别优先匹配。

## 洞察 I-002：GraphQL分页+本地缓存——高效API数据获取

- **陈述**：使用GitHub GraphQL API（v4）而非REST API（v3），通过GraphQL的分页机制（pageInfo.hasNextPage/endCursor）一次性获取所需字段，避免REST API的多次往返请求。cache模块装饰器缓存API响应，减少重复调用和速率限制消耗。
- **证据**：F-020~F-024（GraphQL客户端和分页）、F-028~F-030（缓存装饰器）
- **反常识**：GitHub REST API列出PR需要多次请求（列表→详情→标签→评论），每个PR可能需要3-4次API调用，遇到速率限制后需等待。GraphQL允许在一个查询中精确指定所需字段（title/author/labels/mergedAt等），一次请求获取一个页面（通常100条）的完整数据，请求量减少10倍以上。
- **行动**：处理GitHub等平台大量数据时，优先使用GraphQL API精确获取所需字段，减少请求次数；添加本地缓存避免重复查询；实现自动分页处理。

## 洞察 I-003：pandas DataFrame为中心的数据流

- **陈述**：核心函数`get_activity()`返回pandas DataFrame，所有数据处理（过滤、分类、排序、聚合）都使用DataFrame操作完成，最终通过`generate_activity_markdown()`转换为Markdown输出。这使得数据处理和输出生成完全解耦。
- **证据**：F-015~F-019（DataFrame核心数据流）、F-019~F-020（pandas/numpy依赖）
- **反常识**：很多CLI工具直接将API返回的JSON数据拼接为字符串输出，导致逻辑和格式耦合。使用DataFrame作为中间表示层，使得：（1）数据可以被程序进一步分析（统计贡献者数量、PR类型分布等），（2）可以轻松添加新的输出格式（JSON/HTML/CSV），（3）过滤和排序使用pandas成熟的API而非手写逻辑。
- **行动**：数据处理类CLI工具应使用DataFrame或类似的表格型数据结构作为中间表示，将数据获取、处理、渲染三个阶段解耦。

## 知识地图

```
github-activity/
├── 入门层
│   ├── 00-introduction.md     → I-001 功能概览
│   └── 01-getting-started.md  → 安装与基本CLI用法
├── 核心层
│   ├── 02-cli-usage.md        → CLI命令详解
│   ├── 03-activity-data.md    → I-002,I-003 数据获取与处理
│   └── 04-configuration.md    → I-001 标签分类配置
└── 实践层
    └── examples/
        └── changelog-generation.md → 生成变更日志示例
```
