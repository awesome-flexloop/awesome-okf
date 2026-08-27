---
type: Concept
title: 包发布生命周期
description: 使用 packaging.release 模块管理 Python 包的版本检查、changelog 维护、构建、上传到 PyPI 的完整发布流程
tags: [invocations, packaging, release, pypi, publish, semantic-versioning, twine]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-24" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 包发布生命周期

`invocations.packaging.release` 是 Invocations 中最复杂的模块（约925行），提供 Python 包从版本检查到 PyPI 发布的完整生命周期管理。它采用**状态收敛→执行→验证**的三阶段设计，是学习 Invoke 高级模式的绝佳范例。

## 前提条件

release 模块假设你的项目：
- 使用[语义化版本](https://semver.org/)（semantic versioning）
- 使用 `pyproject.toml` 管理包元数据（符合 PEP 621）
- 使用 [releases](https://releases.readthedocs.io/) 格式的 changelog（RST 格式）
- 使用 Git 进行版本控制
- 使用 [twine](https://twine.readthedocs.io/) 上传到 PyPI

## 快速使用

```python
# tasks.py
from invoke import Collection
from invocations.packaging import release

ns = Collection(release)
ns.configure({
    "packaging": {
        "wheel": True,
        "changelog_file": "docs/changelog.rst",
        "package": "myproject",  # 你的包名（不设置则自动检测）
    },
})
```

## 发布流程总览

release 模块将发布分为三个阶段，对应三个核心任务：

```
status → prepare → publish → push
  ↓         ↓          ↓         ↓
 检查      准备        构建上传    Git推送
状态      changelog   PyPI       分支+tag
         /版本/tag
```

一键执行全部：`inv release`（默认任务 `all`）。

## status：检查发布状态

```bash
inv release.status
```

`status` 是最安全的起点——它只读取状态，不做任何修改。它会检查三个维度：

| 组件 | 检查内容 | OK 状态 | 需要操作 |
|------|---------|---------|---------|
| Changelog | 当前分支是否有未发布的 issue | ✔ no unreleased issues | ✘ needs :release: entry |
| Version | pyproject.toml 中的版本是否匹配预期 | ✔ version up to date | ✘ needs version bump |
| Tag | Git 中是否存在预期版本的 tag | ✔ all set | ✘ needs cutting |

输出使用 tabulate 格式化表格，ANSI 颜色标记通过/失败。

### 分支类型检测

`status` 通过 Git 分支名自动判断发布类型：

| 分支模式 | 发布类型 | 版本递增规则 |
|---------|---------|------------|
| `main` / `master` | FEATURE 发布 | 下一个 minor 版本（如 1.2.2 → 1.3.0） |
| `X.Y`（如 `1.2`） | BUGFIX 发布 | 下一个 patch 版本（如 1.2.2 → 1.2.3） |
| 其他（feature 分支等） | UNDEFINED | 无法自动确定，报错退出 |

## prepare：准备发布

```bash
# 干跑（只显示要做什么，不执行）
inv release.prepare --dry-run

# 实际执行
inv release.prepare
```

`prepare` 执行以下步骤：
1. 调用 `status()` 获取当前状态
2. 如果一切就绪（all_okay），直接返回
3. 否则通过 `confirm()` 请求用户确认
4. 按需执行：
   - **Changelog**：打开 `$EDITOR` 编辑 changelog 文件添加 release 条目
   - **Version**：打开 `$EDITOR` 编辑 `pyproject.toml` 更新版本号
   - **Tag**：如果有未提交的更改则 `git commit -am "Cut <version>"`，然后 `git tag -a <version> -m ""`（annotated tag）
5. 再次调用 `status()` 验证所有操作是否成功

> **半自动设计**：prepare 不会自动修改 changelog 和版本号，而是打开编辑器让人工编辑——这是有意为之的安全设计，确保发布内容经过人工审核。

## build：构建分发包

```bash
# 构建 sdist 和 wheel
inv release.build

# 只构建 wheel
inv release.build --no-sdist

# 构建到指定目录
inv release.build --directory=dist

# 构建前清理
inv release.build --clean

# 使用特定 Python
inv release.build --python=python3.12

# 传递额外选项
inv release.build --opts="--no-isolation"
```

`build` 使用 [pypa/build](https://build.pypa.io/)（`python -m build`）构建 sdist 和/或 wheel。

### build 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sdist` | bool | True | 是否构建源码分发包（.tar.gz） |
| `wheel` | bool | True | 是否构建 wheel（.whl） |
| `directory` | str | `dist/` | 输出目录 |
| `python` | str | `"python"` | 用于构建的 Python 解释器 |
| `clean` | bool | False | 构建前清理 dist 和 build 目录 |
| `opts` | str | None | 传递给 `python -m build` 的额外选项 |

## publish：发布到 PyPI

```bash
# 干跑（构建但不上传）
inv release.publish --dry-run

# 实际发布
inv release.publish

# 发布到自定义 index
inv release.publish --index=private-pypi

# GPG 签名
inv release.publish --sign
```

`publish` 是最核心的发布任务，执行完整的防御链：

1. **构建**：在临时目录中调用 `build()` 构建 sdist/wheel（避免上传旧文件）
2. **环境重建**（可选）：如果配置了 `packaging.rebuild_with_env`，在指定环境变量下重新构建（用于 Fabric 等需要特殊构建环境的项目）
3. **twine check**：使用 `twine.commands.check.check()` 直接在 Python 中调用 twine 检查（验证 README 渲染等元数据问题）
4. **安装测试**：创建临时 venv，安装构建产物，验证 `import <package>` 成功；如果包有 `py.typed` 标记，额外运行 mypy 类型检查
5. **上传**：调用 `upload()` 上传到 PyPI（或指定 index），可选 GPG 签名

### test_install：安装验证

`test_install` 也可单独调用：

```bash
# 测试安装 dist/ 中的包
inv release.test-install --directory=dist

# 详细输出
inv release.test-install --directory=dist --verbose

# 跳过 import 测试
inv release.test-install --directory=dist --skip-import
```

`test_install` 的工作流程：
1. 使用 `venv` 模块创建临时虚拟环境
2. 升级 venv 内的 pip 到与外部相同版本（避免旧 pip 问题）
3. `pip install <archive>` 安装构建产物
4. `python -c 'import <package>'` 验证导入成功
5. 如果包有 `py.typed`，安装 mypy 并验证类型存根

### upload：上传到 PyPI

```bash
inv release.upload --directory=dist --sign
```

`upload` 支持：
- GPG 签名（`--sign`）：使用 `gpg --detach-sign --armor` 为每个包创建 `.asc` 签名文件
- 自定义 PyPI index（`--index`）：通过 twine 的 `--repository` 参数指定
- dry-run 模式：只打印将要执行的命令，不实际上传
- wheel 优先上传（确保 PyPI 先看到更完整的 wheel 元数据）

## push：推送到 Git 远端

```bash
inv release.push

# 干跑
inv release.push --dry-run
```

`push` 执行 `git push --follow-tags --no-verify`，推送当前分支和所有 tag 到默认远端。在 CI 环境中自动使用 git 的 `--dry-run` 而非实际推送。

## all：一键发布

`all` 是 release 模块的默认任务，依次执行：

```
prepare → publish → push
```

```bash
# 一键干跑（强烈建议先做！）
inv release --dry-run

# 实际发布
inv release
```

## 关键设计模式

### 状态收敛模式（_converge）

`_converge(c)` 是 release 的核心函数：
1. 收集状态：Git 分支、changelog 内容、pyproject.toml 版本、Git tags
2. 判断发布类型（BUGFIX/FEATURE）
3. 计算 latest/next/expected version
4. 检查三个维度（changelog/version/tag）是否需要更新
5. 返回 `(actions, state)` 二元组

actions 是一个 Lexicon（属性字典），每个组件映射到 OKAY/NEEDS_* 枚举值；state 包含所有计算出的原始数据。

### 防御性检查链

publish 中的防御链体现了"不信任但验证"原则：
- twine check（元数据验证）→ test_install（安装验证）→ upload（实际上传）
- 每一步失败都立即终止，不会带着已知问题上传

### 猴子补丁增强 twine check

```python
readme_renderer.rst.SETTINGS["halt_level"] = Reporter.INFO_LEVEL
readme_renderer.rst.SETTINGS["report_level"] = Reporter.INFO_LEVEL
```

release 模块猴子补丁了 readme_renderer 的警告级别，让 twine check 比默认更严格（默认会忽略 WARNING 级别的 RST 渲染问题）。这只在直接 Python 调用 twine（而非 subprocess）时生效。

## 配置项

```python
ns.configure({
    "packaging": {
        "wheel": True,                    # 默认构建 wheel
        "sdist": True,                    # 默认构建 sdist
        "changelog_file": "changelog.rst", # changelog 文件路径
        "package": "myproject",           # 包名（不设置则自动检测）
        "index": "private-pypi",          # 默认上传的 PyPI index
        "sign": False,                    # 是否默认 GPG 签名
        "clean": False,                   # 是否默认清理构建目录
        "directory": "dist",              # 构建输出目录
        "python": "python",               # 构建用的 Python
    },
})
```

## 相关概念

- [Sphinx 文档管理](04-docs-sphinx.md)
- [依赖 Vendorize 管理](08-vendorize.md)
- [终端交互工具](07-utilities-watchers.md)
- [自定义发布流程示例](../examples/custom-release-flow.md)
- [打包安装验证示例](../examples/test-install-verification.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](../references/invocations-source.md)。
