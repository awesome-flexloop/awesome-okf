---
type: Concept
title: 四阶段处理管线
description: 读取→执行→转换→渲染四阶段处理流程，每个阶段的核心组件与扩展点
tags: [myst-nb, pipeline, architecture, execute, render]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 四阶段处理管线

MyST-NB 的文档处理是一个四阶段管线：**读取 → 执行 → 转换 → 渲染**。这比 MyST-Parser 的三阶段（解析→Token→渲染）多了关键的「执行」阶段。

## 管线总览

```
┌─────────────────────────────────────────────────────────┐
│                     输入文件                             │
│  .ipynb (JSON Notebook)  /  .md (mystnb 文本格式)        │
│  /  .Rmd (自定义格式)  /  ...                           │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│ 1. 读取层 (core/read.py)                                 │
│    ┌─────────────────────────────────────────────────┐  │
│    │ create_nb_reader() → NbReader                   │  │
│    │   ├─ standard_nb_read() → .ipynb               │  │
│    │   ├─ read_myst_markdown_notebook() → .md       │  │
│    │   └─ nb_custom_formats → 自定义后缀             │  │
│    └─────────────────────────────────────────────────┘  │
│ 输出：NotebookNode (nbformat v4)                          │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 执行层 (core/execute/)                                │
│    ┌─────────────────────────────────────────────────┐  │
│    │ create_client() → NotebookClientBase            │  │
│    │   ├─ off/auto(完整) → NotebookClientBase        │  │
│    │   ├─ auto/force → NotebookClientDirect (nbclient)│  │
│    │   ├─ cache → NotebookClientCache (jupyter-cache)│  │
│    │   └─ inline → NotebookClientInline (eval)       │  │
│    └─────────────────────────────────────────────────┘  │
│ 输出：已执行的 NotebookNode（outputs 已填充）              │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│ 3. 转换层 (core/nb_to_tokens.py)                         │
│    ┌─────────────────────────────────────────────────┐  │
│    │ notebook_to_tokens()                            │  │
│    │   ├─ Markdown cells → markdown-it Token         │  │
│    │   ├─ Code cell source → fence Token              │  │
│    │   ├─ Code cell outputs → render 调用             │  │
│    │   └─ 提取 glue 数据                              │  │
│    └─────────────────────────────────────────────────┘  │
│ 输出：markdown-it Token 流                                │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│ 4. 渲染层 (core/render.py)                               │
│    ┌─────────────────────────────────────────────────┐  │
│    │ NbElementRenderer + MditRenderMixin             │  │
│    │   ├─ MIME 优先级选择                             │  │
│    │   ├─ 文本输出 → Pygments 高亮                    │  │
│    │   ├─ 图片输出 → 文件保存 + image 节点            │  │
│    │   ├─ HTML 输出 → raw nodes                       │  │
│    │   ├─ Markdown 输出 → 递归解析                    │  │
│    │   ├─ Widget 输出 → JS 加载标记                   │  │
│    │   └─ 错误输出 → traceback 高亮                   │  │
│    └─────────────────────────────────────────────────┘  │
│ 输出：docutils AST 节点                                   │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
      Sphinx/Docutils 后处理 → 最终输出（HTML/LaTeX/...）
```

## 阶段 1：读取层

读取层负责将各种输入格式转换为统一的 `NotebookNode` 对象（nbformat v4 格式）。

**核心函数**：`create_nb_reader(path, md_config, nb_config, content)`

**工作流程**：
1. 遍历所有注册的 Reader（默认 `.ipynb` + `nb_custom_formats` 中注册的自定义格式）
2. 按后缀长度降序匹配文件路径，选择最合适的 Reader
3. 对于 `.md` 文件，特殊处理：检查 frontmatter 是否含 `file_format: mystnb` 或 jupytext myst 标记，只有匹配时才作为 notebook 处理
4. 文本格式的 `.md` 文件通过 `read_myst_markdown_notebook()` 解析，识别 `{code-cell}`、`{raw-cell}`、`+++` 分隔符

**扩展点**：
- `nb_custom_formats` 配置注册自定义文件后缀和读取函数
- `jcache.readers` entry point 注册 jupyter-cache 读取插件

## 阶段 2：执行层

执行层负责执行 notebook 中的代码 cell，填充 outputs。

**核心工厂**：`create_client(notebook, source, nb_config, logger)`

**执行客户端**：

| 客户端 | 触发模式 | 行为 |
|--------|---------|------|
| `NotebookClientBase` | `off` / `auto`（输出完整） | 不执行，直接返回 |
| `NotebookClientDirect` | `auto`（缺输出）/ `force` | 使用 nbclient 直接执行 notebook |
| `NotebookClientCache` | `cache` | 使用 jupyter-cache 缓存执行结果（相同代码不重复执行） |
| `NotebookClientInline` | `inline` | 启动持久 kernel 连接，用于 eval 内联求值 |

**执行流程**：
1. 检查排除模式（`execution_excludepatterns`），匹配则跳过
2. `auto` 模式检查所有代码 cell 是否已有输出，全部有则跳过
3. 根据模式创建对应客户端
4. 客户端执行 notebook，处理超时、错误、stderr 等
5. 返回执行结果（包含 execution_metadata）

**扩展点**：自定义执行客户端需继承 `NotebookClientBase`。

## 阶段 3：转换层

转换层将执行后的 NotebookNode 转换为 markdown-it Token 流，接入 MyST-Parser 的渲染管线。

**核心函数**：`notebook_to_tokens()`

**转换规则**：
- Markdown cells → 解析为 markdown-it Token（使用 MyST-Parser 的解析器）
- Code cell 源码 → 生成 fence 类型 Token（标记为 code-cell）
- Code cell 输出 → 委托给渲染层处理
- 在转换过程中提取 glue 数据（从 cell output 的 scrapbook 元数据中）

## 阶段 4：渲染层

渲染层将 code cell 输出（mimebundle）转换为 docutils 节点。

**核心类**：`NbElementRenderer`（通过 `myst_nb.renderers` entry point 加载）

**MIME 类型优先级**：每个 builder（html/latex/text）有不同的 MIME 优先级列表。`SelectMimeType` Post-Transform 在构建后期根据当前 builder 从 mimebundle 中选择最终渲染类型。

**渲染类型**：

| MIME 类型 | 渲染方式 |
|-----------|---------|
| text/plain | Pygments 高亮（myst-ansi lexer 处理 ANSI 颜色） |
| text/html | 作为 raw HTML 节点 |
| text/markdown | 递归解析为 Markdown（支持 commonmark/gfm/myst 格式） |
| text/latex | 作为数学节点 |
| image/png, image/jpeg, image/svg+xml | 保存到文件，生成 image/figure 节点 |
| application/vnd.jupyter.widget* | 标记需要加载 ipywidgets JS |
| error/traceback | Pygments 高亮（ipythontb lexer） |
| application/papermill.record+* | glue 数据，不直接渲染 |

**共享 Mixin**：`MditRenderMixin` 提供 Sphinx 和 Docutils 两种 Renderer 的共享渲染逻辑，包括 `nb_config`、`nb_client`、`nb_renderer` 属性访问和 `get_cell_level_config()` 方法。

**扩展点**：
- `myst_nb.renderers` entry point 注册自定义渲染器
- `myst_nb.mime_renderers` entry point 注册自定义 MIME 类型渲染插件

## Post-Transform 阶段

Sphinx 模式下，渲染后还有几个关键 Post-Transform：

1. **SelectMimeType**：根据 builder 从 mimebundle 中选择最终 MIME 类型
2. **ReplacePendingGlueReferences**：替换 pending 的 glue 引用为实际内容
3. **HideInputCells**：处理代码折叠/隐藏（remove-input、hide-input 等标签）

## 相关概念

- [执行模式与缓存](05-execution-modes.md)
- [渲染与 MIME 类型](06-render-and-mime.md)
- [Glue 变量粘贴](07-glue.md)
- [Eval 内联求值](08-eval.md)
- [配置系统](04-config-system.md)
