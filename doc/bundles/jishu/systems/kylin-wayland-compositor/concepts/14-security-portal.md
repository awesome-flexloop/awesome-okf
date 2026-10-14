---
type: Concept
title: "安全模型与 xdg-desktop-portal-wlcom：四层仲裁、截图录屏、远程桌面与 EI"
description: "梳理内置安全四层（global_filter/ky_security/protector/security_context）、security demo 插件，以及 portal 五接口、PipeWire node 透传与 EIS fd 闭环"
tags: [security, portal, screencast, remote-desktop, ei, pipewire, dbus]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r4
    resource: /references/facts-effect-plugin.md
    title: R4 特效/插件/安全簇事实清单
  - id: facts-r5
    resource: /references/facts-protocols-clients.md
    title: R5 协议/libkywc/portal/示例事实清单
  - id: facts-r1
    resource: /references/facts-build-startup.md
    title: R1 构建/启动/配置/打包事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：安全子系统是画面与数据离开合成器前的最后一道仲裁——[10 特效](/concepts/10-effects-framework.md)里的 capture/stream manager 产出帧，是否允许某客户端拿到、拿到时要不要遮罩，由本篇的四层仲裁决定；portal 则是把这些能力以 xdg-desktop-portal 标准暴露给沙箱应用的进程外前台。

## 内置安全四层：固定启动顺序

安全核心在 src/security/ 下 5 个无条件编入主程序的 `.c`（F-R4-017）。`security_manager_create` 按**固定顺序**创建四个子系统（F-R4-081，src/security/security.c:722-726）：

```c
global_filter_manager_create(server);    /* 第 1 层：Wayland global 过滤 */
ky_security_manager_create(server);      /* 第 2 层：kywc-security-v1 仲裁协议 */
security_protector_create(server);       /* 第 3 层：遮罩渲染 */
security_context_manager_create(server->display); /* 第 4 层：wp_security_context_v1 */
```

仲裁结果是 4 档枚举 `security_decision`：ALLOW / SOFT_ALLOW / SOFT_DENY / DENY（F-R4-071，include/security/security.h:31-36）；受检动作 6 类：ACCESS_NODE、ACCESS_OUTPUT、WRITE_SELECTION、READ_SELECTION、START_DRAG、DROP（F-R4-070）。规则约束：SOFT_ALLOW 必须实现 notify 回调，SOFT_DENY 必须实现 access 回调（F-R4-080，security.c:233-237）。仲裁对象以两类 wlr_addon 挂接，名字串分别为 "security_object" 与 "security_buffer"（F-R4-079）。

### 第 1 层 global_filter：谁能 bind 哪个 global

global_filter.c 调 `wl_display_set_global_filter`（:103）注册全连接级过滤器；没有任何插件注册 filter 时 filter_global 直接返回 true（:39-42），内置规则处目前只有 TODO 注释（:37）。真实的过滤规则由插件经接口表的 `security_add_global_filter/remove_global_filter` 挂载（F-R4-082）。消费实例有两个：security 插件的自定义 global 仅对其 gui 进程可见（F-R4-063），XWayland 的 xwayland_shell_v1 global 仅对 X server client 可见（[13](/concepts/13-xwayland.md)，xwayland.c:58-62）。

### 第 2 层 ky_security：kywc-security-v1，默认 DENY

ky_security.c 是自研协议 protocols/kywc-security-v1.xml 的服务端：manager global `kywc_security_manager_v1` v1（ky_security.c:369-370，F-R4-083），含 2 个 interface、manager 3 请求（destroy、get_security_for_surface、get_security_for_output），security 对象 3 请求（destroy/enable/disable）+ 4 事件（failed/cancelled/enabled/touched）（F-R4-094、F-R4-096）。

仲裁语义要点：

- security 对象**默认决策是 DENY**——enabled 初值 true（ky_security.c:270-271、320-321，F-R4-084），即未显式 enable 前不放行；
- surface 必须已经 map，取祖先节点时排除 WORKSPACE/LAYER/VIEW_PROXY 三种角色（ky_security.c:198-206，F-R4-086）；
- touched 事件载荷格式 `"%s(%d)"`，以 (comm, pid) 拼成 "进程名(pid)" 发给决策方（F-R4-085）。

### 第 3 层 protector：遮罩渲染

protector 决定被 DENY 的画面区域「画成什么样」。默认模式 **FILL_IMAGE**、默认颜色白色 `{1,1,1,1}`（protector.c:268-269，F-R4-087）；当没有设置保护图时，使用内置缺省图：200x100 缓冲，monospace 字体、红色 30px 文字 **"SECURITY"**（F-R4-088，protector.c:39-51）。安全视图圆角固定 `{12,12,12,12}`（F-R4-090）；节点 `has_effect` 时跳过 security 渲染（F-R4-091）。

> **差异块：protector 颜色通道序疑似 r/g 与 b 交换（F-R4-089，静态读码不判运行时）**
> 函数签名是 `security_set_protector_color(float r, float g, float b, float a)`（protector.c:289），结构体赋值却是：
> `protector->color = (struct wlr_render_color){ r, b, g, a };`（protector.c:295）
> 第 2、3 实参位置交换。若 `wlr_render_color` 字段序确为 r,g,b,a，则经此接口设置的颜色绿蓝通道对调；默认白色 {1,1,1,1} 不受影响。是否在实际画面显现，本篇不做运行时裁定。

### 第 4 层 security_context：wp_security_context_v1

security_context.c 实现 wayland-protocols staging 的 wp_security_context_v1（:422 注册，F-R4-092）。create_listener 对 listen_fd 做强校验：fstat 必须是 S_ISSOCK，getsockopt SO_ACCEPTCONN 必须确认是 listening socket（:322-349）；禁止嵌套创建 context（:206-210）；context global 自身也加 filter——已持有 context 的 client 不再看到该 global（:431）。状态携带 sandbox_engine/app_id/instance_id（F-R4-076）。

### 仲裁接口面：include/security/security.h

四层之外，安全子系统对内暴露一套小而稳定的 C API（F-R4-072~077，include/security/security.h）：

- `struct security_interface` 是仲裁方实现的三回调：access（同步裁决，对应 SOFT_DENY）、notify（异步通知，对应 SOFT_ALLOW）、destroy（:79-86）；
- 三个构造器按对象类型分流：`security_create_for_view/output/selection`（:113-121），插件接口表里的 `security_view_create` 等最终分别落到 security_create_for_node（view 树节点）、scene_output 与 selection（interface.c:137-158）；
- 对象 API：selection 检查、access、ref/unref、set_decision（:124-138）；protector 三值枚举与三个 setter 声明（:160-170）；
- 头文件还提供 inline `security_action_client`（:93-110）方便按动作快速生成客户端描述；渲染侧检查与 target/region 接口在 include/security/render.h（F-R4-093），供场景渲染管线在提交前询问「这块区域要不要遮罩」。

## security 插件与第 35 个 XML

四层是内置子系统；[11](/concepts/11-plugin-system.md) 讲过的 security demo 插件是它们的**第一个外部消费者**（src/plugin/security/，F-R4 第七、八节）：

- 插件 FIXED、ABI 1.0，setup 里注册快捷键 "Alt+Shift+d:no" 拉起一个 memfd 内嵌启动的 Qt5 GUI（F-R4-056~059）；
- GUI 通过独立协议 **kywc_security_configuration_v1** 配置 protector：这是全树第 35 个 XML（src/plugin/security/security.xml），MulanPSL-2.0 头，4 个请求 destroy/set_protector_mode/set_protector_color/set_protector_image，mode 枚举 fill_none(0)/fill_color(1)/fill_image(2)，颜色为预乘 alpha、uint 按百分比解释，image 强制 DRM_FORMAT_ARGB8888（F-R4-066~069）；global 在 security.c:466 手写注册，且经 global filter 只对 gui client 可见（F-R4-063、F-R5-052）；
- 判定依据是客户端环境变量 **LAUNCHED_FROM**（security.c:161-163、233-239，F-R4-060）：new_view hook 对带该变量的 view 创建 **SOFT_DENY** 仲裁（:269-303），selection 同样创建 SOFT_DENY（:484-486，F-R4-061、F-R4-062）；
- 处理 3 个 protector 请求：mode 直通；color 的 UINT32 分量除以 UINT32_MAX 转 float；image 经 mmap 并按 width×height×4 校验大小（F-R4-064）。

## portal 主体：xdg-desktop-portal-wlcom

portal/ 是一个独立可执行文件 `xdg-desktop-portal-wlcom`（11 个 `.c`，装入 libexecdir，F-R5-089），作为 xdg-desktop-portal 的后端（impl）。它本身不渲染、不碰 PipeWire 库，只做三件事：弹 D-Bus 对话、经 libkywc 向合成器要帧/流、把 EIS fd 与 PipeWire node id 回传。

总线条理（F-R5-090~093，portal/main.c）：

- D-Bus well-known name `org.freedesktop.impl.portal.desktop.wlcom`（main.c:15），user 总线 request_name，订阅 NameOwnerChanged；
- 初始化顺序 dbus → wayland → remote_desktop → input_capture → access → screenshot → screencast（main.c:177-210）；
- Wayland 侧复用 libkywc 4 项能力：OUTPUT | THUMBNAIL_EXT | TOPLEVEL | STREAM（portal/wayland.c:143-146），output 变化联动 ZonesChanged 与截图/流的 changed 信号；
- 命令行 5 选项：-h/-d(debug)/-v(version)/-r(replace)/-V(verbose)（F-R5-091）。

### 5 个 impl 接口

| 接口 | version / 能力 | 方法要点 | 证据 |
|---|---|---|---|
| RemoteDesktop | v2，AvailableDeviceTypes=3（keyboard+pointer） | 13 方法：CreateSession/SelectDevices/Start、NotifyPointerMotion/MotionAbsolute/Button/Axis/AxisDiscrete、NotifyKeyboardKeycode/Keysym、NotifyTouch×3、**ConnectToEIS→h**；除 Start 外几乎全 UNPRIVILEGED | remote_desktop.c:20-21、1106-1146（F-R5-094） |
| InputCapture | v1，SupportedCapabilities=3 | 7 方法：CreateSession/GetZones/SetPointerBarriers/Enable/Disable/Release/**ConnectToEIS→h**；4 信号 Disabled/Activated/Deactivated/ZonesChanged | input_capture.c:18-19、843-868（F-R5-095） |
| ScreenCast | v5，AvailableSourceTypes=MONITOR|WINDOW=3，AvailableCursorModes=HIDDEN|EMBEDDED=3 | CreateSession/SelectSources/Start；默认 source MONITOR、默认 cursor Hidden | screencast.c:12-13、451-471（F-R5-096） |
| Screenshot | v2 | Screenshot、PickColor（均 UNPRIVILEGED） | screenshot.c:16-17、559-569（F-R5-097） |
| Access | **无 version 属性** | 仅 AccessDialog 1 方法 | access.c:13、234-244（F-R5-098，差异见下） |

Session/Request 子对象各实现 Close，session 关闭发 Closed 信号；会话三类 REMOTE_DESKTOP/INPUT_CAPTURE/SCREENCAST，响应码 SUCCESS=0/CANCELLED=1/ENDED=2（F-R5-099、F-R5-100）。

### UI 不在进程内：spawn_dialog("wldialog") + unix socket + JSON

portal 不链接 GTK/Qt Widgets。所有交互（区域选择、设备选择、访问确认）经 `spawn_dialog("wldialog")` 拉起独立工具 wldialog，返回 unix socket fd，以 json-c 收发 JSON 请求/回复（F-R5-107，portal/stream.c:922、screenshot.c:495、access.c:196、input_capture.c:328、remote_desktop.c:623；spawn 声明 src/util/spawn.c:120）。RemoteDesktop 的 SelectDevices 还额外经 org.freedesktop.Notifications.Notify 发一条通知（remote_desktop.c:604-605）。wldialog 本体见 [15](/concepts/15-libkywc-clients.md)。

### PipeWire node id 透传：portal 不链 libpipewire

ScreenCast/RemoteDesktop 的视频面有一个重要边界：**portal 的 meson 依赖里没有 libpipewire**（portal/meson.build:17-21，F-R5-104）。真正的 PipeWire 节点在合成器侧创建（[10](/concepts/10-effects-framework.md) 的 ky_stream manager），经自研协议 kywc-stream-v1 的 `created(uint32 node)` 事件抛出；portal 的 handle_stream_ready 收到 node 后，仅在 Start 回复里以 `"u"` 原样回给 xdg-desktop-portal 前端（stream.c:181-215、1006）。流的创建按源类型分派 `kywc_stream_create_from_output/toplevel`（stream.c:323-352，F-R5-106）。截图路径同理：libkywc thumbnail + kywc_buffer 静态库把帧写为临时 PNG（mkstemps，screenshot.c:331-357，F-R5-108）。

### EIS fd：自有 D-Bus 回到合成器，与 EIS 后端闭环

输入注入面：portal 进程内用 libei 建 sender（ei_new_sender + ei_setup_backend_fd，seat 绑定 POINTER|KEYBOARD 能力，F-R5-101），但承载事件的 EIS fd 不属于 portal——它通过合成器自有的 D-Bus 接口取得（F-R5-102）：

- RemoteDesktop：总线 `com.kylin.Wlcom`、路径 `/com/kylin/Wlcom/EIS/RemoteDesktop`、接口 `com.kylin.Wlcom.EIS.RemoteDesktop`、方法 ConnectToEIS（remote_desktop.c:1088-1089）；
- InputCapture：对应 `/com/kylin/Wlcom/EIS/InputCapture`（input_capture.c:21-22、156）；
- 返回的 `h` 类型 fd 不做加工，原样回复给前端（:1095-1101）。合成器侧的 EIS backend 把该 fd 接入其虚拟输入体系（server 启动时 eis_backend_create 加入 multi backend），形成「portal 收键 → EIS → 合成器 seat」闭环。键码映射（xkbcommon）在 portal 进程内完成（F-R5-103）。

### data 单元与打包差异

四个数据单元（F-R5-109~112）：wlcom.portal（声明 5 接口、UseIn=UKUI）、ukui-portals.conf（把 5 接口首选指向 wlcom）、systemd user 单元（ConditionEnvironment=WAYLAND_DISPLAY、Type=dbus）、D-Bus service activation 文件。

> **差异块一：三处安装/激活路径不一致（D-R5-150，静态事实）**
> meson 实际安装到 `${libexecdir}`（Debian 系通常 /usr/libexec，portal/meson.build:33）；systemd 单元 ExecStart=/usr/libexec/xdg-desktop-portal-wlcom；而 D-Bus service activation 文件写 Exec=/usr/bin/xdg-desktop-portal-wlcom。D-Bus 激活与 systemd 激活二选一时尚无统一解析结果，本篇不裁定实际触发哪条。
>
> **差异块二：Access vtable 无 version（D-R5-151）**
> 其余 4 个接口都导出 version(u) CONST 属性，Access 缺失；wlcom.portal 声明的接口集合与代码 5 接口对账一致，无多无少。
>
> **差异块三：CURSOR_MODE_METADATA 声明但未映射（D-R5-156）**
> stream.h:16-20 有 CURSOR_MODE_METADATA=4，kywc-stream 协议 enum 也含 metadata；但 ScreenCast 只上报 HIDDEN|EMBEDDED=3，映射函数 `mode == EMBEDDED ? EMBEDDED : HIDDEN` 把 METADATA 一并落成 HIDDEN（stream.c:308-312）。

ei_sender 内部结构（ei_sender.h:8、24-56）持有 eis_fd、ei 实例、ei_seat、pointer/abs_pointer/keyboard 三类设备与 sequence_num、xkb_keyboard；导出的注入函数覆盖 motion/motion_absolute/button/axis/axis_discrete/keycode/keysym，RemoteDesktop 13 个 Notify* 方法最终都汇入这一层（F-R5-101）。portal 11 个 `.c` 的分工也由此清晰：main/request/session 管总线与会话生命周期，remote_desktop/input_capture/screencast/screenshot/access 是五个 impl 面，stream 管 kywc-stream 与 node，ei_sender 管 EI，wayland 管 libkywc context。

另记两条打包事实：portal 独立成包 xdg-desktop-portal-wlcom，debian/control 中 **Conflicts: xdg-desktop-portal-wlr**（F-R1-133）；portal 有独立翻译域 xdg-desktop-portal-wlcom（i18n 细节见 [15](/concepts/15-libkywc-clients.md)，F-R5-113）。

## 端到端一图流

以「沙箱内 Flatpak 应用请求录整个屏幕」为例：应用经 xdg-desktop-portal 调到 wlcom 的 ScreenCast.CreateSession/SelectSources → portal spawn wldialog 让用户确认源 → Start 时经 libkywc 调 kywc-stream，合成器侧 security 层完成帧仲裁、ky_stream 建好 PipeWire node → portal 把 node id 回给前端；若该会话同时是 RemoteDesktop，输入事件走 libei → portal 自有 D-Bus 取 EIS fd → 合成器 EIS backend → seat。截图（Screenshot）与内部 screenshot 特效（[10](/concepts/10-effects-framework.md)）共用同一套 capture/thumbnail 能力，只是出口分别是 portal PNG 与 D-Bus 兼容接口。

## 相关概念

- [11 插件系统：ABI 1.0 与唯一 security 示例](/concepts/11-plugin-system.md)
- [10 特效框架：capture/stream 与截图](/concepts/10-effects-framework.md)
- [12 协议全景](/concepts/12-protocols.md)
- [13 XWayland 兼容层](/concepts/13-xwayland.md)
- [15 libkywc 客户端库、示例生态与自带工具](/concepts/15-libkywc-clients.md)
