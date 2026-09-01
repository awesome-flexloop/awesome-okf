---
type: Reference
title: C API 源码信源
description: libocispec C 语言 API 的核心头文件、公共函数与数据结构定义
tags: [reference, c-api, source, json-c, parsing, code-generation]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: json-common-h
    resource: /bundles/containers/libocispec/references/readme-source.md
    title: json_common.h 公共头文件
  - id: test-1
    resource: /bundles/containers/libocispec/references/readme-source.md
    title: tests/test-1.c 测试用例
---

# C API 源码信源

本文档记录 libocispec C 语言 API 的核心数据结构、公共函数与解析选项定义。C API 基于 json-c 库实现，所有解析器代码均由 Python 脚本从 JSON Schema 自动生成。

## 核心头文件

C API 的公共定义位于 `src/ocispec/json_common.h`，运行时 spec 头文件命名格式为 `runtime_spec_schema_config_schema.h`。

### 解析选项常量

```c
// 遇到 JSON 中未知键时报错
#define OPT_PARSE_STRICT 0x01
// 生成所有键值对
#define OPT_GEN_KEY_VALUE 0x02
// 生成简化（无缩进）JSON 字符串
#define OPT_GEN_SIMPLIFY 0x04
// 保留所有键值对，即使是未知的
#define OPT_PARSE_FULLKEY 0x08
// 不验证 UTF-8 数据
#define OPT_GEN_NO_VALIDATE_UTF8 0x10
```

### 错误类型

```c
typedef char *parser_error;
```

解析错误通过 `parser_error`（即 `char*`）类型返回，发生错误时指向动态分配的错误消息字符串，调用者需负责释放。

### 解析器上下文

```c
struct parser_context
{
  unsigned int options;
  FILE *errfile;
};
```

## 运行时 Spec 核心结构体

`runtime_spec_schema_config_schema` 是 OCI 运行时配置的根结构体，由代码生成器自动生成，主要字段包括：

| 字段 | 类型 | 说明 |
|------|------|------|
| `oci_version` | `char*` | OCI 规范版本号（必需字段） |
| `hostname` | `char*` | 容器主机名 |
| `domainname` | `char*` | 容器域名 |
| `process` | `runtime_spec_schema_config_schema_process*` | 进程配置 |
| `root` | `runtime_spec_schema_config_schema_root*` | 根文件系统配置 |
| `mounts` | `runtime_spec_schema_config_schema_mount**` | 挂载点数组 |
| `mounts_len` | `size_t` | 挂载点数组长度 |
| `linux` | `runtime_spec_schema_config_schema_linux*` | Linux 平台特定配置 |
| `hooks` | `runtime_spec_schema_config_schema_hooks*` | 生命周期钩子 |
| `annotations` | `json_map_string_string*` | 注解键值对 |

## 核心公共函数（代码生成模式）

每个生成的 Schema 类型都遵循相同的函数命名模式：

### 解析函数

```c
// 从文件解析
runtime_spec_schema_config_schema *
runtime_spec_schema_config_schema_parse_file (const char *filename,
                                              unsigned int options,
                                              parser_error *err);

// 从内存 JSON 字符串解析
runtime_spec_schema_config_schema *
runtime_spec_schema_config_schema_parse_data (const char *json_buf,
                                              unsigned int options,
                                              parser_error *err);
```

**参数说明：**
- `filename` / `json_buf`：输入源
- `options`：解析选项（`OPT_PARSE_STRICT` 等按位或组合）
- `err`：输出参数，错误时指向错误消息字符串

**返回值：** 成功返回分配的结构体指针，失败返回 `NULL`。

### 生成 JSON 函数

```c
char *
runtime_spec_schema_config_schema_generate_json (const runtime_spec_schema_config_schema *obj,
                                                 unsigned int options,
                                                 parser_error *err);
```

将 C 结构体序列化为 JSON 字符串。返回的字符串需用 `free()` 释放。

### 释放函数

```c
void
free_runtime_spec_schema_config_schema (runtime_spec_schema_config_schema *obj);
```

递归释放结构体及其所有子对象占用的内存。

### 克隆函数

```c
runtime_spec_schema_config_schema *
clone_runtime_spec_schema_config_schema (const runtime_spec_schema_config_schema *obj);
```

深拷贝整个结构体。

## 辅助数据结构类型

`json_common.h` 定义了多种通用 map 类型用于表示 JSON 对象：

| 类型 | 键类型 | 值类型 |
|------|--------|--------|
| `json_map_string_string` | `char*` | `char*` |
| `json_map_string_int` | `char*` | `int` |
| `json_map_string_bool` | `char*` | `bool` |
| `json_map_string_int64` | `char*` | `int64_t` |
| `json_map_int_int` | `int` | `int` |
| `json_map_int_bool` | `int` | `bool` |
| `json_map_int_string` | `int` | `char*` |

每种 map 类型都有对应的 `make_json_map_*`、`gen_json_map_*`、`free_json_map_*`、`append_json_map_*` 函数。

## 内存管理宏

```c
// 自动清理属性：变量离开作用域时自动调用清理函数
#define __auto_cleanup(cleaner) __attribute__ ((__cleanup__ (cleaner##_function)))

// 自动 free：char* 变量离开作用域时自动释放
#define __auto_free __auto_cleanup (ptr_free)

// 指针移动：将指针置空并返回原值，避免 double-free
#define move_ptr(ptr)               \
  ({                                \
    typeof (ptr) moved_ptr = (ptr); \
    (ptr) = NULL;                   \
    moved_ptr;                      \
  })
```

## JSON 生成器上下文

C API 提供流式 JSON 生成器用于手动构建 JSON：

```c
typedef struct
{
  json_object *stack[JSON_GEN_MAX_DEPTH];
  char *pending_key[JSON_GEN_MAX_DEPTH];
  bool is_map[JSON_GEN_MAX_DEPTH];
  int depth;
  json_object *root;
  char *buf;
  size_t buf_len;
  bool beautify;
} json_gen_ctx;
```

支持的操作：`json_gen_map_open/close`、`json_gen_array_open/close`、`json_gen_string`、`json_gen_number`、`json_gen_bool`、`json_gen_double`、`json_gen_null`、`json_gen_get_buf`。

## 构建系统

C 版本使用 GNU Autotools 构建系统：

- `autogen.sh`：生成 configure 脚本
- `configure`：检测系统依赖与配置
- `Makefile.am`：Automake 输入，定义编译目标
- `cfg.mk`：包本地配置
- `maint.mk`：维护者通用规则

## 测试文件

`tests/` 目录包含 15 个 C 测试文件（`test-1.c` 到 `test-15.c`），覆盖：

- 基本解析与生成（test-1.c）
- 网络设备配置（含 netdevices 数据）
- 各种复杂嵌套结构
- 数组、map 类型
- 可选字段存在性检测（`*_present` 标志）

## 相关概念

- [C API 使用指南](../concepts/01-c-api.md) — C API 完整使用流程与内存管理
- [OCI 规范与代码生成机制](../concepts/00-introduction.md) — Python 代码生成器工作原理
