---
type: Concept
title: 双语言 API 对比
description: C API 与 Rust API 的设计差异对比：内存管理、可选字段、数组表示、错误处理、构建系统、命名约定、适用场景
tags: [concept, comparison, c, rust, api-design, memory-safety]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: c-api-source
    resource: /bundles/containers/libocispec/references/c-api-source.md
    title: C API 源码信源
  - id: rust-api-source
    resource: /bundles/containers/libocispec/references/rust-api-source.md
    title: Rust API 源码信源
---

# 双语言 API 对比

libocispec 同时提供 C 和 Rust 两套独立的语言绑定。虽然它们共享同一个 Python 代码生成器和相同的 JSON Schema 来源，但在 API 设计上遵循各自语言的惯用模式（idiomatic patterns）。本文档详细对比两套 API 的差异，帮助开发者选择适合自己场景的绑定。

## 一、核心设计理念对比

| 维度 | C API | Rust API |
|------|-------|----------|
| **设计目标** | 面向系统编程，零开销抽象 | 面向安全编程，类型安全优先 |
| **内存管理** | 手动管理，free_*() 函数 | RAII + 所有权系统，自动管理 |
| **类型安全** | 编译时部分保障，运行时检查 | 编译时强类型保证 |
| **错误处理** | 返回 NULL + 输出参数 | Result 枚举类型 |
| **抽象级别** | 接近底层 JSON 结构 | 高层，符合 Rust 生态习惯 |
| **依赖** | json-c ≥ 0.14 | serde, serde_json, chrono, url |

## 二、类型系统对比

### 基本类型映射

| OCI JSON 类型 | C 类型 | Rust 类型 | 说明 |
|---------------|--------|-----------|------|
| string (必需) | `char*` | `String` | 必需字符串字段 |
| string (可选) | `char*`（NULL 表示缺失） | `Option<String>` | Option 包装 |
| integer | `int` / `int64_t` | `i64` / `Option<i64>` | 可选数值有 _present 标志 |
| boolean | `bool` / 存在标志 | `bool` / `Option<bool>` | 布尔值可选性 |
| array | `T**` + `size_t xxx_len` | `Option<Vec<T>>` | 指针+长度 vs Vec |
| object | `T*`（指针） | `Option<T>` | 嵌套结构体指针 |
| map<string,string> | `json_map_string_string*` | `Option<HashMap<String, Option<Value>>>` | 专用 map 类型 vs 通用 HashMap |
| null | 指针为 NULL 或标志位 | `None` | Option::None 统一表示 |

### 可选字段表示：最显著的差异

这是两套 API 最核心的设计差异：

#### C API 的可选字段

C 语言没有原生的"可选类型"概念，因此用两种方式处理可选性：

1. **指针类型**（字符串、嵌套结构体、数组）：`NULL` 指针表示字段缺失
2. **数值/布尔类型**：需要额外的 `_present` 布尔标志位

```c
typedef struct {
    char *hostname;           // 可选字符串：NULL = 未设置
    struct {
        int64_t uid;          // 数值
        bool uid_present;     // 存在标志：true = uid 已设置
        int64_t gid;
        bool gid_present;
    } *user;
    bool terminal;            // 布尔值
    bool terminal_present;    // 存在标志
} process;
```

访问时必须检查标志位：
```c
if (process->user && process->user->uid_present) {
    printf("UID: %lld\n", process->user->uid);
}
```

**容易出错的地方**：忘记检查 `_present` 标志会导致把零值（0）当作有效值读取。

#### Rust API 的可选字段

Rust 使用 `Option<T>` 枚举类型统一表示所有可选值，类型系统强制检查：

```rust
pub struct Process {
    pub cwd: Option<String>,
    pub user: Option<User>,
    pub terminal: Option<bool>,
    // ...
}

pub struct User {
    pub uid: Option<i64>,
    pub gid: Option<i64>,
    // 无需要 _present 标志！
}
```

访问时必须通过模式匹配解包：
```rust
if let Some(ref user) = process.user {
    if let Some(uid) = user.uid {
        println!("UID: {}", uid);
    }
}
// 编译错误！不能直接访问 Option 内部的值
// println!("{}", user.uid);
```

**安全性**：编译器保证你不会忘记检查可选性，编译期就捕获错误。

### 数组表示对比

#### C API：指针 + 长度配对

```c
struct {
    mount **mounts;        // 指向指针数组
    size_t mounts_len;     // 数组长度
} config;

// 遍历
for (size_t i = 0; i < config.mounts_len; i++) {
    printf("%s\n", config.mounts[i]->destination);
}
```

需要小心：
- `mounts` 可能为 NULL（数组为空/未设置）
- 长度和指针必须一致
- 数组越界无检查

#### Rust API：Option<Vec<T>>

```rust
pub struct Spec {
    pub mounts: Option<Vec<Mount>>,
}

// 遍历
if let Some(ref mounts) = spec.mounts {
    for mount in mounts {
        println!("{}", mount.destination);
    }
}
```

`Vec` 自带长度，迭代器自动处理边界，Option 处理空/缺失情况。

## 三、内存管理对比

### C API：手动管理

每个生成的类型都有三个内存管理函数：

| 函数 | 用途 | 调用者责任 |
|------|------|-----------|
| `parse_file()`/`parse_data()` | 解析并分配内存 | 必须调用 `free_*()` 释放 |
| `generate_json()` | 生成 JSON 字符串 | 必须 `free()` 返回的 char* |
| `free_*()` | 递归释放整个对象 | 必须对每个 parse 结果调用一次 |
| `clone_*()` | 深拷贝对象 | 克隆结果也需要 free |

**常见陷阱**：
- 忘记调用 `free_*()` 导致内存泄漏
- 重复释放（double free）
- 释放后继续使用（use-after-free）
- 手动修改结构体后 free 不匹配

```c
// C 内存管理样板代码
parser_error err = NULL;
auto *config = parse_file("config.json", 0, &err);
if (!config) { /* 错误处理 */ }

// ... 使用 config ...

// 必须记得释放！
free_runtime_spec_schema_config_schema(config);
```

使用 GCC/Clang 扩展可部分缓解：
```c
// 借助 __attribute__((cleanup)) 自动释放
__attribute__((cleanup(cleanup_config))) 
auto *config = parse_file(...);
```

但这是非标准扩展，可移植性有限。

### Rust API：自动管理

Rust 的所有权系统在编译期自动插入内存释放代码：

- `parse`/`load` 返回的对象在离开作用域时自动 drop
- 所有嵌套结构体、字符串、Vec 自动递归释放
- 无内存泄漏、无 double free、无 use-after-free（unsafe 代码除外）

```rust
{
    let spec = runtime::Spec::load("config.json")?;
    // 使用 spec
    println!("{}", spec.oci_version);
} // <- 这里 spec 自动 drop，所有内存释放
// 没有任何手动 free 调用！
```

即使发生错误或早期 return，RAII 机制也能保证正确清理。

## 四、错误处理对比

### C API：返回 NULL + 输出参数

```c
parser_error err = NULL;
auto *config = runtime_spec_schema_config_schema_parse_file(
    "config.json", 0, &err);

if (config == NULL) {
    fprintf(stderr, "错误: %s\n", err);
    free(err);  // err 也需要释放！
    return -1;
}
```

**问题**：
- 错误消息字符串本身需要 `free()`，容易忘记
- 无法区分错误类型（文件不存在 vs JSON 格式错误 vs 字段缺失）
- `err` 参数可能为 NULL，需要额外检查
- 函数签名中 `options` 参数和 `err` 参数容易混淆

### Rust API：Result 枚举

```rust
match runtime::Spec::load("config.json") {
    Ok(spec) => {
        println!("{}", spec.oci_version);
    }
    Err(e) => {
        eprintln!("错误: {}", e);
        // 可以匹配具体错误类型
        match e {
            SerializeError::Io(io_err) => {
                eprintln!("I/O 错误: {}", io_err.kind());
            }
            SerializeError::Json(json_err) => {
                eprintln!("JSON 错误 at line {}:{}", 
                         json_err.line(), json_err.column());
            }
        }
    }
}
```

**优势**：
- `?` 运算符提供简洁的错误传播
- 错误类型是强类型枚举，可以精确匹配
- 错误消息自动管理，无需手动释放
- `Result` 返回值强制检查（除非用 `.unwrap()` 显式忽略）

## 五、命名约定对比

### 函数/方法命名

| 操作 | C 命名模式 | Rust 命名模式 |
|------|-----------|---------------|
| 从文件解析 | `<type>_parse_file(filename, opts, &err)` | `Type::load(path)` |
| 从字符串解析 | `<type>_parse_data(str, opts, &err)` | `serde_json::from_str(str)` |
| 序列化为 JSON | `<type>_generate_json(obj, opts, &err)` | `serde_json::to_string(obj)` / `obj.save(path)` |
| 释放内存 | `free_<type>(obj)` | 自动 drop（无对应函数） |
| 深拷贝 | `clone_<type>(obj)` | `obj.clone()`（derive(Clone)） |

### 字段命名：snake_case vs camelCase 映射

#### C API

C 直接使用 snake_case 命名，字段名与 JSON 字段名对应（下划线替换点和横杠）：

```c
// JSON: {"ociVersion": "...", "createContainer": [...]}
container->oci_version;
hooks->create_container;
// JSON: {"os.features": [...]}
image->os_features;
```

头文件命名也非常长：
```c
#include <runtime_spec_schema_config_schema.h>
```

#### Rust API

Rust 使用 `#[serde(rename = "...")]` 属性处理映射：

```rust
pub struct Spec {
    #[serde(rename = "ociVersion")]
    pub oci_version: String,  // Rust 用 snake_case
    
    #[serde(rename = "os.features")]
    pub os_features: Option<Vec<String>>,
}
```

Rust 代码中始终使用 snake_case，serde 自动处理 JSON 的 camelCase 转换。

## 六、构建系统对比

| 方面 | C (autotools) | Rust (Cargo) |
|------|---------------|--------------|
| 构建命令 | `./autogen.sh && ./configure && make` | `cargo build` |
| 依赖安装 | 系统包管理器（apt/yum 等安装 json-c-dev） | Cargo 自动下载编译 |
| 包配置 | pkg-config (`ocispec.pc`) | Cargo.toml 直接 git 依赖 |
| 测试 | `make check`（运行 test-1 到 test-15） | `cargo test` |
| 代码生成 | make 规则自动调用 Python 生成器 | `make generate-rust`（手动） |
| 安装 | `make install`（到系统目录） | `cargo install` 或作为依赖 |
| 交叉编译 | 通过 configure --host 参数 | Cargo 内置支持（--target） |

### 引入依赖的难度对比

**在 C 项目中使用 libocispec**：
1. 用户需要预先安装 json-c 库和头文件
2. 需要运行 autogen.sh/configure（可能需要 autotools）
3. 需要 make 和 make install
4. 需要正确设置 CFLAGS 和 LDFLAGS（或使用 pkg-config）
5. 分发时需要处理共享库依赖

**在 Rust 项目中使用 libocispec**：
1. 在 Cargo.toml 添加一行 git 依赖
2. `cargo build` 自动拉取、编译、链接所有依赖
3. 静态链接默认可用，分发简单

## 七、功能覆盖对比

| 功能 | C API | Rust API | 说明 |
|------|:-----:|:--------:|------|
| Runtime Spec 解析 | ✅ | ✅ | 完整支持 |
| Runtime Spec 生成 | ✅ | ✅ | 完整支持 |
| Image Spec 解析 | ✅ | ✅ | 完整支持 |
| Image Spec 生成 | ✅ | ✅ | 完整支持 |
| 严格解析模式 | ✅ (OPT_PARSE_STRICT) | ❌ | serde 默认忽略未知字段 |
| 保留未知字段 | ✅ (OPT_PARSE_FULLKEY) | ❌ | 反序列化丢弃未知字段 |
| 紧凑 JSON 输出 | ✅ (OPT_GEN_SIMPLIFY) | ✅ (to_string vs to_string_pretty) |
| UTF-8 验证选项 | ✅ (OPT_GEN_NO_VALIDATE_UTF8) | ❌ | serde_json 总是验证 |
| 流式 JSON 生成 | ✅ (json_gen_ctx) | ❌ | Rust 直接构建结构体再序列化 |
| 验证函数 | ✅ (validate.c) | ❌ | Rust 依赖类型系统保证结构合法 |
| 从字符串解析 | ✅ (_parse_data) | ✅ (serde_json::from_str) |
| 从文件解析 | ✅ (_parse_file) | ✅ (load()) |
| 写入文件 | ❌（手动 fopen/fwrite） | ✅ (save()) |
| 深拷贝 | ✅ (clone_*()) | ✅ (derive(Clone)) |
| 内存清理 | ✅ (free_*()) | ✅ (自动 drop) |

## 八、性能特征对比

| 维度 | C API | Rust API | 说明 |
|------|-------|----------|------|
| 解析速度 | 极快 | 快 | json-c 是成熟的 C JSON 解析器；serde_json 也非常快 |
| 内存开销 | 低 | 略高 | Rust 有边界检查和 Option 标签开销，但通常可忽略 |
| 二进制大小 | 小 | 较大 | Rust 静态链接依赖；C 动态链接 json-c |
| 编译时间 | 快 | 较慢 | Cargo 需要编译 serde/serde_json/chrono/url 等依赖 |
| 运行时依赖 | libjson-c.so | 无（静态链接） | Rust 二进制自包含 |

> **性能注意**：对于容器运行时这类场景，两者性能差异通常不是瓶颈——配置文件解析是一次性操作，不是热路径。

## 九、适用场景推荐

### 选择 C API 的场景

- **编写 OCI 运行时**：如 runc、crun 本身是 C 项目
- **系统级工具**：资源受限环境、嵌入式系统
- **现有 C 代码库集成**：与遗留 C 代码交互
- **需要精确控制内存布局**：自定义分配器、内存池
- **需要严格模式/未知字段处理**：C 的 OPT_PARSE_STRICT 提供更多控制
- **动态链接偏好**：希望通过系统包管理器分发

### 选择 Rust API 的场景

- **新的 Rust 项目**：如 youki 等 Rust 容器运行时
- **安全性优先**：不想处理手动内存管理和可选标志
- **快速原型开发**：Cargo 一键引入，Result 处理简洁
- **需要高层便捷方法**：`load()`/`save()` 直接读写文件
- **交叉编译需求**：Cargo 交叉编译支持更友好
- **静态链接分发**：单二进制分发无需依赖系统库

### 混合使用场景

libocispec 的 C 和 Rust 绑定是独立的，可以在不同组件中分别使用：

- 容器运行时（C）使用 C API
- 周边工具（Rust）使用 Rust API
- 两者通过 OCI JSON 文件格式互操作

## 十、迁移建议

### 从 C 迁移到 Rust

如果你熟悉 C API 并开始使用 Rust API，注意以下映射：

| C 模式 | Rust 等价模式 |
|--------|---------------|
| 检查 `ptr == NULL` | `if let Some(ref x) = opt` / `match opt` |
| 检查 `field_present` | 自动包含在 `Option` 中 |
| `for (i=0; i<len; i++)` 遍历数组 | `for item in vec.iter()` |
| `free_xxx(ptr)` | 无需操作，自动 drop |
| `err` 输出参数 | `Result` 返回值 + `?` |
| `strcmp(s1, s2) == 0` | `s1 == s2`（String 实现 PartialEq） |
| `strlen(s)` | `s.len()` |
| `asprintf(&err, ...)` | 使用 `format!()` 或 anyhow/thiserror |

### 从 Rust 到 C 的注意事项

- 所有指针都可能为 NULL，访问前必须检查
- 数值字段需要检查对应的 `_present` 标志
- 每个分配的对象都必须配对 free 调用
- 错误消息 char* 也需要释放
- 数组遍历要注意数组长度，防止越界

## 总结

| 判断维度 | 倾向 C | 倾向 Rust |
|---------|:------:|:---------:|
| 现有代码库是 C | ✅ | |
| 现有代码库是 Rust | | ✅ |
| 内存安全是首要考虑 | | ✅ |
| 零依赖/小二进制 | ✅ | |
| 开发速度/人体工程学 | | ✅ |
| 需要严格解析模式 | ✅ | |
| 交叉编译到新平台 | | ✅ |
| 长期维护/贡献者友好 | | ✅ |

两套 API 都是从同一个 JSON Schema 生成的，功能等价，只是编程范式不同。选择哪一个主要取决于你的项目语言和对安全性/控制度的权衡。

## 相关主题

- [C API 使用指南](01-c-api.md) — C API 详细使用
- [Rust API 使用指南](02-rust-api.md) — Rust API 详细使用
- [C 语言示例](../examples/01-c-example.md)
- [Rust 语言示例](../examples/02-rust-example.md)
