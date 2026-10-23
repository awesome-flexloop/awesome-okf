---
type: Concept
title: Zvec 向量索引：六种官方类型与选型决策
description: Flat/HNSW/HNSW-RaBitQ/DiskANN/IVF/IVF-RaBitQ 六种官方索引的原理、参数与权衡，附 Vamana 与稀疏索引的源码补充
tags: [zvec, ann, hnsw, diskann, ivf, rabitq, index]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-source
    resource: /references/source-code.md
    title: alibaba/zvec 源码信源
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# Zvec 向量索引：六种官方类型与选型决策

向量索引是加速相似度检索的专用数据结构。无索引时需与库中每个向量比对（暴力/Flat 检索）——精确但大规模下不可行；近似最近邻（ANN）以极小 Recall 损失换取速度与扩展性质变。Recall@k = top-k 结果中真实最近邻的占比，通常 ≥96% 即与精确检索体验无别。

IndexType 枚举共 10 个成员：HNSW、IVF、IVF_RABITQ、FLAT、HNSW_RABITQ、DISKANN、VAMANA、INVERT（倒排）、FTS（全文）、UNDEFINED。官方文档详述其中 6 种向量索引。

## 六种官方索引对比

| 索引 | 原理 | 适用场景 | 关键权衡 |
|---|---|---|---|
| Flat | 暴力逐一比对 | 小数据集、原型、正确性基准 | 100% Recall；延迟随数据量线性增长 |
| HNSW | 多层可导航小世界图 | 实时低延迟生产系统（**首选**） | O(log n) 查询；内存占用高 |
| HNSW-RaBitQ | HNSW 图 + RaBitQ 二值量化 | 内存受限的超大规模高维数据 | 内存最多省 32 倍；仅 Linux x86_64 + AVX2/AVX512 |
| DiskANN | Vamana 磁盘图 + PQ 内存压缩 | 十亿级、数据远超内存 | 极低内存；查询含磁盘 I/O、QPS 低于内存索引 |
| IVF | 聚类倒排文件 | 自带聚类结构的数据集 | 内存高效；建图慢、参数敏感 |
| IVF-RaBitQ | IVF 分区 + RaBitQ 编码 | 内存受限大规模 + 聚类结构 | 双重削减扫描与内存；同样仅 Linux x86_64 |

## Flat：正确性基线

完美 Recall、零配置、即时构建。官方建议开发测试阶段以 Flat 为正确性基准，验证通过后再切换 HNSW；数据量小（如 30 万级）且正确性优先的场景可直接使用。

## HNSW：生产首选

多层图——上层稀疏做"高速公路"远距离跳转，下层稠密做局部精细搜索；从顶层入口贪心下行。构建参数：`metric_type`（按 Embedding 模型训练度量选择）、`m`（每节点最大邻居数，调大提升 Recall 但增内存）、`ef_construction`（建图候选池，只影响构建时间）、`quantize_type`。查询参数：`ef`（候选池，调 Recall 与延迟的主旋钮，如 300→500）、`radius`（分数阈值过滤，IP 度量下 `radius=0.6` 仅保留分>0.6）、`is_linear`（强制暴力，仅调试用）、`is_using_refiner`（对头部候选用原始向量精算精确分数，量化场景挽回精度）。

调参顺序：默认值 → 先调 `ef` → 必要时才加 `ef_construction`/`m`。

## HNSW-RaBitQ：图导航 + 位运算距离估计

RaBitQ（arXiv:2405.12497）先随机旋转再转二值编码，用位运算估计距离——量化后向量最多比 FP32 小 32 倍。论文口径：`total_bits=7` 约 99% Recall、5 位约 95%、4 位约 90%，最低 1 位。构建参数默认 `total_bits=7`、`num_clusters=16`（KMeans 聚类数），`sample_count=0` 表示全量训练（超大数据集可设如 5,000,000 限内存）。图构建使用原始向量保持图质量，故常无需重排即得高 Recall。限制：仅 Linux x86_64（AVX2/AVX512）、64–4095 维。

## DiskANN：十亿级磁盘图

NeurIPS 2019 论文实现。Vamana 单层图（`max_degree` 边上限、alpha 剪枝鼓励长边、medoid 固定入口）与全精度向量存磁盘；内存只驻留 PQ 压缩编码（`pq_chunk_num` 个子空间、每 chunk 1 字节）。查询走带缓存的束搜索（`list_size` 候选宽度），高频入口节点 BFS 层级缓存。libaio 为可选加速（未装则走备用 I/O 路径）。仅 Linux；适合吞吐延迟不敏感的超大规模场景。

## IVF：聚类倒排文件

构建时聚类出 `n_list` 个质心（建议 ≈ √N），向量入最近质心的倒排列表；查询时比较全部质心选最近 `n_probe` 个列表局部暴力检索。复杂度约 O(N/n_list × n_probe)。`n_iters` 控制质心优化迭代。内存高效、是 IVF-PQ 类复合索引的基础层；代价是建图慢、对参数敏感。

## IVF-RaBitQ：双重削减

IVF 缩小扫描范围，RaBitQ 压缩列表内距离估计（1 位快速估算+误差下界剪枝，保留者再用额外位精算）。默认值：`nlist=1024`、`total_bits=7`、`sample_count=0`；查询 `nprobe=10`、`is_using_refiner=False`、`scale_factor=10.0`（精排时候选扩展倍数）。同 RaBitQ 系平台约束；仅支持 FP32 稠密向量与 L2/IP/COSINE。同等编码下结构性内存低于 HNSW-RaBitQ，但对聚类质量更敏感。

## 源码补充：Vamana 与稀疏索引

源码 `src/core/algorithm/` 中另有 **vamana** 独立算法目录（配套 `VamanaIndexParam`/`VamanaQueryParam`，测试 `test_vamana.py`）——DiskANN 的图算法本体；以及 **flat_sparse** 与 **hnsw_sparse** 两个稀疏向量索引目录，对应 `SPARSE_VECTOR_FP32/FP16` 字段的索引能力。官方文档索引类型页未单列这三者。

## 选型决策树

```text
数据能装入内存？
├─ 否 → DiskANN（十亿级磁盘图）
└─ 是 → 内存预算敏感？
    ├─ 否 → HNSW（低延迟高 Recall 首选）
    └─ 是 → Linux x86_64 + AVX2/512？
        ├─ 是 → 数据有聚类结构？IVF-RaBitQ : HNSW-RaBitQ
        └─ 否 → HNSW + INT8/INT4 量化（见量化章）
小数据/原型/基准 → Flat
```

## 相关概念

- [量化](04-quantization.md)：RaBitQ 与标量量化的双轨关系
- [数据模型](02-data-modeling.md)：VectorSchema 中的 index_param
- [存储与配置](08-storage-and-config.md)：DiskANN 的四种 I/O 后端
