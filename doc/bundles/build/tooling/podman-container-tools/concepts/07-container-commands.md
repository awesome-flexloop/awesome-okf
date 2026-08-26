---
type: Concept
title: 容器操作命令
description: containers/子目录36个命令分类详解：生命周期管理、状态查询、交互执行、文件传输、检查点、提交、导出导入、暂停恢复与清理
tags: [podman, concept, commands, container, lifecycle, exec, ps, checkpoint, commit]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman Container Tools 源码信源登记
---

## 容器命令概览

`cmd/podman/containers/` 目录包含 36 个容器操作命令，覆盖容器从创建、运行到删除的完整生命周期，以及状态查询、交互、文件传输等操作。所有容器命令都在 `podman container` 父命令下，多数常用命令有顶层别名（如 `podman ps` = `podman container ps`）。

## 生命周期管理命令

生命周期命令控制容器的创建、启动、停止、重启和删除，是最基础的容器操作。

### 创建：create / init

| 命令 | 说明 |
|------|------|
| `create` | 创建新容器但不启动，分配资源并生成 OCI 规范 |
| `init` | 初始化已创建的容器，提前完成挂载、网络配置等初始化工作 |

```bash
podman create --name myapp nginx:latest
podman start myapp
```

`podman create` 只创建不启动，适合需要先配置再启动的场景。`podman init` 是可选步骤，在 `start` 之前执行可加速首次启动。

### 运行：run / start

| 命令 | 说明 |
|------|------|
| `run` | 创建并启动容器（create + start 的组合），前台模式下可交互 |
| `start` | 启动一个或多个已创建/已停止的容器 |

```bash
podman run -d --name web -p 8080:80 nginx
podman start -ai myapp
```

`podman run` 是最常用的命令，常用标志：
- `-d, --detach`：后台运行
- `-it`：交互模式（分配 TTY 并保持标准输入）
- `-p, --publish`：端口映射
- `-v, --volume`：挂载卷
- `--name`：指定容器名称
- `--rm`：退出后自动删除

`podman start` 的 `-a`（attach）标志附加到容器输出，`-i`标志保持标准输入打开。

### 停止：stop / kill / wait

| 命令 | 说明 |
|------|------|
| `stop` | 优雅停止容器（先发送 SIGTERM，超时后 SIGKILL） |
| `kill` | 立即发送信号到容器主进程（默认 SIGKILL） |
| `wait` | 阻塞等待容器停止并返回退出码 |

```bash
podman stop myapp
podman kill -s SIGINT web
podman wait myapp
echo $?
```

`podman stop` 发送 SIGTERM 给容器内 PID 1，给予优雅关闭的机会（如保存状态、关闭连接），默认10秒超时后发送 SIGKILL。`podman kill` 可指定任意信号。

### 重启：restart

| 命令 | 说明 |
|------|------|
| `restart` | 重启一个或多个运行中的容器 |

```bash
podman restart myapp
podman restart -t 30 web
```

`-t, --time` 指定停止等待超时时间（秒）。重启本质是 stop + start 的组合。

### 删除：rm

| 命令 | 说明 |
|------|------|
| `rm` | 删除一个或多个容器 |

```bash
podman rm myapp
podman rm -a
podman rm -f web
```

常用标志：
- `-f, --force`：强制删除运行中的容器（先 SIGKILL 再删除）
- `-a, --all`：删除所有容器
- `-v, --volumes`：删除关联的匿名卷

### 克隆：clone

| 命令 | 说明 |
|------|------|
| `clone` | 克隆现有容器，创建配置相同的新容器 |

```bash
podman clone myapp myapp-clone
```

克隆创建一个与原容器配置（镜像、命令、环境变量、挂载等）相同的新容器，但有新的 ID 和名称。

## 状态查询命令

状态查询命令用于查看容器的运行状态、详细配置、资源使用和日志。

### 列表：ps / list

| 命令 | 说明 |
|------|------|
| `ps` | 列出容器（默认只显示运行中的） |
| `list` | `ps` 的别名 |

```bash
podman ps
podman ps -a
podman ps -q
podman ps --format "{{.ID}} {{.Names}} {{.Status}}"
```

常用标志：
- `-a, --all`：显示所有容器（包括已停止的）
- `-q, --quiet`：只显示容器 ID
- `-s, --size`：显示容器文件大小
- `--format`：自定义输出格式（Go template）

`podman ps` 是最高频的查询命令之一，显示容器 ID、名称、状态、端口映射等信息。

### 详情：inspect / exists

| 命令 | 说明 |
|------|------|
| `inspect` | 查看容器的详细配置和状态信息（JSON 格式） |
| `exists` | 检查容器是否存在（脚本友好，返回 0/1 退出码） |

```bash
podman inspect myapp
podman inspect --format "{{.State.PID}}" myapp
podman exists myapp && echo "Container exists"
```

`podman inspect` 返回完整的容器元数据，包括网络设置、挂载点、环境变量、资源限制、重启策略等。`--format` 可提取特定字段。

### 资源使用：stats / top

| 命令 | 说明 |
|------|------|
| `stats` | 实时显示容器资源使用统计（CPU、内存、网络IO、块IO） |
| `top` | 显示容器内运行的进程 |

```bash
podman stats
podman stats myapp web
podman top myapp
podman top myapp -eo pid,user,comm
```

`podman stats` 类似 Linux `top` 命令，实时刷新资源使用情况。`podman top` 显示容器内的进程视图，可传递 ps 命令的选项。

### 日志：logs

| 命令 | 说明 |
|------|------|
| `logs` | 查看容器的标准输出和标准错误日志 |

```bash
podman logs myapp
podman logs -f web
podman logs --tail 100 myapp
podman logs -t myapp
```

常用标志：
- `-f, --follow`：实时跟踪日志输出
- `--tail N`：只显示最后 N 行
- `-t, --timestamps`：显示时间戳
- `--since`：显示指定时间之后的日志

日志由 conmon 进程收集，存储在宿主机上的日志文件中。

### 端口：port

| 命令 | 说明 |
|------|------|
| `port` | 查看容器的端口映射 |

```bash
podman port myapp
podman port myapp 80/tcp
```

显示容器端口到宿主机端口的映射关系。

### 差异：diff

| 命令 | 说明 |
|------|------|
| `diff` | 查看容器文件系统相对于镜像的变更 |

```bash
podman diff myapp
```

输出变更类型：`A`（添加）、`D`（删除）、`C`（修改），以及文件路径。

## 交互执行命令

交互命令允许用户在运行中的容器内执行命令或附加到容器终端。

### 执行命令：exec

| 命令 | 说明 |
|------|------|
| `exec` | 在运行中的容器内执行新命令 |

```bash
podman exec myapp ls /app
podman exec -it myapp /bin/bash
podman exec -u root myapp whoami
podman exec -d myapp /path/to/background-task
```

常用标志：
- `-it`：交互模式（进入 shell）
- `-d, --detach`：后台执行命令
- `-u, --user`：以指定用户执行
- `-e, --env`：设置环境变量
- `--privileged`：赋予特权

`podman exec` 是进入运行中容器调试的主要方式，启动新进程而非附加到现有进程。

### 附加终端：attach

| 命令 | 说明 |
|------|------|
| `attach` | 附加到运行中容器的主进程（PID 1）的标准输入/输出/错误 |

```bash
podman attach myapp
podman attach --sig-proxy=false myapp
```

与 `exec` 的区别：
- `attach` 连接到容器的 PID 1，共享其终端
- `exec` 启动全新进程，有独立终端
- `attach` 后按 `Ctrl-p Ctrl-q` 可分离（不停止容器）
- `--sig-proxy=false` 防止信号代理导致容器意外停止

### 运行标签：runlabel

| 命令 | 说明 |
|------|------|
| `runlabel` | 执行镜像 LABEL 中定义的命令 |

```bash
podman runlabel io.podman.config.image myimage
```

镜像可以通过 LABEL 指令预定义常用操作命令，`runlabel` 读取并执行这些标签中的命令。

## 文件传输命令

### 复制文件：cp

| 命令 | 说明 |
|------|------|
| `cp` | 在容器和宿主机之间复制文件/目录 |

```bash
podman cp myapp:/etc/nginx/nginx.conf ./nginx.conf.bak
podman cp ./local-file.txt myapp:/app/local-file.txt
podman cp ./data/ myapp:/data/
```

路径格式：
- `container:path`：容器内路径
- `path`：宿主机路径（相对或绝对）
- 支持目录递归复制
- `-p, --pause`：复制时暂停容器（保证文件一致性）

## 检查点与恢复命令

Podman 支持 CRIU（Checkpoint/Restore In Userspace）实现容器的检查点和恢复，可用于容器热迁移、快照等场景。

### 检查点：checkpoint

| 命令 | 说明 |
|------|------|
| `checkpoint` | 为运行中的容器创建检查点（冻结并保存进程状态） |

```bash
podman checkpoint myapp
podman checkpoint --export=/tmp/checkpoint.tar.gz myapp
```

`--export` 将检查点导出为归档文件，可在另一台机器上恢复。

### 恢复：restore

| 命令 | 说明 |
|------|------|
| `restore` | 从检查点恢复容器 |

```bash
podman restore myapp
podman restore --import=/tmp/checkpoint.tar.gz
podman restore -n restored-app --import=/tmp/checkpoint.tar.gz
```

`--import` 从归档文件恢复检查点，`-n` 指定恢复后的容器名称。

### 清理：cleanup

| 命令 | 说明 |
|------|------|
| `cleanup` | 清理容器的运行时残留资源（网络、挂载点等） |

```bash
podman cleanup myapp
podman cleanup --rm myapp
```

容器停止后可能残留网络配置、挂载点等资源，`cleanup` 清理这些残留。`--rm` 在清理后同时删除容器。

## 提交与导出导入命令

### 提交镜像：commit

| 命令 | 说明 |
|------|------|
| `commit` | 将容器当前状态提交为新镜像 |

```bash
podman commit myapp myimage:v1
podman commit -a "Author Name" -m "Added config" myapp myimage:v2
podman commit --change "CMD /bin/bash" myapp myimage:v3
```

常用标志：
- `-a, --author`：设置作者
- `-m, --message`：提交说明
- `--change`：应用 Dockerfile 指令修改镜像配置
- `-p, --pause`：提交时暂停容器

`podman commit` 将容器的可写层保存为新镜像层，用于从运行中的容器创建自定义镜像。

### 导出：export

| 命令 | 说明 |
|------|------|
| `export` | 将容器的文件系统导出为 tar 归档 |

```bash
podman export myapp -o container-rootfs.tar
podman export myapp | gzip > container-rootfs.tar.gz
```

导出容器的完整根文件系统为 tar 包，包含所有修改但不包含镜像历史和元数据。

### 导入镜像：import（images 组）

`import` 属于 images 命令组，可将 `export` 导出的 tar 包导入为镜像：

```bash
podman import container-rootfs.tar myimported-image:latest
```

## 暂停与恢复命令

### 暂停：pause

| 命令 | 说明 |
|------|------|
| `pause` | 暂停容器内所有进程（通过 cgroup freezer） |

```bash
podman pause myapp
podman pod pause mypod
```

`pause` 使用 Linux cgroup freezer 冻结容器进程，进程状态保持不变但不再被调度执行。与 `stop` 不同，pause 不发送信号，不终止进程，内存保持不变。

### 恢复：unpause

| 命令 | 说明 |
|------|------|
| `unpause` | 恢复已暂停的容器 |

```bash
podman unpause myapp
```

解除 cgroup freezer 冻结，进程继续从暂停点执行。

## 挂载命令

### 挂载：mount

| 命令 | 说明 |
|------|------|
| `mount` | 挂载容器的根文件系统到宿主机目录 |

```bash
podman mount myapp
podman mount
```

无参数时列出所有已挂载容器的挂载点。挂载后可在宿主机上直接访问容器文件系统。

> **注意**：`podman mount` 主要用于 ABI 本地模式，rootless 模式下可能需要 `podman unshare` 进入用户命名空间才能访问。

### 卸载：unmount

| 命令 | 说明 |
|------|------|
| `unmount` | 卸载容器的根文件系统 |

```bash
podman unmount myapp
podman unmount -a
```

`-a, --all` 卸载所有已挂载容器。

## 清理命令

### 清理：prune

| 命令 | 说明 |
|------|------|
| `prune` | 清理所有已停止的容器 |

```bash
podman container prune
podman container prune -f
```

`-f, --force` 跳过确认提示。`prune` 只删除处于 stopped/exited 状态的容器，不影响运行中的容器。

### 重命名：rename

| 命令 | 说明 |
|------|------|
| `rename` | 重命名容器 |

```bash
podman rename old-name new-name
```

修改容器名称，容器 ID 不变。

### 更新配置：update

| 命令 | 说明 |
|------|------|
| `update` | 更新运行中容器的资源限制配置 |

```bash
podman update --cpus=2 --memory=512m myapp
```

动态更新容器的 cgroup 资源限制（CPU、内存等），无需重启容器。

## 相关概念

- [容器基础](/concepts/04-container-basics.md) — Container结构体、生命周期状态机与命名空间隔离
- [CLI命令结构](/concepts/06-cli-structure.md) — Cobra框架、命令注册表与EngineMode过滤
- [镜像操作命令](/concepts/08-image-commands.md) — 镜像拉取、构建、推送等27个镜像命令
- [Pod一等公民](/concepts/05-pod-first-class.md) — Pod内容器的生命周期协调
- [架构概览](/concepts/02-architecture-overview.md) — 无守护进程架构与容器执行模型
