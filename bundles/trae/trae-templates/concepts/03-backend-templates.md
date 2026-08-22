---
type: Concept
title: 后端服务模板
description: backend-service 分类包含 5 个模板，覆盖 Python/FastAPI、Node.js/Express、Go/Gin、Java/Spring Boot、Rust/Actix 五种主流后端语言和框架，每个模板提供单文件入口和最小可用的 API 服务起点。
tags: [trae-templates, backend, fastapi, express, gin, spring-boot, actix]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 后端服务模板总览

backend-service 分类包含 5 个模板，覆盖 5 种主流后端语言和 Web 框架：

| 模板 | 语言 | 框架 | 默认端口 | 启动命令 | 文件数 |
|------|------|------|----------|----------|--------|
| fastapi-service | Python 3.8+ | FastAPI + Uvicorn | 8000 | `uvicorn app.main:app --reload` | 4 |
| nodejs-express | Node.js | Express | 3000 | `npm start` | 5 |
| go-gin-service | Go | Gin | 8080 | `go run main.go` | 5 |
| java-springboot | Java 17+ | Spring Boot | 8080 | `mvn spring-boot:run` | 4 |
| rust-actix | Rust | Actix-web | 8080 | `cargo run` | 5 |

所有后端模板都遵循最小可用原则：单文件入口、一个示例端点、零额外配置。

## fastapi-service：高性能 Python API

**路径**：`templates/backend-service/fastapi-service/`

基于 FastAPI 的高性能 API 服务模板，支持自动交互式 API 文档。

**文件结构**（4 个文件）：
```
fastapi-service/
├── requirements.txt    # fastapi、uvicorn
├── app/
│   └── main.py         # FastAPI 应用入口
├── README.md
└── README.zh-CN.md
```

**技术栈**：FastAPI、Uvicorn（ASGI 服务器）、Python 3.8+

**启动命令**：
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload    # localhost:8000
```

**自动文档**：
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

**特性**：
- 基于 Python 类型提示的自动参数校验
- 自动生成 OpenAPI 文档
- 异步支持（async/await）
- 高性能（接近 Node.js/Go 的吞吐量）

FastAPI 是近年来增长最快的 Python Web 框架，特别适合构建需要自动文档的 API 服务和 AI/ML 模型推理服务。

## nodejs-express：极简 Node.js 服务器

**路径**：`templates/backend-service/nodejs-express/`

Express.js 极简服务器模板，最精简的后端起点。

**文件结构**（5 个文件）：
```
nodejs-express/
├── package.json    # express 依赖
├── index.js        # 单文件服务器
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Node.js、Express、JavaScript

**启动命令**：
```bash
npm install
npm start    # localhost:3000
```

**示例端点**：
- `GET /` 返回 "Hello World!"

**特点**：文件最少（仅一个 `index.js` 业务文件），适合快速原型、全栈 JS 项目和微服务原型。

## go-gin-service：Go REST API

**路径**：`templates/backend-service/go-gin-service/`

Go + Gin Web 框架的 REST API 模板，适合高并发场景。

**文件结构**（5 个文件）：
```
go-gin-service/
├── go.mod      # Go 模块定义
├── main.go     # Gin 路由和处理函数
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Go、Gin Web 框架

**启动命令**：
```bash
go mod tidy     # 下载依赖
go run main.go  # localhost:8080
```

**示例端点**：
- `GET /ping` 返回 JSON `{"message": "pong"}`

**特点**：
- Go 编译为单一二进制，部署简单
- Gin 高性能 HTTP 路由器
- 适合微服务、高并发 API、云原生应用

## java-springboot：Spring Boot 应用

**路径**：`templates/backend-service/java-springboot/`

Spring Boot 极简应用模板，适合企业级 Java 项目。

**文件结构**（4 个文件）：
```
java-springboot/
├── pom.xml                                # Maven 配置（spring-boot-starter-web）
├── src/main/java/com/example/demo/
│   └── DemoApplication.java               # Spring Boot 主类（@SpringBootApplication）
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Java 17+、Spring Boot、Maven

**启动命令**：
```bash
mvn spring-boot:run    # localhost:8080
```

**特点**：
- Spring Boot 自动配置（auto-configuration）
- 内嵌 Tomcat 服务器
- 丰富的生态系统（Spring Data/Spring Security/Spring Cloud）
- 适合企业级应用、微服务架构、复杂业务系统

## rust-actix：Rust 高性能服务

**路径**：`templates/backend-service/rust-actix/`

Rust + Actix-web 服务模板，极致性能和内存安全。

**文件结构**（5 个文件）：
```
rust-actix/
├── Cargo.toml    # Rust 包配置（actix-web 依赖）
├── src/
│   └── main.rs   # Actix-web 应用入口
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Rust、Actix-web

**前提条件**：需要通过 rustup 安装 Rust 工具链。

**启动命令**：
```bash
cargo run    # 127.0.0.1:8080
```

**示例端点**：
- `GET /` 返回 "Hello World from Rust Actix!"

**特点**：
- Actix-web 是性能最高的 Rust Web 框架之一
- 编译时内存安全保证，无 GC 停顿
- 适合高性能代理、系统级服务、安全敏感应用

## 后端模板对比

| 维度 | FastAPI | Express | Gin | Spring Boot | Actix |
|------|---------|---------|-----|-------------|-------|
| **语言** | Python | JS/TS | Go | Java | Rust |
| **性能** | 高 | 中 | 高 | 中 | 极高 |
| **学习曲线** | 低 | 最低 | 低 | 中高 | 高 |
| **自动文档** | ✅ Swagger/ReDoc | ❌ | ❌ | ❌（需加依赖） | ❌ |
| **类型安全** | 类型提示 | ❌ | ✅ | ✅ | ✅ |
| **异步支持** | ✅ | ✅（回调/Promise） | ✅ | ✅ | ✅ |
| **部署方式** | uvicorn/gunicorn | node | 单二进制 | java -jar | 单二进制 |
| **适用场景** | AI/ML API、快速原型 | 全栈 JS、原型 | 高并发微服务 | 企业级应用 | 系统级服务 |
| **文件数** | 4 | 5 | 5 | 4 | 5 |

## 选择建议

| 需求/场景 | 推荐模板 |
|-----------|----------|
| AI/ML 模型 API、需要自动文档 | fastapi-service |
| 全栈 JavaScript、快速原型 | nodejs-express |
| 高并发微服务、云原生部署 | go-gin-service |
| 企业 Java 生态、复杂业务 | java-springboot |
| 极致性能、系统编程、安全敏感 | rust-actix |
| 团队最熟悉的语言 | 选对应语言的模板 |

## 最小可用设计在后端模板中的体现

所有后端模板严格遵循最小可用原则：

- **单文件入口**：index.js/main.go/main.py/main.rs/DemoApplication.java 都是单文件
- **一个示例端点**：每个模板只定义一个 GET 端点验证服务运行
- **零中间件**：不预设 CORS、认证、日志中间件
- **零数据库**：不预设数据库连接/ORM
- **零目录分层**：不预设 controller/service/repository 分层

开发者按需添加路由、中间件、数据库连接、认证等组件。

## 相关概念

- [五维分面分类体系](/concepts/01-template-classification.md)
- [Web 前端模板](/concepts/02-web-frontend-templates.md)
- [移动端和桌面端模板](/concepts/04-mobile-desktop-templates.md)
- [数据与 AI 模板](/concepts/05-data-ai-templates.md)
- [AGENTS.md 开发契约](/concepts/07-agents-contract.md)

## 相关内容

- [源码信源索引](/references/templates-source.md)
