# 信源参考

本目录包含 libocispec 项目的源码信源解析文档，直接从源代码和官方文档提取关键信息，供概念文档和实践示例引用。

## 信源文档列表

### 项目说明

- [README 项目说明信源](readme-source.md) — 项目定位、依赖要求、构建安装步骤、C/Rust 基本使用示例

### 语言 API 信源

- [C API 源码信源](c-api-source.md) — C 语言公共头文件、核心函数签名、数据结构定义、解析选项常量、内存管理宏、测试文件索引
- [Rust API 源码信源](rust-api-source.md) — Rust crate 配置、模块结构、序列化错误类型、Runtime/Image Spec 核心类型、serde 属性映射

## 源码文件索引

### C 语言源码

| 文件 | 说明 |
|------|------|
| `src/ocispec/json_common.h` | C API 公共头文件，定义解析选项、map 类型、JSON 生成器接口 |
| `src/ocispec/json_common.c` | C API 公共实现，包含内存分配、类型转换、JSON 生成逻辑 |
| `src/ocispec/validate.c` | OCI 规范验证逻辑 |
| `src/ocispec/generate.py` | Python 代码生成器主入口 |
| `src/ocispec/headers.py` | C 头文件代码生成器 |
| `src/ocispec/sources.py` | C 源文件代码生成器 |
| `src/ocispec/json_api.py` | JSON 访问 API 生成器 |
| `src/ocispec/helpers.py` | 代码生成辅助函数 |
| `tests/test-1.c` ~ `tests/test-15.c` | C API 测试用例 |

### Rust 源码

| 文件 | 说明 |
|------|------|
| `Cargo.toml` | Rust crate 配置与依赖声明 |
| `src/lib.rs` | crate 入口，导出模块并为 Spec 类型实现 load/save 方法 |
| `src/serialize.rs` | 序列化/反序列化基础设施与错误类型 |
| `src/runtime/mod.rs` | OCI Runtime Spec 完整类型定义（自动生成） |
| `src/image/mod.rs` | OCI Image Spec 完整类型定义（自动生成） |
| `src/runtime/test/config.test.json` | Rust 单元测试配置文件 |

## 外部资源

- **GitHub 仓库**：[containers/libocispec](https://github.com/containers/libocispec)
- **OCI Runtime Spec**：[opencontainers/runtime-spec](https://github.com/opencontainers/runtime-spec)
- **OCI Image Spec**：[opencontainers/image-spec](https://github.com/opencontainers/image-spec)
- **json-c 库**：[json-c/json-c](https://github.com/json-c/json-c)
- **serde 框架**：[serde-rs/serde](https://github.com/serde-rs/serde)

```{toctree}
:maxdepth: 1

readme-source
c-api-source
rust-api-source
```
