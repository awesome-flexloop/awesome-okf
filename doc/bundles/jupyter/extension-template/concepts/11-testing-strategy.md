---
type: Concept
title: 三层测试策略
description: 理解 Jest 单元测试、pytest 后端测试和 Playwright/Galata 集成测试的三层测试架构，掌握测试编写与运行方法。
tags: [testing, jest, pytest, playwright, galata, unit-test, integration-test, coverage]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: build-yml
    location: template/.github/workflows/build.yml.jinja
    lines: "1-167"
  - id: jest-test
    location: template/src/{% if test %}__tests__{% endif %}/{{python_name}}.spec.ts.jinja
    lines: "1-9"
---

## 三层测试策略

extension-template 采用三层测试架构，从单元到集成逐层验证扩展的正确性。选择 `test: Yes`（默认）时，模板会生成完整的测试基础设施。

## 测试架构总览

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Integration Tests (Playwright + Galata)            │
│ ─ 真实浏览器中运行完整 JupyterLab                            │
│ ─ 测试 UI 交互、扩展在完整环境中的行为                       │
│ ─ 最慢、最真实                                               │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Python Unit Tests (pytest)                         │
│ ─ 测试后端 APIHandler、路由注册、认证逻辑                    │
│ ─ 仅 frontend-and-server 类型生成                           │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: JavaScript Unit Tests (Jest)                       │
│ ─ 测试前端工具函数、纯逻辑模块                               │
│ ─ 最快、最容易写                                             │
└─────────────────────────────────────────────────────────────┘
```

## Layer 1：前端单元测试（Jest）

### 配置

选择 `test: Yes` 时生成：
- `src/__tests__/myextension.spec.ts`：示例测试文件
- `jest.config.js`：Jest 配置
- `babel.config.js`：Babel 转译配置（处理 TypeScript/ESM）
- `tsconfig.test.json`：测试专用 TypeScript 配置

### 运行测试

```bash
jlpm run test              # 运行所有 Jest 测试（单次）
jlpm run test -- --watch   # 监听模式，文件变更时自动重跑
```

### 示例测试

模板生成的占位测试：

```typescript
describe('myextension', () => {
  it('should be tested', () => {
    expect(1 + 1).toEqual(2);
  });
});
```

### 测试模式

Jest 测试适合测试纯逻辑函数、工具方法和数据转换。对于依赖 JupyterLab 服务的代码（如 activate 函数），Jest 测试中需要 mock 依赖。

**测试工具函数**：

```typescript
// src/utils.ts
export function formatData(data: string): string {
  return data.trim().toUpperCase();
}

// src/__tests__/utils.spec.ts
import { formatData } from '../utils';

describe('formatData', () => {
  it('should trim and uppercase', () => {
    expect(formatData('  hello  ')).toBe('HELLO');
  });
});
```

**Mock JupyterLab 依赖**：

```typescript
jest.mock('@jupyterlab/application', () => ({
  JupyterFrontEnd: jest.fn(),
}));
```

### 测试文件约定

- 测试文件放在 `src/__tests__/` 目录
- 文件名以 `.spec.ts` 结尾
- 每个源文件对应一个测试文件（如 `utils.ts` → `__tests__/utils.spec.ts`）

## Layer 2：后端单元测试（pytest）

仅 frontend-and-server 类型生成。

### 配置

- `myextension/tests/test_routes.py`：后端测试
- `conftest.py`：pytest fixtures 配置
- `pyproject.toml` 中的 `[tool.pytest.ini_options]`

### 运行测试

```bash
pytest                     # 运行所有 Python 测试
pytest -vv                 # 详细输出
pytest --cov=myextension   # 带覆盖率报告
```

### 测试 APIHandler

后端测试使用 `pytest-asyncio` 和 `pytest-jupyter`（如果已安装），或者直接使用 Tornado 的 HTTP 测试工具：

```python
import json
import pytest
from tornado.httpclient import HTTPRequest
from jupyter_server.serverapp import ServerApp

@pytest.fixture
def server_app():
    """创建测试用的 ServerApp 实例"""
    app = ServerApp.instance()
    app.initialize(argv=[])
    return app

async def test_hello_endpoint(server_app, http_server_client):
    """测试 /myextension/hello 端点"""
    response = await http_server_client.fetch('/myextension/hello')
    assert response.code == 200
    data = json.loads(response.body)
    assert 'data' in data
```

### 测试认证检查

CI 中的 `check_auth.py` 脚本会自动验证所有 APIHandler 方法都有 `@tornado.web.authenticated` 装饰器：

```bash
python .github/scripts/check_auth.py myextension
```

如果有任何 GET/POST/PUT/DELETE/PATCH/OPTIONS/HEAD 方法缺少认证装饰器，脚本会失败。

## Layer 3：集成测试（Playwright + Galata）

### 配置

- `ui-tests/` 目录：集成测试环境
  - `tests/myextension.spec.ts`：Playwright 测试文件
  - `playwright.config.js`：Playwright 配置
  - `jupyter_server_test_config.py`：Jupyter Server 测试配置
  - `package.json`：测试依赖（@jupyterlab/galata、@playwright/test）
- `.github/workflows/` 中的 `integration-tests` job

### 安装测试浏览器

```bash
cd ui-tests
jlpm install
jlpm playwright install chromium --only-shell
```

### 运行集成测试

```bash
cd ui-tests
jlpm playwright test              # 运行所有集成测试
jlpm playwright test --headed     # 有头模式（可看到浏览器）
jlpm playwright test --debug      # 调试模式
```

### Galata API

Galata 是 JupyterLab 提供的 Playwright 测试工具包，提供了丰富的 JupyterLab 操作 API：

```typescript
import { expect, test } from '@jupyterlab/galata';

test('extension should activate', async ({ page }) => {
  // 等待 JupyterLab 加载完成
  await page.waitForSelector('#jp-main-dock-panel');

  // 检查控制台日志中是否有激活消息
  const logs: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'log') logs.push(msg.text());
  });

  // 等待 JupyterLab 完全加载
  await page.waitForLoadState('networkidle');

  // 验证扩展已激活（检查控制台消息）
  expect(logs).toContain('JupyterLab extension myextension is activated!');
});
```

### 常见集成测试模式

**测试命令面板命令**：

```typescript
test('command should appear in palette', async ({ page }) => {
  await page.menu.clickMenuItem('View>Command Palette');
  await page.getByPlaceholder('SEARCH').fill('My Command');
  await expect(page.getByText('My Command')).toBeVisible();
});
```

**测试文件打开**：

```typescript
test('should open my file type', async ({ page, tmpPath }) => {
  // 上传测试文件
  await page.contents.uploadFile(
    'test-data/sample.my_type',
    `${tmpPath}/sample.my_type`
  );
  // 在文件浏览器中双击打开
  await page.filebrowser.refresh();
  await page.dblclick(`.jp-DirListing-itemText:has-text("sample.my_type")`);
  // 验证 widget 打开
  await expect(page.locator('.mimerenderer-my_type')).toBeVisible();
});
```

## Lint 与格式检查

除了测试之外，模板还配置了完整的代码质量工具链：

| 工具 | 命令 | 检查内容 |
|------|------|---------|
| ESLint | `jlpm run eslint` | TypeScript/JavaScript 代码质量 |
| Prettier | `jlpm run prettier` | 代码格式化 |
| Stylelint | `jlpm run stylelint` | CSS 样式质量 |
| 组合 | `jlpm run lint:check` | 运行以上所有检查 |

自动修复：

```bash
jlpm run eslint:fix   # 自动修复 ESLint 问题
jlpm run prettier:fix # 自动格式化
jlpm run stylelint:fix # 自动修复 CSS 问题
```

## 隔离安装测试（test_isolated）

CI 中还有一个特殊的 `test_isolated` job，它：
1. 从 build job 下载构建好的 wheel 包
2. **删除 Node.js**（模拟用户环境，用户只有 pip，没有 Node）
3. 使用 pip 安装 wheel 包
4. 验证扩展能被 JupyterLab 正确识别
5. 运行 `jupyterlab.browser_check`（无头浏览器检查）

这个测试确保 wheel 包是自包含的，不依赖 Node.js，用户通过 pip 安装后就能使用。这是对双包构建正确性的最终验证。

## 测试运行顺序建议

开发时按以下顺序运行测试：

1. **前端变更后**：`jlpm run test`（Jest 秒级反馈）
2. **后端变更后**：`pytest -vv`（pytest 快速反馈）
3. **提交前**：`jlpm run lint:check && jlpm run test`（本地门禁）
4. **PR 时**：CI 自动运行全部三层测试
5. **发布前**：确保所有测试通过，包括 `test_isolated`

## 相关概念

- [CI/CD 工作流详解](/concepts/12-ci-workflows.md)
- [双包构建系统](/concepts/05-build-system.md)
- [打包与发布](/concepts/13-packaging-release.md)
