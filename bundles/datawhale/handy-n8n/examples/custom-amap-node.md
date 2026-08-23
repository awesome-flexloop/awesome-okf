---
type: example
title: "自定义高德地图天气节点"
bundle: /datawhale/handy-n8n
description: "C05 实践：使用 TypeScript 声明式模式开发 n8n 自定义节点，以高德地图天气 API 为例，含节点类、鉴权类、routing 配置和 npm link 本地调试全流程"
sources: https://github.com/datawhalechina/handy-n8n/blob/main/c05/README.md
related:
  - /datawhale/handy-n8n/concepts/advanced-practice
  - /datawhale/handy-n8n/concepts/data-processing
tags: [custom-node, typescript, declarative, amap, api]
status: stable
---

# 自定义高德地图天气节点

## 概述

本示例对应 handy-n8n 第五章，完整演示了如何使用 TypeScript 开发 n8n 自定义节点。以高德地图天气服务 API 为例，从 API Key 申请到节点开发、鉴权配置、本地测试的全流程。完整项目代码托管在 [github.com/tomowang/n8n-nodes-amap](https://github.com/tomowang/n8n-nodes-amap)，npm 包为 `n8n-nodes-amap`。

## 前置准备

### 申请高德地图 API Key
1. 注册高德开发者：https://console.amap.com/dev/id/phone
2. 创建应用，服务平台选择 **Web 服务**
3. 获取 API Key（每月 5000 次免费调用）
4. API 文档：https://lbs.amap.com/api/webservice/guide/api/weatherinfo

天气 API 参数：`key`（必填）、`city`（必填，adcode 城市编码）、`extensions`（base/all，实况/预报）、`output`（JSON/XML）。

## 项目创建

使用官方模板：
1. 访问 https://github.com/n8n-io/n8n-nodes-starter/generate
2. 命名为 `n8n-nodes-amap`，克隆到本地
3. 项目结构：
```
├── credentials/       # 鉴权类
├── nodes/             # 节点类
│   └── AMap/
│       ├── AMap.node.ts
│       ├── AMap.node.json
│       └── amap.svg
├── package.json
└── tsconfig.json
```

## 节点类实现（AMap.node.ts）

使用 **declarative-style（声明式模式）**，通过 JSON 描述节点，适合 REST API。

### 基本信息与 requestDefaults

```typescript
export class AMap implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'AMap高德地图',
    name: 'aMap',
    icon: 'file:amap.svg',
    group: ['input'],
    version: 1,
    subtitle: '={{$parameter["operation"]}}',
    description: 'Get information from AMap',
    inputs: [NodeConnectionType.Main],
    outputs: [NodeConnectionType.Main],
    defaults: { name: 'AMap高德地图' },
    requestDefaults: {
      baseURL: 'https://restapi.amap.com/v3',
      qs: { output: 'JSON' },
    },
    credentials: [{ name: 'amapApi', required: true }],
    properties: [ /* resource, operation, 参数, routing */ ],
  };
}
```

### Resource + Operation 定义

```typescript
properties: [
  {
    displayName: 'Resource',
    name: 'resource',
    type: 'options',
    default: 'weather',
    noDataExpression: true,
    options: [{ name: '天气', value: 'weather' }],
  },
  {
    displayName: 'Operation',
    name: 'operation',
    type: 'options',
    default: 'getWeather',
    noDataExpression: true,
    options: [
      { name: '获取实况天气', value: 'getWeather', action: '获取实况天气' },
      { name: '获取预报天气', value: 'getForecast', action: '获取预报天气' },
    ],
  },
  // 城市编码参数
  {
    displayName: '城市编码',
    name: 'city',
    type: 'string',
    default: '110000',
    required: true,
    displayOptions: { show: { resource: ['weather'] } },
  },
]
```

### Routing 请求逻辑

```typescript
routing: {
  request: {
    method: 'GET',
    url: '/weather/weatherInfo',
    qs: {
      city: '={{$parameter["city"]}}',
      extensions: 'all',
    },
  },
}
```

`routing` 将 operation 映射到具体的 HTTP 请求，表达式 `{{$parameter["city"]}}` 引用用户配置的参数。

## 鉴权类实现（AMapApi.credentials.ts）

```typescript
export class AMapApi implements ICredentialType {
  name = 'amapApi';
  displayName = 'AMap API';
  documentationUrl = 'https://lbs.amap.com/api/webservice/create-project-and-key';
  properties: INodeProperties[] = [
    {
      displayName: 'API Key',
      name: 'apiKey',
      type: 'string',
      typeOptions: { password: true },
      default: '',
    },
  ];
  authenticate: IAuthenticateGeneric = {
    type: 'generic',
    properties: {
      qs: { key: '={{$credentials.apiKey}}' },
    },
  };
}
```

`authenticate` 将 API Key 自动注入请求查询参数。n8n 支持多种鉴权位置：
- `qs`：URL 查询参数
- `header`：HTTP 请求头
- `auth`：Basic Auth
- `body`：请求体

## 节点描述文件（AMap.node.json）

```json
{
  "node": "n8n-nodes-base.AMap",
  "nodeVersion": "1.0",
  "codexVersion": "1.0",
  "categories": ["Miscellaneous"],
  "resources": {
    "credentialDocumentation": [{ "url": "https://lbs.amap.com/api/webservice/create-project-and-key" }],
    "primaryDocumentation": [{ "url": "https://lbs.amap.com/api/webservice/summary" }]
  }
}
```

## 本地测试流程

```bash
# 1. 全局安装 n8n
npm install n8n -g

# 2. 编译自定义节点
cd n8n-nodes-amap
npm run build

# 3. 全局链接
npm link

# 4. 在 n8n 自定义目录中链接
cd ~/.n8n/custom
npm init -y          # 首次需要
npm link n8n-nodes-amap

# 5. 启动 n8n
n8n start
```

启动后在节点面板搜索 "amap" 即可找到自定义节点，配置 API Key 后选择"获取实况天气"操作，点击运行查看天气数据输出。

## 开发要点

1. **声明式优先**：REST API 场景优先使用 declarative-style，JSON 描述即可，无需写请求代码
2. **Resource/Operation 模式**：沿用 RESTful 理念，resource 定义资源，operation 定义操作
3. **displayOptions**：控制参数的条件显示，根据 resource/operation 动态展示
4. **subtitle 表达式**：`'={{$parameter["operation"]}}'` 让节点标题动态显示当前操作
5. **凭据安全**：`typeOptions: { password: true }` 确保 API Key 不明文显示

## 延伸阅读

- [高级实战](../concepts/advanced-practice.md)——子工作流、错误处理、自定义节点完整概念
- [数据处理与转换](../concepts/data-processing.md)——Code 节点与表达式
- [C05 社区节点与节点开发](../references/c05-community-nodes.md)——完整信源
- [n8n 官方节点开发文档](https://docs.n8n.io/integrations/creating-nodes/)
