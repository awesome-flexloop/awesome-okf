---
type: Concept
title: "RepoProvider 仓库提供者插件系统"
description: "深入解析 BinderHub 的 RepoProvider 插件架构，包括 RepoProvider 抽象基类的配置系统、引用解析机制、构建 slug 生成、九种内置仓库提供者（GitHub/GitLab/Gist/Git/Zenodo/Figshare/Dataverse/Hydroshare/CKAN）的实现细节，以及辅助函数 tokenize_spec、strip_suffix 和 _safe_build_slug 的工作原理。"
tags: [binderhub, repoprovider, github, gitlab, git, zenodo, figshare, dataverse, hydroshare, ckan, plugin, resolvref]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T20:45:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/binderhub/binderhub/
---

# RepoProvider 仓库提供者插件系统

## 概述

BinderHub 的 RepoProvider 系统定义在 repoproviders.py 中，是一个可扩展的插件架构，用于支持多种版本控制平台和数据仓库作为 Binder 镜像的来源。每个提供者负责解析用户提供的仓库引用（spec）、将符号引用（如分支名 `main`）解析为具体的 commit SHA、提供 Git 克隆 URL、生成历史版本 URL，以及创建唯一且安全的构建标识（build slug）。

## 类继承体系

```
LoggingConfigurable
    └── RepoProvider (抽象基类)
        ├── FakeProvider          # 测试用
        ├── ZenodoProvider        # Zenodo DOI
        ├── FigshareProvider      # Figshare DOI
        ├── DataverseProvider     # Dataverse 数据集
        ├── HydroshareProvider    # Hydroshare 资源
        ├── CKANProvider          # CKAN 数据集
        ├── GitRepoProvider       # 通用 Git 仓库
        ├── GitLabRepoProvider    # GitLab
        └── GitHubRepoProvider    # GitHub
            └── GistRepoProvider  # GitHub Gist
```

## 模块级常量与辅助函数

### SHA1_PATTERN

```python
SHA1_PATTERN = re.compile(r"[0-9a-f]{40}")
```

用于验证字符串是否为合法的 Git commit SHA1 哈希值（40位十六进制小写）。`RepoProvider.is_valid_sha1()` 静态方法使用此正则：

```python
@staticmethod
def is_valid_sha1(sha1):
    return bool(SHA1_PATTERN.match(sha1))
```

### GIT_SSH_PATTERN

```python
GIT_SSH_PATTERN = re.compile(r"([\w\-]+@[\w\-\.]+):(.+)", re.IGNORECASE)
```

匹配 Git SSH URL 格式（如 `git@github.com:user/repo.git`），用于在 GitRepoProvider 中将其转换为标准的 `ssh://` URL。

### GITHUB_RATE_LIMIT 指标

```python
from prometheus_client import Gauge
GITHUB_RATE_LIMIT = Gauge(
    "binderhub_github_rate_limit_remaining", "GitHub rate limit remaining"
)
```

Prometheus Gauge 指标，实时记录 GitHub API 的剩余请求配额，用于监控和告警。

### tokenize_spec()

```python
def tokenize_spec(spec):
    """Tokenize a GitHub-style spec into parts, error if spec invalid."""
    spec_parts = spec.split("/", 2)  # allow ref to contain "/"
    if len(spec_parts) != 3:
        msg = f'Spec is not of the form "user/repo/ref", provided: "{spec}".'
        if len(spec_parts) == 2 and spec_parts[-1] not in {"main", "master", "HEAD"}:
            msg += f' Did you mean "{spec}/HEAD"?'
        raise ValueError(msg)
    return spec_parts
```

将 GitHub 风格的 spec（`user/repo/ref`）分割为三部分。使用 `split("/", 2)` 只分割两次，允许 ref 部分包含斜杠（如 feature 分支名 `feature/my-feature`）。当只提供两部分时，给出友好提示建议添加 `/HEAD`。

### strip_suffix()

```python
def strip_suffix(text, suffix):
    if text.endswith(suffix):
        text = text[: -(len(suffix))]
    return text
```

简单工具函数，移除字符串末尾的指定后缀。用于去除仓库 URL 末尾的 `.git`。

### _safe_build_slug() 与 _generate_build_name()

虽然定义在 builder.py 中，但与 RepoProvider 的 `get_build_slug()` 密切相关：

```python
def _safe_build_slug(build_slug, limit, hash_length=6):
    build_slug_hash = hashlib.sha256(build_slug.encode("utf-8")).hexdigest()
    safe_chars = set(string.ascii_letters + string.digits)
    def escape(s):
        return escapism.escape(s, safe=safe_chars, escape_char="-")
    build_slug = escape(build_slug)
    return "{name}-{hash}".format(
        name=build_slug[: limit - hash_length - 1],
        hash=build_slug_hash[:hash_length],
    ).lower()
```

`_safe_build_slug()` 使用 `escapism` 库将任意字符串转为 DNS/镜像名安全的格式（仅小写字母+数字+连字符），并在末尾附加哈希前缀确保唯一性和长度限制。

## RepoProvider 抽象基类

`RepoProvider`（repoproviders.py:55-215）是所有仓库提供者的基类，继承自 `LoggingConfigurable`。

### 核心 Traitlets 属性

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `name` | `Unicode` | 无 | 提供者的人类可读名称（如 "GitHub"） |
| `spec` | `Unicode` | 无 | 用户提供的待解析 spec 字符串 |
| `allowed_specs` | `List(Unicode)` | `[]` | 允许构建的 spec 正则列表（白名单） |
| `banned_specs` | `List(Unicode)` | `[]` | 禁止构建的 spec 正则列表（黑名单） |
| `high_quota_specs` | `List(Unicode)` | `[]` | 享有更高配额的 spec 正则列表 |
| `spec_config` | `List(Dict)` | `[]` | 按仓库匹配的配置覆盖列表 |
| `unresolved_ref` | `Unicode` | 无 | 未解析的引用（如分支名） |
| `git_credentials` | `Unicode` | `""` | Git 克隆凭证 |
| `display_config` | `dict` | `{}` | 前端 UI 展示配置字典 |

### display_config：前端 UI 配置

每个提供者类通过 `display_config` 类属性声明其在前端 UI 中的配置，用于动态生成输入表单和 URL 检测：

```python
display_config = {
    "displayName": "GitHub",
    "id": "gh",
    "spec": {"validateRegex": r"[^/]+/[^/]+/.+"},
    "detect": {"regex": "^(https?://github.com/)?(?<repo>.*[^/])/?"},
    "repo": {
        "label": "GitHub repository name or URL",
        "placeholder": "example: binder-examples/requirements",
        "urlEncode": False,
    },
    "ref": {"enabled": True, "default": "HEAD"},
}
```

| 字段 | 说明 |
|---|---|
| `displayName` | UI 显示名称 |
| `id` | 提供者前缀标识（对应 URL 中的 `/v2/<id>/`） |
| `spec.validateRegex` | 验证 spec 格式的正则 |
| `detect.regex` | 从粘贴 URL 中检测并提取仓库信息的正则 |
| `repo.label` | 仓库输入框标签 |
| `repo.placeholder` | 输入框占位文本 |
| `repo.urlEncode` | 仓库路径部分是否需要 URL 编码 |
| `ref.enabled` | 是否显示 ref 输入框 |
| `ref.default` | 默认 ref 值 |

### is_banned()：黑名单检查

```python
def is_banned(self):
    for banned in self.banned_specs:
        if re.match(banned, self.spec, re.IGNORECASE):
            return True
    if self.allowed_specs and len(self.allowed_specs):
        for allowed in self.allowed_specs:
            if re.match(allowed, self.spec, re.IGNORECASE):
                return False
        return True  # 白名单非空但不匹配 → 禁止
    return False
```

判断逻辑：
1. 若 spec 匹配 `banned_specs` 中任意正则 → **禁止**；
2. 若 `allowed_specs` 非空且 spec 不在其中 → **禁止**；
3. 其他情况 → **允许**。

所有匹配忽略大小写（`re.IGNORECASE`），因为 Git 仓库路径通常大小写不敏感。

### has_higher_quota()：高配额检查

```python
def has_higher_quota(self):
    for higher_quota in self.high_quota_specs:
        if re.match(higher_quota, self.spec, re.IGNORECASE):
            return True
    return False
```

检查 spec 是否匹配高配额正则列表，用于区分普通仓库和特权仓库的并发限制。

### repo_config()：按仓库配置合并

```python
def repo_config(self, settings):
    repo_config = {}
    if self.has_higher_quota():
        repo_config["quota"] = settings.get("per_repo_quota_higher")
    else:
        repo_config["quota"] = settings.get("per_repo_quota")

    for item in self.spec_config:
        pattern = item.get("pattern")
        config = item.get("config")
        if re.match(pattern, self.spec, re.IGNORECASE):
            repo_config.update(config)
    return repo_config
```

`spec_config` 支持细粒度的按仓库配置覆盖，每一项包含 `pattern`（正则）和 `config`（配置字典），匹配时合并到 repo_config 中。配置示例：

```python
c.GitHubRepoProvider.spec_config = [
    {
        "pattern": "jupyter/notebook.*",
        "config": {"quota": 200}
    }
]
```

### 抽象方法接口

每个子类必须实现以下方法：

| 方法 | 返回类型 | 说明 |
|---|---|---|
| `async get_resolved_ref()` | `str` | 将 unresolved_ref 解析为具体的 commit SHA 或版本标识 |
| `async get_resolved_spec()` | `str` | 返回包含已解析 ref 的完整 spec |
| `get_repo_url()` | `str` | 返回可被 repo2docker 克隆的 Git URL（或直接传给 repo2docker 的 spec） |
| `async get_resolved_ref_url()` | `str` | 返回指向具体 commit 的 Web URL（用于链接和徽章） |
| `get_build_slug()` | `str` | 返回用于构建镜像名的唯一 slug |

## GitHubRepoProvider

`GitHubRepoProvider`（repoproviders.py:853-1112）是最常用的提供者，支持 GitHub.com 和 GitHub Enterprise。

### 配置属性

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hostname` | `Unicode` | `"github.com"` | GitHub 主机名（可设为 GHE 域名） |
| `api_base_path` | `Unicode` | `"https://api.{hostname}"` | API 基础路径，支持 `{hostname}` 模板替换 |
| `client_id` | `Unicode` | 环境变量 `GITHUB_CLIENT_ID` | GitHub OAuth App Client ID |
| `client_secret` | `Unicode` | 环境变量 `GITHUB_CLIENT_SECRET` | GitHub OAuth App Client Secret |
| `access_token` | `Unicode` | 环境变量 `GITHUB_ACCESS_TOKEN` | GitHub 个人访问令牌 |

### 两级缓存机制

```python
cache = Cache(1024)           # 成功结果缓存（基于 ETag，永久有效直到 ETag 变化）
cache_404 = Cache(1024, max_age=300)  # 404 结果缓存（5分钟过期）
```

- **cache**：使用 GitHub API 的 ETag 机制实现条件请求（If-None-Match），GitHub 返回 304 时使用缓存的 SHA，不消耗 API 配额；
- **cache_404**：404 结果设置 5 分钟过期，避免永久缓存不存在的仓库/分支（可能稍后创建）。

### 构造函数解析

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.user, self.repo, self.unresolved_ref = tokenize_spec(self.spec)
    self.repo = strip_suffix(self.repo, ".git")
```

使用 `tokenize_spec()` 将 spec 解析为 `(user, repo, unresolved_ref)` 三元组，并去除 `.git` 后缀。

### GitHub API 请求与速率限制

`github_api_request()` 方法（repoproviders.py:970-1051）封装了 GitHub API 调用，处理认证、ETag 缓存和速率限制：

```python
async def github_api_request(self, api_url, etag=None):
    headers = {}
    if self.access_token:
        headers["Authorization"] = f"token {self.access_token}"
    if etag:
        headers["If-None-Match"] = etag

    req = HTTPRequest(api_url, headers=headers, user_agent="BinderHub", **request_kwargs)
    try:
        resp = await client.fetch(req)
    except HTTPError as e:
        if e.code == 304:
            resp = e.response
        elif e.code == 403 and "x-ratelimit-remaining" in e.response.headers \
             and e.response.headers.get("x-ratelimit-remaining") == "0":
            # 速率限制耗尽
            reset_seconds = int(e.response.headers["x-ratelimit-reset"] - time.time())
            minutes_until_reset = 5 * (1 + (reset_seconds // 60 // 5))
            raise ValueError(f"GitHub rate limit exceeded. Try again in {minutes_until_reset} minutes.")
        elif e.code in (404, 422):
            return None
        else:
            raise

    # 记录速率限制指标
    remaining = int(resp.headers["x-ratelimit-remaining"])
    GITHUB_RATE_LIMIT.set(remaining)
    return resp
```

速率限制处理：
- 检测 `x-ratelimit-remaining: 0` 时抛出友好错误，提示等待时间；
- 根据剩余配额比例选择不同日志级别（<20% warning，<50% info，其余 debug）；
- 使用 Prometheus Gauge 实时记录剩余配额。

### 引用解析

```python
async def get_resolved_ref(self):
    api_url = "{api_base_path}/repos/{user}/{repo}/commits/{ref}".format(
        api_base_path=self.api_base_path.format(hostname=self.hostname),
        user=self.user, repo=self.repo, ref=self.unresolved_ref,
    )
    cached = self.cache.get(api_url)
    if cached:
        etag = cached["etag"]
    else:
        cache_404 = self.cache_404.get(api_url)
        if cache_404:
            return None
        etag = None

    resp = await self.github_api_request(api_url, etag=etag)
    if resp is None:
        self.cache_404.set(api_url, True)
        return None
    if resp.code == 304:
        self.resolved_ref = cached["sha"]
        self.cache.move_to_end(api_url)
        return self.resolved_ref

    ref_info = json.loads(resp.body.decode("utf-8"))
    self.resolved_ref = ref_info["sha"]
    self.cache.set(api_url, {"etag": resp.headers.get("ETag"), "sha": self.resolved_ref})
    return self.resolved_ref
```

通过 GitHub Commits API 将 ref 解析为 SHA：
- `main`/`master`/`HEAD` 等分支名 → 最新 commit SHA；
- 完整 SHA → API 返回相同 SHA；
- Tag 名 → 对应 commit SHA。

### Git 凭证生成

```python
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
```

支持两种认证模式：
- OAuth App 模式：`username=client_id\npassword=access_token`；
- 个人访问令牌模式：`username=token\npassword=x-oauth-basic`。

## GistRepoProvider

`GistRepoProvider`（repoproviders.py:1115-1207）继承自 `GitHubRepoProvider`，支持 GitHub Gist。

### 特殊行为

1. **Spec 格式**：`<username>/<gist-id>[/<ref>]`，ref 可选；
2. **Secret Gist 控制**：`allow_secret_gist` 配置项默认 `False`，禁止构建私有 Gist；
3. **Ref 解析**：通过 Gist API 获取历史版本列表，`HEAD`/`main`/`master`/空字符串 → 最新版本；
4. **hostname** 固定为 `gist.github.com`。

```python
async def get_resolved_ref(self):
    api_url = f"https://api.github.com/gists/{self.gist_id}"
    resp = await self.github_api_request(api_url)
    if resp is None:
        return None
    ref_info = json.loads(resp.body.decode("utf-8"))

    if (not self.allow_secret_gist) and (not ref_info["public"]):
        raise ValueError("You seem to want to use a secret Gist...")

    all_versions = [e["version"] for e in ref_info["history"]]
    if self.unresolved_ref in {"", "HEAD", "master", "main"}:
        self.resolved_ref = all_versions[0]
    else:
        if self.unresolved_ref not in all_versions:
            return None
        self.resolved_ref = self.unresolved_ref
    return self.resolved_ref
```

## GitLabRepoProvider

`GitLabRepoProvider`（repoproviders.py:717-850）支持 GitLab.com 和自建 GitLab 实例。

### 配置属性

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hostname` | `Unicode` | `"gitlab.com"` | GitLab 主机名 |
| `access_token` | `Unicode` | 环境变量 `GITLAB_ACCESS_TOKEN` | OAuth2 访问令牌 |
| `private_token` | `Unicode` | 环境变量 `GITLAB_PRIVATE_TOKEN` | 私有令牌 |

### 特殊处理：嵌套命名空间

GitLab 支持多级嵌套的命名空间（如 `group/subgroup/project`），因此 spec 格式为 `<url-encoded-namespace>/<ref>`，命名空间中的 `/` 需要 URL 编码为 `%2F`：

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.quoted_namespace, unresolved_ref = self.spec.split("/", 1)
    self.namespace = urllib.parse.unquote(self.quoted_namespace)
    self.unresolved_ref = urllib.parse.unquote(unresolved_ref)
```

### API 调用

通过 GitLab v4 API 的 commits 端点解析 ref：

```python
async def get_resolved_ref(self):
    namespace = urllib.parse.quote(self.namespace, safe="")
    api_url = "https://{hostname}/api/v4/projects/{namespace}/repository/commits/{ref}".format(
        hostname=self.hostname, namespace=namespace,
        ref=urllib.parse.quote(self.unresolved_ref, safe=""),
    )
    if self.auth:
        api_url = url_concat(api_url, self.auth)
    resp = await client.fetch(api_url, user_agent="BinderHub")
    ref_info = json.loads(resp.body.decode("utf-8"))
    self.resolved_ref = ref_info["id"]
    return self.resolved_ref
```

### Build Slug 生成

由于 GitLab 命名空间包含 `/`，而镜像名不允许 `/`，使用 `-` 替换并转义：

```python
def get_build_slug(self):
    return "-".join(p.replace("-", "_-") for p in self.namespace.split("/"))
```

## GitRepoProvider

`GitRepoProvider`（repoproviders.py:606-714）是通用 Git 提供者，支持任意 Git 仓库 URL。

### 协议白名单

```python
allowed_protocols = Set(Unicode(), default_value={"http", "https", "git", "ssh"}, config=True)
```

限制允许的 Git 协议，防止 SSRF 等安全问题。

### SSH URL 处理

```python
ssh_match = GIT_SSH_PATTERN.match(self.repo)
if ssh_match:
    user_host, path = ssh_match.groups()
    self.repo = f"ssh://{user_host}/{path}"
```

将 `git@github.com:user/repo.git` 格式转换为标准的 `ssh://user@host/path` 格式。

### Ref 解析：git ls-remote

通用 Git 提供者不依赖特定平台 API，而是使用 `git ls-remote` 命令解析 ref：

```python
async def get_resolved_ref(self):
    if self.is_valid_sha1(self.unresolved_ref):
        self.resolved_ref = self.unresolved_ref
    else:
        command = ["git", "ls-remote", "--", self.repo, self.unresolved_ref]
        proc = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        retcode = await proc.wait()
        if retcode:
            raise RuntimeError(f"Unable to run git ls-remote: {stderr.decode()}")
        if not stdout:
            return None
        resolved_ref = stdout.decode().split(None, 1)[0]
        self.resolved_ref = resolved_ref
    return self.resolved_ref
```

这要求 BinderHub 运行环境中安装了 git 命令行工具。

## ZenodoProvider

`ZenodoProvider`（repoproviders.py:253-300）支持 Zenodo 科学数据仓库的 DOI。

### 工作流程

1. 用户提供 DOI（如 `10.5281/zenodo.3242074`）；
2. 通过 `https://doi.org/<doi>` 进行 HTTP 重定向解析，获取 Zenodo 记录页面 URL；
3. 从重定向后的 URL 中提取 record_id；
4. DOI 本身代表所有版本，始终解析到最新版本，resolved_spec 替换为具体版本号。

```python
async def get_resolved_ref(self):
    client = AsyncHTTPClient()
    req = HTTPRequest(f"https://doi.org/{self.spec}", user_agent="BinderHub")
    r = await client.fetch(req)
    self.record_id = r.effective_url.rsplit("/", maxsplit=1)[1]
    return self.record_id
```

## FigshareProvider

`FigshareProvider`（repoproviders.py:303-379）支持 Figshare 学术数据仓库。

### 版本处理

Figshare DOI 有两种形式：
- **版本化**：`10.6084/m9.figshare.9782777.v1`（末尾带 `.vN`）；
- **未版本化**：`10.6084/m9.figshare.9782777`（通过 API 获取最新版本）。

```python
if doi_fields[-1].startswith("v"):
    article_version = doi_fields[-1][1:]
    article_id = doi_fields[-2]
else:
    # 通过 Figshare API 获取最新版本
    r = await client.fetch(
        f"https://api.figshare.com/v2/articles/{article_id}/versions"
    )
    article_versions = json.loads(r.body)
    article_version = sorted(v["version"] for v in article_versions)[-1]
```

## DataverseProvider

`DataverseProvider`（repoproviders.py:382-445）支持 Dataverse 开源数据仓库平台。

### 工作流程

1. 通过 doi.org 解析 DOI 获取 Dataverse 实例 URL；
2. 构造 Dataverse API URL（`/api/datasets/:persistentId`）；
3. 提取数据集标识符、版本号（major.minor）；
4. 返回组合的 record_id。

```python
async def get_resolved_ref(self):
    req = HTTPRequest(f"https://doi.org/{self.spec}", user_agent="BinderHub")
    r = await client.fetch(req)
    search_url = urllib.parse.urlunparse(
        urllib.parse.urlparse(r.effective_url)._replace(
            path="/api/datasets/:persistentId"
        )
    )
    r = await client.fetch(search_url, user_agent="BinderHub")
    resp = json.loads(r.body)
    self.identifier = resp["data"]["identifier"]
    self.record_id = "{datasetId}.v{major}.{minor}".format(
        datasetId=resp["data"]["id"],
        major=resp["data"]["latestVersion"]["versionNumber"],
        minor=resp["data"]["latestVersion"]["versionMinorNumber"],
    )
    return self.record_id
```

## HydroshareProvider

`HydroshareProvider`（repoproviders.py:448-514）支持 Hydroshare 水资源研究共享平台。

### Resource ID 解析

使用正则从 URL 或直接 ID 中提取 32 位十六进制资源 ID：

```python
url_regex = re.compile(r".*([0-9a-f]{32}).*")

def _parse_resource_id(self, spec):
    match = self.url_regex.match(spec)
    if not match:
        raise ValueError("The specified Hydroshare resource id was not recognized.")
    return match.groups()[0]
```

版本标识基于资源的最后修改时间戳（精确到秒）：

```python
def parse_date(json_body):
    json_response = json.loads(json_body)
    date = next(item for item in json_response["dates"] if item["type"] == "modified")["start_date"]
    date = date.split(".")[0]
    parsed_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    return str(int(parsed_date.replace(tzinfo=timezone(timedelta(0))).timestamp()))
```

## CKANProvider

`CKANProvider`（repoproviders.py:517-603）支持 CKAN 开放数据平台。

### URL 解析

CKAN 支持 URL 前缀（不同部署路径），并支持两种方式指定活动（版本）ID：
- URL 路径中：`/dataset/<id>/history/<activity_id>`；
- 查询参数中：`?activity_id=<id>`。

```python
parsed_repo = urlparse(self.repo)
url_prefix, dataset_url = parsed_repo.path.split("/dataset/")
dataset_url_parts = dataset_url.split("/")
self.dataset_id = dataset_url_parts[0]

activity_id = None
if "history" in dataset_url_parts:
    activity_id = dataset_url_parts[dataset_url_parts.index("history") + 1]
elif parse_qs(parsed_repo.query).get("activity_id") is not None:
    activity_id = parse_qs(parsed_repo.query).get("activity_id")[0]
```

根据是否有 activity_id 调用不同的 CKAN API 端点（`activity_data_show` 或 `package_show`），版本基于 `metadata_modified` 时间戳。

## RepoProvider 注册与选择

在 app.py 中，所有内置提供者通过 `repo_providers` 字典注册：

```python
repo_providers = Dict({
    "gh": GitHubRepoProvider,
    "gist": GistRepoProvider,
    "git": GitRepoProvider,
    "gl": GitLabRepoProvider,
    "zenodo": ZenodoProvider,
    "figshare": FigshareProvider,
    "hydroshare": HydroshareProvider,
    "dataverse": DataverseProvider,
    "ckan": CKANProvider,
}, config=True)
```

BuildHandler 处理请求时，根据 URL 中的 provider_prefix 查找对应的类并实例化：

```python
if provider_prefix not in self.settings["repo_providers"]:
    await self.fail(f"No provider found for prefix {provider_prefix}")
    return
provider = self.get_provider(provider_prefix, spec=spec)
```

## 内置提供者速查表

| 前缀 | 类名 | Spec 格式 | Ref 解析方式 | 说明 |
|---|---|---|---|---|
| `gh` | GitHubRepoProvider | `user/repo[/ref]` | GitHub Commits API | GitHub.com/GHE，支持 ETag 缓存 |
| `gist` | GistRepoProvider | `user/gist-id[/ref]` | GitHub Gist API | Gist 支持，默认禁止 secret gist |
| `gl` | GitLabRepoProvider | `encoded-namespace/ref` | GitLab v4 API | 支持嵌套命名空间和私有实例 |
| `git` | GitRepoProvider | `encoded-url/ref` | `git ls-remote` 命令 | 任意 Git 仓库，需本地 git |
| `zenodo` | ZenodoProvider | `10.xxxx/zenodo.xxxxx` | DOI 重定向 | Zenodo 科学数据仓库 |
| `figshare` | FigshareProvider | `10.xxxx/m9.figshare.xxxxx[.vN]` | Figshare API + DOI | Figshare 学术数据 |
| `dataverse` | DataverseProvider | `10.xxxx/DVN/xxxxx` | Dataverse API + DOI | Dataverse 开源数据平台 |
| `hydroshare` | HydroshareProvider | `<resource-id-or-url>` | Hydroshare API | 水资源研究数据 |
| `ckan` | CKANProvider | `<dataset-url>` | CKAN API（package_show/activity_data_show） | CKAN 开放数据平台 |

## 扩展自定义 RepoProvider

要添加新的仓库提供者，需要：

1. 继承 `RepoProvider` 基类；
2. 实现所有抽象方法；
3. 定义 `name`、`display_config`；
4. 在配置中注册：

```python
from binderhub.repoproviders import RepoProvider

class MyCustomProvider(RepoProvider):
    name = Unicode("MyPlatform")
    display_config = {
        "displayName": "My Platform",
        "id": "mp",
        "spec": {"validateRegex": r"[^/]+/.+"},
        "repo": {"label": "My Platform repo", "placeholder": "example: user/repo"},
        "ref": {"enabled": True, "default": "HEAD"},
    }

    async def get_resolved_ref(self):
        # 调用自定义 API 解析 ref
        ...

    def get_repo_url(self):
        return f"https://my-platform.com/{self.spec}"

    # 实现其他抽象方法...

# 注册
c.BinderHub.repo_providers["mp"] = MyCustomProvider
```

## 关键源码引用

- RepoProvider 基类：repoproviders.py:55-215
- GitHubRepoProvider：repoproviders.py:853-1112
- GistRepoProvider：repoproviders.py:1115-1207
- GitLabRepoProvider：repoproviders.py:717-850
- GitRepoProvider：repoproviders.py:606-714
- ZenodoProvider：repoproviders.py:253-300
- FigshareProvider：repoproviders.py:303-379
- DataverseProvider：repoproviders.py:382-445
- HydroshareProvider：repoproviders.py:448-514
- CKANProvider：repoproviders.py:517-603
- 辅助函数：repoproviders.py:36-52
