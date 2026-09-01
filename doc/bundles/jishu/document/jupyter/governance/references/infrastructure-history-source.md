---
type: Reference
title: "文档基础设施与历史文档源码"
description: "文档构建基础设施（noxfile.py、MyST配置、_data目录）和历史治理文档的信源登记。"
tags: [reference, source, myst, nox, infrastructure, history, bdfl]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: noxfile
    resource: https://github.com/jupyter/governance/blob/main/noxfile.py
    title: "noxfile.py"
  - id: readme
    resource: https://github.com/jupyter/governance/blob/main/README.md
    title: "README.md"
  - id: archive-gov
    resource: https://github.com/jupyter/governance/blob/main/docs/archive/governance.md
    title: "docs/archive/governance.md (archived BDFL model)"
  - id: teams-data
    resource: https://github.com/jupyter/governance/blob/main/docs/_data/jupyter-teams.yml
    title: "docs/_data/jupyter-teams.yml"
  - id: contributors-data
    resource: https://github.com/jupyter/governance/blob/main/docs/_data/contributors.yml
    title: "docs/_data/contributors.yml"
---

# 文档基础设施与历史信源

**原始文件路径**：
- `noxfile.py` - Nox 构建脚本
- `README.md` - 仓库说明
- `docs/archive/governance.md` - 旧版 BDFL 治理文档（归档）
- `docs/_data/jupyter-teams.yml` - 团队定义数据
- `docs/_data/contributors.yml` - 贡献者/成员数据
- `docs/src/team-members.mjs` - 团队成员渲染 JS 模块
- `docs/myst.yml` - MyST 配置
- `docs/package.json` - npm 依赖
- `requirements.txt` - Python 依赖
- `.github/workflows/` - CI/CD 工作流

**内容摘要**：

**文档构建基础设施**：
- 使用 MyST (mystmd.org) 作为文档引擎，构建为静态 HTML
- Nox 作为任务运行器，三个 session：
  - `docs`：安装依赖→npm install→myst build --strict --html
  - `docs-live`：热重载开发服务器
  - `redirects`：生成重定向（基URL https://jupyter.org/governance/）
- 默认 venv 后端为 uv，复用现有虚拟环境
- 领导层目录从 `docs/_data/` YAML 数据动态生成
- GitHub Pages 部署，通过 GitHub Actions 自动化
- `docs/_data/` 包含三个数据文件：jupyter-teams.yml、contributors.yml、organizations.yml
- `docs/src/team-members.mjs` 使用 MyST 指令从 YAML 渲染成员列表

**历史演进**：
- 2022年12月前：BDFL + Steering Council 模式
- BDFL：Fernando Pérez (@fperez)，2022年12月自愿卸任
- 旧 Steering Council 于2022年12月解散
- 有 bootstrapping 文档记录初始 EC 和子项目 Council 的创建过程
- 旧版 NumFOCUS Subcommittee 也已解散
- 根目录保留了旧版文件（governance.md→跳转页、people.md、newsubprojects.md等），新版在 docs/ 下

**许可证**：治理文档采用 CC0（公有领域奉献）

**关键事实锚点**：F-001, F-002, F-003, F-004, F-040, F-043, F-044, F-045
