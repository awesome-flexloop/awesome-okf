---
type: Example
title: "本地构建和测试语言包"
description: "从源码克隆仓库、安装开发依赖、构建wheel、本地安装测试的完整开发者操作流程"
tags: [jupyterlab, language-pack, build, test, development, wheel]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: requirements, resource: /references/requirements-source.md, title: "Python 依赖信源" }
  - { id: package-structure, resource: /references/package-structure-source.md, title: "语言包结构信源" }
  - { id: scripts, resource: /references/scripts-source.md, title: "自动化脚本信源" }
---

# 本地构建和测试语言包

本示例面向开发者，演示如何从源码克隆 language-packs 仓库，在本地构建语言包 wheel，并安装到 JupyterLab 中进行测试。

## 完整操作流程

### 步骤 1：克隆仓库并设置环境

```bash
# 克隆仓库
git clone https://github.com/jupyterlab/language-packs.git
cd language-packs

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate
```

### 步骤 2：安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装构建工具
pip install build hatch twine

# 安装 jupyterlab-translate（PO 编译钩子）
pip install "jupyterlab-translate[cli]>=1.2.0"
```

验证依赖安装：
```bash
python -c "
import jupyterlab_translate, hatchling, packaging
print('所有依赖安装成功')
print(f'jupyterlab-translate: {jupyterlab_translate.__version__ if hasattr(jupyterlab_translate, \"__version__\") else \"OK\"}')
"
```

### 步骤 3：检查现有语言包结构

```bash
# 查看中文语言包目录结构
ls language-packs/jupyterlab-language-pack-zh-CN/
ls language-packs/jupyterlab-language-pack-zh-CN/jupyterlab_language_pack_zh_CN/locale/zh_CN/LC_MESSAGES/
```

应看到多个 .po 文件（jupyterlab.po、notebook.po 等）。

### 步骤 4：构建单个语言包 wheel

以中文简体为例：

```bash
cd language-packs/jupyterlab-language-pack-zh-CN

# 清理之前的构建产物
rm -rf dist/ build/ *.egg-info

# 构建 wheel 和 sdist
python -m build

# 查看构建产物
ls dist/
```

成功构建后，`dist/` 目录下应有：
- `jupyterlab_language_pack_zh_CN-{version}-py3-none-any.whl`（wheel 包）
- `jupyterlab_language_pack_zh_CN-{version}.tar.gz`（源码包）

### 步骤 5：检查 wheel 内容

```bash
# 列出 wheel 中的文件
python -m zipfile -l dist/jupyterlab_language_pack_zh_CN-*.whl
```

确认以下文件存在：
- `*.dist-info/METADATA`
- `*.dist-info/entry_points.txt`
- `*/__init__.py`
- `*/locale/zh_CN/LC_MESSAGES/*.mo`（编译后的二进制翻译）
- `*/locale/zh_CN/LC_MESSAGES/*.json`（JSON 格式翻译）
- **不应该包含** `*.po` 文件

检查 entry_points.txt 内容：
```bash
python -c "
import zipfile, glob
whl = glob.glob('dist/*.whl')[0]
with zipfile.ZipFile(whl) as z:
    for name in z.namelist():
        if 'entry_points.txt' in name:
            print(z.read(name).decode())
"
```
应包含 `[jupyterlab.languagepack]` 段和 `zh_CN = jupyterlab_language_pack_zh_CN`。

### 步骤 6：本地安装测试

```bash
# 安装 JupyterLab（如果尚未安装）
pip install "jupyterlab>=4.3"

# 安装刚才构建的 wheel
pip install dist/jupyterlab_language_pack_zh_CN-*-py3-none-any.whl

# 验证安装
pip show jupyterlab-language-pack-zh-CN

# 验证 entry-point 发现
python -c "
from importlib.metadata import entry_points
eps = [ep for ep in entry_points(group='jupyterlab.languagepack') if ep.name == 'zh_CN']
if eps:
    print(f'✓ 发现中文语言包: {eps[0].value}')
else:
    print('✗ 未发现中文语言包')
"
```

### 步骤 7：启动 JupyterLab 验证翻译

```bash
jupyter lab
```

在浏览器中：
1. Settings → Language → 选择 "Chinese (Simplified, China)"
2. 确认刷新
3. 验证菜单、按钮、设置面板等显示中文

### 步骤 8：修改翻译并重新构建

如果需要测试翻译修改：

1. 编辑 PO 文件：
   ```bash
   # 编辑中文翻译（示例：修改某条翻译）
   notepad language-packs/jupyterlab-language-pack-zh-CN/jupyterlab_language_pack_zh_CN/locale/zh_CN/LC_MESSAGES/jupyterlab.po
   ```

2. 注意 PO 文件格式：
   ```gettext
   msgid "Hello World"
   msgstr "你好世界"
   ```

3. 重新构建：
   ```bash
   cd language-packs/jupyterlab-language-pack-zh-CN
   pip uninstall jupyterlab-language-pack-zh-CN -y
   python -m build
   pip install dist/jupyterlab_language_pack_zh_CN-*-py3-none-any.whl
   ```

4. 重启 JupyterLab 查看效果

### 步骤 9：批量构建所有语言包

```bash
cd language-packs

# 创建输出目录
mkdir -p ../dist-all

# 批量构建
for pkg in jupyterlab-language-pack-*/; do
    echo "Building $pkg..."
    cd "$pkg"
    rm -rf dist/ build/ *.egg-info
    python -m build
    cp dist/*.whl ../../dist-all/
    cd ..
done

# 查看所有构建产物
ls ../dist-all/
```

## 使用 hatch 构建（可选）

除了 `python -m build`，也可以使用 hatch：

```bash
pip install hatch

cd language-packs/jupyterlab-language-pack-zh-CN
hatch build
# 产物在 dist/ 目录
```

## 可编辑安装（开发模式）

如果需要频繁修改翻译，可以使用可编辑安装：

```bash
cd language-packs/jupyterlab-language-pack-zh-CN
pip install -e .
```

注意：可编辑模式下 .po 文件修改后需要手动编译为 .mo/.json（因为 hatch build hook 不会自动触发）：

```bash
# 使用 jupyterlab-translate 手动编译
python -m jupyterlab_translate compile \
  jupyterlab_language_pack_zh_CN/locale/zh_CN/LC_MESSAGES/
```

## 运行版本一致性检查

```bash
cd language-packs  # 回到仓库根目录
python scripts/04_check_version.py
```

如果所有语言包版本一致，无输出；不一致会打印错误信息。

## 从本地 wheel 创建测试环境

```bash
# 创建全新测试环境
python -m venv /tmp/test-i18n
# Windows: python -m venv C:\temp\test-i18n

# 激活
/tmp/test-i18n/bin/activate  # Linux/Mac
# C:\temp\test-i18n\Scripts\Activate.ps1  # Windows

# 安装 JupyterLab 和本地构建的语言包
pip install jupyterlab
pip install dist-all/jupyterlab_language_pack_zh_CN-*.whl

# 测试
jupyter lab
```

## 常见构建错误排查

| 错误 | 原因 | 解决 |
|------|------|------|
| `No module named 'jupyterlab_translate'` | jupyterlab-translate 未安装 | `pip install "jupyterlab-translate>=1.2.0"` |
| MO/JSON 文件缺失 | jupyterlab-translate 版本过旧 | `pip install --upgrade jupyterlab-translate` |
| entry_points.txt 缺失 | pyproject.toml 配置错误 | 检查 `[project.entry-points."jupyterlab.languagepack"]` |
| PO 文件语法错误 | PO 文件格式损坏 | 用 `msgfmt -c` 检查语法 |
| fuzzy 条目不编译 | 有 fuzzy 标记的翻译 | 移除 fuzzy 标记或更新翻译 |

## 相关概念

* [语言包结构剖析](../concepts/05-package-anatomy.md)
* [Gettext 国际化基础](../concepts/06-gettext-i18n.md)
* [本地开发环境搭建](../concepts/14-dev-setup.md)
* [故障排查与常见问题](../concepts/15-troubleshooting.md)
