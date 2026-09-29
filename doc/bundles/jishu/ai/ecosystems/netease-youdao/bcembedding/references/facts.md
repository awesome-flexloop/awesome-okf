---
type: reference
title: BCEmbedding 源码事实清单
tags: [embedding, reranker, rag, netease-youdao, source-code]
status: stable
sources:
  - id: bcembedding-vendor
    resource: vendor/netease-youdao/BCEmbedding/
    title: netease-youdao/BCEmbedding（SpecWeave vendor 子模块，只读）
---

# BCEmbedding 事实清单（F-bc 系列）

> 本文件为 R 阶段事实采集产物：全部事实取自 `vendor/netease-youdao/BCEmbedding/` 子模块源码与 README，逐条登记、零推测。"证据位置"列为 vendor 仓库根相对路径 + 符号名。数量陈述均经实际 Glob/Grep 计数。

## 包元数据与依赖

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-bc-001 | setup.py 声明包名 `BCEmbedding`、版本 `0.1.5`、许可证 `apache-2.0`、作者 `Netease Youdao, Inc.` | `setup.py`: `setup(name=..., version='0.1.5', ...)` |
| F-bc-002 | `install_requires` 共 4 项：`torch>=1.6.0`、`transformers>=4.35.0,<4.37.0`、`datasets`、`sentence-transformers` | `setup.py`: `install_requires` |
| F-bc-003 | setup.py 未声明 `python_requires`；README 安装示例使用 `conda create --name bce python=3.10` | `setup.py`（无 python_requires）；`README.md`: Manual/Installation |
| F-bc-004 | 顶层包 `BCEmbedding/__init__.py` 执行 `from .models import *`；`BCEmbedding/models/__init__.py` 以 `__all__` 导出 `EmbeddingModel` 与 `RerankerModel` | `BCEmbedding/__init__.py`；`BCEmbedding/models/__init__.py`: `__all__` |

## EmbeddingModel（`BCEmbedding/models/embedding.py`）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-bc-005 | `class EmbeddingModel` 构造签名为 `__init__(model_name_or_path='maidalun1020/bce-embedding-base_v1', pooler='cls', use_fp16=False, device=None, **kwargs)`，内部以 `AutoTokenizer.from_pretrained` 与 `AutoModel.from_pretrained` 加载 | `BCEmbedding/models/embedding.py`: `class EmbeddingModel`, `__init__` |
| F-bc-006 | `pooler` 断言仅允许 `'cls'` 与 `'mean'`，断言失败信息为 `` `pooler` should be in ['cls', 'mean']. 'cls' is recommended! `` | `embedding.py`: `__init__` 中 `assert pooler in ['cls', 'mean']` |
| F-bc-007 | device 解析逻辑：`device=None` 时按 `torch.cuda.device_count()>0` 选 `cuda`/`cpu`；device 为数字字符串时格式化为 `'cuda:{N}'`；支持 `'xpu'`（`import intel_extension_for_pytorch as ipex` 并 `ipex.optimize`）；其余取值抛 `ValueError` | `embedding.py`: `__init__` device 分支 |
| F-bc-008 | `use_fp16=True` 时 `model.half()`；随后 `model.eval()` 并 `model.to(self.device)`；`num_gpus>1` 时以 `torch.nn.DataParallel` 包装 | `embedding.py`: `__init__` |
| F-bc-009 | `encode` 签名为 `encode(sentences, batch_size=256, max_length=512, normalize_to_unit=True, return_numpy=True, enable_tqdm=True, query_instruction="", **kwargs)`；`return_numpy=True` 时返回 numpy ndarray | `embedding.py`: `def encode` |
| F-bc-010 | encode 输入流：`str` 输入先转为单元素 list；`query_instruction` 为非空字符串时拼接为每条句子的前缀；按 batch 经 `tokenizer(padding=True, truncation=True, max_length=max_length, return_tensors="pt")` 编码并移至 device | `embedding.py`: `encode` 循环体 |
| F-bc-011 | encode 输出流：`pooler='cls'` 取 `outputs.last_hidden_state[:, 0]`；`pooler='mean'` 按 `attention_mask` 加权平均；`normalize_to_unit=True` 时按行 L2 范数归一化；各 batch 结果 `torch.cat(dim=0)` 后 `.numpy()` 返回 | `embedding.py`: `encode` pooling 分支 |
| F-bc-012 | `num_gpus>1` 时 `encode` 内 `batch_size` 乘以 `num_gpus` | `embedding.py`: `encode` 首行分支 |

## RerankerModel（`BCEmbedding/models/reranker.py`）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-bc-013 | `class RerankerModel` 构造签名为 `__init__(model_name_or_path='maidalun1020/bce-reranker-base_v1', use_fp16=False, device=None, **kwargs)`，以 `AutoTokenizer` 与 `AutoModelForSequenceClassification.from_pretrained` 加载 | `BCEmbedding/models/reranker.py`: `class RerankerModel`, `__init__` |
| F-bc-014 | RerankerModel 的 device 分支仅含 `cpu`、`cuda:N`、`cuda`，无 `xpu` 分支；非法取值抛 `ValueError("Please input valid device: 'cpu', 'cuda', 'cuda:0', '0' !")` | `reranker.py`: `__init__` device 分支 |
| F-bc-015 | 构造时读取 `self.max_length = kwargs.get('max_length', 512)` 与 `self.overlap_tokens = kwargs.get('overlap_tokens', 80)`，供长文本分块预处理使用 | `reranker.py`: `__init__` 末尾 |
| F-bc-016 | `compute_score(sentence_pairs, batch_size=256, max_length=512, enable_tqdm=True)` 断言 `sentence_pairs` 为 list；首元素为 str 时自动包装为二元组列表；对 `logits.view(-1,).float()` 施加 `torch.sigmoid` 后返回 Python float 列表；仅一个 pair 时返回标量（float） | `reranker.py`: `def compute_score` |
| F-bc-017 | `rerank(query, passages, batch_size=256)` 返回字典，键为 `'rerank_passages'`、`'rerank_scores'`、`'rerank_ids'`；`rerank_ids` 为分数降序排列的原文索引（`np.argsort(merge_scores)[::-1].tolist()`） | `reranker.py`: `def rerank` 返回值 |
| F-bc-018 | rerank 先过滤 passages：仅保留非空 str 且截断为 `p[:128000]`；`query` 为 `None`/空串或 passages 为空时，直接返回 `{'rerank_passages': [], 'rerank_scores': []}` | `reranker.py`: `rerank` 开头 |
| F-bc-019 | rerank 长文本流程：调用 `reranker_tokenize_preproc` 得 `(sentence_pairs, sentence_pairs_pids)`，逐 batch 以 `tokenizer.pad` 补齐后推理取 sigmoid，同一 passage 的多个 chunk 分数取 `max` 合并，再整体降序排序 | `reranker.py`: `rerank` 主体 |
| F-bc-020 | `num_gpus>1` 时 `compute_score` 与 `rerank` 内 `batch_size` 均乘以 `num_gpus` | `reranker.py`: `compute_score`、`rerank` 首行分支 |

## 工具函数（`BCEmbedding/utils/`）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-bc-021 | `reranker_tokenize_preproc(query, passages, tokenizer=None, max_length=512, overlap_tokens=80)` 断言 `tokenizer is not None`，返回 `(res_merge_inputs, res_merge_inputs_pids)` 二元组 | `BCEmbedding/models/utils.py`: `def reranker_tokenize_preproc` |
| F-bc-022 | 该函数先 `tokenizer.encode_plus(query, truncation=False, padding=False)`；`max_passage_inputs_length = max_length - len(query_inputs['input_ids']) - 2`，并断言其 `> 100`，否则报错 `Your query is too long! Please make sure your query less than 400 tokens!` | `models/utils.py`: `reranker_tokenize_preproc` |
| F-bc-023 | 超长 passage 按 `max_passage_inputs_length` 滑窗切分，实际重叠量为 `min(overlap_tokens, max_passage_inputs_length//4)`；每个 chunk 以 `sep_token_id` 与 query 输入拼接，存在 `token_type_ids` 时追加对应长度全 1 列表 | `models/utils.py`: `_merge_inputs` 与滑窗循环 |
| F-bc-024 | `logger_wrapper(name='BCEmbedding')` 调用 `logging.basicConfig(level=logging.INFO)`，格式串为 `'%(asctime)s - [%(levelname)s]-%(name)s->>> %(message)s'`，返回 `logging.getLogger(name)` | `BCEmbedding/utils/logger.py`: `def logger_wrapper` |
| F-bc-025 | `query_instructions.py` 中 `query_instruction_for_retrieval_dict` 共 17 个键：6 个 `BAAI/bge-*-en*` 英文模型（指令 `"Represent this sentence for searching relevant passages: "`）、7 个 `BAAI/bge-*-zh*` 中文模型（指令 `"为这个句子生成表示以用于检索相关文章："`）、4 个 `intfloat/*e5*` 模型（指令 `"query: "`）；`passage_instruction_for_retrieval_dict` 共 4 个键（intfloat e5 系，指令 `"passage: "`） | `BCEmbedding/utils/query_instructions.py`（键行经 Grep 计数：17+4） |
| F-bc-026 | `BAAI/bge-large-zh-noinstruct` 对应的 query 指令值为 `None`；键 `"BAAI/bge-small-zh-v.15"` 按源码原文登记（点号写法与同文件 `v1.5` 系列不一致） | `query_instructions.py`: 字典条目 |

## 模型清单（README.md）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-bc-027 | README 模型清单共 2 个模型：`bce-embedding-base_v1`（类型 `EmbeddingModel`，语言 ch/en，参数量 279M）与 `bce-reranker-base_v1`（类型 `RerankerModel`，语言 ch/en/ja/ko，参数量 279M），权重发布于 HuggingFace `maidalun1020` 组织 | `README.md`: Model List 表 |
| F-bc-028 | README 声明：`RerankerModel` 支持长 passage 重排序（"more than 512 tokens, less than 32k tokens"）；`EmbeddingModel` "does not need specific instructions" | `README.md`: Our Goals |
| F-bc-029 | README 给出三种调用路径：`BCEmbedding` 封装类、原生 `transformers`（`AutoModel`/`AutoModelForSequenceClassification` + cls pooler + L2 归一化）、`sentence-transformers`（`SentenceTransformer`/`CrossEncoder`） | `README.md`: Quick Start 三小节 |
| F-bc-030 | README 安装方式：`pip install BCEmbedding==0.1.5`，或源码目录 `pip install -v -e .` | `README.md`: Manual/Installation |
| F-bc-031 | README 集成示例的版本要求：LangChain 为 `langchain==0.1.0`、`langchain-community==0.0.9`、`langchain-core==0.1.7`、`langsmith==0.0.77`；LlamaIndex 为 `llama-index==0.9.42.post2`；MTEB 评测为 `mteb==1.1.1`；RAG 评测要求 `transformers==4.36.0` 与 `llama-index==0.9.22` | `README.md`: Integrations / Evaluation 小节 |

## 评测模块（`BCEmbedding/evaluation/c_mteb/`）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-bc-032 | `c_mteb/__init__.py` 通配导入 `.Reranking` 与 `.Retrieval`，显式导入 `YDDRESModel`，并 `from mteb import MTEB` | `BCEmbedding/evaluation/c_mteb/__init__.py` |
| F-bc-033 | `Retrieval.py` 定义 13 个 `AbsTaskRetrieval` 子类（Grep 计数 `class CrosslingualRetrieval*` = 13）：Books、Finance、Law、Others、Paper、Wiki 六个领域各含 En2Zh/Zh2En 双向，Qas 仅含 En2Zh；均注册 `hf_hub_name='maidalun1020/CrosslingualRetrieval*'`、`eval_splits=['dev']`、`main_score='ndcg_at_3'` | `c_mteb/Retrieval.py` |
| F-bc-034 | `Reranking.py` 定义 4 个 `AbsTaskReranking` 子类：`T2RerankingZh2En`、`T2RerankingEn2Zh`、`MMarcoRerankingZh2En`、`MMarcoRerankingEn2Zh`，`eval_langs` 为 zh-en/en-zh，`main_score='map'` | `c_mteb/Reranking.py` |
| F-bc-035 | `Reranking.py` 模块级函数 `evaluate` 被赋值给 `AbsTaskReranking.evaluate`（monkey-patch），改用 `ModChineseRerankingEvaluator`；该评估器按模型有无 `compute_score` 方法分别走 cross-encoder（`model.compute_score`）或 bi-encoder（`encode_queries`/`encode_corpus`）路径，指标为 `map` 与 `mrr` | `c_mteb/Reranking.py`: `ModChineseRerankingEvaluator`, `AbsTaskReranking.evaluate = evaluate` |
| F-bc-036 | `class YDDRESModel(nn.Module)` 包装 `EmbeddingModel`，默认参数 `pooler='cls'`、`normalize_embeddings=True`、`batch_size=160`、`max_length=512`；提供 `encode_queries`、`encode_corpus`、`encode` 三个方法供 MTEB 检索任务调用 | `c_mteb/yd_dres_model.py`: `class YDDRESModel` |
| F-bc-037 | `YDDRESModel.encode_corpus` 对 dict 型 corpus 拼接为 `'{} {}'.format(doc.get('title', ''), doc['text']).strip()`；`instruction_for_all` 在 `model_name_or_path` 含 `"e5-base"` 或 `"e5-large"` 时为 `True`，此时 `encode` 强制使用 query 指令 | `yd_dres_model.py`: `encode_corpus`, `encode` |

## 框架集成（`BCEmbedding/tools/`）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-bc-038 | `tools/langchain/bce_rerank.py` 定义 `BCERerank(BaseDocumentCompressor)`：字段 `client='BCEmbedding'`、`top_n` 默认 3、`model` 默认 `'maidalun1020/bce-reranker-base_v1'`；`compress_documents` 将 rerank 分数写入 `doc.metadata["relevance_score"]`，无效文档置 0，最终截取前 `top_n` 个 | `BCEmbedding/tools/langchain/bce_rerank.py`: `class BCERerank` |
| F-bc-039 | `tools/llama_index/bce_rerank.py` 定义 `BCERerank(BaseNodePostprocessor)`：`top_n` 默认 5；`_postprocess_nodes` 在 `query_bundle is None` 时抛 `ValueError("Missing query bundle in extra info.")`，分数写入 `node.score`，截取前 `top_n` 个 | `BCEmbedding/tools/llama_index/bce_rerank.py`: `class BCERerank` |
| F-bc-040 | 两个 `BCERerank` 均在 `__init__` 内延迟导入 `BCEmbedding.models.RerankerModel` 并实例化为 `_model` 私有属性；导入失败时报错信息要求 `pip install BCEmbedding>=0.1.2` | `tools/langchain/bce_rerank.py` 与 `tools/llama_index/bce_rerank.py`: `__init__` |

## 存疑与说明

- setup.py 未声明 `python_requires`，Python 版本要求仅有 README 安装示例（python=3.10）可作旁证，源码中无权威版本约束。
- `BCEmbedding/evaluation/` 与 `BCEmbedding/tools/` 下各脚本（eval_mteb、eval_rag）为评测入口脚本，本清单仅登记其存在，未逐行采集；如需可追加。
- README 中的性能数字（MTEB/RAG 榜单）属厂商自宣数据，未纳入本源码事实清单（如需引用应另行核验）。
