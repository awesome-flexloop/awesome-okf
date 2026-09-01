---
type: Example
title: "本地构建文档"
description: "从零开始在本地构建Jupyter Surveys文档站点：安装Python/Node.js/nox、运行构建命令、预览HTML、解决常见构建问题。"
tags: ["构建", "nox", "mystmd", "本地开发", "文档站点"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
prerequisites:
  - Python 3.8+
  - Node.js 18+
  - Git
sources:
  - resource: "/references/noxfile-source.md"
    description: "Nox构建脚本解析"
  - resource: "/references/myst-config-source.md"
    description: "MyST配置解析"
---

# 本地构建文档

本示例指导你在本地构建Jupyter Surveys的MyST文档站点，用于预览修改、验证新增数据集的文档渲染效果。

## 前置环境安装

### 1. 确认Python和Node.js

```bash
python --version    # 需要3.8+
node --version      # 需要18+
pip --version
```

如果缺少：
- Python：从 https://python.org 下载安装
- Node.js：从 https://nodejs.org 下载LTS版本

### 2. 安装nox和uv

```bash
pip install nox uv
```

- **nox**：Python任务运行器，自动化构建流程
- **uv**：快速Python包管理器，nox使用它创建虚拟环境

## 构建步骤

### 步骤1：克隆仓库

```bash
git clone https://github.com/jupyter/surveys.git
cd surveys
```

### 步骤2：运行构建

```bash
nox -s docs
```

这个命令会：
1. 自动创建虚拟环境
2. 安装`docs/requirements.txt`中的依赖（包括mystmd）
3. 执行`myst init --ci`初始化MyST
4. 执行`myst build --ci docs _build/html`构建HTML

构建成功后，你会看到类似输出：

```
myst v1.x.x
📖 Built documentation in _build/html!
```

### 步骤3：预览构建结果

构建产物在`_build/html/`目录。你需要一个HTTP服务器来预览（直接file://打开会有跨域问题）：

```bash
# 方式一：使用Python内置服务器
cd _build/html
python -m http.server 8000
# 浏览器访问 http://localhost:8000

# 方式二：使用nox的live preview（推荐开发时使用）
cd ../..
nox -s docs-live
# 自动打开浏览器，支持热重载
```

`nox -s docs-live`启动开发服务器，修改Markdown文件后浏览器自动刷新。

### 步骤4：验证新内容

如果你添加了新数据集：
1. 构建完成后，检查首页是否显示新数据集
2. 点击进入数据集页面，确认frontmatter渲染正确
3. 检查数据文件表格和列定义是否正确
4. 如果有notebook链接，确认链接可跳转

## 模拟CI构建（部署前验证）

在提交PR前，模拟GitHub Pages的构建环境：

```bash
# Linux/macOS
BASE_URL=/surveys/ nox -s docs

# Windows PowerShell
$env:BASE_URL="/surveys/"; nox -s docs
```

这会确保所有链接使用`/surveys/`前缀，避免部署后404。

## 常见问题

### Q: nox: command not found

**原因**：nox未安装或不在PATH中。

**解决**：
```bash
pip install nox
# 如果仍找不到，使用python -m
python -m nox -s docs
```

### Q: myst: command not found

**原因**：docs/requirements.txt中的mystmd未正确安装。

**解决**：
```bash
# 手动安装mystmd
npm install -g mystmd
# 或检查requirements.txt
cat docs/requirements.txt
```

### Q: Node.js版本过旧

**原因**：mystmd需要Node.js 18+。

**解决**：升级Node.js到LTS版本（20.x推荐）。

### Q: 构建后页面空白

**原因**：使用file://协议打开HTML（CORS限制）。

**解决**：使用HTTP服务器（`python -m http.server`）或`nox -s docs-live`。

### Q: 新数据集不出现在导航中

**原因**：TOC使用glob模式，目录名或index.md位置不对。

**解决**：
1. 确认目录名格式为`YYYY-MM-topic-name/`
2. 确认目录下有`index.md`文件
3. 重新运行`nox -s docs`（清理缓存：删除`_build/`目录）

## 清理构建产物

```bash
# 删除构建目录
rm -rf _build/

# Windows
Remove-Item -Recurse -Force _build/
```

## 相关内容

- [MyST文档系统](../concepts/04-myst-docs-system.md)：了解MyST的核心概念
- [noxfile.py解析](../references/noxfile-source.md)：构建脚本源码
- [CI/CD部署](../concepts/07-cicd-deployment.md)：构建如何自动部署
