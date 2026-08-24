# 概念文档索引

按学习阶段排列，建议从入门篇开始顺序阅读。

## 入门篇

| 文档 | 简介 | 前置 |
|------|------|------|
| [00-introduction.md](00-introduction.md) | jupyter_releaser 简介、核心能力、三阶段流水线概览 | 无 |
| [01-getting-started.md](01-getting-started.md) | 两种接入模式、快速开始步骤、首次发布检查清单 | 00-introduction |

## 核心篇

| 文档 | 简介 | 前置 |
|------|------|------|
| [02-architecture-overview.md](02-architecture-overview.md) | 双层架构、模块职责划分、数据流方向 | 00, 01 |
| [03-cli-commands.md](03-cli-commands.md) | 19个CLI子命令、公共选项、ReleaseHelperGroup参数优先级 | 02 |
| [04-config-and-hooks.md](04-config-and-hooks.md) | 三源配置、hooks机制、skip跳过、options覆盖、Schema校验 | 03 |
| [05-release-pipeline.md](05-release-pipeline.md) | 三阶段流水线详解、阶段间数据传递、人工审核环节 | 02, 03 |
| [06-python-npm-dual.md](06-python-npm-dual.md) | Python/npm双生态构建发布、workspace支持、构建顺序约束 | 05 |
| [07-changelog-system.md](07-changelog-system.md) | HTML标记系统、PR聚合、backport处理、占位符机制 | 05 |

## 进阶篇

| 文档 | 简介 | 前置 |
|------|------|------|
| [08-dry-run-and-mock.md](08-dry-run-and-mock.md) | Dry-run模式、Mock GitHub Server、本地PyPI、端到端测试 | 05, 02 |
| [09-github-actions.md](09-github-actions.md) | Composite Actions、工作流模板、权限配置、Secrets管理 | 05, 10 |
| [10-authentication.md](10-authentication.md) | GitHub Token、PyPI OIDC Trusted Publishing、npm Token | 09 |

```{toctree}
:hidden:

00-introduction
01-getting-started
02-architecture-overview
03-cli-commands
04-config-and-hooks
05-release-pipeline
06-python-npm-dual
07-changelog-system
08-dry-run-and-mock
09-github-actions
10-authentication
```
