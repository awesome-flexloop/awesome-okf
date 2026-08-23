---
type: Concept
title: "Python 与 npm 双生态发布"
description: "Python 包和 npm 包的构建、检查、上传流程，workspace monorepo 支持，双生态构建顺序约束"
tags: [python, npm, build, publish, pypi, workspace]
stage: "核心"
prerequisites: ["05-release-pipeline.md"]
sources:
  - /facts.md
---

# Python 与 npm 双生态发布

jupyter_releaser 原生支持 Python 包（sdist/wheel → PyPI）和 npm 包（tgz → npm registry）的发布，并能处理两种包共存的项目（如 Jupyter Lab Extension）。

## 项目检测

jupyter_releaser 通过检测项目根目录的配置文件判断包类型：

| 文件存在 | 判定为 |
|---------|--------|
| `pyproject.toml` 或 `setup.py` | Python 包 |
| `package.json` | npm 包 |
| 两者都有 | 混合包（按顺序构建） |
| 两者都没有 | 报错 |

## Python 包发布流程

### 构建（build-python）

构建命令序列：
1. 检测构建后端（hatchling、setuptools、flit 等）
2. 执行 `python -m build --sdist --wheel --outdir {dist_dir}`
3. 构建产物：`{name}-{version}.tar.gz`（sdist）和 `{name}-{version}-py3-none-any.whl`（wheel）

构建后端检测逻辑（`util.get_version()` 中的类似策略）：
- 优先检查 `pyproject.toml` 中的 `[build-system]`
- 有 hatch 配置 → 使用 hatch
- 有 setup.py → 使用 setuptools
- 有 flit → 使用 flit

### 检查（check-python）

检查序列：
1. **pip install 验证**：创建临时 venv，`pip install dist/*.whl`，验证包能正常安装和导入
2. **twine check**：`twine check dist/*`，验证包元数据（long description、author 等）
3. **可选 piplite 检查**：验证包在 Pyodide 环境中的兼容性（跳过 wheels）

### 上传到 PyPI（publish-assets）

Python 文件（`.whl` 和 `.tar.gz`）通过 twine 上传，支持三种认证方式：

**方式1：OIDC Trusted Publishing（推荐）**

GitHub Actions 环境中自动使用 `id-token: write` 权限，通过 OIDC 交换 PyPI token，不需要存储长期 PYPI_TOKEN。

```yaml
permissions:
  id-token: write
```

信任配置在 PyPI 网站设置（Publisher：GitHub Actions，owner/repo/workflow）。

**方式2：PYPI_TOKEN**

单个 PyPI token，适用于单包项目：
```yaml
secrets:
  PYPI_TOKEN: pypi-xxxxx
```

**方式3：PYPI_TOKEN_MAP**

多包项目的 token 映射，格式：
```
owner1/repo1:pypi-token1,owner2/repo2:pypi-token2
```

包名通过 `pkginfo.SDist/Wheel` 读取分发包中的 `name` 字段，用 `canonicalize_name()` 规范化后匹配。

### 本地 PyPI 服务器（dry-run）

dry-run 模式下启动本地 PyPI 服务器（pypiserver，端口 8081）：
1. 创建临时目录作为包存储
2. 生成 htpasswd 文件
3. 启动 `pypi-server run` 监听 127.0.0.1:8081
4. twine 上传目标替换为 `http://localhost:8081`

## npm 包发布流程

### 构建（build-npm）

构建命令：
```bash
npm pack --ignore-scripts
```
生成 `.tgz` 文件（格式：`{name}-{version}.tgz`，name 中的 `/` 替换为 `-`）。

`--ignore-scripts` 防止执行 npm scripts（prepack/postpack），这些通常在 before-build-npm hook 中显式执行。

### 检查（check-npm）

两步检查：
1. **npm publish --dry-run**：`npm publish {tgz} --dry-run --access public`，验证包内容
2. **npm install -g**：`npm install -g {tgz}`，全局安装验证包可用

### 发布（publish-assets）

发布命令：
```bash
npm publish {tgz} --access public
```

Tag 规则：
- 正式版本（非 prerelease）→ 使用 `latest` tag（默认）
- 预发布版本（alpha/beta/rc/dev）→ 自动使用 `next` tag

`.npmrc` 配置：
自动生成 `.npmrc` 文件写入 token：
```
//registry.npmjs.org/:_authToken={NPM_TOKEN}
```

错误处理：
- **E409/EPUBLISHCONFLICT**：版本已存在时静默忽略（幂等处理）
- 其他错误正常抛出

### npm Workspace Monorepo 支持

对于 npm workspaces（monorepo）：
1. `_get_workspace_packages()` 通过 `npm query` 获取 workspace 包列表
2. `tag_workspace_packages()` 对每个 workspace 包执行 `npm dist-tag`
3. 格式：`npm dist-tag add {pkg}@{version} {tag} --workspace {path}`
4. 非 monorepo 项目跳过此步骤（`--no-git-tag-workspace` 选项可禁用）

## Python + npm 混合包的特殊处理

### 构建顺序约束

**npm 构建必须在 Python 构建之前**。这是因为 Jupyter 生态的常见模式：
1. `npm run build` 生成前端静态资源（JS/CSS）
2. 这些静态文件被包含在 Python 包中（通过 `MANIFEST.in` 或 `package_data`）
3. Python 构建时打包这些资源

如果颠倒顺序，Python 包会缺少前端构建产物。

### 双包识别逻辑

`tag-release` 和其他命令中，同时处理 Python 和 npm：
1. 检测是否有 package.json → 决定是否处理 npm
2. 检测是否有 pyproject.toml/setup.py → 决定是否处理 Python
3. 两种都有时按 npm→Python 顺序

### python-packages 参数

多 Python 包项目使用 `--python-packages` 指定包列表，格式为 `path:name`：

```toml
[tool.jupyter-releaser.options]
populate-release = { python_packages = [".:main-pkg", "./packages/sub-pkg:sub-pkg"] }
```

- `path`：相对于仓库根目录的包路径
- `name`：PyPI 上的包名（用 canonicalize_name 匹配）
- 默认为 `["."]`（当前目录的单个包）

## 发布产物对照

| 产物 | 格式 | 上传目标 | dry-run 目标 |
|------|------|---------|-------------|
| Python sdist | `{name}-{version}.tar.gz` | PyPI (twine) | localhost:8081 (pypiserver) |
| Python wheel | `{name}-{version}-py3-none-any.whl` | PyPI (twine) | localhost:8081 (pypiserver) |
| npm 包 | `{name}-{version}.tgz` | npm registry | npm publish --dry-run |

## 相关文档

- [发布流水线详解](05-release-pipeline.md)
- [Changelog系统](07-changelog-system.md)
- [认证体系](10-authentication.md)
- [Dry-Run与Mock机制](08-dry-run-and-mock.md)
