---
type: Concept
title: "Wayland 与 wlroots 基础：合成器模型、unstable API 与协议代码生成"
description: "建立 Wayland 客户端-合成器-内核心智模型，理解协议 XML 与 wayland-scanner 三件套、global 注册两类方式、wlroots 0.17 unstable API 钉版与协议版本协商"
tags: [wayland, wlroots, wayland-protocols, wayland-scanner, architecture]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
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

> **本篇在数据流中的位置**：本篇横切主线——「协议」是客户端与合成器之间唯一的跨进程接触面，后端、渲染、场景、输入、视图各篇都会反复出现 wlroots 类型与协议对象。前置阅读 [01 构建运行](/concepts/01-build-run.md)；本篇只讲通用机制，kywc 私有协议族（kywc/ukui/kde/wlr 全表）留给 [12 协议全景](/concepts/12-protocols.md)。

## Wayland 三方模型：客户端、合成器、内核

Wayland 把 X11 时代「服务器既管窗口策略又管绘制」的单体拆成两端，通过一条 Unix domain socket 上的二进制协议通信：

- **客户端（client）**：应用程序链接 libwayland-client，连接 `WAYLAND_DISPLAY` 指定的 socket，提交自己的表面内容（buffer）并接收输入事件；
- **合成器（compositor）**：kywc 链接 libwayland-server，是协议的服务端。它持有 DRM/KMS 输出与 libinput 输入，决定每个表面的位置、层级与是否可见，把各表面合成为一帧后送到硬件；
- **内核**：DRM/KMS 提供显示与 buffer 共享（dmabuf），evdev/libinput 提供输入设备。合成器经 logind 会话取得设备 fd（见 [04 后端层](/concepts/04-backends.md)）。

与 X11 不同，Wayland 客户端**不能**自行决定屏幕位置或直接向输出画线：一切呈现都以「提交 buffer 给一个表面（surface）」为单位，是否上屏、上屏到哪里由合成器裁决。这个模型决定了后续所有代码的形态——场景树是合成器内部的裁决结果（[06](/concepts/06-scene-graph.md)），协议 global 是裁决能力对外的暴露面（[12](/concepts/12-protocols.md)）。

## 核心对象：compositor、surface、seat、output

Wayland core 协议定义了一组最基础的 global。docs/PROTOCOLS.md 的 core 表登记了本项目支持的版本（F-R5-060），这些 core global 由 wlroots 在 `wl_display` 上创建，src/ 内没有对应 XML：

| core global | 角色 | 项目支持版本（PROTOCOLS.md 口径） |
|---|---|---|
| `wl_compositor` | 表面工厂：创建 wl_surface/wl_region | 6 |
| `wl_shm` | 共享内存 buffer 池 | 1 |
| `wl_data_device_manager` | 剪贴板/拖拽 | 3 |
| `wl_seat` | 输入席位：聚合键盘/指针/触摸 | 6（文档「说明」列写 9） |
| `wl_output` | 一个物理输出的几何/模式通告 | 4 |
| `wl_subcompositor` | 子表面（subsurface）树 | 1 |
| `wl_shell` | 旧版外壳接口 | 标 deprecated |

kywc 侧的接合点在 wlroots 初始化段：`wlr_compositor_create(server->display, 6, server->renderer)` 与 `wlr_subcompositor_create(server->display)`（F-R1-054，src/server.c:269-270，`wlr_compositor_create` 为 wlroots 符号），版本参数 6 与文档矩阵一致。`wl_output`/`wl_seat` 的具体实例由输出/输入管理器在设备就绪时创建，分别见 [07](/concepts/07-output-management.md) 与 [08 输入](/concepts/08-input.md)。

> 说明：PROTOCOLS.md 中 wl_seat 行「支持 6、说明 9」是文档双列口径（F-R5-060），本教程不替上游解释差异；以代码创建时实际 bind 的版本为准。

## 协议从哪来：XML 与 wayland-scanner 三件套

Wayland 协议本身是用 XML 描述的接口契约（interface、request、event、enum、version），C 代码全部生成、不手写编解码。kywc 的 protocols/ 目录有 34 个 XML、共声明 77 个 interface（F-R5-001）。protocols/meson.build 对字典中的每个协议统一跑 wayland-scanner，产出三件文件（F-R5-047，protocols/meson.build:183-211）：

出处 protocols/meson.build:183-206，片段经裁剪：

```meson
foreach name, path : protocols
  code = custom_target(
    name.underscorify() + '_c',
    output: '@BASENAME@-protocol.c',
    command: [wayland_scanner, 'private-code', '@INPUT@', '@OUTPUT@'])
  wlcom_sources += code              // 协议消息编解码，编入主程序

  server_header = custom_target(
    output: '@BASENAME@-protocol.h',
    command: [wayland_scanner, 'server-header', '@INPUT@', '@OUTPUT@'])
  wlcom_sources += server_header     // 服务端类型与 wl_*_interface 描述符

  client_header = custom_target(
    output: '@BASENAME@-client-protocol.h',
    command: [wayland_scanner, 'client-header', '@INPUT@', '@OUTPUT@'],
    build_by_default: false)        // 客户端头，仅 libkywc/tools/examples 需要
endforeach
```

三件产物的分工：

- **private-code**：消息打包/解包的 `.c`，与 server-header 一起加入主程序源 wlcom_sources（F-R1-036）；
- **server-header**：合成器侧使用的 `*-protocol.h`，提供接口描述符（如 `kywc_capture_manager_v1_interface`）与服务端内联函数；
- **client-header**：`*-client-protocol.h`，默认不构建，只有 libkywc/tools/examples 引用时才生成——例如 libkywc 里 include 的 "kywc-capture-v1-client-protocol.h"（F-R5-048）。

34 个 XML 中，32 个协议键在 protocols/meson.build 的无条件字典中，其余按 meson 选项条件追加（F-R1-035、F-R5-002）；还有第 35 个 XML 位于 src/plugin/security/security.xml，走插件自己的构建路径（F-R5-052）。

## 运行时注册：wl_global_create 与 wlr 助手两类

XML 生成代码只解决「编解码」；客户端要在 registry 里看到一个 global，合成器还必须在运行时把它注册到 `wl_display`。kywc 有两类注册方式：

**第一类：自研协议直接 `wl_global_create` + 手写 bind。** 例如 kywc-capture-v1 的注册：

```c
/* src/effect/ky_capture.c:614-615，经裁剪；wl_global_create 为 libwayland-server 符号 */
manager->global = wl_global_create(server->display, &kywc_capture_manager_v1_interface, 2,
                                   manager, ky_capture_manager_bind);
```

版本参数 2 与 XML 中 kywc_capture_manager_v1 的最高版本一致（F-R5-021、F-R5-049）。同类注册点还有 ky_stream.c:213、ky_security.c:369、ky_output.c:659、ky_toplevel.c:812、ky_workspace.c:339 等（F-R5-049）。

**第二类：wlroots 助手函数内部创建 global，合成器不直接调 `wl_global_create`。** 例如 layer shell：

```c
// src/view/wlr_layer_shell.c:564，经裁剪（wlr_layer_shell_v1_create 为 wlroots 符号）
wlr_layer_shell_v1_create(server->display, 4);
```

外层包装函数为 wlr_layer_shell_manager_create（src/view/wlr_layer_shell.c:557，F-R5-041）。wlr 助手在内部完成 global 创建与 bind，版本 4 作为参数传入。同类还有 `wlr_virtual_pointer_manager_v1_create`、`wlr_output_power_manager_v1_create`、`wlr_foreign_toplevel_manager_v1_create`、`wlr_viewporter_create`、`wlr_fractional_scale_manager_v1_create` 等十余个（F-R5-050）。

这个区分有实际意义：读代码时看到 `wl_global_create`，bind 行为（版本、资源实现）就在本文件里；看到 wlr 助手，行为要去对应 wlroots 版本的头文件与实现里查。另外注意「XML 存在 ≠ 编进二进制 ≠ 运行时 global 存在」的三层裁剪（meson 选项 → HAVE_* 宏 → 运行时注册），详见 [12 协议全景](/concepts/12-protocols.md) 与洞察 I-1。

## wlroots 的角色与 WLR_USE_UNSTABLE

kywc 不直接实现 Wayland core、DRM/KMS、libinput 接入这些底层机制，而是全部建立在 wlroots 之上：`wlr_backend`/`wlr_renderer`/`wlr_allocator` 负责后端与缓冲，`wlr_output`/`wlr_seat`/`wlr_keyboard` 等是设备抽象，`wlr_xdg_shell` 等提供外壳协议实现。kywc 自己的代码做的是**策略与组合**：自研场景树、view/workspace 模型、特效、配置与私有协议。

wlroots 的这些头文件位于 unstable API 命名空间，使用前必须定义 `WLR_USE_UNSTABLE`，kywc 在全局加了该项目参数（F-R1-008，meson.build:63）。unstable 意味着小版本之间可以破坏 ABI/API——这正是版本被钉死在区间的原因。

## 为何钉在 >=0.17,<0.18

meson 要求 `wlroots >=0.17.0,<0.18.0`（F-R1-008），Debian 包进一步要求带发行补丁的 `libwlroots-dev >= 0.17.4-ok19`（F-R1-016，洞察 I-2）。0.17 与 0.18 的 API 形态差异不小，kywc 全树按 0.17 形态编写，本教程后续会反复遇到的代表：

- 输出提交使用事务式的 `wlr_output_state` 与输出测试/提交分离（0.17 形态，渲染/输出篇展开）；
- buffer 交换链使用 `wlr_swapchain`（kywc 还有自有容量 4 的 swapchain，见 F-R2-071）；
- DRM page flip 事件使用 `drmEventContext` version 3 与 `page_flip_handler2`，present flags 为 VSYNC|HW_CLOCK|HW_COMPLETION（F-R2-029）。

因此升级 wlroots 0.18 意味着全量适配，本教程不承诺跨版本；复现环境以 openKylin 发行包为唯一受支持基线。

## wayland-protocols 的 stable/staging/unstable 分层

项目依赖 `wayland-protocols >= 1.36`（F-R1-009）。这个包是上游协议 XML 的集合，按稳定性分三层目录：

- **stable**：接口稳定、只加版本号不破坏语义，如 xdg_shell；
- **staging**：正在固化的协议，接口名已去掉 unstable 前缀但仍可能修订，如 xdg-toplevel-icon-v1、xdg-toplevel-tag-v1（F-R5-045、F-R5-046）；
- **unstable**：试验性协议，接口名带 `z` 前缀与版本号，如 zwlr_layer_shell_v1、zwp_text_input_v2，版本演进时允许破坏式变更。

PROTOCOLS.md 按 core/stable/staging/unstable/wlr/kde/weston/external/ukui/kywc 十个分节登记（F-R5-008）。kywc 同时自带了大量 vendored XML（kde 族来自 plasma-wayland-protocols，ukui/kywc 族为 openKylin/自研），所以「支持某协议」在本项目有 XML 来源（上游包或 protocols/ 目录）与注册点双重含义，完整对账是 [12 协议全景](/concepts/12-protocols.md) 的任务。

## 版本协商：bind 时取最小值

一个 global 发布时带服务端最高版本（`wl_global_create` 的 version 参数），客户端 `wl_registry_bind` 时传入自己实现的版本，协商结果是两者的较小值，之后该对象生命周期内不能改版本。因此：

- 服务端在 bind 回调里必须按客户端 bind 的版本决定能发哪些 event；
- 客户端必须容忍 global 缺失或版本低于预期。

kywc 自家客户端库 libkywc 给出了明确的防御写法：各 provider bind 时把版本钳制为 1，只有 capture provider 在多平面能力（THUMBNAIL_EXT）下才允许更高版本（F-R5-072）：

```c
// libkywc/kywc_output.c:258-262 等四处同构，片段经裁剪
uint32_t version_to_bind = version <= 1 ? version : 1;
// capture: (version > 1 && extend) ? version : 1
```

这与服务端 `wl_global_create(..., 2, ...)`（F-R5-021）共同构成一对具体的协商实例。写任何新客户端前，建议按「meson 默认值 → HAVE 宏 → 运行时 bind」三态检查，这也是洞察 I-1 的行动建议。

## 相关概念

- 前导：[01 构建、运行与打包](/concepts/01-build-run.md)
- 后继：[03 启动序列与 server 总体架构](/concepts/03-startup-architecture.md) — 看 wlroots backend/renderer/compositor 在启动链中如何被创建
- [04 后端层](/concepts/04-backends.md) — `wlr_backend` 的 kywc 自动选择与 multi backend 组装
- [12 协议全景](/concepts/12-protocols.md) — 34 个 XML 全表、注册点对账与 PROTOCOLS.md 差异
- 信源：[R5 协议事实清单](/references/facts-protocols-clients.md)、[R1 构建事实清单](/references/facts-build-startup.md)、[源码信源登记](/references/source-code-map.md)
