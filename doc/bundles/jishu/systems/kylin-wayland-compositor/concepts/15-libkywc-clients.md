---
type: Concept
title: "libkywc 客户端库、示例生态与自带工具：67 个稳定 API 的进程外面"
description: "盘点 libkywc 的 provider 机制、67 个导出 API 与快照模型，导航 9 个示例/wlu/QML GUI，并介绍 wlcctrl、wldialog、kylin-magnifier 与编译期 i18n"
tags: [libkywc, client, examples, wlcctrl, i18n, api]
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
    title: R4 特效/插件/安全簇事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：如果说 [11 插件](/concepts/11-plugin-system.md)是「进程内、ABI 1.0、偏 security 的薄面」，libkywc 就是 I-4 三层 ABI 中唯一面向外部进程、有版本承诺的稳定面——截图、录屏、窗口/工作区/输出管理等合成器能力，经它到达普通客户端、portal（[14](/concepts/14-security-portal.md)）与自带工具。

## 定位：把不稳定的 wlroots 面关在进程内

libkywc 构建为共享库 `libkywc.so`（soname 随项目版本 1.3.0），**只安装一个公共头 libkywc.h**，并生成 pkg-config 文件 kywc.pc（描述 "Kylin wayland compositor client library"）；运行时依赖只有 wayland-client 与 libm（F-R5-063，libkywc/meson.build:48-65）。

设计意图体现在隔离上：合成器主程序全局 `-DWLR_USE_UNSTABLE`、钉死 wlroots 0.17（I-2），40 个特效全部静态编在主二进制内（F-R4-005），但 libkywc 不链接 wlroots，对外只暴露以快照为单位的 `kywc_*` 数据模型——内部 wlroots 结构升级不需要重编客户端。它与主程序的关系是「同一个自研协议的两端」：主程序手写 `wl_global_create` 注册 kywc 私有协议 global（[12](/concepts/12-protocols.md)），libkywc 是这些协议的 client 端封装。

## provider 机制：7 能力位、静态表、双 roundtrip

libkywc/ 共 17 个 C/H：12 个 `.c` 入共享库 + buffer.c 单独成静态库 + 4 个头（F-R5-003、F-R5-065）。核心抽象是 **context + provider**：

- 能力位枚举 `kywc_context_capability` 共 7 位（F-R5-067，libkywc.h:21-30）：OUTPUT、TOPLEVEL、WORKSPACE、THUMBNAIL、THUMBNAIL_EXT（多平面）、CURSOR、STREAM；
- [provider.h](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/libkywc/provider.h) 内是一张 **7 项静态表**，把能力位映射到 Wayland interface 名与 init 函数（F-R5-068，provider.h:20-32）：WORKSPACE/OUTPUT/TOPLEVEL/STREAM 各对应一个 manager；THUMBNAIL、THUMBNAIL_EXT、CURSOR **三项共用** `kywc_capture_manager_v1` 与 `_kywc_capture_init`；
- context 创建时 `kywc_context_init_providers` 按位把 provider 挂入 pending 链（libkywc.c:36-50）；registry 全局事件里逐 pending provider 试 bind，成功移到 providers 链（libkywc.c:12-24）；
- 随后做**两次 `wl_display_roundtrip`**：第一次确保 registry listener 跑完，第二次确保绑定后的初始状态事件收齐（libkywc.c:79-81，F-R5-070）；
- bind 版本统一**钳到 1**：`version_to_bind = version <= 1 ? version : 1`（kywc_output.c:258-262 等四处），唯一例外是 capture provider——THUMBNAIL_EXT 能力下允许 `(version > 1 && extend) ? version : 1` 以使用 v2 多平面帧（kywc_capture.c:229-237，F-R5-072）；
- THUMBNAIL_EXT 置位时会清掉普通 THUMBNAIL 位（libkywc.c:55-57）；provider 按能力单例去重（libkywc_p.h:40，libkywc.c:188-225）。

入口两式：`kywc_context_create(name, caps, impl, data)` 自行 `wl_display_connect`（失败打印 "connect to wayland compositor failed"），`kywc_context_create_by_display` 接入既有 display——后者是 Qt/portal 等已有事件循环场景使用的形态（F-R5-071，libkywc.c:52-101）。

## 67 个导出 API：七组 + 一个静态 buffer 库

脚本对账：libkywc/*.c（排除 buffer.c）非 static `kywc_*` 定义 **67 个**，与 libkywc.h 的 67 条声明一一对应（F-R5-007、F-R5-087）。分组（行号均指 libkywc/libkywc.h）：

| 组 | 数量 | 代表 API（行号） |
|---|---|---|
| context | 9 | kywc_context_create(:44)、create_by_display(:49)、get_fd(:61)、process(:63)、dispatch(:68)、destroy(:70)（F-R5-080） |
| workspace | 11 | for_each_workspace(:99)、find_workspace(:102)、create(:106)、remove(:108)、set_position(:110)、activate(:114)（F-R5-081） |
| output | 6 | for_each_output(:178)、find_output(:183)；能力枚举 POWER/BRIGHTNESS/COLOR_TEMP（:123-127）（F-R5-082） |
| toplevel | 21 | for_each_toplevel(:248)、has_children(:255)、set/unset_maximized(:257/259)、activate(:269)、close(:271)、enter/leave_workspace(:273/275)、move_to_workspace(:277)、set_position/size(:281/283)（F-R5-083） |
| thumbnail | 9 | create(:355)、create_from_output(:359)、create_from_toplevel(:363，带 without_decoration)、create_from_workspace(:368，需 output_uuid)、release(:382，bool wants_buffer)、destroy(:387)（F-R5-084） |
| cursor | 5 | kywc_cursor_create(:402，参数含 struct wl_seat*)、create_from_thumbnail(:405)、destroy(:414)（F-R5-085） |
| stream | 6 | create_from_output(:441)、create_from_toplevel(:445)（source_uuid + cursor_mode + impl + data）、destroy(:455)（F-R5-086） |

合计 9+11+6+21+9+5+6 = 67。数据模型以**快照结构**对外：`_kywc_workspace`（uuid/name/position/activated）、`_kywc_output`（含 modes 链表、几何、power/brightness/color_temp 等）、`_kywc_toplevel`（含 workspaces[MAX_WORKSPACES=15]、pid、icon、四态），配三组 state_mask 位掩码增量更新（F-R5-076、F-R5-077）。

### 快照与多平面：THUMBNAIL_EXT

缩略图缓冲描述 `kywc_thumbnail_buffer` 同时支持 memfd 与 dmabuf（最多 4 plane）：fd、DRM fourcc format、width/height、offset/stride/modifier、flags（IS_DMABUF=1<<0、IS_REUSED=1<<1）、planes[4]（F-R5-078，libkywc.h:304-330）。来源类型枚举 OUTPUT/TOPLEVEL/WORKSPACE（:292-296）。cursor 模型携带 seat 与 thumbnail，回调 position/hotspot/enter/leave/destroy；stream 模型携带 cursor_mode（HIDDEN/EMBEDDED/METADATA，:424-428），ready 回调直接给出 PipeWire node id（F-R5-079、F-R5-074）——这正是 [14 portal](/concepts/14-security-portal.md) 不链 libpipewire 仍能回传 node 的原因。

### kywc_buffer 静态库：9 个像素辅助函数

buffer.c 不进 libkywc.so，而编成 `libkywc_buffer.a`（`build_by_default: false`，依赖 epoxy + libpng），供 portal 与示例静态链入（F-R5-066）。buffer.h 声明 9 个函数（F-R5-088）：kywc_buffer_helper_create/destroy、helper_import_thumbnail、helper_destroy_buffers、write_to_file（PNG 落盘）、get_pixel、read_pixels、buffer_destroy、helper_get_format；import/export dmabuf/memfd 4 个为 static 内部函数。

### 消费的私有协议与符号出口

libkywc 只链 5 个 kywc 协议的 client 生成码：capture/output/toplevel/workspace/stream manager v1（**不含 security**，F-R5-064，libkywc/meson.build:18-29）。帧/光标对象消费在 kywc_capture.c:98-205（release_buffer、capture_output/workspace/toplevel/cursor 请求），stream 的 created(node) 透传在 kywc_stream.c:33-74（F-R5-073、F-R5-074）。

符号出口不是显式清单而是通配版本脚本（[libkywc/kywc.syms](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/libkywc/kywc.syms)，F-R5-087）：

```
{ global: kywc_*; local: *; };
```

仓根还有一份内容**完全相同**的 src/wlcom.syms（F-R5-010），配合主程序 `executable('kylin-wlcom', …, export_dynamic: true, link_args: '-Wl,--version-script,…/wlcom.syms')`（meson.build:311-325，F-R5-009）。两份脚本一个面向外部客户端、一个面向 dlopen 插件，导出命名空间同为 `kywc_*`——这是三层 ABI 共享同一套头文件（include/kywc/，见 [11](/concepts/11-plugin-system.md)）但稳定性承诺不同的符号学注脚。

context 还接受一个 `kywc_context_interface` 回调表（libkywc.h:32-39）：create/destroy/new_output/new_toplevel/new_workspace，初始枚举结束与后续增量变化都经它通知，配合 state_mask 做最小更新；私有头 libkywc_p.h 定义了内部 `_kywc_context`（display/registry/own_display/capabilities/providers/pending_providers 加六个 manager 指针）与各组 ky_* 内部结构（F-R5-075）。事件驱动有两种用法：自己持 fd 用 kywc_context_process/dispatch（如 monitor 的阻塞 dispatch，F-R5-120），或把 kywc_context_get_fd 挂进现成循环（portal 的自研 event_loop、QML 侧的 QSocketNotifier，F-R5-129）。

## 示例生态导航（不重复走读）

examples/ 下 34 个 C/CPP/H：根目录 **9 个独立 `.c` 程序**、lib/ 下 wlu 静态库、gui/ 下 6 个 Qt 目标（F-R5-005）。9 个根程序的依赖形态本身就是选型样本：

| 示例 | 形态 | 门控 |
|---|---|---|
| output-doctor | libwlu + 5 个 kde/xdg 协议生成码 | have_kde_output |
| virtual-desktop | plasma-virtual-desktop 裸协议 | have_kde_virtual_desktop |
| monitor | 仅 libkywc（WORKSPACE|OUTPUT|TOPLEVEL） | 无 |
| ukui-effect-test | ukui-effect-v1 + shm 自建窗口 | have_ukui_effect |
| thumbnail | libkywc(THUMBNAIL_EXT) + kywc_buffer + wlu EGL | 无 |
| kde_keystate | org_kde_kwin_keystate 裸 bind | have_kde_keystate |
| alpha_modifier | libwlu + cairo | have_alpha_modifier |
| pipewire | libkywc STREAM + kywc_buffer + libpipewire | 无 |
| simple_plugin | shared_module，非可执行 | 无 |

三篇走读已分别覆盖，本节只做地图：

- **插件与特效协议侧**：simple_plugin（shared_module、非可执行，导出 simple_plugin_data，注册 6 快捷键 + 7 手势绑定，F-R5-126）、ukui-effect-test、kde_keystate、alpha_modifier —— 见 [示例走读 01](/examples/01-effect-plugin-walkthrough.md)；
- **wlu 工具库与裸协议客户端**：libwlu 静态库（5 源：buffer/display/input/window/wlu，3 协议 xdg-shell/xdg-decoration/linux-dmabuf，F-R5-114~117）支撑 output-doctor（1039+ 行，kde output 管理全家桶，F-R5-118）、virtual-desktop（F-R5-119）、pipewire（消费 stream node，F-R5-125）等 —— 见 [示例走读 02](/examples/02-wlu-utilities-walkthrough.md)；
- **libkywc 与 QML**：monitor（仅依赖 libkywc，打印 output/toplevel/workspace，F-R5-120）、thumbnail（libkywc + kywc_buffer + EGL，F-R5-122）、kywc-gui（QMainWindow 三表 + 全套 toplevel 操作槽，F-R5-128，Context 类以 QSocketNotifier 挂入 Qt 事件循环）、thumbnail QML 查看器（EGLImage/GL 纹理路径，F-R5-131、F-R5-135）——见 [示例走读 03](/examples/03-libkywc-qml-thumbnail.md)。

gui/ 另有 children、ukui-blur、security（kywc-security 协议客户端）、ukui-background 四个不安装目标；缺 C++/Qt5 时整个 gui/ 与 wldialog/magnifier 一样 subdir_done 跳过（F-R5-127、F-R1-161）。示例默认只构建不安装，仅 kywc-gui 与 thumbnail install:true（F-R1-160）。

## 自带工具：tools/ 三子工具

tools/ 由 meson 选项 tools 门控，固定进入 3 个子目录（F-R1-141）：

### wlcctrl：42 个子命令的纯 C 控制 CLI

wlcctrl 11 个 C 源，链接 libkywc + 虚拟输入两协议（virtual-keyboard、wlr-virtual-pointer，F-R1-142）。commands.c 命令表 **42 条**，按命令声明的 caps/needs 惰性初始化运行时（F-R1-143）：列表类 3、窗口操作 18、工作区 4、截图/几何 4（fullscreencapture/setarea/getpixelcolor/getdisplaygeometry）、鼠标 6、键盘 4（keystring/key/keydown/keyup）、exec/sleep。特性包括：短参 `-o/-x/-y/-w/-h/-l/-v`、长选项按命令动态生成、命令按出现顺序执行、任一失败即停（F-R1-144、F-R1-145）。它也是虚拟键盘/指针协议的主要存在理由（[12](/concepts/12-protocols.md)，F-R5-144）——这两个协议的 meson 键挂在 have_tools 下，不装工具就不进代码生成。

### wldialog：portal 与 killer 的对话框后端

wldialog 是 Qt5(C++/QML) 工具，9 个 cpp，协议 xdg-dialog/xdg-foreign-v2/xdg-shell，经 socket fd 收发 JSON（DialogSocket.json 标注 protocol_version "1.0"，control/dialog 互斥、对话框一次性）；缺 C++ 或 Qt5 私有头静默跳过构建（F-R1-147、F-R1-146）。它有两类消费者：portal 的 spawn_dialog（[14](/concepts/14-security-portal.md)）与合成器内 view/killer.c 的关闭确认（F-R1-148）。

### kylin-magnifier：放大镜的 Qt5 前台

zoom 特效（[10](/concepts/10-effects-framework.md)）暴露 org.ukui.Magnifier D-Bus 8 方法，kylin-magnifier 是其 Qt5 Widgets/DBus 前端，两个 D-Bus XML 经 qdbusxml2cpp 生成代码（StartZoom(mode,scale) 等，F-R1-149、F-R1-150）。

另值得一句的构建期生成器：src/config/qtkey_mapper.c 是约 900 行的**宿主端代码生成程序**（main 位于 :894），内嵌完整 Qt::Key 枚举表（273 条有效 XKB↔Qt 映射、29 条注释项），构建时执行并捕获输出为 qtkey_map_table.h，供 KDE 全局快捷键组件做 keysym/Qt key 互转（F-R1-086、F-R1-087）。

## i18n：编译期 .mo 嵌入 .h，两个独立翻译域

本项目不做运行时 /usr/share/locale 查找：每个 .po 经 msgfmt 生成 .mo，再由宿主工具 embed 转成 `<lang>_mo.h` 字节数组，configure_file 注入 `static const struct locale locales[]`（F-R5-012，po/locales.h.in:1-8）。两个域：

- **主域 kylin-wayland-compositor**：po/ 下 27 个 .po，但 LINGUAS 只列 **16** 种（zh_CN/zh_TW/zh_HK/zh_Hant/bo_CN/ug/kk/ky/mn/ms/de_DE/es_ES/fr_FR/th/vi/ar），11 个 .po 存在但不参与嵌入（F-R5-136~138、F-R1-157）；POTFILES.in 仅覆盖 4 个源文件（F-R5-139）；
- **portal 域 xdg-desktop-portal-wlcom**：19 个 .po，LINGUAS 仅 zh_CN 一行，POTFILES 6 个 .c（F-R5-140、F-R5-113）。两域语言码命名还不一致（de_DE vs de 等，D-R5-152）。

分发侧的含义是：新增一种界面语言需要同时交 .po 并把语言码加入对应 LINGUAS，否则文件在树上但不进二进制；POTFILES 覆盖极小（主域 4 文件、portal 6 文件），主合成器大量用户可见字符串当前不在提取清单内（F-R5-139、D-R5-152）。tools/magnifier 另有自己的 Qt translations（26 个 .ts，F-R1-149），三套翻译机制互不通用。

## 开发者选型：何时 link libkywc，何时裸连协议

1. **需要输出/窗口/工作区的查询与控制、缩略图、光标捕获、PipeWire 流** → 直接 link libkywc（pkg-config kywc）：快照模型与状态掩码帮你屏蔽协议增量细节，portal、monitor、kywc-gui 都是这样做的；
2. **目标协议 libkywc 没封装**（xdg-shell 窗口、kde output 管理、alpha-modifier 等）→ 裸连 Wayland 协议，可链 libwlu 拿 display/window/buffer 脚手架——output-doctor 与 [示例走读 02](/examples/02-wlu-utilities-walkthrough.md) 给出了边界结论；
3. **要给合成器进程内部加行为** → 那不是本篇范畴，回到 [11 插件](/concepts/11-plugin-system.md)与 [10 特效](/concepts/10-effects-framework.md)评估三层 ABI；
4. 任何路径都要做 global 缺失防御，理由见 [12 的三态裁剪](/concepts/12-protocols.md)。

## 相关概念

- [12 协议全景：34 个 XML 与编译期裁剪](/concepts/12-protocols.md)
- [14 安全模型与 xdg-desktop-portal-wlcom](/concepts/14-security-portal.md)
- [11 插件系统：ABI 1.0、dlopen 加载器](/concepts/11-plugin-system.md)
- [01 构建与运行](/concepts/01-build-run.md)
- [示例走读 02：wlu 工具集](/examples/02-wlu-utilities-walkthrough.md)
- [示例走读 03：libkywc 与 QML 缩略图](/examples/03-libkywc-qml-thumbnail.md)
