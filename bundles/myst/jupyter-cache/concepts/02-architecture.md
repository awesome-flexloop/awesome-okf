---
type: Concept
title: 缓存架构设计
description: jupyter-cache 的双表数据库设计、内容哈希键机制、缓存文件布局和LRU淘汰策略
tags: [jupyter, cache, architecture, database, sqlalchemy, hash, lru]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:38:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# 缓存架构设计

## 三层架构

jupyter-cache 采用三层架构：

1. **项目层（nbproject表）**：维护"哪些Notebook需要执行"的列表
2. **缓存层（nbcache表+文件系统）**：存储已执行Notebook的结果
3. **执行层（Executors）**：实际执行Notebook的插件引擎

## 数据库设计

### settings 表——键值配置

简单的键值对存储，用于缓存级别等配置：

| 字段 | 类型 | 约束 |
|------|------|------|
| pk | Integer | 主键 |
| key | String(36) | 唯一，配置名 |
| value | JSON | 配置值 |

当前使用的配置键：`cache_limit`（缓存上限，默认1000）。

### nbproject 表——项目Notebook索引

记录"哪些Notebook在项目中"以及如何读取/执行它们：

| 字段 | 类型 | 说明 |
|------|------|------|
| pk | Integer | 主键（自动编号） |
| uri | String(255) | 唯一，Notebook路径/URI |
| read_data | JSON | 读取配置（含name字段指定读取器） |
| assets | JSON | 关联资源文件列表（相对路径） |
| exec_data | JSON | 执行配置 |
| created | DateTime | UTC创建时间 |
| traceback | Text | 执行失败的错误信息 |

关键字段设计：
- **uri**：Notebook的位置标识，可以是本地路径或其他URI
- **read_data**：`{"name": "filesystem", ...}` 指定如何读取Notebook
- **assets**：执行所需的辅助文件列表（如数据文件、图片）
- **traceback**：执行失败时存储错误栈，成功时为空

### nbcache 表——执行结果缓存

记录已执行Notebook的缓存元数据：

| 字段 | 类型 | 说明 |
|------|------|------|
| pk | Integer | 主键 |
| hashkey | String(255) | 唯一，内容哈希 |
| uri | String(255) | 首次添加时的源URI |
| description | String(255) | 可选描述 |
| data | JSON | 额外数据（如执行时间） |
| created | DateTime | UTC创建时间 |
| accessed | DateTime | UTC最后访问时间（onupdate自动更新） |

关键字段设计：
- **hashkey**：内容哈希，是缓存的核心键；不同Notebook如果代码内容相同，hashkey相同
- **accessed**：每次访问缓存时自动更新，用于LRU淘汰

## 内容哈希机制

### hashkey 生成

hashkey 基于Notebook代码单元格内容计算，而非基于文件路径或时间戳：

1. 读取Notebook（.ipynb JSON）
2. 提取所有code类型单元格的source字段
3. 对代码内容进行规范化（去除无关元数据）
4. 计算SHA-256哈希
5. 十六进制编码作为hashkey

### 缓存命中逻辑

```
Notebook A ──┐
             ├──→ 相同代码内容 ──→ 相同hashkey ──→ 命中同一缓存
Notebook B ──┘
```

- 相同代码内容→相同hashkey→直接复用缓存结果
- 代码修改→hashkey变化→缓存miss→重新执行
- 文件移动/重命名但代码不变→hashkey不变→缓存命中

## 文件系统布局

缓存目录结构：

```
.jupyter_cache/
├── global.db                 # SQLite数据库
├── __version__.txt           # 缓存版本（用于迁移检测）
└── executed/
    ├── a1b2c3d4.../          # hashkey作为目录名
    │   ├── base.ipynb        # 执行后的Notebook（含输出）
    │   └── artifacts/        # 执行产物（图片、数据文件等）
    │       ├── figure.png
    │       └── result.csv
    ├── e5f6g7h8.../
    │   ├── base.ipynb
    │   └── artifacts/
    └── ...
```

- `executed/` 下每个目录对应一个缓存条目
- 目录名即hashkey
- `base.ipynb` 是执行完成后的Notebook（包含输出单元格）
- `artifacts/` 存储执行过程中产生的关联文件

## LRU 缓存淘汰

### 自动更新访问时间

`accessed` 字段使用 SQLAlchemy 的 `onupdate=datetime_utcnow()`：
- 每次从缓存读取时，数据库自动更新 `accessed` 时间戳
- 不需要应用层代码手动维护

### 淘汰策略

`truncate_caches()` 在添加新缓存条目时检查：
1. 查询当前缓存记录数
2. 若超过 `cache_limit`，按 `accessed` 升序排列（最旧的在前）
3. 删除超出限制的记录及其文件目录
4. 删除文件系统上的 `executed/{hashkey}/` 目录

默认缓存上限为 1000 条，可通过 CLI 或 API 修改。

## 缓存匹配流程

`match_cache_to_project()` 的工作流程：

1. 遍历项目中所有 Notebook（nbproject表）
2. 读取每个Notebook，计算其内容hashkey
3. 在nbcache表中查找匹配的hashkey
4. 若找到：标记为缓存命中（✅）
5. 若未找到：标记为待执行（-）
6. 若有traceback：标记为执行失败（❌）

## 相关概念

- [简介](/concepts/00-introduction.md)
- [缓存API详解](/concepts/03-cache-api.md)
- [配置项参考](/concepts/07-configuration.md)
- [基本使用示例](/examples/basic-usage.md)
