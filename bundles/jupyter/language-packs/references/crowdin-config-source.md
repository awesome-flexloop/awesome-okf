---
type: Reference
title: "Crowdin 配置信源"
description: "crowdin.yml 定义了 Crowdin 翻译平台的源文件到翻译文件的映射规则"
tags: [jupyterlab, language-pack, crowdin, i18n, configuration]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: crowdin-source
    resource: https://github.com/jupyterlab/language-packs/blob/master/crowdin.yml
    title: "crowdin.yml"
---

# Crowdin 配置信源

## 源码路径

`external/libs/jupyter/language-packs/crowdin.yml`

## 配置结构

### 全局设置

```yaml
append_commit_message: false
commit_message: '[ci skip] New %language% translation from Crowdin'
```

- `append_commit_message: false`：不追加提交信息
- 提交信息模板包含 `%language%` 占位符，Crowdin 自动替换为语言名
- `[ci skip]` 标记避免触发 CI 流水线

### 文件映射（files 列表）

每个文件条目包含：

| 字段 | 说明 |
|------|------|
| `source` | 源 POT 文件路径（以 `/` 开头表示仓库根） |
| `translation` | 翻译 PO 文件输出路径模板 |

### 路径占位符

| 占位符 | 替换值 | 示例 |
|--------|--------|------|
| `%locale%` | 连字符格式 locale | `zh-CN` |
| `%locale_with_underscore%` | 下划线格式 locale | `zh_CN` |
| `%file_name%` | 源文件名（不含扩展名） | `jupyterlab` |

### 核心包（jupyterlab）路径

```
source: /jupyterlab/locale/jupyterlab.pot
translation: /language-packs/jupyterlab-language-pack-%locale%/jupyterlab_language_pack_%locale_with_underscore%/locale/%locale_with_underscore%/LC_MESSAGES/%file_name%.po
```

### 扩展包路径模板

```
source: /extensions/{pkg_name_snake}/locale/{pkg_name_snake}.pot
translation: /language-packs/jupyterlab-language-pack-%locale%/jupyterlab_language_pack_%locale_with_underscore%/locale/%locale_with_underscore%/LC_MESSAGES/%file_name%.po
```

## 自动同步机制

- `02_update_catalogs.py` 中的 `update_crowdin_config()` 函数根据 `repository-map.yml` 自动生成 crowdin.yml 的 files 列表
- 核心包 jupyterlab 始终在列表首位
- 扩展包按字母顺序排列，包名从 kebab-case 转换为 snake_case
