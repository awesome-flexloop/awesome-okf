---
type: Concept
title: "场景图与 surface：三节点树、xdg_shell、装饰与损伤渲染"
description: "读懂 kywc 自研 scene 的 tree/rect/buffer 三节点、23 种角色（22 个有调试名）、两级损伤收集、surface/xdg/popup/layer 接入、SSD 装饰节点与 scene_output 一次合成的完整过程"
tags: [wayland, wlroots, scene-graph, xdg-shell, damage-tracking, ssd, decoration]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r2
    resource: /references/facts-graphics.md
    title: R2 后端/渲染/场景/输出事实清单
  - id: facts-r3
    resource: /references/facts-input-view.md
    title: R3 输入/视图事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：[05 渲染体系](/concepts/05-rendering.md)提供 renderer/pass 能力，本篇把客户端 surface 组织成一棵可增量重绘的场景树；[07 输出管理](/concepts/07-output-management.md)逐输出驱动这棵树完成一帧。指针如何命中树上的节点在 [08 输入](/concepts/08-input.md)，view 如何在树上挂窗口在 [09 视图与工作区](/concepts/09-view-workspace.md)。

kywc 没有直接使用 wlroots 的 wlr_scene，而是自研了一套结构相近、能力更大的 scene 子系统（src/scene/，16 个 .c 加私有头 scene_p.h）。它是整个合成器画面的唯一事实源：view、workspace、layer-shell、装饰、特效全部体现为树上的节点。

## 三种节点类型与 23 种实体角色

节点接口 `scene_node_interface` 有 10 个回调（include/scene/scene.h:74-116，F-R2-100）：accept_input、update_outputs、collect_damage、get_opaque_region、get_round_corner、render、get_bounding_box、get_affected_bounding_box、push_damage、destroy。

节点**类型只有 3 种**（scene.h:119-123，F-R2-101）：

```c
// include/scene/scene.h:119-123，裁剪
enum scene_node_type {
    SCENE_NODE_TREE,    // 容器：children 链表
    SCENE_NODE_RECT,    // 纯色/渐变/描边矩形
    SCENE_NODE_BUFFER,  // 一个 wlr_buffer（客户端像素或自绘缓冲）
};
```

在此之上用 `role`（type + impl + data）区分 **23 个实体角色**（include/scene/scene.h:126-157：SCENE_ROLE_ROOT 到 SCENE_ROLE_SNAPSHOT 共 23 个真实角色，另有 SCENE_ROLE_NONE=0 与 SCENE_ROLE_LAST 哨兵；其中 22 个在 scene.c 调试名表中有字符串、SNAPSHOT 未配名。V 阶段勘 F-R2-102 的「22」口径——22 是有名角色数，枚举真实角色为 23），按功能分组：

| 分组 | 角色 |
|---|---|
| 结构 | NONE、ROOT、LAYER、WORKSPACE、VIEW_PROXY、VIEW |
| Wayland surface | XDG_TOPLEVEL、XDG_POPUP、XDG_SURFACE、SUBSURFACE、SURFACE、DRAG_ICON |
| X11 | XWAYLAND_WINDOW、XWAYLAND_UNMANAGED |
| 层壳/装饰 | LAYER_SURFACE、SSD、SSD_TITLEBAR、SSD_BUTTONS、DECO、WALLPAPER |
| 菜单/快照 | MENU、SUBMEBU（源码拼写，字符串表为 "submenu"）、MENU_ITEM、SNAPSHOT |

枚举尾项 LAST 为哨兵（F-R2-102、scene.c:191-217）。节点公共字段 scene_node 含 parent/children、坐标、四角 radius、damage_type、blur 配置、input/clip/visible 区域、addons 与 add_effect/damage/destroy 事件（scene.h:217-271，F-R2-105）。

默认接口实现是「报错 + assert」：未实现的 render/collect_damage 等会被立刻发现（src/scene/scene.c:24-78，F-R2-108）；节点初始化默认 enabled=true、damage_type=HARMFUL，blur 默认 iterations=4、offset=5.5、alpha=1.0（scene.c:145-183，F-R2-109）。

### tree/rect/buffer 的行为要点

- **tree**：输入命中逆序遍历子节点（后挂的在上层，scene.c:255）；render 时在 DISABLE_SUBEFFECTNODE 模式下跳过 `has_effect` 子节点——特效节点由特效框架单独画（scene.c:328-346，F-R2-111）。
- **rect**：不透明要求 color[3]==1 并减去 clip 与圆角；渲染组 render_rect_options（radius 乘 scale），alpha!=1 用预乘混合（src/scene/rect.c:163-240，F-R2-140）。
- **buffer**：见下节主输出选择。set_input_region/clip_region/blur/radius 只允许 RECT/BUFFER 节点调用，tree 节点直接 assert（F-R2-117）。

## buffer 节点：主输出选择与 64 输出硬上限

scene_buffer 持有 buffer/texture（均可 NULL）、src_box、dst_width/height、transform、repeat_mode、opacity、opaque_region，以及关键字段 `primary_output` 与 `active_outputs`（scene.h:320-362，F-R2-107）。

输出归属在 `buffer_update_outputs`（src/scene/buffer.c:120-214，F-R2-127）计算：

- **主输出 = 与节点几何重叠面积最大的输出**；
- 活动输出集合是 64 位位图：`active_outputs = 1ull << output->index`，输出数组为定长 `outputs_array[64]`；
- assert「有 active 输出必有 primary」（buffer.c:188）。

输出索引在 scene_output_create 分配并 `assert(index < 64)`（src/scene/output.c:126-127）——因此**场景层硬上限 64 个输出**，超出触发 assert（R2 疑点 11）。纹理来源上，wlr_client_buffer 直接取 `client_buffer->texture`，否则 `wlr_texture_from_buffer` 缓存并监听 renderer destroy（buffer.c:304-341）。

buffer 渲染在 buffer.c:343-534（F-R2-128）：安全分支先走 security_get_region/security_render；混合模式按不透明区求交选 PREMULTIPLIED 或 NONE；radius 与 repeat 的 src_box 先乘 scale；挂 blur；调 `render_pass_add_texture`；发 output_sample（release=in_timeline/in_point、direct_scanout=false；直扫场景由 05 篇的 scene_try_direct_scanout 发 true）。

## 两级损伤：HARMFUL / HARMLESS 与 pushed_damage

损伤类型两位（scene.h:160-174，F-R2-103）：

```c
enum scene_damage_type {
    SCENE_DAMAGE_NONE = 0,
    SCENE_DAMAGE_HARMLESS = 1 << 0,  // 内容变了但几何/层级没变
    SCENE_DAMAGE_HARMFUL  = 1 << 1,  // 需要连带周边（如圆角、阴影）重绘
    SCENE_DAMAGE_BOTH = (1 << 2) - 1,
};
```

推送规则 `scene_push_damage`（scene.c:499-522，F-R2-113）：HARMLESS 且节点上次使能时，损伤先与 visible_region 求交再加入；HARMFUL 则遍历相关输出整体加损，并汇入 scene 的 `pushed_damage`。收集在 `scene_collect_damage`（scene.c:613-649，F-R2-114）：只有 pushed_damage 非空才收集，按每个输出的 geometry/viewport 求交分发到具体 scene_output。

典型粒度（buffer.c:626-649 等，F-R2-129）：同尺寸 buffer 提交按客户端 damage 映射出 HARMLESS；尺寸变化或 buffer 丢失推 BOTH；opacity 跨越 0/1 推 BOTH，其余 HARMLESS。rect 节点缩小尺寸时「先推后改」、放大后补推（rect.c:284-343）。

## surface 与 xdg_shell：客户端像素如何挂树

`scene_surface` 包一个 buffer 节点并监听 wlr_surface（include/scene/surface.h:10-27，src/scene/surface.c:278-335，F-R2-118）。两个 addon 名分别是挂 buffer 节点的 "scene_surface" 和挂 wlr_surface 的 "scene_surface_node"，可经 `wlr_surface_try_from_node` 反查。它处理：

- **map/commit**：surface_map 用 `wl_signal_add_next` 挂 map；commit 时映射 OPAQUE_REGION、viewport（VIEWPORT|BUFFER|SCALE|TRANSFORM）、buffer_damage 与 timeline acquire 点（surface.c:116-176，F-R2-122）；
- **分数缩放**：取 surface 所在输出最大 scale，调 `wlr_fractional_scale_v1_notify_scale` 并 `wlr_surface_set_preferred_buffer_scale(ceil)`（surface.c:30，F-R2-119，均为 wlr 符号）；
- **release 同步**：output_sample 仅主输出处理，把 release point 加到 out timeline 并回调 presented（zero_copy 取直扫标志，surface.c:55-75，F-R2-120）；
- SHM 纹理用 n_ignore_locks 计数绕过 wlr_scene 式的无条件 lock（surface.c:92-114，F-R2-121）。

xdg 表面由 `scene_xdg_surface_create` 建一棵外层 tree 加一棵 surface 子树，surface_tree 角色 SCENE_ROLE_XDG_SURFACE；位置取 `wlr_xdg_surface_get_geometry` 的负偏移，popup 用 current.geometry（src/scene/xdg_shell.c:11-96，F-R2-124）。

**子表面**递归成树：`scene_surface_tree_create` 按 current.subsurfaces_below/above 排序（below 先于 above），角色 SCENE_ROLE_SUBSURFACE，初始 enabled=mapped；子表面距父表面各角小于父 radius 时继承圆角（src/scene/subsurface.c:82-319，F-R2-125、126）。

各 shell 在场景层的接入点：

- xdg toplevel：src/view/xdg_shell.c:650 建 surface_tree；xdg popup：src/view/xdg_popup.c:374；
- **layer surface**：src/view/wlr_layer_shell.c:395-396 建 tree 后 `scene_subsurface_tree_create`，挂进四层 layer 树；
- IME 候选窗：src/input/text_input.c:666；XWayland unmanaged：src/xwayland/unmanaged.c:273——它们都复用 scene_surface，场景层不区分客户端来源。

## SSD 装饰与图形节点

服务端装饰（SSD）是 kywc 场景层最复杂的部分，实现在 src/scene/decoration.c（1185+ 行）。`scene_decoration` 首成员是 scene_rect，持有 6 个区域：surface/title/border/round_corner/pure_clip/clip，以及边框厚度、标题高度、四角半径、多层阴影（F-R2-131）。decoration_mask 是 8 方位位掩码，边框分 OUTER/INNER 两型（src/scene/decoration.h:10-26，F-R2-130）。

- 装饰与阴影各用一个**全局 GL program 单例**，构建期 embed scene/shaders/ 的 decoration 与 shadow 两对 vert/frag（decoration.c:100-200，F-R2-132）；阴影模糊半径转高斯 sigma 的系数 0.424660891（注释 =1/(2·sqrt(2ln2))，decoration.c:321-521，F-R2-134）。
- INNER/OUTER 决定区域内缩方式；尺寸变化推 BOTH，size<=0 时延迟到 pending_cause（decoration.c:523-689，F-R2-135）。
- 输入热区含 resize 边框，border 不计入不透明区以防下层画面碎裂（decoration.c:703-761，F-R2-136）。
- **软渲染回退**：GL 不可用时退回 render_pass_add_rect 画平色 surface/title/border；set_round_corner_radius/shadow 在无 GL program 时直接 return——软渲染下圆角/阴影静默失效（decoration.c:905-1073，F-R2-137、138，R2 疑点 9）。

其余图形节点：

| 节点 | 文件 | 能力与限制 |
|---|---|---|
| linear_gradient | src/scene/linear_gradient.c | 固定 2 个 color stop、角度换算，**仅 OpenGL 生效**，否则只画背景 rect（F-R2-141） |
| stroke_rect | src/scene/stroke_rect.c | 外盒减内盒拼环形区，stroke_width 乘 scale（F-R2-142） |
| animation | src/scene/animation.c | 节点跟随输出 frame 事件做 position/size 插值，POSITION/SIZE 两 mask（F-R2-143） |
| thumbnail | src/scene/thumbnail.c（1849 行） | NODE/VIEW/WORKSPACE/OUTPUT 四类离屏缩略图，双缓冲 + 假帧定时器，供任务栏/切换器取图（F-R2-147） |

另有三个与 surface 关联的小协议在场景层落地：alpha-modifier-v1（multiplier 映射 opacity，src/scene/alpha_modifier.c，F-R2-144）、tearing-control-v1（surface hint，scene_is_tearing_needed 遍历判定，src/scene/tearing_control.c，F-R2-145）、presentation-time（version 2、CLOCK_MONOTONIC、zero_copy kind 按直扫裁剪，src/scene/presentation_time.c，F-R2-146）。

## scene_output_do_render：一帧是怎么画出来的

每输出一个 scene_output 持有 wlr_output、wlr_damage_ring、collected/frame_damage、geometry、in/out timeline 与 viewport（scene.h:364-408，F-R2-106）。合成主函数 `scene_output_do_render`（src/scene/output.c:273-399）步骤：

1. `wlr_output_configure_primary_swapchain` 配置的是 **wlr 原生 swapchain**（`wlr_output->swapchain`），`wlr_swapchain_acquire` 同时取回 **buffer_age**（output.c:280-286）；
2. in_point 自增，以 signal_timeline 选项 `wlr_renderer_begin_buffer_pass` 开渲染 pass（:292-296）；
3. `wlr_damage_ring_get_buffer_damage` 按 buffer_age 取出累积损伤，平移到布局坐标（:307-318）；
4. `scene_render_damage_in_target`：先过 security_check_output/SECURITY_ACCESS_OUTPUT 鉴权，无权区域被裁掉，再从根节点递归 render（src/scene/render.c:146-205，F-R2-090）；清屏色 {0,0,0,1}（render.c:124，F-R2-089）；
5. 统一处理 excluded 区域后，`scene_render_target_add_software_cursors` 遍历 output->cursors，跳过禁用/不可见/与硬件光标重合者，用 wlr 原生 add_texture 叠加——**软件光标与安全裁剪在同一条渲染路径内闭环**（render.c:207-269，F-R2-091）；
6. blur 两处入口（背景模糊与带模糊纹理）做多级缩放，注释明确 blur 不支持旋转（render.c:298-526，F-R2-092）；
7. `render_pass_submit(pass, output->quirks)`，失败整损重试；设置 buffer damage 与 state buffer；有 timeline 时接 wait/signal（output.c:362-395）。

直扫在合成前先尝试：scene_output_commit 先 `scene_output_direct_scanout_is_allowed` 判定，再取全屏 buffer 调 `scene_try_direct_scanout`，失败才走上面的 do_render（判定与 transform/src_box/尺寸/test_state 条件详见 [05 渲染体系](/concepts/05-rendering.md)）。

## 场景层与 view 层的分工边界

读代码时最容易混淆的两个词：

- **surface / scene_surface 是场景层对象**：回答「这块像素在哪、多大、是否不透明、归哪个输出、怎么渲染」，跟随 wlr_surface commit 被动更新；
- **view 是合成器的窗口抽象**（src/view/）：回答「这个窗口是什么角色、在哪个工作区与 layer、是否最大化/最小化、是否可聚焦」，并持有挂在 workspace 子树上的 scene_tree。

一个 xdg toplevel 对应一个 view、一棵 view tree、一个 scene_xdg_surface（内含 scene_surface）。view_map 时使能树节点，view 状态变化改的是树的位置/使能/层级，真正画像素仍由场景层完成。view 状态机与 18 个 layer 的细节见 [09 视图与工作区](/concepts/09-view-workspace.md)；特效框架再包一层场景节点回调的机制见 [10 特效框架](/concepts/10-effects-framework.md)。

> ⚠️ 源码阅读提示（R2 疑点 8）：src/scene/rect.c:223 blur 几何处 `.node_ly = geo.x`（ly 赋成 x，疑应为 geo.y），源码原文如此，本教程不做运行时裁决。

## 相关概念

- 前导：[05 渲染体系](/concepts/05-rendering.md) — render pass、timeline 与 direct scanout 判定
- 后继：[07 输出与多显示器管理](/concepts/07-output-management.md) — 谁来驱动 scene_output_commit
- [08 输入系统](/concepts/08-input.md) — scene_node_at 命中与 click/hover 分发
- [09 视图、工作区与窗口管理](/concepts/09-view-workspace.md) — view 与 18 layer 如何挂这棵树
- [10 特效框架](/concepts/10-effects-framework.md) — 9 个节点回调被特效层包装
- 源码锚点：[scene.h](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/include/scene/scene.h#L119-L158)、[scene/output.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/scene/output.c#L273-L399)
- 信源：[R2 图形事实清单](/references/facts-graphics.md)、[R3 输入事实清单](/references/facts-input-view.md)
