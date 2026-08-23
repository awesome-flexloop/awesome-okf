---
okf_version: "0.2"
type: reference
title: "锁定规格模型 (models/lock_spec.py)"
sources:
  - "conda_lock/models/lock_spec.py"
  - "conda_lock/models/channel.py"
  - "conda_lock/models/pip_repository.py"
---

# 锁定规格模型 (models/lock_spec.py)

`LockSpecification` 是 conda-lock 的核心数据模型，承载从源文件解析到求解器输入之间的完整中间状态。它包含按平台分组的依赖字典、通道列表、源文件追踪、PyPI 仓库配置等信息。依赖模型通过 Pydantic 实现，使用 TypeAlias 联合类型支持四类依赖。

## 依赖模型层次

```python
# conda_lock/models/lock_spec.py

from __future__ import annotations
from typing import Dict, List, Optional, Set, Union
from pydantic import BaseModel

class _BaseDependency(BaseModel):
    """依赖基类，包含所有依赖类型共有的字段。"""
    name: str
    manager: str = "conda"  # "conda" 或 "pip"
    category: str = "main"  # 依赖类别，如 main/dev/test
    extras: Optional[List[str]] = None  # pip extras，如 ["dev", "test"]
    markers: Optional[dict] = None  # PEP 508 环境标记

class VersionedDependency(_BaseDependency):
    """版本化依赖：通过名称+版本+build号指定 conda/pip 包。"""
    version: str = ""
    build: Optional[str] = None
    conda_channel: Optional[str] = None
    hash: Optional[str] = None  # md5 for conda, sha256 for pip

class URLDependency(_BaseDependency):
    """URL 依赖：直接通过包文件 URL 指定。"""
    url: str
    hashes: Optional[List[str]] = None

class VCSDependency(_BaseDependency):
    """VCS 依赖：通过 Git 等版本控制系统指定。"""
    source: str = "git"  # 目前仅支持 git
    vcs: str = ""
    rev: Optional[str] = None  # commit/branch/tag
    subdirectory: Optional[str] = None

class PathDependency(_BaseDependency):
    """本地路径依赖：通过文件系统路径指定。"""
    path: str
    is_directory: bool = False
    subdirectory: Optional[str] = None

# Dependency 是四种依赖类型的联合
Dependency = Union[VersionedDependency, URLDependency, VCSDependency, PathDependency]
```

**设计要点**：
- **四层继承**：`_BaseDependency` 定义公共字段（name/manager/category/extras/markers），四个子类各扩展自己的定位字段。
- **TypeAlias 联合**：使用 Python 的 `Union` 类型（或 `|` 语法）将四种依赖类型合并为 `Dependency` 类型别名，在 Pydantic 模型中通过判别字段（discriminator）自动区分。
- **manager 字段**：标记依赖由 conda 还是 pip 管理，决定后续走 conda_solver 还是 pypi_solver 求解路径。

## LockSpecification 主模型

```python
# conda_lock/models/lock_spec.py

from typing import Dict, List, Tuple
from pydantic import BaseModel
from .channel import Channel
from .pip_repository import PipRepository

class LockSpecification(BaseModel):
    """锁定规格：从一个或多个源文件解析出的完整锁定输入。"""
    dependencies: Dict[str, List[Dependency]]
    # 按平台分组的依赖字典，key 为平台标识（如 "linux-64"），
    # value 为该平台需要求解的 Dependency 列表

    channels: List[Channel] = []
    # conda 通道列表，按优先级排列，使用 Channel 不可变模型

    sources: List[str] = []
    # 源文件路径列表，用于追踪锁文件由哪些文件生成

    pip_repositories: List[PipRepository] = []
    # PyPI 私有仓库配置列表

    allow_pypi_requests: bool = True
    # 是否允许向 PyPI 发送请求求解 pip 依赖

    @property
    def platforms(self) -> List[str]:
        """返回所有目标平台，从 dependencies 字典的 key 提取。"""
        return list(self.dependencies.keys())
```

> **注意**：`LockSpecification` 模型本身没有 `with_categories()` 方法。类别过滤是在 `src_parser.make_lock_spec()` 函数中通过 `filtered_categories` 参数实现的——在构建 LockSpecification 时直接过滤 dependencies 字典，仅保留属于目标类别的依赖。详见 [源文件解析](../concepts/07-source-parsers.md) 和 [LockSpecification 模型](../concepts/03-lock-specification.md)。

**设计要点**：
- **按平台分组**：`dependencies` 字典的 key 是平台字符串（如 `linux-64`、`osx-arm64`、`win-64`），value 是该平台的依赖列表。平台 selectors（`# [linux]`）在源解析阶段已经处理，每个平台的依赖已经预先过滤。
- **Channel 不可变模型**：`channels` 列表使用 Pydantic `frozen=True` 的 Channel 模型，确保通道配置不可被意外修改。Channel 自动处理凭证脱敏，不存储明文 token/密码。
- **sources 溯源**：记录参与锁定的所有源文件路径，写入锁文件的 metadata.sources 字段，支持锁文件审计。
- **platforms 属性**：便捷属性，从 dependencies 字典键提取平台列表，避免外部手动遍历。
- **类别过滤**：类别过滤不在 LockSpecification 模型上实现，而是在 `src_parser.make_lock_spec()` 的 `filtered_categories` 参数中完成。`lock`/`render` 命令的 `--dev-dependencies/--no-dev-dependencies` 和 `install` 命令的 `--dev/--no-dev` 标志控制目标类别集合，解析器在构建 LockSpecification 时直接过滤 dependencies。

## Channel 模型（凭证安全）

```python
# conda_lock/models/channel.py

import os
import re
from pydantic import BaseModel

class Channel(BaseModel):
    """Conda 通道模型，自动处理凭证脱敏与环境变量替换。"""
    model_config = {"frozen": True}

    url: str
    used_env_vars: frozenset[str] = frozenset()

    @classmethod
    def from_string(cls, url: str) -> "Channel":
        """从通道字符串解析 Channel，自动检测并脱敏凭证。

        支持的凭证格式：
        - Token: https://conda.anaconda.org/t/$TOKEN/channel 或 /t/<token>/
        - Basic auth: https://user:pass@host/channel
        """
        used_env_vars = set()

        # 检测 /t/$TOKEN/ 格式的 token 认证
        token_match = re.search(r"/t/([^/]+)/", url)
        if token_match:
            token = token_match.group(1)
            env_var = f"CONDA_TOKEN_{abs(hash(url))}"
            url = url.replace(f"/t/{token}/", f"/t/${env_var}/")
            os.environ.setdefault(env_var, token)
            used_env_vars.add(env_var)

        # 检测 user:pass@ 格式的 basic auth
        auth_match = re.match(r"https?://([^:]+):([^@]+)@", url)
        if auth_match:
            user, pwd = auth_match.groups()
            env_var_user = f"CONDA_CHANNEL_USER_{abs(hash(url))}"
            env_var_pwd = f"CONDA_CHANNEL_PWD_{abs(hash(url))}"
            url = url.replace(f"{user}:{pwd}@", f"${env_var_user}:${env_var_pwd}@")
            os.environ.setdefault(env_var_user, user)
            os.environ.setdefault(env_var_pwd, pwd)
            used_env_vars.update([env_var_user, env_var_pwd])

        return cls(url=url, used_env_vars=frozenset(used_env_vars))

    def env_replaced_url(self) -> str:
        """将 URL 中的环境变量占位符替换为实际值，用于传给 conda 命令。"""
        result = self.url
        for var in self.used_env_vars:
            result = result.replace(f"${var}", os.environ.get(var, ""))
        return result

    def conda_token_replaced_url(self) -> str:
        """返回使用 <TOKEN> 脱敏格式的 URL（conda 原生格式）。"""
        return self._token_mask("<TOKEN>")

    def mamba_v1_token_replaced_url(self) -> str:
        """返回使用 ***** 脱敏格式的 URL（mamba v1 格式）。"""
        return self._token_mask("*****")

    def mamba_v2_token_replaced_url(self) -> str:
        """返回使用 ********** 脱敏格式的 URL（mamba v2/libmamba 格式）。"""
        return self._token_mask("**********")

    @classmethod
    def normalize_url_with_placeholders(cls, url: str) -> str:
        """将锁文件中不同格式的脱敏 URL 归一化为环境变量占位符格式，
        确保不同求解器后端输出的锁文件中 URL 表示一致。"""
        for mask in ["<TOKEN>", "*****", "**********"]:
            url = url.replace(mask, "$CONDA_TOKEN")
        return url
```

**关键安全设计**：
- **不存储明文凭证**：解析时将 token/password 存入环境变量，URL 中只保留环境变量引用（`$VAR_NAME`），防止凭证泄露到锁文件。
- **多格式兼容**：conda/mamba v1/mamba v2 三种 token 脱敏格式（`<TOKEN>`/`*****/**********`）都能被识别和归一化。
- **不可变模型**：使用 Pydantic `frozen=True`，Channel 实例创建后不可修改，防止意外篡改凭证状态。
