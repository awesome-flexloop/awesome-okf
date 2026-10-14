---
type: Concept
title: "视图、工作区与窗口管理：view 状态机、workspace、widget 与数据共享"
description: "读懂 kywc_view 的 16 角色/12 能力/18 层、view_map 状态机、21 个窗口动作、默认 4 上限 15 的工作区、各家 shell 接线地图、widget/主题与 util 基础设施"
tags: [wayland, wlroots, window-management, workspace, virtual-desktop, widget, xdg-shell]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r3
    resource: /references/facts-input-view.md
    title: R3 输入/视图/工作区事实清单
  - id: facts-r2
    resource: /references/facts-graphics.md
    title: R2 后端/渲染/场景/输出事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：[08 输入系统](/concepts/08-input.md) 的绑定分发最终调用本篇的 window_action 与 workspace 切换；本篇把窗口状态翻译成 [06 场景图](/concepts/06-scene-graph.md) 上树节点的使能/位置/层级。各家 shell 协议的 XML 细节在 [12 协议全景](/concepts/12-protocols.md)，X11 窗口如何变成 view 在 [13 XWayland](/concepts/13-xwayland.md)。

view 层（src/view/，37 个顶层 .c 加 view_p.h，另含 tile/ 子目录 3 个 .c 加 tile_manager_p.h——递归共 42 个 C/H，即 40 .c + 2 .h）回答的是「窗口」语义：角色、能力、状态、工作区归属、贴靠几何与交互模式；它本身不画像素。

## kywc_view：16 角色、12 能力位与 18 层

公开结构 `kywc_view` 在 include/kywc/view.h。三组核心数字（F-R3-105、F-R4-176；行号已经独立复核）：

- **角色枚举 17 个枚举器 = 16 个真实角色**：ROLE_UNDEF=-1 加 NORMAL(0) 到 AUTHENTICATION(16)——DESKTOP、PANEL、ONSCREENDISPLAY、NOTIFICATION、TOOLTIP、CRITICALNOTIFICATION、SYSTEMWINDOW、INPUTPANEL、LOGOUT、SCREENLOCK、SCREENLOCKNOTIFICATION、WATERMARK、APPLETPOPUP、SWITCHER、AUTHENTICATION（include/kywc/view.h:46-64）；
- **能力位 12 个**（include/kywc/view.h:87-101，`enum kywc_view_capabilities`，1<<0..1<<11 加 CAPABILITIES_ALL 哨兵）：MINIMIZABLE/MAXIMIZABLE/CLOSEABLE/FULLSCREENABLE/MOVABLE/RESIZABLE/FOCUSABLE/ACTIVATABLE/ABOVEABLE/BELOWABLE/MINIMIZE_BUTTON/MAXIMIZE_BUTTON，配套 IS_ 判定宏；
- 状态字段：mapped/minimized/maximized/fullscreen/activated/tiled/kept_above/kept_below/sticky/skip_taskbar/skip_switcher/demands_attention/modal。

窗口**层级 enum layer 共 18 层**（include/view/view.h:20-59，注释标注取自 kwin）：DESKTOP、WATERMARK、BELOW、NORMAL、DOCK、ABOVE、NOTIFICATION、ACTIVE、SYSTEM_WINDOW、SWITCHER、POPUP、INPUT_PANEL（第 12 层，枚举值 11）、CRITICAL_NOTIFICATION、LOGOUT、UNMANAGED、SCREEN_LOCK、SCREEN_LOCK_NOTIFICATION、ON_SCREEN_DISPLAY。焦点变化时 `view_manager_update_input_panel_layer` 抬升 IME 表面所在层（view.c:1657-1682，F-R3-117）。

内部派生结构 struct view（include/view/view.h:104-196，F-R3-106）持有 surface/tree/surface_tree、parent/children、多工作区的 view_proxies、saved geometry/tiled/output 与 pending configure。实现接口 view_impl 有 8 个回调（ping/configure/close_popups/close/destroy/configure_timeout/update_usable_area/get_icon_buffer），xdg 与 xwayland 各一份（F-R3-107）。

## view_map 状态机与两种 view_mode

`view_init`（view.c:375-446，F-R3-108）把视图插入 view_manager.views，在 LAYER_NORMAL 建 scene_tree 且**默认 disable**，设初始输出、角色 NORMAL，发 new_view。

xdg toplevel 的 map 由 wlr xdg_surface map 信号触发 xdg_view_handle_map→view_map（src/view/xdg_shell.c:537-584，F-R3-110）。`view_map`（view.c:621-710，F-R3-109）的顺序是：

1. 发 premap 事件，让外部（特效/插件）先插手；
2. 调当前 view_mode 的 view_map 钩子；
3. 按 minimized 使能树节点 `scene_node_set_enabled`（:633）；mapped=true；
4. 有 pending action 时补兜底几何并 configure；按 buffer 主输出更新 view 输出；
5. kywc_view_activate → view_set_focus（:654-656）；更新圆角；
6. 挂 map 动效（slide 优先，否则按 startup_geometry 选 scale 或 fade，:667-680）；
7. 发 map/new_mapped_view、对每个 proxy 发 workspace.view_enter、取消 show-desktop、`cursor_rebase_all`（:692-709）。

view 的点击/悬停不直接写策略，而是转发给当前**视图模式**：view_mode_interface 定义 map/unmap、各类 request、click/hover、mode enter/leave 等钩子（src/view/view_p.h:16-48，F-R3-112）。两种实现：

- **stack_mode**（src/view/stack_mode.c，桌面模式）：stack_mode_view_click 按下即 kywc_view_activate + view_set_focus（stack_mode.c:197-206）；
- **tablet_mode**（src/view/tablet_mode.c，平板模式）：同接口的另一套交互。

焦点链 view_do_activate→view_set_activated 驱动 wlr 焦点与 layer 重排；view_set_focus 有三道拦截：全局认证视图、模态后代替换、FOCUSABLE 能力，最终 `seat_focus_surface(seat, view->surface)` 并 ping（view.c:1470-1552、1684-1706，F-R3-113）。

## 21 个窗口动作与贴靠/保存几何

枚举 window_action 实测 **21 个真实动作**（include/view/action.h:13-36，F-R3-007）：最小化/最大化/关闭、MOVE/RESIZE、KEEP_ABOVE/BELOW、MENU、8 个贴靠（4 方向 tile + 4 方向 half-screen）、4 个跨输出（SEND_LEFT/RIGHT_OUTPUT 及最大化版）、CAPTURE。

总分发 `window_action`（src/view/action.c:250-317，F-R3-115）：最小化/最大化/关闭直接调 kywc_view_*；MOVE/RESIZE 移光标并 window_begin_*；菜单仅在 SSD title 存在且非全屏时显示（:287）；跨输出在 fullscreen/modal 时直接拒绝（:200）。function_id 到动作的映射表 view_manager_get_window_action 覆盖 16 个 FUNC_ID；view_manager_handle_window_action 限定 NORMAL/AUTHENTICATION 角色，且认证视图只允许 CLOSE（action.c:319-376，F-R3-116）。贴靠几何 view_get_tiled_geometry 处理 NONE/CENTER/ALL 与 8 方向（view.c:448-488），状态切换均有 do_* 实现并发 kywc_view 事件（view.c:1708-1953，F-R3-114）。

配套机制各自独立成文件：interactive.c（MOVE/RESIZE 交互）、positioner.c（定位）、modal.c（模态窗口能力降级）、maximize_switcher.c（最大化遍历）、killer.c（无响应窗口）、exclusive.c（排他层）。窗口内置快捷键 16 条（Alt+F4/F9/F10、Win+方向贴靠等，action.c:28-50，F-R3-118）；SSD 三态位 KYWC_SSD_NONE/TITLE/BORDER/RESIZE/ALL，全屏/最大化/贴靠不圆角（view.c:510-541，F-R3-120）。

## workspace：默认 4、上限 15、每区 3 棵 layer 子树

- `MAX_WORKSPACES=15`（include/view/workspace.h:10）；默认 **num_workspaces=4**（src/view/view.c:2980，F-R3-124），配置键 "num_workspaces"/"workspace_names"，配置名 "Views"。
- workspace_manager 默认 **rows=2**，columns=ceil(count/rows)（workspace.c:424、370-379，F-R3-123）。
- `workspace_create`（workspace.c:541-594，F-R3-125）建 **3 棵 layer 子树 BELOW/NORMAL/ABOVE**（view_proxy 挂这三棵；18 层里的其他层由 view_manager 统一管理），角色 SCENE_ROLE_WORKSPACE，默认 disable，position 插入并移位后续区，自动加入 sticky 视图；达 15 拒绝创建。
- `workspace_activate`（:660-703）：旧区 disable 树、重挂 proxy，关 show-desktop，置 current，激活顶层 view，cursor_rebase_all。

切换方式有三类：

1. **快捷键 8 条**：Ctrl+Alt+Left/Right、Win+Ctrl+Left/Right、Ctrl+F1..F4；F1-F4 在代码内映射 switch_to(4..7)→position 0..3（workspace.c:46-106，F-R3-127）。
2. **4 指横滑跟手**：touchpad/touchscreen 四指左右滑，四阶段 BEFORE|TRIGGER|AFTER|STOP 全启用；touchpad 位移除以 300.0、触屏除以 1.0，**阈值 TRANSLATION_THRESHOLD=0.35**，边缘回缩系数 0.2（workspace.c:21-22、108-187，F-R3-128）。
3. 新建/删除：FUNC_ID_NEW_WORKSPACE 在 count 位置创建，删除仅在 count>1 时删最后一个并把视图迁往相邻区（workspace.c:289-333、596-658，F-R3-129、130）。

> ⚠️ 功能缺口（D-R3-05）：直切快捷键只有 Ctrl+F1..F4 共 **4 个**，而工作区上限 15 且可动态新建——第 5 个及以后的工作区只能靠手势或协议切换，这是代码事实。

对外协议同时出两个口（workspace.c:437-439，F-R3-131）：自有 **kywc-workspace-v1**（ky_workspace_manager_create）与 KDE **plasma-virtual-desktop**（kde_virtual_desktop_management_create，受 HAVE_KDE_VIRTUAL_DESKTOP 保护）。

### view_proxy：一个 view 如何同时出现在多个工作区

view 与 workspace 不是直接一对多，而是经 **view_proxy** 中介（include/view/workspace.h:45-55，F-R3-122）：proxy 同时挂在 view 的 view_proxies 链表与 workspace 的链表上，并持有该工作区内的挂载 scene_tree。view_map 时对每个 proxy 发 workspace 的 view_enter 事件（view.c:695-698）；删除工作区时视图迁移就是 view_add_workspace + view_set_current_proxy + 销毁旧 proxy 三步（workspace.c:621-628，F-R3-130）。sticky 视图在新建工作区时自动 add 进新区（workspace.c:514-527、589-591）。

### view_manager 内置快捷键、手势与特殊功能

view_manager 自身注册内置快捷键 6 条、手势 8 条（src/view/action.c:494-652，F-R3-119）：Win+d/h/m/g/shift+m/home 对应显桌面/隐藏等桌面操作（如 "win+d:no"→TOGGLE_DESKTOP_VISIBILITY）；3/4 指 touchpad/touchscreen 上下滑出多任务视图或显桌面。

特殊功能（显桌面、多任务、最大化遍历、平板任务栏、贴靠手势）在 `view_manager_handle_special_function` 先行处理（src/view/action.c:390-460，F-R3-121）：多任务视图并非合成器内绘制，而是经 D-Bus 调 org.kylin.switch 的 /MultitaskView show/hide；最大化遍历由 maximize_switcher_show 弹出。普通窗口功能再经 view_manager_handle_function→window_action 落到上节的 21 动作。

## 各家 shell 在 src/view/ 的接线地图

view 层一个显著特点是为多个桌面生态各写一份接线文件，它们都产出统一的 struct view：

| 生态/协议 | 文件 |
|---|---|
| xdg 标准 | xdg_shell.c（toplevel）、xdg_popup.c、xdg_dialog.c、xdg_activation.c、xdg_toplevel_icon.c、xdg_toplevel_tag.c |
| layer-shell | wlr_layer_shell.c |
| foreign-toplevel | wlr_foreign_toplevel.c、ext_foreign_toplevel.c |
| KDE Plasma | kde_plasma_shell.c、kde_plasma_window.c、kde_virtual_desktop.c、kde_blur.c、kde_slide.c |
| UKUI | ukui_shell.c、ukui_window.c、ukui_blur.c、ukui_startup.c |
| kywc 自有 | ky_toplevel.c、ky_workspace.c |
| 装饰/菜单 | ssd.c、decoration.c、window_menu.c |
| 贴靠 | tile_flyout.c 加 tile/ 四文件：tile_assist.c、tile_linkage.c、tile_manager.c、tile_manager_p.h |

view 目录文件数口径：磁盘实测 40 个 .c + 1 个私有 .h = 41 个 C/H（顶层 37 + tile/ 3 .c + view_p.h；另含 tile/meson.build），与早期基线 42 差 1，属计数口径差异（D-R3-01）。

## widget、数据共享与主题

**widget**（src/widget/，widget.c/menu.c/scaled_buffer.c）是挂在 scene_tree 下的自绘 scene_buffer 封装：widget_create(parent) 建树，绘制经 painter_draw_buffer，用 struct draw_info 描述 solid/hover/border/corner/text/shortcut/font/align（src/widget/widget.c:20-65、487-501，F-R3-132）；menu 由 menu_item 链表 + 子菜单构成，show/hide 时持有 pointer/keyboard/touch 三类 grab，支持阴影/模糊装饰与超出输出翻转项（menu.c:1081-1121，F-R3-134、135）。绘图能力本身来自 [05 篇](/concepts/05-rendering.md)的 painter。

**数据共享**（选择/拖放）的协议实现在 input 簇：wl_data_device_manager v3、primary-selection v1、data-control v1、xdg-toplevel-drag v1，DnD 在合成器内有 pointer/keyboard/touch 三套 grab（F-R3-098~103，机制见 [08 输入](/concepts/08-input.md)）；Wayland↔X11 的 CLIPBOARD/PRIMARY/Xdnd 双向桥在 [13 XWayland](/concepts/13-xwayland.md)。

scaled_buffer.c 则提供按输出 scale 缓存自绘缓冲的能力，避免菜单等在高分屏反复重绘。

**主题**一句话：theme_manager 加载配置名 "theme"（D-Bus `/com/kylin/Wlcom/Theme`），struct theme 含亮/暗两套配色（DEFAULT/LIGHT=0、DARK=1）、双层 shadow（THEME_MAX_SHADOW_LAYERS=2）、字体、accent、窗口/菜单圆角与 opacity（0-100），更新掩码 11 位（src/theme/config.c、include/theme.h:103-161，F-R3-158、159）；标题栏按钮有 **12 种类型**（最小化/最大化/还原/关闭 × 正常/hover/clicked），图像经 theme_button_buffer_load 获取（F-R3-162）。UKUI token 目录固定 /usr/share/config/theme/token，图标走 ~/.icons、/usr/share/icons 等搜索路径并用 hash_table 缓存（普通表上限 2000、fallback 主题 200），fallback 主题名 "hicolor"（F-R3-160、161）。

## 与本层协作的 util 基础设施

src/util/（24 个 .c，24 个公开头）被上面各子系统共用（F-R3-163~173）：

| 设施 | 一句话 |
|---|---|
| spsc_chain | 链式无锁 SPSC 队列，libinput 输入队列与命令链的底层（F-R3-163） |
| queue | 线程池作业队列，keymap 异步预热即用它（F-R3-164） |
| event/time | 自有事件掩码与时间换算（usec_to_msec 等）（F-R3-171） |
| anim | FUNCTION/BEZIER/HERMITE 三缓动、6 个预设曲线函数（F-R3-168） |
| spawn/dialog | fork+"/bin/sh -c" 执行命令；经 socket fd 收发 JSON 对话框（F-R3-166、167） |
| dbus | 基于 sd-bus 同时开 system/user 总线，封装 call/match/注册对象（F-R3-165） |
| hash_table | pointer/string/int 三类键、容量上限，主题图标缓存使用（F-R3-169） |
| string/file | split/create 等字符串工具（绑定解析大量使用）、XDG 目录与配置解析（F-R3-173） |
| matrix/vec2 | 3x3 矩阵几何、framebuffer/ndc/输出逆变换与 vec2 辅助（F-R3-170） |
| quirks | 11 位显卡 quirk，按 vendor/backend 两路径查询（F-R3-172） |

另有 client 安全信息（pid/uid/gid/comm）、identifier（uuid/md5/base64）、limit（nofile/cloexec）、nls、color、drm_format、wayland 辅助等工具。

## 静态阅读提示

- 看一个窗口「为什么出现在那个位置」的顺序：view_map（默认使能/输出/焦点）→ 当前 view_mode 的几何钩子 → workspace 三棵 layer 子树 → saved geometry（maximized/tiled/output 三套，恢复时按来源各取各的）。
- view 层只改场景树状态，不直接提交输出；几何变化最终体现为 [06 篇](/concepts/06-scene-graph.md)的节点位置/使能损伤，由 [07 篇](/concepts/07-output-management.md)的帧调度统一上屏。
- 本篇全部结论为静态源码阅读，贴靠动画跟手阈值（如工作区切换 0.35）的实际手感未做运行时验证。

## 相关概念

- 前导：[08 输入系统](/concepts/08-input.md) — 绑定/手势如何调用 window_action 与 workspace 功能
- 后继：[10 特效框架](/concepts/10-effects-framework.md) — map/minimize 等动作触发的窗口动效
- [06 场景图与 surface](/concepts/06-scene-graph.md) — view 持有的 scene_tree 与角色
- [12 协议全景](/concepts/12-protocols.md) — kywc/kde/ukui/wlr 各 shell 协议 XML
- [13 XWayland](/concepts/13-xwayland.md) — xwl_surface 如何适配成同一个 view
- 源码锚点：[view.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/view/view.c#L621-L710)、[workspace.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/view/workspace.c#L541-L594)
- 信源：[R3 输入/视图事实清单](/references/facts-input-view.md)、[R2 图形事实清单](/references/facts-graphics.md)
