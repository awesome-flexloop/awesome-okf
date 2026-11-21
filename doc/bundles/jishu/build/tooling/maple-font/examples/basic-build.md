---
type: Example
title: "基本构建"
description: "从零安装依赖到产出第一个 Maple Mono 字体文件——完整的新手友好流程"
tags: ["maple-mono", "build", "basic", "setup"]
sources:
  - id: README-SETUP
    resource: "README.md#Setup"
    description: "官方安装指南"
  - id: PYPROJECT
    resource: "pyproject.toml"
    description: "Python 依赖声明"
prerequisites:
  - "../concepts/00-introduction.md"
  - "../concepts/01-build-pipeline.md"
status: draft
---

# 示例 1：基本构建

本示例带你从零开始构建自己的第一份 Maple Mono 字体。适合**第一次接触 Maple Mono 构建系统**的读者。

## 前置条件

- Python 3.10+
- 任意现代操作系统（macOS / Linux / Windows）
- 网络连接（用于下载仓库）

## Step 1：克隆仓库

```bash
# 变量字体版本（v7 主版本推荐）
git clone https://github.com/subframe7536/maple-font --depth 1 -b variable maple-font

cd maple-font
```

`--depth 1` 只拉最新 commit，`-b variable` 切换到变量字体分支。

## Step 2：安装依赖

```bash
# 推荐方式：pip + requirements.txt
pip install -r requirements.txt

# 或者用 pyproject.toml
pip install -e .
```

**核心依赖**：

| 包 | 版本 | 作用 |
|----|------|------|
| `foundrytools-cli` | latest | 字体批处理（字形修正、hinting、转换） |
| `fontTools` | latest | 低水平字体表操作 |
| `ttfautohint` | latest | 自动 hinting |
| `skia-pathops` | latest | 路径运算（可选） |
| `fontfreeze` | optional | 参考实现（已内置到 freeze.py） |

**验证安装**：

```bash
python -c "from build import FontConfig; print('OK')"
# 应输出 OK
```

## Step 3：运行构建

最简单的构建命令：

```bash
python build.py
```

这条命令会：
1. 加载默认 config.json（不启用 NF/CN）
2. 从源目录实例化 9 种字重的 TTF
3. 并行构建基础字体 + hinted 版
4. 输出到 `fonts/` 目录

**预期输出结构**：

```
maple-font/fonts/
├── Variable/
│   ├── MapleMono[wght]-VF.ttf
│   ├── MapleMono-Italic[wght]-VF.ttf
├── TTF/
│   ├── MapleMono-Regular.ttf
│   ├── MapleMono-Bold.ttf
│   ├── ... (9 个字重 × 2 种风格 = 18 个文件)
├── TTF-AutoHint/
│   └── ... (同 TTF/ 但含 hinting)
├── OTF/
│   └── ... (CFF 轮廓版本)
└── Woff2/
    └── ... (压缩 Web 字体版本)
```

## Step 4：验证输出

用任意字体查看器（如 FontForge、BirdFont、或在线 [glyphr](https://glyphrstudio.com/)）打开 `fonts/Variable/MapleMono[wght]-VF.ttf`，你应该能看到：

- 字重滑块：可以在 100-900 之间连续调节
- 智能连字：在支持的编辑器里输入 `=>` 显示为箭头连字
- 变体切换：如果渲染器支持 OpenType CV/SS，可以手动切换

## Step 5：安装到系统（可选）

### macOS

```bash
cp fonts/Variable/*.ttf ~/Library/Fonts/
```

### Linux

```bash
sudo cp fonts/Variable/*.ttf /usr/local/share/fonts/
fc-cache -f
```

### Windows

把文件复制到 `C:\Windows\Fonts\` 或双击 TTF 文件点「安装」。

## 常见问题排查

### 依赖安装失败

```bash
# 某些字体处理库需要编译工具链
# macOS:
brew install freetype
# Ubuntu:
sudo apt install libfreetype-dev
```

### 构建超时

降低并行度：
```bash
python build.py --pool-size 2
```

### SMB 网络盘慢

把仓库移到本地盘。Maple Mono 会自动检测 SMB 并降级 pool_size=1，但最好直接移走。

### Codespace 容器 OOM

使用 `--least-styles` 只构建 4 种基础字重：
```bash
python build.py --least-styles
```

## 相关资源

- [构建流水线概念](../concepts/01-build-pipeline.md)
- [配置系统概念](../concepts/02-config-system.md)
- [并行构建概念](../concepts/08-parallel-build.md)
