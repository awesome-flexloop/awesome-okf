---
type: Concept
title: "协议全景：34 个 XML、六族协议与编译期三态裁剪"
description: "盘点 kywc  protocols/ 下 34 个 XML、77 个 interface 的族属与门控，讲清 XML 存在≠编入≠运行时 global，并对账 PROTOCOLS.md 的 12 处双源差异"
tags: [wayland-protocols, protocols, wayland-scanner, meson, compatibility]
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
  - id: kywc-docs
    resource: /references/project-docs.md
    title: kywc 项目文档信源登记
---

> **本篇在数据流中的位置**：协议 global 是合成器对客户端暴露能力的唯一通道——输入（[08](/concepts/08-input.md)）、输出（[07](/concepts/07-output-management.md)）、视图（[09](/concepts/09-view-workspace.md)）、截图录屏（[14](/concepts/14-security-portal.md)）各管理器都在此注册 global；进程外消费方（[15 libkywc](/concepts/15-libkywc-clients.md)）能 bind 什么完全由本篇的三态裁剪决定。

## 两套口径：PROTOCOLS.md 的 118 行 vs protocols/ 的 34 个 XML

讨论「kywc 支持多少协议」前必须先对齐口径，两个数字回答的是不同问题：

- **文档口径**：docs/PROTOCOLS.md 是一张 wayland.app 风格的支持矩阵，共 10 个分节、118 个数据行（F-R5-008），列出的是「整个 Wayland 生态里的知名协议 × kywc 是否支持」，包含大量标 `no` 的协议和不在仓内的上游协议；
- **代码口径**：protocols/ 目录实有 **34 个 XML 文件，共声明 77 个 `<interface>`**（F-R5-001，脚本逐个 XML 求和）。这是仓内 vendored、参与本仓代码生成的协议集合。

PROTOCOLS.md 的分节行数（F-R5-008）：

| 分节 | 行数 | 含义 |
|---|---|---|
| Wayland core | 7 | 内建 core global，src/ 无 XML，由 wlroots 创建（F-R5-060） |
| stable | 3 | xdg-shell、viewporter、presentation，取自 wayland-protocols 安装目录 |
| staging | 20 | 含 xwayland_shell_v1 重复一行（去重后 19，F-R5-054） |
| unstable | 24 | 含 4 个标 no、1 个标 "-" |
| wlr | 10 | wlroots 族，含 3 个 no |
| kde | 24 | plasma-wayland-protocols 族，含 11 个 no |
| weston | 10 | **全部标 no**（F-R5-061） |
| external | 8 | wl_drm 与若干 wayland-protocols/weston 外部协议混表 |
| ukui | 7 | openKylin kylin-wayland-protocols 族，全部为 1~3 |
| kywc | 5 | 自研族，**漏了 stream**（见差异表 D-R5-145） |

此外还有**第 35 个 XML** 不在 protocols/ 清单：src/plugin/security/security.xml（F-R5-052），后文专节说明。

## 34 个 vendored XML 六族归属与门控全表

族属按「XML 来源」划分（F-R5-013~046）。「门控」列指 protocols/meson.build 中该键是否包在 `if have_*` 条件块内；标「无条件」者在基础 dict（meson.build:4-30）或追加 dict（:32-41）中始终进入代码生成。

| XML 文件 | 主 interface | 族 | meson 键门控 |
|---|---|---|---|
| drm.xml | wl_drm（v2） | external | 无条件（`wl-drm`） |
| blur.xml | org_kde_kwin_blur_manager | kde | have_kde_blur |
| dpms.xml | org_kde_kwin_dpms_manager | kde | have_kde_output |
| idle.xml | org_kde_kwin_idle | kde | 无条件（`org-kde-kwin-idle`） |
| kde-keystate.xml | org_kde_kwin_keystate（v5） | kde | have_kde_keystate |
| kde-output-device-v2.xml | kde_output_device_v2（v8） | kde | have_kde_output |
| kde-output-management-v2.xml | kde_output_management_v2（v9） | kde | have_kde_output |
| kde-primary-output-v1.xml | kde_primary_output_v1（v2） | kde | have_kde_output |
| plasma-shell.xml | org_kde_plasma_shell（v8） | kde | have_kde_plasma_shell |
| plasma-virtual-desktop.xml | org_kde_plasma_virtual_desktop_management（v2） | kde | have_kde_virtual_desktop |
| plasma-window-management.xml | org_kde_plasma_window_management（v17，5 interface） | kde | have_kde_plasma_window_management |
| slide.xml | org_kde_kwin_slide_manager | kde | have_kde_slide |
| wlr-data-control-unstable-v1.xml | zwlr_data_control_manager_v1（v2，4 interface） | wlr | 无条件 |
| wlr-layer-shell-unstable-v1.xml | zwlr_layer_shell_v1（v4） | wlr | have_wlr_layer_shell |
| wlr-output-power-management-unstable-v1.xml | zwlr_output_power_manager_v1 | wlr | have_wlr_output |
| wlr-screencopy-unstable-v1.xml | zwlr_screencopy_manager_v1（v3） | wlr | 无条件（追加 dict） |
| wlr-virtual-pointer-unstable-v1.xml | zwlr_virtual_pointer_manager_v1（v2） | wlr | have_tools |
| text-input-unstable-v2.xml | zwp_text_input_manager_v2 | wayland/unstable | 无条件 |
| virtual-keyboard-unstable-v1.xml | zwp_virtual_keyboard_manager_v1 | wayland/unstable | have_tools |
| xdg-toplevel-icon-v1.xml | xdg_toplevel_icon_manager_v1 | wayland/staging | have_xdg_toplevel_icon |
| xdg-toplevel-tag-v1.xml | xdg_toplevel_tag_manager_v1 | wayland/staging | have_xdg_toplevel_tag |
| ukui-background-v1.xml | ukui_background_manager_v1 | ukui | have_ukui_background |
| ukui-blur-v1.xml | ukui_blur_manager_v1（v3） | ukui | have_ukui_blur |
| ukui-effect-v1.xml | ukui_effect_v1（4 interface） | ukui | have_ukui_effect |
| ukui-output-v1.xml | ukui_output_management_v1 | ukui | have_ukui_output |
| ukui-shell-v1.xml | ukui_shell_v1（v4，3 interface） | ukui | have_ukui_shell |
| ukui-startup-v2.xml | ukui_startup_management_v2 | ukui | have_ukui_startup |
| ukui-window-management.xml | ukui_window_management（v3，5 interface） | ukui | have_ukui_window_management |
| kywc-capture-v1.xml | kywc_capture_manager_v1（v2，3 interface） | kywc | 无条件 |
| kywc-output-v1.xml | kywc_output_manager_v1（3 interface） | kywc | 无条件 |
| kywc-security-v1.xml | kywc_security_manager_v1（2 interface） | kywc | 无条件 |
| kywc-stream-v1.xml | kywc_stream_manager_v1（2 interface） | kywc | 无条件 |
| kywc-toplevel-v1.xml | kywc_toplevel_manager_v1（2 interface） | kywc | 无条件 |
| kywc-workspace-v1.xml | kywc_workspace_manager_v1（2 interface） | kywc | 无条件 |

族计数：external 1 + kde 11 + wlr 5 + wayland 4 + ukui 7 + kywc 6 = 34。除此之外，protocols/meson.build 还以**绝对路径引用 wayland-protocols pkgdatadir 里的 XML**（xdg-shell、linux-dmabuf、security-context、cursor-shape、tablet-v2、xwayland-shell 等），这些 XML 不在 34 之数——这是「meson 字典键（29 固定键 + 十余个条件块，F-R5-002）多于 34 个本地 XML」的原因。

## 代码生成：scanner 三件套与 @BASENAME@ 命名

[protocols/meson.build:183-211](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/protocols/meson.build) 对字典 foreach，每个协议产出三件（F-R5-047）：

- `<key>_c`：`wayland-scanner private-code` → `@BASENAME@-protocol.c`，编入 wlcom_sources；
- `<key>_server_h`：`server-header` → `@BASENAME@-protocol.h`，编入 wlcom_sources；
- `<key>_client_h`：`client-header` → `@BASENAME@-client-protocol.h`，`build_by_default: false`，仅 libkywc/tools/examples 引用时才构建。

注意输出名按 **XML 文件 basename** 而非 meson 键命名，因此 libkywc 里 include 的是 `"kywc-capture-v1-client-protocol.h"` 这类名字（F-R5-048）。

> **差异块：linux-dmabuf-v1 键重复（D-R5-148）**
> meson.build:24 基础 dict 已有 `'linux-dmabuf-v1'`（指向 stable 路径），:161-166 的 `if have_ukui_background` 块又以同键同值 `protocols += {'linux-dmabuf-v1': …}` 一次。Meson 对 dict 重复键在 `+=` 合并时的行为依版本而定，存在配置期报错风险；本次仅静态读码，未做构建验证。

另一个 XML 层面的异常：kywc-stream-v1.xml 第 2 行 `<protocol name="kywc_capture_v1">` 与 kywc-capture-v1.xml 的 protocol 名相同（D-R5-147），属于复制粘贴遗留；interface 名本身正确，加上 scanner 按 basename 输出，故无文件冲突。

## global 注册的两类方式

代码生成只给出 `wl_*_interface` 描述符，运行时是否真的出现 global 还需要一次显式注册，仓内有两类写法（F-R5-049、F-R5-050）：

1. **手写 `wl_global_create` + 自有 bind**：自研协议全部如此，如 `wl_global_create(server->display, &kywc_capture_manager_v1_interface, 2, …, …_bind)`（src/effect/ky_capture.c:614）、ky_stream.c:213、src/security/ky_security.c:369、src/output/ky_output.c:659、src/view/ky_toplevel.c:812、ky_workspace.c:339、ukui_effect.c:710；wl_data_device_manager（src/input/data_device.c:1524）、wl_drm（src/render/wayland_drm.c:282）等上游协议也由合成器手写注册（F-R5-051）。
2. **wlroots 助手内部注册**：合成器只调一个 create 函数，global 由 wlroots 创建，例如 `wlr_layer_shell_v1_create(display, 4)`（src/view/wlr_layer_shell.c:564）、`wlr_virtual_pointer_manager_v1_create` / `wlr_virtual_keyboard_manager_v1_create`（src/input/input.c:818、823）、`wlr_viewporter_create`、`wlr_fractional_scale_manager_v1_create`（src/server.c:284-285）等（F-R5-050）。注意 xwayland_shell_v1 不在其列：它虽由 xwayland.c:88 调用，实现与 global 注册却在 src/xwayland/shell.c:155-167，是合成器自有代码（见 [13](/concepts/13-xwayland.md)）。

第二类解释了为什么 PROTOCOLS.md 里 `zwlr_foreign_toplevel_manager_v1(v3)`、`zwlr_output_manager_v1(v4)` 有运行时支持却在 protocols/ 和 meson 字典里找不到对应 XML——它们用的是 wlroots 安装头里自带的生成代码（F-R5-058）。

## 编译期三态裁剪：XML 存在 ≠ 编入 ≠ 运行时可 bind（I-1）

I-1 洞察的核心是一个逐层收窄的三态模型：

| 态 | 决定者 | 例子 |
|---|---|---|
| ① XML 存在 | protocols/ 目录或 wayland-protocols 安装包 | 34 个 vendored XML 永远在树上 |
| ② 编入二进制 | meson 44 个选项 → `HAVE_*` 宏 → 条件块是否加入 protocols 字典与源码编译 | have_ukui_background=false 时 ukui-background-v1 不生成代码、src/output/ukui_background.c 不编译 |
| ③ 运行时 global 存在 | 注册点是否被执行（选项运行时门控、管理器创建顺序、global filter） | security 插件的 global 仅对其 gui client 可见（F-R4-063）；`-Dnoxwayland` 可在运行时关闭 XWayland（见 [13](/concepts/13-xwayland.md)） |

构建链路：meson_options.txt 共 **44 个选项**（boolean 37、feature 3、string 4，I-1 数量裁决），协议相关的 `kde_*/ukui_*/wlr_*` 等 30 余个 boolean 默认 true，feature 型（nls、libunwind、libxcb-errors）默认 auto（F-R5-142、meson_options.txt:1-60）；meson.build:177-210 把它们转成 `-DHAVE_KDE_BLUR=@0@` 这类 0/1 宏，各协议 .c 内再以 `#if HAVE_*` 包裹注册代码。发行构建由 debian/rules 固定默认值——当前仅显式追加 `-Dukui_theme=true --buildtype=debugoptimized`，其余取选项默认值（debian/rules override_dh_auto_configure）。

典型三态实例：

- `zwp_virtual_keyboard_manager_v1`：XML vendored 在树上（①），但 meson 键挂在 `if have_tools`（②，meson.build:154-159），且它由 wlr 助手注册，wlcctrl 是其首个客户端（F-R5-039、F-R5-144）；
- `xwayland_shell_v1`：XML 取自 wayland-protocols staging（①），`if have_xwayland` 才进字典（②，meson.build:168-172），运行时还受 enable_xwayland 门控（③，F-R3-136）；
- `wp_content_type_manager_v1`、`ext_session_lock_manager_v1`：PROTOCOLS.md 列在 staging 表但标 `no`，src/ 内 grep 不到对应 global 注册（F-R5-055）——停在①之外。

### 第 35 个 XML：security.xml 例外

src/plugin/security/security.xml 描述 `kywc_security_configuration_v1`（v1，4 请求：destroy 与 set_protector_mode/color/image，F-R4-066、F-R4-067），它**不经过 protocols/meson.build**，而在 src/plugin/security/meson.build:5-24 单独跑 scanner 三件套；其 global 注册在插件 setup 内 security.c:466（F-R5-052）。许可方面，openKylin 自有的 13 个协议 XML（protocols/ 下 6 个 kywc-* + 7 个 ukui-*）均带 MulanPSL-2.0 SPDX 头，上游 wayland/wlr/kde/external 系 XML 为各自原许可；security.xml 是第 14 个 MulanPSL 协议文件，也是唯一位于 protocols/ 目录之外、不经 protocols/meson.build 的一个，PROTOCOLS.md 对它无记录（D-R5-149；早期事实「全树唯一 MulanPSL 协议文件」经复核更正）。语义见 [14](/concepts/14-security-portal.md)。

## PROTOCOLS.md 与代码的双源差异专表（D-R5-145~156）

以下 12 条为静态对账结果。**结论一律以代码（XML + 注册点）为最终事实层**；本表不替上游定性任何运行时影响。

| 编号 | 差异 | XML/代码事实 | PROTOCOLS.md 表述 |
|---|---|---|---|
| D-R5-145 | kywc 节缺 stream | kywc-stream-v1.xml 存在，ky_stream.c:213 注册 v1 global，libkywc provider 与 portal 全链路消费 | kywc 分节仅 5 行（:172-180），无 kywc_stream_manager_v1；同节也无 kywc_security_configuration_v1 |
| D-R5-146 | xwayland_shell 重复 | meson 键仅一次（:168-172），注册点 shell.c:163 与 xwayland.c:88 各一处 | staging 表 :47 与 :52 出现两行 `xwayland_shell_v1,1`，去重后 19 项 |
| D-R5-147 | stream XML protocol 名笔误 | kywc-stream-v1.xml:2 写 `name="kywc_capture_v1"`，interface 名正确，basename 命名避免冲突 | 文档不涉及该字段 |
| D-R5-148 | meson 键重复 | linux-dmabuf-v1 见于 :24 与 :163，同键同值 | 文档 unstable 表记 zwp_linux_dmabuf_v1=4，与 `wlr_linux_dmabuf_v1_create_with_renderer(…,4,…)`（renderer.c:88）一致 |
| D-R5-149 | 第 35 个 XML 未入矩阵 | src/plugin/security/security.xml 独立生成、security.c:466 注册，MulanPSL-2.0 | 无记录 |
| D-R5-150 | （portal 资产） | 与协议矩阵无直接关系，属打包差异，详见 [14](/concepts/14-security-portal.md) | — |
| D-R5-151 | Access 接口无 version | portal/access.c:234-239 vtable 无 version 属性，其余 4 个 impl 接口均有 | 文档不涉及 portal |
| D-R5-152 | i18n 口径 | 主域 27 .po / LINGUAS 16；portal 域 19 .po / LINGUAS 1（见 [15](/concepts/15-libkywc-clients.md)） | — |
| D-R5-153 | external 节归类混杂 | text-input-unstable-v2.xml、virtual-keyboard-unstable-v1.xml 随仓 vendored，来源属 wayland unstable | :146-156 把 zwp_text_input_manager_v2、zwp_virtual_keyboard_manager_v1 放入 external 节 |
| D-R5-154 | blur/plasma-shell 备注 "ukui" | 仓内并存 kde blur（blur.xml，kde_blur.c）与 ukui blur（ukui-blur-v1.xml，ukui_blur.c）两套协议 | :106 org_kde_kwin_blur_manager、:121 org_kde_plasma_shell 备注列填 "ukui"，无进一步说明 |
| D-R5-155 | "no" 行保留版本号数字 | grep 不到对应 *_interface 注册点 | content_type(no,说明1)、session_lock(no,1) 等 6 行在标 no 的同时说明列仍填 1，表头未定义该列语义 |
| D-R5-156 | METADATA 光标模式未映射 | portal/stream.h:16-20 有 CURSOR_MODE_METADATA=4，协议 enum 含 metadata；映射函数只处理 EMBEDDED 否则 HIDDEN | ScreenCast 上报 AvailableCursorModes=HIDDEN|EMBEDDED=3 |

补充回查发现：F-R5-060 记 wl_seat 行为「支持 6、说明 9」，而本次回查 docs/PROTOCOLS.md:15 原文为「支持 **8**、说明 9」，事实清单与文档原文有 1 处数字出入；core global 由 wlroots 创建，实际 bind 版本以 wl_display 上的注册为准，本篇不替上游裁决。

## 给客户端开发者的 bind 防御建议

1. **先查三态再写代码**：目标协议若挂在 `have_*` 下，读你所装发行版的构建配置（协议开关在 meson `summary` 的 Configuration 段输出，F-R1-033），不要因为 XML 在树上就假设可用；
2. **registry 里按名查找并容忍缺失**：global 可能整族缺席（weston 10 项全 no）、可能被 global filter 按 client 过滤（security_configuration 即如此）；bind 前判 version、bind 后处理 missing global；
3. **版本钳到自己测过的下限**：libkywc 的做法可直接借鉴——各 provider 统一 `version_to_bind = version <= 1 ? version : 1`，只有 capture 在 THUMBNAIL_EXT 能力下 bind 更高版本（F-R5-072，[15](/concepts/15-libkywc-clients.md)）；
4. **以代码注册行为准、PROTOCOLS.md 为参考**：文档有 12 条已对账差异，涉及具体版本号/有无时回到 `wl_global_create` 与 wlr 助手调用点核实。

## 相关概念

- [02 Wayland 与 wlroots 基础](/concepts/02-wayland-wlroots-basics.md)
- [13 XWayland 兼容层](/concepts/13-xwayland.md)
- [14 安全模型与 xdg-desktop-portal-wlcom](/concepts/14-security-portal.md)
- [15 libkywc 客户端库、示例生态与自带工具](/concepts/15-libkywc-clients.md)
- [07 输出管理](/concepts/07-output-management.md)
