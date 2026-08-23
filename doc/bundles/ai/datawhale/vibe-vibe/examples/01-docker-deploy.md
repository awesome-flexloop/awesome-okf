---
title: Docker 私有化部署
type: example
bundle: /datawhale/vibe-vibe
description: 通过 docker-compose 一条命令在本地启动 Vibe Vibe 中英文双语文档站，演示多阶段 Docker 构建、端口映射、健康检查与离线运行特性。
related:
  - /datawhale/vibe-vibe/concepts/03-multilingual-docs-architecture
  - /datawhale/vibe-vibe/concepts/01-vibe-coding-philosophy
sources:
  - https://github.com/datawhalechina/vibe-vibe
---

## 场景说明

你想在本地或企业内网环境部署 Vibe Vibe 教程站点，用于离线学习或内部培训。本示例演示使用仓库自带的 Dockerfile 和 docker-compose.yml 一条命令启动服务。

## 前置条件

- 已安装 Docker 和 Docker Compose
- 约 2GB 可用磁盘空间（Node 构建镜像 + Nginx 服务镜像）
- 端口 1024 未被占用

## 部署步骤

### 1. 克隆仓库

```bash
git clone https://github.com/datawhalechina/vibe-vibe.git
cd vibe-vibe
```

### 2. 一键启动

```bash
docker compose up -d --build
```

该命令会：

1. 使用 `node:24-alpine` 镜像安装 pnpm 和项目依赖
2. 执行 `pnpm build` 构建 VitePress 静态站点（中英文双语一次完成）
3. 将构建产物拷贝到 `nginx:alpine` 镜像
4. 启动 Nginx 容器，映射端口 1024:80

### 3. 访问站点

打开浏览器访问：

```
http://localhost:1024
```

首次访问根路径时，`docs/index.md` 中的脚本会根据浏览器语言自动跳转：

- 中文浏览器 → `http://localhost:1024/zh/`
- 其他语言浏览器 → `http://localhost:1024/en/`

## Dockerfile 解析

仓库根目录的 `Dockerfile` 采用多阶段构建：

```dockerfile
# 构建阶段
FROM node:24-alpine AS builder
WORKDIR /app
RUN npm install -g pnpm
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# 服务阶段
FROM nginx:alpine
COPY --from=builder /app/docs/.vitepress/dist /usr/share/nginx/html
EXPOSE 80
```

关键点：

- 使用 `--frozen-lockfile` 确保依赖版本与 lockfile 一致
- 构建产物位于 `docs/.vitepress/dist`，直接拷贝到 Nginx 默认目录
- 最终镜像只含 Nginx + 静态文件，体积小且无需 Node 运行时

## docker-compose.yml 解析

```yaml
services:
  vibevibe:
    build:
      context: .
      dockerfile: Dockerfile
    image: vibevibe-docs:latest
    container_name: vibevibe-app
    restart: unless-stopped
    ports:
      - "1024:80"
    environment:
      - TZ=Asia/Shanghai
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - vibevibe-network
    labels:
      - "com.vibevibe.description=VibeVibe Documentation Service"
      - "com.vibevibe.version=1.0"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

配置要点：

| 配置 | 值 | 说明 |
|------|-----|------|
| 端口映射 | `1024:80` | 主机 1024 → 容器 80（README 约定的默认端口） |
| 时区 | `Asia/Shanghai` | 确保日志时间正确 |
| 重启策略 | `unless-stopped` | 容器退出时自动重启（手动停止除外） |
| 健康检查 | wget spider | 每 30 秒检测 Nginx 是否响应，40 秒启动宽限 |
| 日志限制 | 10m × 3 | 单个日志文件最大 10MB，保留 3 个文件 |

## 其他部署方式

### 直接部署静态文件

如果不想用 Docker，也可以直接构建后部署 `dist/` 目录：

```bash
pnpm install
pnpm build
```

构建产物在 `docs/.vitepress/dist/`，可部署到 Nginx、Apache、IIS、OSS/S3 等任意静态文件托管服务。

### 本地预览（不构建）

```bash
pnpm install
pnpm dev
```

启动 VitePress 开发服务器（带热重载），适用于内容贡献者。

### EdgeOne Pages

在腾讯云 EdgeOne 控制台创建静态网站，关联 GitHub 仓库，每次推送自动构建部署。

## 离线运行说明

Vibe Vibe 是纯静态站点，Docker 部署后**完全离线运行**，无需互联网连接或数据库。但需注意：

1. **Giscus 评论系统**需要互联网连接，离线环境会加载失败（不影响阅读）
2. **部分图片**使用 GitHub raw 链接，离线环境可能不显示
3. **Umami 统计**（u.vibevibe.cn）会请求外部域名，离线环境自动跳过

对于完全离线环境，建议在构建前将图片下载到 `docs/public/` 目录并更新引用路径。

## 常用运维命令

```bash
# 查看日志
docker compose logs -f vibevibe

# 停止服务
docker compose down

# 更新到最新版本
git pull
docker compose up -d --build

# 检查健康状态
docker inspect --format='{{.State.Health.Status}}' vibevibe-app
```

## 许可证注意事项

Vibe Vibe 采用 CC BY-NC-SA 4.0 许可证。私有化部署时：

- ✅ 企业内部培训学习：允许
- ✅ 学校教学使用：允许
- ✅ 修改内容后内部使用：允许（须相同协议共享）
- ❌ 收费课程/训练营：禁止
- ❌ 移除原作者署名：禁止

## 验证清单

- [ ] `docker compose up -d --build` 成功执行
- [ ] 浏览器访问 `http://localhost:1024` 自动跳转到中文或英文首页
- [ ] 顶部导航可切换基础篇、进阶篇、优质文章篇、实践案例篇
- [ ] 语言切换器（LocaleSwitch）可在中英文间切换
- [ ] 基础篇页面显示 BasicEditionUpdateBox 提示
- [ ] 交互组件（如终端模拟器、PRD 对比）正常渲染
- [ ] 健康检查状态为 healthy

## 相关概念

- [多语言文档架构](/ai/datawhale/vibe-vibe/concepts/03-multilingual-docs-architecture.md)：VitePress 双语构建、首页重定向、交互组件体系。
- [Vibe 开发理念](/ai/datawhale/vibe-vibe/concepts/01-vibe-coding-philosophy.md)：站点承载的教学内容与 AI 创造工作流。
