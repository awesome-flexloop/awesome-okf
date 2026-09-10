---
type: Example
title: docker-inline 与 nvidia-smi：内联构建与 GPU 预留
description: 官方 docker-inline（dockerfile_inline 零 Dockerfile 构建）与 nvidia-smi（deploy.resources GPU 预留）两个单服务特殊场景示例
tags: [podman, compose, example, dockerfile-inline, build, gpu, nvidia]
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

# docker-inline 与 nvidia-smi：内联构建与 GPU 预留

这两个示例都是单服务，但各自演示一个"只需要一个字段就能开"的特殊能力：**不写 Dockerfile 的内联构建**与 **Compose 标准语法的 GPU 申请**。

## docker-inline：零 Dockerfile 构建

目录：`examples/docker-inline/`，完整 compose：

```yaml
---
version: '3'
services:
  dummy:
    build:
      context: .
      dockerfile_inline: |
        FROM alpine
        RUN echo "hello world"
```

### 工作机制

`dockerfile_inline` 是 Compose Spec 的 build 字段，允许把 Dockerfile 内容直接内联在 YAML 里。源码 `container_to_build_args` 对它的处理（见[CLI 翻译层](../concepts/05-cli-translation-layer.md)）：

1. 内联内容写入一个临时 `.containerfile` 文件（`tempfile.NamedTemporaryFile(delete=False, suffix=".containerfile")`）；
2. 用它作为 `-f` 参数执行 `podman build`；
3. 构建结束后删除临时文件（cleanup callback）；
4. 与 `dockerfile:` 字段**互斥**——同时设置直接报错 `dockerfile_inline and dockerfile can't be used simultaneously`。

运行：

```bash
cd examples/docker-inline
podman-compose build    # 构建镜像（alpine + 一个 echo 层）
# 或 podman-compose up 时自动构建
```

### 适用场景与限制

- **适用**：一两行指令的微定制（基于官方镜像加个包、打印构建参数、CI 探针），不值得为它维护一个 Dockerfile 文件；
- **限制**：没有 `COPY` 上下文文件可用（context 虽然存在，但内联 Dockerfile 里 COPY 需要 context 里真的有文件）；多行复杂构建仍应写 Dockerfile——示例目录里 hello-python 与 nodeproj 就是对照（它们有真实 Dockerfile，见[08](08-hello-python.md)、[10](10-nodeproj.md)）。

### 对照：标准外置 Dockerfile 长什么样

同样的功能写成 Dockerfile + compose 的传统形态：

```dockerfile
# ./Dockerfile
FROM alpine
RUN echo "hello world"
```

```yaml
services:
  dummy:
    build:
      context: .
```

> Dockerfile 查找顺序：context 下按 `Containerfile → ContainerFile → containerfile → Dockerfile → DockerFile → dockerfile` 6 个候选名依次探测（Podman 社区习惯用 Containerfile），找到即用。

## nvidia-smi：GPU 预留

目录：`examples/nvidia-smi/`，完整 compose：

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

### 字段逐项

| 字段 | 值 | 含义 |
|------|-----|------|
| `image` | nvidia/cuda:12.3.1-base | 自带 CUDA 运行时与 nvidia-smi 工具的基础镜像 |
| `command` | `nvidia-smi` | 容器启动即执行一次 nvidia-smi，打印 GPU 信息后退出 |
| `deploy.resources.reservations.devices` | 列表 | Compose v3 标准的设备预留声明 |
| `driver: nvidia` | — | 设备驱动类型，翻译层只识别 nvidia |
| `count: 1` | — | 申请 1 块 GPU（也可写 `all` 或用 `device_ids: [0,1]` 指定卡号） |
| `capabilities: [gpu]` | — | 能力过滤，必须包含 `gpu` 才被翻译 |

### 翻译结果

源码 `container_to_gpu_res_args` 把它展开为（见[CLI 翻译层](../concepts/05-cli-translation-layer.md)）：

```bash
podman create \
  --device nvidia.com/gpu=0 \
  --security-opt=label=disable \
  nvidia/cuda:12.3.1-base-ubuntu20.04 \
  nvidia-smi
```

- `--device nvidia.com/gpu=0` 经 CDI（Container Device Interface）注入设备；`count: all` 翻译为 `nvidia.com/gpu=all`；
- `--security-opt=label=disable` 是 GPU 透传时自动附加的——SELinux 标签会阻止设备访问，必须关闭；
- 宿主前置条件：安装 NVIDIA 驱动 + nvidia-container-toolkit（CDI 已生成 `/etc/cdi/nvidia.yaml`）。

### 验证

```bash
cd examples/nvidia-smi
podman-compose up
# 无 GPU 环境：podman 报无法解析设备 / 找不到 GPU
# 有 GPU 环境：打印 nvidia-smi 输出（GPU 型号、显存、驱动版本）后容器退出
```

`command: nvidia-smi` 是个一次性命令：容器跑完退出码即命令退出码。想看持续占用可 `podman-compose run test nvidia-smi -l` 或改 command 为常驻进程。

## 两个示例的共同启示

它们都展示了 podman-compose 的**薄翻译层**设计：特殊能力不需要 podman-compose 发明新语法——

- `dockerfile_inline` 是 Compose Spec 标准 build 字段，翻译层只是落临时文件；
- GPU 申请是 Compose v3 标准的 `deploy.resources` 语法，翻译层映射为 podman 的 `--device` 参数。

用户要表达的能力在 podman CLI 里都有对应物，compose 文件只是声明式外壳。

## 相关示例与概念

- [官方示例图鉴](03-official-examples-gallery.md)：模式速查
- [hello-python 本地构建](08-hello-python.md)：有真实 Dockerfile 的标准 build 形态
- [CLI 翻译层与标签状态](../concepts/05-cli-translation-layer.md)：dockerfile_inline 临时文件与 GPU 参数翻译实现
- [x-podman 扩展字段全解](../concepts/08-x-podman-extensions.md)：标准字段无法表达时的 x-podman 逃生门
