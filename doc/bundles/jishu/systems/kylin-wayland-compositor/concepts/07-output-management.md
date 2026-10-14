---
type: Concept
title: "输出与多显示器管理：热插拔、配置编排与五套输出协议"
description: "读懂 kywc 新输出接入、eDP/LVDS 自定义模式、PPI 自适应缩放、configure_outputs 严格排序、硬件/软件色彩三通道与 KDE/wlr/ukui/kywc/xdg 输出协议汇合链"
tags: [wayland, wlroots, multi-monitor, hotplug, color-management, output-protocol]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r2
    resource: /references/facts-graphics.md
    title: R2 后端/渲染/场景/输出事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：后端 emit `new_output` 之后（见 [04 后端层](/concepts/04-backends.md)），本篇决定每个输出的开关、模式、缩放、位置、色彩与主从关系，并把结果组装成 `wlr_output_state` 提交；提交成功后 [06 场景图](/concepts/06-scene-graph.md) 的 scene_output 才开始逐帧合成。外部进程经五套输出协议影响本篇，协议 XML 本身在 [12 协议全景](/concepts/12-protocols.md)。

## 新输出接入：new_output → handle_new_output

后端扫描到连接器后 emit `events.new_output`（DRM 侧见 src/backend/drm/drm.c:1935），输出管理器在创建时监听它（src/output/output.c:1025-1026）。处理函数 `handle_new_output`（output.c:826-912，F-R2-161）按序：

1. non_desktop 输出（VR 头显等）跳过，不配置（:831-834）；
2. 调 wlr 符号 `wlr_output_init_render` 绑定 allocator/renderer（:836）；
3. 分配 kywc `struct output`，接线 present/frame/destroy/commit/request_state 5 个 wlr 输出监听（:848-857）与 11 个 kywc 输出事件（:862-872）；
4. **默认亮度 brightness=100、色温 color_temp=6500K**（:885-886），`output_init_quirks` 锁定软件光标等 quirk；
5. `output_add_custom_modes` 为屏内面板补自定义模式；采集属性、生成 uuid（description 字符串的 md5，output.c:234-246、668-675，F-R2-158）；
6. headless 且名为 "FALLBACK" 的 1920x1080 输出登记为 fallback_output（:896-899）；
7. emit new_output 后立刻 `get_configures(false)` + `output_manager_configure_outputs(NULL)`（:907-911）——**新输出插入即触发一次全量编排**。

### eDP/LVDS 的 13 横 + 12 竖自定义模式

笔记本屏固件往往只给一个原生模式。`output_add_custom_modes`（src/output/modes.c:28-78）只对 DRM 后端且名前缀为 "eDP"/"LVDS" 的面板生效；当面板所有模式同为一个分辨率时，按当前方向补入一组常见分辨率：

- 横向表 `custom_landscape_modes` **13 项**：800x600 到 2160x1440（modes.c:15-20）；
- 竖向表 `custom_portrait_modes` **12 项**：600x800 到 1440x2160（modes.c:22-26）；
- 只添加不超过面板物理分辨率且不等于当前分辨率的项，经 `wlr_output_add_mode` 注册（:66-77）。

## get_configures：默认配置、PPI 缩放与 layouts JSON

编排的第一步是收集「期望状态」。output_manager 只有一个接口回调 `get_configures(bool output_removed)`（src/output/output_p.h:14-55，F-R2-148），实现有三种来源：

1. **layout manager**：`KYWC_USE_LAYOUT_MANAGER`=1 时，配置节 "layouts" 存在则用 `output_manager_get_layout_configs`（src/output/config.c:455-486、558-572，F-R2-170），逐输出读对应布局键 `<layout_uuid>:<output_uuid>`；多输出布局 uuid 是排序后输出 uuid 拼接的 md5，单输出即自身 uuid；UPDATE 编排后自动保存（config.c:383-453）。
2. **UKUI settings daemon**：ukui_output_config 把回调替换为 `output_manager_get_usd_configs`（src/output/ukui_output_config.c:343）。
3. **默认**：`fallback_default_configure` 给每个实际输出填首选状态（config.c:488-515）。

首选状态 `output_fill_preferred_state`（src/output/configure.c:20-103，F-R2-164）：

- enabled=power=true、transform NORMAL；fallback 坐标 (0,0)，其余 (-1,-1) 表示自动摆放；
- 首选模式取第一个 preferred 否则链表头；
- **PPI 自适应缩放**：get_screen_factor 按物理屏幕英寸取系数（<12 英寸 20.0、<20 英寸 24.5、其余 28.0），get_scale_level 把对角 PPI 量化为 **1.0 / 1.25 / 1.5 / 2.0** 四档；
- 亮度缺省 100 并 CLAMP 到 10-100；色温缺省 6500，CLAMP 1000-25000K（configure.c:17-18 宏）。

> ⚠️ 上游/事实差异（R2 疑点 14）：色温钳位宏对 **小于 1000 的值回退为 6500**（而非钳到 1000），大于 25000 才钳到 25000，边界不对称。

## configure_outputs：严格排序与模式逐级回退

收集到的期望状态进 configure_outputs 链表（`output_manager_add_pending_state`，configure.c:153-183，F-R2-165），由 `output_manager_configure_outputs`（configure.c:405-592，F-R2-169）统一提交。排序是这一篇最关键的正确性设计：

```text
0. primary fixup：待禁的主输出清空，自动修正到首个 enabled 输出
   单输出/双输出(含 fallback)坐标强制修正为 (0,0)
1. 所有实际输出都将被禁用 → 拒绝本次配置（唯一例外：最后一个输出拔出）
2. 先改「已启用输出」的状态（模式/位置/色彩…）
3. 再启用「新输出」；有实际输出时拒绝启用 fallback
4. 仍无主输出时自动启用 fallback 并设为 primary
5. 切换 primary output
6. 最后禁用待关闭输出
7. finish 段兜底 primary；实际输出存在时自动禁用 fallback
   emit configured（INIT/UPDATE）
```

证据：全禁用拒绝在 configure.c:490-493（日志 "All outputs will be disabled, reject this configuration"）；四个提交循环在 :498-546；fallback 自动起停在 :527-531、576-581。

单个输出的提交在 `output_set_state`（configure.c:305-397，F-R2-168）：按 state_changed/mode_changed/params_changed 组 `wlr_output_state`；DRM 启用中、同尺寸且场景提交时置 has_pending=true **等一次 page flip** 再改（:337-343）；配 primary swapchain；色彩变化时按硬件是否允许决定整损或调度帧。模式设置 `output_state_set_mode` 找不到精确模式时用 custom_mode，`wlr_output_test_state` 失败则**遍历其余模式逐个 TEST_ONLY 回退**（configure.c:191-244，F-R2-166）。新 swapchain 首帧还需填充：`KYWC_OUTPUT_FILL_WALLPAPER`=1 时取主题背景并启用 "wallpaper" effect，否则清色（configure.c:246-303，F-R2-167）。

状态同步中枢是 `output_update_state`（output.c:517-649，F-R2-157）：scene_output 与 layout_output 同生共灭（assert）；几何变化触发排序与 max_scale 更新；TRANSFORM 挂 OUTPUT_TRANSFORM_EFFECT_ROTATE 特效、POSITION/SCALE 挂 SCALE 特效；usable_area 变化还会调 `xwayland_update_workarea()` 同步 X11 工作区（output.c:476-515，F-R2-156）。VRR/tearing 分别在 attempt_vrr/attempt_tearing 中先 test 再决定（output.c:422-458，F-R2-155）。

### 状态变化位与帧调度

状态差异由 `output_get_state_changes` 归并为 13 类变化位（include/output.h:12-26、src/output/output.c:341-395，F-R2-151）：ENABLE、POWER、MODE、TRANSFORM、SCALE、VRR_POLICY、POSITION、BRIGHTNESS、COLOR_TEMP、OVERSCAN、COLOR_FEATURE、COLOR_FILTER、SCALING_MODE、RGB_RANGE——configure_type 只有 NONE/INIT/UPDATE 三值。这一位集决定 output_set_state 需要组装哪些 wlr_output_state 字段。

帧不是任意时刻都调度：`output_schedule_frame` 以 server->active 为门控，`schedule_frame_timer` 是 10ms 定时器（output.c:96、132、148-162，F-R2-153）；for_each_output 按 enabled 过滤，has_actual_outputs 判断是否存在非 fallback 输出。三个 wlr 事件的分工（output.c:734-798，F-R2-160）：

- **present**：清 scene_commit 标志，has_pending 时合并一次 configure（带 PROFILE_RENDER_COLLECT 打点）；
- **frame**：有待配置则置 frame_pending 跳过本帧，否则 scene_output_commit，并用 CLOCK_MONOTONIC 取时 send_frame_done；
- **commit**：scene_output->frame_damage 非空时 emit layout_damage，通知特效/插件层（插件 LAYOUT_DAMAGE hook 由此驱动，见 [11 插件系统](/concepts/11-plugin-system.md)）。

handle_request_state 只接受 WLR_OUTPUT_STATE_MODE（custom_mode 或具体 mode，F-R2-160），客户端不能绕过编排直接改其他字段。

## 硬件色彩三通道与软件回退

色彩实现在 src/backend/drm/output.c（后端能力侧）与 src/output/（状态侧），共三条硬件通道（F-R2-036）：

| 通道 | KMS 载体 | kywc 内容 |
|---|---|---|
| 亮度 | connector BRIGHTNESS 属性 | 0-100 直接写 |
| 色温 | CRTC GAMMA_LUT | blackbody_color[] 表覆盖 **1000K-25100K**（注释源自 Redshift colorramp.c），fill_gamma_ramp_with_color_temp（output.c:329-351） |
| 色彩滤镜 | CRTC CTM | 内置 **6 个 4x4 矩阵**：default/grayscale/invert/protanopia/deuteranopia/tritanopia（output.c:269-309），值编码为 S31.32 sign-magnitude（:427-434） |

硬件是否可用分四级 color_feature：DISABLE/SOFTCOLOR/SOFTGAMMA/SOFTCTM，由 drm_output_use_hw_brightness/color_temp/color_filter 判定（output.c:755-844）。两条硬规则：

- **INVERT 滤镜永不走硬件**（矩阵存在但 invert 被排除在硬件通道外，强制软件）；
- OpenGL renderer 下 `wlr_output_get_color_capabilities` 直接报告三项全支持，否则才 probe CRTC 属性（output.c:885-908）。

**`KYWC_SOFTWARE_COLOR`=1**（output.c:441）或硬件不支持时，色彩改由主平面 GL blit 实现——这正是 [05 篇](/concepts/05-rendering.md)多 GPU blit 表面 need_primary_blit 的触发条件之一。quirks 还可按显卡禁用 GAMMA/CTM 或强制 YUYV（QUIRKS_MASK_DISABLE_GAMMA/DISABLE_CTM/YUYV_MODE）。

## 五套输出协议：全部汇入同一条 pending_state 链

输出管理对外有六组 Wayland 协议实现（输出侧常称「五套 + xdg-output」），全部在 `output_manager_create` 中创建（output.c:1033-1038）：

| 协议 | kywc 文件 | 注册开关 | 用途 |
|---|---|---|---|
| xdg-output v1 | src/output/xdg_output.c | 无（无条件） | 逻辑位置/逻辑尺寸（F-R2-149） |
| kywc-output（ky_output） | src/output/ky_output.c | 无 | kywc 自有完整输出管理 |
| kde-output-device-v2 + output-management-v2 | src/output/kde_output.c | HAVE_KDE_OUTPUT | KDE 系客户端配置；内含 **kde-primary-output v1** global（kde_output.c:1112-1115） |
| wlr-output-management | src/output/wlr_output.c | HAVE_WLR_OUTPUT | wlr 系工具（wlr-randr 类） |
| ukui-output | src/output/ukui_output.c | HAVE_UKUI_OUTPUT | UKUI 控制面板 |
| ukui-output-config/background | ukui_output_config.c、ukui_background.c | HAVE_UKUI_OUTPUT_CONFIG / HAVE_UKUI_BACKGROUND | USD 配置下发与背景 |

接线要点：无论请求从哪套协议进来，kywc 侧都只改 `output->pending_state` 并经 `output_manager_add_pending_state` 进入同一条 configure_outputs 编排链，再由上面的排序/提交逻辑统一落地——协议差异只体现在状态上报的序列化方式。各协议的 XML、版本号与 global 注册细节在 [12 协议全景](/concepts/12-protocols.md)（注意 I-1：XML 存在 ≠ 运行时 global 存在，HAVE_* 宏受 meson 裁剪）。

另有 D-Bus 接口 `/com/kylin/Wlcom/Output`（com.kylin.Wlcom.Output，src/output/config.c:9-145，F-R2-170）提供 8 个 UNPRIVILEGED 方法：ListAllOutputs（仅 DRM 输出）、GetCapabilities、GetHardwareCursor、SetBrightness、SetColortemp、SetDirectScanout（直接写 scene_output->direct_scanout）、SetColorFilter、SetColorFeature。

## 布局、镜像与热插拔收尾

布局工具在 src/output/layout.c（F-R2-171）：边缘判定取边外 1px；镜像模式 = 所有启用输出 geometry 相同；`kywc_output_at_point` 用 closest_point 选输出；工作区 workarea 只收缩与布局外边缘对齐的边；输出链表按 (x,y) 字典序插入排序。坐标 (-1,-1) 表示交给 `wlr_output_layout_add_auto` 自动摆放。

拔出处理 `handle_output_destroy`（output.c:677-732，F-R2-159）：get_configures(true)、加入待禁 pending、对其余输出重新编排，释放 modes/edid/uuid。挂起/休眠/恢复（output.c:914-923、987-1041，F-R2-162、163）：manager 创建时内建一个 headless 1920x1080 "FALLBACK" 输出兜底，保证无实际输出时合成器仍有渲染目标；suspend 销毁 swapchain，hibernate 断电，resume 损整或重新上电。

## 本篇环境变量速查

| 变量 | 消费点 | 作用 |
|---|---|---|
| `KYWC_DRM_DEVICES` | backend.c:291 | 指定显卡、决定有哪些输出（见 04） |
| `KYWC_USE_LAYOUT_MANAGER` | output.c:1028 | =1 启用 "layouts" JSON 持久化编排 |
| `KYWC_OUTPUT_FILL_WALLPAPER` | configure.c:254 | 新 swapchain 首帧填壁纸而非清色 |
| `KYWC_DISABLE_DIRECT_SCANOUT` | scene/output.c:141 | 关闭直扫（见 05/06） |
| `KYWC_SOFTWARE_COLOR` | backend/drm/output.c:441 | 强制软件色彩通路 |
| `KYWC_FORCE_QUIRKS` | util/quirks.c:46 | 强制 GAMMA/CTM/YUYV/软件光标等位 |

## 相关概念

- 前导：[06 场景图与 surface](/concepts/06-scene-graph.md) — scene_output 与损伤环
- 后继：[08 输入系统](/concepts/08-input.md) — 输出变化如何影响光标与触摸映射
- [04 后端层](/concepts/04-backends.md) — 连接器扫描、page flip 与 GAMMA/CTM KMS 属性
- [12 协议全景](/concepts/12-protocols.md) — 五套输出协议的 XML 与 HAVE_* 裁剪
- [13 XWayland](/concepts/13-xwayland.md) — usable_area 与 workarea 的 X11 同步
- 源码锚点：[output.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/output/output.c#L826-L912)、[configure.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/output/configure.c#L405-L592)
- 信源：[R2 图形事实清单](/references/facts-graphics.md)、[源码信源登记](/references/source-code-map.md)
