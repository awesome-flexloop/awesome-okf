---
okf_version: "0.2"
type: group
title: "🏗️ CMake 构建系统生态"
description: "CMake 跨平台构建系统生成器及其测试/打包工具链"
---

# 🏗️ CMake 构建系统生态

CMake 是业界标准的跨平台构建系统生成器，支持 Unix Makefiles、Ninja、Visual Studio、Xcode 等多种构建后端，配套 CTest 测试框架和 CPack 打包工具，形成"配置-构建-测试-打包"完整工具链。本组涵盖 CMake 核心源码分析教程。

## 学习路径

按 **核心架构 → 实战示例** 的顺序学习：

### 第一步：核心引擎

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 1 | [cmake](cmake/index.md) | CMake 核心构建系统——门面模式两阶段执行、不可变状态快照、多生成器工厂、目标属性传播、find_package、策略系统、CTest/CPack 集成（基于 C++ 源码深度阅读） |

```{toctree}
:hidden:

cmake/index
```
