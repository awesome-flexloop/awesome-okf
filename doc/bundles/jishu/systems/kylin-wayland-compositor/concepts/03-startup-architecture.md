---
type: Concept
title: "启动序列与 server 总体架构"
description: "沿 main.c 函数级启动链读懂 kywc：信号与日志、server_init 各管理器创建顺序、struct server 字段分组、D-Bus 方法与优雅关闭路径"
tags: [wayland, wlroots, startup, architecture, dbus, lifecycle]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r1
    resource: /references/facts-build-startup.md
    title: R1 构建/启动/配置/打包事实清单
  - id: facts-r2
    resource: /references/facts-graphics.md
    title: R2 后端/渲染/场景/输出事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：本篇把 [01](/concepts/01-build-run.md) 装好的 kylin-wlcom 进程从 `main()` 一路带到 wl_display 主循环，是连接「构建运行」与「后端→渲染→场景」主线的枢纽。前置阅读 [02 Wayland 基础](/concepts/02-wayland-wlroots-basics.md)；后端创建一句带过，细节在 [04 后端层](/concepts/04-backends.md)。

## 全局图景：一个文件级静态 server

main.c 持有一个文件级静态 `struct server server`，6 个 options 默认全为 true，`session_pid` 初值 -1（F-R1-037，main.c:25-36）：

```c
// src/main.c:25-35，片段经裁剪
static struct server server = {
    .options = {
        .enable_xwayland = true, .log_to_file = true,
        .log_in_realtime = true,  .log_rate_limit = true,
        .binding_session = true,  .lazy_xwayland = true,
    },
    .session_pid = -1,
};
```

整个进程围绕这一个 server 单例组织：main 负责进程级事务（参数、信号、文件描述符上限、会话子进程），server 负责 Wayland 运行时与各功能 manager。公开 API 只有 6 个函数（F-R1-052，include/server.h:70-83）：`server_init`、`server_start`、`server_run`、`server_finish`、`server_add_destroy_listener`、`server_get_pixman_renderer`。

## main() 函数级启动链

`main(int argc, char *argv[])` 的完整顺序（F-R1-041，src/main.c:184-289）：

1. **本地化**：`setlocale(LC_ALL, "")` 后再把 LC_NUMERIC 钉回 "C"（main.c:186-187），保证配置/日志中的数字格式不受用户语言影响；
2. **NLS**：`HAVE_NLS` 时 `nls_setup_message(TARGET_NAME, locales, ...)`，`.mo` 数据在编译期内嵌、运行期写入 XDG_RUNTIME_DIR 后 bindtextdomain（main.c:189-191，F-R1-120）；
3. **解析参数**：getopt_long 循环，短串 `"hdD:s:vV"`（main.c:196-227），参数细节见 [01](/concepts/01-build-run.md)；
4. **拒绝 SUID**：`detect_suid()` 检测 euid/egid 为 0 且与 uid/gid 不同即打印 "SUID operation is no longer supported, refusing to start." 并退出（F-R1-043，main.c:54-66）；
5. **日志**：默认级别 KYWC_WARN，`-d` 升 DEBUG、`-V` 升 INFO（F-R1-040）；`logger_init(level, "kylin-wlcom.log", ...)` 后设限速 5000ms/10 条（main.c:234-244）；
6. **抬文件句柄上限**：`limit_set_nofile()` 把 RLIMIT_NOFILE 软限抬到硬限（F-R1-050）；
7. **安装 7 个 sigaction**：SIGPIPE 置 IGN，SIGINT 与 SIGSEGV/SIGBUS/SIGILL/SIGFPE/SIGABRT 装 `sig_handler`（main.c:250-258，F-R1-045）；
8. **server_init**：失败走 terminate（main.c:260-263）；
9. **server_start**：建 wayland socket、起后端（main.c:265-268）；
10. **SIGCHLD**：server 就绪后再装 `child_handler`（main.c:271）；
11. **idle 拉起会话**：有 `-s` 会话命令时 `wl_event_loop_add_idle(..., start_session, NULL)`（main.c:273-275）；
12. **server_run**：进入 `wl_display_run` 主循环（main.c:277）；
13. **退出清理**：SIGCHLD 恢复默认，向残留会话进程发 SIGTERM、失败再 SIGKILL，随后 server_finish、logger_finish（main.c:279-289）。

崩溃信号分支会记录 "Caught %s(%u) at address %p"、调用 `debug_backtrace()`（有 libunwind 用 libunwind，否则 glibc backtrace，F-R1-010），再把 SIGABRT 复位默认处置并 abort（F-R1-044）。

### 会话子进程：idle 回调 + wordexp + fork/execvp

会话不是在启动中途同步拉起的，而是作为主循环的第一个 idle 任务（F-R1-048）。`start_session` 调 `spawn_session(server.session_process)`，失败且 binding_session 为真时直接终止合成器（main.c:170-182）。`spawn_session`（src/util/spawn.c:232-278，F-R1-049）的关键动作：

- `wordexp(..., WRDE_NOCMD)` 解析命令行——WRDE_NOCMD 禁用命令替换，避免会话字符串注入 shell；
- 子进程 `setsid()` 独立成会话，先 sigfillset 后 SIG_UNBLOCK，调 `limit_unset_nofile()` 还原句柄上限；
- `execvp(argv[0], argv)`；非 DEBUG 级别下把子进程 stdout/stderr 重定向到 /dev/null。

SIGCHLD 处理器 `child_handler` 只关心 `server.session_pid`，区分 CLD_EXITED/CLD_KILLED/CLD_DUMPED 记日志，回收后置 session_pid=-1；binding_session=true（默认）时会话退出即终止合成器（F-R1-047）。这就是发行版 `kylin-wlcom -s ukui-session`「同生共死」语义的代码来源。

## server_init：18 步创建顺序

`server_init(struct server *server)`（src/server.c:303-352，F-R1-053）严格按序创建运行时：

1. `wl_display_create()`（server.c:305，libwayland-server 符号）；
2. 取 event_loop，并把单个客户端最大 buffer 设为 1 MiB：`wl_display_set_default_max_buffer_size(display, 1024*1024)`（server.c:307）；
3. 初始化 8 个 `wl_signal`：ready/start/terminate/destroy/suspend/hibernate/resume/active（server.c:309-316）；
4. 在 wl 事件循环上注册 SIGHUP/SIGTERM 源，回调 `handle_exit`——注释说明这是为了在多线程环境里把信号同步进主循环（server.c:318-322，F-R1-063）；
5. 初始化 session_active 监听器节点（server.c:324-325）；
6. `dbus_context_create(server)`：D-Bus 上下文（server.c:327）；
7. `server_init_power(server)`：对接 logind 电源管理（见下节）；
8. `queue_create(64, 4, server)`：自研通用工作队列，max_jobs=64、4 个工作线程（server.c:330，注意区别于输入侧容量 64 的 SPSC 队列，见 [04](/concepts/04-backends.md)）；
9. `config_manager_create`、`security_manager_create`、`theme_manager_create`（server.c:332-334）；
10. `wlroots_server_init`：wlroots 核心对象（下节详述，server.c:336）；
11. `output_manager_create`（server.c:340）；
12. `input_manager_create`（server.c:341）；
13. `view_manager_create`（server.c:342）；
14. `xwayland_manager_create`（server.c:343）；
15. `effect_manager_create`（server.c:345）；
16. `plugin_manager_create`（server.c:346）；
17. `ready = true`（server.c:348）；
18. 发射 ready 信号（server.c:349）。

配置管理器对 ready 信号有二次编排：server ready 时再创建 6 个输入/配置管理器——input_action、kde_global_accel、kde_input、ukui_gsettings、ukui_shortcut、ukui_view_mode；后 5 个在对应 HAVE_* 宏关闭时由 config_p.h 提供 inline 空实现（F-R1-071）。这解释了为什么配置/D-Bus 桥接的对象要等 ready 之后才存在。

### wlroots_server_init：后端→渲染器→分配器→compositor→场景

`wlroots_server_init`（src/server.c:236-289，F-R1-054）顺序：

1. `wlr_log_init(WLR_DEBUG, kywc_log_callback)`——把 wlroots 日志枚举映射进 kywc 日志（F-R1-064，`wlr_log_init` 为 wlroots 符号）；
2. `backend_autocreate(display, &session)`：后端自动选择，失败直接致命（server.c:241）；嵌套（无 session）时标记 active=true（server.c:247-254）；
3. `renderer_autocreate(backend, server)` 与 `allocator_create(...)`（server.c:256-262，详见 [05 渲染](/concepts/05-rendering.md)）；
4. `wlr_compositor_create(display, 6, renderer)`、`wlr_subcompositor_create(display)`（server.c:269-270，版本 6 见 [02](/concepts/02-wayland-wlroots-basics.md)）；
5. `renderer_init_wl_display(...)`：shm、single-pixel-buffer、linux-dmabuf、drm_syncobj 等 buffer 协议挂接（server.c:272-273）；
6. `wlr_output_layout_create()` 与自研 `scene_create()`（server.c:275-276，分别见 [07](/concepts/07-output-management.md)/[06 场景](/concepts/06-scene-graph.md)）；
7. 一批全局协议：tearing_control、presentation、viewporter、fractional_scale(v1)、自研 alpha_modifier（server.c:281-286）。

其中第 2 步的 `backend_autocreate` 是 kywc 自有函数（src/backend/backend.c:427），不是 wlroots 的同名函数：嵌套环境直接转发给 wlroots，原生环境组装 multi backend（DRM/fbdev + libinput + session）。它的完整决策树是 [04 后端层](/concepts/04-backends.md) 的主题，证据起点 F-R2-001。

## struct server 字段分组

整个进程的共享状态都挂在 `struct server`（include/server.h:13-68，F-R1-051）：

| 分组 | 代表字段（行号） |
|---|---|
| Wayland 核心 | `wl_display *display`（14）、`wl_event_loop *event_loop`（15）、bool ready/start/terminate/active（16） |
| 选项 | options 内嵌结构 6 个 bool（18-26） |
| 事件 | 8 个 `wl_signal`：ready/start/terminate/destroy/suspend/hibernate/resume/active（28-38） |
| 信号源 | sources.sighup、sources.sigterm（40-44） |
| 会话 | `struct session *session`、session_active 监听器（46-47） |
| wlroots 对象 | renderer、pixman_renderer、allocator、backend、linux_dmabuf_v1、compositor（49-54，均为 wlroots 类型） |
| 场景/输出 | 自研 `struct scene *scene`、`wlr_output_layout *layout`（56-57） |
| 队列 | `struct queue *queue`（59） |
| 会话进程 | session_process 字符串、session_pid（61-62） |
| VT/电源 | `unsigned vtnr`（64）、inhibitor fd、need_inhibit（66-67） |

VT 号从 /sys/class/tty/tty0/active 解析（`sscanf(buf, "tty%u", ...)`，失败置 0，F-R1-062）。

## 电源管理：login1 Inhibit 与 PrepareForSleep

server 内部直接走系统总线对接 org.freedesktop.login1（F-R1-059~061，src/server.c:43-133）：

- 服务/路径/接口为固定的 "org.freedesktop.login1"、"/org/freedesktop/login1"、"org.freedesktop.login1.Manager"；
- `server_create_inhibitor` 调 Inhibit("sleep", TARGET_NAME, "Power off outputs when hibernate", "delay")，拿到的 fd 用 F_DUPFD_CLOEXEC 复制到最小 fd 3；
- 初始化时先 Introspect，仅当 XML 中含 PrepareForSuspend/PrepareForHibernate 字符串才置 need_inhibit；PrepareForSleep 无条件 match，另两个按需 match（F-R1-060）；
- 三个总线信号处理器分别把系统状态转成 server 的 suspend/hibernate/resume `wl_signal`，下行挂起时释放 inhibitor（F-R1-061）。输出管理器据此关闭/恢复输出（见 [07](/concepts/07-output-management.md)）。

## com.kylin.Wlcom：5 个无特权 D-Bus 方法

src/config/common.c 在会话总线上注册对象 /com/kylin/Wlcom、接口 com.kylin.Wlcom，vtable 含 5 个全部标 `SD_BUS_VTABLE_UNPRIVILEGED` 的方法（F-R1-075）：

| 方法 | 签名 | 行为 |
|---|---|---|
| SetLogLevel | "u" | 范围校验后 `logger_set_level`；越界返回固定文案 "Invalid args, please input [0-5]."（F-R1-076） |
| SetLogRateLimit | "uu" | 运行时调整日志限速 |
| PrintConfig | →"s" | 打印当前配置 |
| TrimMemory | "b" | 开/关 5 秒周期定时器，回调 `malloc_trim(4096)`（F-R1-077） |
| LogScene | "u" | 以给定 depth 调 `scene_node_log` 打印场景树（F-R1-078） |

这是运行时观察/干预合成器的轻量控制面，与 [01](/concepts/01-build-run.md) 的 `KYWC_LOG_LEVEL` 环境变量互补。

## manager 分层与关闭路径

kywc 的功能子系统统一采用 `xxx_manager_create(server)` + `wl_signal`/`wl_listener` 接线的模式：manager 在 server_init 中按「先基础设施（config/security/theme）、再 wlroots 核心、后业务（output/input/view/xwayland/effect/plugin）」的顺序创建，彼此通过 server 信号与场景树解耦。

关闭有两套并存的信号入口（F-R1-063）：main.c 的 sigaction（SIGINT 等）与 server.c 的 wl_event_loop 信号源（SIGHUP/SIGTERM），二者都汇到同一个终止策略——`terminate()`：ready 前直接 `exit()`，ready 后调 `wl_display_terminate` 走优雅退出（F-R1-046）。

`server_run` 只打一行 "Running wayland compositor on wayland display '%s'" 就进入 `wl_display_run`（F-R1-056）。循环退出后 `server_finish`（src/server.c:387-432，F-R1-057）逆序拆除：置 terminate、把 wlr 日志换成空回调静默、移除信号源、发 terminate 信号、`queue_destroy`、`wl_display_destroy_clients`、销毁 xwayland manager、`wl_display_destroy`、发 destroy 信号，并断言 8 个信号监听器链表全部为空，最后销毁场景/布局/分配器/渲染器。destroy 监听器用头插法实现「后进先出」（F-R1-058），保证后注册的 manager 先拆除。

## 相关概念

- 前导：[02 Wayland 与 wlroots 基础](/concepts/02-wayland-wlroots-basics.md)
- 后继：[04 后端层](/concepts/04-backends.md) — wlroots_server_init 第 2 步 backend_autocreate 的完整决策
- [05 渲染](/concepts/05-rendering.md) — renderer_autocreate 与 allocator_create
- [06 场景树](/concepts/06-scene-graph.md)、[07 输出管理](/concepts/07-output-management.md) — scene/layout 及电源信号的消费方
- 信源：[R1 事实清单](/references/facts-build-startup.md)、[R2 图形事实清单](/references/facts-graphics.md)、[源码信源登记](/references/source-code-map.md)
