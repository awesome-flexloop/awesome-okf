---
type: concept
title: "Start 开发服务器"
description: "myst start开发服务器架构：双服务器模型、WebSocket热重载、Express内容服务与模板渲染"
tags: [myst-cli, start, dev-server, express, websocket, watch]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/start.ts"
    facts: [F-005]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/site/start.ts"
    facts: [F-061, F-062, F-063]
---

# Start 开发服务器

`myst start` 命令启动一个本地开发服务器，支持实时预览、热重载和交互式网站功能。

## 双服务器架构

start 命令启动两个服务器：

| 服务器 | 默认端口 | 作用 |
|--------|----------|------|
| 内容服务器（Content Server） | 3100-3200（自动选择） | Express 应用，提供 config.json、页面内容 JSON、静态资源 |
| 应用服务器（Application Server） | 可通过 --port 指定 | 渲染站点 UI，通常是 Next.js 或模板渲染的前端 |

通过 `--headless` 选项可以只启动内容服务器（无 UI），适用于仅需要内容 API 的场景。

## 内容服务器实现

内容服务器基于 Express 构建：

```ts
const app = express();
app.use(cors());  // 启用 CORS 支持跨域
app.get('/', (req, res) => {
  res.json({
    version,
    links: { site: `http://${host}:${port}/config.json` },
  });
});
```

### 端口选择策略

使用 `get-port` 库在 3100-3200 范围内查找空闲端口：
1. 优先尝试用户指定的 `--server-port`
2. 如端口被占用（EADDRINUSE），自动在范围内查找下一个空闲端口
3. `--port` 选项控制应用服务器端口，也支持 `PORT` 环境变量

## WebSocket 热重载

内容服务器集成 WebSocket 服务器（ws 库），实现：
- **实时日志推送**：构建错误和警告即时推送到浏览器
- **热重载**：文件变化时通知客户端刷新
- **双向通信**：客户端可以发送指令到服务器

## 文件监视（Watch）

通过 `watchContent()` 监视项目文件变化：
- 监视 markdown 文件、notebook、配置文件
- 文件变化时触发增量重建
- 通过 WebSocket 通知浏览器刷新

## 关键选项

| 选项 | 说明 |
|------|------|
| `--port <port>` | 应用服务器端口（也读 PORT 环境变量） |
| `--server-port <port>` | 内容服务器端口（也读 SERVER_PORT 环境变量） |
| `--headless` | 仅启动内容服务器，无 UI |
| `--keep-host` | 保留 HOST 环境变量（默认改为 localhost） |
| `--template <path>` | 使用指定模板替代 myst.yml 中的模板 |
| `--execute` | 启动时执行 Notebook |
| `--max-size-webp <size>` | WebP 转换阈值（MB） |

## 服务器生命周期

```
myst start
  ├─ startContentServer()
  │   ├─ 创建 Express app
  │   ├─ 注册 CORS
  │   ├─ 注册路由（/, /config.json, /content/*, /public/*）
  │   ├─ 创建 WebSocket 服务器
  │   └─ 监听端口
  ├─ buildSite() 首次构建
  ├─ installSiteTemplate() 安装站点模板
  ├─ watchContent() 开始监视文件
  └─ 启动应用服务器（非 headless 模式）
```

## 与 build --watch 的区别

- `myst build --watch`：监视文件变化并重新执行 build 导出（适合生成静态文件），但不提供 HTTP 服务
- `myst start`：提供完整的开发服务器体验，包括实时预览、热重载、交互式功能（推荐用于开发）

## HOST 环境变量处理

默认情况下，start 命令会将 `HOST` 环境变量改为 `localhost` 以确保安全。如果需要保留原始 HOST 值（例如在 Docker 容器中绑定 0.0.0.0），使用 `--keep-host` 选项。

## 相关概念

- [Build 管线](01-build-pipeline.md) — 构建和导出流程
- [模板系统](06-template-system.md) — 站点模板安装和渲染
- [会话与缓存](08-session-cache.md) — Session 在服务器中的角色
