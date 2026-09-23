---
type: bundles-index
okf_version: "0.2"
scope: tencent
title: "腾讯开源生态"
description: "腾讯开源生态知识包分组，收录 CodeBuddy 产品矩阵、WorkBuddy/CloudStudio 沙箱端点等腾讯系开源与商业项目的 OKF 知识包。"
status: stable
---

# 腾讯开源生态知识库

本分组收录腾讯（Tencent）生态相关项目的 OKF 知识包，涵盖 AI 编程工具、开源基础设施等方向。所有知识包遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)，通过 R→I→E→V→C 阶段链路生成。

## 知识包导航

| 知识包 | 简介 |
|--------|------|
| [codebuddy](codebuddy/index.md) | CodeBuddy 产品矩阵——IDE/插件/CLI 三态一体 AI 编程工具，NPC 云端 AI 员工、WorkBuddy 在线助手、Security 安全审计，含 6 概念 + 2 示例 + 6 信源 |
| [workbuddy-sandbox-public-endpoint](workbuddy-sandbox-public-endpoint/index.md) | WorkBuddy/CloudStudio 沙箱公网 HTTPS 端点核验——CloudStudio Gateway 实证、域名后缀漂移、临时 Demo/Webhook/Agent API 边界，含 3 概念 + 2 信源 |
| [ai-infra-guard](ai-infra-guard/index.md) | 腾讯朱雀实验室 AI 红队平台——Go+Python 分布式 Server-Agent 架构，五种任务类型（AI 基础设施扫描/MCP 扫描/大模型安全体检/Agent 扫描/Skill 安全扫描），自研指纹 DSL，2000+ CVE 规则，含 7 概念 + 3 示例 + 5 信源 |
| [octop](octop/index.md) | WorkBuddy/Octop 自托管多用户 AI 助手——Python 3.12+ 四层架构，OctopServer 编排器、AgentManager、Gateway 多通道、DI 容器、ACP 双向集成、20 CLI 子命令，基于 harness-agent 运行时，含 7 概念 + 3 示例 + 6 信源 |
| [ncnn](ncnn/index.md) | 腾讯优图实验室高性能神经网络推理框架——纯 C++ 零依赖，CPU/Vulkan 双后端，Mat 引用计数张量、Layer 算子抽象、PoolAllocator 内存池、全架构 SIMD 优化（x86/ARM/MIPS/RISC-V/LoongArch）、Python 绑定，含 12 概念 + 4 示例 + 6 信源 |
| [weknora](weknora/index.md) | 腾讯开源 WeKnora 技术综述——AI、数据接入、知识管理三项基础，RAG/Agent/Wiki 组合机制与开源知识库选型维度，含 3 概念 + 2 信源 |
| [tencent-buddy-family](tencent-buddy-family/index.md) | 腾讯 Buddy 系列与 MusicBuddy 产品观察——Buddy AI 统称、WorkBuddy/CodeBuddy/DataBuddy 场景矩阵、腾讯音乐 AI 能力背景与证据边界，非操作教程 |

## 生态项目

除上述知识包外，腾讯开源生态还包含以下项目（暂不建束，仅作导航参考）：

- **OpenSourceTalent（犀牛鸟开源人才计划）**——腾讯发起的开源人才培养生态项目，连接高校学生与开源社区，推动开源贡献与人才成长。作为生态人才项目登记于此，不单独建立知识包。

## 关于本分组

本分组当前包含 7 个已生成知识包，共 41 个概念文档、12 个示例文档、29 个信源登记，基于 2026-08-23 的源码阅读、网页抓取与 2026-09-23 的博文核验生成，总计 470 条编号事实（原有 445 条 + Buddy 25 条）。所有源码知识包均经过 Grep 级 API 真实性验证，博文转化束经过 P0/P1 权威核验。

## 相关链接

- [CodeBuddy 知识包](codebuddy/index.md) — CodeBuddy 产品矩阵完整知识库
- [WorkBuddy 沙箱公网端点](workbuddy-sandbox-public-endpoint/index.md) — 临时 HTTPS 公网入口、域名漂移与生产边界核验
- [AI-Infra-Guard 知识包](ai-infra-guard/index.md) — AI 红队平台源码教程
- [Octop 知识包](octop/index.md) — 自托管 AI 助手源码教程
- [ncnn 知识包](ncnn/index.md) — 神经网络推理框架源码教程
- [CodeBuddy 官网](https://www.codebuddy.cn/) — CodeBuddy 产品入口
- [腾讯开源](https://opensource.tencent.com/) — 腾讯开源项目总览

```{toctree}
:hidden:
:maxdepth: 7

codebuddy/index
workbuddy-sandbox-public-endpoint/index
ai-infra-guard/index
octop/index
ncnn/index
weknora/index
tencent-buddy-family/index
```
