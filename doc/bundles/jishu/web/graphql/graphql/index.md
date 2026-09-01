---
type: bundle
title: GraphQL 核心规范与生态
okf_version: "0.2"
---

# GraphQL 核心知识库

本知识包是 [GraphQL](https://graphql.org/) 查询语言的系统化中文教程，基于官方规范（graphql-spec）7 个章节、AI WG MCP 服务器源码、语义内省 RFC 及官网生态信息，遵循 OKF v0.2 规范。内容覆盖从查询语言语法、Schema 类型系统、验证执行管线到响应序列化、内省系统与 AI 集成的完整知识体系，所有事实均溯源至编号信源。

## 入门篇（concepts/）

* [GraphQL 概览与五大设计原则](concepts/00-overview.md) — GraphQL 是什么、不是什么，五大设计原则（Product-centric / Hierarchical / Strong-typing / Client-specified queries / Introspective）如何塑造其查询语言与运行时，以及验证-执行-响应三阶段管线全局图与生态概览。
* [查询语言基础：文档、操作与选择集](concepts/01-query-language-basics.md) — GraphQL 查询语言的词法规则、Document 结构、OperationDefinition（query/mutation/subscription）、SelectionSet、Field、Arguments、Value 类型体系与 VariablesDefinition。
* [Schema 与类型系统入门](concepts/02-schema-and-types.md) — SchemaDefinition 的根操作类型配置、六种命名类型与两种包装类型概览、内建标量类型规范、Enum/FieldDefinition/InputValueDefinition 基础语法，以及类型引用与 Description 机制。
* [复合类型：对象、接口、联合与枚举](concepts/03-composite-types.md) — ObjectTypeDefinition 的字段/参数/接口实现、InterfaceTypeDefinition 的 implements 机制、UnionTypeDefinition 成员类型、EnumTypeDefinition 枚举值与指令、InputObjectTypeDefinition、@oneOf 指令、类型扩展以及抽象类型的 resolveType 机制。
* [指令、包装类型与输入系统](concepts/04-directives-and-wrapping-types.md) — ListType 与 NonNullType 包装语法、指令系统（@skip/@include/@deprecated/@specifiedBy/@oneOf）、自定义指令 DirectiveDefinition、指令位置分类、输入强制转换规则以及变量定义与类型兼容性。

## 核心篇（concepts/）

* [验证管线与规则体系](concepts/05-validation.md) — 验证在执行前进行，覆盖文档验证、字段验证（叶子字段/字段合并）、参数验证、片段验证（spread 可能性/环检测）、值验证、指令验证以及变量验证的 IsVariableUsageAllowed 类型兼容性算法。
* [执行引擎：字段解析与值完成](concepts/06-execution.md) — ExecuteRequest 入口、CoerceVariableValues、ExecuteOperation（query 并行/mutation 串行/subscription 事件流）、CollectFields/MergeSelectionSets、ExecuteField/ResolveFieldValue、CompleteValue 各分支以及 Non-Null 错误传播与 ResolveAbstractType。
* [响应格式、错误冒泡与序列化](concepts/07-response-and-errors.md) — 响应三种形态、data/errors/extensions 结构、request error 与 execution error 区别、错误对象格式（message/locations/path/extensions）、Non-Null 错误冒泡 path 规则、序列化原语与 JSON 映射、Appendix C 语法产生式汇总。
* [内省系统：GraphQL 的自描述机制](concepts/08-introspection.md) — 通过 __ 前缀保留名称、元字段（__typename/__type/__schema）和一组内省类型（__Schema/__Type/__Field/__InputValue/__EnumValue/__Directive 等）使类型系统自身可被查询，支撑工具生态并成为 AI agent 自动发现 API 能力的基础设施。

## 高级篇（concepts/）

* [片段、变量作用域与 Schema Coordinates](concepts/09-fragments-and-advanced-syntax.md) — FragmentDefinition/FragmentSpread/InlineFragment 的类型条件与 spread 可能性规则，变量定义作用域与 IsVariableUsageAllowed 兼容性检查，以及 Schema Coordinates 自包含坐标语法。
* [Python 生态：客户端与服务端实践](concepts/10-python-ecosystem.md) — Python GraphQL 生态全景：7 个客户端库与 6 个服务端库对比，graphql-core 作为底层实现的地位，以及基于 graphql-core 的测试服务器实现模式（Root 类、resolver 方法、make_handler）。
* [GraphQL 与 AI：MCP、语义内省与 Agent](concepts/11-graphql-and-ai.md) — GraphQL 在 AI 领域的定位、AI WG MCP 服务器架构（FastMCP、list_types/run_query 工具、OpenAIEmbedder+EmbeddingStore 语义索引）、语义内省 RFC（__search/__definitions/__SearchResult）、GraphQL vs REST 在 AI 场景对比及 MCP/RAG/Agents 三大用例。

## 实战示例（examples/）

* [基础查询与变更](examples/basic-query.md) — query/mutation/subscription 三类操作的语法与使用场景。
* [Schema 设计实战](examples/schema-design.md) — 接口/联合/枚举/分页等类型设计模式。
* [错误处理与 Non-Null 冒泡](examples/error-handling.md) — 错误对象构造、Non-Null 字段错误传播路径与 partial response 机制。
* [Python 服务端实战](examples/python-server.md) — 基于 graphql-core 构建 GraphQL 服务端的完整流程。

## 信源登记簿（references/）

* [规范 Section 1：Overview](references/spec-section-1-overview.md) — GraphQL 概览章节，涵盖五大设计原则与三阶段管线。
* [规范 Section 2：Language](references/spec-section-2-language.md) — 查询语言语法，Document/Operation/SelectionSet/Field/Value/Fragments。
* [规范 Section 3：Type System](references/spec-section-3-type-system.md) — 类型系统，Schema/Object/Interface/Union/Enum/InputObject/Directive/包装类型。
* [规范 Section 4：Introspection](references/spec-section-4-introspection.md) — 内省系统，__Schema/__Type/__Field 等内省类型与元字段。
* [规范 Section 5：Validation](references/spec-section-5-validation.md) — 验证规则，文档/字段/参数/片段/值/指令/变量验证。
* [规范 Section 6：Execution](references/spec-section-6-execution.md) — 执行算法，字段收集/解析/值完成/Non-Null 传播/抽象类型解析。
* [规范 Section 7：Response + Appendix C](references/spec-section-7-response.md) — 响应格式与错误处理，附语法产生式汇总。
* [AI WG MCP 服务器源码](references/mcp-server-source.md) — GraphQL AI WG 的 MCP 服务器实现，含 schema 索引器与语义嵌入。
* [语义内省 RFC](references/semantic-introspection-rfc.md) — __search/__definitions 语义内省提议，扩展 GraphQL 自描述能力。

## 信任与生命周期说明

* **status 判定依据**：全部 25 个内容文档（12 个概念 + 4 个示例 + 9 个信源登记）均 `status: stable`。内容基于 GraphQL 官方规范（October 2021 Working Draft）7 个章节、AI WG MCP 服务器源码及语义内省 RFC 的逐节阅读与事实提取（669 条编号事实 F-001~F-669），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-23`。GraphQL 规范自 October 2021 Working Draft 以来核心设计（类型系统/验证/执行/响应）保持稳定，AI 集成（MCP、语义内省）为活跃演进领域；该日期作为针对未来规范大版本或语义内省 RFC 正式落地的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 25 个内容文档（12 个概念 + 4 个示例 + 9 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
