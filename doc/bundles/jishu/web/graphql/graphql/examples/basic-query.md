---
type: example
title: "基础查询与变更示例"
description: "通过电商场景的完整 Schema，演示 query 的字段选择、嵌套对象、参数、别名、片段，mutation 创建订单，subscription 订单状态更新，以及变量的使用。"
sources:
  - resource: /references/spec-section-2-language.md
    facts: [F-011, F-031, F-035, F-037, F-038, F-039, F-040, F-042, F-043, F-044, F-045, F-047, F-048, F-049, F-051, F-053, F-054, F-056, F-073, F-075, F-077, F-078, F-080, F-081, F-082, F-083, F-084, F-085]
  - resource: /references/spec-section-3-type-system.md
    facts: [F-098, F-103, F-104, F-105, F-108, F-118, F-119, F-138, F-140, F-141, F-144, F-149, F-150, F-172, F-174, F-175, F-179, F-180, F-181, F-192, F-195, F-197, F-198]
---

# 基础查询与变更示例

本文以一个简化的电商系统为背景，给出一份完整可运行的 GraphQL Schema，并围绕它演示三种操作类型（query、mutation、subscription）的核心语法：字段选择、嵌套对象、参数、别名、片段以及变量。每个示例都附带对应的 JSON 响应，帮助建立"查询形状即响应形状"的心智模型（F-006）。

## 完整 Schema

以下 Schema 定义了 Query、Mutation、Subscription 三个根操作类型（F-103、F-104、F-105），以及 User、Product、Order 等业务对象。由于使用了默认根类型名 `Query`/`Mutation`/`Subscription`，可以省略显式的 `schema { ... }` 声明（F-108、F-109）。

```graphql
scalar DateTime

type Query {
  user(id: ID!): User
  product(id: ID!): Product
  order(id: ID!): Order
  products(categoryId: ID, limit: Int = 10): [Product!]!
  orders(status: OrderStatus, limit: Int = 10): [Order!]!
}

type Mutation {
  createOrder(input: CreateOrderInput!): Order!
  cancelOrder(orderId: ID!): Order!
}

type Subscription {
  orderStatusUpdated(orderId: ID!): Order!
}

type User {
  id: ID!
  name: String!
  email: String!
  createdAt: DateTime!
  orders(status: OrderStatus): [Order!]!
}

type Product {
  id: ID!
  name: String!
  price: Float!
  description: String
  inStock: Boolean!
  tags: [String!]!
  category: Category!
}

type Category {
  id: ID!
  name: String!
}

type Order {
  id: ID!
  status: OrderStatus!
  items: [OrderItem!]!
  total: Float!
  createdAt: DateTime!
  buyer: User!
}

type OrderItem {
  product: Product!
  quantity: Int!
  unitPrice: Float!
  subtotal: Float!
}

enum OrderStatus {
  PENDING
  PAID
  SHIPPED
  DELIVERED
  CANCELLED
}

input CreateOrderInput {
  userId: ID!
  items: [OrderItemInput!]!
  note: String
}

input OrderItemInput {
  productId: ID!
  quantity: Int!
}
```

几个要点：

- `id: ID!`、`name: String!` 等使用了 Non-Null 标记 `!`，表示这些字段永不为 null（F-195、F-197）；
- `[Product!]!` 表示列表本身不为 null，且列表中每个元素也不为 null（F-192）；
- `description: String` 没有 `!`，是可为 null 的字段；
- `CreateOrderInput` 和 `OrderItemInput` 是输入对象类型，只能用作参数（F-179、F-182）；
- `OrderStatus` 是枚举类型，值为不加引号的名称（F-075、F-176）。

## Query 示例

### 字段选择与嵌套对象

GraphQL 查询是分层的选择集（SelectionSet），由 `{` 和 `}` 包裹一个或多个 Selection（F-042）。对对象类型必须继续选择子字段，直到叶子字段（标量或枚举）（F-044）。

查询指定用户及其订单：

```graphql
query GetUserWithOrders {
  user(id: "u_1") {
    id
    name
    email
    orders {
      id
      status
      total
      createdAt
    }
  }
}
```

响应：

```json
{
  "data": {
    "user": {
      "id": "u_1",
      "name": "张明",
      "email": "zhangming@example.com",
      "orders": [
        {
          "id": "o_1001",
          "status": "DELIVERED",
          "total": 259.8,
          "createdAt": "2026-07-15T08:30:00Z"
        },
        {
          "id": "o_1002",
          "status": "PENDING",
          "total": 89.0,
          "createdAt": "2026-08-20T14:05:00Z"
        }
      ]
    }
  }
}
```

响应数据的形状与查询选择集完全一致：查询里有哪些字段，响应里就有哪些字段（F-008）。字段顺序也与请求顺序保持一致。

### 简写形式

当文档只包含一个无变量、无指令的 query 操作时，可以省略 `query` 关键字和操作名（F-037）：

```graphql
{
  product(id: "p_5") {
    id
    name
    price
    inStock
  }
}
```

响应：

```json
{
  "data": {
    "product": {
      "id": "p_5",
      "name": "无线蓝牙耳机",
      "price": 299.0,
      "inStock": true
    }
  }
}
```

### 参数（Arguments）

字段可以带参数，参数写在括号中，形式为 `Name: Value`（F-045）。参数顺序不影响语义（F-046）。

```graphql
query GetProductsByCategory {
  products(categoryId: "c_2", limit: 3) {
    id
    name
    price
    tags
  }
}
```

响应：

```json
{
  "data": {
    "products": [
      {
        "id": "p_3",
        "name": "机械键盘",
        "price": 459.0,
        "tags": ["键盘", "办公", "机械轴"]
      },
      {
        "id": "p_7",
        "name": "人体工学鼠标",
        "price": 189.0,
        "tags": ["鼠标", "办公"]
      },
      {
        "id": "p_9",
        "name": "显示器支架",
        "price": 129.0,
        "tags": ["支架", "办公"]
      }
    ]
  }
}
```

枚举值在查询中直接写名称（如 `SHIPPED`），不加引号；字符串值需要加双引号（F-075）。

```graphql
query GetShippedOrders {
  orders(status: SHIPPED, limit: 5) {
    id
    status
    total
  }
}
```

### 别名（Alias）

别名允许在同一次查询中用不同的 response name 请求相同字段，语法为 `Alias: Name`（F-047）。这在需要对比不同参数结果时特别有用。

```graphql
query CompareOrders {
  pending: orders(status: PENDING) {
    id
    total
  }
  delivered: orders(status: DELIVERED) {
    id
    total
  }
}
```

响应：

```json
{
  "data": {
    "pending": [
      { "id": "o_1002", "total": 89.0 }
    ],
    "delivered": [
      { "id": "o_1001", "total": 259.8 }
    ]
  }
}
```

响应中的键名是别名（`pending`、`delivered`），而非原始字段名。

### 片段（Fragment）

片段是可复用的选择集，使用 `fragment FragmentName on Type` 定义，通过 `...FragmentName` 展开（F-048、F-049、F-051）。片段不能定义在标量或输入类型上，只能用于对象、接口和联合类型（F-053）。

```graphql
query GetOrderDetails {
  order(id: "o_1001") {
    ...OrderCore
    buyer {
      ...UserCore
    }
    items {
      product {
        ...ProductCore
      }
      quantity
      subtotal
    }
  }
}

fragment OrderCore on Order {
  id
  status
  total
  createdAt
}

fragment UserCore on User {
  id
  name
  email
}

fragment ProductCore on Product {
  id
  name
  price
}
```

响应：

```json
{
  "data": {
    "order": {
      "id": "o_1001",
      "status": "DELIVERED",
      "total": 259.8,
      "createdAt": "2026-07-15T08:30:00Z",
      "buyer": {
        "id": "u_1",
        "name": "张明",
        "email": "zhangming@example.com"
      },
      "items": [
        {
          "product": {
            "id": "p_3",
            "name": "机械键盘",
            "price": 459.0
          },
          "quantity": 1,
          "subtotal": 459.0
        }
      ]
    }
  }
}
```

片段在展开位置被内联替换，最终响应形状与直接写出所有字段相同。片段中使用的变量必须在传递性消费它的顶层操作中声明（F-085）。

### 内联片段（Inline Fragment）

内联片段无需单独命名，直接在选择集中用 `... on Type { ... }` 书写（F-054）。适用于只在一处使用、无需复用的类型条件选择。

```graphql
query GetProductWithContext {
  product(id: "p_3") {
    id
    name
    ... on Product {
      price
      inStock
      category {
        name
      }
    }
  }
}
```

## Mutation 示例

mutation 用于先写入后获取（F-040）。mutation 顶级选择集必须串行执行，以防止副作用竞态（F-321、F-322）。

### 创建订单

```graphql
mutation PlaceOrder {
  createOrder(input: {
    userId: "u_1"
    items: [
      { productId: "p_3", quantity: 1 }
    ]
    note: "请工作日送货"
  }) {
    id
    status
    total
    createdAt
    items {
      product {
        name
      }
      quantity
      subtotal
    }
  }
}
```

响应：

```json
{
  "data": {
    "createOrder": {
      "id": "o_1003",
      "status": "PENDING",
      "total": 459.0,
      "createdAt": "2026-08-23T10:15:00Z",
      "items": [
        {
          "product": {
            "name": "机械键盘"
          },
          "quantity": 1,
          "subtotal": 459.0
        }
      ]
    }
  }
}
```

输入对象字面量用 `{ field: value }` 表示（F-078），列表值用 `[ ... ]` 表示（F-077）。

### 取消订单

```graphql
mutation CancelExistingOrder {
  cancelOrder(orderId: "o_1003") {
    id
    status
  }
}
```

响应：

```json
{
  "data": {
    "cancelOrder": {
      "id": "o_1003",
      "status": "CANCELLED"
    }
  }
}
```

## Subscription 示例

subscription 是长连接请求，服务端随时间推送事件流，每个事件触发一次操作执行并产生一个结果（F-040、F-323）。

```graphql
subscription WatchOrderStatus {
  orderStatusUpdated(orderId: "o_1001") {
    id
    status
    items {
      product {
        name
      }
      quantity
    }
    total
  }
}
```

与 query/mutation 不同，subscription 的响应是一个**结果流**（response stream），每个事件是一个独立的 execution result（F-383）。以下是服务端在订单状态变化时依次推送的三条消息：

第一条（订单已付款）：

```json
{
  "data": {
    "orderStatusUpdated": {
      "id": "o_1001",
      "status": "PAID",
      "items": [
        { "product": { "name": "机械键盘" }, "quantity": 1 }
      ],
      "total": 459.0
    }
  }
}
```

第二条（订单已发货）：

```json
{
  "data": {
    "orderStatusUpdated": {
      "id": "o_1001",
      "status": "SHIPPED",
      "items": [
        { "product": { "name": "机械键盘" }, "quantity": 1 }
      ],
      "total": 459.0
    }
  }
}
```

第三条（订单已送达）：

```json
{
  "data": {
    "orderStatusUpdated": {
      "id": "o_1001",
      "status": "DELIVERED",
      "items": [
        { "product": { "name": "机械键盘" }, "quantity": 1 }
      ],
      "total": 459.0
    }
  }
}
```

subscription 顶级选择集必须恰好包含一个根字段（F-258），规范不规定传输协议或消息确认机制（F-329），实现可使用 WebSocket、SSE 等。

## 变量使用示例

变量允许将动态值从查询文本中分离，避免字符串拼接。变量以 `$Name` 表示（F-080），在操作顶部的变量定义中声明类型和默认值（F-081、F-082、F-083）。变量在整个操作执行期间有效（F-084）。

### 带变量的 Query

```graphql
query GetUserOrders($userId: ID!, $status: OrderStatus) {
  user(id: $userId) {
    id
    name
    orders(status: $status) {
      id
      status
      total
    }
  }
}
```

变量值（通过 HTTP POST 的 `variables` 字段单独传递）：

```json
{
  "userId": "u_1",
  "status": "PENDING"
}
```

响应：

```json
{
  "data": {
    "user": {
      "id": "u_1",
      "name": "张明",
      "orders": [
        {
          "id": "o_1002",
          "status": "PENDING",
          "total": 89.0
        }
      ]
    }
  }
}
```

### 带变量和默认值的 Mutation

变量可以声明默认值（`= Value`），未提供时使用默认值（F-083）。

```graphql
mutation PlaceOrderWithVars(
  $input: CreateOrderInput!
  $quantity: Int! = 1
) {
  createOrder(input: $input) {
    id
    status
    total
  }
}
```

变量值：

```json
{
  "input": {
    "userId": "u_2",
    "items": [
      { "productId": "p_7", "quantity": 2 }
    ]
  }
}
```

响应：

```json
{
  "data": {
    "createOrder": {
      "id": "o_1004",
      "status": "PENDING",
      "total": 378.0
    }
  }
}
```

### 使用 null 值与默认值

GraphQL 有两种表示值缺失的方式：显式提供 `null` 和隐式不提供值（F-074）。对于有默认值的变量，不传该变量时使用默认值；显式传 `null` 则覆盖默认值为 null（若类型允许）。

```graphql
query GetOrdersWithDefault(
  $status: OrderStatus = PENDING
  $limit: Int = 10
) {
  orders(status: $status, limit: $limit) {
    id
    status
    total
  }
}
```

不传任何变量时，等价于查询 `status: PENDING, limit: 10`。

### 多操作文档与 operationName

一个文档可包含多个操作，但每个操作必须命名；提交时通过 `operationName` 指定执行哪个（F-036、F-308）。

```graphql
query FetchUser {
  user(id: "u_1") {
    id
    name
  }
}

mutation CreateNewOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    id
    total
  }
}
```

HTTP 请求体示例：

```json
{
  "query": "...上面的完整文档...",
  "operationName": "FetchUser",
  "variables": {}
}
```

## 值类型速查

GraphQL 输入值支持以下类型（F-056）：

| 类型 | 语法示例 | 说明 |
|------|---------|------|
| Int | `42` | 整数（F-057） |
| Float | `3.14` | 浮点数（F-061） |
| String | `"hello"` | 字符串（F-065） |
| Boolean | `true` / `false` | 布尔值（F-064） |
| Null | `null` | 空值（F-073） |
| Enum | `PENDING` | 枚举值，不加引号（F-075） |
| List | `[1, 2, 3]` | 列表（F-077） |
| Object | `{ key: "value" }` | 输入对象（F-078） |
| Variable | `$userId` | 变量引用（F-080） |

## 相关概念

- [查询语言基础：文档、操作与选择集](../concepts/01-query-language-basics.md) — 本文语法的规范来源：Document、OperationDefinition、SelectionSet、Field、Arguments、Value、Variables
- [Schema 与类型系统入门](../concepts/02-schema-and-types.md) — 本文 Schema 中使用的标量、对象、枚举、输入对象类型定义
- [指令、包装类型与输入系统](../concepts/04-directives-and-wrapping-types.md) — Non-Null (`!`) 和 List (`[]`) 包装类型的语义
- [片段、变量作用域与 Schema Coordinates](../concepts/09-fragments-and-advanced-syntax.md) — 片段复用与变量作用域的深入讨论
- [响应格式、错误冒泡与序列化](../concepts/07-response-and-errors.md) — 本文 JSON 响应的格式规范
