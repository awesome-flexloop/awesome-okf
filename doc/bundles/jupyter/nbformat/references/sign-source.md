---
type: Reference
title: "签名与信任机制源码"
description: "sign.py中NotebookNotary、SignatureStore、HMAC签名、信任判断、jupyter-trust CLI的源码解析"
tags: [sign, trust, hmac, signature, notary, sqlite, jupyter-trust]
sources:
  - id: sign-py
    resource: "../../../../../external/libs/jupyter/nbformat/nbformat/sign.py"
    title: "nbformat/sign.py"
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# 签名与信任机制源码

nbformat 的信任机制用于标记笔记本输出是否可信（防止加载恶意HTML/JavaScript输出）。

## 核心类层次

```
SignatureStore (抽象基类)
├── MemorySignatureStore    # 内存存储（OrderedDict，LRU淘汰）
└── SQLiteSignatureStore    # SQLite持久化存储
```

### SignatureStore 接口

| 方法 | 功能 |
|------|------|
| `store_signature(digest, algorithm)` | 存储签名（幂等） |
| `check_signature(digest, algorithm)` | 检查签名是否可信，返回bool |
| `remove_signature(digest, algorithm)` | 移除签名 |
| `close()` | 关闭连接（SQLite需要） |

### MemorySignatureStore

- 使用 `OrderedDict` 作为有序集合（值为None）
- `cache_size = 65535`，超出时淘汰最旧的25%
- LRU访问：check时将命中的签名移到末尾

### SQLiteSignatureStore

- 默认数据库路径：`{data_dir}/nbsignatures.db`
- 表结构：`nbsignatures(id INTEGER PK, algorithm TEXT, signature TEXT, path TEXT, last_seen TIMESTAMP)`
- 索引：`algosig ON (algorithm, signature)`
- 数据库损坏时自动重命名为 `.bak` 并新建
- 支持 `:memory:` 内存模式

## NotebookNotary 主类

基于 traitlets `LoggingConfigurable`，提供笔记本签名和信任检查：

### 核心配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `algorithm` | `"sha256"` | HMAC哈希算法（从hashlib.algorithms_guaranteed中排除shake_*） |
| `secret_file` | `{data_dir}/notebook_secret` | 密钥文件路径 |
| `db_file` | `{data_dir}/nbsignatures.db` | SQLite数据库路径 |
| `data_dir` | JupyterApp.data_dir | Jupyter数据目录 |
| `store_factory` | SQLite或Memory | 签名存储工厂函数 |

### 核心方法

| 方法 | 功能 |
|------|------|
| `compute_signature(nb)` | 使用HMAC计算notebook签名（排除旧signature字段） |
| `check_signature(nb)` | 验证notebook签名是否在可信存储中，nbformat<3返回False |
| `sign(nb)` | 签名notebook并存储到数据库 |
| `unsign(nb)` | 从可信存储中移除notebook签名 |
| `mark_cells(nb, trusted)` | 标记所有code cell的 `metadata.trusted` |
| `check_cells(nb)` | 检查所有code cell是否可信 |

### 签名计算流程

1. 创建HMAC实例（`HMAC(secret, digestmod=hashlib.sha256)`）
2. 使用 `signature_removed(nb)` 上下文管理器临时移除metadata.signature
3. 通过 `yield_everything(nb)` 递归遍历整个notebook结构（dict按键排序、list/tuple按序、str编码为utf8），将每个字节喂给HMAC
4. 返回 `hmac.hexdigest()`

### 信任判断逻辑（`_check_cell`）

Cell被信任的条件（满足任一）：
1. `cell.metadata.trusted == True`（显式标记）
2. 没有不安全输出（只有stream/error输出，或execute_result/display_data仅含安全键）

不安全输出类型：v4的 `execute_result`/`display_data`，v3的 `pyout`/`display_data`。
安全键白名单：v4为 `{output_type, execution_count, metadata}`，v3为 `{output_type, prompt_number, metadata}`。

## TrustNotebookApp CLI

入口点：`jupyter-trust = "nbformat.sign:TrustNotebookApp.launch_instance"`

- `jupyter trust notebook.ipynb`：签名一个或多个notebook
- `jupyter trust --reset`：清除所有可信签名缓存并生成新密钥
- 支持stdin管道输入

## 相关信源

- [包入口公共API](init-api.md)
- [信任与签名概念](../concepts/08-trust-and-signing.md)
