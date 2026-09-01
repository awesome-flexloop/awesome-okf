# 示例文档索引

本目录包含 podman-compose 的实战示例文档，每个示例都是可直接运行的完整用例。

## 示例列表

| 序号 | 文档 | 描述 | 涉及概念 | 难度 |
|------|------|------|---------|------|
| 01 | [01-wordpress.md](01-wordpress.md) | WordPress + MariaDB 双服务部署：经典的 Web + 数据库模式，适合初学者 | 命名卷、端口映射、环境变量、服务发现 | ⭐ 入门 |
| 02 | [02-multi-container.md](02-multi-container.md) | Web + Redis 集群多容器编排：网络隔离、依赖管理、多卷配置、参数化配置 | 自定义网络、服务依赖、多卷管理、环境变量插值、profiles、健康检查 | ⭐⭐ 进阶 |

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

1. **新手入门**：先做 [01-wordpress.md](01-wordpress.md)，理解最基础的双服务编排
2. **进阶学习**：再做 [02-multi-container.md](02-multi-container.md)，掌握网络隔离、依赖管理等高级特性
3. **实践项目**：结合 [concepts/](../concepts/03-compose-patterns.md) 中的模式，为自己的应用编写 Compose 文件

## 更多官方示例

podman-compose 源码仓库的 `examples/` 目录下还有更多示例可供参考：

| 示例目录 | 描述 |
|---------|------|
| `busybox/` | 最小化 busybox 容器测试 |
| `echo/` | 简单的 echo 服务示例 |
| `hello-app/` | 单容器 Hello World 应用 |
| `hello-python/` | Python Flask 应用构建示例 |
| `nvidia-smi/` | NVIDIA GPU 容器示例 |
| `azure-vote/` | Azure 投票应用（前端+Redis） |
| `awx3/` | AWX/Ansible Tower 部署示例 |
| `nodeproj/` | Node.js 项目开发环境配置 |

```{toctree}
:hidden:
:maxdepth: 2

01-wordpress
02-multi-container
```
