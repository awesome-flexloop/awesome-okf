---
type: concept
title: "版本迁移"
description: "myst-migrate包的内容版本迁移机制：迁移管线、升级/降级支持与现有迁移脚本"
tags: [myst-cli, migration, myst-migrate, versioning, upgrade]
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

# 版本迁移

myst-cli 通过 myst-migrate 包提供内容版本迁移能力，确保旧版本的 MyST 内容可以自动升级到当前规范版本。

## 迁移架构

myst-migrate 采用**链式迁移**设计，每个版本间的变更封装为独立的 Migration 对象：

```ts
type Migration = {
  upgrade(src: IFile): Promise<void>;   // 升级到下一版本
  downgrade(src: IFile): Promise<void>; // 降级到上一版本
};
```

## migrate() 函数

```ts
export async function migrate(src: IFile, opts?: Options): Promise<IFile> {
  const to = opts?.to ?? MIGRATIONS.length;  // 默认迁移到最新版
  let currentVersion = src.version || 0;

  // 升级：依次应用各版本 migration.upgrade()
  while (currentVersion < to) {
    const migration = MIGRATIONS[currentVersion];
    await migration.upgrade(src);
    currentVersion++;
    src.version = currentVersion;
  }

  // 降级：依次应用各版本 migration.downgrade()
  while (currentVersion > to) {
    const migration = MIGRATIONS[currentVersion - 1];
    await migration.downgrade(src);
    currentVersion--;
    src.version = currentVersion;
  }

  return src;
}
```

### 关键设计特点

1. **双向迁移**：每个 migration 同时提供 upgrade 和 downgrade，支持向前和向后迁移
2. **链式执行**：跨版本迁移时依次经过每个中间版本，确保不遗漏任何转换
3. **版本跟踪**：`IFile.version` 字段记录当前内容版本
4. **目标版本可选**：默认迁移到最新版（MIGRATIONS.length），也可指定目标版本

## 当前迁移列表

MIGRATIONS 数组按版本顺序排列：

| 版本 | 迁移模块 | 变更内容 |
|------|----------|----------|
| v0 → v1 | `v1_footnotes.ts` | 脚注语法迁移 |
| v1 → v2 | `v2_blockClasses.ts` | 块级 CSS 类名迁移 |
| v2 → v3 | `v3_outputs.ts` | Notebook 输出格式迁移 |

当前 MIGRATIONS.length = 3，即最新内容版本为 v3。这与 myst-cli 中 `SPEC_VERSION = 3` 一致。

## IFile 接口

```ts
type IFile = {
  version?: number;     // 当前内容版本
  content: string;      // 文件内容
  path: string;         // 文件路径
  // ... 其他字段
};
```

## Jupyter Book 1.x 升级

除了 myst-migrate 的内容版本迁移外，init 命令还处理 Jupyter Book 1.x 到 MyST 的配置迁移：

检测到 `_config.yml` 时，`upgradeJupyterBook()` 执行：
1. **术语表迁移**：Sphinx-style glossaries → MyST-style glossary 指令
2. **Admonition 名称标准化**：大小写不敏感的名称（`Note`、`WARNING`）→ 小写（`note`、`warning`）
3. **配置迁移**：`_config.yml` + `_toc.yml` → `myst.yml`
4. **文件隐藏**：重命名不再需要的文件（加下划线前缀）

这是一次性配置迁移，不同于 myst-migrate 的逐版本内容迁移。

## 配置版本

myst.yml 配置文件有独立的版本控制：
- `version: 1`：当前配置格式版本（在 config.ts 中定义 `VERSION = 1`）
- 配置版本和内容版本（SPEC_VERSION = 3）是独立的版本号

## 使用场景

- **`myst init`**：检测到 legacy Jupyter Book 时触发配置迁移
- **文件加载**：处理旧版本的 .md/.ipynb 文件时可通过 myst-migrate 升级内容
- **导出时**：确保内容版本与目标格式兼容
- **降级需求**：团队需要在不同版本 myst-cli 间共享内容时使用 downgrade

## 相关概念

- [Init 项目初始化](03-init-project.md) — init 中的 Jupyter Book 升级
- [CLI 架构](00-cli-architecture.md) — SPEC_VERSION 和 CLI 的关系
