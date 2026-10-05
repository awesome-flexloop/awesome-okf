---
type: Concept
title: "连接器系统：25 连接器与 MCP 三模式网关"
description: "Octop 把一切外部能力统一抽象为 MCP 工具：remote/gateway/internal 三种接入模式、8 种鉴权、25 项目录、OAuth 2.1 PKCE/DCR/PRM、Fernet 凭证保管、13 个进程内适配器与企查查 internal 特例。"
tags: [octop, connectors, mcp, oauth, gateway, adapters]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: "Octop 源码事实清单 F-276~F-315、F-382~F-383"
  - id: catalog
    resource: /references/connectors-catalog.md
    title: 连接器目录与 MCP 三模式网关信源登记
---

# 连接器系统：25 连接器与 MCP 三模式网关

在 Octop 里，"帮我查腾讯文档""读一封 QQ 邮箱""问企查查这家公司"都走同一套抽象：**外部能力即 MCP 工具**。Agent 不直接调用某个 SDK，而是从 MCP server 上发现 `tools/list`、再发起 `tools/call`；连接器子系统负责把厂商各异的 HTTP API、CLI 命令、OAuth 流程统一翻译成这一面。连接器目录的逐项信源登记见 [/references/connectors-catalog.md](../references/connectors-catalog.md)。

## 统一模型：一切外部能力都是 MCP 工具

连接器实例在装配给 harness 时得到一个形如 `f"{kind}__{instance_id}"` 的 MCP server 名（F-284），其工具在 LangChain 侧再被命名为 `sanitize_llm_tool_name(f"{mcp_server_name}_{name}")`（F-301）。因此 Agent 眼里只有"某个 MCP server 提供了若干工具"，厂商差异被收敛到三个维度：

- **传输**：`RemoteTransport = Literal["raw_http", "streamable_http", "sse"]`（F-277）；
- **鉴权**：8 种 `AuthKind`（见下节）；
- **运行位置**：`McpMode` 三模式（见下节）。

自定义 MCP 也复用同一模型，kind 固定 `"custom-mcp"`，合成 ID 形如 `custom:{name}`，共享实例为 `custom:{parent}:{name}`（F-288）。

## 类型字典：AuthKind 8 种与 ConnectorCategory 7 类

> 事实单 F-276/F-278 措辞为"枚举"，经源码核实二者实为 `typing.Literal` 类型别名（非 `enum.Enum`），此处按源码逐字呈现（信源登记同此订正）。

```python
AuthKind = Literal[
    "personal_token", "oauth2", "auth_code", "api_key",
    "imap_app_password", "session_cookie", "api_credentials", "custom_fields",
]                                   # 8 个，catalog.py:8-17（F-276）

ConnectorCategory = Literal[
    "office", "knowledge", "travel", "productivity",
    "media", "professional", "self_hosted",
]                                   # 7 个，catalog.py:22-30（F-278）
```

凭证字段类型只有 4 种：`CredentialFieldType = Literal["text", "password", "url", "tags"]`（F-277）。目录条目 `ConnectorCatalogEntry` 是 frozen dataclass，字段含 kind、name、auth_kind、phase（`available`/`coming_soon`）、mcp_mode、category、可选的 oauth_issuer/mcp_url/oauth_scopes/credential_fields/remote_transport 等（F-278）；25 项目录的 `phase` 全部为 `"available"`（F-279）。

## McpMode 三模式选型

`McpMode = Literal["remote", "gateway", "internal"]`（F-277）。catalog.py:54-56 的源码注释把三模式语义说得很直白：

| 模式 | 语义 | harness 如何连 | 目录条目数 |
|------|------|----------------|-----------|
| `remote` | harness 直连厂商 MCP URL | 标准 MCP HTTP/SSE 客户端 | 11（F-279） |
| `gateway` | 进程内 Python 适配器 | harness 配置仅为占位名，由 Octop 进程内桥接 | 13（F-279） |
| `internal` | Octop 托管的 HTTP MCP（`/api/internal/mcp`） | harness 经本机回环 HTTP 加载 | 1，仅 qcc（F-279） |

判定谓词同样写死在 catalog.py：`is_inprocess_gateway`（mode=="gateway"）、`uses_internal_http_mcp`（mode=="internal"）、`is_mcp_oauth_remote`（oauth2 且 mode∈{remote,internal} 且 issuer/mcp_url 齐全）（F-278）。

internal 模式的回环 URL 模板（F-284）：

```python
f"http://{host}:{config.port}/api/internal/mcp/{gateway_kind}/{instance_id}?token={token_q}"
# host 为 0.0.0.0 / :: 时折为 127.0.0.1；token 由 secrets.token_urlsafe(32) 生成
```

gateway/internal 两类实例创建时都会生成 internal_token（F-286）。

## 25 项目录分布

`_CATALOG` 是起点 `catalog.py:110` 的 tuple，经计数恰 25 项（F-279）。模式分布 13/1/11，按类目则横跨办公、知识、差旅、媒体、专业服务等：

| 类目 | kind（逐字） |
|------|--------------|
| office | tencent-docs、tencent-meeting、tencent-lexiang、tencent-weiyun、tencent-ardot、feishu-cli、wecom-cli（F-278、F-279） |
| knowledge | tencent-ima、youdao-note、notion、openalex、weknora（F-279） |
| travel | fliggy、baidu-map、ctrip-wendao、meituan-travel、didi（F-279） |
| productivity | qq-mail、dida365（F-279） |
| media | tencent-news、wechat-reading、qq-music（F-279） |
| professional | yuandian、qcc（F-279） |
| self_hosted | dify（F-279） |

逐行的 auth_kind、transport、URL 与工具白名单见 [/references/connectors-catalog.md](../references/connectors-catalog.md) 第 1 节大表。一个容易踩坑的细节：**目录项没有 `default_open` 字段**——默认开启是实例级 `config_json` 的运行时键，`read_default_open` 仅在值 `is True` 时认作开启（F-294）。

## remote 模式：直连厂商，鉴权头各有暗号

builder.py 为不同厂商写了专门的 URL 与请求头（F-285、F-286）：

| kind | URL / 鉴权要点 |
|------|----------------|
| tencent-docs | `https://docs.qq.com/openapi/mcp`，Authorization 头直传 token（F-285） |
| tencent-weiyun | `https://www.weiyun.com/api/v3/mcpserver`，头含 `mcp_token`（F-285） |
| tencent-meeting | `https://mcp.meeting.tencent.com/mcp/wemeet-open/v1`，头 X-Tencent-Meeting-Token + X-Skill-Version: `v1.0.1`（F-285） |
| youdao-note | SSE 端点 `https://open.mail.163.com/api/ynote/mcp/sse`，头 x-api-key（F-286） |
| didi | `https://mcp.didichuxing.com/mcp-servers` 派生 URL，streamable_http（F-284、F-279） |

凭证创建时还有前缀校验：微信读书必须 `wrk-`、QQ 音乐必须 `qmk-`、元典必须 `sk_`；腾讯 IMA 必填 client_id，乐享必填 company_from（F-286）。

## OAuth 2.1：PKCE + 动态注册 + PRM 发现

qcc、Notion、OpenAlex、滴答、腾讯设计 Ardot 这类 `auth_kind="oauth2"` 的连接器走动态客户端授权（F-281、F-297）：

```
1. PRM 发现：WWW-Authenticate 头
   → /.well-known/oauth-protected-resource{path}
   → 根路径；解析 resource_metadata="..."（发现缓存 TTL 3600s）   (F-299)
2. 拉授权服务器元数据：{issuer}/.well-known/oauth-authorization-server (F-298)
3. DCR 动态注册：client_name="Octop Connector"，
   grant_types=["authorization_code","refresh_token"]，
   token_endpoint_auth_method="none" 或 "client_secret_post"        (F-298)
4. 授权：code_challenge_method="S256"（PKCE）                       (F-298)
   verifier = secrets.token_urlsafe(64)，
   challenge = urlsafe_b64(sha256(verifier)) 去 "="                  (F-295)
5. 令牌表单 application/x-www-form-urlencoded，timeout 30           (F-298)
```

第 1 步的 `/.well-known/oauth-protected-resource` 正是 RFC 9728 定义的 PRM（Protected Resource Metadata）机制（F-299）。内置客户端表 `_BUILTIN_CLIENTS` 是空字典，客户端凭据按"环境变量 → settings → builtin"顺序解析（F-296）；元数据没有 `registration_endpoint` 即判定该 issuer 不支持动态授权，本地/LAN 地址跳过发现（F-299）。

## 凭证保管：一把 Fernet 钥匙

所有连接器凭证在落库前经同一把对称密钥加密（F-287）：

```python
_FERNET_KEY = "connector_fernet"
# 加密：Fernet.encrypt(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
# 解密反向（crypto.py:20-27）
```

CLI 类连接器的凭证保护更进一步：飞书 CLI 的 app secret 通过 `--app-secret-stdin` 写入、文件权限 0o600，并留指纹文件 `.octop_feishu_fingerprint`（pbkdf2_hmac sha256，10 000 次迭代，salt `b"octop.cli-creds.fingerprint.v1"`）（F-303、F-304）；企微 CLI 的 bot.enc/mcp_config.enc 用 AES-256-GCM（12 字节 nonce 前置）（F-305）。

## gateway 模式：13 个进程内适配器

`_ADAPTERS` 字典注册了 13 个适配器（F-300）：qq-mail、qq-music、fliggy、baidu-map、ctrip-wendao、meituan-travel、yuandian、tencent-ima、tencent-news、wechat-reading、feishu-cli、wecom-cli、weknora。它们实现同一个 Protocol（F-300）：

```python
class GatewayAdapter(Protocol):
    def list_tools(self): ...
    def call_tool(self, creds, name, args): ...
    def probe_credentials(self, creds): ...
```

适配器对外暴露的仍是标准 MCP 协议面：`MCP_PROTOCOL_VERSION = "2024-11-05"`，方法集合 initialize、notifications/initialized、tools/list、tools/call、ping，`serverInfo = {"name": f"octop-{kind}", "version": "0.1.0"}`，未知方法回 JSON-RPC `-32601`（F-301）。13 个适配器合计暴露 49 个工具，逐项清单见信源登记第 5 节（F-306~F-315）。典型两种形态：

- **HTTP API 翻译器**：如百度地图把 3 个工具映射到 `https://api.map.baidu.com/agent_plan/v1`（Bearer 头）（F-307）；元典把 5 个工具映射到 law/case/enterprise 等路由，X-API-Key 鉴权（F-314）。
- **邮箱/IMAP 翻译器**：qq-mail 适配器暴露 search_emails（limit 默认 10）/read_email/send_email，IMAP ID 自报 "Octop"/"1.0.0"，SMTP starttls 587、IMAP 993（F-310）；邮箱预设内置 qq 与 gmail 双组主机端口（imap.qq.com/993、smtp.qq.com/587 等），并覆盖 163/126/yeah 三域网易服务器，默认 IMAP 主机 imap.qq.com、连接超时 30s（F-290）。
- **本机 CLI 包装器**：feishu-cli/wecom-cli 把本机命令行能力翻成 MCP 工具。飞书适配器暴露 doc/base/calendar/im/help 5 个工具，argv 固定追加 `--format json`，`+` 快捷方式展开为 `--k v`、否则 `--params {json}`，身份用 `--as user|bot`，探测执行 `auth status --json`（F-315）。CLI 由 Octop 负责安装（feishu-cli → lark-cli / npm 包 `@larksuite/cli`；wecom-cli → `@wecom/cli`，安装超时 300s），错误提示明确"禁止在 Agent 终端中查找或安装该命令"（F-302、F-303）。

## internal 特例：企查查 qcc

qcc 是 25 项中唯一的 internal 模式（F-279）。它不是普通 HTTP 转发，而是 Octop 在 `/api/internal/mcp` 后面代持 OAuth、代理 5 个受保护资源（F-280、F-291）：

- issuer `https://agent.qcc.com`，5 个资源 company/risk/ipr/operation/executive，各自地址 `f"{ISSUER}/mcp/{name}/stream"`，工具名拼成 `f"{resource}__{tool_name}"`（F-291、F-292）；
- PRM 路径模板 `/mcp/.well-known/oauth-protected-resource/{resource}/stream`（F-292）；
- 内部入口仅放行 `tools/list` 与 `tools/call`，失败统一回 JSON-RPC `-32603` 与字面信息 "QCC MCP request failed; check connection or authorize again"（F-283）；
- httpx 客户端 timeout=30、follow_redirects=False、trust_env=False，401 判未授权，刷新偏斜窗口 120s（F-282、F-292）。

文档侧的验收记录可佐证该链路真实跑通：2026-09-24 在提交 `bf1ea4e` 上"五类 Server 共发现 6 个精选工具"，解绑返回 204，已撤销刷新令牌再刷新返回 400/`invalid_grant`（F-383）。

## 工具缓存与凭证探测

远端 MCP 的工具清单不重复拉取：指纹键为 `("transport","url","headers","command","args","env")`，把值 JSON `sort_keys` 后取 sha256 前 16 字符（F-294）；共享工具用 `wrap_tools_for_shared_use` 包成 StructuredTool，并以 asyncio.Lock 串行化（F-294）。

探测（"测试连接"）同样按 MCP 规范握手：initialize 报文 protocolVersion `"2024-11-05"`、clientInfo `{"name":"octop","version":"0.1"}`（F-293）；SSE/streamable 超时 20s 重试 2 次，stdio 超时 25s，本地 weknora 探 `http://127.0.0.1:8080/health`（timeout 2.0）；HTTP 401/403 归认证错误、其余归连接错误（F-293）。

## 自定义 MCP 与安全边界

除 25 个内置目录项外，用户可挂载自定义 MCP：transport 支持 streamable_http/stdio（传入 http 归一为 streamable_http）（F-289）。URL 校验对公网地址强制 HTTPS 并做 SSRF 检查，内网地址放行；stdio 规格必填 command，server 名仅允许 `^[A-Za-z0-9_-]+$`（F-288、F-289）。

## 相关概念

- [/concepts/03-gateway-channels.md](03-gateway-channels.md) —— 连接器之外的 IM 通道与消息路由
- [/concepts/00-architecture.md](00-architecture.md) —— connectors 在 infra 层中的位置
- [/references/connectors-catalog.md](../references/connectors-catalog.md) —— 25 项逐条信源登记
