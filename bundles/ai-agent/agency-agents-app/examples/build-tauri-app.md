---
type: Example
title: 构建 Tauri 桌面应用
description: 从源码构建 Agency Agents 桌面应用，包括 pnpm 依赖安装、Rust 编译、Tauri 开发模式启动、前后端命令调用，以及跨平台构建配置。
tags: [agency-agents-app, example, tauri, svelte, rust, build, desktop]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: agency-agents-app 源码事实清单
---

## 场景说明

你需要从源码构建和运行 Agency Agents 桌面应用。Agency Agents App 是一个基于 Tauri 2 的原生桌面应用（macOS/Linux/Windows），前端使用 Svelte 5（runes 模式）+ SvelteKit 2，后端使用 Rust。

本示例覆盖：
1. 环境准备（Node.js、pnpm、Rust）
2. 前端依赖安装（pnpm）
3. Rust 依赖编译（cargo）
4. Tauri 开发模式启动
5. 前后端命令调用（invoke）
6. 生产构建与打包

## 技术栈概览

| 层 | 技术 | 版本/说明 |
|---|------|----------|
| 前端框架 | Svelte 5 (runes) | `$state`/`$derived`/`$effect`，非传统 store |
| 前端路由 | SvelteKit 2 | adapter-static，SPA 模式（`ssr = false`） |
| 构建工具 | Vite 6 | 开发服务器 + 生产构建 |
| UI 组件 | 自研 + @lucide/svelte | 纯 SVG+CSS 图表，无图表库依赖 |
| 后端框架 | Tauri 2 (Wry) | Rust 2021 edition |
| 跨平台 | Tauri 2 | macOS / Linux / Windows |
| 状态管理 | Svelte 5 runes class 单例 | 非 writable/readable store |

## 环境准备

### 1. 安装前置依赖

**Node.js（≥20）和 pnpm**：

```bash
# 安装 Node.js（推荐使用 fnm/nvm）
fnm install 20
fnm use 20

# 安装 pnpm
npm install -g pnpm

# 验证
node --version   # v20+
pnpm --version   # 9+
```

**Rust 工具链**：

```bash
# 安装 Rust（macOS/Linux）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Windows 下载 rustup-init.exe
# https://rustup.rs

# 安装 Tauri 2 CLI
cargo install tauri-cli --version "^2.0"

# 验证
rustc --version  # 1.75+
cargo --version
```

**平台特定依赖**：

```bash
# macOS（需要 Xcode Command Line Tools）
xcode-select --install

# Ubuntu/Debian
sudo apt install libwebkit2gtk-4.1-dev build-essential curl wget file \
  libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev

# Fedora
sudo dnf install webkit2gtk4.1-devel openssl-devel libxdo-devel \
  libappindicator-gtk3-devel librsvg2-devel

# Windows（需要 WebView2，Windows 10/11 已预装）
# 安装 Visual Studio Build Tools 2022（C++ 桌面开发工作负载）
```

### 2. 克隆仓库

```bash
git clone https://github.com/msitarzewski/agency-agents-app.git
cd agency-agents-app
```

## 前端依赖安装

前端使用 pnpm workspaces 管理，根目录 `package.json` 包含所有依赖：

```bash
# 安装所有前端依赖
pnpm install
```

核心前端依赖（package.json 节选）：

```json
{
  "dependencies": {
    "@lucide/svelte": "^0.x",
    "@tauri-apps/api": "^2.0"
  },
  "devDependencies": {
    "@sveltejs/adapter-static": "^3.0",
    "@sveltejs/kit": "^2.0",
    "@tauri-apps/cli": "^2.0",
    "svelte": "^5.0",
    "typescript": "^5.0",
    "vite": "^6.0"
  }
}
```

SvelteKit 配置为 SPA 模式（无 SSR）：

```typescript
// src/routes/+layout.ts
export const ssr = false;
```

## Rust 后端编译

Rust 后端代码位于 `src-tauri/` 目录，使用 Cargo 管理：

```toml
# src-tauri/Cargo.toml 关键依赖
[package]
name = "agency-agents-app"
version = "0.3.0"
edition = "2021"

[dependencies]
tauri = { version = "2", features = ["dialog", "opener", "window-state", "updater"] }
tauri-plugin-dialog = "2"
tauri-plugin-opener = "2"
tauri-plugin-updater = "2"
tauri-plugin-window-state = "2"
window-vibrancy = "0.5"  # macOS 毛玻璃效果
keyring = { version = "2", features = ["apple-native", "windows-native", "sync-secret-service", "crypto-rust"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["full"] }
reqwest = { version = "0.12", features = ["json"] }
```

```bash
# 预下载 Rust 依赖（可选，加速首次编译）
cd src-tauri
cargo fetch
cd ..
```

## 启动 Tauri 开发模式

```bash
# 启动开发模式（自动启动 Vite dev server + 编译 Rust + 打开窗口）
pnpm tauri dev

# 或使用 cargo tauri
cargo tauri dev
```

开发模式执行以下操作：
1. 启动 Vite 开发服务器（前端 HMR 热更新）
2. 以 debug 模式编译 Rust 后端
3. 打开桌面应用窗口
4. 前端代码修改自动热更新
5. Rust 代码修改自动重新编译并重启

启动后窗口标题栏为 36px 高的自定义拖拽区域，侧边栏显示 7 个导航分区：
- ⌘0 Dashboard（仪表盘）
- ⌘1 Personas（Agents 首页，默认）
- ⌘2 Tools（工具）
- ⌘3 Teams（团队）
- ⌘4 Projects（项目）
- ⌘5 Runbooks（操作手册）
- ⌘6 Activity（活动）

### 首次启动体验

首次启动时会触发 `CatalogFirstRun` 组件，引导选择 catalog 源：
- **Bundled**：app 内置快照（默认，离线可用）
- **Managed clone**：app 管理的 git clone（`~/.agency-agents`）
- **User clone**：用户自己的 clone 路径

## 前后端命令调用

### Tauri 命令注册

后端在 `src-tauri/src/lib.rs` 中注册了约 35 个 Tauri 命令，分为五组：

```rust
// src-tauri/src/lib.rs 中的 invoke_handler 注册（概念示意）
.invoke_handler(tauri::generate_handler![
    // 基础设施
    app_version, settings_get, settings_set, settings_reset,

    // GitHub 集成（OAuth Device Flow）
    github_repo_stats, github_status, github_signin_start,
    github_signin_poll, github_signout, github_star, github_unstar,
    github_is_starred, github_watch, github_unwatch, github_create_issue,

    // 更新器
    update_check_now, update_install, update_skip, update_relaunch,

    // Corpus 子系统（Agent 库管理）
    corpus_status, corpus_refresh, corpus_list, corpus_get,
    corpus_categories, catalog_source_get, catalog_configured,
    catalog_source_set, catalog_detect, catalog_provision_managed,
    catalog_pull, catalog_status, catalog_check_updates, runbooks_list,

    // 安装/协调
    install_agent, update_agent, track_agent, agent_diff,
    uninstall_agent, project_forget, installs_reconcile, installs_for_agent,
    tools_list, tool_versions, reveal_path, projects_list,
    loadout_export, loadout_import
])
```

### 前端调用 Tauri 命令

前端通过 `@tauri-apps/api` 的 `invoke` 函数调用后端命令：

```typescript
// src/lib/api.ts（概念示意）
import { invoke } from '@tauri-apps/api/core';

// 获取应用版本
export async function getAppVersion(): Promise<string> {
  return invoke('app_version');
}

// 获取设置
export async function getSettings(): Promise<AppSettings> {
  return invoke('settings_get');
}

// 安装 Agent
export async function installAgent(
  slug: string,
  toolId: string,
  projectPath?: string
): Promise<InstallResult> {
  return invoke('install_agent', { slug, toolId, projectPath });
}

// 获取 Corpus 列表
export async function corpusList(
  category?: string,
  query?: string
): Promise<Agent[]> {
  return invoke('corpus_list', { category, query });
}

// GitHub Device Flow 认证
export async function githubSigninStart(): Promise<{
  userCode: string;
  verificationUri: string;
  expiresIn: number;
  interval: number;
  deviceCode: string;
}> {
  return invoke('github_signin_start');
}

// 轮询 GitHub 认证状态
export async function githubSigninPoll(
  deviceCode: string,
  interval: number
): Promise<
  | { status: 'pending' }
  | { status: 'slowDown'; interval: number }
  | { status: 'approved'; username: string; scopes: string[] }
  | { status: 'denied' }
  | { status: 'expired' }
> {
  return invoke('github_signin_poll', { deviceCode });
}
```

### Rust 端命令实现示例

```rust
// src-tauri/src/commands/settings.rs（概念示意）
use serde::Serialize;
use crate::state::AppState;

#[derive(Serialize)]
pub struct AppSettings {
    paranoid_mode: bool,
    catalog_stale_banner_days: u32,
    github_enabled: bool,
    ai_features_enabled: bool,
    update_auto_check: bool,
    trending_ttl_minutes: u32,
    tool_paths: std::collections::HashMap<String, String>,
}

#[tauri::command]
pub async fn settings_get(state: tauri::State<'_, AppState>) -> Result<AppSettings, String> {
    let settings = state.settings.read().await;
    Ok(AppSettings {
        paranoid_mode: settings.paranoid_mode,
        catalog_stale_banner_days: settings.catalog_stale_banner_days,
        github_enabled: settings.github_enabled,
        ai_features_enabled: settings.ai_features_enabled,
        update_auto_check: settings.update_auto_check,
        trending_ttl_minutes: settings.trending_ttl_minutes,
        tool_paths: settings.tool_paths.clone(),
    })
}

#[tauri::command]
pub async fn settings_set(
    state: tauri::State<'_, AppState>,
    partial: serde_json::Value,
) -> Result<AppSettings, String> {
    let mut settings = state.settings.write().await;
    // 乐观更新，失败回滚
    settings.apply_partial(&partial)?;
    settings.save().map_err(|e| e.to_string())?;
    Ok(settings.clone().into())
}
```

## Svelte 5 Runes 状态管理

前端所有 store 使用 Svelte 5 runes 在 class 中实现，导出为单例：

```svelte
<!-- src/lib/stores/catalog.svelte.ts（概念示意） -->
class CatalogStore {
  source = $state<CatalogSource>({ kind: 'bundled' });
  status = $state<CatalogStatus>('idle');

  async load() {
    this.status = 'loading';
    const configured = await invoke('catalog_configured');
    if (!configured) {
      this.status = 'first-run';
      return;
    }
    const source = await invoke<CatalogSource>('catalog_source_get');
    this.source = source;
    this.status = 'idle';
  }

  async pull() {
    this.status = 'pulling';
    await invoke('catalog_pull');
    await this.load();
  }
}

export const catalog = new CatalogStore();
```

使用方式（Svelte 组件中）：

```svelte
<script lang="ts">
  import { catalog } from '$lib/stores/catalog.svelte';
  import { install } from '$lib/stores/install.svelte';
</script>

<div class="sidebar">
  {#if catalog.status === 'first-run'}
    <CatalogFirstRun />
  {/if}

  {#each categories as cat}
    <button onclick={() => install.bulk('install', selectedAgents)}>
      Install {cat.label}
    </button>
  {/each}
</div>
```

全局快捷键在 `+page.svelte` 中注册：

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { ui } from '$lib/stores/ui.svelte';

  onMount(() => {
    function handleKeydown(e: KeyboardEvent) {
      if (e.metaKey || e.ctrlKey) {
        if (e.key === 'k') { e.preventDefault(); ui.openCommandPalette(); }
        if (e.key === ',') { e.preventDefault(); ui.openSettings(); }
        if (e.key >= '0' && e.key <= '6') {
          e.preventDefault();
          ui.navigateToSection(parseInt(e.key));
        }
        if (e.key === '[') { e.preventDefault(); ui.goBack(); }
        if (e.key === ']') { e.preventDefault(); ui.goForward(); }
      }
      if (e.key === '/' && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        ui.focusSearch();
      }
      if (e.key === 'Escape') ui.closeModals();
    }
    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  });
</script>
```

## 生产构建

```bash
# 构建生产版本
pnpm tauri build

# 平台特定构建
pnpm tauri build --target universal-apple-darwin   # macOS Universal
pnpm tauri build --target x86_64-pc-windows-msvc  # Windows x64
pnpm tauri build --target x86_64-unknown-linux-gnu # Linux x64
```

构建产物位置：

| 平台 | 产物路径 |
|------|---------|
| macOS | `src-tauri/target/release/bundle/dmg/` (.dmg) 和 `.app` |
| Windows | `src-tauri/target/release/bundle/msi/` (.msi) 和 `.exe` |
| Linux | `src-tauri/target/release/bundle/` (AppImage / deb / rpm) |

### Tauri 插件注册

```rust
// src-tauri/src/lib.rs 中的插件注册
fn build_app() -> tauri::App {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())        // 打开 URL/文件
        .plugin(tauri_plugin_dialog::init())         // 原生对话框
        .plugin(tauri_plugin_updater::init())        // 应用内更新
        .plugin(tauri_plugin_window_state::Builder::default()
            .with_state_flags(StateFlags::all())
            .build())                                // 窗口状态持久化
        .setup(|app| {
            // macOS 毛玻璃效果
            #[cfg(target_os = "macos")]
            {
                let window = app.get_webview_window("main").unwrap();
                use window_vibrancy::NSVisualEffectMaterial;
                apply_vibrancy(&window, NSVisualEffectMaterial::HudWindow, None, None)?;
            }

            // Linux WebKit 兼容性修复
            #[cfg(target_os = "linux")]
            std::env::set_var("WEBKIT_DISABLE_DMABUF_RENDERER", "1");

            // 初始化应用状态
            state::initialize(app)?;

            // 菜单（macOS）
            #[cfg(target_os = "macos")]
            setup_menus(app);

            Ok(())
        })
        .invoke_handler(/* 35 个命令 */)
        .build(tauri::generate_context!())
        .expect("error while building app")
}
```

## 常见构建问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Linux WebView 崩溃 | NVIDIA/Wayland DMABUF 问题 | 设置 `WEBKIT_DISABLE_DMABUF_RENDERER=1`（已在代码中自动设置） |
| Windows 控制台窗口 | 未设置 Windows 子系统 | `main.rs` 中已有 `#![windows_subsystem = "windows"]` |
| macOS 毛玻璃不生效 | 窗口背景非 transparent | CSS body 设置 `background: transparent` |
| 编译慢（首次） | Rust 依赖编译 | 首次约 5-15 分钟，后续增量编译很快 |
| pnpm 安装失败 | Node 版本过旧 | 确保 Node ≥ 20 |
| keyring 编译失败 | 缺少系统依赖 | Linux 安装 `libsecret-1-dev`（或 `libsecret`） |

## 开发调试技巧

1. **打开开发者工具**：开发模式按 `Ctrl+Shift+I`（Windows/Linux）或 `Cmd+Option+I`（macOS）
2. **Rust 日志**：设置 `RUST_LOG=debug` 环境变量查看后端日志
3. **前端热更新**：Svelte 组件和 TypeScript 修改自动 HMR
4. **重新编译 Rust**：修改 `src-tauri/src/` 中的代码后，`tauri dev` 自动重编译
5. **清理构建缓存**：`cargo clean` 清理 Rust 构建缓存（不推荐频繁使用）

## 相关概念

- [Tauri 后端命令体系](../concepts/tauri-backend-commands.md)
- [Svelte 5 Runes 架构](../concepts/svelte5-runes-architecture.md)
- [Catalog 与安装 Store](../concepts/catalog-install-store.md)
