---
type: Reference
title: XERJ × DeepSeek Search/Fetch 对比——信源登记
description: 对比束的信源登记——XERJ 源码快照、DeepSeek 官方 API 文档（在线核验）、仓库内两个 DeepSeek 知识包，以及三者的采信关系
tags: [xerj, deepseek, 对比, 信源登记, 检索选型]
generated: { by: source-code-to-okf-wiki/R, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-snapshot
    resource: /references/source.md
    title: XERJ 源码快照登记
  - id: deepseek-search-guide
    resource: https://api-docs.deepseek.com/zh-cn/guides/search
    title: DeepSeek API 文档——网页搜索与抓取
  - id: deepseek-pricing
    resource: https://api-docs.deepseek.com/zh-cn/quick_start/pricing
    title: DeepSeek API 定价页
---

# XERJ × DeepSeek Search/Fetch 对比——信源登记

## 三类信源与采信关系

| 侧 | 信源 | 身份 | 采信规则 |
|---|---|---|---|
| **XERJ** | `external/dao/search/xerj` @ `51ff219276d7e55d9d85b4938e8b94f235f9d099` | 源码快照（18 crate、552 个 `.rs`、521,684 行） | 以**代码**为唯一事实源；官方文档仅作意图与边界的辅助材料（该仓库的文档站首页即声明「If the docs and the code disagree, the code is right」） |
| **DeepSeek** | `https://api-docs.deepseek.com/zh-cn/guides/search`（在线核验）+ `/zh-cn/quick_start/pricing` | 官方 API 文档 | 以**在线官方文档**为事实源，本轮已逐条复核 |
| **仓库内既有束** | `jishu/ai/ecosystems/deepseek-search-fetch/`（7 篇）、`jishu/ai/practice/deepseek-v41-flash-1017/`（5 概念 + 2 参考） | 本知识库内已有的 DeepSeek 知识包 | **只读引用**；本束不重复其内容，只在需要对比时交叉链接 |

## 本轮做了什么核验

**DeepSeek 侧**：本轮**重新拉取在线官方文档**逐条复核，而非直接采信仓库内既有束的转述。复核项与结论：

| 复核项 | 官方文档 | 结论 |
|---|---|---|
| 两个端点路径 | `POST https://api.deepseek.com/v1/tools/search`、`POST /v1/tools/fetch` | ✅ 与既有束一致 |
| 鉴权 | `Authorization: Bearer <DeepSeek API Key>`，`Content-Type: application/json` | ✅ |
| Search 请求字段 | `query`（1～128 Unicode 字符，必填）、`count`（1～50，默认 10）、`ori_question`、`localization`、`need_content`（默认 false） | ✅ |
| 搜索语法 | `site:` `-site:` `-词` `-"短语"` `"短语"` `lang:` `after:` `before:` | ✅ 逐条一致 |
| results 字段 | `rerank_score`（0～3，≥1.5 优质）、`title`、`url`、`snippet`（100～200）、`summary`（600～800）、`content`、`site_name`、`site_icon`、`date`（UTC RFC 3339）、`authority`（0～4，-1 未知，≥3 极权威） | ✅ |
| Fetch 请求/响应 | `url`（≤8192 字符，须含 host 的 HTTP/HTTPS URL，不得带用户名密码）；响应 `title` + `content`（Markdown） | ✅ |
| 错误格式与状态码 | OpenAI 兼容格式，`param` 恒为 `null`；400/401/402/403/404/408/413/429/500/504 | ✅ |
| 404 的成因 | 官方原文列出五种：URL 不可用、被站点策略拦截、目标站点返回错误、内容类型不受支持、页面没有可提取的 Markdown 正文 | ✅ 与既有束 [03 错误处理](../../../ecosystems/deepseek-search-fetch/concepts/03-error-handling.md) 一致 |
| 计费 | Search 与 Fetch 各「每 1,000 次成功请求 5 元」；只有 HTTP 200 且产生结果才计费；`count` 不影响价格 | ✅ |
| 限速 | 账号级 Search 100 QPS / Fetch 25 QPS，两者独立，与模型并发独立；Fetch 另有域名级限制 | ✅ |
| 计费切换时点 | 「当前用户在 DeepSeek Harness/Claude Code/Codex 中使用 DeepSeek API 时，已经会通过 Server 端工具调用访问到 Search/Fetch 接口，这部分……目前未计费，并将于北京时间 2026 年 11 月 1 日 00:00 起按次收取调用费用」 | ✅ 逐字一致 |
| 只读声明 | 「Search 和 Fetch 都是只读请求」 | ✅ |

**XERJ 侧**：全部事实来自既有 xerj 束的第一、二轮（已在各束内完成 Grep 级验证与计数复核），本束**不重复采集**，只做跨束引用与对照。

## 交叉引用

| 主题 | 既有束 | 本束对应文档 |
|---|---|---|
| XERJ 整体架构与定位 | [XERJ 源码学习知识包](../../../frameworks/xerj/index.md) | [00 对比框架与结论](../concepts/00-comparison-frame.md) |
| XERJ 检索与响应裁剪 | [04 检索路径与响应裁剪](../../../frameworks/xerj/concepts/04-search-query-path.md) | [02 上下文成本与接口契约](../concepts/02-context-cost-and-contracts.md) |
| XERJ 记忆与第二大脑 | [06 智能体记忆与第二大脑](../../../frameworks/xerj/concepts/06-agent-memory-and-brain.md) | [01 语料归属](../concepts/01-corpus-ownership.md) |
| XERJ 基准诚实性 | [07 ES 兼容与基准诚实性](../../../frameworks/xerj/concepts/07-es-compat-and-benchmarks.md) | [03 失败语义与可诊断性](../concepts/03-failure-semantics-and-boundaries.md) |
| DeepSeek Search/Fetch API | [DeepSeek 网页搜索与抓取 API](../../../ecosystems/deepseek-search-fetch/index.md) | 全篇 |
| DeepSeek 计费倒计时与成本账 | [DeepSeek V4.1-Flash-1017](../../deepseek-v41-flash-1017/index.md) | [04 成本曲线与选型](../concepts/04-cost-model-and-selection.md) |

## 事实编号约定

本束使用**独立编号** `F-001` 起，与既有束的编号体系并行（xerj 束 F-001～F-362、deepseek-v41-flash-1017 束 F-0xx、deepseek-search-fetch 束未编号）。每条事实标注**所属侧**（XERJ / DeepSeek / 对照），便于逐侧回查。

## 相关参考

- [事实清单](facts.md)：本束全部编号事实与核验备注
- [核验记录](verification.md)：本轮核验方法与结论
- [References 索引](index.md)：本目录汇总
