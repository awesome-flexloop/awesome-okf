# 更新日志

本文件记录 libocispec OKF Wiki bundle 的版本变更历史。

## 2026-08-26

### 新增

- 初始版本，基于 libocispec 源码和事实文件生成完整 OKF Wiki bundle
- 建立标准 bundle 目录结构：concepts/、examples/、references/

### 信源参考（references/）

- `readme-source.md`：README 项目说明信源，包含安装方法和官方示例
- `c-api-source.md`：C API 源码信源，包含公共头文件定义、函数命名模式、解析选项、内存管理宏
- `rust-api-source.md`：Rust API 源码信源，包含 Cargo 配置、模块结构、SerializeError 错误类型、Runtime/Image Spec 核心类型
- `index.md`：信源索引和源码文件清单

### 概念文档（concepts/）

- `00-introduction.md`：OCI 规范与代码生成机制
  - libocispec 项目定位
  - OCI Runtime/Image 规范简介
  - 从 JSON Schema 到 C/Rust 代码的生成流程
  - 双语言绑定架构设计对比
  - 设计哲学与适用场景
- `01-c-api.md`：C API 使用指南
  - 编译链接与 pkg-config 使用
  - parse_file/parse_data 解析函数
  - 字段访问（字符串、嵌套结构体、数组、map）
  - 可选字段 `_present` 标志使用
  - 手动构建配置与 generate_json 序列化
  - 内存管理：free_/clone_ 函数、__auto_free 自动清理宏
  - 错误处理模式
  - 完整可编译示例程序
- `02-rust-api.md`：Rust API 使用指南
  - Cargo.toml 依赖配置与 feature 说明
  - load()/save() 便捷方法
  - Option 类型安全访问模式
  - Vec/HashMap 遍历
  - 构建新配置与修改现有配置
  - Result 错误处理与 ? 运算符
  - serde 底层函数直接使用
- `03-bindings-comparison.md`：双语言 API 对比
  - 类型系统映射（可选字段、数组、map 表示）
  - 内存管理模型对比（手动 free vs RAII 自动 drop）
  - 错误处理机制对比（NULL+输出参数 vs Result 枚举）
  - 命名约定与构建系统对比
  - 功能覆盖矩阵（严格模式、流式生成、验证等）
  - 性能特征
  - 适用场景推荐与双向迁移建议

### 实践示例（examples/）

- `01-c-example.md`：C 语言解析 OCI 配置
  - 完整 C 程序 `oci_inspect.c`（约 200 行）
  - 解析 config.json 并打印配置摘要（进程、挂载、Linux namespace、capabilities 等）
  - 演示：修改字段→生成 JSON→重新解析 round-trip
  - 包含：gcc 编译命令、pkg-config 用法、运行步骤、预期输出
  - 代码要点解析：可选字段检查模式、内存管理注意事项、常见错误排查
- `02-rust-example.md`：Rust 语言解析 OCI 配置
  - 完整 Rust 项目：Cargo.toml + src/main.rs（约 400 行）
  - 三个子命令：inspect（runtime spec）、inspect-image（image spec）、modify（修改并保存）
  - Runtime Spec 摘要打印（进程、挂载、Linux 配置、hooks、注解、seccomp）
  - Image Spec 摘要打印（层 diff_id、历史记录、运行时配置）
  - 修改配置演示：主机名、工作目录、注解
  - 包含：Option 处理模式、引用级别注意事项、错误友好提示、常见问题解决

### 根文件

- `index.md`：bundle 首页，包含快速导航、核心特性表、快速开始代码片段、学习路径、架构图
- `log.md`：本文件

### 内容统计

- 总文件数：15 个 Markdown 文件
- 概念文档：4 篇
- 示例文档：2 篇
- 信源文档：3 篇 + 索引
- 所有文档交叉链接正确，代码块标注语言（c/rust/toml/sh）
- 正文全中文，frontmatter 完整（type/title/description/tags/generated/status/sources）
- 符合 OKF v0.2 规范，包含 toctree 指令支持 Sphinx 构建
