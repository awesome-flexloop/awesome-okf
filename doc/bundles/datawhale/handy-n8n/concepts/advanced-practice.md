---
type: concept
title: "高级实战"
bundle: /datawhale/handy-n8n
description: "子工作流模块化、Error Trigger 错误处理、社区节点安装、TypeScript 自定义节点开发（声明式/程序式）、GitHub 实战案例"
sources: https://github.com/datawhalechina/handy-n8n/blob/main/c05/README.md
related:
  - /datawhale/handy-n8n/concepts/workflow-design
  - /datawhale/handy-n8n/concepts/data-processing
  - /datawhale/handy-n8n/concepts/ai-api-integration
  - /datawhale/handy-n8n/references/c04-advanced-usage
  - /datawhale/handy-n8n/references/c05-community-nodes
  - /datawhale/handy-n8n/references/c06-case-studies
tags: [sub-workflow, error-handling, custom-node, typescript, cases]
status: stable
---

# 高级实战

## 核心理解

当基础节点和 Code 节点无法满足需求时，n8n 提供三层高级能力：**子工作流**实现模块化复用，**错误处理**保障生产环境稳定性，**自定义节点开发**扩展 n8n 的能力边界。最终通过实战案例将这些能力整合为解决真实问题的工作流。

## 子工作流

子工作流将复杂任务分解为更小、可重用的部分，实现工作流的模块化。

### 调用机制
- **主工作流**使用 **Execute Workflow** 节点调用子工作流
- **子工作流**使用 **Execute Sub-Workflow Trigger** 节点（"When Executed by Another Workflow"）接收调用
- 支持参数传递：在子工作流触发器中定义接收参数，主工作流通过拖拽映射前序节点数据

### 使用模式
- 可创建独立子工作流，也可嵌入主工作流
- 子工作流可拥有独立的触发节点用于测试
- 执行日志中可分别查看主工作流和子工作流的执行记录

### 典型场景
- 可复用的计算逻辑（如课程中的计算器示例：加减乘除）
- 跨工作流共享的数据处理流程
- 将复杂工作流拆分为多个可维护的模块

## 错误处理

生产环境中的工作流必须考虑容错。n8n 使用独立的**错误处理工作流**机制。

### 配置步骤
1. 创建新工作流，选择 **Error Trigger** 作为触发节点（无配置项）
2. 添加后续处理节点（如 Email 发送错误通知、飞书/企微告警）
3. Error Trigger 输出错误上下文数据：触发错误的工作流名称、执行 URL 等，可通过表达式引用
4. 在需要容错的工作流中，Settings → Error Workflow 选择刚创建的错误处理工作流

### 通知配置
以邮件通知为例（网易邮箱 SMTP）：
- SMTP 服务器：`smtp.163.com`，端口：`465`
- 需在邮箱设置中开启 IMAP/SMTP 服务并生成授权码
- 授权码作为三方客户端密码使用

也可使用飞书、企业微信等通知服务替代邮件。

## 社区节点

n8n 社区贡献了大量第三方节点，发布在 npm 上。

### 安装方式
1. Settings → Community nodes → Install a community node
2. 在 [npm 搜索](https://www.npmjs.com/search?q=keywords%3An8n-community-node-package) 找到需要的包（关键字 `n8n-community-node-package`）
3. 填入 npm 包名（如 `n8n-nodes-text-manipulation`），勾选同意风险，点击 Install
4. 安装后在节点面板中即可搜索使用

### 官方节点 vs 社区节点
- 官方节点位于 [n8n 仓库](https://github.com/n8n-io/n8n/tree/master/packages/nodes-base/nodes)，由 n8n 团队维护
- 社区节点由社区成员开发维护，发布在 npm，安装时需注意安全风险

## 自定义节点开发

当官方和社区节点都不满足需求时，可使用 TypeScript 开发自定义节点。

### 开发风格

| 风格 | 描述 | 适用场景 |
|------|------|---------|
| **declarative-style（声明式）** | 使用 JSON 描述节点，官方推荐 | REST 风格 API |
| **programmatic-style（程序式）** | 使用代码实现节点逻辑 | 复杂逻辑 API |

### 项目结构
使用 [n8n-nodes-starter](https://github.com/n8n-io/n8n-nodes-starter/generate) 模板创建项目：

```
├── credentials/          # 鉴权类
│   └── ExampleCredentialsApi.credentials.ts
├── nodes/                # 节点类
│   └── ExampleNode/
│       ├── ExampleNode.node.ts
│       └── ExampleNode.node.json
├── package.json
└── tsconfig.json
```

### 节点类（INodeType）
实现 `INodeType` 接口，核心是 `description` 属性（`INodeTypeDescription`）：

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
    requestDefaults: {
      baseURL: 'https://restapi.amap.com/v3',
      qs: { output: 'JSON' },
    },
    credentials: [{ name: 'amapApi', required: true }],
    properties: [
      // resource + operation 定义
      // 参数配置
      // routing 请求逻辑
    ],
  };
}
```

关键设计：
- **resource**：资源定义（如 weather）
- **operation**：针对资源的操作（如 getWeather、getForecast）
- **routing**：操作对应的 HTTP 请求逻辑（method、url、qs）
- 参数通过 `displayOptions.show` 控制条件显示

### 鉴权类（ICredentialType）
实现 `ICredentialType` 接口：

```typescript
export class AMapApi implements ICredentialType {
  name = 'amapApi';
  displayName = 'AMap API';
  properties: INodeProperties[] = [
    { displayName: 'API Key', name: 'apiKey', type: 'string',
      typeOptions: { password: true }, default: '' },
  ];
  authenticate: IAuthenticateGeneric = {
    type: 'generic',
    properties: { qs: { key: '={{$credentials.apiKey}}' } },
  };
}
```

`authenticate` 支持多种鉴权参数位置：`qs`（查询参数）、`auth`（Basic Auth）、`header`（请求头）、`body`（请求体）。

### 节点描述文件（.node.json）
```json
{
  "node": "n8n-nodes-base.AMap",
  "nodeVersion": "1.0",
  "codexVersion": "1.0",
  "categories": ["Miscellaneous"],
  "resources": {
    "credentialDocumentation": [{ "url": "..." }],
    "primaryDocumentation": [{ "url": "..." }]
  }
}
```

### 本地测试流程
```bash
npm install n8n -g          # 安装 n8n
npm run build               # 编译自定义节点
npm link                    # 全局链接
cd ~/.n8n/custom            # n8n 自定义节点目录
npm init -y                 # 初始化（首次）
npm link n8n-nodes-amap     # 链接自定义节点
n8n start                   # 启动 n8n
```

## 实战案例

### GitHub Trending 每日推送
- **触发器**：Schedule Trigger（定时）
- **流程**：定时获取 GitHub Trending 数据 → 格式化 → 邮件发送
- **推广**：可替换信息源为 RSS 等，通知渠道替换为飞书/企微/Slack

### GitHub Issue 通知
- **触发器**：Webhook Trigger（监听 GitHub Issue 事件）
- **流程**：接收 GitHub Issue 事件 → 解析内容 → 飞书机器人发送通知
- **关键**：GitHub Webhook 配置指向 n8n Webhook URL

## 在 handy-n8n 中的位置

C04 的子工作流与错误处理子文档讲解模块化和容错，C05 完整教授社区节点安装和自定义节点开发（以高德地图天气服务为贯穿案例），C06 提供两个整合性实战案例。这三章共同构成"从会用到会造"的完整进阶路径。

## 延伸阅读

- [工作流设计](workflow-design.md)——节点编排基础
- [数据处理与转换](data-processing.md)——Code 节点能力
- [AI 与 API 集成](ai-api-integration.md)——AI 集群节点和 MCP
- [自定义高德地图天气节点](../examples/custom-amap-node.md)——C05 完整实践
- [GitHub Trending 每日推送](../examples/github-trending-digest.md)——C06 案例
- [GitHub Issue 飞书通知](../examples/github-issue-notify.md)——C06 案例
