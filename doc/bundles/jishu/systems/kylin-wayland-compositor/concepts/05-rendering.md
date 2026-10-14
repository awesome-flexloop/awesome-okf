---
type: Concept
title: "渲染体系：renderer、allocator、drm_syncobj、direct scanout 与 painter"
description: "读懂 kywc 渲染器选择与软件回退、GBM/dumb 分配链、drm_syncobj timeline 显式同步、direct scanout 判定、扩展 render pass 与 CPU painter 绘图面"
tags: [wayland, wlroots, opengl, gbm, drm-syncobj, pixman, cairo]
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

> **本篇在数据流中的位置**：[04 后端层](/concepts/04-backends.md)把显卡变成 `wlr_backend` 并给出 DRM fd；本篇负责把 fd 变成渲染器（renderer）、缓冲（allocator）与同步原语（drm_syncobj），再由 [06 场景图](/concepts/06-scene-graph.md)消费这些能力把节点画进缓冲。上屏编排（direct scanout 之后的提交）在 [07 输出管理](/concepts/07-output-management.md)。

## renderer 自动选择：GL 优先、pixman 兜底

渲染器总入口是 `renderer_autocreate`（src/render/renderer.c:27-68，F-R2-057）。选择逻辑很短，但分支有「两层解释」：

```c
// src/render/renderer.c:27-55，裁剪
const char *api = getenv("KYWC_RENDERER");        // renderer.c:30
if (api && strcmp(api, "pixman") == 0) {
    renderer = pixman_renderer_create();           // 纯 CPU 渲染器
    goto done;
}
if (api && strcmp(api, "vulkan") == 0) {
    renderer = wlr_vk_renderer_create_with_drm_fd(drm_fd); // wlr 符号，受 WLR_HAS_VULKAN_RENDERER
} else {
    renderer = opengl_renderer_create_with_drm_fd(drm_fd); // 默认：GL 系
}
if (!renderer) {
    renderer = pixman_renderer_create();           // renderer.c:52-55 硬件失败回退
}
```

环境变量 **`KYWC_RENDERER`** 识别四个值：`gl`/`gles2`/`vulkan`/`pixman`。但要注意：renderer.c 这一层只显式区分 `"pixman"`、`"vulkan"` 和默认 GL——`"gl"`/`"gles2"` 字串没有分支，落入默认 GL 路径；它们的**二次解释发生在 EGL 初始化**（src/render/opengl/egl.c:593-619，F-R2-061）：

- 值为 `"gl"` 时只试桌面 GL：`try_opengl_api`（egl.c:464、596）；
- 值为 `"gles2"` 时只试 GLES：`try_gles_api`（egl.c:525、601）；
- 未指定时按 quirk `QUIRKS_MASK_PREFER_OPENGL` 决定尝试顺序——带该 quirk 先 GL 后 GLES2，否则先 GLES2 后 GL（egl.c:607、613）；最终 `egl->is_gles = !epoxy_is_desktop_gl()`（egl.c:619，`epoxy_*` 为 libepoxy 符号）。

> ⚠️ 上游/事实差异（R2 疑点 1）：同一个 `KYWC_RENDERER` 被 getenv 两次（renderer.c:30、egl.c:593 附近），两层的分支集合不一致。阅读时不要以为 renderer.c 里没有 `"gl"` 分支它就不生效。

软件光栅器默认被拒绝：GL renderer 创建时检查 `GL_RENDERER` 字符串，含 "softpipe" 或以 "llvmpipe" 开头即判失败（src/render/opengl/renderer.c:636-645，F-R2-063）。需要在 llvmpipe/softpipe 上运行时，必须显式设置 **`KYWC_RENDERER_ALLOW_SOFTWARE`**（egl.c:392-398，F-R2-062）。**`KYWC_EGL_NO_MODIFIERS`** 则禁用 EGL 侧 modifiers（egl.c:200-204）。

渲染器身份还能经 D-Bus 查询：对象路径 `/com/kylin/Wlcom/Renderer`、接口 `com.kylin.Wlcom.Renderer`，方法 IsHardwareRendering→b、GetRendererName→s，名字集合为 "gles2"/"gl"/"vulkan"/"pixman"（src/render/config.c:1-51，F-R2-064）。

### wl_display 侧的缓冲协议初始化

`renderer_init_wl_display`（renderer.c:70-101，F-R2-058）按序初始化：`wlr_renderer_init_wl_shm`、single_pixel_buffer_manager、linux-dmabuf（version 4），wayland_buffer 创建失败时回退 wayland_drm。timeline 管理器 `drm_syncobj_manager_v1_create` 只在三个条件同时成立时创建：**`KYWC_ENABLE_TIMELINE`=1**、`renderer_support_timeline` 与 `backend_support_timeline` 均真（renderer.c:82-86）。其中 renderer 侧仅 OpenGL 报告支持 timeline（renderer.c:160-168，F-R2-059）——pixman/vulkan 路径无此判定。

## allocator：GBM 优先、SCANOUT 失败加 RENDERING 重试

缓冲类型在 include/render/allocator.h 定义为四类：`GBM`、`DUMB`、`SHM`、`MEM`，flags 含 AUTO/RENDERING/NO_SCANOUT/CURSOR/LINEAR/SINGLE_PLANE（F-R2-068）。

`allocator_create`（src/render/allocator/allocator.c:232-280，F-R2-070）的选择顺序：

1. backend 与 renderer 都支持 DMABUF → GBM 分配器；
2. 需要 `drmIsMaster`（libdrm 符号）且 quirk 含 `QUIRKS_MASK_PREFER_DRM_DUMB` 时追加 DRM dumb 能力；
3. 无 buffer_caps 时以 SHM 兜底。quirks 来自 `quirks_by_backend(drm_fd)`，可用 **`KYWC_FORCE_QUIRKS`** 强制（src/util/quirks.c:46，F-R2-076）。

GBM 分配的 usage 映射与关键回退在 src/render/allocator/gbm.c:133-178（F-R2-072）：默认带 `GBM_BO_USE_SCANOUT`，RENDERING/CURSOR/LINEAR 追加对应位，NO_SCANOUT 去掉 SCANOUT；**带 SCANOUT 的分配失败后，加 RENDERING 标志重试一次**（gbm.c:170-178）。仍失败再由上层退回 DRM dumb（drm_dumb.c:64、197-214）或 SHM（shm.c:111）/MEM（mem.c:59，F-R2-074）。

kywc 自有的多 GPU swapchain 容量固定为 4：`SWAPCHAIN_CAP 4`（src/render/allocator/swapchain.c:18，F-R2-071），每个 slot 记录 age（注释引用 EGL_EXT_buffer_age）。注意它与场景合成用的 wlr 原生 swapchain（`WLR_SWAPCHAIN_CAP`）是两套并存实现（见 06 篇，R2 疑点 7）。

### 多 GPU blit：四模式与 swapchain 选择

非主 GPU 输出不能直接使用主 GPU renderer 产出的缓冲，需要 blit。表面模式有四种（src/backend/drm/drm_p.h:192-213，F-R2-021）：

| 模式 | 含义 |
|---|---|
| NONE | 无需 blit（缓冲本就属于该 GPU） |
| RENDER | GL blit：renderer 在子 GPU 上重绘纹理 |
| COPY | readpixels 拷贝到 dumb buffer |
| RENDER_COPY | 两阶段组合 |

多 GPU renderer 初始化同样是 GL 优先、pixman 兜底（src/backend/drm/renderer.c:50-102，F-R2-065），每批最多 86 个四边形（`MAX_QUADS=86`，renderer.c:32）；blit shader 三选一：tex_frag/tex_oes_frag/tex_yuv_frag（renderer.c:172-202，F-R2-066）。swapchain 在 test 失败后去 modifier 重试；pixman renderer 用 DUMB、否则 GBM，copy swapchain 恒为 DUMB；timeline 创建条件为 backend 与 renderer 双支持且 drm_fd≥0（renderer.c:487-544、626-676、753-761，F-R2-067）。

## drm_syncobj：timeline 显式同步

显式同步的核心对象是 `drm_syncobj_timeline`（include/render/drm_syncobj.h，F-R2-077）：持有 drm_fd、syncobj handle 与引用计数，API 覆盖 create/export/import/transfer/signal/check/waiter 与 sync_file 导入导出。关键实现行：create src/render/drm_syncobj.c:34、`export_sync_file` :111、`import_sync_file` :136、`waiter_init` :215（F-R2-078）。多个 sync fd 可用 merger 聚合（drm_syncobj_merger.h，F-R2-079）。

场景输出侧维护 in/out 两条 timeline（src/scene/output.c:151-163，F-R2-085）：`wlr_backend_get_drm_fd`≥0 且 renderer/backend 双支持时各建一条；任一创建失败则两条都丢弃并回退 implicit sync（日志 "Failed to create DRM syncobj timeline, falling back to implicit sync"），销毁时对两条 timeline signal(UINT64_MAX)（output.c:189-196）。

合成帧提交时：in_point 自增并经 `wlr_output_set_wait_timeline` 等待，out_point 自增并经 `wlr_output_set_signal_timeline` 发出信号（src/scene/output.c:292-294、390-395）。DRM 原子提交侧，等待点由 `drm_syncobj_timeline_export_sync_file` 导出为 sync_file，写入 plane 的 `IN_FENCE_FD` 属性（src/backend/drm/kms.c:640-647，F-R2-034）。

Wayland 协议面（linux-explicit-synchronization 同类思想的 kywc 自有 drm_syncobj v1 协议）通过 `wlr_surface_synced` 挂到 surface commit：set_acquire_point/set_release_point（src/render/drm_syncobj_v1.c:106-149），finish_state/move_state/commit 三回调随 surface commit 轮换 acquire/release 状态（:167-209，F-R2-082）；eventfd 支持探测 check_syncobj_eventfd 在 :428-496（F-R2-084）。

## 扩展 render pass 与 profile

kywc 没有另起渲染器，而是在 wlroots 的 render pass 外包了一层扩展选项（include/render/pass.h:1-99，F-R2-086）：

- `render_texture_options` 在 wlr 原生选项外增加 radius（四角圆角）、force_opaque、rotation_angle、repeat_mode、mix_options、wait_timeline；
- 重复模式枚举 `render_texture_repeat_mode` 为 NONE/NORAML（源码拼写）/CLAMP/MIRROR/DECAL；
- `render_rect_options` 带 transform、radius、rotation、stroke_width、linear_gradient；
- 另有 render_round_corner、render_color_stop、双停点 render_linear_gradient 与 render_texture_mix_options。

分派在 src/render/pass.c：OpenGL/pixman 各有实现，不支持的选项回退到 wlr 原生选项，并提供 render_pass_save/restore（F-R2-087）。性能打点 PROFILE_RENDER_* 宏受 TRACY_ENABLE 条件编译，未启用时为空宏（include/render/profile.h、src/render/profile.c，F-R2-088）。

## 像素格式：35 处表项与外部 YUV 数组

格式表结构 `pixel_format` 同时携带 GL 与 pixman 双映射（include/render/pixel_format.h，F-R2-094）。表规模口径：src/render/pixel_format.c 中 `.drm_format =` 赋值 **35 处**（脚本计数口径，F-R2-095），覆盖 ARGB/XRGB/XBGR/ABGR 等 8888 系列、R8/GR88/RGB888、4444/565/5551、2101010、16161616(F)、YVYU/VYUY 等。另有 18 个外部 YUV 格式数组（YUYV/UYVY/NV12…YUV444 等，pixel_format.c:257-268），P010/P012/P016 按宏条件追加（F-R2-096）。注释明确 DRM_FORMAT_ARGB8888 实际兼容 GL_BGRA_EXT（pixel_format.c:15，F-R2-097）。

格式还驱动 KMS 侧选择：max_bpc 按格式推导（101010→10、161616→16、默认 8，kms.c:107-123，F-R2-098）；YUYV scanout 时 AddFB 用 DRM_FORMAT_YUYV、缓冲宽度折半，由 quirk `QUIRKS_MASK_YUYV_MODE` 与 `drm_output_yuyv_enabled`（src/backend/drm/output.c:910-918）控制（F-R2-099）。

## direct scanout：全屏客户端缓冲直上扫描out

direct scanout（直接扫描输出）让单个全屏不透明客户端缓冲不经合成直接进入 KMS，省一次 GPU 拷贝。开关初始值在 scene_output_create 计算（src/scene/output.c:141-143）：

```c
char *env = getenv("KYWC_DISABLE_DIRECT_SCANOUT");        // output.c:141
scene_output->direct_scanout =
    !(env && strcmp(env, "true") == 0) &&
    !(_output->quirks & QUIRKS_MASK_DISABLE_DIRECT_SCANOUT);
```

允许判定 `scene_output_direct_scanout_is_allowed`（output.c:466-487）依次要求：本地开关为真、`wlr_output_is_direct_scanout_allowed`（wlr 符号）为真、硬件色彩通路可用、特效层 `effect_manager_allow_direct_scanout` 不反对。

具体尝试在 `scene_try_direct_scanout`（output.c:489-572），条件全部命中才直扫：

1. buffer 的 transform 必须等于 output transform（:498）；
2. src_box 为空或等于按 transform 交换宽高后的默认整盒（:502-514）；
3. buffer 尺寸必须**精确等于**输出模式尺寸，否则记 "Scene buffer size mismatch" 并放弃（:516-520）；
4. 拷贝一份 `wlr_output_state`，对 client_buffer 解开 n_locks 取源缓冲（:532-544），接 wait/signal timeline（:546-553）；
5. **`wlr_output_test_state` 原子 TEST_ONLY 成功**才采纳（:555-558），失败回退普通合成；成功后发 output_sample 事件，direct_scanout=true（:563-569）。

全屏候选缓冲由 `scene_output_get_fullscreen_buffer` 自根节点逆序递归、按不透明区完全覆盖输出几何选出（output.c:401-464）。运行期还可用 D-Bus SetDirectScanout 改写开关（src/output/config.c:77-87、141）。

scanout 成功时 present 事件携带的 flags 在 DRM 后端固定为 VSYNC|HW_CLOCK|HW_COMPLETION，非多 GPU 子设备再追加 ZERO_COPY（src/backend/drm/drm.c:1630-1716，`page_flip_handler2`、drmEventContext version=3，F-R2-029）——这是客户端判断「零拷贝上屏」的依据。

## painter：独立的 CPU 绘图面

菜单、SSD 标题栏文字、安全保护提示等不需要 GL 的自绘内容走独立子系统 src/painter/（4 个文件）。它产出的是标准 `wlr_buffer`：`painter_buffer` 首成员即 `struct wlr_buffer base`，只实现 destroy/begin_data_ptr_access/end_data_ptr_access，数据访问固定上报 **DRM_FORMAT_ARGB8888**，stride=width*4（src/painter/painter_p.h:14-24、painter.c:13-52，F-R2-172）。

- 缓冲按 scale 以 ceil 分配物理像素：`painter_create_buffer(width,height,scale)`（painter.c:54-87，F-R2-173）；
- 绘制管线是 cairo+pango：CAIRO_FORMAT_ARGB32、`cairo_surface_set_device_scale`，顺序 svg→底色（solid/hover/border）→文本，FONT_WEIGHT 固定 500（src/painter/render.c:20-63、336-384，F-R2-176）；
- 文本支持斜体、勾选 "✓"、子菜单箭头、快捷键、加速键标记、RTL 与中段省略；圆角由 cairo_arc 拼出，SVG 经 librsvg `rsvg_handle_render_document` 渲染（render.c:65-334，F-R2-177，`rsvg_*`/`pango_*`/`cairo_*` 均为外部库符号）；
- 图像解码按文件头魔术数分派（src/painter/image.c，F-R2-178）：PNG→libpng（含预乘行回调）、JPEG→libjpeg/libjpeg-turbo（turbo 用 JCS_EXT_BGRA）、ICO（选 32bpp 最佳项）、BMP（仅 32bpp 无压缩）、XPM（自解析，宽高上限 1024）；编码仅 PNG 或 BMP，按文件名后缀选择。

painter 的产物经 widget 层挂成 scene_buffer（见 [09 视图与工作区](/concepts/09-view-workspace.md) 的 widget 小节），与 GL 渲染路径解耦。

## 渲染相关回退链（洞察 I-5 的中间三级）

整条图形栈是「理想路径 + 显式回退 + 环境变量开关」，渲染层贡献其中三级：

| 级别 | 理想路径 | 回退 | 开关/条件 | 证据 |
|---|---|---|---|---|
| 渲染器 | OpenGL（GL/GLES2）/Vulkan 硬件 | pixman 纯 CPU；llvmpipe 默认被拒 | `KYWC_RENDERER`、`KYWC_RENDERER_ALLOW_SOFTWARE` | F-R2-057、061-063 |
| 缓冲分配 | GBM+SCANOUT | GBM+RENDERING 重试 → DRM dumb → SHM/MEM | `QUIRKS_MASK_PREFER_DRM_DUMB`、`KYWC_FORCE_QUIRKS` | F-R2-068~074 |
| 上屏 | direct scanout 零拷贝 | swapchain 合成；多 GPU 时 RENDER/COPY blit | `KYWC_DISABLE_DIRECT_SCANOUT`、quirk、test_state | F-R2-021、029 |

同步原语同理：drm_syncobj timeline 需要 `KYWC_ENABLE_TIMELINE`=1 且 renderer/backend 双向支持才建立，否则回退 implicit sync（F-R2-058、085）。排查黑屏/撕裂/色彩异常时，先定位命中了哪条路径，比盯主路径更有效（洞察 I-5）。

## 本篇环境变量速查

| 变量 | 消费点 | 作用 |
|---|---|---|
| `KYWC_RENDERER` | renderer.c:30、egl.c:593 | gl/gles2/vulkan/pixman 选择（两层解释） |
| `KYWC_RENDERER_ALLOW_SOFTWARE` | egl.c:392 | 放行 llvmpipe/softpipe |
| `KYWC_EGL_NO_MODIFIERS` | egl.c:200 | 禁用 EGL modifiers |
| `KYWC_ENABLE_TIMELINE` | renderer.c:82 | 允许建 drm_syncobj timeline manager |
| `KYWC_DISABLE_DIRECT_SCANOUT` | scene/output.c:141 | =true 关闭直扫 |
| `KYWC_SOFTWARE_COLOR` | backend/drm/output.c:441 | 色彩管理强制 GL blit 软件通路（见 07） |
| `KYWC_FORCE_QUIRKS` | util/quirks.c:46 | 强制 quirks 位 |

## 相关概念

- 前导：[04 后端层](/concepts/04-backends.md) — DRM fd、多 GPU 后端与 page flip 事件
- 后继：[06 场景图与 surface](/concepts/06-scene-graph.md) — render pass 如何被场景节点消费
- [07 输出与多显示器管理](/concepts/07-output-management.md) — 模式 test、提交排序与硬件/软件色彩
- [10 特效框架](/concepts/10-effects-framework.md) — blur 等特效对 render pass 与 direct scanout 的拦截
- 源码锚点：[renderer.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/render/renderer.c#L27-L101)、[scene/output.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/scene/output.c#L466-L572)
- 信源：[R2 图形事实清单](/references/facts-graphics.md)、[源码信源登记](/references/source-code-map.md)
