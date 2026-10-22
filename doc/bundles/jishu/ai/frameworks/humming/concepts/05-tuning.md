---
type: Concept
title: "调优与启发式：设备能力如何决定配置"
description: "Humming 的调优体系——按 SM 版本分派的启发式类族、计算/访存瓶颈判定、M 维候选集合与对齐规则、设备能力约束与 MoE 栅格化调度"
tags: [humming, tuning, heuristics, autotune, bottleneck, smem, moe-raster, 核心]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /references/facts.md
    title: 本地源码检出事实清单
  - id: blog
    url: https://vllm.ai/blog/2026-10-21-humming
---

# 调优与启发式：设备能力如何决定配置

> 核心层。Humming **当前没有自动搜索（autotune）**，靠的是按设备架构分派的**针对性启发式**（F-090）。本页讲这套启发式怎么工作。

## 一、为什么不用 autotune

官方路线图把「引入 autotune」列为**未来计划**（F-090）：

> 当前靠针对性调优，尚未有自动搜索，预期与现有启发式互补。

这是合理的取舍：Humming 用 JIT 编译，若再叠加 autotune 的搜索空间，编译时间会失控——而 Humming 的核心竞争力恰恰是编译只花 1.82 秒（F-080）。启发式是「用架构知识换搜索时间」。

## 二、启发式按 SM 版本分派

`heuristics_map` 覆盖 11 个 SM 版本（F-056，`humming/tune/__init__.py:26-38`）：

| SM | 启发式类 | 备注 |
|----|---------|------|
| 75 | `Sm75Heuristics`（`tune/sm75.py`） | Turing |
| 80 | `Sm80Heuristics`（`tune/sm8x.py`） | Ampere |
| 86 | `Sm86Heuristics`（`tune/sm8x.py`） | Ampere（GA10x） |
| 87 | `Sm87Heuristics`（`tune/sm8x.py`） | Ampere（Orin） |
| 89 | `Sm89Heuristics`（`tune/sm8x.py`） | Ada |
| 90 | `Sm90Heuristics`（`tune/sm90.py`） | Hopper |
| 100 / 103 / 110 | `Sm100Heuristics`（`tune/sm100.py`） | Blackwell |
| 120 | `Sm120Heuristics`（`tune/sm120.py`） | Blackwell（消费级） |
| 121 | `Sm121Heuristics`（`tune/sm121.py`） | Blackwell |
| 80（PPU） | `PPUSm80Heuristics`（`tune/ppu_sm80.py`） | 独立映射表 `ppu_heuristics_map` |

**每个 SM 版本一个独立类**（不是「Sm8x」这种合并写法）——86/87/89 虽在同一个 `sm8x.py` 文件里，但各是一个类，且存在继承关系（89 继承 86、87 继承 80），行为并不统一。

**特殊分派**：SM90 上还有一层名称判断——设备名含 "H20" 且不含 "H200" 时改用 `Sm90H20Heuristics`（`tune/sm90_h20.py`，H20 是降配版 Hopper，算力与带宽配比不同，需独立启发式）。

### DeviceHeuristics 基类

所有启发式继承同一基类（F-059，`humming/tune/base.py:35-41`）：

| 字段 | 含义 |
|------|------|
| `max_smem_size` | 设备共享内存上限——决定 tile 能开多大 |
| `b16_allowed_dtypes` / `b8_allowed_dtypes` / `b4_allowed_dtypes` | 按权重位宽分档的允许 dtype 列表 |
| `sm_version` | 目标架构 |
| `expert_probability_cv` | **MoE 专家负载波动指标**（coefficient of variation） |

`expert_probability_cv` 是 MoE 专属：它量化「各专家被路由到的 token 数有多不均匀」。波动大意味着 kernel 需要更保守的调度策略（栅格化、masked 模式）。

## 三、瓶颈判定：算力受限还是带宽受限

`_estimate_compute_bound_threshold()`（F-058，`tune/base.py:15-32`）是启发式的核心判据。它读设备信息并估算阈值：

```python
max_tops = info.tensorcore_tops[dtype]          # Tensor Core 峰值
max_bandwidth = info.memory_bandwidth_gbps      # 显存带宽

# SM75/86/89 + 浮点 dtype + f16 累加 → 峰值翻倍
if info.sm_version in (75, 86, 89) and "float" in dtype and use_f16_accum:
    max_tops *= 2

left_bias  = weight_nbytes / max_bandwidth                    # 权重读取时间
left_factor  = shape_k * a_dtype.num_bits / 8 / max_bandwidth # 激活读取时间
right_factor = shape_n * shape_k * 2 / max_tops               # 计算时间

threshold = left_bias / (right_factor - left_factor) * 1e3
```

**读法**：把「M 维多大时，计算时间开始超过访存时间」算成一个阈值 M。

- **M 小于阈值** → 访存受限（memory-bound）：权重读一次是主要成本，应优化访存（用 `dequant_fused`、更大的 tile 复用权重）。
- **M 大于阈值** → 计算受限（compute-bound）：应优化 MMA 利用率（更深的流水、更大的 warp tile）。

**SM75/86/89 峰值翻倍的原因**：这几个架构上没有原生 FP16 累加器，Humming 用 FP16 累加来模拟双倍吞吐——但前提是 dtype 是浮点。所以这个修正只在浮点 dtype 且显式开启 f16 累加时生效。

## 四、M 维候选集合

内核按 M（token 数）分档预编译——同一份权重在不同 M 下用不同 tile 配置，避免小 M 时浪费算力（F-057，`tune/base.py:546-560`）。

### 候选生成

```python
shape_m_candidates = [1, 2, 4, 8]
if cls.sm_version == 90:
    shape_m_candidates += list(range(8, max_shape_m, 8))     # 步长 8
else:
    shape_m_candidates += list(range(16, max_shape_m, 16))   # 步长 16
```

| 项 | 值 | 说明 |
|----|-----|------|
| 基础档 | `1, 2, 4, 8` | 小 batch 不浪费 |
| SM90 步长 | 8 | SM90 的候选步长为 8（`tune/base.py:546-560`） |
| 其他步长 | 16 | |
| Dense 上限 | 8192 | `max_shape_m = 8192` |
| MoE 上限 | 65536 | `max_shape_m = 65536`（MoE 聚合后 token 更多） |

### 对齐规则

```python
if shape_m > 1024  and shape_m % 16  != 0: continue
if shape_m > 2048  and shape_m % 32  != 0: continue
if shape_m > 4096  and shape_m % 64  != 0: continue
if shape_m > 16384 and shape_m % 128 != 0: continue
```

M 越大，tile 对齐要求越严——因为大 M 时 tile 边界的浪费占比虽小，但绝对误差会累积。

### 候选去重

源码在生成候选时会比较相邻候选的 `config_str`，相同则合并（F-057 上下文，`last_config_str == config_str` 分支）。这避免了为配置完全相同的 M 值重复编译——**直接减少编译时间与缓存条目数**。

## 五、约束闭合：设备能力反作用于 dtype

启发式不只选 tile，还要**否决**硬件不支持的组合：

```python
elif a_dtype.num_bits == 16:
    assert a_dtype in cls.b16_allowed_dtypes
elif a_dtype.num_bits == 8:
    assert a_dtype in cls.b8_allowed_dtypes
elif a_dtype.num_bits == 4:
    assert a_dtype in cls.b4_allowed_dtypes
else:
    raise AssertionError(f"unsupported a_dtype {a_dtype} on sm{cls.sm_version}")
```

即：**激活位宽 → 查对应档位的允许列表 → 断言**。这与 `check_dtype()` 的类型合法性检查是两道独立的关卡：

| 关卡 | 位置 | 检查什么 |
|------|------|---------|
| 类型合法性 | `check_dtype()`（kernel 层） | 位宽关系、符号性、架构门槛（F-013~F-017） |
| 设备可执行性 | `DeviceHeuristics`（tune 层） | 该架构的共享内存够不够、该 dtype 在该档位是否被允许（F-059） |

`max_smem_size` 是硬约束——`TuningConfig.block_shape` / `warp_shape` / `num_stages` 的组合不能超出共享内存上限。这也是 `TuningConfig` 里 `num_stages` 默认只有 2 的原因（SM100 除外）。

## 六、MoE 栅格化调度

`tune/raster.py` 提供两个函数（F-060）：

- `raster_group_m_for_config(config)` —— 给定配置算栅格化的 M 分组
- `get_moe_raster_group_m(...)` —— 供外部调用

配合 `TuningConfig.raster_group_m` 使用。

**栅格化（rasterization）是什么**：把 M 维的输出块在 GPU 上按二维栅格重新排列，而不是简单的线性顺序。目的是**改善 L2 cache 命中率**——把计算上邻近的 block 安排到物理上邻近的 SM，使共享的权重能留在 L2 中。

对 MoE 尤其重要：grouped GEMM 中同一专家的多个 token 块如果能聚到一起，权重读取次数会显著下降。这与 `evict_weights_first`（优先淘汰权重而非激活的缓存策略）是同一方向的优化。

## 七、启发式的稳定性（重要提醒）

**启发式是手工维护的类，不是稳定的 API**（F-056）：

- 每个 SM 版本一个独立类，类内手写 tile 形状、split-K、`num_stages` 等参数——**新增一张卡 = 新增或修改一个类**。
- `DeviceHeuristics` 的字段（如 `expert_probability_cv`）在基类给默认值，由各子类覆写。
- Humming 处于 0.1.x 快速迭代期（版本号三位数滚动），**这些参数不承诺跨版本兼容**。

**实践建议**：

1. **把启发式当作待观测的黑盒**，而不是可以直接抄进自有系统的配置来源。
2. 若要从源码抄某个 tile 配置到自己的系统，**必须在自己的机型上实测**——抄来的数字在升级后可能静默劣化。
3. 升级 Humming 版本后，务必重跑 [04 基准对拍](../examples/04-benchmarking.md) 的对照。
4. `tests/test_tuning_candidates.py` 验证的正是 M 维候选生成逻辑——升级后先跑它（F-098）。

## 八、常用调优参数速查

| 想要 | 调什么 | 注意 |
|------|--------|------|
| 大 batch 吞吐更高 | 更大的 `block_shape`、更多 `num_stages` | 受 `max_smem_size` 约束 |
| 小 batch 延迟更低 | 更小的 M 档位命中、`use_stream_k` | `use_stream_k` 默认已开 |
| MoE 专家负载不均 | `raster_group_m`、考虑 `GROUPED_MASKED` | 关注 `expert_probability_cv` |
| 需要 batch 不变性 | `use_batch_invariant=True` | 会牺牲部分性能 |
| Hopper 上极致性能 | `mma_type=WGMMA` + warp specialization | SM90 专属 |
| Blackwell 上极致性能 | `mma_type=UMMA` + `umma_*` 参数 | SM100+ 专属 |

> **默认即自动选择**：`tuning_config` 是可选参数，默认由启发式自动选定（README 示例注释，F-069）。手动指定前先跑基线。

## 九、延伸阅读

- [03 架构总览](03-architecture.md)：TuningConfig 的完整字段
- [04 内核设计](04-kernel-design.md)：tile 与流水级数如何落地
- [06 MoE 路径](06-moe.md)：栅格化在 MoE 中的实际作用
- [09 进阶主题](09-advanced.md)：autotune 的规划方向
