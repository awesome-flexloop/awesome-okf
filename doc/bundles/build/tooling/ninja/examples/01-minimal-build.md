---
type: Example
title: 最简构建：编译单个C程序
description: 从零开始，用Ninja编译一个Hello World C程序，理解build.ninja的基本结构、rule与build语句、自动变量以及增量构建判断机制。
tags: [ninja, example, beginner, c, build-rule, incremental]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 最简构建：编译单个C程序

本示例通过编译一个最简单的 Hello World C 程序，带你入门 Ninja 的基本使用。学完本示例，你将理解：

- `build.ninja` 文件的基本结构
- `rule` 和 `build` 语句的写法
- `$in`、`$out` 自动变量的含义
- Ninja 如何判断是否需要重编译
- `ninja -v`、`ninja -n`、`ninja -d explain` 等常用调试选项

> **前置知识**：建议先阅读 [入门指南](../concepts/01-getting-started.md) 和 [清单语言](../concepts/05-manifest-language.md)。

---

## 1. 项目准备

创建一个新的工作目录，并进入该目录：

```shell
$ mkdir -p ~/ninja-demo/01-minimal && cd ~/ninja-demo/01-minimal
```

### 1.1 创建源文件 main.c

```c
// main.c
#include <stdio.h>

int main(void) {
    printf("Hello, Ninja!\n");
    return 0;
}
```

---

## 2. 编写 build.ninja

`build.ninja` 是 Ninja 的构建清单文件（manifest），类似于 Make 的 `Makefile`。我们需要定义一个编译规则和一个构建目标。

创建 `build.ninja` 文件，内容如下：

```ninja
# build.ninja —— 最简 Ninja 构建文件

# 定义编译规则：使用 gcc 将 C 源文件编译为可执行文件
rule cc
  command = gcc -Wall -o $out $in
  description = CC $out

# 声明构建目标：将 main.c 编译为 main
build main: cc main.c

# 设置默认目标
default main
```

### 逐行解释

| 部分 | 说明 |
|------|------|
| `rule cc` | 定义一个名为 `cc` 的构建规则（rule），相当于 Makefile 中的模式规则 |
| `command = gcc -Wall -o $out $in` | 规则执行的命令。`$out` 代表输出文件，`$in` 代表输入文件 |
| `description = CC $out` | 构建时显示的描述信息，使输出更简洁友好 |
| `build main: cc main.c` | 构建边（build edge）：目标 `main` 依赖 `main.c`，使用 `cc` 规则构建 |
| `default main` | 指定执行裸 `ninja` 命令时的默认目标 |

### 自动变量

- **`$in`**：构建语句中列出的所有输入文件（空格分隔）。本例中为 `main.c`。
- **`$out`**：构建语句中列出的所有输出文件（空格分隔）。本例中为 `main`。

这两个变量由 Ninja 在执行时自动展开，无需手动赋值。更多自动变量参见 [清单语言](../concepts/05-manifest-language.md#自动变量)。

---

## 3. 执行构建

### 3.1 首次构建（ninja）

```shell
$ ninja
[1/1] CC main
```

输出 `[1/1]` 表示总共 1 个任务，当前正在执行第 1 个。构建成功后，目录下会生成可执行文件 `main`：

```shell
$ ls
build.ninja  main  main.c
```

### 3.2 运行程序

```shell
$ ./main
Hello, Ninja!
```

### 3.3 冗余构建检查（ninja 无参数）

如果没有任何文件被修改，再次运行 `ninja` 将不会执行任何命令：

```shell
$ ninja
ninja: no work to do.
```

这就是 Ninja 的核心价值之一——**增量构建**：只重新构建过期的目标，跳过无需更新的目标。

### 3.4 干运行（ninja -n）

`-n`（dry-run）选项只打印将要执行的命令，而不实际执行：

```shell
$ ninja -n
$ ninja -n   # 修改 main.c 之后再试
[1/1] gcc -Wall -o main main.c
```

在无修改时无输出；修改源文件后会显示即将执行的编译命令。

### 3.5 详细输出（ninja -v）

`-v`（verbose）选项显示完整的编译命令，而不是 `description` 中的简短描述：

```shell
$ touch main.c    # 标记源文件为"已修改"
$ ninja -v
[1/1] gcc -Wall -o main main.c
```

使用 `-v` 可以看到 `$in` 和 `$out` 被替换成实际文件名后的完整命令。

---

## 4. 理解增量构建判断

Ninja 通过比较**输入文件**和**输出文件**的修改时间戳（mtime）来决定是否需要重编译。这一机制在 [增量构建](../concepts/06-incremental-build.md) 中有详细描述。

### 4.1 观察解释输出（ninja -d explain）

`-d explain` 调试选项让 Ninja 解释它为什么决定重建（或不重建）某个目标：

**场景 A：不修改任何文件**

```shell
$ ninja -d explain
ninja: Entering directory `/home/user/ninja-demo/01-minimal'
ninja: no work to do.
```

**场景 B：修改源文件 main.c 后**

```shell
$ touch main.c       # 或者用编辑器修改文件
$ ninja -d explain
ninja: Entering directory `/home/user/ninja-demo/01-minimal'
ninja: explain: output 'main' of edge 'cc' is older than input 'main.c'
[1/1] CC main
```

关键信息：`output 'main' is older than input 'main.c'`——输出文件 `main` 比输入文件 `main.c` 旧，因此需要重编译。

**场景 C：修改 build.ninja 本身**

```shell
$ touch build.ninja
$ ninja -d explain
ninja: Entering directory `/home/user/ninja-demo/01-minimal'
ninja: explain: output 'main' of edge 'cc' is older than most recent input 'build.ninja' (1234567890 vs 1234567891)
[1/1] CC main
```

Ninja 自动将 `build.ninja` 本身作为所有构建边的隐式依赖——修改构建规则也会触发重编译。

### 4.2 修改时间验证

可以用 `ls -la` 和 `stat` 查看文件时间戳，验证 Ninja 的判断：

```shell
$ stat -c '%Y %n' main.c main
1755820800 main.c
1755820700 main
```

`main.c` 的 mtime（1755820800）大于 `main` 的 mtime（1755820700），所以 `main` 需要被重建。

---

## 5. 清理与重建

虽然本示例没有定义 `clean` 规则，但可以手动删除构建产物后重新构建：

```shell
$ rm main
$ ninja
[1/1] CC main
```

删除输出文件后，Ninja 发现输出不存在，会重新执行构建。

> 在更复杂的项目中，通常会使用 `ninja -t clean` 子命令来清理，参见 [子命令实用指南](05-subcommand-usage.md#ninja--t-clean)。

---

## 6. 完整文件汇总

### main.c

```c
#include <stdio.h>

int main(void) {
    printf("Hello, Ninja!\n");
    return 0;
}
```

### build.ninja

```ninja
rule cc
  command = gcc -Wall -o $out $in
  description = CC $out

build main: cc main.c

default main
```

---

## 7. 小结

| 概念 | 本例体现 |
|------|----------|
| `rule` | `cc` 规则定义了如何编译 C 文件 |
| `build` 边 | `build main: cc main.c` 声明了目标-依赖关系 |
| 自动变量 | `$in` = `main.c`，`$out` = `main` |
| 默认目标 | `default main` 指定无参数时的构建目标 |
| 增量构建 | 通过 mtime 比较决定是否重建，`-d explain` 可查看原因 |
| 常用选项 | `-n` 干运行、`-v` 详细输出、`-d explain` 解释原因 |

**下一步**：继续学习 [多文件C++项目](02-cxx-project.md)，了解头文件依赖追踪、分离编译与链接等更实用的模式。
