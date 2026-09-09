---
type: example
title: 一次学术搜索的完整调用
description: "基于 scholar.sh 真实脚本与 examples/scholar-search.md 示例，演练学术搜索的完整流程：查询分析、带参数搜索、上下文追问，以及响应结构解读。"
tags: [scholarclaw, example, scholar-search, walkthrough]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: ScholarClaw 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: ScholarClaw 架构洞察
---

# 一次学术搜索的完整调用

本演练基于 `scripts/scholar.sh` 的真实参数（F-sc-032）与 `examples/scholar-search.md` 示例文档（F-sc-054），场景为：调研"多模态学习"的最新进展。

## 前置条件

已完成安装（`install.sh` 落盘 `~/.scholarclaw` 并生成 `sc-*` 别名，F-sc-042），环境变量或 `~/.scholarclaw/config.json` 中已配置服务端地址与 apiKey（F-sc-002、F-sc-003）。下文用 `./scripts/scholar.sh` 表示直接调用脚本；已装别名的环境可用 `sc-scholar` 等价替换。

## 第一步：先分析查询，不执行搜索

`--analyze-only` 参数把请求从默认的 `POST /scholar/search` 切换为 `POST /scholar/analyze`（F-sc-032），只返回 AI 对查询的分析结果：

```bash
./scripts/scholar.sh -q "How do vision transformers compare to CNNs?" --analyze-only
```

响应（对应 `QueryAnalysis` 类型，含 core_question/keyword_queries/semantic_queries/required_criteria/nice_to_have_criteria/time_range/search_engine，F-sc-023）：

```json
{
  "core_question": "What is the comparative performance of vision transformers versus convolutional neural networks?",
  "keyword_queries": [
    "vision transformer vs CNN",
    "ViT comparison CNN",
    "transformer convolutional benchmark"
  ],
  "semantic_queries": [
    "comparing self-attention to convolution for image recognition",
    "when to use transformers over CNNs for computer vision"
  ],
  "required_criteria": ["comparative study", "benchmark results"],
  "nice_to_have_criteria": ["ImageNet evaluation", "computational cost analysis"],
  "time_range": { "start": "2020", "end": null },
  "search_engine": "arxiv"
}
```

这一步的价值：在烧掉一次完整搜索之前，先确认 AI 理解的研究问题、关键词与时间范围是否符合预期；不合适就改写查询。

## 第二步：执行完整学术搜索

```bash
./scripts/scholar.sh -q "What are the latest advances in multimodal learning?" -e arxiv -m 10
```

参数说明（忠实于 `scholar.sh` 的选项定义，F-sc-032）：`-q/--query` 必填；`-e/--engine` 指定搜索引擎（如 `pubmed`、`arxiv`，不传则由服务端自动选择）；`-m/--max-results` 限制返回条数（脚本默认值 20）。脚本以 curl `--max-time 60` 发送 `POST /scholar/search`（F-sc-032），请求体对应 `ScholarSearchRequest`（含 query/max_results/search_engine/enable_citation_expansion/enable_rerank，F-sc-023）。

响应（`ScholarSearchResponse`，含 query/results/summary/analysis/usage/total_results，F-sc-023）：

```json
{
  "query": "What are the latest advances in multimodal learning?",
  "results": [
    {
      "title": "Paper Title",
      "abstract": "Abstract...",
      "url": "https://arxiv.org/abs/...",
      "authors": "Author 1, Author 2",
      "year": 2024,
      "source": "arxiv",
      "rerank_score": 0.95,
      "citation_count": 150
    }
  ],
  "summary": "Recent advances in multimodal learning include...",
  "total_results": 20
}
```

要点解读：

- `summary` 是 AI 生成的调研摘要，快速回答研究问题；
- `rerank_score` 体现语义重排得分——默认开启引用扩展与重排（F-sc-032），追求速度时可分别用 `--no-citation-expansion`、`--no-rerank` 关闭（对应 `enable_citation_expansion`/`enable_rerank` 两个布尔字段，F-sc-023）；
- 输出格式取决于本机是否有 jq：有 jq 时为美化 JSON，无 jq 时为原始紧凑 JSON（F-sc-030），脚本化解析请用 `jq -c` 归一化。

## 第三步：带上下文追问

`-c/--context` 传入对话历史 JSON 数组（对应 `ScholarSearchRequest.messages`，F-sc-023），实现多轮调研：

```bash
./scripts/scholar.sh \
  -q "What about their computational efficiency?" \
  -c '[{"role":"user","content":"Tell me about vision transformers"},{"role":"assistant","content":"Vision Transformers (ViT) apply transformer architecture to image patches..."}]'
```

TS 客户端对照写法（`scholarSearch()` 同路由，F-sc-012）：

```typescript
const result = await client.scholarSearch({
  query: 'What are the scaling laws?',
  messages: [
    { role: 'user', content: 'Tell me about GPT models' },
    { role: 'assistant', content: 'GPT models are large language models...' },
  ],
  max_results: 10,
});
```

## 常见变体

```bash
# 文献综述：放宽结果数量
./scripts/scholar.sh -q "What is the state of the art in neural machine translation?" -m 30

# 生物医学问题：切换 PubMed 引擎
./scripts/scholar.sh -q "What are the mechanisms of mRNA vaccines?" -e pubmed
```

## 排错提示

- 请求挂起超过 60 秒会触发脚本内 curl 超时（F-sc-032），属预期上限而非故障；
- 服务端返回 503/504 时，SKILL.md 契约建议按 2s/4s/8s 退避重试最多 3 次（F-sc-048）；
- 401/403/429 判定为认证类错误，检查 apiKey 配置（F-sc-020）。

## 相关概念

- [/concepts/01-server-client.md](/concepts/01-server-client.md)
- [/concepts/02-shell-toolchain.md](/concepts/02-shell-toolchain.md)
- [/concepts/03-skill-contract.md](/concepts/03-skill-contract.md)
