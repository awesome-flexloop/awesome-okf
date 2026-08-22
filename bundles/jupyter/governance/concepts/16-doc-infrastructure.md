---
type: Concept
title: "文档基础设施与构建系统"
description: "Jupyter治理文档使用MyST Markdown编写，通过nox构建系统自动生成HTML，领导层数据存于YAML文件中，通过GitHub Pages自动部署到jupyter.org/governance。"
tags: [infrastructure, myst, nox, documentation-build, github-pages, data-driven]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: infra-history
    resource: /references/infrastructure-history-source.md
    title: "基础设施与历史信源"
---

## 技术栈概览

Jupyter 治理文档的技术栈：

```
┌─────────────────────────────────────────────────┐
│  docs/                          文档源文件       │
│  ├── *.md (MyST Markdown)                        │
│  ├── conduct/                                    │
│  ├── elections/                                  │
│  ├── _data/        YAML 结构化数据（领导层等）     │
│  └── _static/      静态资源（图片/Logo）          │
├─────────────────────────────────────────────────┤
│  nox -s docs      构建任务（nox + MyST）         │
├─────────────────────────────────────────────────┤
│  _build/html/     构建输出（HTML）               │
├─────────────────────────────────────────────────┤
│  GitHub Pages     自动部署 → jupyter.org/governance│
└─────────────────────────────────────────────────┘
```

## MyST Markdown

文档使用 [MyST](https://mystmd.org)（Markedly Structured Text）格式编写：
- MyST 是 CommonMark Markdown 的超集
- 支持 Sphinx 式的角色（roles）和指令（directives）
- 专为技术文档设计，支持交叉引用、脚注、表格等高级功能
- 可输出为 HTML、PDF、LaTeX 等多种格式

## Nox 构建系统

使用 [nox](https://nox.thea.codes) 作为任务自动化工具：

```bash
# 安装依赖
pip install nox

# 构建 HTML 文档
nox -s docs

# 启动热重载开发服务器（文件变化自动重建）
nox -s docs-live
```

`noxfile.py` 定义了所有构建任务，确保构建环境的可重复性。

## 数据驱动的领导层页面

领导层信息（EC 成员、SSC 成员、各委员会成员等）不硬编码在 Markdown 中，而是存储在 `docs/_data/` 目录下的 YAML 文件中：

```
docs/_data/
├── executive_council.yml     # EC 成员数据
├── ssc.yml                    # SSC 成员数据
├── distinguished_contributors.yml  # DC 名单
└── ...（其他机构数据）
```

这种数据驱动的方式确保：
- 人员变更时只需更新 YAML，无需修改文档正文
- 数据可被其他工具/页面复用
- 避免多处维护导致的不一致

## 文档许可证

治理文档采用 **CC0**（Creative Commons Zero）许可证——在法律允许范围内，Project Jupyter 放弃所有版权和邻接权，文档属于公有领域。这意味着任何人都可以自由复制、修改、分发这些文档，无需申请许可。

## 目录结构

```
governance/
├── README.md                  # 仓库说明、构建指南
├── noxfile.py                 # Nox 构建配置
├── docs/
│   ├── index.md               # 文档首页
│   ├── overview.md            # 治理模型总览
│   ├── executive_council.md   # EC 文档
│   ├── software_steering_council.md  # SSC 文档
│   ├── decision_making.md     # 决策流程
│   ├── software_subprojects.md  # 子项目体系
│   ├── standing_committees_and_working_groups.md  # 委员会与工作组
│   ├── conduct/               # 行为准则文档
│   │   ├── code_of_conduct.md
│   │   └── enforcement.md
│   ├── elections/             # 选举流程与工具
│   │   ├── election_process.md
│   │   └── process-votes.py   # 计票脚本
│   ├── trademarks.md          # 商标政策
│   ├── license_use.md         # 许可证使用
│   ├── distinguished_contributors.md  # DC 制度
│   ├── papers.md              # 学术论文流程
│   ├── newsubprojects.md      # 新子项目准入
│   ├── _data/                 # YAML 结构化数据
│   ├── _static/               # 静态资源
│   └── archive/               # 归档的旧治理文档
│       └── governance.md      # BDFL时代旧文档
```

## 在线发布

文档通过 GitHub Pages 自动部署到：
**https://jupyter.org/governance**

每次推送到 main 分支时，CI/CD 流水线自动运行 `nox -s docs` 构建并部署。

## 文档治理

文档本身也是 Jupyter 治理的一部分：
- 文档修改通过 GitHub PR 流程
- 涉及治理模型变更的修改需 EC+SSC 双重批准
- 欢迎社区贡献者通过 PR 提交改进
- 文档使用 CC0 许可证，鼓励翻译和复用

## 反常识要点

- **CC0 而非 CC-BY**：治理文档使用最宽松的 CC0（公有领域奉献），而非需要署名的 CC-BY。这反映了 Jupyter 对治理知识开放共享的态度——治理模式应该被自由学习和复制。
- **领导层数据与文档分离**：人员频繁变动但文档结构稳定，YAML 数据驱动避免了频繁修改 Markdown 正文。
- **治理文档也有版本控制**：旧治理模型（BDFL时代）文档被归档在 `docs/archive/` 而非删除，保留了历史演进的完整记录。
- **计票脚本放在文档仓库**：选举用的 Python 脚本 `process-votes.py` 与文档一起存放在 governance 仓库中，而非单独的工具仓库，确保文档和工具的一致性。

## 相关概念

- [Jupyter Governance 仓库简介](/concepts/00-introduction.md)
- [从 BDFL 到分布式治理的历史演进](/concepts/02-history-and-evolution.md)
- [选举与投票机制](/concepts/10-elections-and-voting.md)
- [软件子项目体系](/concepts/06-software-subprojects.md)
