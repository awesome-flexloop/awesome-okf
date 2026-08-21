---
okf_version: "0.2"
type: "concept"
title: "Channel 与凭证安全"
sources:
  - "conda_lock/models/channel.py"
---

# Channel 与凭证安全

`Channel` 是 conda-lock 中表示 conda 包通道的不可变模型，核心设计目标是**凭证安全**——不在锁文件中存储明文 token 或密码，始终通过环境变量引用凭证。同时支持 conda/mamba v1/mamba v2(libmamba) 三种 token 脱敏格式的识别和归一化。

## 不可变模型

```python
# conda_lock/models/channel.py

class Channel(BaseModel):
    model_config = {"frozen": True}

    url: str
    used_env_vars: frozenset[str] = frozenset()
```

[F-001]

使用 Pydantic 的 `frozen=True` 配置，Channel 实例创建后不可修改。`url` 字段存储的是包含环境变量占位符的 URL（而非含明文凭证的 URL），`used_env_vars` 记录该通道引用的所有环境变量名称。

使用 `frozenset` 而非 `set` 进一步确保不可变性。

## from_string()：通道字符串解析

`Channel.from_string()` 类方法是创建 Channel 实例的主要入口，它自动检测两种凭证格式并脱敏：

```python
@classmethod
def from_string(cls, url: str) -> "Channel":
```

[F-002]

### Token 认证（/t/$TOKEN/ 格式）

私有通道（如 Anaconda Enterprise、私有 conda-forge 镜像）常使用 token 认证，URL 格式为 `https://host/t/<token>/channel`。`from_string()` 检测到 `/t/.../` 模式时：

1. 提取 token 值
2. 生成唯一环境变量名（如 `CONDA_TOKEN_12345`）
3. 将 token 存入环境变量 `os.environ[env_var] = token`
4. URL 中的 token 替换为 `$ENV_VAR` 引用
5. 记录使用的环境变量到 `used_env_vars`

```python
# 输入
ch = Channel.from_string("https://conda.anaconda.org/t/abc123token/my-channel")
# ch.url == "https://conda.anaconda.org/t/$CONDA_TOKEN_12345/my-channel"
# ch.used_env_vars == frozenset({"CONDA_TOKEN_12345"})
# os.environ["CONDA_TOKEN_12345"] == "abc123token"
```

[F-003]

### Basic Auth（user:pass@ 格式）

另一种常见的私有通道认证方式是 HTTP Basic Auth，URL 格式为 `https://user:password@host/channel`。`from_string()` 检测到该模式时同样脱敏，分别为用户名和密码创建环境变量。

```python
# 输入
ch = Channel.from_string("https://admin:s3cret@private.conda.com/channel")
# ch.url == "https://$CONDA_CHANNEL_USER_67890:$CONDA_CHANNEL_PWD_67890@private.conda.com/channel"
```

[F-004]

## env_replaced_url()：运行时 URL 展开

当需要将通道 URL 传给 conda/mamba 命令行时，调用 `env_replaced_url()` 将环境变量占位符替换为实际值：

```python
def env_replaced_url(self) -> str:
    result = self.url
    for var in self.used_env_vars:
        result = result.replace(f"${var}", os.environ.get(var, ""))
    return result
```

[F-005]

```python
# 假设环境变量已设置
ch = Channel.from_string("https://conda.anaconda.org/t/abc123/my-channel")
print(ch.url)              # "https://conda.anaconda.org/t/$CONDA_TOKEN_.../my-channel"
print(ch.env_replaced_url())  # "https://conda.anaconda.org/t/abc123/my-channel"
```

锁文件中存储的是含占位符的 URL（安全），传给 conda 命令时才展开（需要凭证），两者职责分离。

## 三种 Token 脱敏格式

不同的 conda 求解器后端在 dry-run JSON 输出中对 token URL 有不同的脱敏格式 [F-006]：

| 后端 | 脱敏格式 | 示例 |
|------|---------|------|
| conda (classic) | `<TOKEN>` | `/t/<TOKEN>/channel` |
| mamba v1 | `*****` | `/t/*****/channel` |
| mamba v2 (libmamba) | `**********` | `/t/**********/channel` |

Channel 提供三个方法分别生成对应格式的脱敏 URL：

```python
def conda_token_replaced_url(self) -> str: ...      # <TOKEN>
def mamba_v1_token_replaced_url(self) -> str: ...    # *****
def mamba_v2_token_replaced_url(self) -> str: ...    # **********
```

## normalize_url_with_placeholders()：归一化

`normalize_url_with_placeholders()` 类方法将不同脱敏格式统一归一化为环境变量占位符格式，确保不同求解器后端输出的锁文件中 URL 表示一致 [F-007]：

```python
@classmethod
def normalize_url_with_placeholders(cls, url: str) -> str:
    for mask in ["<TOKEN>", "*****", "**********"]:
        url = url.replace(mask, "$CONDA_TOKEN")
    return url
```

这在写入锁文件时非常重要——无论用 conda 还是 mamba 求解，锁文件中的通道 URL 格式统一，避免因求解器不同导致锁文件无意义的差异。

## 凭证安全设计原则

Channel 模型遵循以下安全原则：

1. **不存储明文**：任何时候 `url` 字段都不包含明文 token/密码，只包含环境变量引用 [F-008]
2. **环境变量传递**：凭证通过 `os.environ` 存储，传给子进程时通过环境变量继承
3. **锁文件脱敏**：写入锁文件时使用脱敏格式（`<TOKEN>` 或 `$ENV_VAR`），防止凭证意外提交到版本控制
4. **格式归一化**：统一不同求解器的脱敏格式，避免锁文件 diff 噪音

```
用户输入 URL (含明文凭证)
        │
        ▼
  from_string() 检测凭证
        │
        ├─→ 凭证存入环境变量
        │
        ▼
  Channel.url = 含 $VAR 占位符的 URL  ←── 安全存储/写入锁文件
        │
        ▼
  env_replaced_url() 展开
        │
        ▼
  完整 URL (含凭证)  ←── 仅在执行子进程时临时使用
        │
        ▼
  conda/mamba 子进程 (通过环境变量/命令行参数接收凭证)
```

## 相关概念

- [LockSpecification 模型](03-lock-specification.md)
- [四类依赖模型](05-dependency-types.md)
- [Conda 求解器](08-conda-solver.md)
- [Conda 调用层](13-invoke-conda.md)
