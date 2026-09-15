---
type: Concept
title: 五个演示模型档案与可信边界
description: 生态/边界层——YOLO-Fastest、Conformer、SESR（博文误写ESR）等五个端侧演示模型开源档案、TFLite Micro+Vela软件栈与厂商自述等四条可信边界
tags: [YOLO-Fastest, wav2letter, Conformer, kws-micronet, MicroNets, SESR, ML-zoo, TinyML, 模型档案, 可信边界]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-15T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-15T20:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: yolo-fastest-github
    resource: https://github.com/dog-qiuqiu/Yolo-Fastest
    title: YOLO-Fastest GitHub 仓库（dog-qiuqiu）
  - id: wav2letter-github
    resource: https://github.com/flashlight/wav2letter
    title: wav2letter GitHub 仓库（flashlight，原 FAIR）
  - id: conformer-paper
    resource: https://arxiv.org/abs/2005.08100
    title: "Conformer: Convolution-augmented Transformer for Speech Recognition（Interspeech 2020）"
  - id: micronets-paper
    resource: https://arxiv.org/abs/2010.11267
    title: MicroNets（MLSys 2021，TinyMLPerf KWS 网络）
  - id: arm-ml-zoo
    resource: https://github.com/Arm-Examples/ML-zoo
    title: Arm 官方 ML-zoo 模型库（kws micronet / SESR int8 模型）
  - id: sesr-paper
    resource: https://arxiv.org/abs/2103.09404
    title: "SESR: Collapsible Linear Blocks for Super-Efficient Super Resolution（MLSys 2022，Arm Research）"
---

# 五个演示模型档案与可信边界

> 本篇为**生态/边界层**：给出四个用例所涉五个模型的可溯源档案（含博文"ESR"名称勘误），梳理端侧软件栈，并集中声明本知识包的可信边界。平台事实见 [00 平台与四大用例](00-platform-and-demos.md)，硬件机制见 [01 CPU+NPU 异构设计](01-cpu-npu-heterogeneous-design.md)。

## 1. 模型选择的共同约束

能进入 Cortex-M + microNPU 演示的模型须满足：int8/int16 量化、算子落在 TFLite Micro + Vela 支持集合内（不支持的算子允许回退 CPU）、内存占用为 KB~数百 KB 级。五个模型恰好覆盖**检测、CNN 语音、混合架构语音、KWS、超分**五类 TinyML 典型任务（F-005、F-011~F-014）。

## 2. 模型档案

### 2.1 YOLO-Fastest（人脸探测）

- **项目**：[github.com/dog-qiuqiu/Yolo-Fastest](https://github.com/dog-qiuqiu/Yolo-Fastest)（2020-08 建仓，主语言 C，约 2.1k stars）
- **定位**：作者自述"ultra-lightweight universal target detection algorithm"——超轻量通用目标检测，**250 MFLOPS**，ncnn 模型仅约 **666KB**；树莓派 3B 约 15fps、手机端约 178fps
- **演示形态**：预录制视频与摄像头实时双模人脸探测；目标场景为门禁/监控目标探测（F-011）

### 2.2 wav2letter（语音识别演示 1，CNN 路线）

- **项目**：[github.com/flashlight/wav2letter](https://github.com/flashlight/wav2letter)（原 facebookresearch，FAIR）
- **架构**：**全卷积端到端 ASR**（CNN + CTC/ASG），博文"基于 CNN 架构"表述准确（F-012、F-023）
- **时间**：Lua/Torch 原版 2017 年开源；C++ 重写版 **wav2letter++ 于 2018-12-21 开源**（Meta Engineering 公告）
- **论文链**：Wav2Letter（[arXiv:1609.03193](https://arxiv.org/abs/1609.03193)）→ Gated ConvNets（[arXiv:1712.09444](https://arxiv.org/abs/1712.09444)）→ wav2letter++（[arXiv:1812.07625](https://arxiv.org/abs/1812.07625)）

### 2.3 Conformer（语音识别演示 2，卷积增强 Transformer 路线）

- **论文**：Google，[arXiv:2005.08100](https://arxiv.org/abs/2005.08100)（2020-05，**Interspeech 2020**），标题即"**Convolution-augmented** Transformer for Speech Recognition"
- **架构**：Macaron 前馈 + 自注意力 + 卷积模块交替的混合编码器——博文简称"基于 Transformer"可接受，严格表述应为**卷积增强 Transformer（CNN + Self-Attention 混合）**
- **在平台上的运行机制**：U55 不原生支持 Transformer，靠 Vela 图分区把卷积/全连接卸载 NPU、注意力等算子回退 M52 CPU（F-021，详见 [01 异构设计 §4](01-cpu-npu-heterogeneous-design.md#4-vela-图分区conformer-为何能跑)）

### 2.4 kws-micronet（关键字检测）

- **模型出处**：**Arm 官方 ML-zoo** 的 `keyword_spotting/` 目录，提供 micronet_small / medium / large 三档 **tflite_int8** 量化模型（[ML-zoo KWS](https://github.com/Arm-Examples/ML-zoo/tree/master/models/keyword_spotting)）
- **论文出处**：MicroNets——"Neural Network Architectures for Deploying TinyML Applications on Commodity Microcontrollers"（[arXiv:2010.11267](https://arxiv.org/abs/2010.11267)，MLSys 2021），也是 TinyMLPerf 关键字识别任务的参考网络族
- **演示词表**：英文单词 **No / Right / Stop / Up / Yes**（F-026）；目标场景为穿戴/手机唤醒与语音控制、行车记录仪及车载语音控制（F-013）

### 2.5 SESR 超分（博文"ESR"名称勘误，F-024）

- **勘误结论**：arXiv/GitHub 查无名为"ESR"的独立超分模型；两个近似名称均不是它——ESPCN（亚像素卷积开山作，[arXiv:1609.05158](https://arxiv.org/abs/1609.05158)）与 ESRGAN（GAN 路线，模型沉重，不适合 M 级 MCU，[arXiv:1809.00219](https://arxiv.org/abs/1809.00219)）
- **真身**：**SESR（Super-Efficient Super Resolution）**，Arm Research 的 Bhardwaj 等人论文《Collapsible Linear Blocks for Super-Efficient Super Resolution》（[arXiv:2103.09404](https://arxiv.org/abs/2103.09404)，**MLSys 2022**），官方代码 [github.com/ARM-software/sesr](https://github.com/ARM-software/sesr)（Apache-2.0，x2/x4、QAT 全 int8，旗舰变体 SESR-M5）
- **判定依据（三方吻合，高置信）**：① Arm 官方 ML-zoo 超分目录有且仅有 SESR 一族且只提供 Ethos-U 部署用 int8 模型（[ML-zoo SESR](https://github.com/Arm-Examples/ML-zoo/tree/master/models/superresolution/SESR/tflite_int8)）；② SESR 系 Arm 自家模型，与安谋平台同生态；③ 演示规格 128×128→512×512 恰为 **4×**，与 SESR x4/int8 用例一致
- **残余不确定性**：名称"漏字"的发生环节（安谋演讲 slides 还是媒体转述）无法证实，一手 slides 未公开；本包正文统一采用 SESR，保留"博文写作 ESR"的标注

## 3. 软件栈

| 层 | 组件 | 作用 |
|----|------|------|
| 模型格式 | int8 / int16 **TensorFlow Lite for Microcontrollers** | Cortex-M 上的轻量推理引擎，持有完整计算图 |
| NPU 编译 | **Vela**（PyPI 包 ethos-u-vela） | 将支持的算子编译为 U55 命令流，其余算子保留在图中回退 CPU |
| CPU 算子库 | **CMSIS-NN / CMSIS-DSP** | Helium 加速的神经网络与信号处理内核 |
| 运行环境 | RTOS 或裸机 | MPS3 FPGA 原型；量产形态如 Synaptics SYN765x |

安谋官方另在 WAIC 演讲中列举平台支持 Yolo v4、DeepLab v3+、MobileNet v2、UNet、ESRGAN 等小模型（F-029，厂商口径，注意 ESRGAN 与演示所用 SESR 不是同一模型）。

## 4. 可信边界（四条）

1. **厂商自述，无第三方实测**：平台能力与四用例"跑通"均来自安谋科技通稿与自导演示视频；无公开精度、时延、功耗、mW/推理数据；多媒体同稿分发不构成独立多源（F-002、F-004）。应用领域（门禁/眼镜/穿戴/车载/监控）是**目标场景宣称**，无绑定的量产客户案例。
2. **英文语料边界**：ASR 例句与 KWS 词表均为英文，没有中文语音能力的演示证据，不能据此外推中文场景表现（F-026）。
3. **FPGA ≠ 量产芯片**：32MHz 是 FPGA 软核时钟（F-022）；"500MHz/1GHz 下快 20-30 倍"是厂商线性外推，忽略存储带宽与 NPU 频率比等非线性因素，**不构成性能预测**（F-027）；量级感可参考商用 Synaptics 方案 200MHz/约 50 GOPS（F-025）。
4. **数字引用边界**：Helium 5×/15× 属 Cortex-M55（非平台所用 M52，M52 为 2.7×/5.6×）（F-019）；0.5 TOPS 属 U55 顶配峰值（F-020）；440+ 客户/425 亿出货、+900% AI 为安谋自述（F-028）；平台/器件基础事实（型号、发布日期、架构归属）已经 Arm 官方与工商/媒体记录交叉确认，可放心引用。

## 5. 复核触发条件（stale_after 2026-12-31 前）

出现以下任一事件应复核并更新本包：① 星辰300 由 FPGA 平台转为流片/量产芯片并公布规格；② 任一方发布四用例的第三方实测（精度/时延/功耗）；③ Arm 或安谋更新 STAR-MC2/Cortex-M52 与 Ethos-U 组合的官方材料（如 Corstone 新增 M52+U55 参考设计）；④ SESR/模型清单出现官方一手材料证实或否定"ESR"名称成因。
