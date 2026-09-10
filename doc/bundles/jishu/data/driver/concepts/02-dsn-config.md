---
type: Concept
title: DSN 解析与 Config
description: "driver v2 的 DSN 格式规范：file:// 前缀要求、必需参数（commitname/commitemail）、可选参数（database/multistatements/clientfoundrows），以及 LoadMultiEnvFromDir 多库模式。F-003~F-007、F-012。"
tags: [driver, dolt, dsn, config]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: driver-repo
    resource: https://github.com/dolthub/driver
    title: dolthub/driver（官方仓库）
  - id: driver-local
    resource: "本地克隆（tag v2.2.0-18，commit 61ccedb7035925b3e4a5f91be6bd68b100e3b1e7）"
    title: driver 源码逐文件精读
---

# DSN 解析与 Config

> **对应 F 编号**：F-003 ~ F-007、F-012

## file:// 前缀要求（F-003）

所有 DSN 必须使用 `file://` scheme 前缀，这是 driver v2 的硬性约束：

```go
// data_source.go
const fileUrlPrefix = "file://"

func ParseDataSource(dataSource string) (*DoltDataSource, error) {
    if !strings.HasPrefix(dataSource, fileUrlPrefix) {
        return nil, fmt.Errorf("datasource url '%s' must have a file url scheme", dataSource)
    }
    // ...
}
```

典型格式：

```
file:///path/to/dbs?commitname=Billy%20Bob&commitemail=bb@gmail.com&database=mydb
```

## 必需参数（F-004）

| 参数 | 说明 | 校验规则 |
|------|------|---------|
| `commitname` | commit 作者名 | 必须有且仅有一个值 |
| `commitemail` | commit 作者邮箱 | 必须有且仅有一个值 |

参数名不区分大小写，内部统一转为小写处理（[low](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/data_source.go#L58-L61)）。

## 可选参数（F-005）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `database` | 空 | 连接后自动 USE 的初始数据库（Dolt repo 子目录名） |
| `multistatements` | `false` | 是否开启多语句支持（`;` 分隔） |
| `clientfoundrows` | `false` | 是否设置 MySQL CLIENT_FOUND_ROWS 能力位 |

布尔参数通过 `ParamIsTrue()` 判断，要求值为 `"true"`（不区分大小写）：

```go
func (ds *DoltDataSource) ParamIsTrue(paramName string) bool {
    values, ok := ds.Params[paramName]
    return ok && len(values) == 1 && strings.ToLower(values[0]) == "true"
}
```

## Config 结构体（F-007）

[cfg](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/config.go#L30-L67) 是 DSN 解析结果的结构化表示：

```go
type Config struct {
    DSN           string              // 原始 DSN 字符串（可选）
    Directory     string              // Dolt repo 父目录（必需）
    CommitName    string              // commit 作者名（必需）
    CommitEmail   string              // commit 作者邮箱（必需）
    Database      string              // 初始数据库（可选）
    MultiStatements bool             // 多语句支持（可选）
    ClientFoundRows bool             // CLIENT_FOUND_ROWS（可选）
    Params        map[string][]string // 原始参数字典（可选，保留兼容）
    BackOff       backoff.BackOff     // 引擎打开重试策略（可选）
    Version       string              // Dolt 引擎版本（默认 "0.40.17"）
}
```

## LoadMultiEnvFromDir 多库模式（F-012）

当 `Directory` 指向一个文件夹时，driver 支持**多库模式**：该文件夹下每个子目录视为一个独立的 Dolt repository：

```go
// driver.go
func LoadMultiEnvFromDir(
    ctx context.Context,
    cfg config.ReadWriteConfig,
    fs filesys.Filesys,
    path, version string,
    dbLoadParams map[string]any,
) (*env.MultiRepoEnv, error)
```

实际调用链：

```
Directory = "/data/dbs"
    ↓
LoadMultiEnvFromDir("/data/dbs")
    ↓
env.MultiEnvForConfigAndDirectory(ctx, cfg, fs, dbLoadParams)
    ↓
每个子目录 → DoltEnv（独立 Dolt repo）
```

这意味着：

```
/data/dbs/
├── mydb/      ← 可通过 database=mydb 指定
├── analytics/ ← 可通过 database=analytics 指定
└── logs/      ← 可通过 database=logs 指定
```

一个 DSN 即可操作多个数据库，`CREATE DATABASE` 会自动在 Directory 下创建新子目录。

## DSN 解析流程

```
"file:///data/dbs?commitname=Alice&commitemail=a@x.com&database=mydb&multistatements=true"
    ↓
ParseDataSource()
    ├── 检查 file:// 前缀
    ├── 提取 Directory = "/data/dbs"
    └── 提取 Params = map["commitname"]=>["Alice"], ...
    ↓
ParseDSN()
    ├── 验证 commitname/commitemail 各只有一个值
    └── 填充 Config 结构体
    ↓
NewConnector(cfg)
    ├── 校验 Directory 存在且为目录
    ├── 校验 CommitName/CommitEmail 非空
    └── 设置默认 Version = "0.40.17"
```
