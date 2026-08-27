---
type: example
title: "启动开发服务器"
description: "使用myst start启动本地开发服务器，支持实时预览、热重载和双端口架构"
tags: [myst-cli, start, dev-server, hot-reload, preview]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/site/start.ts"
    facts: [F-061, F-062, F-063]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/start.ts"
    facts: [F-005]
---

# 启动开发服务器

本文档演示如何使用 `myst start` 启动本地开发服务器进行实时预览。

## 基本使用

### 启动服务器

在项目目录中运行：

```bash
myst start
```

服务器会：
1. 自动寻找空闲端口（默认在 3100-3200 范围内）
2. 首次构建站点内容
3. 安装站点模板
4. 开始监视文件变化
5. 在终端显示访问 URL

### 指定端口

```bash
# 指定应用服务器端口
myst start --port 3000

# 指定内容服务器端口
myst start --server-port 3100

# 通过环境变量指定
PORT=3000 SERVER_PORT=3100 myst start
```

### Headless 模式（仅内容API）

```bash
myst start --headless
```

只启动内容服务器（提供 JSON API），不启动应用 UI 服务器。适用于：
- 仅需要内容 API 的场景
- 自定义前端开发
- CI/CD 中的内容验证

### 执行 Notebook 后启动

```bash
myst start --execute
```

启动前执行所有 Jupyter Notebook，确保内容是最新的。

### 使用自定义模板

```bash
myst start --template ./path/to/template
```

临时使用指定模板，覆盖 myst.yml 中的模板配置。

## 开发服务器功能

### 实时预览

启动后在浏览器中访问显示的 URL（通常是 `http://localhost:3000` 或类似地址），即可看到站点预览。

### 热重载

- 编辑 Markdown 文件保存后，浏览器自动刷新
- 编辑 myst.yml 配置后自动重新加载
- Notebook 输出变化后自动更新
- 通过 WebSocket 实现实时通信

### 双服务器架构

```
浏览器
  │
  ├──→ 应用服务器 (--port, 默认自动)
  │     └── 渲染 UI（导航、搜索、交互组件）
  │
  └──→ 内容服务器 (--server-port, 默认 3100-3200)
        ├── GET /              → 版本信息和链接
        ├── GET /config.json   → 站点配置
        ├── GET /content/*     → 页面内容 JSON
        └── WebSocket          → 热重载和日志
```

## 常见用例

### Docker 容器中运行

在 Docker 容器中，需要绑定 0.0.0.0 而非 localhost：

```bash
# 不使用 --keep-host 时，HOST 环境变量会被改为 localhost
# 在容器中应保留原始 HOST
myst start --keep-host --port 3000
```

### 指定图片优化阈值

```bash
myst start --max-size-webp 2
# 大于 2MB 的图片自动转换为 WebP
```

### 自定义模板开发

```bash
# 使用本地模板开发
myst start --template ./my-custom-template/
```

## 与 build --watch 的区别

| 功能 | `myst start` | `myst build --watch` |
|------|-------------|---------------------|
| HTTP 服务器 | ✅ | ❌ |
| 热重载（浏览器自动刷新） | ✅ | ❌ |
| WebSocket 日志 | ✅ | ❌ |
| 静态文件输出 | 内存+磁盘 | 仅磁盘 |
| 交互式 UI | ✅ | ❌ |
| 适合场景 | 开发预览 | CI/CD 或生成静态文件 |

## 停止服务器

- 终端中按 `Ctrl+C` 停止服务器
- 服务器会自动清理资源（关闭 Jupyter 内核、断开 WebSocket 等）

## 故障排查

### 端口被占用

服务器会自动尝试范围内的其他端口，无需手动指定。如果需要固定端口且被占用：

```bash
# 查找占用端口的进程
# Windows
netstat -ano | findstr :3000

# macOS/Linux
lsof -i :3000
```

### 内容不更新

1. 确认文件已保存
2. 检查终端是否有构建错误
3. 尝试硬刷新浏览器（Ctrl+Shift+R）
4. 清理缓存后重启：`myst clean --cache && myst start`

### Notebook 不执行

确认使用了 `--execute` 标志，且 Jupyter 内核可用：

```bash
myst start --execute
```

## 相关命令

- [构建站点](02-build-site.md)
- [初始化项目](01-init-project.md)
- [Start 开发服务器架构](../concepts/02-start-dev-server.md)
