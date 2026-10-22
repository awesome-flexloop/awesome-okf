---
okf_version: "0.2"
type: group
title: "🏗️ 基础设施即代码与云应用部署（iac）"
description: "基础设施即代码、云资源编排与应用部署框架的源码级与官方文档级教程；现有知识包为 SST 与微信云托管。"
---

# 🏗️ 基础设施即代码与云应用部署

本分组收录基础设施即代码（IaC）与云应用部署框架的结构化教程，关注配置模型、资源编排、运行时集成和开发/部署生命周期。

## 束清单

| Bundle | 简介 | 入口 |
|---|---|---|
| **sst** | SST v4.17.2 源码与官方文档教程：Go CLI、Pulumi 平台组件、provider、runtime、资源链接及 Live/Mosaic 开发边界 | [SST 教程](sst/index.md) |
| **wxcloudrun** | 微信云托管官方文档教程：环境—服务—版本—实例资源模型、发布单灰度回滚、callContainer 身份透传、微信生态集成、刊例价计费口径与安全迁移边界 | [微信云托管教程](wxcloudrun/index.md) |

```{toctree}
:hidden:
:maxdepth: 7

sst/index
wxcloudrun/index
```
