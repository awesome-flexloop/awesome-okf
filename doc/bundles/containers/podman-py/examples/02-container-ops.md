---
type: Example
title: "容器创建、启动、停止完整操作"
description: "从零开始完成容器的拉取镜像、创建、启动、日志查看、执行命令、停止与删除的完整操作流程示例。"
tags: [podman-py, containers, create, start, stop, logs, exec_run, example]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:45:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: client
    resource: /references/client-source.md
    title: client.py PodmanClient 核心客户端
---

# 容器创建、启动、停止完整操作

本示例演示使用 podman-py 完成容器从创建到删除的完整生命周期操作：拉取镜像 → 创建容器 → 启动 → 查看状态与日志 → 执行命令 → 停止 → 删除。

## 前置条件

1. 已安装 Podman 并启动服务：

```bash
# 检查 Podman 是否可用
podman info

# 如果是 rootless 模式，确保用户 socket 可用
systemctl --user enable --now podman.socket
```

2. 已安装 podman-py：

```bash
pip install podman
```

## 完整操作脚本

```python
from podman import PodmanClient, from_env
import time

def main():
    # 使用 with 语句自动管理连接
    with from_env() as client:
        print("=" * 50)
        print("1. 检查 Podman 连接")
        print("=" * 50)

        version = client.version()
        print(f"Podman 版本: {version['Version']}")
        print(f"API 版本: {version['ApiVersion']}")
        print(f"服务可达: {client.ping()}")
        info = client.info()
        print(f"操作系统: {info['host']['os']}")
        print(f"内核版本: {info['host']['kernel']}")
        print()

        print("=" * 50)
        print("2. 拉取镜像")
        print("=" * 50)

        IMAGE = "alpine:latest"
        CONTAINER_NAME = "demo-hello"

        # 检查镜像是否存在，不存在则拉取
        if not client.images.exists(IMAGE):
            print(f"正在拉取镜像 {IMAGE} ...")
            image = client.images.pull(IMAGE, progress_bar=False)
            print(f"镜像拉取完成: {image.short_id}")
        else:
            print(f"镜像 {IMAGE} 已存在")
            image = client.images.get(IMAGE)
        print()

        print("=" * 50)
        print("3. 清理同名旧容器（如果存在）")
        print("=" * 50)

        try:
            old = client.containers.get(CONTAINER_NAME)
            print(f"发现旧容器 {CONTAINER_NAME}，正在删除...")
            old.remove(force=True)
            print("旧容器已删除")
        except Exception:
            print("没有旧容器需要清理")
        print()

        print("=" * 50)
        print("4. 创建容器")
        print("=" * 50)

        # 方式一：create() 创建后手动 start()
        container = client.containers.create(
            image=IMAGE,
            command=["sh", "-c", "echo '容器已启动' && sleep 300 && echo '容器即将退出'"],
            name=CONTAINER_NAME,
            detach=True,
            environment={
                "DEMO_ENV": "hello-podman-py",
                "PYTHONUNBUFFERED": "1",
            },
            labels={
                "app": "podman-py-demo",
                "env": "example",
            },
            hostname="demo-container",
            working_dir="/tmp",
        )
        print(f"容器已创建: {container.short_id}")
        print(f"容器名称: {container.name}")
        print(f"容器状态（创建后）: {container.status}")
        print()

        print("=" * 50)
        print("5. 启动容器")
        print("=" * 50)

        container.start()
        print("容器启动命令已发送")

        # 等待容器进入运行状态
        time.sleep(1)
        container.reload()
        print(f"容器状态（启动后）: {container.status}")
        print(f"容器 PID: {container.attrs['State'].get('Pid')}")
        print(f"启动时间: {container.attrs['State'].get('StartedAt')}")
        print()

        print("=" * 50)
        print("6. 列出运行中的容器")
        print("=" * 50)

        running = client.containers.list()
        print(f"运行中容器数量: {len(running)}")
        for c in running:
            c.reload()
            print(f"  - {c.short_id}  {c.name:20s}  {c.status:10s}  {c.image.tags[0] if c.image.tags else ''}")
        print()

        print("=" * 50)
        print("7. 在容器内执行命令")
        print("=" * 50)

        # 执行简单命令
        exit_code, output = container.exec_run("echo $DEMO_ENV")
        print(f"环境变量 DEMO_ENV: {output.decode().strip()} (exit code: {exit_code})")

        exit_code, output = container.exec_run("hostname")
        print(f"主机名: {output.decode().strip()} (exit code: {exit_code})")

        exit_code, output = container.exec_run("pwd")
        print(f"当前目录: {output.decode().strip()} (exit code: {exit_code})")

        exit_code, output = container.exec_run("id")
        print(f"用户信息: {output.decode().strip()} (exit code: {exit_code})")

        exit_code, output = container.exec_run("cat /etc/os-release | head -2")
        print("操作系统信息:")
        print(output.decode())
        print()

        print("=" * 50)
        print("8. 获取容器日志")
        print("=" * 50)

        logs = container.logs()
        print("容器日志:")
        print(logs.decode())
        print()

        print("=" * 50)
        print("9. 停止容器")
        print("=" * 50)

        print("正在停止容器...")
        container.stop(timeout=10)
        container.reload()
        print(f"容器状态（停止后）: {container.status}")
        print(f"退出码: {container.attrs['State'].get('ExitCode')}")
        print(f"结束时间: {container.attrs['State'].get('FinishedAt')}")
        print()

        print("=" * 50)
        print("10. 查看所有容器（包括已停止）")
        print("=" * 50)

        all_containers = client.containers.list(all=True)
        print(f"所有容器数量: {len(all_containers)}")
        for c in all_containers:
            c.reload()
            print(f"  - {c.short_id}  {c.name:20s}  {c.status:10s}")
        print()

        print("=" * 50)
        print("11. 删除容器")
        print("=" * 50)

        container.remove()
        print(f"容器 {CONTAINER_NAME} 已删除")

        # 验证删除
        if not client.containers.exists(CONTAINER_NAME):
            print("确认容器已不存在")
        print()

        print("=" * 50)
        print("12. 清理已停止容器（prune）")
        print("=" * 50)

        prune_result = client.containers.prune()
        print(f"清理了 {len(prune_result['ContainersDeleted'])} 个已停止容器")
        print(f"回收空间: {prune_result['SpaceReclaimed']} bytes")
        print()

        print("=" * 50)
        print("容器生命周期操作演示完成！")
        print("=" * 50)

if __name__ == "__main__":
    main()
```

## 使用 run() 快捷方式

如果不需要分步控制，`containers.run()` 可以一步完成 create + start：

```python
from podman import from_env

with from_env() as client:
    # 后台运行 Nginx 并映射端口
    print("启动 Nginx 容器...")
    nginx = client.containers.run(
        image="nginx:alpine",
        name="demo-nginx",
        ports={"80/tcp": 8080},
        detach=True,
        remove=True,  # 停止后自动删除
    )

    nginx.reload()
    print(f"Nginx 运行中: {nginx.status}")
    print(f"访问 http://localhost:8080 查看 Nginx 欢迎页")
    print()

    # 获取 Nginx 访问日志（实时流）
    print("Nginx 日志（前5秒）:")
    import time
    start = time.time()
    for line in nginx.logs(stream=True, follow=True):
        print(line.decode(), end="")
        if time.time() - start > 5:
            break
    print()

    # 停止容器（remove=True 会自动删除）
    print("停止 Nginx...")
    nginx.stop()
    print("Nginx 已停止并自动删除")
```

## 批量操作示例

```python
from podman import from_env

with from_env() as client:
    # 启动多个 Alpine 容器
    print("启动 3 个演示容器...")
    for i in range(3):
        client.containers.run(
            "alpine:latest",
            command=["sleep", "60"],
            name=f"demo-batch-{i}",
            detach=True,
            labels={"demo": "batch"},
        )
    print()

    # 列出带特定标签的容器
    print("标签为 demo=batch 的容器:")
    demo_containers = client.containers.list(
        filters={"label": "demo=batch"}
    )
    for c in demo_containers:
        c.reload()
        print(f"  - {c.name}: {c.status}")
    print()

    # 批量停止
    print("批量停止所有 demo-batch 容器...")
    for c in demo_containers:
        print(f"  停止 {c.name}...")
        c.stop(timeout=5)

    # 批量删除
    print("批量删除所有 demo-batch 容器...")
    result = client.containers.prune(
        filters={"label": ["demo=batch"]}
    )
    print(f"删除了 {len(result['ContainersDeleted'])} 个容器")
```

## 相关概念

- [/concepts/01-connection.md](/concepts/01-connection.md)
- [/concepts/03-containers.md](/concepts/03-containers.md)
- [/examples/01-migration.md](/examples/01-migration.md)
