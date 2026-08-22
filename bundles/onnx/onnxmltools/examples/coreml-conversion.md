---
type: example
title: "CoreML模型转换：从CoreML spec到ONNX"
description: "CoreML模型转ONNX完整流程：加载CoreML模型→convert_coreml转换→metadata自动提取→神经网络与传统ML算子转换→onnxruntime推理验证"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/02-conversion-pipeline.md, ../concepts/05-tree-models.md, ../concepts/06-pipeline-metadata.md]
  references: [../references/convert-entry.md, ../references/topology-ir.md]
---

# CoreML模型转换：从CoreML spec到ONNX

## 目标

将 CoreML 模型（.mlmodel 格式）转换为 ONNX 格式，了解 CoreML 转换器对传统 ML 算子和神经网络算子的支持，验证元数据传播和推理正确性。

## 前置条件

```bash
pip install coremltools onnxmltools onnxruntime numpy
```

注意：CoreML 转换器在 Linux/Windows 上需要 coremltools（苹果官方支持 macOS，但 Linux 上的 coremltools 也支持基本的 spec 操作）。

## 示例1：CoreML 广义线性模型（GLM）转换

CoreML 的 GLMClassifier/GLMRegressor 映射到 ONNX-ML 的 LinearClassifier/LinearRegressor。

```python
import numpy as np
import coremltools as ct
from onnxmltools.convert import convert_coreml
from onnxmltools.utils import save_model
import onnxruntime as ort

# 1. 加载或构造CoreML模型
# 这里使用coremltools创建一个简单的GLM分类器
# （实际使用中通常是加载已有的.mlmodel文件）
# model = ct.models.MLModel("my_model.mlmodel")

# 或者直接操作proto spec
from coremltools.proto import Model_pb2

spec = Model_pb2.Model()
spec.specificationVersion = 4

# 设置GLMClassifier
glm = spec.glmClassifier
glm.weights.append(1.0)
glm.weights.append(-0.5)
glm.weights.append(0.3)
glm.offset.append(0.0)
glm.postEvaluationTransform = Model_pb2.GLMClassifier.Logit

# 设置输入输出描述
input_desc = spec.description.input.add()
input_desc.name = "input"
input_desc.type.multiArrayType.shape.extend([1, 3])
input_desc.type.multiArrayType.dataType = Model_pb2.ArrayFeatureType.DOUBLE

output_label = spec.description.output.add()
output_label.name = "classLabel"
output_label.type.stringType.MergeFromString(b"")

output_prob = spec.description.output.add()
output_prob.name = "classProbability"
output_prob.type.dictionaryType.stringKeyType.MergeFromString(b"")

# 设置元数据
spec.description.metadata.shortDescription = "Test GLM Classifier"
spec.description.metadata.author = "Test Author"
spec.description.metadata.license = "MIT"

# 2. 转换为ONNX
onnx_model = convert_coreml(spec, target_opset=15)

# 3. 检查元数据是否传播
print("doc_string:", onnx_model.doc_string)
print("metadata_props:", [(p.key, p.value) for p in onnx_model.metadata_props])
# 预期输出：
# doc_string: "Test GLM Classifier"
# metadata_props: [('author', 'Test Author'), ('license', 'MIT')]
```

## 示例2：CoreML TreeEnsemble 转换

CoreML TreeEnsemble 映射到 ONNX-ML TreeEnsembleClassifier/Regressor，是 CoreML 转换器最常用的场景之一。

```python
import numpy as np
from onnxmltools.convert import convert_coreml
from onnxconverter_common.data_types import FloatTensorType
import coremltools.proto as pb
import onnxruntime as ort

# 构造CoreML TreeEnsembleClassifier
spec = pb.Model_pb2.Model()
spec.specificationVersion = 4

# 创建简单的决策树
tree = spec.treeEnsembleClassifier
tree.treeEnsemble.nodes.add()
tree.treeEnsemble.nodes[0].treeId = 0
tree.treeEnsemble.nodes[0].nodeId = 0
tree.treeEnsemble.nodes[0].branchFeatureIndex = 0
tree.treeEnsemble.nodes[0].branchFeatureValue = 0.5
tree.treeEnsemble.nodes[0].trueChildNodeId = 1
tree.treeEnsemble.nodes[0].falseChildNodeId = 2
tree.treeEnsemble.nodes[0].nodeBehavior = pb.TreeEnsembleParameters.BranchOnValueLessThanEqual

# 左叶子（类别0概率1.0）
tree.treeEnsemble.nodes.add()
tree.treeEnsemble.nodes[1].treeId = 0
tree.treeEnsemble.nodes[1].nodeId = 1
tree.treeEnsemble.nodes[1].evaluationInfo.append("*")
tree.treeEnsemble.nodes[1].nodeBehavior = pb.TreeEnsembleParameters.LeafNode

# 右叶子（类别1概率1.0）
tree.treeEnsemble.nodes.add()
tree.treeEnsemble.nodes[2].treeId = 0
tree.treeEnsemble.nodes[2].nodeId = 2
tree.treeEnsemble.nodes[2].nodeBehavior = pb.TreeEnsembleParameters.LeafNode

# 设置输入输出
inp = spec.description.input.add()
inp.name = "input"
inp.type.multiArrayType.shape.extend([1, 1])
inp.type.multiArrayType.dataType = pb.ArrayFeatureType.DOUBLE

out_label = spec.description.output.add()
out_label.name = "classLabel"
out_label.type.int64Type.MergeFromString(b"")

out_prob = spec.description.output.add()
out_prob.name = "classProbability"
out_prob.type.dictionaryType.int64KeyType.MergeFromString(b"")

# 转换
onnx_model = convert_coreml(spec, target_opset=15)

# 验证结构
print("ONNX节点数:", len(onnx_model.graph.node))
print("输入:", [i.name for i in onnx_model.graph.input])
print("输出:", [o.name for o in onnx_model.graph.output])
```

## 示例3：从.mlmodel文件加载并转换

实际使用中最常见的场景是加载已训练的.mlmodel文件：

```python
import numpy as np
import coremltools as ct
from onnxmltools.convert import convert_coreml
from onnxmltools.utils import save_model, load_model
import onnxruntime as ort

# 1. 加载CoreML模型
coreml_model = ct.models.MLModel("MyTrainedModel.mlmodel")
spec = coreml_model.get_spec()

# 2. 检查模型类型
print("模型类型:", spec.WhichOneof('Type'))
# 可能输出: treeEnsembleClassifier, glmClassifier, neuralNetworkClassifier, pipelineClassifier等

# 3. 转换为ONNX
# CoreML不需要initial_types（从spec的输入描述自动推断），但推荐传入
onnx_model = convert_coreml(
    spec,
    target_opset=15,
    name="MyCoreMLModel",
    doc_string="Converted from CoreML",
)

# 4. 保存
save_model(onnx_model, "model_from_coreml.onnx")

# 5. 推理验证
sess = ort.InferenceSession("model_from_coreml.onnx")
input_name = sess.get_inputs()[0].name
input_shape = [d.dim_value or 1 for d in sess.get_inputs()[0].type.tensor_type.shape.dim]
print(f"输入名称: {input_name}, 预期shape: {input_shape}")

# 构造测试输入
test_input = np.random.randn(1, *input_shape[1:]).astype(np.float32)
outputs = sess.run(None, {input_name: test_input})
for i, output in enumerate(sess.get_outputs()):
    print(f"输出 {output.name}: shape={outputs[i].shape}")
```

## CoreML支持的算子一览

### 传统ML算子（15个顶层注册）

| CoreML算子 | ONNX-ML映射 | 说明 |
|-----------|-------------|------|
| ArrayFeatureExtractor | ArrayFeatureExtractor | 数组特征提取 |
| DictVectorizer | DictVectorizer | 字典向量化 |
| FeatureVectorizer | FeatureVectorizer | 特征拼接 |
| GLMClassifier | LinearClassifier | 广义线性分类器 |
| GLMRegressor | LinearRegressor | 广义线性回归器 |
| Identity | Identity | 恒等映射 |
| Imputer | Imputer | 缺失值填充 |
| Normalizer | Normalizer | 归一化 |
| OneHotEncoder | OneHotEncoder | 独热编码 |
| Scaler | Scaler | 标准化/缩放 |
| SVC | SVMClassifier | 支持向量分类 |
| SVR | SVMRegressor | 支持向量回归 |
| TensorToLabel | ArgMax | 张量转标签 |
| TensorToProbabilityMap | ZipMap | 张量转概率字典 |
| TreeEnsemble | TreeEnsembleClassifier/Regressor | 树模型 |

### 神经网络算子（40+个，neural_network/子包）

包括：Convolution、Pooling、InnerProduct、LSTM、GRU、BatchNormalization、ReLU、Sigmoid、Softmax、Concat、Reshape、Transpose、Embed、Flatten、ReduceL2、UnaryFunction、LoadConstant、ReshapeStatic、Bias、Scale、Crop、Padding、Upsample、UnaryExp、UnaryLog、UnaryTanh、UnaryAbs、UnarySqrt、UnaryReciprocal、UnaryPower、UnaryThreshold、UnaryNegation、Split、ConcatSequence、SequenceRepeat、GetSequence、L2Normalize、Permute、DotProduct、CosineDistance、CropResize、FlattenTo2D、Slice、BroadcastToLike、MatMul、Gemm、AddMode、MultiplyMode、ConcatMode、DotProductMode、ReduceMode、Reciprocal、ClipReLU、HardSigmoid、ELU、PReLU、ThresholdedReLU、Softplus、Softsign、LeakyReLU等。

## 要点解析

### CoreML转换器的独特之处

1. **不需要initial_types**：CoreML spec的 `description.input` 已经声明了输入名称和类型，转换器可以自动推断。但推荐传入以获得更好的控制。

2. **metadata自动传播**：`spec.description.metadata` 中的 `shortDescription`、`author`、`license` 等字段自动提取到ONNX模型的 `doc_string` 和 `metadata_props`。

3. **2D→4D shape fix**：compile阶段的 `_fix_shapes()` 会自动将2D图像输入补全为4D（NCHW格式），处理CoreML中常见的2D图像表示。

4. **神经网络支持最全面**：CoreML neural_network子包注册了40+神经网络层算子，是onnxmltools中神经网络转换能力最强的前端。

### 与委托路径的区别

CoreML转换器走自有Topology IR路径（与LightGBM/XGBoost相同），而Keras/TF/sklearn/CatBoost走委托路径。CoreML是onnxmltools自主维护最完整的转换器。

### 常见问题

**Q：CoreML NeuralNetwork和Keras转换有什么区别？**
A：CoreML NeuralNetwork走onnxmltools自有IR（CoreML→Topology→ONNX），Keras在TF≥2.0时委托给tf2onnx。两者转换路径完全不同。

**Q：所有CoreML模型都支持吗？**
A：传统ML算子（GLM/Tree/SVM/Scaler等）和神经网络层（Conv/LSTM/BN等）支持较好；CoreML的CustomModel、MLProgram（iOS15+）等较新特性可能支持不完整。

## 延伸阅读

- CoreML元数据和Pipeline处理：[Pipeline转换、元数据传播与校验工具](../concepts/06-pipeline-metadata.md)
- 树模型转换范式：[树模型转换范式](../concepts/05-tree-models.md)
- 整体架构理解：[onnxmltools 整体架构](../concepts/00-overall-architecture.md)
