---
okf_version: "0.2"
type: index
title: "handy-n8n 章节信源登记"
sources: https://github.com/datawhalechina/handy-n8n
---

# 信源登记簿

本目录登记 handy-n8n 教程全部 6 章的信源信息。所有概念文档和示例文档的 `sources` 字段均指向 GitHub 源码仓库中的对应章节。

## 入门篇

* [C01 n8n 初识](c01-introduction.md) — n8n 定义、特点、应用场景、节点分类、与 dify/coze 对比。
* [C02 n8n 安装与配置](c02-installation.md) — 官方 SaaS、本地 PC Docker、云主机 Docker Compose、HuggingFace Space 四种部署方式。

## 基础篇

* [C03 n8n 基本概念](c03-basic-concepts.md) — 平台介绍、触发器节点（Manual/Schedule/Webhook/Chat）、核心节点（数据处理/控制流/HTTP）、代码节点（表达式/Code）。

## 进阶篇

* [C04 n8n 高阶用法](c04-advanced-usage.md) — 子工作流、错误处理、集群节点、Memory、RAG、Tools、MCP。
* [C05 n8n 社区节点与节点开发](c05-community-nodes.md) — 社区节点安装、TypeScript 自定义节点开发（高德地图天气示例）。

## 实战篇

* [C06 n8n 案例分享](c06-case-studies.md) — GitHub Trending 每日推送、GitHub Issue 飞书通知。

```{toctree}
:hidden:

c01-introduction
c02-installation
c03-basic-concepts
c04-advanced-usage
c05-community-nodes
c06-case-studies
```
