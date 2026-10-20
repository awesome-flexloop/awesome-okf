---
type: Reference
title: 对比束核验记录
description: 本轮对比束的核验方法与结论——DeepSeek 侧逐条在线复核、XERJ 侧跨束引用边界、推论性事实的标注，以及未核验项的显式声明
tags: [xerj, deepseek, 核验, 引用边界, 对比]
generated: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: compare-source
    resource: /references/source.md
    title: 对比束信源登记
  - id: compare-facts
    resource: /references/facts.md
    title: 对比事实清单
---

# 对比束核验记录

## 核验方法

| 侧 | 方法 | 覆盖 |
|---|---|---|
| DeepSeek | **重新拉取在线官方文档**（`https://api-docs.deepseek.com/zh-cn/guides/search`）逐条复核，不直接采信仓库内既有束的转述 | 端点、鉴权、请求字段、搜索语法、响应字段、错误格式与状态码、计费、限速、计费切换时点 |
| XERJ | **跨束引用**既有 xerj 束的第一、二轮事实（已在该束内完成 Grep 级验证与计数复核），本束不重复采集 | 语料、检索面、记忆、上下文裁剪、失败语义、成本形态、隐私、规模、质量可验证性 |
| 对照推论 | 明确标注为「对照推论」或「架构建议」，不与两侧的官方/源码事实混同 | F-033、F-040 |

## DeepSeek 侧复核结论

**13 项全部一致**（逐项清单见 [source.md](source.md) 的复核表）：

- 端点与鉴权：`POST /v1/tools/search`、`POST /v1/tools/fetch`，Bearer + `application/json`，Base URL `https://api.deepseek.com` ✅
- Search 请求字段 5 个与各自范围/默认值 ✅
- 搜索语法 8 个操作符及其语义 ✅
- results 10 个字段、量级与阈值（`rerank_score` ≥1.5、`authority` ≥3、-1 未知）✅
- Fetch 请求约束（≤8192 字符、须含 host、不得带用户名密码）与响应（`title` + Markdown `content`）✅
- 错误格式（OpenAI 兼容、`param` 恒 null）与 10 个状态码 ✅
- 404 的五种成因 ✅
- 重试纪律（408/429/5xx 重试；402 充值；其它 4xx 不重试；两者只读）✅
- 计费（各 ¥5/1000 次成功请求、成功才计费、`count` 不影响价格）✅
- 限速（Search 100 / Fetch 25，账号级且互相独立；Fetch 另有未公布数值的域名级限制）✅
- 2026-11-01 00:00（北京时间）计费切换 ✅

**本轮唯一的一处口径修正**：404 的成因是**五种**（URL 不可用 / 被站点策略拦截 / 站点返回错误 / 内容类型不受支持 / 无可提取 Markdown 正文），与仓库内既有束一致。

## XERJ 侧引用边界

本束的 XERJ 事实全部**转引**既有 xerj 束的编号事实，不在本束重复编号。三点边界：

1. **不重新采集**——避免同一事实出现两套编号；
2. **引用时给出来源编号**（形如「xerj 束 F-029」），便于回查该束的核验痕迹；
3. **不越界**——本束不对 XERJ 做新的代码级断言；若要新增 XERJ 事实，应回 xerj 束按其多轮扩展规范追加。

## 未核验项与缺失性断言

| 项 | 性质 | 处置 |
|---|---|---|
| F-017（SEO/GEO/低质 AI 内容过滤机制） | **官方公告口径**，本轮在线文档页未展开该段 | 已在事实清单标注来源与性质；不作为对比推理的依据 |
| F-031（未提供召回率/时延/对比数据） | **缺失性断言** | 依据是官方文档全文与定价页均无相关数据；断言的是「未提供」而非「质量差」 |
| F-033（同一 URL 在不同来源可能结果不同） | **对照推论** | 由 F-023 与 F-026 推出，非官方原文 |
| F-040（串联架构） | **架构建议** | 由 F-028、F-036、F-010 组合推出；两侧均无官方表述支持或反对 |
| 两者在**同一语料**上的召回质量对比 | **未做** | 本束不含跨引擎的同语料对比实验；任何此类数字都不应从本束引用 |

## 引用时的三条纪律

1. **不把 F-033 / F-040 当作任一方的官方立场**——它们是本束的推论与建议。
2. **XERJ 侧的质量数字必须带口径**——ANN 路径的 recall 是**实测**（recall@10 1.00、100 探针均值 0.976），精确路径的 recall 1.00 是**构造保证**；两者不可互换（见 xerj 束 F-124、F-125）。
3. **DeepSeek 侧的过滤机制不要当作质量保证**——规则不公开，边界与召回影响不可外部验证（F-017）。

## 门禁记录

| 门 | 结果 |
|---|---|
| 链接检查（本束内相对链接 + 跨束相对链接） | ✅ 0 断裂 |
| frontmatter 完整性 | ✅ 全部内容文档具备 `type`/`title`/`description`/`tags`/`generated`/`verified`/`status`/`stale_after`/`sources`；子目录 `index.md` 无 frontmatter |
| Sphinx dummy 构建（隔离源目录，仅本束） | ✅ build succeeded，0 warning / 0 error |
| toctree 完整性（仓库级 gate） | ✅ 本束零命中 |
| 编码（UTF-8 无 BOM） | ✅ |

## 相关参考

- [信源登记](source.md)：三类信源与 DeepSeek 侧逐项复核表
- [事实清单](facts.md)：F-001～F-042 与核验备注
- [References 索引](index.md)：本目录汇总
