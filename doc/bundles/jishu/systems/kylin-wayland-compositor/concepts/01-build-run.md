---
type: Concept
title: "构建、运行与打包：依赖、meson 选项、CLI、环境变量与会话单元"
description: "掌握 kywc 的依赖版本约束、44 个 meson 选项裁剪链、命令行参数、环境变量分组、双层 JSON 配置与 systemd 用户会话启动模型"
tags: [wayland, wlroots, meson, build, systemd, openkylin]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r1
    resource: /references/facts-build-startup.md
    title: R1 构建/启动/配置/打包事实清单
  - id: kywc-docs
    resource: /references/project-docs.md
    title: kywc 仓库自带文档登记与口径说明
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：本篇位于「硬件/会话→后端」主线之前，解决「这套代码如何变成可运行的 kylin-wlcom、又如何被 openKylin 会话拉起」的问题。前置阅读 [00 全景](/concepts/00-overview.md)；构建选项中涉及的协议机制在 [02](/concepts/02-wayland-wlroots-basics.md) 展开，会话拉起后的进程内行为在 [03](/concepts/03-startup-architecture.md) 展开。

## 依赖清单与版本约束

工程为纯 C 的 meson 项目，根 meson.build 声明的核心依赖及下限如下（F-R1-009，meson.build:74-97）：

| 依赖 | 版本约束 | 用途 |
|---|---|---|
| wlroots | `>=0.17.0,<0.18.0` | 合成器底座（unstable API，见 [02](/concepts/02-wayland-wlroots-basics.md)） |
| wayland-server | `>=1.23.0` | Wayland 服务端库（`wl_*` 符号） |
| wayland-protocols | `>=1.36` | 上游协议 XML 集合 |
| libinput | `>=1.19` | 输入设备事件（`libinput_*` 符号） |
| json-c | `>=0.13` | JSON 配置读写 |
| librsvg-2.0 | `>=2.46` | SVG 资源光栅化 |
| gbm | `>=21.1` | GPU buffer 分配 |
| libpipewire-0.3 | 无下限 | screencast 相关（portal/特效侧） |
| xkbcommon、libdrm、pixman-1、libudev、libdisplay-info、libsystemd(sd-bus) | 无版本下限 | 键位、DRM、像素、设备枚举、EDID、D-Bus |
| cairo/pango/pangocairo、libjpeg、libpng、m/dl/rt/threads | 无下限 | CPU 绘图、图像与系统库 |

wlroots 这一条最关键，也最「不上游」。除版本区间外，工程还以 `dependency()` 的 default_options 强压其 subproject 构建形态，并全局开启 unstable API 宏（F-R1-008，meson.build:56-63）：

出处 meson.build:56-63，片段经裁剪：

```meson
wlroots = dependency(
  'wlroots',
  default_options: ['default_library=static', 'examples=false', 'renderers=vulkan',
                    'backends=x11', 'xwayland=disabled', 'session=disabled'],
  version: ['>=0.17.0', '<0.18.0'],
)
add_project_arguments('-DWLR_USE_UNSTABLE', language: 'c')
```

> ⚠️ 上游差异（D-R1-02，洞察 I-2）：Debian 构建依赖写的是 `libwlroots-dev (>= 0.17.4-ok19)`（F-R1-016，debian/control:5-33），`ok19` 是 openKylin 自有打包后缀，暗示发行版 wlroots 携带发行补丁。拿到上游官方 0.17 release 未必能构建，受支持基线是 openKylin 发行包。

另有两类可选项：libunwind 为 feature(auto)，经 `HAVE_LIBUNWIND` 条件编译，缺失时回退 glibc `backtrace()`（F-R1-010）；tracy 是默认关闭的 profiler 选项，限定 0.11 系列（F-R1-011）。Xwayland 子构建固定探测 9 个 xcb 库（F-R1-013）。

> ⚠️ 上游差异（D-R1-02）：README 运行时依赖清单列有 libseat，但根 meson 未声明该 dependency，且 wlroots 以 `session=disabled` 构建；会话由 kywc 自有的 src/backend/session/（仅 logind 一种实现）承担，详见 [04 后端层](/concepts/04-backends.md)。README 同时未列 libdisplay-info、libpipewire、libunwind（F-R1-017）。

## 构建三步（本次未执行）

项目文档口径给出的最小构建流程为（F-R1-151，README.md:42-47）：

以下命令本次均未执行，仅转述 README 口径：

```bash
meson setup build -Dbuildtype=debugoptimized
ninja -C build
meson install -C build --skip-subprojects
```

安装依赖可用 `apt build-dep kylin-wayland-compositor`（需配置 deb-src 源，README.md:38-40，本次未执行）。配置结束时 meson 会打印 Directories 与 Configuration 两段 summary，列出全部协议开关与 extra 路径（F-R1-034）。

版本字符串在配置期确定：初值为 project version 1.3.0；存在 `dpkg-parsechangelog` 时用其输出覆盖，存在 git 时追加 `.g<7位短hash>`，最终注入 `-DKYWC_VERSION`（F-R1-002）。

> ⚠️ 上游差异（D-R1-01）：meson.build 工程版本 1.3.0 与 debian/changelog 顶端 1.3.1-ok36 不一致。故 Debian 构建产物的 `KYWC_VERSION` 实际为 `1.3.1-ok36[.g<hash>]`，非 Debian 直编为 `1.3.0[.g<hash>]`。

## 44 个 meson 选项与 HAVE_* 裁剪链

meson_options.txt 共 44 个选项，脚本复核分布（F-R1-018~020）：

- **boolean 37 个**：默认 true 35 个；仅 `ukui_theme`、`tracy` 默认 false；
- **feature 3 个**：libunwind、libxcb-errors、nls（值 auto）；
- **string 4 个**：plugin_directory（默认空串）、extra_icon_path、extra_apps_path、extra_pixmap_path。

完整 44 行名单与含义以事实清单 F-R1-018 和 meson_options.txt 原文为准，这里只讲裁剪机制与三组代表：

1. **功能/构建门**：xwayland、examples、tools、portal、libkywc 分别门控同名子目录（F-R1-026）；
2. **协议族开关**：命名即协议族，如 wlr 族 `wlr_output`/`wlr_layer_shell`/`wlr_foreign_toplevel`，kde 族 `kde_output`/`kde_plasma_shell`/`kde_blur`，ukui 族 `ukui_shell`/`ukui_window_management`/`ukui_effect`，以及 wayland staging 的 `xdg_toplevel_icon`/`xdg_toplevel_tag`（F-R1-018）；
3. **路径与主题**：三个 extra_* 路径经宏同时传给 C 与 C++（F-R1-022）；plugin_directory 留空时回退 `${prefix}/lib/kylin-wlcom/plugins`，经 `PLUGIN_DIR` 宏传入（F-R1-023）。

裁剪链为三层：**meson 选项 → `-DHAVE_*` 0/1 编译宏 → 源码 `#if HAVE_*` 门控**。每个协议/功能选项都映射为一个 HAVE 宏，共 32 个（F-R1-021，meson.build:177-210），xwayland 单独产出 `-DHAVE_XWAYLAND`（F-R1-014）。此外还有编译期探测型宏：libinput 三个符号探测、`HAVE_EVENTFD`、`HAVE_LINUX_SYNC_FILE`（F-R1-027、F-R1-028）；nls 的实际可用性由是否找到 msgfmt 决定，独立于 nls 选项值（F-R1-025）。

发行构建再固定一层：Debian rules 强制 `-Dukui_theme=true --buildtype=debugoptimized`（上游默认 ukui_theme=false，F-R1-024）。这意味着「protocols/ 里有 XML」不等于「运行时有该 global」，详见 [02](/concepts/02-wayland-wlroots-basics.md) 与 [12 协议全景](/concepts/12-protocols.md)。

## 命令行接口：5 个长选项与短串 hdD:s:vV

主程序的命令行定义在 src/main.c：5 个长选项 help/debug/version/session/verbose（F-R1-038，main.c:38-42），getopt 短串 `"hdD:s:vV"`，仅 `-D`、`-s` 带参数（F-R1-038，main.c:198）。

| 选项 | 含义 | 证据 |
|---|---|---|
| `-h, --help` | 打印 usage 退出 | main.c:203-206 |
| `-d, --debug` | 日志级别升至 KYWC_DEBUG | F-R1-040 |
| `-V, --verbose` | 日志级别升至 KYWC_INFO（默认 KYWC_WARN） | F-R1-040 |
| `-v, --version` | 打印 `kylin-wlcom version <KYWC_VERSION>` 退出 | F-R1-042 |
| `-s, --session <process>` | 启动后拉起会话进程，发行版传 `ukui-session` | F-R1-124 |
| `-D <flag>` | 扩展调试开关，共 6 个 flag，见下 | F-R1-039 |

6 个 `-D` flag（仅短形式，main.c:70-82）：`noxwayland`（关 Xwayland）、`logtostdout`（日志转 stdout）、`loginmtime`（改用 CLOCK_MONOTONIC 时间戳）、`lognoratelimit`（关日志限速）、`nosessionbinding`（会话退出不连带终止合成器）、`nolazyxwayland`（关闭 Xwayland 惰性启动）。未知名只打印 "Unknown debug flag"（F-R1-039）。

> ⚠️ 上游差异（D-R1-03）：README 写成 `-D, --debug <options>` 且仅举 3 个 flag；源码中 `--debug` 是不带参数的 `-d`，`-D` 没有长形式，flag 共 6 个。man 页（data/kylin-wlcom.1.scd）只收录 h/d/s/v/V，完全未提 `-D`（F-R1-131）。以源码为准。

## 日志：默认文件、级别与限速

- 默认写入 `$HOME/.log/kylin-wlcom.log`，目录不存在时创建；`-Dlogtostdout` 时改到 stdout（F-R1-109，README.md:66 与之一致）。
- 单文件上限 1 MiB，超限按时间戳轮转重命名（F-R1-108）。
- 六档级别 DEBUG/INFO/WARN/ERROR/FATAL/SILENT，可用环境变量 `KYWC_LOG_LEVEL` 设置，非法值回退原级别（F-R1-112）。
- 默认限速 interval=5000ms、burst=10，按线程独立计数，被抑制条数定期汇报；`-Dlognoratelimit` 关闭（F-R1-111）。
- 运行时还可经 com.kylin.Wlcom D-Bus 调级别/限速（见 [03](/concepts/03-startup-architecture.md)，F-R1-113）。

## 环境变量：ENV.md 21 条与源码 24 个去重名

项目文档 docs/ENV.md 登记 21 个条目：15 个 `KYWC_*`、2 个 XCURSOR、4 个应用侧变量（F-R1-115）；而源码中共有 24 个去重变量名、27 个 getenv 调用点——合成器本体消费 17 个 `KYWC_*` 加 7 个标准变量（F-R1-114）。按用途分组（完整变量名与行号以 F-R1-114/F-R1-115 为准，此处不全贴）：

- **日志**：`KYWC_LOG_LEVEL`；
- **显示/后端**：`KYWC_BACKEND`（仅识别精确值 `fbdev`，F-R1-119）、`KYWC_FB_DEVICES`、`KYWC_DRM_DEVICES`、`KYWC_DRM_NO_ATOMIC`、`KYWC_DRM_NO_MODIFIERS`、`KYWC_SOFTWARE_COLOR`、`KYWC_OUTPUT_FILL_WALLPAPER`——在 [04 后端层](/concepts/04-backends.md) 与 [07 输出管理](/concepts/07-output-management.md) 展开；
- **渲染**：`KYWC_RENDERER`（gl/gles2/pixman/vulkan）、`KYWC_EGL_NO_MODIFIERS`、`KYWC_RENDERER_ALLOW_SOFTWARE`、`KYWC_ENABLE_TIMELINE`——在 [05 渲染](/concepts/05-rendering.md) 展开；
- **输出**：`KYWC_DISABLE_DIRECT_SCANOUT`、`KYWC_USE_LAYOUT_MANAGER`；
- **应用侧 4 个**：DRI_PRIME、__VK_LAYER_NV_optimus、__NV_PRIME_RENDER_OFFLOAD、__GLX_VENDOR_LIBRARY_NAME，ENV.md 自述供 vkcube/glxgears 等应用使用，合成器源码不读取（F-R1-116）；
- **其他**：XCURSOR_THEME、XCURSOR_SIZE、`KYWC_FORCE_QUIRKS`（十进制 quirks 位，如 2 强制软件鼠标）。

> ⚠️ 上游差异（D-R1-04）：`KYWC_XWAYLAND`（Xwayland 可执行路径，src/xwayland/server.c:133）与 `KYWC_EIS_SOCKET`（EIS 调试 socket 名，src/backend/eis/backend.c:93）在源码有 getenv 消费点，ENV.md 未收录。另 5 个标准变量（WAYLAND_DISPLAY、WAYLAND_SOCKET、DISPLAY、XDG_RUNTIME_DIR、XDG_SESSION_ID）源码使用但文档不列。

## 双层 JSON 配置

配置是「系统默认 + 用户覆盖」的双层 JSON 模型（src/config/config.c）：

- 系统层固定读 `/etc/kylin-wlcom/config.json`，缺失仅 WARN（F-R1-068）；该文件由 data/config.json 安装（出厂仅 7 个顶层键：theme、outputs、layouts、Inputs、Seats、InputAction、plugins，F-R1-074）；
- 用户层为 `~/.config/kylin-wlcom/config.json`，目录不存在时创建，读取失败则新建空 object；server 销毁时回盘（F-R1-067、F-R1-069）；
- 各子系统以 `config_manager_add_config(name)` 按名取两层 json 的子对象，全仓共有 12 个配置段名（大小写不统一，如 "Inputs"/"Seats"/"Effects"/"Xwayland"，F-R1-072、F-R1-073）。

## 会话单元：desktop → wrapper → target → service

发行安装的图形会话入口不是合成器本体，而是一条 systemd 用户单元链（F-R1-122~128）：

```text
wayland-sessions/kylin-wlcom.desktop
  Exec = kylin-wlcom-wrapper
      └─ D-Bus StartUnit kylin-wlcom.target ("replace")
             └─ Requires/BindsTo kylin-wlcom.service
                    ExecStart = kylin-wlcom -s ukui-session
```

- desktop 文件 `Exec=kylin-wlcom-wrapper`（F-R1-123）；
- wrapper 是无命令行参数的 sd-bus/sd-event 程序：打开用户总线后先 `drop_session_envs`，再 StartUnit，target 进入 inactive 即退出，全程输出走 journald（F-R1-127、F-R1-129）；
- wrapper 清环境有精确规则：仅当本进程 getenv 为空且名字命中 DISPLAY/XAUTHORITY/WAYLAND_DISPLAY/WAYLAND_SOCKET 或 `XDG_` 前缀时，通过 User Manager 的 UnsetEnvironment 下发删除（F-R1-121）；
- target 仅两行 Requires/BindsTo service（F-R1-125）；service 的 ExecStart 为 `kylin-wlcom -s ukui-session`（F-R1-124）。

`-s ukui-session` 使合成器在事件循环首次 idle 时 fork/execvp 会话进程，并默认与之「同生共死」（binding_session，详见 [03](/concepts/03-startup-architecture.md)）。另含一条 udev 规则把 graphics 子系统节点设为 video 组 0666（F-R1-126）。

## Debian 打包：5 个二进制包与 3 个子工具

debian/control 定义 5 个二进制包（F-R1-133）：主包 kylin-wayland-compositor、-client（libkywc 的 so/头/pkgconfig）、-tools、-examples、xdg-desktop-portal-wlcom（详见 [14](/concepts/14-security-portal.md)、[15](/concepts/15-libkywc-clients.md)）。主包 install 清单含 kylin-wlcom、wrapper、两个 man page，以及两个 Qt 工具 kylin-magnifier 与 wldialog（F-R1-136）。

tools/ 目录构建 3 个子工具（F-R1-141），此处各一句话：

- **wlcctrl**：纯 C 命令行遥控工具，42 个子命令覆盖窗口/工作区/截图/鼠标/键盘，按命令行出现顺序依次执行（F-R1-143、F-R1-145）；
- **wldialog**：Qt5/QML 对话框工具，经 socket fd 收发 JSON（DialogSocket 协议 1.0），由合成器 view/killer.c 以 `spawn_dialog("wldialog")` 拉起（F-R1-146、F-R1-148）；
- **kylin-magnifier**：Qt5 Widgets/DBus 放大镜，暴露 org.ukui.Magnifier 接口（F-R1-149、F-R1-150）。

三者的深入使用与 libkywc 编程面统一在 [15 客户端面](/concepts/15-libkywc-clients.md) 讲解。

## 相关概念

- 前导：[00 kywc 全景](/concepts/00-overview.md)
- 后继：[02 Wayland 与 wlroots 基础](/concepts/02-wayland-wlroots-basics.md) — HAVE_* 宏裁剪的协议如何经 scanner 生成并注册
- [03 启动序列与 server 总体架构](/concepts/03-startup-architecture.md) — `-s` 会话拉起与 server 生命周期
- [04 后端层](/concepts/04-backends.md) — KYWC_BACKEND/KYWC_DRM_DEVICES 等显示侧环境变量
- 信源：[项目文档登记](/references/project-docs.md)、[源码信源登记](/references/source-code-map.md)、[R1 事实清单](/references/facts-build-startup.md)
