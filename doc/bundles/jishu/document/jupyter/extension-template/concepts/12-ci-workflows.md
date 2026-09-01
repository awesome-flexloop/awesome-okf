---
type: Concept
title: CI/CD 工作流详解
description: 理解 extension-template 提供的 GitHub Actions 工作流体系：Build、Check Release、Prep Release、Publish Release、链接检查、Binder 预览和集成测试更新。
tags: [ci-cd, github-actions, jupyter-releaser, build-workflow, automation, release-pipeline]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: build-yml
    location: template/.github/workflows/build.yml.jinja
    lines: "1-167"
  - id: check-release
    location: template/.github/workflows/check-release.yml.jinja
    lines: "1-30"
  - id: prep-release
    location: template/.github/workflows/prep-release.yml
    lines: "1-48"
  - id: publish-release
    location: template/.github/workflows/publish-release.yml
    lines: "1-58"
---

## CI/CD 工作流详解

extension-template 预配置了完整的 GitHub Actions CI/CD 流水线，涵盖代码检查、测试、构建、打包和自动化发布。所有工作流文件位于 `.github/workflows/` 目录。

## 工作流总览

| 工作流文件 | 触发条件 | 核心功能 |
|-----------|---------|---------|
| `build.yml` | push to main / PR to any branch | Lint、测试、构建、打包、隔离安装测试、集成测试 |
| `check-release.yml` | push to main / PR to any branch | 使用 Jupyter Releaser 验证发布就绪状态 |
| `enforce-label.yml` | PR opened/edited/labeled | 强制 PR 标签规范 |
| `prep-release.yml` | 手动触发（workflow_dispatch） | 准备发布：更新 CHANGELOG、创建 draft release |
| `publish-release.yml` | 手动触发（workflow_dispatch） | 执行发布：推送到 PyPI、NPM、GitHub Releases |
| `binder-on-pr.yml`（条件） | PR 事件 | 在 Binder 上构建 PR 预览（has_binder 时生成） |
| `update-integration-tests.yml`（条件） | PR 更新 | 更新集成测试快照（test 时生成） |

## Build 工作流（build.yml）

这是最核心的 CI 工作流，每次 push 或 PR 时运行。包含多个 job。

### 并发控制

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

同一分支/PR 的重复运行会取消旧的构建，节省 CI 资源。

### Job 1: build（主构建）

在 `ubuntu-latest` 上运行，按顺序执行以下步骤：

```
1. Checkout → 检出代码
2. Base Setup → jupyterlab/maintainer-tools 提供的基础环境（Python + Node）
3. Install dependencies → pip install jupyterlab>=4.0.0
4. Lint → jlpm install → jlpm run lint:check
5. Test（条件）→ jlpm run test（Jest 单元测试）
6. Build → pip install .[test]
   → pytest（frontend-and-server 类型）
   → jupyter server extension list 验证后端扩展
   → jupyter labextension list 验证前端扩展
   → python -m jupyterlab.browser_check 无头浏览器检查
7. Auth Check（条件）→ check_auth.py 验证端点认证（frontend-and-server 类型）
8. Package → pip install build → python -m build → 生成 wheel/sdist
   → pip uninstall（清理，为隔离测试准备）
9. Upload Artifacts → 上传 dist/ 下的 wheel/sdist 包
```

**browser_check**：JupyterLab 内置的无头浏览器测试工具，会启动 JupyterLab 并验证基本功能正常工作（扩展不报错、界面可加载）。这是对扩展最基本的端到端验证。

### Job 2: test_isolated（隔离安装测试）

依赖 build job 完成后运行：

```
1. Setup Python（3.10）
2. Download artifacts → 下载 build job 生成的 wheel
3. Install and Test →
   ⚠️ 删除 Node.js（模拟终端用户环境！）
   → pip install jupyterlab + wheel
   → 验证扩展注册成功
   → python -m jupyterlab.browser_check --no-browser-test
```

**关键设计**：这个 job 故意删除 Node.js，模拟普通用户通过 pip 安装的环境。如果 wheel 包构建不正确（如遗漏前端静态文件），这个测试会失败。

### Job 3: integration-tests（集成测试，条件）

仅在 `test: Yes` 时生成：

```
1. Checkout + Base Setup
2. Download wheel artifact
3. Install extension from wheel
4. cd ui-tests → jlpm install（安装 Playwright/Galata）
5. Cache/Install Chromium 浏览器
6. jlpm playwright test → 运行集成测试
7. 上传测试报告（playwright-report 和 test-results）
```

集成测试在真实浏览器中运行 JupyterLab，验证扩展的 UI 交互行为。

### Job 4: check_links（链接检查）

```
1. Checkout
2. Base Setup
3. jupyterlab/maintainer-tools check-links action → 检查文档中的死链
```

## 发布工作流

extension-template 集成了 [Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser)，提供标准化的两步发布流程。

### 发布前检查（check-release.yml）

每次 push/PR 自动运行，使用 `jupyter_releaser/.github/actions/check-release@v2`：
- 验证 CHANGELOG 格式
- 验证版本号一致性
- 检查构建配置正确性
- 验证打包产物
- 上传检查通过的 dist 产物作为 artifact

这个检查确保 main 分支始终处于可发布状态。

### Step 1: Prep Release（prep-release.yml）

**手动触发**（workflow_dispatch），运行 `jupyter_releaser/.github/actions/prep-release@v2`：

输入参数：
- `version_spec`：版本说明符（默认 "next"，自动选择下一个版本号）
- `branch`：目标分支
- `post_version_spec`：发布后的版本号
- `since`：从哪个日期/引用开始收集 PR
- `since_last_stable`：从上个稳定版本标签开始

执行操作：
1. 自动更新版本号（同步 package.json 和 pyproject.toml）
2. 根据 PR 标签生成 CHANGELOG 条目
3. 创建一个 draft GitHub Release
4. 构建并附加 dist 产物到 release

完成后输出 `release_url`，维护者可以在 GitHub 上审核 draft release 的 CHANGELOG 和产物。

### Step 2: Publish Release（publish-release.yml）

**手动触发**（workflow_dispatch），在 release 环境中运行（需要审批）：

输入参数：
- `branch`：目标分支
- `release_url`：draft release 的 URL
- `steps_to_skip`：要跳过的步骤（逗号分隔）

执行操作：
1. **Populate Release**：完善 release 信息
2. **Finalize Release**：
   - 发布到 PyPI（使用 trusted publishing 或 NPM_TOKEN）
   - 发布到 NPM（使用 trusted publishing 或 NPM_TOKEN）
   - 创建 GitHub Release
   - 创建 Git tag
   - 更新版本号到下一个 dev 版本

权限配置：
- `environment: release`：使用 GitHub 的环境保护规则，可以要求人工审批
- `id-token: write`：用于 PyPI trusted publishing
- `APP_ID` + `APP_PRIVATE_KEY`：GitHub App 凭证，用于创建 PR 和推送

### Secrets 和 Variables 配置

要使用 Jupyter Releaser 自动化发布，需要在 GitHub 仓库配置：

| 类型 | 名称 | 说明 |
|------|------|------|
| Variable | `APP_ID` | GitHub App 的 ID |
| Secret | `APP_PRIVATE_KEY` | GitHub App 的私钥 |
| Secret | `NPM_TOKEN` | NPM 发布 token（不使用 trusted publishing 时需要） |
| Environment | `release` | 创建名为 "release" 的环境，配置审批规则 |

推荐使用 [NPM Trusted Publishing](https://docs.npmjs.com/trusted-publishers) 替代 NPM_TOKEN。

## 其他工作流

### enforce-label.yml

对 PR 强制标签检查。Jupyter Releaser 根据 PR 标签生成 CHANGELOG，因此每个 PR 必须有正确的标签（如 `enhancement`、`bug`、`maintenance` 等）。

### binder-on-pr.yml（条件）

启用 `has_binder` 时生成。当 PR 被创建或更新时，在 Binder（mybinder.org）上构建预览环境，允许评审者通过浏览器直接测试 PR 的效果。

### update-integration-tests.yml（条件）

启用 `test` 时生成。当集成测试的视觉快照需要更新时，维护者可以触发此工作流自动更新快照。

## 相关概念

- [三层测试策略](11-testing-strategy.md)
- [打包与发布](13-packaging-release.md)
- [CI/CD 工作流源码解析](../references/ci-workflows-source.md)
