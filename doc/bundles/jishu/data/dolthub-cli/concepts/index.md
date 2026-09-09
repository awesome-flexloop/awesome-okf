# 概念索引（Concepts）

本目录包含 `dh` CLI 的五篇核心概念文档，按"概述 → 架构 → 认证 → 数据链路 → 协作/输出"递进。

## 概念列表

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 00 | [dh CLI 概述与安装](00-overview.md) | 产品定位、安装/构建、14 个命令组全貌 | F-001~F-006、F-011 |
| 01 | [dh CLI 架构与分层](01-architecture.md) | 入口、Cobra 命令树、Factory 注入、IOStreams、错误/退出码 | F-007~F-016 |
| 02 | [认证与凭据管理](02-authentication.md) | OAuth PKCE、keyring/文件双源存储、token 刷新、安全脱敏 | F-022~F-031、F-060 |
| 03 | [SQL 查询与表导入](03-sql-and-import.md) | 读/写 SQL、分片上传、异步导入 | F-047~F-057 |
| 04 | [仓库协作操作](04-repository-operations.md) | db/branch/pr/release/tag、仓库解析规则 | F-039~F-042、F-052、F-058 |
| 05 | [结构化输出与异步操作](05-output-and-operations.md) | JSON/jq/template、表格渲染、Operation 轮询、分页 | F-043~F-046、F-050~F-051 |

## 阅读路径建议

```
00-overview（认识工具全貌）
    ↓
01-architecture（理解工程分层）
    ↓
02-authentication（理解身份与安全）
    ↓
03-sql-and-import（核心数据链路）
    ↓
04-repository-operations（协作模型）
    ↓
05-output-and-operations（输出与异步抽象）
```

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-architecture
02-authentication
03-sql-and-import
04-repository-operations
05-output-and-operations
```
