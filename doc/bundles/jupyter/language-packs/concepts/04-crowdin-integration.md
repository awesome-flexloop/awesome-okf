---
type: Concept
title: "Crowdin 翻译平台集成"
description: "Crowdin 是 JupyterLab 翻译众包平台——通过 GitHub Action 实现 POT 上传、翻译下载的双向自动化同步"
tags: [jupyterlab, language-pack, crowdin, i18n, translation, automation]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:23:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: crowdin-config, resource: /references/crowdin-config-source.md, title: "Crowdin 配置信源" }
  - { id: workflows, resource: /references/workflows-source.md, title: "CI/CD 工作流信源" }
---

# Crowdin 翻译平台集成

[Crowdin](https://crowdin.com/project/jupyterlab) 是 JupyterLab 翻译的众包平台，全球译者通过 Web 界面协作翻译字符串。language-packs 仓库通过官方 Crowdin GitHub Action 实现与 Crowdin 平台的双向自动化同步。

## Crowdin 项目信息

| 属性 | 值 |
|------|-----|
| 项目地址 | https://crowdin.com/project/jupyterlab |
| 项目 ID | 409874 |
| 同步分支 | main |
| 翻译 PR 分支 | `l10n_crowdin_translations` |

## 双向同步机制

```
POT文件变更 → GitHub Action → 上传POT到Crowdin → 译者翻译 → GitHub Action → 下载PO → 创建PR
```

### 上传源文件（Upload Sources）

当 `.pot` 文件变更推送到 main 分支时：
1. crowdin.yml 工作流触发
2. 使用 `crowdin/github-action@v2`，设置 `upload_sources: true`
3. 新字符串自动出现在 Crowdin 翻译界面
4. 参数：`--branch=main --preserve-hierarchy`

### 下载翻译（Download Translations）

触发条件：
- POT 文件变更后（上传新字符串后通常也会下载已有翻译）
- 每日定时：`cron: '45 1 * * *'`（UTC 1:45）
- 手动触发

下载配置：
- `download_translations: true`
- `export_only_approved: false`（非只下载已审核，所有翻译都下载）
- 参数：`--branch=main`
- 自动创建 PR 到 main 分支

## crowdin.yml 配置文件

仓库根目录的 `crowdin.yml` 定义了源文件和翻译文件的映射关系：

```yaml
append_commit_message: false
commit_message: '[ci skip] New %language% translation from Crowdin'
files:
  - source: /jupyterlab/locale/jupyterlab.pot
    translation: /language-packs/jupyterlab-language-pack-%locale%/jupyterlab_language_pack_%locale_with_underscore%/locale/%locale_with_underscore%/LC_MESSAGES/%file_name%.po
  - source: /extensions/{pkg}/locale/{pkg}.pot
    translation: /language-packs/jupyterlab-language-pack-%locale%/jupyterlab_language_pack_%locale_with_underscore%/locale/%locale_with_underscore%/LC_MESSAGES/%file_name%.po
```

### 路径占位符

| 占位符 | 含义 | 示例值 |
|--------|------|--------|
| `%locale%` | 连字符格式 locale | `zh-CN`、`fr-FR` |
| `%locale_with_underscore%` | 下划线格式 locale | `zh_CN`、`fr_FR` |
| `%file_name%` | 源文件名（不含扩展名） | `jupyterlab`、`notebook` |
| `%language%` | 语言名称（用于commit message） | `Chinese`、`French` |

### 提交信息

- `[ci skip]` 前缀避免翻译 PR 触发 CI 流水线（节省资源）
- 格式：`[ci skip] New {language} translation from Crowdin`

### 自动生成

`crowdin.yml` 的 files 列表由 `02_update_catalogs.py` 中的 `update_crowdin_config()` 函数自动生成：
- jupyterlab 核心 POT 固定在首位
- 扩展包按字母顺序排列
- 包名自动从 kebab-case 转为 snake_case
- 人工不应手动编辑 files 列表

## In-Context 翻译功能

特殊语言包 `jupyterlab-language-pack-ach-UG`（Acholi/阿乔利语）不是真正的翻译，而是 Crowdin 的 [In-Context Localization](https://developer.crowdin.com/in-context-localization/) 功能载体：

- 安装此包后，JupyterLab 界面直接显示 Crowdin 的 in-context 翻译界面
- 译者可以直接在运行的 JupyterLab 中点击字符串进行翻译
- 翻译内容不是真正的阿乔利语，而是特殊标记
- **普通用户不应安装此包**（README 中有明确警告）

## 翻译贡献流程

普通译者无需接触 Git 或 GitHub：

1. 访问 https://crowdin.com/project/jupyterlab
2. 选择目标语言
3. 在 Web 界面中翻译字符串
4. 翻译保存后，下一次 Crowdin 同步（每日或手动触发）会自动创建 PR
5. PR 经审查合并后，下一次发布包含新翻译

## 翻译 PR 处理规范

来自 Crowdin Bot 的 PR：

1. **合并前 squash**：将多个翻译提交压缩为单个 commit 保持历史整洁
2. **冲突处理**：如有冲突，关闭 PR 删除分支，等待 Crowdin 重新生成（新分支无冲突）
3. **不手动编辑**：不要直接在 PR 中修改 .po 文件，修改应在 Crowdin 平台进行

## Secrets 配置

GitHub 仓库需要配置两个 Secrets：

| Secret | 用途 | 获取方式 |
|--------|------|---------|
| `CROWDIN_PROJECT_ID` | Crowdin 项目 ID | Crowdin 项目设置 → Tools → API |
| `CROWDIN_TOKEN` | Crowdin 个人访问令牌 | Crowdin 账户设置 → API → New token |

发布准备还需要 `CROWDIN_API_KEY`（即 CROWDIN_TOKEN）用于获取贡献者列表。

## 相关概念

- [整体架构概览](01-architecture-overview.md)
- [Gettext 国际化基础](06-gettext-i18n.md)
- [CI/CD 流水线](08-cicd-pipeline.md)
- [贡献翻译](../examples/03-contribute-translation.md)
