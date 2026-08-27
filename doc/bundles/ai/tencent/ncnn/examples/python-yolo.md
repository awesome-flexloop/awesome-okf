---
type: Example
title: Python YOLO 目标检测
description: 使用 ncnn Python 绑定和 model_zoo 加载 YOLOv8 预训练模型，对图像进行目标检测，含 numpy 零拷贝输入和检测结果解析。
tags: [ncnn, python, yolo, detection, model-zoo]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: model-zoo
    resource: /python/ncnn/model_zoo/model_zoo.py
    title: model_zoo.py
---

# Python YOLO 目标检测

本例使用 ncnn 的 `model_zoo` 加载 YOLOv8s 预训练模型进行目标检测，展示 Python 绑定的 numpy 零拷贝互操作。

## 完整代码

```python
import cv2
import numpy as np
import ncnn
from ncnn.model_zoo import get_model

# 1. 加载预训练模型（首次运行自动下载权重）
net = get_model(
    "yolov8s",
    num_threads=4,
    use_gpu=True,           # 启用 Vulkan GPU
)

# 2. 读取图像
image = cv2.imread("street.jpg")
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 3. 推理（model_zoo 封装了预处理/推理/后处理）
detections = net(image_rgb)

# 4. 绘制结果
for det in detections:
    x1, y1, x2, y2 = det.rect
    label = det.label
    prob = det.prob
    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)),
                  (0, 255, 0), 2)
    cv2.putText(image, f"{label}: {prob:.2f}",
                (int(x1), int(y1) - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

cv2.imwrite("result.jpg", image)
print(f"检测到 {len(detections)} 个目标")
```

## 直接使用 Net/Extractor（不使用 model_zoo）

```python
import ncnn
import numpy as np

# 1. 创建 Net 并加载
net = ncnn.Net()
net.opt.use_vulkan_compute = True
net.load_param("yolov8s.param")
net.load_model("yolov8s.bin")

# 2. 预处理为 numpy 数组（HWC uint8 -> CHW float32）
img = cv2.imread("street.jpg")
img = cv2.resize(img, (640, 640))
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
img = img.transpose(2, 0, 1)  # HWC -> CHW

# 3. numpy 零拷贝构造 Mat
mat_in = ncnn.Mat(img)
mat_in.substract_mean_normalize(
    mean_vals=[0.0, 0.0, 0.0],
    norm_vals=[1.0, 1.0, 1.0])

# 4. 推理
ex = net.create_extractor()
ex.input("in0", mat_in)
ret, mat_out = ex.extract("out0")

# 5. Mat 转 numpy（零拷贝）
out = np.array(mat_out)
print(f"输出形状: {out.shape}")
```

## 零拷贝原理

Python 绑定通过 pybind11 的 buffer protocol 暴露 Mat：

- `ncnn.Mat(numpy_array)`：numpy 数组的内存直接被 Mat 引用，不拷贝（要求 `elempack=1`、`elemsize=1/2/4`）；
- `np.array(mat)`：从 Mat 构造 numpy 数组同样共享内存；
- strides 使用 `cstep * elemsize` 而非紧凑布局，反映 ncnn 的 16 字节通道对齐。

## model_zoo 可用模型

```python
from ncnn.model_zoo import get_model_list
print(get_model_list())
# ['faster_rcnn', 'mobilenet_ssd', 'mobilenet_yolov2',
#  'mobilenetv2_ssdlite', 'mobilenetv2_yolov3', 'mobilenetv3_ssdlite',
#  'nanodet', 'peleenet_ssd', 'retinaface', 'rfcn', 'shufflenetv2',
#  'simplepose', 'squeezenet', 'squeezenet_ssd', 'yolact',
#  'yolov2', 'yolov4', 'yolov4_tiny', 'yolov5s', 'yolov7_tiny', 'yolov8s']
```

每个模型封装类自动处理：
- 权重下载与缓存（`utils/download.py`）；
- 图像 resize、归一化、通道转换；
- NMS 后处理（`utils/functional.py`）；
- 返回 `objects.Object` 列表（含 label/prob/rect/关键点）。

## 相关概念

- [10 Python 绑定](../concepts/10-python-binding.md)
- [01 Net 与 Extractor 推理流程](../concepts/01-net-extractor.md)
- [02 Mat 张量系统](../concepts/02-mat-tensor-system.md)
- [06 Vulkan GPU 后端](../concepts/06-vulkan-gpu.md)
