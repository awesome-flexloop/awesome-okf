---
type: Example
title: 官方示例图鉴：12 个 examples/ 用例模式速查
description: 逐模式拆解 podman-compose 仓库 12 个官方示例，从单服务最小用例到 6 节点 Redis 集群、GPU、内联构建与 extends 继承的可运行配方
tags: [podman, compose, example, official-examples, patterns, recipes]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: examples
    resource: /references/examples-source.md
    title: podman-compose examples/ 目录信源登记
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
---

# 官方示例图鉴：12 个 examples/ 用例模式速查

podman-compose 仓库 `examples/` 目录提供 12 个可直接运行的官方示例。它们不是随意的 demo，而是按复杂度梯度排列的**可执行特性矩阵**：每个示例只引入一两个新模式，读者可以按需抄用对应片段。本文按模式分组拆解；示例与概念文档的对应关系在文末汇总。

## 第一级：单服务最小用例

### echo / hello-app —— 5 行起步

`echo/` 与 `hello-app/` 都只有一个服务，且共享同一套参数化端口写法：

```yaml
services:
  web:
    image: k8s.gcr.io/echoserver:1.4
    ports:
      - "${HOST_PORT:-8080}:8080"
```

要点：

- `${HOST_PORT:-8080}` 是 bash 风格插值（见[配置加载管线](../concepts/06-config-pipeline.md)）：宿主可用 `HOST_PORT=9090 podman-compose up` 换端口，不设则默认 8080；
- `podman-compose up` 后 `curl -X POST -d "foobar" http://localhost:8080/` 可看到 echoserver 回显完整请求头——这也是验证容器网络可达性的最快手段。

### docker-inline —— 零 Dockerfile 构建

`docker-inline/` 演示不写 Dockerfile 文件，直接在 compose 里内联构建脚本：

```yaml
services:
  dummy:
    build:
      context: .
      dockerfile_inline: |
        FROM alpine
        RUN echo "hello world"
```

`dockerfile_inline` 由源码 `container_to_build_args` 写入临时 `.containerfile` 并在构建后清理，适合"只需要一两行构建指令"的轻量场景。

### nvidia-smi —— GPU 预留

`nvidia-smi/` 用 Compose v3 的 deploy 标准语法申请 GPU（需要 NVIDIA Container Toolkit/CDI）：

```yaml
services:
  test:
    image: nvidia/cuda:12.3.1-base-ubuntu20.04
    command: nvidia-smi
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

翻译层将其展开为 `--device nvidia.com/gpu=0 --security-opt=label=disable`（`device_ids` 可替代 count 指定具体卡号）。

## 第二级：双服务与基础编排

### azure-vote —— 前后端的标准形态

两个服务，前端通过环境变量指向后端服务名：

```yaml
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

要点：**服务发现零配置**——前端直接用后端服务名 `azure-vote-back` 作主机名，由默认网络的 DNS/别名解析；这里也演示了 dict 语法 env 与 `container_name`。README 用 `echo "HOST_PORT=8080" > .env` 展示了 `.env` 文件惯例。

### wordpress —— 命名卷持久化

`wordpress/` 是 Web + 数据库的经典持久化模式：

```yaml
volumes:
  db_data:
services:
  db:
    image: docker.io/library/mariadb:10.6.4-focal
    volumes:
      - db_data:/var/lib/mysql
  wordpress:
    image: docker.io/library/wordpress:latest
    ports:
      - 8080:80
    environment:
      - WORDPRESS_DB_HOST=db
```

要点：

- 顶层声明的 `db_data` 命名卷由 podman-compose 加项目前缀（`<项目>_db_data`）并在首次使用时自动 `podman volume create`；
- `WORDPRESS_DB_HOST=db` 用列表语法 env 表达数据库连接——**隐式依赖**：不需要 depends_on，服务名解析即依赖声明；
- 短端口语法 `8080:80` 等价于 `"8080:80"`。

> 完整教学版讲解见 [01-wordpress.md](01-wordpress.md)。

### busybox —— 语法多样性参考卡

`busybox/` 只有两个服务，却是最密集的语法样本：

```yaml
services:
  redis:
    image: docker.io/redis:alpine
    environment:
      - SECRET_KEY=aabbcc
      - ENV_IS_SET            # 列表短格式：从宿主继承 ENV_IS_SET
  frontend:
    image: docker.io/library/busybox:latest
    command: ["/bin/busybox", "httpd", "-f", "-p", "8080"]
    environment:
      SECRET_KEY2: aabbcc
      ENV_IS_SET2:             # dict 短格式：值为 null，同样从宿主继承
    links:
      - redis:myredis          # links 带别名：frontend 可用 myredis 访问 redis
    labels:
      my.label: my_value
```

文件底部还以注释形式列出了 tmpfs/user/hostname/ipc/mac_address/privileged/read_only/shm_size/stdin_open/tty 等一批可选字段——官方把它当作"选项目录"维护。`links: redis:myredis` 会被归一化为网络别名（见[CLI 翻译层](../concepts/05-cli-translation-layer.md)）。

### hello-python —— build + image 双轨与只读根文件系统

```yaml
volumes:
  redis:
services:
  redis:
    read_only: true
    image: docker.io/redis:alpine
    command: ["redis-server", "--appendonly", "yes", "--notify-keyspace-events", "Ex"]
    volumes:
      - redis:/data
  web:
    read_only: true
    build:
      context: .
    image: hello-py-aioweb
    ports:
      - 8080:8080
    environment:
      REDIS_HOST: redis
```

要点：

- **build 与 image 同时存在**：从本地 Dockerfile 构建并打成 `hello-py-aioweb` 标签（镜像名不含 `/`，被 `is_local()` 判定为本地镜像，不参与 pull）；
- `read_only: true` 让容器根文件系统只读，需要写数据的路径（redis 的 /data）用命名卷显式挂出——最小权限实践；
- 配套 Dockerfile 是标准 Python 构建（COPY requirements → pip install → COPY 代码 → CMD）。

## 第三级：多服务与高级模式

### hello-app-redis —— 6 节点 Redis 集群

这是规模最大的示例：5 个数据节点 + 1 个集群创建者（creator）+ 1 个 Web 计数器。

```yaml
services:
  web:
    image: gcr.io/google-samples/hello-app-redis:1.0
    depends_on:
      - redis-cluster
    ports:
      - "${HOST_PORT:-8080}:8080"
  redis-node1:        # ... redis-node5 同构
    image: docker.io/bitnami/redis-cluster:6.2
    volumes:
      - redis-node1-data:/bitnami/redis/data
    environment:
      - ALLOW_EMPTY_PASSWORD=yes
      - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster
  redis-cluster:
    image: docker.io/bitnami/redis-cluster:6.2
    depends_on:
      - redis-node1      # creator 等待 5 个节点
      # ... node2-5
    environment:
      - REDIS_CLUSTER_CREATOR=yes
```

要点：每个节点独立命名卷持久化；`REDIS_NODES` 用服务名枚举全部集群成员（DNS 解析）；两层 depends_on 表达启动拓扑（web → creator → 5 节点），注意列表式 depends_on 默认条件是 `service_started`，集群就绪保证来自镜像自身的初始化逻辑。

> 教学版编排讲解见 [02-multi-container.md](02-multi-container.md)。

### nodeproj —— extends 继承与开发环境工作流

Node.js 开发环境示例，是模式密度最高的一个：

```yaml
services:
  init:                          # 基服务：公共配置
    read_only: true
    user: ${UID:-1000}           # 容器内以当前宿主 UID 运行（rootless 友好）
    build:
      context: ./containers/${NODE_IMG:-node16-runtime}   # build context 路径也可插值
    image: ${NODE_IMG:-node16-runtime}
    env_file:
      - local.env                # 服务级 env_file
    volumes:
      - .:/app/code              # bind mount 源码做热开发
    command: ["/bin/sh", "-c", "mkdir -p ~/; [ -d ./node_modules ] && echo ok || npm install"]
    tmpfs:
      - /tmp
      - /run
  task:
    extends:
      service: init              # 继承 init 的全部配置，只覆写 command
    command: ["npm", "run", "cli", "--", "task"]
    links:
      - redis
  web:
    extends:
      service: init
    command: ["npm", "run", "cli", "--", "web"]
    ports:
      - ${WEB_LISTEN_PORT:-3000}:3000
    depends_on:
      - redis
```

README 给出的完整开发工作流：

```bash
cp example.local.env local.env   # 服务级 env_file 模板
cp example.env .env              # 项目级 .env（REDIS_HOST=redis）
echo "UID=$UID" >> .env          # 注入当前用户 UID
podman-compose build
podman-compose run --rm --no-deps init   # 一次性初始化（装依赖），--rm 退出即删
podman-compose up
```

要点：`extends` 消除三个 Node 服务间的重复配置；`run --rm --no-deps init` 展示了用一次性容器跑初始化任务（不触发依赖服务启动）；bind mount + tmpfs + read_only 的组合是 rootless 开发环境的典型配方。

### awx3 / awx17 —— 大型应用与模板化生成

- **awx3**：AWX/Ansible Tower 3.0.1 的 5 服务部署（postgres、rabbitmq、memcached、awx_web、awx_task），演示多服务 `links`、`hostname`、`user: root` 与大量 dict env——结构是"基础设施三件套 + 应用双角色"的企业应用样板。
- **awx17**：更进一步，compose 文件不由人写，而是由 Ansible role 的 Jinja2 模板（`docker-compose.yml.j2`）渲染生成；README 展示了两个工程技巧：
  - 渲染后用 `sed` 把宿主机绝对路径改写成相对路径（`s#"$PWD/awx17/(.*):/#- "./\1:/#`），使生成文件可移植；
  - 用 `podman-compose run --rm --service-ports task awx-manage migrate --no-input` 跑一次性数据库迁移，再 `up -d` 启动——与 nodeproj 的 init 模式同源。

## 横向模式总结

| 模式 | 出现的示例 | 一句话 |
|------|-----------|--------|
| `${VAR:-default}` 插值 | echo/hello-app/hello-app-redis/azure-vote/nodeproj | 端口/UID/镜像名参数化，配置不写死 |
| `.env` + `env_file` 分层 | azure-vote/nodeproj | 项目级 .env 控制 compose，服务级 env_file 注入容器 |
| 服务名即主机名 | 全部多服务示例 | 默认网络 DNS，零额外配置服务发现 |
| 命名卷持久化 | wordpress/hello-python/hello-app-redis/nodeproj | `<项目>_<卷名>` 自动创建、跨 up/down 保留 |
| read_only + tmpfs | hello-python/nodeproj | 根文件系统只读，写路径显式声明 |
| build + image 双轨 | hello-python/nodeproj | 本地构建打自定义 tag，默认不参与 pull |
| depends_on / links | hello-app-redis/nodeproj/awx3 | 启动拓扑 + 网络别名（links 同时隐含依赖） |
| extends 继承 | nodeproj | 基服务承载公共配置，变体只覆写 command |
| 一次性任务容器 | nodeproj/awx17 | `run --rm` 跑 init/migrate 等管理命令 |
| deploy.resources GPU | nvidia-smi | 标准 Compose v3 语法申请设备 |
| dockerfile_inline | docker-inline | 无需 Dockerfile 文件的内联构建 |

> 特性覆盖边界：官方示例不涉及自定义 networks、healthcheck、profiles、secrets、x-podman 扩展字段——这些以仓库 `tests/integration/` 的测试用例（40+ 个测试目录）为权威覆盖，对应概念文档见[配置加载管线](../concepts/06-config-pipeline.md)与[x-podman 扩展字段全解](../concepts/08-x-podman-extensions.md)。

## 相关示例与概念

- [WordPress 部署示例](01-wordpress.md)：wordpress 示例的完整教学版
- [多容器应用编排](02-multi-container.md)：Redis 集群模式的教学版
- [Compose 文件常见模式](../concepts/03-compose-patterns.md)：配置字段系统讲解
- [配置加载管线](../concepts/06-config-pipeline.md)：插值、env_file、extends 的实现机制
- [依赖图与 up/down 生命周期](../concepts/07-dependency-lifecycle.md)：depends_on 与 run 一次性任务
- [官方示例信源登记](../references/examples-source.md)：12 个示例的文件清单与事实索引
