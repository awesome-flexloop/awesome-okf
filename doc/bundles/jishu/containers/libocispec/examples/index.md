# 实践示例

本目录提供可直接运行的完整代码示例，帮助开发者快速上手 libocispec 的 C 和 Rust 绑定。每个示例都包含完整代码、编译/运行步骤和代码要点解析。

## 示例列表

### C 语言示例

- [01-C 语言解析 OCI 配置](01-c-example.md) ⭐入门
  - 完整 C 程序：解析 `config.json`、打印配置摘要
  - 包含：基本字段访问、可选字段检查、数组遍历、嵌套结构体访问
  - 演示：修改字段→生成 JSON→重新解析 round-trip
  - 附带：编译命令、常见错误排查、扩展练习建议

### Rust 语言示例

- [02-Rust 语言解析 OCI 配置](02-rust-example.md)
  - 完整 Rust 项目：`Cargo.toml` 配置 + `main.rs` 实现
  - 三个子命令：`inspect`（打印 runtime spec）、`inspect-image`（打印 image spec）、`modify`（修改并保存）
  - 演示：Option 处理模式、? 错误传播、HashMap 操作、引用注意事项
  - 覆盖：Runtime Spec 和 Image Spec 两套类型
  - 包含：serde 直接操作技巧、常见编译错误解决

## 前置准备

### 运行 C 示例需要

- GCC 或 Clang 编译器
- libocispec 已安装（`make install`）
- json-c ≥ 0.14 开发包
- pkg-config（推荐，用于自动获取编译 flags）
- 一个有效的 OCI `config.json`（可用 `runc spec` 生成）

### 运行 Rust 示例需要

- Rust 工具链（rustup 安装即可）
- Cargo 包管理器
- 网络连接（Cargo 首次会从 GitHub 拉取 libocispec 源码）

### 获取示例配置文件

如果还没有 OCI 配置文件，可以用 runc 生成默认配置：

```sh
# 安装 runc 后执行
runc spec
# 当前目录会生成 config.json
```

或者手动创建一个最小配置 `minimal.json`：

```json
{
  "ociVersion": "1.0.0",
  "hostname": "test-container",
  "root": {
    "path": "rootfs",
    "readonly": true
  },
  "process": {
    "cwd": "/",
    "args": ["/bin/sh"],
    "terminal": true
  }
}
```

## 学习路径建议

### 快速验证安装

1. 从 [C 示例](01-c-example.md) 开始，编译运行确认 libocispec 工作正常
2. 如果熟悉 Rust，再尝试 [Rust 示例](02-rust-example.md) 感受类型安全 API

### 深入学习

1. 阅读示例代码，对照 [概念文档](../concepts/index.md) 理解每个 API 调用
2. 修改示例程序添加新功能（如打印更多字段、修改其他配置）
3. 故意传入无效 JSON 观察错误处理行为
4. 尝试处理 Image Spec（C: `image_spec_schema_config_schema.h`，Rust: `image::ImageSpec`）

### 项目集成

在实际项目中使用时，参考：
- C 项目：参考 C 示例的编译命令，将 `$(pkg-config --cflags --libs ocispec)` 加入 Makefile
- Rust 项目：参考 Rust 示例的 `Cargo.toml` 依赖配置

```{toctree}
:maxdepth: 1

01-c-example
02-rust-example
```
