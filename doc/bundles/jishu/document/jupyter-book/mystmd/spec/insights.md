# MySTmd 核心引擎架构洞察

> I阶段产出：核心洞察四元组（陈述/证据/反常识/行动）+ 知识地图

## 洞察1：两阶段解析架构——markdown-it 分词器 + 栈式 MDAST 构建器

**陈述**：myst-parser 不使用 micromark/unified 的 parser 链，而是将 markdown-it 作为底层分词器（tokenizer），通过自定义 `MarkdownParseState` 栈式状态机将 markdown-it Token 流转换为 MDAST（Markdown Abstract Syntax Tree）。Token→MDAST 节点的映射通过声明式的 `TokenHandlerSpec` 表驱动。

**证据**：
- F-007/F-010：`createTokenizer` 创建 MarkdownIt 实例，配置插件链，`mystParse` 调用 `tokenizer.parse(content, {vfile})` 再调用 `tokensToMyst`
- F-014~F-022：MarkdownParseState 使用 stack 维护节点嵌套关系，openNode 压栈、closeNode 弹栈、addNode 添加子节点
- F-024~F-027：TokenHandlerSpec 是声明式映射表，getTokenHandlers 自动为 open/close token 对生成入栈/出栈 handler
- F-030：defaultMdast 表包含 40+ 个 token type 到 MDAST 节点的映射
- F-005：mystParser 作为 unified Plugin 暴露，但内部 Parser 直接委托给 mystParse，不走 unified parser pipeline

**反常识**：
- 与 remark/unified 生态的常见实践不同，mystmd 没有使用 micromark（CommonMark 分词器）+ mdast-util-from-markdown 的组合，而是复用 markdown-it（HTML 导向的 Markdown 解析器）作为分词层。这意味着 myst 的扩展语法（指令、角色、引用、数学公式）全部以 markdown-it 插件形式实现（F-010/F-044），而非 remark 插件。
- `MarkdownParseState` 的设计参考了 prosemirror-markdown，而非 unified 生态的任何库（F-014 注释 "Loosely based on prosemirror-markdown"）。
- `_lift` 和 `_remove` 是特殊的伪节点类型：`_lift` 在 tokensToMyst 后处理中提升子节点（如 thead/tbody 不产生 AST 节点，直接将 tableRow 提升到 table），`_remove` 则删除节点（如 footnote_anchor）（F-029）。

**行动**：
- 自定义 Token 映射时，在 MdastOptions.handlers 中添加 TokenHandlerSpec，无需修改核心解析器
- 指令/角色的 markdown-it 插件（rolePlugin/directivePlugin 等）产生 parsed_directive/parsed_role 等中间 token，由 defaultMdast 映射为 mystDirective/mystRole 节点，再由 applyDirectives/applyRoles 二次处理
- 解析嵌套内容时，通过 DirectiveContext.parseMyst 回调递归调用 mystParse

## 洞察2：指令与角色的两阶段处理——原始 AST 节点到语义 AST 节点

**陈述**：markdown-it 插件（rolePlugin/directivePlugin）将 `{role}`text`{role}` 和 ``` ```{directive} ``` 语法解析为 mystRole/mystDirective 原始节点（带有 `processed: false` 标记），之后 `applyDirectives`/`applyRoles` 函数通过 DirectiveSpec/ RoleSpec 查表找到对应实现，提取 arg/options/body，执行 validate 和 run 方法，用 run 返回的 GenericNode[] 替换原始节点的 children。

**证据**：
- F-038~F-041：applyDirectives 查找 mystDirective[processed=false] 节点，通过 specLookup 匹配 DirectiveSpec，解析 arg/options/body，调用 run(data, vfile, ctx) 替换 children
- F-042~F-043：applyRoles 同理，但 run 签名无 ctx 参数
- F-056/F-057：DirectiveSpec.run 签名 `(data, vfile, ctx) => GenericNode[]`，RoleSpec.run 签名 `(data, vfile) => GenericNode[]`
- F-081：basicTransformations 的第一步是 liftMystDirectivesAndRolesTransform，将指令/角色节点从 AST 中提升（liftChildren），将目标属性转移给首个子节点

**反常识**：
- mystDirective/mystRole 是"临时"节点类型——它们只在 parse 阶段存在于 AST 中，经过 liftMystDirectivesAndRolesTransform 后被 liftChildren 移除。最终渲染的 AST 中不包含这两种节点类型。
- 未知指令不会导致解析失败，而是 fileError 并将 options 折叠回 value 字段，删除 children（F-039："We probably want to do something better than just delete the children... but for now this gets myst-spec tests passing"）。
- 指令体如果 body.type !== 'myst'（如 code 类型），子节点会被 markChildrenAsProcessed 标记为已处理，避免后续递归解析报错。
- 指令的 parseMyst 回调会自动修正位置偏移（offset + node.position.start.line），使嵌套解析的节点位置对应全局行号（F-008/F-041）。

**行动**：
- 自定义指令实现 DirectiveSpec 接口：name（必填）、arg/options/body（定义 schema）、validate（可选校验）、run（返回 AST 节点数组）
- 自定义角色实现 RoleSpec 接口：name、body/options、validate、run（无 ctx 参数）
- 通过 mystParse 的 options.directives/options.roles 数组传入自定义指令/角色，与默认指令/角色合并
- 插件包可通过 MystPlugin 类型导出 directives/roles/transforms 数组

## 洞察3：转换管线的有序组合——basicTransformations 作为标准处理序列

**陈述**：myst-transforms 包导出 30+ 个独立的 transform 插件，每个插件遵循 unified Plugin 接口。`basicTransformations` 函数按严格顺序组合 22 个核心 transform，形成单文档的标准 MDAST 处理管线。Transform 间存在隐式顺序依赖（注释中标注了 ordering 要求）。

**证据**：
- F-075~F-078：myst-transforms 导出 30+ transform，每个都有 XxxTransform 函数和 XxxPlugin（unified Plugin 包装）两种形式
- F-079~F-080：basicTransformations 按序执行 22 个 transform，basicTransformationsPlugin 是其 unified Plugin 包装
- F-079 注释明确标注了顺序依赖：如 "lifting roles and directives must happen before the mystTarget transformation"、"Target transformation must happen after lifting the directives, and before the heading labels"、"Must be before header transforms"、"This should be before block nesting"
- F-081：liftMystDirectivesAndRoles 是管线第一步，在 mystTargets 之前执行

**反常识**：
- Transform 的执行顺序至关重要但完全是手动管理的——没有声明式的依赖图或拓扑排序，basicTransformations 中的顺序注释是唯一文档。调换两个 transform 的顺序可能产生微妙 bug（如标题标签重复、目标解析错误）。
- 很多 transform 是"破坏性"的：它们直接修改树结构（liftChildren、remove、节点类型替换），而非返回新树。这意味着 transform 不是纯函数，多次应用同一 transform 可能产生不同结果。
- myst-transforms 同时导出函数形式（直接操作 tree）和 Plugin 形式（unified 插件包装），允许在 unified pipeline 外直接调用 transform 函数。
- basicTransformations 只覆盖单文档处理，跨文档的引用解析（enumerateTargets/resolveReferences）是独立的 project 阶段 transform（TransformSpec.stage: 'project'）。

**行动**：
- 标准处理管线使用 basicTransformationsPlugin，不要自行组合基础 transform
- 自定义 transform 添加到 basicTransformations 之后执行
- project 阶段 transform（引用解析、目录生成等）在所有文档完成 basicTransformations 后执行
- 编写 transform 时参考现有 transform 的 Plugin/Transform 双模式导出模式

## 洞察4：以 GenericNode 为核心的松散类型系统

**陈述**：myst-common 定义了 GenericNode/GenericParent 作为基础节点类型（type+children+value+identifier+label+position），所有具体节点类型（来自 myst-spec）通过交叉类型 `GenericNode<T>` 扩展。DirectiveSpec/ RoleSpec/TransformSpec/MystPlugin 构成插件接口契约。类型系统在运行时不做校验，全部依赖 TypeScript 编译期检查。

**证据**：
- F-046~F-047：GenericNode 是 `{type, kind?, children?, value?, identifier?, label?, position?} & T`，GenericParent 强制要求 children
- F-056~F-060：DirectiveSpec/RoleSpec/TransformSpec/MystPlugin 构成完整的插件接口体系
- F-095~F-101：myst-spec 定义了 50+ 具体节点类型，但它们都是 interface/type alias，运行时无反射能力
- F-073~F-074：RuleId 枚举为 80+ 种校验规则提供唯一标识，每个规则有对应的 RULE_ID_DESCRIPTIONS
- F-105~F-112：simple-validators 提供运行时校验原语（validateBoolean/String/Number/Object/List/Enum/Date/Url/Email 等）

**反常识**：
- myst-spec 的节点类型定义与实际运行时 AST 节点之间没有运行时校验——不存在 Zod/Joi 式的 schema validator，TypeScript 类型在编译后完全擦除。节点结构正确性依赖于 parser 和 transforms 的正确实现。
- myst-spec-ext 包完全是 myst-spec 的 deprecated 别名导出（F-103~F-104），这是为了向后兼容保留的包，本身无新逻辑。
- simple-validators 不是用于 AST 节点校验，而是用于配置文件（myst.yml）和 frontmatter 的运行时校验。
- RuleId 枚举将构建/导出/解析/校验等所有阶段的错误码统一到一个命名空间，每个错误通过 fileError/fileWarn 上报到 VFile。

**行动**：
- 使用 GenericNode/GenericParent 作为遍历/操作 AST 的基础类型，必要时用类型断言收窄
- 自定义插件遵循 MystPlugin 接口：导出 directives/roles/transforms 数组
- 校验配置和 frontmatter 时使用 simple-validators 的 validateXxx 函数
- 错误报告使用 fileError/fileWarn 并传入 RuleId，便于用户通过 error_rules 配置调整严重级别

## 洞察5：配置系统的分层设计——project/site 双配置 + error_rules 错误治理

**陈述**：myst-config 将配置分为 ProjectConfig（项目级，扩展 ProjectFrontmatter）和 SiteConfig（站点级，扩展 SiteFrontmatter），通过 Config 类型组合。支持 extend 数组继承配置，error_rules 允许按规则 ID 覆盖严重级别（ignore/warn/error）。插件通过 PluginInfo 声明，区分 javascript 和 executable 类型。

**证据**：
- F-084~F-085：Config = {version:1, extend?, project?: ProjectConfig, site?: SiteConfig}
- F-085/F-086：ProjectConfig 扩展 ProjectFrontmatter，添加 remote/index/exclude/plugins/error_rules
- F-088~F-091：SiteConfig 扩展 SiteFrontmatter，添加 projects（deprecated）/nav/actions/domains/template
- F-092：ErrorRule = {id: string, severity: 'ignore'|'warn'|'error', key?: string}
- F-094：myst-frontmatter 导出 20+ 个 frontmatter 子模块（affiliations/biblio/contributors/downloads/exports/funding/jupytext/kernelspec/licenses/numbering/page/project/references/settings/site/socials/thebe/utils/venues/math/execute）

**反常识**：
- SiteConfig 中的 projects 字段已 deprecated（F-088/F-091 注释："Multiple projects per site is deprecated; a site maps 1:1 to a project"），但类型定义中仍保留。这反映了从多项目站点到单项目站点的架构演进。
- error_rules 不是黑名单/白名单模式，而是基于 RuleId 的精细粒度控制——每个 80+ 种错误码都可以单独设置为 ignore/warn/error（F-092）。
- myst-frontmatter 有 20+ 个子模块但入口统一导出，每个子模块（如 affiliations/contributors/exports）负责各自 frontmatter 字段的解析和校验。
- myst-config 和 myst-frontmatter 是两个独立包：myst-frontmatter 定义纯数据类型（PageFrontmatter/ProjectFrontmatter/SiteFrontmatter），myst-config 定义包含构建行为的配置类型（plugins/error_rules/nav/actions）。

**行动**：
- 项目配置放在 project 字段，站点导航/主题/域名放在 site 字段
- 需要忽略特定警告时，在 error_rules 中按 RuleId 设置 severity: 'ignore'
- 自定义插件通过 project.plugins 注册，type 指定 javascript/executable
- 多项目配置复用使用 extend 数组

## 知识地图

### 文档分组与学习路径

```
入门路径：
  00-overview.md          → 01-unified-plugin-architecture.md → 02-myst-parser.md
  （MySTmd整体架构）         （unified/插件体系基础）              （解析器：tokenizer→MDAST）

核心概念：
  03-myst-transforms.md   → 04-myst-common-types.md    → 05-myst-config.md
  （30+转换管线）            （GenericNode/DirectiveSpec）（配置系统project/site）

  06-myst-frontmatter.md  → 07-myst-spec.md           → 08-simple-validators.md
  （20+frontmatter模块）    （AST节点类型规范）           （运行时验证器）

高级/周边：
  09-citation-js-utils.md → 10-markdown-it-myst.md → 11-mystmd-py-python-binding.md
  （引用处理Citation.js）    （markdown-it兼容层）      （Python绑定）

  12-myst-transform-basic.md
  （basicTransformations复合插件详解）
```

### 概念文档覆盖事实映射

| 文档 | 覆盖事实 |
|------|---------|
| 00-overview | F-001~F-004, F-145~F-148 |
| 01-unified-plugin-architecture | F-058, F-059, F-075~F-080 |
| 02-myst-parser | F-005~F-045, F-145 |
| 03-myst-transforms | F-075~F-083, F-146 |
| 04-myst-common-types | F-046~F-074 |
| 05-myst-config | F-084~F-093 |
| 06-myst-frontmatter | F-094 |
| 07-myst-spec | F-095~F-102 |
| 08-simple-validators | F-105~F-112 |
| 09-citation-js-utils | F-127~F-138 |
| 10-markdown-it-myst | F-125~F-126, F-010, F-044 |
| 11-mystmd-py-python-binding | （Python绑定包） |
| 12-myst-transform-basic | F-079~F-081 |

### 示例文档规划

| 示例 | 对应概念 |
|------|---------|
| 01-parse-markdown | mystParse API（F-007~F-009） |
| 02-custom-transform | TransformSpec 编写（F-058） |
| 03-configure-project | ProjectConfig/SiteConfig（F-084~F-092） |
| 04-parse-frontmatter | getFrontmatter（F-082~F-083） |
| 05-custom-directive | DirectiveSpec 编写（F-056, F-038~F-041） |

### references信源文件

| 信源文件 | 对应源码 | 覆盖事实 |
|---------|---------|---------|
| myst-parser-source.md | myst-parser/src/ (myst.ts, fromMarkdown.ts, tokensToMyst.ts, directives.ts, roles.ts, plugins.ts, config.ts) | F-005~F-045 |
| myst-transforms-source.md | myst-transforms/src/ (index.ts, basic.ts, liftMystDirectivesAndRoles.ts, frontmatter.ts) | F-075~F-083 |
| myst-common-source.md | myst-common/src/ (index.ts, types.ts, ruleids.ts, utils.ts) | F-046~F-074 |
| myst-config-source.md | myst-config/src/ (index.ts, project/types.ts, site/types.ts, errorRules/types.ts) | F-084~F-093 |
| myst-frontmatter-source.md | myst-frontmatter/src/index.ts | F-094 |
| myst-spec-source.md | myst-spec/src/ (index.ts, ext.ts), myst-spec-ext/src/index.ts | F-095~F-104 |
| simple-validators-source.md | simple-validators/src/ (index.ts, validators.ts, types.ts) | F-105~F-112 |
| mystmd-cli-source.md | mystmd/src/ (index.ts, build.ts), citation-js-utils/src/index.ts, markdown-it-myst/src/index.ts | F-113~F-144, F-125~F-138 |
