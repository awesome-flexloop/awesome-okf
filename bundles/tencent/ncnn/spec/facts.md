---
type: spec-facts
title: ncnn 源码事实采集
description: ncnn 高性能神经网络推理框架核心头文件逐文件阅读提取的 100 条编号事实，覆盖 Net/Mat/Layer/Allocator/Option/Vulkan/Python/CMake 全部模块。
tags: [ncnn, facts, source-reading]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: net-h
    resource: /src/net.h
    title: net.h — Net 与 Extractor
  - id: mat-h
    resource: /src/mat.h
    title: mat.h — Mat/VkMat/VkImageMat
  - id: layer-h
    resource: /src/layer.h
    title: layer.h — Layer 基类
  - id: blob-h
    resource: /src/blob.h
    title: blob.h — Blob
  - id: option-h
    resource: /src/option.h
    title: option.h — Option
  - id: allocator-h
    resource: /src/allocator.h
    title: allocator.h — Allocator 与 VkAllocator
  - id: paramdict-h
    resource: /src/paramdict.h
    title: paramdict.h — ParamDict
  - id: modelbin-h
    resource: /src/modelbin.h
    title: modelbin.h — ModelBin
  - id: gpu-h
    resource: /src/gpu.h
    title: gpu.h — VulkanDevice/GpuInfo
  - id: pipeline-h
    resource: /src/pipeline.h
    title: pipeline.h — Pipeline
  - id: command-h
    resource: /src/command.h
    title: command.h — VkCompute/VkTransfer
  - id: pipelinecache-h
    resource: /src/pipelinecache.h
    title: pipelinecache.h — PipelineCache
  - id: c-api-h
    resource: /src/c_api.h
    title: c_api.h — C 语言 API
  - id: cmake
    resource: /CMakeLists.txt
    title: CMakeLists.txt — 构建系统
  - id: cpu-h
    resource: /src/cpu.h
    title: cpu.h — CPU 特性检测
  - id: ruapu-h
    resource: /src/ruapu.h
    title: ruapu.h — 单文件 ISA 检测
  - id: datareader-h
    resource: /src/datareader.h
    title: datareader.h — DataReader
  - id: layer-type-h
    resource: /src/layer_type.h
    title: layer_type.h — 层类型枚举
---

# ncnn 源码事实采集

> 信源根目录：`external/libs/ai/Tencent/ncnn/`。版本 1.0.20260526（MAJOR=1, MINOR=0, PATCH=构建日期），BSD-3-Clause，腾讯优图实验室。

## 一、Net 与 Extractor（net.h）

- F-001：`Net` 类使用 PIMPL 模式，私有成员 `NetPrivate* const d` 隐藏全部实现（net.h:163）。
- F-002：`Extractor` 类同样使用 PIMPL，私有成员 `ExtractorPrivate* const d`（net.h:255）。
- F-003：`Net::opt` 是 `Option` 类型的公开成员，可在模型加载前修改（net.h:37）。
- F-004：`Net::register_custom_layer` 提供两种重载：按类型名 `const char* type` 和按类型索引 `int index`（net.h:52,57）。
- F-005：`register_custom_layer` 参数为 `layer_creator_func creator, layer_destroyer_func destroyer=0, void* userdata=0`（net.h:52）。
- F-006：Net 加载 API 包含 `load_param`（文本，支持 FILE*/路径/wchar_t*/内存/AAsset/AAssetManager）、`load_param_bin`（二进制）、`load_model`（权重）（net.h:60-125）。
- F-007：内存加载 `load_param(const unsigned char* mem)` 返回 `size_t`（消费字节数），要求指针 32 位对齐（net.h:99-101）。
- F-008：内存权重 `load_model(const unsigned char* mem)` 采用引用而非拷贝，外部内存在使用期间必须保持存活，要求 32 位对齐（net.h:103-108）。
- F-009：`create_extractor() const` 从网络构造一个 `Extractor`（net.h:131）。
- F-010：`Extractor::set_light_mode(bool enable)` 控制中间 blob 回收，默认启用（net.h:184）。
- F-011：`Extractor` 可设置 `blob_allocator`、`workspace_allocator`、`kvcache_allocator`（net.h:187-196）。
- F-012：Vulkan 编译下 `Extractor` 额外可设置 `blob_vkallocator`、`workspace_vkallocator`、`staging_vkallocator`、`kvcache_vkallocator`（net.h:199-206）。
- F-013：`Extractor::input/extract` 同时支持按 blob 名称（`const char*`）和 blob 索引（`int`）（net.h:211-228）。
- F-014：`extract` 的 `type` 参数：0=默认，1=不转换 fp16/bf16/packing（用于 KV cache）（net.h:217,228）。
- F-015：Vulkan 下 `input/extract` 支持 `VkMat` 输入输出并接受 `VkCompute& cmd`（net.h:234-247）。
- F-016：Net 提供 `input_indexes()/output_indexes()/blobs()/layers()` 及对应 mutable 版本（net.h:134-145）。
- F-017：`Net` 的拷贝构造和赋值运算符声明为 private 且未实现，禁止拷贝（net.h:159-160）。
- F-018：`Net::clear()` 卸载网络结构和权重数据（net.h:128）。
- F-019：Vulkan 下 `Net::set_vulkan_device` 支持按设备索引和 `VulkanDevice*` 两种方式（net.h:41-44）。

## 二、Mat 张量系统（mat.h）

- F-020：`Mat` 公共字段：`void* data`、`int* refcount`、`size_t elemsize`、`int elempack`、`Allocator* allocator`、`int dims`、`int w/h/d/c`、`size_t cstep`（mat.h:343-373）。
- F-021：`elemsize` 语义：4=float32/int32，2=float16/bfloat16，1=int8/uint8，0=empty（mat.h:349-354）。
- F-022：`elempack` 注释：1=scalar，4=sse/neon，8=avx/fp16（mat.h:357-359）。
- F-023：`NCNN_BATCH` 编译时 `Mat` 额外含 `int n`（batch count，默认1）和 `size_t nstep`；非 batch 时 `n` 为静态常量 1（mat.h:375-383）。
- F-024：`Mat` 构造函数覆盖 dims 1-4（vec/image/dim/cube），每个维度均有普通、packed（带 elempack）、packed+batch、external（外部数据）变体（mat.h:56-104）。
- F-025：external 构造函数接受 `void* data`，构造时 `refcount=NULL` 表示不管理用户内存（mat.h:82-104）。
- F-026：`Mat` 拷贝构造执行浅拷贝，复制所有字段后调用 `addref()`（mat.h:1036-1045）。
- F-027：external 构造时 `cstep = alignSize((size_t)w*h*elemsize, 16) / elemsize`（mat.h:1055,1069）。
- F-028：`Mat::clone(Allocator*)` 深拷贝；`reshape(w/h/d/c)` 变形；`create(...)` 重新分配；`create_like(m)` 按同形状分配（mat.h:153-201）。
- F-029：视图方法：`channel(c)`、`depth(z)`、`row(y)`、`channel_range`、`depth_range`、`row_range`、`range(x,n)`、`batch(b)`、`batch_range`，均返回共享数据的新 Mat（mat.h:217-242）。
- F-030：`from_pixels/to_pixels` 静态方法支持 RGB/BGR/GRAY/RGBA/BGRA 及 resize/roi/stride 变体，`PixelType` 枚举用移位编码格式转换（mat.h:255-316）。
- F-031：`substract_mean_normalize(const float* mean_vals, const float* norm_vals)` 执行通道级减均值乘归一化，传 0 跳过（mat.h:335）。
- F-032：`Mat::addref()`/`release()` 管理引用计数，`refcount` 为 NULL 时无操作。
- F-033：`VkMat` 字段：`VkBufferMemory* data`、`int* refcount`、`elemsize/elempack`、`VkAllocator* allocator`、`dims/w/h/d/c/cstep`，batch 时含 `n/nstep/offset`（mat.h:513-556）。
- F-034：`VkImageMat` 字段：`VkImageMemory* data`、`refcount` 等，提供 `image()`/`imageview()` 底层访问（mat.h:655-684）。
- F-035：`vk_specialization_type` 和 `vk_constant_type` 均为 `union { int i; float f; uint32_t u32; }`（mat.h:687-698）。
- F-036：`float32_to_bfloat16` 直接取高 16 位（`tmp.u >> 16`），`bfloat16_to_float32` 左移 16 位（mat.h:826-848）。
- F-037：全局 Mat 处理函数含 `copy_make_border`、`resize_nearest/bilinear/bicubic`、`convert_packing`、`flatten`、`cast_*`、`quantize_to_int8`、`dequantize_from_int32`、`requantize_from_int32_to_int8`（mat.h:876-892）。

## 三、Layer 基类（layer.h）

- F-038：`Layer` 能力标志位（bool）：`one_blob_only`、`support_inplace`、`support_vulkan`、`support_packing`、`support_bf16_storage`、`support_fp16_storage`、`support_int8_storage`、`support_tensor_storage`、`support_vulkan_packing`、`support_any_packing`、`support_vulkan_any_packing`、`support_batch`（layer.h:46-79）。
- F-039：`Layer` 生命周期虚函数：`load_param(const ParamDict&)`、`load_model(const ModelBin&)`、`create_pipeline(const Option&)`、`destroy_pipeline(const Option&)`（layer.h:30-42）。
- F-040：CPU `forward` 虚函数重载：`forward(const std::vector<Mat>&, std::vector<Mat>&, const Option&) const` 和 `forward(const Mat&, Mat&, const Option&) const`（layer.h:95-96）。
- F-041：CPU `forward_inplace` 虚函数重载：`forward_inplace(std::vector<Mat>&, const Option&) const` 和 `forward_inplace(Mat&, const Option&) const`（layer.h:100-101）。
- F-042：Vulkan `forward` 虚函数重载：`forward(const std::vector<VkMat>&, std::vector<VkMat>&, VkCompute&, const Option&) const` 和 `forward(const VkMat&, VkMat&, VkCompute&, const Option&) const`（layer.h:111-112）。
- F-043：Vulkan `forward_inplace` 虚函数重载：`forward_inplace(std::vector<VkMat>&, VkCompute&, const Option&) const` 和 `forward_inplace(VkMat&, VkCompute&, const Option&) const`（layer.h:116-117）。
- F-044：`Layer` 字段：`void* userdata`、`int typeindex`、`std::string type`、`std::string name`、`std::vector<int> bottoms`、`std::vector<int> tops`、`std::vector<Mat> bottom_shapes/top_shapes`（layer.h:126-141）。
- F-045：Vulkan 下 `Layer` 有 `upload_model(VkTransfer&, const Option&)` 虚函数和 `const VulkanDevice* vkdev` 成员（layer.h:106,121）。
- F-046：`layer_creator_func` 类型为 `Layer* (*)(void*)`；`layer_destroyer_func` 类型为 `void (*)(Layer*, void*)`（layer.h:145-146）。
- F-047：`DEFINE_LAYER_CREATOR(name)` 宏生成 `name_layer_creator(void*)` 返回 `new name`；`DEFINE_LAYER_DESTROYER(name)` 宏生成 `delete layer`（layer.h:199-209）。
- F-048：工厂函数 `create_layer` 支持 by name/index，并有 `naive`/`cpu`/`vulkan` 变体（layer.h:182-197）。
- F-049：`layer_registry_entry` 结构含 `name`（NCNN_STRING）和 `creator`；`custom_layer_registry_entry` 额外含 `destroyer/userdata`；`overwrite_builtin_layer_registry_entry` 含 `typeindex`（layer.h:148-178）。

## 四、Blob（blob.h）

- F-050：`Blob` 字段：`std::string name`（NCNN_STRING）、`int producer`（产生该 blob 的层索引）、`int consumer`（消费该 blob 的层索引）、`Mat shape`（形状提示）（blob.h:19-28）。

## 五、Option 推理选项（option.h）

- F-051：`Option::lightmode` 默认 true，启用中间 blob 回收（option.h:27）。
- F-052：`Option::num_threads` 默认值为 `get_cpu_count()` 返回值（option.h:38）。
- F-053：`Option` 持有 `blob_allocator`、`workspace_allocator`、`kvcache_allocator` 三个 `Allocator*`（option.h:41-47）。
- F-054：`openmp_blocktime` 默认 20ms，控制 OpenMP 线程自旋等待时间（option.h:72）。
- F-055：`use_winograd_convolution` 和 `use_sgemm_convolution` 默认 true（option.h:78,84）。
- F-056：`use_int8_inference` 默认 true（option.h:90）。
- F-057：`use_vulkan_compute` 默认 false（option.h:93）。
- F-058：`use_bf16_storage`、`use_fp16_packed/storage/arithmetic`、`use_int8_packed/storage/arithmetic`、`use_int16_packed/storage` 控制低精度（option.h:97-105,158-159）。
- F-059：`use_packing_layout` 默认 true，启用 SIMD 友好打包内存布局（option.h:111）。
- F-060：`flush_denormals` 默认 3，即 DAZ ON + FTZ ON（option.h:130）。
- F-061：Vulkan 下 Option 含 `blob_vkallocator/workspace_vkallocator/staging_vkallocator/kvcache_vkallocator` 和 `PipelineCache* pipeline_cache`（option.h:54-67）。
- F-062：`use_shader_local_memory`、`use_cooperative_matrix`、`use_winograd23/43/63_convolution`、`use_a53_a55_optimized_kernel` 等细分优化开关（option.h:139-151）。

## 六、Allocator 内存管理（allocator.h）

- F-063：`NCNN_MALLOC_ALIGN` 常量：NCNN_AVX512=64，NCNN_AVX=32，否则=16（allocator.h:25-31）。
- F-064：`NCNN_MALLOC_OVERREAD=64` 字节，为 SIMD 循环越界读取预留安全余量（allocator.h:36）。
- F-065：`fastMalloc`/`fastFree` 跨平台实现：MSVC 用 `_aligned_malloc`，POSIX 用 `posix_memalign`，旧 Android 用 `memalign`，其他用手动对齐包装（allocator.h:56-92）。
- F-066：`Allocator` 抽象基类含纯虚 `fastMalloc(size_t)` 和 `fastFree(void*)`（allocator.h:142-148）。
- F-067：`PoolAllocator` 线程安全内存池，PIMPL（`PoolAllocatorPrivate* const d`），支持 `set_size_compare_ratio`/`set_size_drop_threshold`/`clear`（allocator.h:151-177）。
- F-068：`UnlockedPoolAllocator` 单线程内存池，接口同 PoolAllocator 但无锁，PIMPL（allocator.h:180-206）。
- F-069：`NCNN_XADD(addr, delta)` 原子加操作，覆盖 GCC `__atomic_fetch_add`、Clang C11 atomics、MSVC `_InterlockedExchangeAdd`、ICC、无 A 扩展 RISC-V、无线程降级（allocator.h:98-140）。
- F-070：`VkBufferMemory` 含 `VkBuffer buffer`、`offset/capacity`、`VkDeviceMemory memory`、`mapped_ptr`、`memory_type_index`、`access_flags/stage_flags`、`refcount`（allocator.h:212-232）。
- F-071：`VkAllocator` 抽象基类含纯虚 buffer 和 image 两套 `fastMalloc/fastFree`，持有 `vkdev` 和内存类型索引（allocator.h:267-299）。
- F-072：`VkBlobAllocator` 块大小默认 16MB（allocator.h:305）。
- F-073：`VkWeightAllocator` 块大小默认 8MB，支持 `prefer_host_memory` 选项（allocator.h:329）。
- F-074：`VkStagingAllocator` 默认 `size_compare_ratio=0.75`（allocator.h:364）。
- F-075：`VkWeightStagingAllocator` 权重暂存分配器（allocator.h:383-401）。

## 七、ParamDict / ModelBin / DataReader

- F-076：`NCNN_MAX_PARAM_COUNT=32`，每层最多 32 个参数（paramdict.h:10）。
- F-077：`ParamDict::get` 支持 `int/float/Mat/string` 四种类型重载并接受默认值；`set` 对应四种（paramdict.h:35-50）。
- F-078：`ParamDict` 使用 PIMPL（`ParamDictPrivate* const d`），友元类为 Net（paramdict.h:53-61）。
- F-079：`ModelBin::load` type 枚举：0=auto，1=float32，2=float16，3=int8，4=weight block quantize int4，6=int6，8=int8（modelbin.h:18-24）。
- F-080：`ModelBinFromDataReader` 从 `DataReader` 加载；`ModelBinFromMatArray` 从 `const Mat* weights` 数组加载（modelbin.h:36-68）。
- F-081：`DataReader` 虚函数 `scan`（NCNN_STRING 文本解析）、`read`（二进制读取）、`reference`（零拷贝引用），子类 `FromStdio`/`FromMemory`/`FromAndroidAsset`（datareader.h:21-107）。

## 八、Vulkan GPU 后端（gpu.h/pipeline.h/command.h/pipelinecache.h）

- F-082：`create_gpu_instance(driver_path=0)`/`destroy_gpu_instance()` 管理全局 `VkInstance` 生命周期（gpu.h:21-30）。
- F-083：gpu.h 声明约 90 个 `PFN_vk*` 函数指针全局变量，由 simplevk 内置 loader 在运行时解析（gpu.h:33-127）。
- F-084：`GpuInfo` 类提供物理设备属性、内存属性、扩展列表、硬件限制、subgroup 信息、fp16/int8/bf16/cooperative matrix 特性查询（gpu.h:189-433）。
- F-085：`VulkanDevice` 类持有 `const GpuInfo& info`，提供 `compile_shader_module`、`create_pipeline`、`create_descriptorset_layout`、`find_memory_index`、`acquire_queue/reclaim_queue`（gpu.h:442-471）。
- F-086：`VulkanDevice::acquire_blob_allocator/reclaim_blob_allocator` 和 staging 版本提供池化 VkAllocator（gpu.h:474-478）。
- F-087：`Pipeline` 类封装 `VkShaderModule`/`VkDescriptorSetLayout`/`VkPipelineLayout`/`VkPipeline`/`VkDescriptorUpdateTemplateKHR`，PIMPL（pipeline.h:18-65）。
- F-088：`Pipeline::set_optimal_local_size_xyz` 默认参数 w=4,h=4,c=4（pipeline.h:25）。
- F-089：`PipelineCache` 提供 `get_pipeline`（两种重载：spv 数据和 shader_type_index）和 `save_cache/load_cache`（内存/文件/FILE*）（pipelinecache.h:22-85）。
- F-090：`VkCompute` 类录制 `record_upload/record_download/record_clone/record_pipeline`，`submit_and_wait()` 提交等待，PIMPL（command.h:22-88）。
- F-091：`VkTransfer` 类仅录制 `record_upload`，用于权重上传，PIMPL（command.h:91-111）。
- F-092：`ShaderInfo` 含 `specialization_count/binding_count/push_constant_count` 和 `binding_types[16]`（1=storage buffer,2=storage image,3=combined image sampler）（gpu.h:577-594）。
- F-093：`simplevk.h` 存在于 src/；CMake 选项 `NCNN_SIMPLEVK` 默认 ON（CMakeLists.txt:83）。

## 九、C 语言 API（c_api.h）

- F-094：`ncnn_version()` 返回版本字符串，`ncnn_version_number()` 返回版本号（c_api.h:18-19）。
- F-095：C API 通过不透明句柄（`ncnn_net_t`/`ncnn_extractor_t`/`ncnn_mat_t` 等）和函数指针表（`__ncnn_allocator_t`/`__ncnn_datareader_t`/`__ncnn_modelbin_t`/`__ncnn_layer_t`）覆盖 allocator/option/mat/blob/paramdict/datareader/modelbin/layer/net/extractor 全部模块（c_api.h）。

## 十、构建系统（CMakeLists.txt）

- F-096：`NCNN_VERSION_MAJOR=1`、`NCNN_VERSION_MINOR=0`、`NCNN_VERSION_PATCH=${NCNN_VERSION}`（`string(TIMESTAMP NCNN_VERSION "%Y%m%d")`），版本字符串 `1.0.${日期}`（CMakeLists.txt:14-23）。
- F-097：`NCNN_VULKAN` 默认 OFF；`NCNN_OPENMP` 默认 ON；`NCNN_INT8` 默认 ON；`NCNN_PYTHON` 默认 OFF（CMakeLists.txt:82,63,92,91）。
- F-098：`NCNN_BF16` 默认 ON；`NCNN_WEIGHT_QUANT` 默认 ON；`NCNN_BATCH` 默认 ON；`NCNN_PIXEL` 默认 ON（CMakeLists.txt:94,93,75,77）。
- F-099：`NCNN_RUNTIME_CPU` 默认 ON；`NCNN_SIMPLEVK` 默认 ON（CMakeLists.txt:85,83）。
- F-100：`NCNN_SIMPLEOCV/SIMPLEOMP/SIMPLESTL/SIMPLEMATH` 默认 OFF；ANDROID/IOS/SIMPLESTL 时自动禁用 RTTI 和异常（CMakeLists.txt:67-70,97-103）。

## 十一、CPU 特性检测与平台优化（cpu.h/ruapu.h）

- F-101：`ruapu.h` 单文件 CPU ISA 检测库，提供 `ruapu_init()`/`ruapu_supports(const char*)`/`ruapu_rua()`（ruapu.h:14-18）。
- F-102：`cpu.h` 声明 ARM（edsp/neon/vfpv4/asimdhp/asimddp/asimdfhm/bf16/i8mm/sve/sve2）、x86（avx/fma/xop/f16c/avx2/avx512/vnni/bf16/fp16）、MIPS（msa/mmi）、LoongArch（lsx/lasx）、RISC-V（v/zfh/zvfh/xtheadvector/vlenb）全套检测函数（cpu.h:45-119）。
- F-103：`src/layer/` 子目录文件数：arm=265、x86=282、mips=163、riscv=180、loongarch=170、vulkan=128；根目录 110 个 .cpp + 111 个 .h。

## 十二、零依赖基础设施与 Python 绑定

- F-104：src/ 下存在 `simplestl.h/.cpp`、`simpleomp.h`、`simpleocv.h`、`simplemath.h`、`simplevk.h` 五个内嵌替代实现，对应 CMake `NCNN_SIMPLESTL/SIMPLEOMP/SIMPLEOCV/SIMPLEMATH/SIMPLEVK` 选项。
- F-105：`python/src/` 含 `main.cpp`、`pybind11_bind.h`、`pybind11_layer.h`、`pybind11_mat.h`。
- F-106：`pybind11_mat.h` 的 `to_buffer_info` 仅支持 `elemsize` 为 1/2/4 且 `elempack==1`，据此构造 numpy buffer_info（pybind11_mat.h:41-55）。
- F-107：`python/ncnn/model_zoo/` 含 20 个预训练模型类：YOLOv2/v3/v4/v5/v7/v8、Yolact、MobileNet-SSD/SqueezeNet-SSD/SSDLite、SqueezeNet、Faster-RCNN、PeleeNet-SSD、RetinaFace、RFCN、ShuffleNetV2、SimplePose、NanoDet（model_zoo.py:26-47）。
- F-108：`layer_type.h` 通过 `#include "layer_type_enum.h"` 引入层类型枚举（该文件由 CMake 在构建期生成），`CustomBit = (1 << 8)`（layer_type.h:9-14）。
