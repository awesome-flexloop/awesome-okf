---
type: example
title: "SyncTeX 双向跳转工作流"
description: "使用 SyncTeX 在 LaTeX 编辑器和 PDF 预览之间双向定位的完整操作流程，包括正向跳转（光标→PDF）和反向跳转（Shift+Click→编辑器）"
tags: [synctex, forward-search, inverse-search, navigation, click, cursor-tracking]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: index-ts
    resource: "/references/index-ts-source.md"
    title: "插件入口源码"
  - id: pdf-ts
    resource: "/references/pdf-ts-source.md"
    title: "PDF查看器源码"
  - id: synctex-py
    resource: "/references/synctex-py-source.md"
    title: "SyncTeX处理器源码"
prerequisites:
  - concepts/01-getting-started
  - concepts/05-synctex-sync
---

# SyncTeX 双向跳转工作流

SyncTeX 是 jupyterlab-latex 最高效的导航功能，让你在编辑源码和查看 PDF 之间无缝切换。

## 前置条件确认

1. **SyncTeX 设置已开启**（默认开启）：Settings → LaTeX → 确认 "Enable SyncTeX" 已勾选
2. **至少成功编译过一次**：确保 `.synctex.gz` 文件已在 `.tex` 文件同目录生成
3. **PDF 预览面板已打开**：SyncTeX 需要 PDF 面板存在才能工作

验证 SyncTeX 是否工作：
```bash
# 在 .tex 文件目录下检查
ls -la *.synctex.gz
# 如果文件存在且非空，SyncTeX 数据已生成
```

## 工作流 1：正向搜索（编辑器 → PDF）

正向搜索帮助你快速定位当前编辑位置在 PDF 中的对应页面。

### 操作步骤

1. **确保 PDF 预览已打开**（点击 Preview 按钮）
2. **在编辑器中点击任意位置**（移动光标）
3. **观察 PDF 面板自动跳转**——PDF 会自动翻到对应页面并滚动到对应位置

### 典型使用场景

| 场景 | 操作 |
|------|------|
| 编辑某段文字想看效果 | 点击该段落 → PDF 自动跳到对应页 |
| 检查公式排版 | 点击公式源码 → PDF 定位到公式位置 |
| 找表格位置 | 点击 `\begin{tabular}` 处 → PDF 跳到表格页 |
| 查看参考文献引用 | 点击 `\cite{}` 处 → PDF 跳到引用位置 |

### 注意事项

- 正向搜索在**光标移动时自动触发**，无需按键
- 每次触发前会自动**保存文件**（确保 SyncTeX 数据是最新的）
- 如果编译后 PDF 尚未加载完成，跳转可能不生效——等待 PDF 加载完成后再点击
- 跨文件引用（`\input{subfile}`）的位置也能正确映射

## 工作流 2：反向搜索（PDF → 编辑器）

反向搜索帮助你在 PDF 中发现问题后快速跳回源码。

### 操作步骤

1. 在 PDF 预览面板中，找到要修改的内容
2. **按住 Shift+Ctrl**（Windows/Linux）或 **Shift+Cmd**（macOS）
3. **点击 PDF 中的对应位置**
4. **观察编辑器自动激活并跳转到对应行**——光标定位到产生该 PDF 内容的源码行

### 典型使用场景

| 场景 | 操作 |
|------|------|
| PDF 中有错别字 | Shift+Click 错字位置 → 跳回源码修改 |
| 公式排版有问题 | Shift+Click 公式 → 跳回公式环境 |
| 表格格式不对 | Shift+Click 表格 → 跳回 tabular 环境 |
| 检查交叉引用 | Shift+Click 引用编号 → 跳回 `\ref` 命令处 |
| 图片位置调整 | Shift+Click 图片 → 跳回 `\includegraphics` 处 |

### 键盘快捷键说明

| 操作系统 | 组合键 |
|---------|--------|
| Windows / Linux | **Shift + Ctrl + 鼠标左键单击** |
| macOS | **Shift + ⌘Cmd + 鼠标左键单击** |

注意：必须**按住修饰键的同时点击**，单独点击不会触发（避免干扰正常的 PDF 滚动和选择操作）。

## 工作流 3：编辑-查看循环

最高效的 LaTeX 编辑工作流是**编辑器+PDF双面板+SyncTeX**：

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   LaTeX 编辑器       │    PDF 预览面板      │
│   (左/主区域)        │    (右面板)          │
│                     │                     │
│  编辑代码 → Ctrl+S   │ → 自动编译→刷新     │
│      ↑              │                     │
│   Shift+Click       │ ← 发现问题          │
│  (反向跳回编辑处)    │                     │
└─────────────────────┴─────────────────────┘
```

### 推荐编辑循环

1. **写代码**：在编辑器中编写或修改 LaTeX 内容
2. **保存**：Ctrl+S 触发编译，PDF 自动更新
3. **查看效果**：PDF 面板中检查排版
4. **发现问题**：Shift+Click 问题位置，跳回编辑器
5. **修改**：在跳转位置直接修改
6. **重复**：回到步骤 2

这个循环避免了手动翻页查找对应位置的繁琐操作，显著提升编辑效率。

## 工作流 4：大文档导航

对于长文档（论文、报告、书籍），SyncTeX 尤为有用：

### 快速跳到特定章节

1. 在编辑器中点击 `\section{...}` 行
2. PDF 自动翻到该章节首页
3. 在 PDF 中浏览该章节排版
4. 需要修改时 Shift+Click 对应位置跳回

### 多文件项目

对于使用 `\input{chapters/intro.tex}` 的多文件项目：

1. 反向搜索返回的是**实际产生该内容的源文件路径**
2. 如果内容来自子文件，JupyterLab 会激活（或打开）该子文件的标签页
3. 光标定位到子文件中的对应行
4. 在子文件中编辑后保存，编译仍然从主文件执行（因为 PDF 关联的是主文件）

### 配合命令面板使用

使用命令面板（Ctrl+Shift+C）搜索以下命令：
- `LaTeX: SyncTeX from editor` — 手动触发正向同步
- `LaTeX: SyncTeX from PDF` — 手动触发反向同步（需要当前焦点在 PDF 面板）

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 点击 PDF 无反应 | 没按对组合键 | 确认按住 Shift+Ctrl/Cmd 再点击 |
| 光标移动不跳转 | PDF 面板未打开 | 先点击 Preview 打开 PDF |
| 跳转位置不准 | `.synctex.gz` 过期 | 保存文件重新编译 |
| 跳转到错误文件 | 多文件项目映射问题 | 确保从主文件打开预览 |
| 报错 "synctex not found" | synctex 命令不在 PATH | 安装完整 TeX Live（含 synctex 二进制） |
| 跳转后不在正确行 | SyncTeX 精度限制 | 点击更靠近文字的位置（而非空白处） |

## 关闭 SyncTeX

如果不需要 SyncTeX（如在低性能环境中减少开销）：

1. 打开 Settings → Settings Editor → LaTeX
2. 取消勾选 "Enable SyncTeX"
3. 刷新页面（或重新打开文档）

关闭后：
- 编译速度略有提升（不生成 .synctex.gz）
- 减少磁盘空间占用
- 失去双向跳转功能
- 光标移动不再触发同步请求

---

**相关概念文档**：
- [SyncTeX 双向同步](../concepts/05-synctex-sync.md) — SyncTeX 的底层原理和坐标转换
- [基本使用示例](01-basic-usage.md) — 基础编译预览操作
