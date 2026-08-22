---
type: spec
title: MyST-NB 架构洞察（spec/insights.md）
description: MyST-NB 源码洞察记录
tags:
- myst-nb
- spec
- insights
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: myst-nb-source
  resource: /references/mystnb-source.md
  title: MyST-NB mystnb-source
- id: myst-nb-source-1
  resource: /references/notebook-cheatsheet.md
  title: MyST-NB notebook-cheatsheet
---

# MyST-NB 架构洞察（spec/insights.md）

> I 阶段产出：基于 [facts.md](facts.md) 的事实综合，提炼 MyST-NB 的核心架构模式、设计决策和知识地图。
> 每条洞察包含：洞察陈述、事实证据、行动指南。

---

## 洞察 1：四阶段 Notebook 处理管线

**陈述**：MyST-NB 的核心处理流程是四阶段管线——「读取 → 执行 → 转换 → 渲染」，而非 MyST-Parser 的三阶段管线。新增的「执行」阶段是 MyST-NB 区别于 MyST-Parser 的根本差异。

**事实证据**：
- 读取层：`core/read.py` 提供 `create_nb_reader()` 工厂函数，支持 .ipynb 和 .md（mystnb 格式）两种输入格式，以及自定义格式扩展
- 执行层：`core/execute/__init__.py` 的 `create_client()` 工厂根据 `execution_mode` 分发到 4 种客户端：Base（不执行）、Direct（直接执行）、Cache（缓存执行）、Inline（内联执行）
- 转换层：`core/nb_to_tokens.py` 的 `notebook_to_tokens()` 将执行后的 NotebookNode 转换为 markdown-it Token 流
- 渲染层：`core/render.py` 的 `NbElementRenderer` 通过 MIME 类型优先级选择输出格式，生成 docutils 节点

**设计意义**：四阶段管线实现了「读/执/转/渲」关注点分离，使得每个阶段都可以独立替换或扩展（如自定义 Reader、自定义执行客户端、自定义渲染插件）。

**行动指南**：
- 理解 MyST-NB 文档处理时，按「输入格式→执行模式→Token 转换→MIME 渲染」顺序排查问题
- 自定义扩展应在对应阶段插入（自定义 Reader 通过 nb_custom_formats，自定义 Renderer 通过 entry point）

---

## 洞察 2：双模式架构复用 MyST-Parser 基础设施

**陈述**：MyST-NB 延续了 MyST-Parser 的 Sphinx/Docutils 双模式设计，但采用 Mixin 模式（`MditRenderMixin`）实现代码复用，而非 MyST-Parser 的基类继承方案。

**事实证据**：
- `sphinx_.py L60`：Sphinx Parser 继承 `MystParser`（MyST-Parser 的 Sphinx 解析器）
- `docutils_.py L74`：Docutils Parser 继承 MyST-Parser 的 Docutils Parser
- `render.py L62`：`MditRenderMixin` 是共享渲染逻辑的 Mixin 类
- `docutils_.py L58-71`：Docutils 模式使用 `DocutilsApp` 模拟 Sphinx app，注册 roles/directives
- sphinx_setup() 先调用 `setup_myst_parser(app)` 初始化 MyST-Parser（sphinx_ext.py L49），再叠加 MyST-NB 配置

**设计意义**：
- Mixin 模式比基类继承更灵活——共享逻辑集中在 `MditRenderMixin`，SphinxRenderer 和 DocutilsRenderer 各自继承 MyST-Parser 对应类后混入即可
- `DocutilsApp` 轻量模拟类避免了 Docutils 模式对 Sphinx 的导入依赖
- MyST-Parser 初始化后叠加配置，确保 MyST 基础语法和 MyST-NB 扩展共存

**行动指南**：
- 编写 MyST-NB 自定义扩展时，同时实现 Sphinx 和 Docutils 两个加载函数（参考 glue/eval 的 load_*_sphinx 和 load_*_docutils）
- 共享渲染逻辑放在使用 MditRenderMixin 的方法中，平台特定逻辑放在各自的 Renderer 子类中

---

## 洞察 3：三层配置覆盖体系（全局→文件→Cell）

**陈述**：NbParserConfig 实现了全局配置、文件级 frontmatter、cell 级 metadata 的三层覆盖，优先级 cell > file > global > default。配置字段通过 metadata 中的 `sections` 标签标记适用范围。

**事实证据**：
- `config.py L590-644`：`get_cell_level_config()` 方法实现三级优先级查找
- Section 枚举定义 global_lvl/file_lvl/cell_lvl 三个级别（config.py L98-108）
- 字段 metadata 中的 `cell_key` 指定 cell metadata 中的键名（如 `remove_code_source` 的 cell_key 为字段名本身，`render_image_options` 的 cell_key 为 `"image"`）
- 文件级配置通过 myst_parser 的 `merge_file_level` 机制从 notebook metadata 中读取
- 旧版 `render` key 自动迁移到 `mystnb` key 并发弃用警告（config.py L611-622）

**设计意义**：三层覆盖使得同一配置项可以在不同粒度精确控制——全局统一设置，个别文件覆盖，单个 cell 微调。这对于 notebook 文档的细粒度控制（如隐藏某个 cell 的输出、为单个 cell 设置图片选项）至关重要。

**行动指南**：
- 全局统一设置放在 conf.py 的 `nb_*` 配置中
- 单个 notebook 的特殊设置放在 frontmatter 的 `mystnb:` 键下
- 单个 cell 的特殊设置放在 cell metadata 的 `mystnb:` 键下
- 注意 cell_key 不一定等于字段名（如图片选项在 cell metadata 中用 `mystnb.image` 而非 `mystnb.render_image_options`）

---

## 洞察 4：Glue/Eval 变量系统——文档与代码的数据桥梁

**陈述**：Glue 和 Eval 是 MyST-NB 独有的变量系统，实现了代码执行结果与文档正文的双向数据流通。Glue 是「代码→文档」的粘贴机制，Eval 是「文档→代码」的内联求值机制。

**事实证据**：
- Glue 机制：
  - `glue(name, variable, display)` 函数（ext/glue/__init__.py L63-84）：在代码 cell 中调用，通过 IPython display 机制将变量的 mimebundle 存入 cell 输出，带 scrapbook 元数据标记
  - GLUE_PREFIX = "application/papermill.record/"（ext/glue/__init__.py L20）：display=False 时使用此前缀，避免立即显示
  - Paste 指令/角色：{glue:any}/{glue:text}/{glue:md}/{glue:figure}/{glue:math} 多种渲染模式
  - NbGlueDomain：Sphinx Domain 实现跨页面 glue 数据共享
- Eval 机制：
  - `{eval}` 角色/指令：在文档正文中内联求值 kernel 变量
  - `eval_name_regex`：默认 `^[a-zA-Z_][a-zA-Z0-9_]*$`，限制可求值的变量名（安全考虑）
  - NotebookClientInline：inline 执行模式，维护持久 kernel 连接
- extract_glue_data()（ext/glue/__init__.py L87-107）：遍历 notebook cells 提取所有 glue 数据，检测重复 key 警告

**设计意义**：
- Glue 借鉴了 papermill 的 scrapbook 模式，允许在代码中「粘贴」变量，然后在文档任意位置（包括跨页面）引用
- Eval 实现了「内联代码」效果，类似 R Markdown 的 `` `r expr` ``，但通过 kernel 实时求值
- 两者结合实现了「计算→存储→引用」的完整数据叙事闭环

**行动指南**：
- 需要在文档中引用代码计算结果（数值、图表、公式）时使用 glue
- 需要在正文句子中嵌入动态计算值时使用 eval
- Glue 变量名全局唯一，跨 notebook 使用需注意 NbGlueDomain 的作用域

---

## 洞察 5：MIME 类型优先级与多输出渲染

**陈述**：MyST-NB 的输出渲染基于 MIME 类型优先级系统，每个 builder（html/latex/text）有不同的 MIME 优先级列表。代码 cell 的输出是一个 mimebundle（多格式数据包），渲染时根据当前 builder 选择优先级最高的可用 MIME 类型。

**事实证据**：
- `get_mime_priority()`（core/render.py）：根据 builder_name 返回 MIME 类型优先级列表
- `mime_priority_overrides` 配置：允许用户覆盖默认优先级（如强制 HTML builder 优先用 LaTeX 输出数学）
- `SelectMimeType` Post-Transform（sphinx_.py）：在 Sphinx 构建后期从 mimebundle 中选择最终 MIME 类型
- 内置 MIME 渲染器：文本（text/plain→ANSI高亮）、图片（image/png→保存文件+image节点）、HTML（text/html→raw节点）、Markdown（text/markdown→解析）、Widget（application/vnd.jupyter.widget*→JS加载）、错误（error/traceback→ipythontb高亮）
- 插件扩展：通过 `myst_nb.mime_renderers` entry point 注册自定义 MIME 渲染插件（ExampleMimeRenderPlugin 是示例）
- 渲染器本身也通过 entry point（`myst_nb.renderers`）加载，默认为 NbElementRenderer

**设计意义**：
- MIME 优先级系统与 Jupyter 前端的渲染逻辑一致，确保 notebook 在 Sphinx 中渲染效果与 Jupyter 中一致
- 多 builder 支持通过优先级切换实现：HTML builder 优先 text/html，LaTeX builder 优先 text/latex
- Entry point 插件机制允许第三方扩展自定义输出类型的渲染

**行动指南**：
- 自定义输出格式渲染时，注册 `myst_nb.mime_renderers` entry point
- 跨格式文档需要注意 MIME 优先级设置（如数学公式在 LaTeX 中应优先 text/latex）
- ipywidgets 输出需要加载 RequireJS 和 Jupyter Widgets JS，这些由 MyST-NB 自动处理

---

## 知识地图

```
MyST-NB 架构全景
├── 核心管线（core/）
│   ├── 读取层（read.py）
│   │   ├── .ipynb → standard_nb_read()
│   │   ├── .md（mystnb格式）→ read_myst_markdown_notebook()
│   │   └── 自定义格式 → nb_custom_formats + import_object
│   ├── 执行层（execute/）
│   │   ├── off/auto(已有输出) → NotebookClientBase
│   │   ├── auto/force → NotebookClientDirect（nbclient）
│   │   ├── cache → NotebookClientCache（jupyter-cache）
│   │   └── inline → NotebookClientInline（eval 用）
│   ├── 转换层（nb_to_tokens.py）
│   │   └── notebook_to_tokens() → markdown-it Token 流
│   ├── 渲染层（render.py）
│   │   ├── NbElementRenderer（entry point 加载）
│   │   ├── MIME 优先级选择（get_mime_priority）
│   │   └── MditRenderMixin（Sphinx/Docutils 共享）
│   ├── 配置（config.py）
│   │   └── NbParserConfig（三层覆盖：全局→文件→Cell）
│   ├── 日志（loggers.py）
│   ├── Lexer（lexers.py：ANSI/IPythonTB）
│   └── 变量（variables.py：eval/glue 共用）
├── Sphinx 集成（sphinx_.py + sphinx_ext.py）
│   ├── Parser（继承 MystParser）
│   ├── SphinxRenderer（混入 MditRenderMixin）
│   ├── Post-Transforms（SelectMimeType/HideInputCells/ReplacePendingGlueReferences）
│   ├── NbMetadataCollector（JS 资源收集）
│   └── HideCodeCellNode（可折叠代码块）
├── Docutils 独立模式（docutils_.py）
│   ├── Parser（继承 MystParser Docutils版）
│   ├── DocutilsApp（轻量 app 模拟）
│   └── CLI 命令（mystnb-docutils-*）
├── 扩展（ext/）
│   ├── glue/ → 变量粘贴（指令/角色/Domain/跨引用）
│   ├── eval/ → 内联变量求值（角色/指令）
│   ├── download.py → {nb-download} 角色
│   └── execution_tables.py → 执行统计表
├── CLI（cli.py）
│   ├── mystnb-quickstart → 项目模板生成
│   └── mystnb-to-jupyter → .md → .ipynb 转换
└── 静态资源（static/mystnb.css）
```
