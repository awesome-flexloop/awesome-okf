---
type: Concept
title: "XWayland 兼容层：rootless xwm、atom 管理与选择/DND 桥"
description: "讲清 kywc 如何拉起 Xwayland 进程、rootless xwm 如何把 X11 窗口接入 view 体系，以及约 90 个 atom、剪贴板/INCR/Xdnd 桥与 256 定点缩放"
tags: [xwayland, xwm, x11, atom, clipboard, dnd, compatibility]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r3
    resource: /references/facts-input-view.md
    title: R3 输入/视图/XWayland 簇事实清单
  - id: facts-r1
    resource: /references/facts-build-startup.md
    title: R1 构建/启动/配置/打包事实清单
  - id: facts-r5
    resource: /references/facts-protocols-clients.md
    title: R5 协议/libkywc/portal/示例事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：XWayland 是横在 legacy X11 应用与 [09 view 体系](/concepts/09-view-workspace.md)之间的适配层——它在进程外拉起一个真正的 X server，又在进程内扮演它的窗口管理器（xwm），把 X11 窗口翻译成 kywc view。本篇对应 src/xwayland/ 的 15 个 `.c`（顶层 11 个 + selection/ 子目录 4 个，F-R3-004、F-R3-008）。

## 两道开关：构建期 HAVE_XWAYLAND 与运行时 -Dnoxwayland

XWayland 支持受两层独立开关控制（I-1 三态裁剪的典型样本）：

- **构建期**：meson 选项 `xwayland`（boolean，默认 true，meson_options.txt:13-16）。src/meson.build 中 `if have_xwayland` 才进入 src/xwayland 子目录（F-R1-015）；子构建固定拉取 9 个 xcb 库（xcb、composite、ewmh、icccm、render、res、shape、xfixes、sync，libxcb-errors 可选），并探测 4 个特性宏 `HAVE_XWAYLAND_LISTENFD / NO_TOUCH_POINTER_EMULATION / FORCE_XRANDR_EMULATION / TERMINATE_DELAY`，`XWAYLAND_PATH` 默认 `/usr/bin/Xwayland`（F-R1-013、F-R1-014，src/xwayland/meson.build:13-32）；
- **运行时**：即使编入，命令行 `-Dnoxwayland` 会把 `enable_xwayland` 置 false，`xwayland_manager_create` 直接记录 "Xwayland is disabled by cmdline" 并返回（F-R1-041，src/xwayland/xwayland.c:73-76）。相关调试 flag 还有 `-Dnolazyxwayland`（关闭 lazy 启动）。

## rootless 模型：fork + displayfd + lazy 重启

kywc 不自己实现 X11 协议，而是启动一个真实的 Xwayland 进程并充当其 WM。进程管理在 [src/xwayland/server.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/xwayland/server.c)：

- Xwayland argv 固定含 `-rootless -core -terminate`；`-wm` 传入 WM socket fd，就绪通知走 `-displayfd`；listen fd 有两套路径由 `HAVE_XWAYLAND_LISTENFD` 选择；`WAYLAND_SOCKET` 经环境变量传入；可选 `-auth`、`-noTouchPointerEmulation`、`-force-xrandr-emulation`（F-R3-138，server.c:45-115）；
- 进程采用两次 fork + displayfd 读就绪管道；`XAUTHORITY` 由 generate_xauthority_file 生成并 setenv，失败则 unsetenv（F-R3-139，server.c:253-325、472-518、509-514）；
- **lazy 模式**：选项 `{.lazy = lazy_xwayland, .enable_wm = true, .terminate_delay = lazy ? 10 : 0}`（xwayland.c:97-101）。Xwayland 退出后 lazy 模式下经 server_start_lazy 重启（F-R3-139，server.c:225-227）；
- 可执行路径可用环境变量 `KYWC_XWAYLAND` 覆盖，否则取编译期 XWAYLAND_PATH（F-R3-138，server.c:133-135、479）。

进程骨架本身复用 wlroots 的 `wlr_xwayland_server`（xwayland.c:102-106 日志原文 "Cannot create wlroots xwayland server"）。

### xwm 的启动与会话关系

ready 事件到达后（F-R3-137，xwayland.c:44-56）：`xwm_create(wm_fd[0])` 建立 xcb 连接并接管 WM 职责，随后 `xwm_set_seat` 绑定默认 seat0；start 事件中把 xwayland_shell 的特殊 client 绑定为 XWayland server client（xwayland.c:37-42）；`DISPLAY` 环境变量被 setenv 为 display_name（xwayland.c:120）。

`xwm_create` 做的事（F-R3-140，xwm.c:3202-3289）：`xcb_connect_to_fd(wm_fd)`、把 xcb fd 挂进 wl_event_loop（`x11_event_handler`）、查询 atoms 与 shape/xfixes/sync/xres 扩展、给 root 窗订 `SUBSTRUCTURE_NOTIFY|SUBSTRUCTURE_REDIRECT|PROPERTY_CHANGE` 掩码、`xcb_composite_redirect_subwindows(MANUAL)`——**rootless 的关键**：X11 顶层窗被手动重定向，每个窗口的内容成为一个 Wayland surface，由合成器而非 X server 决定上屏；xfixes≥6 且 terminate_delay>0 时开启 client disconnect mode TERMINATE。

xwm 还创建三个 WM 窗口：持有 `WM_S0`/`_NET_WM_CM_S0` selection 的 WM 窗口（名为 "wlcom wm"）、no_focus 窗口、名为 "wlcom guard window" 的 guard 窗口，`_NET_SUPPORTING_WM_CHECK` 互相指向（F-R3-141，xwm.c:2937-2962、3169-3200）。

## xwayland_shell_v1：X11 窗口与 wlr_surface 的关联线

XWayland 给每个重定向窗口关联一个 wlr_surface，但「这个 wlr_surface 对应哪个 X11 窗口、其串行化几何如何」需要 staging 协议 xwayland-shell-v1 补充。这里 kywc **没有用 wlr 助手注册 global，而是自有实现**：src/xwayland/shell.c:155-167 的 `xwayland_shell_v1_create` 手写 `wl_global_create(display, &xwayland_shell_v1_interface, SHELL_VERSION, …, shell_bind)`，并维护 surfaces 链表与 new_surface/destroy 信号（shell.c:162-172）。

该 global 经 security 全局过滤器**仅对 XWayland server client 可见**（xwayland.c:58-62、88-95，`xwayland_filter_global` → `xwayland_check_client`）。server start 时 `xwayland_shell_v1_set_client` 完成绑定（xwayland.c:39-41）。其 XML 取自 wayland-protocols staging，meson 键 `xwayland-shell-v1` 挂在 `if have_xwayland`（protocols/meson.build:168-172，F-R5-146）。xwm 同时监听合成器 new_surface 与 shell new_surface 两个来源（F-R3-142，xwm.c:3297-3312）。

## atom 管理：约 90 个 atom、12 个 _NET_WM_STATE

xwm 不依赖外部 EWMH 库，自管一张约 90 项的 atom_map（F-R3-144，xwm.c:2622-2784，启动时 xwm_get_atoms 统一 intern，:2786-2812）。每个 atom 可挂三类处理器：`handle_surface_property`（属性通知）、`handle_client_message`（client message）、`handle_net_wm_state`（状态翻转）。分组包括：

- **WM 基础**：WM_S0、WM_PROTOCOLS、WM_STATE、WM_DELETE_WINDOW、WM_TAKE_FOCUS、WM_HINTS、WM_NORMAL_HINTS、_MOTIF_WM_HINTS；
- **EWMH 通告**：_NET_SUPPORTED、_NET_SUPPORTING_WM_CHECK、_NET_CLIENT_LIST(_STACKING)、_NET_WORKAREA、_NET_ACTIVE_WINDOW、_NET_SHOWING_DESKTOP；
- **窗口类型**：_NET_WM_WINDOW_TYPE_DESKTOP/DOCK/.../NOTIFICATION/NORMAL，以及 UKUI 私有的 _UKUI_NET_WM_WINDOW_TYPE_SYSTEMWINDOW/INPUTPANEL/LOGOUT/SCREENLOCK/WATERMARK（xwm.c:2726-2731）——这些类型是 X11 窗口映射到 kywc view 17 种角色（[09](/concepts/09-view-workspace.md)）的依据；
- **选择与 Xdnd**：CLIPBOARD、PRIMARY、TARGETS、INCR、UTF8_STRING、XdndSelection、XdndAware/Status/Position/Enter/Leave/Drop/Finished 等全套；
- **sync**：_NET_WM_SYNC_REQUEST/_COUNTER、_XWAYLAND_ALLOW_COMMITS。

`_NET_WM_STATE` 有 **12 个状态双向同步**（F-R3-145，xwm.c:215-260、1820-2008）：modal、fullscreen、maximized_vert、maximized_horz、hidden、sticky、skip_taskbar、above、below、demands_attention、skip_switcher（实际 atom 用 `_KDE_NET_WM_STATE_SKIP_SWITCHER`）、focused。client message 动作 0=REMOVE / 1=ADD / 2=TOGGLE（:1792-1818）。另外 `_NET_WM_MOVERESIZE` 的 9 个方向码映射到 move/resize，11=CANCEL 取消交互（F-R3-146）。

> **差异块：历史拼写 atom "_KWIN_UKUI_DECORAION"（D-R3-06）**
> xwm.c:2680-2681 源码原文：
> `[KWIN_UKUI_DECORATION] = {.name = "_KWIN_UKUI_DECORAION", // it has been misspelled since V10, …}`
> 枚举名是正确的 DECORATION，但 intern 到 X server 的 atom 字符串少一个 T，且源码注释自认 V10 起即拼错。这意味着线上与客户端约定的实际 wire 字面值就是错拼版本，修复需双向兼容；本篇仅记录静态事实。

## 窗口映射：从 X11 窗口到 kywc view

X11 事件总分发是 `x11_event_handler`（F-R3-143，xwm.c:2306-2378）：selection 事件最先处理（:2321），随后 shape/sync alarm，再按 create/destroy/configure/map request/map notify/unmap/property/client_message/focus_in/reparent/error 分派。

- map_request/map_notify/unmap_notify 驱动 xwayland_surface 的受管状态；窗口 withdrawn 时按 EWMH 删除其 _NET_WM_STATE（F-R3-154，xwm.c:1595-1611、1613-1672）；
- 受管 X11 窗口在 view 层有一份**自有 view_impl**：`xwl_surface_impl`（src/xwayland/view.c:334）以及 input_event_node_impl（hover/click/leave/get_root/get_toplevel，view.c:23-100）。move/resize/minimize/maximize/fullscreen/activate/sticky/above/below 等请求 1:1 映射到 view_mode 钩子，点击同样汇聚到 view_click（F-R3-147，view.c:525-663）——这保证 X11 窗口与原生窗口走同一套 stack/tablet 模式与工作区逻辑；
- override-redirect 窗口（菜单、 tooltip 等）不经受管流程，由 unmanaged.c 单独处理，restack 时保证 OR 窗口置顶且不越过最顶层受管窗口，guard 窗口作为层叠底锚；注释原文 "X11 clients expect their override_redirect windows to stay on top"（F-R3-150，xwm.c:3325-3369）；
- 焦点侧：view 激活切到原生 Wayland 窗口时，xwm 主动清 X11 焦点（xwm_handle_activate_view，xwm.c:3153-3167）。

## 剪贴板与拖放：双向 INCR 桥与全套 Xdnd

xwm 初始化三个 selection：**CLIPBOARD、PRIMARY、XdndSelection**（F-R3-141，xwm.c:3293-3295），经 xfixes 订阅 SET_SELECTION_OWNER|SELECTION_WINDOW_DESTROY|SELECTION_CLIENT_CLOSE 三类事件掩码（F-R3-155，selection/selection.c:153-220）。

桥接代码在 src/xwayland/selection/ 四个文件里：

- **incoming.c（X11 → Wayland，含 INCR）**：`xwm_handle_xfixes_selection_notify` 入口（:568），大数据走 X11 INCR 分块传输；
- **outgoing.c（Wayland → X11）**：`xwm_send_incr_chunk`（:161）同样支持 INCR；
- 来源判定靠 data_source_is_xwayland / primary_selection_source_is_xwayland，xwm 销毁时清理源自 X11 的 seat selection（F-R3-156，xwm.c:2546-2554）；
- **dnd.c 实现全套 Xdnd**：client message 入口 xwm_handle_selection_client_message（:264），Wayland 侧 start_drag 时挂接（xwm_seat_handle_start_drag :610），负责发送 XdndStatus/Position/Enter/Leave/Drop/Finished（:687、:714），日志有 "Wayland drag dropped over an Xwayland window"（:510）。由此 Wayland 原生应用与 X11 应用之间可以双向拖放（F-R3-157）。

## 256 定点缩放、DPI 与键窃听

**整屏缩放**用定点整数而非浮点贯穿 X11 边界（F-R3-148，xwayland.c:158-188）：

```c
/* 源码原文，src/xwayland/xwayland.c:164-178（节选） */
int32_t K = (int32_t)(xwayland->xwm->scale * 256.0f);
/* unscale: (value*256 + K/2) / K；scale: (value*K + 128) / 256 */
```

256 为定点基数，正负值分别四舍五入并 CLAMP 到 int32。xwm->scale 取 output_manager_get_max_scale；XWayland 客户端光标 surface、workarea 几何都经 xwayland_scale/unscale 换算（:199-213；输入侧 X11 客户端光标 hotspot 的 unscale 见 F-R3-062）。同时 xwm_update_xresources 向 RESOURCE_MANAGER 写 `Xft.dpi=scale*96` 与 Xcursor.size/theme（xwm.c:3038-3055），让 X11 应用按 DPI 自渲染。

**键窃听（eavesdrops）**默认模式 `ALL_KEYS_WITH_MODIFIER`（另一档 NONE_KEYS），在 xwayland_manager_create:84 设定（F-R3-136、F-R3-151）。管理器维护按下键位图（pressed_keys[4]，覆盖 Linux keycode 8-255），保证「已转发给 Xwayland 且仍按下的键，其释放事件一定转发」以维持 Xwayland 键盘状态一致（eavesdrops.c:22-30、140-204），在 xwm_create 末尾创建（xwm.c:3320）。

其他兼容细节：通过 Xres（xcb_res ≥1.2）读客户端 PID 作为 _NET_WM_PID 之外的通道（F-R3-149，xwm.c:2882-2906）；支持 _NET_WM_PING 的窗口 ping 超时 10000ms（:3220、3437-3464）；root 窗 _NET_WM_NAME 写 "LG3D" 以绕过 Java 应用在非 reparenting WM 下白屏的问题（F-R3-153，xwm.c:2918-2929）。

## 11 个顶层源文件的职责地图

src/xwayland/meson.build:62-74 显式枚举 11 个顶层 `.c`，加 selection/ 子目录 4 个共 15 个（F-R3-008）。除前文已展开的 server.c、xwm.c、shell.c、view.c、unmanaged.c、eavesdrops.c 外：

| 文件 | 职责 |
|---|---|
| sockets.c | display socket 生命周期：open_display_sockets(int socks[2])、unlink_display_sockets、set_cloexec（:29、157、173） |
| xauth.c | generate_xauthority_file（xauth.c:68）：生成 .Xauthority，server.c:509 取用并配合 setenv/unsetenv（F-R3-139） |
| grab.c | X11 表面的指针 grab：xwayland_grab_pointer(wlr_surface, wlr_seat, grab)（grab.c:189） |
| config.c | 配置节 "Xwayland"（src/xwayland/config.c:47），读取 eavesdrops 键模式等运行时选项 |
| selection/selection.c | 三 selection 的 xfixes 订阅与统一入口 xwm_handle_selection_event |
| selection/incoming.c | X11 → Wayland 方向，含 INCR 接收 |
| selection/outgoing.c | Wayland → X11 方向，含 INCR 分块发送 |
| selection/dnd.c | Xdnd 全套 client message 状态机 |

xwm 与 seat 的关系在运行时可变：seat 切换时经 xwm_update_seat → xwm_set_seat 更新（xwayland.c:19-28），避免 xwm_destroy 后 hover 重入触发问题（注释见 :21）。

## 与原生 Wayland view 路径的对照

| 维度 | 原生 xdg view（[09](/concepts/09-view-workspace.md)） | XWayland view |
|---|---|---|
| 表面来源 | xdg_surface map 信号（xdg_shell.c:537-584） | X11 map_request/map_notify，经 rootless 重定向为 wlr_surface + xwayland_shell 关联 |
| 协议 | xdg-shell（wlroots 跟踪器） | X11 协议 + xcb；xwayland_shell_v1 仅对 X server client 可见 |
| view_impl | xdg 系列 | xwl_surface_impl（view.c:334） |
| 状态同步 | xdg_toplevel 状态事件 | 约 90 atom 上的属性/client message，12 个 _NET_WM_STATE 双向写 |
| 剪贴板/DND | wl_data_device / primary-selection | 经 selection/ 四文件双向桥，含 INCR 与 Xdnd |
| 缩放 | Wayland scale + fractional-scale | 256 定点 + Xft.dpi/Xcursor RESOURCE_MANAGER |
| 特殊窗口 | layer-shell / popup | override-redirect → unmanaged.c |
| PID | 内核 peer 凭证 | _NET_WM_PID + Xres 查询 |

## 已知限制（静态读码口径）

- 唯一进入 docs/KNOWN_ISSUES.md 的问题与 X11 无直接关系：部分 UKUI 应用未走 SDK 接口导致双标题栏，需应用侧修改（F-R1-154）；
- XWayland 路径上存在针对具体客户端的硬编码兼容（LG3D/Java，D-R3-08）与错拼 atom（D-R3-06），属于长期兼容债务而非临时开关；
- 本篇全部结论来自固定提交的静态阅读，未运行实际 X11 客户端验证；行为排障建议结合运行日志（"Xwayland is ready"、display 名等在 xwayland.c:46、121-122）。

## 相关概念

- [09 视图与工作区](/concepts/09-view-workspace.md)
- [08 输入系统](/concepts/08-input.md)
- [12 协议全景：34 个 XML 与编译期裁剪](/concepts/12-protocols.md)
- [01 构建与运行](/concepts/01-build-run.md)
- [14 安全模型与 xdg-desktop-portal-wlcom](/concepts/14-security-portal.md)
