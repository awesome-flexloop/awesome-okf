---
okf_version: "0.2"
type: examples-index
title: "Nuitka 实战示例索引"
description: "Nuitka编译实战示例——从基本编译到插件开发"
---

# Nuitka 实战示例索引

本索引包含5个实战示例，覆盖Nuitka最常用的使用场景。

| 示例 | 难度 | 说明 | 前置知识 |
|------|------|------|---------|
| [基本编译](basic-compilation.md) | ⭐ 入门 | 将Python脚本编译为可执行文件，理解编译输出 | 无 |
| [独立可执行文件构建](standalone-build.md) | ⭐⭐ 中级 | --standalone模式，DLL依赖、数据文件、GUI应用 | 基本编译 |
| [单文件打包](onefile-build.md) | ⭐⭐ 中级 | --onefile模式，压缩、临时目录、闪屏 | 独立构建 |
| [编译为扩展模块](module-mode.md) | ⭐⭐ 中级 | --module模式，生成.pyd/.so加速Python库 | 基本编译 |
| [使用与创建插件](plugin-usage.md) | ⭐⭐⭐ 高级 | 标准插件使用、YAML插件、Python代码插件编写 | 独立构建 |

## 推荐阅读顺序

```
basic-compilation
  ├→ standalone-build → onefile-build
  ├→ module-mode
  └→ plugin-usage（需standalone-build基础）
```

```{toctree}
:maxdepth: 7

basic-compilation
module-mode
onefile-build
plugin-usage
standalone-build
```
