---
type: reference
title: "转换入口 API：from_keras / from_saved_model / from_function / 命令行"
description: "tf2onnx 提供的模型转换入口 API 信源登记，包括 Python API 五个核心转换函数与命令行接口"
sources:
  - path: "tf2onnx/convert.py"
    facts: [F-006, F-007, F-008, F-009, F-010, F-034, F-039, F-040, F-041]
  - path: "tf2onnx/tf_loader.py"
    facts: [F-035]
  - path: "tf2onnx/constants.py"
    facts: [F-003]
---

# 转换入口 API：from_keras / from_saved_model / from_function / 命令行

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `tf2onnx/convert.py` | Python 模块 | 所有转换入口的实现：Python API 函数、命令行解析、_convert_common 核心流程 |
| `tf2onnx/tf_loader.py` | Python 模块 | 多种 TF 模型格式的加载器，_Lazy 代理模式解决 TF 跨版本导入问题 |
| `tf2onnx/constants.py` | Python 常量 | PREFERRED_OPSET、POSSIBLE_TARGETS 等常量定义 |

## 关键事实登记

### F-006：五个核心 Python 转换函数

**信源**：`tf2onnx/convert.py`

tf2onnx 提供五个 Python API 转换函数，所有函数均返回 `(model_proto, external_tensor_storage)` 元组：

```python
# 函数签名概览
def from_keras(model, name=None, input_signature=None, doc_string="",
               target=None, opset=None, custom_ops=None,
               custom_op_handlers=None, custom_rewriter=None,
               inputs_as_nchw=None, outputs_as_nchw=None,
               extra_opset=None, shape_override=None,
               inputs_dtype=None, large_model=False,
               output_path=None): ...

def from_function(function, name=None, input_signature=None, ...): ...
def from_graph_def(graph_def, name=None, input_names=None,
                   output_names=None, ...): ...
def from_tflite(tflite_path, input_names=None, output_names=None, ...): ...
# from_saved_model 通过 tf_loader 间接提供
```

| 函数 | 输入类型 | 说明 |
|------|----------|------|
| `from_keras` | `tf.keras.Model` | Keras 模型，内部通过 `_get_concrete_function` 获取 concrete function |
| `from_function` | `tf.function` | TF2 函数，必须提供 `input_signature` |
| `from_graph_def` | `GraphDef` proto | 冻结图 protobuf |
| `from_tflite` | `.tflite` 文件路径 | TFLite 模型，走专用转换路径 |
| `from_saved_model` | SavedModel 目录路径 | TF2 SavedModel 格式 |

### F-007：from_keras 的多版本 TF 兼容处理

**信源**：`tf2onnx/convert.py`

from_keras 通过 `_get_concrete_function` 获取 concrete function，处理两种路径：

- **TF < 2.16**：使用 `trace_model_call` 追踪模型调用
- **TF 2.16+**：回退到 `tf.function` 方式获取 concrete function

同时处理 legacy keras 模型（独立 `keras` 包而非 `tf.keras`）的兼容问题。

### F-008：from_function 的 input_signature 要求

**信源**：`tf2onnx/convert.py`

`from_function` 要求 TF 2.0+ 且必须提供 `input_signature` 参数；通过 `function.get_concrete_function()` 获取具体函数，自动过滤掉 `resource` 类型的输入输出（如 HashTable 资源句柄）。

### F-009：_convert_common 内部核心流程

**信源**：`tf2onnx/convert.py`

`_convert_common` 是所有转换入口共用的内部函数，流程为：

```
1. 处理 custom_op_handlers（旧 API 兼容层）
2. 大模型时压缩常量
3. 将冻结图导入到 tf.Graph（/cpu:0 设备）
4. 调用 process_tf_graph 执行图转换
5. optimizer.optimize_graph 优化 ONNX 图
6. make_model 构建最终 ONNX ModelProto
7. （可选）保存到文件
```

### F-010：强制 CPU 执行

**信源**：`tf2onnx/convert.py`

所有转换操作强制在 `/cpu:0` 设备上执行，避免 GPU 相关问题；`from_tflite` 直接传 `None` 给 `frozen_graph` 参数，通过 `tflite_path` 走 TFLite 专用转换路径。

### F-034：tf_loader 的多格式加载函数

**信源**：`tf2onnx/convert.py` / `tf2onnx/tf_loader.py`

`tf_loader` 提供六种模型加载函数：

| 加载函数 | 输入 | 说明 |
|----------|------|------|
| `from_graphdef` | GraphDef 文件 | 加载冻结图 |
| `from_checkpoint` | checkpoint meta 文件 | 从 checkpoint 恢复并冻结 |
| `from_saved_model` | SavedModel 目录 | TF2 SavedModel 加载 |
| `from_keras` | Keras 模型 | Keras 模型加载 |
| `from_function` | tf.function | TF2 concrete function |
| `from_trackable` | TF2 trackable 对象 | TF2 trackable 对象 |

### F-035：_Lazy 代理模式解决 TF 跨版本导入问题

**信源**：`tf2onnx/tf_loader.py`

tf_loader 大量使用 `_Lazy` 代理类延迟 TF 符号查找，解决 Windows `tensorflow-intel` 在模块导入时不暴露 `tf.compat`/`tf.io` 等符号的问题；同时对缺失的 TF 导入提供 `_not_implemented_tf_placeholder` 占位函数，给出明确的错误提示。

```python
class _Lazy:
    """延迟属性查找代理，解决 TF 跨版本导入问题"""
    def __init__(self, name):
        self._name = name
    def __getattr__(self, attr):
        module = importlib.import_module(self._name)
        return getattr(module, attr)
```

### F-039：命令行接口

**信源**：`tf2onnx/convert.py`

命令行入口为 `python -m tf2onnx.convert`，支持 6 种输入格式：

| 参数 | 格式 | 必须指定 inputs/outputs |
|------|------|------------------------|
| `--saved-model` | SavedModel 目录 | 否 |
| `--checkpoint` | checkpoint 路径 | 是（`--inputs`/`--outputs`） |
| `--keras` | Keras 模型文件 | 否 |
| `--tflite` | TFLite 文件 | 否 |
| `--tfjs` | TF.js 模型目录 | 否 |
| `--graphdef` / `--input` | GraphDef 文件 | 是（`--inputs`/`--outputs`） |

输出通过 `--output` 指定 ONNX 文件路径。

### F-040：命令行形状指定与重命名

**信源**：`tf2onnx/convert.py`

- `--inputs` 参数支持内联形状指定：`name:0[dim1,dim2,...]`，通过 `utils.split_nodename_and_shape` 解析，`-1` 表示未知维度
- `--rename-inputs` / `--rename-outputs` 支持重命名输入输出张量

```bash
# 示例：指定输入形状
python -m tf2onnx.convert --saved-model saved_model_dir \
  --output model.onnx \
  --inputs "input:0[1,224,224,3]"
```

### F-041：命令行自定义算子支持

**信源**：`tf2onnx/convert.py`

- `--custom-ops` 参数标记未识别算子，格式为 `OpName:domain`（逗号分隔）
- 未指定 domain 时使用默认域 `"ai.onnx.converters.tensorflow"`
- 自动将 `TENSORFLOW_OPSET` 添加到 `extra_opset`

### F-003：PREFERRED_OPSET 常量

**信源**：`tf2onnx/constants.py`

- 支持 Python 3.10-3.12 和 TensorFlow 2.13+
- `PREFERRED_OPSET = 15`，策略为默认使用 18 个月前发布的最新 opset
- 官方测试支持 opset-14 到 opset-18，opset-6 到 opset-13 理论可用但未测试

## 代码引用

```python
# convert.py - 核心转换流程（简化）
def _convert_common(frozen_graph, name="", ...):
    # 1. 处理自定义算子处理器
    # 2. 大模型常量压缩
    # 3. 导入到 TF 图（强制 /cpu:0）
    with tf.device("/cpu:0"):
        # 导入 frozen graph
        ...
    # 4. TF 图 → ONNX 图转换
    g = process_tf_graph(tf_graph, opset=opset, ...)
    # 5. ONNX 图优化
    g = optimizer.optimize_graph(g)
    # 6. 构建 ModelProto
    model_proto = g.make_model(...)
    return model_proto, external_tensor_storage
```
