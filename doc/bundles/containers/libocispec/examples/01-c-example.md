---
type: Example
title: C 语言解析 OCI 配置
description: 完整的 C 语言示例程序：解析 OCI runtime config.json、打印关键字段、修改后重新生成 JSON，包含编译命令和内存管理说明
tags: [example, c, parsing, runtime-config, walkthrough]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: test-1
    resource: /bundles/containers/libocispec/references/c-api-source.md
    title: tests/test-1.c 参考实现
  - id: c-api-concept
    resource: /bundles/containers/libocispec/concepts/01-c-api.md
    title: C API 使用指南
---

# C 语言解析 OCI 配置

本示例提供一个完整的 C 程序，演示如何使用 libocispec C API 解析 OCI 运行时配置文件、访问关键字段、修改配置并重新生成 JSON。

## 前置条件

- 已安装 libocispec（`make install` 完成）
- 已安装 json-c ≥ 0.14 开发包
- GCC 或 Clang 编译器
- 一个有效的 OCI `config.json` 文件（可以用 `runc spec` 生成示例）

## 示例程序：打印容器配置摘要

下面的程序读取一个 `config.json` 文件，打印容器的关键配置信息，并演示解析→访问→生成的完整流程。

### 完整代码

创建文件 `oci_inspect.c`：

```c
#include <config.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <runtime_spec_schema_config_schema.h>

static void print_usage(const char *progname) {
    fprintf(stderr, "用法: %s <config.json>\n", progname);
    fprintf(stderr, "  解析 OCI config.json 并打印配置摘要\n");
}

static void print_mount_summary(const runtime_spec_schema_config_schema *container) {
    if (container->mounts_len == 0) {
        printf("  挂载点: (无)\n");
        return;
    }
    printf("  挂载点 (%zu 个):\n", container->mounts_len);
    for (size_t i = 0; i < container->mounts_len; i++) {
        const auto *m = container->mounts[i];
        printf("    [%zu] %s -> %s", 
               i,
               m->source ? m->source : "(无来源)",
               m->destination);
        if (m->type) {
            printf(" (type=%s)", m->type);
        }
        printf("\n");
    }
}

static void print_process_summary(const runtime_spec_schema_config_schema_process *proc) {
    if (!proc) {
        printf("  进程配置: (无)\n");
        return;
    }

    printf("  进程配置:\n");
    printf("    终端: %s\n", proc->terminal_present && proc->terminal ? "是" : "否");
    printf("    工作目录: %s\n", proc->cwd ? proc->cwd : "/");
    
    if (proc->user) {
        printf("    用户: ");
        if (proc->user->uid_present) printf("uid=%d ", proc->user->uid);
        if (proc->user->gid_present) printf("gid=%d ", proc->user->gid);
        if (!proc->user->uid_present && !proc->user->gid_present) {
            printf("(未指定)");
        }
        printf("\n");
    }

    if (proc->args_len > 0) {
        printf("    命令: ");
        for (size_t i = 0; i < proc->args_len; i++) {
            printf("%s%s", proc->args[i], i < proc->args_len - 1 ? " " : "");
        }
        printf("\n");
    }

    if (proc->env_len > 0) {
        printf("    环境变量 (%zu 个):\n", proc->env_len);
        for (size_t i = 0; i < proc->env_len && i < 5; i++) {
            printf("      %s\n", proc->env[i]);
        }
        if (proc->env_len > 5) {
            printf("      ... (还有 %zu 个)\n", proc->env_len - 5);
        }
    }
}

static void print_linux_summary(const runtime_spec_schema_config_schema_linux *linux) {
    if (!linux) {
        printf("  Linux 配置: (无)\n");
        return;
    }

    printf("  Linux 配置:\n");
    
    if (linux->namespaces_len > 0) {
        printf("    Namespaces (%zu 个):\n", linux->namespaces_len);
        for (size_t i = 0; i < linux->namespaces_len; i++) {
            const auto *ns = linux->namespaces[i];
            printf("      - %s", ns->type ? ns->type : "(未知类型)");
            if (ns->path) {
                printf(" (path=%s)", ns->path);
            }
            printf("\n");
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }

    const char *config_path = argv[1];
    parser_error err = NULL;

    /* 步骤 1: 解析配置文件 */
    printf("=== 正在解析: %s ===\n\n", config_path);
    
    runtime_spec_schema_config_schema *container =
        runtime_spec_schema_config_schema_parse_file(config_path, 0, &err);

    if (container == NULL) {
        fprintf(stderr, "错误: 解析配置文件失败\n");
        if (err) {
            fprintf(stderr, "详细信息: %s\n", err);
            free(err);
        }
        return 1;
    }

    printf("解析成功!\n\n");

    /* 步骤 2: 访问基本字段 */
    printf("=== 配置摘要 ===\n");
    printf("  OCI 版本: %s\n", container->oci_version ? container->oci_version : "(未设置)");
    printf("  主机名: %s\n", container->hostname ? container->hostname : "(未设置)");
    
    if (container->root) {
        printf("  根文件系统: path=%s", container->root->path ? container->root->path : "rootfs");
        if (container->root->readonly_present && container->root->readonly) {
            printf(" (只读)");
        }
        printf("\n");
    }

    printf("\n");
    print_process_summary(container->process);
    printf("\n");
    print_mount_summary(container);
    printf("\n");
    print_linux_summary(container->linux);

    /* 步骤 3: 修改并重新生成 JSON（演示） */
    printf("\n=== 演示：修改主机名后重新生成 JSON ===\n");
    
    /* 修改主机名 */
    if (container->hostname) {
        free(container->hostname);
    }
    container->hostname = safe_strdup("modified-by-libocispec-example");

    /* 生成 JSON */
    char *json_buf = runtime_spec_schema_config_schema_generate_json(
        container, 0, &err);

    if (json_buf == NULL) {
        fprintf(stderr, "生成 JSON 失败: %s\n", err ? err : "未知错误");
        free(err);
        free_runtime_spec_schema_config_schema(container);
        return 1;
    }

    printf("新主机名已设置为: modified-by-libocispec-example\n");
    printf("生成的 JSON 长度: %zu 字节\n", strlen(json_buf));
    
    /* 验证：重新解析生成的 JSON */
    runtime_spec_schema_config_schema *regenerated =
        runtime_spec_schema_config_schema_parse_data(json_buf, 0, &err);
    
    if (regenerated && regenerated->hostname) {
        printf("验证：重新解析后的主机名 = %s\n", regenerated->hostname);
        free_runtime_spec_schema_config_schema(regenerated);
    }

    /* 步骤 4: 清理内存 */
    free(json_buf);
    free_runtime_spec_schema_config_schema(container);

    printf("\n=== 完成 ===\n");
    printf("提示: 如果需要保存到文件，可以将生成的 JSON 字符串写入文件\n");

    return 0;
}
```

### 编译命令

使用 pkg-config 获取编译和链接 flags：

```sh
gcc -Wall -Wextra -o oci_inspect oci_inspect.c $(pkg-config --cflags --libs ocispec)
```

如果 pkg-config 不可用，手动指定：

```sh
gcc -Wall -Wextra -o oci_inspect oci_inspect.c \
    -I/usr/local/include \
    -L/usr/local/lib \
    -locispec -ljson-c
```

### 运行示例

首先生成一个示例配置（需要安装 runc）：

```sh
# 生成默认 config.json
runc spec

# 运行我们的检查程序
./oci_inspect config.json
```

预期输出：

```
=== 正在解析: config.json ===

解析成功!

=== 配置摘要 ===
  OCI 版本: 1.0.0
  主机名: runc
  根文件系统: path=rootfs

  进程配置:
    终端: 是
    工作目录: /
    用户: uid=0 gid=0
    命令: /bin/sh
    环境变量 (8 个):
      PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
      TERM=xterm
      ... (还有 3 个)

  挂载点 (6 个):
    [0] proc -> /proc (type=proc)
    [1] tmpfs -> /dev (type=tmpfs)
    [2] devpts -> /dev/pts (type=devpts)
    ...

  Linux 配置:
    Namespaces (5 个):
      - pid
      - network
      - ipc
      - uts
      - mount

=== 演示：修改主机名后重新生成 JSON ===
新主机名已设置为: modified-by-libocispec-example
生成的 JSON 长度: 5234 字节
验证：重新解析后的主机名 = modified-by-libocispec-example

=== 完成 ===
提示: 如果需要保存到文件，可以将生成的 JSON 字符串写入文件
```

## 代码要点解析

### 1. 解析选项

```c
runtime_spec_schema_config_schema_parse_file(config_path, 0, &err);
```

第二个参数 `0` 表示使用默认选项。可用选项：

- `OPT_PARSE_STRICT` (0x01)：遇到未知字段时报错
- `OPT_PARSE_FULLKEY` (0x08)：保留未知字段

### 2. 可选字段访问模式

**指针类型（字符串/结构体）**：直接检查 NULL
```c
if (container->hostname) {  // 字符串字段
    printf("%s\n", container->hostname);
}
```

**数值字段**：检查 `_present` 标志
```c
if (proc->user->uid_present) {  // 数值字段必须检查标志
    printf("uid=%d", proc->user->uid);
}
```

> **常见错误**：直接读取 `proc->user->uid` 而不检查 `uid_present`。当字段不存在时，`uid` 的值是 0（memset 初始化），但这不代表字段值就是 0——必须检查 `_present` 标志才能确定。

### 3. 数组遍历

数组使用指针+长度配对，遍历前检查长度：

```c
for (size_t i = 0; i < container->mounts_len; i++) {
    const auto *m = container->mounts[i];
    // 使用 m
}
```

### 4. 内存管理

代码中三处内存释放：

| 分配来源 | 释放方式 |
|---------|---------|
| `parse_file()` 返回的 container | `free_runtime_spec_schema_config_schema(container)` |
| `generate_json()` 返回的 json_buf | `free(json_buf)` |
| 错误消息 err | `free(err)` |
| 手动 `safe_strdup()` 的字符串 | `free()` |

> **注意**：在修改 hostname 时，我们先 `free(container->hostname)` 再赋新值。这是因为原始字符串是 parse 时分配的，替换前必须释放旧值，否则会内存泄漏。如果一开始就是 memset 清零的结构体（手动构建），则不需要先 free。

### 5. 完整循环：解析→生成→再解析

示例展示了 round-trip 验证：
1. 从文件解析为 C 结构体
2. 修改结构体
3. 生成 JSON 字符串
4. 从字符串重新解析
5. 验证字段值正确

这是 libocispec 的典型使用模式：程序操作内存中的类型化结构体，只在 I/O 边界进行 JSON 转换。

## 扩展练习

你可以基于此示例扩展更多功能：

1. **添加命令行选项**：使用 getopt 支持 `--no-color`、`--output <file>` 等参数
2. **合并两个配置**：用 `clone_*()` 函数克隆后修改合并
3. **验证配置合法性**：结合 `validate.c` 提供的验证函数
4. **处理 image spec**：包含 `image_spec_schema_config_schema.h`，用相同模式处理镜像配置
5. **严格模式测试**：添加故意包含未知字段的 JSON，使用 `OPT_PARSE_STRICT` 观察错误

## 常见问题排查

### 编译错误：runtime_spec_schema_config_schema.h: No such file or directory

确保已运行 `make install`，或者在编译时指定头文件路径：
```sh
gcc -I/usr/local/include ...
```
或检查 pkg-config 路径：
```sh
pkg-config --cflags ocispec
```

### 运行时错误：error while loading shared libraries: libocispec.so.0

运行 `ldconfig` 更新共享库缓存：
```sh
sudo ldconfig
```
或者设置 `LD_LIBRARY_PATH`：
```sh
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

### 解析总是失败，err 显示 JSON 错误

检查 JSON 文件格式是否正确。可以用 `jq . config.json` 验证：
```sh
jq . config.json > /dev/null && echo "JSON 格式正确" || echo "JSON 格式错误"
```

## 相关主题

- [C API 使用指南](../concepts/01-c-api.md) — C API 完整文档
- [Rust 语言示例](02-rust-example.md) — Rust 版本的相同功能示例
- [C API 源码信源](../references/c-api-source.md) — 函数签名和类型定义
