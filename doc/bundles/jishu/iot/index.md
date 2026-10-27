---
okf_version: "0.2"
type: group
title: "🏠 物联网（IoT）"
description: "物联网与远程连接知识包——开源智能家居平台源码解读、跨平台 IoT SDK 架构、贝锐远控产品生态与横向对比"
---

# 🏠 物联网（IoT）知识包

本组收录物联网与远程连接相关的知识包：开源智能家居平台（Home Assistant）的核心架构与集成开发、跨平台 IoT SDK（TuyaOpen）的双层抽象与全栈能力、贝锐（Oray/向日葵）远控产品生态，以及厂商与工具横向对比；另收录经七概念方法论（R→I→E→V→C）与博文转化工作流产出的端侧 AI 资讯核验包，厂商自宣数据与独立核验结论分栏呈现。

## 知识包列表

| 知识包 | 定位 | 说明 |
|--------|------|------|
| [home-assistant/](home-assistant/index.md) | Home Assistant 源码教程 | 开源智能家居平台——三层架构、运行时内核、集成开发模式与 hassfest 质量工具链 |
| [tuya-iot/](tuya-iot/index.md) | TuyaOpen IoT SDK 源码教程 | 涂鸦跨平台 IoT SDK——TAL/TKL 双层抽象、组件化构建、全栈 IoT 能力与 8 款芯片平台支持 |
| [sunlogin/](sunlogin/index.md) | 向日葵远程控制产品矩阵 | 贝锐向日葵全线产品——安全架构、远控硬件、CLI 与 AI 开发者生态（MCP/Skill/HSK/UI Locator）、离线硬件 |
| [oray/](oray/index.md) | 贝锐（Oray）公司与产品生态 | 贝锐科技公司全景与核心产品笔记——产品矩阵与商业模式分析 |
| [comparison/](comparison/index.md) | IoT 厂商与工具横向对比 | 内网穿透工具六维度选型对比（神卓互联/cpolar/花生壳）与向日葵 vs 涂鸦智能七维度范式对比 |

### 📰 端侧 AI 资讯（博文核验）

| 知识包 | 定位 | 说明 |
|--------|------|------|
| [xingchen-300-edge-ai/](xingchen-300-edge-ai/index.md) | 端侧 AI 平台资讯核验 | 安谋科技星辰300（STAR-MC2/Cortex-M52 + Ethos-U55，MPS3 FPGA）原型平台——四大实测用例、CPU+NPU 异构机制、Helium 性能数字与 Transformer 能力勘误、五个开源模型档案与厂商自述可信边界 |
| [embedded-weekly-03/](embedded-weekly-03/index.md) | 端侧 AI 资讯周报核验 | 《嵌入式周报·第三期》全量学习——openTPU AI 设计芯片、NPU 下沉 MCU、Zephyr 版本节奏/CVE-2026-19569/白金会员、RVA23 软件栈、社区硬件与打假，事实 F-001~F-052 与 17 项 P0 核验 |
| [rtx-spark/](rtx-spark/index.md) | Windows本地AI PC概念教程 | NVIDIA上市稿与8个补充信源——统一内存、FP4、Windows Arm、智能体、创作和游戏；64条事实、23项核验，厂商性能未独立实测 |

### 🔬 开源源码精读

| 知识包 | 定位 | 说明 |
|--------|------|------|
| [opentpu/](opentpu/index.md) | AI 加速器源码教程 | openTPU 固定提交 ffe997e 一手精读——17 条指令 ISA、四列脉动 MXU、fp32 数值契约、FP4 量化（4.25 bits/weight）、ol 编译器、STREAM 状态引擎、MoE 专家流、Kintex-7 板卡与 NanGate45 ASIC、三端位精确验证；17 概念 + 3 示例 + F-001~F-123 pinned 溯源 |
| [hwe-bench/](hwe-bench/index.md) | LLM 硬件基准源码教程 | HWE Bench（auto-arch-tournament）固定提交 4a137bb 一手精读——LLM 自主进化 RISC-V CPU 的七门验证器：假设 schema、worktree 沙箱与契约指纹、RVFI NRET=2、riscv-formal/ALTOPS 分层、22% 反压 cosim、3-seed FPGA fitness、严格接受规则；v1 九胜场进化史、16 模型 V1 排行榜、V2 holdout 与 harness 故障方向工程；17 概念 + 3 示例 + F-001~F-126 + K-1~K-6 口径勘误 |

```{toctree}
:hidden:
:maxdepth: 7

home-assistant/index
tuya-iot/index
sunlogin/index
oray/index
comparison/index
xingchen-300-edge-ai/index
embedded-weekly-03/index
rtx-spark/index
opentpu/index
hwe-bench/index
```
