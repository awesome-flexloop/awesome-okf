---
title: GPU/CUDA 加速使用
id: ex-03-gpu-cuda
version: 0.2.0
okf-spec: v0.2
bundle: jupyter-docker-stacks
category: examples
tags: [gpu, cuda, pytorch, tensorflow, nvidia]
sources:
  - references/dockerfiles.md
  - references/startup-scripts.md
prerequisites:
  - concepts/06-specialized-stacks.md
  - examples/01-basic-run.md
  - examples/02-custom-image.md
difficulty: intermediate
estimated-time: 15min
---

# GPU/CUDA 加速使用

本示例展示如何使用 Jupyter Docker Stacks 的 GPU 加速镜像进行深度学习计算，包括 PyTorch 和 TensorFlow 的 CUDA 变体使用。

## 前置条件

- NVIDIA GPU（支持 CUDA 的显卡）
- 已安装 [NVIDIA Driver](https://www.nvidia.com/Download/index.aspx)（版本需满足 CUDA 要求）
- 已安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- Docker 配置了 `nvidia` 作为默认 runtime（或使用 `--gpus` 参数）

### 环境验证

运行以下命令验证 GPU 环境是否就绪：

```bash
# 验证 NVIDIA 驱动
nvidia-smi

# 验证 Docker 能访问 GPU
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

如果两条命令都能正常输出 GPU 信息，则环境已就绪。

## 官方 CUDA 镜像

Jupyter Docker Stacks 为 PyTorch 和 TensorFlow 提供了预构建的 CUDA 镜像。

### PyTorch CUDA 镜像

PyTorch 镜像支持 CUDA 12 和 CUDA 13 两个版本：

| 镜像标签 | CUDA 版本 | 说明 |
|----------|-----------|------|
| `quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28` | CUDA 12 | 稳定版本，兼容性好 |
| `quay.io/jupyter/pytorch-notebook:cuda13-2026-07-28` | CUDA 13 | 最新版本，需要新驱动 |

**启动 PyTorch GPU 容器**：

```bash
docker run -it --rm \
    --gpus all \
    -p 8888:8888 \
    -v "${PWD}":/home/jovyan/work \
    quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28
```

:::{note}
`--gpus all` 参数将所有可用 GPU 传递给容器。如需指定特定 GPU，使用 `--gpus '"device=0,1"'` 格式。
:::

### TensorFlow CUDA 镜像

TensorFlow 镜像使用单个 CUDA 前缀：

| 镜像标签 | CUDA 版本 |
|----------|-----------|
| `quay.io/jupyter/tensorflow-notebook:cuda-2026-07-28` | 最新官方支持 CUDA |
| `quay.io/jupyter/tensorflow-notebook:cuda-latest` | CUDA latest 标签 |

**启动 TensorFlow GPU 容器**：

```bash
docker run -it --rm \
    --gpus all \
    -p 8888:8888 \
    -v "${PWD}":/home/jovyan/work \
    quay.io/jupyter/tensorflow-notebook:cuda-2026-07-28
```

### TensorBoard 代理

TensorFlow 镜像预装了 Jupyter Server Proxy，可直接在 JupyterLab 中访问 TensorBoard：

1. 在 notebook 中启动 TensorBoard：
```python
%load_ext tensorboard
%tensorboard --logdir logs/
```

2. 或在 JupyterLab 启动面板中点击 "TensorBoard" 图标

TensorBoard 将通过代理在 JupyterLab 中打开，无需额外端口映射。

## 验证 GPU 可用性

启动容器后，在 Jupyter Notebook 中执行以下验证代码：

### PyTorch GPU 验证

```python
import torch

print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 可用: {torch.cuda.is_available()}")
print(f"CUDA 版本: {torch.version.cuda}")
print(f"GPU 数量: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"  显存总量: {torch.cuda.get_device_properties(i).total_mem / 1024**3:.1f} GB")

    # 简单 GPU 计算测试
    x = torch.randn(1000, 1000, device='cuda')
    y = torch.randn(1000, 1000, device='cuda')
    z = torch.mm(x, y)
    print(f"GPU 矩阵计算测试: {z.shape}, 设备: {z.device}")
    print("✅ PyTorch GPU 工作正常!")
```

### TensorFlow GPU 验证

```python
import tensorflow as tf

print(f"TensorFlow 版本: {tf.__version__}")
print(f"GPU 设备: {tf.config.list_physical_devices('GPU')}")

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        print(f"  - {gpu.name}")
    
    # 简单 GPU 计算测试
    with tf.device('/GPU:0'):
        a = tf.random.normal([1000, 1000])
        b = tf.random.normal([1000, 1000])
        c = tf.matmul(a, b)
    print(f"GPU 矩阵计算测试: {c.shape}")
    print("✅ TensorFlow GPU 工作正常!")
```

## 自定义 GPU 镜像

基于官方 GPU 镜像构建自定义镜像：

### JAX GPU 镜像

```dockerfile
FROM quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28

USER ${NB_UID}

# 安装 JAX with CUDA 支持
RUN pip install --no-cache-dir \
    "jax[cuda12]" \
    "flax" \
    "optax" && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

构建并运行：

```bash
docker build --rm -t jax-gpu-notebook .

docker run -it --rm \
    --gpus all \
    -p 8888:8888 \
    jax-gpu-notebook
```

### 添加额外 CUDA 库

```dockerfile
FROM quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28

USER root

# 安装额外的 CUDA 库（如需要）
RUN mamba install --yes \
    'cudnn' \
    'nccl' && \
    mamba clean --all -f -y

USER ${NB_UID}

# 安装 GPU 加速的 Python 包
RUN mamba install --yes \
    'cupy' \
    'cuml' \
    'cugraph' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

### NVIDIA 库路径配置

对于 TensorFlow 等需要正确设置 NVIDIA 库路径的场景，镜像中包含环境配置脚本。查看 `cuda/` 子目录下的 `nvidia-lib-dirs.sh`：

```bash
# 该脚本在构建时设置 LD_LIBRARY_PATH
# 可在自定义镜像中扩展
```

## 多 GPU 训练

### 使用所有 GPU

```bash
docker run -it --rm \
    --gpus all \
    -p 8888:8888 \
    quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28
```

### 指定特定 GPU

```bash
# 仅使用 GPU 0 和 1
docker run -it --rm \
    --gpus '"device=0,1"' \
    -p 8888:8888 \
    quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28
```

### PyTorch 多 GPU 示例

```python
import torch
import torch.nn as nn
from torch.nn.parallel import DataParallel

# 简单模型
model = nn.Linear(10, 2)

if torch.cuda.device_count() > 1:
    print(f"使用 {torch.cuda.device_count()} 个 GPU 进行数据并行训练")
    model = DataParallel(model)

model = model.cuda()

# 训练循环
x = torch.randn(64, 10).cuda()
y = model(x)
print(f"输出形状: {y.shape}, 设备: {y.device}")
```

## Docker Compose GPU 配置

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  jupyter-gpu:
    image: quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28
    ports:
      - "8888:8888"
    volumes:
      - ./work:/home/jovyan/work
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - JUPYTER_ENABLE_LAB=yes
    # 对于旧版 Docker Compose（v1），使用 runtime: nvidia
    # runtime: nvidia
```

启动：

```bash
docker compose up -d
```

## GPU 性能优化建议

1. **设置 CUDA 缓存分配**：
```python
import torch
# 对于 PyTorch，设置内存分配策略
torch.backends.cudnn.benchmark = True  # 自动寻找最优算法
```

2. **使用混合精度训练**：
```python
from torch.cuda.amp import GradScaler, autocast

scaler = GradScaler()

with autocast():
    outputs = model(inputs)
    loss = criterion(outputs, targets)
```

3. **监控 GPU 使用**：
```bash
# 在容器内或主机上监控
nvidia-smi -l 1  # 每秒刷新
```

4. **Jupyter 终端中使用 htop 和 nvtop**：
```bash
# 在容器内安装 nvtop（如需要）
pip install nvtop
```

## 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| `--gpus` 参数报错 | NVIDIA Container Toolkit 未安装 | 安装 nvidia-container-toolkit 并重启 Docker |
| `torch.cuda.is_available()` 返回 False | 驱动版本不匹配 | 检查 NVIDIA 驱动版本是否满足 CUDA 要求 |
| CUDA out of memory | 显存不足 | 减小 batch size，或使用 `torch.cuda.empty_cache()` |
| 容器启动慢 | 首次拉取 CUDA 镜像较大 | 预拉取镜像 `docker pull` |
| GPU 计算结果异常 | CUDA/cuDNN 版本不匹配 | 使用官方 CUDA 镜像，避免混合安装 |
| 多卡环境只看到一张卡 | `--gpus` 参数不正确 | 使用 `--gpus all` 或 `--gpus '"device=0,1,2,3"'` |

### 验证 CUDA 版本兼容性

```bash
# 检查主机 CUDA 驱动版本
nvidia-smi | grep "CUDA Version"

# 检查容器内 CUDA 版本
docker run --rm --gpus all quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28 \
    python -c "import torch; print(f'PyTorch CUDA: {torch.version.cuda}')"
```

:::{warning}
- 主机 NVIDIA 驱动版本必须 **>=** 容器内 CUDA 版本要求的驱动版本
- CUDA 12.x 需要驱动版本 >= 525.60.13
- CUDA 13.x 需要更新的驱动版本，请参考 NVIDIA 官方文档
:::

## 非 GPU 环境回退

如果在没有 GPU 的机器上运行 GPU 镜像，需注意：
- PyTorch/TensorFlow 会自动回退到 CPU 模式
- 但 CUDA 库仍会占用大量磁盘空间
- 建议非 GPU 环境使用普通镜像（非 `cuda-` 前缀）

## 下一步

- 学习 [CI/CD 集成](04-ci-integration.md) 实现 GPU 镜像的自动构建和测试
- 查看 [常用配方集锦](05-recipes.md) 获取更多 GPU 相关的 Dockerfile 模板
- 阅读官方 PyTorch/TensorFlow Docker 文档了解更多 GPU 配置选项
