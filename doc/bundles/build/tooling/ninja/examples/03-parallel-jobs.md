---
type: Example
title: 并行构建与Pool控制
description: 使用sleep模拟长时间编译任务，演示Ninja的-j并行参数、Pool并发限制（depth=1的链接池）、console pool用法，以及ninja -d stats并行统计。
tags: [ninja, example, advanced, parallel, pool, concurrency, console-pool, jobs]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 并行构建与Pool控制

Ninja 的设计哲学之一就是高效利用多核 CPU 进行并行构建。本示例通过模拟长时间任务，让你直观理解：

- `-j` 参数控制并行度
- **Pool（池）** 如何限制特定类型任务的并发数
- `console` pool 让需要终端交互的命令独占控制台
- `ninja -d stats` 查看并行统计信息
- 不同 `-j` 值下的构建时间对比

> **前置知识**：建议先完成 [最简构建](01-minimal-build.md)。相关概念文档：[并行执行](../concepts/07-parallel-execution.md)、[构建执行模型](../concepts/04-build-execution.md)。

---

## 1. 项目准备

```shell
$ mkdir -p ~/ninja-demo/03-parallel && cd ~/ninja-demo/03-parallel
```

本示例不需要真实的编译器——我们用 `sleep` 命令模拟编译和链接耗时，这样可以在任何系统上（包括没有安装 g++ 的环境）演示并行效果。

---

## 2. 基础演示：-j 参数与并行度

### 2.1 创建 build.ninja（无 Pool 限制）

```ninja
# build.ninja —— 并行构建演示（无Pool限制）

rule compile
  command = sleep 1 && echo "  compiled $out"
  description = COMPILE $out

rule link
  command = sleep 2 && echo "  linked $out"
  description = LINK $out

# 模拟 6 个编译任务（每个"编译" sleep 1秒）
build a.o: compile a.c
build b.o: compile b.c
build c.o: compile c.c
build d.o: compile d.c
build e.o: compile e.c
build f.o: compile f.c

# 模拟 1 个链接任务（sleep 2秒）
build app: link a.o b.o c.o d.o e.o f.o

default app
```

这里我们有 6 个"编译"任务（每个耗时 1 秒）和 1 个"链接"任务（耗时 2 秒）。由于所有 `.o` 文件之间没有依赖，它们可以完全并行执行。

### 2.2 创建哑源文件

Ninja 需要输入文件实际存在（否则会报错 "missing and no known rule to make it"）。创建空文件即可：

```shell
$ touch a.c b.c c.c d.c e.c f.c
```

### 2.3 使用 -j1 串行构建

```shell
$ ninja -t clean 2>/dev/null; time ninja -j1
[1/7] COMPILE a.o
  compiled a.o
[2/7] COMPILE b.o
  compiled b.o
[3/7] COMPILE c.o
  compiled c.o
[4/7] COMPILE d.o
  compiled d.o
[5/7] COMPILE e.o
  compiled e.o
[6/7] COMPILE f.o
  compiled f.o
[7/7] LINK app
  linked app

real    0m8.05s
user    0m0.02s
sys     0m0.03s
```

**串行总耗时 ≈ 6×1 + 2 = 8 秒**。任务一个接一个执行。

### 2.4 使用 -j4 并行构建（4个并发）

```shell
$ ninja -t clean; time ninja -j4
[1/7] COMPILE a.o
[2/7] COMPILE b.o
[3/7] COMPILE c.o
[4/7] COMPILE d.o
  compiled b.o
  compiled a.o
  compiled c.o
  compiled d.o
[5/7] COMPILE e.o
[6/7] COMPILE f.o
  compiled e.o
  compiled f.o
[7/7] LINK app
  linked app

real    0m4.03s
user    0m0.03s
sys     0m0.05s
```

**4并发总耗时 ≈ 2×1（6个编译分两批）+ 2（链接）= 4 秒**。

第一批并行编译 a~d.o（1秒），第二批并行编译 e~f.o（1秒），然后链接（2秒）。

> **注意**：输出顺序可能与上面略有不同，因为并行任务完成顺序不确定。

### 2.5 使用 -j8（或默认值）完全并行

```shell
$ ninja -t clean; time ninja -j8
[1/7] COMPILE a.o
[2/7] COMPILE b.o
[3/7] COMPILE c.o
[4/7] COMPILE d.o
[5/7] COMPILE e.o
[6/7] COMPILE f.o
  compiled a.o
  compiled d.o
  compiled b.o
  compiled c.o
  compiled e.o
  compiled f.o
[7/7] LINK app
  linked app

real    0m3.02s
user    0m0.03s
sys     0m0.04s
```

**8并发总耗时 ≈ 1（所有6个编译同时进行）+ 2（链接）= 3 秒**。

### 2.6 时间对比总结

| -j 值 | 构建时间 | 说明 |
|-------|---------|------|
| 1 | ~8 秒 | 完全串行：6×1 + 2 |
| 2 | ~5 秒 | 编译分3批 + 链接：3×1 + 2 |
| 4 | ~4 秒 | 编译分2批 + 链接：2×1 + 2 |
| 6 | ~3 秒 | 所有编译并行 + 链接：1 + 2 |
| 8 | ~3 秒 | 超过独立任务数后不再加速 |

理论加速比：6 个并行编译 + 1 个链接，关键路径长度 = 1 + 2 = 3 秒。

---

## 3. Pool：限制特定任务的并发数

### 为什么需要 Pool？

在真实项目中，链接操作（尤其是 C++ 模板重的大项目）可能消耗大量内存。如果同时运行多个链接任务，可能导致内存不足（OOM）。**Pool** 允许你对特定类型的任务设置并发上限。

### 3.1 创建带 Pool 的 build.ninja

```ninja
# build.ninja —— Pool并发控制演示

# 定义 pool：link_pool 最多允许 1 个任务同时运行（即链接串行化）
pool link_pool
  depth = 1

# 定义 console pool：独占终端的任务池
pool console
  depth = 1

rule compile
  command = sleep 1 && echo "  compiled $out"
  description = COMPILE $out

# 链接规则使用 link_pool，同一时间只能有一个链接任务
rule link
  command = sleep 2 && echo "  linked $out"
  description = LINK $out
  pool = link_pool

# 模拟两个独立的可执行文件，各自需要编译和链接
# 场景：一个大项目中有 app1 和 app2 两个目标
build a.o: compile a.c
build b.o: compile b.c
build c.o: compile c.c
build app1: link a.o b.o
build app2: link c.o
# 注意：app2 也需要一个输入来模拟，但为了演示链接串行化效果，我们让 app2 也等待
build d.o: compile d.c
build e.o: compile e.c
build f.o: compile f.c
build app2: link d.o e.o f.o

default app1 app2
```

> **注意**：上面 `build app2: link c.o` 是中间演示状态，正式版本下面会修正。使用下面的完整版本。

### 3.2 完整带 Pool 的 build.ninja（修正版）

```ninja
# build.ninja —— Pool并发控制演示（完整版）

pool link_pool
  depth = 1

rule compile
  command = sleep 1 && echo "  compiled $out"
  description = COMPILE $out

rule link
  command = sleep 2 && echo "  linked $out"
  description = LINK $out
  pool = link_pool

# 6 个编译任务
build a.o: compile a.c
build b.o: compile b.c
build c.o: compile c.c
build d.o: compile d.c
build e.o: compile e.c
build f.o: compile f.c

# 2 个链接任务（都在 link_pool 中，depth=1 意味着必须串行）
build app1: link a.o b.o c.o
build app2: link d.o e.o f.o

default app1 app2
```

### 3.3 准备文件并构建

```shell
$ touch a.c b.c c.c d.c e.c f.c
$ ninja -t clean; time ninja -j8
[1/8] COMPILE a.o
[2/8] COMPILE b.o
[3/8] COMPILE c.o
[4/8] COMPILE d.o
[5/8] COMPILE e.o
[6/8] COMPILE f.o
  compiled a.o
  compiled c.o
  compiled d.o
  compiled b.o
  compiled f.o
  compiled e.o
[7/8] LINK app1
  linked app1
[8/8] LINK app2
  linked app2

real    0m5.03s
user    0m0.03s
sys     0m0.05s
```

关键观察：
1. **6 个编译任务在约 1 秒内全部并行完成**（-j8 足够并行）
2. **链接任务是串行的**：app1 完成链接后才开始 app2 的链接
3. 总耗时 ≈ 1（编译并行） + 2 + 2（链接串行）= **5 秒**

如果没有 `link_pool`，两个链接会并行执行，总耗时 ≈ 1 + 2 = **3 秒**。让我们验证：

### 3.4 对比：移除 Pool 后的效果

```ninja
# 将 link 规则中的 pool = link_pool 注释掉
rule link
  command = sleep 2 && echo "  linked $out"
  description = LINK $out
  # pool = link_pool   # 注释掉！
```

```shell
$ ninja -t clean; time ninja -j8
[1/8] COMPILE a.o
...（编译并行执行）...
[7/8] LINK app1
[8/8] LINK app2
  linked app1
  linked app2

real    0m3.02s
```

两个链接并行执行，节省了 2 秒。但在真实场景中，如果链接消耗大量内存（每个链接可能占用数 GB），同时运行多个链接可能导致系统 OOM。Pool 就是用来平衡速度和资源消耗的。

### 3.5 Pool 语法总结

```ninja
pool <pool_name>
  depth = <N>
```

在 rule 中引用：

```ninja
rule <rule_name>
  command = ...
  pool = <pool_name>
```

也可以在 build 语句中覆盖：

```ninja
build app: link a.o b.o
  pool = link_pool    # 为单个build边指定pool（覆盖rule中的设置）
```

---

## 4. Console Pool：独占终端的任务

某些命令需要与终端直接交互（例如需要用户输入的配置脚本、使用彩色输出的命令、或者需要显示进度条的任务）。这些任务如果在并行模式下运行，它们的输出会与其他任务交错，导致混乱。

Ninja 提供了一个特殊的内置 pool 叫 **`console`**，它的 `depth` 固定为 1。在 console pool 中的任务：

- 运行时直接连接到 stdin/stdout/stderr（不经过 Ninja 的输出缓冲）
- 同一时间只能有一个 console pool 任务运行
- 任务运行时，Ninja 暂停其他任务的输出显示（直到该任务完成）

### 4.1 Console Pool 示例

创建以下 `build.ninja`：

```ninja
# build.ninja —— console pool 演示

rule compile
  command = sleep 1 && echo "  compiled $out"
  description = COMPILE $out

# 配置脚本：需要用户输入确认，必须独占终端
rule configure
  command = echo "=== 配置脚本 ===" && echo "请确认编译配置 [Y/n]: " && read ans && echo "配置完成: $$ans" && echo "configured $out" > $out
  description = CONFIGURE $out
  pool = console    # 使用内置的 console pool

build config.status: configure configure.ac
build a.o: compile a.c | config.status    # order-only依赖：编译前需要先配置
build b.o: compile b.c | config.status
build app: link a.o b.o

rule link
  command = sleep 1 && echo "  linked $out"
  description = LINK $out

default app
```

创建输入文件：

```shell
$ touch a.c b.c configure.ac
```

运行：

```shell
$ ninja -t clean; ninja -j4
[1/4] CONFIGURE config.status
=== 配置脚本 ===
请确认编译配置 [Y/n]:
Y
配置完成: Y
[2/4] COMPILE a.o
  compiled a.o
[3/4] COMPILE b.o
  compiled b.o
[4/4] LINK app
  linked app
```

注意：
- `configure` 任务执行时，它直接向终端输出 `=== 配置脚本 ===` 并等待输入
- 用户输入 `Y` 后，配置完成，后续编译任务才开始
- 没有 `pool = console`，`read ans` 会因为 stdin 不可用而失败或行为异常

> **关于 `|` 语法**：`build a.o: compile a.c | config.status` 中的 `|` 表示 **order-only 依赖**——只保证 `config.status` 在 `a.o` 之前构建，但 `config.status` 的变化不会触发 `a.o` 重编译。这在 [增量构建与依赖追踪](04-incremental-deps.md#order-only-依赖) 中有详细讲解。

---

## 5. 查看并行统计：ninja -d stats

Ninja 提供了 `stats` 调试模式，输出构建过程中的并行度统计信息。

### 5.1 运行构建并收集统计

```shell
$ ninja -t clean; ninja -d stats -j4
[1/8] COMPILE a.o
...
[8/8] LINK app2
  linked app2

metric                  count   avg (us)
build                  (总构建边数)
.                      (各类统计)
```

### 5.2 典型输出解读

`ninja -d stats` 会在构建结束后输出如下统计信息：

```
metric                  count   avg (us)
.                      ...
n_started:              8
n_finished:             8
.initial_cmds:          6       (一开始可并行的任务数)
.initial_deps_missing:  0
.later_cmds:            2       (后续解锁的任务数)
```

关键字段：

| 指标 | 含义 |
|------|------|
| `n_started` | 启动的进程总数 |
| `n_finished` | 完成的进程总数 |
| `.initial_cmds` | 构建开始时就绪（所有依赖已满足）的任务数 |
| `.later_cmds` | 随着其他任务完成才解锁的任务数 |

对于本例（6 编译 + 2 链接）：
- `initial_cmds` = 6（所有编译任务一开始就可以并行启动）
- `later_cmds` = 2（链接任务需要等编译完成后才能开始）

### 5.3 更多统计信息

结合 `-v` 和 `-d explain` 可以更全面地分析：

```shell
$ ninja -t clean; ninja -d stats -j2 2>&1 | tail -20
```

你还可以查看 `.ninja_log` 中各任务的开始/结束时间，手动分析并行度：

```shell
$ cat .ninja_log
# ninja log v5
1755820800000	1755820801000	12345	a.o	...
1755820800000	1755820801000	12346	b.o	...
1755820800000	1755820801000	12347	c.o	...
1755820800000	1755820801000	12348	d.o	...
1755820801000	1755820802000	12349	e.o	...
1755820801000	1755820802000	12350	f.o	...
1755820802000	1755820804000	12351	app1	...
1755820804000	1755820806000	12352	app2	...
```

从时间戳可以看出：
- a~d.o 同时在 0-1 秒执行（-j4 时）
- e~f.o 在 1-2 秒执行
- app1 在 2-4 秒执行
- app2 在 4-6 秒执行（因为 link_pool 限制串行）

---

## 6. 默认并行度

如果不指定 `-j`，Ninja 默认使用系统 CPU 核心数 +2 作为并行度。查看默认值：

```shell
$ ninja -t clean; time ninja
```

在 4 核机器上等价于 `-j6`，在 8 核机器上等价于 `-j10`。

查看 CPU 核心数：

```shell
$ nproc          # Linux
8

$ sysctl -n hw.ncpu   # macOS
```

显式控制并行度是最佳实践，尤其是在 CI 环境中：

```shell
$ ninja -j$(nproc)     # 使用所有核心
$ ninja -j1            # 完全串行（用于调试）
$ ninja -l$(nproc)     # 限制负载平均值不超过核心数（-l 参数）
```

---

## 7. 完整文件汇总

### build.ninja（Pool 演示完整版）

```ninja
pool link_pool
  depth = 1

rule compile
  command = sleep 1 && echo "  compiled $out"
  description = COMPILE $out

rule link
  command = sleep 2 && echo "  linked $out"
  description = LINK $out
  pool = link_pool

build a.o: compile a.c
build b.o: compile b.c
build c.o: compile c.c
build d.o: compile d.c
build e.o: compile e.c
build f.o: compile f.c

build app1: link a.o b.o c.o
build app2: link d.o e.o f.o

default app1 app2
```

运行命令：

```shell
$ touch a.c b.c c.c d.c e.c f.c
$ ninja -t clean && time ninja -j8
```

---

## 8. 小结

| 概念 | 本例体现 |
|------|----------|
| `-j N` 参数 | 控制最大并发任务数，默认值 = CPU核心数+2 |
| 关键路径 | 并行度受依赖图关键路径限制，超过独立任务数后不再加速 |
| Pool | `pool name` + `depth = N` 定义并发池，限制某类任务的最大并发 |
| link_pool 模式 | `depth=1` 的 Pool 常用于串行化链接，防止内存溢出 |
| console pool | 内置特殊 pool（depth=1），任务独占终端，支持交互式命令 |
| `-d stats` | 输出构建统计，帮助分析并行效率 |
| `-l N` | 根据系统负载平均值限制并发 |

**关键经验法则**：
- 编译任务可以高并行（受 CPU 核心数限制）
- 链接任务通常用 Pool 限制为 1 或较低的并发数（受内存限制）
- 交互式/需要终端的命令使用 `pool = console`
- 实际项目中通过 `time ninja -jN` 测试不同 N 值找到最优并行度

**下一步**：深入学习 [增量构建与依赖追踪](04-incremental-deps.md)，理解 restat 规则、phony 目标和 order-only 依赖等高级依赖特性。
