# 概念文档

本目录包含 libocispec 的核心概念文档，从项目定位到 API 使用逐步深入，帮助开发者理解和使用 libocispec。

## 文档列表

### 入门概念

- [00-OCI规范与代码生成机制](00-introduction.md) ⭐
  - libocispec 是什么、解决什么问题
  - OCI Runtime/Image 规范简介
  - 从 JSON Schema 生成代码的核心机制
  - C/Rust 双语言绑定架构概览
  - 设计哲学与适用场景

### API 使用指南

- [01-C API 使用指南](01-c-api.md)
  - 编译链接与头文件包含
  - 从文件/内存解析 OCI 配置
  - 字段访问（字符串、嵌套结构体、数组、map）
  - 手动构建配置并生成 JSON
  - 内存管理：free 函数与自动清理宏
  - 错误处理模式
  - 完整可编译示例

- 02-Rust API 使用指南
  - Cargo.toml 依赖配置
  - load()/save() 便捷方法
  - 类型安全字段访问（Option、Vec、HashMap）
  - 构建新配置与修改现有配置
  - 错误处理：Result 与 ? 运算符
  - serde 底层函数直接使用
  - 完整可运行示例

### 深度对比

- [03-双语言API对比](03-bindings-comparison.md)
  - 类型系统映射（可选字段、数组、map）
  - 内存管理模型对比（手动 vs RAII）
  - 错误处理机制对比（NULL+输出参数 vs Result）
  - 命名约定与构建系统对比
  - 功能覆盖矩阵
  - 性能特征与适用场景推荐
  - 双向迁移注意事项

## 推荐阅读顺序

### C 开发者路径

1. [00-introduction](00-introduction.md) — 理解项目定位与代码生成机制
2. [01-c-api](01-c-api.md) — 学习 C API 具体用法
3. [01-c-example](../examples/01-c-example.md) — 动手实践完整示例
4. [03-bindings-comparison](03-bindings-comparison.md) — 了解与 Rust API 的差异（可选）

### Rust 开发者路径

1. [00-introduction](00-introduction.md) — 理解项目定位与代码生成机制
2. [02-rust-api](02-rust-api.md) — 学习 Rust API 具体用法
3. [02-rust-example](../examples/02-rust-example.md) — 动手实践完整示例
4. [03-bindings-comparison](03-bindings-comparison.md) — 了解与 C API 的差异（可选）

### 选型决策路径

如果你在为新项目选择绑定，请阅读：
- [00-introduction](00-introduction.md) 中的"适用场景"章节
- [03-bindings-comparison](03-bindings-comparison.md) 中的"适用场景推荐"章节

```{toctree}
:maxdepth: 1

00-introduction
01-c-api
02-rust-api
03-bindings-comparison
```
