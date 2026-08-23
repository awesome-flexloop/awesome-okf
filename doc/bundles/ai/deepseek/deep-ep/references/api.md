---
type: reference
scope: deep-ep
name: DeepEP 公开 API
version: "2.1.0"
source: deep_ep/__init__.py
description: DeepEP 包的公开导出 API 清单，包括 Buffer、ElasticBuffer、EPHandle、EventOverlap、EventHandle、Config、topk_idx_t 及工具函数
---

# DeepEP 公开 API 参考

DeepEP 包入口为 `deep_ep/__init__.py`，导入时自动执行 NCCL 库一致性检查（`check_nccl_so()`）和 JIT 运行时初始化（`init_jit()`）。版本号为 `__version__ = '2.1.0'`。

## 模块导出一览

| 符号 | 类型 | 来源模块 | 说明 |
|------|------|----------|------|
| `Buffer` | class | `deep_ep.buffers.legacy` | V1 遗留通信缓冲区 |
| `ElasticBuffer` | class | `deep_ep.buffers.elastic` | V2 弹性通信缓冲区（推荐使用） |
| `EPHandle` | class | `deep_ep.buffers.elastic` | Dispatch 返回的通信句柄，用于 combine 和缓存 dispatch |
| `EventOverlap` | class | `deep_ep.utils.event` | 计算-通信重叠事件包装器 |
| `EventHandle` | class | C 扩展 `_C` | 底层 CUDA 事件句柄 |
| `Config` | struct | C 扩展 `_C` | V1 Buffer 的 dispatch/combine 配置 |
| `topk_idx_t` | dtype | C 扩展 `_C` | Top-k 索引张量类型（默认 `torch.int64`） |
| `get_physical_domain_size` | function | `deep_ep.utils.envs` | 获取物理域大小 `(num_rdma_ranks, num_nvlink_ranks)` |
| `get_logical_domain_size` | function | `deep_ep.utils.envs` | 获取逻辑域大小 `(num_scaleout_ranks, num_scaleup_ranks)` |

---

## 初始化行为

包导入时自动执行以下操作：

1. **持久化环境变量加载**：从 `deep_ep.envs.persistent_envs` 读取安装时捕获的环境变量默认值（如 `EP_JIT_CACHE_DIR`、`EP_NCCL_ROOT_DIR`、`EP_NUM_TOPK_IDX_BITS`），仅在用户未设置时生效。

2. **NCCL 库一致性检查**（`check_nccl_so()`）：
   - 读取 `/proc/self/maps` 检查运行时加载的 `libnccl.so`
   - 若发现多个不同的 NCCL 库或版本不匹配，assert 失败
   - 设置环境变量 `EP_SUPPRESS_NCCL_CHECK=1` 可跳过

3. **JIT 运行时初始化**（`init_jit()`）：
   - 调用 `_C.init_jit(library_root_path, cuda_home, nccl_root)`
   - CUDA 路径查找顺序：`CUDA_HOME` → `CUDA_PATH` → `which nvcc` → `/usr/local/cuda`
   - NCCL 路径通过 `find_nccl_root()` 查找

---

## 数据类型

### topk_idx_t

```python
deep_ep.topk_idx_t  # torch.int64（默认 EP_NUM_TOPK_IDX_BITS=64）
```

Top-k 专家索引专用 dtype。默认 64 位整数，可通过环境变量 `EP_NUM_TOPK_IDX_BITS` 在安装时配置为更小位宽以节省带宽。

### Config（V1 遗留）

```python
Config(num_sms, num_max_nvl_chunked_send_tokens, num_max_nvl_chunked_recv_tokens,
       num_max_rdma_chunked_send_tokens, num_max_rdma_chunked_recv_tokens)
```

V1 `Buffer` 的 dispatch/combine 内核配置结构体，包含5个整数字段：

| 字段 | 说明 |
|------|------|
| `num_sms` | 使用的 SM 数量 |
| `num_max_nvl_chunked_send_tokens` | NVLink 分块发送最大 token 数 |
| `num_max_nvl_chunked_recv_tokens` | NVLink 分块接收最大 token 数（必须 > send） |
| `num_max_rdma_chunked_send_tokens` | RDMA 分块发送最大 token 数 |
| `num_max_rdma_chunked_recv_tokens` | RDMA 分块接收最大 token 数（必须 ≥ 2×send） |

构造时自动将 `num_max_rdma_chunked_recv_tokens` 向上对齐到 `num_max_rdma_chunked_send_tokens` 的整数倍。

**推荐配置**：通过静态方法获取：
- `Buffer.get_dispatch_config(num_ranks) -> Config`：支持 rank 数 2/4/8/16/24/32/48/64/96/128/144/160
- `Buffer.get_combine_config(num_ranks) -> Config`：同样的 rank 数支持

---

## 工具函数

### get_physical_domain_size()

```python
from deep_ep import get_physical_domain_size
num_rdma_ranks, num_nvlink_ranks = get_physical_domain_size(group)
```

返回指定进程组的物理域大小。`num_rdma_ranks` 是跨节点 RDMA 通信的 rank 组数，`num_nvlink_ranks` 是节点内 NVLink 直连的 rank 数。

### get_logical_domain_size()

```python
from deep_ep import get_logical_domain_size
num_scaleout_ranks, num_scaleup_ranks = get_logical_domain_size(group, allow_hybrid_mode=True)
```

返回指定进程组的逻辑域大小。`num_scaleout_ranks` 对应跨节点通信维度，`num_scaleup_ranks` 对应节点内通信维度。

---

## 相关参考

- [ElasticBuffer API](/ai/deepseek/deep-ep/references/buffer-elastic) — V2 弹性缓冲区完整 API
- [Buffer (Legacy) API](/ai/deepseek/deep-ep/references/buffer-legacy) — V1 遗留缓冲区 API
- [事件系统](/ai/deepseek/deep-ep/references/events) — EventOverlap/EventHandle 使用方法
- [JIT 编译系统](/ai/deepseek/deep-ep/references/jit-system) — 运行时内核编译机制
