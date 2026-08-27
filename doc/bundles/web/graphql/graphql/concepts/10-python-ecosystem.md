---
type: concept
title: "Python 生态：客户端与服务端实践"
description: "Python GraphQL 生态全景：7 个客户端库与 6 个服务端库对比，graphql-core 作为底层实现的地位，以及基于 graphql-core 的测试服务器实现模式（Root 类、resolver 方法、make_handler）。"
sources:
  - resource: /references/mcp-server-source.md
    facts: [F-437, F-561, F-562, F-563, F-564, F-565, F-566, F-567, F-568, F-569, F-570, F-571, F-572, F-573, F-625, F-626, F-627, F-628, F-629, F-630, F-631, F-632, F-633, F-634, F-635, F-636, F-637]
---

# Python 生态：客户端与服务端实践

GraphQL 拥有跨语言的丰富生态，Python 社区提供了从底层规范实现到高层框架的完整工具链。本文梳理 Python GraphQL 生态中的客户端库、服务端库，并以 graphql-core 为核心展示一个最小可运行的 GraphQL 服务器实现模式。

## Python GraphQL 生态全景

Python GraphQL 生态可分为三层：

1. **底层规范实现**：graphql-core——GraphQL 规范的 Python 移植，提供 schema 构建、查询解析、验证和执行引擎；
2. **服务端框架**：Strawberry、Ariadne、Graphene、Tartiflette 等，在 graphql-core 之上提供更高层的 API；
3. **客户端库**：GQL、Qlient、sgqlc 等，简化 GraphQL 查询的构造、发送和响应处理。

graphql-core 是大多数 Python GraphQL 服务端库的基础。MCP 服务器源码中从 graphql-core 导入了 `build_client_schema`、`build_schema`、`get_introspection_query`、`graphql_sync`、`print_schema` 等核心函数（F-437），展示了其作为底层引擎的角色。

## 客户端库对比

官网 tools-and-libraries 页面列出了 7 个 Python 客户端库（F-625~F-631）：

| 库名 | 描述 | URL |
|---|---|---|
| **GQL** | Python 中的 GraphQL 客户端，功能全面 | https://github.com/graphql-python/gql |
| **python-graphql-client** | 面向 Python 2.7+ 的简单 GraphQL 客户端 | https://github.com/prisma/python-graphql-client |
| **Qlient** | 快速现代的 GraphQL 客户端，以简洁为设计理念，支持链式字段查询 | https://github.com/qlient-org/python-qlient |
| **sgqlc** | 简单的 Python GraphQL 客户端，支持根据 schema 生成代码 | https://github.com/profusion/sgqlc |
| **ql** | 基于 pydantic 的非侵入式 GraphQL 客户端，通过 pydantic 类进行类型验证 | https://dsal3389.github.io/ql/ |
| **Ariadne Codegen** | 从任意 schema 和查询生成完全类型化的 Python GraphQL 客户端（异步） | https://github.com/mirumee/ariadne-codegen |
| **graphql-query** | 完整的 Python GraphQL 查询字符串生成库，提供 Operation/Query/Field/Argument 等构建块 | https://denisart.github.io/graphql-query/ |

### 客户端选型要点

- **需要代码生成和完整类型安全**：选择 Ariadne Codegen，从 schema 和查询文件生成异步客户端代码；
- **需要灵活的查询构造**：GQL 是最成熟的通用客户端，支持多种传输方式；
- **偏好链式 API**：Qlient 提供链式字段查询，代码简洁；
- **需要 schema 驱动的代码生成**：sgqlc 可根据 schema 生成 Python 类型；
- **偏好 pydantic 模型验证**：ql 将 pydantic 与 GraphQL 查询结合；
- **仅需构造查询字符串**：graphql-query 专注查询字符串生成，不处理网络传输。

### 安装示例

```bash
pip install gql
pip install qlient
pip install ariadne-codegen
pip install graphql_query
pip install pydantic-graphql
```

Ariadne Codegen 配置示例（`pyproject.toml`）：

```toml
[ariadne-codegen]
queries_path = "queries/"
remote_schema_url = "https://example.com/graphql"
```

运行 `ariadne-codegen` 即可生成类型化的异步客户端代码。

## 服务端库对比

官网列出了 6 个 Python 服务端库（F-632~F-637）：

| 库名 | 描述 | URL |
|---|---|---|
| **Strawberry** | 使用现代 Python 类型注解的 code-first GraphQL 服务器库，基于 dataclass | https://strawberry.rocks/ |
| **Ariadne** | schema-first 的 GraphQL 服务器库，支持同步和异步执行，API 简单易扩展 | https://ariadnegraphql.org/ |
| **Graphene** | 经典的 code-first GraphQL 库，提供 Relay/Django/SQLAlchemy 绑定 | http://graphene-python.org/ |
| **Tartiflette** | 面向 Python 3.6+ 的 asyncio GraphQL 构建库，使用 `@Resolver` 装饰器 | https://tartiflette.io/ |
| **Django Graphbox** | 快速构建 Django 模型 CRUD GraphQL API 的包，自动生成 schema 和 mutation | https://90horasporsemana.com/graphbox/ |
| **Graphene Django CRUDDALS** | 将 Django 模型转换为完整 CRUD GraphQL API，自动生成 Schema/Query/Mutation | https://graphene-django-cruddals.readthedocs.io/en/latest/ |

### Schema-first vs Code-first

服务端库按设计哲学可分为两类：

**Schema-first（模式优先）**：先编写 GraphQL SDL（Schema Definition Language），再绑定 resolver 函数。代表库为 Ariadne。

```python
from ariadne import QueryType, make_executable_schema

type_defs = """
    type Query {
        user(id: ID!): User
    }
    type User {
        id: ID!
        name: String!
    }
"""

query = QueryType()

@query.field("user")
def resolve_user(*_, id):
    return {"id": id, "name": "Alice"}

schema = make_executable_schema(type_defs, query)
```

**Code-first（代码优先）**：用 Python 类型/类定义 schema，框架自动生成 SDL。代表库为 Strawberry 和 Graphene。

```python
import strawberry

@strawberry.type
class User:
    id: strawberry.ID
    name: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: strawberry.ID) -> User:
        return User(id=id, name="Alice")

schema = strawberry.Schema(query=Query)
```

### 服务端选型建议

- **现代新项目**：推荐 **Strawberry**（code-first，充分利用 Python 类型注解，活跃维护）或 **Ariadne**（schema-first，SDL 即文档，适合团队偏好显式 schema 的场景）；
- **Django 集成项目**：推荐 **Graphene Django**（成熟的 Django 集成）或 **Graphene Django CRUDDALS**（快速生成 CRUD API）；Django Graphbox 适合需要快速搭建管理型 API 的场景；
- **asyncio 原生项目**：Tartiflette 提供原生 asyncio 支持；
- **遗留项目**：Graphene 生态最成熟，但开发节奏已放缓，新项目需谨慎评估。

## graphql-core：底层规范实现

graphql-core 是 GraphQL 规范在 Python 中的参考实现，也是上述大多数服务端框架的底层引擎。MCP 服务器源码展示了 graphql-core 的核心 API 使用方式（F-437）：

```python
from graphql import build_client_schema, build_schema, get_introspection_query, graphql_sync, print_schema
```

### 核心函数

| 函数 | 用途 |
|---|---|
| `build_schema(sdl)` | 从 GraphQL SDL 字符串构建内存中的 schema 对象 |
| `build_client_schema(introspection_result)` | 从内省查询结果构建客户端 schema |
| `get_introspection_query(descriptions=True)` | 生成标准内省查询字符串 |
| `graphql_sync(schema, query)` | 同步执行 GraphQL 查询，返回 ExecutionResult |
| `print_schema(schema)` | 将 schema 对象打印为 SDL 字符串 |

### 内省到 SDL 的转换流程

MCP 服务器的 `_introspect_schema_sdl` 函数展示了典型流程（F-462）：

1. 使用 `get_introspection_query(descriptions=True)` 生成内省查询；
2. 发送 HTTP POST 到远端 GraphQL endpoint；
3. 用 `build_client_schema` 将内省结果构建为 schema 对象；
4. 用 `print_schema` 将 schema 转为 SDL 字符串。

这个流程使得任何 GraphQL endpoint 的 schema 都可以被程序化获取和转换。

## 基于 graphql-core 的测试服务器

AI WG 仓库中的 `test_graphql_server/server.py` 是一个基于 graphql-core 和 Python 标准库的最小 GraphQL 服务器实现（F-561~F-573）。它不依赖任何 Web 框架，直接使用 `http.server` 模块，是理解 Python GraphQL 服务端核心模式的优秀范例。

### 架构概览

测试服务器的架构分为三层：

1. **数据层（Root 类）**：`Root` 类在内存中构造全部测试数据，并定义 resolver 方法；
2. **执行层（graphql_sync）**：使用 `build_schema` 加载 SDL，用 `graphql_sync` 执行查询；
3. **传输层（make_handler）**：创建 HTTP 请求处理器，处理 CORS、路由和 JSON 序列化。

### 导入与依赖

测试服务器仅依赖 graphql-core 和 Python 标准库（F-561）：

```python
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from graphql import build_schema, graphql_sync
```

### Root 类：数据与 Resolver

`Root` 类是服务器的核心，在 `__init__` 中构造完整的内存数据集（F-564），包括：

- `addresses`（4 条）、`companies`（2 条）、`categories`（5 条，含层级关系）；
- `products`（5 条，含 related/inventory 关联）、`discounts`（2 条）；
- `carriers`（2 条）、`shipments`（2 条）、`payments`（2 条）；
- `orders`（2 条）、`user_store`（3 条）、`reviews`（4 条）。

数据之间建立双向关联，模拟真实的数据图。

#### Query Resolver 方法

`Root` 类为 schema 中每个 Query 字段定义 resolver 方法（F-566）：

```python
class Root:
    def user(self, info, id): ...
    def users(self, info, limit=10, offset=0): ...
    def order(self, info, id): ...
    def orders(self, info, status=None, limit=10): ...
    def product(self, info, id): ...
    def products(self, info, limit=10, offset=0): ...
    def searchProducts(self, info, term, limit=10): ...
    def category(self, info, id): ...
    def categories(self, info): ...
```

resolver 方法的第一个参数是 `info`（GraphQLResolveInfo），后续参数与 schema 中字段参数一一对应，默认值在方法签名中提供。

#### Count Resolver

`Root` 还定义了聚合计数方法（F-567）：

```python
def usersCount(self): ...
def productsCount(self): ...
def ordersCount(self, status=None): ...
def categoriesCount(self): ...
def reviewsCount(self): ...
```

这些方法返回整数，对应 schema 中的 `*Count: Int!` 字段。

#### Connection 分页

`Root._build_connection(items, first=10, after=None)` 方法构建符合 Connection 模式的响应（F-568）：

- 游标使用 item ID；
- `first` 参数上限为 100；
- 返回 `totalCount`、`pageInfo`、`edges` 三部分。

三个 Connection resolver 方法分别为 `usersConnection`、`productsConnection`、`ordersConnection`（F-569）。

#### Mutation Resolver

`Root.placeOrder(self, info, input)` 实现下单 mutation（F-570），流程包括：

1. 验证用户和商品存在；
2. 计算小计；
3. 应用优惠券折扣；
4. 返回 `OrderConfirmation`。

#### ID 规范化

`Root._normalize_id(value, prefix)` 是静态方法，若 value 不以指定前缀开头则添加前缀（F-565），确保 ID 格式一致。

### HTTP 处理器（make_handler）

`make_handler(schema_sdl)` 是一个工厂函数，创建闭包 `Handler` 类（F-572）：

```python
def make_handler(schema_sdl):
    schema = build_schema(schema_sdl)
    root = Root()

    class Handler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            # CORS 预检
            ...

        def do_GET(self):
            if self.path == "/healthz":
                # 健康检查
                ...

        def do_POST(self):
            if self.path == "/graphql":
                # 读取请求体，执行 graphql_sync，返回 JSON
                ...

    return Handler
```

关键设计点：

- **CORS 支持**：`_json_response` 函数设置 `Access-Control-Allow-Origin: *` 头（F-562）；
- **健康检查**：`GET /healthz` 返回服务状态；
- **GraphQL 端点**：`POST /graphql` 从请求体读取 JSON（F-563），执行 `graphql_sync(schema, query, root_value=root)`，格式化结果返回；
- **schema 和 root 共享**：通过闭包，schema 只构建一次，root 实例在请求间共享（内存数据持久化）。

### 结果格式化

`_format_result(result)` 将 `graphql_sync` 返回的 ExecutionResult 转为标准字典（F-571）：

```python
def _format_result(result):
    payload = {}
    if result.data is not None:
        payload["data"] = result.data
    if result.errors:
        payload["errors"] = [str(e) for e in result.errors]
    return payload
```

### CLI 入口

`main()` 函数解析命令行参数（F-573）：

- `--host`：默认 `127.0.0.1`；
- `--port`：默认 `4000`；
- `--schema`：默认 `../schema.graphql`。

启动 HTTPServer 监听请求。

### 运行方式

```bash
python server.py --host 0.0.0.0 --port 4000 --schema ../schema.graphql
```

## Python 服务端核心模式总结

从测试服务器实现中，可以提炼出 Python GraphQL 服务端的三个核心模式：

### 1. Root Value 模式

`graphql_sync(schema, query, root_value=root)` 的第三个参数 `root_value` 是根值对象。GraphQL 执行引擎在解析 Query/Mutation 根字段时，将 `root_value` 作为 `objectValue` 传入 resolver。这意味着 root 对象的方法名与 schema 根字段名对应即可自动调用。

### 2. Resolver 方法签名

resolver 方法遵循统一签名：`resolve_field_name(objectValue, info, **args)`。在测试服务器中，`objectValue` 即为 Root 实例自身（对于根字段）或父对象（对于嵌套字段）。

### 3. Schema 与 Resolver 绑定

`build_schema(sdl)` 仅构建类型系统，不绑定 resolver。resolver 通过 `root_value` 的方法解析。更复杂的场景可以使用 `graphql_sync` 的 `field_resolver` 参数自定义全局 resolver 策略，或使用 Ariadne/Strawberry 等框架提供的装饰器绑定。

## 相关概念

- [执行引擎：字段解析与值完成](06-execution.md) — graphql_sync 的执行流程对应规范的 ExecuteRequest 算法
- [响应格式、错误冒泡与序列化](07-response-and-errors.md) — ExecutionResult 的 data/errors 结构对应规范响应格式
- [内省系统：GraphQL 的自描述机制](08-introspection.md) — get_introspection_query 和 build_client_schema 的内省流程
- [GraphQL 与 AI：MCP、语义内省与 Agent](11-graphql-and-ai.md) — MCP 服务器基于 graphql-core 构建，test_graphql_server 为其提供真实数据源
