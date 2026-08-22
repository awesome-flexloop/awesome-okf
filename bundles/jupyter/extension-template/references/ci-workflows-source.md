---
type: Reference
title: CI/CD 工作流模板解析
description: extension-template 预置的 GitHub Actions 工作流（build、check-release、enforce-label、prep-release、publish-release）完整解析。
tags: [github-actions, ci-cd, testing, release, jupyter-releaser, playwright]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:15:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ci-workflows
    resource: /references/ci-workflows-source.md
    title: GitHub Actions 工作流模板源码
---

## CI/CD 工作流模板解析

模板预置了五套 GitHub Actions 工作流，覆盖构建测试、发布检查、标签检查、发布准备和发布执行全流程。

## 工作流文件清单

| 文件 | 触发条件 | 用途 |
|------|---------|------|
| `build.yml.jinja` | push(main) / PR(* ) | 构建、Lint、测试、打包 |
| `check-release.yml.jinja` | push(main) / PR(*) | Jupyter Releaser 发布前检查 |
| `enforce-label.yml` | PR | 强制 PR 标签 |
| `prep-release.yml` | 手动 | Step 1: 准备发布 |
| `publish-release.yml` | 手动 | Step 2: 执行发布 |

## build.yml 详解

### 触发条件与并发控制

```yaml
on:
  push:
    branches: main
  pull_request:
    branches: '*'
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

同一 PR/分支的多次推送会取消旧的构建，节省 CI 资源。

### Job 1: build（主构建）

运行环境：`ubuntu-latest`

步骤序列：

1. **Checkout**：`actions/checkout@v4`
2. **Base Setup**：`jupyterlab/maintainer-tools/.github/actions/base-setup@v1`（安装 Node.js、Python 等基础环境）
3. **Install dependencies**：`pip install -U "jupyterlab>=4.0.0,<5"`
4. **Lint**：`jlpm && jlpm run lint:check`
5. **Test**（条件 test）：`jlpm run test`（Jest 单元测试）
6. **Build**：
   - `pip install .[test]`（安装扩展）
   - frontend-and-server 时：`pytest -vv -r ap --cov {{ python_name }}`
   - frontend-and-server 时：`jupyter server extension list` + grep 检查 OK
   - `jupyter labextension list` + grep 检查 OK
   - `python -m jupyterlab.browser_check`（浏览器兼容性检查）
7. **Auth Check**（frontend-and-server）：`python .github/scripts/check_auth.py`
8. **Package**：`pip install build && python -m build`，卸载 jupyterlab
9. **Upload Artifacts**：上传 `dist/{{ python_name }}*` 为 `extension-artifacts`

### Job 2: test_isolated（隔离安装测试）

依赖：`needs: build`

在全新环境中（先删除 NodeJS）安装 wheel 包，验证：
- 扩展可以在无 NodeJS 环境中通过 pip install 安装
- `jupyter labextension list` 显示 OK
- `python -m jupyterlab.browser_check --no-browser-test` 通过

此步骤验证 wheel 包是自包含的预构建扩展，不需要终端用户安装 NodeJS。

### Job 3: integration-tests（集成测试，条件 test）

依赖：`needs: build`

使用 Playwright + Galata 进行端到端测试：
- 下载 build job 的 wheel 包并安装
- 在 ui-tests 目录执行 `jlpm install` 和 `jlpm playwright install chromium`
- 运行 `jlpm playwright test`
- 上传 Playwright 测试报告

### Job 4: check_links（链接检查）

使用 `jupyterlab/maintainer-tools/.github/actions/check-links@v1` 检查文档中的链接有效性。

## check-release.yml 详解

使用 `jupyter-server/jupyter_releaser/.github/actions/check-release@v2` 执行发布前的自动化检查，上传构建产物到 `{{ python_name }}-releaser-dist-${{ github.run_number }}`。

## enforce-label.yml

非模板的静态工作流文件，用于确保 PR 带有正确的标签（如 `bug`、`enhancement`、`maintenance` 等）。

## prep-release.yml 和 publish-release.yml

这两个工作流配合 [Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser) 使用：

1. **prep-release**：手动触发，生成 changelog、构建包、创建 GitHub Release PR
2. **publish-release**：在 prep-release 完成后手动触发，发布到 PyPI 和 npm

## ui-tests 测试配置

### playwright.config.js

```javascript
const baseConfig = require('@jupyterlab/galata/lib/playwright-config');
module.exports = {
  ...baseConfig,
  webServer: {
    command: 'jlpm start',
    url: 'http://localhost:8888/lab',
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI
  }
};
```

基于 `@jupyterlab/galata` 的默认配置，自动启动 JupyterLab 服务器。

### jupyter_server_test_config.py

```python
from jupyterlab.galata import configure_jupyter_server
configure_jupyter_server(c)
```

注意：此配置仅用于测试，不可在生产环境使用——它会开放服务器访问权限并暴露全局 window 变量。

### 集成测试模板

非 mimerenderer 类型测试：
```typescript
test.use({ autoGoto: false });
test('should emit an activation console message', async ({ page }) => {
  const logs = [];
  page.on('console', msg => logs.push(msg.text()));
  await page.goto();
  expect(logs.filter(s => s === 'JupyterLab extension {{ labextension_name }} is activated!')).toHaveLength(1);
});
```

验证扩展激活消息出现在控制台。

mimerenderer 类型测试：
1. 创建文件并打开，验证 MIME 渲染器正确显示（截图对比）
2. 在 notebook 中 display 该 MIME 类型输出，验证渲染器被调用

## 相关概念

- [三层测试策略](/concepts/11-testing-strategy.md)
- [CI/CD 工作流详解](/concepts/12-ci-workflows.md)
- [打包与发布](/concepts/13-packaging-release.md)
