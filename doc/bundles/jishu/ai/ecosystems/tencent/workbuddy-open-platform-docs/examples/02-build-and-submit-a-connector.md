---
type: Example
title: "照做：构建并提交一个连接器"
description: "从选择 MCP+Skill 或 CLI+Skill 接入方式开始，按官方「连接器」页（D5）逐段落到目录结构、mcp.json / cli.json 的逐字键名、connector-meta.json 元信息、认证与凭证（OAuth 对比用户自填 Token）、图标规范与 11 项提交前检查，最后打包提交审核；含勘误 E1 的处置与「未在本机实跑」声明。"
tags: [WorkBuddy, 开放平台, 连接器, MCP, CLI, Skill, connector-meta.json, mcp.json, cli.json, OAuth, token, 接入示例, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-16" }
verified: { by: "process:seven-concepts-v", at: "2026-10-16" }
status: stable
stale_after: "2027-04-16"
sources:
  - { id: D1, resource: "https://open.workbuddy.cn/docs/what-is-open-platform" }
  - { id: D5, resource: "https://open.workbuddy.cn/docs/connector" }
---

# 照做：构建并提交一个连接器

> 适用场景：你要把一项第三方服务做成 WorkBuddy「连接器」，让用户安装后即可通过自然语言调用第三方服务（F-089）。本篇按官方「连接器」页（D5）的叙述顺序，把「选型 → 目录 → 配置 → 元信息 → 认证 → 图标 → 提交前检查 → 提交审核」串成一条可照做的路径。机制与概念见[连接器：两种接入方式、元信息与认证凭证](../concepts/03-connector-development-and-access-modes.md)；勘误 E1/E3 与口径分层见[核验报告](../references/verification.md)。
>
> 信源纪律：本篇**未在本机实跑**任何连接、鉴权、打包或提交审核流程，未注册账号、未提交审核；全部内容为厂商（腾讯 WorkBuddy）自有开发者文档的自述转述。文档未写明处一律标「**官方未给**」。

## 前置条件

- **已选定接入方案（二选一，不可混用）**：`MCP + Skill`（推荐）或 `CLI + Skill`；**一个连接器只能选择一种方案，二者不可混用**（F-090、F-094）。
- **选型依据成立**：若服务能通过网络 API 提供能力，优先选 `MCP + Skill`；只有在已有稳定、跨平台 CLI 的情况下才选 `CLI + Skill`（F-093）。
- **长期凭证形态已判定**：若服务要求用户自行填写 Access Token 或 API Key 等长期凭证、而非走 OAuth，应使用 MCP 方案的**用户自填 Token 模式**（F-095）。
- **目录四件套已备好**：MCP 方案为 `connector-meta.json`、`mcp.json`、`icon.svg`（均必须）+ `skills/`（可选）；CLI 方案为 `connector-meta.json`（`type` 为 `cli`）、`cli.json`、`icon.svg`（均必须）+ `skills/{skill-name}/SKILL.md`（强烈推荐）（F-096、F-108）。
- **开发者身份与资质**：需先在开放平台完成入驻与相应资质认证后才可开发与发布资产（F-002）；具体认证材料与流程见[入驻与资质](../concepts/01-onboarding-and-qualification.md)，本篇不展开。
- **本机未实跑声明**：本机未创建任何连接器目录、未写入任何真实凭证、未提交审核。

## 操作步骤

> 以下每一步**未在本机实跑，依据官方文档（F-xxx）**；本束未注册账号、未打包、未提交审核、未调用任何真实接口。

1. **选择接入方式**：在 `MCP + Skill` 与 `CLI + Skill` 中二选一，不可混用；能走网络 API 就优先 MCP，只有已有稳定跨平台 CLI 才选 CLI（F-090、F-093、F-094）。〔**未在本机实跑，依据官方文档 F-090、F-093、F-094**〕
2. **按方案搭建目录结构**：MCP 为 `connector-meta.json`/`mcp.json`/`icon.svg`（必须）+ `skills/`（可选）；CLI 为 `connector-meta.json`（`type` 为 `cli`）/`cli.json`/`icon.svg`（必须）+ `skills/{skill-name}/SKILL.md`（强烈推荐）（F-096、F-108）。〔**未在本机实跑，依据官方文档 F-096、F-108**〕
3. **编写 `mcp.json`（MCP 方案）或 `cli.json`（CLI 方案）**：MCP 远程服务使用 HTTPS 并支持 SSE 或 streamableHttp、本地进程可用 stdio，且一个连接器只配置一个 MCP Server（F-098、F-103）；CLI 需 `auth`/`status`/`unAuth` 三条命令约束（F-111、F-117～F-122）。〔**未在本机实跑，依据官方文档 F-098、F-103、F-116、F-117～F-122**〕
4. **编写 Skill 文件**：MCP 已提供标准工具描述时可选，CLI 方案强烈推荐提供——因 CLI 没有标准的工具描述协议，AI 只能依赖 Skill 了解命令与参数（F-129、F-109）。〔**未在本机实跑，依据官方文档 F-109、F-129、F-130、F-131**〕
5. **填写连接器元信息 `connector-meta.json`**：注册连接器并在市场展示名称、描述与使用示例；`source` 为全局限一标识，只能使用小写字母、数字和连字符，提交前检查要求 kebab-case 且全局唯一（F-123、F-124、F-125）。〔**未在本机实跑，依据官方文档 F-123～F-128**〕
6. **配置认证与凭证**：按四类场景选模式（F-132～F-135）；走 OAuth 的服务端端点与行为见 F-139～F-143；走自填 Token 需 `token-schema.json` 且占位符与字段 key 完全一致（F-145、F-146）。〔**未在本机实跑，依据官方文档 F-132～F-151**〕
7. **准备图标**：格式 SVG（推荐）、PNG 或 JPG，文件名 `icon.svg`/`icon.png`/`icon.jpg`，PNG/JPG 建议 64×64 px，背景建议透明（F-152）。〔**未在本机实跑，依据官方文档 F-152**〕
8. **逐项跑提交前检查 11 项**（见下方清单，F-153）。〔**未在本机实跑，依据官方文档 F-153**〕
9. **打包连接器目录并提交 WorkBuddy 团队审核**（F-154）。〔**未在本机实跑，依据官方文档 F-154**〕

### 第 2 步示例：两方案的目录结构（逐字照抄）

MCP + Skill 基础结构（F-096）：

```
your-connector/
├── connector-meta.json          # 连接器元信息（必须）
├── mcp.json                     # MCP Server 连接配置（必须）
├── icon.svg                     # 市场图标（必须）
└── skills/                      # AI 使用说明（可选）
    └── {skill-name}/
        └── SKILL.md
```

CLI + Skill 基础结构（F-108）：

```
your-cli-connector/
├── connector-meta.json          # 连接器元信息（必须，type 为 cli）
├── cli.json                     # CLI 安装与认证配置（必须）
├── icon.svg                     # 市场图标（必须）
└── skills/
    └── {skill-name}/
        └── SKILL.md             # CLI 使用说明（强烈推荐）
```

### 第 3 步示例：`mcp.json` 远程与 stdio（逐字照抄）

远程 MCP 示例（F-105，逐字照抄）：

```
{
  "mcpServers": {
    "your-service": {
      "type": "streamableHttp",
      "url": "https://mcptokenSchema 字段.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${SERVICE_TOKEN}"
      },
      "timeout": 30000
    }
  }
}
```

> **⚠️ 勘误 E1 处置**：上例 `url` 字段的原文**含乱入文本**——「**tokenSchema 字段**」被插在主机名位置，使该 URL 的主机名与路径均被破坏。**原文如此（含乱入文本），疑似编辑错误，以官方页面为准**；**不得**将其作为可用端点照抄，本束也不擅自「更正」为推断值（F-105 的核验状态为 `已核验（原文瑕疵）`，见[核验报告](../references/verification.md) 勘误 E1）。该乱入文本与自填 Token 模式的 `token-schema.json` 机制**无关**，不可据此推断键名。

stdio MCP 示例（F-106，逐字照抄）：

```
{
  "mcpServers": {
    "your-service": {
      "type": "stdio",
      "command": "npx",
      "args": ["your-mcp-package"],
      "runtime": {
        "type": "node",
        "version": "20"
      },
      "npmRegistry": "https://registry.npmmirror.com"
    }
  }
}
```

字段要点：`mcpServers` 为顶层配置，仅配置一个 Server；`type` 可取 `sse`、`streamableHttp` 或 `stdio`；`url` 仅 SSE/streamableHttp 必填且生产环境必须 HTTPS；`headers`/`env` 用 `${VAR_NAME}` 变量引用、不得写入真实凭证；`timeout` 默认 30000 毫秒（F-105、F-106、F-098、F-103）。使用带版本号的字段时，须在 `connector-meta.json` 中声明对应的 `minWorkbuddyVersion`（F-107）。

### 第 3 步示例：`cli.json`（逐字照抄）

```
{
  "runtime": {
    "type": "node",
    "version": "20"
  },
  "init": {
    "darwin": "npm install -g your-cli",
    "linux": "npm install -g your-cli",
    "win32": "npm install -g your-cli"
  },
  "auth": {
    "darwin": "your-cli auth login",
    "linux": "your-cli auth login",
    "win32": "your-cli.cmd auth login"
  },
  "unAuth": {
    "darwin": "your-cli auth logout",
    "linux": "your-cli auth logout",
    "win32": "your-cli.cmd auth logout"
  },
  "status": {
    "darwin": "your-cli auth status",
    "linux": "your-cli auth status",
    "win32": "your-cli.cmd auth status"
  },
  "statusMatch": "Logged in",
  "authUrlDomain": "example.com"
}
```

`cli.json` 示例顶层键为 `runtime`、`init`、`auth`、`unAuth`、`status`、`statusMatch`、`authUrlDomain`；`init`/`auth`/`unAuth`/`status` 均为按平台（`darwin`/`linux`/`win32`）分键的命令对象（F-116）。其中 **`statusMatch`** 是判断已登录状态的文本正则、**`authUrlDomain`** 是限定 WorkBuddy 可提取并打开的认证域名（F-116）。CLI 认证流程与关键约束：点击「连接」后依次检查安装、执行 `status`、未登录时执行 `auth` 提取认证 URL 并打开浏览器，随后每 3 秒轮询 `status`、最长等待 5 分钟；提取到 URL 后会立即终止 `auth` 子进程，故 `auth` 子进程不能作为 OAuth 回调接收方，且 `auth` 须在 10 秒内在 stdout/stderr 输出完整 `https://` URL（不被引号或尖括号包裹）（F-117、F-118、F-120、F-121）；重启后只会自动执行 `status` 恢复连接、不会重跑 `auth`，故登录态必须跨进程重启有效（F-122）。

### 第 4 步要点：Skill 编写重点五项（F-131）

Skill 用于指导 AI 正确使用连接器（F-129）：① 每个 MCP Tool 或 CLI 命令的用途；② 参数名称、类型、是否必填和默认值；③ 典型调用示例及返回格式；④ 认证前置条件、错误场景和恢复方式；⑤ 高风险操作需要的确认规则（F-131）。能力较多时可拆分为多个 Skill，每个放置在独立子目录下，WorkBuddy 会全部加载（F-130）。

> **⚠️ 勘误 E3 提示**：原页把 Skill 的目录与 `SKILL.md` 格式指向本页「开发—技能」小节，但该小节在原页实际章节表（`选择接入方式` / `MCP + Skill 接入` / `CLI + Skill 接入` / `连接器元信息` / `Skill 文件` / `认证与凭证` / `图标规范` / `提交前检查`）中**不存在**，属**文档内部引用缺陷**；**不得据该引用推断被引用内容**，需要技能结构时请回源官方页面或查阅同束[技能](../concepts/02-skill-development-and-marketplace.md)（F-130，见[核验报告](../references/verification.md) 勘误 E3）。

### 第 5 步示例：`connector-meta.json`（逐字照抄）

```
{
  "name": "任务管理",
  "name_zh": "任务管理",
  "name_en": "Task Manager",
  "description": "Create and manage tasks in WorkBuddy.",
  "description_zh": "通过自然语言创建、查询和更新任务。",
  "description_en": "Create, query, and update tasks with natural language.",
  "source": "task-manager",
  "type": "mcp",
  "version": "1.0.0",
  "examples_zh": [
    "创建一个明天下午到期的评审任务",
    "列出本周尚未完成的任务"
  ],
  "examples_en": [
    "Create a review task due tomorrow afternoon",
    "List unfinished tasks for this week"
  ]
}
```

示例键为 `name`、`name_zh`、`name_en`、`description`、`description_zh`、`description_en`、`source`、`type`、`version`、`examples_zh`、`examples_en`（F-124）；`type` 示例值 `"mcp"`，CLI 方案必须设为 `cli`（F-124、F-108）。展示优先级：名称为 `name_map`（命中环境）> `name_zh` > `name_en` > `name`，描述回退到 `description_zh` → `description_en` → `description`（F-126）。**版本兼容性**：使用较新字段时必须声明 `minWorkbuddyVersion`，否则低版本客户端可能拉取到不兼容配置；同时使用多个新特性时取其中最高版本作为声明值（F-127）；对低于所声明版本的客户端——从未启用过时不展示，已启用或曾连接过则降级置灰并提示升级（F-128）。`maxWorkbuddyVersion` 等键未编入本束 F 编号，本篇不展开。

### 第 6 步：认证与凭证（区分两种模式）

**四类场景分工**（F-132～F-135）：

| 场景 | 接入方式 | 是否打开浏览器 | 事实 |
| --- | --- | --- | --- |
| MCP Server 自带 OAuth 或无需认证 | `auth_mode` **省略**，按标准 MCP 流程连接 | 需授权时会打开 | F-132 |
| WorkBuddy 云端托管 OAuth | 使用 `server-side` 或 `gateway`，**接入前需与 WorkBuddy 团队确认** | 需授权时会打开 | F-133 |
| 用户自行填写 Access Token / API Key | 使用 **`auth_mode: "token"`**，并提供 `token-schema.json` 描述表单 | **不打开** | F-134 |
| CLI 登录 | 通过 `cli.json` 的 `auth`/`status`/`unAuth` 管理，凭证由 CLI 自行安全存储 | 取决于 CLI 认证方式 | F-135 |

**OAuth 模式**（MCP Server 访问用户私有数据时）：WorkBuddy 内置 OAuth 管理器自动完成客户端侧流程，采用 OAuth 2.1 + PKCE、以公共客户端身份接入（不持有 `client_secret`），**开发者只需实现服务端端点**（F-137）。整体流程为「未携带 Token 返回 401 → 发现元数据 → 动态客户端注册 → 打开浏览器授权 → 校验 state 并交换 Token → 携带 Bearer Token 正常调用」（F-138）。服务端端点五项：`/.well-known/oauth-protected-resource`（GET）、`/.well-known/oauth-authorization-server`（GET）、`/oauth/register`（POST，动态客户端注册 RFC 7591）、`/oauth/authorize`（GET，须支持 `code_challenge_method: S256`）、`/oauth/token`（POST，须支持 `refresh_token` 授权类型）（F-139）。行为要求：必须支持 PKCE（`S256`）、授权码一次性使用且有效期约 10 分钟（F-140）；`redirect_uri` 按字符串精确匹配，优先支持私有协议回调 `workbuddy://workbuddy/mcp/connector%3A<source>/oauth/callback`，若平台仅允许 HTTP/HTTPS 回调则应允许本机回环地址 `http://127.0.0.1:{动态端口}/oauth/callback`（F-141）；动态注册响应除 `client_id` 外必须回显 `redirect_uris`（F-142）；`access_token` 建议有效期 1 小时、`refresh_token` 建议不少于 30 天（F-143）；过期时 WorkBuddy 自动用 `refresh_token` 续期并重试原请求，对用户透明（F-144）。

**用户自填 Token 模式**（服务不提供 OAuth，仅提供 Personal Access Token / API Key，或需用户指定私有部署地址）：使用 `auth_mode: "token"`——WorkBuddy 弹出表单收集凭证，凭证**仅保存在用户本机**并在连接时注入、**不经过云端**，整个过程不打开浏览器；该模式需声明 `minWorkbuddyVersion` 不低于 `4.23.0`（F-145）。凭证注入位置：stdio → `env`（典型写法 `"env": { "API_KEY": "${API_KEY}" }`）；sse / streamableHttp → `headers` 或 `url`（典型写法 `"Authorization": "Bearer ${API_KEY}"`）（F-147）。**占位符名称必须与表单字段的 `key` 完全一致（区分大小写）**（F-146）。`token-schema.json` 示例（逐字照抄，F-148）：

```
{
  "title": "服务对接配置",
  "title_en": "Service Configuration",
  "description": "连接您的账号以调用服务。凭证仅存储在本机 ~/.workbuddy 目录下。",
  "description_en": "Connect your account. Credentials are stored locally only.",
  "docUrl": "https://example.com/docs/api-token",
  "docLabel": "如何获取 Access Token？",
  "fields": [
    {
      "key": "API_KEY",
      "label": "Access Token",
      "type": "password",
      "required": true,
      "placeholder": "在个人中心 → 开放平台 → API 中生成",
      "description": "用于访问服务 OpenAPI 的个人访问令牌。"
    },
    {
      "key": "API_BASE_URL",
      "label": "API 基础地址",
      "label_en": "API Base URL",
      "type": "text",
      "required": true,
      "defaultValue": "https://api.example.com",
      "description": "私有部署可改为内网地址。"
    }
  ]
}
```

`description` 建议明确告知凭证的存储位置（示例文案：凭证仅存储在本机 `~/.workbuddy` 目录下）（F-149）；多语言文案通过新增 `_en` 后缀的平行字段实现，原字段必须保持字符串类型、不可改为对象，否则低版本客户端无法渲染（F-150）。**同一服务若需同时提供 OAuth 与 Token 两种方式，必须使用两个不同的 `source` 分别提交，作为两个独立的连接器**（F-151）。

**安全要求五项**：不得在 `connector-meta.json`、`mcp.json`、`cli.json`、Skill 或示例中硬编码真实 Token / 密钥；仅申请最小权限；远程 MCP 使用 HTTPS；敏感凭证字段应使用密码类型、日志与错误信息中不得输出完整凭证；授权失效时应返回可识别错误并引导用户重新连接（F-136）。

> **口径澄清（防张冠李戴）**：本页（D5）实际出现的相关键名为 `statusMatch`、`authUrlDomain`（F-116）、`auth_mode`（F-134、F-145）与文件名 `token-schema.json`（F-146）；**原页未出现 `auth.tokenSchema` 这一路径式键名**。camelCase 的 `tokenSchema` 字段口径属**同族另页（D6/D7）内容，非本篇来源**，本篇不引用其明细；另注意 D5 远程 MCP 示例 URL 中的「tokenSchema 字段」是**乱入文本（勘误 E1）**，与 `token-schema.json` 机制无关。

### 第 8 步清单：提交前检查 11 项（F-153，逐条）

1. 已选择 MCP 或 CLI 接入方案，目录结构符合规范；
2. `source` 使用 kebab-case 且保持全局唯一；
3. 连接器名称、说明和中英文示例填写完整；
4. MCP 仅配置一个 Server，远程地址使用 HTTPS；
5. 或 CLI 已验证安装、认证、状态检查、登出和跨平台行为；
6. CLI 方案已验证登录态跨重启有效，且 `unAuth` 能正确清理授权；
7. 涉及 OAuth 时已实现元数据发现、动态注册与 PKCE 校验，并接受约定的回调地址；
8. 使用自填 Token 模式时，`${VAR}` 占位符与表单字段 key 一一对应，敏感字段为 `password` 类型；
9. Skill 能准确指导 AI 调用全部核心能力；
10. 未在任何文件中写入真实凭证；
11. 图标清晰可辨，版本号和最低 WorkBuddy 版本声明正确，且已覆盖超时、授权失效、参数错误等常见异常。

## 结果判据

> 本节判据均**取自官方文档描述的可观察迹象**；**本机无法闭环**——审核结果由平台判定、打包与提交流程本次未实跑，判据来自文档而非实测。

- **可提交判据**：上述 11 项提交前检查全部满足，即视为「准备完成」（F-153）。
- **提交后走向**：将连接器目录打包并提交 WorkBuddy 团队审核；**审核通过后连接器将进入连接器市场**；后续更新**重新提交审核即可，通常在 10～15 分钟内同步生效**（F-154）。
- **审核结论归属**：连接器是否通过审核**由平台判定**，本次未提交、未获得任何审核结论；本束不作「已通过审核 / 已上线」的判断。
- **配置生效判据（文档描述）**：对低于所声明 `minWorkbuddyVersion` 的客户端，从未启用过该连接器时**不展示**、已启用或曾连接过则**降级置灰并提示升级**（F-128）。

## 限制与边界

- **未实跑声明**：本篇**未在本机实跑**——未创建连接器目录、未编写或验证任何配置与凭证、未打包、未提交审核；文中端点、键名、示例值与判定条件均来自官方文档（F-089～F-154）。
- **官方未给（不得据名称或常识补全）**：连接器的**审核时长**未给出（仅 F-154 给出提交更新后「通常 10～15 分钟同步生效」，**非审核时长**）；**全局限流与配额、席位上限**未给出；**移动端开放时间点**未给出。`MCP Server` 自述的「可用性不低于 99.9%」「单次请求 30 秒内响应」为**建议值**而非平台硬门槛（F-100、F-101）。
- **E1 复述**：D5 示例 MCP URL 的 `url` 含乱入文本「tokenSchema 字段」，**原文如此，疑似编辑错误，以官方页面为准**；**不得**将其作为可用端点照抄（F-105）。
- **E3 复述**：D5 正文引用的「开发—技能」小节在原页章节表中不存在，属文档内部引用缺陷；**不得据编号或小节名推断被引用内容**（F-130）。
- **未采集页登记**：站点侧栏另有 `api-token`、`contact`、`developer-profile`、`legal-basis-and-examples`、`operations-data`、`service-categories-individual`、`service-categories-enterprise` 共 7 篇 `/docs/` 页**本次未采集，仅登记入口**，不得据其名称推断功能细节、字段、权限或门槛（见[核验报告](../references/verification.md) 第二节）。
- **表述红线**：本篇不出现「已上线 / 已 GA / 已完成审核 / 功能已验证可用」；文档未写明 = **官方未给**，不等于默认无限制。

> 相关：概念篇[连接器：两种接入方式、元信息与认证凭证](../concepts/03-connector-development-and-access-modes.md)、[技能开发与市场](../concepts/02-skill-development-and-marketplace.md)；核验[核验报告](../references/verification.md)、[来源代号与 F 编号事实登记](../references/article-source.md)；平级束[WorkBuddy 官方站点与四区文档](../../workbuddy-official-docs/index.md)、[分享能力接入与推广管理](../../workbuddy-open-platform-sharing-and-promotion/index.md)。
