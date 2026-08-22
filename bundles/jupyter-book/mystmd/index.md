# mystmd：MyST Markdown 引擎核心

mystmd 是 MyST（Markedly Structured Text）生态的 TypeScript 引擎核心，提供 Markdown 解析（基于 markdown-it + micromark 风格插件）、MDAST 转换管线（30+ 个 transform 插件）、公共类型系统、配置加载、frontmatter 解析和多格式导出的底层基础设施。

## 架构核心

mystmd 采用 **解析→转换→导出** 三段式管线，基于 [unified](https://unifiedjs.com/) 生态：

1. **解析（myst-parser）**：markdown-it tokenizer + `tokensToMyst` 将 token 流转换为 MDAST 树，支持指令（directive）和角色（role）的递归解析
2. **转换（myst-transforms）**：30+ 个 unified 插件对 MDAST 树做语义增强（引用解析、编号、 admonition、数学公式、脚注、目录等）
3. **导出（myst-to-*）**：各格式序列化器将 MDAST 转换为 HTML/LaTeX/DOCX/JATS/Markdown/Typst

## 知识地图

```
mystmd
├── 解析层 ──────── myst-parser（markdown-it + tokensToMyst）
│   ├── 插件系统 ── frontmatter/footnote/math/citation/directive/role
│   ├── 指令处理 ── applyDirectives（递归 parseMyst）
│   └── 角色处理 ── applyRoles
├── 转换层 ──────── myst-transforms（30+ unified 插件）
│   ├── 基础转换 ── admonitions/blocks/code/containers/headings
│   ├── 引用系统 ── enumerate/targets/links/indices
│   ├── 学术排版 ── math/glossary/footnotes/abbreviations
│   └── 复合插件 ── basicTransformations（一键加载核心转换）
├── 类型与工具 ──── myst-common（GenericNode/DirectiveSpec/RoleSpec）
├── 配置系统 ────── myst-config（project/site/errorRules）
├── Frontmatter ─── myst-frontmatter（20+ 元数据模块）
├── 规范定义 ────── myst-spec / myst-spec-ext（AST 节点类型）
└── 主入口 ──────── mystmd（CLI: build/init/start/clean）
```

## 文档导航

### 入门示例
- [基本解析](examples/00-basic-parsing.md) — 使用 mystParse 解析 Markdown
- [自定义 Transform](examples/02-custom-transform.md) — 编写 MDAST 转换插件
- [参考文献引用](examples/03-citations-example.md) — Citation 处理
- [自定义角色](examples/04-custom-role.md) — 创建 Role
- [自定义指令](examples/05-custom-directive.md) — 创建 Directive

### 核心概念（按学习路径）
1. [整体架构](concepts/00-overview.md) — 包结构、数据流转、设计哲学
2. [unified 插件架构](concepts/01-unified-plugin-architecture.md) — markdown-it 插件 + unified 插件体系
3. [MyST 解析器](concepts/02-myst-parser.md) — tokenizer→tokensToMyst→MDAST
4. [MDAST 转换管线](concepts/03-myst-transforms.md) — 30+ transform 插件
5. [公共类型系统](concepts/04-myst-common-types.md) — GenericNode/DirectiveSpec/RoleSpec
6. [错误处理](concepts/05-error-handling.md) — VFile 消息和 RuleId
7. [指令与角色](concepts/06-directives-and-roles.md) — 扩展机制
8. [目标与引用](concepts/07-targets-references.md) — 交叉引用解析
9. [Frontmatter 元数据](concepts/08-frontmatter.md) — 20+ 元数据模块
10. [AST 节点类型](concepts/09-myst-spec-node-types.md) — myst-spec 节点定义
11. [配置系统](concepts/10-configuration-system.md) — project/site 配置
12. [CLI 工具链](concepts/11-cli-toolchain.md) — build/init/start/clean
13. [Citation 工具](concepts/12-citation-js-utils.md) — 参考文献处理

### 信源参考
- [myst-parser 源码](references/myst-parser-source.md)
- [myst-transforms 源码](references/myst-transforms-source.md)
- [myst-common 源码](references/myst-common-source.md)
- [myst-config 源码](references/myst-config-source.md)
- [myst-frontmatter 源码](references/myst-frontmatter-source.md)
- [myst-spec 源码](references/myst-spec-source.md)
- [simple-validators 源码](references/simple-validators-source.md)
- [mystmd CLI 源码](references/mystmd-cli-source.md)

### 规格说明
- [事实清单](spec/facts.md) — 148 条编号源码事实
- [架构洞察](spec/insights.md) — 5 个核心洞察与知识地图
