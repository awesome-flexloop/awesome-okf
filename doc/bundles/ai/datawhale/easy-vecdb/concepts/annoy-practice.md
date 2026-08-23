---
title: Annoy 实践
type: concept
bundle: /datawhale/easy-vecdb
description: Spotify 开源的轻量级近似最近邻库 Annoy，随机投影森林原理、mmap 内存映射、多进程共享、核心 API、参数调优与工程实践
related:
  - /datawhale/easy-vecdb/concepts/ann-algorithms
  - /datawhale/easy-vecdb/concepts/hnsw-lsh
  - /datawhale/easy-vecdb/concepts/faiss-milvus-engineering
sources:
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Annoy/chapter1/Annoy入门与环境搭建.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Annoy/chapter2/Annoy核心API详解.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Annoy/chapter3/Annoy进阶技巧与最佳实践.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/base/chapter5/Annoy算法.md
tags:
  - annoy
  - spotify
  - random-projection-tree
  - mmap
---

# Annoy 实践

Annoy（Approximate Nearest Neighbors Oh Yeah）是 Spotify 开发并开源的轻量级近似最近邻搜索库，最初用于 Spotify 的音乐推荐系统。它以简洁的 API、内存映射机制和多进程共享能力著称，适合单机静态数据的高效检索。

## Annoy 核心特性

| 特性 | 说明 |
|------|------|
| **内存映射（mmap）** | 索引文件通过 mmap 加载，不需要将整个索引读入内存 |
| **多进程共享** | 多个进程可共享同一份索引文件，大幅降低内存开销 |
| **API 简洁** | 只有几个核心方法，5 分钟即可上手 |
| **跨语言** | 支持 Python、C++、Java、Go 等多种语言绑定 |
| **静态索引** | 构建后不可修改，适合定期全量重建的场景 |

## 随机投影森林原理

Annoy 基于**随机投影树（Random Projection Tree）**构建索引：

1. **构建树**：
   - 在向量空间中随机选择两个点，取它们的中垂面（超平面）将空间一分为二
   - 在每个子空间中递归重复此过程，直到每个叶子节点包含的向量数不超过阈值 K
   - 重复上述过程构建多棵树（n_trees 棵），形成随机投影森林

2. **查询**：
   - 在每棵树中从根节点遍历到叶子节点（根据查询向量在超平面的哪一侧）
   - 收集所有遍历到的叶子节点中的向量作为候选
   - 对候选集计算精确距离，返回 Top-K

3. **多棵树的作用**：
   - 单棵树的划分是随机的，可能错过近邻
   - 多棵树增加了覆盖范围，提高召回率
   - n_trees 越大召回率越高，但索引体积和查询时间也增加

### Annoy 算法在 ANN 分类中的位置

Annoy 属于**空间划分类**索引，与 IVF 同属一类，但使用随机超平面而非 K-Means 聚类进行空间划分。它的树结构天然适合磁盘存储和内存映射。

## 安装与验证

```bash
pip install annoy
```

验证安装：

```python
from annoy import AnnoyIndex

# 创建索引：维度为 3，使用余弦距离（angular）
t = AnnoyIndex(3, 'angular')
t.add_item(0, [1, 0, 0])
t.add_item(1, [0, 1, 0])
t.add_item(2, [0, 0, 1])
t.build(10)  # 构建 10 棵树

# 查询与 [1, 0.5, 0] 最相似的 2 个向量
result = t.get_nns_by_vector([1, 0.5, 0], 2)
print(result)  # [0, 1]
```

## 核心 API

### 创建索引

```python
AnnoyIndex(f, metric)
```

- `f`：向量维度
- `metric`：距离度量，可选：
  - `'angular'`：余弦距离（默认，基于归一化向量的欧氏距离）
  - `'euclidean'`：欧氏距离
  - `'manhattan'`：曼哈顿距离
  - `'hamming'`：汉明距离
  - `'dot'`：内积距离

### 添加向量

```python
t.add_item(i, v)
```

- `i`：向量的非负整数 ID
- `v`：向量（list 或 numpy 数组）
- 必须在 `build()` 之前调用，构建后不能再添加

### 构建索引

```python
t.build(n_trees, n_jobs=-1)
```

- `n_trees`：树的数量。越大召回率越高，但索引文件越大、查询越慢。推荐值：数据量 <10 万用 10~100，百万级用 100~1000
- `n_jobs`：并行构建的线程数，-1 表示使用所有 CPU 核心

### 保存与加载

```python
t.save(fn)          # 保存索引到文件
t = AnnoyIndex(f, metric)
t.load(fn)          # 从文件加载（mmap 方式）
t.load(fn, prefault=True)  # prefault=True 预读整个文件到内存
```

`load()` 默认使用 mmap，多个进程加载同一文件时共享物理内存。`prefault=True` 适合索引文件小于可用内存的场景，可减少查询延迟抖动。

### 查询

```python
# 按向量查询
t.get_nns_by_vector(v, n, search_k=-1, include_distances=False)

# 按物品 ID 查询
t.get_nns_by_item(i, n, search_k=-1, include_distances=False)
```

- `n`：返回的最近邻数量
- `search_k`：搜索过程中检查的节点数。默认值为 `n_trees * n * 10`。增大 search_k 可提高召回率但增加查询时间
- `include_distances`：是否同时返回距离值

### 其他方法

```python
t.get_item_vector(i)     # 获取指定 ID 的向量
t.get_n_items()          # 获取索引中向量总数
t.get_n_trees()          # 获取树的数量
t.unload()               # 卸载索引
t.unbuild()              # 清除树结构（保留向量数据，可重新 build）
t.on_disk_build(fn)      # 在磁盘上构建（减少内存使用）
```

## 参数调优

### n_trees 与召回率/性能的关系

| n_trees | 召回率 | 索引大小 | 查询速度 | 适用场景 |
|---------|--------|---------|---------|---------|
| 10 | 较低 | 小 | 极快 | 原型验证、对精度要求低 |
| 100 | 中等 | 中 | 快 | 一般推荐系统 |
| 1000 | 高 | 大 | 较慢 | 高精度要求的离线任务 |

经验法则：`n_trees` 越大越好，但收益递减。通常从 100 开始，根据召回率测试结果调整。

### search_k 运行时调节

`search_k` 是查询时参数，不需要重建索引即可调节：

- `search_k = -1`（默认）：使用 `n_trees * n * 10`
- 增大 `search_k`：检查更多候选，提高召回率，但增加延迟
- 减小 `search_k`：查询更快，但可能漏检

建议在生产环境中动态设置 `search_k`，根据延迟要求和召回率监控调整。

## 适用与不适用场景

### 适用场景

- **单机部署**：不需要分布式架构
- **只读索引**：数据不频繁更新，可定期全量重建
- **数据量中等**：百万到千万级向量
- **多进程 Web 服务**：Gunicorn/uWSGI 多 worker 共享同一索引
- **内存受限**：mmap 机制使索引不必完全加载到内存

### 不适用场景

- 需要频繁增删改的实时场景（Annoy 不支持增量更新）
- 需要分布式部署的超大规模数据（考虑 Milvus）
- 需要丰富索引类型和 GPU 加速（考虑 Faiss）
- 数据量超过单机内存且无法接受磁盘查询延迟

## 工程实践建议

### 多进程共享索引

```python
from annoy import AnnoyIndex
from flask import Flask

app = Flask(__name__)
index = AnnoyIndex(128, 'angular')
index.load('recommendations.ann')  # 多进程共享 mmap

@app.route('/recommend/<int:item_id>')
def recommend(item_id):
    neighbors = index.get_nns_by_item(item_id, 20)
    return {'items': neighbors}
```

使用 Gunicorn 多 worker 部署时，所有 worker 共享同一份索引的物理内存页。

### 索引构建策略

由于 Annoy 不支持增量更新，推荐以下策略：

1. **定时全量重建**：每天/每周在低峰期重新构建索引
2. **双索引切换**：构建新索引时保留旧索引提供服务，构建完成后原子切换
3. **使用 `on_disk_build`**：数据量大时在磁盘上构建，避免内存不足

### 与其他工具的对比

| 维度 | Annoy | Faiss | Milvus |
|------|-------|-------|--------|
| 定位 | 轻量 ANN 库 | 高性能检索库 | 分布式向量数据库 |
| 索引类型 | 随机投影树 | Flat/IVF/PQ/HNSW 等 | 多种工业级索引 |
| GPU 支持 | 无 | 强大 | 支持 |
| 分布式 | 无 | 无 | 原生支持 |
| 持久化 | 文件 mmap | 需自行实现 | 内置 |
| 多进程共享 | 原生支持 | 有限 | 通过服务 |
| 增量更新 | 不支持 | 部分支持 | 支持 |
| 学习曲线 | 极低 | 中等 | 较高 |

## 延伸阅读

- [ANN 近似最近邻算法](/ai/datawhale/easy-vecdb/concepts/ann-algorithms.md) — Annoy 在六大索引分类中的位置
- [HNSW 与 LSH](/ai/datawhale/easy-vecdb/concepts/hnsw-lsh.md) — 其他索引算法的对比
- [Faiss 与 Milvus 工程实践](/ai/datawhale/easy-vecdb/concepts/faiss-milvus-engineering.md) — 更强大的向量检索方案
