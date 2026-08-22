# MySTmd 核心引擎源码信源索引

本目录登记 mystmd 各核心模块的源码位置与导出 API 清单，供 concepts 文档溯源引用。

| 信源文件 | 对应源码 | 覆盖API |
|---------|---------|---------|
| [myst-parser-source.md](myst-parser-source.md) | `myst-parser/src/` (myst.ts, fromMarkdown.ts, tokensToMyst.ts, directives.ts, roles.ts, plugins.ts, config.ts) | mystParse, mystParser, createTokenizer, MarkdownParseState, tokensToMyst, applyDirectives, applyRoles, TokenHandlerSpec |
| [myst-transforms-source.md](myst-transforms-source.md) | `myst-transforms/src/` (index.ts, basic.ts, liftMystDirectivesAndRoles.ts, frontmatter.ts) | 30+ transforms, basicTransformations, basicTransformationsPlugin, getFrontmatter |
| [myst-common-source.md](myst-common-source.md) | `myst-common/src/` (index.ts, types.ts, ruleids.ts, utils.ts) | GenericNode, GenericParent, DirectiveSpec, RoleSpec, TransformSpec, MystPlugin, RuleId, 工具函数 |
| [myst-config-source.md](myst-config-source.md) | `myst-config/src/` (index.ts, project/types.ts, site/types.ts, errorRules/types.ts) | Config, ProjectConfig, SiteConfig, ErrorRule, PluginInfo, SiteManifest |
| [myst-frontmatter-source.md](myst-frontmatter-source.md) | `myst-frontmatter/src/index.ts` | 20+ frontmatter 子模块导出 |
| [myst-spec-source.md](myst-spec-source.md) | `myst-spec/src/` (index.ts, ext.ts), `myst-spec-ext/src/index.ts` | 50+ AST 节点类型, SourceFileKind |
| [simple-validators-source.md](simple-validators-source.md) | `simple-validators/src/` (index.ts, validators.ts, types.ts) | validateBoolean, validateString, validateNumber, validateObject 等 20+ 验证函数 |
| [mystmd-cli-source.md](mystmd-cli-source.md) | `mystmd/src/` (index.ts, build.ts), `citation-js-utils/src/index.ts`, `markdown-it-myst/src/index.ts` | CLI命令, CitationRenderer, markdown-it-myst 插件导出 |
