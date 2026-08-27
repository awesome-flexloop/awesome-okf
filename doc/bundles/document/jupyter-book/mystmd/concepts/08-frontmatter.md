---
type: concept
title: Frontmatter 元数据系统
description: MyST 通过 YAML frontmatter 定义页面、项目和站点三个层级的元数据，myst-frontmatter 包提供 20+ 子模块分别处理 affiliations/contributors/biblio/numbering/kernelspec 等各类元数据。
tags: [mystmd, frontmatter, yaml, metadata, bibliography]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-frontmatter-source.md"
    facts: [F-094]
  - path: "/references/myst-config-source.md"
    facts: [F-085, F-088, F-092]
---

## Frontmatter 概述

Frontmatter 是文档开头的 YAML 元数据块，用于描述文档的标题、作者、日期、许可证、参考文献配置等。MyST 支持三个层级的 frontmatter：

```
SiteFrontmatter (站点级，myst.yml)
    └── ProjectFrontmatter (项目级，myst.yml 中 project 字段)
          └── PageFrontmatter (页面级，每个 .md/.ipynb 文件的 YAML 头)
```

## 页面级 Frontmatter（PageFrontmatter）

每个 MyST Markdown 文件可以以 YAML frontmatter 开头：

```markdown
---
title: 文档标题
short_title: 短标题
description: 文档描述
authors:
  - name: 张三
    orcid: 0000-0000-0000-0000
    affiliations:
      - univ1
affiliations:
  - id: univ1
    name: 某大学
    department: 计算机系
date: 2024-01-15
license: CC-BY-4.0
bibliography: references.bib
math:
  '\R': '\mathbb{R}'
numbering:
  figure: true
  equation: true
tags:
  - tag1
  - tag2
thumbnail: thumbnail.png
banner: banner.png
---

# 文档内容
```

### PageFrontmatter 关键字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 文档标题 |
| `short_title` | string | 短标题（用于导航/面包屑） |
| `description` | string | 文档描述/摘要 |
| `authors` | Contributor[] | 作者列表 |
| `affiliations` | Affiliation[] | 机构列表 |
| `date` | string\|Date | 发布日期 |
| `license` | License | 许可证 |
| `funding` | Funding[] | 资助信息 |
| `bibliography` | string\|string[] | 参考文献文件路径 |
| `math` | Record<string,string> | 数学宏定义 |
| `numbering` | NumberingConfig | 编号配置 |
| `tags` | string[] | 标签 |
| `thumbnail` | string | 缩略图路径 |
| `banner` | string | 横幅图片路径 |
| `exports` | Export[] | 导出配置 |
| `downloads` | Download[] | 下载链接 |
| `kernelspec` | KernelSpec | Jupyter 内核规格 |
| `jupytext` | JupytextConfig | Jupytext 格式配置 |
| `thebe` | ThebeConfig | Thebe 交互式执行配置 |
| `execute` | ExecuteConfig | 代码执行配置 |
| `references` | ReferencesConfig | 引用/链接配置 |
| `venues` | Venue[] | 出版/会议信息 |
| `socials` | Social[] | 社交链接 |
| `doi` | string | 数字对象标识符 |
| `open_access` | boolean | 是否开放获取 |
| `subject` | string | 学科分类 |
| `github` | string | GitHub 仓库 URL |
| `repository` | RepositoryConfig | 代码仓库配置 |
| `parts` | Record<string,string> | 文档部分（abstract/acknowledgments 等） |

## 项目级 Frontmatter（ProjectFrontmatter）

在 myst.yml 的 `project` 字段中定义，继承 PageFrontmatter 的所有字段，并增加：

| 字段 | 类型 | 说明 |
|------|------|------|
| `remote` | string | 远程项目 URL |
| `index` | string | 首页文件路径 |
| `exclude` | string[] | 排除的文件模式 |
| `plugins` | PluginInfo[] | 插件列表 |
| `error_rules` | ErrorRule[] | 错误级别覆盖规则 |
| `id` | string | 项目 ID |
| `requirements` | RequirementsConfig | 依赖文件配置 |
| `github` | string | 项目 GitHub URL |

项目级 frontmatter 作为该项目所有页面的默认值，页面级 frontmatter 会覆盖项目级设置。

## 站点级 Frontmatter（SiteFrontmatter）

在 myst.yml 的 `site` 字段中定义：

```yaml
site:
  title: 我的文档站点
  description: 一个使用 MyST 构建的文档站点
  logo: logo.png
  favicon: favicon.ico
  domains:
    - example.com
  nav:
    - title: 首页
      url: /
    - title: 指南
      children:
        - title: 快速开始
          url: /quickstart
  actions:
    - title: 下载 PDF
      url: /book.pdf
      format: pdf
  projects:
    - slug: guide
      path: .
  template: book-theme
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 站点标题 |
| `description` | string | 站点描述 |
| `logo` | string | Logo 图片路径 |
| `favicon` | string | 网站图标路径 |
| `domains` | string[] | 绑定的域名列表 |
| `nav` | SiteNavItem[] | 导航菜单（支持嵌套） |
| `actions` | SiteAction[] | 操作按钮 |
| `template` | string | 站点模板名称 |

## Frontmatter 子模块

myst-frontmatter 将各类元数据拆分为独立子模块：

| 模块 | 处理内容 | 核心类型 |
|------|---------|---------|
| `contributors` | 作者/贡献者 | Contributor（name/orcid/roles/corresponding/email/url） |
| `affiliations` | 机构关联 | Affiliation（id/name/department/address/city/country/url） |
| `biblio` | 参考文献 | BiblioConfig（bibliography/references/intersphinx） |
| `exports` | 导出配置 | Export（format/template/output/contents） |
| `downloads` | 下载链接 | Download（url/title/filename/format） |
| `funding` | 资助信息 | Funding（award/name/investigator/source/funder） |
| `licenses` | 许可证 | License（id/name/url） |
| `numbering` | 编号配置 | NumberingConfig（heading_X/figure/table/equation/code） |
| `kernelspec` | Jupyter 内核 | KernelSpec（name/display_name/language） |
| `jupytext` | Jupytext 格式 | JupytextConfig（formats/text_representation） |
| `thebe` | Thebe 交互 | ThebeConfig（kernelName/binderUrl/live/...） |
| `socials` | 社交链接 | Social（kind/url） |
| `venues` | 出版/会议 | Venue（title/url/doi/series/volume/issue） |
| `math` | 数学配置 | MathConfig（macros/dollars） |
| `execute` | 代码执行 | ExecuteConfig（allow_errors/timeout/notebook/...） |
| `references` | 引用配置 | ReferencesConfig（intersphinx/biblio） |
| `settings` | 构建设置 | Settings（folders/output/...） |
| `page` | 页面元数据 | PageFrontmatter 验证与类型 |
| `project` | 项目元数据 | ProjectFrontmatter 验证与类型 |
| `site` | 站点元数据 | SiteFrontmatter 验证与类型 |
| `utils` | 工具函数 | fillProjectFrontmatter 等 |

## Frontmatter 提取流程

1. **解析阶段**：markdown-it 的 frontMatterPlugin 将 `---...---` 块解析为 front_matter Token
2. **AST 构建**：tokensToMyst 将 front_matter Token 标记为 `__delete__`（从 AST 树移除），但保留 Token 内容
3. **提取阶段**：`getFrontmatter(vfile, mdast, preFrontmatter)` 从 VFile 中提取并解析 YAML
4. **合并阶段**：页面 frontmatter 与项目 preFrontmatter 合并（页面优先）
5. **H1 标题合并**：如果 frontmatter 无 title 但文档首个节点是 H1，使用 H1 文本作为 title
6. **验证阶段**：各子模块 validateXxx 函数验证字段合法性，错误上报到 VFile
7. **填充阶段**：fillFrontmatter/finalizeFrontmatter transform 补全默认值和派生字段

## fillProjectFrontmatter

`fillProjectFrontmatter(predefined, received)` 工具函数用于合并两层 frontmatter：
- predefined：项目级/配置级默认值
- received：页面级/文件级值
- 合并策略：received 优先；数组合并（去重）；对象递归合并；null 清除预定义值

## 相关概念

- [配置系统](10-configuration-system.md)
- [公共类型系统](04-myst-common-types.md)
- [错误处理与规则 ID](05-error-handling.md)
- [基本解析示例](../examples/00-basic-parsing.md)
