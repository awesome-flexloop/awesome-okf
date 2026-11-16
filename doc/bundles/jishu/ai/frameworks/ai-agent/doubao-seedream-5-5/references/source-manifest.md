---
type: Reference
title: 来源登记与采集口径
description: 源文档身份、采集命令、版本锚点、图片未入库说明与已知局限。
status: stable
stale_after: 2027-05-16
sensitivity: internal
generated: { by: "agent:lark-doc-to-okf-wiki", at: "2026-11-16T15:40:00+08:00" }
sources:
  - id: guide
    resource: https://bytedance.larkoffice.com/docx/HkvNdjRwIoK4DcxHThicjQS3nig
    title: 豆包 Seedream 5.5 使用指南
---

# 来源登记与采集口径

## 1. 源文档身份

| 字段 | 值 |
| --- | --- |
| 类型 | 飞书 docx（`file-type: docx`） |
| 标题 | 豆包 Seedream 5.5 使用指南 |
| document_id | `HkvNdjRwIoK4DcxHThicjQS3nig` |
| revision_id | 3367 |
| URL | https://bytedance.larkoffice.com/docx/HkvNdjRwIoK4DcxHThicjQS3nig |
| 采集时间 | 2026-11-16 |
| 采集命令 | `lark-cli docs +fetch --doc "<above>" --doc-format markdown` |
| 画板 | 0（无 whiteboard 块，未走 `whiteboard +export`） |
| 评论 | 0（reference_map 无 comments 字段） |

文档末尾列出的关联文档（F-038）：

| 文档 | 类型 | token |
| --- | --- | --- |
| 豆包 Seedance 2.5 & Seedream 5.0 Pro 升级介绍 | docx | `EvLJdw9n8oX1HExDfllcA22jnLe` |
| 豆包 Seedream 4.5 使用指南 | wiki | `P1wyw0TPmiq87BkjvCychEdGnGd` |
| 豆包 Seedream 4.0 使用指南 | docx | `XwngdqdhIowfF8xhEA4cwpS2nLb` |

## 2. 采集产物

| 产物 | 位置 | 是否入库 |
| --- | --- | --- |
| `raw_full.json`（接口原始返回，含正文/tips/reference_map） | 采集临时目录 | 否 |
| `raw.md`（正文 markdown，73,231 字符） | 采集临时目录 | 否 |
| `outline.json`（两级标题大纲） | 采集临时目录 | 否 |

临时目录不作为知识包内容：接口原始返回包含内网临时资源路径与图片 token，与发布口径无关。知识包内只保留经核验的事实与改写后的教程正文。

## 3. 图片为何不入库

源文档内嵌 197 张示例图（F-006），本包一张未复制，原因三条：

1. **性质**：这些图是厂商示例结果图，文档自述"结果图均由 AI 生成"（F-009），版权与授权状态未在文档中说明。
2. **体量**：197 张图的体积远超本仓知识包的常规预算，本仓现有知识包几乎全部为纯文本（全库图片文件仅个位数）。
3. **可替代性**：教程需要的是**提示词写法**，而不是示例图的复现；词条、示例提示词、结构描述已足以支撑学习。想看效果时回到源文档对应小节。

代价是：本包无法替代"看图找感觉"这一环。风格词与美学词的**视觉参照**只能从源文档取得（[词库](../examples/keyword-library.md) 已标注该缺口）。

## 4. 改写边界

本包对源文档做了三类处理，均可复核：

| 处理 | 做法 | 例子 |
| --- | --- | --- |
| 短句直引 | 关键规则原样引用并标 F 编号 | 像素级保持原话（F-013）、四个透明触发词（F-021） |
| 结构重排 | 把散落在 callout、亮点表、技巧章的同一规则合并成一张表 | 9 条技巧 → 写作顺序表 |
| 释义补充 | 只在明确标注处补充本包的解读 | 词库第二列释义、"覆盖维度"标注 |

未做的一类处理是**删改原文数字**：95% 原样保留并标 ⚠️（F-016），不替换成本包的估计值。

## 5. 已知局限

1. **无实测**：本包未调用模型生成任何图片，全部能力结论为文档口径，未做行为验证。
2. **示例提示词不完整**：44 条 blockquote（F-039）是正文可见的全部提示词，但示例图对应的模型版本、参考图编号、迭代次数、采样参数均未公开；据此复现只能得到"近似同类"的结果。
3. **词条无定义**：22 组风格词 + 18 组美学词（F-036）无任何参数化说明（F-010），强度与稳定性不可比。
4. **单一信源**：没有第二份独立资料交叉验证能力描述；三篇历史文档（F-038）为同厂商同系列，不构成独立信源。
5. **时效**：产品文档随版本更新，本包锚定 revision 3367；复核触发条件见[核验](verification.md)。

## 6. 敏感度与落位说明

源文档位于企业域名下（`bytedance.larkoffice.com`），按启动协议内容敏感度预检属**私域信源**；按用户指示落位到本仓 bundles 分组，故在本包 frontmatter 标 `sensitivity: internal`，并在此记录这一判断：

- 正文内容为产品使用指南（能力说明、提示词写法、场景玩法），未含个人信息、客户数据、内部指标或未发布路线图。
- 197 张示例图未复制，降低了素材外流面。
- **若本仓或本站为公开可见**，`sensitivity: internal` 这一标记需要复核：或改为公开口径（仅保留方法论层内容），或把本包迁至私有仓库。此事本包不擅自决定，记录待决。
