---
type: reference
title: LangChain 文档站事实采集
description: 从 docs 仓库源码提取的文档站结构、MDX 组织方式与构建管道事实
tags: [langchain, docs, mintlify, mdx, build-pipeline]
sources:
  - id: repo-root
    resource: /langchain-ai/docs
    title: langchain-ai/docs 仓库根目录
  - id: docs-json
    resource: /langchain-ai/docs/src/docs.json
    title: Mintlify 站点配置与导航
  - id: agents-md
    resource: /langchain-ai/docs/AGENTS.md
    title: 文档贡献指南
  - id: pyproject
    resource: /langchain-ai/docs/pyproject.toml
    title: Python 项目配置
  - id: makefile
    resource: /langchain-ai/docs/Makefile
    title: 构建命令入口
  - id: pipeline-cli
    resource: /langchain-ai/docs/pipeline/cli.py
    title: 构建管道 CLI
  - id: builder
    resource: /langchain-ai/docs/pipeline/core/builder.py
    title: 文档构建器
  - id: link-map
    resource: /langchain-ai/docs/pipeline/preprocessors/link_map.py
    title: API 交叉引用链接映射
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23
status: stable
---

# LangChain 文档站事实采集

## 仓库概览

1. 仓库路径：`d:/spaces/SpecWeave/external/libs/ai/langchain-ai/docs/`，Git 仓库 `langchain-ai/docs`。
2. 文档托管平台：Mintlify，主题 `aspen`，站点名 "Docs by LangChain"，线上地址 `https://docs.langchain.com`。
3. 仓库同时包含手写内容（`src/`）、Python 构建管道（`pipeline/`）、辅助脚本（`scripts/`）和 CI 配置（`.github/`）。
4. `build/` 目录是 Mintlify 构建输出，禁止手动编辑，通过 `make build` 或 `make dev` 重新生成。
5. 项目使用 `uv` 管理 Python 依赖（`pyproject.toml`），要求 Python `>=3.13.0,<4.0.0`。
6. npm 依赖极简：仅 `@langchain/docs-sandbox`（`package.json`），Mintlify CLI `mint` 需全局安装。

## src/ 目录结构

7. `src/` 是所有手写内容的根目录，核心配置文件为 `src/docs.json`（Mintlify 配置 + 导航）。
8. 首页为 `src/index.mdx`，使用 `mode: "custom"` 自定义布局，通过 `<CardGroup>`/`<Card>` 组件呈现 Build/Test/Deploy/Monitor 四大生命周期入口。
9. `src/langsmith/`：LangSmith 商业产品文档，扁平组织（无子目录，除 `fleet/` 和 `images/`），约 474 个 `.mdx` 文件。
10. `src/langsmith/fleet/`：LangSmith Fleet（无代码 Agent 平台）文档，约 25 个 `.mdx`，含独立 `index.mdx` 和 `changelog.mdx`。
11. `src/oss/`：开源框架文档，按产品和语言双维度组织，包含以下子目录：
    - `deepagents/`：Deep Agents 框架文档（36 个顶层 `.mdx` + `code/`、`frontend/`、`cli/` 子目录）
    - `langchain/`：LangChain 框架文档（32 个顶层 `.mdx`）
    - `langgraph/`：LangGraph 框架文档（约 30 个 `.mdx` + `errors/`、`frontend/` 子目录）
    - `python/integrations/`：Python 集成文档，按组件类型分目录（chat、embeddings、vectorstores、tools、retrievers、document_loaders 等）
    - `javascript/integrations/`：TypeScript/JavaScript 集成文档，结构与 Python 对应
    - `concepts/`：跨产品概念文档（context、memory、products、providers-and-models）
    - `contributing/`：贡献指南（documentation、code、integrations、publish 等）
    - `reference/`：API 参考入口页（链接到外部 `reference.langchain.com`）
    - `integrations/`：共享集成内容
    - `images/`：OSS 文档专用图片
12. `src/snippets/`：可复用 MDX 片段，约 1047 个 `.mdx` 文件，按产品分子目录（`langsmith/`、`oss/`、`code-samples/`）。
13. `src/code-samples/`：可执行代码示例（Python/TypeScript/Go），约 404 个源文件，通过 Bluehawk 风格的行标签提取为 MDX 片段。
14. `src/images/`：图片资源，含 `brand/`（Logo、favicon）、`providers/`（提供商图标，dark/light 双主题）。
15. `src/fonts/`：TWK Lausanne 字体文件（woff2 格式，7 个字重 × 正斜体）。
16. `src/.mintlify/skills/`：Mintlify AI 技能定义，为 LangChain、LangGraph、LangSmith 各提供一个 `SKILL.md`。
17. `src/.well-known/security.txt`：安全联系信息。

## docs.json 导航结构

18. `docs.json` 使用 Mintlify v2 导航格式，顶层 `navigation.products` 数组定义 4 个产品：Home、LangSmith、LangSmith Fleet、Open source。
19. Home 产品为单页（`index`），无标签页。
20. LangSmith 产品有 7 个标签页：Get started、Observability、Evaluation、Prompt engineering、Agent deployment、Platform setup、Reference。
21. Open source 产品有 2 个语言下拉菜单（Python、TypeScript），每个语言下共享 7 个同名标签页：Deep Agents、LangChain、LangGraph、Integrations、Learn、Reference、Contribute。
22. 导航支持嵌套层级：`tab` → `group` → `pages`，pages 中可嵌套 `{ group, pages }` 实现二级分组。
23. 集成页面通过组件目录下的 `index.mdx` 自注册，新建组件组时才需修改 `docs.json`。
24. 站点配置了 GTM（`GTM-MBBX68ST`）、canonical URL、Google Search Console 验证、自定义 CSS、ChatLangChain 嵌入脚本。
25. `contextual.options` 配置了 AI 助手入口：copy、view、llms.txt、ChatGPT、Claude、MCP、Cursor、VSCode。

## MDX frontmatter 规范

26. 每个 `.mdx` 文件必须包含 YAML frontmatter，至少有 `title` 和 `description` 字段。
27. `description` 字段禁止使用 Markdown 语法（链接、反引号、格式化），因为会破坏 SEO。
28. 集成页 description 有固定格式：`"Integrate with the ClassName type using LangChain Python."`。
29. 首页使用特殊 frontmatter：`title:`（空）、`sidebarTitle: Home`、`mode: "custom"`。
30. frontmatter 不包含 `type` 字段——Mintlify 不使用 OKF 的 type 概念。

## MDX 语法与组件

31. 使用 `:::python` / `:::js` 围栏标记语言特定内容，构建管道据此生成 Python 和 JavaScript 两个版本的页面。
32. 代码高亮使用行内注释：`[!code highlight]`、`[!code ++]`（新增）、`[!code --]`（删除）。
33. API 交叉引用使用 `@[ClassName]` 语法，由 `pipeline/preprocessors/link_map.py` 解析为 `reference.langchain.com` 的 URL。
34. `link_map.py` 维护 Python 和 JavaScript 两个 scope 的映射表，覆盖 langchain、langchain-core、langgraph、deepagents 等包的类和函数。
35. 内置组件包括：`<Tabs>`/`<Tab>`、`<Steps>`/`<Step>`、`<Accordion>`、`<CodeGroup>`、`<Card>`/`<CardGroup>`、`<Note>`/`<Tip>`/`<Warning>`/`<Info>`。
36. 图标统一使用 Tabler 图标库（`icon="home"`），不使用 FontAwesome；缺失图标可用 SVG 路径 `icon="/images/providers/name.svg"`。
37. Mermaid 图表要求使用 LangChain 品牌色板（process 蓝、trigger 绿、decision 紫、output 梅、alert 桃、neutral 灰蓝）。

## 代码片段复用机制

38. 可复用片段通过 ES import 语法引入：`import PascalCaseName from '/snippets/<product>/<name>.mdx';`，然后以 `<PascalCaseName />` 渲染。
39. 不使用 Mintlify 的 `<Snippet file="..." />` 组件，因为构建管道的 `_rewrite_snippet_imports_for_language` 只匹配 import 形式。
40. 构建管道将片段 import 重写为语言特定副本（`/snippets/python/...` 或 `/snippets/javascript/...`）。
41. `src/snippets/code-samples/` 下的片段按 `<topic>-<variant>-<lang>.mdx` 命名（如 `agents-intro-py.mdx`、`agents-intro-js.mdx`），由 `scripts/extract_code_snippets.py` 从 `src/code-samples/` 自动生成。
42. 代码片段提取使用 Bluehawk 兼容的行标签系统，`scripts/generate_code_snippet_mdx.py` 将提取结果转为 MDX。

## 构建管道（pipeline/）

43. `pipeline/` 是 Python 包，入口点 `docs = "pipeline.cli:main"`（在 `pyproject.toml` 的 `[project.scripts]` 中注册）。
44. CLI 提供 4 个子命令：`dev`（开发模式+文件监听）、`build`（构建）、`mv`（移动文件并更新交叉引用）、`migrate`（MkDocs 迁移）、`migrate-docusaurus`（Docusaurus 迁移）。
45. `pipeline/core/builder.py` 的 `DocumentationBuilder` 是核心构建器：
    - 清空 `build/` 目录后重新生成
    - 分别为 Python 和 JavaScript 生成两个版本（URL 前缀 `/python/` 和 `/javascript/`）
    - 复制 `.mdx`、`.md`、`.json`、图片、字体、CSS、JS 等 20+ 种扩展名
    - 通过 preprocessors 处理 MDX 内容
46. `pipeline/core/watcher.py` 提供开发模式文件监听。
47. `pipeline/preprocessors/` 包含两个预处理器：
    - `link_map.py`：解析 `@[ClassName]` 为 API 文档 URL
    - `utm_links.py`：为外部链接添加 UTM 参数
48. `pipeline/tools/` 包含：
    - `notebook/convert.py`：Jupyter notebook 转 Markdown
    - `docusaurus_parser.py`：Docusaurus 格式迁移
    - `parser.py`：MkDocs 到 Mintlify 的通用解析器
    - `links.py`：链接处理（去后缀、移动文件时更新链接）
    - `highlights.py`：代码高亮处理
    - `lexer.py`：词法分析
    - `partner_pkg_table.py`：合作伙伴包表格生成
49. `pipeline/commands/` 包含 `build.py` 和 `dev.py` 两个命令实现。

## Makefile 目标

50. `make dev`：启动开发模式（`npm install` + `uv run pipeline dev`）。
51. `make build`：构建文档（`npm install` + `uv run pipeline build`）。
52. `make export`：构建后用 `mint export` 导出离线 zip。
53. `make broken-links`：构建后运行 `mint broken-links`，通过 `scripts/filter_mint_broken_links.py` 过滤已知误报（OpenAPI 生成页、片段文件）。
54. `make lint_prose`：使用 Vale 检查散文风格（术语、em-dash 空格等），CI 必过。
55. `make lint`：ruff format/check + ty 类型检查 + codespell 拼写检查。
56. `make test`：运行 pytest（`--disable-socket --allow-unix-socket`）。
57. `make code-snippets`：从 `src/code-samples/` 提取代码片段生成 MDX。
58. `make test-code-samples`：执行代码示例验证正确性。
59. `make check-cross-refs`：检查所有 `@[ref]` 交叉引用是否在 `link_map.py` 中有定义。
60. `make install`：安装全部依赖（`uv sync --all-groups` + `npm install` + 全局安装 `mint@latest`）。

## 辅助脚本（scripts/）

61. `check_cross_refs.py`：验证 `@[ref]` 引用完整性。
62. `check_import_mappings.py` + `import_mappings.json`：检查导入映射一致性。
63. `check_llms_urls.py`：验证 llms.txt 中的 URL。
64. `check_pr_imports.py`：PR 中检查导入规范。
65. `extract_code_snippets.py`：从代码源文件提取带标签的代码片段。
66. `generate_code_snippet_mdx.py`：将提取的片段转为 MDX 文件。
67. `test_code_samples.py`：执行代码示例验证。
68. `update_mdx.py`：批量更新 MDX 文件。
69. `filter_mint_broken_links.py`：过滤 `mint broken-links` 的已知误报。
70. `assemble_changelog.py` + `audit_changelog_coverage.py`：changelog 组装与覆盖率审计。
71. `packages_yml_get_downloads.py`：从 `packages.yml` 获取包下载量（用于生成下载量表格片段）。
72. `sync_deepagents_signatures.py`：同步 Deep Agents 函数签名。
73. `process_langsmith_openapi.py`：处理 LangSmith OpenAPI 规范。
74. `convert_pip_to_codegroup.py`：将 pip 安装命令转换为 CodeGroup 组件。

## 质量保障与 CI

75. `.github/workflows/ci.yml`：主 CI 流水线。
76. `.github/workflows/_lint.yml`：lint 检查。
77. `.github/workflows/_test.yml`：测试。
78. `.github/workflows/_check-links.yml`：链接检查。
79. `.github/workflows/lint-prose.yml`：Vale 散文检查。
80. `.github/workflows/check-deprecated.yml`：检查弃用内容。
81. `.github/workflows/check-llms-urls.yml`：检查 llms.txt URL。
82. `.github/workflows/check-pr-imports.yml`：PR 导入检查。
83. `.github/workflows/publish.yml`：发布流程。
84. Vale 配置在 `.vale.ini`，自定义规则在 `.github/vale/styles/LangChain/`（But、They 等禁用词）。
85. `.markdownlint.json` 配置 Markdown lint 规则。
86. `.pre-commit-config.yaml` 配置 pre-commit 钩子。
87. `.codespellignore` 定义 codespell 忽略词。
88. 代码示例需要实际测试通过才能合入（`make test-code-samples`）。

## 文档规范要点

89. 风格指南遵循 Google Developer Documentation Style Guide。
90. 使用第二人称祈使句、主动语态、一般现在时。
91. 标题使用 sentence case，以主动动词开头（"Add a tool" 而非 "Adding a tool"）。
92. 禁止使用缩写（"do not" 而非 "don't"）、第一人称、将来时、H5/H6 标题。
93. 产品名大写（LangChain、LangGraph、LangSmith、Deep Agents、Fleet、Engine），普通名词小写。
94. 模型引用使用最新 GA 模型 ID，避免 preview/beta 标识符。
95. 版本新增功能使用 `<Note>` callout 注明最低版本要求。
96. 内部链接使用相对路径（不以 `/python/` 或 `/javascript/` 开头，由构建管道解析）。
97. 链接文本使用描述性文字（"[View the tracing docs]" 而非 "click here"）。
98. 新页面必须同时更新 `src/docs.json` 导航；新组必须包含 index 页。
99. AGENTS.md 和 CLAUDE.md 内容保持同步，四个派生文件（`.cursorrules`、`.cursor/rules/docs-style.mdc`、`.github/copilot-instructions.md`、`.github/instructions/docs-style.instructions.md`）需同步更新。
100. 仓库根目录有 `AGENTS.md`、`CLAUDE.md`、`IDE_SETUP.md`、`README.md`、`idea.md` 等指导文件。
