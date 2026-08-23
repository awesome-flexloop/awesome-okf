---
type: Concept
title: "发布流程"
description: "从翻译积累到 PyPI/conda-forge 发布的完整流程——手动触发 prepare_release、创建 GitHub Release、自动构建wheel、conda-forge 跟进"
tags: [jupyterlab, language-pack, release, pypi, conda-forge, build]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: release, resource: /references/release-process-source.md, title: "发布流程信源" }
  - { id: workflows, resource: /references/workflows-source.md, title: "CI/CD 工作流信源" }
  - { id: requirements, resource: /references/requirements-source.md, title: "Python 依赖信源" }
---

# 发布流程

JupyterLab 语言包的发布流程以"翻译积累到一定程度"为触发点，维护者手动触发发布准备工作流，创建 GitHub Release 后自动构建并发布到 PyPI，conda-forge 包则由 conda-forge 的机器人自动跟进。

## 发布前条件

在触发发布前，需要确认：

1. **Crowdin PR 已合并**：近期的翻译更新已通过 Crowdin PR 合入 main 分支
2. **CI 检查通过**：main 分支的所有检查（check_version等）为绿色
3. **上游版本稳定**：当前跟踪的 JupyterLab 版本是稳定版（非RC/beta）
4. **维护者权限**：需要有仓库写权限以触发 workflow 和创建 Release

## 发布步骤

### 步骤 1：触发 Prepare Release 工作流

在 GitHub 仓库页面：
1. 进入 **Actions** 标签
2. 选择 **Prepare Release** 工作流
3. 点击 **Run workflow**
4. 可选择指定 `version-tag`（默认使用最新 JupyterLab tag）

此工作流（`prepare_release.yml`）执行：
- **版本提升**：更新所有 31 个语言包 `__init__.py` 中的 `__version__`
- **贡献者更新**：调用 Crowdin API 获取翻译贡献者列表，重写每个包的 CONTRIBUTORS.md
- **Copier 同步**：对每个语言包执行 `copier --defaults update`，同步 cookiecutter 模板变更
- **版本检查**：运行 `04_check_version.py` 确认所有版本一致
- **创建 PR**：所有变更打包为一个发布准备 PR

### 步骤 2：审查并合并 Prepare Release PR

- 检查所有 `__init__.py` 中的版本号是否正确
- 检查 CONTRIBUTORS.md 中的贡献者列表是否合理
- 确认 CI 检查通过
- **Squash 合并**到 main 分支

### 步骤 3：创建 GitHub Release

在 GitHub 仓库页面：
1. 进入 **Releases** → **Draft a new release**
2. **Choose a tag**：输入新版本号标签（如 `v4.5.post3`），格式为 `vX.Y.postZ`
3. **Target**：选择 main 分支
4. **Release title**：`Release {version-tag}`（如 `Release v4.5.post3`）
5. **描述**：简要说明更新内容（如"Updated translations for 30+ languages"）
6. 点击 **Publish release**

⚠️ **不要勾选 "Set as a pre-release"**，这会导致 release_publish 工作流不触发。

### 步骤 4：自动构建发布（PyPI）

Release 发布后，`release_publish.yml` 工作流自动触发：
1. 对 `language-packs/` 下每个语言包执行构建
2. 使用 hatchling + jupyterlab-translate build hook 编译 PO → MO/JSON
3. 生成 wheel（.whl）和 sdist（.tar.gz）
4. 通过 `gh-action-pypi-publish` 使用 PyPI trusted publisher 认证上传到 PyPI
5. 30 个语言包依次发布，约 10-20 分钟完成

### 步骤 5：验证 PyPI 发布

发布完成后验证：
1. 访问 `https://pypi.org/project/jupyterlab-language-pack-zh-CN/` 查看新版本
2. 或使用 pip 测试安装：`pip install --upgrade jupyterlab-language-pack-zh-CN`
3. 启动 JupyterLab 确认翻译加载正常

### 步骤 6：conda-forge 跟进

conda-forge 包由 conda-forge 的 regro-cf-autotick-bot 自动检测 PyPI 新版本并创建更新 PR：
1. Bot 检测到 PyPI 新版本
2. 自动更新 conda-forge feedstock 的 recipe（版本号和 hash）
3. 维护者审查合并
4. conda-forge CI 构建完成后包即可通过 conda 安装

这个过程通常在 PyPI 发布后几小时到1天内完成。

## 版本号规则

语言包版本格式：`X.Y.postZ`

| 组成部分 | 含义 | 示例 |
|---------|------|------|
| `X` | JupyterLab 主版本 | 4 |
| `Y` | JupyterLab 次版本 | 5 |
| `.postZ` | 翻译修订号 | post3 |

版本号含义：
- `4.5.post0`：首次针对 JupyterLab 4.5.x 的翻译发布
- `4.5.post1`：JupyterLab 4.5.x 的第一次翻译更新
- `4.5.post2`：第二次翻译更新
- `4.6.post0`：JupyterLab 升级到 4.6.x 后的首次翻译发布

### 何时提升 post 编号？
- Crowdin 翻译有显著更新时
- 修复翻译错误时
- Copier 模板更新需要重新打包时

### 何时提升主版本号（X.Y）？
- JupyterLab 发布新的次要版本（如 4.5 → 4.6）时
- `01_check_releases.py` 检测到新的 JupyterLab tag 并更新 repository-map.yml 后

## 构建过程详解

### 构建依赖

构建语言包需要：
- **hatchling**（>=1.4.0）：PEP 517 构建后端
- **jupyterlab-translate**（>=1.2.0）：构建钩子，编译 .po → .mo/.json
- **Python**：3.8+

### 构建过程

```
pip install build
python -m build
```

或使用 hatch：
```
pip install hatch
hatch build
```

构建过程中 jupyterlab-translate build hook 执行：
1. 扫描 LC_MESSAGES 目录下所有 .po 文件
2. 使用 `msgfmt`（gettext工具）或 Python 实现编译 .po → .mo
3. 同时生成 JSON 格式翻译文件（供前端 JS 使用）
4. .mo 和 .json 放入 wheel 包，.po 被排除

### Wheel 内容

最终 wheel 文件包含：
- `*.dist-info/`：包元数据、entry_points.txt
- Python 包目录（含 `__init__.py`）
- `locale/{locale}/LC_MESSAGES/*.mo`
- `locale/{locale}/LC_MESSAGES/*.json`
- CONTRIBUTORS.md

不包含 .po 源文件。

## 从源码安装（开发者）

如果需要从源码安装语言包：

```bash
# 克隆仓库
git clone https://github.com/jupyterlab/language-packs.git
cd language-packs

# 安装某个语言包（以中文为例）
cd language-packs/jupyterlab-language-pack-zh-CN
pip install -e .
```

源码安装需要先安装构建依赖：`pip install hatchling jupyterlab-translate`。

## 发布故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| release_publish 未触发 | Release 是 pre-release | 取消 pre-release 标记，重新发布 |
| 某些语言包上传失败 | PyPI 网络问题 | 检查 PyPI 状态，可手动下载 artifact 上传 |
| 版本检查失败 | 某些语言包 __version__ 未更新 | 重新运行 prepare_release |
| 翻译不显示 | .mo/.json 未正确编译 | 检查 jupyterlab-translate 版本是否 >=1.2.0 |
| conda-forge 未更新 | Bot 尚未检测到 | 等待或手动触发 feedstock 更新 |

## 相关概念

- [CI/CD 流水线](08-cicd-pipeline.md)
- [版本管理策略](11-version-management.md)
- [语言包结构剖析](05-package-anatomy.md)
- [安装语言包](../examples/01-install-language-pack.md)
