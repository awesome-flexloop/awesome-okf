# 信源登记簿

本目录登记本知识包所有内容据以派生的信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。信源先行是 source-code-to-okf-wiki 的核心原则——所有API描述、参数说明、流程解释均直接溯源至源码。

## 信源文件

* [源码索引](source-index.md) — Plugin Playground 源码路径、版本信息、8个核心模块（index.ts/loader.ts/transpiler.ts/resolver.ts/modules.ts/known-modules.ts/requirejs.ts/runtime-shared-modules.ts）的职责说明、公开API映射表、辅助工具函数清单。
* [PluginLoader 与 PluginTranspiler API](loader-transpiler-api.md) — PluginLoader 类完整构造器选项与方法签名（load/loadFile/_resolvePlugins/_resolvePluginTokens/_discoverSchema/_discoverDeclaredStyles）、PluginTranspiler 类 API、IPluginLoadResult/IResult/IOptions 接口定义、PluginLoadingError 错误类。
* [ImportResolver API](resolver-api.md) — ImportResolver 类完整构造器选项与公开方法（resolve/rollbackLocalStyleMutations/commitLocalStyleMutations）、四级解析策略链详解、CSS处理内部方法（_loadLocalStyle/_rewriteRelativeCssImports/_snapshotLocalStyle）、快照栈事务机制、静态方法（removeLocalStyles），以及相关模块导出函数（loadSharedScopeModule/loadInIsolated/RequireJSLoader/registerCoreKnownModules/discoverFederatedKnownModules）。

## 信源溯源说明

本知识包基于 plugin-playground 源码 `external/libs/jupyter/plugin-playground/src/` 目录的深度阅读生成。R阶段共提取215条编号事实（F-001~F-215），覆盖：

* 项目元数据与依赖（package.json）：F-001~F-015
* 类型定义（tokens.ts/content.ts 等）：F-016~F-045
* 转译器（transpiler.ts）：F-046~F-080
* 加载器（loader.ts）：F-081~F-130
* 解析器（resolver.ts）：F-131~F-175
* 模块注册（modules.ts/known-modules.ts）：F-176~F-195
* RequireJS隔离（requirejs.ts）：F-196~F-205
* 共享模块加载（runtime-shared-modules.ts）：F-206~F-215

所有API签名、参数名、返回类型、默认值均经过源码验证，禁止虚构API。

```{toctree}
:maxdepth: 7

loader-transpiler-api
resolver-api
source-index
```
