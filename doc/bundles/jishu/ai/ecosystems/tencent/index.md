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
| [workbuddy-sandbox-public-endpoint](workbuddy-sandbox-public-endpoint/index.md) | WorkBuddy/CloudStudio 沙箱公网 HTTPS 端点核验——CloudStudio Gateway 实证、域名后缀漂移、临时 Demo/Webhook/Agent API 边界，含 4 概念 + 2 信源 |
| [ai-infra-guard](ai-infra-guard/index.md) | 腾讯朱雀实验室 AI 红队平台——Go+Python 分布式 Server-Agent 架构，五种任务类型（AI 基础设施扫描/MCP 扫描/大模型安全体检/Agent 扫描/Skill 安全扫描），自研指纹 DSL，2000+ CVE 规则，含 7 概念 + 3 示例 + 5 信源 |
| [octop](octop/index.md) | WorkBuddy/Octop 自托管多用户多 Agent AI 助手——Python 3.12+ 四层架构，1.0 系列品牌独立（octop-harness/memory/gateway/browser>=1.0.0，schema v19），OctopServer 17 步装配/25 Repo、25 连接器 MCP 三模式网关、每库 SQLite RAG、专家团队主持人剥权、Octop↔Octop 联邦桥接、history v2 内容寻址、26 权限 RBAC+SSO/验证码、60 router 挂载/CLI 22 命令、Docker/Wails/FnOS 多形态部署；v0.9.25→v1.0.2b5 双版本口径并存，含 22 概念 + 8 示例 + 10 信源、592 条编号事实与 15 条洞察（v1.0.2b5 commit e473dd3c） |
| [ncnn](ncnn/index.md) | 腾讯优图实验室高性能神经网络推理框架——纯 C++ 零依赖，CPU/Vulkan 双后端，Mat 引用计数张量、Layer 算子抽象、PoolAllocator 内存池、全架构 SIMD 优化（x86/ARM/MIPS/RISC-V/LoongArch）、Python 绑定，含 12 概念 + 4 示例 + 6 信源 |
| [weknora](weknora/index.md) | 腾讯开源 WeKnora 技术综述——AI、数据接入、知识管理三项基础，RAG/Agent/Wiki 组合机制与开源知识库选型维度，含 3 概念 + 2 信源 |
| [tencent-buddy-family](tencent-buddy-family/index.md) | 腾讯 Buddy 系列与 MusicBuddy 产品观察——Buddy AI 统称、WorkBuddy/CodeBuddy/DataBuddy 场景矩阵、腾讯音乐 AI 能力背景与证据边界，非操作教程 |
| [workbuddy-one-sentence-mvp](workbuddy-one-sentence-mvp/index.md) | WorkBuddy「一句话做 MVP」实测软文核验——需求澄清/多 Agent 迭代/用户画像/连接器/微信小程序发布五阶段拆解，沙利文双榜与 5.6.1 小程序发布能力核验（6✅/2⚠️/0❌），含 3 概念 + 2 信源，非操作教程 |
| [lightvela-personal-agent](lightvela-personal-agent/index.md) | LightVela 与 Personal Agent 赛道观察——腾讯轻量云托管开源 Hermes Agent、微信/QQ/企微/飞书/钉钉五通道，对标 Meta Muse；事实/机制/Context 锁定论点三层拆解，含 3 概念 + 2 信源、62 条编号事实与 5 处口径勘误，非操作教程 |
| [tencent-meeting-cli](tencent-meeting-cli/index.md) | 腾讯会议官方 CLI（tmeet）v1.0.18——CLI + CLI-Skill 双件架构、OAuth2 设备码授权、10 命令域 44 子命令、录制与元宝双纪要体系、Agent 安全契约、per-host 实时事件总线；含 14 概念（9 用户面 + 5 源码内部机制）+ 4 示例 + 8 信源、199 条编号事实（含腾讯文档用户手册、19→44 命令跨版本比对与 v1.0.18 固定 tag 源码 F-113~F-199） |
| [tencentdb-agent-memory](tencentdb-agent-memory/index.md) | TencentDB Agent Memory 源码学习（commit 8b86874 截面）——MemoryCore/Knowledge/Panel/Proxy 四件架构，L0-L3 跨会话沉淀与 offload 上下文压缩双管线，Skill/Wiki/CodeGraph 资产，v3 三元组强隔离，双协议代理零插件接入；含 13 概念 + 4 示例 + 5 信源、300 条编号事实与 6 条四元组洞察 |

## 生态项目

除上述知识包外，腾讯开源生态还包含以下项目（暂不建束，仅作导航参考）：

- **OpenSourceTalent（犀牛鸟开源人才计划）**——腾讯发起的开源人才培养生态项目，连接高校学生与开源社区，推动开源贡献与人才成长。作为生态人才项目登记于此，不单独建立知识包。

## 关于本分组

本分组当前包含 11 个已生成知识包，共 90 个概念文档、25 个示例文档、50 个信源登记，基于 2026-08-23 的源码阅读、网页抓取、2026-09-23 与 2026-09-28 的博文核验、2026-10-03 的官方文档与腾讯文档用户手册学习、2026-10-04 的腾讯会议 CLI v1.0.18 固定 tag 源码主体学习、TencentDB Agent Memory（commit 8b86874，feat/server_team 分支）源码学习与 Octop v1.0.2b5（commit e473dd3c，新信源 external/dao/runtime/tencent/Octop/）固定 tag 增量学习生成，总计 1522 条编号事实（原有 763 条 + TencentDB Agent Memory 300 条 + Octop v1.0.2b5 增量 459 条；概念数含 workbuddy-sandbox 横向对标增强后补登的 1 篇、tencent-meeting-cli v0.3.0 源码概念 5 篇与 Octop v1.0.2b5 增量 15 篇 07-21）。所有源码知识包均经过 Grep 级 API 真实性验证，博文转化束经过 P0/P1 权威核验。

## 相关链接

- [WorkBuddy 一句话做 MVP](workbuddy-one-sentence-mvp/index.md) — 实测软文五阶段拆解、沙利文双榜与小程序发布能力核验
- [CodeBuddy 知识包](codebuddy/index.md) — CodeBuddy 产品矩阵完整知识库
- [WorkBuddy 沙箱公网端点](workbuddy-sandbox-public-endpoint/index.md) — 临时 HTTPS 公网入口、域名漂移与生产边界核验
- [AI-Infra-Guard 知识包](ai-infra-guard/index.md) — AI 红队平台源码教程
- [Octop 知识包](octop/index.md) — 自托管 AI 助手源码教程
- [ncnn 知识包](ncnn/index.md) — 神经网络推理框架源码教程
- [腾讯会议 CLI 知识包](tencent-meeting-cli/index.md) — 腾讯会议官方 CLI 完整使用教程（v1.0.18）
- [TencentDB Agent Memory 知识包](tencentdb-agent-memory/index.md) — 四件架构记忆系统源码教程（commit 8b86874 截面）
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
workbuddy-one-sentence-mvp/index
lightvela-personal-agent/index
tencent-meeting-cli/index
tencentdb-agent-memory/index
```
