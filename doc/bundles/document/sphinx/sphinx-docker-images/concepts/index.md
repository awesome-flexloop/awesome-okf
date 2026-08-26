# 概念文档索引

## 入门

| 文档 | 说明 |
|------|------|
| [00. Sphinx Docker 镜像项目介绍](00-introduction.md) | 项目是什么、提供哪些镜像、解决什么问题 |
| [01. 5 分钟快速上手](01-getting-started.md) | 拉取镜像→创建项目→构建 HTML/PDF 的完整入门教程 |

## 核心架构

| 文档 | 说明 |
|------|------|
| [02. 三镜像架构解析](02-image-architecture.md) | sphinx/sphinx-latexpdf/docker-ci 三层设计与选型决策 |
| [03. Base 镜像详解](03-base-image.md) | 基础镜像逐层构建解析、体积优化策略、最佳实践 |
| [04. LaTeX/PDF 镜像详解](04-latexpdf-image.md) | TeXLive 包选择、CJK 多语言支持、中文 PDF 配置要点 |
| [05. CI 测试镜像详解](05-ci-image.md) | Ubuntu 基础、全工具链配置、日构建策略、与用户镜像差异 |

## 高级主题

| 文档 | 说明 |
|------|------|
| [06. 构建流水线详解](06-build-pipeline.md) | GitHub Actions 双工作流设计、矩阵构建、多架构、双 Registry |
| [07. 自定义扩展与最佳实践](07-customization.md) | 创建自定义镜像、docker-compose、性能优化、常见问题 |

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-image-architecture
03-base-image
04-latexpdf-image
05-ci-image
06-build-pipeline
07-customization
```
