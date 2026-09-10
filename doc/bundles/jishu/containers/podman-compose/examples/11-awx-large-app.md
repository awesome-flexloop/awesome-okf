---
type: Example
title: awx3 与 awx17：大型多服务应用与模板化生成
description: 官方 awx3（AWX 3.0.1 五服务直写）与 awx17（Ansible Jinja2 模板生成 compose + migrate 一次性命令）两个企业级示例
tags: [podman, compose, example, awx, ansible, large-app, template, migration, links]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: examples
    resource: /references/examples-source.md
    title: podman-compose examples/ 目录信源登记
---

# awx3 与 awx17：大型多服务应用与模板化生成

`awx3/` 与 `awx17/` 是 AWX（Ansible Tower 上游开源版）的两个版本示例，代表示例集中的**企业级复杂度**：5+ 服务、大量配置注入、links 网络、以及"compose 文件不由人直接写"的模板化生成模式。

## awx3：五服务直写编排

目录：`examples/awx3/docker-compose.yml`，服务拓扑：

```text
                 ┌────────────┐
   :8080────────▶│  awx_web   │  Web UI（端口 8080→8052）
                 └─────┬──────┘
                       │ links
        ┌──────────────┼──────────────┐
   ┌────┴────┐   ┌─────┴─────┐   ┌─────┴─────┐
   │ postgres│   │ rabbitmq  │   │ memcached │
   └─────────┘   └───────────┘   └───────────┘
                 ┌────────────┐
                 │  awx_task  │  后台任务worker（links 上述全部 + awx_web）
                 └────────────┘
```

5 个服务：

| 服务 | 镜像 | 角色 |
|------|------|------|
| postgres | postgres:9.6 | 数据库（AWX 库） |
| rabbitmq | rabbitmq:3 | 消息队列（web 与 task 间任务分发） |
| memcached | memcached:alpine | 缓存 |
| awx_web | ansible/awx_web:3.0.1 | Web/API 进程 |
| awx_task | ansible/awx_task:3.0.1 | Celery 任务 worker |

### 关键配置手法

**links 显式组网（旧式但直观）**：

```yaml
awx_web:
  links:
    - rabbitmq
    - memcached
    - postgres
awx_task:
  links:
    - rabbitmq
    - memcached
    - awx_web:awxweb     # 带别名：task 用 awxweb 也能访问 web
    - postgres
```

在现代 podman-compose 中默认网络 + 服务名 DNS 已使 links 冗余（links 仍提供两件事：网络别名与隐含 service_started 依赖，见[CLI 翻译层](../concepts/05-cli-translation-layer.md)）。

**配置注入：dict env 集中声明连接信息**：

```yaml
awx_web:
  hostname: awxweb
  user: root
  environment:
    SECRET_KEY: aabbcc
    DATABASE_HOST: postgres
    DATABASE_PORT: 5432
    RABBITMQ_HOST: rabbitmq
    RABBITMQ_PORT: 5672
    RABBITMQ_VHOST: awx
    MEMCACHED_HOST: memcached
    MEMCACHED_PORT: 11211
    # ...
```

模式要点：连接信息全部通过环境变量注入，主机名一律写服务名（`postgres`/`rabbitmq`/`memcached`）；基础设施三件套各自只设最少的自身配置（如 postgres 的 POSTGRES_USER/PASSWORD/DB、rabbitmq 的 RABBITMQ_DEFAULT_VHOST）。`hostname: awxweb` 固定容器主机名供应用间相互识别，`user: root` 是镜像内权限要求（旧版 AWX 镜像假设 root 运行）。

## awx17：模板生成 + 一次性迁移命令

awx17 更进一步——它没有可供直接 `up` 的 compose 文件，而是 AWX 官方 Ansible 安装器（`installer/roles/local_docker`）的角色目录：

```text
awx17/roles/local_docker/
├── defaults/main.yml                    # 角色默认变量
├── tasks/（main.yml、set_image.yml、compose.yml、upgrade_postgres.yml）
└── templates/
    ├── docker-compose.yml.j2            # Jinja2 模板：compose 由此渲染
    ├── environment.sh.j2
    ├── credentials.py.j2
    ├── nginx.conf.j2
    └── redis.conf.j2
```

### 模板长什么样

`docker-compose.yml.j2` 用 Jinja2 条件块按变量渲染不同片段：

```jinja
version: '2'
services:
  web:
    image: {{ awx_docker_actual_image }}
    depends_on:
      - redis
      {% if pg_hostname is not defined %}
      - postgres
      {% endif %}
    {% if host_port is defined %}
    ports:
      - "{{ host_port }}:8052"
    {% endif %}
    volumes:
      - "{{ docker_compose_dir }}/SECRET_KEY:/etc/tower/SECRET_KEY"
      - "{{ docker_compose_dir }}/environment.sh:/etc/tower/conf.d/environment.sh"
      # ...
```

即：同一份模板，通过 Ansible 变量（是否外置 postgres、是否配 SSL、是否自定义 hosts/DNS/标签）渲染出形态不同的 compose。

### README 的完整工作流

```bash
mkdir deploy awx17
ansible localhost \
    -e host_port=8080 \
    -e awx_secret_key='awx,secret.123' \
    -e pg_password='awx,123.' \
    -e redis_image="docker.io/library/redis:6-alpine" \
    -e postgres_data_dir="./data/pg" \
    -e awx_version='17.1.0' \
    -e docker_deploy_base_path=$PWD/deploy \
    -e docker_compose_dir=$PWD/awx17 \
    -m include_role -a name=local_docker        # ① 渲染生成 docker-compose.yml + 配置文件
cp awx17/docker-compose.yml awx17/docker-compose.yml.orig
sed -i -re "s#- \"$PWD/awx17/(.*):/#- \"./\1:/#" awx17/docker-compose.yml   # ② 绝对路径→相对
cd awx17
podman-compose run --rm --service-ports task awx-manage migrate --no-input  # ③ 一次性数据库迁移
podman-compose up -d                                                          # ④ 启动
```

四个步骤各有工程含义：

1. **Ansible 渲染**：模板 + 变量生成 compose 与 AWX 配置文件（secret、nginx、redis 配置）；
2. **sed 路径改写**：模板渲染出的 bind mount 源路径是渲染机的绝对路径（`$PWD/awx17/...`），用 sed 改成相对路径 `./...`，使生成文件可在同目录其他位置/其他机器使用；
3. **一次性迁移**：`podman-compose run --rm --service-ports task awx-manage migrate --no-input`——在 awx_task 镜像上跑 Django 数据库迁移命令，`--rm` 退出即删容器，`--service-ports` 保留服务端口映射；
4. **常驻启动**：`up -d` 拉起全部服务。

## 两个示例连起来的启示

| 主题 | awx3 | awx17 |
|------|------|-------|
| compose 来源 | 人手维护 | Ansible 模板渲染 |
| 组网 | links 显式 | 模板按变量条件生成 depends_on/卷/DNS |
| 初始化 | 无（镜像自带） | `run --rm` 显式跑数据库迁移 |
| 适用规模 | 固定拓扑快速体验 | 可配置的生产部署 |

它们共同展示了编排复杂度的两个上升方向：

- **服务数量与连接关系**：5 服务、每个应用服务连全部基础设施——靠"配置全部走环境变量、主机名全部用服务名"保持可读；
- **部署流程**：初始化/迁移这类一次性操作不写进常驻服务的 command，而是用 `podman-compose run --rm` 显式执行（与 nodeproj 的 init 模式同源，见[10](10-nodeproj.md)），compose 文件描述"系统应该长什么样"，流程性动作用命令行编排。

## 相关示例与概念

- [nodeproj Node 开发环境](10-nodeproj.md)：`run --rm --no-deps init` 一次性初始化的开发侧对应
- [官方示例图鉴](03-official-examples-gallery.md)
- [依赖图与 up/down 生命周期](../concepts/07-dependency-lifecycle.md)：run 一次性容器、links 与依赖
- [x-podman 扩展字段全解](../concepts/08-x-podman-extensions.md)：大型应用中 userns/pod 参数的取舍
