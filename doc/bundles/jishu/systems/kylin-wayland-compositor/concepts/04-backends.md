---
type: Concept
title: "后端层：DRM/fbdev/session/libinput/EIS 与后端自动选择"
description: "读懂 kywc 的 multi backend 组装与 backend_autocreate 决策树、DRM 原子/传统双模、fbdev 软件回退、logind 会话、EIS 虚拟输入与 libinput 独立线程边界"
tags: [wayland, wlroots, drm, kms, fbdev, logind, libinput, libeis]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r2
    resource: /references/facts-graphics.md
    title: R2 后端/渲染/场景/输出事实清单
  - id: facts-r1
    resource: /references/facts-build-startup.md
    title: R1 构建/启动/配置/打包事实清单
  - id: facts-r3
    resource: /references/facts-input-view.md
    title: R3 输入/视图事实清单
  - id: kywc-docs
    resource: /references/project-docs.md
    title: kywc 仓库自带文档登记与口径说明
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：本篇是主线的第一站——硬件/会话经后端层变成 wlroots 可消费的 `wlr_backend` 与输入事件，之后才轮到 [05 渲染](/concepts/05-rendering.md) 与 [08 输入](/concepts/08-input.md)。前置阅读 [03 启动架构](/concepts/03-startup-architecture.md)，其中 wlroots_server_init 的第 2 步就是调用本篇的 `backend_autocreate`。

## 后端总览与自动选择决策

kywc 没有直接使用单一后端，而是自研了一个后端组装层（src/backend/backend.c）。三个等待/规模常量先立边界（F-R2-001，backend.c:23-25）：`WAIT_SESSION_TIMEOUT=10000`ms、`WAIT_GPU_TIMEOUT=5000`ms、`MAX_NUM_GPUS=8`。

`backend_autocreate(display, session_ptr)`（src/backend/backend.c:427-484，F-R2-007~009）的决策树如下：

```text
WAYLAND_DISPLAY / WAYLAND_SOCKET / DISPLAY 任一存在？
├─ 是（嵌套会话）→ wlr_backend_autocreate(display, NULL)，直接返回
│                  （wlroots 符号；不需要 session，server 侧标 active=true）
└─ 否（原生硬件）
   1. wlr_multi_backend_create(display)            // multi backend 容器
   2. session_create_and_wait(display)             // 只尝试 logind，见后文
   3. KYWC_BACKEND == "fbdev"？
      ├─ 是 → 只尝试 fbdev
      └─ 否 → attempt_drm_backend；失败回退 fbdev
                （日志 "Failed to open any drm device, fallback to fbdev"）
   4. libinput_backend_create 加入 multi（失败即整体失败）
   5. 返回 multi backend
```

两个分支的证据要点：

- **嵌套优先**：检测三个环境变量任一存在即整体转发给 wlroots 自带后端（F-R2-007，backend.c:430-431）。这就是 README 所说「x11/wayland 嵌套运行」的实现路径，嵌套后端不出现在 kywc 自己的后端名表里——该表为 {"none","drm","headless","fbdev"}（F-R2-012，src/output/output.c:227）。
- **原生 multi**：原生路径创建 multi backend 与 session，显示后端与 libinput 后端都作为子 backend 加入（F-R2-008、F-R2-009，backend.c:440-477）。EIS 与 headless 不在 backend_autocreate 内创建（F-R2-011）。

### GPU 发现与主 GPU 选取

原生 DRM 路径的设备来源（F-R2-002~006）：

- `KYWC_DRM_DEVICES` 指定设备列表（冒号分隔，backend.c:291 读取）；**第一个设备即默认渲染设备**（ENV.md:13 项目文档口径一致）。未设置该变量时才创建 drm_backend_monitor 做运行时热插监控（backend.c:421-423，F-R2-003）；
- 自动发现走 udev：enumerate subsystem "drm"、sysname 匹配 `card[0-9]*`、使用 DRM_PRIMARY_MINOR_NAME、经 libdrm 的 `drmIsKMS` 过滤，并按 udev ID_SEAT 与当前 seat 匹配（F-R2-004，backend.c:171-189，`drmIsKMS` 为 libdrm 符号）；
- 枚举无结果时在 session 的 new_dev 事件上等待 5 秒（WAIT_GPU_TIMEOUT），超时失败（F-R2-005）；
- 主 GPU 选取 `pick_main_gpu` 按属性优先级：boot_display → boot_vga → 首个 PCI 设备，并有 USB 设备特殊分支（F-R2-006，backend.c:208-266）。

每个成功创建的 DRM 设备经 `wlr_multi_backend_add` 加入容器，首个成功者作为 primary_drm（backend.c:402-424）；多 GPU 场景的 blit/timeline 协作在渲染篇展开。

## DRM 后端：原子/传统双模与提交链

DRM 后端代码集中在 src/backend/drm/（backend.c、drm.c、fb.c、kms.c、lease.c、monitor.c、properties.c、renderer.c、util.c 加 gen_pnpids.sh 与 shaders/）。

### 启动、能力与模式

- backend_impl.start 调 `drm_scan_connectors(..., NULL)` 做首轮连接器扫描；buffer caps 返回 `WLR_BUFFER_CAP_DMABUF|SHM|DATA_PTR` 三位，并实现 get_drm_fd（F-R2-013）。
- KMS 模式只有两种：`enum drm_kms_mode { ATOMIC=0, LEGACY }`（F-R2-018，drm_p.h:28-31）。特性检查 `drm_check_features` 要求 DRM_CLIENT_CAP_UNIVERSAL_PLANES、CRTC_IN_VBLANK_EVENT、TIMESTAMP_MONOTONIC 等能力；环境变量 **`KYWC_DRM_NO_ATOMIC`=1** 时强制 LEGACY（F-R2-024，drm.c:79）。
- **`KYWC_DRM_NO_MODIFIERS`=1** 禁用 modifiers；否则查 DRM_CAP_ADDFB2_MODIFIERS。异步翻页（tearing）能力按模式分别查 DRM_CAP_ASYNC_PAGE_FLIP（LEGACY）与 DRM_CAP_ATOMIC_ASYNC_PAGE_FLIP（ATOMIC），并使能 CURSOR_PLANE_HOTSPOT 客户端能力（F-R2-025，drm.c:105-116）。
- 传统模式下还用 `drmModeSetCursor` 以 ARGB8888 LINEAR 尝试补登一个 cursor plane（F-R2-026）。
- 每设备输出状态是 9 位字段掩码：BRIGHTNESS、GAMMA_LUT、RGB_CTM、DAMAGE、RGB_RANGE、OVERSCAN、SCALING_MODE、SIGNAL_TIMELINE、WAIT_TIMELINE（F-R2-019）。KMS 属性枚举规模为 CRTC 7、plane 19、connector 14，字符串表在 properties.c（F-R2-020）。

### framebuffer、提交与 page flip

- framebuffer 添加三级回退：`drmModeAddFB2WithModifiers` → `drmModeAddFB2` → legacy `drmModeAddFB`；YUYV 路径宽度折半、格式 DRM_FORMAT_YUYV；另有 "drm_fb"/"drm_poisoned_fb" 两个 addon 名，关闭失败回退 RmFB（F-R2-035，fb.c:26-76，`drmMode*` 均为 libdrm 符号）。
- 原子提交在 kms.c：设置 CRTC_ID/MODE_ID/ACTIVE、brightness/rgb_range/overscan/scaling_mode/GAMMA_LUT/CTM/VRR_ENABLED、plane 属性与 FB_DAMAGE_CLIPS、hotspot；IN_FENCE_FD 由 `drm_syncobj_timeline_export_sync_file` 导出 sync_file 写入（F-R2-034，kms.c:640-647）。提交 flags 为 TEST_ONLY/ALLOW_MODESET/NONBLOCK；plane 坐标是 16.16 定点；色彩矩阵硬编码 BT601 + LIMITED 范围（F-R2-034，深入见 [05 渲染](/concepts/05-rendering.md)）。
- page flip 事件交换 queued/current buffer 并发 present，flags 为 VSYNC|HW_CLOCK|HW_COMPLETION，非多 GPU 子设备时追加 ZERO_COPY；`drmEventContext` version=3、处理函数 `page_flip_handler2`（F-R2-029，drm.c:1630-1716）——这是 0.17 API 形态的典型触点（见 [02](/concepts/02-wayland-wlroots-basics.md)）。

### 连接器、热插拔与 lease

- `drm_scan_connectors` 维护 seen 数组，分别处理 connect/disconnect，新输出在末尾 emit `events.new_output`；LINK_STATUS_BAD 触发断开（F-R2-030）。session 失活期间的变更走 `drm_update_connector`，VT 切回走 `drm_restore_connectors`（F-R2-031）；后端层的 handle_device_change 还区分 HOTPLUG 与 LEASE 两类 udev change（F-R2-014）。
- 连接时跳过 INTERLACE 模式，解析 EDID、采集 max_bpc/VRR/色彩属性（F-R2-032）。CRTC 再分配是二分图匹配且禁止夺取已启用输出的 CRTC（F-R2-027）。
- DRM lease：lease 对象集合为 connector+crtc+primary plane+cursor plane，每输出最多 4 个；经 libdrm `drmModeCreateLease` 创建，lease_device_v1 全局在后端创建时一并建立（F-R2-033、F-R2-016，受 drm_lease_device meson 选项门控）。

### 关键私有结构与主平面 blit 触发

两个核心私有结构承载了每设备/每连接器状态（F-R2-022、F-R2-023，drm_p.h:318-428）：

- `drm_device`：fd、name、addfb2_modifiers、supports_tearing_page_flips、cursor 尺寸、mgpu_renderer，以及 crtcs/planes/connectors/page_flips/fbs 链表头与 session_active 标志；
- `drm_connector`：name[24]、edid、brightness、rgb_range、overscan、scaling_mode、cursor_*、state、adaptive_sync_supported、max_bpc_bounds 等；非 master fd 通过重开节点并 `drmDropMaster` 获得，用于 quirks 查询（F-R2-017）。

主平面是否需要 blit 在 `drm_connector_state_update_primary_fb` 判定（F-R2-028，drm.c:912-1020）：先依次做硬件亮度/色温/色彩滤镜三项判定；need_primary_blit 成立条件包括「非主 GPU」「硬件不支持色彩」「use_yuyv」「分配器为 SHM」，命中即调 drm_surface_blit，YUYV 路径缓冲宽度为像素宽的一半。这是多 GPU 与软件色彩最终汇入 DRM 提交的接合点。

### 色彩硬件通路与 4 个 DRM shader

输出色彩支持色温（blackbody 表覆盖 1000K-25100K，注释标注源自 Redshift colorramp.c）、6 个内置 4x4 矩阵（default/grayscale/invert/三种色盲模拟）、GAMMA_LUT 与 CTM；硬件能力按 kywc_output_state 的色彩特性分级，INVERT 滤镜不走硬件；**`KYWC_SOFTWARE_COLOR`=1** 强制软件色彩（F-R2-036，output.c:441）。多 GPU blit 表面有 NONE/RENDER/COPY/RENDER_COPY 四模式（F-R2-021），由 4 个 DRM blit shader 支撑：tex.vert、tex.frag、tex_oes.frag、tex_yuv.frag（shaders/ 目录实测，配合多 GPU GL 优先/pixman 兜底的 renderer.c，F-R2-065、F-R2-066）。

## fbdev：软件后备后端

当 DRM 不可用（老旧/嵌入式显卡）或显式要求时使用 fbdev：

- 环境变量 **`KYWC_BACKEND=fbdev`** 是唯一识别的精确值（backend.c:453-454，F-R1-119）；设备列表来自 **`KYWC_FB_DEVICES`**（冒号分隔，backend.c:68，F-R2-002）。
- caps 为 DATA_PTR|SHM，backend_start 即 emit new_output；session 非激活时离屏（F-R2-037）。
- 像素格式由屏幕信息推算（calculate_drm_format，F-R2-039）；test/commit/create 三个输出操作齐备（F-R2-040）。
- present 事件不依赖硬件 vblank，而是用 `wlr_event_loop_add_idle` 延迟发送（F-R2-041，`wlr_output_send_present` 为 wlroots 符号）；提交时按 damage 矩形把 shadow framebuffer 逐块拷贝到 mmap 的 fb，并断言 stride 与像素宽一致（F-R2-042）。

## session/logind：设备授权与 VT 切换

kywc 没有使用 wlroots 的 session 后端（构建时 `session=disabled`，F-R1-008），而是自带 src/backend/session/。会话接口含 destroy/open/close/change_vt/seat_name/get_fd/dispatch 共 7 个回调，仓内仅有 logind 一种实现（F-R2-043）。

- `ACTIVATION_TIMEOUT=0`，session_init 只尝试 logind，并 `setenv("XDG_SESSION_TYPE","wayland")`（F-R2-044，session.c:22、64-65）。
- udev 监视器只过滤 drm 子系统：add→new_dev 事件，change→读 HOTPLUG/LEASE 分类，remove→销毁设备，按 devnum 去重（F-R2-045、F-R2-046）。后端层的 5 秒等设备等的就是 new_dev。
- logind 实现走 sd-bus（libsystemd 符号 `sd_bus_*`），固定服务名 org.freedesktop.login1；打开设备（TakeDevice）取得可访问 fd，销毁时在互斥锁保护下异步调 Session.ReleaseControl（F-R2-048）。实现文件 logind.c 共 543 行、23 个函数，含 open/close_device、change_vt、pause_device、会话/seat 路径查找等（F-R2-049）。

> ⚠️ 上游差异（D-R1-02）：README 依赖清单列 libseat，但 kywc 会话层不链接 libseat，设备授权直接对接 logind。详见 [01 构建运行](/concepts/01-build-run.md) 的依赖差异块。

## EIS：libeis 虚拟输入后端

src/backend/eis/ 实现基于 libeis（`libeis` 为独立库，Debian 构建依赖 libeis-dev/libei-dev，F-R1-016）的虚拟输入后端，服务于远程桌面/输入捕获，与 portal 的 RemoteDesktop/InputCapture 配套（深入在 [14 安全与 portal](/concepts/14-security-portal.md)）。要点：

- EIS context 有 NORMAL/REMOTE_DESKTOP/INPUT_CAPTURE 三种类型；backend_start 固定创建一个 REMOTE_DESKTOP context（F-R2-050、F-R2-053）。
- D-Bus 上暴露 InputCaptureManager（路径 /com/kylin/Wlcom/EIS/InputCapture），方法 AddInputCapture/RemoveInputCapture；per-context 发 Activated/Deactivated/Disabled 信号（F-R2-051、F-R2-055）。
- 能力位为 POINTER|POINTER_ABSOLUTE|KEYBOARD|SCROLL|BUTTON，不含 touch——源码注释直言 "touch is not support current"（F-R2-054）。
- 输入过滤挂在 backend_handle_event，配合 barrier 命中测试与 lock_filter（F-R2-056）。
- 调试 socket 名取环境变量 **`KYWC_EIS_SOCKET`**（backend.c:93，F-R2-052）。

> ⚠️ 上游差异（D-R1-04）：`KYWC_EIS_SOCKET` 与 `KYWC_XWAYLAND` 在源码有 getenv 消费点，但 docs/ENV.md 未收录。

## libinput 后端：只看线程边界

输入设备后端 src/backend/libinput/ 是 kywc 与主流 wlroots 合成器写法差异最大的地方（洞察 I-3），此处只交代线程边界，完整事件链在 [08 输入](/concepts/08-input.md)：

- 自起一个 libinput 线程，入口 `libinput_thread_func`（src/backend/libinput/backend.c:121，本次回查核实）；线程内 epoll_wait 监听 libinput fd，`libinput_dispatch` 后把事件交给 handle_libinput_event（`libinput_*` 为 libinput 符号）。
- 事件不直接进主循环，而是压入无锁 SPSC 环形队列 input_queue：`INPUT_QUEUE_CAPACITY 64`（src/backend/libinput/input_queue.h:147，本次回查核实），生产者在 events.c:54 `input_queue_push`，消费者在 events.c:361 `input_queue_pop`。
- 跨线程唤醒用 eventfd：线程侧 `eventfd_write(backend->notify_fd, 1)`，并用 atomic exchange 合并高频通知（backend.c:148-152）；主循环侧的回调 `handle_input_batch` 在 backend.c:189 `eventfd_read` 后调 `dispatch_input_events`，在主线程批量出队；另有容量 8 的命令链（LIBINPUT_CMD_QUEUE_CAPACITY）下发 SUSPEND/RESUME/STOP（libinput_p.h:55）。

因此排查输入问题的第一步是判断事件丢失发生在「libinput 线程前 / 容量 64 的队列中 / 主线程分发后」的哪一段；队列满队行为是输入延迟/丢失的第一现场（洞察 I-3 的行动建议）。

## 后端相关环境变量速查

下列变量的 getenv 消费点均在后端层（F-R1-114、F-R1-115），完整环境变量分组见 [01 构建运行](/concepts/01-build-run.md)：

| 变量 | 取值/形态 | 消费点 | 效果 |
|---|---|---|---|
| `KYWC_BACKEND` | 仅精确值 `fbdev` | backend.c:453 | 强制 fbdev；否则先试 DRM、失败自动回退（F-R1-119） |
| `KYWC_DRM_DEVICES` | 冒号分隔卡节点 | backend.c:291、421 | 指定 DRM 设备，第一个为默认渲染设备；设置后不建热插 monitor |
| `KYWC_FB_DEVICES` | 如 /dev/fb0:/dev/fb1 | backend.c:68 | 指定 fbdev 输出节点 |
| `KYWC_DRM_NO_ATOMIC` | `=1` | drm/drm.c:79 | 强制 KMS LEGACY 模式（F-R2-024） |
| `KYWC_DRM_NO_MODIFIERS` | `=1` | drm/drm.c:105 | 禁用 AddFB2 modifiers（F-R2-025） |
| `KYWC_SOFTWARE_COLOR` | `=1` | drm/output.c:441 | 亮度/色温/色彩管理强制走软件通路（F-R2-036） |
| `KYWC_EIS_SOCKET` | socket 名 | eis/backend.c:93 | EIS 调试 socket（ENV.md 缺录，D-R1-04） |

## 后端层文件地图

| 目录 | 角色 | 本篇对应小节 |
|---|---|---|
| src/backend/backend.c | 自动选择决策、multi 组装、GPU 发现 | 后端总览 |
| src/backend/drm/ | KMS 双模、fb、lease、monitor、色彩、多 GPU blit | DRM 后端 |
| src/backend/fbdev/ | shadow framebuffer 软件后端 | fbdev |
| src/backend/session/ | session 接口与唯一 logind 实现 | session/logind |
| src/backend/eis/ | libeis 虚拟输入、D-Bus capture 对象 | EIS |
| src/backend/libinput/ | 独立输入线程与 SPSC 队列 | libinput 边界（完整链见 08） |

## 相关概念

- 前导：[03 启动序列与 server 总体架构](/concepts/03-startup-architecture.md)
- 后继：[05 渲染](/concepts/05-rendering.md) — renderer_autocreate、allocator 与多 GPU blit/timeline
- [07 输出管理](/concepts/07-output-management.md) — new_output 之后的连接器编排、模式与色彩
- [08 输入](/concepts/08-input.md) — libinput 事件在主线程的完整分发链
- [14 安全与 portal](/concepts/14-security-portal.md) — EIS 与 RemoteDesktop/InputCapture 的完整关系
- 信源：[R2 图形事实清单](/references/facts-graphics.md)、[R3 输入事实清单](/references/facts-input-view.md)、[项目文档登记](/references/project-docs.md)
