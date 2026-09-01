---
type: Reference
title: Agency Agents App 源码信源登记
description: AI Agent 原生桌面应用（Tauri 2 + Svelte 5）源码结构、Rust 后端命令、Svelte 前端组件、数据模型与状态管理信源清单
tags: [agency-agents-app, tauri, svelte, sveltekit, rust, desktop, agent-catalog, source, reference]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T23:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: agency-agents-app-github
    resource: https://github.com/msitarzewski/agency-agents-app
    title: Agency Agents App GitHub 仓库
---

# Agency Agents App 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | agency-agents-app |
| 版本 | v0.3.0 |
| 描述 | "a native macOS app store for AI agents"——浏览、安装和追踪 251+ 个 AI agent 的原生桌面应用 |
| 作者 | Michael Sitarzewski |
| 许可证 | MIT |
| 技术栈 | Svelte 5 (runes) + SvelteKit 2 + TypeScript + Vite 6（前端）；Rust (edition 2021) + Tauri 2（后端） |
| UI 图标 | @lucide/svelte |
| 渲染模式 | SPA（SSR 关闭，adapter-static） |
| 支持平台 | macOS（主要）、Linux、Windows |
| 源码位置 | `d:\spaces\SpecWeave\external\libs\models\ai\agency-agents-app\` |

## 核心目录结构

```
agency-agents-app/
├── package.json                 # 前端依赖与脚本
├── src/                         # SvelteKit 前端源码
│   ├── routes/
│   │   ├── +layout.svelte       # 根布局（初始化流程）
│   │   ├── +layout.ts           # SSR 关闭配置
│   │   └── +page.svelte         # 主页面（快捷键、标题栏）
│   ├── lib/
│   │   ├── components/          # Svelte 组件
│   │   │   ├── Sidebar.svelte   # 侧边栏导航
│   │   │   ├── AgencyDashboard.svelte  # 仪表盘
│   │   │   ├── CommandPalette.svelte   # 命令面板（⌘K）
│   │   │   ├── Settings.svelte  # 设置模态框
│   │   │   └── DeployBrowser.svelte    # 部署选择器
│   │   ├── stores/              # Svelte 5 runes 状态管理
│   │   │   ├── catalog.svelte.ts       # Catalog 源管理
│   │   │   ├── install.svelte.ts       # 安装协调
│   │   │   ├── corpus.svelte.ts        # Agent 语料库（懒加载）
│   │   │   ├── projects.svelte.ts      # 项目列表
│   │   │   ├── settings.svelte.ts      # 用户设置
│   │   │   └── ui.svelte.ts            # UI 状态（导航历史、主题）
│   │   ├── data/                # 静态数据
│   │   │   ├── toolRegistry.ts  # 工具注册表（前端）
│   │   │   ├── presetTeams.ts   # 5 个预设团队
│   │   │   └── playbook.ts      # Playbook 最佳实践
│   │   ├── types.ts             # 全部 TypeScript 类型定义
│   │   ├── api.ts               # Tauri invoke 封装
│   │   └── i18n/locales/        # 11 种语言本地化
│   └── landing/                 # 独立 PWA 营销页面
├── src-tauri/                   # Rust 后端（Tauri 2）
│   ├── Cargo.toml               # Rust 依赖
│   ├── src/
│   │   ├── main.rs              # 极简入口（调用 run()）
│   │   ├── lib.rs               # Tauri 应用初始化、命令注册、菜单
│   │   ├── error.rs             # 错误类型
│   │   ├── types.rs             # Rust DTO（serde camelCase）
│   │   ├── registry.rs          # 注册表
│   │   ├── state.rs             # 应用状态管理
│   │   ├── commands/            # Tauri 命令
│   │   │   ├── github.rs        # GitHub OAuth/Star/Watch/Issue
│   │   │   ├── settings.rs      # 设置读写
│   │   │   └── updater.rs       # 应用更新
│   │   ├── corpus/              # Agent 语料库解析
│   │   │   ├── mod.rs
│   │   │   └── parse.rs         # Markdown frontmatter 解析
│   │   ├── github/              # GitHub API 集成
│   │   │   ├── auth.rs          # Device Flow 认证
│   │   │   ├── actions.rs       # Star/Watch/Issue
│   │   │   ├── stats.rs         # 仓库统计
│   │   │   └── url.rs
│   │   ├── install/             # Agent 安装协调
│   │   ├── render/              # 格式渲染（各工具格式输出）
│   │   └── util/                # 工具函数
│   │       ├── fs.rs
│   │       ├── mod.rs
│   │       └── net.rs
│   ├── data/
│   │   └── tools.json           # 工具定义（后端单一真相源）
│   └── resources/
│       └── corpus-baseline/     # 内置 Agent 库基线（17 分类 .md 文件）
└── landing/                     # PWA 营销站静态资源
```

## 关键文件清单

### Rust 后端入口与配置

| 文件 | 内容 |
|------|------|
| `src-tauri/src/main.rs` | 极简入口，仅 `agency_agents_lib::run()`；Windows 设置 `windows_subsystem = "windows"` |
| `src-tauri/src/lib.rs` | Tauri setup 钩子（毛玻璃、Linux WebKit 兼容、插件注册）、~35 个 invoke_handler 命令注册、macOS 原生菜单 |
| `src-tauri/Cargo.toml` | Rust 依赖：tauri 2、tokio、serde、reqwest、keyring、window-vibrancy 等 |

### Rust 命令模块

| 文件 | 内容 |
|------|------|
| `src-tauri/src/commands/github.rs` | GitHub Device Flow OAuth、Star/Watch/Issue 操作 |
| `src-tauri/src/commands/settings.rs` | 设置读写（settings.json） |
| `src-tauri/src/commands/updater.rs` | 应用更新检查/安装/跳过/重启 |
| `src-tauri/src/corpus/parse.rs` | Agent .md 文件解析（frontmatter 提取、三哈希索引计算） |
| `src-tauri/src/corpus/mod.rs` | 语料库管理（list/get/categories/status/refresh） |
| `src-tauri/src/install/` | Agent 安装/卸载/更新/track/diff/reconcile 逻辑 |
| `src-tauri/src/render/` | 各工具格式渲染（identity/codex-toml/gemini-md/qwen-md/zcode-md/cursor-mdc/opencode-md/skill-md） |
| `src-tauri/src/state.rs` | AppState 初始化、自动更新调度器（24h 周期，退避 1h→6h→24h） |

### Rust 类型定义

| 文件 | 内容 |
|------|------|
| `src-tauri/src/types.rs` | 全部 DTO：Settings、Agent、CorpusEntry（三哈希）、InstallState/UpdateKind、CatalogSource 三源模型、GitHubAuth 等；`#[serde(rename_all = "camelCase")]` |
| `src-tauri/src/error.rs` | 错误类型定义 |

### 前端类型与 API

| 文件 | 内容 |
|------|------|
| `src/lib/types.ts` | TypeScript 类型全量定义：Settings、AppErrorPayload（14 种错误码）、Agent、InstallState、CatalogSource、GitHubDeviceFlow、UpdateCheckOutcome、CorpusEntry、ThemePreference、PaletteItem |
| `src/lib/api.ts` | Tauri invoke 封装：githubSigninStart/Poll、updateCheck/Install/Skip/Relaunch 等 |

### Svelte 5 Stores（runes 单例）

| 文件 | 内容 |
|------|------|
| `src/lib/stores/catalog.svelte.ts` | Catalog 源管理：load/detect/setSource/useBundled/useClone/provisionManaged/pull |
| `src/lib/stores/install.svelte.ts` | 安装协调：reconcile（去重）、install/uninstall/update/track/bulk、loadout_export/import、选中工具持久化 |
| `src/lib/stores/corpus.svelte.ts` | 语料库懒加载：ensureLoaded/get/filtered/bodyCache Map |
| `src/lib/stores/projects.svelte.ts` | 项目注册/遗忘/添加（localStorage key: `agency-agents:projects:v1`） |
| `src/lib/stores/settings.svelte.ts` | 设置三态加载（loading→loaded/corrupt）、乐观更新、失败回滚 |
| `src/lib/stores/ui.svelte.ts` | UI 状态：navStack 导航历史（上限100）、back/forward、主题切换、快捷键 |

### 前端组件

| 文件 | 内容 |
|------|------|
| `src/lib/components/Sidebar.svelte` | 7 分区导航（dashboard/personas/tools/teams/projects/runbooks/activity），折叠(56px)/拖拽宽度(168-360px) |
| `src/lib/components/AgencyDashboard.svelte` | 仪表盘：4 统计卡 + InstallSunburst + 分类堆叠条 + HealthDonut + Coverage 图表（纯 SVG+CSS） |
| `src/lib/components/CommandPalette.svelte` | ⌘K 命令面板：9 命令，模糊搜索，上下键导航 |
| `src/lib/components/Settings.svelte` | 设置模态框：6 分区（Appearance/Catalog/Network/GitHub/Activity/About），z-index 90/91 |
| `src/lib/components/DeployBrowser.svelte` | 双窗格部署选择器：4 类可部署单元 + 工具三态 toggle 网格 |

### 前端静态数据

| 文件 | 内容 |
|------|------|
| `src/lib/data/toolRegistry.ts` | 工具注册表前端：15 工具定义，IMPLEMENTED_FORMATS（8 种已实现渲染格式） |
| `src/lib/data/presetTeams.ts` | 5 预设团队：Mobile Launch、Ship It (Web)、Growth Squad、Product Discovery、AI Builders |
| `src/lib/data/playbook.ts` | 5 条最佳实践原则、3 个 Starter Prompt 模板 |

### 前端路由与初始化

| 文件 | 内容 |
|------|------|
| `src/routes/+layout.ts` | `export const ssr = false`（SPA 模式） |
| `src/routes/+layout.svelte` | 初始化流程：i18n→UI偏好→导航历史→activity→install.reconcile→settings.load→catalog.load；监听菜单事件；CatalogFirstRun 首启引导 |
| `src/routes/+page.svelte` | 全局快捷键、36px 自定义标题栏（`data-tauri-drag-region`） |

### Tauri 资源

| 文件 | 内容 |
|------|------|
| `src-tauri/data/tools.json` | 工具定义后端单一真相源（15 个工具） |
| `src-tauri/resources/corpus-baseline/` | 17 分类内置 Agent 库基线 .md 文件 |

## Tauri 命令注册清单（约 35 个）

| 分组 | 命令 |
|------|------|
| 基础设施 | `app_version`、`settings_get`、`settings_set`、`settings_reset` |
| GitHub 集成 | `github_repo_stats`、`github_status`、`github_signin_start`、`github_signin_poll`、`github_signout`、`github_star`、`github_unstar`、`github_is_starred`、`github_watch`、`github_unwatch`、`github_create_issue` |
| 更新器 | `update_check_now`、`update_install`、`update_skip`、`update_relaunch` |
| Corpus 子系统 | `corpus_status`、`corpus_refresh`、`corpus_list`、`corpus_get`、`corpus_categories`、`catalog_source_get`、`catalog_configured`、`catalog_source_set`、`catalog_detect`、`catalog_provision_managed`、`catalog_pull`、`catalog_status`、`catalog_check_updates`、`runbooks_list` |
| 安装/协调 | `install_agent`、`update_agent`、`track_agent`、`agent_diff`、`uninstall_agent`、`project_forget`、`installs_reconcile`、`installs_for_agent`、`tools_list`、`tool_versions`、`reveal_path`、`projects_list`、`loadout_export`、`loadout_import` |

## 核心数据模型索引

### TypeScript / Rust 共享 DTO

| 类型 | 定义位置 | 说明 |
|------|---------|------|
| `Settings` | `types.ts:26-89` / `types.rs` | paranoidMode、catalogStaleBannerDays、toolPaths 等 |
| `AppErrorPayload` | `types.ts:234-288` | 14 种错误码（json_parse/io/network/auth_required 等） |
| `Agent` | `types.ts:318-335` / `types.rs:138-157` | slug/name/description/category/emoji/color/vibe/body |
| `CorpusEntry` | `types.ts:342-356` / `types.rs:165-181` | 三哈希：sourceHash/frontmatterHash/bodyHash |
| `InstallState` | `types.ts:465-474` / `types.rs:224-241` | current/outdated/modified/removed/foreign 五状态 |
| `UpdateKind` | 同上 | cosmetic（仅 frontmatter）/substantive（正文） |
| `CatalogSource` | `types.ts:372-375` / `types.rs:40-59` | bundled/managed/userClone 三源判别联合 |
| `GitHubDeviceFlow` | `types.ts:127-164` | OAuth 2.0 Device Authorization Grant (RFC 8628) |
| `UpdateCheckOutcome` | `types.ts:219-228` | upToDate/available 判别联合 |

### 前端 Store 关键方法

| Store | 关键方法 | 说明 |
|-------|---------|------|
| `catalog` | `load()`、`checkUpdates()`、`detect(scan)`、`setSource()`、`provisionManaged()`、`pull()` | Catalog 源生命周期 |
| `install` | `reconcile()`、`install_agent()`、`bulk()`、`loadout_export/import()` | 安装协调与批量操作 |
| `corpus` | `ensureLoaded()`、`get(slug)`、`filtered()`、`reload()` | 懒加载语料库 |
| `projects` | `register()`、`unregister()`、`addViaPicker()`、`forgetProject()` | 项目管理 |
| `settings` | `load()`、`save(partial)`、`reset()` | 设置持久化（乐观更新） |
| `ui` | `navigate()`、`back()`、`forward()`、`setTheme()` | 导航历史与主题 |

## 侧边栏导航分区

| 分区 | 快捷键 | 说明 |
|------|--------|------|
| dashboard | ⌘0 | 概览仪表盘 |
| personas | ⌘1 | Agents 首页（初始分区，front door） |
| tools | ⌘2 | 工具管理 |
| teams | ⌘3 | 团队管理 |
| projects | ⌘4 | 项目管理 |
| runbooks | ⌘5 | Runbook |
| activity | ⌘6 | 活动日志 |

## 全局快捷键

| 快捷键 | 功能 |
|--------|------|
| ⌘K | 打开命令面板 |
| ⌘, | 打开设置 |
| ⌘Shift+L | 循环主题（light/dark/system） |
| ⌘L | 切换活动抽屉 |
| ⌘[/⌘] | 前进/后退导航 |
| ⌘0-6 | 切换分区 |
| `/` | 聚焦搜索框 |
| Esc | 关闭面板/设置 |

## Tauri 插件

| 插件 | 功能 |
|------|------|
| `tauri_plugin_opener` | 打开 URL/文件 |
| `tauri_plugin_dialog` | 原生对话框 |
| `tauri_plugin_updater` | 应用内更新（SHA-256 + minisign 签名验证） |
| `tauri_plugin_window_state` | 窗口大小/位置持久化 |

## 平台特有实现

| 平台 | 实现 |
|------|------|
| macOS | 毛玻璃效果（`NSVisualEffectMaterial::HudWindow`）、原生 App/Edit/Window 菜单、交通灯按钮 |
| Linux | 自动设置 `WEBKIT_DISABLE_DMABUF_RENDERER=1` 修复 WebView 崩溃 |
| Windows | `windows_subsystem = "windows"` 隐藏控制台、Credential Manager 密钥存储 |
| 跨平台 | `keyring` crate 密钥存储（macOS Keychain / Windows Credential Manager / Linux Secret Service） |

## 国际化

支持 **11 种语言**：English (en)、German (de)、Spanish (es)、Persian (fa)、French (fr)、Japanese (ja)、Korean (ko)、Brazilian Portuguese (pt-BR)、Russian (ru)、Simplified Chinese (zh-CN)、Traditional Chinese (zh-TW)。

## 已实现渲染格式（8 种）

`identity`、`codex-toml`、`gemini-md`、`qwen-md`、`zcode-md`、`cursor-mdc`、`opencode-md`、`skill-md`

未实现（app 不可安装）：Hermes（plugin）、Aider（aider-conventions）、Windsurf（windsurf-rules）、Kimi（kimi-agent）、OpenClaw（openclaw-workspace）。
