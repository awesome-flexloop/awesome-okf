---
type: Playbook
title: Awesome OKF for Xuanspace 智能体协作入口
sources:
  - id: xuanspace-agents
    resource: https://github.com/xinetzone/xuanspace
    title: XuanSpace（玄境）智能体协作入口模板
---

# Awesome OKF for Xuanspace 智能体协作入口

> **🚨 启动协议（PRIORITY ZERO — 所有智能体必须在收到任务后立即执行）**
>
> **步骤 1**：读取本文件全文
>
> **步骤 2**：按「上下文路由表」确定本次任务需要读取的规范文件
> - **步骤 2.3**（内容敏感度预检·必做）：在读取规范文件之前，先判定分析对象/产出物的内容敏感度级别：
>   - **公开内容（Public）**：公开发布的开源知识、官方文档、公开文章等 → 标准工作流，存放于 `doc/bundles/` 或 `doc/`
>   - **私域内容（Private）**：个人笔记、内部讨论、含访问控制的内容 → 跳过公开规划，在用户指定目录执行
>   - 不确定时默认按私域处理或向用户确认
>
> **步骤 3**：读取对应的规范文件（按需读取，不要一次加载全部）
>
> **步骤 3.5**（自检·必做）：在执行任何操作之前，逐项确认：
> - □ 是否已读取上下文路由表中与当前任务直接相关的入口？
> - □ 是否已完成内容敏感度预检（步骤 2.3）？产出物路径是否与级别匹配？
> - □ 是否明确目标文档的存放位置（`doc/bundles/` 或 `doc/`）？
> - □ 涉及知识文档时，是否已读取 frontmatter 规范？
> - □ 涉及新增/修改 bundle 时，是否了解 toctree 完整性要求？
> - □ 若从 SpecWeave 主项目路由进入，是否已了解本项目的轻量定位（无复杂子命令体系）？
>
> **步骤 4**：在规范指导下执行任务
>
> ⚠️ **禁止在完成步骤 1-3.5 之前生成任何产出物。跳过此协议将导致文档路径错误、格式不符合规范。**

## 项目概述

**awesome-okf-xs** 是 Xuanspace（玄境）项目的**开源知识格式（Open Knowledge Format，OKF）文档库**。

- **定位**：以 [XuanSpace](https://github.com/xinetzone/xuanspace) 为基底（内容来源与规范模板），将玄境项目的知识资产以 OKF 格式组织、存储与发布
- **核心理念**：技术为器、思想为道，器以载道——xuanspace 承载"器"（代码与工具），本库承载"道"（知识与思想）
- **知识形态**：文档、复盘、洞察、模式、最佳实践等，统一以 OKF bundle 组织
- **嵌套关系**：本项目是 SpecWeave 的 projects/ 区域下的第一方子项目（git submodule），通过 [projects/AGENTS.md](../AGENTS.md) 路由进入；本项目规范自治，保持轻量

本文件是 awesome-okf-xs 文档库 AI 智能体的最高优先级入口与上下文路由。所有智能体在启动时必须首先读取本文件，依据上下文路由表定位到具体的 `.agents/` 规范后执行任务。

## 核心规范入口表

| 规范 | 入口 | 说明 |
|---|---|---|
| 📁 规范目录索引 | [.agents/README.md](.agents/README.md) | .agents/ 目录结构与文件清单 |
| 🚀 入门指南 | [.agents/ONBOARDING.md](.agents/ONBOARDING.md) | 快速开始、常用操作、文档库结构速览 |
| 📜 全局核心规则 | [.agents/global-core-rules.md](.agents/global-core-rules.md) | 启动协议、内容敏感度分流、OKF 文档规范、构建验证 |
| 🧭 上下文路由表 | [.agents/context-routing.md](.agents/context-routing.md) | 任务类型→必读规范映射表 |
| 📄 文档元数据规范 | [.agents/rules/frontmatter.md](.agents/rules/frontmatter.md) | OKF v0.2 YAML frontmatter 规范（含 Sphinx 构建兼容性） |

## 目录结构说明

```
awesome-okf-xs/
├── doc/                # Sphinx 文档工程（源文件目录）
│   ├── bundles/        # OKF bundle 文档（结构化知识包）
│   ├── _static/        # 静态资源（CSS/图片等）
│   ├── conf.py         # Sphinx 构建配置（含 frontmatter 日期兼容性钩子）
│   └── index.md        # 文档首页
├── tasks/              # Invoke 任务包（命名空间组织）
│   ├── __init__.py     # 命名空间入口
│   ├── docs.py         # 文档构建任务（build/clean/browse/...）
│   └── gates.py        # CI 质量门任务（utf8/toctrees）
├── scripts/            # CI 检查脚本（被 tasks/gates.py 调用）
│   ├── check-toctrees.py  # toctree 完整性检查（含 bundle-root 检测与自检探针）
│   ├── check-utf8.py      # UTF-8 编码检查
│   └── scan-history-utf8.py  # Git 历史 UTF-8 扫描
├── .agents/            # AI 智能体规范目录（本规范所在目录）
├── .github/workflows/  # CI/CD 工作流（GitHub Pages 自动部署）
├── pyproject.toml      # 项目元数据与依赖声明
├── AGENTS.md           # 本文件 - 智能体入口
└── README.md           # 项目说明
```

### 目录用途

| 目录/文件 | 适用场景 |
|---|---|
| `doc/bundles/` | 以 OKF bundle 形式组织的结构化知识文档（核心内容区） |
| `doc/_static/` | Sphinx 静态资源（CSS、图片等） |
| `tasks/` | Invoke 任务定义（`invoke build` 构建、`invoke gates.all` 跑质量门） |
| `scripts/` | CI 质量门底层检查脚本（一般通过 `invoke gates.*` 间接调用） |

## 常用命令速查

| 操作 | 命令 | 说明 |
|---|---|---|
| 构建 HTML 文档 | `invoke build` | Sphinx 构建输出到 `_build/html/` |
| 清理构建产物 | `invoke clean` | 清理 `_build/` 目录 |
| 运行全部质量门 | `invoke gates.all` | UTF-8 编码 + toctree 完整性检查 |
| 仅检查 toctree | `invoke gates.toctrees` | 验证无断链、无孤立文档、bundle 根 index 完整 |
| 仅检查 UTF-8 | `invoke gates.utf8` | 验证所有文件 UTF-8 编码无 BOM |
| 本地预览文档 | `invoke browse` | 构建后启动本地服务器预览 |

## 关键规则速查

> 以下规则是高频操作必须遵守的硬性约束，详细说明见对应规范文件。

- **Bundle 导航完整性**：含子目录的 bundle 根目录必须生成 `index.md`，并以 `{toctree}` 引用全部内容文档；新增/迁移 bundle 后必须运行 `invoke gates.toctrees` 验证
- **修复落地验证**：修复完成后必须用 `git diff`/`git status` 核对变更实际写入，并运行构建/测试验证；禁止仅凭过程描述自认为"已完成"
- **Frontmatter 日期兼容性**：OKF v0.2 的裸日期格式（如 `stale_after: 2026-09-23`）在 Sphinx 构建时由 `doc/conf.py` 的钩子自动处理，无需手动加引号
- **路径引用**：Markdown 交叉引用使用相对路径，禁止 `file:///` 绝对路径
- **派生产物溯源**：源自外部（如 xuanspace 或其他项目）的知识文档须在 frontmatter 中标注 `sources` 字段

## 文档规范要点

- **语言**：正文使用中文，文件名使用 kebab-case 纯英文
- **格式**：Markdown，遵循 OKF v0.2 YAML frontmatter 规范（详见 [.agents/rules/frontmatter.md](.agents/rules/frontmatter.md)）
- **知识组织**：结构化的知识文档优先使用 OKF bundle 组织，存放在 `doc/bundles/` 下
- **路径引用**：Markdown 交叉引用使用相对路径，禁止 `file:///` 绝对路径
- **派生产物溯源**：源自外部（如 xuanspace 或其他项目）的知识文档须在 frontmatter 中标注 `sources` 字段
