---
type: examples
title: "Papyri 示例文档索引"
description: "从基础到进阶的 Papyri 使用示例，覆盖 gen 配置、打包上传、指令处理器扩展等核心场景"
tags: [examples, index, cookbook, patterns, papyri]
generated: { by: "reference_agent/trae-soLO", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: basic
    resource: "/examples/01-basic-gen.md"
    title: "基础 gen 工作流"
---

# 示例文档索引

Papyri 示例文档，覆盖从基础用法到进阶扩展的完整工作流。

## 示例清单

| 编号 | 示例 | 核心功能 | 对应概念 |
|------|------|---------|---------|
| 01 | [基础 gen 工作流](01-basic-gen.md) | TOML 配置、gen 命令、输出检查、--only 调试 | 01, 05, 07 |
| 02 | [自定义 TOML 配置](02-custom-config.md) | 子模块、排除项、指令注册、叙述文档、严格模式 | 05, 07, 11 |
| 03 | [Pack 与 Upload 工作流](03-pack-and-upload.md) | pack/unpack、确定性验证、上传到 viewer、CI 部署 | 03, 08, 12 |
| 04 | [自定义指令处理器](04-custom-directive-handler.md) | RST 指令处理、Admonition、代码块、多节点返回 | 10, 11 |

## 示例分类

### 入门基础

- **[01 基础 gen 工作流](01-basic-gen.md)**：最小 TOML 配置、运行 gen、检查输出、--only 调试、--exec 执行 doctest

### 配置与定制

- **[02 自定义 TOML 配置](02-custom-config.md)**：完整配置模板、子模块、排除项、叙述文档、多包配置、CI 严格模式

### 打包与部署

- **[03 Pack 与 Upload 工作流](03-pack-and-upload.md)**：打包、解包验证、确定性测试、本地上传、远程部署、CI 一条龙

### 扩展开发

- **[04 自定义指令处理器](04-custom-directive-handler.md)**：drop/code_handler 内置处理器、Admonition 处理器、多节点返回、Admonition 样式映射

## 前置条件

运行示例前确保：

```bash
# 安装 papyri
pip install papyri

# 验证安装
papyri --version

# 初始化目录（首次使用）
papyri bootstrap
```

部分示例需要启动 viewer（示例 03）：

```bash
cd papyri/ts
pnpm install
pnpm dev
# Viewer 运行在 http://localhost:4321
```

## 导航

- [教程首页](../index.md)
- [概念文档索引](../concepts/index.md)
- [源码信源索引](../references/index.md)
