---
type: Concept
title: "连接器：两种接入方式、元信息与认证凭证"
description: "按「选型 → MCP + Skill → CLI + Skill → 元信息 → Skill 文件 → 认证与凭证 → 图标 → 提交前检查」八段归纳 WorkBuddy 开放平台连接器资产的自述口径：两种接入方式的选型对照与不可混用约束、MCP 的远程/本地形态与传输类型、CLI 的安装认证与状态检查约束、connector-meta.json 字段与版本兼容、以及 OAuth 模式与用户自填 Token 模式的分工与键名。"
tags: [WorkBuddy, 开放平台, 连接器, MCP, CLI, Skill, connector-meta.json, mcp.json, cli.json, OAuth, token, OKF]
generated: { by: "process:seven-concepts-e", at: "2026-10-16" }
verified: { by: "process:seven-concepts-v", at: "2026-10-16" }
status: stable
stale_after: "2027-04-16"
sources:
  - { id: D5, resource: "https://open.workbuddy.cn/docs/connector" }
---

# 连接器：两种接入方式、元信息与认证凭证

> 本篇归纳 WorkBuddy 开放平台开发者文档「连接器」页（D5）的自述内容：连接器是什么、`MCP + Skill` 与 `CLI + Skill` 怎么选、包结构、元信息字段、认证凭证各模式的键名与约束、图标规范与提交前检查。事实编号（F-089～F-154，共 66 条）见[来源代号与 F 编号事实登记](../references/article-source.md)；勘误 E1/E3 与口径分层见[核验报告](../references/verification.md)；页级覆盖见[页级采集与覆盖台账](../references/source-manifest.md)。构建与提交连接的完整示例见[构建并提交一个连接器](../examples/02-build-and-submit-a-connector.md)。
>
> 信源纪律：本篇内容**仅为厂商（腾讯 WorkBuddy）开放平台开发者文档的自述**，**未在本平台实跑**任何连接、鉴权、上架或审核流程；文档未写明处一律标「**官方未给**」。

## 一、连接器是什么，两种接入方式怎么选

**连接器是 WorkBuddy 的能力扩展接口**，用户安装后即可**通过自然语言调用第三方服务**（F-089）。WorkBuddy 支持两种接入方式：**`MCP + Skill`（推荐）** 与 **`CLI + Skill`**（F-090）。二者的选型对照如下：

| 维度 | MCP + Skill（推荐） | CLI + Skill |
| --- | --- | --- |
| 适用场景 | 已有 API 服务，或可以开发 MCP Server（F-091） | 已有成熟的命令行工具（F-092） |
| 机制 | 基于 MCP 协议暴露工具（F-091） | WorkBuddy 负责安装和调度 CLI（F-092） |
| 职责边界 | 工具由 MCP Server 暴露；远程服务优先采用 HTTPS 的 SSE 或 streamableHttp（F-091） | CLI **自行管理登录态和凭证**（F-092） |
| 选型优先级 | 若服务可通过网络 API 提供能力，**优先选择 MCP + Skill**（F-093） | 只有在已有**稳定、跨平台 CLI**的情况下才选择（F-093） |
| 可否混用 | **一个连接器只能选择一种方案，二者不可混用**（F-094） | 同左（F-094） |

> **选型两问**（据 F-093）：① 服务能否通过网络 API 提供能力？能 → 选 MCP；② 是否已有稳定、跨平台 CLI？有且不具备① → 才选 CLI。**不可混用**是硬约束（F-094）：同一连接器不能在两种方案间拼装。
>
> **长期凭证走哪个模式**：若服务要求用户自行填写 Access Token 或 API Key 等**长期凭证**（而非走 OAuth），应使用 **MCP 方案的用户自填 Token 模式**（F-095，详见第六节）。

## 二、MCP + Skill 接入

### 基础结构（F-096，逐字）

```
your-connector/
├── connector-meta.json          # 连接器元信息（必须）
├── mcp.json                     # MCP Server 连接配置（必须）
├── icon.svg                     # 市场图标（必须）
└── skills/                      # AI 使用说明（可选）
    └── {skill-name}/
        └── SKILL.md
```

四项中 `connector-meta.json`、`mcp.json`、`icon.svg` 为**必须**，`skills/` 为**可选**（内含 `{skill-name}/SKILL.md`）（F-096）。

### MCP Server 要求（F-097～F-103）

- 遵循 **MCP 稳定协议版本**（F-097）；
- **远程服务使用 HTTPS，支持 SSE 或 streamableHttp；本地进程可使用 stdio**（F-098）——即远程/本地两种形态由传输类型区分：远程 = HTTPS + SSE/streamableHttp，本地 = stdio；
- 工具名称、描述、参数和返回值应清晰、稳定，便于 AI 正确选择和调用（F-099）；
- 返回可读错误信息，并设置合理超时，**单次请求建议在 30 秒内响应**（F-100）；
- 服务保持稳定可达，**建议可用性不低于 99.9%**（F-101）；
- 涉及用户数据时**必须提供认证鉴权**，并遵循最小权限原则（F-102）；
- **一个连接器只配置一个 MCP Server**（F-103）。

开发资源（F-104）：MCP 协议规范 `https://modelcontextprotocol.io/`；Python SDK `https://github.com/modelcontextprotocol/python-sdk`；TypeScript SDK `https://github.com/modelcontextprotocol/typescript-sdk`。

### mcp.json

远程 MCP 示例（F-105，逐字）：

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

> **⚠️ 勘误 E1 处置**：上例 `url` 字段的原文**含乱入文本**——「**tokenSchema 字段**」被插在主机名位置，使该 URL 主机名与路径均被破坏。**原文如此（含乱入文本），疑似编辑错误，以官方页面为准**；**不得**将该 `url` 当作可用端点照抄，本束也不擅自「更正」为推断值（F-105 的核验状态标注为 `已核验（原文瑕疵）`，见[核验报告](../references/verification.md) 勘误 E1）。

远程示例使用键 **`mcpServers` → `your-service`**，字段为 `type: "streamableHttp"`、`url`、`headers.Authorization: "Bearer ${SERVICE_TOKEN}"`、`timeout: 30000`（F-105）。另有 **stdio MCP 示例**（F-106），其字段为 `type: "stdio"`、`command: "npx"`、`args: ["your-mcp-package"]`、`runtime: { type: "node", version: "20" }`、`npmRegistry: "https://registry.npmmirror.com"`——对应第二节「本地进程可使用 stdio」形态（F-098）。

> **版本声明要求**：使用**带版本号的字段**时，须在 `connector-meta.json` 中声明对应的 **`minWorkbuddyVersion`**（F-107）。原页另列有 `cwd`、`disabledTools`、`staticEnv`、`staticHeaders`、`preAuth` 等带最低版本号的 `mcp.json` 字段，但**未逐条编入本束 F 编号**（F-001～F-439 内无对应条目）；本篇仅登记该边界，如需引用须回源官方页面。

## 三、CLI + Skill 接入

### 基础结构（F-108，逐字）

```
your-cli-connector/
├── connector-meta.json          # 连接器元信息（必须，type 为 cli）
├── cli.json                     # CLI 安装与认证配置（必须）
├── icon.svg                     # 市场图标（必须）
└── skills/
    └── {skill-name}/
        └── SKILL.md             # CLI 使用说明（强烈推荐）
```

其中 `connector-meta.json`（**必须，`type` 为 `cli`**）、`cli.json`（必须）、`icon.svg`（必须），`skills/{skill-name}/SKILL.md`（CLI 使用说明，**强烈推荐**）（F-108）。**CLI 工具没有标准的工具描述协议**，AI 需依赖 Skill 了解可用命令和参数，因此本方案**强烈推荐**提供 Skill 文件（F-109）。

### CLI 开发要求（F-109～F-115）

- 至少支持 **macOS 和 Linux**，建议同时支持 Windows（F-110）；
- 提供**非交互式安装方式**，以及明确的 **`auth`、`status`、`unAuth`** 命令（F-111）；
- `auth` 成功后由 CLI 自行持久化登录态；**`status` 只检查状态且不产生副作用**；`unAuth` 负责撤销或清理登录态（F-112）；
- 命令应返回明确退出码和可读错误信息，**业务结果优先使用 JSON**（F-113）；
- **不要依赖用户机器预装的 Node.js、Python 或全局包**；依赖运行时时应在 `cli.json` 中声明 `runtime`（F-114）；
- 凭证与 CLI 安装目录分离，**不得把密钥写入安装包、Skill 或配置样例**（F-115）。

### cli.json（F-116）

`cli.json` 示例顶层键为 **`runtime`、`init`、`auth`、`unAuth`、`status`、`statusMatch`、`authUrlDomain`**；`init`/`auth`/`unAuth`/`status` 均为**按平台（`darwin`/`linux`/`win32`）分键的命令对象**（F-116，示例值：`"statusMatch": "Logged in"`、`"authUrlDomain": "example.com"`、`"runtime": { "type": "node", "version": "20" }`）。其中 **`statusMatch`** 是判断已登录状态的文本正则、**`authUrlDomain`** 是限定 WorkBuddy 可提取并打开的认证域名（F-116）。

### 认证流程与关键约束（F-117～F-122）

用户点击「连接」后，WorkBuddy 依次执行：**检查安装（未安装则执行 `init`）→ 执行 `status` 判断登录态 → 未登录时执行 `auth`，从命令输出中提取认证 URL 并打开浏览器 → 随后每 3 秒轮询一次 `status`，最长等待 5 分钟**（F-117）。

关键约束：

- WorkBuddy **在提取到认证 URL 后会立即终止 `auth` 子进程**，因此 **`auth` 子进程本身不能作为 OAuth 回调的接收方**（F-118）；OAuth 回调可选三种方案——**后台 Daemon 接收回调**（复杂度中）、**Device Code Flow**（复杂度低、推荐，需认证服务器支持 RFC 8628）、**服务端 Token 存储**（复杂度中）（F-119）；
- `auth` 命令需在 **stdout 或 stderr** 中输出**完整的 `https://` 认证 URL 并在 10 秒内输出**；URL 前后需有**空白字符分隔，不能被引号或尖括号包裹**，否则会被截断（F-120）；
- `auth` 命令**不得进入交互式输入等待**（执行环境没有 TTY），也不应自行打开浏览器而不输出 URL（F-121）；
- WorkBuddy 重启后**会自动执行 `status` 恢复连接，但不会重新执行 `auth`**，因此 CLI 的登录态**必须跨进程重启有效**（F-122）。

## 四、连接器元信息

`connector-meta.json` 用于**注册连接器**，并在**市场中展示名称、描述和使用示例**（F-123）。其示例键为 `name`、`name_zh`、`name_en`、`description`、`description_zh`、`description_en`、`source`、`type`、`version`、`examples_zh`、`examples_en`（F-124；示例值 `"type": "mcp"`、`"source": "task-manager"`、`"version": "1.0.0"`）。关键字段：

| 字段 | 说明 | 事实 |
| --- | --- | --- |
| `source` | **全局限一标识**，只能使用**小写字母、数字和连字符**；提交前检查要求使用 **kebab-case 且全局唯一** | F-125 |
| `name` / `name_zh` / `name_en` | 名称；展示优先级为 **`name_map`（命中环境）> `name_zh` > `name_en` > `name`** | F-124、F-126 |
| `description` / `description_zh` / `description_en` | 描述；展示回退顺序同为 `description_zh` → `description_en` → `description` | F-124、F-126 |
| `type` | 连接器类型（示例值 `"mcp"`；CLI 方案必须设为 `cli`） | F-124、F-108 |
| `version` | 版本号（示例 `"1.0.0"`） | F-124 |
| `examples_zh` / `examples_en` | 中英文使用示例（示例各 2 条） | F-124 |
| `auth_mode` | 认证模式：省略 / `server-side` / `gateway` / `token` | F-132、F-133、F-134、F-145 |
| `minWorkbuddyVersion` | 使用较新字段时声明的最低 WorkBuddy 版本 | F-107、F-127、F-145 |

> **版本兼容性（F-127、F-128）**：不同 WorkBuddy 客户端支持的配置字段不同；**使用较新字段时必须声明 `minWorkbuddyVersion`**，否则低版本客户端可能**拉取到不兼容的配置**；若同时使用多个新特性，**取其中最高版本作为声明值**（F-127）。对**低于所声明版本**的客户端：**从未启用过**该连接器时**不展示**；**已启用或曾连接过**则**降级置灰并提示升级**（F-128）。
>
> **未编入 F 表项**：原页元信息表另列出 `maxWorkbuddyVersion` 等键及其最低版本号，但**未编入本束 F 编号**（F-001～F-439 内无对应条目）；本篇仅登记该边界，**不展开其语义**，如需引用须回源官方页面。

## 五、Skill 文件：CLI 与 MCP 两种形态的差异

Skill 用于**指导 AI 正确使用连接器**：**MCP 已提供标准工具描述时可选，CLI 方案强烈推荐提供**（F-129）。这一「可选 / 强烈推荐」的差异，正对应第二节与第三节的机制差异——**MCP 由协议暴露工具描述，CLI 没有标准的工具描述协议、只能靠 Skill 说明命令与参数**（F-098、F-109）。

Skill 的目录与 `SKILL.md` 格式**参见本页「开发—技能」**；能力较多时可拆分为多个 Skill，**每个放置在独立子目录下，WorkBuddy 会全部加载**（F-130）。编写重点五项（F-131）：每个 MCP Tool 或 CLI 命令的用途；参数名称、类型、是否必填和默认值；典型调用示例及返回格式；认证前置条件、错误场景和恢复方式；高风险操作需要的确认规则。

> **⚠️ 勘误 E3 提示**：本文引用的「开发—技能」小节名，在原页实际章节表（`选择接入方式` / `MCP + Skill 接入` / `CLI + Skill 接入` / `连接器元信息` / `Skill 文件` / `认证与凭证` / `图标规范` / `提交前检查`）中**不存在**，属**文档内部引用缺陷**；**不得据该引用推断被引用内容**，需要技能结构时请查阅同束[技能](../concepts/02-skill-development-and-marketplace.md)或回源官方页面（F-130，见[核验报告](../references/verification.md) 勘误 E3）。

## 六、认证与凭证

### 四类场景分工（F-132～F-135）

| 场景 | 接入方式 | 是否打开浏览器 | 事实 |
| --- | --- | --- | --- |
| MCP Server **自带 OAuth 或无需认证** | `auth_mode` **省略**，按标准 MCP 流程连接 | 需授权时**会**打开 | F-132 |
| **WorkBuddy 云端托管 OAuth** | 使用 `server-side` 或 `gateway`，**接入前需与 WorkBuddy 团队确认** | 需授权时**会**打开 | F-133 |
| **用户自行填写 Access Token / API Key** | 使用 **`auth_mode: "token"`**，并提供 `token-schema.json` 描述表单 | **不打开** | F-134 |
| **CLI 登录** | 通过 `cli.json` 的 `auth`、`status`、`unAuth` 管理，凭证由 CLI 自行安全存储 | **取决于 CLI 认证方式** | F-135 |

**安全要求五项**（F-136）：不得在 `connector-meta.json`、`mcp.json`、`cli.json`、Skill 或示例中**硬编码真实 Token / 密钥**；仅申请完成业务所需的**最小权限**；**远程 MCP 使用 HTTPS**；**敏感凭证字段应使用密码类型**，日志和错误信息中不得输出完整凭证；**授权失效时应返回可识别错误并引导用户重新连接**。

### MCP OAuth 流程（F-137～F-144）

当 MCP Server 需访问用户私有数据并采用 OAuth 时，**WorkBuddy 内置的 OAuth 管理器会自动完成客户端侧流程**，采用 **OAuth 2.1 + PKCE**，并以**公共客户端身份接入（不持有 `client_secret`）**；**开发者只需实现服务端端点**（F-137）。

整体流程：首次请求未携带 Token **返回 401** → **发现元数据** → **动态客户端注册** → **打开浏览器授权** → **校验 state 并交换 Token** → 携带 **Bearer Token** 正常调用（F-138）。服务端端点五项（F-139）：`/.well-known/oauth-protected-resource`（GET）、`/.well-known/oauth-authorization-server`（GET）、`/oauth/register`（POST，动态客户端注册 RFC 7591）、`/oauth/authorize`（GET，须支持 `code_challenge_method: S256`）、`/oauth/token`（POST，须支持 `refresh_token` 授权类型）。

服务端行为要求（F-140～F-143）：**必须支持 PKCE（`S256`）**，授权码**一次性使用且有效期约 10 分钟**（F-140）；**`redirect_uri` 需按字符串精确匹配**，优先支持 WorkBuddy 私有协议回调 `workbuddy://workbuddy/mcp/connector%3A<source>/oauth/callback`，若平台仅允许 HTTP/HTTPS 回调则应允许本机回环地址 `http://127.0.0.1:{动态端口}/oauth/callback`，WorkBuddy 会在私有协议被拒绝时**自动回退一次**（F-141）；**动态注册响应除 `client_id` 外必须回显 `redirect_uris`**（F-142）；**令牌有效期建议 `access_token` 1 小时、`refresh_token` 不少于 30 天**，所有端点强制 HTTPS 并遵循 OAuth 2.1 标准错误格式（F-143）。`access_token` 过期时，WorkBuddy 会**自动用 `refresh_token` 续期并重试原请求，对用户透明**（F-144）。

### 用户自填 Token 模式（F-145～F-151）

当第三方服务**不提供 OAuth**、仅提供 Personal Access Token / API Key，或需用户指定**私有部署地址**时，使用 **`auth_mode: "token"`**：WorkBuddy **弹出表单收集凭证，凭证仅保存在用户本机并在连接时注入，不经过云端，整个过程不打开浏览器**；该模式需声明 **`minWorkbuddyVersion` 不低于 `4.23.0`**（F-145）。该模式需额外提供 **`token-schema.json`** 描述表单字段，并在 `mcp.json` 中用 **`${VAR}`** 占位引用；**占位符名称必须与表单字段的 `key` 完全一致（区分大小写）**（F-146）。

凭证注入位置（F-147）：**stdio → `env`（环境变量，典型写法 `"env": { "API_KEY": "${API_KEY}" }`）；`sse` / `streamableHttp` → `headers` 或 `url`（典型写法 `"Authorization": "Bearer ${API_KEY}"`）**。

`token-schema.json` 示例含 `title`、`title_en`、`description`、`description_en`、`docUrl`、`docLabel`、`fields[]`（F-148）；`fields` 每项示例含 `key`（`API_KEY` / `API_BASE_URL`）、`label`、`label_en`、`type`（`password` / `text`）、`required`、`placeholder`、`defaultValue`、`description`（F-148）。`description` 建议明确告知凭证的**存储位置**（示例文案：凭证仅存储在本机 `~/.workbuddy` 目录下）（F-149）。**多语言文案通过新增 `_en` 后缀的平行字段实现**（如 `title_en`、`label_en`），**原字段必须保持字符串类型、不可改为对象**，否则低版本客户端将无法渲染（F-150）。**同一服务若需同时提供 OAuth 与 Token 两种方式，必须使用两个不同的 `source` 分别提交，作为两个独立的连接器**（F-151）。

### 键名速查与一处口径澄清

| 键名 / 文件 | 出处 | 事实 |
| --- | --- | --- |
| `statusMatch` | `cli.json` 顶层键（判断已登录的文本匹配） | F-116 |
| `authUrlDomain` | `cli.json` 顶层键（限定可提取并打开的认证域名） | F-116 |
| `auth_mode: "token"` | `connector-meta.json` 中启用自填 Token 模式 | F-134、F-145 |
| `token-schema.json` | 自填 Token 模式的表单描述文件 | F-146 |
| `statusMatchJson` | `cli.json` 同类键 | —（原页表格出现，**未编入本束 F 编号**，本篇不展开） |

> **口径澄清（防张冠李戴）**：本篇（D5）原页实际出现的相关键名为 **`statusMatch`、`authUrlDomain`**（F-116）、**`auth_mode`**（F-134）与文件名 **`token-schema.json`**（F-146）；原页**未出现** `auth.tokenSchema` 这一路径式键名。camelCase 的 **`tokenSchema`** 字段口径属**同族另页（D6/D7）内容，非本篇来源**，本篇不引用其明细，需要时请回源对应官方页面。另注意：D5 远程 MCP 示例 URL 中出现的「tokenSchema 字段」是**乱入文本（勘误 E1）**，与 `token-schema.json` 机制**无关**，不可据此推断键名（F-105）。

## 七、图标规范（F-152）

| 项目 | 要求 |
| --- | --- |
| 格式 | SVG（推荐）、PNG 或 JPG |
| 文件名 | `icon.svg`、`icon.png` 或 `icon.jpg` |
| 尺寸 | PNG/JPG 建议 **64×64 px** |
| 背景 | 建议透明 |
| 风格 | 简洁清晰，小尺寸下可辨识 |

## 八、提交前检查与提交审核

**提交前检查共 11 项**（F-153）：① 已选择 MCP 或 CLI 接入方案，目录结构符合规范；② `source` 使用 kebab-case 且全局唯一；③ 连接器名称、说明和中英文示例填写完整；④ MCP 仅配置一个 Server，远程地址使用 HTTPS；⑤ 或 CLI 已验证安装、认证、状态检查、登出和跨平台行为；⑥ CLI 方案已验证登录态跨重启有效，且 `unAuth` 能正确清理授权；⑦ 涉及 OAuth 时已实现元数据发现、动态注册与 PKCE 校验，并接受约定的回调地址；⑧ 使用自填 Token 模式时，`${VAR}` 占位符与表单字段 key 一一对应，敏感字段为 `password` 类型；⑨ Skill 能准确指导 AI 调用全部核心能力；⑩ 未在任何文件中写入真实凭证；⑪ 图标清晰可辨，版本号和最低 WorkBuddy 版本声明正确，且已覆盖超时、授权失效、参数错误等常见异常。

**提交与同步**：准备完成后，将连接器目录**打包并提交 WorkBuddy 团队审核**；审核通过后连接器将**进入连接器市场**；后续更新**重新提交审核即可，通常在 10～15 分钟内同步生效**（F-154）。

> **边界与未给项**：
> - 文档**未给出**连接器的**审核时长**（仅 F-154 给出同步生效的「10～15 分钟」，非审核时长）；连接器审核时长属**官方未给**。
> - 文档**未给出**接口限流/配额、席位上限等数字（全局限额属**官方未给**）；`MCP Server` 自述的可用性「不低于 99.9%」与「单次请求 30 秒内响应」为**建议值**而非平台硬门槛（F-100、F-101）。
> - 本篇及全束**未在本机实跑**任何连接、鉴权、OAuth 回调或提交审核流程，上述要求均属**文档声称**，不得写成「已验证可用 / 已通过审核」。

同束入口：[连接器页 F 编号事实](../references/article-source.md)｜[核验报告（含 E1/E3）](../references/verification.md)｜[页级采集台账](../references/source-manifest.md)｜[构建并提交一个连接器（示例）](../examples/02-build-and-submit-a-connector.md)。相关平级束：[WorkBuddy 官方站点与四区文档](../../workbuddy-official-docs/index.md)（产品侧 MCP/连接器口径）。
