# Plugin Playground 架构洞察 (Insights)

> I阶段产出：基于 facts.md 中215条事实提炼核心架构洞察，设计知识地图与文档清单。

## 核心洞察

### 洞察1：四级回退模块解析链

- **陈述**：ImportResolver.resolve() 实现了四层模块解析策略——runtime known module → federated extension → local file → CDN AMD module，每层失败后自动回退到下一层。
- **证据**：F-063, F-064, F-065, F-066, F-067
- **反常识**：初学者可能以为 import 只能加载已安装的npm包，实际上Plugin Playground支持相对路径本地文件（.ts/.tsx/.js/.css）动态转译加载，且CSS文件会被注入为<style>标签而非JS模块。
- **行动**：概念文档中需要专门解释模块解析顺序，并在示例中展示本地相对导入和CSS导入的用法。

### 洞察2：浏览器端TypeScript即时转译与AsyncFunction沙箱

- **陈述**：PluginTranspiler 使用 TypeScript Compiler API 在浏览器中实时将ES6+ TypeScript转译为CommonJS，再通过AsyncFunction构造函数创建沙箱执行环境，await所有require()调用。
- **证据**：F-023, F-024, F-027, F-028, F-047, F-049, F-050
- **反常识**：TypeScript转译不在构建时完成，而是在用户点击"Load"时实时在浏览器中完成；require()被_transformer改写为await require()，所有模块导入都是异步的。
- **行动**：概念文档需解释转译管道（三个Transformer的作用）和AsyncFunction沙箱机制，这是理解插件为何能在浏览器中"即写即运行"的关键。

### 洞察3：Proxy驱动的Token依赖注入映射

- **陈述**：_createTokenAwareModule 使用ES6 Proxy包装模块对象，当代码访问`import { INotebookTracker } from '@jupyterlab/notebook'`时，Proxy拦截属性访问并从tokenMap中查找对应的Token实例返回。
- **证据**：F-069, F-250~F-252（loader中_resolvePluginTokens）, F-286~F-288
- **反常识**：Token不是从模块中"导出"的，而是在PluginLoader._resolvePluginTokens中将requires数组中的字符串替换为Token对象，Proxy确保`import { TokenName } from 'package'`语法能正确工作。
- **行动**：需要单独的概念文档解释Token系统，包括字符串Token名到Token实例的映射机制，以及requires/optional/provides的工作原理。

### 洞察4：CSS样式的快照-提交-回滚事务机制

- **陈述**：ImportResolver为每个插件加载维护CSS样式快照栈，支持rollbackLocalStyleMutations()回滚和commitLocalStyleMutations()提交，插件卸载时样式可恢复到加载前状态。
- **证据**：F-077, F-079, F-080, F-081, F-082, F-659~F-673
- **反常识**：CSS不是通过shadow DOM隔离，而是通过全局<style>标签注入+快照回滚机制管理；多个插件加载同一CSS时维护版本栈，顶层插件卸载时恢复前一版本。
- **行动**：高级概念文档需要解释样式处理机制，包括相对路径CSS @import重写为Jupyter files/ URL的逻辑。

### 洞察5：双模式插件兼容与联邦扩展动态发现

- **陈述**：PluginLoader支持两种插件格式——新风格ES module default export（JupyterLab 4.x标准）和旧风格return object（RequireJS兼容），同时能从window._JUPYTERLAB和webpack shared scope动态发现已安装的联邦扩展。
- **证据**：F-046, F-048, F-065, F-107, F-108, F-130, F-136
- **反常识**：playground不仅能加载用户写的插件代码，还能动态发现并导入当前JupyterLab环境中已安装的其他federated extensions的Token和模块；CDN加载需要用户明确同意（安全策略）。
- **行动**：概念文档需区分两种插件编写风格，并解释如何引用其他已安装扩展的Token。

## 知识地图

### 学习路径设计

```
入门篇（新手必读）
├─ 00-introduction.md         → 什么是Plugin Playground，解决什么问题
├─ 01-architecture-overview.md → 整体架构：编辑器→转译器→加载器→解析器→JupyterLab
└─ 02-plugin-basics.md        → 插件结构：id/autoStart/requires/activate

核心篇（理解机制）
├─ 03-typescript-transpilation.md → 浏览器端TS转译管道与三个Transformer
├─ 04-module-resolution.md   → 四级模块解析链
├─ 05-plugin-loader.md       → PluginLoader加载流程
└─ 06-token-system.md        → Token依赖注入与Proxy映射

高级篇（深入特性）
├─ 07-federated-extensions.md → 联邦扩展发现与共享模块
├─ 08-style-handling.md      → CSS注入与快照事务
└─ 09-export-share.md        → 导出为zip/wheel、分享链接

示例篇（动手实践）
├─ 01-hello-world.md
├─ 02-token-injection.md
├─ 03-custom-command.md
└─ 04-local-import.md
```

### 文档依赖关系

- concepts/00~02 不依赖其他概念文档
- concepts/03~06 依赖 00~02
- concepts/07~09 依赖 03~06
- examples/* 依赖对应的 concepts/*

## 文档清单

### references/ (信源先行，第一批生成)

| 文件 | 类型 | 内容 |
|------|------|------|
| source-index.md | Reference | 核心源码模块索引、版本信息、文件路径映射 |
| loader-transpiler-api.md | Reference | PluginLoader/PluginTranspiler 公开API签名 |
| resolver-api.md | Reference | ImportResolver 公开API、模块解析策略 |

### concepts/ (分批生成，每批≤7)

**第一批：入门+核心基础（00-03）**

| 文件 | 类型 | 标题 | 覆盖事实 |
|------|------|------|---------|
| 00-introduction.md | Concept | Plugin Playground 简介 | F-001~F-009, F-010~F-011 |
| 01-architecture-overview.md | Concept | 整体架构与数据流 | F-040~F-059, F-060~F-085 |
| 02-plugin-basics.md | Concept | JupyterLab 插件基础结构 | F-210~F-215, F-029~F-030 |
| 03-typescript-transpilation.md | Concept | 浏览器端TypeScript转译机制 | F-020~F-030 |

**第二批：核心机制（04-06）**

| 文件 | 类型 | 标题 | 覆盖事实 |
|------|------|------|---------|
| 04-module-resolution.md | Concept | 模块解析系统 | F-060~F-085, F-090~F-095 |
| 05-plugin-loader.md | Concept | 插件加载流程 | F-040~F-059 |
| 06-token-system.md | Concept | Token依赖注入系统 | F-069, F-281~F-304 |

**第三批：高级特性（07-09）**

| 文件 | 类型 | 标题 | 覆盖事实 |
|------|------|------|---------|
| 07-federated-extensions.md | Concept | 联邦扩展与共享模块 | F-100~F-137 |
| 08-style-handling.md | Concept | 样式处理与CSS隔离 | F-098~F-119, F-583~F-692 |
| 09-export-share.md | Concept | 导出、分享与工具栏集成 | F-195~F-209 |

### examples/ (在concepts后生成)

| 文件 | 类型 | 标题 |
|------|------|------|
| 01-hello-world.md | Example | Hello World 插件 |
| 02-token-injection.md | Example | 使用Token注入依赖 |
| 03-custom-command.md | Example | 自定义命令与面板 |
| 04-local-import.md | Example | 本地文件相对导入 |

### index.md (最后生成)

- 根 index.md: 包含okf_version frontmatter
- concepts/index.md: 无frontmatter，列出所有概念文档
- examples/index.md: 无frontmatter，列出所有示例文档
- references/index.md: 无frontmatter，列出所有信源文档
