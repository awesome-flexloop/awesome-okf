---
title: IVF 与 PQ 量化
type: concept
bundle: /datawhale/easy-vecdb
description: IVF 倒排文件索引（K-Means 聚类、nlist/nprobe 参数）、PQ 乘积量化（分块、子码本、查表距离估算）、IVF-PQ 混合索引原理与实践
related:
  - /datawhale/easy-vecdb/concepts/ann-algorithms
  - /datawhale/easy-vecdb/concepts/hnsw-lsh
  - /datawhale/easy-vecdb/concepts/faiss-milvus-engineering
  - /datawhale/easy-vecdb/examples/mini-vector-db
sources:
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/base/chapter5/IVF算法.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/base/chapter5/PQ算法.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/base/chapter5/ANN搜索算法.md
tags:
  - ivf
  - pq
  - quantization
  - clustering
---

# IVF 与 PQ 量化

IVF（倒排文件索引）和 PQ（乘积量化）是向量检索中最经典的两种技术。IVF 通过聚类缩小搜索范围，PQ 通过压缩降低内存和计算成本。二者组合为 IVF-PQ，是 FAISS 和 Milvus 中最广泛使用的混合索引方案。

## IVF：倒排文件索引

### 核心思想

IVF（Inverted File Index）采用"分而治之"策略：将向量空间通过 K-Means 聚类划分为若干簇，搜索时只在与查询向量最相近的几个簇内查找。

可以类比为图书馆找书：如果所有书籍杂乱堆放（暴力搜索），只能一本本翻；而按主题分类摆放后，找"物理学"相关书籍只需去"科学"书架查找。

### 工作流程

**索引构建阶段**：

1. 使用 K-Means 将所有向量聚类为 nlist 个簇
2. 记录每个簇的中心点（Centroid）
3. 将每个向量分配到最近的簇，形成倒排表（簇 ID → 向量列表）

**查询阶段**：

1. 计算查询向量与所有 nlist 个簇中心的距离
2. 选出距离最近的 nprobe 个簇
3. 仅在这些簇内部计算精确相似度并排序
4. 返回 Top-K 结果

### 关键参数

| 参数 | 含义 | 调优建议 |
|------|------|---------|
| **nlist** | 聚类簇数 | 通常设为数据量的平方根量级；百万级数据可用 1024~4096 |
| **nprobe** | 查询时探测的簇数 | 越大精度越高、速度越慢；通常 nprobe ≈ nlist 的 1%~10% |

nprobe 是 IVF 最核心的运行时调节参数：
- nprobe = nlist 时等价于暴力搜索（精度 100%）
- nprobe = 1 时只查最近的 1 个簇（速度最快但可能漏检）
- 通过调节 nprobe 可以在精度和速度间平滑切换

### IVF 的优势与局限

**优势**：
- 大幅减少需要比较的向量数量（从 N 降到 N×nprobe/nlist）
- 聚类结构清晰，易于理解和实现
- 可与 PQ、HNSW 等算法组合使用

**局限**：
- 高维空间中 K-Means 聚类效果可能不佳
- 簇边界附近的向量容易被漏检
- 数据分布不均时（某些簇过大），性能退化
- 不适合动态数据（增量插入需重新聚类）

## PQ：乘积量化

### 核心思想

PQ（Product Quantization）通过"分块 + 量化"将高维向量压缩为短码，在保证较高检索精度的同时显著降低存储空间和计算成本。

类比：将一本厚重的百科全书拆分成若干主题册，每册只保留索引编号。虽然丢失了一些细节（近似计算），但通过编号能快速定位最相关的内容。

### 工作流程

**1. 分块（Subspace Division）**

将 d 维原始向量均匀切分为 m 个子空间，每个子空间维度为 d/m。例如 128 维向量切分为 8 个 16 维子向量。

**2. 量化（Quantization）**

对每个子空间独立执行 K-Means 聚类，生成 m 个子码本（Codebook），每个子码本包含 k 个中心点（通常 k=256，即 8 位编码）。每个向量在每个子空间中被表示为最近中心点的编号。

最终，一个 128 维 float32 向量（512 字节）被压缩为 8 个 uint8 编号（8 字节），**压缩率达 64 倍**。

**3. 近似距离计算（Lookup Table）**

查询时，PQ 不计算完整的欧氏距离，而是：

1. 将查询向量也切分为 m 个子向量
2. 预计算每个子向量与对应子码本中所有 k 个中心点的距离，生成 m×k 的距离查找表
3. 对数据库中的每个向量，根据其 m 个子码本编号，从查找表中取出对应距离并求和
4. 求和结果即为近似距离

这种查表计算只需要 m 次加法和 m 次查表，远快于 d 维浮点运算。

### PQ 的变体

| 变体 | 改进 |
|------|------|
| **OPQ**（Optimized PQ） | 在 PQ 前增加正交旋转矩阵，使各子空间方差更均衡，降低量化误差 |
| **SQ**（Scalar Quantization） | 每个维度独立量化（如 float32→uint8），简单但压缩率有限 |
| **PQ with PCA** | 先用 PCA 降维再做 PQ，进一步压缩 |
| **RabitQ** | 带理论误差界的高维向量量化，教程补充章节有介绍 |

### PQ 的优势与局限

**优势**：
- 极高压缩率（通常 10~64 倍）
- 查表法距离计算常数时间复杂度 O(m)
- 与 IVF 组合效果极佳

**局限**：
- 量化引入信息损失，精度低于原始向量
- 码本训练需要代表性数据
- 压缩率越高，精度损失越大
- 对向量分布有假设（各子空间独立同分布）

## IVF-PQ 混合索引

IVF-PQ 是工业界最经典的混合索引方案，结合了 IVF 的空间划分和 PQ 的压缩能力：

**构建流程**：

1. 用 K-Means 将向量聚类为 nlist 个簇（IVF 阶段）
2. 对每个簇内的残差向量（向量减去簇中心）执行 PQ 量化
3. 存储时只保存 PQ 压缩码和簇 ID

**查询流程**：

1. 计算查询向量与所有簇中心的距离，选 nprobe 个最近簇
2. 对每个候选簇，用 PQ 查表法计算近似距离
3. 按近似距离排序，返回 Top-K

### 为什么 IVF 和 PQ 配合效果好

- IVF 解决了"搜哪里"的问题（缩小搜索范围）
- PQ 解决了"怎么存和怎么算"的问题（压缩内存和加速计算）
- 对残差做 PQ 比对原始向量做 PQ 量化误差更小（残差分布更集中）
- 两者的参数（nlist/nprobe 和 m/nbits）可以独立调节

### 在 FAISS/Milvus 中的使用

```python
import faiss

# IVF-PQ 索引：128维，1024个簇，PQ切分为8段，每段8位
quantizer = faiss.IndexFlatL2(128)
index = faiss.IndexIVFPQ(quantizer, 128, 1024, 8, 8)

# 训练（需要代表性数据）
index.train(train_vectors)
index.add(database_vectors)

# 查询：探测 16 个簇
index.nprobe = 16
distances, indices = index.search(query_vectors, k=10)
```

Milvus 中创建 IVF_PQ 索引：

```python
index_params = {
    "index_type": "IVF_PQ",
    "params": {"nlist": 1024, "m": 8, "nbits": 8},
    "metric_type": "L2"
}
collection.create_index(field_name="vector", index_params=index_params)

# 查询时设置 nprobe
search_params = {"params": {"nprobe": 16}}
results = collection.search(data, "vector", search_params, limit=10)
```

## 延伸阅读

- [HNSW 与 LSH](/datawhale/easy-vecdb/concepts/hnsw-lsh.md) — 图索引和哈希索引方案
- [ANN 近似最近邻算法](/datawhale/easy-vecdb/concepts/ann-algorithms.md) — 六大索引类型总览
- [Faiss 与 Milvus 工程实践](/datawhale/easy-vecdb/concepts/faiss-milvus-engineering.md) — IVF-PQ 在工业系统中的应用
- [手写 Mini Vector DB](/datawhale/easy-vecdb/examples/mini-vector-db.md) — 实现 IVF 索引
