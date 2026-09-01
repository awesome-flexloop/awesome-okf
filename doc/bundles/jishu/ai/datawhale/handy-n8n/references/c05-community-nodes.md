---
type: reference
title: "C05 n8n 社区节点与节点开发"
bundle: /datawhale/handy-n8n
description: "社区节点安装方法、TypeScript 自定义节点开发全流程（声明式/程序式、节点类、鉴权类、本地调试），以高德地图天气 API 为例"
source: https://github.com/datawhalechina/handy-n8n/blob/main/c05/README.md
path: c05/README.md
tags: [community-nodes, custom-node, typescript, declarative, amap]
status: stable
---

# C05 n8n 社区节点与节点开发

## 信源信息

- **文件路径**：`c05/README.md`
- **GitHub**：https://github.com/datawhalechina/handy-n8n/blob/main/c05/README.md
- **sidebar 标题**：C05 - n8n 社区节点与节点开发

## 内容概要

本章介绍如何扩展 n8n 的节点生态：安装社区节点，以及开发自定义节点。

## 社区节点

- n8n 官方节点位于 [n8n 仓库 packages/nodes-base/nodes](https://github.com/n8n-io/n8n/tree/master/packages/nodes-base/nodes)
- 社区节点由社区成员开发维护，发布在 npm（关键字 `n8n-community-node-package`）
- 安装步骤：Settings → Community nodes → Install a community node → 填入 npm 包名（如 `n8n-nodes-text-manipulation`）→ 勾选风险 → Install
- 安装后在工作流节点面板中可搜索使用

## 自定义节点开发

以高德地图天气服务为贯穿案例，完整演示自定义节点开发流程。

### 准备工作
- 申请高德地图 API Key（Web 服务类型，每月 5000 次免费）
- 天气 API：`/v3/weather/weatherInfo`，参数 key/city/extensions/output
- 使用官方模板 [n8n-nodes-starter](https://github.com/n8n-io/n8n-nodes-starter/generate) 创建项目

### 两种开发风格
- **declarative-style（声明式）**：JSON 描述节点，适合 REST API，官方推荐
- **programmatic-style（程序式）**：代码实现逻辑，适合复杂 API

### 节点类（AMap.node.ts）
- 实现 `INodeType` 接口
- `description` 属性（`INodeTypeDescription`）包含：
  - 基本信息：displayName、name、icon、group、version、subtitle、description
  - 连接：inputs、outputs
  - 请求默认配置：`requestDefaults`（baseURL、qs）
  - 鉴权：`credentials` 数组
  - `properties`：resource（资源）+ operation（操作）+ 参数 + routing（请求逻辑）
- 使用表达式 `={{$parameter["city"]}}` 引用参数

### 鉴权类（AMapApi.credentials.ts）
- 实现 `ICredentialType` 接口
- `properties` 定义凭据字段（API Key，password 类型）
- `authenticate` 定义鉴权注入方式：支持 qs/auth/header/body 四种位置
- 高德使用 qs 方式注入 key 参数

### 节点描述文件（AMap.node.json）
- node、nodeVersion、codexVersion、categories、resources（文档链接）

### 本地测试
```bash
npm install n8n -g
npm run build
npm link
cd ~/.n8n/custom && npm init -y && npm link n8n-nodes-amap
n8n start
```

### 参考资源
- 完整项目：https://github.com/tomowang/n8n-nodes-amap
- npm 包：https://www.npmjs.com/package/n8n-nodes-amap
- 官方文档：节点结构对比、声明式节点、标准参数、routing 参数、本地测试

## 对应概念

- [高级实战](../concepts/advanced-practice.md)——社区节点与自定义节点开发
- [自定义高德地图天气节点示例](../examples/custom-amap-node.md)——完整实践
