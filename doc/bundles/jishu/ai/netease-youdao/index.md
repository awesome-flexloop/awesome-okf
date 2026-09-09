---
type: bundles-index
okf_version: "0.2"
scope: netease-youdao
title: "网易有道开源生态"
description: "网易有道开源生态知识包分组，收录 Embedding/RAG、语音合成、AI Agent 桌面应用、学术搜索等方向的 OKF 知识包。"
status: stable
---

# 网易有道开源生态知识库

本分组收录网易有道（NetEase Youdao）生态相关项目的 OKF 知识包。有道开源生态覆盖四个方向：**Embedding/RAG**（向量检索与检索增强生成）、**语音合成**（高保真与情感控制 TTS）、**AI Agent 桌面应用**（桌面级智能体框架）、**学术搜索**（面向科研文献的搜索 Agent 服务）。所有知识包遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)，通过 R→I→E→V→C 阶段链路生成。

## 知识包导航

| 知识包 | 简介 |
|--------|------|
| [bcembedding](bcembedding/) | BCEmbedding——双语 Embedding/Reranker 模型库（Apache-2.0） |
| [confucius4-tts](confucius4-tts/) | Confucius4-TTS——基于 LLM 的高保真 TTS（flow-matching + BigVGAN 声码器） |
| [emotivoice](emotivoice/) | EmotiVoice——多音色情感控制 TTS（v0.3） |
| [lobsterai](lobsterai/) | LobsterAI——Electron 桌面 AI Agent 应用（IM 网关 + MCP 运行时 + 技能系统） |
| [qanything](qanything/) | QAnything——本地知识库问答 RAG 系统（v2.0.0） |
| [scholarclaw](scholarclaw/) | ScholarClaw——学术搜索 Agent 服务（服务端 TS + shell 脚本） |

## 关于本分组

本分组 6 个知识包均基于 `vendor/netease-youdao/` 下固定的 git 子模块基线（详见各束 sources.md 登记），经 R（事实采集，共 344 条 F 编号事实）→ I（架构洞察，29 条）→ E（批量生成，60 篇内容文档）三阶段完成；V 阶段独立验证与 C 阶段模式沉淀随后执行。内容文档 frontmatter `type` 取值采用小写（`concept`/`example`），与仓库内其他分组大写先例并存——OKF v0.2 规范声明该取值大小写不敏感，本分组成员内部保持一致。

```{toctree}
:hidden:
:maxdepth: 7

bcembedding/index
confucius4-tts/index
emotivoice/index
lobsterai/index
qanything/index
scholarclaw/index
```
