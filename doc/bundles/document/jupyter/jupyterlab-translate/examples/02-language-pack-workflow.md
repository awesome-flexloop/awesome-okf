---
type: Example
title: 语言包仓库工作流
description: 维护JupyterLab集中式语言包仓库的完整工作流，从多个扩展提取字符串、更新翻译到编译发布
tags: [example, language-pack, workflow, crowdin, extract-pack, update-pack, compile-pack]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: api-source
    resource: /references/api-source.md
    title: API层函数映射
  - id: plugin-source
    resource: /references/plugin-source.md
    title: Hatch构建钩子源码
---

# 语言包仓库工作流

本示例演示如何维护[jupyterlab/language-packs](https://github.com/jupyterlab/language-packs)集中式语言包仓库，包括从JupyterLab核心和多个第三方扩展提取字符串、更新翻译、编译最终语言包。

## 语言包仓库结构

```
language-packs/
├── jupyterlab/                      # JupyterLab核心源码（或已安装包）
├── extensions/                      # 第三方扩展源码目录
│   ├── jupyterlab-git/
│   ├── jupyterlab-lsp/
│   └── ...
├── repository/                      # 语言包仓库工作目录
│   ├── jupyterlab/
│   │   └── locale/
│   ├── extensions/                  # POT文件（extract产物）
│   ├── jupyterlab_extensions/       # PO文件（update产物）
│   └── language-packs/              # 最终编译的语言包
│       ├── jupyterlab-language-pack-zh-CN/
│       ├── jupyterlab-language-pack-ko-KR/
│       └── ...
└── README.md
```

## 步骤一：提取JupyterLab核心字符串

```bash
# 从JupyterLab核心提取POT模板
jupyterlab-translate extract-pack \
    ./jupyterlab \
    ./repository \
    jupyterlab
```

这会在 `repository/jupyterlab/locale/` 下生成 `jupyterlab.pot`。

## 步骤二：提取第三方扩展字符串

对每个扩展执行extract-pack：

```bash
# 方法1：逐个提取
jupyterlab-translate extract-pack ./extensions/jupyterlab-git ./repository jupyterlab_git
jupyterlab-translate extract-pack ./extensions/jupyterlab-lsp ./repository jupyterlab_lsp

# 方法2：批量循环（bash）
for ext_dir in ./extensions/*/; do
    ext_name=$(basename "$ext_dir" | tr '-' '_')
    jupyterlab-translate extract-pack "$ext_dir" ./repository "$ext_name"
done
```

扩展的POT文件会生成在 `repository/extensions/<project>/locale/<project>.pot`。

## 步骤三：上传POT到Crowdin（可选）

语言包项目通常使用Crowdin进行协作翻译：

```bash
# 使用Crowdin CLI上传新的POT文件
crowdin upload sources
```

## 步骤四：从Crowdin下载翻译（或手动更新）

```bash
# 方法1：通过Crowdin CLI下载
crowdin download -l zh-CN,ko-KR,es-ES

# 方法2：手动将PO文件放到正确位置
# repository/jupyterlab/locale/zh_CN/LC_MESSAGES/jupyterlab.po
# repository/jupyterlab_extensions/jupyterlab_git/locale/zh_CN/LC_MESSAGES/jupyterlab_git.po
```

## 步骤五：更新PO文件

使用update-pack命令将新字符串合并到已有的PO文件：

```bash
# 更新核心
jupyterlab-translate update-pack ./jupyterlab ./repository jupyterlab -l zh_CN -l ko_KR

# 更新扩展
jupyterlab-translate update-pack ./extensions/jupyterlab-git ./repository jupyterlab_git -l zh_CN
```

update-pack会将POT中的新字符串合并到对应语言的PO文件中，保留已有翻译。

## 步骤六：编译语言包

```bash
# 编译JupyterLab核心语言包
jupyterlab-translate compile-pack ./repository jupyterlab -l zh_CN -l ko_KR

# 编译扩展语言包（每个扩展单独compile-pack）
jupyterlab-translate compile-pack ./repository jupyterlab_git -l zh_CN
```

compile-pack会：
1. 将PO文件编译为MO和JSON
2. 自动移动文件到 `language-packs/jupyterlab-language-pack-<locale>/` 目录
3. 如果语言包目录不存在，使用copier从cookiecutter模板创建

## 步骤七：更新贡献者列表

设置Crowdin API密钥并更新贡献者：

```bash
export CROWDIN_API_KEY="your-key"
jupyterlab-translate update-contributors ./repository/language-packs/jupyterlab-language-pack-zh-CN
```

或在Hatch构建时自动更新：

```bash
# 构建sdist时会自动更新贡献者（需要CROWDIN_API_KEY）
cd repository/language-packs/jupyterlab-language-pack-zh-CN
pip install build
python -m build --no-isolation
```

## 步骤八：构建和发布

进入每个语言包目录构建wheel：

```bash
cd repository/language-packs/jupyterlab-language-pack-zh-CN

# 构建sdist和wheel
python -m build --no-isolation

# wheel中只包含.json和.mo文件（不含.po）
# sdist中包含.po文件和CONTRIBUTORS.md
```

## 自动化脚本示例

以下是一个简化的批量处理脚本：

```bash
#!/bin/bash
set -e

REPO_DIR="./repository"
LOCALES="zh_CN ko_KR es_ES fr_FR de_DE ja_JP"

# 1. 提取核心
echo "Extracting JupyterLab core..."
jupyterlab-translate extract-pack ./jupyterlab "$REPO_DIR" jupyterlab

# 2. 提取扩展
echo "Extracting extensions..."
for ext_dir in ./extensions/*/; do
    ext_name=$(basename "$ext_dir" | tr '-' '_' | tr '[:upper:]' '[:lower:]')
    echo "  Extracting $ext_name..."
    jupyterlab-translate extract-pack "$ext_dir" "$REPO_DIR" "$ext_name"
done

# 3. 更新和编译每个语言
for locale in $LOCALES; do
    echo "Processing $locale..."

    # 核心
    jupyterlab-translate update-pack ./jupyterlab "$REPO_DIR" jupyterlab -l "$locale"
    jupyterlab-translate compile-pack "$REPO_DIR" jupyterlab -l "$locale"

    # 扩展
    for ext_dir in ./extensions/*/; do
        ext_name=$(basename "$ext_dir" | tr '-' '_' | tr '[:upper:]' '[:lower:]')
        jupyterlab-translate update-pack "$ext_dir" "$REPO_DIR" "$ext_name" -l "$locale"
        jupyterlab-translate compile-pack "$REPO_DIR" "$ext_name" -l "$locale"
    done
done

echo "Done! Language packs are in $REPO_DIR/language-packs/"
```

## 新语言添加

添加新语言（如葡萄牙语pt_BR）：

```bash
# 1. update-pack会自动创建新的PO文件
jupyterlab-translate update-pack ./jupyterlab ./repository jupyterlab -l pt_BR

# 2. compile-pack会自动创建语言包目录
jupyterlab-translate compile-pack ./repository jupyterlab -l pt_BR

# 3. 首次创建时会自动从cookiecutter模板生成包结构
```

## 相关概念

- [CLI命令参考](/concepts/03-cli-commands.md)
- [翻译目录管理](/concepts/05-catalog-management.md)
- [Hatch构建钩子集成](/concepts/07-hatch-build-hook.md)
- [Crowdin贡献者集成](/concepts/10-contributors-crowdin.md)
- [双模式分发机制](/concepts/11-dual-mode-distribution.md)
