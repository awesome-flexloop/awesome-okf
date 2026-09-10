# 示例文档索引

本目录包含 podman-compose 的实战示例文档，每个示例都是可直接运行的完整用例。

## 示例列表

| 序号 | 文档 | 描述 | 涉及概念 | 难度 |
|------|------|------|---------|------|
| 01 | [01-wordpress.md](01-wordpress.md) | WordPress + MariaDB 双服务部署：经典的 Web + 数据库模式，适合初学者 | 命名卷、端口映射、环境变量、服务发现 | ⭐ 入门 |
| 02 | [02-multi-container.md](02-multi-container.md) | Web + Redis 集群多容器编排：网络隔离、依赖管理、多卷配置、参数化配置 | 自定义网络、服务依赖、多卷管理、环境变量插值、profiles、健康检查 | ⭐⭐ 进阶 |
| 03 | [03-official-examples-gallery.md](03-official-examples-gallery.md) | 官方 12 个 examples/ 用例模式图鉴：从单服务到 6 节点集群、GPU、内联构建、extends 继承 | 插值、命名卷、links/extends、read_only、GPU、dockerfile_inline、一次性任务容器 | ⭐⭐ 进阶 |
| 04 | [04-echo-hello-app.md](04-echo-hello-app.md) | echo/hello-app 单服务最小用例逐行详解：端口参数化、curl 回显探针、单服务生命周期 | 端口插值、最小编排、up/down | ⭐ 入门 |
| 05 | [05-docker-inline-gpu.md](05-docker-inline-gpu.md) | docker-inline（dockerfile_inline 零文件构建）与 nvidia-smi（GPU 预留）特殊场景 | dockerfile_inline、deploy.resources GPU、--device CDI | ⭐⭐ 进阶 |
| 06 | [06-azure-vote.md](06-azure-vote.md) | azure-vote 前端+Redis：服务名零配置发现、dict 语法 env、.env 参数化 | 服务发现、两种 env 语法、项目级 .env | ⭐ 入门 |
| 07 | [07-busybox-syntax.md](07-busybox-syntax.md) | busybox 配置语法参考卡：links 别名、空值 env 透传、labels、注释形式的 12 个可选字段目录 | links、environment 两种语法、labels、字段速查 | ⭐⭐ 进阶 |
| 08 | [08-hello-python.md](08-hello-python.md) | hello-python 本地构建：build/image 双轨、read_only 安全加固、命名卷承接写路径 | 本地构建、read_only+卷、is_local、aiohttp/redis | ⭐⭐ 进阶 |
| 09 | [09-redis-cluster.md](09-redis-cluster.md) | hello-app-redis 6 节点 Redis 集群：creator 初始化角色、REDIS_NODES 发现、两层 depends_on | 同构服务、集群初始化、depends_on 条件边界 | ⭐⭐⭐ 高级 |
| 10 | [10-nodeproj.md](10-nodeproj.md) | nodeproj Node 开发环境：extends 继承、env_file 分层、tmpfs、UID 传递、run --rm 初始化 | extends、env_file、tmpfs、rootless UID、bind mount、一次性容器 | ⭐⭐⭐ 高级 |
| 11 | [11-awx-large-app.md](11-awx-large-app.md) | awx3/awx17 企业级示例：五服务 links 组网、Ansible Jinja2 模板生成、migrate 一次性命令 | links 大型组网、模板化 compose、run --service-ports 迁移 | ⭐⭐⭐ 高级 |

## 示例使用指南

### 前置准备

所有示例都假设你已经：

1. 安装了 podman（>= 3.4）
2. 安装了 podman-compose
3. （CNI 网络）安装了 dnsname 插件
4. 有一个工作目录用于存放 compose.yaml

### 运行示例的通用步骤

```bash
# 1. 创建工作目录
mkdir example-dir && cd example-dir

# 2. 创建 compose.yaml（参考示例中的 YAML）

# 3. 启动服务（后台运行）
podman-compose up -d

# 4. 查看状态和日志
podman-compose ps
podman-compose logs -f

# 5. 测试访问（根据示例）
curl http://localhost:8080

# 6. 停止并清理
podman-compose down
```

### 学习路径建议

1. **新手入门**：先做 [04-echo-hello-app.md](04-echo-hello-app.md)（单服务最小用例），再做 [01-wordpress.md](01-wordpress.md) 与 [06-azure-vote.md](06-azure-vote.md) 理解双服务编排
2. **语法速查**：遇到字段写法疑问查 [07-busybox-syntax.md](07-busybox-syntax.md)；特殊场景看 [05-docker-inline-gpu.md](05-docker-inline-gpu.md)
3. **进阶学习**：[08-hello-python.md](08-hello-python.md)（本地构建+只读根）、[02-multi-container.md](02-multi-container.md)（网络隔离与健康检查）
4. **高级专题**：[09-redis-cluster.md](09-redis-cluster.md)（集群拓扑）、[10-nodeproj.md](10-nodeproj.md)（开发环境+extends）、[11-awx-large-app.md](11-awx-large-app.md)（企业级部署）
5. **全局索引**：[03-official-examples-gallery.md](03-official-examples-gallery.md) 提供 12 个官方示例的模式对照表

## 官方示例图鉴

仓库 `examples/` 目录的 12 个官方示例（echo、hello-app、azure-vote、busybox、wordpress、hello-python、hello-app-redis、nodeproj、nvidia-smi、docker-inline、awx3、awx17）已逐个拆解为模式速查，见 [03-official-examples-gallery.md](03-official-examples-gallery.md)。

```{toctree}
:hidden:
:maxdepth: 2

01-wordpress
02-multi-container
03-official-examples-gallery
04-echo-hello-app
05-docker-inline-gpu
06-azure-vote
07-busybox-syntax
08-hello-python
09-redis-cluster
10-nodeproj
11-awx-large-app
```
