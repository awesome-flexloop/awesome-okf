---
type: Concept
title: C API 使用指南
description: libocispec C 语言绑定的完整使用流程：解析配置、访问字段、生成 JSON、内存管理、错误处理、解析选项
tags: [concept, c-api, guide, json-c, memory-management, parsing, serialization]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: c-api-source
    resource: /bundles/containers/libocispec/references/c-api-source.md
    title: C API 源码信源
  - id: readme-source
    resource: /bundles/containers/libocispec/references/readme-source.md
    title: README 项目说明信源
---

# C API 使用指南

本文档详细介绍 libocispec C 语言绑定的使用方法，包括编译链接、解析 OCI 配置、访问字段、生成 JSON、内存管理和错误处理。

## 编译与链接

### 前置依赖

- **json-c** ≥ 0.14：JSON 解析库
- **C 编译器**：GCC 或 Clang，支持 C99 及以上
- **autotools**：autoconf、automake、libtool（从源码构建时需要）

### 安装 libocispec

```sh
$ ./autogen.sh
$ ./configure
$ make
$ sudo make install
```

安装后使用 pkg-config 获取编译 flags：

```sh
$ pkg-config --cflags --libs ocispec
```

### 编译示例程序

```sh
$ gcc -o myprogram myprogram.c $(pkg-config --cflags --libs ocispec)
```

## 头文件包含

C 程序需要包含生成的 spec 头文件和 config.h：

```c
#include <config.h>
#include <runtime_spec_schema_config_schema.h>
```

如果需要使用 Image Spec，则包含对应的头文件：

```c
#include <image_spec_schema_config_schema.h>
```

## 解析 OCI 配置文件

### 从文件解析

使用 `_parse_file` 函数从 JSON 文件解析：

```c
parser_error err = NULL;
runtime_spec_schema_config_schema *container = 
    runtime_spec_schema_config_schema_parse_file("config.json", 0, &err);

if (container == NULL) {
    fprintf(stderr, "解析错误: %s\n", err);
    free(err);
    exit(EXIT_FAILURE);
}
```

**函数签名：**
```c
runtime_spec_schema_config_schema *
runtime_spec_schema_config_schema_parse_file(const char *filename,
                                             unsigned int options,
                                             parser_error *err);
```

### 从内存字符串解析

也可以从内存中的 JSON 字符串解析：

```c
const char *json_str = "{\"ociVersion\": \"1.0.0\", \"hostname\": \"test\"}";
runtime_spec_schema_config_schema *container =
    runtime_spec_schema_config_schema_parse_data(json_str, 0, &err);
```

### 解析选项

`options` 参数是位掩码，可以组合以下选项：

| 选项 | 值 | 说明 |
|------|:--:|------|
| `OPT_PARSE_STRICT` | 0x01 | 遇到 JSON 中未知键时报错 |
| `OPT_PARSE_FULLKEY` | 0x08 | 保留所有键值对，即使是未知的 |

使用示例：
```c
// 严格模式：未知键导致解析失败
runtime_spec_schema_config_schema_parse_file("config.json", OPT_PARSE_STRICT, &err);
```

传 `0` 使用默认选项（宽松模式，忽略未知键）。

## 访问解析后的字段

解析成功后，可以通过指针访问结构体各字段。

### 基本字段访问

```c
// 访问字符串字段
if (container->hostname) {
    printf("主机名: %s\n", container->hostname);
}

// 访问数值字段（必需字段总是存在）
printf("OCI 版本: %s\n", container->oci_version);
```

### 嵌套结构体访问

使用箭头运算符链式访问嵌套结构体：

```c
// 访问进程配置
if (container->process) {
    printf("工作目录: %s\n", container->process->cwd);
    
    // 访问用户配置
    if (container->process->user) {
        // 使用 _present 标志判断可选数值字段是否存在
        if (container->process->user->uid_present) {
            printf("用户 ID: %d\n", container->process->user->uid);
        }
        if (container->process->user->gid_present) {
            printf("组 ID: %d\n", container->process->user->gid);
        }
    }
    
    // 访问终端标志
    if (container->process->terminal_present) {
        printf("启用终端: true\n");
    }
}
```

> **重要**：可选数值字段（如 `uid`、`gid`）需要检查对应的 `_present` 布尔标志来区分"字段未设置"和"字段值为 0"。字符串字段和指针类型直接检查 `NULL` 即可。

### 数组字段访问

数组字段使用指针+长度配对表示：

```c
// 遍历挂载点数组
for (size_t i = 0; i < container->mounts_len; i++) {
    printf("挂载 %zu: 目标=%s, 源=%s, 类型=%s\n",
           i,
           container->mounts[i]->destination,
           container->mounts[i]->source,
           container->mounts[i]->type ? container->mounts[i]->type : "(none)");
}

// 遍历进程参数
if (container->process && container->process->args_len > 0) {
    printf("命令: ");
    for (size_t i = 0; i < container->process->args_len; i++) {
        printf("%s ", container->process->args[i]);
    }
    printf("\n");
}
```

### 访问 Linux 特定配置

```c
if (container->linux) {
    // 遍历 namespaces
    for (size_t i = 0; i < container->linux->namespaces_len; i++) {
        printf("Namespace %zu: type=%s", i, container->linux->namespaces[i]->type);
        if (container->linux->namespaces[i]->path) {
            printf(", path=%s", container->linux->namespaces[i]->path);
        }
        printf("\n");
    }
    
    // 访问 resources 配置
    if (container->linux->resources) {
        // 访问 CPU/memory/pids 等限制
        if (container->linux->resources->memory) {
            if (container->linux->resources->memory->limit_present) {
                printf("内存限制: %lld\n", container->linux->resources->memory->limit);
            }
        }
    }
}
```

### Map 类型字段访问

注解等键值对字段使用生成的 map 类型：

```c
// 访问 annotations
if (container->annotations) {
    json_map_string_string *ann = container->annotations;
    for (size_t i = 0; i < ann->len; i++) {
        printf("注解: %s = %s\n", ann->keys[i], ann->values[i]);
    }
}
```

## 从零构建配置并生成 JSON

除了解析现有配置，也可以手动构建 C 结构体然后序列化为 JSON。

### 初始化结构体

使用 `memset` 清零初始化：

```c
runtime_spec_schema_config_schema container;
memset(&container, 0, sizeof(runtime_spec_schema_config_schema));

// 设置必需字段
container.oci_version = "1.0.0";
container.hostname = "my-container";

// 设置进程配置
container.process = safe_malloc(sizeof(runtime_spec_schema_config_schema_process));
memset(container.process, 0, sizeof(runtime_spec_schema_config_schema_process));
container.process->cwd = "/";
container.process->terminal = true;
container.process->terminal_present = true;
```

> **注意**：手动构建时需要自己负责分配嵌套结构体的内存。使用 `safe_malloc` （来自 json_common.h）分配内存，它在分配失败时不会返回 NULL。

### 设置字符串数组

```c
// 设置 args
const char *args[] = {"/bin/sh", "-c", "echo hello"};
size_t args_len = sizeof(args) / sizeof(args[0]);
container.process->args = safe_malloc(sizeof(char*) * args_len);
container.process->args_len = args_len;
for (size_t i = 0; i < args_len; i++) {
    container.process->args[i] = safe_strdup(args[i]);
}
```

### 生成 JSON 字符串

```c
parser_error err = NULL;
char *json_buf = runtime_spec_schema_config_schema_generate_json(
    &container, 0, &err);

if (json_buf == NULL) {
    fprintf(stderr, "生成 JSON 错误: %s\n", err);
    free(err);
    // 清理已分配的内存...
    exit(EXIT_FAILURE);
}

printf("生成的 JSON:\n%s\n", json_buf);

// 使用完毕后释放
free(json_buf);
```

### 生成选项

`_generate_json` 函数的 options 参数支持：

| 选项 | 值 | 说明 |
|------|:--:|------|
| `OPT_GEN_KEY_VALUE` | 0x02 | 生成所有键值对 |
| `OPT_GEN_SIMPLIFY` | 0x04 | 生成无缩进的紧凑 JSON |
| `OPT_GEN_NO_VALIDATE_UTF8` | 0x10 | 跳过 UTF-8 验证 |

示例：
```c
// 生成紧凑 JSON
char *json_buf = runtime_spec_schema_config_schema_generate_json(
    &container, OPT_GEN_SIMPLIFY, &err);
```

## 内存管理

C API 的内存管理是使用中最需要注意的部分。每个解析出来的对象都必须正确释放。

### 释放解析的对象

```c
runtime_spec_schema_config_schema *container = 
    runtime_spec_schema_config_schema_parse_file("config.json", 0, &err);

// ... 使用 container ...

// 释放整个对象（递归释放所有子对象）
free_runtime_spec_schema_config_schema(container);
```

每个生成的类型都有对应的 `free_` 函数，命名规则为 `free_<type_name>`。该函数会递归释放结构体中的所有字符串、数组、嵌套结构体。

### 克隆对象

如果需要深拷贝一个对象：

```c
runtime_spec_schema_config_schema *copy = 
    clone_runtime_spec_schema_config_schema(container);

// ... 使用 copy ...

free_runtime_spec_schema_config_schema(copy);
```

### 手动构建的内存清理

手动构建结构体时，需要自己清理所有分配的内存。最简单的方式是构建完成后生成 JSON，然后直接清理：如果逻辑复杂，也可以手动释放每个字段：

```c
// 手动清理示例
void free_my_container(runtime_spec_schema_config_schema *c) {
    if (c->hostname) free(c->hostname);
    if (c->oci_version) free(c->oci_version);  // 如果是 strdup 的
    
    if (c->process) {
        for (size_t i = 0; i < c->process->args_len; i++) {
            free(c->process->args[i]);
        }
        free(c->process->args);
        free(c->process->cwd);
        free(c->process);
    }
    
    // ... 其他字段 ...
    
    free(c);
}
```

但更安全的方式是直接使用库提供的 `free_` 函数——即使你手动分配了内存，只要你遵循了与生成代码相同的内存布局约定，`free_` 函数就能正确释放。

### 自动清理宏（GCC/Clang 扩展）

`json_common.h` 提供了 `__auto_free` 宏，利用 GCC/Clang 的 `__cleanup__` 属性实现变量离开作用域时自动释放：

```c
void example() {
    __auto_free char *str = safe_strdup("hello");
    // str 离开作用域时自动调用 free()
}
```

这在处理临时 JSON 缓冲区时特别有用：

```c
{
    __auto_free char *json_buf = 
        runtime_spec_schema_config_schema_generate_json(&container, 0, &err);
    if (json_buf) {
        printf("%s\n", json_buf);
    }
    // json_buf 自动释放，无需手动 free
}
```

## 错误处理

### 错误检查模式

所有可能失败的函数都通过返回值和 `parser_error` 参数报告错误：

```c
parser_error err = NULL;
runtime_spec_schema_config_schema *container =
    runtime_spec_schema_config_schema_parse_file("config.json", 0, &err);

if (container == NULL) {
    // 错误处理
    fprintf(stderr, "错误位置: %s:%d\n", __FILE__, __LINE__);
    if (err) {
        fprintf(stderr, "错误信息: %s\n", err);
        free(err);  // 错误消息需要释放
    }
    return -1;
}
```

> **注意**：错误消息字符串 `err` 是动态分配的，使用后必须调用 `free(err)` 释放。

### 常见错误场景

1. **文件不存在或无法读取**：返回 NULL，err 包含 "No such file or directory" 等
2. **JSON 格式错误**：返回 NULL，err 包含 json-c 的解析错误
3. **缺少必需字段**：严格模式下返回 NULL
4. **类型不匹配**：返回 NULL，err 包含类型错误信息
5. **内存分配失败**：生成 JSON 时可能发生

### GEN_SET_ERROR_AND_RETURN 宏

内部代码使用 `GEN_SET_ERROR_AND_RETURN` 宏统一设置错误并返回：

```c
if (something_wrong) {
    GEN_SET_ERROR_AND_RETURN(-1, err);
}
```

该宏会自动填充文件名、函数名、行号和错误码。

## 完整示例：解析并重新生成

```c
#include <config.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <runtime_spec_schema_config_schema.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "用法: %s <config.json>\n", argv[0]);
        return 1;
    }

    parser_error err = NULL;
    
    // 1. 解析文件
    runtime_spec_schema_config_schema *container =
        runtime_spec_schema_config_schema_parse_file(argv[1], 0, &err);
    
    if (!container) {
        fprintf(stderr, "解析失败: %s\n", err ? err : "unknown error");
        free(err);
        return 1;
    }

    // 2. 读取一些字段
    printf("=== OCI 配置信息 ===\n");
    printf("OCI 版本: %s\n", container->oci_version ? container->oci_version : "(未设置)");
    printf("主机名: %s\n", container->hostname ? container->hostname : "(未设置)");
    
    if (container->process) {
        printf("工作目录: %s\n", container->process->cwd ? container->process->cwd : "/");
        if (container->process->user) {
            if (container->process->user->uid_present)
                printf("UID: %d\n", container->process->user->uid);
        }
    }
    
    printf("挂载点数量: %zu\n", container->mounts_len);

    // 3. 重新生成 JSON
    char *json_out = runtime_spec_schema_config_schema_generate_json(
        container, 0, &err);
    if (json_out) {
        printf("\n=== 重新生成的 JSON ===\n");
        printf("%s\n", json_out);
        free(json_out);
    } else {
        fprintf(stderr, "生成 JSON 失败: %s\n", err ? err : "unknown");
        free(err);
    }

    // 4. 清理
    free_runtime_spec_schema_config_schema(container);
    return 0;
}
```

## 相关主题

- [Rust API 使用指南](02-rust-api.md) — Rust 版本的类型安全 API
- [双语言 API 对比](03-bindings-comparison.md) — C vs Rust API 设计差异
- [C 语言解析 OCI 配置示例](../examples/01-c-example.md) — 完整可运行示例
