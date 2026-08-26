---
type: "index"
title: "nbconvert 概念文档索引"
description: "nbconvert核心概念文档按学习路径组织"
tags: [concepts, index, learning-path]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
---

# nbconvert 概念文档索引

本目录包含nbconvert的系统概念文档，按从入门到进阶的学习路径组织。

## 📖 学习路径

### 入门篇（00-01）：快速了解与上手

| 序号 | 文档 | 内容 | 前置 |
|------|------|------|------|
| 00 | [nbconvert介绍](00-introduction.md) | 项目定位、核心能力、生态角色、版本信息 | 无 |
| 01 | [5分钟快速上手](01-getting-started.md) | 安装、CLI基本用法、Python API快速示例 | 00 |

### 核心篇（02-08）：架构深度理解

| 序号 | 文档 | 内容 | 前置 |
|------|------|------|------|
| 02 | [架构总览](02-architecture-overview.md) | 四阶段流水线、核心组件交互、数据流 | 01 |
| 03 | [导出器体系](03-exporter-hierarchy.md) | Exporter类层次、14个内置导出器详解 | 02 |
| 04 | [预处理器系统](04-preprocessor-system.md) | Preprocessor机制、11个内置预处理器 | 02 |
| 05 | [模板系统](05-template-system.md) | Jinja2模板、conf.json配置、模板继承链 | 02 |
| 06 | [过滤器系统](06-filters-system.md) | 40+内置过滤器、自定义过滤器注册 | 05 |
| 07 | [写入器与后处理器](07-writers-and-postprocessors.md) | FilesWriter/StdoutWriter/ServePostProcessor | 02 |
| 08 | [CLI与配置系统](08-cli-and-configuration.md) | 命令行参数、traitlets配置、配置文件编写 | 01 |

### 进阶篇（09-12）：扩展与集成

| 序号 | 文档 | 内容 | 前置 |
|------|------|------|------|
| 09 | [自定义导出器](09-custom-exporter.md) | 继承TemplateExporter、entry points注册 | 03 |
| 10 | [自定义预处理器](10-custom-preprocessor.md) | Cell/Notebook转换、预处理器注册模式 | 04 |
| 11 | [自定义模板](11-custom-template.md) | Jinja2模板编写、skeleton复用、包注册 | 05, 06 |
| 12 | [Notebook执行与生态集成](12-execution-and-integration.md) | ExecutePreprocessor、Kernel机制、自动化报告 | 04, 08 |

## 🔗 概念依赖关系

```
00-introduction
  └─ 01-getting-started
       └─ 02-architecture-overview
            ├─ 03-exporter-hierarchy ──→ 09-custom-exporter
            ├─ 04-preprocessor-system ──→ 10-custom-preprocessor ──┐
            ├─ 05-template-system ──→ 11-custom-template          ├─→ 12-execution-and-integration
            ├─ 06-filters-system ──→ 11-custom-template          │
            └─ 07-writers-postprocessors                         │
       └─ 08-cli-and-configuration ──────────────────────────────┘
```

## 📚 推荐阅读顺序

**新用户路径**：00 → 01 → 02 → 03 → 08
- 了解项目 → 上手使用 → 理解架构 → 掌握核心 → 配置定制

**开发者路径**：02 → 03 → 04 → 05 → 06 → 09 → 10 → 11
- 架构理解 → 核心组件 → 扩展开发

**自动化/CI路径**：01 → 04 → 08 → 12
- 快速上手 → 执行机制 → CLI配置 → 自动化报告

## 🏷️ 主题标签索引

| 主题 | 相关文档 |
|------|---------|
| 架构/设计 | 02-architecture-overview |
| 格式导出 | 03-exporter-hierarchy, 09-custom-exporter |
| 数据转换 | 04-preprocessor-system, 10-custom-preprocessor |
| 模板/渲染 | 05-template-system, 06-filters-system, 11-custom-template |
| 输出/IO | 07-writers-and-postprocessors |
| CLI/配置 | 08-cli-and-configuration |
| 执行/运行 | 12-execution-and-integration |
| 入门教程 | 00-introduction, 01-getting-started |

## 📂 配套资源

- **源码参考**：[references/index.md](../references/index.md) - 核心模块源码解析
- **示例代码**：[examples/index.md](../examples/index.md) - 可运行的Python示例

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-exporter-hierarchy
04-preprocessor-system
05-template-system
06-filters-system
07-writers-and-postprocessors
08-cli-and-configuration
09-custom-exporter
10-custom-preprocessor
11-custom-template
12-execution-and-integration
```
