---
type: Concept
title: "认证体系"
description: "GitHub Token、PyPI OIDC Trusted Publishing、npm Token 三种认证方式的配置和使用"
tags: [authentication, token, oidc, trusted-publishing, pypi, npm]
stage: "进阶"
prerequisites: ["09-github-actions.md"]
sources:
  - /facts.md
  - /references/util-source.md#github-api-操作
---

# 认证体系

jupyter_releaser 需要三种外部服务认证：GitHub API、PyPI、npm。每种都有多种认证方式。

## GitHub 认证

### ADMIN_GITHUB_TOKEN

所有阶段都需要 GitHub API 访问权限。通过 `--auth` CLI 参数或 `GITHUB_ACCESS_TOKEN` 环境变量传入。

**为什么需要 PAT 而不是默认 GITHUB_TOKEN？**

默认的 `secrets.GITHUB_TOKEN` 在某些场景下权限不足：
1. 不能触发其他 workflow（如 release published 事件触发的 workflow）
2. 在仓库内模式下，push tag 后可能无法触发 release 工作流
3. 需要 `workflow` 权限范围才能操作其他 Actions

**PAT 权限要求**：
- `repo`：完全仓库访问（创建 release、上传 assets、push commits/tags）
- `workflow`：操作 GitHub Actions 工作流

**安全建议**：
- 使用 Fine-grained PAT，只授予目标仓库的权限
- Fork 模式下，PAT 存储在 fork 仓库，目标仓库不需要
- Token 过期时间设置合理（建议 90 天轮换）

### 认证流程

`util.get_gh_object()` 创建 GhApi 实例：
- 使用 `GITHUB_ACCESS_TOKEN` 环境变量或 `--auth` 参数
- dry-run 模式下连接 Mock 服务器，使用任意字符串作为 token

## PyPI 认证

### 方式一：OIDC Trusted Publishing（推荐）

最安全的方式，不需要存储长期 PyPI token。利用 GitHub Actions 的 OIDC 功能，在运行时动态交换短期 PyPI token。

**GitHub Actions 配置**：
```yaml
permissions:
  id-token: write  # 必需：允许请求 OIDC token
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi  # 需要与 PyPI 配置的环境名一致
    steps:
      - uses: jupyter-server/jupyter_releaser/.github/actions/finalize-release@v2
        env:
          ADMIN_GITHUB_TOKEN: ${{ secrets.ADMIN_GITHUB_TOKEN }}
```

**PyPI 侧配置**：
1. 登录 PyPI → 项目 Settings → Publishing
2. 添加新的 Publisher：
   - Owner：GitHub 用户名/组织
   - Repository：仓库名
   - Workflow name：工作流文件名（如 `full-release.yml`）
   - Environment：`pypi`（可选但推荐）
3. 保存后，GitHub Actions 运行时即可通过 OIDC 获取发布权限

**优势**：
- 无需在 GitHub 存储长期 PyPI token
- Token 自动轮换（短期有效）
- 绑定特定仓库、workflow、environment，无法被其他项目滥用
- 支持 GitHub Environment 审批流程

### 方式二：PYPI_TOKEN（单包）

适用于单包项目或不支持 OIDC 的场景：

```yaml
env:
  PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

Token 格式：`pypi-<随机字符串>`，从 PyPI 账号设置创建。

### 方式三：PYPI_TOKEN_MAP（多包）

用于 monorepo 包含多个 PyPI 包的场景：

```yaml
env:
  PYPI_TOKEN_MAP: "owner/repo1:pypi-token1,owner/repo2:pypi-token2"
```

格式：`owner/repo:token,owner/repo:token,...`，包名通过 `pkginfo` 读取分发包元数据后用 `canonicalize_name()` 匹配。

### twine 上传逻辑

`python.upload_dist()` 中的认证处理优先级：
1. 检查 `ACTIONS_ID_TOKEN_REQUEST_TOKEN`（GitHub Actions OIDC 环境）→ 使用 Trusted Publishing
2. 检查 `PYPI_TOKEN_MAP` → 按包名查找对应 token
3. 检查 `PYPI_TOKEN` → 使用统一 token
4. dry-run 模式 → 连接本地 PyPI 服务器

## npm 认证

### NPM_TOKEN

npm 发布需要 Automation Token（不受 2FA 限制）：

```yaml
env:
  NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**npm Token 类型**：
- **Read-only**：只能下载包，不能发布
- **Publish**：可以发布，但受 2FA 限制
- **Automation**：可以发布，跳过 2FA（CI/CD 必需）

**配置流程**：
1. 登录 npm → Access Tokens → Generate New Token
2. 选择 "Automation" 类型
3. 复制 token 到 GitHub Secrets

### .npmrc 配置

`npm.run_npm()` 在 publish 前自动生成 `.npmrc`：
```
//registry.npmjs.org/:_authToken=${NPM_TOKEN}
```

### npm Tag 规则

- 正式版本 → `latest` tag（默认）
- 预发布版本（alpha/beta/rc/dev）→ `next` tag

通过 `is_prerelease()` 正则判断版本字符串。

### 错误处理

npm publish 的错误处理：
- **E409**（409 Conflict）：版本已存在 → 静默忽略（幂等）
- **EPUBLISHCONFLICT**：版本冲突 → 静默忽略
- 其他错误 → 抛出异常中断流程

## 认证配置对照表

| 服务 | 推荐方式 | Secrets/配置 | 权限范围 |
|------|---------|-------------|---------|
| GitHub | Fine-grained PAT | `ADMIN_GITHUB_TOKEN` | repo + workflow |
| PyPI | OIDC Trusted Publishing | `id-token: write` + PyPI Publisher配置 | 绑定仓库/workflow |
| npm | Automation Token | `NPM_TOKEN` | 发布权限 |

## 相关文档

- [GitHub Actions集成](09-github-actions.md)
- [Python与npm双生态发布](06-python-npm-dual.md)
- [Dry-Run与Mock机制](08-dry-run-and-mock.md)
