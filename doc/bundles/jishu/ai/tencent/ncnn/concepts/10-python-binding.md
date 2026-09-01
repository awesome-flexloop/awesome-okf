---
type: Concept
title: Python 绑定
description: ncnn Python 绑定基于 pybind11，pybind11_mat.h 实现 Mat 与 numpy 零拷贝互操作（buffer protocol），pybind11_net.h 绑定 Net/Extractor，pybind11_layer.h 支持 Python 自定义层，model_zoo 提供 20 个预训练模型。
tags: [ncnn, python, pybind11, numpy, model-zoo]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: pybind-mat
    resource: /python/src/pybind11_mat.h
    title: pybind11_mat.h
  - id: model-zoo
    resource: /python/ncnn/model_zoo/model_zoo.py
    title: model_zoo.py
---

# Python 绑定

ncnn 的 Python 绑定基于 pybind11，源码在 `python/src/`，通过 `NCNN_PYTHON=ON` 构建。绑定目标是让 Python 用户能以 numpy 数组直接推理，同时支持从 Python 继承实现自定义层。

## 绑定文件结构

```
python/src/
├── main.cpp             # 模块入口，注册所有类
├── pybind11_bind.h      # Net/Extractor/Option 等核心绑定
├── pybind11_mat.h       # Mat ↔ numpy 零拷贝互操作
└── pybind11_layer.h     # Layer 基类绑定与 Python 自定义层
```

## Mat 与 numpy 零拷贝

`pybind11_mat.h` 的 `to_buffer_info` 函数将 Mat 暴露为 Python buffer protocol 对象，numpy 可直接零拷贝访问（F-106）：

```cpp
py::buffer_info to_buffer_info(ncnn::Mat& m, const std::string& format = "") {
    // 仅支持 elemsize 1/2/4
    if (m.elemsize != 1 && m.elemsize != 2 && m.elemsize != 4)
        py::pybind11_fail("...");
    // elempack 必须为 1
    if (m.elempack != 1)
        py::pybind11_fail("...");

    // elemsize 4 -> float32, 2 -> float16(e), 1 -> int8
    // shape: dims=1 [w], dims=2 [h,w], dims=3 [c,h,w]
    // strides 使用 cstep*elemsize 保证通道间对齐
}
```

关键点：
- `elemsize=4` 映射 numpy `float32`，`elemsize=2` 映射 `float16`（格式符 `e`），`elemsize=1` 映射 `int8`；
- `elempack` 必须为 1（打包张量需先解包才能转 numpy）；
- strides 使用 `cstep * elemsize` 而非紧凑 `w*h*elemsize`，因为 Mat 通道间有 16 字节对齐填充；
- numpy 数组与 Mat 共享内存，修改 numpy 数据直接反映到 Mat，无需拷贝。

## Net / Extractor 绑定

`pybind11_bind.h` 将 C++ API 映射为 Python 风格：

```python
import ncnn

net = ncnn.Net()
net.opt.use_vulkan_compute = True
net.load_param("model.param")
net.load_model("model.bin")

ex = net.create_extractor()
ex.input("data", ncnn.Mat(in))  # numpy 数组自动构造 Mat
ret, out = ex.extract("output")  # 返回 (ret_code, Mat)
```

`Option` 的字段作为 Python 属性直接赋值。Extractor 的 `input/extract` 接受 numpy 数组并返回 Mat（自动转换）。

## Python 自定义层

`pybind11_layer.h` 通过 pybind11 的 trampoline 类支持从 Python 继承 Layer：

```python
class MyLayer(ncnn.Layer):
    def __init__(self):
        super().__init__()
        self.one_blob_only = True

    def load_param(self, pd):
        self.my_param = pd.get(0, 0)
        return 0

    def forward(self, bottom, opt):
        top = bottom.clone()
        # 自定义计算
        return 0, top
```

Python 层通过 `net.register_custom_layer("MyLayer", MyLayer)` 注册，C++ 推理时回调 Python 方法。

## model_zoo 预训练模型

`python/ncnn/model_zoo/` 内置 20 个预训练模型封装（F-107），自动下载权重并构造 Net：

| 类别 | 模型 |
|---|---|
| YOLO 检测 | mobilenet_yolov2、mobilenetv2_yolov3、yolov4_tiny、yolov4、yolov5s、yolov7_tiny、yolov8s |
| 实例分割 | yolact |
| SSD 检测 | mobilenet_ssd、squeezenet_ssd、mobilenetv2_ssdlite、mobilenetv3_ssdlite、peleenet_ssd |
| 分类 | squeezenet、shufflenetv2 |
| 两阶段检测 | faster_rcnn、rfcn |
| 人脸检测 | retinaface |
| 姿态估计 | simplepose |
| 轻量检测 | nanodet |

```python
from ncnn.model_zoo import get_model

net = get_model("yolov8s", num_threads=4, use_gpu=True)
detections = net(image)  # 直接传 numpy 图像
```

`utils/` 提供 `download.py`（模型下载缓存）、`functional.py`（NMS、resize 等预处理）、`objects.py`（检测框/关键点数据结构）、`visual.py`（可视化绘制）。

## Python 示例

`python/examples/` 含 13 个完整示例：squeezenet 分类、yolov2-v8 检测、fasterrcnn/rfcn、retinaface 人脸、simplepose 姿态、nanodet、yolact 分割等。

## 相关概念

- [02 Mat 张量系统](02-mat-tensor-system.md)
- [01 Net 与 Extractor 推理流程](01-net-extractor.md)
- [09 层注册表与自定义层](09-layer-registry.md)
- [Python YOLO 检测示例](../examples/python-yolo.md)
