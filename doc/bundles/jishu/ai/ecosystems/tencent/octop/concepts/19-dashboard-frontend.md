---
type: Concept
title: "Dashboard 前端架构"
description: "octop-dashboard 0.1.0 的 React 18 + Vite 6 + antd 5 技术栈、77 个 API 层 TS 文件三层划分、pathToKey/routeConfigs 路由表、38 个页面与 19 键侧边栏、hooks/locales/PWA 装配与构建产物衔接。"
tags: [octop, dashboard, react, vite, antd, pwa, frontend, i18n, routing]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-566~F-575（v1.0.2b5，commit e473dd3c）
  - id: map
    resource: /references/source-v1-map.md
    title: Octop v1.0.2b5 源码地图（§7 前端构建链）
---

# Dashboard 前端架构

Dashboard 是 Octop 唯一的 GUI 形态：一个以 PWA 方式安装的 React 单页应用，开发时由 Vite 独立起服务，发布时构建进 Python wheel，由后端 FastAPI 的 SPA fallback 直接托管。包名 `octop-dashboard`，版本 `0.1.0`（与后端 OpenAPI 自报版本一致，但独立于发行版 `1.0.2b5`），`private: true`、`"type": "module"`（F-566）。

## 技术栈与规模

`package.json` 实测 **30 条 dependencies、26 条 devDependencies、14 条 scripts**（F-566）。关键版本逐字：

| 面 | 选型与版本 |
|---|---|
| UI 框架 | react / react-dom `^18`、antd `^5.29.1`、antd-style `^3.7.1`、ahooks |
| 路由 | react-router-dom `^7.13.0` |
| 构建 | vite `^6.3.5`、typescript `~5.8.3`、vite-plugin-pwa `^0.21.2` |
| 终端/图形 | @xterm/xterm `5.5.0`（+fit/web-links 插件）、mermaid `^11.13.0`、recharts `^3.10.1` |
| 富内容 | react-markdown 10、remark-gfm/remark-math/rehype-katex、react-pdf、docx-preview、@aiden0z/pptx-renderer、@monaco-editor/react |
| 国际化 | i18next `^25.8.4`、react-i18next |
| 测试 | vitest 3、@testing-library/react、jsdom |

14 条 scripts 为 `dev`、`build`、`build:docker`、`build:prod`、`build:test`、`format`、`format:check`、`lint`、`test`、`test:watch`、`test:coverage`、`preview`、`preview:prod`、`preview:test`；其中 `build = tsc -b && vite build`，而 **`build:docker = vite build`**——镜像内构建跳过完整 tsc 类型检查（F-566，Dockerfile 第 58 行有同样注释）。`overrides` 钉了两个供应链相关版本：`serialize-javascript ^7.0.3` 与 `@rollup/plugin-terser ^1.0.0`（F-566）。

## 构建输出与后端托管的衔接

Vite 的输出目录不在前端工程内，而是直接指回 Python 包（F-567）：

```ts
// vite.config.ts
outDir: path.resolve(__dirname, "../src/octop/dashboard"),
emptyOutDir: true,
chunkSizeWarningLimit: 1600,
maxParallelFileOps: 3,
```

```
dashboard/  ──vite build──▶  ../src/octop/dashboard/  ──hatch include──▶  wheel
                                      │
浏览器 ◀── FastAPI SPA fallback（Path(__file__).parent.parent / "dashboard"）
```

后端 catch-all 路由对 `sw.js`/`manifest.json`/`index.html` 给 `no-cache`，`assets/` 给 `public, max-age=31536000, immutable`，`api/`、`ws/` 前缀直接 404，且 hash asset 缺失必须 404 而不是回退 index.html（旧 shell 升级场景）。开发期 Vite dev server 监听 `0.0.0.0:5173`（端口取 `VITE_DEV_PORT`），把 `/api` 代理到 `http://127.0.0.1:${VITE_API_PORT||8088}`，并开启 `xfwd` 与 WebSocket 代理（F-567）。

PWA 策略刻意保守（F-567）：`registerType="prompt"`（有新版先问用户）、`injectRegister=false`、`manifest=false`（改用静态 `public/manifest.json`）、`navigateFallback=null`（不做 SW 离线回退，避免把鉴权 API 缓存进 SW）、`clientsClaim=true`、`skipWaiting=false`、单缓存文件上限 3MiB。manifest 中 name/short_name 均为 "Octop"、`display: standalone`、`lang: zh-CN`，4 个图标（192/512 普通、512 maskable、apple-touch 180）（F-567）。

## API 层：77 个 TS 文件的三层划分

`src/api/` 全量 Glob 实测 **77 个 `.ts`**，按职责分三层（F-568）：

| 层 | 文件数 | 内容 |
|---|---:|---|
| `api/modules/` | 55（=51 业务 + 4 测试） | 按资源切分的端点封装，如 `agentChat.ts`、`octopAgents.ts`、`memoryDashboard.ts`、`bridge.ts`、`mobile.ts`、`sso.ts`；4 个测试为 sso/skillPackages/publishedExperts/knowledgeBases |
| `api/types/` | 15 | 纯类型：agent、chat、channel、cronjob、provider、mbti、hitl、env、embedding 等 |
| `api/` 根 | 7 | `config.ts`、`request.ts`、`index.ts`、`probeHealth.ts` + 3 个 request 测试 |

底层三件套：

- **config.ts**：`declare const BASE_URL: string`；`getApiUrl(path)` 拼 `${BASE_URL||""}/api${path}`；`getWsUrl` 把 `http://`→`ws://`、`https://`→`wss://`，同源空 BASE_URL 时按 `window.location` 协议推导（F-569）。
- **request.ts**：统一 fetch 封装，导出 `request`/`requestBlob`/`requestStream`/`requestUpload`/`probeAuthResource` 五个函数（F-570）。
- **probeHealth.ts**：探活与鉴权资源探测，供登录页/健康检查使用。

`request()` 的处理链值得展开（F-570）：

```ts
const AUTH_TOKEN_KEY = "auth_token";
const AUTH_REMEMBER_PREF_KEY = "auth_remember_pref";
export const UNAUTHORIZED_EVENT = "octop:unauthorized";
export const FORBIDDEN_EVENT = "octop:forbidden";
export const ACCESS_TOKEN_RESPONSE_HEADER = "X-Octop-Access-Token";
```

请求前先 `assertNotSetupLocked`；响应依次处理 503（setup 锁定）→ 401（发可取消的未授权事件，由 React 树内监听器接管跳登录，避免整页撕裂）→ 续期头（200 响应若带 `X-Octop-Access-Token` 就调 `applyRenewedAccessToken` 换新）→ 204 回 `undefined`、非 JSON 回 text。令牌存储遵循「记住登录状态」：remember=false 时用 sessionStorage，关闭标签页即失效（F-570）。

## 路由表：41 键 pathToKey 与 63 条 routeConfigs

路由不是散落在页面里的 `<Route>`，而是两张集中式数据表（F-571、F-572）：

```
                         routes/index.tsxf
        ┌──────────────────────┴──────────────────────┐
 pathToKey: Record<string,string>（41 键）   routeConfigs: RouteConfig[]（63 条）
 URL path → 侧边栏高亮 key                    路径 → 元素/包装器/重定向
```

- `pathToKey` 实测 **41 键**，覆盖 chat、experts、tasks、token-usage、personalization 系列、workbench 系列、remote-desktop 系列、acp、admin-users、models、admin-storage、admin-plugins、admin-security、admin-advanced 等；同文件还导出 `FULLSCREEN_PATHS`（10 条）、`resolveSelectedKey` 与 `isWorkbenchPath`/`isRemoteDesktopPath`/`isPersonalizationPath` 三个判定函数（F-571）。
- `routeConfigs` 实测 **63 条**（Grep `element:` 64 命中减去 interface 声明 1）。除业务页外包含 3 个 chat wrapper（`useWrapper`）、若干 `RedirectPreserveSearch`（如 `/skills` → `/personalization/skills`，保留查询参数）与一批 `Navigate replace` 旧链重定向（`/models`、`/admin/sso`、`/orca/*`、`/octop/*`、`/sessions`、`/cron-jobs` 等）；末三条是 `/pwa-debug`、`/` → `/chat`、`*` → NotFound（F-572）。

## 页面、侧边栏与 hooks

页面层 Glob `src/pages/**/index.tsx` 实测 **38 个**页面入口，归属 **12 个顶层目录**：Admin、Agent、Chat、Control、Experts、Invite、KnowledgeBases、Login、PwaDebug、Setup、Settings、SkillPackages；其中 Settings 下有 13 个子页（语音、安全、搜索、可观测、模型、媒体生成、语言、HTTPS、环境变量、嵌入、桥接、备份恢复、高级设置），Control 下 7 个（Workbench、TokenUsage、Terminal、RemoteDesktop、RemoteBrowser、RemoteAndroid、CronJobs），Admin 下 4 个（F-573）。

侧边栏的 19 个可见键以前端常量与后端偏好双份维护，注释明确要求二者保持同步（F-574）：

```tsx
// src/layouts/sidebarNav.tsx
/** Every nav item key the sidebar can show. Keep in sync with
 *  `SIDEBAR_NAV_KEYS` in `octop.infra.users.preferences`. */
export const SIDEBAR_NAV_KEYS = [
  "chat", "experts", "tasks", "token-usage", "personalization",
  "channels", "connectors", "skill-packages", "knowledge-bases", "bridge",
  "workbench", "remote-desktop", "acp", "admin-users", "models",
  "admin-storage", "admin-plugins", "admin-security", "admin-advanced",
] as const;
export const BUILTIN_NAV_GROUP_IDS = ["settings", "control", "admin"] as const;
```

这与后端权限三组（settings/control/admin）及用户自定义侧栏偏好一一对应：后端按角色裁剪可见键，前端按键渲染导航。

复用逻辑集中在 `src/hooks/`，Glob 实测 **56 个文件 = 55 个 `use*` + 1 个 `viewport.ts`**（含 10 个 `.test`；55 个 use* 中 52 个 `.ts` + 3 个 `.tsx`）（F-575）。覆盖面包括：鉴权与用户（`useCurrentUser`、`useUserRole`、`useUnauthorizedRedirect`）、设备串流（`useMobileStream`、`useDesktopStream`、`useBrowserStream` 及配套 canvas 交互 hook）、服务状态（`useUpdateStatus`、`useServiceRestart`、`useServerCapabilities`、`useServerUploadLimit`）、终端与语音（`useTerminalAutopilot`、`useVoiceInput/Output/Config`）、视口适配（`useIsMobile`、`useViewportMode`、`useAutoViewportResize`、`useKeepInVisualViewport`）等。Chat 页面另在 `Chat/hooks/` 下维护 45 个会话专用 hook（F-575）。

## 通用层：layouts、locales 与 utils

- **layouts/**：承载侧边栏、分组、全屏布局与导航解析；`sidebarNav.tsx` 是权限键到导航 UI 的唯一映射点。
- **locales/**：`zh.json` 与 `en.json` 各实测 **80 个顶层键**（F-575），与后端 `i18n/zh.json`、`i18n/en.json`（错误码/服务端文案）是两套独立文案。
- **utils/**：放跨页面工具，典型如 `reloadOnStaleChunk`——发布新版后旧 chunk 失效时自动刷新，请求层在发起导航前会调用 `markNavigatingAway` 与之配合（F-570）。

整体分层与后端四层架构对齐：页面/hooks 只消费 `api/modules`，modules 只经 `request.ts` 发出 `/api` 调用，前端没有任何直连 `infra/` 或数据库的路径——浏览器永远只是 HTTP/WS 客户端。

## 相关概念

- [/concepts/00-architecture.md](00-architecture.md)
- [/concepts/20-api-cli-surface.md](20-api-cli-surface.md)
- [/concepts/17-users-auth-security.md](17-users-auth-security.md)
- [/concepts/21-packaging-deployment.md](21-packaging-deployment.md)
