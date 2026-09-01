---
type: concept
title: "LaTeX 编译流程"
description: "jupyterlab-latex 后端如何构建编译命令序列、管理多轮编译（含 BibTeX）、过滤错误输出、清理临时文件，以及 Tectonic 引擎的特殊处理"
tags: [compilation, build-pipeline, xelatex, bibtex, tectonic, shell-escape, error-filtering, cleanup]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: build-py
    resource: "/references/build-py-source.md"
    title: "编译处理器源码"
  - id: config-py
    resource: "/references/config-py-source.md"
    title: "配置类源码"
  - id: util-py
    resource: "/references/util-py-source.md"
    title: "命令执行工具源码"
  - id: error-tsx
    resource: "/references/error-tsx-source.md"
    title: "错误面板源码"
---

# LaTeX 编译流程

jupyterlab-latex 的编译过程由后端 Tornado handler (`LatexBuildHandler`) 全权负责，前端仅通过 HTTP GET 请求触发编译并接收结果。整个编译流程可以分为六个阶段：路径验证 → 上下文切换与清理 → 命令序列构建 → 执行编译 → 输出解析 → 临时文件清理。

## 编译触发时机

前端在以下三种情况下触发编译：

| 触发点 | 代码位置 | 说明 |
|--------|---------|------|
| 首次打开预览 | `findOpenOrRevealPDF()` 中调用 `latexBuildRequest()` | 确保 PDF 存在并是最新的 |
| 文件保存后 | `onFileChanged()` 监听 `fileChanged` 信号 | 每次保存自动编译（350ms debounce） |
| 用户点击 Preview 按钮 | `CommandIDs.latexPreview` 命令 | 首次或显式刷新 |

## 阶段一：路径验证

编译请求到达 `LatexBuildHandler.get(path)` 后首先验证：

```python
filename = os.path.basename(self.filepath_local)
if not filename.lower().endswith('.tex'):
    raise web.HTTPError(400, ...)
if not os.path.isfile(self.filepath_local):
    raise web.HTTPError(403, ...)
```

- 路径由 `url2path_unix` 将 URL 路径转为 OS 路径，确保跨平台兼容
- `self.tex_base_name` 取文件名不含 `.tex` 后缀，用于后续生成 `.aux`/`.pdf`/`.synctex.gz` 等文件名

## 阶段二：上下文切换与临时文件管理

编译在 `latex_cleanup` 上下文管理器中执行：

```python
with latex_cleanup(self.tex_base_name, self.tex_dir):
    os.chdir(self.tex_dir)  # 切换到 .tex 文件所在目录
    # ... 执行编译命令
```

**`latex_cleanup` 上下文管理器行为**：

1. **进入时**：
   - 记录当前工作目录
   - 切换到 `.tex` 文件所在目录（因为 LaTeX 引擎需要在源文件目录执行）

2. **退出时**：
   - 扫描当前目录下以 `tex_base_name.` 开头的所有文件
   - 对照 `WHITELISTED_EXTENSIONS` 白名单删除临时文件
   - 恢复原始工作目录

**白名单保留的文件扩展名**（这些文件不会被删除）：

```
.tex, .pdf, .bib, .png, .jpg, .svg, .csv,
._tex, ._pdf, ._bib, ._png, ._jpg, ._svg, ._csv
```

注意：`.aux`、`.log`、`.synctex.gz`、`.bbl`、`.blg`、`.out` 等中间文件会被**删除**，确保每次编译从干净状态开始（但 BibTeX 需要 `.aux` 文件，所以多轮编译在单次 handler 调用内完成，不跨请求保留中间文件）。

## 阶段三：命令序列构建

`build_tex_cmd_sequence()` 方法根据配置构建编译命令列表。有三条分支：

### 分支 A：自定义命令（manual_cmd_args）

当配置了 `manual_cmd_args`（用户完全自定义编译命令）：

```python
if self.manual_cmd_args:
    cmd = self.manual_cmd_args.copy()
    cmd.append(self.tex_base_name)
    if self.run_synctex:
        cmd.extend(['-synctex=1', '-interaction=nonstopmode'])
    return [cmd]
```

- 将 `manual_cmd_args` 列表原样使用，追加 `.tex` 基础名
- synctex=1 时自动追加 SyncTeX 参数
- 只执行**一次**命令（忽略 `run_times` 配置）

### 分支 B：Tectonic 引擎

当 `latex_command` 设置为 `tectonic`：

```python
elif self.latex_command == 'tectonic':
    base_cmd = ['tectonic', f'{tex_base_name}.tex']
    if self.run_synctex:
        base_cmd.append('--synctex')
    cmd_sequences = [base_cmd + ['--keep-logs', '--outfmt', 'pdf']]
    return cmd_sequences
```

Tectonic 是现代 Rust 编写的 LaTeX 引擎，内置自动依赖下载，无需 BibTeX 额外步骤。命令序列只有一条。

### 分支 C：传统 TeX Live 引擎（默认路径）

当 `latex_command` 为 `xelatex`（默认）/`pdflatex`/`lualatex` 等：

```python
base_cmd = [self.latex_command]
if self.shell_escape:
    base_cmd.append('-shell-escape')
if self.run_synctex:
    base_cmd.append('-synctex=1')
base_cmd.extend(['-interaction=nonstopmode', '-file-line-error', tex_base_name])
```

构建基础命令后，根据 `run_times` 决定编译轮数，再根据 `.bib` 文件是否存在插入 BibTeX：

```
默认 run_times=1：
  [latex]
检测到 .bib 文件（bib_condition 为 True）：
  [latex, bibtex, latex, latex]  (4轮：编译→bibtex→编译→编译)
run_times=N 且有 bib：
  latex 重复 N 次 → bibtex → latex → latex
```

**BibTeX 检测逻辑**：
```python
if os.path.isfile(f'{self.tex_base_name}.bib'):
    bib_condition = True
else:
    bib_condition = any(
        re.findall(re.compile(r'\\bibliography|\\addbibresource'), line)
        for line in self.contents
    )
```
检测方式有两种：
1. 同名 `.bib` 文件存在
2. `.tex` 文件内容中包含 `\bibliography` 或 `\addbibresource` 命令

## 阶段四：执行编译

`run_latex(sequence)` 遍历命令序列逐个执行：

```python
async def run_latex(self, cmd_sequences):
    for command in cmd_sequences:
        code, output = await run_command(command)
        if code != 0:
            # 非0退出码 = 编译错误
            return code, output
    return 0, "LaTeX compiled successfully!"
```

**子进程执行**：通过 `jupyterlab_latex/util.py` 中的 `run_command` 函数执行：
- Unix/Linux/macOS：使用 `tornado.process.Subprocess`（异步）
- Windows：使用 `subprocess.run`（同步回退，因为 Tornado 异步子进程在 Windows 上不支持）
- 所有命令的 stderr 被重定向到 stdout，统一读取

**`-interaction=nonstopmode` 的作用**：编译遇到错误时不停顿等待用户输入，直接继续并在日志中记录错误，确保服务器不会挂起。

## 阶段五：输出解析与错误响应

编译成功（所有命令返回 0）：
- 直接返回字符串 `"LaTeX compiled"`，状态码 200
- 前端收到后刷新 PDF 面板，关闭错误面板

编译失败（任意命令返回非 0）：
- 调用 `filter_output(output)` 过滤输出
- 返回 HTTP 500，JSON 体包含：
```json
{
  "fullMessage": "完整的编译输出...",
  "errorOnlyMessage": "仅 ! 和 ? 开头的错误行..."
}
```

**输出过滤器 `filter_output()`**：

使用正则 `r"(^(?:!|l\.).*)|(^.*?(?:Error|Undefined))"` 匹配错误行：

| 模式 | 匹配 | 示例 |
|------|------|------|
| `^!` | 以 `!` 开头的错误消息 | `! Undefined control sequence.` |
| `^l\.` | 以 `l.` 开头的错误位置 | `l.42 \nonexistentcmd` |
| `Error` | 包含 Error 的行 | `! LaTeX Error: File ... not found.` |
| `Undefined` | 包含 Undefined 的行 | `! Undefined control sequence.` |

注意：正则中 `?` 是正则元字符而非字面量，这是代码中的一个小瑕疵——`?` 行（TeX 错误提示中的用户输入提示行）不会被匹配到。

## 阶段六：错误面板显示

前端收到 500 响应后调用 `errorPanelInit()`：

```typescript
await errorPanelInit(latexError, path, widget, translator);
```

创建或复用 ErrorPanel 并添加到编辑器 widget 的底部区域：
- 面板标题显示 `LaTeX build failed!` + 文件名
- `LatexError` React 组件解析 JSON 响应，提供三种查看模式：
  - **Filtered**（默认）：仅显示 `errorOnlyMessage` 中的错误行
  - **Unfiltered**：显示 `fullMessage` 完整输出
  - **JSON**：原始 JSON 响应

## 编译流程图

```
GET /latex/build/{path}?synctex=1
    │
    ├─ 验证 .tex 扩展名 + 文件存在
    │
    ├─ [latex_cleanup 上下文开始]
    │    ├─ chdir 到 tex 文件目录
    │    │
    │    ├─ build_tex_cmd_sequence()
    │    │    ├─ manual_cmd_args? → 单条自定义命令
    │    │    ├─ tectonic? → 单条 tectonic 命令
    │    │    └─ 默认 → xelatex/pdflatex/...
    │    │         ├─ -shell-escape? (配置)
    │    │         ├─ -synctex=1? (参数)
    │    │         ├─ -interaction=nonstopmode
    │    │         ├─ -file-line-error
    │    │         └─ bib? → xelatex→bibtex→xelatex→xelatex
    │    │
    │    ├─ run_latex(sequence)
    │    │    └─ for each cmd:
    │    │         yield run_command(cmd)
    │    │         code != 0? → break & return error
    │    │
    │    └─ [latex_cleanup 上下文退出]
    │         └─ 删除非白名单扩展名的临时文件
    │
    ├─ 200 OK: "LaTeX compiled"
    │
    └─ 500 ERROR: {fullMessage, errorOnlyMessage}
```

## 多文件项目支持

虽然当前编译直接对单个 `.tex` 文件执行，但以下机制支持多文件项目：

1. **`\input`/`\include`**：LaTeX 引擎本身支持在子文件中引用主文件中的宏包和定义，只要所有文件在同一目录树中
2. **BibTeX 自动检测**：即使主文件使用 `\input{subfile}` 包含的子文件中有 `\bibliography`，检测会扫描主文件内容
3. **路径处理**：编译在 `.tex` 文件所在目录执行，因此相对路径的图片/数据文件可以正常工作

注意：如果使用 `\input{../subdir/chapter.tex}` 引用上级目录的文件，可能需要配置 LaTeX 的 `\graphicspath` 或调整目录结构。

## 编译性能建议

| 建议 | 原因 |
|------|------|
| 大文档使用 Tectonic | Tectonic 自动缓存依赖且只编译一次，速度优于多轮 xelatex |
| 启用 `-shell-escape` 仅在必要时 | `shell_escape` 允许 LaTeX 执行外部命令，有安全风险 |
| 将图片放于子目录 | 避免临时文件扫描误删图片（白名单包含常见图片格式，但子目录中的文件不受清理影响） |
| 使用 `manual_cmd_args` 自定义 | 高级用户可配置 latexmk 等工具获得更智能的增量编译 |

---

**下一步阅读：**
- [PDF 查看器](04-pdf-viewer.md) — 编译成功后的 PDF 渲染与交互
- [SyncTeX 双向同步](05-synctex-sync.md) — 编辑器与 PDF 之间的精确跳转
- [配置指南](../examples/03-configuration.md) — 如何自定义编译引擎和参数
