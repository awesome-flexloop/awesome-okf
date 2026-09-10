---
type: Example
title: azure-vote：前端 + Redis 双服务标准形态
description: 官方 azure-vote 示例详解：两个服务通过服务名零配置发现、dict 语法 environment、container_name 与 .env 参数化
tags: [podman, compose, example, azure-vote, redis, two-service, service-discovery]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: examples
    resource: /references/examples-source.md
    title: podman-compose examples/ 目录信源登记
---

# azure-vote：前端 + Redis 双服务标准形态

`azure-vote/` 是 Azure 官方投票应用（源自 [Azure-Samples/azure-voting-app-redis](https://github.com/Azure-Samples/azure-voting-app-redis)），架构是一个前端 + 一个 Redis 后端。它是从单服务跨到多服务后**最小但完整**的样板：演示了 podman-compose 最核心的承诺——服务间用服务名直接通信，零网络配置。

## compose 全文

```yaml
# 来自 Azure-Samples/azure-voting-app-redis
version: '3'
services:
  azure-vote-back:
    image: mcr.microsoft.com/oss/bitnami/redis:6.0.8
    container_name: azure-vote-back
    environment:
      ALLOW_EMPTY_PASSWORD: "yes"
  azure-vote-front:
    image: mcr.microsoft.com/azuredocs/azure-vote-front:v1
    environment:
      REDIS: azure-vote-back
    ports:
        - "${HOST_PORT:-8080}:80"
```

## 字段逐项解读

### 后端 azure-vote-back

| 字段 | 值 | 作用 |
|------|-----|------|
| `image` | bitnami/redis:6.0.8 | Redis 6.0.8，镜像从微软容器仓库（mcr）拉取 |
| `container_name` | azure-vote-back | 固定容器名（否则默认 `<项目>_azure-vote-back_1`） |
| `environment.ALLOW_EMPTY_PASSWORD` | `"yes"` | Bitnami 镜像约定：允许空密码启动（演示环境用，生产禁用） |

### 前端 azure-vote-front

| 字段 | 值 | 作用 |
|------|-----|------|
| `image` | azure-vote-front:v1 | 含 supervisord + nginx + uwsgi/python 的前端镜像 |
| `environment.REDIS` | `azure-vote-back` | **服务发现的关键**：前端应用读 `REDIS` 环境变量得到后端主机名 |
| `ports` | `${HOST_PORT:-8080}:80` | 容器内服务监听 80（nginx），宿主默认 8080 |

## 运行（README 原始步骤）

```bash
cd examples/azure-vote
echo "HOST_PORT=8080" > .env
podman-compose up
# 浏览器打开 http://localhost:8080/
# 页面为投票应用，每次点击的票数持久化在 Redis 中
```

## 服务发现为什么零配置

这是本例最值得理解的机制：

1. 两个服务都未声明 `networks`，podman-compose 自动创建默认网络 `<项目>_default` 并把两个容器接入；
2. 每个容器在网络中自动注册**服务名作为 DNS 别名**（源码翻译层还会把服务名加为 `alias=` 网络选项，见[CLI 翻译层](../concepts/05-cli-translation-layer.md)）；
3. 前端容器内解析主机名 `azure-vote-back` 直接得到后端容器 IP——由网络的 DNS 插件（netavark/aardvark-dns 或 CNI + dnsname）解析；
4. 前端应用从 `REDIS` 环境变量读到这个主机名，建立 Redis 连接。

整条链路没有任何地方配置 IP、链接或网络。作为对照，awx3 示例（见[11](11-awx-large-app.md)）还保留着老式 `links` 写法，而 azure-vote 已经完全不依赖 links。

## 与 wordpress 示例的对照

| 维度 | azure-vote | wordpress（见[01](01-wordpress.md)） |
|------|-----------|--------------------------------------|
| 后端 | redis | mariadb |
| 环境变量语法 | dict（`KEY: value`） | 列表（`- KEY=value`） |
| 连接配置 | `REDIS: azure-vote-back` | `WORDPRESS_DB_HOST=db` |
| 数据持久化 | 无（演示数据随容器删除） | 命名卷 db_data |
| 容器命名 | container_name 固定 | 默认命名 |

两种 env 语法等价（源码 `norm_as_dict/norm_as_list` 互相归一化），两个示例放在一起正好覆盖 Compose 环境变量的两种书写风格。

## .env 文件在这里的角色

`echo "HOST_PORT=8080" > .env` 创建的是**项目级 .env**，被 podman-compose 在加载 compose 前读取（见[配置加载管线](../concepts/06-config-pipeline.md)的环境分层）：

- 作用对象是 compose 文件的插值（`${HOST_PORT}`）与 podman-compose 自身；
- 与服务级 `env_file:`（如 nodeproj 示例注入容器的 local.env）是两层不同的东西；
- 这里其实是显式写出默认值的演示用法——不写这个 .env，`${HOST_PORT:-8080}` 同样默认 8080。

## 验证与排障

```bash
podman-compose up -d                       # 后台启动
podman-compose ps                          # 两个服务 Up
podman-compose logs azure-vote-front       # 前端日志
# 进入前端容器手动验证服务发现：
podman-compose exec azure-vote-front sh -c 'getent hosts azure-vote-back || ping -c1 azure-vote-back'
```

常见问题：

| 现象 | 原因 | 处理 |
|------|------|------|
| 前端日志报无法连接 redis | 后端启动慢于前端首连 | 前端镜像自带重试；或给后端配健康检查 + depends_on condition |
| 投票数在 down 后丢失 | 本示例无卷 | 持久化需加命名卷（参考 wordpress 的 db_data 写法） |
| 8080 冲突 | 宿主端口占用 | `.env` 改 `HOST_PORT=9090` |

## 相关示例与概念

- [WordPress 部署示例](01-wordpress.md)：双服务 + 命名卷持久化的完整教学版
- [官方示例图鉴](03-official-examples-gallery.md)
- [CLI 翻译层与标签状态](../concepts/05-cli-translation-layer.md)：服务别名 alias 的生成
- [rootless 模式下的网络与卷](../concepts/02-rootless.md)：DNS 插件与 netavark 说明
