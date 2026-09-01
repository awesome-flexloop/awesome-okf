---
type: Reference
title: cgroup 与 OOM 检测信源
description: src/cgroup.c cgroup管理与OOM检测源码信源——cgroup v1/v2版本判断、OOM事件监听、memory.events解析完整API
tags: [reference, cgroup, oom, cgroup-v1, cgroup-v2, inotify, eventfd, memory-events]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: conmon-cgroup
    title: src/cgroup.c
    path: external/dao/action/Containers/conmon/src/cgroup.c
  - id: conmon-cgroup-h
    title: src/cgroup.h
    path: external/dao/action/Containers/conmon/src/cgroup.h
---

# cgroup 与 OOM 检测信源

> 信源文件：cgroup.c、cgroup.h

本文档记录 conmon 中 cgroup 管理与 OOM（Out of Memory）检测的完整实现，包括 cgroup v1 和 v2 双版本支持。

---

## 关键宏定义与全局变量

```c
#define CGROUP2_SUPER_MAGIC 0x63677270
#define CGROUP_ROOT "/sys/fs/cgroup"

int oom_event_fd = -1;
int oom_cgroup_fd = -1;
```

- `CGROUP2_SUPER_MAGIC`：cgroup v2 文件系统魔法数，用于 `statfs` 判断版本
- `CGROUP_ROOT`：cgroup 根目录路径
- `oom_event_fd`：cgroup v1 OOM 事件 eventfd
- `oom_cgroup_fd`：cgroup v1 memory.oom_control 文件 fd

---

## setup_oom_handling(int pid)

**功能**：根据系统 cgroup 版本设置 OOM 处理。

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

**逻辑**：
1. 通过 `statfs("/sys/fs/cgroup")` 获取文件系统信息
2. 若 `f_type == CGROUP2_SUPER_MAGIC`（0x63677270），判定为 cgroup v2
3. 根据版本调用对应的设置函数

---

## process_cgroup_subsystem_path()

**功能**：解析 `/proc/<pid>/cgroup` 文件，获取指定子系统的 cgroup 路径。

```c
static char *process_cgroup_subsystem_path(int pid, bool cgroup2, const char *subsystem);
```

**参数**：
- `pid`：目标进程 PID
- `cgroup2`：是否为 cgroup v2
- `subsystem`：子系统名称（v1 使用，如 "memory"）

**cgroup v2 逻辑**：
- 查找格式为 `0::/path/to/cgroup` 的统一层级条目（hierarchy ID 为 0）
- 跳过 v1 控制器条目（如 `1:net_cls:/`）
- 返回路径：`/sys/fs/cgroup` + 解析出的 cgroup 路径（去除末尾换行）

**cgroup v1 逻辑**：
- 按冒号分割每行：`hierarchy-id:controller-list:cgroup-path`
- 分割 controller-list 为子系统数组
- 匹配指定 subsystem
- 返回路径：`/sys/fs/cgroup/<controller>/<cgroup-path>`

---

## setup_oom_handling_cgroup_v2(int pid)

**功能**：设置 cgroup v2 的 OOM 检测，使用 inotify 监控 `memory.events` 文件。

```c
static void setup_oom_handling_cgroup_v2(int pid)
{
    cgroup2_path = process_cgroup_subsystem_path(pid, true, "");
    // ...
    char *memory_events_file_path = g_build_filename(cgroup2_path, "memory.events", NULL);

    int ifd = inotify_init();
    inotify_add_watch(ifd, memory_events_file_path, IN_MODIFY);

    inotify_fd = ifd;
    g_unix_fd_add(inotify_fd, G_IO_IN, oom_cb_cgroup_v2, NULL);
}
```

**实现机制**：
1. 获取容器进程的 cgroup v2 路径
2. 构造 `memory.events` 文件路径（cgroup v2 内存事件统计文件）
3. 调用 `inotify_init()` 创建 inotify 实例
4. 调用 `inotify_add_watch()` 监控 `memory.events` 的 `IN_MODIFY` 事件
5. 将 inotify fd 注册到 GLib 主循环，回调为 `oom_cb_cgroup_v2`

> **注意**：inotify 只通知文件修改事件，实际 OOM 判断需要在回调中解析文件内容比较计数器。

---

## setup_oom_handling_cgroup_v1(int pid)

**功能**：设置 cgroup v1 的 OOM 检测，使用 eventfd + cgroup.event_control。

```c
static void setup_oom_handling_cgroup_v1(int pid)
{
    char *memory_cgroup_path = process_cgroup_subsystem_path(pid, false, "memory");
    char *memory_cgroup_file_path = g_build_filename(memory_cgroup_path, "cgroup.event_control", NULL);
    int cfd = open(memory_cgroup_file_path, O_WRONLY | O_CLOEXEC);

    char *memory_cgroup_file_oom_path = g_build_filename(memory_cgroup_path, "memory.oom_control", NULL);
    oom_cgroup_fd = open(memory_cgroup_file_oom_path, O_RDONLY | O_CLOEXEC);

    oom_event_fd = eventfd(0, EFD_CLOEXEC);

    char *data = g_strdup_printf("%d %d", oom_event_fd, oom_cgroup_fd);
    write_all(cfd, data, strlen(data));

    g_unix_fd_add(oom_event_fd, G_IO_IN, oom_cb_cgroup_v1, memory_cgroup_file_path);
}
```

**实现机制**：
1. 获取 memory 子系统 cgroup 路径
2. 打开 `cgroup.event_control`（写）用于注册事件
3. 打开 `memory.oom_control`（读）作为 OOM 事件源
4. 创建 `eventfd(0, EFD_CLOEXEC)` 作为事件通知 fd
5. 向 `cgroup.event_control` 写入 `<event_fd> <oom_control_fd>` 格式字符串注册
6. 将 eventfd 注册到 GLib 主循环，回调为 `oom_cb_cgroup_v1`

> **历史背景**：cgroup v1 的 event_control 接口在 PREEMPT_RT 内核配置中被禁用，因此 write 失败时仅警告不致命。

---

## oom_cb_cgroup_v2()

**功能**：cgroup v2 OOM 事件回调，inotify 触发时调用。

```c
static gboolean oom_cb_cgroup_v2(int fd, GIOCondition condition, gpointer user_data)
{
    char events[sizeof(struct inotify_event) + NAME_MAX + 1];
    ssize_t num_read = read(fd, &events, events_size);
    // 丢弃 inotify 事件

    if ((condition & G_IO_IN) != 0) {
        ret = check_cgroup2_oom();
    }

    if (ret == G_SOURCE_REMOVE) {
        close(fd);
        inotify_fd = -1;
    }
    return ret;
}
```

**逻辑**：
1. 读取并丢弃 inotify 事件（只需要知道有修改发生）
2. 调用 `check_cgroup2_oom()` 解析 `memory.events` 并判断是否发生 OOM
3. 根据返回值决定是否继续监听：`G_SOURCE_REMOVE` 表示停止监听，`G_SOURCE_CONTINUE` 表示继续

---

## oom_cb_cgroup_v1()

**功能**：cgroup v1 OOM 事件回调，eventfd 触发时调用。

```c
static gboolean oom_cb_cgroup_v1(int fd, GIOCondition condition, gpointer user_data)
{
    char *cgroup_event_control_path = (char *)user_data;

    // 检查 cgroup 是否已被移除
    gboolean cgroup_removed = (access(cgroup_event_control_path, F_OK) < 0);

    uint64_t event_count;
    ssize_t num_read = read(fd, &event_count, sizeof(uint64_t));

    // event_count == 1 && cgroup_removed: 只是 cgroup 移除，非 OOM
    if (event_count == 1 && cgroup_removed)
        return G_SOURCE_CONTINUE;

    // 其他情况（event_count > 1 或 !cgroup_removed）：OOM 发生
    ninfo("OOM event received");
    create_oom_files();

    return G_SOURCE_CONTINUE;
}
```

**三种事件情况处理**：
1. **OOM kill 发生**（1 个事件）：`event_count=1`，`cgroup_removed=FALSE`
2. **cgroup 被移除**（1 个事件）：`event_count=1`，`cgroup_removed=TRUE` → 非 OOM，忽略
3. **OOM kill 后 cgroup 被移除**（2 个事件）：`event_count=2` → 判定为 OOM

---

## check_cgroup2_oom()

**功能**：解析 cgroup v2 的 `memory.events` 文件，检测 OOM 事件是否发生。

```c
gboolean check_cgroup2_oom()
{
    static long int last_oom_counter = 0;
    static long int last_oom_kill_counter = 0;

    char *memory_events_file_path = g_build_filename(cgroup2_path, "memory.events", NULL);
    FILE *fp = fopen(memory_events_file_path, "re");

    gboolean oom_detected = FALSE;
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

        long int *last_counter = is_oom_kill ? &last_oom_kill_counter : &last_oom_counter;
        if (counter != *last_counter) {
            if (create_oom_files() == 0) {
                *last_counter = counter;
                oom_detected = TRUE;
            }
        }
    }
    return oom_detected ? G_SOURCE_CONTINUE : G_SOURCE_REMOVE;
}
```

**memory.events 文件格式**：
```
low 0
high 0
max 0
oom 1
oom_kill 1
oom_group_kill 0
```

**检测逻辑**：
1. 使用两个静态变量 `last_oom_counter` 和 `last_oom_kill_counter` 记录上次值
2. 逐行解析，识别 `oom ` 和 `oom_kill ` 两个键
3. 比较当前计数器与上次值：若计数器增长，说明发生了新的 OOM 事件
4. 调用 `create_oom_files()` 创建 OOM 标记文件

> **关键设计**：cgroup v2 没有像 v1 那样的 eventfd 即时通知机制，而是在文件修改时通过比较计数器差值来判断 OOM。主循环退出后也会调用此函数做最终检查，避免漏掉退出前瞬间发生的 OOM。

---

## create_oom_files() / create_oom_file()

**功能**：创建 OOM 事件标记文件，通知上层管理程序发生了 OOM。

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
1. `opt_persist_path/oom`：容器持久化目录
2. `opt_bundle_path/oom`：bundle 目录

管理程序（Podman/CRI-O）可以通过检查这两个位置是否存在名为 "oom" 的文件来判断容器是否因 OOM 被杀死。

---

## cgroup v1 vs v2 OOM 检测对比

| 特性 | cgroup v1 | cgroup v2 |
|------|-----------|-----------|
| **事件通知机制** | eventfd + cgroup.event_control | inotify 监控 memory.events IN_MODIFY |
| **事件判定方式** | eventfd 计数 + cgroup 存在性检查 | 解析 memory.events 比较 oom/oom_kill 计数器 |
| **事件文件** | memory.oom_control | memory.events |
| **OOM 标记文件** | 同（persist_path/bundle_path 下的 "oom"） | 同 |
| **注册复杂度** | 需要写入 event_control 注册 | 只需 inotify_add_watch |
| **PREEMPT_RT 兼容** | event_control 可能被禁用 | 兼容（不依赖 event_control） |
| **主循环退出后检查** | 不需要（事件即时通知） | 需要调用 check_cgroup2_oom() 最终检查 |
