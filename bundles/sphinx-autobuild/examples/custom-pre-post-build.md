---
type: Example
title: 自定义前后置命令
description: 使用 --pre-build 和 --post-build 钩子集成自定义命令——桌面通知、资源复制、自定义检查
tags: [sphinx-autobuild, pre-build, post-build, hooks, notification, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-autobuild-source
    resource: /references/sphinx-autobuild-source.md
    title: sphinx-autobuild 源码信源登记
---

# 自定义前后置命令

## 场景

你想在文档构建前后执行自定义操作，例如发送桌面通知、复制静态资源、运行 API 文档生成器等。sphinx-autobuild 通过 `--pre-build` 和 `--post-build` 选项支持这类钩子。

## 前置命令（--pre-build）

前置命令在每次 sphinx-build 执行之前运行。如果任何前置命令失败（返回非零退出码），构建会被跳过。

### 示例：构建前发送通知

**Linux（notify-send）：**

```bash
sphinx-autobuild docs docs/_build/html \
  --pre-build 'notify-send "sphinx-autobuild" "Build starting..."'
```

**macOS（osascript）：**

```bash
sphinx-autobuild docs docs/_build/html \
  --pre-build 'osascript -e "display notification \"Build starting...\" with title \"sphinx-autobuild\""'
```

**Windows（PowerShell）：**

```powershell
sphinx-autobuild docs docs/_build/html `
  --pre-build "powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Build starting...')\""
```

### 示例：构建前生成 API 文档

如果你的项目使用 `sphinx-apidoc` 自动生成 API 文档，可以在构建前运行：

```bash
sphinx-autobuild docs docs/_build/html \
  --pre-build "sphinx-apidoc -o docs/api src/my_package --force"
```

### 示例：构建前清理

```bash
sphinx-autobuild docs docs/_build/html \
  --pre-build "rm -rf docs/_build/html/*"
```

## 后置命令（--post-build）

后置命令在 sphinx-build **成功**后运行。如果构建失败，后置命令不会执行。

### 示例：构建完成后发送通知

```bash
sphinx-autobuild docs docs/_build/html \
  --post-build 'notify-send "sphinx-autobuild" "Build completed!"'
```

### 示例：构建后复制额外资源

Sphinx 的 `html_extra_path` 可以复制文件，但如果你需要更复杂的复制逻辑：

```bash
sphinx-autobuild docs docs/_build/html \
  --post-build "cp -r assets/downloads docs/_build/html/downloads"
```

### 示例：构建后验证链接

```bash
sphinx-autobuild docs docs/_build/html \
  --post-build "python -m http.server 8765 -d docs/_build/html &" \
  --post-build "sleep 1" \
  --post-build "linkchecker http://127.0.0.1:8765"
```

## 完整工作流示例

### 场景：完整文档构建流水线

```bash
sphinx-autobuild docs docs/_build/html \
  --pre-build "sphinx-apidoc -o docs/api src/my_package --force" \
  --pre-build "notify-send 'sphinx-autobuild' 'Building documentation...'" \
  --post-build "cp -r examples/generated docs/_build/html/examples" \
  --post-build "notify-send 'sphinx-autobuild' 'Build complete!'" \
  --open-browser
```

执行顺序：
1. 检测到文件变化
2. 运行 `sphinx-apidoc` 生成 API 文档
3. 发送"构建开始"通知
4. 运行 `sphinx-build` 构建文档
5. 如果构建成功，复制示例文件
6. 发送"构建完成"通知
7. 浏览器自动刷新

### 场景：Python 项目常用配置

对于使用 MyST（Markdown）的 Python 项目，常见配置如下：

```bash
sphinx-autobuild docs docs/_build/html \
  --watch src/my_package \
  --pre-build "sphinx-apidoc -f -o docs/api src/my_package" \
  --re-ignore '_autosummary' \
  --re-ignore 'api/modules.rst' \
  --open-browser --port=0
```

- `--watch src/my_package`：监听 Python 源码目录，docstring 变化触发重建
- `--pre-build "sphinx-apidoc ..."`：自动生成 API 文档
- `--re-ignore '_autosummary'`：忽略 autosummary 生成的临时文件
- `--port=0 --open-browser`：自动选择端口并打开浏览器

## 多命令顺序

`--pre-build` 和 `--post-build` 都可以多次指定，命令按指定顺序执行。命令字符串通过 `shlex.split()` 解析，支持引号和转义：

```bash
sphinx-autobuild docs docs/_build/html \
  --pre-build "echo Step 1" \
  --pre-build "echo Step 2" \
  --pre-build "echo Step 3"
```

输出顺序：

```
[sphinx-autobuild] pre-build
[sphinx-autobuild] > echo Step 1
Step 1
[sphinx-autobuild] pre-build
[sphinx-autobuild] > echo Step 2
Step 2
[sphinx-autobuild] pre-build
[sphinx-autobuild] > echo Step 3
Step 3
[sphinx-autobuild] > python -m sphinx build ...
```

## 错误处理行为

### 前置命令失败

如果前置命令失败（退出码非零）：
- 打印错误信息和 traceback
- **跳过 sphinx-build 构建**
- 服务器继续运行，等待下一次文件变化
- 浏览器不会刷新（因为没有构建完成）

```
Pre-Build command exited with exit code: 1
Please fix the cause of the error above or press Ctrl+C to stop the server.
The server will continue serving the build folder...
Traceback (most recent call last):
  ...
```

### 构建失败

如果 sphinx-build 失败：
- 打印退出码
- **后置命令不执行**
- 服务器继续运行，提供旧版本的文档
- 浏览器不会刷新

### 后置命令失败

如果后置命令失败：
- 打印错误信息
- 浏览器**仍然会刷新**（构建已成功完成）
- 服务器继续运行

## 与 Makefile 结合

在 Makefile 中定义带钩子的 livehtml 目标：

```makefile
livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) \
		--open-browser \
		--pre-build "echo Starting build..." \
		--post-build "echo Build complete!"
```

运行：

```bash
make livehtml
```

## 相关概念

- [构建系统](/concepts/04-builder-system.md)
- [CLI 入口与参数解析](/concepts/03-cli-and-entrypoint.md)
- [基础使用](/examples/basic-usage.md)
