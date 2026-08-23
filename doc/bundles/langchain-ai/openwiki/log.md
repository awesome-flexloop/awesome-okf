---
type: log
scope: openwiki
name: log
version: "0.3.3"
source: https://github.com/langchain-ai/openwiki
description: OpenWiki OKF bundle 生成日志
---

# 生成日志

## 2026-08-23

- **OKF 版本**：0.2
- **Bundle 版本**：0.3.3
- **源码版本**：openwiki v0.3.3（package.json）
- **源码路径**：`external/libs/ai/langchain-ai/openwiki/src/`

### R（阅读）

阅读了以下核心模块并提取事实：

- `agent/index.ts`（~2488 行）：runOpenWikiAgent、createOpenWikiAgent、createModel、createAgentBackend、checkpoint 管理、流式事件解析、OpenRouter debug fetch
- `agent/types.ts`（61 行）：OpenWikiCommand、OpenWikiRunResult、OpenWikiRunEvent、OpenWikiRunOptions、RunContext
- `agent/utils.ts`（560 行）：createRunContext、getUpdateNoopStatus、writeLastUpdateMetadata、createOpenWikiContentSnapshot、临时文件清理
- `auth/oauth.ts`（635 行）：runOAuthAuth、createCallbackServer、PKCE、MCP 动态客户端注册、Slack token 映射
- `auth/tokens.ts`（287 行）：getOAuthAccessToken、refreshOAuthAccessToken、isOAuthAccessTokenExpired
- `auth/ngrok.ts`（323 行）：startNgrokTunnel、getRedirectUriFromNgrokTunnels、ngrok API 轮询发现
- `auth/types.ts`（39 行）：AuthProviderId、OAuthProviderConfig、OAuthTokenMapping
- `cli/cli.tsx`（116 行）：shebang 入口、installCrashGuard、命令分派、Ink TUI/Print 模式选择
- `cli/guards.ts`（24 行）：isRecord、isDiagnosticValue
- `cli/runners.ts`（375 行）：runPrintCommand、runAuthCommand、runNgrokCommand、runCronCommand、runIngestCommand、runVisualizeCommand
- `cli/startup.ts`（147 行）：resolveStartupCommand、TTY/凭证/消息守卫
- `cli/debug.ts`（16 行）：isDebugMode、shouldShowCredentialDiagnostics
- `cli/format.ts`（52 行）：isExitMessage、formatCount、formatCwd、getDisplayModelId
- `config/env.ts`（680 行）：loadOpenWikiEnv、saveOpenWikiEnv、MANAGED_ENV_KEYS、parseEnv、凭证诊断
- `config/constants.ts`（前 120 行）：OpenWikiProvider 类型、环境变量键名常量、默认值
- `version.ts`（81 行）：OPENWIKI_VERSION、OPENWIKI_PRODUCER_ACTOR
- `package.json`：依赖、脚本、元信息

共提取 **76 条编号事实**，写入 `spec/facts.md`。

### I（洞察）

提炼 3 个架构洞察，写入 `spec/insights.md`：

1. **Agent-CLI 分层架构**：两级 API 职责分离（runOpenWikiAgent 边界 vs createOpenWikiAgent 工厂）、三种命令模式差异、DeepAgent 图组装
2. **OAuth + Token 管理**：PKCE 本地回调、RFC 7591 动态客户端注册、60 秒时钟偏移容差的 token 刷新、Slack 嵌套 token 处理
3. **auth-ngrok 内网穿透**：预留/随机域名双模式、ngrok 本地 API 轮询发现、环境变量桥接 OAuth 流程、安全考量

### E（导出）

生成文档文件：

- `index.md` — Bundle 根索引（okf_version: "0.2"）
- `concepts/overview.md` — 项目总览
- `concepts/agent-system.md` — Agent 系统架构
- `concepts/auth-cli.md` — Auth 与 CLI 认证体系
- `concepts/index.md` — 概念索引
- `references/api.md` — Agent 与 CLI API 参考
- `references/env-config.md` — 配置与环境变量参考
- `references/index.md` — 参考索引
- `examples/oauth-ngrok.md` — OAuth + ngrok 使用示例
- `examples/index.md` — 示例索引

交叉链接统一使用 `/langchain-ai/openwiki/` 前缀，文件名 kebab-case，正文中文。

### V（验证）

- Grep 验证所有导出的函数名/类名在 `.ts`/`.tsx` 源码中存在
- Frontmatter 格式检查（type、scope、name、version、source、description）
- 内部链接完整性检查
