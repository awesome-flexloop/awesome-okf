---
type: Example
title: "实战 02：MoE GEMM"
description: "Humming MoE GEMM 实战——四种 GEMM 形态的选择、grouped 布局的构造、expert 分布不均的模拟与栅格化调优、MoE 专属参数逐项说明"
tags: [humming, example, moe, grouped-gemm, routing, rasterization, expert-balance]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /references/facts.md
    title: 本地源码检出事实清单
---

# 实战 02：MoE GEMM

> 场景页。MoE 是 Humming 性能优势最集中的领域（官方 MoE W4A16 加速比普遍高于 Dense，F-083）。本文讲清四种 GEMM 形态怎么选，以及 grouped 布局怎么构造。

## 一、先选对 GEMM 形态

`GemmType` 四态（F-036）：

| 形态 | 权重布局 | 何时用 |
|------|---------|--------|
| `DENSE` | 普通 (N, K) | MoE 的某个专家单独计算（调试基线） |
| `INDEXED` | (E, N, K) + 行索引数组 | router 动态决定每 token 用哪个专家权重行 |
| `GROUPED_CONTIGUOUS` | (E, N, K) 连续 + 分组偏移 | token 已按专家排序分组（**主流 MoE 布局**） |
| `GROUPED_MASKED` | 同上 + 掩码 | 专家容量受限，需要丢弃多余 token |

**派生属性自动从 `gemm_type` 推导**（F-033）：`is_indexed_gemm`、`is_grouped_contiguous_gemm`、`is_grouped_masked_gemm`、`is_grouped_gemm`——不需要手工设置。

**约束**：`INDEXED` 不支持 m-major input scale（F-034）。

## 二、GROUPED_CONTIGUOUS 的数据结构

### 核心参数（F-049）

| 参数 | 含义 |
|------|------|
| `sorted_ids` | 按专家分组排序后的 token ID 序列 |
| `expert_ids` | 每个分组的专家 ID |
| `num_tokens_padded` | 补齐后各分组的 token 数 |
| `expert_layout` | 专家权重排布方式 |
| `locks` | **stream-k 累加锁**（非专家级锁；vLLM 侧由 `create_humming_locks` 创建，F-076） |

### 分组构造示意（以 GROUPED_CONTIGUOUS 为例）

假设 3 个专家、8 个 token，router 结果为：

```
token:  0  1  2  3  4  5  6  7
expert: 2  0  2  1  2  0  1  2
```

按专家分组后：

```
expert 0: tokens [1, 5]       → 2 个
expert 1: tokens [3, 6]       → 2 个
expert 2: tokens [0, 2, 4, 7] → 4 个
```

对应参数：

```python
# expert_layout：长度 = num_experts + 1 = 4，token 边界 offset
expert_layout = torch.tensor([0, 2, 4, 8], dtype=torch.int32)

# 权重按专家连续排布：(num_experts, shape_n, shape_k)
weight = torch.randn((3, shape_n, shape_k), ...)
```

**边界 offset 的含义**：`expert_layout[i]` 到 `expert_layout[i+1]` 之间是第 i 个专家的 token 区间。上例中 expert 0 占 `[0, 2)`、expert 1 占 `[2, 4)`、expert 2 占 `[4, 8)`。

**为什么需要补齐**：不同专家分到的 token 数不同，kernel 要按统一 tile 处理就必须把每段补齐到对齐边界。补齐部分通过掩码排除在计算之外。`num_tokens_padded` 正是记录补齐后数量的参数（INDEXED 形态下必需）。

> ⚠️ **GROUPED_MASKED 的 `expert_layout` 不同**：它是长度 `num_experts` 的「每专家 token 数」数组，不是 offset 数组。两者的构造方式不能互换。


### 权重布局

```python
weight = torch.randn((num_experts, shape_n, shape_k),
                     dtype=torch.float16, device=dev)
```

MoE 时 `load_from_unquantized()` 的输入形状断言为 `(num_experts, shape_n, shape_k)`（F-066）。

## 三、GROUPED_MASKED：容量受限

当 MoE 用了 **capacity factor** 限制每个专家最多接收 N 个 token 时，超出的 token 必须被丢弃。这时需要 masked 形态——**掩码掉**多余 token 而不是重路由到兜底专家。

```python
# 概念示意：每个专家最多接收 capacity 个 token
capacity = 4
# 假设有 4 个专家、每个专家最多接收 4 个 token：
# 当某专家被路由的 token 数超过 4 时，多出的 token 被掩码丢弃
```

**关键区别**：`GROUPED_CONTIGUOUS` 保证每个 token 都有一个有效归属；`GROUPED_MASKED` 允许 token 无归属（被丢弃）。

> 实践含义：如果你在 vLLM 里看到某些 token 输出为 0 或异常值，检查是否该用 masked 形态而用了 contiguous。

## 四、模拟专家负载不均

真实 MoE 的 router 会产生**不均衡的专家分布**——这正是 `expert_probability_cv`（专家负载波动系数）存在的意义（F-059）。

```python
import numpy as np

def make_skewed_expert_ids(num_tokens: int, num_experts: int, skew: float = 0.0):
    """skew=0 均衡；skew 越大越集中到少数专家"""
    if skew == 0:
        return np.random.randint(0, num_experts, size=num_tokens)

    # 用幂律制造长尾
    probs = (np.arange(1, num_experts + 1) ** (-skew))
    probs = probs / probs.sum()
    return np.random.choice(num_experts, size=num_tokens, p=probs)
```

### 观察不均衡的影响

```python
for skew in [0.0, 1.0, 2.0]:
    expert_ids = make_skewed_expert_ids(4096, 8, skew)
    counts = np.bincount(expert_ids, minlength=8)
    cv = counts.std() / counts.mean()   # 变异系数 ≈ expert_probability_cv
    print(f"skew={skew}  counts={counts}  cv={cv:.3f}")
```

**预期**：skew 越大，cv 越大。cv 大意味着：

1. 某些分组的 M 远大于其他分组 → tile 浪费
2. 权重访问的局部性变差 → L2 命中率下降
3. 栅格化调度的收益变大（F-060）

## 五、栅格化调优

栅格化把 M 维输出块按二维栅格重排而非线性排列，目的是**让计算上邻近的 block 落在物理上邻近的 SM**，共享权重留在 L2 中（F-060，`tune/raster.py`）。

```python
from humming.tune.raster import get_moe_raster_group_m

group_m = get_moe_raster_group_m(...)
```

配合 `TuningConfig.raster_group_m` 使用。

**调优建议**：

| 场景 | 建议 |
|------|------|
| 专家分布均衡（cv 小） | 栅格化收益有限，用默认即可 |
| 专家分布倾斜（cv 大） | 尝试不同 `raster_group_m` 值，用 [04 基准对拍](04-benchmarking.md) 的方法实测 |
| 有 `evict_weights_first` 可用 | 与栅格化同方向（优先保留权重在 cache 中），可一并启用 |

> **注意**：`raster_group_m` 的最优值依赖 shape、位宽、架构，**没有通用答案**。源码提供 `raster_group_m_for_config()` 按配置计算，但实际是否更优仍需实测。

## 六、MoE 性能基线

```python
import time

def bench_moe(num_experts=8, top_k=2, num_tokens=4096,
              shape_n=512, shape_k=7168, dtype="int4"):
    layer = HummingLayer(
        shape_n=shape_n,
        shape_k=shape_k,
        num_experts=num_experts,
        weight_config={"dtype": dtype},
        torch_dtype=torch.float16,
    ).cuda()

    weight = torch.randn((num_experts, shape_n, shape_k),
                         dtype=torch.float16, device=dev)
    layer.load_from_unquantized(weight)
    layer.transform()

    # 构造分组（GROUPED_CONTIGUOUS 语义）
    expert_ids = make_skewed_expert_ids(num_tokens, num_experts)
    order = np.argsort(expert_ids, kind="stable")   # 按专家稳定排序
    grouped = expert_ids[order]
    counts = np.bincount(grouped, minlength=num_experts)  # 每专家 token 数
    # padding 到 16 对齐 → 补齐后的每专家 token 数
    padded = ((counts + 15) // 16) * 16
    # expert_layout：token 边界 offset，长度 = num_experts + 1
    expert_layout = torch.tensor(
        [0] + np.cumsum(padded).tolist(), dtype=torch.int32
    )

    # warmup
    for _ in range(5):
        layer(inputs)
    torch.cuda.synchronize()

    t0 = time.perf_counter()
    for _ in range(50):
        layer(inputs)
    torch.cuda.synchronize()
    dt = (time.perf_counter() - t0) / 50 * 1e3
    print(f"moe e={num_experts} top{top_k} tok={num_tokens}: {dt:.3f} ms")
```

**M 维上限差异**（F-057）：Dense 的 M 候选上限是 8192，**MoE 是 65536**。因为 MoE 把所有专家的 token 聚合后计算，总 M 更大——这直接导致 MoE 的 kernel 候选空间更大、编译时间更长。

**官方基准的用例命名可作参考**（F-096）：

```
moe_e256_k8_n512_k7168_g128x128
     │   │  │   │     │    └── group size 128x128
     │   │  │   │     └────── K=7168
     │   │  │   └──────────── N=512
     │   │  └──────────────── top-8
     │   └─────────────────── 256 专家
     └─────────────────────── MoE
```

## 七、在 vLLM 中跑 MoE

真实场景通常不直接调 `humming_gemm()`，而是通过 vLLM：

```bash
vllm serve <model> --moe-backend humming
```

vLLM 侧会处理分组构造、激活表达式翻译、专家锁等（见 [06 MoE 路径](../concepts/06-moe.md) 与 [07 vLLM 集成](../concepts/07-vllm-integration.md)）。

**vLLM 侧为此专门实现的两套逻辑**（F-078）：

| 模块 | 作用 |
|------|------|
| `utils/humming/priority.py` | `prefers_humming()` / `prioritize_humming()` — 决定何时该用 Humming |
| `utils/humming/activation.py` | 12 种 MoE 激活 → humming 可执行表达式 |

## 八、排查清单

| 症状 | 优先排查 |
|------|---------|
| 输出为 0 或异常 | 该用 masked 形态却用了 contiguous；检查 `num_tokens_padded` |
| 分组边界错位 | `sorted_ids` 未稳定排序；`expert_ids` 与分组数不一致 |
| 专家数对不上 | `num_experts` 与权重 shape 的第 0 维一致 |
| 性能不如预期 | 专家负载不均衡（看 cv）；栅格化未调；M 档位命中不佳 |
| 编译时间过长 | MoE 的 M 上限 65536 → 候选更多；确认缓存目录可写且已被复用 |

## 九、下一步

- [04 基准对拍](04-benchmarking.md)：与 Marlin / Triton MoE 横向比
- [06 MoE 路径](../concepts/06-moe.md)：机制细节与端到端数据
- [03 vLLM 服务化](03-vllm-serving.md)：完整服务化流程
