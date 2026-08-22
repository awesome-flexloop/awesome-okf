---
type: example
scope: engram
name: run-demo
description: 运行 Engram 演示代码，理解模块核心数据流
---

# 运行演示示例

本文展示如何运行 Engram 官方演示代码，理解模块的核心数据流。

## 环境准备

```bash
pip install torch numpy transformers sympy
```

Python 3.8+，建议使用 PyTorch 2.x 以支持 Flash Attention（完整版）。

## 运行官方 Demo

```bash
cd Engram
python engram_demo_v1.py
```

预期输出：

```
✅ Forward Complete!
input_ids.shape=torch.Size([1, L])
output.shape=torch.Size([1, L, 129280])
```

Demo 使用的示例文本：
```
"Only Alexander the Great could tame the horse Bucephalus."
```

## Demo 流程解析

### 1. 初始化模型

```python
from engram_demo_v1 import (
    EngramConfig, BackBoneConfig, engram_cfg, backbone_config,
    Engram, TransformerBlock, LLM
)

# 查看配置
print(f"Engram 插入层: {engram_cfg.layer_ids}")        # [1, 15]
print(f"最大 n-gram: {engram_cfg.max_ngram_size}")     # 3
print(f"嵌入维度: {engram_cfg.n_embed_per_ngram}")     # 512
print(f"哈希头数: {engram_cfg.n_head_per_ngram}")      # 8
print(f"骨干层数: {backbone_config.num_layers}")       # 30
print(f"隐藏维度: {backbone_config.hidden_size}")      # 1024
```

### 2. 分词

```python
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(
    engram_cfg.tokenizer_name_or_path, trust_remote_code=True
)
text = "Only Alexander the Great could tame the horse Bucephalus."
input_ids = tokenizer(text, return_tensors='pt').input_ids
print(f"Token 数: {input_ids.shape[1]}")
```

### 3. 前向传播

```python
import torch
import torch.nn as nn

# 构建简化的 LLM（含 mock 的 Attention/MoE）
LLM = nn.Sequential(
    nn.Embedding(backbone_config.vocab_size, backbone_config.hidden_size),
    *[TransformerBlock(layer_id=i) for i in range(backbone_config.num_layers)],
    nn.Linear(backbone_config.hidden_size, backbone_config.vocab_size)
)

B, L = input_ids.shape
hidden_states = LLM[0](input_ids)  # Token Embedding
hidden_states = hidden_states.unsqueeze(2).expand(-1, -1, backbone_config.hc_mult, -1)  # Mock mHC

# 逐层前向（Layer 1 和 15 有 Engram 模块）
for layer_idx in range(1, len(LLM) - 1):
    layer = LLM[layer_idx]
    if layer.engram is not None:
        print(f"  层 {layer_idx}: 包含 Engram 模块")
    hidden_states = layer(input_ids=input_ids, hidden_states=hidden_states)

hidden_states = hidden_states[:, :, 0, :]  # Mock mHC 聚合
output = LLM[-1](hidden_states)
print(f"输出形状: {output.shape}")  # (1, L, 129280)
```

## 独立测试 Engram 模块

```python
import torch
import numpy as np
from engram_demo_v1 import Engram, engram_cfg, backbone_config

# 创建 Layer 1 的 Engram 模块
engram = Engram(layer_id=1)
engram.eval()

# 构造模拟输入
B, L = 2, 32
# input_ids 需要 numpy 数组（哈希在 CPU 上用 numpy 计算）
input_ids_np = np.random.randint(0, 129280, size=(B, L), dtype=np.int64)
# hidden_states 需要 (B, L, hc_mult, D)
hidden_states = torch.randn(B, L, backbone_config.hc_mult, backbone_config.hidden_size)

# Engram 前向
with torch.no_grad():
    engram_output = engram(hidden_states=hidden_states, input_ids=input_ids_np)

print(f"Engram 输出形状: {engram_output.shape}")  # (2, 32, 4, 1024)
# 残差连接
hidden_states = engram_output + hidden_states
```

## 观察 N-gram 哈希行为

```python
from engram_demo_v1 import NgramHashMapping

hash_mapping = NgramHashMapping(
    engram_vocab_size=engram_cfg.engram_vocab_size,
    max_ngram_size=engram_cfg.max_ngram_size,
    n_embed_per_ngram=engram_cfg.n_embed_per_ngram,
    n_head_per_ngram=engram_cfg.n_head_per_ngram,
    layer_ids=engram_cfg.layer_ids,
    tokenizer_name_or_path=engram_cfg.tokenizer_name_or_path,
    pad_id=engram_cfg.pad_id,
    seed=engram_cfg.seed,
)

# 构造简单序列测试哈希
test_ids = np.array([[100, 200, 300, 400, 500]], dtype=np.int64)
hashes = hash_mapping.hash(test_ids)

for layer_id, layer_hashes in hashes.items():
    print(f"\n层 {layer_id} 哈希形状: {layer_hashes.shape}")
    # shape: (1, 5, 16) — B=1, L=5, num_heads=(2 ngram orders) * 8 heads = 16
    print(f"位置 0 的 bigram 头0哈希: {layer_hashes[0, 0, 0]}")
    print(f"位置 1 的 bigram 头0哈希: {layer_hashes[0, 1, 0]}")
    print(f"位置 1 的 trigram 头0哈希: {layer_hashes[0, 1, 8]}")

# 相同 n-gram 应映射到相同地址（确定性）
test_ids2 = np.array([[999, 200, 300, 400, 999]], dtype=np.int64)
hashes2 = hash_mapping.hash(test_ids2)
# 位置 1 (999,200) 和位置 2 (200,300) 的 bigram 应该与前面对应位置相同
# 验证：位置 2 的 bigram (200,300) 在两个序列中
print(f"\n相同 bigram 哈希一致: {hashes[1][0, 2, 0] == hashes2[1][0, 2, 0]}")
```

## 注意事项

1. **Demo 简化**：官方 Demo 中 Attention 和 MoE 是恒等映射（`lambda x: x`），仅展示 Engram 数据流
2. **Hyper-connection**：Demo 中 mock 了 mHC（multiplied by 4），完整实现中 hc 有复杂的路由机制
3. **CPU 哈希**：`NgramHashMapping.hash()` 接受 numpy 数组并在 CPU 上计算，生产版本可优化为 GPU 自定义 kernel
4. **嵌入表大小**：Demo 中嵌入表较小，生产版本的 Engram-27B 嵌入表规模更大
5. **质数模生成**：首次运行时 `find_next_prime` 可能需要几秒时间查找质数
