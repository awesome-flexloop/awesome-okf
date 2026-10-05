---
type: Reference
title: "连接器目录与 MCP 三模式网关信源登记"
description: "Octop connectors 子系统源码信源登记：25 项静态连接器目录、AuthKind 等 Literal 字典、remote/gateway/internal 三模式、OAuth 2.1 PKCE/DCR/PRM、13 个进程序适配器与凭证加密。"
tags: [octop, connectors, mcp, catalog, oauth, gateway, adapters]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: src
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-276~F-315、F-382~F-383
---

# 连接器目录与 MCP 三模式网关

本信源登记 `src/octop/infra/connectors/`（含 `oauth/`、`gateway/`、`gateway/adapters/`）与 `docs/connectors-qcc.md` 的全部可验证事实。源码版本 v1.0.2b5（commit e473dd3c，MIT）。

## 1. 连接器总览（_CATALOG 25 项）

`_CATALOG` 为 `tuple[ConnectorCatalogEntry, ...]`，起点 `src/octop/infra/connectors/catalog.py:110`，经计数恰 25 项，kind 顺序与下表逐行一致；25 项 `phase` 全部为 `"available"`（F-279）。

| # | kind | 显示名 | mcp_mode | auth_kind | category | remote_transport | 目录项 default_open |
|---|------|--------|----------|-----------|----------|------------------|---------------------|
| 1 | tencent-docs | 腾讯文档 | remote | personal_token | office | raw_http（默认） | 目录无此字段¹ |
| 2 | tencent-ima | 腾讯 IMA | gateway | api_key | knowledge | raw_http（默认） | 目录无此字段¹ |
| 3 | tencent-meeting | 腾讯会议 | remote | personal_token | office | raw_http（默认） | 目录无此字段¹ |
| 4 | tencent-news | 腾讯新闻 | gateway | api_key | media | raw_http（默认） | 目录无此字段¹ |
| 5 | wechat-reading | 微信读书 | gateway | api_key | media | raw_http（默认） | 目录无此字段¹ |
| 6 | tencent-lexiang | 腾讯乐享 | remote | api_key | office | raw_http（默认） | 目录无此字段¹ |
| 7 | tencent-weiyun | 腾讯微云 | remote | personal_token | office | raw_http（默认） | 目录无此字段¹ |
| 8 | qq-mail | 个人邮箱 | gateway | imap_app_password | productivity | raw_http（默认） | 目录无此字段¹ |
| 9 | qq-music | QQ 音乐 | gateway | api_key | media | raw_http（默认） | 目录无此字段¹ |
| 10 | fliggy | 飞猪 | gateway | api_key | travel | raw_http（默认） | 目录无此字段¹ |
| 11 | baidu-map | 百度地图 | gateway | api_key | travel | raw_http（默认） | 目录无此字段¹ |
| 12 | ctrip-wendao | 携程问道 | gateway | api_key | travel | raw_http（默认） | 目录无此字段¹ |
| 13 | meituan-travel | 美团旅游助手 | gateway | api_key | travel | raw_http（默认） | 目录无此字段¹ |
| 14 | didi | 滴滴 | remote | api_key | travel | streamable_http | 目录无此字段¹ |
| 15 | yuandian | 元典 | gateway | api_key | professional | raw_http（默认） | 目录无此字段¹ |
| 16 | qcc | 企查查 | internal | oauth2 | professional | streamable_http | 目录无此字段¹ |
| 17 | tencent-ardot | 腾讯设计 Ardot | remote | oauth2 | office | raw_http（默认） | 目录无此字段¹ |
| 18 | youdao-note | 有道云笔记 | remote | personal_token | knowledge | raw_http（默认；builder 特判 SSE） | 目录无此字段¹ |
| 19 | notion | Notion | remote | oauth2 | knowledge | raw_http（默认） | 目录无此字段¹ |
| 20 | openalex | OpenAlex | remote | oauth2 | knowledge | streamable_http | 目录无此字段¹ |
| 21 | dida365 | 滴答清单 | remote | oauth2 | productivity | raw_http（默认） | 目录无此字段¹ |
| 22 | feishu-cli | 飞书 CLI | gateway | api_key | office | raw_http（默认） | 目录无此字段¹ |
| 23 | wecom-cli | 企业微信 CLI | gateway | api_key | office | raw_http（默认） | 目录无此字段¹ |
| 24 | weknora | WeKnora | gateway | custom_fields | knowledge | raw_http（默认） | 目录无此字段¹ |
| 25 | dify | Dify | remote | custom_fields | self_hosted | streamable_http | 目录无此字段¹ |

来源：F-279、F-280、F-281。

¹ **目录项不存在 `default_open` 字段**：`ConnectorCatalogEntry` 的字段尾项为 `remote_transport`（catalog.py:76），全表无默认开启属性。`default_open` 是**实例级** `config_json` 的运行时键——`knowledge/default_open.py` 的 `read_default_open` 仅在值 `is True` 时认作开启（F-294）；自定义 MCP 的规格元数据键集合 `_META_KEYS = frozenset({"enabled","display_name","default_open","shared"})` 同样属于实例规格而非目录项（F-288）。

**模式计数**（对 25 项逐条点数，catalog.py:110-585）：gateway 13 项（#2、#4、#5、#8、#9、#10、#11、#12、#13、#15、#22、#23、#24）、internal 仅 qcc 1 项（#16）、remote 11 项（F-279）。`remote_transport="streamable_http"` 的目录项 4 个：didi、qcc、openalex、dify（catalog.py:359、396、465、583）；youdao-note 目录默认 `raw_http`，实际由 builder 特判为 SSE 端点（F-286）。

## 2. 类型字典与数据结构

### 2.1 Literal 类型别名

> 事实单 F-276/F-278 措辞为"枚举"，经源码核实二者均为 `typing.Literal` 类型别名（非 `enum.Enum`），以下按源码逐字登记。

```python
AuthKind = Literal[
    "personal_token",
    "oauth2",
    "auth_code",
    "api_key",
    "imap_app_password",
    "session_cookie",
    "api_credentials",
    "custom_fields",
]                       # 8 成员，catalog.py:8-17（F-276）

CredentialFieldType = Literal["text", "password", "url", "tags"]        # catalog.py:19（F-277）
RemoteTransport = Literal["raw_http", "streamable_http", "sse"]         # catalog.py:20（F-277）
McpMode = Literal["remote", "gateway", "internal"]                      # catalog.py:21（F-277）

ConnectorCategory = Literal[
    "office", "knowledge", "travel", "productivity",
    "media", "professional", "self_hosted",
]                       # 7 成员，catalog.py:22-30（F-278）
# phase 的 Literal 字面为 available / coming_soon（catalog.py:53，F-278）
```

### 2.2 frozen 数据类与判定函数

`ConnectorCredentialField`（catalog.py:33-41）与 `ConnectorCatalogEntry`（catalog.py:44-76）均为 `@dataclass(frozen=True)`；后者字段含 kind、name、description、auth_kind、doc_url、icon、color、phase、mcp_mode、category，以及可选的 quick_auth_url/login_url/guide_url/manual_url/auth_hint、`allowed_tools: tuple[str, ...] | None`、oauth_issuer、mcp_url、oauth_resource、oauth_scopes、mcp_user_agent、credential_fields、remote_transport（F-278）。

```python
def is_inprocess_gateway(entry) -> bool:   # mcp_mode == "gateway"，catalog.py:79-81
def uses_internal_http_mcp(entry) -> bool: # mcp_mode == "internal"，catalog.py:84-86
def is_mcp_oauth_remote(entry) -> bool:    # auth_kind=="oauth2" 且 mode in {"remote","internal"}
                                           # 且 oauth_issuer、mcp_url 均非空，catalog.py:89-96
```

三模式语义（catalog.py:54-56 源码注释逐字）：remote = harness 直连厂商 URL；gateway = 进程序 Python 适配器，harness 配置仅为占位名；internal = Octop 托管的 HTTP MCP（`/api/internal/mcp`），harness 经 HTTP 加载。`mcp_oauth_remote_kinds()` 与 `get_mcp_oauth_remote(kind)` 按上述谓词筛选目录（catalog.py:99-107）。

来源：F-277、F-278。

## 3. OAuth 2.1 动态授权（PKCE / DCR / PRM）

OAuth 子系统位于 `src/octop/infra/connectors/oauth/`（6 个文件）。

| 文件 | 登记事实 |
|------|----------|
| pkce.py | `s256_challenge` 为 sha256 摘要后 urlsafe base64 并去除 `=`（:10-13）；verifier 由 `secrets.token_urlsafe(64)` 生成（:17）（F-295） |
| builtin.py | `_BUILTIN_CLIENTS: dict[str, tuple[str, str]] = {}` 为空字典（:10）；`resolve_client` 查找顺序为环境变量 → settings → builtin（F-296） |
| registry.py | `OAUTH_CTX_PREFIX = "connector.oauth.ctx."`（:23）；`_AUTH_CODE_PASSTHROUGH_KINDS: frozenset[str] = frozenset()` 为空（:25）；`oauth_mode_for_kind` 返回字面 `"dynamic"`；目标类型仅认 catalog 与 custom_mcp；flow 字面为 `"mcp"` 与 `"custom_mcp"`（F-297） |
| mcp.py | 授权服务器元数据 URL 为 `f"{issuer.rstrip('/')}/.well-known/oauth-authorization-server"`（:72）；DCR 默认 `client_name="Octop Connector"`、`grant_types=["authorization_code","refresh_token"]`、`token_endpoint_auth_method` 取 `"none"` 否则 `"client_secret_post"`（:97-105）；授权参数 `code_challenge_method="S256"`（:130）；令牌表单 Content-Type 为 application/x-www-form-urlencoded、timeout 30，元数据 GET timeout 20（F-298） |
| discovery.py | `_DISCOVERY_CACHE_TTL_SEC = 3600.0`（:23）；PRM URL 发现顺序：WWW-Authenticate 头 → `/.well-known/oauth-protected-resource{path}` → 根路径（:41-63）；解析正则字面 `resource_metadata\s*=\s*"([^"]+)"`（:18-21）；元数据无 registration_endpoint 即判不可用；本地/LAN 地址跳过发现（F-299） |
| __init__.py | 包再导出，合计 13 个名字 |

来源：F-295、F-296、F-297、F-298、F-299。

## 4. MCP 三模式配置构建与网关协议面

### 4.1 远端/internal MCP 构建（connectors/builder.py）

```python
_MCP_STREAMABLE_HTTP_ACCEPT = "application/json, text/event-stream"   # builder.py:23（F-284）
DIDI_MCP_BASE_URL = "https://mcp.didichuxing.com/mcp-servers"          # builder.py:25（F-284）
# mcp_server_name 形如 f"{kind}__{instance_id}"（builder.py:58-59，F-284）
# internal URL：f"http://{host}:{config.port}/api/internal/mcp/{gateway_kind}/{instance_id}?token={token_q}"
#   host 为 0.0.0.0 / :: 时折为 127.0.0.1（builder.py:62-73，F-284）
# internal token 由 secrets.token_urlsafe(32) 生成（builder.py:77，F-284）
```

远端特判 URL 与请求头（F-285、F-286）：

| kind | URL 字面 | 鉴权要点 | 行号 |
|------|----------|----------|------|
| tencent-docs | `https://docs.qq.com/openapi/mcp` | Authorization 头直传 token | builder.py:111 |
| tencent-weiyun | `https://www.weiyun.com/api/v3/mcpserver` | WyHeader 含 `mcp_token`（`normalize_weiyun_mcp_token`，:32） | builder.py:129 |
| tencent-meeting | `https://mcp.meeting.tencent.com/mcp/wemeet-open/v1` | 头 X-Tencent-Meeting-Token 与 X-Skill-Version: `v1.0.1` | builder.py:142-146 |
| tencent-lexiang | `https://mcp.lexiang-app.com/mcp?preset=meta` | 必填 company_from | builder.py:151 |
| youdao-note | `https://open.mail.163.com/api/ynote/mcp/sse`（SSE） | 请求头 x-api-key | builder.py:171-173 |
| didi | `f"{DIDI_MCP_BASE_URL}?key={...}"`（streamable_http） | query 携带 api_key | builder.py:97 |

`validate_create_credentials` 的令牌前缀校验（builder.py:324-337）：wechat-reading 必须 `wrk-` 前缀（:324）、qq-music 必须 `qmk-` 前缀（:329）、yuandian 必须 `sk_` 前缀（:334）；tencent-ima 必填 client_id；gateway/internal 两类均生成 internal_token（F-286）。

### 4.2 网关 MCP 协议面（gateway/protocol.py、registry.py、langchain.py）

- `MCP_PROTOCOL_VERSION = "2024-11-05"`（gateway/protocol.py:12）；协议方法名集合：initialize、notifications/initialized、tools/list、tools/call、ping；`serverInfo = {"name": f"octop-{kind}", "version": "0.1.0"}`；未知方法返回 JSON-RPC code `-32601`（protocol.py:68）（F-301）。
- `_ADAPTERS` 字典含 13 个键（gateway/registry.py:32-46）：qq-mail、qq-music、fliggy、baidu-map、ctrip-wendao、meituan-travel、yuandian、tencent-ima、tencent-news、wechat-reading、feishu-cli、wecom-cli、weknora（F-300）。
- `GatewayAdapter` 为 `typing.Protocol`，声明 3 个方法：`list_tools()`、`call_tool(creds, name, args)`、`probe_credentials(creds)`（registry.py:24-29）（F-300）。
- langchain 桥接工具名：`sanitize_llm_tool_name(f"{mcp_server_name}_{name}")`（gateway/langchain.py:69）（F-301）。

### 4.3 CLI 连接器子系统（feishu-cli / wecom-cli）

| 主题 | 登记事实 |
|------|----------|
| 目录解析 | `_CLI_KINDS = frozenset({"feishu-cli","wecom-cli"})`，解析顺序 cli_config_key → instance_id（gateway/cli_dirs.py:10）（F-302） |
| 子进程执行 | `DEFAULT_TIMEOUT_S = 30.0`、`_MAX_ERR_CHARS = 4000`；错误提示含字面"禁止在 Agent 终端中查找或安装该命令。"（gateway/cli_runner.py:11）（F-302） |
| 安装器 | `_INSTALL_TIMEOUT_S = 300.0`（cli_install.py:14）；CliInstallSpec 共 2 条：feishu-cli → 二进制 lark-cli / npm 包 `@larksuite/cli`，wecom-cli → wecom-cli / `@wecom/cli`；用户级前缀目录名 `_NPM_USER_PREFIX_NAME = ".npm-global"`（F-303） |
| 凭证指纹 | salt 字面 `b"octop.cli-creds.fingerprint.v1"`；pbkdf2_hmac sha256 迭代 `_ITERATIONS = 10_000`（gateway/cli_fingerprint.py）（F-303） |
| 飞书应用凭证 | 标记文件名 `.octop_feishu_fingerprint`；`_BRAND="feishu"`；配置目录环境变量 LARKSUITE_CLI_CONFIG_DIR；写入前 pop 掉 LARKSUITE_CLI_APP_ID/LARKSUITE_CLI_APP_SECRET；初始化命令 `config init --app-id ... --app-secret-stdin --brand feishu`；凭证文件权限 0o600（gateway/feishu_creds.py）（F-304） |
| 飞书用户授权 | 默认域名元组 `("all",)`、默认 scope `("search:docs:read",)`；命令含 `auth login --no-wait --json`、`--device-code`、`config default-as user`；tokenStatus 集合 expired、invalid、missing、revoked（gateway/feishu_user_auth.py）（F-304） |
| 企微凭证 | `_MCP_CONFIG_URL="https://qyapi.weixin.qq.com/cgi-bin/aibot/cli/get_mcp_config"`；标记文件 `.octop_wecom_fingerprint`；`_BIND_SOURCE_INTERACTIVE=1`；UA 形如 `f"WeComCLI/0.1.9 distribution/octop {system}/{machine}"`；AES-256-GCM（12 字节 nonce 前置密文）；磁盘文件名 `.encryption_key`、`bot.enc`、`mcp_config.enc`；签名 `sha256(f"{bot_secret}{bot_id}{now}{nonce}")`（gateway/wecom_creds.py）（F-305） |

来源：F-302、F-303、F-304、F-305。

## 5. 进程序网关适配器（13 个）

`src/octop/infra/connectors/gateway/adapters/` 经 Glob 实测 14 个 `.py`：13 个适配器加 `__init__.py`（F-306）。13 个适配器暴露的工具逐一点数如下（合计 49 个工具）。

| # | kind | 适配器模块 | 工具数 | 工具名（逐字） |
|---|------|-----------|--------|----------------|
| 1 | tencent-ima | tencent_ima.py | 14 | list_notebooks、list_notes、get_note、search_notes、create_note、append_note、list_knowledge_bases、list_addable_knowledge_bases、get_knowledge_base、list_knowledge、search_knowledge、import_urls、add_note_to_knowledge、get_media |
| 2 | qq-music | qq_music.py | 5 | search_music、list_charts、get_chart_detail、get_playlist_detail、listening_report |
| 3 | yuandian | yuandian.py | 5 | search_laws、search_cases、search_enterprises、get_enterprise、detect_hallucination |
| 4 | feishu-cli | feishu_cli.py | 5 | doc、base、calendar、im、help |
| 5 | qq-mail | qq_mail.py | 3 | search_emails、read_email、send_email |
| 6 | baidu-map | baidu_map.py | 3 | search_place、plan_direction、get_weather |
| 7 | weknora | weknora.py | 3 | list_knowledge_bases、search、read_document |
| 8 | wecom-cli | wecom_cli.py | 4 | doc、schedule、msg、help |
| 9 | fliggy | fliggy.py | 2 | fliggy_ai_search、fliggy_fast_search |
| 10 | wechat-reading | wechat_reading.py | 2 | list_bookshelf、get_book_notes |
| 11 | tencent-news | tencent_news.py | 1 | search_news |
| 12 | ctrip-wendao | ctrip_wendao.py | 1 | ask_wendao |
| 13 | meituan-travel | meituan_travel.py | 1 | travel_query |

来源：F-306、F-307、F-308、F-309、F-310、F-311、F-312、F-313、F-314、F-315。

各适配器端点与鉴权细节：

- **tencent_ima**：主机 `https://ima.qq.com`，请求头 ima-openapi-clientid、ima-openapi-apikey；分页参数 clamp 1-20（部分 1-50）；`import_urls` 上限 10；`add_note_to_knowledge` 的 media_type 字面值 11（F-312）。
- **qq_music**：BASE_URL `https://a.y.qq.com`，`SKILL_VERSION="0.0.3"`，令牌强制 qmk- 前缀（F-311）。
- **yuandian**：BASE_URL `https://open.chineselaw.com/open`，请求头 X-API-Key，令牌 sk_ 前缀；路由名 law_vector_search（POST）、case_vector_search（POST）、rh_enterpriseSearch（GET）、rh_company_info（GET）、hall_detect（POST，timeout 60，其余 4 个 timeout 45）（F-314）。
- **feishu_cli**：`_DOMAIN_BY_TOOL` 映射 doc→docs、base→base、calendar→calendar、im→im；`_USER_ONLY_SHORTCUTS=frozenset({("docs","+search")})`；argv 追加 `--format json`；`+` 快捷方式展开为 `--k v`，否则展开为 `--params {json}`；身份参数 `--as user|bot`；探测执行 `auth status --json`（F-315）。
- **qq_mail**：search_emails 的 limit 默认 10；IMAP ID 参数字面 `("name" "Octop" "version" "1.0.0" "vendor" "Octop" "support-email" "support@octop.local")`，并注册 `imaplib.Commands["ID"]=("AUTH","NONAUTH","SELECTED")`；SMTP starttls 默认端口 587，IMAP 端口 993（F-310）。
- **baidu_map**：BASE_URL `https://api.map.baidu.com/agent_plan/v1`，Bearer 认证头，探测入参 region 字面"北京"（F-307）。
- **weknora**：`_MAX_RESULTS=8`、`_MAX_CHUNK_CHARS=1200`；请求头 X-API-Key、X-Tenant-ID；路径含 /knowledge-bases、/knowledge-search（params resource_urls 取 handle）、/knowledge/{id}、/chunks/{id}；read_document 的 page_size clamp 1-50、默认 20（F-314）。
- **wecom_cli**：`_CATEGORIES=("doc","schedule","msg")`；环境变量 WECOM_CLI_CONFIG_DIR；普通调用 argv 为 `[binary, name, method, json.dumps(payload, ...)]`，help 为 `[binary, category, "--help"]`（F-315）。
- **fliggy**：MCP_URL `https://flyai.open.fliggy.com/mcp`；`_SIGN_SECRET="XSbdYnucPARDc9knhD8+X6hxdD1Nh6ZGI6Hadg25kBw="`、`_TTID="ai2c(sk.clawhub)"`；签名头 x-flyai-sign-ver 值 `"7"`、x-flyai-sign-alg 值 `"hmac-sha256"`；canonical 串形如 `f"POST\n/mcp\n{ts}\n{nonce}\n{digest}\n{digest}"`；x-ff-ctx 经 AESGCM 生成（F-309）。
- **wechat_reading**：WEREAD_GATEWAY_URL `https://i.weread.qq.com/api/agent/gateway`，WEREAD_SKILL_VERSION `"1.0.3"`，令牌强制 wrk- 前缀（F-313）。
- **tencent_news**：OPENAPI_SEARCH_URL `https://openapi.inews.qq.com/api/v1/agent/search`；`_CALLER_SKILL="octop_tencent-news_0.1"`；请求头 Skill-Request-Id、Caller-Skill；limit clamp 1-50、默认 10；错误码字面 4006（F-313）。
- **ctrip_wendao**：QUERY_URL `https://wendao-skill-prod.ctrip.com/skill/query`；令牌正则 `^[0-9a-f]{32}$`；请求体含 `"source":"octop"`；timeout 60（F-308）。
- **meituan_travel**：QUERY_URL `https://mcp-open-cater.meituan.com/v1/api/voyage/openapi/query`；令牌正则 `^[0-9a-f]{32,}$`；timeout 120；Authorization 直传 raw token（F-308）。

## 6. 凭证保管、自定义 MCP 与周边安全机制

### 6.1 Fernet 凭证加密

`_FERNET_KEY = "connector_fernet"`（connectors/crypto.py:12）；加密路径为 `json.dumps(payload, ensure_ascii=False)` 后 utf-8 编码再经 Fernet 加密，解密反向（crypto.py:20-27）（F-287）。

### 6.2 自定义 MCP（custom_mcp.py）

```python
CUSTOM_MCP_KIND = "custom-mcp"                                   # :16（F-288）
CUSTOM_MCP_DISPLAY_NAME = "自定义 MCP"                            # :17（F-288）
_SERVER_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")                # :19（F-288）
_META_KEYS = frozenset({"enabled","display_name","default_open","shared"})  # :20（F-288）
_DISPLAY_NAME_MAX = 64
Transport = Literal["streamable_http", "stdio"]                  # :27（F-288）
# 合成 ID 形态：custom:{name} / 共享实例 custom:{parent}:{name} / custom__{parent}__{name}（:34-43，F-288）
```

`normalize_server_spec` 接受 streamable_http/stdio/http，其中 http 归一为 streamable_http（:173-176）；`validate_mcp_http_url` 对公网地址强制 HTTPS 并做 SSRF 校验、内网地址放行（:118-166）；stdio 规格必填 command（F-289）。

### 6.3 邮箱预设

qq=(imap.qq.com, 993, smtp.qq.com, 587)、gmail=(imap.gmail.com, 993, smtp.gmail.com, 587)（mail_servers.py:9-12）；`_NETEASE_DOMAIN_SERVERS` 覆盖 163.com、126.com、yeah.net 三域（:15-19）；DEFAULT_IMAP_HOST=imap.qq.com、DEFAULT_SMTP_HOST=smtp.qq.com、IMAP_CONNECT_TIMEOUT=30（:25-27）（F-290）。

### 6.4 MCP 工具缓存与 default_open

`_FINGERPRINT_KEYS = ("transport","url","headers","command","args","env")`（mcp_tool_cache.py:13-20）；指纹为 JSON `sort_keys` 后 sha256 取前 16 字符（:36-37）；`wrap_tools_for_shared_use` 生成 StructuredTool 并以 asyncio.Lock 串行化（F-294）。包 `__init__.py` 注释字面为 "Connector catalog, credential handling, and MCP config builders."；`read_default_open` 仅在值 `is True` 时认作开启（F-294）。

### 6.5 凭证探测（probe.py）

MCP initialize 报文 protocolVersion 字面 `"2024-11-05"`，clientInfo 为 `{"name":"octop","version":"0.1"}`（probe.py:433-436）；本地 weknora 探测地址 `http://127.0.0.1:8080/health`、timeout 2.0（:32-58）；SSE/streamable 超时 20、重试 2 次，stdio 超时 25（:550）；`_REMOTE_STATIC_TOOL_KINDS = frozenset({"tencent-weiyun"})`（:327）；HTTP 401/403 归为认证错误类，其余归连接错误类（F-293）。

### 6.6 企查查 internal MCP 专项

- 目录项字段：oauth_issuer `https://agent.qcc.com`、mcp_url `https://agent.qcc.com/mcp/company/stream`、oauth_resource 同址、oauth_scopes `mcp:tools`、remote_transport=streamable_http（catalog.py:392-396）（F-280）。
- `qcc.py`：`ISSUER = "https://agent.qcc.com"`（:15）；`RESOURCES` 含 5 键 company、risk、ipr、operation、executive，值为 `f"{ISSUER}/mcp/{name}/stream"`（:16-19）；`PREFERRED_TOOL_SUFFIXES` frozenset 含 get_company_profile、get_change_records、get_business_exception、get_patent_info、get_administrative_license、get_executive_positions 共 6 项（:24-33）；`_METADATA_TTL_SEC = 600.0`（F-291）。
- PRM 路径模板 `/mcp/.well-known/oauth-protected-resource/{resource}/stream`（:62）；工具名拼接 `f"{resource}__{tool['name']}"`（:129）；httpx 客户端 timeout=30、follow_redirects=False、trust_env=False（:84-89）；HTTP 401 判未授权（:155-158）；revoke 请求 POST 表单含 token_type_hint=refresh_token（F-292）。
- 服务层：`_OAUTH_REFRESH_SKEW_SEC = 120`（service.py:52）；`_QCC_LOCKS` 为 WeakKeyDictionary（:55）；`ConnectorNameTakenError` 定义于 :58；`ConnectorService` 定义于 :78（F-282）。`handle_qcc_request` 仅放行方法名 `tools/list` 与 `tools/call`，JSON-RPC 错误 code `-32603`，错误信息字面 "QCC MCP request failed; check connection or authorize again"（service.py:219-260）（F-283）。
- 文档侧（docs/connectors-qcc.md）：表格列出 5 个 MCP 地址与工具名前缀——company→`https://agent.qcc.com/mcp/company/stream`/`company__`、risk→`.../risk/stream`/`risk__`、ipr→`.../ipr/stream`/`ipr__`、operation→`.../operation/stream`/`operation__`、executive→`.../executive/stream`/`executive__`（:5-11）；OAuth 回调路径字面 `/api/connectors/oauth/callback`、Client Name `Octop Connector`、scope `mcp:tools`（:19-20）（F-382）。
- 验收记录：2026-09-24 在提交 `bf1ea4e`、实例 `127.0.0.1:8089` 上，"五类 Server 共发现 6 个精选工具"；解绑返回 204、旧内部入口 404、已撤销刷新令牌再刷新返回 400/`invalid_grant`（docs/connectors-qcc.md:47-54）（F-383）。

### 6.7 其他 OAuth MCP 目录项特殊字段

notion 条目 mcp_user_agent 字面 `octop-connector/0.1`（catalog.py:446；issuer `https://mcp.notion.com`、mcp_url `https://mcp.notion.com/mcp`）；openalex scopes 字面 `openalex:query`（issuer `https://mcp.openalex.org`）；dida365 scopes 字面 `tasks:read tasks:write`（issuer `https://dida365.com`）；tencent-ardot issuer `https://ardot.tencent.com`、mcp_url `https://ardot.tencent.com/mcp`（F-281）。

**custom_fields 凭证表单**：weknora 定义 4 个 credential_fields——base_url（url，必填，placeholder `http://127.0.0.1:8080 或 https://weknora.example.com`）、api_key（password，可选，secret）、tenant_id（可选）、knowledge_base_ids（tags，可选）（catalog.py:529-559）；dify 定义 1 个——mcp_url（url，secret，完整含访问标识的 MCP Server URL）（catalog.py:573-582）。tencent-docs allowed_tools 10 个、tencent-weiyun allowed_tools 12 个（catalog.py:126-137、231-244），其余条目 allowed_tools 为 None（不限制）。

## 相关概念

- [/concepts/03-gateway-channels.md](../concepts/03-gateway-channels.md)
- [/concepts/00-architecture.md](../concepts/00-architecture.md)
- [/references/gateway.md](./gateway.md)
