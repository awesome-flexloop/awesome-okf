---
title: CI/CD 集成
id: ex-04-ci-integration
version: 0.2.0
okf-spec: v0.2
bundle: jupyter-docker-stacks
category: examples
tags: [ci, github-actions, makefile, testing, automation]
sources:
  - references/makefile-ci-source.md
  - references/tests-source.md
prerequisites:
  - concepts/11-testing-framework.md
  - concepts/12-build-ci-cd.md
  - examples/02-custom-image.md
difficulty: advanced
estimated-time: 30min
---

# CI/CD 集成

本示例展示如何将自定义 Jupyter Docker Stacks 镜像集成到 CI/CD 流水线中，包括本地测试、GitHub Actions 自动构建和镜像测试。

## 本地开发测试流程

### 使用 Makefile 构建

Jupyter Docker Stacks 项目使用 Makefile 管理构建流程。对于自定义项目，可以参考其模式：

```makefile
# Makefile 示例
REGISTRY?=quay.io/jupyter
OWNER?=my-org
# 或者使用本地标签
TAG?=2026-07-28

# 镜像列表（按依赖顺序）
IMAGES:=docker-stacks-foundation base-notebook minimal-notebook scipy-notebook

# 构建单个镜像
build/%:
    docker build \
        --build-arg REGISTRY=$(REGISTRY) \
        --build-arg OWNER=$(OWNER) \
        --tag $(OWNER)/$*:$(TAG) \
        images/$*

# 构建所有镜像
build-all: $(foreach I,$(IMAGES),build/$(I))

# 测试单个镜像
test/%:
    python -m pytest tests/by_image/$*/ -v

# 运行所有测试
test-all:
    python -m pytest tests/ -v --numprocesses=auto

# 清理
clean:
    docker system prune -f
```

### 本地快速验证命令

```bash
# 构建镜像
make build/scipy-notebook

# 运行容器冒烟测试
docker run --rm my-org/scipy-notebook:2026-07-28 \
    python -c "import numpy, pandas, scipy, matplotlib; print('All imports OK')"

# 启动容器进行手动测试
docker run -it --rm -p 8888:8888 my-org/scipy-notebook:2026-07-28

# 运行完整测试套件
make test/scipy-notebook
```

## GitHub Actions 集成

### 基础构建流水线

创建 `.github/workflows/docker-build.yml`：

```yaml
name: Build and Test Custom Jupyter Image

on:
  push:
    branches: [main]
    paths:
      - 'Dockerfile'
      - '.github/workflows/**'
  pull_request:
    branches: [main]
  schedule:
    # 每周一重建（与官方同步）
    - cron: '0 0 * * 1'

env:
  REGISTRY: quay.io
  IMAGE_NAME: my-org/my-jupyter-image
  IMAGE_TAG: ${{ github.sha }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Build and export to Docker
        uses: docker/build-push-action@v5
        with:
          context: .
          load: true
          tags: ${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }}
          build-args: |
            BASE_IMAGE=quay.io/jupyter/scipy-notebook:2026-07-28
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Smoke test - imports
        run: |
          docker run --rm ${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }} \
              python -c "import numpy, pandas, scipy, matplotlib, sklearn; print('Core packages OK')"

      - name: Smoke test - Jupyter starts
        run: |
          docker run -d --name test-jupyter -p 8888:8888 ${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }}
          sleep 5
          # 检查 Jupyter 是否响应
          docker logs test-jupyter
          curl -f http://localhost:8888/api || (docker logs test-jupyter && exit 1)
          docker stop test-jupyter
          docker rm test-jupyter

      - name: Build and push
        if: github.event_name != 'pull_request'
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }}
          build-args: |
            BASE_IMAGE=quay.io/jupyter/scipy-notebook:2026-07-28
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 多架构构建

```yaml
name: Multi-Arch Build

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  build-multiarch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: quay.io
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Build and push multi-arch
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            quay.io/my-org/my-jupyter-image:latest
            quay.io/my-org/my-jupyter-image:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## 自动化测试

### 使用 pytest + Docker SDK 测试

创建测试目录结构：

```
tests/
├── conftest.py
├── test_imports.py
├── test_jupyter.py
└── data/
    └── test_notebook.ipynb
```

`conftest.py`（参考官方 TrackedContainer 模式）：

```python
# tests/conftest.py
import docker
import pytest
import os

@pytest.fixture(scope="session")
def docker_client():
    return docker.from_env()

@pytest.fixture(scope="session")
def image_name():
    return os.environ.get("TEST_IMAGE", "my-org/my-jupyter-image:latest")

@pytest.fixture
def tracked_container(docker_client, image_name):
    """自动创建和清理容器的 fixture"""
    containers = []
    
    def _create(**kwargs):
        kwargs.setdefault("detach", True)
        kwargs.setdefault("image", image_name)
        c = docker_client.containers.run(**kwargs)
        containers.append(c)
        return c
    
    yield _create
    
    # 清理所有容器
    for c in containers:
        try:
            c.stop(timeout=1)
            c.remove(force=True)
        except Exception:
            pass
```

`test_imports.py`：

```python
# tests/test_imports.py
import time

def test_python_imports(tracked_container):
    """测试核心 Python 包能正常导入"""
    c = tracked_container(
        command="python -c \"import numpy, pandas, scipy, matplotlib; print('OK')\"",
        detach=False
    )
    result = c.wait()
    logs = c.logs().decode()
    assert result["StatusCode"] == 0, f"Import failed: {logs}"
    assert "OK" in logs

def test_conda_available(tracked_container):
    """测试 conda/mamba 可用"""
    c = tracked_container(
        command="mamba --version",
        detach=False
    )
    result = c.wait()
    logs = c.logs().decode()
    assert result["StatusCode"] == 0
    assert "mamba" in logs.lower() or "conda" in logs.lower()
```

`test_jupyter.py`：

```python
# tests/test_jupyter.py
import time
import requests

def test_jupyter_starts(tracked_container):
    """测试 Jupyter 服务能正常启动"""
    c = tracked_container(
        ports={"8888/tcp": None},
        environment={"JUPYTER_TOKEN": "test-token"}
    )
    
    # 等待 Jupyter 启动
    time.sleep(10)
    
    # 获取实际映射端口
    c.reload()
    port = c.ports["8888/tcp"][0]["HostPort"]
    
    # 测试 API 可访问
    resp = requests.get(f"http://localhost:{port}/api", timeout=5)
    assert resp.status_code == 200
    
    logs = c.logs().decode()
    assert "Jupyter Server" in logs or "JupyterLab" in logs
```

运行测试：

```bash
# 安装测试依赖
pip install pytest docker requests

# 运行测试
TEST_IMAGE=my-org/my-jupyter-image:latest pytest tests/ -v
```

### Notebook 执行测试

```python
# tests/test_notebook_execution.py
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

def test_notebook_runs(tracked_container):
    """测试 notebook 能正常执行"""
    # 使用 nbconvert 在容器内执行 notebook
    c = tracked_container(
        command=(
            "jupyter nbconvert --to notebook --execute "
            "/home/jovyan/data/test_notebook.ipynb "
            "--output /tmp/test_output.ipynb"
        ),
        volumes={
            "./tests/data": {"bind": "/home/jovyan/data", "mode": "ro"}
        },
        detach=False,
        mem_limit="2g",
    )
    result = c.wait(timeout=60)
    logs = c.logs().decode()
    assert result["StatusCode"] == 0, f"Notebook execution failed: {logs}"
```

## 官方测试框架参考

Jupyter Docker Stacks 官方测试框架提供了可复用的共享检查：

| 检查模块 | 测试内容 |
|----------|----------|
| `shared_checks/kernelspec_check.py` | 验证 Jupyter kernelspec 正确注册 |
| `shared_checks/nbconvert_check.py` | 验证 nbconvert 导出功能 |
| `shared_checks/pluto_check.py` | 验证 Pluto.jl（Julia）可用 |
| `shared_checks/r_mimetypes_check.py` | 验证 R MIME 类型 |

使用方式（在自定义测试中参考）：

```python
# 参考官方 tests/shared_checks/ 中的模式
# 使用 nbconvert 执行 notebook 作为端到端验证
```

## Docker Compose 开发环境

创建 `docker-compose.yml` 用于本地开发：

```yaml
version: '3.8'

services:
  jupyter-dev:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BASE_IMAGE: quay.io/jupyter/scipy-notebook:2026-07-28
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work
      - ./data:/home/jovyan/data
    environment:
      - JUPYTER_TOKEN=dev-token
      - DOCKER_STACKS_JUPYTER_CMD=lab
    # 开发时启用 sudo（仅本地开发！）
    user: root
    command: start-notebook.py --IdentityProvider.token=dev-token
```

```bash
# 启动开发环境
docker compose up --build

# 后台运行
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

## Makefile 完整示例

参考项目官方 Makefile 模式：

```makefile
# 配置
REGISTRY?=quay.io
OWNER?=my-org
PLATFORM?=linux/amd64
TAG?=$(shell date +%Y-%m-%d)

# 镜像构建
.PHONY: build
build:
    docker buildx build \
        --platform $(PLATFORM) \
        --build-arg BASE_IMAGE=quay.io/jupyter/scipy-notebook:2026-07-28 \
        --tag $(OWNER)/my-jupyter:$(TAG) \
        --load \
        .

.PHONY: build-all
build-all: build

# 测试
.PHONY: test
test:
    TEST_IMAGE=$(OWNER)/my-jupyter:$(TAG) pytest tests/ -v

.PHONY: test-smoke
test-smoke:
    @echo "Running smoke tests..."
    docker run --rm $(OWNER)/my-jupyter:$(TAG) python -c "import numpy, pandas; print('OK')"
    @echo "Smoke tests passed!"

# 推送
.PHONY: push
push:
    docker push $(REGISTRY)/$(OWNER)/my-jupyter:$(TAG)
    docker tag $(OWNER)/my-jupyter:$(TAG) $(REGISTRY)/$(OWNER)/my-jupyter:latest
    docker push $(REGISTRY)/$(OWNER)/my-jupyter:latest

# 开发
.PHONY: dev
dev:
    docker compose up --build

.PHONY: dev-shell
dev-shell:
    docker compose exec jupyter-dev bash

# 清理
.PHONY: clean
clean:
    docker compose down -v
    docker system prune -f
```

## CI Secrets 配置

在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `REGISTRY_USERNAME` | 镜像仓库用户名（如 Quay.io 用户名） |
| `REGISTRY_PASSWORD` | 镜像仓库密码或机器人账号 token |
| `REGISTRY_URL` | 仓库地址（如 `quay.io`） |

:::{note}
Quay.io 需要创建 Robot Account 并授予写入权限。Docker Hub 使用 Access Token。
:::

## 标签管理策略

参考官方 Tagging 系统，为自定义镜像建立一致的标签策略：

| 标签类型 | 格式 | 用途 |
|----------|------|------|
| 日期标签 | `2026-07-28` | 可复现的历史版本 |
| SHA 标签 | `sha-a1b2c3d4e5f6` | 精确对应 Git commit |
| 最新标签 | `latest` | 始终指向最新构建 |
| 版本标签 | `v1.0.0` | 语义化版本发布 |
| Python 版本 | `python-3.12` | Python 版本标识 |

## 最佳实践清单

- [ ] CI 流水线包含构建 → 冒烟测试 → 推送 三个阶段
- [ ] PR 构建不推送镜像（仅测试）
- [ ] 使用 GitHub Actions Cache 加速 Docker 构建
- [ ] 测试包含 import 检查和 Jupyter 启动检查
- [ ] 定期（每周）重建基础镜像以获取安全更新
- [ ] 使用固定日期标签而非 `latest` 保证可复现
- [ ] 生产镜像使用镜像签名（cosign）验证
- [ ] 敏感信息通过 Secrets 管理，不硬编码

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| CI 构建太慢 | 使用 buildx cache-from/cache-to 启用缓存 |
| 测试超时 | 增加 `time.sleep()` 等待时间，或使用轮询机制 |
| Docker in Docker 问题 | 使用 `setup-buildx-action` 而非 DinD |
| 权限错误 | CI 中运行容器注意 UID/GID 映射 |
| 镜像拉取限流 | 配置 Registry 镜像缓存或使用登录认证 |

## 下一步

- 查看 [常用配方集锦](05-recipes.md) 获取更多实用模板
- 学习 [测试框架](../concepts/11-testing-framework.md) 深入了解测试设计
- 阅读 [构建与 CI/CD](../concepts/12-build-ci-cd.md) 理解官方构建流程
