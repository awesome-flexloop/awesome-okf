---
type: example
title: "故障排查"
description: "jupyterlab-latex 常见问题诊断与解决方案，包括安装问题、编译失败、SyncTeX 不工作、PDF 不显示、中文乱码等典型问题"
tags: [troubleshooting, debugging, errors, common-issues, faq, diagnostics]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: build-py
    resource: "/references/build-py-source.md"
    title: "编译处理器源码"
  - id: error-tsx
    resource: "/references/error-tsx-source.md"
    title: "错误面板源码"
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/README.md"
    title: "README.md"
prerequisites:
  - concepts/01-getting-started
  - concepts/03-latex-compilation
---

# 故障排查

本示例覆盖 jupyterlab-latex 的常见问题，按症状分类提供诊断步骤和解决方案。

## 诊断工具

在排查问题之前，使用以下工具收集信息：

### 1. 查看 Jupyter Server 终端日志

启动 `jupyter lab` 的终端窗口会显示所有 HTTP 请求和编译输出，是排障的第一手信息源。关注以下日志：
- `Building: xelatex ...` — 实际执行的编译命令
- `[LabServerApp] Build failed with code N` — 编译退出码
- HTTP 状态码（404, 403, 500）

### 2. 使用错误面板的三种视图模式

编译失败时底部面板显示错误信息，切换视图模式获取不同粒度的信息：
- **Filtered**（默认）：只显示关键错误行（! 和 l. 开头的行）
- **Unfiltered**：显示完整编译输出（含警告和包信息）
- **JSON**：显示后端返回的原始 JSON，包含 `fullMessage` 和 `errorOnlyMessage`

### 3. 浏览器开发者工具

前端问题（如面板不显示、按钮不出现）可在浏览器 F12 开发者工具中查看：
- Console 标签：JavaScript 错误
- Network 标签：HTTP 请求状态和响应内容

---

## 安装问题

### 问题：pip install 成功但 JupyterLab 中看不到扩展

**诊断**：
```bash
jupyter labextension list
jupyter server extension list
```

**解决方案**：
1. 确认两个扩展都显示 `enabled OK`
2. 如果 labextension 未启用：
   ```bash
   jupyter labextension install @jupyterlab/latex
   ```
3. 如果 server extension 未启用：
   ```bash
   jupyter server extension enable jupyterlab_latex
   ```
4. 重启 Jupyter Server：`jupyter lab`

### 问题：前端预构建扩展不兼容 JupyterLab 版本

**诊断**：浏览器 Console 显示 API 版本不匹配错误。

**解决方案**：
1. 确认 JupyterLab 版本 ≥ 4.0：`jupyter lab --version`
2. 升级 jupyterlab-latex：`pip install -U jupyterlab-latex`
3. 重新构建 JupyterLab：`jupyter lab build`

### 问题：conda 安装后 server extension 报 404

**诊断**：点击 Preview 返回 404 Not Found。

**解决方案**：
1. 确认 conda 环境与 JupyterLab 运行环境一致
2. 显式启用：`jupyter server extension enable jupyterlab_latex`
3. 检查是否有多个 Python 环境冲突

---

## 编译问题

### 问题：点击 Preview 报 "xelatex not found" 或类似错误

**诊断**：错误面板显示 `command not found` 或 `xelatex: command not found`。

**原因**：LaTeX 发行版未安装或不在 PATH 中。

**解决方案**：

| 操作系统 | 安装方法 |
|---------|---------|
| Ubuntu/Debian | `sudo apt install texlive-xetex texlive-latex-extra` |
| Fedora/RHEL | `sudo dnf install texlive-xetex texlive-collection-latexextra` |
| macOS | `brew install --cask mactex`（完整版）或 `brew install basictex`（精简版） |
| Windows | 安装 [MiKTeX](https://miktex.org/) 或 [TeX Live](https://tug.org/texlive/) |
| 跨平台 | 安装 [Tectonic](https://tectonic-typesetting.github.io/)，配置 `latex_command='tectonic'` |

验证安装：
```bash
xelatex --version
```

### 问题：编译报错 "Undefined control sequence"

**诊断**：错误面板 Filtered 视图显示 `! Undefined control sequence.` 和 `l.<N> \<command>`。

**解决方案**：

| 错误命令 | 缺少的宏包 | 添加到导言区 |
|---------|-----------|-------------|
| `\textcite` / `\autocite` | biblatex | `\usepackage[backend=biber]{biblatex}` |
| `\includegraphics` | graphicx | `\usepackage{graphicx}` |
| `\mint` / minted 环境 | minted | `\usepackage{minted}` + `shell_escape=True` |
| `\ctexset` / ctex 命令 | ctex | 使用 `\documentclass{ctexart}` |
| `\begin{algorithm}` | algorithm2e | `\usepackage{algorithm2e}` |
| `\textcolor` | xcolor | `\usepackage{xcolor}` |

### 问题：编译报错 "File X not found"

**诊断**：`! LaTeX Error: File 'xxx.sty' not found.` 或 `! LaTeX Error: File 'xxx.xxx' not found.`

**解决方案**：
1. **宏包缺失**：安装对应的 TeX Live/MiKTeX 包
   - TeX Live：`tlmgr install <packagename>`
   - MiKTeX：使用 MiKTeX Console 安装
2. **图片/数据文件缺失**：确认文件路径正确，相对路径相对于 `.tex` 文件所在目录
3. **`.bib` 文件缺失**：确认 `\bibliography{ref}` 中的 `ref.bib` 文件存在

### 问题：BibTeX 不工作（参考文献显示 [?]）

**诊断**：PDF 中引用显示为 `[?]`，或没有参考文献列表。

**解决方案**：
1. 确认 `.bib` 文件与 `.tex` 在同一目录（或路径正确）
2. 确认 `\bibliographystyle{plain}` 和 `\bibliography{ref}` 在正文中
3. 检查编译日志是否运行了 BibTeX（应看到 `bibtex <filename>` 命令）
4. 如果使用 biber，确认配置了 `c.LatexConfig.bib_command = 'biber'`
5. 手动清理中间文件后重试：删除 `.aux`、`.bbl`、`.blg`、`.out` 后重新编译

### 问题：中文乱码或不显示

**诊断**：PDF 中中文部分为空白、方块或乱码。

**解决方案**：

| 引擎 | 中文支持方案 |
|------|------------|
| **XeLaTeX**（推荐） | 使用 `\documentclass{ctexart}` 或 `\usepackage{xeCJK}` |
| pdfLaTeX | 使用 CJK 宏包（不推荐）或转换输入 |
| LuaLaTeX | 使用 `\documentclass{ctexart}` 或 `\usepackage{luatexja}` |
| Tectonic | 同 XeLaTeX，但需确认字体可用 |

XeLaTeX + ctex 的最小中文文档：
```latex
\documentclass{ctexart}
\begin{document}
中文内容正常显示。
\end{document}
```

### 问题：编译成功但 PDF 不更新

**诊断**：保存后 PDF 面板没有变化，或显示旧内容。

**解决方案**：
1. 确认文件确实已保存（标题栏无 ● 未保存标记）
2. 点击 Preview 按钮手动刷新
3. 检查 PDF 面板的缩放设置——可能已经更新但你在看错误的位置
4. 检查浏览器缓存：在 PDF 面板中按 F5 刷新
5. 确认编译输出目录与 PDF 查找目录一致（如果修改了 `pdf_dir`）

### 问题：shell_escape 启用后仍报错

**诊断**：使用 minted 等包时仍然报 "minted Error: You must invoke LaTeX with the -shell-escape flag"。

**解决方案**：
1. 确认配置文件中 `c.LatexConfig.shell_escape = True` 已设置
2. **重启 Jupyter Server**——配置更改需要重启才能生效
3. 确认编译日志中包含 `-shell-escape` 参数：
   ```
   Building: xelatex -shell-escape -synctex=1 -interaction=nonstopmode ...
   ```
4. 确认 pygmentize 在 PATH 中：`pygmentize -V`

---

## SyncTeX 问题

### 问题：Shift+Click 无反应

**诊断**：在 PDF 中按住 Shift+Ctrl/Cmd 点击，编辑器不跳转。

**解决方案**：
1. 确认 SyncTeX 设置已开启（Settings → LaTeX → synctex: true）
2. 确认 `.synctex.gz` 文件存在（编译时含 `-synctex=1` 参数）
3. 确认按对了组合键：
   - Windows/Linux：**Shift + Ctrl**（不是 Shift + Alt）
   - macOS：**Shift + Cmd**（不是 Shift + Ctrl）
4. 点击位置应该在文字内容上，不是页面空白处
5. 检查终端日志中是否有 `/latex/synctex/` 请求

### 问题：正向搜索（光标移动）不跳转

**诊断**：在编辑器中移动光标，PDF 不自动跳转。

**解决方案**：
1. 确认 PDF 预览面板已打开
2. 确认 SyncTeX 设置已开启
3. 确认文件已保存（正向搜索前会自动保存）
4. 检查是否有编译错误（编译失败时不生成新的 SyncTeX 数据）

### 问题：SyncTeX 跳转到错误位置

**诊断**：跳转了但位置不对（如偏移几行）。

**原因**：SyncTeX 精度有限，尤其在宏展开、复杂公式、分页附近。

**解决方案**：
1. 尝试点击更靠近目标文字的位置
2. 重新编译（中间文件可能过期）
3. 大文档中分章节编译，减少单文件复杂度

---

## PDF 显示问题

### 问题：PDF 面板空白或显示 "Failed to load PDF"

**诊断**：PDF 面板打开但无内容，或显示错误消息。

**解决方案**：
1. 检查编译是否真正成功（状态码 200，输出 "LaTeX compiled"）
2. 检查 `.pdf` 文件是否存在且非空：
   ```bash
   ls -la *.pdf
   ```
3. 打开浏览器开发者工具（F12），在 Network 标签查看 PDF 请求的响应
4. 尝试在 JupyterLab 文件浏览器中双击 PDF 文件独立打开
5. 清除浏览器缓存后刷新页面

### 问题：PDF 面板工具栏不显示

**诊断**：PDF 面板中只有内容没有工具栏按钮。

**解决方案**：
1. 这是预期行为——jupyterlab-latex 的 PDF 工具栏是精简版
2. 右键 PDF 面板标签 → 检查是否可以显示工具栏
3. 如果完全没有工具栏按钮（连翻页缩放都没有），可能是 CSS 加载问题，刷新页面

### 问题：PDF 中文文字不显示

**诊断**：PDF 中中文为空白或方块。

**解决方案**：
1. 确认使用 XeLaTeX/LuaLaTeX 引擎
2. 确认文档使用 `ctexart` 文档类或正确配置了中文字体
3. 确认系统安装了中文字体
   - Linux：安装 `fonts-noto-cjk` 或 `fonts-wqy-zenhei`
   - Windows：系统自带中文字体
   - macOS：安装 Xcode Command Line Tools 或中文字体包

---

## 性能问题

### 问题：编译很慢

**诊断**：每次保存需要等待数秒甚至更长。

**解决方案**：
1. 大文档考虑使用 Tectonic 或 latexmk（增量编译更快）
2. 减少 `run_times`（如果不复杂可以用 1 轮）
3. 使用 `\includeonly{}` 只编译部分章节
4. 将图片放在子目录（减少清理扫描时间）
5. 关闭 SyncTeX（`synctex: false`）小幅提升速度

### 问题：JupyterLab 卡顿

**诊断**：编辑时 JupyterLab 界面响应慢。

**解决方案**：
1. 每次保存触发编译，如果频繁自动保存会导致持续编译
2. 调整 JupyterLab 自动保存间隔：Settings → Document Manager → autosaveInterval
3. 关闭 SyncTeX 减少光标移动时的 HTTP 请求
4. 大文档在编辑时可以关闭 PDF 预览面板，需要时再打开

---

## 错误面板显示的 HTTP 状态码

| 状态码 | 含义 | 排查方向 |
|--------|------|---------|
| 200 | 编译成功 | PDF 应正常显示 |
| 400 | 请求错误 | 文件不是 `.tex` 扩展名 |
| 403 | 文件不存在 | 检查文件路径和权限 |
| 404 | 端点不存在 | 服务端扩展未启用 |
| 500 | 编译错误 | 查看错误面板的 Unfiltered 模式获取完整日志 |

## 获取帮助

如果以上方案都不能解决问题：

1. 查看 [GitHub Issues](https://github.com/jupyterlab/jupyterlab-latex/issues) 是否有已知问题
2. 收集以下信息提交 Issue：
   - jupyterlab-latex 版本：`pip show jupyterlab-latex`
   - JupyterLab 版本：`jupyter lab --version`
   - 操作系统和 LaTeX 发行版
   - 完整的错误日志（Unfiltered 模式）
   - 最小复现示例（一个最小的 `.tex` 文件）

---

**相关概念文档**：
- [LaTeX 编译流程](../concepts/03-latex-compilation.md) — 理解编译过程和错误输出
- [配置指南](../concepts/07-configuration.md) — 配置项详解
- [配置示例](03-configuration.md) — 典型配置代码
