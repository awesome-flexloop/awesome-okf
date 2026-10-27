---
type: Concept
title: Windows Arm 原生开发与迁移
description: 区分 CPU/CUDA 构建、Python 包覆盖、Windows ML 实验 API 与跨平台部署条件
tags: [Windows on Arm, CUDA, PyTorch, WSL, Windows ML]
source: ../references/article-source.md
sources:
  - id: facts
    resource: ../references/article-source.md
  - id: nvidia
    resource: https://developer.nvidia.com/blog/code-test-and-deploy-on-one-machine-with-nvidia-rtx-spark
  - id: microsoft
    resource: https://devblogs.microsoft.com/foundry-on-windows/build-on-winml-oct-7-26/
  - id: history
    resource: https://blogs.windows.com/windowsdeveloper/2025/04/23/pytorch-arm-native-builds-now-available-for-windows/
status: stable
stale_after: 2026-12-31
---

# Windows Arm 原生开发与迁移

微软新公告区分两条路径：PyTorch 官方原生 Windows Arm64 CPU 构建，以及 NVIDIA 面向受支持硬件发布的 CUDA-enabled Arm64 包（[F-045](../references/article-source.md)）。原生指匹配处理器/操作系统架构的构建，不能据此推断任意 wheel、扩展或 GPU 内核都已兼容。

PyTorch负责模型计算，CUDA提供NVIDIA GPU计算平台，TensorRT用于推理优化，Triton用于编写和编译GPU计算内核。wheel是Python分发包，依赖锁固定版本，ABI规定二进制如何调用；ONNX与GGUF是不同模型表示/存储路径。更多入门释义见[入口术语表](../index.md#术语速查)，此处解释工具职责不表示对应版本已经实测兼容。

## “首个”的准确范围

2025-04-23 微软已公布 PyTorch 2.7 的 Windows Arm64 原生构建，当时面向 Python 3.12，示例使用 CPU（F-044）。本次 RTX Spark 发布稿的“首个”指 **Windows on Arm PyTorch-CUDA build**（F-043），不应改写成“Windows Arm 第一次能运行 PyTorch”。

NVIDIA 开发稿写 Python 3.15 默认原生、超过 2,000 个 Conda 包；微软示例则选 Python 3.14-arm64 和明确版本的 CUDA/Triton 包（F-046、F-048）。两者是不同文本中的发布说明与示例组合，本包不把它们拼成一套未经验证的安装命令。

## 97% 的限制

发布稿说前 15,000 个 Python 包支持率为 97%，开发稿表述为超过 97% 的 Arm 兼容版本（F-047）。它们是 NVIDIA 的包覆盖声明，未附本包可审计的全量测试结果。

包是否提供兼容构建、该构建是否可安装、应用能否正确运行、GPU 路径是否加速，是不同层次。一个应用的依赖锁可能命中剩余缺口；CPU 可用也不能证明 CUDA 可用。判断现有项目应审计锁定版本、wheel 平台标签、原生扩展、插件和目标驱动，而不是依据整体覆盖率跳过逐依赖检查。

## 两条开发环境路线

| 环境 | 发布资料中的作用 | 验收时关注 |
|---|---|---|
| Windows 原生 | Windows Developer Config、Arm64 Python/PyTorch、Windows 应用接入 | 安装器架构、原生扩展、CUDA 与应用接口 |
| WSL Linux | 熟悉的 Linux 开发工具和云开发依赖 | 发行版架构、GPU 支持、依赖版本与目标 Linux 一致性 |

依据为 F-040~F-041、F-045~F-051。共享 NVIDIA GPU 平台使开发路径有共性，但 Windows Arm64、Linux Arm64、Linux x86_64 的二进制不能因使用 CUDA 而自动互换。官方开发稿也要求审计依赖与移植测试（F-051）。“代码不迁移”应理解为目标条件满足时的工作流愿景，不是任意平台的二进制兼容承诺。

Arm64EC 是开发稿给出的渐进移植选择（F-051），不是本包建议所有项目立即采用的统一 ABI。确定路线后，分别验证安装、功能、性能与实际使用的 GPU 路径。

## Windows ML 的状态

微软将llama.cpp/GGUF集成与新Windows-native Runtime API标为experimental/preview，列Windows ML版本2.7.2021-experimental，既有ONNX Runtime路径仍受支持（F-049）。Text Generation API提供ONNX/GGUF路径及OpenAI-compatible本地端点；Speech Recognition API使用ONNX Whisper（F-050）。复核需绑定该实验版本与发行通道，不能仅凭后续有正式版就改写本次支持范围。

这为应用提供多条推理接入路径，但“OpenAI-compatible”并不保证所有 OpenAI 功能、工具调用参数与流式事件都相同。生产使用前需要核对 API 文档、支持场景与已知限制。本包不把微软博客中的实验示例写成长期有效的生产安装教程。

## 怎样读性能比较

NVIDIA 开发稿将 RTX Spark 与 Intel Core Ultra X9 388H 对比：编码智能体 4.6x、LoRA 微调 2.7x、Linux 内核编译 1.8x，三项对应不同测试与模型（F-052）。这是 NVIDIA 自测结果，不是本包实测，更不是同一指标的三次测量。

这些数字不能证明任意开发任务整体提效，也不能把模型推理吞吐当作工程师完成工作的速度。移植评估应使用自己的测试集，记录完成率、代码正确性、任务耗时、失败重试和云回退量。基础知识可结合现有[Python 知识包](../../../python/index.md)、[Conda 知识包](../../../build/conda/index.md)及[WSL 教程](../../../systems/wsl/index.md)阅读。
