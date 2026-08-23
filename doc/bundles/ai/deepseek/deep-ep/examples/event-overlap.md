---
type: example
scope: deep-ep
name: 计算-通信重叠
version: "2.1.0"
source: deep_ep/utils/event.py, deep_ep/buffers/elastic.py
description: 使用 EventOverlap 实现 dispatch/combine 通信与专家计算重叠的完整示例，包括基本重叠、钩子回调、链式事件等待、异步模式
---

# 计算-通信重叠示例

计算-通信重叠是 DeepEP 性能优化的核心技术之一。通过独立的通信流和 `EventOverlap` 事件系统，可以在通信进行的同时在计算流上执行不依赖通信结果的计算，隐藏通信延迟。

## 1. 基本重叠模式

最常见的重叠模式：dispatch 通信在后台进行，同时准备下一批数据或执行不依赖 dispatch 结果的计算。

```python
import torch
import torch.distributed as dist
import deep_ep

dist.init_process_group('nccl')
rank = dist.get_rank()
torch.cuda.set_device(rank)

# 创建缓冲区
buffer = deep_ep.ElasticBuffer(
    group=dist.group.WORLD,
    num_max_tokens_per_rank=2048,
    hidden=4096,
    num_topk=8,
    prefer_overlap_with_compute=True,  # 倾向使用更少 SM，留给计算
)

hidden_states = torch.randn(1024, 4096, device='cuda', dtype=torch.bfloat16)
topk_idx = torch.randint(0, 64, (1024, 8), device='cuda',
                          dtype=deep_ep.topk_idx_t)
topk_weights = torch.softmax(
    torch.randn(1024, 64, device='cuda'), dim=-1
)
topk_weights = torch.topk(topk_weights, 8, dim=-1).values

# ---- 方法 A：with 语句自动等待 ----
# Dispatch 在通信流上异步执行，立即返回
recv_x, recv_topk_idx, recv_weights, handle, event = buffer.dispatch(
    x=hidden_states,
    topk_idx=topk_idx,
    topk_weights=topk_weights,
    num_experts=64,
)

# 此时通信正在通信流上进行
# 计算流可以执行不依赖 recv_x 的工作：
# - 准备下一批数据的 embedding
# - LayerNorm 等预处理
# - CUDA Graph 重放
prepare_next_batch()
do_layernorm_for_next_step()

# with 语句退出时自动调用 event.current_stream_wait()
# 确保 recv_x 已就绪后才使用
with event:
    # 这里 recv_x 已保证就绪
    expert_output = expert_forward(recv_x)

# Combine 同样支持重叠
combined, _, combine_event = buffer.combine(
    expert_output, handle, topk_weights=recv_weights,
)

with combine_event:
    # 通信完成后使用 combined 结果
    output = post_process(combined)
```

## 2. 手动等待模式

对等待时机需要精细控制时，使用 `current_stream_wait()`：

```python
recv_x, _, _, handle, event = buffer.dispatch(
    hidden_states, topk_idx=topk_idx, topk_weights=topk_weights,
    num_experts=64,
)

# 做一些不依赖 recv_x 的工作
do_some_computation()

# 显式等待 dispatch 完成
event.current_stream_wait()

# 现在 recv_x 可以安全使用
expert_output = expert_forward(recv_x)
```

## 3. 钩子回调（Hook After Wait）

`register_hook_after_wait()` 允许在等待完成后自动执行回调函数。典型用途是确定性排序——dispatch 完成后需要对接收的 token 排序，但排序在等待通信完成后才能执行：

```python
recv_x, _, recv_weights, handle, event = buffer.dispatch(
    hidden_states, topk_idx=topk_idx, topk_weights=topk_weights,
    num_experts=64,
)

# 注册钩子：等待完成后自动执行排序
# 这在 deterministic=True 时由 dispatch 自动注册，
# 但你也可以自定义钩子
def post_dispatch_hook():
    # 在通信完成后、使用 recv_x 之前执行的操作
    # 例如：自定义重排、统计信息收集等
    pass

event.register_hook_after_wait(post_dispatch_hook)

with event:
    # 退出 with 时：
    # 1. current_stream_wait() 等待通信完成
    # 2. 执行 post_dispatch_hook()
    # 3. 然后执行下方代码
    expert_output = expert_forward(recv_x)
```

注意：
- 同一 `EventOverlap` 实例只能注册一个钩子
- 钩子执行后自动清空，不会重复执行

## 4. 链式事件等待

当有多个通信操作需要串行执行时（避免网络资源竞争），使用 `previous_event` 参数形成事件链：

```python
# 第一次 dispatch
recv_x1, _, _, handle1, event1 = buffer.dispatch(
    x1, topk_idx=topk_idx1, num_experts=64,
)

# 第二次 dispatch 等待第一次完成后才开始
# 避免两个 dispatch 同时竞争网络带宽
recv_x2, _, _, handle2, event2 = buffer.dispatch(
    x2, topk_idx=topk_idx2, num_experts=64,
    previous_event=event1.event,  # 等待 event1 完成
)

# 使用 with 分别等待
with event1:
    out1 = expert_forward(recv_x1)

with event2:
    out2 = expert_forward(recv_x2)
```

`previous_event_before_epilogue` 类似，但只在 epilogue 阶段前等待，允许前一个通信的主体和后一个通信重叠。

## 5. 异步模式（async_with_compute_stream）

`async_with_compute_stream=True` 时，dispatch/combine 不在计算流上插入等待，完全异步执行。用户需要手动管理同步：

```python
recv_x, _, _, handle, event = buffer.dispatch(
    hidden_states, topk_idx=topk_idx, num_experts=64,
    async_with_compute_stream=True,  # 完全异步，不阻塞计算流
)

# 计算流继续执行，完全不等待通信
# 可以执行大量计算工作
do_heavy_computation()

# 需要使用 recv_x 时，必须显式等待
event.current_stream_wait()
expert_output = expert_forward(recv_x)
```

这种模式提供最大的灵活性，但要求用户完全负责同步管理，容易出错。建议在充分理解流同步机制时使用。

## 6. release_handle 自动释放

使用 `event(release_handle=True)` 在等待完成后自动释放事件引用，适用于短生命周期事件：

```python
recv_x, _, _, handle, event = buffer.dispatch(
    hidden_states, topk_idx=topk_idx, num_experts=64,
)

# with 块退出时自动释放事件句柄
with event(release_handle=True):
    expert_output = expert_forward(recv_x)
# 退出后 event.event 已被置为 None，张量引用释放
```

## 7. 典型训练步中的重叠策略

在 MoE 训练的前向传播中，通常的重叠策略如下：

```python
def moe_layer_forward(buffer, hidden_states, expert_modules, config):
    """
    MoE 层前向传播，带计算-通信重叠。
    """
    num_tokens = hidden_states.shape[0]

    # ---- (1) Gating 网络计算（在计算流上）----
    gate_logits = gate_proj(hidden_states)
    topk_weights = torch.softmax(gate_logits, dim=-1)
    topk_weights, topk_idx = torch.topk(topk_weights, config.top_k, dim=-1)
    topk_idx = topk_idx.to(deep_ep.topk_idx_t)

    # ---- (2) Dispatch（异步启动通信）----
    recv_x, _, recv_weights, handle, dispatch_event = buffer.dispatch(
        x=hidden_states,
        topk_idx=topk_idx,
        topk_weights=topk_weights,
        num_experts=config.num_experts,
        expert_alignment=config.expert_alignment,
    )

    # ---- (3) 通信与计算重叠：准备 attention/其他层 ----
    # 此时 dispatch 在通信流上进行，计算流空闲
    # 可以做 dropout 准备、缩放因子计算等
    prepare_dropout_mask()

    # ---- (4) 等待 dispatch 完成 ----
    with dispatch_event:
        # recv_x 就绪
        expert_output = run_experts(recv_x, handle, expert_modules)

    # ---- (5) Combine（异步启动通信）----
    combined, _, combine_event = buffer.combine(
        expert_output, handle,
        topk_weights=recv_weights,
    )

    # ---- (6) 通信与计算重叠：准备 residual ----
    # combine 在通信流上进行，可以准备 residual 连接等
    residual = hidden_states  # residual 不需要 combine 结果

    # ---- (7) 等待 combine 完成 ----
    with combine_event:
        output = combined + residual  # residual add
        output = output_norm(output)

    return output
```

## 8. 反向传播中的重叠

反向传播同样需要 dispatch/combine（梯度的分发和聚合），重叠策略与前向类似：

```python
# 前向
recv_x, _, recv_weights, handle, fwd_event = buffer.dispatch(...)
with fwd_event:
    expert_out = expert_forward(recv_x)
combined, _, fwd_combine_event = buffer.combine(expert_out, handle, ...)
with fwd_combine_event:
    loss = criterion(combined, labels)

# 反向
loss.backward()

# 反向传播中的 EP 梯度通信由 autograd 自动处理
# 但可以通过设置 prefer_overlap_with_compute=True 让 DeepEP
# 自动在反向中使用更少 SM 以重叠计算和梯度通信
```

## 9. 多流等待场景

一个事件可以被多个流等待：

```python
recv_x, _, _, handle, event = buffer.dispatch(
    hidden_states, topk_idx=topk_idx, num_experts=64,
)

# 在不同流上等待同一个事件
stream1 = torch.cuda.Stream()
stream2 = torch.cuda.Stream()

with torch.cuda.stream(stream1):
    event.current_stream_wait()
    # stream1 上的计算等待 dispatch 完成
    compute_on_stream1(recv_x)

with torch.cuda.stream(stream2):
    event.current_stream_wait()  # 注意：不使用 release_handle
    # stream2 上的计算也等待 dispatch 完成
    compute_on_stream2(recv_x)

# 最后在主流上等待
event.current_stream_wait(release_handle=True)  # 最后使用的流可以释放
```

注意：多流等待时不要在前几个流上使用 `release_handle=True`，否则事件会被提前释放，后续流无法等待。

## 10. 使用 capture() 手动记录事件

`ElasticBuffer.capture()` 静态方法可以在任意流上捕获事件：

```python
# 在当前流上记录一个事件
my_event = deep_ep.ElasticBuffer.capture()

# 在通信流上等待这个事件
# （通过 previous_event 参数间接实现）
recv_x, _, _, handle, event = buffer.dispatch(
    hidden_states, topk_idx=topk_idx, num_experts=64,
    previous_event=my_event,
)
```

## 性能提示

1. **SM 分配权衡**：`prefer_overlap_with_compute=True` 让通信使用更少 SM，留出更多 SM 给计算，通常在训练中效果更好；纯通信场景（无计算重叠）设为 `False` 可最大化带宽。

2. **避免空等**：`with event:` 之前尽可能放置不依赖通信结果的工作，最大化重叠窗口。

3. **通信流优先级**：ElasticBuffer 使用高优先级通信流，确保通信操作及时获得 GPU 调度。

4. **NUMA 亲和性**：确保 GPU 和 NIC 在同一 NUMA 节点上，减少跨 NUMA 访问开销。

5. **CUDA Graph 兼容**：`EventOverlap` 的 `extra_tensors` 参数设计为兼容 CUDA Graph，但 V2 中张量记录已移至 `EventHandle` 内部，通常不需要手动设置。

## 相关参考

- [事件系统 API](/ai/deepseek/deep-ep/references/events)
- [ElasticBuffer API](/ai/deepseek/deep-ep/references/buffer-elastic)
- [基础 MoE 示例](basic-moe.md)
- [ElasticBuffer 配置示例](elastic-buffer.md)
- [Dispatch/Combine 流程](/ai/deepseek/deep-ep/concepts/dispatch-combine)
