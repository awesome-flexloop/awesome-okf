---
okf_version: "0.2"
type: group
title: "🔧 通用开发工具"
description: "不绑定特定生态、可独立服务任意项目的通用开发工具"
---

# 🔧 通用开发工具（Tooling）

本组存放**不依附于特定大生态、可独立服务任意项目**的通用开发工具。

> **准入标准**：如果一个工具主要服务于某个特定生态（如 conda-pack 主要服务 conda 用户、sphinx-docker-images 主要服务 sphinx 用户），则归入对应生态组；只有跨生态、可独立使用的工具才归入本组。

## 学习路径

按 **项目脚手架 → 执行引擎 → 任务集合 → CI 集成** 的工具链顺序学习：

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 1 | [ninja](ninja/index.md) | Ninja 极速构建系统——Node-Edge二分图依赖模型、关键路径并行调度、mtime增量构建、depfile头依赖追踪、dyndep动态依赖、CMake/Meson后端引擎 |
| 2 | [copier](copier/index.md) | 项目模板渲染与更新——Jinja2 沙箱渲染、交互式问卷、Git 版本管理、三向合并更新、条件任务/迁移、Python API 集成 |
| 3 | [pyinvoke](pyinvoke/index.md) | PyInvoke 任务自动化引擎——Pythonic 的 CLI 任务定义、Context 对象、Collection 命名空间、Runner 执行模型、Watcher 文件监控、Terminal IO |
| 4 | [invocations](invocations/index.md) | PyInvoke 官方任务集合——打包发布、测试（pytest）、文档（Sphinx）、CI 自动化、代码检查格式化、自动文档组合模式 |
| 5 | [github-problem-matcher](github-problem-matcher/index.md) | GitHub Actions 错误注解——Problem Matcher JSON 模式、正则捕获组、测试验证、将编译器/linter 错误在 PR 中高亮显示 |

```{toctree}
:hidden:

ninja/index
copier/index
pyinvoke/index
invocations/index
github-problem-matcher/index
nuitka/index
```
