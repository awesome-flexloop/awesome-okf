# 示例

* [C++ 完整推理示例](first-inference.md) — Option 配置、Net 加载模型、from_pixels_resize 预处理、substract_mean_normalize、Extractor input/extract、PoolAllocator 内存池。
* [Python YOLO 目标检测](python-yolo.md) — model_zoo 加载 YOLOv8s、numpy 零拷贝输入、检测结果解析、直接使用 Net/Extractor。
* [自定义 Layer 注册与实现](custom-layer.md) — 继承 Layer、设置能力标志位、load_param/forward/forward_inplace、DEFINE_LAYER_CREATOR、C++ 与 Python 双版本。
* [启用 Vulkan GPU 推理](vulkan-inference.md) — create_gpu_instance、use_vulkan_compute、VkMat 全 GPU 路径、PipelineCache 持久化、CPU/GPU 混合执行。

```{toctree}
:maxdepth: 7

custom-layer
first-inference
python-yolo
vulkan-inference
```
