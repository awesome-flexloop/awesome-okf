# jupyter_releaser

> **Jupyter Releaser**：基于 GitHub Actions 的 Python/npm 包发布工具库，用于 Jupyter 生态系统的标准化包发布流程。

- **源码路径**：`d:\spaces\SpecWeave\external\libs\jupyter\jupyter_releaser`
- **PyPI**：<https://pypi.org/project/jupyter-releaser/>
- **GitHub**：<https://github.com/jupyter-server/jupyter_releaser>

## 文档结构

```
jupyter_releaser/
├── index.md              ← 本文件（入口）
├── log.md                ← 生成日志
├── facts.md              ← R阶段事实清单（128条编号事实）
├── insights.md           ← I阶段架构洞察（5个核心洞察+知识地图）
├── concepts/             ← 概念文档
│   ├── index.md          ← 概念索引
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-architecture-overview.md
│   ├── 03-cli-commands.md
│   ├── 04-config-and-hooks.md
│   ├── 05-release-pipeline.md
│   ├── 06-python-npm-dual.md
│   ├── 07-changelog-system.md
│   ├── 08-dry-run-and-mock.md
│   ├── 09-github-actions.md
│   └── 10-authentication.md
├── examples/             ← 示例文档
│   ├── index.md
│   ├── 01-basic-release-workflow.md
│   ├── 02-custom-hooks-config.md
│   └── 03-dry-run-testing.md
└── references/           ← 源码信源
    ├── index.md
    ├── cli-source.md
    ├── lib-source.md
    ├── util-source.md
    └── actions-source.md
```

## 学习路径

### 新手上路（入门篇）

1. 读 [concepts/00-introduction.md](concepts/00-introduction.md) — 了解 jupyter_releaser 是什么
2. 读 [concepts/01-getting-started.md](concepts/01-getting-started.md) — 快速接入
3. 跟着 [examples/01-basic-release-workflow.md](examples/01-basic-release-workflow.md) 走一遍发布流程

### 深入理解（核心篇）

4. 读 [concepts/02-architecture-overview.md](concepts/02-architecture-overview.md) — 理解双层架构
5. 读 [concepts/03-cli-commands.md](concepts/03-cli-commands.md) — 掌握 CLI 原语
6. 读 [concepts/04-config-and-hooks.md](concepts/04-config-and-hooks.md) — 学习自定义配置
7. 读 [concepts/05-release-pipeline.md](concepts/05-release-pipeline.md) — 深入三阶段流水线
8. 读 [concepts/06-python-npm-dual.md](concepts/06-python-npm-dual.md) — 理解双生态发布
9. 读 [concepts/07-changelog-system.md](concepts/07-changelog-system.md) — 掌握 Changelog 机制

### 进阶使用（进阶篇）

10. 读 [concepts/08-dry-run-and-mock.md](concepts/08-dry-run-and-mock.md) — 本地测试发布流程
11. 读 [concepts/09-github-actions.md](concepts/09-github-actions.md) — Actions 集成细节
12. 读 [concepts/10-authentication.md](concepts/10-authentication.md) — 认证体系配置
13. 参考 [examples/02-custom-hooks-config.md](examples/02-custom-hooks-config.md) — 配置定制化
14. 跟着 [examples/03-dry-run-testing.md](examples/03-dry-run-testing.md) — 做本地 dry-run 测试

### 源码溯源

15. 查阅 [references/](references/index.md) 中的信源文档，对照源码理解实现

## 核心设计思想

jupyter_releaser 的核心设计可以概括为：

1. **三阶段分离**：prep → populate → finalize，阶段间有人工审核
2. **CLI 原语 + Actions 编排**：底层是原子化 CLI 命令，上层是 Actions 工作流编排
3. **Hook + Skip + Options 三位一体**：配置系统提供正交的扩展机制
4. **双生态统一**：Python 和 npm 包在同一套流水线中发布
5. **Dry-Run 优先**：完整流程可在本地 Mock 环境中测试，不触碰真实服务
