---
type: Concept
title: Zvec 量化：存储压缩与距离估计的双轨体系
description: turbo 层标量/PQ 量化（FP16/INT8/INT4）与 core 层 RaBitQ/Uniform 距离估计量化的分层设计、enable_rotate 旋转与双份存储行为
tags: [zvec, quantization, rabitq, pq, int8, uniform]
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

# Zvec 量化：存储压缩与距离估计的双轨体系

量化将向量从原始格式（如 FP32）转为更紧凑表示，减少索引常驻内存、降低 I/O 与查询延迟。QuantizeType 枚举共 8 个成员：FP16、INT8、INT4、RABITQ、UNIFORM_UINT7、UNIFORM_UINT8、UNIFORM_UINT4（及 UNDEFINED）——恰好映射源码中的两条量化轨道。

## 双轨架构

```text
QuantizeType 枚举的两条轨道
├─ 存储压缩轨（src/turbo/quantizer/）
│   FP16 / INT8 / INT4 + pq_fast / pq_int4 / pq_int8
│   作用：改变向量在索引中的存储格式
│   入口：VectorSchema(quantize_type=...)
└─ 距离估计轨（src/core/quantizer/）
    RABITQ + UNIFORM_UINT4/7/8
    作用：改变距离计算方式（旋转→二值/均匀编码→位运算估距）
    入口：独立索引类型 HnswRabitqIndexParam / IvfRabitqIndexParam
```

关键差异：多数向量库把量化当索引参数；Zvec 把 **RaBitQ 升格为独立索引类型**（HNSW-RaBitQ / IVF-RaBitQ），因为它替换的是距离计算内核而非仅存储格式——这也解释了 RaBitQ 系的平台约束（Linux x86_64 + AVX2/AVX512）来自位运算内核。v0.8.0 新增的 Uniform 系列量化器（UNIFORM_UINT4/7/8）避免逐点分数反算，但共享 Min/Max 可能增大量化误差、降低召回率。

## 存储行为：双份并存

Zvec **同时存储原始向量与量化版本**：磁盘总占用可能增加，但构建索引与检索只加载量化向量（内存省）；原始向量随时可按需取回。因此量化是"有损且不可逆"的压缩——务必验证对检索质量的影响。量化仅在 FP32 向量上收益。

## 标量量化三档（存储轨）

| 类型 | 表示 | 适用 |
|---|---|---|
| FP16 | 16 位半精度浮点 | 接近 FP32 精度 + 更快计算 |
| INT8 | 8 位整数 | 速度/体积/精度的平衡点 |
| INT4 | 每维 4 位 | 极致紧凑、延迟敏感、资源受限 |

启用方式：创建向量索引时在 `VectorSchema` 设置 `quantize_type`：

```python
zvec.VectorSchema(
    name="description_vec",
    data_type=zvec.DataType.VECTOR_FP32,
    dimension=768,
    index_param=zvec.HnswIndexParam(
        metric_type=zvec.MetricType.COSINE,
        quantize_type=zvec.QuantizeType.INT8,
    ),
)
```

## enable_rotate：量化前的正交旋转

INT8/INT4 场景可经 `quantizer_param` 开启随机正交旋转，使各维分布更均匀、减小量化信息损失：

```python
zvec.VectorSchema(
    ...,
    index_param=zvec.HnswIndexParam(...),
    quantizer_param=zvec.QuantizerParam(enable_rotate=True),
)
```

源码对应 `src/turbo/preprocessor/` 的 fht_rotator（快速 Hadamard 变换）与 opq_rotator。

## 距离估计轨：RaBitQ 精度-内存标尺

RaBitQ 先随机旋转再二值编码，位运算估距。`total_bits` 控制精度-内存权衡（1–9 位）：7 位约 99% Recall、5 位约 95%、4 位约 90%、1 位极限压缩。图构建用原始向量，故常无需精排即得高 Recall；量化后向量最多比 FP32 小 32 倍。详见[索引类型](03-index-types.md)的 HNSW-RaBitQ / IVF-RaBitQ 两节。

## 精排挽回精度

量化场景下查询参数 `is_using_refiner=True` 对头部候选重新计算精确 FP32 距离（IVF-RaBitQ 另有 `scale_factor` 候选扩展倍数）——以少量延迟换回召回质量。

## 相关概念

- [索引类型](03-index-types.md)：六种官方索引与 RaBitQ 索引参数
- [源码架构](01-architecture.md)：turbo 与 core 两层量化器目录
- [混合检索](06-hybrid-retrieval.md)：is_using_refiner 的查询层配合
