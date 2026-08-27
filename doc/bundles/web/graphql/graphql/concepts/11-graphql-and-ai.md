---
type: concept
title: "GraphQL 与 AI：MCP、语义内省与 Agent"
description: "GraphQL 在 AI 领域的定位与实践：AI WG MCP 服务器架构（FastMCP、list_types/run_query 工具、OpenAIEmbedder+EmbeddingStore 语义索引）、语义内省 RFC（__search/__definitions/__SearchResult/__SchemaDefinition）、GraphQL vs REST 在 AI 场景对比及 MCP/RAG/Agents 三大用例。"
sources:
  - resource: /references/mcp-server-source.md
    facts: [F-435, F-436, F-437, F-438, F-439, F-440, F-441, F-442, F-443, F-444, F-445, F-446, F-447, F-448, F-449, F-450, F-451, F-452, F-453, F-454, F-455, F-456, F-457, F-458, F-459, F-460, F-461, F-462, F-463, F-464, F-465, F-466, F-467, F-468, F-469, F-470, F-471, F-472, F-473, F-474, F-475, F-476, F-477, F-478, F-479, F-480, F-481, F-482, F-483, F-484, F-485, F-486, F-487, F-488, F-489, F-490, F-491, F-492, F-493, F-494, F-495, F-496, F-497, F-498, F-499, F-500, F-501, F-502, F-503, F-504, F-505, F-506, F-507, F-508, F-509, F-510, F-511, F-512, F-513, F-514, F-515, F-516, F-517, F-518, F-519, F-520, F-521, F-522, F-523, F-524, F-525, F-526, F-527, F-528, F-529, F-530, F-531, F-532, F-533, F-534, F-535, F-536, F-537, F-538, F-539, F-540, F-541, F-542, F-543, F-544, F-545, F-546, F-547, F-548, F-549, F-550, F-551, F-552, F-553, F-554, F-555, F-556, F-557, F-558, F-559, F-560, F-574, F-575, F-576, F-577, F-578, F-579, F-580, F-581, F-582, F-583, F-584, F-585, F-586, F-653, F-654, F-655, F-656, F-657, F-658, F-659, F-660, F-661, F-662, F-663, F-664, F-665, F-666, F-667, F-668, F-669]
  - resource: /references/semantic-introspection-rfc.md
    facts: [F-587, F-588, F-589, F-590, F-591, F-592, F-593, F-594, F-595, F-596, F-597, F-598, F-599, F-600, F-601, F-602, F-603, F-604, F-605, F-606, F-607, F-608, F-609, F-610, F-611, F-612]
---

# GraphQL 与 AI：MCP、语义内省与 Agent

GraphQL 官网将其定位为"The API language for humans and agents"（面向人类和智能体的 API 语言）（F-653）。从 2012 年 Facebook 内部使用到 2015 年开源，GraphQL 的自描述类型系统、字段级精确查询和强类型验证恰好满足了 AI agent 发现 API 能力、构造类型安全工具调用的需求。本文从三个层面展开：GraphQL 在 AI 场景的核心优势、AI WG MCP 服务器的架构实现、语义内省 RFC 的前沿提议。

## GraphQL 在 AI 领域的定位

### 三大核心特性

GraphQL 用于 AI 场景有三大核心特性（F-654）：

1. **自描述 schema（Self-describing schemas）**：让 agent 自动发现 API 能力；
2. **执行前验证（Invalid queries fail validation before they execute）**：无效查询在执行前即被拒绝，LLM 可获得命名的验证错误并自我修正；
3. **字段选择精确响应（Field selection keeps responses to what the query asked for）**：响应仅包含请求的字段，最小化 token 消耗。

GraphQL 从第一天起就为机器可读而设计——其内省系统、类型安全和可组合性为工具和客户端而构建，恰好满足 agent 理解 API 能力并请求部分数据的需求（F-655）。

### Self-describing：Agent 自动发现

每个 GraphQL API 内置类型系统。AI agent 查询 `__schema` 即可立即了解可用数据、字段接受的参数及类型关系，无需手写工具描述（F-656）。这支撑了三个关键能力：

- 自动生成 LLM 工具定义；
- agent 运行时动态发现能力；
- 从 schema 生成 MCP 服务器。

### Strongly typed：减少幻觉

每个字段有已知的验证类型。LLM 可自信地推理输入和输出；错误猜测返回命名的验证错误供 agent 修正，而非返回 HTTP 200 但携带错误数据。类型系统减少了 LLM 产生幻觉的 API 交互（F-657）。

### Composable：动态组合查询

AI agent 可动态组合精确查询——请求嵌套数据、使用别名、应用过滤器。单个 endpoint 服务于 schema 允许的任何数据访问模式，无需客户端拼接多个 REST endpoint；响应大小跟随查询而非 endpoint（F-658）。

### GraphQL vs REST+OpenAPI 在 AI 场景的对比

| 维度 | GraphQL | REST+OpenAPI |
|---|---|---|
| **Discovery（发现）** | 内省来自 endpoint 本身，在 agent 已调用的同一 endpoint 上响应，无需定位或同步第二个制品（F-659） | OpenAPI 文档发布在 endpoint 旁边，需定位和保持同步的第二个制品 |
| **Response shape（响应形状）** | 响应包含查询请求的字段，调用者决定（F-660） | endpoint 返回固定载荷，缩小响应需稀疏字段集约定或另一个 endpoint |
| **Traversal（遍历）** | 一次查询遍历多类型关系，agent 无需同时持有整个类型图（F-661） | 每个资源一个 endpoint，关系存在于 agent 脑中，需自行组合结果 |
| **Documentation（文档）** | 描述附着在类型、每个字段和每个参数上，通过同一内省调用返回，无单独文档文件（F-662） | 文档在规范文档和指令文件中 |

文档存在于 schema 中：使用 `"""` 编写的描述存储在类型和每个字段上，agent 通过内置 `__type` 内省查询读回，无需单独的文档文件（F-664）。

### Apollo 的测量数据

Apollo 报告称当 MCP 服务器暴露精选操作集而非整个 schema 时，schema 上下文减少约 40%，工具调用减少 40-75%（F-663）。需注意这是 Apollo 对自己服务器的测量而非独立基准，描述的是工具选择策略而非 GraphQL 对 REST 的对比。

## AI WG MCP 服务器架构

AI Working Group（AI WG）开发了一个 Docker 化的 Python MCP 服务器，为 LLM 索引 GraphQL schema，按 `type->field` 存储 OpenAI embeddings，支持快速查找和查询执行（F-574）。

### 架构组件

MCP 服务器由四个核心组件构成（F-575）：

| 组件 | 文件 | 职责 |
|---|---|---|
| 示例 Schema | `schema.graphql` | 电商领域的完整 GraphQL schema |
| Schema 索引器 | `schema_indexer.py` | 将 schema 展平为 `type.field` 签名并计算嵌入 |
| MCP 服务器 | `server.py` | 暴露 `list_types` 和 `run_query` 两个 MCP 工具 |
| 持久化存储 | `data/` 目录 | 存储 `metadata.json` 和 `vectors.npz`（已 gitignore） |

### 技术栈与依赖

MCP 服务器基于以下技术栈（F-436~F-439）：

```python
import os, json, threading
from pathlib import Path
from typing import Literal
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from graphql import (
    build_client_schema, build_schema,
    get_introspection_query, graphql_sync, print_schema
)
from mcp.server.fastmcp import FastMCP
from schema_indexer import (
    DEFAULT_DATA_DIR, DEFAULT_EMBED_MODEL, DEFAULT_SCHEMA_PATH,
    EmbeddingStore, OpenAIEmbedder, ensure_index, ensure_index_text
)
```

- **graphql-core**：GraphQL 规范的 Python 实现，提供 schema 构建、内省查询生成和同步执行；
- **FastMCP**：MCP 服务器框架，通过装饰器快速定义 MCP 工具；
- **OpenAI + NumPy**：用于文本嵌入和向量相似度搜索。

MCP 实例声明依赖 `graphql-core`、`openai`、`numpy`（F-456）。

### 全局配置

服务器通过环境变量配置运行时行为（F-440~F-455）：

| 配置项 | 环境变量 | 默认值 |
|---|---|---|
| 传输方式 | `MCP_TRANSPORT`/`FASTMCP_TRANSPORT` | `sse` |
| Schema 文件路径 | `GRAPHQL_SCHEMA_PATH` | `DEFAULT_SCHEMA_PATH` |
| 远端 endpoint URL | `GRAPHQL_ENDPOINT_URL` | 无 |
| 嵌入数据目录 | `GRAPHQL_EMBEDDER_DATA_DIR` | `DEFAULT_DATA_DIR` |
| 嵌入模型 | `GRAPHQL_EMBED_MODEL` | `text-embedding-3-small` |
| MCP 指令 | `MCP_INSTRUCTIONS` | 默认指令 |

全局实例化 `embedder = OpenAIEmbedder(model=EMBED_MODEL)` 和 `store = EmbeddingStore(data_dir=DATA_DIR, embedding_model=embedder.model)`（F-448）。索引构建通过 `_INDEX_LOCK = threading.Lock()` 进行线程同步（F-452）。

默认指令指示 LLM 将此 MCP 服务器视为 GraphQL 抽象层，先调用 `list_types` 再调用 `run_query`，避免不必要的工具调用（F-442）。

### 两种运行模式

MCP 服务器支持两种 schema 来源（F-435）：

1. **文件模式（file）**：从本地 `.graphql` 文件加载 SDL；
2. **Endpoint 模式（endpoint）**：连接运行中的 GraphQL 服务，通过内省获取 schema。

Endpoint 模式下，`_introspect_schema_sdl` 函数使用 `get_introspection_query(descriptions=True)` 发送内省查询，通过 `build_client_schema` 和 `print_schema` 将结果转为 SDL 字符串（F-462）。

### MCP 工具一：list_types

`list_types(query: str, limit: int = 20)` 对 schema 进行模糊搜索，自动构建/更新持久化嵌入索引（F-474）。

#### 工作流程

1. **数量限制**：`capped_limit = max(1, min(limit, 20))`，限制返回 1-20 条（F-475）；
2. **语义检索**：使用 `embedder.embed_one(query)` 生成查询向量，`store.search(query_vec, limit=capped_limit)` 检索结果（F-476）；
3. **智能排序**：排序优先级考虑查询类型、聚合特征和 Connection 字段（F-477）；
4. **结果构造**：每个结果包含 `type`、`field`、`summary` 字段，Query 类型字段额外生成 `query_template`（F-478）。

#### 排序策略

`list_types` 的排序键根据查询类型智能调整（F-477）：

- **聚合查询**（包含 count/total/sum 等关键词，F-454）：优先级为 Query 类型 > 聚合字段 > Connection 字段 > 相似度分数；
- **非聚合查询**：优先级为 Query 类型 > 相似度分数。

聚合检测通过 `_is_aggregate_query` 和 `_is_aggregate_field` 实现（F-467、F-468）。

#### 智能查询模板生成

`list_types` 根据字段类型生成不同的辅助信息：

- **Connection 字段**（以 "connection" 结尾，F-469）：生成深度 2、最多 8 字段的 selection set，添加 `usage_hint` 提示使用游标分页（F-479）；
- **聚合字段**：生成无 selection set 的 `query_template`，标注为 O(1) count 操作（F-480）；
- **非标量返回字段**（非 Query 类型）：生成 `selection_hint`（深度 1，最多 5 字段）（F-481）。

selection set 的渲染由 `_render_selection_set` 递归完成，优先选择标量字段和 token 匹配字段，`id`/`name` 字段加分（F-472）。

### MCP 工具二：run_query

`run_query(query: str) -> dict` 验证并执行 GraphQL 查询（F-482）。

#### Endpoint 模式

在 endpoint 模式下，查询被代理到 `ENDPOINT_URL`，返回包含 `valid`、`errors`、`data`、`extensions` 的字典（F-483）。HTTP 请求通过 `_post_json` 发送，设置 Content-Type 和 Accept 头，HTTPError 时尝试解析错误响应体（F-461）。

#### 本地模式

在本地模式下，使用 `build_schema(SCHEMA_PATH.read_text())` 构建 schema，通过 `graphql_sync(schema, query)` 执行（F-484）。无 resolver 时字段解析为 null，主要用于验证查询语法和形状检查。

### schema_indexer.py：语义索引引擎

`schema_indexer.py` 实现了将 GraphQL schema 转换为可搜索嵌入索引的核心逻辑。

#### 数据结构：TypeField

```python
@dataclass
class TypeField:
    type_name: str
    field_name: str
    summary: str
```

`TypeField` 是索引的基本单元，包含类型名、字段名和摘要（F-493）。

#### flatten_schema：Schema 展平

`flatten_schema(schema_text: str) -> List[TypeField]` 是索引的核心函数（F-495）：

1. 使用 `build_schema` 解析 SDL；
2. 遍历 `schema.type_map`；
3. 跳过 `__` 开头的内省类型和非 `GraphQLObjectType`；
4. 为每个字段生成 `"Type.field(args) -> ReturnType"` 签名；
5. 附加字段 description 作为 summary。

类型字符串由 `describe_type` 递归生成：`GraphQLNonNull` 添加 `!`，`GraphQLList` 包装为 `[]`（F-494）。

#### OpenAIEmbedder：嵌入生成器

`OpenAIEmbedder` 类封装 OpenAI embeddings API（F-496~F-499）：

- `__init__(model=DEFAULT_EMBED_MODEL)`：创建 OpenAI 客户端，默认模型为 `text-embedding-3-small`（F-492）；
- `embed_many(texts) -> np.ndarray`：批量嵌入，返回 L2 归一化后的 float32 向量数组，空输入返回 `zeros((0,0))`；
- `embed_one(text) -> np.ndarray`：单个文本嵌入，委托给 `embed_many`；
- `_normalize(vectors)`：静态方法，按行 L2 归一化，零范数替换为 1.0 防除零。

#### EmbeddingStore：向量持久化

`EmbeddingStore` 类管理向量和元数据的持久化（F-500~F-503）：

- 存储路径：`metadata.json`（元数据）和 `vectors.npz`（向量，NumPy 压缩格式）；
- `is_ready()`：检查两个文件是否存在；
- `load()`：加载数据，若 `embedding_model` 不匹配则抛出 ValueError；
- `save(vectors, items, schema_sha, schema_source)`：保存向量和元数据（含 embedding_model、schema_sha、items、可选 schema_source）。

#### 索引管理函数

- `index_schema(schema_path, ...)`：读取 schema 文件，委托给 `index_schema_text`（F-507）；
- `ensure_index_text(schema_text, ..., force=False)`：检查索引是否存在且 schema_sha/schema_source 未变，未变则直接返回，否则重建（F-508）；
- `ensure_index(schema_path, ..., force=False)`：文件模式版本，读取 schema 计算 sha，委托给 `index_schema`（F-509）；
- `search_index(query, ..., limit=5)`：加载 store、嵌入查询、搜索，附加 schema_sha（F-510）。

`server.py` 中的 `ensure_schema_indexed` 使用 `_INDEX_LOCK` 同步，endpoint 模式调用 `ensure_index_text`，文件模式调用 `ensure_index`（F-473）。

### schema.graphql：电商示例 Schema

MCP 服务器附带一个完整的电商领域示例 schema，共 17 个 Query 字段（F-513~F-529）。

#### Query 类型字段

Query 类型包含 17 个字段，可分为四类：

| 类别 | 字段 |
|---|---|
| 单实体查询 | `user(id: ID!)`、`order(id: ID!)`、`product(id: ID!)`、`category(id: ID!)` |
| 列表查询 | `users(limit, offset)`、`orders(status, limit)`、`products(limit, offset)`、`searchProducts(term, limit)`、`categories` |
| Connection 分页 | `usersConnection(first, after)`、`ordersConnection(first, after, status)`、`productsConnection(first, after)` |
| 聚合计数 | `usersCount`、`ordersCount(status)`、`productsCount`、`categoriesCount`、`reviewsCount` |

Mutation 类型包含一个字段：`placeOrder(input: PlaceOrderInput!): OrderConfirmation!`（F-537）。

#### Connection/Edge/PageInfo 分页模式

schema 采用 Relay 风格的游标分页模式（F-530~F-536）：

```graphql
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: ID
  endCursor: ID
}

type UserConnection {
  totalCount: Int!
  pageInfo: PageInfo!
  edges: [UserEdge!]!
}

type UserEdge {
  cursor: ID!
  node: User!
}
```

同样的模式应用于 `ProductConnection`/`ProductEdge` 和 `OrderConnection`/`OrderEdge`。

#### 业务对象与枚举

schema 定义了丰富的业务对象（F-538~F-553）：`User`、`UserProfile`、`Preferences`、`Company`、`Address`、`Product`、`Review`、`Category`、`Order`、`OrderItem`、`Shipment`、`Carrier`、`TrackingEvent`、`Payment`、`Discount`、`InventoryLocation`。

输入类型包括 `PlaceOrderInput`（含 userId、items、note、couponCode）和 `PlaceOrderItemInput`（含 productId、quantity）（F-554、F-555）。返回类型 `OrderConfirmation` 包含 id、estimatedDelivery、message 和 order（F-556）。

枚举类型包括：`OrderStatus`（PENDING/SHIPPED/DELIVERED/CANCELLED）、`PaymentStatus`、`PaymentMethod`、`InventoryStatus`（F-557~F-560）。

### 部署与运行

#### Docker 部署

Docker 方式通过 `docker compose up --build` 启动，MCP 服务器在 `http://127.0.0.1:8000/sse`（F-577）。可通过 `GRAPHQL_ENDPOINT_URL` 环境变量连接测试 endpoint。

Setup 需要创建 `.env` 文件设置 `OPENAI_API_KEY`，使用 venv 安装 `requirements.txt`（F-576）。

#### CLI 参数

MCP 服务器支持丰富的命令行参数（F-485、F-579）：

```bash
python server.py \
  --transport sse \
  --schema ./schema.graphql \
  --data-dir ./data \
  --model text-embedding-3-small \
  --host 127.0.0.1 \
  --port 8000
```

`--transport` 支持 `stdio`/`sse`/`streamable-http`，`--schema` 和 `--endpoint` 互斥（F-486）。启动时在 daemon 线程 `"graphql-mcp-indexer"` 中后台调用 `ensure_schema_indexed(force=False)`（F-487）。

#### schema_indexer CLI

`schema_indexer.py` 也提供独立 CLI（F-511、F-512、F-578）：

```bash
python schema_indexer.py index
python schema_indexer.py search "user orders" --limit 5
```

#### 测试服务器

`test_graphql_server/` 目录提供带真实 resolver 的测试服务器，默认端口 4000（F-585）。在 endpoint 模式下连接测试服务器时，`run_query` 返回真实数据，`list_types` 仍需 `OPENAI_API_KEY`。

#### MCP 客户端集成

可配置到 Claude Desktop/CLI，使用 `claude mcp add --transport sse` 命令或 JSON 配置文件（F-586）。也可通过 `npx @modelcontextprotocol/inspector` 连接 SSE 服务器进行测试（F-584）。

## 语义内省 RFC

语义内省 RFC（Semantic Introspection）由 Pascal Senn 和 Michael Staib（ChilliCream）撰写（F-587），提议扩展 GraphQL 内省系统，通过标准化 `__search` 端点实现 schema 能力的语义搜索（F-588）。

### 动机：标准内省的局限

当前 LLM 与 GraphQL API 交互有三种方式，各有不足（F-592）：

1. **遍历完整 schema**：通过内省获取全部类型和字段，token 消耗大，昂贵；
2. **依赖预训练知识**：LLM 在训练时见过 API，但知识可能过时，脆弱且不可泛化；
3. **接收手工工具描述**：每个 API 需要人工编写工具定义，维护成本高。

RFC 观察到 MCP 的工具抽象与 GraphQL 高度相似（F-589、F-590）：

- 读数据的 MCP 工具等价于 Query 字段；
- 写数据的工具等价于 Mutation 字段；
- MCP 用 JSON Schema 定义输入输出，GraphQL 用类型系统；
- 差异主要是表面的（JSON Schema vs 类型系统、扁平 vs 图组合）。

核心机会在于实现"学一次，到处用"模式——LLM 学一次规范，API 提供者索引一次 schema，无需每 API 训练或自定义工具定义（F-593）。RFC 提出问题：GraphQL 现有 schema 和内省能力能否扩展为 AI agent 的一等工具提供者，包括 prompts（F-591）。

### 提议一：`__search` 语义搜索

提议在 Query 类型上扩展 `__search` 字段（F-594）：

```graphql
type Query {
  __search(
    query: String!
    first: Int! = 10
    after: String
    minScore: Float
  ): [__SearchResult!]!
}
```

参数说明：

- `query: String!`：描述所需能力的自然语言查询（F-595）；
- `first: Int! = 10`：最大结果数；
- `after: String`：前向分页游标，值必须从之前 `__SearchResult.cursor` 获取（F-596）；
- `minScore: Float`：可选最低分数阈值，所有返回结果必须 `score >= minScore`（F-597）。

结果按 score 降序排列（F-595）。分页采用简单快进模型：将最后结果的 cursor 作为 after 参数获取下一页；返回结果少于 first 时表示无更多页（F-598）。

### `__SearchResult` 类型

```graphql
type __SearchResult {
  coordinate: String!
  definition: __SchemaDefinition!
  pathsToRoot: [[String!]!]!
  score: Float
  cursor: String!
}
```

各字段含义（F-599）：

| 字段 | 说明 |
|---|---|
| `coordinate` | Schema 坐标字符串，如 `"Query.user"` |
| `definition` | 匹配的 schema 定义（联合类型） |
| `pathsToRoot` | 从根字段到匹配定义的路径列表 |
| `score` | 相关性分数，应在 [0.0, 1.0] 范围 |
| `cursor` | 分页游标 |

`pathsToRoot` 提供从根字段到匹配定义的路径列表，每条路径是 schema 坐标序列（F-600）。若定义可通过多条路径到达，可返回多条路径，但不保证穷尽。若匹配定义本身是根字段，路径只包含单个元素（F-601）。

编者注指出 `pathsToRoot` 可能更应属于 schema 定义类型本身（如 `__Field`、`__Type`），需进一步讨论（F-602）。

### `__SchemaDefinition` 联合类型

```graphql
union __SchemaDefinition = __Type | __Field | __InputValue | __EnumValue | __Directive
```

`__SchemaDefinition` 表示可通过语义搜索发现的所有可内省 schema 定义的联合（F-603），覆盖类型、字段、输入值、枚举值和指令。

### 提议二：`__definitions` 坐标查找

提议在 Query 类型上扩展 `__definitions` 字段（F-604）：

```graphql
type Query {
  __definitions(coordinates: [String!]!): [__SchemaDefinition!]!
}
```

`__definitions` 通过 schema 坐标直接查找定义，按输入坐标顺序返回解析结果（F-604）。它消除了通过 `__schema`、`__type` 等遍历内省图的需要，可独立于 `__search` 使用（F-605）。

编者注指出 `__definitions` 与 `__search` 自然配合形成"发现-解析"两步工作流，但其本身也是通用内省原语，任何处理 schema 坐标的工具都可受益（F-606）。

### 索引要求

遵循此规范的实现必须维护活跃 schema 的索引；可使用任意向量化或索引策略；应至少索引类型名、字段名和描述（F-607）。这一要求与 AI WG MCP 服务器的 `schema_indexer.py` 实现方向一致。

### 潜在扩展 A：使用示例（`__Example`）

RFC 提议引入 `__Example` 类型（F-608）：

```graphql
type __Example {
  operation: String!
  description: String
}
```

并在 `__Type`、`__Field`、`__InputValue`、`__EnumValue`、`__Directive` 上扩展 `examples: [__Example!]` 字段（F-609）。这使得 schema 可以附带可执行的使用示例，LLM 可直接参考学习正确的查询模式。

### 潜在扩展 B：MCP 风格 Prompts（`__Prompt`）

提议在 Query 上扩展 `__prompts: [__Prompt!]!` 字段（F-610）：

```graphql
type __Prompt {
  name: String!
  description: String
  arguments: [__InputValue!]!
}
```

`__Prompt` 包含唯一标识名、可读描述和可自定义参数（F-611），将 prompt 模板作为 schema 的一等公民，使 GraphQL 服务器不仅提供数据能力，还提供 AI 交互指引。

### 开放问题

RFC 列出三个开放问题（F-612）：

1. 此方法对 LLM 是否实际有效（需实证验证）；
2. 语义搜索的速率限制和访问控制安全指导；
3. `capabilities` 命名可能与主仓库中已有的 Semantic Introspection RFC 冲突。

## GraphQL + MCP 的协同模式

### 内省自动生成工具定义

MCP 服务器利用 GraphQL 内省系统自动生成工具定义。工作流程为：

1. **内省获取 schema**：`get_introspection_query(descriptions=True)` 获取完整类型信息；
2. **构建内存 schema**：`build_client_schema` 将内省结果转为 schema 对象；
3. **展平为签名**：`flatten_schema` 将 schema 转为 `Type.field(args) -> ReturnType` 签名列表；
4. **语义索引**：`OpenAIEmbedder` + `EmbeddingStore` 为每个签名生成向量嵌入；
5. **工具暴露**：`list_types` 和 `run_query` 两个 MCP 工具让 LLM 发现和执行查询。

### Agent 工作流

AI agent 通过 MCP 查询 GraphQL 的典型流程：

```
Agent → list_types("查找用户订单")
      ← 返回相关字段（user.orders、ordersConnection 等）+ query_template
Agent → run_query("query { user(id: \"1\") { orders { id total } } }")
      ← 返回 { "data": { "user": { "orders": [...] } } }
```

DEFAULT_INSTRUCTIONS 明确指示 LLM 先调用 `list_types` 发现相关字段，再调用 `run_query` 执行查询（F-442），避免盲目猜测字段名。

### MCP 工具与 GraphQL 操作的对应

RFC 指出 MCP 工具与 GraphQL 操作存在天然对应（F-589）：

| MCP 概念 | GraphQL 对应 |
|---|---|
| 只读工具 | Query 字段 |
| 写入工具 | Mutation 字段 |
| 流式通知 | Subscription |
| JSON Schema 输入输出 | GraphQL 类型系统 |
| 工具描述 | 字段/类型 description |

一个 MCP 服务器可暴露整个 GraphQL API 表面（F-666），schema 即契约，工具定义从 schema 生成而非旁边维护。

## AI 三大用例

官网 AI 页面定义了 GraphQL 在 AI 领域的三大用例（F-666~F-668）。

### 用例一：MCP Servers

构建由 GraphQL 驱动的 Model Context Protocol 服务器（F-666）：

- 每个 query、mutation 和 subscription 成为自动可发现的工具；
- schema 即契约，工具定义从 schema 生成而非旁边维护；
- 类型安全的输入和结构化输出；
- 一个 MCP 服务器暴露整个 API 表面。

### 用例二：RAG Applications

用 GraphQL 驱动检索增强生成（Retrieval-Augmented Generation）（F-667）：

- 单次请求精确获取文档、嵌入和交叉引用，无需 REST 分页加客户端合并；
- 跨集合和来源 join 数据；
- 字段选择最小化上下文窗口浪费。

### 用例三：AI Agents & Tool Calling

为 AI agent 提供结构化、类型安全的数据层访问（F-668）：

- GraphQL 查询组合让 LLM 在单次往返中构建复杂多步数据获取——调用多个服务、过滤和聚合；
- 支持实时订阅用于流式 agent；
- 单个 endpoint 处理所有数据操作。

### 交互式演示

AI 页面提供基于 Star Wars schema 的交互式演示，展示 agent 如何组合查询回答业务问题（F-665）。例如使用 search 联合类型和三个内联片段（inline fragments），每个结果成员匹配片段并仅返回片段中命名字段。

## GraphQL AI 工作组

GraphQL AI Working Group（AI WG）对所有人开放，在 GitHub 上协作（https://github.com/graphql/ai-wg）（F-669）。社区通过 Discord（https://discord.graphql.org/）和 GitHub 协作定义 GraphQL 如何驱动下一代智能系统。

相关博客文章包括：
- 2025-07-03 "GraphQL: Supercharging AI"
- 2025-10-14 "Announcing the GraphQL AI Working Group"

## 相关概念

- [内省系统：GraphQL 的自描述机制](08-introspection.md) — __schema/__type 内省是 MCP 自动工具发现和语义内省的基础（洞察5）
- [Python 生态：客户端与服务端实践](10-python-ecosystem.md) — MCP 服务器基于 graphql-core 构建，test_graphql_server 提供真实数据源
- [片段、变量作用域与 Schema Coordinates](09-fragments-and-advanced-syntax.md) — Schema Coordinates 是 __search 和 __definitions 的坐标语法基础
- [验证管线与规则体系](05-validation.md) — GraphQL 执行前验证使 LLM 获得命名错误并自我修正
- [GraphQL 概览与五大设计原则](00-overview.md) — 自描述（Self-describing）原则是 AI 集成的设计基石
