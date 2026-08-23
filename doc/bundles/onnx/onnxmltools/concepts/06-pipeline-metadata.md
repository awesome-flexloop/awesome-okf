---
type: concept
title: "Pipeline转换、元数据传播与校验工具"
description: "onnxmltools 中的Pipeline/复合模型转换处理（SparkML Pipeline、CoreML Pipeline）、模型元数据传播机制（doc_string/author/license/version）、输入输出命名合规校验、模型I/O工具"
sources:
  references: [../references/convert-entry.md, ../references/topology-ir.md, ../references/registration-types.md]
  facts: [F-034, F-037, F-038, F-040]
---

# Pipeline转换、元数据传播与校验工具

## 核心理解

onnxmltools 不仅支持单模型转换，还处理复合模型（Pipeline）的转换——这涉及多算子串联、中间变量连接、元数据传递等问题。同时，模型元数据（doc_string、author、license等）的传播确保转换后的ONNX模型保留原始模型的文档信息。

## SparkML Pipeline 转换

SparkML（Apache Spark MLlib）的 Pipeline 概念与 sklearn Pipeline 类似，由多个 Stage 组成（Transformer和Estimator）。onnxmltools 的 SparkML 转换器走自有 Topology IR 路径：

```
SparkML PipelineModel
  ├─ Stage 0: VectorAssembler → 特征组装
  ├─ Stage 1: StandardScaler   → 标准化
  ├─ Stage 2: GBTClassifier    → GBDT分类
  └─ ...
```

转换时每个 Stage 被解析为 IR 中对应的 Operator，Stage 之间通过 Variable 连接：
- 前一个Stage的输出Variable作为后一个Stage的输入
- 作用域管理通过Scope嵌套或Scope间变量引用来处理
- 最终输出是最后一个Stage的输出

SparkML转换器特点：
- `initial_types` 不强制但推荐传入
- 支持Spark MLlib的特征工程算子（VectorAssembler、StringIndexer、OneHotEncoder等）
- Pipeline中的每个Stage有独立的parser

## CoreML Pipeline 与元数据传播（F-034）

CoreML 模型本身支持Pipeline结构（串联多个模型），onnxmltools 的 CoreML 转换器处理Pipeline时递归解析每个子模型。

### 元数据自动提取

CoreML 转换器独有**元数据自动传播**能力——从 CoreML spec 的 `description.metadata` 提取信息附加到输出 ONNX 模型：

```python
# coreml/convert.py 元数据提取逻辑
if spec.description.metadata.shortDescription:
    doc_string = spec.description.metadata.shortDescription

metadata_props = {}
if spec.description.metadata.author:
    metadata_props["author"] = spec.description.metadata.author
if spec.description.metadata.license:
    metadata_props["license"] = spec.description.metadata.license
if spec.description.metadata.versionString:
    metadata_props["version"] = spec.description.metadata.versionString
```

这些元数据被写入 ONNX ModelProto 的 `metadata_props` 字段，在模型加载后可通过 `model.metadata_props` 访问。

## 模型I/O工具（F-037）

`onnxmltools.utils` 提供模型序列化/反序列化工具：

### save_model / load_model

```python
from onnxmltools.utils import save_model, load_model

# 保存模型（Protobuf二进制序列化）
save_model(onnx_model, "model.onnx")
# 内部：校验model为ModelProto实例 → model.SerializeToString() → 写文件

# 加载模型
loaded_model = load_model("model.onnx")
# 内部：读文件 → ModelProto.ParseFromString(data) → 返回ModelProto
```

### 元数据修改工具

```python
from onnxmltools.utils import set_model_domain, set_model_version, set_model_doc_string

set_model_domain(model, "custom.domain")
set_model_version(model, 1)
set_model_doc_string(model, "My awesome model")
```

## 输入输出命名合规校验（F-040）

`convert_topology` 对输入输出名称做ONNX命名合规校验：

```python
import re
def _check_name(name):
    cleaned = re.sub(r"[_:/\\]", "", name)
    if cleaned and (cleaned[0].isdigit() or not cleaned.isalnum()):
        warnings.warn(f"Name '{name}' is not compliant with ONNX naming convention.")
```

规则：
- 替换 `_`、`:`、`/`、`\` 字符
- 检查首字符不能是数字
- 检查所有字符必须是字母数字
- 不合规时发出警告（不报错，不阻止转换）

ONNX命名规范要求：
- 名称只能包含字母、数字、下划线、冒号等特定字符
- 不能以数字开头
- 这是为了兼容不同推理引擎和代码生成器

## 形状计算器校验工具（F-038）

编写自定义形状计算器时，`shape_calculator.py` 提供两个通用校验函数：

### check_input_and_output_numbers

```python
def check_input_and_output_numbers(operator, input_count_range=None, output_count_range=None):
    """校验输入/输出个数
    
    参数：
        input_count_range: 允许的输入个数范围
            - None: 不检查
            - int: 精确个数
            - (min, max): 范围
        output_count_range: 同上
    """
```

示例：

```python
def my_shape_calculator(operator):
    # 校验：1个输入，1到2个输出
    check_input_and_output_numbers(operator, input_count_range=1, output_count_range=(1, 2))
```

### check_input_and_output_types

```python
def check_input_and_output_types(operator, good_input_types=None, good_output_types=None):
    """校验输入/输出类型白名单
    
    参数：
        good_input_types: 允许的输入类型列表（DataType子类）
        good_output_types: 允许的输出类型列表
    """
```

示例：

```python
def my_shape_calculator(operator):
    check_input_and_output_types(operator, 
                                  good_input_types=[FloatTensorType, DoubleTensorType])
    # 设置输出形状
    operator.outputs[0].type = FloatTensorType(operator.inputs[0].type.shape)
```

### calculate_linear_regressor_output_shapes

默认的线性回归形状计算器：
- 输入形状 `[N, C]` → 输出形状 `[N, nout]`
- nout 从 raw_operator 的系数维度推断

## 框架特有后处理

各框架在标准流水线之外有各自的后处理步骤：

| 框架 | 后处理 |
|------|--------|
| LightGBM | zipmap/split/without_onnx_ml（参见[树模型转换范式](05-tree-models.md)） |
| CoreML | metadata提取、2D→4D shape fix |
| H2O | MOJO临时文件清理 |
| Keras/TF | opset版本修正、initial_types→TensorSpec映射 |

## 设计洞察

1. **元数据传播是模型可追溯性的基础**：CoreML的metadata自动提取确保了模型的来源和文档信息在转换后不丢失，这对模型治理很重要。
2. **Pipeline转换本质是算子串联**：无论SparkML还是CoreML Pipeline，转换时都是将每个Stage/子模型解析为IR Operator，通过Variable连接成图——IR的统一表示天然支持复合模型。
3. **校验工具是开发自定义算子的安全网**：`check_input_and_output_numbers`和`check_input_and_output_types`帮助早期发现形状计算器的错误，而不是等到推理时才崩溃。
4. **命名合规是跨引擎兼容性的保障**：不同ONNX推理引擎对命名的严格程度不同，提前警告不合规名称可以避免部署时的问题。

## 关联概念

- [onnxmltools 整体架构](00-overall-architecture.md) — 了解9个入口的架构总览
- [编译流水线五阶段](02-conversion-pipeline.md) — 了解convert_topology中命名校验的位置
- [转换器注册与分发](03-converter-registration.md) — 了解自定义算子开发
- [树模型转换范式](05-tree-models.md) — LightGBM特有后处理
