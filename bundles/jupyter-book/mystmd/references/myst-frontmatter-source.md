---
type: Reference
title: myst-frontmatter Frontmatter 解析源码信源
description: myst-frontmatter 包导出的 20+ 个 frontmatter 子模块索引，包括 affiliations、biblio、contributors、exports、numbering、page、project、site 等。
tags: [mystmd, frontmatter, metadata, yaml, bibliography]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-frontmatter/src/index.ts"
    facts: [F-094]
---

## 源码位置

- `myst-frontmatter/src/index.ts` — 包导出入口
- 各子模块目录：
  - `affiliations/` — 作者所属机构
  - `biblio/` — 参考文献/书目
  - `contributors/` — 贡献者/作者
  - `downloads/` — 下载链接
  - `exports/` — 导出配置
  - `funding/` — 资助信息
  - `jupytext/` — Jupytext 格式支持
  - `kernelspec/` — Jupyter 内核规格
  - `licenses/` — 许可证
  - `numbering/` — 编号配置
  - `page/` — 页面级 frontmatter
  - `project/` — 项目级 frontmatter
  - `references/` — 交叉引用配置
  - `settings/` — 设置
  - `site/` — 站点级 frontmatter
  - `socials/` — 社交链接
  - `thebe/` — Thebe（交互式代码执行）配置
  - `utils/` — 工具函数
  - `venues/` — 出版/会议信息
  - `math/` — 数学配置
  - `execute/` — 代码执行配置

## 导出模块清单

| 模块 | 内容 |
|------|------|
| affiliations | 机构关联信息解析与验证 |
| biblio | 参考文献数据结构与处理 |
| contributors | 作者/贡献者信息（含 ORCID、角色等） |
| downloads | 下载项配置（PDF、源文件等） |
| exports | 导出格式配置（tex/pdf/docx/jats/md/typst/meca 等） |
| funding | 资助信息（基金号、机构等） |
| jupytext | Jupytext 笔记本格式 frontmatter |
| kernelspec | Jupyter 内核规格（名称、显示名、语言） |
| licenses | 开源许可证标识 |
| numbering | 标题/公式/图表编号配置 |
| page | PageFrontmatter 页面元数据类型与验证 |
| project | ProjectFrontmatter 项目元数据类型与验证 |
| references | 引用配置（intersphinx、bib 文件等） |
| settings | 构建设置（文件夹路径等） |
| site | SiteFrontmatter 站点元数据类型与验证 |
| socials | 社交媒体链接 |
| thebe | Thebe 交互式执行配置 |
| utils | fillProjectFrontmatter 等合并工具 |
| venues | 出版/会议场地信息 |
| math | 数学配置（宏、dollar 分隔符等） |
| execute | 代码执行配置 |

## 关键函数

| 函数 | 说明 |
|------|------|
| `fillProjectFrontmatter` | 合并预定义 frontmatter 与文件 frontmatter |
| 各模块 validateXxx 函数 | 对应模块的验证器 |

## Frontmatter 类型层级

```
PageFrontmatter (页面级)
├── title, description, short_title
├── authors/contributors/affiliations
├── funding/license
├── bibliography/references
├── math/numbering
├── exports/downloads
├── kernelspec/jupytext
├── tags, thumbnail, banner
└── settings/execute/thebe

ProjectFrontmatter (项目级，扩展 PageFrontmatter)
├── ... PageFrontmatter 所有字段
├── github/repository
├── bibliography (项目级)
├── requirements
└── id

SiteFrontmatter (站点级)
├── title, description
├── logo, favicon
├── domains
└── template 相关字段
```
