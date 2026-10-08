---
type: Concept
title: "打包与部署：Wails 桌面、便携 runtime、Docker、FnOS"
description: "Go 1.25 + Wails v3 桌面壳（1200x800 无边框/托盘/防睡眠/便携升级）、绿色便携包 launch.py 与 start 脚本/vendor-wheels、两阶段 Docker 镜像与三套 compose、飞牛云 docker/native 双形态模板。"
tags: [octop, wails, go, portable, docker, uv, compose, pgvector, redroid, fnos, deployment]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-576~F-592（v1.0.2b5，commit e473dd3c）
  - id: map
    resource: /references/source-v1-map.md
    title: Octop v1.0.2b5 源码地图（§8 桌面与便携包、§9 容器与部署）
---

# 打包与部署：Wails 桌面、便携 runtime、Docker、FnOS

Octop 有四种互不替代的分发形态：Python wheel（`pip install`）、Go/Wails 桌面壳、免安装绿色便携包、容器镜像，外加面向飞牛云（FnOS）应用中心的两套模板。本文覆盖后四类的装配事实。

## Go/Wails 桌面壳

桌面壳是一个独立的 Go module（F-576）：

| 项 | 值 |
|---|---|
| module | `octop.desktop` |
| Go 版本 | `go 1.25.0` |
| GUI 框架 | `github.com/wailsapp/wails/v3 v3.0.0-beta.13` |
| 直接依赖 | godbus/dbus/v5 v5.2.2、wails/v3、golang.org/x/sys v0.46.0（3 个） |
| indirect | xdg、coder/websocket、go-ole、go-winloader、go-colorable、go-isatty（6 个） |

Glob `desktop/src/**/*.go` 实测 **30 个文件 = 23 个非测试 + 7 个 `_test.go`**（desktop_copy、dock_reopen、download、portable_upgrade、settings、tray_click、window_chrome），含 `cmd/devserver/main.go`（F-577）。主包按平台拆文件名：`preventsleep_{darwin,linux,windows,other}.go`、`process_{unix,windows}.go`、`icons_{darwin,other}.go`（F-577）。

主窗口与设置窗的创建参数（F-578）：

```go
// main.go:321
app.Window.NewWithOptions(application.WebviewWindowOptions{
    Title: "Octop", Width: 1200, Height: 800, URL: "/",
    Frameless: true,
    AllowSimpleEventEmit: true,
    BackgroundColour: application.NewRGB(247, 248, 250),
})
// 隐藏设置窗：Title "Octop 设置"、URL "/?settings=1"、Hidden + Frameless
//              + AlwaysOnTop + DisableResize + Windows.HiddenOnTaskbar
```

运行时行为（F-579、F-580）：

- 三平台均 `DisableQuitOnLastWindowClosed`，关窗改为 `hideToTray`（Mac 用 `ApplicationShouldTerminateAfterLastWindowClosed:false` 与 Dock 重开钩子）
- 前端可发自定义事件 `desktop:toggle-maximise`、`desktop:minimise`、`desktop:close`、`desktop:status`
- 系统托盘 tooltip 为 "Octop"，设置窗挂到托盘；左键按平台分流（部分平台用 400ms 双击判定），右键开设置
- 资源经 `//go:embed assets/*` 由 BundledAssetFileServer 内嵌提供
- 启动时读 `OCTOP_DESKTOP_URL`：有值则 `waitHealth`（60 秒）后打开远程 URL（开发/外接后端）；否则走 `ensurePortable → startOctop(root, port) → waitHealth（2 分钟）→ showDashboard`，即壳负责拉起便携 Python 后端
- 平台能力包括**防睡眠**（preventsleep 四平台文件）、**安装包下载/便携升级**（download.go、portable_upgrade.go）、桌面拷贝（desktop_copy.go）

## 版本滞后与 NSIS 盖戳

Wails 构建配置的版本号落后于 Python 包，这是读源码时容易误报的「不一致」（F-581、F-582）：

- `build/config.yml` 顶层 `version: "3"`（Wails 配置格式版本），`info.productIdentifier: "com.tencent.octop"`，`info.version: "0.9.26"`，comments 逐字 "Wails v3 + green portable"
- `build/windows/info.json` 的 fixed.file_version 与 ProductVersion 也都是 `"0.9.26"`
- config.yml 注释明确：`info.version` 只是本地 `wails3 generate` 的兜底；**release packaging 会把 pyproject.toml 的版本盖到 .app/exe/NSIS 元数据上**
- Windows 打包链含 `create:nsis:installer` 任务（summary 逐字 "Wraps Octop.exe in an NSIS installer (Program Files + shortcuts)"），`stamp_version.py` 的 `nsis-defines` 子命令写 NSIS `!define`，`package-release.sh` 检测 `makensis`（缺失提示 "choco install nsis"）

## 绿色便携包：runtime/ + packages/

便携包不依赖系统 Python，产物布局为 `runtime/`（python-build-standalone 解释器）+ `packages/`（Octop 与全部依赖的 site-packages），CI 在 6 个 runner 上出 zip（F-585）。入口三件套位于 `desktop/portable/templates/`：`launch.py`、`start.sh`、`start.bat`。

`launch.py` 的引导顺序（F-583）：

```python
packages = root / "packages"
if not packages.is_dir():
    sys.stderr.write(f"launch.py: packages/ missing next to {root}\n")
    raise SystemExit(1)
site.addsitedir(str(packages))          # 处理 .pth（PYTHONPATH 方式会跳过）
if sys.platform == "win32":
    # packages/pywin32_system32 挂 DLL：PATH + os.add_dll_directory
    ...
runpy.run_module("octop", run_name="__main__", alter_sys=True)
```

两个细节：解释器目录会前置到 PATH，使子进程继承的 `python3` 仍解析到捆绑解释器；Windows 下必须用 `site.addsitedir` + `pywin32_system32` DLL 路径，单纯 `PYTHONPATH=packages` 无法 `import pywintypes`（F-583）。

`start.sh` 与 `start.bat` 是同构的用户入口：默认 `OCTOP_HOME=<包>/data`、`--host 127.0.0.1`、`--port 8088`，支持 `--home/--host/--port` 与透传额外 `octop run` 参数；脚本定位 `runtime/bin/python3`（Windows 为 `runtime\python.exe`），设 `PYTHONNOUSERSITE=1` 并清空 `PYTHONPATH`，最终 `exec python launch.py run --host ... --port ...`。

构建侧（F-584、F-585）：

- `Makefile` 目标 `bootstrap` / `wheels` / `package` / `green` / `green-linux` / `clean`；`green` 依赖 `build-frontend + bootstrap-runtime.sh + package.sh`，`green-linux` 调 `package-linux-docker.sh`（默认 linux-amd64）
- 产物目录逐字 `desktop/portable/release/`；`clean` 删除 runtimes/wheels/.cache/release 与 requirements/overrides 临时文件
- 离线依赖由 `vendor-wheels.sh` 预先 vendor，`verify_imports.py` 在打包后做导入校验

## Docker：两阶段镜像

`docker/Dockerfile` 是标准两阶段构建（F-586）：

```
┌─ stage 1: node:20-slim AS frontend-builder ──────────────┐
│  npm ci（失败清缓存重试一次）→ npm run build:docker        │
│  ARG NODE_MAX_OLD_SPACE_SIZE=2048（低内存机构建可降到 1024）│
│  产物：/build/src/octop/dashboard                          │
└───────────────────────────────────────────────────────────┘
                           │ COPY --from
┌─ stage 2: python:3.12-slim AS runtime ───────────────────┐
│  COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/      │
│  ① uv sync --frozen --no-install-project --no-dev \       │
│  │      --extra browser      （仅锁依赖，利于层缓存）      │
│  ② COPY src/ + 前端产物后再次 uv sync --frozen --no-dev \ │
│         --extra browser       （装入项目本身）             │
│  ENV OCTOP_BIND_HOST=0.0.0.0 OCTOP_PORT=8088 HOME=/data   │
│      PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright  │
│  EXPOSE 8088                                              │
└───────────────────────────────────────────────────────────┘
```

健康检查逐字为 `--interval=30s --timeout=10s --start-period=90s --retries=3`，CMD `curl -f http://localhost:${OCTOP_PORT:-8088}/api/health`；文件内没有 `USER` 指令（以 root 运行，F-586）。第二次 sync 后还会装 `fonts-noto-cjk` 并 purge build-essential。`--extra browser` 把 Playwright 装进镜像，对应 fnos 模板里「已预装 browser / desktop 附加组件」的说法。

**entrypoint 首启逻辑**（F-587）：以 `~/.octop/octop.db` 是否存在判断首启；首启执行 `octop init --yes --admin-username ... --admin-password ...`，默认用户名 admin、端口 8088；未给 `OCTOP_DEFAULT_PASSWORD` 时生成 **16 位随机密码**（首字符取字母、末位取数字、避开易混淆字符），若指定密码被应用口令策略拒绝（弱口令黑名单）也改用随机密码重试；凭据写入 `/data/.octop/credential.txt` 并 `chmod 600`；无参数最终 `exec octop run --host 0.0.0.0 --port "$PORT"`。

## 三套 compose

| 文件 | 形态 | 关键事实 |
|---|---|---|
| `docker-compose.yml` | 基础 | 单服务 octop，build context `..`、image `octop:latest`、restart unless-stopped；端口 `${OCTOP_PORT:-8088}` 双侧；卷 `${OCTOP_DATA:-~/.octop}:/data/.octop`；透传 8 个 `OCTOP_DATABASE_*` 键与 OPENAI_API_KEY、DASHSCOPE_API_KEY、LANGFUSE_*（`LANGFUSE_TRACING_ENABLED` 默认 true）（F-588） |
| `docker-compose.postgres.yml` | PostgreSQL | 镜像 `pgvector/pgvector:pg16`、容器名 octop-postgres、端口 `${OCTOP_PG_PORT:-5432}`，库/用户/密码默认均 octop；挂载 `postgres/init-vector.sql` 到 `/docker-entrypoint-initdb.d/01-vector.sql:ro`（F-589） |
| `docker-compose.mobile.yml` | 云手机 | **独立文件而非 overlay**：注释逐字说明 `network_mode: host` 与基础 compose 的 `ports` 冲突（F-589） |

pgvector 的初始化 SQL 全文只有一条有效语句：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

注释声明它不属于控制面迁移（控制面 schema 由 Octop 自己的 `NNN_*.pg.sql` 迁移负责，Agent memory 表由 octop-memory 运行时建，分层依据 ADR 002，F-589）。

mobile compose 的特权面（F-589）：`privileged: true` + `network_mode: host`；挂载 `/var/run/docker.sock`（DinD 拉起 Redroid）、`/dev/binderfs` 与只读的 platform-tools；环境变量 `OCTOP_MOBILE_ADB_HOST=127.0.0.1:5555`、`OCTOP_MOBILE_CONTAINER=octop-mobile-android`、`OCTOP_ENABLE_MOBILE=1`、`ANDROID_HOME/ANDROID_SDK_ROOT=/opt/android-sdk`。

## FnOS：docker / native 双形态

飞牛云模板两套 manifest 的版本锚点均为 **0.9.15**（F-590）：

| 项 | docker 形态 | native 形态 |
|---|---|---|
| appname | `octop` | `octop-native` |
| service_port | 8088 | 8089 |
| desktop_applaunchname | `octop.Application` | `octop-native.Application` |
| 依赖 | 自动拉取 `ghcr.io/tencentcloud/octop:latest`，已预装 browser/desktop 附加组件 | `install_dep_apps=python312`（自动关联安装 Python 3.12 开发工具） |
| 凭据 | 安装向导设置，数据目录 `octop-login.txt` 备份 | 同左，desc 默认地址 `http://设备IP:8089`，支持官方 octop CLI |

两套共有键：`display_name=OCTOP`、`source=thirdparty`、`maintainer=TencentCloud OrcaKit`、`micro_app=true`、`checkport=true`、`ctl_stop=true`（F-590）。两目录另含 `cmd/` 生命周期回调（config/install/uninstall/upgrade 的 `_init`/`_callback` + main）、`wizard/`、`ui/config` 与 ICON/LICENSE。

## 版本锚点一览

读部署文件时要区分三套独立版本号，避免张冠李戴：

```
Python 包 / 发行版      1.0.2b5   （src/octop/__init__.py、pyproject.toml）
Wails build config      0.9.26    （发布时被 pyproject 版本盖戳）
FnOS manifest           0.9.15    （docker 8088 / native 8089）
HTTP API 自报           0.1.0     （FastAPI title/version，独立口径）
```

## 相关概念

- [/concepts/19-dashboard-frontend.md](19-dashboard-frontend.md)
- [/concepts/00-architecture.md](00-architecture.md)
- [/concepts/01-server-lifecycle.md](01-server-lifecycle.md)
- [/concepts/18-mobile-desktop-proactive.md](18-mobile-desktop-proactive.md)
