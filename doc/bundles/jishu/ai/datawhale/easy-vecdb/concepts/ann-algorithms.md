---
title: ANN 近似最近邻算法
type: concept
bundle: /datawhale/easy-vecdb
description: ANN 核心思想、六大索引分类（空间划分/图索引/量化压缩/哈希/混合/磁盘分布式）、精度-速度-内存三角权衡与选型
related:
  - /datawhale/easy-vecdb/concepts/vector-retrieval-basics
  - /datawhale/easy-vecdb/concepts/ivf-pq-quantization
  - /datawhale/easy-vecdb/concepts/hnsw-lsh
  - /datawhale/easy-vecdb/concepts/annoy-practice
sources:
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/base/chapter5/ANN搜索算法.md
tags:
  - ann
  - index
  - tradeoff
---

# ANN 近似最近邻算法

ANN（Approximate Nearest Neighbors，近似最近邻）搜索通过引入近似计算，在保持较高召回率的同时显著减少计算复杂度。其核心价值是：**牺牲微不足道的精度，换取数百倍甚至数千倍的速度提升**。

## 为什么需要 ANN

暴力搜索的时间复杂度为 O(N)，且在高维空间中面临维度灾难——数据点间距离趋同，区分度急剧下降。当数据量从千级增长到百万、千万甚至亿级时，暴力搜索的耗时从毫秒级增加到分钟甚至小时级，无法满足实时应用需求。

ANN 通过构建精巧的索引结构，避免遍历全部向量，将搜索复杂度降低到 O(log N) 甚至更低。

## 六大索引类型

### 1. 空间划分类（Spatial Partitioning）

通过划分向量空间来减少搜索范围。

| 算法 | 核心思想 | 特点 |
|------|---------|------|
| **IVF** | K-Means 聚类成簇，搜索时只查最近的 nprobe 个簇 | 粗筛效果好，高维下性能下降 |
| **KD-Tree/Ball Tree** | 树结构递归划分空间 | 适合低维向量 |
| **Annoy** | 多棵随机投影树，磁盘高效存储 | 适合静态数据，mmap 共享 |

### 2. 图索引类（Graph-based Index）

通过构建向量间的邻接图实现高效导航搜索。

| 算法 | 核心思想 | 特点 |
|------|---------|------|
| **HNSW** | 分层小世界图，从稀疏层向密集层逐层细化 | 召回率高、延迟低，当前最优之一 |
| **NSG** | 优化边连接减少图复杂度 | 工业大规模检索常用 |
| **NN-Descent** | 近邻传播逐步逼近 KNN 图 | 常用于 HNSW/NSG 预构建 |

### 3. 量化压缩类（Quantization-based Index）

通过压缩向量存储与近似距离计算节省资源。

| 算法 | 核心思想 | 特点 |
|------|---------|------|
| **PQ** | 高维向量分块后分别量化为短码 | 压缩率极高（1/10+），查表计算 |
| **OPQ** | PQ 基础上增加旋转优化 | 量化误差更小 |
| **SQ** | 每个维度独立量化 | 简单但压缩率有限 |

### 4. 哈希类（Hash-based Index）

通过哈希函数将相似向量映射到相同桶。

| 算法 | 核心思想 | 特点 |
|------|---------|------|
| **LSH** | 局部敏感哈希保持相似性 | 计算极快、可并行，召回率较低 |
| **SimHash/MinHash** | 文本/稀疏特征快速相似度匹配 | 常用于粗筛 |

### 5. 混合索引（Hybrid Index）

融合多种技术取长补短，是工业级应用的主流方案。

| 组合 | 方式 | 应用 |
|------|------|------|
| **IVF + PQ** | 先聚类再量化 | FAISS 默认方案，平衡性能与存储 |
| **HNSW + PQ** | 图索引 + 量化压缩 | 高精度且资源受限场景 |
| **IVF + HNSW** | 粗粒度聚类 + 分区内图搜索 | 同时提升速度与局部召回 |
| **Hash + IVF/HNSW** | 哈希粗筛 + 精细检索 | 亿级以上预筛阶段 |

### 6. 磁盘/分布式扩展索引

针对数十亿向量的超大规模场景。

| 系统 | 特点 |
|------|------|
| **DiskANN**（Microsoft） | 图索引 + 顺序磁盘访问，TB 级数据亚秒响应 |
| **SPANN**（Microsoft） | 分布式向量搜索，多层索引与分区调度 |
| **ScaNN**（Google） | 空间划分 + 量化，优化 TPU/GPU 性能 |

## 索引类型对比

| 索引类型 | 代表算法 | 优势 | 局限 |
|---------|---------|------|------|
| 空间划分类 | IVF, Annoy | 简单高效 | 高维退化 |
| 图索引类 | HNSW, NSG | 高召回、低延迟 | 构建成本高、更新慢 |
| 量化压缩类 | PQ, OPQ | 内存极低、速度快 | 精度下降 |
| 哈希类 | LSH | 查询极快、可并行 | 召回率较低 |
| 混合索引 | IVF+PQ, HNSW+PQ | 均衡速度/精度/存储 | 实现复杂、参数多 |

## 精度-速度-内存三角权衡

所有 ANN 算法都在三个维度间权衡：

```
        精度（Recall）
           /\
          /  \
         /    \
        /      \
       /________\
   速度（QPS）  内存（Memory）
```

- **Flat（暴力搜索）**：精度 100%，速度最慢，内存最大（存原始向量）
- **IVF**：通过 nprobe 调节——nprobe 越大精度越高但越慢；内存与 Flat 相当
- **PQ**：内存最小（压缩 10 倍以上），但精度有损；速度快（查表计算）
- **HNSW**：精度高、速度快，但内存最大（需额外存储图结构）；构建慢
- **IVF-PQ**：三者均衡——IVF 缩小搜索范围，PQ 压缩内存，是工业界最常用的组合

### 关键参数调节

| 索引 | 参数 | 作用 | 调优方向 |
|------|------|------|---------|
| IVF | nlist | 聚类簇数 | 数据量的平方根量级 |
| IVF | nprobe | 查询时探测的簇数 | 增大→精度↑速度↓ |
| HNSW | M | 每层最大连接数 | 增大→精度↑内存↑构建↑ |
| HNSW | efConstruction | 构建时搜索宽度 | 增大→构建质量↑构建时间↑ |
| HNSW | efSearch | 查询时搜索宽度 | 增大→精度↑延迟↑ |
| PQ | m（子空间数） | 向量分块数 | 增大→精度↑压缩率↓ |
| PQ | nbits | 每个子码本位数 | 通常 8 位（256 个中心点） |

## ANN-Benchmarks 性能参考

在 GloVe-100 维度（angular 距离）数据集上的基准测试显示，各算法在 Recall-QPS 曲线上的表现不同：

- HNSW 通常在高 Recall 区域保持最高 QPS
- IVF-PQ 在中低 Recall 区域有良好的吞吐量
- Annoy 在静态数据场景下表现稳定
- 最优选择取决于具体的 Recall 目标和硬件约束

## 延伸阅读

- [IVF 与 PQ 量化](ivf-pq-quantization.md) — 深入理解空间划分与向量压缩
- [HNSW 与 LSH](hnsw-lsh.md) — 图索引与哈希索引的原理
- [Annoy 实践](annoy-practice.md) — 轻量级 ANN 库的使用
- [Faiss 与 Milvus 工程实践](faiss-milvus-engineering.md) — 工业级向量检索引擎
