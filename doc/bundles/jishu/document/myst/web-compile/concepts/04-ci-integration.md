---
type: Concept
title: CI集成
description: web-compile在CI/CD流水线中的使用：变更检测退出码、GitHub Actions配置、预提交钩子和开发工作流
tags: [web, compile, ci, cd, github-actions, pre-commit, exit-code, automation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:26:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: wc-source
    resource: /references/compile-source.md
    title: web-compile 源码路径映射
---

# CI集成

web-compile 的核心设计理念之一是 CI 友好：通过退出码区分"成功无变更"和"成功有变更"，可以直接集成到各种CI流水线中。

## 退出码语义

| 退出码 | 含义 | CI中的处理 |
|--------|------|-----------|
| 0 | 编译成功，输出文件与现有文件一致 | ✅ 通过 |
| 1 | 编译错误（SCSS语法错误、文件不存在等） | ❌ 失败，需修复 |
| 3（默认） | 编译成功，输出文件有变化 | ⚠️ 需提交变更 |

退出码3可通过 `--exit-code` 自定义。

## GitHub Actions 集成

### 检查资源是否已编译

在PR中检查是否提交了最新的编译后资源：

```yaml
# .github/workflows/check-assets.yml
name: Check Compiled Assets

on:
  pull_request:
    paths:
      - 'src/**/*.scss'
      - 'src/**/*.js'
      - 'web-compile-config.yml'

jobs:
  check-assets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install web-compile
        run: pip install web-compile

      - name: Compile assets
        run: web-compile

      - name: Check for uncommitted changes
        run: |
          if ! git diff --quiet; then
            echo "::error::Compiled assets are out of date. Run 'web-compile' and commit the changes."
            git diff
            exit 1
          fi
```

### 使用退出码检测变更

```yaml
- name: Compile and check
  run: web-compile --exit-code 3
  # 如果退出码3，说明有文件变更，以下步骤处理
  continue-on-error: true

- name: Commit compiled assets
  if: failure()
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add -A
    git commit -m "chore: compile web assets [skip ci]"
    git push
```

## pre-commit 钩子集成

将web-compile作为pre-commit钩子，在提交前自动编译资源：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: web-compile
        name: Compile web assets
        entry: web-compile
        language: system
        files: '\.(scss|sass|js|j2|jinja2)$'
        pass_filenames: false
        additional_dependencies: []
```

安装pre-commit钩子：

```bash
pip install pre-commit
pre-commit install
```

### 使用test-run模式做检查

如果你想在pre-commit中检查但不自动修改文件：

```yaml
  - id: web-compile-check
    name: Check compiled assets
    entry: web-compile --test-run
    language: system
    files: '\.(scss|sass|js)$'
    pass_filenames: false
```

## 开发工作流

### 本地开发

1. 修改源文件（SCSS/JS/Jinja模板）
2. 运行 `web-compile` 编译
3. 确认输出正确
4. 提交源文件**和**编译后文件

```bash
# 开发时使用expanded格式便于调试
web-compile --sass-format expanded --verbose

# 提交前使用compressed格式
web-compile --sass-format compressed
```

### 自动编译（配合文件监听）

web-compile本身不带watch模式，但可以配合其他工具：

```bash
# 使用entr（Linux/Mac）
find src -name "*.scss" -o -name "*.js" | entr web-compile

# 使用watchdog（Python）
pip install watchdog
watchmedo shell-command \
  --patterns="*.scss;*.js;*.html" \
  --recursive \
  --command='web-compile' \
  src/
```

### package.json脚本（如果混合项目）

```json
{
  "scripts": {
    "build:assets": "web-compile",
    "watch:assets": "watchmedo shell-command --patterns='*.scss;*.js' --recursive --command='web-compile' src/"
  }
}
```

## 多环境配置

### 开发vs生产配置

开发配置 `web-compile-config.dev.yml`：

```yaml
sass_files:
  src/main.scss: dist/main.css
jinja_variables:
  debug: true
  minified: false
```

生产配置 `web-compile-config.yml`：

```yaml
sass_files:
  src/main.scss: dist/main.[hash].css
js_files:
  src/app.js: dist/app.[hash].min.js
jinja_variables:
  debug: false
  minified: true
```

```bash
# 开发
web-compile -c web-compile-config.dev.yml --sass-format expanded

# 生产
web-compile --sass-format compressed
```

## tox/nox集成

### tox

```ini
[testenv:compile-assets]
deps = web-compile
commands = web-compile
```

运行：

```bash
tox -e compile-assets
```

### nox

```python
import nox

@nox.session
def compile_assets(session):
    session.install("web-compile")
    session.run("web-compile")
```

运行：

```bash
nox -s compile-assets
```

## Makefile集成

```makefile
.PHONY: assets clean-assets

assets:
	web-compile --sass-format compressed

assets-dev:
	web-compile --sass-format expanded --verbose

assets-check:
	web-compile --test-run

clean-assets:
	rm -rf dist/css/* dist/js/*
```

## 最佳实践

1. **始终提交编译后文件**：将 `dist/` 目录纳入版本控制（不要gitignore），因为用户pip安装后不会运行web-compile
2. **CI检查**：在PR CI中运行web-compile，确保没有忘记提交编译后资源
3. **使用[hash]文件名**：生产环境使用内容哈希文件名，避免浏览器缓存问题
4. **配置文件纳入版本控制**：`web-compile-config.yml` 必须提交
5. **pre-commit钩子**：本地开发时自动编译，减少遗漏
6. **--continue-on-error批量处理**：大项目使用 `--continue-on-error` 一次看到所有错误

## 相关概念

- [三种编译类型](02-compilation-types.md)
- [配置文件详解](03-configuration.md)
- [资产编译流水线示例](../examples/asset-pipeline.md)
