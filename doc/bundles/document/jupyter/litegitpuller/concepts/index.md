# 概念文档索引

本目录包含 litegitpuller 的概念文档，按学习路径分为入门、核心和高级三个层次。

## 入门层（零基础）

| 文档 | 说明 |
|------|------|
| [00-简介](00-introduction.md) | litegitpuller是什么、核心特性、与nbgitpuller的区别 |
| [01-安装与快速开始](01-getting-started.md) | 安装方法、URL参数基础、第一个使用示例 |

## 核心层（理解原理）

| 文档 | 说明 |
|------|------|
| [02-整体架构](02-architecture.md) | 三层架构、模板方法模式、数据流向 |
| [03-GitPuller抽象基类](03-gitpuller-base.md) | clone流程、目录创建、文件上传、错误处理 |
| [04-平台Puller实现](04-platform-pullers.md) | GithubPuller/GitlabPuller API差异 |
| [05-扩展插件机制](05-extension-plugin.md) | JupyterLab插件结构、激活流程、nbgitpuller冲突检测 |

## 高级层（深入与扩展）

| 文档 | 说明 |
|------|------|
| [06-URL参数完整参考](06-url-parameters.md) | 所有参数详解、URL编码、链接生成 |
| [07-限制与注意事项](07-limitations.md) | API速率限制、文件冲突、不支持的特性 |
| [08-自定义Provider](08-custom-provider.md) | 添加新Git平台支持的完整指南 |

## 推荐学习路径

```
00-简介 → 01-安装与快速开始 → [动手试试examples/]
    ↓
02-整体架构 → 03-GitPuller基类 → 04-平台Puller → 05-扩展插件机制
    ↓
06-URL参数参考 → 07-限制注意事项 → 08-自定义Provider
```
