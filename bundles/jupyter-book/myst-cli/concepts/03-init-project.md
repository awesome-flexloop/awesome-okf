---
type: concept
title: "Init 项目初始化"
description: "myst init 命令的项目初始化流程：配置生成、Jupyter Book升级、TOC自动生成与CI配置"
tags: [myst-cli, init, project-setup, configuration, jupyter-book]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/init/init.ts"
    facts: [F-039, F-040, F-041, F-042, F-043]
---

# Init 项目初始化

`myst init` 命令用于初始化 MyST 项目，生成配置文件、设置 Git 忽略规则，并提供交互式引导。

## 初始化流程

```
myst init
  ├─ 打印欢迎信息
  ├─ writeGitignore() 更新 .gitignore
  ├─ loadConfig() 加载现有配置
  ├─ 检测现有配置
  │   ├─ 已有配置 → 更新配置（添加缺失的 project/site 段）
  │   └─ 无配置 → 检测 legacy Jupyter Book → 生成新配置
  ├─ --write-toc → 自动生成 TOC 并写入配置
  ├─ 子命令处理（--gh-pages/--gh-curvenote/--readthedocs）
  └─ 交互式询问是否启动开发服务器
```

## 生成的配置文件

### myst.yml 结构

初始化生成的 `myst.yml` 包含：

```yaml
# See docs at: https://mystmd.org/guide/frontmatter
version: 1

project:
  id: <uuid-v4>
  # title:
  # description:
  # keywords: []
  # authors: []
  # github: <自动检测的仓库URL>
  # To autogenerate a Table of Contents, run "myst init --write-toc"

site:
  template: book-theme
  # options:
  #   favicon: favicon.ico
  #   logo: site_logo.png
```

### 配置段说明

| 段 | 生成条件 | 内容 |
|-----|---------|------|
| `version: 1` | 总是 | 配置格式版本 |
| `project:` | `--project` 或无参数 | 项目 UUID 和元数据字段 |
| `site:` | `--site` 或无参数 | 站点模板配置（默认 book-theme） |

- `--project` 仅生成 project 段
- `--site` 仅生成 site 段
- 无参数时同时生成 project 和 site 段

### Project ID

每个项目生成一个 UUID v4 作为唯一标识，用于：
- 跨项目引用解析
- 缓存隔离
- 站点部署标识

### GitHub URL 自动检测

初始化时通过 `getGithubUrl()` 检测 Git 远程仓库 URL，自动填充 `project.github` 字段。

## Git 集成

### .gitignore 更新

自动检测是否在 Git 仓库中，如果是则：
- 已存在 .gitignore：追加 `_build` 忽略规则
- 不存在 .gitignore：创建包含 `_build` 规则的 .gitignore

```gitignore
# MyST build outputs
_build
```

## Jupyter Book 升级

如果检测到 `_config.yml`（Jupyter Book 1.x 的配置文件），init 会：

1. 交互式询问用户是否升级
2. 执行 `upgradeJupyterBook()` 升级操作：
   - 术语表迁移（Sphinx-style → MyST-style glossaries）
   - Admonition 名称小写化（`Note` → `note`）
   - 配置迁移（`_config.yml` + `_toc.yml` → `myst.yml`）
   - 重命名不需要的文件（加下划线前缀隐藏）
3. 提示用户如想继续使用 JB 1.x 可安装 `jupyter-book<2`

## TOC 自动生成

`myst init --write-toc` 选项：

1. 加载配置
2. 调用 `loadProjectFromDisk(..., { writeTOC: true })`
3. 根据文件系统结构或现有 _toc.yml 生成 TOC
4. 将 TOC 写入 myst.yml 的 `project.toc` 字段
5. Legacy `_toc.yml` 存在时提示升级信息

## CI/CD 配置

通过以下选项生成 CI/CD 配置文件：

| 选项 | 生成内容 |
|------|----------|
| `--gh-pages` | GitHub Pages 部署 Action |
| `--gh-curvenote` | Curvenote 部署 Action |
| `--readthedocs` | Read the Docs 配置 |

这些通过对应的 action 模块（`gh-actions/`、`readthedocs/`）实现。

## 交互式启动

初始化完成后（无 --project/--site/--write-toc 等非交互选项时），询问用户是否立即启动开发服务器：
- "Yes" → 调用 `startServer(session, {})` 启动服务器
- "No" → 输出提示信息告诉用户后续命令

## 相关概念

- [CLI 架构](00-cli-architecture.md) — 命令注册机制
- [项目加载与TOC](05-project-load-toc.md) — TOC 解析和项目加载
- [版本迁移](07-migration.md) — MyST 内容版本迁移
