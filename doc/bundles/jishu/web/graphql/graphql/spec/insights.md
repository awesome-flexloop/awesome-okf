# I 阶段：架构洞察与知识地图

> 基于 facts.md 中 F-001 ~ F-669 共 669 条事实提炼。
> 事实来源：GraphQL 规范 Section 1–7（434 条）、AI WG MCP 服务器源码+README（152 条）、语义内省 RFC（26 条）、官网生态信息（57 条）。

## 核心洞察

### 洞察 1：类型系统即契约——从文档到可执行规范

- **陈述**：GraphQL 的类型系统不是辅助文档，而是客户端与服务端之间可执行、可验证的契约；schema 定义了所有可能的数据形状与能力边界，查询必须在其上下文中验证通过才能执行。
- **证据**：F-007（强类型原则：请求在类型系统上下文中执行，工具可在执行前确保有效性）、F-098（SchemaDefinition 语法定义根操作类型）、F-249（验证确保请求在 schema 上下文中无歧义无错误）、F-309（只有通过所有验证规则的请求才应执行）、F-251（类型系统演进而导致的 breaking change 概念）
- **反常识**：初学者常把 schema 当作"数据模型文档"或"接口说明书"，但它实际上是运行时强制执行的契约——无效查询在执行前就被拒绝，字段选择、参数类型、变量兼容性都在开发时即可校验。schema 既是类型定义也是验证依据，还是内省查询的数据源，三位一体。
- **行动**：类型系统概念应前置到入门阶段，不应放到"高级主题"。schema 定义（F-098~F-109）、六种命名类型（F-112~F-191）、验证规则（F-249~F-302）应形成连续学习链。00 概览 → 02 类型入门 → 03 复合类型 → 04 指令与包装类型 → 05 验证，构成"契约建立→契约执行"的认知闭环。

### 洞察 2：查询即响应形状——分层同构原则

- **陈述**：GraphQL 查询本身是分层嵌套结构，响应数据的形状与查询选择集精确同构；字段别名直接映射为响应键，嵌套选择集递归生成嵌套对象，响应恰好包含客户端请求的内容。
- **证据**：F-006（Hierarchical 原则：请求形状与响应数据形状一致）、F-042（SelectionSet 由 Field/FragmentSpread/InlineFragment 组成）、F-336（操作递归收集并执行每个选定字段直到叶子）、F-347（ExecuteCollectedFields 按 responseName 存入 resultMap）、F-391（data 条目是操作执行结果，query 为 query root type 对象）、F-412（序列化 Map 应按字段请求顺序写入）
- **反常识**：初学者可能以为响应是服务端决定的固定结构（像 REST 那样），但实际上客户端通过选择集"塑造"响应——请求什么字段就得到什么字段，别名决定响应键名，嵌套深度决定响应嵌套。这不是"便利性"，而是 GraphQL 的核心设计原则（F-008 Client-specified response）。
- **行动**：选择集语法（01 文档）与字段执行算法（06 执行）应放在一起教学，建立"语法树→执行树→响应树"的同构心智模型。响应格式（07）不应作为独立知识点记忆，而应从执行流程自然推导。示例文档应直观展示查询与响应的形状对应关系。

### 洞察 3：验证→执行→响应——三阶段管线架构

- **陈述**：GraphQL 请求处理是严格分层的三阶段管线：验证（静态检查文档与 schema 的一致性）→执行（字段解析、参数强制转换、值完成）→响应（序列化与错误报告）；验证失败产生 request error（无 data），执行失败产生 execution error（部分 data）。
- **证据**：F-307（ExecuteRequest 流程：GetOperation → CoerceVariableValues → 按类型分派）、F-309（已知验证错误应在 response 中报告且请求必须不执行）、F-368（execution error 在特定 response position 引发，通过产生部分 data 来"处理"）、F-386（request error result 不得包含 data 条目）、F-395（request error 通常是客户端过错，execution error 通常是服务端过错）
- **反常识**：初学者常混淆"验证错误"和"执行错误"——前者导致整个请求无数据（语法错误、验证失败、变量强制转换失败），后者只影响出错字段并产生部分数据。同样是错误，响应结构截然不同：request error 无 `data` 键，execution error 有 `data` 键（可能为 null）。
- **行动**：三阶段管线应作为核心骨架贯穿所有核心篇文档。05 验证、06 执行、07 响应三个文档都应回溯到管线模型，明确各自处于哪个阶段、输入输出是什么、错误如何分类传播。00 概览文档应引入管线图作为全局导航。

### 洞察 4：Non-Null 错误冒泡——类型驱动的错误传播

- **陈述**：Non-Null 类型不仅是"字段不返回 null"的承诺，更是错误传播的控制机制；当 Non-Null 字段解析失败或强制转换为 null 时，null 沿响应树向上冒泡到第一个可为 null 的父位置，若整条路径均为 Non-Null 则整个 data 为 null。
- **证据**：F-199（Non-Null 类型结果强制转换为 null 必须引发 execution error）、F-349（Non-Null 位置引发 error 时错误传播到父位置，父位置可 null 则解析为 null，否则继续传播）、F-373（Non-Null response position 不能为 null，execution error 传播到父位置处理）、F-375（从请求根到错误源每个位置都是 Non-Null 时 data 为 null）、F-404（错误 path 应包含完整路径，即使该字段不在响应中）
- **反常识**：初学者常以为 Non-Null 只是"更严格的类型约束"，但它实际上改变了错误处理语义——一个深层叶子字段的错误可能因为 Non-Null 类型链而抹掉整个父对象，甚至导致全部数据为 null。Non-Null 越强，错误爆炸半径越大。这是 schema 设计中需要权衡的关键决策。
- **行动**：Non-Null 类型（04）必须与错误处理（07）交叉引用、一起教学。需要专门的示例文档（error-bubbling.md）用具体 schema 和查询展示冒泡链：从叶子字段错误 → 父 Non-Null 传播 → 可 null 位置停止。这是从"会写查询"到"能设计健壮 schema"的关键认知跃迁。

### 洞察 5：自描述内省——从工具生态到 AI 原生基础设施

- **陈述**：GraphQL 通过 `__schema`/`__type` 内省系统使类型系统自身可被 GraphQL 语言查询，这不仅支撑了 GraphiQL、代码生成等开发工具，更成为 AI agent 自动发现 API 能力的基础设施；语义内省 RFC（`__search`/`__definitions`）和 MCP 集成正在将内省从"结构查询"升级为"语义发现"。
- **证据**：F-009（Self-describing：类型系统可通过 GraphQL 语言本身查询）、F-223（`__schema` 和 `__type` 从 query 根类型访问）、F-462（MCP 服务器用 `get_introspection_query` 获取 schema 并转 SDL）、F-588（语义内省 RFC 提议 `__search` 端点实现自然语言能力发现）、F-656（AI agent 查询 `__schema` 即可了解可用数据，无需手写工具描述）、F-589（MCP 工具抽象与 GraphQL Query/Mutation 高度相似）
- **反常识**：初学者常把内省当作"高级调试功能"或"GraphiQL 的实现细节"，但它是 GraphQL 设计哲学的核心体现——自描述不是附加特性，而是工具生态（代码生成、验证、IDE 支持）和 AI 集成（MCP 服务器、agent 工具调用）的基石。没有内省就没有 GraphQL 的工具链优势。
- **行动**：内省（08）应定位为核心概念而非高级主题，放在核心篇而非高级篇。10 Python 生态应展示 graphql-core 的 `build_client_schema`/`get_introspection_query` 实践。11 GraphQL+AI 应从内省自然延伸：内省 → MCP 服务器自动生成工具定义 → 语义内省 `__search` 实现自然语言发现。官网生态信息（F-653~F-669）作为应用层佐证。

## 知识地图

### 学习路径

整体采用"入门建立心智模型 → 核心掌握管线机制 → 高级拓展生态视野"的三阶段递进路径：

**入门篇（00→01→02）**：从 00 概览建立五大设计原则和三阶段管线全局认知；01 学习查询语言基础语法（文档、操作、选择集、值、变量），能读写简单查询；02 学习 schema 与标量/枚举类型，理解类型系统如何定义契约。01 和 02 可并行阅读，但都依赖 00。

**核心篇（03→04→05→06→07）**：03 在 02 基础上深入复合类型（对象、接口、联合）；04 学习指令、包装类型（List/Non-Null）和输入对象；05 系统学习验证规则（依赖 01~04 的语法和类型知识）；06 学习执行引擎算法（依赖 05 理解验证前置）；07 学习响应格式与错误冒泡（依赖 06，特别关联 04 的 Non-Null）。08 内省可在 04 之后阅读，作为类型系统的"镜像"。

**高级篇（09→10→11）**：09 深入片段、变量作用域、Schema Coordinates 等高级语法（依赖 01 和 03）；10 Python 生态实践（依赖 06~08，展示规范的具体实现）；11 GraphQL+AI（依赖 08 内省和 10 Python 实践，延伸到 MCP 和语义内省前沿）。

```
00 概览
├── 01 查询语言基础 ──────────┐
│   └── 09 片段与高级语法     │
└── 02 Schema与类型入门       │
    ├── 03 复合类型 ──────────┤
    │   └── 08 内省系统       │
    └── 04 指令与包装类型 ────┤
        └── 05 验证管线       │
            └── 06 执行引擎   │
                └── 07 响应与错误
                    ├── 10 Python生态
                    └── 11 GraphQL与AI
```

### 概念文档清单（concepts/）

| 编号 | 文件名 | 标题 | 覆盖事实 | 依赖 |
|---|---|---|---|---|
| 00 | 00-overview.md | GraphQL 概览与五大设计原则 | F-001~F-010, F-613~F-624 | 无 |
| 01 | 01-query-language-basics.md | 查询语言基础：文档、操作与选择集 | F-011~F-044, F-056~F-083 | 00 |
| 02 | 02-schema-and-types.md | Schema 与类型系统入门 | F-094~F-137 | 00 |
| 03 | 03-composite-types.md | 复合类型：对象、接口、联合与枚举 | F-138~F-194 | 02 |
| 04 | 04-directives-and-wrapping-types.md | 指令、包装类型与输入系统 | F-195~F-218 | 03 |
| 05 | 05-validation.md | 验证管线与规则体系 | F-249~F-302 | 01, 03, 04 |
| 06 | 06-execution.md | 执行引擎：字段解析与值完成 | F-303~F-375 | 05 |
| 07 | 07-response-and-errors.md | 响应格式、错误冒泡与序列化 | F-376~F-434 | 06 |
| 08 | 08-introspection.md | 内省系统：GraphQL 的自描述机制 | F-219~F-248 | 02, 04 |
| 09 | 09-fragments-and-advanced-syntax.md | 片段、变量作用域与 Schema Coordinates | F-045~F-055, F-084~F-093 | 01, 03 |
| 10 | 10-python-ecosystem.md | Python 生态：graphql-core 与服务端实践 | F-437, F-482~F-484, F-495, F-561~F-573, F-625~F-637 | 06, 07, 08 |
| 11 | 11-graphql-and-ai.md | GraphQL 与 AI：MCP、语义内省与 Agent | F-435~F-586, F-587~F-612, F-653~F-669 | 08, 10 |

**Section 覆盖检查**：

| 规范章节 | 覆盖文档 |
|---|---|
| Section 1 — Overview | 00 |
| Section 2 — Language | 01（操作/选择集/值/变量）、09（片段/指令/坐标） |
| Section 3 — Type System | 02（schema/标量）、03（对象/接口/联合/枚举/输入对象）、04（指令/包装类型/OneOf） |
| Section 4 — Introspection | 08 |
| Section 5 — Validation | 05 |
| Section 6 — Execution | 06 |
| Section 7 — Response | 07 |
| Appendix C — Grammar | 01、09（语法汇总分散引用） |
| Python 生态 | 10 |
| GraphQL + AI | 11 |

### 信源文件清单（references/）

| 文件名 | 标题 | 覆盖事实 |
|---|---|---|
| spec-section-1-overview.md | GraphQL 规范 Section 1：Overview | F-001~F-010 |
| spec-section-2-language.md | GraphQL 规范 Section 2：Language | F-011~F-093 |
| spec-section-3-type-system.md | GraphQL 规范 Section 3：Type System | F-094~F-218 |
| spec-section-4-introspection.md | GraphQL 规范 Section 4：Introspection | F-219~F-248 |
| spec-section-5-validation.md | GraphQL 规范 Section 5：Validation | F-249~F-302 |
| spec-section-6-execution.md | GraphQL 规范 Section 6：Execution | F-303~F-375 |
| spec-section-7-response.md | GraphQL 规范 Section 7：Response | F-376~F-412 |
| mcp-server-source.md | AI WG MCP 服务器源码与文档（server.py / schema_indexer.py / schema.graphql / README） | F-435~F-586 |
| semantic-introspection-rfc.md | 语义内省 RFC（Semantic Introspection） | F-587~F-612 |

### 示例文件清单（examples/）

| 文件名 | 标题 | 内容 |
|---|---|---|
| basic-query.md | 基础查询与变更示例 | 展示 query/mutation/subscription 三种操作的语法、选择集嵌套、别名、参数、变量；对应 01 和 02 文档，使用电商 schema 中的 `user`/`users`/`placeOrder` 字段（F-513~F-537） |
| schema-ecommerce.md | 电商 Schema 定义示例 | 完整解读 MCP 测试 schema.graphql：Query/Mutation 根类型、Connection 分页模式（F-530~F-536）、业务对象关系（User/Product/Order/Category，F-538~F-553）、Input 类型（F-554~F-556）、Enum（F-557~F-560）；对应 02~04 文档 |
| error-bubbling.md | Non-Null 错误冒泡示例 | 构造从叶子字段到根的 Non-Null 链场景，展示执行错误如何沿类型链冒泡、在可 null 位置停止为 null、全链 Non-Null 时 data 为 null；对照 F-349/F-373/F-375/F-404；对应 07 文档 |
| mcp-ai-integration.md | MCP 与 AI 集成示例 | 演示 MCP 服务器 `list_types`（语义搜索 type.field，F-474~F-481）和 `run_query`（验证执行 GraphQL，F-482~F-484）两个工具的调用流程；展示语义内省 `__search`/`__definitions` 提议（F-594~F-606）；对应 11 文档 |
