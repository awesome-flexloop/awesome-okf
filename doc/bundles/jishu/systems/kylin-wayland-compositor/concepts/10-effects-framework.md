---
type: Concept
title: "特效框架与 40 个内置特效：钩子、动画时钟、transform 体系与 shader"
description: "读懂 effect manager 在 server_init 的位置、17 个特效钩子、animator 动画时钟、transform 节点体系、40 个静态内置特效的四组分工、14 个内嵌 shader 与 Effect D-Bus"
tags: [wayland, wlroots, compositor-effects, animation, opengl, shaders, dbus]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r4
    resource: /references/facts-effect-plugin.md
    title: R4 特效/插件/安全事实清单
  - id: facts-r2
    resource: /references/facts-graphics.md
    title: R2 后端/渲染/场景/输出事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：特效层横切 [06 场景图](/concepts/06-scene-graph.md)（包装节点渲染回调、拦截帧渲染与 direct scanout）和 [09 视图工作区](/concepts/09-view-workspace.md)（响应 map/minimize 等窗口动作），并提供截图/录屏/放大镜等功能给 [15 客户端面](/concepts/15-libkywc-clients.md)。外部插件如何挂载是 [11 插件系统](/concepts/11-plugin-system.md) 的内容，安全相关特效见 [14 安全与 portal](/concepts/14-security-portal.md)。

## effect manager 在启动序列中的位置

特效管理器在 `server_init` 中创建于 view/xwayland 之后、plugin_manager 之前（src/server.c:340-346）：

```c
output_manager_create(server);
input_manager_create(server);
view_manager_create(server);
xwayland_manager_create(server);
effect_manager_create(server);   // server.c:345
plugin_manager_create(server);
```

`effect_manager_create`（src/effect/effect.c:1011-1071，F-R4-109）先把 time_scale 置 1.0，再按固定顺序建 **9 个内部 manager**：action_effect、animation、thumbnail、snapshot、capture、ky_capture、stream、ky_stream、wlr_screencopy（:1021-1029），随后建 blurrer（:1030）与 ukui_effect（:1032，注释要求在 animation manager 之后）；最后在 :1043-1068 分 4 组创建 23 个特效（6+5+5+7 个 _effect_create；F-R4-110 逐组列出）；连同 showkey/wallpaper（延迟到 server_ready 回调，effect.c:991-995，F-R4-111）与 ukui_effect（:1032），该函数内 `_effect_create` 调用点合计 26 个——注意两个数字的口径：23 是 :1043-1068 分组创建块内的数量，26 是 effect_manager_create 全部特效创建调用（含 3 个块外项）。

## effect_interface：17 个钩子与包装机制

特效与场景层的契约是 `struct effect_interface`，共 **17 个函数指针**（include/effect/effect.h:36-66，F-R4-098），按作用点分五段：

| 段 | 钩子 |
|---|---|
| 实体生命周期（3） | entity_create、entity_destroy、entity_enable |
| 几何查询（3） | entity_bounding_box、entity_clip_region、entity_opaque_region |
| 节点（3） | node_push_damage、node_render、node_destroy |
| 帧渲染（5） | frame_render_pre、frame_render_begin、frame_render、frame_render_end、frame_render_post |
| 策略（3） | configure、allow_direct_scanout、allow_enabled |

特效分类 effect_category 有 5 值：UNKNOWN/STYLE/ACTION/SCENE/UTILS（effect.h:68-74，F-R4-099）。动作掩码 effect_action 覆盖 MAP/UNMAP/MOVE/RESIZE/MAXIMIZE(_RESTORE)/MINIMIZE(_RESTORE)/SHAKE/ACTIVATE，其中 `TRANSFORM=(1<<8)-1` 是前八位的并集（effect.h:76-89，F-R4-100）。

特效通过 effect_chain/slot 挂到节点或场景（effect.h:115-168，F-R4-103），节点链 addon 名为 "node_effect_chain"（effect.c:238-241）；effect 层**包装替换了 9 个 scene_node_interface 回调**（effect.c:566-577，F-R4-107），从而在场景递归渲染时插入特效逻辑。5 个 scene_output_render_* 包装点在 effect.c:1188-1226（F-R4-114）：frame_render 阶段钩子返回 true 表示特效接管整帧。

优先级规则写在注释里（effect.h:121-132，F-R4-102）：priority 值越大越靠链表尾、影响面越大；取边界从高到低，渲染顺序从高到低逆序。工厂是 `effect_create(name,priority,enabled,impl,data)`（effect.c:953-978，F-R4-108）。

> ⚠️ 死代码事实（R4 疑点 7）：内部 effect_type 枚举有 NONE/NODE/VIEW/SCENE 三类（effect.c:17-22），但 get_effect_types 只置 SCENE 与 NODE 两位（:26-38），**EFFECT_TYPE_VIEW 全树零引用**——视图级特效类型定义了却未使用。

特效与窗口状态的对接面是 kywc_view：角色枚举 17 个枚举器（=16 个真实角色加 ROLE_UNDEF 哨兵）、12 能力位、**23 个事件信号**（include/kywc/view.h:161-209，F-R4-176），特效监听这些信号决定何时把自己挂上节点。

## action_effect 与 animator 动画时钟

窗口开关类动效有两条平行体系。action_effect（include/effect/action.h）类型为 NONE/FADE/SLIDE（F-R4-117），接口 3 钩子 init_options/add_to_node/add_to_view（action.h:53-59），节点/视图挂载实现在 src/effect/action.c:123-155，管理器 action_effect_manager_create 在 action.c:69（F-R4-119）。

通用动画时钟在 src/effect/animator.c：

- 空闲对象池上限 **UNUSED_ANIMATION_MAX_COUNT=30**（animator.c:19，F-R4-120）；
- **10 种动画类型**（CUSTOM + 9 预设曲线），控制点为静态表：LINER（源码拼写）、EASE、EASE_IN/OUT/IN_OUT 与四组三次贝塞尔（:29-36，F-R4-121）；
- 属性掩码 6 位：ALPHA/ANGLE/GEOMETRY_X/Y/W/H（:38-47，F-R4-122）；
- 三次贝塞尔求参数 t 用 Newton-Raphson，8 次迭代、1e-6 阈值（:79-127，F-R4-123）。

全局时间缩放 time_scale 默认 1.0、下限 0.1（effect.c:1018、1079-1088），D-Bus 入参允许范围 0.1-20（config.c:150-162）。

## transform 节点体系

几何类特效共享 transform 基类：`transform_effect_create` 是 effect_create 的包装，category=ACTION，**软件渲染器下默认禁用**（src/effect/transform.c:236-270，F-R4-125）；内置名 "transform_effect"、priority 98（:778-788，F-R4-126）。transform impl 实挂 7 个钩子（entity_bounding_box、node_push_damage、node_render、frame_render_pre/post、configure、allow_direct_scanout，:426-435，F-R4-129）。

体系内各特效：

- **fade**（fade.c:362-374）：同时注册 action_effect(FADE) 与 transform "fade"（priority 10），服务 MAP/UNMAP（F-R4-133）；
- **slide**（slide.c，HAVE_KDE_SLIDE 条件编译）：action SLIDE + transform "slide"(5)，并把系统窗重定父到 LAYER_NORMAL（F-R4-134）；
- **scale**（scale.c:177-190）：transform "scale"(5)，支持 RESIZE/MAXIMIZE/MAXIMIZE_RESTORE/MINIMIZE/MINIMIZE_RESTORE 五动作，crossfade 需 OpenGL（F-R4-135）；
- **translation**（translation.c:319-338）：("translation",105)，SCENE 类，duration=400ms，服务工作区切换跟手；
- **output_transform**（output_transform.c:734-759）：("output_transform",105)，SCENE 类、仅 OpenGL，SCALE/ROTATE 两型，scale_duration 默认 1400ms；
- **move**（move.c:207-214）：("move",0,false)，仅 configure 钩子，对外提供 move_proxy API；
- **shake_view**（shake_view.c:236-243）：("shake_view",0,true)，用 wl_event_loop 定时器；
- **magic_lamp**（magic_lamp.c:666-694）：("magic_lamp",5,true)，最小化神灯效果，subdiv 32x8，LINER 动画，有专属 shader。

## 40 个内置 .c：四组分工与文件地图

src/effect/ 实测 **40 个 .c**：36 个随构建无条件编入（meson 两段 files()，含 ky_capture/ky_stream），4 个条件编译（screenshot/watermark/slide/ukui_effect，F-R4-002、006-011）。按功能四组：

### 1. 窗口动效与模糊

| 文件 | 注册 | 要点 |
|---|---|---|
| blur.c | ("blur",**999**,true)，STYLE 类（blur.c:709-724，F-R4-130） | 挂 frame_render_begin/end/post，实时模糊，优先级全树最高 |
| blurrer.c | blurrer_create 仅 OpenGL（:580-582，F-R4-131） | 建 **3 个 GL 程序**（blur_down:514 / blur_up:524 / blur_up_last:533） |
| fade/slide/scale/translation/output_transform/move/shake_view/magic_lamp | 见上节 transform 体系 | |

### 2. 截图、录屏与快照（内部 manager + 协议 global 混编）

| 文件 | 性质 | 注册点 |
|---|---|---|
| capture.c | **内部 manager，无 wayland global**；5 个 CAPTURE_NEED_* 位，4 回调 | capture_manager_create，capture.c:1277（F-R4-160） |
| snapshot.c | 内部快照 manager，可从 node/view 建 | snapshot.c:992（F-R4-161） |
| stream.c | 内部录屏 manager，像素格式 ARGB8888/XRGB8888 | stream.c:979（F-R4-162） |
| wlr_screencopy.c | 发 zwlr_screencopy_manager_v1 global **version 3** | wlr_screencopy.c:436-443（F-R4-165） |
| ky_capture.c | 发 kywc_capture_manager_v1 global **version 2** | ky_capture.c:607-614（F-R4-163） |
| ky_stream.c | 发 kywc_stream_manager_v1 global version 1 | ky_stream.c:206-213（F-R4-164） |
| screenshot.c | HAVE_UKUI_SCREENSHOT；非 effect_create，D-Bus 兼容 org.ukui.KWin/org.kde.KWin 两套名，输出 /tmp/kywc_screenshot_XXXXXX.bmp | screenshot.c:262-270（F-R4-156） |

### 3. 辅助功能

| 文件 | 注册 | 对外接口 |
|---|---|---|
| zoom.c | ("zoom",**122**,false)（zoom.c:926-933，F-R4-146） | D-Bus org.ukui.Magnifier 8 方法 + 5 快捷键（Win+=/-/KP_Add/KP_Sub/Esc） |
| locate_pointer.c | ("locate_pointer",**111**,false)（:327-335，F-R4-141） | 选项 long_press_timeout |
| color_filter.c | ("color_filter",**200**,true)（:286-293，F-R4-144） | org.ukui.KWin /ColorFilter 8 方法，含 GrayScale/Invert，快捷键 Win+Ctrl+c |
| color_picker.c | ("color_picker",116,true)（:722-730，F-R4-145） | /ColorPicker，PickColor 返回 "ddd" |
| showfps.c | ("showfps",112,false)（:353-360，F-R4-142） | always_repaint、allow_direct_scanout 选项 |

### 4. 输入可视化、水印与壁纸

| 文件 | 注册 | 要点 |
|---|---|---|
| mouse_click.c | ("mouse_click",100,false)，经 tap_ripple 工厂（:121-143，F-R4-147） | 监听 seat 按钮，size=50、duration=600 |
| mouse_trail.c | ("mouse_trail",100,false)，经 trail 工厂（F-R4-148） | 监听 motion，thickness=8、life=120 |
| touch_click/touch_touch_long/touch_trail | ("touch_click",100) / ("touch_long",102,true) / ("touch_trail",100)（F-R4-149~151） | touch_long 经 circle_progressbar 工厂 |
| tap_ripple.c / trail.c / circle_progressbar.c | 三个基类工厂，SCENE 类、仅 OpenGL（F-R4-152~154） | 形状接口集中在 include/effect/shape.h |
| showkey.c | ("showkey",106,true)（showkey.c:754-761，F-R4-143） | enable 时注册 /com/kylin/Wlcom/Showkey 两 D-Bus 方法 |
| wallpaper.c | ("wallpaper",0,false)，监听 new_enabled_output 与主题更新（:397-404，F-R4-157） | **server_ready 时创建** |
| watermark.c | HAVE_UKUI_WATERMARK；("watermark",0,true)，UTILS，allow_enabled 恒 false（:583-599，F-R4-158） | 两套 D-Bus（org.ukui.KWin /Watermark 与 /com/kylin/Wlcom/Watermark） |

另有 ukui_effect.c（HAVE_UKUI_EFFECT）发布 ukui_effect_v1 global version 1，surface 以 addon 挂载（ukui_effect.c:702-710，F-R4-159）。

## 14 个 shader：构建期 embed 与引用点

src/effect/shaders/ 实测 **14 个 shader 源文件 = 7 对 vert/frag**（F-R4-003）：blur_down、blur_up、blur_up_last、circle_progressbar、magic_lamp、shape_color、tap_ripple。它们经 meson embed 程序在构建期生成下划线化同名 `.h`（如 blur_down.vert → `blur_down_vert.h`）编入主二进制（src/effect/shaders/meson.build:18-29，F-R4-012）。

引用点共 5 处（F-R4-166~172）：

1. 6 个 blur shader 头由 blurrer.c:17-22 include，建 3 个程序（:514/:524/:533），up_last 带 roundCornerRadius 等 uniform（通用 uniform 名 `frambufferSize` 为源码拼写，须与 shader 内字面一致）；
2. circle_progressbar：circle_progressbar.c:15-16、:57；
3. magic_lamp：magic_lamp.c:25-26、:371；
4. shape_color：trail.c:18-19、:64；
5. tap_ripple：tap_ripple.c:21-22、:62。

特效之外，场景装饰另有 4 个 shader（decoration/shadow 各一对，见 [06 场景图](/concepts/06-scene-graph.md)），DRM blit 另有 4 个（见 [05 渲染](/concepts/05-rendering.md)）。

## D-Bus 接口：/com/kylin/Wlcom/Effect

对象路径 `/com/kylin/Wlcom/Effect`、接口 `com.kylin.Wlcom.Effect`，vtable 暴露 **5 个方法且全部 UNPRIVILEGED**（src/effect/config.c:10-12、150-162，F-R4-115）：

| 方法 | 签名 | 作用 |
|---|---|---|
| ListAllEffects | → a(sub) | 列出全部特效与启用态 |
| EnableEffect | sb | 运行时启用/禁用 |
| PrintEffectOptions | s → s | 打印某特效选项 |
| SetEffectOption | ssv | 设置单个选项 |
| SetEffectTimeScale | d → d | 全局动画时间缩放，入参钳到 **0.1-20**，回值按 0.1 取整 |

配置节名为 "Effects"（config.c:166）；每个特效的强制启用键是 **"force_enabled"，缺省 -1**（-1 表示沿用代码默认 enabled，0/1 覆盖；config.c:9、191-199，F-R4-116）。功能键分发共 4 个 FUNC_ID（effect.c:1104-1122，F-R4-113）。

## 编译边界：静态内置，插件极薄

40 个特效 `.c` **全部以 `wlcom_sources += files(...)` 静态编入主二进制**，src/effect/ 内没有任何 shared_module（src/effect/meson.build:1-65，F-R4-005、006）。整个 **src/ 主程序构建图内唯一的 shared_module 是 src/plugin/security 的 security 示例插件（install:false）**；examples/meson.build:95 另有 simple 插件示例同为 shared_module 且 install:false——即发行安装内容中不含任何可安装插件 .so。这意味着二开窗口动效的现实路径是「进 src/effect 照 40 个范例加静态 .c 重新编译」，而不是丢一个 .so 进插件目录（架构洞察 I-4）；插件 ABI 1.0、加载器与 `<name>_plugin_data` 契约的细节见 [11 插件系统](/concepts/11-plugin-system.md)。

## 相关概念

- 前导：[09 视图、工作区与窗口管理](/concepts/09-view-workspace.md) — 窗口动作与特效触发源
- 后继：[11 插件系统](/concepts/11-plugin-system.md) — ABI 1.0、dlopen 加载与 3 个插件 hook
- [06 场景图与 surface](/concepts/06-scene-graph.md) — 9 个被包装的节点回调与 blur 渲染挂载
- [05 渲染体系](/concepts/05-rendering.md) — render pass、软件渲染器降级与 direct scanout 拦截
- [14 安全与 portal](/concepts/14-security-portal.md) — src/ 内唯一 shared_module（security 示例）与 capture 安全闸门
- 源码锚点：[effect.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/effect/effect.c#L1011-L1071)、[effect.h](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/include/effect/effect.h#L36-L89)
- 信源：[R4 特效/插件事实清单](/references/facts-effect-plugin.md)、[R2 图形事实清单](/references/facts-graphics.md)
