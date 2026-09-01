---
type: reference
title: "AI WG MCP 服务器源码与文档"
description: "GraphQL AI 工作组 MCP 服务器源码登记，涵盖 server.py、schema_indexer.py、schema.graphql、测试服务器及 README 的完整结构与功能。"
sources:
  - path: "external/libs/GraphQL/ai-wg/mcp/server.py"
    facts: [F-435, F-436, F-437, F-438, F-439, F-440, F-441, F-442, F-443, F-444, F-445, F-446, F-447, F-448, F-449, F-450, F-451, F-452, F-453, F-454, F-455, F-456, F-457, F-458, F-459, F-460, F-461, F-462, F-463, F-464, F-465, F-466, F-467, F-468, F-469, F-470, F-471, F-472, F-473, F-474, F-475, F-476, F-477, F-478, F-479, F-480, F-481, F-482, F-483, F-484, F-485, F-486, F-487, F-488]
  - path: "external/libs/GraphQL/ai-wg/mcp/schema_indexer.py"
    facts: [F-489, F-490, F-491, F-492, F-493, F-494, F-495, F-496, F-497, F-498, F-499, F-500, F-501, F-502, F-503, F-504, F-505, F-506, F-507, F-508, F-509, F-510, F-511, F-512]
  - path: "external/libs/GraphQL/ai-wg/mcp/schema.graphql"
    facts: [F-513, F-514, F-515, F-516, F-517, F-518, F-519, F-520, F-521, F-522, F-523, F-524, F-525, F-526, F-527, F-528, F-529, F-530, F-531, F-532, F-533, F-534, F-535, F-536, F-537, F-538, F-539, F-540, F-541, F-542, F-543, F-544, F-545, F-546, F-547, F-548, F-549, F-550, F-551, F-552, F-553, F-554, F-555, F-556, F-557, F-558, F-559, F-560]
  - path: "external/libs/GraphQL/ai-wg/mcp/test_graphql_server/server.py"
    facts: [F-561, F-562, F-563, F-564, F-565, F-566, F-567, F-568, F-569, F-570, F-571, F-572, F-573]
  - path: "external/libs/GraphQL/ai-wg/mcp/README.md"
    facts: [F-574, F-575, F-576, F-577, F-578, F-579, F-580, F-581, F-582, F-583, F-584, F-585, F-586]
---

# AI WG MCP 服务器源码与文档

## 信源概述

| 信源 | 类型 | 事实范围 | 职责 |
|------|------|----------|------|
| external/libs/GraphQL/ai-wg/mcp/server.py | 源码 | F-435~F-488 | MCP 服务器主体，暴露 list_types 和 run_query 工具 |
| external/libs/GraphQL/ai-wg/mcp/schema_indexer.py | 源码 | F-489~F-512 | Schema 展平、嵌入索引与持久化存储 |
| external/libs/GraphQL/ai-wg/mcp/schema.graphql | Schema | F-513~F-560 | 电商示例 GraphQL Schema（SDL） |
| external/libs/GraphQL/ai-wg/mcp/test_graphql_server/server.py | 源码 | F-561~F-573 | 带内存数据的测试 GraphQL HTTP 服务器 |
| external/libs/GraphQL/ai-wg/mcp/README.md | 文档 | F-574~F-586 | MCP 服务器架构、部署与使用说明 |

## 关键事实登记

### 架构总览（F-574~F-575）

该 MCP 服务器是 Docker 化的 Python 服务，为 LLM 索引 GraphQL schema，按 `type->field` 存储 OpenAI embeddings，支持快速查找和 `run_query` 执行。

架构组件：

| 组件 | 职责 |
|------|------|
| `schema.graphql` | 电商示例 Schema 定义 |
| `schema_indexer.py` | 将 Schema 展平为 type.field 签名并生成嵌入向量 |
| `server.py` | 暴露 `list_types`（语义搜索）和 `run_query`（验证/执行）两个 MCP 工具 |
| `data/` 目录 | 持久化索引（metadata.json + vectors.npz，已 gitignore） |

### server.py — MCP 服务器主体

#### 模块与依赖（F-435~F-439）

模块 docstring 说明该 MCP 服务器暴露 `list_types` 和 `run_query` 工具，支持 schema 文件或实时 endpoint 两种模式。

**导入依赖**：

| 来源 | 导入内容 |
|------|----------|
| 标准库 | `os`, `json`, `threading`, `pathlib.Path`, `typing.Literal`, `urllib.error.HTTPError`, `urllib.request.Request/urlopen` |
| graphql-core | `build_client_schema`, `build_schema`, `get_introspection_query`, `graphql_sync`, `print_schema` |
| mcp.server.fastmcp | `FastMCP` |
| schema_indexer | `DEFAULT_DATA_DIR`, `DEFAULT_EMBED_MODEL`, `DEFAULT_SCHEMA_PATH`, `EmbeddingStore`, `OpenAIEmbedder`, `ensure_index`, `ensure_index_text` |

#### 全局常量与配置（F-440~F-456）

| 常量/变量 | 值/说明 |
|-----------|---------|
| `APP_NAME` | `"graphql-mcp"` |
| `DEFAULT_TRANSPORT` | 依次从 `MCP_TRANSPORT`、`FASTMCP_TRANSPORT` 环境变量读取，默认 `"sse"` |
| `DEFAULT_INSTRUCTIONS` | 指示 LLM 先调用 `list_types` 再调用 `run_query` |
| `MCP_INSTRUCTIONS` | 可通过 `MCP_INSTRUCTIONS` 环境变量覆盖 |
| `SCHEMA_PATH` | 从 `GRAPHQL_SCHEMA_PATH` 读取，默认 `DEFAULT_SCHEMA_PATH` |
| `ENDPOINT_URL` | 从 `GRAPHQL_ENDPOINT_URL` 读取 |
| `DATA_DIR` | 从 `GRAPHQL_EMBEDDER_DATA_DIR` 读取，默认 `DEFAULT_DATA_DIR` |
| `EMBED_MODEL` | 从 `GRAPHQL_EMBED_MODEL` 读取，默认 `DEFAULT_EMBED_MODEL` |
| `_SCALAR_TYPES` | `{"String", "Int", "Float", "Boolean", "ID"}` |
| `_AGGREGATE_KEYWORDS` | `{"count", "total", "sum", "avg", "average", "how many", "number of"}` |
| `_AGGREGATE_FIELD_PATTERNS` | `{"count", "total", "sum", "avg", "aggregate"}` |
| `_INDEX_LOCK` | `threading.Lock()` 用于索引构建线程同步 |

全局实例化：`embedder = OpenAIEmbedder(model=EMBED_MODEL)`、`store = EmbeddingStore(data_dir=DATA_DIR, embedding_model=embedder.model)`。FastMCP 实例声明依赖 `["graphql-core", "openai", "numpy"]`。

#### 函数签名表

| 函数 | 签名 | 职责 |
|------|------|------|
| `_run_with_default_transport` | `(self, transport: Literal["stdio","sse","streamable-http"] \| None = None, mount_path: str \| None = None)` | Monkey-patch 覆盖 `mcp.run`，使默认传输使用 `DEFAULT_TRANSPORT` |
| `configure_runtime` | `(*, schema_path: Path, data_dir: Path, embed_model: str) -> None` | 重新设置文件模式的全局变量 |
| `configure_runtime_endpoint` | `(*, endpoint_url: str, data_dir: Path, embed_model: str, schema_text: str, schema_source: dict) -> None` | 重新设置 endpoint 模式的全局变量 |
| `_parse_headers` | `(raw_headers: list[str] \| None) -> dict[str, str]` | 将 "Name: Value" 格式字符串列表解析为字典 |
| `_post_json` | `(url: str, payload: dict, headers: dict \| None = None, timeout_s: float = 30.0) -> dict` | 发送 POST JSON 请求，HTTPError 时尝试解析错误响应体 |
| `_introspect_schema_sdl` | `(endpoint_url: str, headers: dict[str,str], timeout_s: float) -> str` | 使用 `get_introspection_query` 获取 schema，通过 `build_client_schema` 和 `print_schema` 转为 SDL |
| `_parse_signature` | `(signature: str) -> tuple[str, str, list[tuple[str,str]], str]` | 解析 "Type.field(arg: Type) -> ReturnType" 格式签名 |
| `_base_type` | `(type_str: str) -> str` | 递归去除 NonNull（!）和 List（[]）包装，返回基础类型名 |
| `_tokenize` | `(text: str) -> list[str]` | 将文本转为小写字母数字 token 列表 |
| `_token_score` | `(tokens: list[str], *values: str) -> int` | 统计 token 在 values 拼接文本中的出现次数 |
| `_is_aggregate_query` | `(query: str) -> bool` | 检查查询是否包含聚合关键词 |
| `_is_aggregate_field` | `(field_name: str) -> bool` | 检查字段名是否包含聚合模式 |
| `_is_connection_field` | `(field_name: str) -> bool` | 检查字段名是否以 "connection" 结尾 |
| `_parse_field_info` | `(meta: dict) -> dict[str, list[dict]]` | 从索引元数据解析字段签名，按 type_name 分组 |
| `_format_args` | `(args: list[tuple[str,str]]) -> str` | 将参数列表格式化为 "(name: <type>, ...)" 字符串 |
| `_render_selection_set` | `(type_name, fields_by_type, tokens, depth=1, max_fields=6) -> str \| None` | 递归为对象类型生成 GraphQL selection set，优先标量和 token 匹配字段 |
| `ensure_schema_indexed` | `(*, force: bool = False) -> dict` | 使用 `_INDEX_LOCK` 同步；endpoint 模式调 `ensure_index_text`，文件模式调 `ensure_index` |

#### MCP 工具：list_types（F-474~F-481）

```python
@mcp.tool()
def list_types(query: str, limit: int = 20) -> list:
```

对 schema 进行模糊搜索，自动构建/更新持久化嵌入索引。

工作流程：
1. `capped_limit = max(1, min(limit, 20))`，限制返回数量 1-20
2. 使用 `embedder.embed_one(query)` 生成查询向量，`store.search()` 检索结果
3. **智能排序**：
   - 聚合查询时：Query 类型 > 聚合字段 > Connection 字段 > 相似度分数
   - 非聚合查询时：Query 类型 > 相似度分数
4. 对每个结果构造 entry，包含 `type`、`field`、`summary`
5. Query 类型字段额外生成 `query_template`：
   - Connection 字段：生成深度 2、最多 8 字段的 selection set，添加游标分页 usage_hint
   - 聚合字段：无 selection set，标注 O(1) count 操作
   - 非标量返回字段：生成 selection set
6. 非 Query 类型的非标量返回字段生成 `selection_hint`（深度 1，最多 5 字段）

#### MCP 工具：run_query（F-482~F-484）

```python
@mcp.tool()
def run_query(query: str) -> dict:
```

验证并执行 GraphQL 查询。两种模式：

| 模式 | 行为 |
|------|------|
| endpoint 模式 | 将查询代理到 `ENDPOINT_URL`，返回 `{valid, errors, data, extensions}` |
| 本地模式 | 使用 `build_schema(SCHEMA_PATH.read_text())` 和 `graphql_sync(schema, query)` 执行；无 resolver 时字段解析为 null，主要用于验证和形状检查 |

#### CLI 入口（F-485~F-488）

`__main__` 块使用 argparse，支持参数：

| 参数 | 说明 |
|------|------|
| `--transport` | stdio/sse/streamable-http，默认 sse |
| `--schema` / `--endpoint` | 互斥，Schema 文件路径或 endpoint URL |
| `--data-dir` | 嵌入索引存储目录 |
| `--model` | OpenAI 嵌入模型 |
| `--header` | 可重复，endpoint 模式 HTTP 头 |
| `--timeout` | HTTP 超时秒数，默认 30.0 |
| `--host` / `--port` / `--log-level` / `--mount-path` | 服务器配置 |

启动时在 daemon 线程 `"graphql-mcp-indexer"` 中后台调用 `ensure_schema_indexed(force=False)`，最后调用 `mcp.run()` 启动服务器。

### schema_indexer.py — Schema 索引引擎

#### 模块与常量（F-489~F-492）

| 常量 | 值 |
|------|-----|
| `DEFAULT_DATA_DIR` | `Path(__file__).parent / "data"` |
| `DEFAULT_SCHEMA_PATH` | `Path(__file__).parent / "schema.graphql"` |
| `DEFAULT_EMBED_MODEL` | `"text-embedding-3-small"` |

导入：`numpy as np`、graphql-core（`GraphQLList`, `GraphQLNonNull`, `GraphQLObjectType`, `build_schema`）、`openai.OpenAI`、`dotenv.load_dotenv`。

#### 数据结构（F-493）

```python
@dataclass
class TypeField:
    type_name: str
    field_name: str
    summary: str
```

#### 核心类表

**OpenAIEmbedder 类**（F-496~F-499）：

| 方法 | 签名 | 职责 |
|------|------|------|
| `__init__` | `(self, model=DEFAULT_EMBED_MODEL)` | 创建 OpenAI() 客户端并保存 model |
| `embed_many` | `(self, texts: Sequence[str]) -> np.ndarray` | 调用 OpenAI embeddings API，返回 L2 归一化后的 float32 向量数组；空输入返回 zeros((0,0)) |
| `embed_one` | `(self, text: str) -> np.ndarray` | 调用 embed_many 并返回第一个向量 |
| `_normalize` | `(vectors) -> np.ndarray` | 静态方法，按行计算 L2 范数并归一化，零范数替换为 1.0 |

**EmbeddingStore 类**（F-500~F-504）：

| 方法 | 签名 | 职责 |
|------|------|------|
| `__init__` | `(self, data_dir: Path, embedding_model: str)` | 设置 meta_path/vectors_path，延迟加载 |
| `is_ready` | `(self) -> bool` | 检查 metadata.json 和 vectors.npz 是否存在 |
| `load` | `(self) -> dict` | 加载元数据和向量；模型不匹配则抛出 ValueError |
| `save` | `(self, vectors, items, schema_sha, schema_source=None) -> dict` | 保存向量为 npz、元数据为 JSON（含 embedding_model、schema_sha、items、可选 schema_source） |
| `search` | `(self, query_vector, limit=5) -> list[dict]` | 矩阵乘法计算余弦相似度，返回 top-N 结果，每项含 type/field/summary/score |

#### Schema 展平函数（F-494~F-495）

- `describe_type(graphql_type) -> str`：递归将 GraphQL 类型转为字符串表示（NonNull 添加 `!`，List 包装为 `[]`）
- `flatten_schema(schema_text: str) -> List[TypeField]`：使用 `build_schema` 解析 SDL，遍历 `schema.type_map`，跳过 `__` 开头的内省类型和非 `GraphQLObjectType`，为每个字段生成 `"Type.field(args) -> ReturnType"` 签名，附加 description 作为 summary

#### 索引构建函数表

| 函数 | 职责 |
|------|------|
| `compute_schema_sha(schema_text) -> str` | 返回 schema_text 的 SHA-256 十六进制摘要 |
| `index_schema_text(schema_text, *, data_dir, embed_model, embedder, store, schema_source) -> dict` | 调用 flatten_schema、embed_many、compute_schema_sha、store.save，返回含 count 的元数据 |
| `index_schema(schema_path, *, data_dir, embed_model, embedder, store, schema_source) -> dict` | 读取 schema_path 文件内容，构造源信息，委托给 index_schema_text |
| `ensure_index_text(schema_text, *, schema_source, data_dir, embed_model, embedder, store, force=False) -> dict` | 检查索引是否存在且 schema_sha/schema_source 未变，未变则直接返回，否则重建 |
| `ensure_index(schema_path, *, data_dir, embed_model, embedder, store, force=False) -> dict` | 文件模式版本，读取 schema_path 计算 sha，委托给 index_schema |
| `search_index(query, data_dir, embed_model, embedder, limit=5) -> list[dict]` | 加载 store、嵌入查询、搜索，为每个结果附加 schema_sha |

#### CLI（F-511~F-512）

`cli(argv=None) -> int` 提供两个子命令：
- **index**：索引 schema（默认无子命令时执行）
- **search**：自然语言搜索，`--limit` 默认 5，上限 20；先调用 `ensure_index` 再调用 `search_index`，以 JSON 格式输出结果

### schema.graphql — 电商示例 Schema

#### 类型清单总览

| 类别 | 类型 |
|------|------|
| 根类型 | `Query`、`Mutation` |
| 分页类型 | `PageInfo`、`UserConnection`、`UserEdge`、`ProductConnection`、`ProductEdge`、`OrderConnection`、`OrderEdge` |
| 业务对象 | `User`、`UserProfile`、`Preferences`、`Company`、`Address`、`Product`、`Review`、`Category`、`Order`、`OrderItem`、`Shipment`、`Carrier`、`TrackingEvent`、`Payment`、`Discount`、`InventoryLocation` |
| Input 类型 | `PlaceOrderInput`、`PlaceOrderItemInput` |
| 返回类型 | `OrderConfirmation` |
| Enum 类型 | `OrderStatus`、`PaymentStatus`、`PaymentMethod`、`InventoryStatus` |

#### Query 类型字段（F-513~F-529）

```graphql
type Query {
  user(id: ID!): User
  users(limit: Int = 10, offset: Int = 0): [User!]!
  usersConnection(first: Int = 10, after: ID): UserConnection!
  usersCount: Int!
  order(id: ID!): Order
  orders(status: OrderStatus, limit: Int = 10): [Order!]!
  ordersConnection(first: Int = 10, after: ID, status: OrderStatus): OrderConnection!
  ordersCount(status: OrderStatus): Int!
  product(id: ID!): Product
  products(limit: Int = 10, offset: Int = 0): [Product!]!
  productsConnection(first: Int = 10, after: ID): ProductConnection!
  productsCount: Int!
  searchProducts(term: String!, limit: Int = 10): [Product!]!
  category(id: ID!): Category
  categories: [Category!]!
  categoriesCount: Int!
  reviewsCount: Int!
}
```

Query 类型涵盖三种数据访问模式：
- **单条查询**：`user`、`order`、`product`、`category`（按 ID 获取）
- **列表查询**：`users`、`orders`、`products`、`searchProducts`、`categories`（offset 分页）
- **Connection 分页**：`usersConnection`、`ordersConnection`、`productsConnection`（游标分页）
- **聚合查询**：`usersCount`、`ordersCount`、`productsCount`、`categoriesCount`、`reviewsCount`

#### Connection 分页类型（F-530~F-536）

遵循 Relay-style Connection 模式：

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

ProductConnection/ProductEdge、OrderConnection/OrderEdge 结构相同。

#### Mutation 类型（F-537）

```graphql
type Mutation {
  placeOrder(input: PlaceOrderInput!): OrderConfirmation!
}
```

#### 业务对象类型（F-538~F-553）

核心业务关系：
- **User**：包含 profile、address、company、orders、wishlist、reviews 等关联
- **Product**：包含 category、reviews、related products、inventory locations
- **Order**：包含 items、shipment、payment、discounts
- **Category**：自引用层级关系（parent/children），关联 products
- **Review**：关联 author（User）和 product

#### Input 与 Enum 类型（F-554~F-560）

```graphql
input PlaceOrderInput {
  userId: ID!
  items: [PlaceOrderItemInput!]!
  note: String
  couponCode: String
}

input PlaceOrderItemInput {
  productId: ID!
  quantity: Int!
}

type OrderConfirmation {
  id: ID!
  estimatedDelivery: String!
  message: String
  order: Order
}

enum OrderStatus { PENDING SHIPPED DELIVERED CANCELLED }
enum PaymentStatus { AUTHORIZED CAPTURED FAILED REFUNDED }
enum PaymentMethod { CARD PAYPAL BANK_TRANSFER }
enum InventoryStatus { IN_STOCK LOW_STOCK OUT_OF_STOCK }
```

### test_graphql_server/server.py — 测试服务器（F-561~F-573）

基于 Python 标准库 `http.server` 的测试 GraphQL HTTP 服务器，使用 graphql-core 的 `build_schema` 和 `graphql_sync` 执行查询。

| 组件 | 职责 |
|------|------|
| `Root` 类 | 在 `__init__` 中构造内存数据（addresses、companies、categories、products、discounts、carriers、shipments、payments、orders、user_store、reviews），建立双向关联 |
| Query resolvers | `user`、`users`、`order`、`orders`、`product`、`products`、`searchProducts`、`category`、`categories` |
| Count resolvers | `usersCount`、`productsCount`、`ordersCount`、`categoriesCount`、`reviewsCount` |
| `_build_connection` | 构建 Connection 响应，游标为 item ID，first 上限 100，返回 totalCount/pageInfo/edges |
| Connection resolvers | `usersConnection`、`productsConnection`、`ordersConnection` |
| `placeOrder` | 下单逻辑：验证用户和商品、计算小计、应用优惠券折扣、返回 OrderConfirmation |
| `make_handler` | 闭包 Handler 类，处理 OPTIONS（CORS 预检）、GET /healthz、POST /graphql |
| `main` | 解析 --host（默认 127.0.0.1）、--port（默认 4000）、--schema（默认 ../schema.graphql） |

### README — 部署与使用（F-576~F-586）

- **Setup**：创建 `.env` 设置 `OPENAI_API_KEY`，使用 venv 安装 requirements.txt
- **Docker**：`docker compose up --build` 启动，MCP 服务器在 `http://127.0.0.1:8000/sse`
- **CLI 索引**：`python3 schema_indexer.py`（索引）、`python3 schema_indexer.py search "query"`（搜索）
- **嵌入模型**：默认使用 `text-embedding-3-small`
- **环境变量**：支持 `FASTMCP_` 前缀变量（HOST/PORT/LOG_LEVEL）和 `MCP_INSTRUCTIONS`
- **测试**：可通过 `npx @modelcontextprotocol/inspector` 连接 SSE 服务器测试
- **测试服务器**：位于 `test_graphql_server/`，默认端口 4000，`run_query` 返回真实数据
- **Claude 集成**：可配置到 Claude Desktop/CLI，使用 `claude mcp add --transport sse` 命令或 JSON 配置文件
