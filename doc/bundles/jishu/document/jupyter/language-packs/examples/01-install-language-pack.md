---
type: Example
title: "安装语言包"
description: "通过 pip 和 conda 两种方式安装 JupyterLab 中文语言包，并切换界面语言的完整步骤"
tags: [jupyterlab, language-pack, install, pip, conda, chinese]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-readme, resource: /references/repo-readme.md, title: "仓库根 README 信源" }
  - { id: package-structure, resource: /references/package-structure-source.md, title: "语言包结构信源" }
---

# 安装语言包

本示例演示如何安装 JupyterLab 中文（简体）语言包并切换界面语言。

## 前置条件

- JupyterLab >= 4.3 已安装
- Python 3.8+
- pip 或 conda 包管理器

## 方法一：使用 pip 安装

### 步骤 1：安装语言包

```bash
pip install jupyterlab-language-pack-zh-CN
```

安装其他语言只需替换包名后缀：

```bash
# 日语
pip install jupyterlab-language-pack-ja-JP
# 法语
pip install jupyterlab-language-pack-fr-FR
# 韩语
pip install jupyterlab-language-pack-ko-KR
# 繁体中文
pip install jupyterlab-language-pack-zh-TW
```

### 步骤 2：启动 JupyterLab

```bash
jupyter lab
```

### 步骤 3：切换语言

1. 在 JupyterLab 界面中，点击菜单栏 **Settings** → **Language**
2. 选择 **Chinese (Simplified, China)**（中文（简体，中国））
3. 在弹出的确认对话框中点击**确认**
4. 页面自动刷新后，界面显示为中文

## 方法二：使用 conda/mamba 安装

### 步骤 1：安装语言包

```bash
conda install -c conda-forge jupyterlab-language-pack-zh-CN

# 或使用 mamba（更快）
mamba install -c conda-forge jupyterlab-language-pack-zh-CN
```

### 步骤 2：启动并切换语言

与 pip 安装后相同（参见方法一步骤 2-3）。

## 方法三：同时安装多个语言包

可以同时安装多个语言包，在 Settings 中随时切换：

```bash
pip install jupyterlab-language-pack-zh-CN \
            jupyterlab-language-pack-ja-JP \
            jupyterlab-language-pack-fr-FR
```

## 验证安装

### 检查语言包是否安装成功

```bash
pip list | grep jupyterlab-language-pack
# 应输出：
# jupyterlab-language-pack-zh-CN  X.Y.postZ
```

### 验证 entry-point 注册

```bash
python -c "
from importlib.metadata import entry_points
for ep in entry_points(group='jupyterlab.languagepack'):
    print(f'已发现语言包: {ep.name}')
"
# 应输出包含 zh_CN 的行
```

## 卸载语言包

```bash
pip uninstall jupyterlab-language-pack-zh-CN
# 或
conda remove jupyterlab-language-pack-zh-CN
```

卸载后重启 JupyterLab，语言选项中不再有中文。

## 更新语言包

```bash
pip install --upgrade jupyterlab-language-pack-zh-CN
# 或
conda update -c conda-forge jupyterlab-language-pack-zh-CN
```

翻译更新通过 post 版本发布（如 4.5.post1 → 4.5.post2），`pip install --upgrade` 会自动获取最新翻译。

## 通过环境变量设置默认语言

如果希望启动时默认使用中文，可以设置环境变量：

```bash
# Linux/Mac
export LANG=zh_CN.UTF-8
jupyter lab

# Windows (PowerShell)
$env:LANG = "zh_CN.UTF-8"
jupyter lab
```

或通过 Jupyter 配置文件：
```python
# ~/.jupyter/jupyter_server_config.py
c.LanguageManager.preferred_language = 'zh_CN'
```

## 常见问题

- **看不到语言选项？** → 确认语言包装在 JupyterLab 所在的同一个 Python 环境中
- **部分界面仍是英文？** → 已安装的第三方扩展可能没有翻译，属正常现象
- **切语言后没变化？** → 尝试硬刷新浏览器（Ctrl+Shift+R）或重启 JupyterLab

## 更多语言包名称

完整的 PyPI 包名列表：

| 语言 | PyPI 包名 |
|------|----------|
| 中文（简体） | `jupyterlab-language-pack-zh-CN` |
| 中文（繁體） | `jupyterlab-language-pack-zh-TW` |
| 日本語 | `jupyterlab-language-pack-ja-JP` |
| 한국어 | `jupyterlab-language-pack-ko-KR` |
| Français | `jupyterlab-language-pack-fr-FR` |
| Deutsch | `jupyterlab-language-pack-de-DE` |
| Español | `jupyterlab-language-pack-es-ES` |
| Português (Brasil) | `jupyterlab-language-pack-pt-BR` |
| Русский | `jupyterlab-language-pack-ru-RU` |
| Italiano | `jupyterlab-language-pack-it-IT` |

⚠️ **注意**：不要安装 `jupyterlab-language-pack-ach-UG`，这是 Crowdin in-context 翻译工具，不是真正的语言包。
