---
type: category
title: "数据序列化生态"
okf_version: "0.2"
description: "Protocol Buffers 序列化生态源码级中文教程——2个核心知识包，覆盖 protobuf 主仓（C++/upb 双内核运行时、protoc 编译器、Editions、九语言绑定）与 protobuf-ci（GitHub Actions 复用动作与五层 CI 缓存）"
total_bundles: 2
status: stable
---

# 数据序列化生态知识库

本知识包分组收录 Google Protocol Buffers 序列化生态的系统化中文源码教程。内容涵盖 protobuf 主仓的完整技术版图——双运行时内核（C++ 全功能内核与 upb 轻量 C 内核）、protoc 编译器管线（Parser/Importer/生成器/插件协议）、Editions 特性系统、九大语言绑定与双构建系统（Bazel/CMake），以及独立仓库 protobuf-ci 的 GitHub Actions composite action 复用体系与五层 CI 缓存治理。

所有知识包遵循 [OKF v0.2 规范](../../../meta/okf-spec/index.md)，通过源码深度阅读（R→I→E→V→C 五阶段链路）生成，所有 API 引用均经 Grep 级源码验证。

## 📊 知识包概览

| 层次 | 知识包 | 简介 | 文档数 |
|------|--------|------|--------|
| 序列化核心 | [protobuf](protobuf/index.md) | protobuf 主仓 v37.0-dev——双运行时内核、descriptor 单一事实源、protoc 生成器体系、Editions 特性系统、双构建系统 | 27 |
| CI 基础设施 | [protobuf-ci](protobuf-ci/index.md) | protobuf 家族共享 CI 动作集合——9 顶层 + 7 internal composite action、Bazel/ccache/sccache 五层缓存、跨平台容器底座 | 6 |

## 序列化核心

| 知识包 | 简介 |
|--------|------|
| [protobuf](protobuf/index.md) | protobuf 主仓——C++/upb 双内核（Python 默认 upb、Rust 双 kernel、hpb 多后端）、descriptor 单一事实源（protobuf 用 protobuf 描述 protobuf）、protoc 命令行/Parser/生成器/插件协议、Editions 八值枚举与协商矩阵、WKT/Conformance/Benchmarks、Bazel 与 CMake 双构建系统 |

## CI 基础设施

| 知识包 | 简介 |
|--------|------|
| [protobuf-ci](protobuf-ci/index.md) | protobuf-ci @v6——bazel/bazel-docker 构建动作与 GCS 远程缓存、ccache/sccache 编译缓存（三级 restore-keys 回退）、docker/checkout/bash 基础动作、composer-setup 与 cross-compile-protoc 专项动作、@v6 release 版本纪律 |

## 生态关系概览

```
┌──────────────────────────────────────────────────────────────────────┐
│                    应用层（Application Layer）                         │
│                                                                      │
│   九语言绑定：Python(upb) · Rust(双kernel) · Java · C# · ObjC         │
│              PHP(upb) · Ruby(upb) · Lua(upb) · hpb(C++多后端)        │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ 代码生成（protoc --*_out / 插件协议）
┌──────────────────────────────▼───────────────────────────────────────┐
│                    编译层（Compiler Layer）                            │
│                                                                      │
│   protoc：命令行框架 → Parser/Importer → 生成器/插件                   │
│   （descriptor.proto = 贯穿全生命周期的单一事实源）                     │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ 序列化 / 反序列化（wire format）
┌──────────────────────────────▼───────────────────────────────────────┐
│                    运行时内核层（Runtime Kernel Layer）                  │
│                                                                      │
│   ┌──────────────────────────┐   ┌──────────────────────────┐       │
│   │  C++ 全功能内核            │   │  upb 轻量 C 内核          │       │
│   │  Message/反射/Arena       │   │  Python/Rust/PHP/Ruby/   │       │
│   │  （C++/C#/ObjC/Java）     │   │  Lua/hpb 绑定复用         │       │
│   └──────────────────────────┘   └──────────────────────────┘       │
└──────────────────────────────────────────────────────────────────────┘

  横向支撑：protobuf-ci（CI 动作集合）
  —— bazel/ccache/sccache 五层缓存 · 10 语言 × 9 平台构建矩阵
```

## 推荐学习路径

### 路径一：protobuf 核心原理（序列化栈）

```
📦 protobuf（主仓束）
  00-02 入门组（仓库总览 → 消息模型 → wire format）
  → 03-06 核心机制组（descriptor → Arena → 容器/扩展 → Text/JSON）
  → 07-10 编译器组（命令行 → Parser → 生成器 → 插件协议）
  → 11-14 运行时组（Python → upb/Rust → hpb → 其他语言）
  → 15-16 高级组（Editions → WKT/Conformance/Benchmarks）
```

从仓库总览与消息模型入手，理解 wire format 二进制编码；再深入 descriptor 单一事实源与 Arena 内存管理两大核心机制；随后沿 protoc 编译管线（命令行 → 解析 → 生成 → 插件）走一遍 schema 到代码的完整旅程；最后横向铺开多语言运行时（双内核视角）与 Editions 演进主线。

### 路径二：CI 基础设施（工程治理）

```
🔧 protobuf-ci（CI 束）
  01 仓库定位 → 02 bazel 构建 → 03 编译缓存 → 04 基础动作 → 05 专项动作
```

从 protobuf-ci 的 composite action 组织结构与 @v6 release 纪律入手，掌握 Bazel 远程缓存、ccache/sccache 三级回退链等五层缓存治理，适用于需要构建大规模多语言 CI 矩阵的工程团队。

## 信源与验证

- **源码根目录**：`external/libs/protocolbuffers/`
- **生成方法**：source-code-to-okf-wiki 技能（R→I→E→V→C 五阶段链路）
  - **R**（Read/Retrospective）：源码深度阅读与编号事实采集（542 条：主仓 486 + CI 56）
  - **I**（Insight）：架构洞察与知识地图设计（5 个核心洞察四元组）
  - **E**（Extraction/Execution）：OKF 文档批量生成（信源先行、分批生成、Index 最后写）
  - **V**（Verification）：Grep 级 API 真实性验证、链接完整性检查、frontmatter 校验
  - **C**（Commit）：可复用模式沉淀
- **API 验证**：所有类名/方法名经 Grep 源码验证存在性，杜绝虚构 API
- **frontmatter**：所有文档遵循 OKF v0.2 YAML frontmatter 规范

```{toctree}
:hidden:
:maxdepth: 7

protobuf/index
protobuf-ci/index
```
