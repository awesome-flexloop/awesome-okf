---
type: Concept
title: Copier 简介
description: 项目模板渲染库——什么是 Copier、设计哲学、安装方法、与 Cookiecutter/Cruft 的对比
tags: [copier, introduction, template-rendering, project-scaffolding]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# Copier 简介

## 什么是 Copier

Copier 是一个 Python 库和命令行工具，用于**渲染项目模板**和**从模板生成/更新项目**。它通过 Jinja2 模板引擎将模板目录中的文件渲染为实际项目文件，并通过交互式问卷收集模板变量值，支持版本控制、模板更新迁移、任务钩子等高级特性。[^copier-source]

Copier 的核心能力包括：

- **模板渲染**：基于 Jinja2 沙箱环境渲染文件内容和路径名，支持 `.jinja` 后缀标记模板文件
- **交互式问卷**：通过 YAML 配置定义问题，支持多种类型（str/int/float/bool/json/yaml/secret）、条件显示、选项选择
- **VCS 版本管理**：原生支持 Git 模板仓库，自动克隆、标签版本检测、commit 追踪
- **项目更新**：不仅能从零生成项目，还能将已有项目更新到模板的新版本，智能合并冲突
- **任务执行**：模板可以定义生成前后执行的 shell 命令任务，以及跨版本迁移任务
- **扩展机制**：支持自定义 Jinja2 扩展、Ansible 过滤器、外部数据文件

Copier 的名字来源于 "copy" + "er"，但它远不止是文件复制工具——它是一个完整的项目生命周期管理工具。

## 设计哲学

Copier 遵循以下设计原则：

- **模板即代码（Template as Code）**：模板就是普通的目录结构，使用标准 Jinja2 语法，不需要学习专用 DSL
- **配置驱动（Configuration-driven）**：通过 `copier.yml` 单一配置文件定义所有模板行为（问题、任务、排除规则等）
- **更新优先（Update-first）**：不同于一次性脚手架工具，Copier 将项目更新视为一等公民，支持从旧版本模板智能迁移
- **安全沙箱（Safety by Default）**：默认使用 Jinja2 SandboxedEnvironment，不安全特性（自定义扩展、任务执行、迁移）需显式 `--trust`/`--UNSAFE` 授权
- **Git 原生（Git-native）**：深度集成 Git，支持标签版本检测、镜像缓存加速、dirty changes 处理、可执行位保留
- **懒加载（Lazy Evaluation）**：外部数据使用 LazyDict 延迟加载，避免循环依赖；模板路径通过 ContextVar 追踪渲染阶段

## 安装方法

Copier 通过 pip 安装，要求 Python 版本 ≥ 3.10：[^copier-source]

```bash
pip install copier
```

安装后获得 `copier` 命令行工具。验证安装：

```bash
copier --version
```

Copier 也可以作为 Python 库在代码中调用：

```python
from copier import run_copy, run_update, run_recopy
```

## 与 Cookiecutter 的对比

| 特性 | Copier | Cookiecutter |
|------|--------|-------------|
| 模板引擎 | Jinja2（沙箱模式） | Jinja2 |
| 配置格式 | `copier.yml`/`copier.yaml` | `cookiecutter.json` |
| 交互式问卷 | questionary 库，支持条件问题、类型验证、secret 输入 | 简单 prompt，类型支持较弱 |
| 项目更新 | ✅ 原生支持 `copier update`，含冲突解决和迁移任务 | ❌ 不支持（需 Cruft 扩展） |
| 版本管理 | Git 标签 PEP440 版本检测、镜像缓存、commit 追踪 | 无原生支持 |
| 任务钩子 | ✅ 前后任务、跨版本迁移任务、条件执行 | 有限的 pre/post gen hooks |
| 模板扩展 | 自定义 Jinja2 扩展、Ansible 过滤器 | 有限的扩展支持 |
| 路径模板化 | ✅ 文件名和目录名均可模板化，支持 yield 多文件生成 | 仅文件名支持模板 |
| 安全机制 | 沙箱环境、不安全特性需显式信任 | 默认信任模板 |
| 可执行位 | ✅ Git index 感知，跨平台保留可执行权限 | ❌ 不保留 |
| 符号链接 | ✅ 可选保留符号链接 | ❌ 不支持 |

## 与 Cruft 的对比

Cruft 是 Cookiecutter 的包装器，添加了项目更新能力。Copier 相比之下：

1. **一体化设计**：更新能力是核心功能而非附加层，迁移任务、冲突解决都是内置的
2. **更丰富的模板语法**：支持 `{% yield %}` 在路径名中生成多个文件、条件文件渲染
3. **更好的性能**：远程模板使用 Git 镜像缓存+worktree 机制，重复使用无需重新克隆
4. **更安全**：默认沙箱+信任机制，防止恶意模板执行任意代码
5. **更活跃的生态**：原生支持 Jinja2 扩展生态、Ansible 过滤器

## 适用场景

Copier 特别适合以下场景：

- **项目脚手架**：快速创建标准化的项目结构（如 Python 包、Web 应用、微服务）
- **模板分发**：通过 Git 仓库分发组织内部的项目模板
- **持续更新**：当模板改进时，已有项目可以智能合并更新而不丢失本地修改
- **多变量生成**：需要复杂条件逻辑和多类型变量的模板渲染场景
- **CI/CD 集成**：通过 `--defaults`、`--data`、`--overwrite` 等参数支持非交互式自动化

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [模板配置文件](02-template-configuration.md)
- [问题与答案系统](03-questions-and-answers.md)
- [Jinja2 模板渲染](04-jinja2-templating.md)
- [Copier 源码信源登记](/references/copier-source.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](/references/copier-source.md)。
