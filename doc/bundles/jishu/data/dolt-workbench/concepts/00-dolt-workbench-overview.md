---
type: concept
title: dolt-workbench 概览
description: DoltWorkbench 项目定位、功能特性、支持数据库与核心价值主张
tags: [dolt-workbench, overview, introduction]
status: stable
generated:
  by: reference_agent/agnes-2.5-flash
  at: 2026-09-09T04:00:00Z
sources:
  - id: dolt-workbench-repo
    resource: https://github.com/dolthub/dolt-workbench
    title: Dolt Workbench GitHub 仓库
  - id: dolt-workbench-readme
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb67574a12509f009aa046f4a71e615078e7e4c/README.md
    title: Dolt Workbench README
---

# dolt-workbench 概览

## 项目定位

DoltWorkbench 是 [DoltHub](https://www.dolthub.com/) 官方推出的现代 SQL 工作台，专为数据库开发者和数据工程师设计。它提供了一个统一的图形界面，支持多种数据库类型，并集成了 Git 版本控制能力（通过 Dolt/Doltgres）。

## 核心特性

1. **多数据库支持**: MySQL、PostgreSQL、Dolt、Doltgres
2. **表格浏览器**: 可视化浏览和编辑表格数据
3. **自动 SQL 生成**: 点击表格单元格即可生成 SQL 语句
4. **点击编辑**: 直接点击数据单元格进行编辑
5. **Agent Mode**: 基于 Claude AI 的智能助手模式，支持自然语言查询
6. **ER 图**: 可视化数据库关系图
7. **文件上传**: 支持 CSV/PSV/TSV 文件导入
8. **分支管理**: 支持 Dolt/Doltgres 分支操作
9. **提交历史**: 可视化提交图和日志
10. **Diff 对比**: 支持 two-dot 和 three-dot diff

## 支持数据库

| 数据库 | 类型标识 | 说明 |
|---|---|---|
| MySQL | `mysql` | 标准 MySQL 数据库 |
| PostgreSQL | `postgres` | 标准 PostgreSQL 数据库 |
| Dolt | `mysql` (自动检测) | Dolt 版本控制系统内嵌 MySQL 协议 |
| Doltgres | `postgres` (自动检测) | Dolt 版本控制系统内嵌 PostgreSQL 协议 |
| SQLite | `sqlite` | 标准 SQLite 数据库 |
| DoltLite | `sqlite` (自动检测) | 无服务器版 Dolt，基于 SQLite |

## 安装方式

### 桌面应用

- **macOS**: 从 [DoltHub 发布页面](https://github.com/dolthub/dolt-workbench/releases) 下载 `.dmg`
- **Windows**: 从 [DoltHub 发布页面](https://github.com/dolthub/dolt-workbench/releases) 下载 `.exe`

### Docker

```bash
docker run -p 9002:9002 -p 3000:3000 dolthub/dolt-workbench:latest
```

### 源码构建

```bash
yarn install
yarn compile
yarn dev
# graphql-server 监听 :9002，web 应用监听 :3002
```

桌面应用需要额外下载 Dolt CLI：

```bash
yarn download:dolt
yarn dev:app
```

## 适用场景

- 数据库开发和调试
- Dolt 版本控制工作流
- 团队协作（通过 DoltHub 远程仓库）
- AI 辅助数据分析（Claude Agent Mode）
- 本地 SQLite/DoltLite 数据库管理
