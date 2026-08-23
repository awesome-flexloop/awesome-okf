---
type: Concept
title: 标签分类配置
description: 自定义PR分类规则：修改默认标签和前缀匹配、创建自定义分类、配置文件格式
tags: [github, activity, configuration, tags, labels, categorization]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:10:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: ga-source
    resource: /references/activity-source.md
    title: github-activity 源码路径映射
---

# 标签分类配置

## 默认分类规则

github-activity 内置8种PR分类，每种分类有两种匹配方式：

- **tags**：匹配GitHub PR标签（labels），如 `bug`、`enhancement`、`breaking`
- **pre**：匹配PR标题前缀（大写关键字），如 `FIX:`、`ENH:`、`BREAK:`

分类按优先级排列，第一个匹配的分类生效。

### 默认分类表

| 分类 | 标题（英文） | tags | pre |
|------|------------|------|-----|
| api_change | API and Breaking Changes | api-change, apichange, breaking | BREAK, BREAKING, BRK, UPGRADE |
| new | New features added | feature, new | NEW, FEAT, FEATURE |
| deprecate | Deprecated features | deprecation, deprecate | DEPRECATE, DEPRECATION, DEP |
| enhancement | Enhancements made | enhancement, enhancements | ENH, ENHANCEMENT, IMPROVE, IMP |
| bug | Bugs fixed | bug, bugfix, bugs | FIX, BUG |
| maintenance | Maintenance | maintenance, maint | MAINT, MNT |
| documentation | Documentation | documentation, docs, doc | DOC, DOCS |
| ci | CI improvements | ci, continuous-integration | CI |

## 标题前缀约定

使用前缀约定（Conventional Commits风格）可以确保PR被正确分类，即使忘记打标签：

```
BREAK: remove support for Python 3.7     → api_change
FEAT: add dark mode support              → new
ENH: improve performance of parser       → enhancement
FIX: resolve crash on Windows            → bug
DOC: update installation guide           → documentation
CI: add Python 3.12 to test matrix       → ci
MAINT: refactor utility functions        → maintenance
DEP: deprecate old API                   → deprecate
```

## 自定义分类配置

通过 `--tags` 选项传入JSON配置文件，自定义分类规则：

```bash
github-activity owner/repo --tags my_tags.json
```

### 配置文件格式

```json
{
  "security": {
    "tags": ["security", "vulnerability"],
    "pre": ["SEC", "SECURITY"],
    "description": "Security fixes"
  },
  "performance": {
    "tags": ["performance", "perf"],
    "pre": ["PERF"],
    "description": "Performance improvements"
  },
  "i18n": {
    "tags": ["i18n", "internationalization", "translation"],
    "pre": ["I18N"],
    "description": "Internationalization"
  }
}
```

自定义分类会与默认分类合并。如果自定义分类的key与默认分类相同，则覆盖默认配置。

### 完全自定义分类

配置文件中的分类按定义顺序排列优先级。若想完全替换默认分类，可以只在配置中提供自己的分类。

### 中文分类示例

```json
{
  "breaking": {
    "tags": ["breaking", "破坏性变更"],
    "pre": ["BREAK", "破坏"],
    "description": "破坏性变更"
  },
  "feature": {
    "tags": ["feature", "新功能"],
    "pre": ["FEAT", "NEW", "功能"],
    "description": "新功能"
  },
  "fix": {
    "tags": ["bug", "bugfix", "修复"],
    "pre": ["FIX", "BUG", "修复"],
    "description": "Bug修复"
  }
}
```

## Python API使用自定义分类

```python
from github_activity import get_activity, generate_activity_markdown

# 自定义分类
tags = {
    "security": {
        "tags": ["security"],
        "pre": ["SEC"],
        "description": "Security fixes"
    },
}

# 获取活动数据
df = get_activity("owner/repo", since="2024-01-01", tags=tags)

# 生成Markdown
md = generate_activity_markdown(df)
print(md)
```

## 相关概念

- [CLI命令详解](/concepts/02-cli-usage.md)
- [数据获取与处理](/concepts/03-activity-data.md)
- [变更日志生成示例](/examples/changelog-generation.md)
