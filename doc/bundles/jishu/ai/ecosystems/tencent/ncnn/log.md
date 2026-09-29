---
type: Changelog
title: ncnn 知识包变更日志
---

# 更新日志

## 2026-08-23

- 初始化 ncnn OKF 知识包，基于 ncnn 源码版本 1.0.20260526（MAJOR=1, MINOR=0, PATCH=构建日期）。
- R 阶段：逐文件阅读 `src/` 下 14 个核心头文件（net.h、mat.h、layer.h、blob.h、option.h、allocator.h、paramdict.h、modelbin.h、gpu.h、pipeline.h、command.h、pipelinecache.h、c_api.h、datareader.h）及 CMakeLists.txt、cpu.h、ruapu.h、python/ 绑定，提取 108 条编号事实（F-001~F-108），写入 `spec/facts.md`。
- 统计 `src/layer/` 子目录文件数：arm=265、x86=282、mips=163、riscv=180、loongarch=170、vulkan=128、根目录 110 .cpp + 111 .h。
- I 阶段：提炼 5 个架构洞察（零依赖极简基础设施、PIMPL 编译防火墙、引用计数 Mat 浅拷贝零拷贝、编译期多套 kernel + ruapu 运行时分发、Vulkan/CPU 统一 Layer 抽象），写入 `spec/insights.md`。
- E 阶段：生成 22 个内容文档：
  - 6 个信源登记（references/）：net-extractor、mat-tensor、layer-base、allocator、vulkan-backend、build-system；
  - 12 个概念文档（concepts/）：00 整体架构、01 Net/Extractor、02 Mat、03 Layer、04 Allocator、05 Option、06 Vulkan、07 SIMD 打包、08 ParamDict/ModelBin、09 层注册表、10 Python 绑定、11 量化；
  - 4 个示例（examples/）：C++ 推理、Python YOLO、自定义 Layer、Vulkan GPU。
- 生成各级 index.md（concepts/examples/references 子目录无 frontmatter，根 index.md 含 `okf_version: "0.2"`）。
- V 阶段：通过 Grep 验证 20 个核心类名存在于 src/、Layer 虚函数签名与 layer.h 一致、Mat 字段与 mat.h 一致、CMake 选项名与 CMakeLists.txt 一致。
