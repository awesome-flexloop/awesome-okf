---
type: example
title: "Python 服务端实战"
description: "基于 graphql-core 从零构建可运行的 GraphQL 服务器：SDL 定义、Root resolver 类、graphql_sync 执行、HTTP handler，以及 Strawberry/Ariadne 等 code-first 替代方案。"
sources:
  - resource: /references/mcp-server-source.md
    facts: [F-437, F-561, F-562, F-563, F-564, F-565, F-566, F-567, F-568, F-569, F-570, F-571, F-572, F-573]
---

# Python 服务端实战

本文展示如何使用 Python 的 `graphql-core` 库从零构建一个可运行的 GraphQL 服务器。我们将以一个简单的任务管理系统为场景，完整覆盖 Schema 定义（SDL）、Root resolver 类、`graphql_sync` 同步执行、HTTP 请求处理，以及 query 和 mutation 的 resolver 实现。代码模式参考了测试服务器中 `Root` 类、`_build_connection` 和 `make_handler` 的实现方式（F-564~F-573）。

## graphql-core 简介

`graphql-core` 是 GraphQL 规范的 Python 移植，提供 Schema 构建、查询解析、验证和执行引擎。它是 Strawberry、Ariadne 等高层框架的底层依赖。核心 API 包括（F-437）：

- `build_schema(sdl)`：从 GraphQL Schema 语言字符串构建 Schema；
- `graphql_sync(schema, query, ...)`：同步执行查询，返回 `ExecutionResult`；
- `print_schema(schema)`：将 Schema 打印为 SDL；
- `get_introspection_query()`：获取内省查询字符串。

## 安装

```bash
pip install graphql-core
```

本文代码仅依赖 `graphql-core` 和 Python 标准库（`http.server`、`json`、`argparse`），无需额外框架。

## 完整服务器

以下是一个单文件、可直接运行的 GraphQL 服务器。它使用内存数据存储，支持查询任务列表、按 ID 获取任务、按状态筛选、创建任务和更新任务状态。

### Schema 定义（SDL）

```graphql
type Query {
  task(id: ID!): Task
  tasks(status: TaskStatus, limit: Int = 10): [Task!]!
  tasksConnection(first: Int = 10, after: ID): TaskConnection!
  projects: [Project!]!
}

type Mutation {
  createTask(input: CreateTaskInput!): Task!
  updateTaskStatus(id: ID!, status: TaskStatus!): Task!
}

type Task {
  id: ID!
  title: String!
  description: String
  status: TaskStatus!
  priority: Priority!
  assignee: User
  project: Project!
  tags: [String!]!
  createdAt: String!
  updatedAt: String
}

type User {
  id: ID!
  name: String!
  email: String!
}

type Project {
  id: ID!
  name: String!
  tasks: [Task!]!
}

enum TaskStatus {
  TODO
  IN_PROGRESS
  DONE
  CANCELLED
}

enum Priority {
  LOW
  MEDIUM
  HIGH
}

input CreateTaskInput {
  title: String!
  description: String
  priority: Priority = MEDIUM
  assigneeId: ID
  projectId: ID!
  tags: [String!]
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: ID
  endCursor: ID
}

type TaskEdge {
  cursor: ID!
  node: Task!
}

type TaskConnection {
  totalCount: Int!
  pageInfo: PageInfo!
  edges: [TaskEdge!]!
}
```

### Python 实现

将以下代码保存为 `server.py`：

```python
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from graphql import build_schema, graphql_sync

SCHEMA_SDL = """
type Query {
  task(id: ID!): Task
  tasks(status: TaskStatus, limit: Int = 10): [Task!]!
  tasksConnection(first: Int = 10, after: ID): TaskConnection!
  projects: [Project!]!
}

type Mutation {
  createTask(input: CreateTaskInput!): Task!
  updateTaskStatus(id: ID!, status: TaskStatus!): Task!
}

type Task {
  id: ID!
  title: String!
  description: String
  status: TaskStatus!
  priority: Priority!
  assignee: User
  project: Project!
  tags: [String!]!
  createdAt: String!
  updatedAt: String
}

type User {
  id: ID!
  name: String!
  email: String!
}

type Project {
  id: ID!
  name: String!
  tasks: [Task!]!
}

enum TaskStatus {
  TODO
  IN_PROGRESS
  DONE
  CANCELLED
}

enum Priority {
  LOW
  MEDIUM
  HIGH
}

input CreateTaskInput {
  title: String!
  description: String
  priority: Priority = MEDIUM
  assigneeId: ID
  projectId: ID!
  tags: [String!]
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: ID
  endCursor: ID
}

type TaskEdge {
  cursor: ID!
  node: Task!
}

type TaskConnection {
  totalCount: Int!
  pageInfo: PageInfo!
  edges: [TaskEdge!]!
}
"""


class Root:
    def __init__(self) -> None:
        self.users = {
            "u_1": {"id": "u_1", "name": "陈晨", "email": "chenchen@example.com"},
            "u_2": {"id": "u_2", "name": "林峰", "email": "linfeng@example.com"},
        }

        self.projects = {
            "p_1": {"id": "p_1", "name": "网站重构", "tasks": []},
            "p_2": {"id": "p_2", "name": "移动 App", "tasks": []},
        }

        self.tasks: dict[str, dict[str, Any]] = {
            "t_1": {
                "id": "t_1",
                "title": "设计首页原型",
                "description": "完成首页高保真原型设计",
                "status": "DONE",
                "priority": "HIGH",
                "assignee": self.users["u_1"],
                "project": self.projects["p_1"],
                "tags": ["设计", "前端"],
                "createdAt": "2026-08-01T09:00:00Z",
                "updatedAt": "2026-08-05T16:00:00Z",
            },
            "t_2": {
                "id": "t_2",
                "title": "实现登录接口",
                "description": "使用 JWT 实现用户认证",
                "status": "IN_PROGRESS",
                "priority": "HIGH",
                "assignee": self.users["u_2"],
                "project": self.projects["p_1"],
                "tags": ["后端", "安全"],
                "createdAt": "2026-08-10T10:30:00Z",
                "updatedAt": None,
            },
            "t_3": {
                "id": "t_3",
                "title": "编写 API 文档",
                "description": None,
                "status": "TODO",
                "priority": "MEDIUM",
                "assignee": None,
                "project": self.projects["p_2"],
                "tags": ["文档"],
                "createdAt": "2026-08-15T14:00:00Z",
                "updatedAt": None,
            },
        }

        for task in self.tasks.values():
            task["project"]["tasks"].append(task)

        self._next_id = 4

    def _next_task_id(self) -> str:
        task_id = f"t_{self._next_id}"
        self._next_id += 1
        return task_id

    def task(self, info, id: str):
        return self.tasks.get(id)

    def tasks(self, info, status: str | None = None, limit: int = 10):
        result = list(self.tasks.values())
        if status:
            result = [t for t in result if t["status"] == status]
        return result[: max(0, int(limit))]

    def projects(self, info):
        return list(self.projects.values())

    def _build_connection(
        self,
        items: list[dict],
        first: int = 10,
        after: str | None = None,
    ) -> dict:
        total_count = len(items)
        first = max(1, min(first, 100))

        start_index = 0
        if after:
            for i, item in enumerate(items):
                if item.get("id") == after:
                    start_index = i + 1
                    break

        end_index = start_index + first
        page_items = items[start_index:end_index]

        edges = [{"cursor": item["id"], "node": item} for item in page_items]

        page_info = {
            "hasNextPage": end_index < total_count,
            "hasPreviousPage": start_index > 0,
            "startCursor": edges[0]["cursor"] if edges else None,
            "endCursor": edges[-1]["cursor"] if edges else None,
        }

        return {
            "totalCount": total_count,
            "pageInfo": page_info,
            "edges": edges,
        }

    def tasksConnection(
        self, info, first: int = 10, after: str | None = None
    ) -> dict:
        items = sorted(self.tasks.values(), key=lambda t: t["createdAt"])
        return self._build_connection(items, first=first, after=after)

    def createTask(self, info, input: dict) -> dict:
        project_id = input.get("projectId")
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Unknown projectId: {project_id}")

        assignee_id = input.get("assigneeId")
        assignee = self.users.get(assignee_id) if assignee_id else None

        task = {
            "id": self._next_task_id(),
            "title": input["title"],
            "description": input.get("description"),
            "status": "TODO",
            "priority": input.get("priority", "MEDIUM"),
            "assignee": assignee,
            "project": project,
            "tags": input.get("tags") or [],
            "createdAt": "2026-08-23T12:00:00Z",
            "updatedAt": None,
        }

        self.tasks[task["id"]] = task
        project["tasks"].append(task)
        return task

    def updateTaskStatus(self, info, id: str, status: str) -> dict:
        task = self.tasks.get(id)
        if not task:
            raise ValueError(f"Unknown task id: {id}")

        valid = {"TODO", "IN_PROGRESS", "DONE", "CANCELLED"}
        if status not in valid:
            raise ValueError(f"Invalid status: {status}")

        task["status"] = status
        task["updatedAt"] = "2026-08-23T12:30:00Z"
        return task


def _json_response(
    handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]
) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "content-type")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("content-length") or "0")
    raw = handler.rfile.read(length) if length else b""
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def _format_result(result) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if result.data is not None:
        payload["data"] = result.data
    if result.errors:
        payload["errors"] = [err.formatted for err in result.errors]
    return payload


def make_handler(schema_sdl: str):
    schema = build_schema(schema_sdl)
    root = Root()

    class Handler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "content-type")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.end_headers()

        def do_GET(self):
            if self.path == "/healthz":
                _json_response(self, 200, {"ok": True})
                return
            _json_response(self, 404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/graphql":
                _json_response(self, 404, {"error": "not found"})
                return
            try:
                body = _read_json(self)
                query = body.get("query")
                variables = body.get("variables") or {}
                operation_name = body.get("operationName")
                if not query:
                    _json_response(
                        self, 400, {"error": "Missing 'query' in JSON body"}
                    )
                    return
                result = graphql_sync(
                    schema,
                    query,
                    variable_values=variables,
                    operation_name=operation_name,
                    root_value=root,
                )
                payload = _format_result(result)
                status = 200 if not result.errors else 400
                _json_response(self, status, payload)
            except Exception as exc:
                _json_response(self, 500, {"error": str(exc)})

        def log_message(self, format, *args):
            return

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal GraphQL server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4000)
    args = parser.parse_args()

    handler = make_handler(SCHEMA_SDL)
    httpd = HTTPServer((args.host, args.port), handler)
    print(f"GraphQL server running at http://{args.host}:{args.port}/graphql")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 核心模式解析

### 1. Root Value 模式

`graphql_sync(schema, query, root_value=root)` 的 `root_value` 参数是根值对象。执行引擎在解析 Query/Mutation 根字段时，将 `root_value` 作为父值传入默认 resolver。默认 resolver 会在父值上查找与字段同名的属性或键——如果是可调用对象（方法），则调用它并传入 `info` 和参数。

这就是为什么 `Root` 类的方法名直接对应 Schema 中的根字段名（F-566）：

| Schema 根字段 | Root 方法 |
|--------------|-----------|
| `task(id: ID!)` | `def task(self, info, id: str)` |
| `tasks(status, limit)` | `def tasks(self, info, status=None, limit=10)` |
| `createTask(input:)` | `def createTask(self, info, input: dict)` |

对于嵌套字段（如 `Task.project`），父值是字典，默认 resolver 通过键名 `project` 自动取值，无需额外编写 resolver。

### 2. Resolver 方法签名

resolver 方法遵循统一签名：`method_name(self, info, **kwargs)`。

- `self`：Root 实例（根字段）或父对象（嵌套字段，若使用类实例而非字典）；
- `info`：`GraphQLResolveInfo` 对象，包含字段名、Schema、上下文、变量等执行信息；
- `**kwargs`：Schema 中定义的参数，名称必须与参数名匹配。

枚举类型的参数值以**字符串**形式传入（如 `"IN_PROGRESS"`），因为 graphql-core 内部将枚举值序列化为字符串。输入对象类型参数以**字典**形式传入。

### 3. Connection 分页构建

`_build_connection` 方法实现了游标分页（F-568）：

- `first` 限制每页数量，上限 100；
- `after` 是上一页最后一条记录的 ID（即 cursor）；
- 通过遍历 items 找到 cursor 位置，从下一项开始切片；
- 返回 `totalCount`、`pageInfo`（含 `hasNextPage`/`hasPreviousPage`/`startCursor`/`endCursor`）和 `edges`（每条含 `cursor` 和 `node`）。

这种模式的优势是游标锚定具体记录 ID，在数据插入/删除时不会像 offset 分页那样出现重复或跳过。

### 4. Mutation 中的错误处理

在 resolver 中抛出 `ValueError` 等异常时，graphql-core 会将其捕获为 execution error，放入结果的 `errors` 列表，同时已成功解析的其他字段仍会出现在 `data` 中。错误对象通过 `err.formatted` 获取标准格式（含 `message`、`locations`、`path`）。

### 5. HTTP Handler 工厂

`make_handler(schema_sdl)` 通过闭包创建 `Handler` 类（F-572）：

- Schema 只构建一次，在请求间复用；
- `Root()` 实例在请求间共享，实现内存数据持久化；
- `GET /healthz` 提供健康检查；
- `POST /graphql` 接收 JSON 格式的请求体（含 `query`、`variables`、`operationName`），调用 `graphql_sync` 执行，返回标准 JSON 响应；
- CORS 头允许浏览器跨域访问（F-562）。

## 运行与测试

### 启动服务器

```bash
python server.py --host 127.0.0.1 --port 4000
```

### 查询任务

```bash
curl -X POST http://127.0.0.1:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { tasks(status: IN_PROGRESS) { id title status priority assignee { name email } } }"
  }'
```

响应：

```json
{
  "data": {
    "tasks": [
      {
        "id": "t_2",
        "title": "实现登录接口",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "assignee": {
          "name": "林峰",
          "email": "linfeng@example.com"
        }
      }
    ]
  }
}
```

### 创建任务（Mutation + 变量）

```bash
curl -X POST http://127.0.0.1:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation Create($input: CreateTaskInput!) { createTask(input: $input) { id title status priority tags } }",
    "variables": {
      "input": {
        "title": "修复登录页样式",
        "description": "移动端按钮错位",
        "priority": "HIGH",
        "projectId": "p_1",
        "assigneeId": "u_1",
        "tags": ["前端", "Bug"]
      }
    }
  }'
```

### 游标分页查询

```bash
curl -X POST http://127.0.0.1:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ tasksConnection(first: 2) { totalCount pageInfo { hasNextPage endCursor } edges { cursor node { id title } } } }"
  }'
```

使用返回的 `endCursor` 作为 `after` 变量获取下一页：

```bash
curl -X POST http://127.0.0.1:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query($after: ID) { tasksConnection(first: 2, after: $after) { pageInfo { hasNextPage } edges { node { id title } } } }",
    "variables": { "after": "t_2" }
  }'
```

## code-first 替代方案

`graphql-core` 是 schema-first 方式——先用 SDL 定义 Schema，再通过 root_value 绑定 resolver。Python 生态还提供了 code-first 方案，直接用 Python 类型注解定义 Schema。

### Strawberry

Strawberry 基于 Python dataclass 和类型注解，使用装饰器定义类型（F-636）：

```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from enum import Enum


@strawberry.enum
class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


@strawberry.type
class User:
    id: strawberry.ID
    name: str
    email: str


@strawberry.type
class Task:
    id: strawberry.ID
    title: str
    status: TaskStatus
    assignee: User | None


@strawberry.type
class Query:
    @strawberry.field
    def task(self, id: strawberry.ID) -> Task | None:
        ...

    @strawberry.field
    def tasks(self, status: TaskStatus | None = None) -> list[Task]:
        ...


schema = strawberry.Schema(query=Query)
```

Strawberry 自动从类型注解生成 SDL，适合偏好 Python 原生类型体验的团队。

### Ariadne

Ariadne 是 schema-first 库，但使用装饰器绑定 resolver，比手动 root_value 更灵活（F-632）：

```python
from ariadne import QueryType, MutationType, make_executable_schema

type_defs = """
    type Query {
        task(id: ID!): Task
        tasks(status: TaskStatus): [Task!]!
    }
    type Task { id: ID! title: String! status: TaskStatus! }
    enum TaskStatus { TODO IN_PROGRESS DONE CANCELLED }
"""

query = QueryType()
mutation = MutationType()


@query.field("task")
def resolve_task(*_, id):
    return tasks_store.get(id)


@query.field("tasks")
def resolve_tasks(*_, status=None):
    result = list(tasks_store.values())
    if status:
        result = [t for t in result if t["status"] == status]
    return result


schema = make_executable_schema(type_defs, query, mutation)
```

### 选型建议

| 方案 | 风格 | 适用场景 |
|------|------|---------|
| graphql-core | schema-first（手动绑定） | 学习原理、极简服务、作为其他库基础 |
| Strawberry | code-first（类型注解） | 新项目、偏好 Python 原生类型、与 FastAPI 集成 |
| Ariadne | schema-first（装饰器绑定） | 已有 SDL、需要灵活的 resolver 组织 |
| Graphene | code-first（经典 ORM 风格） | Django/SQLAlchemy 集成、遗留项目 |

## 相关概念

- [Python 生态：客户端与服务端实践](/concepts/10-python-ecosystem.md) — Python GraphQL 生态全景，graphql-core 的定位及客户端/服务端库对比
- [执行引擎：字段解析与值完成](/concepts/06-execution.md) — graphql_sync 的执行流程对应规范的 ExecuteRequest 算法、resolver 调用与值完成
- [响应格式、错误冒泡与序列化](/concepts/07-response-and-errors.md) — ExecutionResult 的 data/errors 结构、错误对象格式与 Non-Null 冒泡
- [内省系统：GraphQL 的自描述机制](/concepts/08-introspection.md) — get_introspection_query 与 build_client_schema 的内省流程
- [Schema 设计实战](/examples/schema-design.md) — 本文 Schema 中使用的 Connection 分页、枚举、输入对象等设计模式
- [错误处理与 Non-Null 冒泡](/examples/error-handling.md) — resolver 抛错时 graphql-core 如何处理 execution error 和部分数据
