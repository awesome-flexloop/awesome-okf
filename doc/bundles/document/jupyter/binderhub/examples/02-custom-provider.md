---
type: Example
title: "自定义RepoProvider开发"
description: "从零开发自定义RepoProvider的完整教程，理解RepoProvider契约、实现必需方法、display_config配置、注册Provider、GiteaProvider完整示例、Git凭证支持、Spec验证规则"
tags: [binderhub, repoprovider, development, plugin, gitea, custom-provider, git-credentials]
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T20:45:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/binderhub/binderhub/
---

# 自定义 RepoProvider 开发

BinderHub 的 Provider 系统采用插件化设计，通过继承 `RepoProvider` 基类即可扩展支持新的代码仓库或数据源。本文档将从零开始，逐步讲解如何开发一个自定义 RepoProvider，并以自建 Gitea 实例的 `GiteaProvider` 作为完整示例。

## 1. 理解 RepoProvider 契约

### 1.1 RepoProvider 的角色

RepoProvider 负责将用户提供的 spec（如 `gh/user/repo/HEAD`）解析为具体的 Git 仓库 URL 和确定的 Git 引用（commit SHA）。每个 Provider 对应一种代码托管平台或数据源类型。

### 1.2 必须实现的方法

继承 `RepoProvider` 时，以下方法**必须**在子类中重写：

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `get_resolved_ref()` | `async → str` | 将用户提供的 ref（分支名/tag/HEAD）解析为完整的 40 字符 commit SHA |
| `get_resolved_spec()` | `async → str` | 返回包含已解析 ref 的 spec 字符串 |
| `get_repo_url()` | `str` | 返回 repo2docker 可克隆的 Git 仓库 URL（HTTPS/SSH） |
| `get_resolved_ref_url()` | `async → str` | 返回指向该 commit 的网页 URL（用于页面展示和链接） |
| `get_build_slug()` | `str` | 返回唯一的构建标识符（用于镜像命名和缓存） |

### 1.3 Provider 生命周期

```
用户提交 spec（如 "gitea/myorg/myrepo/main"）
    │
    ▼
__init__(spec=...)     # 解析 spec，提取 user/repo/ref 等信息
    │
    ▼
get_resolved_ref()     # 异步：调用平台API或git ls-remote解析ref为commit SHA
    │
    ▼
get_resolved_spec()    # 返回 "myorg/myrepo/<sha>" 格式的已解析spec
    │
    ▼
get_repo_url()         # 返回 "https://gitea.example.com/myorg/myrepo.git"
    │
    ▼
get_build_slug()       # 返回 "myorg-myrepo" 作为构建标识
    │
    ▼
get_resolved_ref_url() # 返回 "https://gitea.example.com/myorg/myrepo/commit/<sha>"
```

## 2. RepoProvider 基类结构

先看一下 `RepoProvider` 基类的核心 traitlets 和方法：

```python
from traitlets import Bool, Dict, List, Set, Unicode
from traitlets.config import LoggingConfigurable

class RepoProvider(LoggingConfigurable):
    # ---- 基本属性 ----
    name = Unicode(help="人类可读的Provider名称")
    spec = Unicode(help="用户提供的待解析spec字符串")
    unresolved_ref = Unicode()  # 解析前的ref（如main/HEAD/v1.0）

    # ---- 访问控制 ----
    allowed_specs = List(Unicode(), config=True, help="允许构建的spec正则列表")
    banned_specs = List(Unicode(), config=True, help="禁止构建的spec正则列表")
    high_quota_specs = List(Unicode(), config=True, help="高配额spec正则列表")
    spec_config = List(Dict(), config=True, help="按spec匹配的自定义配置")

    # ---- Git凭证 ----
    git_credentials = Unicode("", config=True,
        help="克隆私有仓库时的Git凭证，格式符合git-credential helper输出")

    # ---- 前端展示配置 ----
    display_config = {}  # 前端UI配置字典

    # ---- 必须重写的方法 ----
    async def get_resolved_ref(self):
        raise NotImplementedError
    async def get_resolved_spec(self):
        raise NotImplementedError
    def get_repo_url(self):
        raise NotImplementedError
    async def get_resolved_ref_url(self):
        raise NotImplementedError
    def get_build_slug(self):
        raise NotImplementedError

    # ---- 工具方法 ----
    def is_banned(self):       # 检查spec是否被禁止
    def has_higher_quota(self): # 检查spec是否享有高配额
    def repo_config(self, settings): # 获取该repo的配置（配额等）
    @staticmethod
    def is_valid_sha1(sha1):   # 验证是否为合法SHA1哈希
```

## 3. display_config 详解

`display_config` 是前端 React UI 用来渲染仓库输入表单的配置字典，决定了用户如何在界面上选择和输入仓库信息。

### 3.1 display_config 字段说明

```python
display_config = {
    "displayName": "Gitea",           # 下拉菜单中显示的名称
    "id": "gitea",                    # URL路径中的provider前缀（如 /v2/gitea/...）
    "spec": {
        "validateRegex": r"[^/]+/[^/]+/.+",  # 验证spec格式的正则
    },
    "detect": {
        "regex": r"^(https?://gitea\.example\.com/)?(?<repo>.*[^/])/?"  # 自动检测URL
    },
    "repo": {
        "label": "Gitea 仓库名或URL",  # 输入框标签
        "placeholder": "example: myorg/myrepo or https://gitea.example.com/myorg/myrepo",
        "urlEncode": False,            # repo部分是否需要URL编码
    },
    "ref": {
        "enabled": True,               # 是否显示ref输入框
        "default": "HEAD",             # 默认ref值
    },
}
```

### 3.2 各字段参考（内置Provider对比）

| Provider | id | spec.validateRegex | repo.urlEncode | ref.enabled |
|----------|-----|-------------------|----------------|-------------|
| GitHub | `gh` | `[^/]+/[^/]+/.+` | False | True |
| GitLab | `gl` | `[^/]+/.+` | True（嵌套命名空间） | True |
| Git | `git` | `[^/]+/.+` | True（URL编码） | True |
| Gist | `gist` | `[^/]+/[^/]+(/[^/]+)?` | False | True |
| Zenodo | `zenodo` | `10\.\d+\/(.)+` | False | False |
| Figshare | `figshare` | `10\.\d+\/(.)+` | False | False |
| CKAN | `ckan` | `[^/]+` | True | False |
| Hydroshare | `hydroshare` | `[^/]+` | True | False |
| Dataverse | `dataverse` | `10\.\d+\/(.)+` | False | False |

> **关键区分**：Git 类 Provider 的 `ref.enabled=True`（分支/tag 可选），DOI/数据集类 Provider 的 `ref.enabled=False`（版本由 API 解析）。

## 4. 完整示例：GiteaProvider

下面我们为自建 Gitea 实例开发一个完整的 `GiteaProvider`。Gitea 是一个开源的轻量级 Git 托管服务，API 兼容 GitHub 风格。

### 4.1 第一步：创建 Provider 类文件

创建 Python 文件（如 `gitea_provider.py`），定义 Provider 类：

```python
"""
Gitea RepoProvider for BinderHub.

支持自建 Gitea 实例的仓库构建，通过 Gitea API v1 解析 ref。
"""

import asyncio
import json
import os
import re
from urllib.parse import quote

from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
from traitlets import Unicode, default
from traitlets.config import LoggingConfigurable

from binderhub.repoproviders import RepoProvider, SHA1_PATTERN


class GiteaProvider(RepoProvider):
    """
    BinderHub RepoProvider for self-hosted Gitea instances.

    Spec 格式: <owner>/<repo>/<ref>
    示例: myorg/myproject/main
    """

    name = Unicode("Gitea")

    # ---- 可配置项（traitlets） ----
    hostname = Unicode(
        "gitea.example.com",
        config=True,
        help="""Gitea 实例的主机名。
        对于自建 Gitea 服务器，修改为你的域名。""",
    )

    access_token = Unicode(
        config=True,
        help="""Gitea API 访问令牌。
        用于访问私有仓库和提高 API 速率限制。
        默认从 GITEA_ACCESS_TOKEN 环境变量读取。""",
    )

    @default("access_token")
    def _access_token_default(self):
        return os.getenv("GITEA_ACCESS_TOKEN", "")

    api_base_path = Unicode(
        "https://{hostname}/api/v1",
        config=True,
        help="""Gitea API 基础路径。
        支持 {hostname} 占位符替换。""",
    )

    # ---- 前端展示配置 ----
    display_config = {
        "displayName": "Gitea",
        "id": "gitea",
        "spec": {"validateRegex": r"[^/]+/[^/]+/.+"},
        "detect": {
            "regex": r"^(https?://gitea\.example\.com/)?(?<repo>.*[^/])/?"
        },
        "repo": {
            "label": "Gitea 仓库名或 URL",
            "placeholder": "example: myorg/myrepo or https://gitea.example.com/myorg/myrepo",
            "urlEncode": False,
        },
        "ref": {"enabled": True, "default": "HEAD"},
    }

    def __init__(self, *args, **kwargs):
        """解析 spec 为 owner、repo 和 unresolved_ref。"""
        super().__init__(*args, **kwargs)

        # spec 格式: "owner/repo/ref"，ref 可包含 "/"
        parts = self.spec.split("/", 2)
        if len(parts) != 3:
            msg = f'Spec must be of the form "owner/repo/ref", provided: "{self.spec}".'
            if len(parts) == 2 and parts[-1] not in {"main", "master", "HEAD"}:
                msg += f' Did you mean "{self.spec}/HEAD"?'
            raise ValueError(msg)

        self.user, self.repo, self.unresolved_ref = parts
        # 去掉 .git 后缀
        if self.repo.endswith(".git"):
            self.repo = self.repo[:-4]

    @default("git_credentials")
    def _default_git_credentials(self):
        """配置 Git 凭证以支持私有仓库克隆。"""
        if self.access_token:
            # Gitea 访问令牌可直接作为密码使用
            return rf"username={self.access_token}\npassword=x-oauth-basic"
        return ""

    def get_repo_url(self):
        """返回 repo2docker 可克隆的 Git HTTPS URL。"""
        return f"https://{self.hostname}/{self.user}/{self.repo}"

    def get_build_slug(self):
        """返回 DNS 安全的构建标识符，用短横线连接 owner 和 repo。"""
        # 将 repo 名中的短横线替换为 _- 以避免歧义
        safe_user = self.user.replace("-", "_-")
        safe_repo = self.repo.replace("-", "_-")
        return f"{safe_user}-{safe_repo}"

    async def get_resolved_ref(self):
        """
        异步解析 unresolved_ref 为 40 字符 commit SHA。

        - 如果 unresolved_ref 已经是 SHA1，直接返回
        - 如果是 HEAD/main/master，通过 API 获取默认分支的最新 commit
        - 否则通过 Gitea API 获取对应分支/tag 的 commit SHA
        """
        if hasattr(self, "resolved_ref"):
            return self.resolved_ref

        # 如果已经是完整 SHA1，直接使用
        if self.is_valid_sha1(self.unresolved_ref):
            self.resolved_ref = self.unresolved_ref
            return self.resolved_ref

        client = AsyncHTTPClient()

        # 处理 HEAD：先获取默认分支名
        ref = self.unresolved_ref
        if ref in ("HEAD", "main", "master"):
            repo_api_url = "{api}/repos/{owner}/{repo}".format(
                api=self.api_base_path.format(hostname=self.hostname),
                owner=quote(self.user, safe=""),
                repo=quote(self.repo, safe=""),
            )
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"token {self.access_token}"

            req = HTTPRequest(repo_api_url, headers=headers, user_agent="BinderHub")
            try:
                resp = await client.fetch(req)
            except HTTPError as e:
                if e.code in (404, 422):
                    return None
                raise

            repo_info = json.loads(resp.body.decode("utf-8"))
            default_branch = repo_info.get("default_branch", "main")

            if ref == "HEAD":
                ref = default_branch
            elif ref == "main" or ref == "master":
                # 如果用户显式指定 main/master 但默认分支不同，仍按指定分支处理
                pass

        # 获取分支或 tag 的 commit SHA
        # 先尝试分支 API
        commit_sha = await self._resolve_ref_via_api(client, ref)
        if commit_sha:
            self.resolved_ref = commit_sha
            return self.resolved_ref

        # API 查询失败，尝试 git ls-remote（备选方案）
        return await self._resolve_ref_via_git()

    async def _resolve_ref_via_api(self, client, ref):
        """通过 Gitea API 获取 ref 对应的 commit SHA。"""
        # Gitea API: GET /api/v1/repos/{owner}/{repo}/git/commits/{sha}
        # 也可以用 branches/tags 端点
        api_base = self.api_base_path.format(hostname=self.hostname)

        # 尝试通过 commit 端点获取（支持分支名、tag名、SHA）
        commit_api_url = "{api}/repos/{owner}/{repo}/git/commits/{ref}".format(
            api=api_base,
            owner=quote(self.user, safe=""),
            repo=quote(self.repo, safe=""),
            ref=quote(ref, safe=""),
        )

        headers = {}
        if self.access_token:
            headers["Authorization"] = f"token {self.access_token}"

        req = HTTPRequest(commit_api_url, headers=headers, user_agent="BinderHub")
        try:
            resp = await client.fetch(req)
        except HTTPError as e:
            if e.code in (404, 422):
                return None
            raise

        commit_info = json.loads(resp.body.decode("utf-8"))
        sha = commit_info.get("sha")
        if sha and self.is_valid_sha1(sha):
            return sha
        return None

    async def _resolve_ref_via_git(self):
        """备选方案：使用 git ls-remote 解析 ref。"""
        repo_url = self.get_repo_url()
        cmd = ["git", "ls-remote", "--", repo_url, self.unresolved_ref]

        # 设置凭证环境变量
        env = os.environ.copy()
        if self.git_credentials:
            env["GIT_CREDENTIAL_ENV"] = self.git_credentials

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, stderr = await proc.communicate()
        retcode = await proc.wait()
        if retcode:
            self.log.error(
                f"git ls-remote failed for {repo_url}: {stderr.decode()}"
            )
            return None
        if not stdout:
            return None
        resolved_ref = stdout.decode().split(None, 1)[0]
        if self.is_valid_sha1(resolved_ref):
            self.resolved_ref = resolved_ref
            return self.resolved_ref
        return None

    async def get_resolved_spec(self):
        """返回包含已解析 commit SHA 的 spec。"""
        if not hasattr(self, "resolved_ref"):
            self.resolved_ref = await self.get_resolved_ref()
        return f"{self.user}/{self.repo}/{self.resolved_ref}"

    async def get_resolved_ref_url(self):
        """返回指向该 commit 的 Gitea 网页 URL。"""
        if not hasattr(self, "resolved_ref"):
            self.resolved_ref = await self.get_resolved_ref()
        return f"https://{self.hostname}/{self.user}/{self.repo}/commit/{self.resolved_ref}"
```

### 4.2 关键实现细节解析

#### 4.2.1 __init__ 中的 spec 解析

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    parts = self.spec.split("/", 2)  # 最多分3段，ref可包含"/"
    self.user, self.repo, self.unresolved_ref = parts
```

**注意**：使用 `split("/", 2)` 而非 `split("/")`，因为 ref 部分可能包含 `/`（如 `feature/my-branch`）。

#### 4.2.2 get_resolved_ref 的分层解析策略

1. **缓存检查**：已解析过则直接返回
2. **SHA1 直接匹配**：如果 ref 已是 40 字符 SHA，无需 API 调用
3. **HEAD 特殊处理**：先通过 API 获取默认分支名
4. **API 查询**：调用 Gitea/Git 平台 API 获取 commit SHA
5. **git ls-remote 备选**：API 不可用时通过 git 命令行解析

#### 4.2.3 get_build_slug 的命名安全

构建 slug 会用于 Docker 镜像名称，必须符合 DNS 标签规范：
- 只能包含小写字母、数字、短横线
- 不能以短横线开头/结尾
- 使用 `_-` 转义原始名称中的短横线，避免歧义

## 5. 在 BinderHub 中注册 Provider

创建 Provider 类后，需要在 `binderhub_config.py` 中注册它。

### 5.1 基本注册

```python
# binderhub_config.py
from gitea_provider import GiteaProvider

# 将 GiteaProvider 添加到已有的 Provider 列表中
c.BinderHub.repo_providers["gitea"] = GiteaProvider
```

### 5.2 替换默认 Provider 列表

如果只想使用自定义 Provider 集合：

```python
# binderhub_config.py
from binderhub.repoproviders import GitHubRepoProvider, GitRepoProvider
from gitea_provider import GiteaProvider

# 仅注册 GitHub、通用 Git 和 Gitea
c.BinderHub.repo_providers = {
    "gh": GitHubRepoProvider,
    "git": GitRepoProvider,
    "gitea": GiteaProvider,
}
```

### 5.3 配置自定义 Provider 的参数

```python
# binderhub_config.py
from gitea_provider import GiteaProvider

c.BinderHub.repo_providers["gitea"] = GiteaProvider

# 配置 Gitea 实例地址和访问令牌
c.GiteaProvider.hostname = "gitea.mycompany.com"
c.GiteaProvider.access_token = "your-gitea-access-token"
c.GiteaProvider.api_base_path = "https://{hostname}/api/v1"

# 配置黑白名单
c.GiteaProvider.banned_specs = [
    ".*test-repo.*",
    ".*spam/.*",
]
c.GiteaProvider.high_quota_specs = [
    "^official-org/.*",
]
```

### 5.4 支持多个 Gitea 实例

如果需要同时支持多个 Gitea 实例，可以创建子类：

```python
# binderhub_config.py
from gitea_provider import GiteaProvider

class GiteaCompanyProvider(GiteaProvider):
    """公司内部 Gitea"""
    hostname = "git.company.com"
    display_config = {
        **GiteaProvider.display_config,
        "displayName": "公司 Git",
        "id": "gitea-company",
        "detect": {"regex": r"^(https?://git\.company\.com/)?(?<repo>.*[^/])/?"},
    }

class GiteaOSSProvider(GiteaProvider):
    """开源社区 Gitea"""
    hostname = "gitea.oss-community.org"
    display_config = {
        **GiteaProvider.display_config,
        "displayName": "社区 Gitea",
        "id": "gitea-oss",
        "detect": {"regex": r"^(https?://gitea\.oss-community\.org/)?(?<repo>.*[^/])/?"},
    }

c.BinderHub.repo_providers["gitea-company"] = GiteaCompanyProvider
c.BinderHub.repo_providers["gitea-oss"] = GiteaOSSProvider
```

## 6. Git 凭证支持（私有仓库）

要支持私有仓库的克隆，需要配置 `git_credentials`。凭证通过 `GIT_CREDENTIAL_ENV` 环境变量传递给 repo2docker，格式符合 git-credential helper 的输出规范。

### 6.1 凭证格式

```
username=<username>\npassword=<password-or-token>
```

### 6.2 Gitea Token 凭证配置

```python
# 在 GiteaProvider 中已实现的默认凭证逻辑
@default("git_credentials")
def _default_git_credentials(self):
    if self.access_token:
        # Gitea 支持用 token 作为用户名或密码
        return rf"username={self.access_token}\npassword=x-oauth-basic"
    return ""
```

### 6.3 其他平台的凭证方式参考

```python
# GitHub Personal Access Token
@default("git_credentials")
def _default_git_credentials(self):
    if self.access_token:
        if self.client_id:
            return r"username={client_id}\npassword={token}".format(
                client_id=self.client_id, token=self.access_token
            )
        else:
            return rf"username={self.access_token}\npassword=x-oauth-basic"
    return ""

# GitLab Private Token
@default("git_credentials")
def _default_git_credentials(self):
    if self.private_token:
        return rf"username=binderhub\npassword={self.private_token}"
    return ""
```

### 6.4 凭证安全注意事项

1. **不要硬编码 Token**：从环境变量或 Kubernetes Secret 读取
2. **最小权限原则**：Token 只需 `repo:read` 权限
3. **凭证传递路径**：`git_credentials` → `GIT_CREDENTIAL_ENV` 环境变量 → 构建 Pod → repo2docker → git clone
4. **Kubernetes 部署**：通过 Secret 挂载为环境变量，不要写入 ConfigMap

```python
# 安全的凭证加载方式
import os
c.GiteaProvider.access_token = os.environ.get("GITEA_ACCESS_TOKEN", "")
```

## 7. Spec 验证规则

### 7.1 banned_specs 黑名单

```python
c.GiteaProvider.banned_specs = [
    # 禁止恶意用户
    "^malicious-user/.*",
    # 禁止测试仓库（忽略大小写）
    "(?i).*/test-.*",
    # 禁止特定组织的所有仓库
    "^banned-org/.*",
]
```

判断逻辑：
```python
def is_banned(self):
    for banned in self.banned_specs:
        if re.match(banned, self.spec, re.IGNORECASE):
            return True
    if self.allowed_specs:
        for allowed in self.allowed_specs:
            if re.match(allowed, self.spec, re.IGNORECASE):
                return False
        return True
    return False
```

### 7.2 allowed_specs 白名单

设置后只有匹配白名单的 spec 才被允许（黑名单优先）：

```python
c.GiteaProvider.allowed_specs = [
    "^trusted-org/.*",
    "^partner-org/.*",
]
```

### 7.3 spec_config 自定义配置

为匹配特定模式的仓库设置自定义配额等配置：

```python
c.GiteaProvider.spec_config = [
    {
        "pattern": "^official-org/course-.*",
        "config": {"quota": 50},  # 课程仓库高并发
    },
    {
        "pattern": "^research-group/.*",
        "config": {"quota": 10},
    },
]
```

### 7.4 high_quota_specs 高配额标记

```python
c.GiteaProvider.high_quota_specs = [
    "^official-org/.*",
    "^trusted-partner/.*",
]
c.BinderHub.per_repo_quota = 5          # 普通仓库配额
c.BinderHub.per_repo_quota_higher = 20   # 高配额仓库上限
```

## 8. 测试自定义 Provider

### 8.1 单元测试模板

```python
# test_gitea_provider.py
import pytest
from gitea_provider import GiteaProvider
from traitlets.config import Config


@pytest.fixture
def provider():
    """创建测试用的 GiteaProvider 实例。"""
    cfg = Config()
    cfg.GiteaProvider.hostname = "gitea.example.com"
    p = GiteaProvider(spec="myorg/myrepo/main", config=cfg)
    return p


def test_spec_parsing(provider):
    """测试spec解析是否正确。"""
    assert provider.user == "myorg"
    assert provider.repo == "myrepo"
    assert provider.unresolved_ref == "main"


def test_repo_url(provider):
    """测试克隆URL生成。"""
    assert provider.get_repo_url() == "https://gitea.example.com/myorg/myrepo"


def test_build_slug(provider):
    """测试构建slug生成。"""
    slug = provider.get_build_slug()
    assert slug == "myorg-myrepo"
    assert "-" in slug  # 符合DNS命名


def test_invalid_spec():
    """测试无效spec抛出异常。"""
    cfg = Config()
    cfg.GiteaProvider.hostname = "gitea.example.com"
    with pytest.raises(ValueError):
        GiteaProvider(spec="invalid-spec", config=cfg)


@pytest.mark.asyncio
async def test_sha1_ref_direct_return():
    """测试已为SHA1的ref直接返回。"""
    cfg = Config()
    cfg.GiteaProvider.hostname = "gitea.example.com"
    sha = "a" * 40
    p = GiteaProvider(spec=f"myorg/myrepo/{sha}", config=cfg)
    resolved = await p.get_resolved_ref()
    assert resolved == sha
```

### 8.2 手动测试（命令行触发构建）

```bash
# 启动BinderHub后，使用curl测试构建流程
# 注意：需要先获取build_token，这里简化演示

# 1. 先访问UI页面获取token
curl -c cookies.txt http://localhost:8585/v2/gitea/myorg/myrepo/main

# 2. 连接SSE事件流
curl -N \
  -H "Accept: text/event-stream" \
  "http://localhost:8585/build/gitea/myorg/myrepo/main"
```

### 8.3 Provider 注册验证

启动 BinderHub 后，访问 `/api/repoproviders` 端点验证 Provider 是否正确注册：

```bash
curl http://localhost:8585/api/repoproviders | python -m json.tool
```

响应中应包含：

```json
{
  "gitea": {
    "displayName": "Gitea",
    "id": "gitea",
    "spec": {"validateRegex": "[^/]+/[^/]+/.+"},
    "repo": {
      "label": "Gitea 仓库名或URL",
      "placeholder": "example: myorg/myrepo or https://gitea.example.com/myorg/myrepo",
      "urlEncode": false
    },
    "ref": {"enabled": true, "default": "HEAD"}
  }
}
```

## 9. 高级主题

### 9.1 带嵌套命名空间的 Provider（类 GitLab）

如果你的 Git 平台支持嵌套组织/分组（如 `group/subgroup/repo`），需要 URL 编码处理：

```python
class NestedGitProvider(RepoProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 只在第一个"/"处分割，因为namespace包含"/"
        self.quoted_namespace, unresolved_ref = self.spec.split("/", 1)
        self.namespace = urllib.parse.unquote(self.quoted_namespace)
        self.unresolved_ref = urllib.parse.unquote(unresolved_ref)

    def get_build_slug(self):
        # 将多层namespace的"/"替换为"-"
        return "-".join(
            part.replace("-", "_-")
            for part in self.namespace.split("/")
        )
```

对应的 `display_config` 中 `repo.urlEncode` 应设为 `True`。

### 9.2 DOI/数据集类 Provider（无 Ref）

对于非 Git 数据源（如 Zenodo、Figshare），ref 由 API 自动解析，不需要用户指定：

```python
class DatasetProvider(RepoProvider):
    display_config = {
        "displayName": "My Dataset",
        "id": "mydataset",
        "spec": {"validateRegex": r"10\.\d+\/(.)+"},
        "repo": {
            "label": "数据集 DOI",
            "placeholder": "example: 10.1234/dataset.12345",
            "urlEncode": False,
        },
        "ref": {"enabled": False},  # 不显示ref输入框
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doi = self.spec  # 整个spec就是DOI

    async def get_resolved_ref(self):
        # 通过DOI解析API获取版本号
        client = AsyncHTTPClient()
        resp = await client.fetch(f"https://doi.org/{self.doi}")
        self.record_id = extract_version(resp.effective_url)
        return self.record_id
```

### 9.3 添加事件 Schema

新增 Provider 后，如果需要让事件日志系统识别该 Provider，需要更新 `event-schemas/launch.json`：

```json
{
  "properties": {
    "provider": {
      "enum": ["gh", "gist", "git", "gl", "zenodo", "figshare",
               "hydroshare", "dataverse", "ckan", "gitea"]
    }
  }
}
```

### 9.4 Provider 中的缓存策略

对于 API 调用频繁的 Provider，建议实现缓存以避免触发速率限制：

```python
from binderhub.utils import Cache

class CachedProvider(RepoProvider):
    # 成功结果缓存（带ETag）
    cache = Cache(1024)
    # 404结果缓存（5分钟过期）
    cache_404 = Cache(1024, max_age=300)

    async def get_resolved_ref(self):
        api_url = self._build_api_url()
        cached = self.cache.get(api_url)
        if cached:
            return cached["sha"]
        # ... API调用逻辑 ...
        self.cache.set(api_url, {"etag": resp.headers.get("ETag"), "sha": sha})
        return sha
```

## 10. 常见陷阱

| 陷阱 | 说明 | 解决方案 |
|------|------|----------|
| spec 分割错误 | 使用 `split("/")` 导致含 `/` 的分支名被截断 | 使用 `split("/", 2)` 只分三段 |
| build_slug 含非法字符 | Docker 镜像名不允许大写、下划线、点号 | 使用 `escapism` 库或手动转义 |
| ref 解析未缓存 | 每次请求都调用 API，触发速率限制 | 实现基于 LRU Cache 的缓存 |
| 忘记处理 `.git` 后缀 | 用户输入 `repo.git` 导致 API 404 | 在 `__init__` 中 strip `.git` 后缀 |
| HEAD 处理不当 | 直接把 HEAD 传给 API 返回 404 | 先获取默认分支名，再解析 |
| 异步方法未 await | `get_resolved_ref_url` 调用 `get_resolved_ref` 忘记 await | 所有 async 方法调用必须 await |
| display_config.id 冲突 | 自定义 Provider 的 id 与内置冲突 | 使用唯一前缀（如 `gitea-`） |
| git_credentials 格式错误 | 换行符未正确转义 | 使用 raw string `rf"..."` 确保 `\n` 正确 |
| URL 编码问题 | 嵌套命名空间中的 `/` 未编码导致路由错误 | 设置 `repo.urlEncode: True` |
| API 错误处理不足 | 404/403/429 等 HTTP 错误未捕获 | 使用 try/except 处理 HTTPError，区分错误码 |
