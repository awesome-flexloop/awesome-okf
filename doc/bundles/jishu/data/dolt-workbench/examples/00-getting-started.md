---
type: example
title: 快速开始
description: 从零开始安装和运行 dolt-workbench 的完整指南
tags: [dolt-workbench, getting-started, installation, tutorial]
status: stable
generated:
  by: reference_agent/agnes-2.5-flash
  at: 2026-09-09T04:00:00Z
sources:
  - id: readme
    resource: https://github.com/dolthub/dolt-workbench/blob/8fb6757a8e6b3b3c0c3e4f8d3b6e2f1a5c9d8e7f/README.md
    title: Dolt Workbench README
---

# 快速开始

## 安装方式

### 方式一：桌面应用（推荐）

#### macOS

1. 访问 [DoltHub 发布页面](https://github.com/dolthub/dolt-workbench/releases)
2. 下载最新版本的 `.dmg` 文件
3. 双击打开并拖动到 Applications 文件夹
4. 从 Applications 启动 DoltWorkbench

#### Windows

1. 访问 [DoltHub 发布页面](https://github.com/dolthub/dolt-workbench/releases)
2. 下载最新版本的 `.exe` 安装程序
3. 运行安装程序并按提示完成安装
4. 从开始菜单启动 DoltWorkbench

### 方式二：Docker

```bash
# 拉取并运行最新版本
docker run -p 9002:9002 -p 3000:3000 dolthub/dolt-workbench:latest

# 访问 http://localhost:3000
```

### 方式三：源码构建

```bash
# 1. 克隆仓库
git clone https://github.com/dolthub/dolt-workbench.git
cd dolt-workbench

# 2. 安装依赖
yarn install

# 3. 编译
yarn compile

# 4. 开发模式启动
yarn dev
# - graphql-server 监听 :9002
# - web 应用监听 :3002
# 访问 http://localhost:3002
```

#### 桌面应用开发模式

```bash
# 下载 Dolt CLI（必需）
yarn download:dolt

# 启动桌面应用
yarn dev:app
```

## 首次使用

### 1. 创建数据库连接

启动后，点击 "New Connection" 创建数据库连接：

#### MySQL 连接

```
Host: localhost
Port: 3306
User: root
Password: your_password
Database: my_database
```

#### PostgreSQL 连接

```
Host: localhost
Port: 5432
User: postgres
Password: your_password
Database: my_database
```

#### Dolt 连接

Dolt 使用 MySQL 协议，连接方式与 MySQL 相同。确保 Dolt sql-server 正在运行：

```bash
# 启动 Dolt sql-server
dolt sql-server --listen-address=:3306
```

然后使用相同的 MySQL 连接参数。

#### DoltLite 连接

选择 SQLite 文件路径即可：

```
Database File: /path/to/your/database.db
```

如果文件不存在，可以选择创建新的 DoltLite 数据库。

### 2. 环境变量配置（可选）

对于 Docker 或服务器部署，可以使用环境变量：

```bash
# 单数据库连接
DW_DB_HOST=localhost
DW_DB_PORT=3306
DW_DB_USER=root
DW_DB_PASS=your_password
DW_DB_DBNAME=my_database

# 或使用连接 URI
DW_DB_CONNECTION_URI=mysql://root:your_password@localhost:3306/my_database

# SSL 配置
DW_DB_USE_SSL=false
```

## 核心功能导航

### 数据浏览

1. 选择数据库 → 左侧导航栏 "Data"
2. 选择表和 ref（分支/标签/提交）
3. 查看表格数据，支持排序和筛选

### SQL 查询

1. 选择 "Query" 页面
2. 在 Ace Editor 中编写 SQL
3. 按 `Ctrl+Enter` 执行查询
4. 查看结果和执行情况

### 分支管理

1. 选择 "Branches" 页面
2. 创建新分支、切换分支、删除分支
3. 查看分支列表和最后更新时间

### 提交历史

1. 选择 "Commits" 页面
2. 查看提交列表和详细信息
3. 切换到 "Graph" 查看提交图

### Diff 对比

1. 选择 "Compare" 页面
2. 选择两个 ref 进行对比
3. 查看 schema diff 和行 diff

### AI 助手

1. 点击右侧 "Agent" 面板
2. 输入自然语言查询
3. AI 生成并执行 SQL
4. 查看结果和解释

## 快捷键

| 快捷键 | 功能 |
|---|---|
| `Ctrl+Enter` | 执行 SQL 查询 |
| `Ctrl+I` | 导入文件 |
| `Ctrl+G` | 打开提交图 |
| `Ctrl+D` | 打开 Schema 视图 |
| `Ctrl+Q` | 打开查询页面 |

## 下一步

- [连接数据库详解](./01-connecting-databases.md)
- [使用 Agent Mode](./02-using-agent-mode.md)
