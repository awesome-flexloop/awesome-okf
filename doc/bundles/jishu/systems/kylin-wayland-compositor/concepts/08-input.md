---
type: Concept
title: "输入系统：libinput 独立线程、seat、键盘/IME、指针/触摸/手势与绑定"
description: "读懂 kywc 自起 libinput 线程加 SPSC64 队列的输入边界、seat 能力聚合、xkb/keyboard_group/IME 五注册点、指针命中链、13 个内置手势与两套绑定语法"
tags: [wayland, wlroots, libinput, xkb, ime, touchpad, gestures, keybindings]
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

> **本篇在数据流中的位置**：[04 后端层](/concepts/04-backends.md)结尾交代了 libinput 独立线程的边界，本篇从事件跨进主循环开始，经 seat 聚合、键盘/指针/触摸分发、绑定匹配，最终调用 [09 视图与工作区](/concepts/09-view-workspace.md) 的 window_action/workspace 功能。命中测试发生在 [06 场景图](/concepts/06-scene-graph.md) 的树上；X11 客户端的输入桥接在 [13 XWayland](/concepts/13-xwayland.md)。

## libinput 线程到主循环：SPSC 队列与 eventfd

kywc 不消费 wlr libinput backend 的设备事件，而是自起线程（架构洞察 I-3，这是它与主流 wlroots 合成器最大的差异）。完整边界：

1. **线程侧**：`libinput_thread_func`（src/backend/libinput/backend.c:121-152）在 epoll 上等待 libinput fd，取事件后在 mutex 内调 handle_libinput_event，再 `eventfd_write(notify_fd, 1)` 通知主线程，并用 `atomic_exchange(&notify_pending, true)` 合并高频通知（注释称 KWin pattern）。
2. **入队**：事件不直接发 wlr 信号，而是压入链式扩容的无锁 SPSC 环形队列。单槽容量 **`INPUT_QUEUE_CAPACITY = 64`**（src/backend/libinput/input_queue.h:14-23、147-157），事件内联存储、无逐事件 malloc，满时在 head 挂新节点；生产者注释明写 "libinput thread / main thread"（util/spsc_chain，F-R3-012）。
3. **主线程侧**：`wl_event_loop_add_fd` 注册 notify_fd（backend.c:245-247），回调 `handle_input_batch` 先 eventfd_read 再 `dispatch_input_events`（backend.c:189-197）批量排空；dispatch 把队列事件翻译成 wlr 设备信号（src/backend/libinput/events.c:358-699）。
4. 线程挂起/恢复走第二根 eventfd 加命令链，下发 LIBINPUT_CMD_SUSPEND/RESUME/STOP（backend.c:153-183，F-R3-019）。

> ⚠️ 阅读风险（D-R3-02）：仓内有**两套同名** `enum input_event_type` / `struct input_event`——队列侧在 input_queue.h:25-60（从 1 顺序编号，覆盖 33 种事件），过滤器侧在 include/input/input.h:19-56（100/200/…分段编号）。两者分属不同翻译单元、取值不兼容，读代码时务必先确认文件。

总分发 handle_libinput_event（events.c:231-356，F-R3-014）覆盖设备增删、键盘、指针 4 种、触摸 5 种、手势 8 种、tablet 7 种、switch 与 RAW_TAP/ZONE；旧的 POINTER_AXIS 事件被显式忽略（注释要求用 SCROLL_*）。设备热插拔在分发线程同步处理，按 6 种能力 init 对应 wlr 设备（events.c:59-110）；DEVICE_ADDED 在主线程 dispatch 阶段才发 `backend.events.new_input`（events.c:368-395，F-R3-017）。

排查输入丢失/延迟的第一现场因此是三段定位：**libinput 线程前 / 容量 64 的队列中 / 主线程分发后**（I-3 行动建议）。

## seat：能力聚合与三类 grab

输入总装函数 `input_manager_create`（src/input/input.c:785-871，F-R3-022）创建 EIS、虚拟指针/键盘、pointer_gestures、relative_pointer、shortcuts_inhibit、pointer_constraints、cursor_shape 等全局，最后建默认 seat **"seat0"**（seat_create，input.c:867）。

设备名格式为 "type:vendor:product:name"，EIS/虚拟设备加 "V_" 前缀（input.c:593-665，F-R3-023、024）。seat_create（src/input/seat.c:115-180）同时建 wlr_seat、wlr_cursor 和一个虚拟 keyboard group 容器，默认 cursor_size=24、数字锁开、锁模式 LOCK_MODE_KEY_CUSTOM。

能力聚合规则（seat.c:189-222，F-R3-026）：TOUCH 同时置 TOUCH|POINTER；TABLET_TOOL/POINTER 置 POINTER；KEYBOARD 置 KEYBOARD；SWITCH/TABLET_PAD 不贡献能力；指针能力消失自动隐藏光标。设备分流 seat_add_input：指针/触摸/平板进 cursor（函数名源码拼写为 `curosr_add_input`，seat.c:233），键盘进 keyboard（F-R3-027）。

seat 维护 pointer/keyboard/touch 三类内部 grab，启动新 grab 取消旧 grab（seat.c:295-366，F-R3-028）。键盘焦点中枢 `seat_focus_surface`（seat.c:406-441，F-R3-029）一次联动五件事：输入面板层更新、shortcuts inhibitor 反激活/激活、`wlr_seat_keyboard_notify_enter`、tablet 焦点、IME 焦点与 pointer constraint。

## 键盘：xkb、keyboard_group 与完整事件链

物理键盘的 key/modifiers 信号接 keyboard_handle_key/modifiers（src/input/keyboard.c:396-427）。keycode→keysym 用 xkb 符号 `xkb_state_key_get_syms(state, key + 8, &syms)`（+8 为 evdev 偏移，keyboard.c:166）；按下 keysym 列表去重、上限 MAX_PRESSED_KEY=10。

**VT 切换在 keysym 解析阶段拦截**：XKB_KEY_XF86Switch_VT_1..12 调 input_manager_switch_vt 后返回 false（keyboard.c:173-179，F-R3-035）。keymap 用 `xkb_context_new(XKB_CONTEXT_NO_SECURE_GETENV)` + xkb_keymap_new_from_names 编译并缓存，首个默认 keymap 经 queue_add_job 异步预热（keyboard.c:673-687、input.c:738-808，F-R3-039）。按键重复由合成器自管 wl_event_loop 定时器，仅物理键盘创建（keyboard.c:205-245，F-R3-038）。compose/dead key 尚是 TODO（keyboard.c:80，D-R3-03）。

keyboard_group（src/input/keyboard_group.c）把同 keymap_string、同 rate/delay 的物理键盘归组，虚拟键盘不入组（keyboard.c:481-538，F-R3-043）；组是名为 "keyboard-group" 的自定义 wlr_keyboard_impl，用按键引用计数去重（keyboard_group.c:58-152，F-R3-044）。

**键盘完整事件链（F-R3-174，逐跳行号）**：

```text
libinput 线程 handle_keyboard_key (backend/libinput/keyboard.c:56)
  → queue_input_event (:73)，事件入 SPSC64
主线程 dispatch_input_events → wlr_keyboard_notify_key (events.c:397-406，wlr 符号)
  → keyboard_handle_key (input/keyboard.c:396) → keyboard_feed_key (:413/:269)
     ├ keyboard_get_key_binding (:190) → bindings_get_key_binding (binding.c:510)
     ├ ACTIVE 阶段回调 (binding.c:634)
     └→ function_manager_handle_key_binding (function.c:1336)
         ├ workspace_manager_handle_function (:1358) → switch_to/activate
         └ view_manager_handle_function (:1383) → window_action (view/action.c:250)
```

`keyboard_feed_key` 的消费优先级（keyboard.c:269-348，F-R3-036）：IME 注入键直发 wlr_seat → 绑定匹配 → grab（可 BYPASS）→ bindings_handle_key_binding → IME 处理 → `wlr_seat_keyboard_notify_key`。VT、激活的 inhibitor、命中 binding 等都在 seat 事件里标 consumed（F-R3-037）。

## IME：五个协议注册点

| 协议 | 实现方 | 注册点 |
|---|---|---|
| input-method-unstable-v2 | **wlr 实现** | `wlr_input_method_manager_v2_create`，src/input/text_input.c:843 |
| text-input v3 | kywc 自有（wl_global_create version 1） | text_input.c:844 → text_input_v3.c:280-296 |
| text-input v2 | kywc 自有 version 1 | text_input.c:845 → text_input_v2.c:285-296 |
| text-input v1 | kywc 自有 version 1（请求不带 seat） | text_input.c:847-848 → text_input_v1.c:283-294 |
| virtual-keyboard v1 | **wlr 实现** | `wlr_virtual_keyboard_manager_v1_create`，input.c:823-826 |

（F-R3-047~051。）每个 seat 在 new_seat 时建独立 input_method_relay 挂接 input_method v2 与 text_input v2/v3，v1 由 manager 统一挂接（text_input.c:785-852，F-R3-052）。焦点经 seat_focus_surface→input_method_set_focus 下发，按 wl_client 匹配（F-R3-053）；IME 候选窗作为场景节点接入 hover/click（text_input.c:618-684，F-R3-055）。

## 指针：wlr_cursor 汇聚、场景命中与软件光标 quirk

`cursor_create`（src/input/cursor.c:892-971）创建 wlr_cursor、attach output_layout，挂接 motion/button/axis、swipe/pinch/hold、touch、tablet tool 等共 21 个信号（F-R3-056，`wlr_cursor_*` 均为 wlr 符号）。xcursor 主题取 XCURSOR_THEME/XCURSOR_SIZE，光标名表 **cursor_image 实测 35 项**（"none" 起到 zoom-out，cursor.c:31-38，F-R3-060），经 `wlr_cursor_set_xcursor` 设置。

**指针点击完整事件链（F-R3-175）**：

```text
libinput POINTER_BUTTON 入队 → 主线程发 wlr_pointer.button (events.c:429-437)
wlr_cursor 汇聚 → cursor_handle_button (cursor.c:317) → cursor_feed_button (:328/:183)
  → scene_node_at(&seat->scene->tree.node, lx,ly,&sx,&sy) 命中场景节点 (cursor.c:63-64)
  → inode->impl->click (:272-275)
  → xdg_view_click (view/xdg_shell.c:82) → view_click (:88)
  → stack_mode_view_click (view/stack_mode.c:197)
  → kywc_view_activate + view_set_focus
  → seat_focus_surface (seat.c:406) → wlr_seat 键盘焦点 + IME 焦点
```

运动链并行：cursor_feed_motion 先发 relative_pointer，再应用 constraint，做场景命中与 hover/leave（cursor.c:74-149、288-301，F-R3-058）。双击判定窗口 double_click_time（cursor.c:264-266）；axis 乘 per-device scroll_factor，并有针对同 time_msec 的 "fix zwcada2023 crash" 补 frame 兼容（cursor.c:353-374，F-R3-066）。pointer constraint（locked/confined）自管 active/pending 两槽，LOCKED 吞运动、CONFINED 用 `wlr_region_confine` 裁剪（cursor.c:1179-1430，F-R3-063）。

软件光标不是输入子系统决定的——quirks 表在 util（src/util/quirks.c:28-38），命中 **nouveau、virtio_gpu(Mesa Project)、vmwgfx、linlondp(ARM)** 四款驱动置 QUIRKS_MASK_SOFTWARE_CURSOR；真正执行点是 output 初始化 `wlr_output_lock_software_cursors`（src/output/output.c:661-662）、fbdev 恒锁（src/backend/fbdev/fbdev.c:616）以及截图/zoom 临时加解锁（D-R3-10 跨簇事实，F-R3-064、065）。触摸 down 与 tablet tip 可模拟鼠标（合成 BTN_LEFT，cursor.c:535-642）。

## 触摸、tablet 与 13 个内置手势

- 触摸在 src/input/touch.c：touch_handle_down 找 surface、过 grab、`wlr_seat_touch_notify_down`，多点触发触屏手势（touch.c:542-642、747-916，F-R3-069）；边缘由 touch_calc_edge 计算（F-R3-070）。
- tablet v2 global 由 wlr 创建（`wlr_tablet_v2_create`，tablet.c:396），tool/pad 按设备建 wlr 对象并转发 mode/button/strip/ring（F-R3-072）。
- **手势状态机四阶段** BEFORE/TRIGGER/AFTER/STOP（src/input/gesture.c:14-27）：swipe 触发阈值 touchpad 10、touchscreen 0.15；hold/tap 用定时器（默认 200ms、touchpad tap 1ms、触屏 hold 800ms）；pinch 最小转角 5°、缩放增量 0.1（F-R3-073）。touchpad 三类 wlr 手势在 cursor.c:644-773 转成内部 gesture_state，同时转发 `wlr_pointer_gestures_v1`，合成器未消费才取消给客户端（F-R3-074、075）。

内置手势 **13 条**（src/input/action.c:773-947，F-R3-091）：触屏 1/3/4 指 hold/swipe、touchpad 单指边缘滑动（亮度/进度/音量，follow_threshold=50.0）、3 指 tap/swipe、4 指 tap（如 "touchpad_(4)fingers_tap"→显示 UKUI 侧边栏）。

## 绑定：两套语法、分桶与三级 block

键绑定字符串语法为 `Mod+Key[:no]`（src/input/binding.c:237-291，F-R3-076）：以 "+" 连接，键名经 xkb 符号 `xkb_keysym_from_name`（CASE_INSENSITIVE）解析并转小写，`:no` 后缀关闭重复触发。类型枚举 key_binding_type 实测 **20 个真实类型**（include/kywc/binding.h:82-104：CUSTOM_DEF=0 起至 ZOOM=19，共 20 个可用类型，KEY_BINDING_TYPE_NUM=20 仅为哨兵；CUSTOM_DEF/CUSTOM_CONFIG 均被 function.c 实际使用。V 阶段勘 F-R3-007 的「19」口径），绑定按类型分 20 个 keysyms_binding 桶（`[KEY_BINDING_TYPE_NUM]`，binding.c:67-81，F-R3-077）加位图 mask 加速；匹配要求修饰精确相等、keysym 在按下列表中（binding.c:498-556，F-R3-079）；回调有 ACTIVE/REPEAT/INACTIVE 三阶段（F-R3-080）。

手势字符串语法（binding.c:849-936，F-R3-081）：

```text
<type>:<device>:<fingers>:<direction>[:edge][:stages][:follow_threshold][:follow_directions]
```

type=tap/hold/pinch/swipe，device=touch/touchpad，direction 含 up/down/inward/clockwise 等，edge=top/bottom/left/right，stage=before/trigger/after/stop。合法性规则例如 pinch 至少 2 指且不能带 edge、触屏单指 swipe 必须带边缘（binding.c:938-985，F-R3-082）。block 三级：全键绑定 block_all、按类型 type_nlocks、单绑定 nblocks（binding.c:1228-1320，F-R3-084）。

## action 与 function_id：总分发

配置动作文本为 "dbus"/"command"/"button"/"key" 四类执行体（src/input/action.c:23-41、493-501，F-R3-086）：dbus 走会话/系统总线，command 经 spawn，SEND_BUTTON 合成移动+按下+释放+leave，SEND_KEY 按 modifiers 先按、keys 再按、反序释放（action.c:299-336，F-R3-088）；内置键码表 31 项、鼠标码 5 项（F-R3-089）。配置来自 "InputAction" JSON 与 D-Bus `/com/kylin/Wlcom/InputAction`（F-R3-087）。

功能 ID 枚举 function_id 实测 **64 个有效 ID**（include/input/function.h:11-78，F-R3-006）。两个总分发器：

- 键：`function_manager_handle_key_binding`（function.c:1336-1403）——FUNC_ID_CONFIG→input_action、CUSTOM→global_shortcuts、SWITCH_*→workspace_manager、窗口/桌面类→view_manager、滤镜/缩放→effect_manager、UKUI 菜单/亮度→D-Bus；
- 手势：`function_manager_handle_gesture_binding`（function.c:1405-1526）——额外处理 windows switch（TRIGGER 阶段合成 Alt+Tab 键序列，:1293-1322）、媒体键（D-Bus 调 org.ukui.SettingsDaemon）、侧边栏等。

内置键绑定仅 1 条："Win:no"→ukui_menu_show（action.c:949-973，F-R3-090）。注意「全局快捷键/全局手势」不是 Wayland 协议 global，而是基于 D-Bus 名称占用的会话机制（global_shortcuts.c:1218，D-R3-07）。

## 合成输入、事件过滤器与其余输入全局

seat 还提供一套合成事件注入 API（src/input/seat.c:443-482，F-R3-031）：seat_feed_pointer_button 内部转 cursor_feed_button 并补发 `wlr_seat_pointer_notify_frame`；seat_feed_keyboard_key 在 seat 自有键盘没有物理设备时，遍历 seat->keyboards 选一个非空 group 发出。08 篇前文 action 的 SEND_KEY/SEND_BUTTON 与手势合成的 Alt+Tab 序列都走这套 API。

server start/active 时 seat 会同步键盘并补发锁定键（seat.c:21-51，F-R3-030）：无硬件键盘时先用空 rules 编译一份 keymap set 上去，再补发 KEY_CAPSLOCK/KEY_NUMLOCK/KEY_SCROLLLOCK——这保证无键盘开机（如 kiosk）时虚拟键盘/IME 仍有有效 xkb 状态。

所有输入事件在分发前先过 `input_event_filter`（input.c:1003-1026，F-R3-032）：过滤器先通知 idle_manager_notify_activity（空闲计时），再调用可安装的 event_filter_func_t（由 input_manager_set_event_filter 设置，EIS 输入过滤就挂这里，见 [04 后端层](/concepts/04-backends.md)）。封装的 struct input_event 含 seat/input/type/event，type 取 include/input/input.h:19-56 那套 100 分段编号——即 D-R3-02 提示的第二套同名枚举。

其余输入相关全局（F-R3-104）：org_kde_kwin_idle 与 ext_idle_notifier_v1（src/input/idle.c:361-368）、idle_inhibit 走 wlr 实现（idle_inhibit.c:175）、org_kde_kwin_keystate（kde_keystate.c:317）、ext_transient_seat_manager_v1（transient_seat.c:153）。

## data_device 与 primary_selection（简述）

剪贴板/拖放协议多为 kywc 自有实现：wl_data_device_manager version 3 于 selection_manager_create 时 wl_global_create（src/input/data_device.c:1524，F-R3-098）；data_source 带 allow_read/drop/write/start_drag 安全闸门（F-R3-099）；DnD 在合成器内实现 pointer/keyboard/touch 三套 grab（data_device.c:996-1301，F-R3-100）；primary_selection v1、data_control v1、xdg_toplevel_drag v1 各有自有 global（F-R3-101、102）。Wayland↔X11 的选择双向桥在 [13 XWayland](/concepts/13-xwayland.md)。

## 相关概念

- 前导：[04 后端层](/concepts/04-backends.md) — libinput 线程与 SPSC 队列的后端侧
- 后继：[09 视图、工作区与窗口管理](/concepts/09-view-workspace.md) — window_action 21 动作与 workspace 切换
- [06 场景图](/concepts/06-scene-graph.md) — scene_node_at 命中的树
- [10 特效框架](/concepts/10-effects-framework.md) — 滤镜/缩放等 FUNC_ID 的 effect 侧
- [13 XWayland](/concepts/13-xwayland.md) — 键窃听、选择桥与整屏缩放
- 源码锚点：[backend/libinput/backend.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/backend/libinput/backend.c#L121-L197)、[input/function.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/input/function.c#L1336-L1405)
- 信源：[R3 输入事实清单](/references/facts-input-view.md)、[R2 图形事实清单](/references/facts-graphics.md)
