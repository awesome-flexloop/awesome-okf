---
type: Example
title: conmon 基本命令行使用
description: 编译安装conmon、通过命令行手动启动容器、理解CLI参数、观察日志文件和退出状态的完整实践示例
tags: [example, cli, basic-usage, build, install, command-line]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: readme-source
    resource: /bundles/containers/conmon/references/readme-source.md
    title: README 项目说明信源
  - id: conmon-source
    resource: /bundles/containers/conmon/references/conmon-source.md
    title: conmon 主入口信源
---

# conmon 基本命令行使用

本示例演示如何从源码编译 conmon，理解其主要命令行参数，以及如何手动通过 conmon + runc 启动一个 OCI 容器。

> **注意**：实际使用中 conmon 通常由 Podman/CRI-O 自动调用，很少需要手动执行。本示例用于理解 conmon 的工作机制。

## 前置条件

- Linux 操作系统（conmon 是 Linux 特定的容器组件）
- GCC 编译器
- GLib 2.0 开发库
- systemd 开发库（可选，用于 journald 日志支持）
- runc 或 crun（OCI 运行时）
- make、pkg-config 等构建工具

### 安装依赖（Fedora/CentOS/RHEL）

```bash
sudo yum install -y gcc git glib2-devel glibc-devel systemd-devel make pkgconfig runc
```

### 安装依赖（Debian/Ubuntu）

```bash
sudo apt-get install gcc git libc6-dev libglib2.0-dev pkg-config make runc
```

## 步骤1：编译安装 conmon

从源码编译：

```bash
git clone https://github.com/containers/conmon.git
cd conmon
make
```

编译成功后，当前目录会生成 `conmon` 二进制文件。可以选择安装到系统：

```bash
# 安装到 /usr/local/bin
sudo make install

# 或安装到 Podman 使用的路径
sudo make podman

# 或安装到 CRI-O 使用的路径
sudo make crio
```

验证安装：

```bash
conmon --version
conmon --help
```

## 步骤2：准备 OCI bundle

conmon 需要一个 OCI bundle 目录来运行容器。最简单的方式是准备一个根文件系统和 config.json：

```bash
# 创建工作目录
mkdir -p /tmp/conmon-test/rootfs
cd /tmp/conmon-test

# 导出一个最小 Alpine 镜像作为 rootfs（需要 skopeo 或 podman）
# 方式1：使用 podman
podman create --name conmon-temp alpine
podman export conmon-temp | tar -C rootfs -xf -
podman rm conmon-temp

# 方式2：如果没有 podman，可以下载 busybox 静态二进制做极简测试
# mkdir -p rootfs/bin
# curl -Lo rootfs/bin/busybox https://busybox.net/downloads/binaries/1.35.0-x86_64-linux-musl/busybox
# chmod +x rootfs/bin/busybox
# for cmd in sh ls echo cat; do ln -s busybox rootfs/bin/$cmd; done
```

生成 OCI 运行时配置 `config.json`：

```bash
# 使用 runc 生成默认配置
runc spec

# 修改 config.json：调整 args 和 terminal
# 默认配置运行 "sh"，需要设置 "terminal": false 方便测试
# 将 args 改为运行一个简单命令如 ["sleep", "10"]
```

简单修改 config.json 示例：

```json
{
  "ociVersion": "1.0.0",
  "process": {
    "terminal": false,
    "user": { "uid": 0, "gid": 0 },
    "args": ["/bin/sleep", "10"],
    "env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "TERM=xterm"
    ],
    "cwd": "/"
  },
  "root": {
    "path": "rootfs",
    "readonly": false
  },
  "hostname": "conmon-test"
}
```

## 步骤3：创建必要的目录和文件

conmon 需要几个目录来存储 pidfile、日志和持久化数据：

```bash
# 容器持久化目录（用于 exit 文件、oom 文件等）
mkdir -p /tmp/conmon-test/persist

# 日志文件路径
LOG_PATH=/tmp/conmon-test/container.log

# PID 文件路径
CONMON_PIDFILE=/tmp/conmon-test/conmon.pid
CONTAINER_PIDFILE=/tmp/conmon-test/container.pid

# 容器 ID（自定义）
CID=conmon-test-$(date +%s)
```

## 步骤4：通过 conmon 启动容器

现在使用 conmon 启动 runc 容器：

```bash
cd /tmp/conmon-test

conmon \
  --cid $CID \
  -b /tmp/conmon-test \
  -p /tmp/conmon-test/container.pid \
  -P /tmp/conmon-test/conmon.pid \
  --log-path $LOG_PATH \
  --persist-dir /tmp/conmon-test/persist \
  --runtime /usr/bin/runc \
  --exit-dir /tmp/conmon-test/ \
  --log-size-max -1 \
  -u $CID
```

### 常用 CLI 参数说明

| 参数 | 全称 | 说明 |
|------|------|------|
| `-c` / `--cid` | Container ID | 容器唯一标识符 |
| `-b` / `--bundle` | Bundle path | OCI bundle 目录路径（包含 config.json 和 rootfs） |
| `-p` | Container pidfile | 写入容器进程 PID 的文件路径 |
| `-P` | Conmon pidfile | 写入 conmon 守护进程 PID 的文件路径 |
| `-t` / `--terminal` | Terminal | 使用终端（PTY）模式 |
| `-e` / `--exec` | Exec session | 是 exec 会话而非 create 会话 |
| `-T` / `--timeout` | Timeout | 容器超时时间（秒），超时后杀死容器 |
| `--log-path` | Log path | 容器日志文件路径 |
| `--persist-dir` | Persist directory | 容器持久化目录（存放 exit/oom 文件） |
| `--runtime` | Runtime path | OCI 运行时路径（runc/crun） |
| `--exit-dir` | Exit directory | 退出目录（inotify 监控用） |
| `--api-version` | API version | API 版本（0=旧版，1=新版） |
| `-u` / `--cuuid` | Container UUID | 容器 UUID（通常与 cid 相同） |
| `--sync` | Sync mode | 同步模式（不双 fork，前台运行） |
| `--no-sync-log` | No sync log | 退出前不 fsync 日志 |
| `--log-driver` | Log driver | 日志驱动（file/journald/passthrough） |

## 步骤5：观察容器运行

conmon 双 fork 后会立即返回（因为默认守护进程化），可以通过以下方式观察：

### 查看 conmon 进程

```bash
# 查看 conmon PID
cat /tmp/conmon-test/conmon.pid

# 查看进程树
ps auxf | grep conmon
# 应该看到 conmon 进程，其孙子进程是 runc init，然后是 sleep 10

# 查看容器 PID
cat /tmp/conmon-test/container.pid
```

### 查看容器日志

容器的 stdout/stderr 会写入日志文件：

```bash
# 如果容器有输出
cat /tmp/conmon-test/container.log

# Kubernetes CRI 格式日志示例：
# 2024-01-01T00:00:00.000000000Z stdout F Hello from container
```

对于 `sleep 10` 这样没有输出的命令，日志文件可能为空。

### 等待容器退出

等待约 10 秒让 sleep 完成，然后检查退出状态：

```bash
# 等待 conmon 退出
while kill -0 $(cat /tmp/conmon-test/conmon.pid) 2>/dev/null; do
    sleep 1
done

# 查看退出码
cat /tmp/conmon-test/persist/exit
# 应该输出 0（sleep 正常退出）

# exit-dir 下也有以容器ID命名的退出文件
cat /tmp/conmon-test/$CID
```

### 检查 OOM 文件（如果容器因 OOM 被杀）

```bash
# 正常退出时 oom 文件不存在
ls -la /tmp/conmon-test/persist/oom 2>/dev/null || echo "No OOM (expected)"
```

## 步骤6：使用终端模式（交互式）

要启动交互式 shell，需要使用 `-t`（terminal）模式，并设置 console socket：

```bash
# 创建一个新的 bundle 用于测试
mkdir -p /tmp/conmon-tty/rootfs
cd /tmp/conmon-tty
# 准备 rootfs...（同前）
runc spec
# 修改 config.json 设置 "terminal": true
```

由于终端模式需要通过 console socket 连接 PTY，这通常由 Podman/CRI-O 处理。手动测试可以使用 `--sync` 模式前台运行并观察：

```bash
# 同步模式前台运行（不双 fork），便于调试
conmon \
  --cid test-tty \
  -b /tmp/conmon-tty \
  -p /tmp/conmon-tty/container.pid \
  -P /tmp/conmon-tty/conmon.pid \
  --log-path /tmp/conmon-tty/container.log \
  --persist-dir /tmp/conmon-tty/persist \
  --runtime /usr/bin/runc \
  --exit-dir /tmp/conmon-tty/ \
  --sync \
  -t \
  -u test-tty
```

`--sync` 模式下 conmon 不双 fork，可以直接在前台看到调试日志。

## 步骤7：超时测试

使用 `-T` 参数设置超时，验证超时杀死机制：

```bash
# 创建 bundle，运行 sleep 60，但设置超时 5 秒
conmon \
  --cid timeout-test \
  -b /tmp/conmon-test \
  -p /tmp/conmon-test/container.pid \
  -P /tmp/conmon-test/conmon.pid \
  --log-path /tmp/conmon-test/container.log \
  --persist-dir /tmp/conmon-test/persist \
  --runtime /usr/bin/runc \
  --exit-dir /tmp/conmon-test/ \
  -T 5 \
  -u timeout-test

# 等待约 5 秒
sleep 6

# 检查退出码
cat /tmp/conmon-test/persist/exit
# 超时退出的状态码不是 0，exit-message 为 "command timed out"
```

## 步骤8：清理测试环境

```bash
# 确保容器已停止
CONTAINER_PID=$(cat /tmp/conmon-test/container.pid 2>/dev/null)
if [ -n "$CONTAINER_PID" ] && kill -0 $CONTAINER_PID 2>/dev/null; then
    kill -9 $CONTAINER_PID
fi

# 清理临时目录
rm -rf /tmp/conmon-test /tmp/conmon-tty
```

## 常见问题排查

### conmon 立即退出且无日志

检查：
1. `--bundle/-b` 路径是否正确，config.json 是否存在且有效
2. rootfs 路径是否正确（config.json 中的 root.path）
3. runc 是否在 PATH 中或通过 `--runtime` 指定了正确路径
4. 使用 `--sync` 前台运行查看错误输出

### "Container ID not provided. Use --cid" 错误

必须使用 `--cid/-c` 参数提供容器 ID：

```bash
conmon -c my-container-id ...
```

### 日志文件为空

- 确认 `--log-path` 指定的路径可写
- 确认进程确实有输出（sleep 不会产生输出）
- 非终端模式下 stderr 管道总是创建，stdout 需要进程实际写入

## 相关概念

- [进程生命周期管理](../concepts/01-process-lifecycle.md) — 理解为什么 conmon 启动后立即返回
- [事件循环与信号处理](../concepts/02-event-loop.md) — 理解 conmon 如何在后台监控容器
- [与Podman/CRI-O集成](02-integration.md) — 了解实际场景中 Podman 如何调用 conmon
