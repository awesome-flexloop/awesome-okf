---
type: Example
title: busybox：配置语法参考卡
description: 官方 busybox 示例逐行详解：links 服务别名、dict/list 两种 environment 语法、空值变量透传、labels 与注释形式的选项目录
tags: [podman, compose, example, busybox, syntax, links, labels, environment]
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

# busybox：配置语法参考卡

`busybox/` 示例只有两个服务，却是官方在 `examples/` 中维护的**语法密度最高的文件**：在 30 行正文里同时演示 links 别名、两种 environment 语法、空值变量透传、labels，文件底部还用注释列出了一整份"可选字段目录"。读这一个文件，可以掌握 Compose 配置的大半语法点。

## compose 全文

```yaml
services:

    redis:
      image: docker.io/redis:alpine
      ports:
        - "6379:6379"
      environment:
        - SECRET_KEY=aabbcc
        - ENV_IS_SET

    frontend:
      image: docker.io/library/busybox:latest
      #entrypoint: []
      command: ["/bin/busybox", "httpd", "-f", "-p", "8080"]
      working_dir: /
      environment:
        SECRET_KEY2: aabbcc
        ENV_IS_SET2:
      ports:
        - "8080:8080"
      links:
        - redis:myredis
      labels:
        my.label: my_value

#tmpfs: /run
#tmpfs:
#  - /run
#  - /tmp
#user: postgresql
#working_dir: /code
#domainname: foo.com
#hostname: foo
#ipc: host
#mac_address: 02:42:ac:11:65:43
#privileged: true
#read_only: true
#shm_size: 64M
#stdin_open: true
#tty: true
```

## 正文语法点

### 1. 两种 environment 语法

redis 服务用**列表语法**：

```yaml
environment:
  - SECRET_KEY=aabbcc    # 显式赋值
  - ENV_IS_SET           # 无等号：从 podman-compose 的宿主环境继承该变量
```

frontend 服务用**dict 语法**：

```yaml
environment:
  SECRET_KEY2: aabbcc
  ENV_IS_SET2:           # 值为 null（冒号后留空）：同样表示从宿主环境继承
```

两种语法由源码 `norm_as_dict`/`norm_as_list` 归一化处理（见[配置加载管线](../concepts/06-config-pipeline.md)）：

- 列表项无 `=` 与 dict 值为 null 语义完全等价——"这个变量我不在 compose 里写死，取运行环境里的值"；
- 翻译层对这类变量的处理是：若宿主环境中存在该变量，展开为 `-e VAR=<宿主值>`（`container_to_args` 中逐变量查 `compose.environ`）；
- 实际用途：密码/密钥这类不希望写进 compose 文件的值，运行时由 shell 环境或 .env 注入。

### 2. links 服务别名

```yaml
links:
  - redis:myredis
```

含义：frontend 容器除了可以用服务名 `redis` 访问后端，还可以用别名 `myredis` 访问。源码归一化时（`flat_deps`）：

- links 项被解析为 `ServiceDependency(redis, "service_started")` 加入 `_deps`——**links 隐含启动依赖**（redis 先于 frontend 就绪）；
- 冒号后的别名 `myredis` 写入被依赖服务的 `_aliases`，最终翻译成网络别名选项。

> links 是 Docker 早期的遗留语法（在现代 Compose 中默认网络 + 服务名 DNS 已让它冗余）。本示例保留它是为了演示别名能力；新配置可以只依赖服务名，参考 azure-vote（见[06](06-azure-vote.md)）完全不写 links。

### 3. 其他正文字段

| 字段 | 值 | 说明 |
|------|-----|------|
| `command` | `["/bin/busybox", "httpd", "-f", "-p", "8080"]` | list 形式覆盖容器启动命令（busybox 自带 httpd 前台跑 8080） |
| `working_dir` | `/` | 容器内工作目录，翻译为 `-w /` |
| `labels` | `my.label: my_value` | dict 形式容器标签，翻译为 `--label my.label=my_value`（与项目自动打的 io.podman.compose.* 标签并存） |
| `ports` | `"6379:6379"` / `"8080:8080"` | 显式加引号避免 YAML 把 `6379:6379` 解析为 60 进制数字 |
| `#entrypoint: []` | 注释 | 空 list 形式覆盖 entrypoint 的写法提示 |

## 注释中的选项目录

文件底部 13 行注释（tmpfs 给出单值与列表两种写法，共 12 个可选字段）是一份"可取消注释试用"的字段清单，等价于官方语法速查：

| 注释字段 | 对应 podman 参数 / 行为 |
|---------|------------------------|
| `tmpfs: /run`（单值）/ 列表多值 | `--tmpfs` 挂载内存文件系统 |
| `user: postgresql` | `-u postgresql`，指定运行用户 |
| `working_dir: /code` | `-w /code` |
| `domainname` / `hostname: foo` | `--hostname foo`（domainname 在现代 podman 中并入 hostname 处理） |
| `ipc: host` | `--ipc=host`，共享宿主 IPC 命名空间 |
| `mac_address: 02:42:ac:11:65:43` | 网络选项 `mac=...` |
| `privileged: true` | `--privileged`，容器特权模式（危险） |
| `read_only: true` | `--read-only`，根文件系统只读 |
| `shm_size: 64M` | `--shm-size=64M` |
| `stdin_open: true` | `-i`，保持 stdin 打开 |
| `tty: true` | `--tty`，分配伪终端 |

这些字段在 [CLI 翻译层](../concepts/05-cli-translation-layer.md) 中都有对应的 argv 生成逻辑，注释清单与 `container_to_args` 的处理顺序可以互相参照。

## 运行

```bash
cd examples/busybox
ENV_IS_SET=hello ENV_IS_SET2=world podman-compose up -d
podman-compose ps
curl http://localhost:8080/          # busybox httpd 响应
podman-compose exec redis env | grep SECRET_KEY   # 验证 env 注入
podman-compose exec frontend env | grep -E "MYREDIS|ENV_IS_SET2"
```

## 学习价值

- 当你需要确认"某个字段列表形式和 dict 形式怎么写""空值环境变量什么语义""labels 写哪一层"，这是最短的可运行验证文件；
- 取消底部注释逐行实验，比读规范文档更直接；
- 它与 hello-python（[08](08-hello-python.md)）形成对照：busybox 演示"有什么字段可写"，hello-python 演示"生产式的最小安全配置（read_only+卷）"。

## 相关示例与概念

- [官方示例图鉴](03-official-examples-gallery.md)
- [Compose 文件常见模式](../concepts/03-compose-patterns.md)：字段写法系统讲解
- [配置加载管线](../concepts/06-config-pipeline.md)：环境变量归一化与短格式透传
- [CLI 翻译层与标签状态](../concepts/05-cli-translation-layer.md)：links 别名与 labels 的 argv 生成
