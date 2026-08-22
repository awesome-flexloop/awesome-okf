---
type: Example
title: 安装与使用 Echo Kernel
description: 在JupyterLite站点中安装和使用Echo Kernel的完整步骤，包括pip安装、站点构建和验证
tags: [install, usage, quickstart, jupyterlite, pip]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/python-source.md
    title: Python包与构建配置信源
  - id: plugin-src
    resource: /references/plugin-source.md
    title: 插件注册源码信源
---

## 前置条件

- Python 3.9+ 
- JupyterLite >= 0.6.0
- Node.js（开发模式需要，普通安装不需要）

## 安装步骤

### 步骤1：安装Python包

```bash
pip install jupyterlite-echo-kernel
```

此命令会：
1. 从PyPI下载 `jupyterlite-echo-kernel` 包
2. 自动构建前端扩展（TypeScript编译 + labextension打包）
3. 将labextension静态文件安装到JupyterLab扩展目录

### 步骤2：构建JupyterLite站点

```bash
jupyter lite build
```

此命令会：
1. 扫描所有已安装的JupyterLite扩展
2. 发现Echo Kernel扩展
3. 将Echo Kernel的静态资源打包到站点中
4. 生成 `_output/` 目录，包含可部署的静态站点

### 步骤3：预览站点

```bash
jupyter lite serve
# 或
python -m http.server 8000 --directory _output
```

打开浏览器访问 `http://localhost:8000`，即可看到JupyterLite界面。

### 步骤4：使用Echo Kernel

1. 打开JupyterLite后，点击 **Launcher**（启动器）
2. 在Notebook部分，可以看到 **Echo** 内核图标
3. 点击 **Echo** 创建一个新的Notebook
4. 在代码cell中输入任意文本，按Shift+Enter执行
5. 输出区域会**原样显示你输入的内容**

## 验证安装

### 方法1：检查已安装扩展

```bash
jupyter labextension list
```

输出中应包含：
```
@jupyterlite/echo-kernel v0.4.0 enabled  OK
```

### 方法2：在Notebook中验证

创建一个Echo内核的Notebook，在cell中输入：

```
Hello, Echo Kernel!
```

执行后输出应为：
```
Hello, Echo Kernel!
```

输入代码（不会被执行）：

```python
print("test")
1 + 1
```

输出为：
```
print("test")
1 + 1
```

注意：代码不会被执行，只是原样回显。

## 在现有JupyterLite项目中添加

如果你已有一个JupyterLite项目（包含 `jupyter-lite.json` 配置），只需：

```bash
# 安装Echo Kernel
pip install jupyterlite-echo-kernel

# 重新构建站点
jupyter lite build --output-dir ./dist
```

重新构建后，Echo Kernel会自动出现在内核选择器中。

## 卸载

```bash
pip uninstall jupyterlite-echo-kernel
```

然后重新构建JupyterLite站点：

```bash
jupyter lite build
```

## 开发模式安装

如果你想修改Echo Kernel源码并实时测试：

```bash
# 克隆仓库
git clone https://github.com/jupyterlite/echo-kernel.git
cd echo-kernel

# 安装Python包（开发模式）
python -m pip install -e .

# 链接JupyterLab扩展
jupyter labextension develop . --overwrite

# 启动监听模式（一个终端）
jlpm run watch

# 启动JupyterLab（另一个终端）
jupyter lab
```

开发模式下，修改 `src/` 下的TypeScript文件后，自动重新编译和打包。刷新浏览器即可看到变化。

## 部署到静态托管

构建后的 `_output/` 目录是纯静态文件，可以部署到任意静态托管服务：

```bash
# 构建
jupyter lite build --output-dir ./dist

# 部署到GitHub Pages
# 将dist/目录推送到gh-pages分支

# 部署到Vercel/Netlify
# 将dist/目录作为发布目录
```

## 常见问题

### Q: Echo Kernel在内核选择器中看不到？

A: 确保执行了 `jupyter lite build`，而不仅仅是pip install。pip安装扩展后需要重新构建站点才能生效。

### Q: 构建时提示Node.js相关错误？

A: 从PyPI安装的wheel包应该已经包含预构建的labextension，不需要Node.js。如果从源码安装，需要Node.js 18+。

### Q: 可以同时安装多个自定义内核吗？

A: 是的。JupyterLite支持同时安装多个内核（Pyodide、Xeus、Echo等），用户可以在Notebook中切换内核。

## 相关示例

- [自定义内核开发教程](02-custom-kernel-tutorial.md) — 基于Echo Kernel模板开发自己的内核

## 相关概念

- [插件注册机制](/concepts/02-plugin-registration.md)
- [构建与打包](/concepts/04-build-and-packaging.md)
