---
type: reference
title: "LaTeX 编译处理器源码（jupyterlab_latex/build.py）"
description: "LatexBuildHandler 服务端处理器，负责 LaTeX 编译命令序列构建、BibTeX 自动检测、输出过滤、编译清理与错误返回"
tags: [build, latex, handler, tornado, bibtex, tectonic, cleanup, output-filter]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: build-py
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/build.py"
    title: "jupyterlab_latex/build.py"
---

# LaTeX 编译处理器源码（jupyterlab_latex/build.py）

本信源登记 `jupyterlab_latex/build.py`（约317行），这是服务端核心模块，包含 LaTeX 编译的 HTTP 处理器、编译命令序列构建、输出过滤和临时文件清理上下文管理器。

## 导出项

### latex_cleanup 上下文管理器

签名：`@contextmanager def latex_cleanup(cleanup=False, workdir='.', whitelist=None, greylist=None)`

功能：在指定工作目录执行 LaTeX 编译，完成后清理编译产生的临时文件。

**工作流程**：
1. 保存原始工作目录，`os.chdir` 到 workdir
2. 删除 greylist 中的文件（先删后重建），将其加入 keep_files
3. 记录编译前的文件列表（`before = set(glob.glob("*"))`）
4. `yield` 执行编译
5. 如果 cleanup=True：
   - 记录编译后文件列表
   - 删除不在 keep_files（before ∪ whitelist ∪ greylist 残留）中的新文件
   - 文件直接 `os.remove`，目录 `shutil.rmtree`
6. `os.chdir` 回到原始目录

### LatexBuildHandler 类

继承自 `jupyter_server.base.handlers.APIHandler`，处理 GET `/latex/build/{path}` 请求。

#### initialize(root_dir)

设置 `self.root_dir` 为服务器根目录。

#### build_tex_cmd_sequence(tex_base_name)

构建 LaTeX 编译命令序列，返回 `list[tuple[str,...]]`。

**三种引擎模式**：

1. **manual_cmd_args 模式**（c.manual_cmd_args 非空时）：
   - 用户完全自定义命令行参数
   - 每个参数中的 `{filename}` 占位符替换为 tex_base_name
   - 命令序列长度取决于 run_times

2. **Tectonic 模式**（engine_name == 'tectonic'）：
   ```python
   ('tectonic', '{base}.tex', '--outfmt=pdf', f'--synctex={1|0}')
   ```
   - 自动跳过 BibTeX（Tectonic 内置处理）

3. **TeX Live 模式**（默认，xelatex/pdflatex 等）：
   ```python
   (engine_name, escape_flag, '-interaction=nonstopmode', '-halt-on-error',
    '-file-line-error', f'-synctex={1|0}', '{base}')
   ```
   - escape_flag 由 shell_escape 配置决定：
     - `'allow'` → `'-shell-escape'`
     - `'disallow'` → `'-no-shell-escape'`
     - `'restricted'`（默认）→ `'-shell-restricted'`

**BibTeX 集成逻辑**：

当以下条件**都不满足**时运行 BibTeX：
- `c.disable_bibtex` 不为 True
- 不是 Tectonic 引擎
- 当前目录存在 `.bib` 文件（`bib_condition()` 检测）

BibTeX 命令序列：
```python
[full_latex_sequence,                          # 第一次编译
 (c.bib_command, f'{base}'),                   # bibtex
 full_latex_sequence,                          # 第二次编译（解析引用）
 full_latex_sequence]                          # 第三次编译（修正引用）
```

无 BibTeX 时：`command_sequence = [full_latex_sequence] * c.run_times`

#### bib_condition()

返回 `bool`，检测当前目录是否有 `.bib` 文件：
```python
return any([re.match(r'.*\.bib', x) for x in set(glob.glob("*"))])
```

#### filter_output(latex_output)

基于 texfot（Karl Berry 的公共领域 Perl 脚本）的三正则输出过滤器，过滤 LaTeX 编译输出中的噪音信息。

**三组正则**：

| 正则组 | 变量 | 匹配内容 | 处理方式 |
|--------|------|---------|---------|
| ignore | `ignore` | 已知噪音警告（字体警告、auxhook、fixltx2e、libpng 等） | 跳过（不输出） |
| next_line | `next_line` | 错误起始行（`file:line:`、`!`、`> `、pdfTeX warning、Runaway argument 等） | 输出本行 + 下一行 |
| show | `show` | 重要信息（Output written、Error/Warning、Citation undefined、Fatal error、Over/Underfull 等） | 输出本行 |

**状态机**：`print_next` 标志控制是否输出下一行。

#### run_latex(command_sequence)

`@gen.coroutine` 异步执行编译命令序列：

1. 遍历每个命令元组
2. 调用 `run_command(cmd)`（异步/自动根据平台选择）
3. 返回码非0时：
   - 设置 HTTP 500
   - 返回 JSON：`{'fullMessage': output, 'errorOnlyMessage': filter_output(output)}`
4. 全部成功返回 `"LaTeX compiled"`

#### get(path='')

`@web.authenticated` + `@gen.coroutine`，主请求处理器：

1. 拼接完整路径：`tex_file_path = os.path.join(root_dir, path.strip('/'))`
2. 提取 `tex_base_name` 和扩展名 `ext`
3. 路径验证：
   - 文件不存在 → 403
   - 扩展名不是 `.tex` → 400
4. 使用 `latex_cleanup` 上下文管理器：
   - workdir = .tex 文件所在目录
   - whitelist = `['{base}.pdf', '{base}.synctex.gz']`（保留编译产物）
   - greylist = `['{base}.aux']`（编译前删除）
   - cleanup 由配置决定
5. 构建命令序列并调用 `run_latex`
6. 返回结果
