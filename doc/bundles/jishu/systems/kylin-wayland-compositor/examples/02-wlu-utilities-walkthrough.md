---
type: Example
title: "wlu 示例工具库与三个状态客户端：monitor / output_doctor / virtual_desktop"
description: "走读 examples/lib 静态库 wlu 的 display/buffer/input/window 四件，以及 monitor、output_doctor、virtual_desktop 三个客户端如何分别走 libkywc 与裸协议两条路线"
tags: [kylin-wlcom, wlu, wayland-client, output-management, virtual-desktop, libkywc, walkthrough]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r5
    resource: /references/facts-protocols-clients.md
    title: R5 协议/libkywc/portal/示例事实清单
  - id: facts-r1
    resource: /references/facts-build-startup.md
    title: R1 构建/启动/配置/打包事实清单
  - id: facts-r4
    resource: /references/facts-effect-plugin.md
    title: R4 特效/插件/安全事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 固定快照 4df6562
---

> **本篇在教程中的位置**：本篇是实战篇第 2 篇，跟读示例专用工具库 `examples/lib/`（wlu）和三个"观察/配置桌面状态"的小工具。前置概念建议先读 [12 协议全景](/concepts/12-protocols.md)（弄清 kywc 自研协议与 kde/plasma 协议族的边界）与 [15 libkywc 与客户端生态](/concepts/15-libkywc-clients.md)。所有行号锚定固定提交 `4df6562`。

## wlu 的定位：examples 私有、静态链接的客户端脚手架

wlu 不是合成器库，也不安装。[examples/lib/meson.build](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/examples/lib/meson.build):38-42 把 5 个源文件编成 `static_library('wlu', ...)`，再用 `declare_dependency` 暴露为 `libwlu`（:44-48），只有 examples 内的 `alpha_modifier` 和顶层 `thumbnail` 两个目标链接它（examples/meson.build:65、47）。

- 五个源：`src/display.c`、`src/buffer.c`、`src/input.c`、`src/window.c`、`src/wlu.c`（meson.build:1-7）；
- 内链三套协议生成码：xdg-shell、xdg-decoration、linux-dmabuf-v1（:9-18）；
- 依赖 wayland-client、pixman-1、libdrm、gbm、egl、glesv2（:20-34）——它同时支持纯 SHM 与 EGL/GL 两条绘制路径。

公开面只有一个头 [examples/lib/include/wlu.h](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/examples/lib/include/wlu.h)；`wlu_private.h` 是内部结构头，结构体布局不对外承诺。

## wlu.h 公开面速览

- display 组（wlu.h:34-50）：`wlu_display_create(callbacks, flags)`，标志位仅 `WLU_DISPLAY_CREATE_NONE/EGL`（:22-25）；回调只有 `registry_global` 与 `registry_global_remove` 两个（:27-32）；外加 `run/exit` 与三个 getter。
- window 组（:56-129）：`wlu_window_create_info` 8 字段（:76-85），创建标志 RESIZABLE/TRANSPARENT/DECORATION/GL/GLES（:56-63），6 个窗口回调（:65-74），双缓冲常量 `WLU_SWAPCHAIN_COUNT = 2`（:54）。
- buffer/draw 组（:133-199）：缓冲类型 `WLU_BUFFER_TYPE_SHM/DMABUF_GL`（:133-137，VK 留空注释），三种导入入口 `wlu_buffer_import_shmbuf / import_shmbuf_gl / import_dmabuf`（:178-185），多平面上限 `WLU_MAX_DMABUF_PLANES = 4`（:147），以及 `wlu_draw_init/texture/fini` 三件套（:195-199）。

## display.c：连接与 registry 轮询的固定套路

核心是一个"内部先 bind 刚需全局，再把事件透传给使用者"的 registry handler。`registry_global`（examples/lib/src/display.c:112-144）依次识别 6 个全局：`wl_compositor`（钳到 v4，:117-119）、`xdg_wm_base`（:120-123）、`zxdg_decoration_manager_v1`（:124-126）、`wl_seat`（:127-129）、`wl_shm`（:130-132）、`zwp_linux_dmabuf_v1`（仅 EGL 标志下 bind，:133-138）；最后无条件回调使用者挂的 `event_callbacks.registry_global`（:141-143）——alpha_modifier 正是借这个透传口子 bind 到自己的私有协议。

连接流程 `wlu_display_connect`（:198-228）是 Wayland 客户端的标准"双 roundtrip"：第一次拿全局（:210），第二次处理绑定后事件（:212），随后检查 compositor/xdg_wm_base/seat 三者必须就位（:214）。EGL 路径额外做两步：`display_init_gbm`（:159-178）写死打开 `/dev/dri/renderD128`（:161）建 gbm device，`display_init_egl`（:180-196）用 `eglGetPlatformDisplay(EGL_PLATFORM_GBM_KHR, ...)` 初始化；任何一步失败都不致命，靠 `wlu_display_supports_egl`（:298-301）事后判断。公开构造/析构为 `wlu_display_create`（:230-250）与 `wlu_display_destroy`（:252-296），事件循环 `wlu_display_run`（:318-326）就是 `wl_display_dispatch` 包一层 running 标志。

## buffer.c：memfd+mmap 的 SHM 缓冲与 dmabuf/GL 缓冲

SHM 路径从"匿名文件"开始：`create_anonymous_file`（examples/lib/src/buffer.c:24-40）用 `memfd_create("wlu-shared", MFD_CLOEXEC | MFD_ALLOW_SEALING | MFD_NOEXEC_SEAL)`（:26，旧内核回退不带 NOEXEC_SEAL），加 `F_SEAL_SHRINK` 再 `ftruncate`。`buffer_init_shm`（:55-85）随后 `mmap(PROT_READ|PROT_WRITE, MAP_SHARED)`（:67），建 `wl_shm_pool` 并 `wl_shm_pool_create_buffer`（:74-76），挂 release 监听（:77）。

GL 路径 `buffer_init_dmabuf`（:108-181）用 gbm 分配 `GBM_BO_USE_RENDENDING` 的 bo（:112-113），经 `zwp_linux_buffer_params_v1` 提交并 roundtrip 等 created 事件（:123-129），再走 `eglCreateImageKHR`（:147-148）→ `glEGLImageTargetTexture2DOES`（:163）→ 挂到 FBO（:165-168）。统一入口 `wlu_buffer_create`（:183-208）按窗口的 buffer_type 二选一；析构 `wlu_buffer_destroy`（:210 起）对称 munmap/删 GL 资源。三种导入函数（:282、:306、:368）供外部把现成的 thumbnail fd 变成可绘制缓冲，03 篇的 thumbnail/ 与 gui/ 都靠它。

## input.c：seat 能力监听与极简按键/指针转发

`seat_capabilities`（display.c:28-47）在 seat 给出 keyboard/pointer 位时 `wl_seat_get_keyboard/get_pointer` 并挂上 input.c 的监听。input.c 自己只实现"转发给当前活动窗口"：

- `keyboard_key`（examples/lib/src/input.c:25-33）取 `display->activated_window`，若窗口注册了 `.keyboard` 回调就转发原始 key/state；
- `pointer_motion`（:64-78）先把 `wl_fixed_t` 转 double 存进 `display->pointer_position`（:67-72），再转发；`pointer_button`（:80-89）回调时带上最后位置；
- 其余事件（keymap/enter/leave/modifiers/axis）都是空实现（:9-23、:54-62、:91-94）；
- 两组监听通过 `wlu_input_keyboard_listener()`（:49-52）与 `wlu_input_pointer_listener()`（:104-107）暴露给 display.c。

也就是说 wlu 不做 xkb 键位解析，alpha_modifier 收到的 `KEY_EQUAL/KEY_MINUS` 是 linux/input-event-codes 键码（examples/alpha_modifier.c:6、80、86）。

## window.c：xdg-toplevel 窗口与双缓冲交换链

`wlu_window_create`（examples/lib/src/window.c:253-329）按 info 建 surface→xdg_surface→xdg_toplevel（:289-297），非 RESIZABLE 时锁死 min/max 尺寸（:302-305），DECORATION 标志下请求 server-side decoration（:306-311），设置 app_id/title（:316-320），触发使用者的 `.create` 回调后首帧 commit（:322-326）。

configure 处理体现双缓冲：`xdg_surface_configure`（:65-109）先 `ack_configure`（:67），尺寸变化时重建两个交换链缓冲（:75-90），挂 frame callback（:92-93），执行 resize 回调并立即提交一帧防闪烁（:99-107）。`commit_buffer`（:13-49）负责 attach、不透明区/脏矩形（pixman_region32，:28-38）与 commit。绘制调度 API 是 `wlu_window_request_draw`（:464-474）与内部 `wlu_window_try_invoke_draw`（:496，声明于 wlu_private.h:177），帧信号到达才真正重绘（frame_done :51-60）。

防重复绘制的状态机在内部结构里（wlu_private.h:110-121）：`swapchain[2]` 双缓冲、`draw_pending{done,callback,data}` 保证同一帧只画一次、`frame_done` 跟随合成器帧信号翻转；缓冲被合成器占超时，release 事件（buffer.c:42-49）会再触发一次 try_invoke_draw。窗口查询 API 集中在 window.c:403-461：`wlu_window_get_width/height`（:403/408）、`get_buffer(window, swapchain_index)`（:433）、maximized/minimized 状态对（:438-458）；alpha_modifier 与 thumbnail 两个客户端正是只用这一小组 getter + `request_draw` 就完成了各自的绘制循环。

## wlu.c：格式映射与纹理绘制的 GL/pixman 双实现

前半是纯格式表：`wlu_format_to_shm/from_shm`（:10-47）、`to_drm/from_drm`（:49-81）、`to_pixman`（:83-98），SHM 与 DRM fourcc 双向兼容（:39-42 特意兼容合成器用 DRM fourcc 发 shm 格式的情况）。后半 `wlu_draw_init`（:180-199）内嵌编译一段纹理 blit 着色器（顶点着色器 :153-161、片元 :163-170）；`wlu_draw_texture`（:314-327）按两端缓冲类型分派：DMABUF_GL 对走 `draw_texture_gl`（:201-253，FBO+glDrawArrays），SHM 对走 `draw_texture_pixman`（:255-312，pixman composite，尺寸不一还带双线性缩放 :295-302）。

## wlu 的两个真实消费方：标志位与回调用法对照

wlu 在本仓只有两个消费者，它们恰好示范了两套标志组合（源码可直接核对）：

| 用法点 | alpha_modifier.c | thumbnail.c |
|---|---|---|
| display 标志 | `WLU_DISPLAY_CREATE_NONE`（:113） | `WLU_DISPLAY_CREATE_EGL`（:214） |
| 窗口标志 | `DECORATION | TRANSPARENT`（:126） | `RESIZABLE | DECORATION | GLES`（:48-49） |
| 像素格式 | `WLU_FORMAT_ARGB8888`（:124） | `WLU_FORMAT_ARGB8888`（:46） |
| display 回调 | `registry_global` 用来 bind 私有协议（:101-103） | 传 NULL（:214） |
| window 回调 | `create` + `keyboard`（:105-108） | 只用 `destroy`（:32-34） |
| 绘制方式 | draw 回调里 cairo 直接写 SHM（:16-54） | draw 回调里 `wlu_draw_texture` blit（:15-22） |
| 外部缓冲导入 | 无 | dmabuf / shmbuf-gl / shmbuf 三路（:67-84） |

读这张表就能确定 wlu 的设计意图：纯软件绘制零 EGL 依赖也能跑（alpha_modifier），而需要把合成器给的 dmabuf 贴进窗口时才开 EGL 并走导入 API（thumbnail）。

## monitor：libkywc 路线的状态打印器（不走裸协议）

需要先纠正一个直觉：[examples/monitor.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/examples/monitor.c) 虽然叫 monitor，却**不直接 bind 任何 kde/wlr output 协议**，examples/meson.build:27-32 显示它只依赖 `libkywc`。它演示的是稳定客户端库路线（F-R5-120）：

- `main`（monitor.c:120-135）以 `WORKSPACE | OUTPUT | TOPLEVEL` 三个能力位调 `kywc_context_create(NULL, caps, &context_impl, NULL)`（:122-124），随后 `kywc_context_dispatch` 阻塞（:129）；
- 上下文接口 `context_impl`（:114-118）把 new_output/new_toplevel/new_workspace 转给三个打印函数，并在新建对象上 `kywc_*_set_interface` 订阅后续状态（:36、:70、:111）；
- 输出内容直接读 libkywc 的快照结构：`output->mode->refresh / 1000`（:45-46，refresh 单位 mHz）、toplevel 的 workspaces 数组按 `MAX_WORKSPACES`（=15）遍历（:84-88），并用 `kywc_toplevel_has_children`（:89）打印父子关系。

三组对象各自的 interface 都只实现了 `state` 与 `destroy` 两槽（:28-31、:62-65、:103-106），这正是 libkywc 三组快照接口的全部回调面；`state(obj, mask)` 拿到的掩码在本程序被忽略——它每次都全量重打印（:18-21、:52-55、:93-96），不演示按位增量更新。`main` 末尾注释掉的 `kywc_context_process(ctx)`（:130）也值得留意：`dispatch` 是内部阻塞循环，`process` 是配合外部 poll/`get_fd` 的非阻塞步进，gui 客户端用的是后者（见 [03 篇](./03-libkywc-qml-thumbnail.md)）。整个 monitor.c 只有 135 行，是对比"裸写客户端（kde_keystate 77 行）"与"库封装客户端"代码量的直接样本。

## output_doctor：裸连 kde output-management/v2 的配置工具

[examples/output_doctor.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/examples/output_doctor.c) 共 1154 行，门控 `have_kde_output`（examples/meson.build:7-16），链接 5 套协议生成码：kde-output-management-v2、kde-output-device-v2、kde-primary-output-v1、dpms、xdg-output。文件头注释自陈"some code is from wlr-randr"（:18-20）。

数据模型在开头：`struct output_manager`（:22-32）同时握 management/primary/dpms/xdg 四个全局与设备/输出两条链表；`output_device_state`（:34-44）记 current/pending 两套状态。`registry_handle_global`（:630 起）bind 五个全局：management（:640）、device（:654）、`kde_primary_output_v1` 固定 v2（:659）、dpms manager v1（:664）、xdg-output v3（:697）。

配置应用是本篇的核心段（:235-311）：逐设备 diff current 与 pending，对每个差异发一个 configuration 请求——enable（:241/247）、mode（:251）、transform（:255）、position（:260）、scale（`wl_fixed_from_double`，:265）、overscan（先查 capability 位，:268-272）、vrr_policy（:273-278）、rgb_range（:279-284）；主输出在版本足够时 `set_primary_output`（:287-295）；最后有差异才 `kde_output_configuration_v2_apply`（:297-299），DPMS 走另一条 `org_kde_kwin_dpms_set`（:309）。命令行能力见 usage（:1021-1037），main（:1039）在拿不到 management 时直接报"compositor doesn't support kde-output-management-v2"（:1056-1059）。

字符串到协议枚举的映射表在文件前部写死：subpixel（:91-98）、transform 八向（:100-109）、vrr_policy 三值 never/always/automatic（:111-115）、rgb_range 三值 automatic/full/limited（:117-120）。模式清单来自 device 的 mode 事件：`output_device_mode_size`（:319-326）与 `output_device_mode_refresh`（:328-334）把宽高与刷新率（mHz）填进链表，--mode 参数据此匹配，--preferred 则用 mode 事件给出的 preferred 标记。配置事务由 :229 的 `kde_output_management_v2_create_configuration` 开启，configuration 自身的 applied/cancelled 事件经 `output_config_listener`（:230）维护 pending_configs 计数后才销毁。

## virtual_desktop：plasma-virtual-desktop 客户端

[examples/virtual_desktop.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/examples/virtual_desktop.c) 门控 `have_kde_virtual_desktop`（examples/meson.build:18-25），bind 的全局名是 `org_kde_plasma_virtual_desktop_management`（virtual_desktop.c:161-164），版本钳到 2（:162）——对应的是 kywc 自研 workspace 协议之外的 **kde/plasma 协议**（服务端 src/view/kde_virtual_desktop.c:284，F-R5-028）。

事件模型用两级 listener + pending_done 计数：management 的 `desktop_created/done/rows`（:147-152），每个 desktop 再挂 id/name/activated/deactivated/done/removed 六个事件（:92-99）；main 里循环 dispatch 直到 pending_done 归零（:234-239），保证打印前状态收齐。动作请求有三个：`request_create_virtual_desktop(management, name, 0)`（:271-272）、`request_remove_virtual_desktop`（:288-289）、对单个桌面 `request_activate`（:284）。无请求参数时打印清单（:182-193、:307），`--monitor` 进入持续监听（:310-312），用法串在 :205-211。

资源回收是显式的：收到 removed 事件时 `desktop_removed`（:80-90）先销毁协议对象、摘链表再 free name/id/结构体；退出前 :316-323 统一销毁所有 desktop 与 management、销毁 registry、flush 后断连。写 Wayland 客户端易漏的一点在这里有示范——发完写请求后 :300-305 先 `prepare_read/read_events/dispatch_pending` 再 flush + roundtrip，确保请求真正送达并处理完成。

## 建议的读码顺序

如果只带着"怎么写一个原生 Wayland 客户端"的目的，推荐顺序：先读 kde_keystate.c（77 行，见 [01 篇](./01-effect-plugin-walkthrough.md)，掌握 connect→registry bind→roundtrip→dispatch 五件套）→ 再读 monitor.c 看 libkywc 如何把同一套样板封掉 → 然后读 wlu/display.c 对比手写版 registry 轮询 → 最后读 output_doctor.c 的多全局、多状态事务。需要自己画窗口时再回头看 wlu/window.c + buffer.c；thumbnail.c 与 pipewire.c 属于"两种事件循环合体"的进阶题，放到最后。

## 其余三个独立示例（一句话定位）

- **pipewire.c**（门控无，依赖 libkywc + kywc_buffer + libpipewire-0.3）：把 kywc stream 客户端接入 PipeWire 主循环——`pw_loop_add_io(..., kywc_context_get_fd(...), ...)`（examples/pipewire.c:429-431）让两个循环共用线程，创建流时光标模式固定 HIDDEN（:434、:437）；参数 `<output|toplevel> <uuid> [avoid_dmabufs 0|1]`（:387-406，F-R5-125）。
- **thumbnail.c**：libkywc 缩略图 + wlu 显示窗的最小组合，先建带 EGL 的 wlu_display 再 `kywc_context_create_by_display`（:214-221），深入走读放在 [03 篇](./03-libkywc-qml-thumbnail.md)。
- **ukui-effect-test.c**（门控 `have_ukui_effect`）：ukui-effect-v1 私有协议客户端，自建 SHM 窗口后触发 fade/slide/animation-curve（F-R5-121），不属于输出/桌面管理范畴。

## 如何用 meson 编译这些小工具（本次未执行）

以下命令**本次未执行**，边界以构建文件为准：

- 总开关 `-Dexamples=true`（boolean，默认 true；meson.build:243-245 控制是否 `subdir('examples')`）。examples/meson.build:30/47/73 直接引用 `libkywc`、`kywc_buffer` 变量，它们只在 `-Dlibkywc=true`（默认 true，meson.build:239-241）时定义；静态阅读看两个开关需同时为 true（该组合未做配置验证）。
- 条件目标：output-doctor 需 `-Dkde_output=true`，virtual-desktop 需 `-Dkde_virtual_desktop=true`，kde_keystate 需 `-Dkde_keystate=true`，alpha_modifier 需 `-Dalpha_modifier=true`，ukui-effect-test 需 `-Dukui_effect=true`（均默认 true）。
- foreach 产出的 8 个可执行文件均未设 install，默认只在构建树；`-Dtools=true` 是**另一条边界**——tools/ 下的 wlcctrl/wldialog/magnifier 不属于 examples，virtual-keyboard/virtual-pointer 两套协议码也挂在 have_tools 下（F-R5-039/044/144）。

## 为什么 monitor 链 libkywc，而 output_doctor / virtual_desktop 不链

这是 examples 目录里最值得对照的架构选择（对应洞察 I-4 的"客户端库稳定"层，见 [15 libkywc 与客户端生态](/concepts/15-libkywc-clients.md)）：

| | monitor | output_doctor | virtual_desktop |
|---|---|---|---|
| 协议来源 | kywc 自研 output/toplevel/workspace v1 | kde output 族（device v8/management v9 等） | plasma-virtual-desktop v2 |
| 接入方式 | 链接 libkywc，收 C 快照结构 + 回调 | 手写 registry bind + 协议 listener | 同左 |
| ABI 承诺 | 67 个 `kywc_*` 稳定 API（kywc.syms） | 无，协议版本自己钳 | 无 |
| 能力覆盖 | 只覆盖 kywc 五协议 | libkywc 不管控 KDE 配置协议，只能裸连 | 同上 |

规则很直白：**合成器自有能力（屏幕/窗口/工作区/截图）走 libkywc；上游 KDE/Plasma 兼容协议没有封装库，按 wayland-scanner 生成的 client 头直连。** 两条路线在 examples 里都有完整范本，按目标协议选边即可。

## 相关概念

- [15 libkywc 与客户端生态](/concepts/15-libkywc-clients.md)：67 个稳定 API、provider 机制与两条客户端路线
- [12 协议全景](/concepts/12-protocols.md)：kywc/ukui/kde/plasma 协议族与编译期门控
- [03 libkywc + QML 缩略图客户端走读](./03-libkywc-qml-thumbnail.md)
- [01 跟写一个特效插件](./01-effect-plugin-walkthrough.md)
- [R5 协议/libkywc/portal/示例事实清单](/references/facts-protocols-clients.md)
