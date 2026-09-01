---
okf_version: "0.2"
type: example
title: 配置网关渠道
description: 配置飞书/微信/飞书CLI等IM网关渠道，设置认证凭据、群组策略、权限模式，通过PlatformAdapter实现自定义平台接入
tags: [zleap-agent, example, gateway, feishu, wechat, im, platform-adapter, integration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/gateway-multi-platform.md
  - /concepts/agent-core-loop.md
  - /concepts/tool-approval-policy.md
sources:
  - id: zleap-agent-self
    resource: /references/zleap-agent-sources.md
    title: Zleap-Agent 源码参考
---

# 配置网关渠道

## 场景说明

本示例演示如何配置 Zleap Agent 的 IM 网关渠道，包括飞书（Feishu/Lark）、微信（WeChat iLink Bot）和飞书 CLI 三种内置渠道。网关负责将 IM 平台的消息转换为 Zleap 的入站消息格式，驱动 Agent 执行，再将回复发送回 IM 平台。同时演示如何通过 `PlatformAdapter` 接口实现自定义平台接入。

**前置条件**：
- 已完成 Zleap Agent 安装配置（参见 [安装配置 Zleap Agent](setup-zleap-agent.md)）
- PostgreSQL 数据库已启动并可连接
- 拥有飞书/微信开发者账号和应用凭据
- Node.js ≥ 22，已构建所有包（`pnpm build`）

## 完整代码示例

### 示例 1：通过环境变量配置飞书渠道

```bash
# .env.local 或 ~/.zleap/.env — 飞书渠道配置

# --- 飞书应用凭据（必填）---
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_DOMAIN=feishu          # 国内版填 'feishu'，国际版 Lark 填 'lark'

# --- 事件回调安全（可选，用于 Webhook 模式验证）---
FEISHU_ENCRYPT_KEY=
FEISHU_VERIFICATION_TOKEN=

# --- 群组策略 ---
FEISHU_GROUP_POLICY=open      # open | allowlist | blacklist | admin_only | disabled
FEISHU_ALLOWED_USERS=ou_xxxxxxxxx,ou_yyyyyyyyy  # allowlist/blacklist 时的用户列表

# --- 权限模式 ---
FEISHU_PERMISSION_MODE=request_approval  # request_approval（默认，安全）| full_access

# --- Bot 信息（可选，首次连接后自动获取）---
FEISHU_BOT_OPEN_ID=
FEISHU_BOT_USER_ID=
FEISHU_BOT_NAME=Zleap助手
```

启动网关服务：

```bash
# 方式 A：使用 Docker Compose 启动网关
docker compose --profile gateway up -d

# 方式 B：开发模式启动网关
pnpm dev:gateway

# 方式 C：通过 CLI 连接飞书渠道
pnpm cli serve --gateway
# 然后在另一个终端：
pnpm cli connect feishu
```

### 示例 2：通过代码加载和解析飞书配置

```typescript
// examples/gateway-feishu-config.ts
// 演示：通过代码加载飞书配置

import {
  loadFeishuConfig,
  resolveFeishuConfig,
  feishuConfigFromRecord,
  type FeishuConfig,
  type GroupPolicy,
  type GatewayPermissionMode,
} from '@zleap/gateway/config';

// ── 方式 A：从环境变量加载 ──
const envConfig = loadFeishuConfig(process.env);

if (envConfig) {
  console.log('=== 从环境变量加载的飞书配置 ===');
  console.log(`App ID: ${envConfig.appId}`);
  console.log(`App Secret: ${envConfig.appSecret.slice(0, 4)}***`);
  console.log(`域名: ${envConfig.domain}`);
  console.log(`群组策略: ${envConfig.groupPolicy}`);
  console.log(`允许用户: ${envConfig.allowedUsers.join(', ') || '(无限制)'}`);
  console.log(`权限模式: ${envConfig.permissionMode}`);
} else {
  console.log('未检测到飞书凭据（FEISHU_APP_ID / FEISHU_APP_SECRET 未设置）');
}

// ── 方式 B：从数据库记录构建配置 ──
// Web UI 保存的配置存储在数据库 integrations 表中
const dbRecord = {
  config: {
    appId: 'cli_xxxxxxxxxxxxxxxx',
    appSecret: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    domain: 'feishu',
    groupPolicy: 'allowlist',
    allowedUsers: ['ou_xxxxxxxxx'],
    permissionMode: 'request_approval',
    encryptKey: '',
    verificationToken: '',
    botName: 'Zleap助手',
  },
};

const dbConfig = feishuConfigFromRecord(dbRecord.config);
if (dbConfig) {
  console.log('\n=== 从数据库加载的飞书配置 ===');
  console.log(`App ID: ${dbConfig.appId}`);
  console.log(`群组策略: ${dbConfig.groupPolicy}`);
  console.log(`允许用户数: ${dbConfig.allowedUsers.length}`);
}

// ── 方式 C：数据优先解析（DB > ENV 降级）──
// 模拟一个 store 实现
const mockStore = {
  integrations: {
    async getIntegration(channel: string) {
      // 实际实现会查询数据库
      if (channel === 'feishu') {
        return dbRecord;
      }
      return undefined;
    },
  },
};

async function demoResolveConfig() {
  // resolveFeishuConfig 优先使用数据库配置，失败时降级到环境变量
  const resolved = await resolveFeishuConfig(mockStore);
  if (resolved) {
    console.log('\n=== 数据优先解析结果 ===');
    console.log(`配置来源: 数据库优先`);
    console.log(`最终 App ID: ${resolved.appId}`);
    console.log(`最终群组策略: ${resolved.groupPolicy}`);
  }
}

await demoResolveConfig();
```

### 示例 3：配置微信渠道

```bash
# .env.local — 微信渠道配置

# --- 启用微信渠道 ---
WECHAT_ENABLED=true

# --- iLink 协议配置（通常不需要修改）---
WECHAT_BASE_URL=                    # 默认使用内置 iLink 端点
WECHAT_BOT_TYPE=                    # 默认 bot 类型
WECHAT_CHANNEL_VERSION=             # 默认协议版本

# --- 群组策略 ---
WECHAT_GROUP_POLICY=admin_only      # 微信推荐使用 admin_only 策略
WECHAT_ALLOWED_USERS=wxid_xxxxxxxxx

# --- 权限模式 ---
WECHAT_PERMISSION_MODE=request_approval
```

```typescript
// examples/gateway-wechat-config.ts
// 演示：加载微信配置

import { loadWeChatConfig, resolveWeChatConfig, type WeChatConfig } from '@zleap/gateway/config';

// 微信渠道使用扫码登录，不需要 appId/appSecret
const wechatConfig = loadWeChatConfig(process.env);

if (wechatConfig) {
  console.log('=== 微信渠道配置 ===');
  console.log(`已启用: ${wechatConfig.enabled}`);
  console.log(`iLink Base URL: ${wechatConfig.baseUrl}`);
  console.log(`Bot Type: ${wechatConfig.botType}`);
  console.log(`协议版本: ${wechatConfig.channelVersion}`);
  console.log(`群组策略: ${wechatConfig.groupPolicy}`);
  console.log(`权限模式: ${wechatConfig.permissionMode}`);
} else {
  console.log('微信渠道未启用（设置 WECHAT_ENABLED=true 来启用）');
}
```

### 示例 4：配置飞书 CLI 渠道

飞书 CLI 渠道通过官方 `@larksuite/cli`（lark-cli）作为子进程驱动，使用 OAuth 设备码流认证：

```bash
# .env.local — 飞书 CLI 渠道配置

FEISHU_CLI_ENABLED=true
FEISHU_CLI_IDENTITY=user          # user（OAuth 用户身份）| bot
FEISHU_CLI_DOMAIN=feishu
FEISHU_CLI_GROUP_POLICY=disabled  # CLI 渠道默认禁用群聊
FEISHU_CLI_PERMISSION_MODE=request_approval

# 可选：预置 App ID/Secret 用于非交互式 init
FEISHU_CLI_APP_ID=
FEISHU_CLI_APP_SECRET=

# 可选：lark-cli 二进制路径
FEISHU_CLI_BIN=lark-cli

# 可选：CLI 凭据隔离目录（Docker 部署时持久化）
FEISHU_CLI_HOME=
```

### 示例 5：使用 GatewayRunner 连接渠道

```typescript
// examples/gateway-runner.ts
// 演示：通过代码启动网关并连接平台适配器

import { GatewayRunner } from '@zleap/gateway/runner';
import { FeishuAdapter } from '@zleap/gateway/platforms/feishu';
import { WeChatAdapter } from '@zleap/gateway/platforms/wechat';
import type { PlatformAdapter, GatewayLogger } from '@zleap/gateway/types';
import type { ConversationService } from '@zleap/agent/conversation';
import { localDevActorContext } from '@zleap/core';

// ── 步骤 1：创建 Logger ──
const logger: GatewayLogger = {
  info: (msg, meta) => console.log(`[INFO] [gateway] ${msg}`, meta ?? ''),
  warn: (msg, meta) => console.warn(`[WARN] [gateway] ${msg}`, meta ?? ''),
  error: (msg, meta) => console.error(`[ERROR] [gateway] ${msg}`, meta ?? ''),
};

// ── 步骤 2：初始化 GatewayRunner ──
// 注意：实际使用时需要先构建 ConversationService
// 这里展示类型签名和使用方式
declare const conversationService: ConversationService;

const runner = new GatewayRunner({
  service: conversationService,
  logger,
  actor: localDevActorContext(),  // 网关流量使用本地开发者身份
  handleOptions: {
    // 可以传入全局 handle 选项，如 targetSpace 等
  },
});

// ── 步骤 3：设置渠道权限策略 ──
runner.setPermission('feishu', 'request_approval');  // 飞书：需审批
runner.setPermission('wechat', 'full_access');       // 微信：完全访问（谨慎使用！）

// ── 步骤 4：创建并附加适配器 ──
async function startGateway() {
  const adapters: PlatformAdapter[] = [
    new FeishuAdapter({
      config: {
        appId: process.env.FEISHU_APP_ID!,
        appSecret: process.env.FEISHU_APP_SECRET!,
        domain: 'feishu',
        groupPolicy: 'open',
        allowedUsers: [],
        permissionMode: 'request_approval',
      },
      logger,
    }),
    // 微信适配器需要扫码登录，配置不同
    // new WeChatAdapter({ ... }),
  ];

  for (const adapter of adapters) {
    await runner.attach(adapter);
    logger.info(`渠道已连接: ${adapter.channel}`);
  }

  logger.info('网关启动完成，等待消息...');
}

// ── 步骤 5：优雅关闭 ──
async function stopGateway(adapters: PlatformAdapter[]) {
  for (const adapter of adapters) {
    await runner.detach(adapter);
  }
  logger.info('网关已停止');
}
```

### 示例 6：实现自定义 PlatformAdapter

```typescript
// examples/custom-platform-adapter.ts
// 演示：实现一个自定义 IM 平台适配器

import type {
  PlatformAdapter,
  PlatformMessageEvent,
  MessageHandler,
  OutboundTarget,
  ChatType,
} from '@zleap/gateway/types';
import type { SendResult } from '@zleap/core';

// 自定义平台适配器必须实现 PlatformAdapter 接口
class CustomSlackAdapter implements PlatformAdapter {
  readonly channel = 'slack';  // 渠道唯一标识

  private messageHandler?: MessageHandler;
  private connected = false;

  constructor(
    private readonly config: {
      botToken: string;
      signingSecret: string;
      appToken?: string;  // Socket Mode 所需
    },
    private readonly logger?: { info: (msg: string) => void; error: (msg: string) => void },
  ) {}

  // 注册消息处理器（由 GatewayRunner 调用）
  setMessageHandler(handler: MessageHandler): void {
    this.messageHandler = handler;
  }

  // 连接到平台（WebSocket 长连接或 Webhook 服务启动）
  async connect(): Promise<void> {
    this.logger?.info(`[${this.channel}] 正在连接...`);

    // 实际实现中：
    // 1. 建立到 Slack API 的 WebSocket 连接（Socket Mode）
    // 2. 或启动 HTTP 服务器接收 Events API 回调
    // 3. 验证凭据并获取 bot 信息

    this.connected = true;
    this.logger?.info(`[${this.channel}] 已连接`);

    // 模拟消息接收（实际中由平台 SDK 触发）
    this.startListening();
  }

  // 断开连接
  async disconnect(): Promise<void> {
    this.connected = false;
    this.logger?.info(`[${this.channel}] 已断开`);
  }

  // 发送消息到平台
  async send(target: OutboundTarget, content: string): Promise<SendResult> {
    if (!this.connected) {
      return { ok: false, error: 'Not connected' };
    }

    try {
      // 实际实现中调用 Slack API 发送消息
      // await slack.client.chat.postMessage({
      //   channel: target.conversationId,
      //   text: content,
      //   ...(target.replyTo ? { thread_ts: target.replyTo } : {}),
      // });

      this.logger?.info(`[${this.channel}] 消息已发送到 ${target.conversationId}`);
      return { ok: true };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return { ok: false, error: message };
    }
  }

  // 可选：消息确认（如添加 emoji 反应）
  async ack?(event: PlatformMessageEvent): Promise<void> {
    // 实际实现中添加一个 "眼睛" emoji 表示"已读"
  }

  // 可选：重新认证
  async reauth?(): Promise<void> {
    // 刷新 OAuth token 或重新连接 WebSocket
  }

  // 可选：登出并清除凭据
  async logout?(): Promise<void> {
    await this.disconnect();
    // 清除存储的 token
  }

  // 将平台原生消息转换为标准化 PlatformMessageEvent
  private handleIncomingMessage(rawMessage: {
    channelId: string;
    userId: string;
    text: string;
    messageId: string;
    chatType: 'im' | 'channel';
    mentionsBot?: boolean;
  }): void {
    if (!this.messageHandler) return;

    const event: PlatformMessageEvent = {
      channel: this.channel,
      conversationId: rawMessage.channelId,
      chatType: rawMessage.chatType === 'im' ? 'p2p' : 'group',
      text: rawMessage.text,
      userId: rawMessage.userId,
      messageId: rawMessage.messageId,
      mentionsBot: rawMessage.mentionsBot,
      raw: rawMessage,
    };

    // 异步调用 handler（不阻塞消息接收）
    this.messageHandler(event).catch((error) => {
      this.logger?.error(`[${this.channel}] 消息处理失败: ${error}`);
    });
  }

  private startListening(): void {
    // 实际实现中订阅平台消息事件
    // 这里仅作为示意
  }
}

// 使用自定义适配器
async function useCustomAdapter() {
  const slackAdapter = new CustomSlackAdapter({
    botToken: 'xoxb-xxxxxxxxx',
    signingSecret: 'xxxxxxxxxx',
  });

  // 注册到 GatewayRunner（同示例 5）
  // await runner.attach(slackAdapter);
  console.log('自定义 SlackAdapter 已创建，channel =', slackAdapter.channel);
}
```

### 示例 7：群组策略与权限模式详解

```typescript
// examples/gateway-policies.ts
// 演示：不同群组策略和权限模式的效果

// ── 群组策略（GroupPolicy）──
// 'open'       : 所有人都可以与 Bot 对话（默认）
// 'allowlist'  : 仅 FEISHU_ALLOWED_USERS 列表中的用户可以使用
// 'blacklist'  : FEISHU_ALLOWED_USERS 列表中的用户被禁止使用
// 'admin_only' : 仅管理员可以使用
// 'disabled'   : 完全禁用该渠道的群聊功能（仅私聊可用）

// ── 权限模式（GatewayPermissionMode）──
// 'request_approval'（默认，安全）:
//   - 自动批准无风险工具（如读文件、搜索）
//   - 需要人工审批的工具直接拒绝（IM 没有交互式审批界面）
//   - 推荐用于所有 IM 渠道
//
// 'full_access'（完全访问，危险）:
//   - 自动批准所有工具，包括 run_command、write_file 等危险操作
//   - 仅在完全受控的内部环境中使用
//   - 配合严格的群组策略（如 admin_only）降低风险

// 推荐配置组合：
const recommendedConfigs = {
  // 企业内部飞书（受信任用户群）
  internalFeishu: {
    groupPolicy: 'open' as const,
    permissionMode: 'request_approval' as const,
  },
  // 外部/公开微信群
  externalWeChat: {
    groupPolicy: 'admin_only' as const,
    permissionMode: 'request_approval' as const,
  },
  // 个人飞书 CLI（用户自己的账号）
  personalCli: {
    groupPolicy: 'disabled' as const,  // CLI 不进群
    permissionMode: 'full_access' as const,  // 个人使用可放宽
  },
};

console.log('=== 推荐网关配置 ===');
for (const [name, config] of Object.entries(recommendedConfigs)) {
  console.log(`${name}:`);
  console.log(`  群组策略: ${config.groupPolicy}`);
  console.log(`  权限模式: ${config.permissionMode}`);
}
```

## 逐步解释

### 1. 配置加载优先级

每个渠道的配置都遵循**数据优先**（data-first）原则：
1. 首先尝试从数据库 `integrations` 表读取（通过 Web UI 保存的配置）
2. 如果数据库读取失败或没有配置，降级到环境变量
3. 环境变量也未配置时，该渠道不启用

这种设计确保：
- 普通用户通过 Web UI 配置即可，无需编辑文件
- 运维部署可以通过环境变量快速配置
- DB 不可用时网关仍能通过环境变量启动

### 2. PlatformAdapter 接口

每个 IM 平台通过 `PlatformAdapter` 接口接入：

```typescript
interface PlatformAdapter {
  readonly channel: string;           // 渠道 ID（如 'feishu', 'wechat'）
  setMessageHandler(handler): void;   // 注册消息回调
  connect(): Promise<void>;           // 连接平台
  disconnect(): Promise<void>;        // 断开连接
  send(target, content): Promise<SendResult>;  // 发送消息
  ack?(event): Promise<void>;         // 可选：消息确认
  reauth?(): Promise<void>;           // 可选：重新认证
  logout?(): Promise<void>;           // 可选：登出
}
```

适配器只负责**协议转换**：将平台原生消息转为 `PlatformMessageEvent`，将 Zleap 的回复转为平台 API 调用。它不包含任何 Agent 逻辑。

### 3. GatewayRunner 工作流程

`GatewayRunner` 是适配器和 Agent 之间的桥梁：

1. **attach(adapter)**：注册适配器的 outbound sender，设置消息 handler，调用 `adapter.connect()`
2. **消息接收**：适配器收到消息后调用 `onEvent()`，将 `PlatformMessageEvent` 转为 `InboundMessage`
3. **Agent 执行**：调用 `conversationService.run(inbound, options)` 驱动 Agent
4. **回复发送**：将 Agent 的文本回复通过 `adapter.send()` 发回平台
5. **错误处理**：执行失败时发送错误提示消息，不让用户"无响应"

关键设计：
- 入站消息统一转为 `InboundMessage`（kind: 'im'），与 Web UI 的消息格式一致
- 网关流量默认使用 `localDevActorContext()` 身份（与 Web UI 共享记忆/任务/审批范围）
- 每个渠道有独立的工具审批策略（`setPermission()`）

### 4. 入站消息转换

`toInbound()` 函数将平台事件转换为标准入站消息：

```typescript
function toInbound(event: PlatformMessageEvent, actor: ActorContext): InboundMessage {
  return {
    channel: event.channel,
    conversationId: event.conversationId,
    kind: 'im',
    text: event.text,
    actor: { ...actor },
    metadata: {
      chatType: event.chatType,        // 'p2p' | 'group'
      mentionsBot: event.mentionsBot,   // 群聊中是否 @ 了 Bot
      senderId: `${channel}:${userId}`, // 带渠道前缀的发送者标识
    },
  };
}
```

元数据中的 `senderId` 和 `platformTenantId` 用于审计和多租户记忆隔离。

### 5. 工具审批策略

IM 渠道没有交互式审批界面（不像 Web UI 可以弹出确认对话框），所以需要预设策略：

```typescript
// 默认策略：自动批准无风险工具，拒绝需要审批的工具
const defaultGatewayConfirm = async (request) =>
  shouldAutoApproveToolWithoutHitl(request.name);

// 完全访问策略：批准所有工具
const fullAccessConfirm = async () => true;
```

`shouldAutoApproveToolWithoutHitl()` 内部维护了一个安全工具白名单，如：
- 读文件、搜索文件
- Web 搜索、网页内容提取
- 记忆查询
- 只读类工具

不在白名单中的工具（如 `run_command`、`write_file`、`send_email`）在 `request_approval` 模式下会被拒绝，返回"需要审批，但 IM 渠道不支持交互式审批"的提示。

### 6. 并发控制

网关支持全局并发上限配置：

```typescript
// 通过环境变量设置
// ZLEAP_GATEWAY_MAX_CONCURRENT=5

const config = loadGatewayProcessConfig(env);
// config.maxConcurrent = 5（0 表示不限制）
```

并发限制防止大量 IM 消息同时触发 Agent 执行导致资源耗尽。

### 7. 飞书 CLI 渠道

飞书 CLI 渠道不同于标准的飞书 WebSocket/Webhook 模式，它通过 `@larksuite/cli` 子进程驱动：
- 使用 OAuth 设备码流认证（用户扫码授权）
- 支持 `user` 身份（以用户名义发消息）或 `bot` 身份
- 凭据存储在 `cliHome` 目录（Docker 部署时需持久化）
- 首次连接时自动安装 `@larksuite/cli@1.0.56`

### 8. ChannelSupervisor 动态管理

`ChannelSupervisor`（在 supervisor.ts 中）负责适配器的生命周期管理：
- 支持运行时动态启用/禁用渠道（无需重启进程）
- 配置变更时自动 detach 旧适配器、attach 新适配器
- 处理连接断开的自动重连

## 输出结果

启动网关后控制台输出：

```
[INFO] [gateway] 加载飞书配置: appId=cli_xxxxxx, domain=feishu
[INFO] [gateway] 飞书 WebSocket 连接中...
[INFO] [gateway] gateway channel started, channel: feishu
[INFO] [gateway] 网关启动完成，等待消息...

# 收到消息时
[INFO] [gateway] gateway run complete, channel: feishu, chars: 256
```

Docker Compose 启动网关：

```
$ docker compose --profile gateway up -d
✔ Container zleap-postgres   Running
✔ Container zleap-gateway    Started

$ docker compose logs -f gateway
zleap-gateway  | [INFO] 数据库连接成功
zleap-gateway  | [INFO] 飞书渠道已连接
zleap-gateway  | [INFO] 网关已启动
```

## 注意事项

1. **IM 渠道默认使用 `request_approval` 模式**：这是安全默认值。如果需要在 IM 中执行写文件/运行命令等操作，必须显式设置 `full_access`，且强烈建议配合 `admin_only` 群组策略。

2. **飞书凭据安全**：`FEISHU_APP_SECRET` 是敏感信息，不要提交到代码仓库。通过环境变量或 Docker secrets 管理。

3. **微信渠道需要扫码登录**：微信 iLink Bot 使用扫码认证，Bot token 存储在数据库会话行中，重启后可能需要重新扫码。

4. **飞书 CLI 的凭据隔离**：Docker 部署时，`ZLEAP_GATEWAY_STATE_DIR`（默认 `/app/.gateway-state`）必须挂载为持久化 volume，否则容器重启后需要重新 OAuth 认证。

5. **群聊消息过滤**：在群聊中，Bot 默认只响应 @提及自己的消息（`mentionsBot: true`）。这是为了避免 Bot 对群内所有消息做出响应造成打扰。

6. **消息去重**：网关内置了 `dedup.ts` 模块，使用事件 ID + 消息 ID 进行去重，防止飞书/微信的消息重试机制导致重复处理。

7. **平台 ID 不是用户 ID**：`PlatformMessageEvent.userId` 是平台侧的 ID（如飞书 open_id），不是 Zleap 的用户 ID。当前版本网关流量统一使用 `localDevActorContext()`，即所有 IM 用户共享同一个本地用户身份（记忆、会话、任务在同一作用域）。

8. **自定义适配器必须处理重连**：平台 WebSocket 连接可能断开，适配器应实现自动重连逻辑，或通过 `reauth()` 方法支持 Supervisor 触发重连。

9. **网关进程独立部署**：在生产环境中，网关 worker 应该与 Web 服务独立部署（通过 Docker Compose profile 分离），避免 IM 消息处理影响 Web UI 响应速度。
