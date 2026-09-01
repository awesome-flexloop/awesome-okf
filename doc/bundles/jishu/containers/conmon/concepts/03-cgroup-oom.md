---
type: Concept
title: cgroup 与 OOM 检测
description: conmon中cgroup v1与v2双版本OOM检测实现对比——eventfd vs inotify机制、memory.events解析、oom标记文件完整解析
tags: [concept, cgroup, oom, cgroup-v1, cgroup-v2, inotify, eventfd, memory-events, out-of-memory, linux-kernel]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: cgroup-source
    resource: /bundles/containers/conmon/references/cgroup-source.md
    title: cgroup 与 OOM 检测信源
  - id: oom-source
    resource: /bundles/containers/conmon/references/oom-source.md
    title: OOM 分数调整信源
---

# cgroup 与 OOM 检测

OOM（Out of Memory，内存不足）检测是容器监控的关键功能。当容器内进程消耗内存超过 cgroup 限制时，Linux 内核的 OOM killer 会杀死容器内进程，conmon 需要可靠地检测到这一事件并通知上层管理程序（Podman/CRI-O）。

conmon 同时支持 **cgroup v1** 和 **cgroup v2** 两种版本的 OOM 检测，两种版本使用完全不同的机制。

## OOM 检测的两层机制

conmon 有两个独立但相关的 OOM 机制：

| 机制 | 作用 | 位置 |
|------|------|------|
| **OOM 分数自我保护** | conmon 自身设置 oom_score_adj=-1000 免疫 OOM，容器 exec 前恢复 | oom.c |
| **cgroup OOM 事件检测** | 监听容器 cgroup 的 OOM 事件，创建 oom 标记文件 | cgroup.c |

本文重点讨论 cgroup OOM 事件检测机制。

## cgroup 版本判断

conmon 启动时通过 `statfs` 判断系统使用的 cgroup 版本：

```c
void setup_oom_handling(int pid)
{
    struct statfs sfs;
    if (statfs("/sys/fs/cgroup", &sfs) == 0 && sfs.f_type == CGROUP2_SUPER_MAGIC) {
        is_cgroup_v2 = TRUE;
        setup_oom_handling_cgroup_v2(pid);
        return;
    }
    setup_oom_handling_cgroup_v1(pid);
}
```

- **cgroup v2 魔法数**：`0x63677270`（`CGROUP2_SUPER_MAGIC`）
- **判断依据**：`/sys/fs/cgroup` 挂载点的文件系统类型
- **全局标志**：`is_cgroup_v2 = TRUE` 标记版本，供后续 `check_cgroup2_oom()` 使用

### 获取容器 cgroup 路径

无论是 v1 还是 v2，首先需要从 `/proc/<pid>/cgroup` 解析容器的 cgroup 路径：

```c
static char *process_cgroup_subsystem_path(int pid, bool cgroup2, const char *subsystem);
```

**cgroup v2 解析逻辑**：
- 查找以 `0::` 开头的行（hierarchy ID 为 0 表示统一层级）
- 跳过 v1 控制器行（混合挂载系统可能同时有 v1 和 v2 条目）
- 返回路径：`/sys/fs/cgroup` + cgroup 路径

**cgroup v1 解析逻辑**：
- 按冒号分割：`hierarchy-id:controller1,controller2:/path/to/cgroup`
- 查找匹配指定 subsystem（如 "memory"）的行
- 返回路径：`/sys/fs/cgroup/<controller>/<path>`

---

## cgroup v1 OOM 检测：eventfd 机制

cgroup v1 使用 **eventfd + cgroup.event_control** 的内核通知机制。

### 工作流程

```
conmon 主循环
    │
    ├─ 打开 memory.cgroup.event_control（写）
    ├─ 打开 memory.oom_control（读）
    ├─ 创建 eventfd(0, EFD_CLOEXEC)
    ├─ 向 cgroup.event_control 写入 "<eventfd> <oom_control_fd>"
    └─ 将 eventfd 注册到 GMainLoop → oom_cb_cgroup_v1
        │
        ▼
    内核 OOM 发生
        │
        └─ eventfd 变为可读 → 触发回调
            │
            ├─ 读取 eventfd 计数
            ├─ 检查 cgroup 是否被移除（非 OOM）
            └─ 判定为 OOM → create_oom_files()
```

### 关键实现

```c
static void setup_oom_handling_cgroup_v1(int pid)
{
    char *memory_cgroup_path = process_cgroup_subsystem_path(pid, false, "memory");
    
    // 1. 打开 cgroup.event_control 用于注册
    int cfd = open("<path>/cgroup.event_control", O_WRONLY | O_CLOEXEC);
    
    // 2. 打开 memory.oom_control 作为事件源
    oom_cgroup_fd = open("<path>/memory.oom_control", O_RDONLY | O_CLOEXEC);
    
    // 3. 创建 eventfd
    oom_event_fd = eventfd(0, EFD_CLOEXEC);
    
    // 4. 注册：向 event_control 写入 "<event_fd> <oom_control_fd>"
    char *data = g_strdup_printf("%d %d", oom_event_fd, oom_cgroup_fd);
    write_all(cfd, data, strlen(data));
    
    // 5. 注册到 GLib 主循环
    g_unix_fd_add(oom_event_fd, G_IO_IN, oom_cb_cgroup_v1, memory_cgroup_file_path);
}
```

### 事件判定逻辑

`oom_cb_cgroup_v1` 需要区分两种事件：

1. **OOM kill 事件**：容器内存超限，内核杀死进程
2. **cgroup 移除事件**：容器退出后 cgroup 被清理

```c
// 检查 cgroup.event_control 是否存在（cgroup 被移除会删除该文件）
gboolean cgroup_removed = (access(cgroup_event_control_path, F_OK) < 0);

uint64_t event_count;
read(fd, &event_count, sizeof(uint64_t));

// 三种情况：
// 1. event_count=1 且 cgroup_removed → 只是 cgroup 移除，非 OOM
// 2. event_count=1 且 !cgroup_removed → OOM kill
// 3. event_count>1 → OOM kill + cgroup 移除
if (event_count == 1 && cgroup_removed)
    return G_SOURCE_CONTINUE;  // 非 OOM，继续监听

// 其他情况都是 OOM
create_oom_files();
```

> **注意**：cgroup v1 的 event_control 接口在 **PREEMPT_RT 实时内核**中被禁用（[内核提交 2343e88d](https://github.com/torvalds/linux/commit/2343e88d238f5de973d609d861c505890f94f22e)），因此 write 失败时只警告不致命退出。

---

## cgroup v2 OOM 检测：inotify + 轮询机制

cgroup v2 移除了 cgroup.event_control 接口，改用**inotify 监控文件修改 + 解析计数器**的方式。这是两种版本最大的差异——v2 没有内核级的即时事件通知。

### 工作流程

```
conmon 主循环
    │
    ├─ 获取容器 cgroup v2 路径
    ├─ 创建 inotify_init()
    ├─ inotify_add_watch(..., "memory.events", IN_MODIFY)
    └─ 将 inotify fd 注册到 GMainLoop → oom_cb_cgroup_v2
        │
        ▼
    容器内发生 OOM 或其他内存事件
        │
        └─ memory.events 文件被修改 → inotify 通知
            │
            ├─ 读取并丢弃 inotify 事件
            └─ 调用 check_cgroup2_oom()
                │
                ├─ 打开 memory.events 文件
                ├─ 逐行解析 oom 和 oom_kill 计数器
                ├─ 与 last_oom_counter/last_oom_kill_counter 比较
                └─ 计数器增长 → OOM 发生 → create_oom_files()
```

### memory.events 文件格式

cgroup v2 的 `memory.events` 文件是一个简单的键值对文件：

```
low 0
high 0
max 0
oom 1
oom_kill 1
oom_group_kill 0
```

**关键字段**：
- `oom`：cgroup 中发生 OOM 的次数（次数）
- `oom_kill`：OOM killer 实际杀死进程的次数
- 计数器是**单调递增**的，只增不减

### 关键实现

#### 注册 inotify 监听

```c
static void setup_oom_handling_cgroup_v2(int pid)
{
    cgroup2_path = process_cgroup_subsystem_path(pid, true, "");
    char *memory_events_file_path = g_build_filename(cgroup2_path, "memory.events", NULL);
    
    int ifd = inotify_init();
    inotify_add_watch(ifd, memory_events_file_path, IN_MODIFY);
    
    inotify_fd = ifd;
    g_unix_fd_add(inotify_fd, G_IO_IN, oom_cb_cgroup_v2, NULL);
}
```

#### 计数器差值检测

`check_cgroup2_oom()` 使用两个**静态变量**保存上次读取的计数器值：

```c
gboolean check_cgroup2_oom()
{
    static long int last_oom_counter = 0;
    static long int last_oom_kill_counter = 0;
    
    FILE *fp = fopen(memory_events_file_path, "re");
    
    while ((read = getline(&line, &len, fp)) != -1) {
        // 匹配 "oom " 或 "oom_kill " 前缀
        if (memcmp(line, "oom_kill ", 9) == 0) {
            prefix_len = 9;
            is_oom_kill = TRUE;
        } else if (memcmp(line, "oom ", 4) == 0) {
            prefix_len = 4;
            is_oom_kill = FALSE;
        } else {
            continue;
        }
        
        counter = strtol(&line[prefix_len], &endptr, 10);
        if (counter == 0)
            continue;
        
        // 比较当前计数器与上次值
        long int *last_counter = is_oom_kill ? &last_oom_kill_counter : &last_oom_counter;
        if (counter != *last_counter) {
            // 计数器增长 → 发生了新的 OOM 事件
            create_oom_files();
            *last_counter = counter;
            oom_detected = TRUE;
        }
    }
    return oom_detected ? G_SOURCE_CONTINUE : G_SOURCE_REMOVE;
}
```

### 为什么 v2 需要主循环退出后最终检查？

主循环退出后，conmon 还会调用一次 `check_cgroup2_oom()`：

```c
#ifdef __linux__
check_cgroup2_oom();
#endif
```

**原因**：inotify 通知和实际计数器更新之间可能存在竞态条件：
1. 容器退出前瞬间发生 OOM
2. 容器退出导致主循环退出（container_exit_cb 调用 g_main_loop_quit）
3. inotify 事件可能还没被处理，或者 memory.events 还没被更新
4. 主循环退出后最终检查一次，确保不遗漏 OOM 事件

这是 v1 不需要的额外步骤——v1 的 eventfd 是同步通知，事件触发时 OOM 已经发生。

---

## cgroup v1 vs v2 OOM 检测对比

| 特性 | cgroup v1 | cgroup v2 |
|------|-----------|-----------|
| **通知机制** | 内核主动通知（eventfd） | 文件修改通知（inotify）+ 用户态轮询解析 |
| **核心系统调用** | `eventfd()` + `write(cgroup.event_control)` | `inotify_init()` + `inotify_add_watch(IN_MODIFY)` |
| **事件文件** | `memory.oom_control` + `cgroup.event_control` | `memory.events` |
| **事件判定** | eventfd 计数 + cgroup 存在性检查 | 比较 `oom`/`oom_kill` 计数器差值 |
| **即时性** | 高（内核直接通知） | 中（inotify 通知后需解析文件） |
| **主循环退出后检查** | 不需要 | 需要 `check_cgroup2_oom()` 兜底 |
| **PREEMPT_RT 兼容** | 不兼容（event_control 可能被禁用） | 兼容 |
| **计数器状态** | 无（事件驱动，每次都是新事件） | 静态变量保存上次值 `last_oom_counter` |
| **OOM 标记位置** | 相同（persist_path/oom + bundle_path/oom） | 相同 |

---

## OOM 标记文件

无论 v1 还是 v2，检测到 OOM 后都调用 `create_oom_files()` 在两个位置创建名为 `oom` 的空文件：

```c
static int create_oom_files()
{
    ninfo("OOM received");
    int r = 0;
    r |= create_oom_file(opt_persist_path);
    r |= create_oom_file(opt_bundle_path);
    return r;
}

static int create_oom_file(const char *base_path)
{
    if (base_path == NULL || base_path[0] == '\0')
        return 0;
    char *ctr_oom_file_path = g_build_filename(base_path, "oom", NULL);
    int ctr_oom_fd = open(ctr_oom_file_path, O_CREAT | O_CLOEXEC, 0666);
    // ...
}
```

**创建位置**：
1. `<opt_persist_path>/oom`：容器持久化目录（通常是 `/var/lib/containers/storage/overlay-containers/<cid>/userdata/`）
2. `<opt_bundle_path>/oom`：OCI bundle 目录

**上层使用方式**：
- Podman/CRI-O 在容器退出后检查这些文件是否存在
- 存在则将容器退出原因标记为 OOM Killed
- 用户通过 `podman inspect` 可以看到 `OOMKilled: true`

---

## OOM 分数调整：自我保护机制

除了检测容器的 OOM 事件，conmon 还通过调整自身的 `oom_score_adj` 来确保自己比容器更晚被杀死：

```c
// main 函数早期：conmon 自身设为 -1000（完全免疫）
attempt_oom_adjust(-1000);

// fork 后的容器子进程中 exec 前：恢复为正常值（通常 0）
reset_oom_adjust();
```

**oom_score_adj 取值范围**：-1000 到 1000
- **-1000**（`OOM_SCORE_ADJ_MIN`）：进程完全免疫 OOM killer
- **值越小**：越不容易被选中杀死
- **值越大**：越容易被选中杀死

**为什么需要这样设计？**

| 场景 | 如果 conmon 不自我保护 | conmon 自我保护 |
|------|---------------------|----------------|
| 系统内存严重不足 | OOM killer 可能选中 conmon 杀死 | conmon 存活 |
| conmon 被杀后果 | 容器变成孤儿，无法回收；日志丢失；退出状态丢失 | 容器被杀死后 conmon 记录 OOM 事件、写入退出码、清理资源 |
| 容器内进程 | 继承 -1000，无法被 OOM 杀死 → 系统挂死 | reset 后正常 OOM 优先级，内存超限时被杀 |

这是监控程序的经典设计模式：**监控者必须比被监控者存活更久**。

---

## 相关概念

- [进程生命周期管理](01-process-lifecycle.md) — set_pdeathsig 如何与 OOM 保护配合
- [事件循环与信号处理](02-event-loop.md) — inotify/eventfd 如何集成到 GMainLoop
- [conmon定位与架构概览](00-introduction.md) — cgroup OOM 检测在 conmon 职责中的位置
