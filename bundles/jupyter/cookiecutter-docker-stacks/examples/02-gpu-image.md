---
type: Example
title: "GPU/CUDA 深度学习镜像"
description: "创建基于pytorch-notebook:cuda12的GPU深度学习镜像，验证CUDA可用性、配置GPU测试"
tags: [example, gpu, cuda, pytorch, deep-learning]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-files, resource: "/references/template-files.md", title: "模板文件源码索引" }
  - { id: src-workflow, resource: "/references/workflow-source.md", title: "CI/CD工作流源码索引" }
---

# GPU/CUDA 深度学习镜像

本示例演示如何创建一个基于 PyTorch CUDA 12 的 GPU 深度学习镜像，添加额外的深度学习库，并编写 GPU 可用性测试。

## 前置条件

- 主机有 NVIDIA GPU
- 已安装 NVIDIA Driver
- 已安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

验证GPU环境：
```bash
nvidia-smi
```

## 步骤1：生成项目

```bash
cookiecutter https://github.com/jupyter/cookiecutter-docker-stacks \
  --config-file configs/pytorch-cuda12.yaml \
  --no-input \
  --output-dir .
```

将默认的 `my-jupyter-stack` 重命名为有意义的名称：
```bash
mv my-jupyter-stack my-gpu-ml-stack
cd my-gpu-ml-stack
```

## 步骤2：编写 Dockerfile

编辑 `image/Dockerfile`：

```dockerfile
FROM quay.io/jupyter/pytorch-notebook:cuda12-latest

LABEL maintainer="Your Name <your@email.com>"
LABEL description="GPU-accelerated ML stack with PyTorch CUDA 12"

# 安装额外的深度学习库
RUN pip install --no-cache-dir \
    'pytorch-lightning' \
    'torchmetrics' \
    'transformers' \
    'datasets' \
    'accelerate' \
    'wandb' \
    'tensorboard' \
    'opencv-python-headless' \
    'albumentations' \
    'timm'

# 切换到root安装系统工具
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git-lfs \
        libgl1-mesa-glx \
        libglib2.0-0 \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 配置Git LFS
RUN git lfs install

# 切回非特权用户
USER ${NB_UID}
```

## 步骤3：编写GPU测试

创建 `tests/test_gpu.py`：

```python
"""GPU/CUDA可用性测试"""
import pytest
from tests.utils.tracked_container import TrackedContainer


def test_pytorch_cuda_available(container: TrackedContainer):
    """验证PyTorch可以检测到CUDA"""
    container.run_detached(
        runtime="nvidia",
        environment={"NVIDIA_VISIBLE_DEVICES": "all"}
    )
    output = container.exec_cmd(
        "python -c 'import torch; print(torch.cuda.is_available())'"
    )
    assert "True" in output, "CUDA is not available. Ensure --gpus flag is used."


def test_pytorch_cuda_device_count(container: TrackedContainer):
    """验证GPU设备数量"""
    container.run_detached(
        runtime="nvidia",
        environment={"NVIDIA_VISIBLE_DEVICES": "all"}
    )
    output = container.exec_cmd(
        "python -c 'import torch; print(torch.cuda.device_count())'"
    )
    count = int(output.strip())
    assert count > 0, f"Expected at least 1 GPU, got {count}"


def test_pytorch_cuda_version(container: TrackedContainer):
    """验证CUDA版本信息"""
    container.run_detached(
        runtime="nvidia",
        environment={"NVIDIA_VISIBLE_DEVICES": "all"}
    )
    output = container.exec_cmd(
        "python -c 'import torch; print(torch.version.cuda)'"
    )
    assert "12" in output, f"Expected CUDA 12.x, got {output.strip()}"


def test_gpu_tensor_operation(container: TrackedContainer):
    """验证GPU张量运算"""
    container.run_detached(
        runtime="nvidia",
        environment={"NVIDIA_VISIBLE_DEVICES": "all"}
    )
    output = container.exec_cmd("""python -c '
import torch
if torch.cuda.is_available():
    x = torch.randn(100, 100, device="cuda")
    y = torch.matmul(x, x)
    print(f"GPU matmul OK: {y.shape}, device={y.device}")
else:
    print("CUDA not available")
'""")
    assert "GPU matmul OK" in output
    assert "cuda" in output
```

> **注意**：GPU测试需要 `--gpus all` 参数才能访问GPU，CI/CD中通常没有GPU环境，可以通过pytest marker标记跳过：
> ```python
> @pytest.mark.gpu
> def test_pytorch_cuda_available(container):
>     ...
> ```
>
> 运行时通过 `-m "not gpu"` 跳过GPU测试。

## 步骤4：本地构建和测试

```bash
# 安装依赖
pip install -r requirements-dev.txt

# 构建镜像
docker build --rm -t myusername/my-gpu-ml-stack image/

# 运行非GPU测试（不需要GPU）
TEST_IMAGE=myusername/my-gpu-ml-stack pytest tests/ -v -m "not gpu"

# 运行GPU测试（需要GPU）
TEST_IMAGE=myusername/my-gpu-ml-stack pytest tests/ -v -m "gpu"
```

## 步骤5：运行GPU容器

```bash
# 使用--gpus all启动（必须！）
docker run -it --rm \
    --gpus all \
    -p 8888:8888 \
    -v "${PWD}":/home/jovyan/work \
    myusername/my-gpu-ml-stack
```

### 多GPU配置

```bash
# 使用所有GPU
docker run -it --rm --gpus all -p 8888:8888 myusername/my-gpu-ml-stack

# 使用特定GPU（如第0和第1号GPU）
docker run -it --rm --gpus '"device=0,1"' -p 8888:8888 myusername/my-gpu-ml-stack

# 使用单个GPU
docker run -it --rm --gpus '"device=0"' -p 8888:8888 myusername/my-gpu-ml-stack
```

## 步骤6：在Notebook中验证GPU

```python
import torch

print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
print(f"CUDA版本: {torch.version.cuda}")
print(f"GPU数量: {torch.cuda.device_count()}")
print(f"当前GPU: {torch.cuda.get_device_name(0)}")

# 简单的GPU运算测试
x = torch.randn(1000, 1000, device="cuda")
y = torch.randn(1000, 1000, device="cuda")
z = torch.matmul(x, y)
print(f"GPU矩阵乘法完成: {z.shape}")
```

## CI/CD注意事项

GitHub Actions 默认没有GPU环境。修改 `.github/workflows/docker.yml` 处理GPU测试：

```yaml
- name: Run tests ✅
  run: python3 -m pytest tests -m "not gpu"
  env:
    TEST_IMAGE: "{{cookiecutter.stack_org}}/{{cookiecutter.stack_name}}"
```

如果需要在CI中运行GPU测试，可以使用[GPU自托管runner](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/using-self-hosted-runners-in-a-workflow)。

## 常见问题

### Q: 容器内看不到GPU？

A: 确保：
1. 主机安装了NVIDIA Driver和NVIDIA Container Toolkit
2. 运行容器时加了 `--gpus all` 参数
3. `nvidia-smi` 在主机上正常工作

### Q: CUDA版本不匹配？

A: 确保主机NVIDIA Driver版本支持容器内的CUDA版本。CUDA 12需要Driver ≥ 525.60.13。

### Q: 镜像体积很大？

A: GPU镜像本身就比较大（PyTorch+CUDA通常5-10GB）。可以通过以下方式优化：
- 使用 `--no-cache-dir` 安装pip包
- 清理apt缓存
- 考虑多阶段构建（但PyTorch+CUDA本身就很大）

## 相关示例

- [创建自定义数据科学镜像](01-basic-custom-image.md)
- [高级测试编写](03-advanced-testing.md)

## 相关概念

- [预设配置与基础镜像选择](/concepts/08-config-presets.md)
- [Dockerfile模板与编写指南](/concepts/04-dockerfile-template.md)
- [测试框架详解](/concepts/05-testing-framework.md)
