---
type: Reference
title: OOM 分数调整信源
description: src/oom.c OOM自我保护机制源码信源——oom_score_adj读写、attempt_oom_adjust与reset_oom_adjust完整API
tags: [reference, oom, oom-score-adj, procfs, self-protection, linux]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: conmon-oom
    title: src/oom.c
    path: external/dao/action/Containers/conmon/src/oom.c
  - id: conmon-oom-h
    title: src/oom.h
    path: external/dao/action/Containers/conmon/src/oom.h
---

# OOM 分数调整信源

> 信源文件：oom.c、oom.h

本文档记录 conmon 的 OOM（Out of Memory）自我保护机制，通过调整 `/proc/self/oom_score_adj` 确保监控进程自身不会在内存压力下被 OOM killer 优先杀死。

---

## 全局变量

```c
int old_oom_score = 0;
```

`old_oom_score` 保存调整前的原始 oom_score_adj 值，用于在容器子进程 exec 前恢复。

---

## write_oom_adjust()

**功能**：底层函数，读写 `/proc/self/oom_score_adj` 文件。

```c
static void write_oom_adjust(int oom_score, int *old_value)
{
#ifdef __linux__
    char fmt_oom_score[16];
    int oom_score_fd = open("/proc/self/oom_score_adj", O_RDWR | O_CLOEXEC);
    if (oom_score_fd < 0) {
        ndebugf("failed to open /proc/self/oom_score_adj: %m");
        return;
    }
    if (old_value) {
        ssize_t nread = read(oom_score_fd, fmt_oom_score, sizeof(fmt_oom_score) - 1);
        if (nread < 0) {
            ndebugf("failed to read from /proc/self/oom_score_adj: %m");
            nread = 0;
        }
        fmt_oom_score[nread] = '\0';
        *old_value = atoi(fmt_oom_score);
    }
    snprintf(fmt_oom_score, sizeof(fmt_oom_score), "%d", oom_score);
    if (write(oom_score_fd, fmt_oom_score, strlen(fmt_oom_score)) < 0) {
        ndebugf("failed to write to /proc/self/oom_score_adj: %m");
    }
    close(oom_score_fd);
#else
    (void)oom_score;
    (void)old_value;
#endif
}
```

**参数**：
- `oom_score`：要设置的 oom_score_adj 值
- `old_value`：输出参数，若非 NULL 则读取并保存原始值

**执行流程**：
1. 以读写模式打开 `/proc/self/oom_score_adj`（带 `O_CLOEXEC`）
2. 若 `old_value` 非 NULL：先读取当前值并解析为整数保存
3. 将新的 oom_score 格式化为字符串写入
4. 关闭文件描述符

**非 Linux 平台**：函数为空操作，所有参数转为 `(void)` 避免未使用警告。

---

## attempt_oom_adjust()

**功能**：设置 conmon 自身的 oom_score_adj，保存旧值。

```c
void attempt_oom_adjust(int oom_score)
{
    write_oom_adjust(oom_score, &old_oom_score);
}
```

**调用时机**：main 函数早期（`src/conmon.c#L57`），在 fork 容器进程之前调用。

**参数值**：传入 `-1000`（`src/conmon.c#L57`：`attempt_oom_adjust(-1000)`）

**oom_score_adj 取值范围**：-1000 到 1000
- **-1000**：特殊值，表示进程完全免疫 OOM killer（`OOM_SCORE_ADJ_MIN`）
- **负值**：降低被 OOM killer 选中的概率
- **0**：默认值，不调整
- **正值**：增加被 OOM killer 选中的概率

**设计意图**：
- conmon 作为容器监控进程，必须比容器进程存活更久
- 如果 conmon 先被 OOM killer 杀死，容器进程会变成孤儿进程，无法被正确回收
- 设置为 -1000 确保 conmon 是系统中最后被杀死的进程之一

---

## reset_oom_adjust()

**功能**：恢复 oom_score_adj 到原始值。

```c
void reset_oom_adjust()
{
    write_oom_adjust(old_oom_score, NULL);
}
```

**调用时机**：容器子进程（中间进程）中，execv 运行时之前（`src/conmon.c#L284`：`reset_oom_adjust()`）。

**为什么需要 reset**：
1. fork 创建的子进程会继承父进程的 oom_score_adj
2. 如果不 reset，容器内的所有进程都会继承 -1000 的免疫设置
3. 这会导致容器内进程无法被 OOM killer 杀死，可能耗尽系统内存
4. 在 execv 之前恢复为原始值（通常是 0），确保容器进程有正常的 OOM 优先级

---

## 完整调用时序

```
conmon main 进程启动
    │
    ├─ attempt_oom_adjust(-1000)
    │   └─ write_oom_adjust(-1000, &old_oom_score)
    │       ├─ 读取当前 oom_score_adj → 保存到 old_oom_score（通常为0）
    │       └─ 写入 -1000 → conmon 免疫 OOM
    │
    ├─ [双fork守护进程化...]
    ├─ [setsid, set_subreaper...]
    │
    └─ fork() → 创建中间子进程（create_pid）
        │
        └─ 中间子进程（容器运行时父进程）
            ├─ set_pdeathsig(SIGKILL)
            ├─ [dup2 标准流...]
            ├─ reset_oom_adjust()
            │   └─ write_oom_adjust(old_oom_score, NULL)
            │       └─ 写入 old_oom_score（0）→ 恢复正常OOM优先级
            └─ execv(runc/crun) → OCI运行时
                │
                └─ 容器内进程（继承正常OOM优先级，可被OOM杀死）
```

---

## OOM 保护机制的关键设计点

### 1. 自我保护优先

conmon 作为监控者必须存活到最后，否则：
- 容器输出日志无法被记录
- 容器退出状态无法被传递给 Podman/CRI-O
- 容器进程变成孤儿，无法被正确回收
- attach socket 失效，用户无法附加到容器

### 2. 子进程不继承保护

免疫属性只属于 conmon 自身，容器进程必须可以被 OOM killer 正常杀死：
- 这是内存资源管理的基本要求
- 容器内存超限时应当被杀死，而非 conmon 被杀
- `reset_oom_adjust()` 在 exec 前调用，确保 runc 和容器进程恢复正常优先级

### 3. 非 Linux 兼容性

通过 `#ifdef __linux__` 条件编译，在非 Linux 平台（如 Windows/macOS）上这些函数为空操作，不影响编译和基本运行（虽然 conmon 主要设计为 Linux 容器运行时组件）。

### 4. 错误容忍

`write_oom_adjust()` 中打开或写入 `/proc` 文件失败时只记录 debug 日志，不调用 `pexit()` 致命退出：
- 某些容器环境或特殊内核配置可能不允许修改 oom_score_adj
- OOM 保护是增强可靠性的特性，但不是功能正确性的必要条件
- 即使设置失败，conmon 仍然可以正常工作，只是在极端内存压力下生存概率降低
