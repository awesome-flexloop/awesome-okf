---
okf_version: "0.2"
type: concept
title: 安装现状、企业落地与边界约束
description: 仓库安装配置现状（无 requirements.txt）、企业团队四步用法、五类适用场景、五项局限与 License 非商用约束（F-025~F-045）
tags: [rag, practice, license, team-adoption, limitations]
generated:
  by: seven-concepts-cmd
  at: "2026-10-31T11:00:00+08:00"
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/WsgnBpEtTytatRFkKUlfeA
  - id: github-rag-techniques
    url: https://github.com/NirDiamant/RAG_Techniques
---

# 安装现状、企业落地与边界约束

> **性质提示**：本篇的「企业团队怎么用」四节为**博文作者的落地建议**（F-031~F-035），非仓库官方文档内容；适用场景与局限亦以作者观点为主（F-036~F-044），已在表中标注。

## 安装与配置现状

仓库 Getting Started 很短，博文称「就三步」（F-025）：

```
git clone https://github.com/NirDiamant/RAG_Techniques.git

cd RAG_Techniques
```

然后呢？**没有然后了**（F-025）。

> ⚠️ **关键事实（P0 已核验）**：**这个仓库没有 `requirements.txt`**（F-026 / F-050，全树检索 COUNT=0）。根目录只有 `helper_functions.py`、`CITATION.cff`、`CONTRIBUTING.md`、`LICENSE`、`README.md`、`REVIEW.md`、`AGENTS.md`、`llms.txt`、`.pr_agent.toml`。依赖散在每个 notebook 首个 cell 里（F-027）。

**博文建议的路径**（F-028 / F-029）：

1. **先用 Colab 跑通**——官方每个技术都挂了 Colab 徽章，点进去环境现成；等确认某篇真有用，再本地配环境，能省掉大量版本冲突时间；
2. **本地复现示意流程**：`jupyter lab` → 打开 `all_rag_techniques/simple_rag.ipynb` → 执行首个 cell 装依赖、配置 `OPENAI_API_KEY`；
3. **涉 Milvus 的篇目**（`graphrag_with_milvus_vectordb`）：要么本地起 Milvus，要么用 Zilliz Cloud 免费集群，连上后把 Public Endpoint 与 Token 填进 notebook（F-030）。

## 企业团队怎么用（作者建议四步）

### 1. 团队改造思路（F-031 / F-032）

- **别一次推 42 篇**；
- 先做一次 RAG 现状盘点，把团队当前问题归到四类：**召回不准、答非所问、多跳失败、没法评估**；
- 按类挑 **5-8 篇**，每人认领一篇，做 20 分钟内部分享，**要求讲完必须带一段自己业务数据上的复现**；
- 价值不在学技术，在于**让团队有一套共同的参照系**——以后讨论要不要上重排序，大家说的是同一个东西。

### 2. 批量部署方案（F-033）

fork 到内部 GitLab，**先看 License**（见下文合规约束）。部署侧做三件事：

| 事项 | 说明 |
|------|------|
| **锁环境** | 仓库没有 requirements.txt，自己得有一份，否则半年后全员环境不一致 |
| **清空 notebook 输出再入库** | 原仓库 37MB 量级、图片占大头，输出不清会越滚越大（37MB 为博文口径） |
| **建索引表** | 字段：技术名 / 解决什么问题 / 前置依赖 / 对应业务线 / 谁认领 |

### 3. 流水线集成（F-034）

| 点位 | 做法 |
|------|------|
| **评估进 CI** | `evaluation/` 目录思路可抽成固定问题集，每次改切分策略或 prompt 就跑一遍——RAG 改动更需要回归，不是感觉 |
| **脚本转内部工具** | 21 个 `.py` 比 notebook 好改；挑高频的（重排序、融合检索、上下文压缩）包成内部函数接入现有检索服务 |
| **Java 团队注意** | notebook 是 Python 生态，LangChain/LlamaIndex 实现搬不过来。SpringAI 对应 Advisor / RetrievalAugmentor / QueryTransformer，LangChain4j 对应 ContentRetriever / QueryTransformer |

> **要搬的是策略，不是代码**——直接拷 Python 代码进 Java 项目，「最后一定是一地鸡毛」。

### 4. 团队规范定制（F-035）

四份规范可基于该仓库直接落地：

- **切分规范**：按文档类型定基线 chunk 大小与重叠，把 `choose_chunk_size` 的方法固化成脚本；
- **检索规范**：默认必须配重排序；多路召回以融合检索为基线；
- **评估规范**：任何 RAG 改动必须带评估集结果，不接受口头「效果变好了」；
- **提示词规范**：上下文模板版本化，跟代码一起 review。

## 五类适用场景（作者观点，F-036）

- RAG 上线后**效果不稳**，需要系统排查而不是瞎试参数；
- 要做**多跳或关系型问答**，想先评估 Graph RAG、LightRAG 的改造成本；
- 要给团队做 **RAG 内训**，需要一套能跑、带参考文献的教材；
- 要设计 **RAG 评估体系**，`evaluation/` 目录可直接当起点；
- **技术选型阶段**，想知道 CRAG、Self-RAG 这类方案到底解决什么、代价多大。

## 合规约束：License 非商用（重点）

> ✅ **P0 已核验**（F-037 / F-038 / F-052 / F-056）：LICENSE 关键条款逐字命中；GitHub API 对该仓库 License 字段返回 NOASSERTION（页面显示为「其它」）。

GitHub 页面显示 License 是「其它」；点进 LICENSE 原文，是 **Custom License Agreement**，**不属于任何标准开源协议**。关键条款：

1. 只授予**非商业用途**的使用、复制、修改、分发；
2. **商业用途必须取得作者书面许可**；
3. 所有商业权利由作者独占。

**第 3 条贡献条款**：提交 Contribution 即授予作者**独占、永久、不可撤销、全球、免费**的许可，包含商业再许可（原文含 `exclusive, perpetual, irrevocable, worldwide, royalty-free license`）——「你贡献的代码作者可以商用，你不能」。

**实践含义**：

| 用途 | 是否可行 |
|------|---------|
| 学习、内部研究、非商业项目 | ✅ 可行 |
| 直接拷 notebook 代码进公司商业产品 | ❌ **违约** |
| 商业产品要用 | 取得作者书面许可，或只借鉴思路自己重写实现 |

博文建议：**转载和二次分发前，先看一眼 License 原文**（F-044）。

## 五项局限（F-039 / F-040 等）

| 局限 | 说明 |
|------|------|
| ① License 非商用 | 见上节，商业用途受限 |
| ② 贡献条款对贡献者不利 | 提交 PR 即授予作者商业再许可（F-038） |
| ③ **它是学习资源，不是库** | 没有 pip 包、没有 API 稳定承诺、没有语义化版本（F-039） |
| ④ 没有统一依赖清单 | 无 requirements.txt，跨篇依赖冲突是常事，LangChain 系列版本变动快（F-026） |
| ⑤ 跑一遍有成本 | 多数 notebook 默认走 OpenAI，42 篇全跑一遍 token 开销不小——挑 3-5 篇够了（F-040） |

## 四个具体的坑（作者观点，F-041）

| 坑 | 说明 |
|----|------|
| 照抄参数不回测 | chunk size、top_k 与语料强相关——别人的 500 到你这里可能是 800 |
| 忽略 embedding 模型差异 | notebook 里的模型和你线上不是同一个，结论不能直接迁移 |
| 把 demo 数据当效果证明 | notebook 语料都是精选小样本，跑通不等于在十万份文档上有效 |
| 以为看完就会了 | 42 篇刷一轮要一两周，但不改自己系统代码，两周后基本全忘——**挑一篇、改一处，比看十篇有用** |

## 作者结论

> 作者观点（F-042 / F-043）：42 个 notebook 更像 42 个病例——不需要全读完，需要的是**知道自己现在是什么症状，然后翻到对应那一页**。对个人，它省的是试错时间；对团队，正确用法是**共建一张内部能力地图**（谁认领哪一段、对应哪个业务、验证了什么结论），发个链接让大家自学最后一定是零产出。两条前提必须记住：**它不能商用，它也不是库**——当教材用，别当依赖用。

## 主题关联

- [00-intro](./00-intro.md)：项目定位与核心数据
- [01-techniques](./01-techniques.md)：七段技术机制与代表性架构
