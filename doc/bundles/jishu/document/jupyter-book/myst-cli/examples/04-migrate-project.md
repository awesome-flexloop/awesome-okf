---
type: example
title: "迁移现有项目"
description: "将Jupyter Book 1.x项目和旧版本MyST内容迁移到当前版本的操作指南"
tags: [myst-cli, migrate, jupyter-book, upgrade, legacy]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-migrate/src/index.ts"
    facts: [F-066, F-067]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-migrate/src/migrations.ts"
    facts: [F-068]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/init/init.ts"
    facts: [F-042]
---

# 迁移现有项目

本文档演示如何将 Jupyter Book 1.x 项目和旧版 MyST 内容迁移到当前版本。

## 场景一：从 Jupyter Book 1.x 迁移

### 检测 Legacy 项目

在包含 `_config.yml` 的 Jupyter Book 1.x 项目目录中运行：

```bash
cd my-jupyter-book
myst init
```

init 命令会自动检测到 `_config.yml` 并显示升级提示：

```
📘 Found a legacy Jupyter Book. To proceed, myst needs to perform an upgrade which will:
‣ Upgrade any Sphinx-style glossaries to MyST-style glossaries
‣ Upgrade any case-insensitive admonition names to lowercase (Note → note)
‣ Migrate configuration from _config.yml and (if applicable) _toc.yml files
‣ Rename any modified or unneeded files so that they are hidden

Are you willing to proceed with the upgrade? (Y/n)
```

### 执行升级

按 Enter 确认升级，`upgradeJupyterBook()` 会自动：

1. **术语表迁移**：将 Sphinx 格式的 glossary 指令转换为 MyST 格式
2. **Admonition 名称标准化**：将 `{Note}`、`{WARNING}` 等大小写不敏感的名称改为小写（`{note}`、`{warning}`）
3. **配置迁移**：将 `_config.yml` 中的设置迁移到 `myst.yml`
4. **TOC 迁移**：将 `_toc.yml` 迁移到 `myst.yml` 的 `project.toc` 字段
5. **文件隐藏**：重命名不需要的 legacy 文件（加下划线前缀）

### 迁移后验证

```bash
# 启动开发服务器验证
myst start

# 构建所有导出验证
myst build --all
```

### 不想升级？

如果想继续使用 Jupyter Book 1.x：

```bash
pip install "jupyter-book<2"
```

### 手动升级 TOC

如果 init 时选择了不升级，后续可以手动升级 TOC：

```bash
myst init --write-toc
```

## 场景二：旧版本 MyST 内容迁移

myst-migrate 包提供了内容版本迁移功能，通过 `migrate()` 函数逐版本升级/降级。

### 当前迁移版本

| 版本迁移 | 变更内容 |
|----------|----------|
| v0 → v1 | 脚注语法迁移 |
| v1 → v2 | 块级 CSS 类名迁移 |
| v2 → v3 | Notebook 输出格式迁移 |

当前最新版本为 v3（对应 `SPEC_VERSION = 3`）。

### 迁移 API（编程使用）

```ts
import { migrate } from 'myst-migrate';

const file = {
  path: 'my-file.md',
  content: '# Old content\n...',
  version: 1,  // 当前版本
};

// 升级到最新版本
const upgraded = await migrate(file);
// upgraded.version === 3

// 迁移到指定版本
const downgraded = await migrate(file, { to: 2 });
```

迁移是双向的：
- `to` > 当前版本：依次执行各版本的 `upgrade()`
- `to` < 当前版本：依次执行各版本的 `downgrade()`

### 配置版本

myst.yml 配置文件有独立的版本号：

```yaml
version: 1  # 配置格式版本
```

当前配置版本为 1。内容规范版本（SPEC_VERSION = 3）与配置版本独立。

## 迁移检查清单

迁移完成后，建议执行以下检查：

1. **配置检查**：确认 myst.yml 中 project 和 site 配置正确
2. **TOC 检查**：确认目录结构正确，没有遗漏页面
3. **链接检查**：`myst build --site --check-links`
4. **Admonition 检查**：确认所有 `{Note}` 等已变为 `{note}`
5. **引用检查**：确认 BibTeX 引用正常工作
6. **Notebook 检查**：确认 Notebook 输出正确显示

```bash
# 完整验证命令
myst build --all --check-links --strict
```

## 清理 legacy 文件

迁移确认无误后，可以清理隐藏的 legacy 文件：

```bash
# 清理构建产物
myst clean --all

# （可选）手动删除已隐藏的 legacy 文件
# 这些文件已被重命名为 _config.yml.bak 等
```

## 常见问题

### Q: 升级后 admonition 样式不对？

检查 CSS 类名是否正确。v2 迁移将块级类名从旧格式迁移到新格式，如果使用了自定义 CSS，可能需要更新选择器。

### Q: 脚注不显示？

v1 迁移处理了脚注语法变化。如果脚注仍然有问题，检查是否使用了已弃用的脚注语法。

### Q: Notebook 输出丢失？

v3 迁移处理了 Notebook 输出格式。尝试重新执行 Notebook：

```bash
myst build --site --execute
```

### Q: 如何回滚迁移？

myst-migrate 支持 downgrade，但 init 中的 Jupyter Book 升级是不可逆的（文件被修改/隐藏）。建议在迁移前使用 Git 提交或备份：

```bash
git add -A && git commit -m "before myst migration"
myst init
# 如果有问题
git checkout -- .
```

## 相关命令

- [初始化项目](01-init-project.md)
- [构建站点](02-build-site.md)
- [版本迁移概念](../concepts/07-migration.md)
