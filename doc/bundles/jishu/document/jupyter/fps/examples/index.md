# FPS 示例文档索引

本目录包含 FPS 框架的实践示例，建议配合概念文档阅读。

## 基础示例

| 示例 | 说明 |
|------|------|
| [01-first-app.md](01-first-app.md) | 最简FPS应用，体验模块生命周期和CLI参数 |
| [02-sharing-objects.md](02-sharing-objects.md) | 模块间通过put/get共享对象，异步依赖注入 |

## Web应用

| 示例 | 说明 |
|------|------|
| [03-web-server.md](03-web-server.md) | 使用FastAPIModule/ServerModule构建Web服务器 |
| [04-declarative-config.md](04-declarative-config.md) | JSON配置文件声明式组装应用 |

## 核心机制

| 示例 | 说明 |
|------|------|
| [05-standalone-context.md](05-standalone-context.md) | 独立使用Context管理资源生命周期 |
| [06-signals-usage.md](06-signals-usage.md) | Signal事件通知的回调与迭代器模式 |

```{toctree}
:hidden:
:maxdepth: 7

01-first-app
02-sharing-objects
03-web-server
04-declarative-config
05-standalone-context
06-signals-usage
```
