---
type: "concept"
title: "信任与签名"
description: "NotebookNotary签名机制、HMAC签名算法、SQLite/内存存储、信任判断规则、jupyter-trust CLI"
tags: [trust, sign, hmac, signature, notary, jupyter-trust, security]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sign
    resource: /references/sign-source.md
    title: "签名与信任机制源码"
---

# 信任与签名

Jupyter Notebook 的信任机制防止自动执行不受信任的HTML/JavaScript输出。nbformat 提供了基于HMAC的签名系统，标记哪些Notebook是用户信任的。

## 为什么需要信任机制

Notebook的输出区域可以包含任意HTML/JavaScript代码。如果用户打开一个恶意Notebook，浏览器可能在不知情的情况下执行JS代码（例如通过`<script>`标签或`onload`事件）。信任机制确保：

1. **用户生成的输出可信**：用户自己执行的代码产生的输出是安全的
2. **外部来源的Notebook输出不可信**：从网络下载的Notebook，其输出被清除或标记为不可信
3. **显式签名标记信任**：用户通过`jupyter trust`命令显式信任Notebook

[F-090]

## 信任判断规则

Notebook被判定为可信的条件（满足任一）：
1. 存在有效的HMAC签名（之前被用户签名过）
2. 所有code cell都被标记为 `metadata.trusted == True`
3. Notebook不包含不安全的输出类型

**不安全输出类型**：v4的 `execute_result` 和 `display_data`；v3的 `pyout` 和 `display_data`。

**安全输出类型**：`stream`（stdout/stderr）和 `error`，以及仅包含安全键的输出。

安全输出的白名单键：
- v4: `{"output_type", "execution_count", "metadata"}`
- v3: `{"output_type", "prompt_number", "metadata"}`

如果一个execute_result/display_data的顶层键全在白名单中（没有data字段），它也是安全的 [F-091]。

## HMAC签名算法

签名使用HMAC（Hash-based Message Authentication Code）：

1. **密钥**：随机生成的1024字节密钥，存储在 `{data_dir}/notebook_secret`
2. **算法**：默认为SHA-256（可配置）
3. **签名输入**：递归遍历Notebook整个结构（排除旧signature字段），将所有字节喂给HMAC
   - dict按key排序遍历
   - list/tuple按顺序遍历
   - str编码为utf8字节
   - 特殊值（True/False/None/int/float）转为repr字符串
4. **签名存储**：hex digest存储在Notebook的 `metadata.signature` 字段和签名数据库中

[F-092]

### 签名计算伪代码

```python
def compute_signature(nb):
    h = hmac.HMAC(secret, digestmod=hashlib.sha256)
    with signature_removed(nb):  # 临时移除metadata.signature
        for b in yield_everything(nb):  # 递归序列化
            h.update(b)
    return h.hexdigest()
```

`yield_everything()` 按确定顺序遍历所有内容，保证相同Notebook总是产生相同签名。[F-093]

## NotebookNotary 门面类

`NotebookNotary(traitlets.LoggingConfigurable)` 是签名功能的主要接口：

### 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `algorithm` | `"sha256"` | HMAC哈希算法（排除shake_*） |
| `secret_file` | `{data_dir}/notebook_secret` | HMAC密钥文件路径 |
| `db_file` | `{data_dir}/nbsignatures.db` | SQLite数据库路径 |
| `data_dir` | `jupyter_core.paths.jupyter_data_dir()` | Jupyter数据目录 |
| `secret` | 从secret_file读取 | 64位编码的密钥 |

### 核心方法

| 方法 | 功能 |
|------|------|
| `compute_signature(nb)` | 计算Notebook的HMAC签名（hex digest） |
| `check_signature(nb)` | 检查Notebook签名是否在可信数据库中（返回bool） |
| `sign(nb)` | 签名Notebook：计算签名→存储→写入metadata.signature |
| `unsign(nb)` | 取消信任：从数据库移除签名→删除metadata.signature |
| `mark_cells(nb, trusted)` | 标记所有code cell的 `metadata.trusted` 字段 |
| `check_cells(nb)` | 检查所有code cell是否可信（metadata.trusted或输出安全） |

[F-094]

### 使用示例

```python
from nbformat.sign import NotebookNotary

# 作为上下文管理器使用（自动关闭SQLite连接）
with NotebookNotary() as notary:
    nb = nbformat.read("my_notebook.ipynb", as_version=4)

    # 检查是否可信
    if notary.check_signature(nb):
        print("Trusted")
    else:
        print("Not trusted - outputs will be sanitized")

    # 签名（信任）
    notary.sign(nb)
    nbformat.write(nb, "trusted.ipynb")

    # 取消信任
    notary.unsign(nb)
```

[F-095]

## 签名存储

### MemorySignatureStore（内存存储）

- 使用 `OrderedDict` 作为有序集合（LRU淘汰）
- `cache_size = 65535`，超出时淘汰最旧的25%
- check时将命中签名移到末尾（LRU访问模式）
- 适用于临时/测试场景

### SQLiteSignatureStore（SQLite持久化）

- 默认存储后端
- 表结构：`nbsignatures(id INTEGER PK, algorithm TEXT, signature TEXT, path TEXT, last_seen TIMESTAMP)`
- 索引：`algosig ON (algorithm, signature)` 加速查询
- 自动处理数据库损坏：损坏时重命名为 `.bak` 并新建数据库
- 支持 `:memory:` 内存模式（通过 `db_file=":memory:"`）

[F-096]

### store_factory

存储工厂函数根据配置选择后端：
- 默认创建 `SQLiteSignatureStore(db_file)`
- 可通过 `NotebookNotary.store_factory` trait覆盖

## jupyter-trust CLI

nbformat 注册了一个命令行工具 `jupyter trust`：

```bash
# 签名一个或多个Notebook
jupyter trust notebook1.ipynb notebook2.ipynb

# 清除所有可信签名并生成新密钥
jupyter trust --reset
```

[F-097]

### CLI行为

- 对于每个输入文件，读取后检查是否已签名
- 已签名：打印"already signed: {path}"
- 未签名：签名并打印"signing: {path}"
- 签名后Notebook的metadata.signature会被写入
- 支持管道输入：`cat notebook.ipynb | jupyter trust -`

### --reset

`--reset` 选项：
1. 生成新的随机密钥（覆盖notebook_secret）
2. 删除nbsignatures.db（清除所有可信签名记录）
3. 重新初始化数据库
4. 打印"Trust store reset and new secret generated"

## trust/notebook的关系

- 签名不等于信任：签名只是一个标记，信任判断由调用方（JupyterLab/Notebook Server）根据签名和输出安全性决定
- `metadata.trusted` 字段是运行时标记，在写入时被`strip_transient()`移除
- `metadata.signature` 是持久化的签名，写入文件时保留
- 签名数据库是用户级别的，与具体Notebook无关

[F-098]

## 安全注意事项

- 不要在Notebook中硬编码密钥
- 共享环境下每个用户应有独立的密钥和数据库
- 不信任来源的Notebook打开时会提示"Not Trusted"，输出被清理
- 仅对自己信任的Notebook执行`jupyter trust`
- 密钥文件权限应为600（仅所有者可读写）

## 相关概念

- [读写API](04-read-write-api.md)
- [v4格式详解](09-v4-format.md)
