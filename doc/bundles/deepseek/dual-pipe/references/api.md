---
type: reference
scope: dual-pipe
name: DualPipe 公开 API
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/dualpipe/__init__.py, dualpipe/dualpipe.py, dualpipe/dualpipev.py
description: DualPipe 公开 API 参考，包含 DualPipe、DualPipeV 类和工具函数的完整签名
---

# DualPipe 公开 API 参考

## 模块入口

| 符号 | 类型 | 来源 |
|------|------|------|
| `DualPipe` | class | `dualpipe.dualpipe` |
| `DualPipeV` | class | `dualpipe.dualpipev` |
| `WeightGradStore` | class | `dualpipe.utils` |
| `set_p2p_tensor_shapes` | function | `dualpipe.comm` |
| `set_p2p_tensor_dtype` | function | `dualpipe.comm` |

---

## class DualPipe(nn.Module)

双向流水线并行引擎。每个 GPU 持有两个对称 pipeline stage，实现计算-通信完全重叠。

```python
DualPipe(
    modules: Tuple[nn.Module, nn.Module],
    batch_dim: int = 0,
    process_group: Optional[dist.ProcessGroup] = None,
    rank_mapping: Optional[List[int]] = None
)
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `modules` | `Tuple[nn.Module, nn.Module]` | 两个 pipeline stage 的模块 |
| `batch_dim` | `int` | 微批次切分维度，默认 0 |
| `process_group` | `Optional[dist.ProcessGroup]` | PyTorch 分布式进程组，默认使用默认组 |
| `rank_mapping` | `Optional[List[int]]` | PP rank 到进程组 rank 的映射，默认为恒等映射 |

**关键实例属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `module` | `nn.ModuleList` | 两个模块的 ModuleList 容器 |
| `group` | `dist.ProcessGroup` | 进程组 |
| `num_ranks` | `int` | 进程组中的 rank 总数（必须为偶数） |
| `rank` | `int` | 当前 rank 在 PP 中的位置 |
| `is_first_rank` | `bool` | 是否为第一个 stage |
| `is_last_rank` | `bool` | 是否为最后一个 stage |
| `is_in_second_half` | `bool` | 是否在后半部分 rank |
| `is_middle_rank` | `bool` | 是否为中间两个 rank 之一 |
| `overlapped_forward_backward` | `bool` | 模块是否支持自定义前后向重叠 |

### DualPipe.step()

```python
step(
    *inputs: Optional[torch.Tensor],
    num_chunks: int = 0,
    criterion: Optional[Callable] = None,
    labels: List[Optional[torch.Tensor]] = [],
    return_outputs: bool = False
) -> Tuple[Optional[torch.Tensor], Optional[Union[torch.Tensor, Tuple[torch.Tensor]]]]
```

执行一个完整的前向-反向训练步或前向推理步。

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `*inputs` | `Optional[torch.Tensor]` | 输入 tensor（第一/最后 rank 提供，中间 rank 传 None） |
| `num_chunks` | `int` | 微批次数量，必须为偶数且 ≥ 2×num_ranks |
| `criterion` | `Optional[Callable]` | 损失函数，签名 `criterion(outputs, labels) -> loss` |
| `labels` | `List[Optional[torch.Tensor]]` | 标签，对应两个方向 |
| `return_outputs` | `bool` | 是否返回模型输出 |

**返回值：**

`(loss, outputs)` 元组：
- `loss`：仅在第一/最后 rank 返回损失 tensor，其他 rank 返回 None
- `outputs`：当 `return_outputs=True` 时返回输出 tensor，否则 None

**约束：**
- `num_ranks` 必须为偶数
- `num_chunks` 必须为正偶数且 ≥ 2×num_ranks
- 训练模式需要 `criterion` 和 `labels`

---

## class DualPipeV(nn.Module)

V 型双向流水线并行引擎。比 DualPipe 节省一半 GPU，每个 GPU 持有两个 stage，但采用 V 型连接。

```python
DualPipeV(
    modules: Tuple[nn.Module, nn.Module],
    batch_dim: int = 0,
    process_group: Optional[dist.ProcessGroup] = None,
    rank_mapping: Optional[List[int]] = None
)
```

参数与 DualPipe 相同。

**与 DualPipe 的关键差异：**
- GPU 数量只需要 pp_size 个（DualPipe 需要 2×pp_size 个）
- `num_chunks` 只需 ≥ 2×num_ranks，不需要是偶数
- Loss 仅在 `is_first_rank` 处计算
- 最后 rank 处 phase 0 输出直接传递给 phase 1 输入（V 型连接）

### DualPipeV.step()

签名与 DualPipe.step() 相同。

---

## 通信配置函数

### set_p2p_tensor_shapes()

```python
set_p2p_tensor_shapes(shapes: List[Tuple[int]]) -> None
```

设置 P2P 通信 tensor 的形状列表。必须在调用 `step()` 之前调用。

### set_p2p_tensor_dtype()

```python
set_p2p_tensor_dtype(dtype: torch.dtype) -> None
```

设置 P2P 通信 tensor 的数据类型。必须在调用 `step()` 之前调用。

---

## class WeightGradStore

权重梯度计算延迟存储工具类，用于零气泡优化。

| 方法 | 签名 | 说明 |
|------|------|------|
| `put` | `put(func: Callable) -> None` | 将权重梯度计算函数加入缓存 |
| `flush` | `flush() -> None` | 将缓存函数移到执行队列 |
| `pop` | `pop() -> None` | 从队列取出并执行一批函数 |
| `clear` | `clear() -> None` | 清空缓存和队列 |

**类属性：**

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | `bool` | `False` | 是否启用延迟存储（零气泡模式） |
| `cache` | `List[Callable]` | `[]` | 当前缓存的函数列表 |
| `funcs_queue` | `queue.Queue` | 空队列 | 待执行函数队列 |
