---
type: reference
title: "图表示 Graph 类与重写机制（Rewriter / GraphMatcher）"
description: "tf2onnx 内部图表示 Graph/Node 类 API 与图重写机制（rewriter 函数签名、OpTypePattern 模式匹配）的信源登记"
sources:
  - path: "tf2onnx/graph.py"
    facts: [F-022, F-023, F-024, F-025, F-026]
  - path: "tf2onnx/graph_matcher.py"
    facts: [F-030]
  - path: "tf2onnx/tfonnx.py"
    facts: [F-027, F-028, F-029]
---

# 图表示 Graph 类与重写机制（Rewriter / GraphMatcher）

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `tf2onnx/graph.py` | Python 模块 | Node 类（ONNX NodeProto 包装）、Graph 类（图操作 API）、ExternalTensorStorage（大模型外部存储） |
| `tf2onnx/graph_matcher.py` | Python 模块 | OpTypePattern 树形模式匹配器、MatchResult 匹配结果 |
| `tf2onnx/tfonnx.py` | Python 模块 | run_rewriters 重写器执行框架、预处理/后处理重写器注册、重写器函数实现 |

## 关键事实登记

### F-022：Node 类——ONNX NodeProto 的包装器

**信源**：`tf2onnx/graph.py`

Node 类是 ONNX `NodeProto` 的包装器，维护内部状态并提供图操作方法：

```python
class Node(object):
    def __init__(self, node, graph=None):
        self._node = node  # 底层 ONNX NodeProto
        self._input = list(node.input)   # 输入列表
        self._output = list(node.output)  # 输出列表
        self._attr = {}  # 属性字典（从 proto 提取并缓存）
        self.graph = graph  # 所属 Graph 引用
```

**核心方法分类**：

| 类别 | 方法 | 说明 |
|------|------|------|
| 类型判断 | `is_const()` | 是否为常量节点 |
| | `is_graph_input()` | 是否为图输入 |
| | `is_while()` | 是否为循环节点 |
| 属性操作 | `get_attr(name, default=None)` | 获取属性值 |
| | `set_attr(name, value)` | 设置属性 |
| 输入操作 | `replace_input(idx, new_input)` | 替换指定位置输入 |
| | `replace_all_inputs(old, new)` | 全局替换输入引用 |

### F-023：Graph 类的索引体系

**信源**：`tf2onnx/graph.py`

Graph 类维护多个索引以加速图遍历和操作：

```python
class Graph(object):
    def __init__(self, nodes, outputs, op_name_counts, dtypes,
                 shapes, output_shapes, target=None, ...):
        self._nodes_by_name = {}        # 节点名 → Node
        self._output_to_node_name = {}  # 输出张量名 → 产出节点名
        self._output_to_consumers = {}  # 输出张量名 → 消费者 Node 列表
        self.shapes = shapes or {}      # 张量名 → 形状列表
        self._dtypes = dtypes or {}     # 张量名 → ONNX dtype
        self.contained_graphs = {}      # 子图字典（If/Loop/Scan 的 body）
```

**三大索引的作用**：

1. `_nodes_by_name`：通过节点名 O(1) 查找 Node 对象
2. `_output_to_node_name`：通过张量名找到产出它的节点（反向追踪）
3. `_output_to_consumers`：通过张量名找到所有消费它的节点（正向传播），用于高效替换输入

### F-024：Graph 构造时的 Identity 保护与 Placeholder 创建

**信源**：`tf2onnx/graph.py`

Graph 构造时执行两个重要操作：

1. **输出 Identity 保护**：为每个图输出添加 Identity 节点，防止转换过程中输出节点被重写导致名称变化。原始输出节点可能被重写器替换或消除，Identity 确保输出名称稳定。

2. **Placeholder 创建**：当输入名称与现有节点冲突时，创建 Placeholder 节点，确保输入节点的唯一性。

### F-025：make_model——构建最终 ONNX ModelProto

**信源**：`tf2onnx/graph.py`

```python
def make_model(self, doc_string="", graph_name="tf2onnx",
               producer_name="tf2onnx", **kwargs):
```

make_model 执行以下步骤：

1. 调用 `make_graph()` 生成 `GraphProto`（序列化所有节点、输入、输出）
2. 设置 `producer_name` 和 `producer_version`
3. 添加 `opset_imports`（ONNX 主 domain、AI_ONNX_ML_OPSET、extra_opset）
4. 根据 opset 版本设置 IR 版本
5. （可选）调用 ONNX optimizer 优化
6. 返回完整的 `ModelProto`

### F-026：ExternalTensorStorage——大模型外部张量存储

**信源**：`tf2onnx/graph.py`

```python
class ExternalTensorStorage(object):
    def __init__(self):
        self._data = {}  # 张量名 → raw_data
        self._threshold = 1024  # 元素数阈值
```

- 超过 1024 元素的常量张量，`raw_data` 被提取到外部存储
- 原张量设置 `data_location = EXTERNAL`
- 通过 `external_data` 字段引用外部文件名
- 解决大模型 protobuf 超过 2GB 的限制

### F-030：OpTypePattern——树形模式匹配器

**信源**：`tf2onnx/graph_matcher.py`

`OpTypePattern` 实现树形模式匹配，支持子图结构识别：

```python
class OpTypePattern(object):
    def __init__(self, op_type, name=None, inputs=None,
                 allow_reorder=False, shape=None, type=None):
```

**模式语法**：

| 语法 | 含义 | 示例 |
|------|------|------|
| 单个 op 类型 | 精确匹配 | `OpTypePattern("Relu")` |
| `'*'` 通配符 | 匹配任意算子 | `OpTypePattern("*")` |
| `'\|'` 分隔 | 匹配多类型之一 | `OpTypePattern("Relu|Relu6")` |
| `inputs` 嵌套 | 指定子模式 | `OpTypePattern("Conv", inputs=[OpTypePattern("*")])` |
| `allow_reorder=True` | 允许输入顺序重排 | 用于可交换算子 |

匹配结果通过 `MatchResult` 返回，包含匹配到的所有节点及其在模式中的角色。

### F-027：预处理重写器列表

**信源**：`tf2onnx/tfonnx.py`

预处理重写器（pre-rewriters）在算子映射之前按顺序运行，共 20+ 个：

| 类别 | 重写器 | 功能 |
|------|--------|------|
| 常量折叠 | `rewrite_constant_fold` | numpy 层面常量折叠 |
| 量化 | `rewrite_quantize_and_dequantize` | QDQ 模式处理 |
| 融合算子 | `rewrite_fused_ops` | TF 融合算子拆分 |
| 布局 | `rewrite_transpose` | 转置优化 |
| 形状 | `rewrite_flatten` | Flatten 转换 |
| 随机 | `rewrite_random_uniform/normal` | 随机数生成 |
| 正则化 | `rewrite_dropout` | Dropout 处理 |
| 卷积 | `rewrite_conv_dilations` | 膨胀卷积 |
| | `rewrite_conv2d_with_pad` | Conv+Pad 融合 |
| | `rewrite_biasadd_with_conv2d` | Conv+BiasAdd 融合 |
| 激活 | `rewrite_leakyrelu` | LeakyReLU |
| | `rewrite_thresholded_relu` | ThresholdedReLU |
| RNN | LSTM/GRU 重写器 | LSTM/GRU 子图识别 |
| 归一化 | `rewrite_layer_normalization` | LayerNorm |
| 矩阵 | `rewrite_gemm` | GEMM 模式识别 |
| 不规则张量 | `rewrite_ragged_variant_shape` | RaggedTensor 处理 |
| 其他 | `rewrite_eye` | Eye 矩阵生成 |

### F-028：run_rewriters——重写器执行框架

**信源**：`tf2onnx/tfonnx.py`

```python
def run_rewriters(g, ops, rewriters, name="rewriter"):
```

重写器执行机制：

1. **顺序执行**：按列表顺序逐个执行重写器
2. **统一签名**：每个重写器接收 `(g, ops)` 参数，返回新的 `ops` 列表
3. **子图递归**：对主图和所有 `contained_graphs`（子图）递归应用重写器
4. **完整性检查**：debug 模式下检查图的完整性（输入输出连接一致性）
5. **迭代稳定**：重写器可能改变图结构，框架确保所有节点被正确处理

### F-029：后处理重写器——Target 条件激活

**信源**：`tf2onnx/tfonnx.py`

后处理重写器（late_rewriters）根据 `target` 平台条件性应用：

| Target | 重写器 | 功能 |
|--------|--------|------|
| `rs5` | `rewrite_incomplete_type_support_rs5` | Windows ML RS5 类型兼容 |
| `rs6` | `rewrite_incomplete_type_support_rs6` | Windows ML RS6 类型兼容 |
| `nhwc` (channels_last) | `rewrite_channels_last` | Channels Last 布局适配 |

## 代码引用

```python
# graph.py - Graph 类核心索引（简化）
class Graph(object):
    def __init__(self, nodes, outputs, ...):
        # 构建三大索引
        for node in nodes:
            self._nodes_by_name[node.name] = node
            for out in node.output:
                self._output_to_node_name[out] = node.name
                self._output_to_consumers[out] = []
        # 第二次遍历：建立消费者索引
        for node in nodes:
            for inp in node.input:
                if inp in self._output_to_consumers:
                    self._output_to_consumers[inp].append(node)

    def make_node(self, op_type, inputs, attr=None, ...):
        """创建新节点并添加到图中"""
        node = helper.make_node(op_type, inputs=inputs, ...)
        return Node(node, graph=self)

    def set_dtype(self, tensor_name, dtype):
        """设置张量数据类型"""
        self._dtypes[tensor_name] = dtype

    def get_dtype(self, tensor_name):
        """获取张量数据类型"""
        return self._dtypes.get(tensor_name)

    def set_shape(self, tensor_name, shape):
        """设置张量形状"""
        self.shapes[tensor_name] = shape

    def get_shape(self, tensor_name):
        """获取张量形状"""
        return self.shapes.get(tensor_name)
```

```python
# graph_matcher.py - 模式匹配示例
# 匹配 Conv -> BiasAdd -> Relu 模式
conv_pattern = OpTypePattern("Conv", name="conv")
bias_pattern = OpTypePattern("BiasAdd", name="bias",
                              inputs=[conv_pattern, OpTypePattern("Const")])
relu_pattern = OpTypePattern("Relu", name="relu",
                              inputs=[bias_pattern])

# 匹配结果：MatchResult 对象包含 conv/bias/relu 三个节点
```
