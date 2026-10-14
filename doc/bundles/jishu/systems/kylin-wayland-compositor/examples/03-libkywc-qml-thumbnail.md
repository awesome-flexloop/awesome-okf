---
type: Example
title: "libkywc + QML 缩略图客户端走读：67 个稳定 API 与 examples/gui"
description: "先速览 libkywc 的 67 个导出 API 与 7 项 provider 静态表，再逐文件走读 examples/gui 的两个 Qt 入口、Context 桥、ThumbnailItem/ThumInfo 与 QML 数据边界"
tags: [kylin-wlcom, libkywc, qt5, qml, thumbnail, egldmabuf, walkthrough]
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
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 固定快照 4df6562
---

> **本篇在教程中的位置**：本篇是实战篇第 3 篇，处理"带稳定 ABI 的客户端库 + Qt/QML 界面"这一层。前置概念请先读 [15 libkywc 与客户端生态](/concepts/15-libkywc-clients.md)（provider 绑定与快照模型）；[02 篇](./02-wlu-utilities-walkthrough.md) 里的顶层 thumbnail.c 是同一能力的 C 语言最小版，可对照阅读。所有行号锚定固定提交 `4df6562`。

## libkywc 是什么：一个只装一个头文件的共享库

[libkywc/meson.build](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/libkywc/meson.build):48-57 把 12 个 `.c` 编成 `shared_library('kywc', ...)`，soname 随项目版本 1.3.0，`install: true`，但只安装一个公共头 `libkywc.h`（:65）并生成 `kywc.pc`（:67-72，描述 "Kylin wayland compositor client library"）。它只依赖 wayland-client 与 libm（:54），内链 5 套 kywc 自研协议的 client 生成码（:18-24）。

导出面由版本脚本 [libkywc/kywc.syms](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/libkywc/kywc.syms) 决定，全文就是通配规则 `global: kywc_*; local: *;`。脚本核对非 static 的 `kywc_*` 定义共 **67 个**，与 libkywc.h 的声明一一对应（F-R5-007/087）。另有一个 `build_by_default: false` 的静态库 `kywc_buffer`（meson.build:33-42），提供 PNG 落盘/像素读取等 9 个 `kywc_buffer_*` 函数，**不进** libkywc.so，只被 portal 与 examples 的 thumbnail/pipewire 静态链入（F-R5-066/088）。

## 67 个 API 分组速览（行号均在 libkywc/libkywc.h）

| 组 | 数量 | 声明位置 | 代表 API |
|---|---|---|---|
| context | 9 | :44-70 | `kywc_context_create`（:44）、`create_by_display`（:49）、`get_fd`（:61）、`process`（:63）、`dispatch`（:68）、`destroy`（:70） |
| workspace | 11 | :93-118 | `set_interface`、`context_for_each_workspace`、`find_workspace`、`create/remove/set_position/set_name/activate` |
| output | 6 | :174-187 | `set_interface`、`for_each_output`、`find_output`、user_data 对 |
| toplevel | 21 | :243-287 | `has_children`（:255）、max/min/fullscreen、`activate/close`、enter/leave/move_to_workspace、`move_to_output`、`set_position/set_size` |
| thumbnail | 9 | :355-387 | `create`（:355）、`create_from_output/toplevel/workspace`、`release(wants_buffer)`（:382）、`destroy`（:387） |
| cursor | 5 | :402-414 | `create`、`create_from_thumbnail`、user_data 对、`destroy` |
| stream | 6 | :441-455 | `create_from_output`、`create_from_toplevel`（带 cursor_mode）、user_data 对、`destroy` |

上下文能力是 7 个位（libkywc.h:21-30）：OUTPUT/TOPLEVEL/WORKSPACE/THUMBNAIL/THUMBNAIL_EXT（多平面）/CURSOR/STREAM。能力到 Wayland 全局名的映射是 [libkywc/provider.h](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/libkywc/provider.h):20-32 的**编译期静态表** 7 项：workspace/output/toplevel/stream 各指向同名 `*_manager_v1`，而 THUMBNAIL、THUMBNAIL_EXT、CURSOR 三项共用 `kywc_capture_manager_v1`（:28-30）。各 provider bind 版本普遍钳到 1，只有 capture 在扩展能力下允许 bind v2（F-R5-072）。

## context 内部：pending provider 链表与双 roundtrip

创建流程在 [libkywc/libkywc.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/libkywc/libkywc.c)：`kywc_context_init_providers`（:36-50）按 capabilities 位把对应 provider 挂进 `pending_providers`；registry 事件回调（:12-24）遍历 pending 链调 `provider->bind`，成功就移到 `providers` 链——绑定是事件驱动的，调用方不写一行 registry 代码。`kywc_context_create_by_display`（:52-84）先回调 `impl->create`（:69-71），再 init providers（:74），然后两次 roundtrip（:79 等 listener 注册完成、:81 等初始事件收齐）。两个易忽略的细节：THUMBNAIL_EXT 置位时会清掉普通 THUMBNAIL 位（:55-57）；`kywc_context_create`（:86-101）只是 `wl_display_connect(name)` 后转调 by_display，并置 own_display 负责收尾断连（失败时 fprintf "connect to wayland compositor failed"，:91）。

## 快照模型：C 结构体 + state_mask + interface 回调

libkywc 不暴露 wayland 对象，暴露的是三组**只读快照结构**：`_kywc_workspace`（uuid/name/position/activated，libkywc.h:75-80）、`_kywc_output`（:136-155，含 modes 链表、几何、enabled/power/primary、brightness/color_temp）、`_kywc_toplevel`（:199-221，含 parent、primary_output、`workspaces[MAX_WORKSPACES]`（:197 宏=15）、几何与四个状态 bool、pid）。每组配一个 state_mask 枚举（workspace 3 位 :82-86、output 9 位 :157-167、toplevel 12 位 :223-236）和一个两槽 interface（`state(obj, mask)` + `destroy`），状态推送只给掩码，字段读取直接解引用结构体。缩略图缓冲 `kywc_thumbnail_buffer`（:316-330）携带 fd/fourcc/宽高/offset/stride/modifier/flags 与最多 4 平面数组，注释明确 **fd 在缓冲回调返回后由 libkywc 关闭**（:317），消费者要长期持有必须自己 dup 或导入。

## examples/gui 的真实结构与 6 个 Qt 目标

examples/gui 是 6 个独立可执行目标的集合，不是一个程序的 6 个模块。[examples/gui/meson.build](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/examples/gui/meson.build) 开头先探测 C++ 与 Qt5（Core/Gui/Widgets/Qml/Quick/QuickWidgets + Gui 私有头，:1-22），任一缺失整个 `subdir_done()` 跳过。

| 目标 | 行 | 安装 | 作用 |
|---|---|---|---|
| `kywc-gui` | :38-48 | 是 | QMainWindow 三 QTableWidget 的工作台 |
| `children` | :55-61 | 否 | 纯 Qt 父子窗口演示（不链 libkywc） |
| `thumbnail` | :68-78 | 是 | QML + QQuickView 缩略图查看器 |
| `ukui-blur` | :85-94 | 否 | ukui-blur-v1 私有协议客户端 |
| `security` | :101-110 | 否 | kywc-security-v1 协议客户端 |
| `ukui-background` | :123-134 | 否 | ukui-background-v1 客户端，门控 `have_ukui_background` |

## 两个入口：main.cpp 与 ThumMain.cpp

`kywc-gui` 的入口极简（examples/gui/main.cpp:8-15）：`QApplication` + 栈上 `MainWindow w; w.show(); return app.exec();`，全部界面在 `MainWindow`（widget.h:18-89）里——三个 `QTableWidget`（widget.h:73-75）分别列 workspace/output/toplevel，槽函数几乎与 libkywc toplevel 组 21 个 API 一一对应（widget.h:47-68）。

MainWindow 的实现集中在 examples/gui/ui.cpp：构造函数（ui.cpp:26）随后在 :42 建 `new Context(display, Output | Toplevel | ...)`（三个能力组合位），三个 init 函数分别把 Context 的 `workespaceAdded/outputAdded/toplevelAdded` 信号连到表格追加槽（:109、:175、:230），每行对象再连自身的 `stateUpdated/deleted`（如 :411-412、:598-599、:626-627）。右键菜单与缩略图入口对应 `toplevel_menu`、`show_toplevel_thumbnail/show_output_thumbnail/show_workspace_thumbnail`（widget.h:64-68）。也就是说 kywc-gui 本身不用 QML，它是"Context QObject 桥 + QTableWidget"这条纯 Widgets 路线的完整样例。

QML 缩略图程序的入口是另一个文件 `ThumMain.cpp`（注意不是 main.cpp，F-R5-131）：

```cpp
// examples/gui/ThumMain.cpp:21
qmlRegisterType<ThumbnailItem>("MyComponents", 1, 0, "ThumbnailItem");
```

:24-51 解析三种命令行形态：`output <uuid>`、`toplevel <uuid> <remove-decorations>`、`workspace <uuid> <output-id>`，写进一个 `ThumInfo thum;`。:57-63 建 `QQuickView`，通过 `rootContext()->setContextProperty("dataInfo", &thum)`（:60）把数据对象注入 QML 上下文，再 `QWidget::createWindowContainer` 把 QQuickView 嵌进普通 QWidget（:63-64）。

## main.qml 与 qml.qrc：整个 QML 树只有 16 行

[examples/gui/main.qml](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/examples/gui/main.qml):9-16 的界面树就是一个填满父项的 `ThumbnailItem`，`thumInfo: dataInfo` 绑定到 C++ 注入的上下文属性；qml.qrc（:1-7）只内嵌这一个 qml 文件。复杂逻辑全部在 C++ 侧，QML 只承担场景图承载。

## Context：libkywc 句柄与 Qt 事件循环的桥

`context.h` 在一个头里定义了 5 个 QObject：`Workspace`（:19-51）、`Output`（:55-116）、`Toplevel`（:121-190）、`Thumbnail`（:195-238）、`Context`（:242-282），每个都带 `stateUpdated/deleted` 信号与和 libkywc state_mask 数值完全对应的 `Mask` 枚举（如 Output::Mask 9 位对照 libkywc.h:157-167）。

桥接实现在 examples/gui/context.cpp：

- `Private::setup`（:75-82）二选一：已有 `wl_display*` 时 `kywc_context_create_by_display`，否则 `kywc_context_create(NULL, caps, ...)`；
- 静态回调表 `context_impl`（:71-73）把 newOutput/newToplevel/newWorkspace 转成 `new` 出来的 QObject 并 emit Qt 信号（:47-69）；
- `start()`（:106-125）用 `QSocketNotifier(kywc_context_get_fd(ctx), Read)`（:115）把 wayland fd 挂进 Qt 事件循环，槽 `onContextReady`（:127-134）里调非阻塞的 `kywc_context_process`（:129）；
- 查询三件套 `findWorkspace/findOutput/findToplevel`（:152-174）走 libkywc 的 `context_find_*` + 对象 user_data 反查；
- 注意 context.cpp:96-97：Qt 侧的 `Context::Capability::Thumbnail` 一个枚举位实际映射成 `KYWC_CONTEXT_CAPABILITY_THUMBNAIL_EXT`，即 gui 默认就要多平面捕获。

## ThumbnailItem 与 ThumInfo：QML 可见的数据与绘制边界

`ThumInfo`（ThumInfo.h:12-40）是无逻辑的属性袋：type/sourceUuid/outputUuid/removeDecorations 四个字段，setter 里 emit `thumInfoChanged()`（ThumInfo.cpp:12-57）。

`ThumbnailItem`（继承 `QQuickItem`）通过一个 `Q_PROPERTY(ThumInfo *thumInfo ...)`（ThumbnailItem.h:17）暴露给 QML，绘制走场景图渲染线程回调 `updatePaintNode`（ThumbnailItem.cpp:43 起）。它的私有实现里有两种像素来源（ThumbnailItem.cpp:21-37）：dmabuf 走 `eglCreateImageKHR(EGL_LINUX_DMA_BUF_EXT, ...)`（:224-227），memfd 走 `mmap(PROT_READ, MAP_PRIVATE, fd, 0)`（:240）；首帧纹理未就绪时用一张蓝色占位 QImage（:49-51）。它还在 :155 自建 `new Context(display, Context::Capability::Thumbnail)`、:157 `new Thumbnail`，并在 :273 调 `context->thumbnail_init(...)` 发起捕获；:115-117 连接 `QQuickWindow::afterRendering` 做帧同步。EGL 原生资源通过 `QGuiApplication::platformNativeInterface()` 与 "egldisplay" 集成（依赖 Gui private_headers，meson.build:13-18，F-R5-135）。

## thumbnail.cpp：Thumbnail QObject 如何承载 kywc thumbnail

examples/gui/thumbnail.cpp 是 libkywc thumbnail 组 API 的 C++ 包装层：

- 回调实现 `thumbnail_impl`（:102-106）含 `buffer / destroy / buffer_update` 三槽，对应 libkywc.h:332-349；
- `Private::setup`（:108 起）按类型分流到三个便捷构造：`kywc_thumbnail_create_from_output`（:118）、`kywc_thumbnail_create_from_toplevel(ctx, str, without_decoration, ...)`（:125，第三个参数对应 libkywc.h:363-366 的去装饰开关）、`kywc_thumbnail_create_from_workspace(ctx, str, output, ...)`（:132）；
- `release(bool wants_buffer)`（:152 附近，声明 context.h:216）包 `kywc_thumbnail_release`，`destroy()`（:159）包 `kywc_thumbnail_destroy`；
- 缓冲元数据（fd/format/stride/modifier/n_planes）经 getter 暴露给 ThumbnailItem（context.h:219-229，字段定义对照 libkywc.h:316-330）。

## toplevel.cpp / workspace.cpp / output.cpp：逐组 API 的薄封装

- **toplevel.cpp**：`Private::setup` 在 :163-164 调 `kywc_toplevel_set_interface` + `set_user_data`（把 QObject 挂回 C 对象）；:140 经 `toplevel->parent` 的 user_data 还原父窗口 QPointer（对应 `_kywc_toplevel.parent`，libkywc.h:206）。动作方法是一组一一转发：`has_children`（:253）、maximized（:260/265）、minimized（:270/275）、fullscreen（:282/287）、`activate`（:292）、`close`（:297）、`set_position/set_size`（:302/307）、enter/leave/move_to_workspace（:314/321/328）、`move_to_output`（:335）。
- **workspace.cpp**：:69-70 同样挂 interface 与 user_data；动作只有 `activate`（:104）、`set_name`（:111）、`set_position`（:116）、`remove`（:121）四个，与 workspace 组 API 面一致。
- **output.cpp**：只有 :157-158 的订阅绑定，没有任何控制类调用——libkywc 的 output 组本来就只暴露读接口（6 个，libkywc.h:174-187）；要改输出配置得用 02 篇的 output_doctor 走 kde 协议。

## children.cpp / security.cpp / ukui_blur.cpp / ukui_background.cpp

- **children.cpp**（目标 children，只依赖 qt5，meson.build:55-61）：纯 Qt 程序，`SubWindow : public QMainWindow`（:15 起）递归生成"第 N 层第 M 号"子窗口，用于肉眼验证 `kywc_toplevel_has_children`/parent 语义——它自身不调 libkywc，是 monitor/kywc-gui 的配合观察对象。
- **security.cpp**（目标 security，:101-110）：链接的协议键是 `kywc-security-manager-v1`，include 的生成头却是 `kywc-security-v1-client-protocol.h`（security.cpp:15）；通过 `nativeResourceForScreen("output", screen)`（:28-30）与 `nativeResourceForWindow("surface", window)`（:55-57）取原生 wl 资源，再 `kywc_security_manager_v1_get_security_for_output`（:36）/`get_security_for_surface`（:63），复选框切换 `kywc_security_v1_enable/disable`（:41、:68）。
- **ukui_blur.cpp**（:85-94）：链 ukui-blur-v1 生成码，用 QPlatformNativeInterface 取 surface 后操作模糊协议，界面是自绘 SliderWidget（:24 起），对应服务端 src/view/ukui_blur.c（F-R5-033）。
- **ukui_background.cpp**（:123-134，门控 have_ukui_background）：同时链 ukui-background-v1 与 linux-dmabuf-v1 两组协议码，源码侧可见 gbm/drm_fourcc/mmap（:34-39）与文件选择（QFileDialog，:10），演示把本地图片做成 dmabuf 背景；gbm 缺失时 meson 用空 `declare_dependency()` 占位（:113-116）。

## C++ 与 QML 的数据边界

综合上面文件，边界划得很干净：

1. 所有 `kywc_*` 调用只出现在 `.cpp`（context.cpp 与四个包装文件），QML 侧看不到 libkywc；
2. C 快照结构（`_kywc_output`/`_kywc_toplevel` 等，libkywc.h:136-221）在包装类里转成 QString/QSize/QPoint/QStringList 与 Qt 信号；
3. QML 只触达两个注册符号：QML 类型 `ThumbnailItem` 与上下文属性 `dataInfo`（ThumInfo*）；
4. wayland 事件经 fd→QSocketNotifier→Qt 信号槽，绘制经 QSGNode，两套事件循环合一，没有额外轮询线程。

这条边界在构建层也有对应：四个带 Q_OBJECT 的头 `context.h / widget.h / ThumbnailItem.h / ThumInfo.h` 由 `qt5.preprocess(moc_headers: ...)` 统一跑 moc（gui/meson.build:33-36），而 children/security/ukui_blur/ukui_background 四个独立目标用的是 `moc_sources`（:50-53、:96-99 等）——QObject 声明在头还是在 .cpp，决定了两种 moc 喂法，照着各自目标的写法抄即可。

## 构建与运行前置（本次未执行）

以下命令**本次未执行**，前置条件以 meson 文件为准：

- openKylin + wlroots 0.17 ok 系环境；Qt5 开发包需覆盖 Core/Gui/Widgets/Qml/Quick/QuickWidgets 及 Gui 私有头（qtbase5-private-dev、qtdeclarative5-dev 等，见 debian/control，F-R1-016），外加 egl/glesv2/libdrm；
- `-Dexamples=true -Dlibkywc=true`（默认均为 true）；缺 C++ 编译器或 Qt5 时整个 gui 子目录静默跳过，不影响其余示例；
- ukui-background 目标还需 `-Dukui_background=true`（默认 true）与系统 gbm；
- 安装后仅 `kywc-gui` 与 gui 版 `thumbnail` 进 `/usr/bin`（debian/kylin-wayland-compositor-examples.install 仅两行）。

> **同名目标提示（D-R1-10）**：examples 顶层还有一个 C 程序也叫 `thumbnail`（examples/meson.build:44-49，foreach 产出、**不安装**），与 gui 的 Qt 目标 `thumbnail`（gui/meson.build:68-78，**install: true**）同名。二者分属不同 meson 子目录、构建产物在不同构建子目录，但最终只有 QML 版被安装为 `/usr/bin/thumbnail`；排障时不要拿错二进制。

## 相关概念

- [15 libkywc 与客户端生态](/concepts/15-libkywc-clients.md)：67 API、provider 静态表与快照/回调模型
- [12 协议全景](/concepts/12-protocols.md)：kywc-capture/output/toplevel/workspace/stream 五协议
- [02 wlu 示例工具库与三个协议客户端](./02-wlu-utilities-walkthrough.md)：同一缩略图能力的 C + wlu 版本
- [01 跟写一个特效插件](./01-effect-plugin-walkthrough.md)
- [R5 协议/libkywc/portal/示例事实清单](/references/facts-protocols-clients.md)
