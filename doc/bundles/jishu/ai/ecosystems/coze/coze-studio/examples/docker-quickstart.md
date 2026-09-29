---
type: example
title: "Docker Compose 快速入门"
description: "使用 Docker Compose 一键部署 Coze Studio 的完整步骤：环境准备、配置 .env、启动服务、验证健康状态与首次注册"
tags: [Docker, 快速开始, 部署, 入门]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-006
    resource: /references/deployment-infrastructure.md
    title: "最低配置 2CPU/4GB Docker"
  - id: F-cs-007
    resource: /references/deployment-infrastructure.md
    title: "Docker Compose 一键部署 make web"
  - id: F-cs-086
    resource: /references/deployment-infrastructure.md
    title: "11 个 Docker 服务"
---

# Docker Compose 快速入门

本指南介绍如何使用 Docker Compose 在本地一键部署 Coze Studio 全栈平台。从零开始，大约需要 10-20 分钟完成。

## 前置条件

### 系统要求

| 资源 | 最低配置 |
|------|----------|
| CPU | 2 核 |
| 内存 | 4GB |
| 磁盘 | 20GB 可用空间 |
| 软件 | Docker + Docker Compose |

### 软件安装

确保已安装 Docker 和 Docker Compose：

```bash
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker compose version
```

## 步骤 1：获取代码

```bash
git clone https://github.com/coze-dev/coze-studio.git
cd coze-studio
```

## 步骤 2：配置环境变量

复制环境变量模板：

```bash
cp docker/.env.example docker/.env
```

`.env.example` 包含 270+ 配置项，首次体验使用默认配置即可。如需配置外部 LLM 模型，请参考 [添加 LLM 模型](add-llm-model.md)。

如需配置管理员邮箱白名单（限制注册），编辑 `.env`：

```bash
# 可选：设置管理员邮箱（同时限制只有该邮箱可注册）
ALLOW_REGISTRATION_EMAIL=admin@example.com

# 可选：完全禁止注册
# DISABLE_USER_REGISTRATION=true
```

## 步骤 3：一键启动

```bash
make web
```

此命令会执行以下操作：
1. 拉取所有必要的 Docker 镜像
2. 创建 `coze-network` 桥接网络
3. 按依赖顺序启动 11 个服务
4. 初始化数据库 schema、ES 索引、MinIO bucket

首次启动需要拉取镜像，可能需要 5-15 分钟（取决于网络速度）。

## 步骤 4：验证服务状态

启动完成后，检查所有容器的健康状态：

```bash
docker compose -f docker/docker-compose.yml ps
```

预期所有服务的 Status 列显示 `healthy`（或 `running`）：

```
NAME                STATUS                          PORTS
coze-mysql          Up About a minute (healthy)     3306/tcp
coze-redis          Up About a minute (healthy)     6379/tcp
coze-elasticsearch  Up About a minute (healthy)     9200/tcp
coze-minio          Up About a minute (healthy)     9000/tcp, 9001/tcp
coze-etcd           Up About a minute (healthy)     2379/tcp
coze-milvus         Up About a minute (healthy)     19530/tcp
coze-nsqlookupd     Up About a minute (healthy)     4160-4161/tcp
coze-nsqd           Up About a minute (healthy)     4150-4151/tcp
coze-nsqadmin       Up About a minute (healthy)     4171/tcp
coze-server         Up About a minute (healthy)     8888/tcp
coze-web            Up About a minute               0.0.0.0:8888->80/tcp
```

逐一验证关键服务：

```bash
# 验证 MySQL
docker compose -f docker/docker-compose.yml exec mysql mysql -uroot -pcoze -e "SELECT 1"

# 验证 Elasticsearch
curl http://localhost:9200/_cluster/health

# 验证 MinIO（浏览器访问 http://localhost:9001）
# 默认 Access Key: minioadmin / Secret Key: minioadmin

# 验证后端 API
curl http://localhost:8888/api/config  # 应返回配置信息
```

## 步骤 5：访问 Web 界面

打开浏览器访问：

```
http://localhost:8888
```

页面标题显示 **"扣子 Studio"**。

## 步骤 6：注册首个用户

1. 点击登录/注册按钮
2. 选择邮箱注册
3. 填写邮箱和密码
4. 如果配置了 `ALLOW_REGISTRATION_EMAIL`，确保注册邮箱在白名单中
5. 注册成功后自动登录

注册后即可开始：
- 创建智能体（Agent）
- 编排工作流（Workflow）
- 上传知识库文档
- 配置插件工具

## 常用运维命令

```bash
# 停止所有服务
make down

# 查看服务日志
docker compose -f docker/docker-compose.yml logs -f coze-server

# 重启后端服务
docker compose -f docker/docker-compose.yml restart coze-server

# 清理所有容器和数据卷（⚠️ 会删除所有数据）
make clean
```

## 故障排查

| 问题 | 排查方法 |
|------|----------|
| 端口 8888 被占用 | 修改 `.env` 中的 `WEB_LISTEN_ADDR`，如 `WEB_LISTEN_ADDR=8889` |
| ES 启动失败 | 确保 `vm.max_map_count>=262144`（Linux）；Mac/Windows 忽略 |
| Milvus 启动慢 | Milvus 依赖 etcd+MinIO，等待依赖服务完全 healthy 后会自动恢复 |
| 镜像拉取慢 | 配置 Docker 镜像加速器 |
| 内存不足 | 确保 Docker 分配至少 4GB 内存 |

## 相关文档

- [部署与运维](../concepts/08-deployment-operations.md)
- [添加 LLM 模型](add-llm-model.md)
- [配置基础设施](configure-infrastructure.md)
- [部署与基础设施参考](../references/deployment-infrastructure.md)
