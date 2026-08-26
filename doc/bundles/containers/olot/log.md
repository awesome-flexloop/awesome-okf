# Changelog - olot OKF Bundle

本文档记录 olot OKF Wiki Bundle 的版本变更。

## [1.0.0] - 2026-08-26

### Added

- 初始版本生成，基于 olot v1.2.2 源码
- 信源文件（references/）：
  - `readme-source.md` - 官方 README 信源
  - `oci-source.md` - OCI 层操作源码信源
  - `backend-source.md` - 后端抽象层源码信源
  - `index.md` - 信源索引
- 概念文档（concepts/）：
  - `00-introduction.md` - olot 定位与 ModelCar 标准
  - `01-oci-layers.md` - OCI 层操作与四元组注解
  - `02-backends.md` - 后端抽象层（skopeo/oras）
  - `03-python-api.md` - Python API 编程
  - `index.md` - 概念索引
- 示例文档（examples/）：
  - `01-cli-usage.md` - 命令行基本使用
  - `02-python-api.md` - Python API 打包模型
  - `index.md` - 示例索引
- 根文件：
  - `index.md` - Bundle 首页与导航
  - `log.md` - 本变更日志

### Documentation

- 所有文档使用中文撰写
- 代码块标注 python/bash 语言
- 交叉链接使用 `/bundles/containers/olot/...` 开头的 bundle-relative 路径
- 所有文档包含完整的 OKF v0.2 frontmatter
- 所有 API 引用基于源码验证（Grep 级验证）

### Sources

基于以下源码版本生成：
- olot v1.2.2
- 源码路径：`d:\spaces\SpecWeave\external\dao\action\Containers\olot`
- 事实文件：`d:\spaces\SpecWeave\.trae\specs\containers-okf-wiki\facts-olot.md`
