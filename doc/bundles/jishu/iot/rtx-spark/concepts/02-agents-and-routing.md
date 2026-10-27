---
type: Concept
title: 本地智能体与多设备推理
description: 区分模型推理、工具执行、云端路由和权限隔离，解释 PAIR 的服务拓扑
tags: [AI Agent, OpenShell, PAIR, 本地 AI, 安全]
source: ../references/article-source.md
sources:
  - id: facts
    resource: ../references/article-source.md
  - id: release
    resource: https://nvidianews.nvidia.com/news/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/
  - id: dev
    resource: https://developer.nvidia.com/blog/code-test-and-deploy-on-one-machine-with-nvidia-rtx-spark
  - id: pair
    resource: https://www.nvidia.com/en-us/ai-on-rtx/personal-ai-router/
status: stable
stale_after: 2026-12-31
---

# 本地智能体与多设备推理

发布稿列出 Copilot、Hermes、OpenClaw、Perplexity、Pi 和 WorkBuddy 的引导设置与安装器（[F-019](../references/article-source.md)）。这说明存在入门路径，不能由名单推断每个产品、每个功能均在离线环境运行。

## 四层执行关系

| 层次 | 作用 | 本包依据 |
|---|---|---|
| 模型 | 接收上下文并生成文本或工具调用意图 | Nemotron 定位与框架清单，F-021~F-023 |
| 智能体 | 维护任务过程、选择工具、处理结果 | 发布稿列任务完成、资产生成与编码，F-019~F-020 |
| 工具 | 读写文件、调用创作软件、执行开发任务 | Skills 与 Broadcast/Remix/Omniverse 集成，F-025 |
| 权限和路由 | 约束访问范围，选择本地或云模型 | OpenShell/MXC、混合路由，F-024、F-028 |

模型在本机运行，不会自动限制工具权限。一个具有文件写入或联网能力的智能体仍可能删除文件、发送数据或触发付费操作。以上是通用风险分析；本包没有验证某个产品的具体漏洞。

**教学任务例子，未实际执行**：整理测试目录时，模型提出分类意图，智能体选择文件工具，工具执行获准的读写，权限层拦截越界访问。若检索服务、遥测或云回退发送文件内容，即使模型本地运行也有数据出口；检索是查找辅助材料，遥测是运行诊断信息，云回退是改用远端模型。客户端发起请求，服务端执行服务，PAIR中的两者可在不同机器。

## 本地与混合

开发稿明确讨论本地/云端混合路由（F-028）。理解“本地 AI”时需逐项确认模型推理、检索、工具服务、遥测、登录和更新的流向。只证明推理本地，不能证明完整任务链离线。

NVIDIA 在发布稿中把 OpenShell Secure Runtime 与 Microsoft Execution Containers 定位为权限控制工具（F-024）。本包未检查其策略配置、支持版本与隔离实现，因此不宣称“绝对安全”。在实际接入时，应先限定一个测试目录、使用低权限账户，并观察拒绝访问越界文件与未授权网络的行为。这是**本包建议**，不是已运行的实验。

## Skills 的边界

NVIDIA Skills 的发布定位是教兼容智能体使用 CUDA-X 工具，以及 Broadcast、RTX Remix 和 Omniverse 等创作能力（F-025、F-042）。技能说明与可执行程序、驱动、应用许可证是不同对象。

使用某项技能前仍需核对被调用工具的安装、版本与权限；商用时另核应用自动化、模型使用/再分发及素材权利，付费不等于全部用途获准。技能能表达工作步骤，不代表每个步骤都可在当前设备执行，也不能替代质量验收。直播调整与录制片段批量处理是发布稿的示例场景，本文没有实装复现。

## PAIR 的拓扑

PAIR 的官方定位是让 RTX Spark 在家庭网络内向兼容 Windows、Linux、macOS 客户端提供推理，同时让其他 PC 保留资源用于创作和游戏（F-026~F-027）。可将其理解为“应用在客户端，模型服务在另一台本地设备”；这是从官方拓扑得到的**概念解释**，不是具体协议实现。

多设备意味着需要重新确认网络信任范围、客户端身份、服务端访问控制与并发配额。局域网传输也不是“数据始终留在同一台机器”。本包只读取 PAIR 定位页面，未读取完整认证、加密及端口文档，不填写猜测的 API 路径或安装命令。

| 使用意图 | 需要补证据的地方 |
|---|---|
| 私有代码助手 | 模型与工具实际流向、云回退关闭后的行为 |
| 多设备共享推理 | 客户端兼容版本、认证与传输策略、并发延迟 |
| 创作自动化 | 应用授权、技能版本、修改范围、人工确认与恢复路径 |
| 长期运行智能体 | 设备保活、休眠策略、资源竞争、更新后的回归 |

这些问题构成后续评估输入，不代表相关产品已经缺失这些能力。
