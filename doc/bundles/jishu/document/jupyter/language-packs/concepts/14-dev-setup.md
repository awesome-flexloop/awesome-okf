---
type: Concept
title: "本地开发环境搭建"
description: "克隆 language-packs 仓库、安装依赖、运行脚本、本地构建语言包的完整开发环境配置指南"
tags: [jupyterlab, language-pack, development, setup, environment, local]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-readme, resource: /references/repo-readme.md, title: "仓库根 README 信源" }
  - { id: requirements, resource: /references/requirements-source.md, title: "Python 依赖信源" }
  - { id: scripts, resource: /references/scripts-source.md, title: "自动化脚本信源" }
---

# 本地开发环境搭建

本文档说明如何在本地搭建 language-packs 开发环境，用于测试脚本、本地构建语言包、或贡献代码修改。

## 前置要求

| 工具 | 最低版本 | 用途 |
|------|---------|------|
| Python | 3.8+ | 运行自动化脚本、构建语言包 |
| Git | 2.x | 克隆仓库、提交代码 |
| Node.js | 18+ | jupyterlab-translate 部分功能依赖 |
| pip | 最新版 | 安装 Python 包 |
| gettext（可选）| 0.21+ | 手动编译 .po 文件（通常 jupyterlab-translate 自带）|

## 步骤 1：克隆仓库

```bash
git clone https://github.com/jupyterlab/language-packs.git
cd language-packs
```

如果需要提交 PR，先 Fork 再克隆自己的 Fork：
```bash
git clone https://github.com/{your-username}/language-packs.git
cd language-packs
git remote add upstream https://github.com/jupyterlab/language-packs.git
```

## 步骤 2：安装 Python 依赖

```bash
# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装核心依赖
pip install -r requirements.txt

# 安装 jupyterlab-translate（用于 POT 提取和 PO 编译）
pip install "jupyterlab-translate[cli]>=1.2.0"

# 安装 copier（用于模板更新）
pip install copier

# 安装 hatchling（用于构建 wheel）
pip install hatchling
```

### requirements.txt 内容

```
# GitHub API
PyGithub
requests

# 版本解析
packaging
semantic-version

# 模板管理
copier

# 构建工具
hatchling
jupyterlab-translate>=1.2.0
```

## 步骤 3：验证环境

```bash
# 验证 Python 依赖
python -c "import jupyterlab_translate; print('jupyterlab-translate OK')"
python -c "import github; print('PyGithub OK')"
python -c "import packaging.version; print('packaging OK')"
python -c "import semantic_version; print('semantic_version OK')"

# 验证脚本可运行
python scripts/04_check_version.py
# 如果有语言包目录且版本一致，应无报错退出
```

## 常见开发任务

### 任务 A：本地更新 POT 文件

运行 `02_update_catalogs.py` 从上游仓库提取最新字符串：

```bash
# 设置 GitHub token（避免API速率限制）
export GH_TOKEN=your_github_token  # Linux/Mac
set GH_TOKEN=your_github_token     # Windows

# 运行脚本
python scripts/02_update_catalogs.py
```

注意：
- 脚本会克隆上游仓库到 `repos/` 目录（需要网络）
- 首次运行需要较长时间（克隆17个仓库）
- `repos/` 在 .gitignore 中，不会被提交
- 如果不需要更新所有包，可以临时修改脚本只处理特定包

### 任务 B：本地构建单个语言包

```bash
cd language-packs/jupyterlab-language-pack-zh-CN

# 安装构建依赖
pip install build hatchling "jupyterlab-translate>=1.2.0"

# 构建 wheel
python -m build

# 产物在 dist/ 目录
ls dist/
# jupyterlab_language_pack_zh_CN-4.5.post3-py3-none-any.whl
# jupyterlab_language_pack_zh_CN-4.5.post3.tar.gz
```

### 任务 C：本地安装语言包测试

```bash
# 从源码可编辑安装
cd language-packs/jupyterlab-language-pack-zh-CN
pip install -e .

# 或者从构建的 wheel 安装
pip install dist/jupyterlab_language_pack_zh_CN-4.5.post3-py3-none-any.whl

# 安装 JupyterLab（如果尚未安装）
pip install jupyterlab>=4.3

# 启动 JupyterLab
jupyter lab
```

在 JupyterLab 中：
1. 菜单 Settings → Language → Chinese (Simplified, China)
2. 确认提示后刷新页面
3. 界面应显示中文

### 任务 D：检查版本一致性

```bash
python scripts/04_check_version.py
```

所有语言包版本一致时无输出（退出码0），不一致时报错。

### 任务 E：手动编译 PO 文件

```bash
# 使用 jupyterlab-translate 编译
python -m jupyterlab_translate compile \
  --locale zh_CN \
  language-packs/jupyterlab-language-pack-zh-CN/jupyterlab_language_pack_zh_CN/locale

# 或使用 msgfmt（gettext命令行工具）
msgfmt -o zh_CN/LC_MESSAGES/jupyterlab.mo zh_CN/LC_MESSAGES/jupyterlab.po
```

## 目录权限注意事项

- `repos/` 目录由脚本自动创建，用于临时克隆上游仓库
- `extensions/` 和 `jupyterlab/locale/` 下的 .pot 文件由脚本自动生成
- `language-packs/*/locale/` 下的 .po 文件主要由 Crowdin Bot 更新
- `**/LC_MESSAGES/*.mo` 和 `*.json` 是构建产物，不纳入 Git

## 使用 Conda/Mamba（可选）

如果使用 Conda 环境：

```bash
conda create -n jupyter-i18n python=3.12 -y
conda activate jupyter-i18n

# 从 conda-forge 安装
conda install -c conda-forge jupyterlab-translate copier hatchling packaging

# pip 安装 PyGithub 和 semantic-version
pip install PyGithub semantic-version
```

## 环境变量

开发时可能需要设置的环境变量：

| 变量 | 用途 | 获取方式 |
|------|------|---------|
| `GH_TOKEN` | GitHub API token，避免速率限制 | GitHub Settings → Developer settings → Personal access tokens |
| `BOT_TOKEN` | 模拟 Bot 身份（脚本中自动使用 GH_TOKEN） | 同上 |
| `CROWDIN_TOKEN` | Crowdin API 访问 | Crowdin 账户设置 |
| `CROWDIN_PROJECT_ID` | Crowdin 项目 ID（409874） | Crowdin 项目设置 |

## 故障排查

### git clone 失败
检查网络连接，或使用 SSH 方式克隆。中国大陆用户可配置 Git 代理。

### pip install 速度慢
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### jupyterlab-translate 提取 POT 失败
- 确保 Node.js 已安装（某些提取步骤需要调用 jupyterlab CLI）
- 检查目标扩展是否正确安装了 jupyterlab-translate 依赖

### 构建 wheel 时 MO 文件未生成
- 确认 `jupyterlab-translate>=1.2.0` 已安装
- 检查 .po 文件语法是否正确（无 fuzzy 标记且 msgstr 非空）
- 查看构建日志中的 jupyter-translate hook 输出

### 本地安装后翻译不显示
- 确认 JupyterLab 版本 >= 4.3
- 检查 entry-point 是否正确注册：`pip show jupyterlab-language-pack-zh-CN`
- 重启 JupyterLab（不是刷新页面）
- 检查浏览器控制台是否有错误

## 相关概念

- [自动化脚本体系](07-automation-scripts.md)
- [语言包结构剖析](05-package-anatomy.md)
- [添加新扩展到翻译](12-adding-extension.md)
- [安装语言包](../examples/01-install-language-pack.md)
