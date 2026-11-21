---
type: Concept
title: "Maple Mono 简介"
description: "Maple Mono v7.9 等宽编程字体是什么——设计目标、版本演进、与 JetBrains Mono/Fira Code 的定位区别"
tags: ["maple-mono", "font", "introduction", "typography", "monospace"]
sources:
  - id: README-MAPLE
    resource: "README.md"
    description: "项目说明、功能列表、下载与使用方法"
  - id: CONFIG-SCHEMA
    resource: "source/schema.json"
    description: "构建配置 JSON Schema 完整声明"
  - id: CONFIG-JSON
    resource: "config.json"
    description: "默认构建配置"
prerequisites: []
next:
  - "01-build-pipeline"
related:
  - "../examples/basic-build.md"
status: draft
---

# Maple Mono 简介

## Maple Mono 是什么

Maple Mono 是一款**专为编程体验优化的开源等宽字体**，由 subframe7536 自 2020 年代起开发。v7 版本是一次完全重制，引入了变量字体格式和完整的构建源文件。

**设计目标**：让编码更流畅——圆润的转角、优化的连字、圆角斜体字母（`f i j k l x y`）、清晰的 Nerd Font 图标集成。

**版本演进**：
- v1-v6：静态格式字体，广泛发行
- **v7（当前）**：完全重制，变量字体（Variable Font），支持无限字重（100-900），源码构建系统公开

**许可证**：SIL Open Font License 1.1（可自由使用、修改、分发）

## 核心特性

| 特性 | 说明 |
|------|------|
| ✨ Variable | 变量字体格式，字重可在 100-900 之间连续调节 |
| ☁️ 优化字形 | 圆角 `@ $ % & Q ->`、斜体草书 `f i j k l x y` |
| 💪 智能连字 | 大量上下文感知连字（`=>` `!=` `->` `//` `>=` 等） |
| 🎨 Nerd Font | 一等公民支持，终端图标无缝集成 |
| 🔨 定制化 | 通过 config.json / CLI 参数自由启用或禁用 OpenType 特征 |
| 🇨🇳 中日韩 | 基于 Resource Han Rounded 的中日韩字形完整支持 |

## 与同类字体的定位对比

| 对比项 | Maple Mono | JetBrains Mono | Fira Code | Victor Mono |
|--------|-----------|----------------|-----------|------------|
| 变量字体 | ✅ v7+ | ✅ | ❌ | ❌ |
| Nerd Font | ✅ 一等公民 | ✅ 可选补丁 | ✅ 可选补丁 | ✅ 可选补丁 |
| 中文支持 | ✅ 内置 CN 版 | ❌ | ❌ | ❌ |
| 构建系统 | ✅ Python DSL | 闭源 | 闭源 | 闭源 |
| 自定义特征 | ✅ 三模式冻结 | 有限 | 有限 | 有限 |
| 斜体风格 | 草书（手写感） | 倾斜 | 倾斜 | 草书 |
| 圆角处理 | 全局圆角 | 直角为主 | 直角 | 部分圆角 |

**核心差异**：Maple Mono 是少数**公开完整构建系统源码**的编程字体。这意味着你可以：
- 定制 OpenType 特征规则（Python 代码）
- 冻结特征到字形表
- 调整字重映射
- 直接修改 AST 风格的查找表生成逻辑

## 构建系统全貌

Maple Mono 的构建系统是一个**纯 Python 项目**，技术栈：

```
Python 3.10+
├── foundrytools-cli (ftcli)     ← 字体批处理（字形修正、dehint、converter）
├── fontTools (TTLib)            ← 低水平字体表操作
├── ttfautohint                  ← 自动 hinting
├── skia-pathops                 ← 路径运算
└── glyphslib                    ← Glyphs 文件支持
```

构建系统入口有两个：
- **`build.py`**：主构建流水线（字体变换 + 输出）
- **`task.py`**：开发辅助子命令（NF 基座更新、.fea 文件生成、版本发布等）

## 基本使用

最简单的本地构建：

```bash
git clone https://github.com/subframe7536/maple-font --depth 1 -b variable
pip install -r requirements.txt
python build.py
```

详见 [基本构建示例](../examples/basic-build.md)。

## 学习路径

```
00-introduction（本文档）
  → 01-build-pipeline：理解四阶段构建流水线
    → 02-config-system：配置驱动的双层架构
      → 03-feature-system：OpenType Feature 三层结构
        → 04-feature-ast-generator：Python AST 生成器
          → 05-freeze-mechanism：特征冻结三模式
            → 06-nerd-font-patching：NF 补丁策略
              → 07-cn-font-merge：中英合并
                → 08-parallel-build：并行流水线
```
