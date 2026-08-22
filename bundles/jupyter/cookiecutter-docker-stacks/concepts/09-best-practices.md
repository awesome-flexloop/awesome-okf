---
type: Concept
title: "最佳实践"
description: "Dockerfile编写、镜像优化、安全加固、版本管理、测试策略、CI/CD配置的最佳实践总结"
tags: [best-practices, security, optimization, versioning, testing, production]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-files, resource: "/references/template-files.md", title: "模板文件源码索引" }
  - { id: src-workflow, resource: "/references/workflow-source.md", title: "CI/CD工作流源码索引" }
  - { id: src-tests, resource: "/references/tests-source.md", title: "测试框架源码索引" }
---

# 最佳实践

本章总结使用 cookiecutter-docker-stacks 创建和维护自定义 Jupyter Docker 镜像的最佳实践，涵盖 Dockerfile 编写、安全、性能、版本管理、测试和 CI/CD 等方面。

## Dockerfile 编写最佳实践

### 1. 始终以非root用户运行

```dockerfile
# ✅ 正确：末尾切回非特权用户
USER root
RUN apt-get update && apt-get install -y some-package
USER ${NB_UID}

# ❌ 错误：忘记切回用户，容器以root运行
USER root
RUN apt-get update && apt-get install -y some-package
# 没有 USER ${NB_UID}
```

验证方法：
```bash
docker run --rm my-image id
# 应输出 uid=1000(jovyan)
```

### 2. 合并RUN指令减少镜像层数

```dockerfile
# ✅ 正确：合并相关命令
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        pkg1 \
        pkg2 \
        pkg3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ❌ 错误：多个RUN创建多余层
RUN apt-get update
RUN apt-get install -y pkg1
RUN apt-get install -y pkg2
RUN apt-get clean
```

### 3. 清理包管理器缓存

```dockerfile
# apt
RUN apt-get update && \
    apt-get install -y --no-install-recommends <packages> && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# pip
RUN pip install --no-cache-dir <packages>

# mamba/conda
RUN mamba install --yes <packages> && \
    mamba clean --all -f -y
```

### 4. 利用构建缓存

将变化频率低的指令放在前面：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

# 1. 安装依赖（变化少，缓存命中率高）
RUN pip install --no-cache-dir \
    polars \
    duckdb \
    seaborn

# 2. 系统包（变化较少）
USER root
RUN apt-get update && ... && rm -rf /var/lib/apt/lists/*
USER ${NB_UID}

# 3. 复制代码和notebooks（变化频繁，放在最后）
COPY --chown=${NB_UID}:${NB_GID} notebooks/ ${HOME}/work/
COPY --chown=${NB_UID}:${NB_GID} custom-config.py /etc/jupyter/
```

### 5. 使用 --chown 复制文件

```dockerfile
# ✅ 正确：复制时设置所有者
COPY --chown=${NB_UID}:${NB_GID} my-file.txt ${HOME}/

# ❌ 错误：文件属于root，jovyan无法修改
COPY my-file.txt ${HOME}/
```

### 6. 同层清理原则

文件的创建、修改、删除必须在同一RUN层完成：

```dockerfile
# ✅ 正确：下载、使用、清理在同一层
RUN wget -q https://example.com/data.tar.gz -O /tmp/data.tar.gz && \
    tar -xzf /tmp/data.tar.gz -C /opt/ && \
    rm /tmp/data.tar.gz

# ❌ 错误：下载在上层，清理在下层，文件仍在镜像中
RUN wget -q https://example.com/data.tar.gz -O /tmp/data.tar.gz && \
    tar -xzf /tmp/data.tar.gz -C /opt/
RUN rm /tmp/data.tar.gz  # 不会减小镜像体积！
```

## 安全最佳实践

### 1. 固定基础镜像版本

```dockerfile
# ✅ 生产环境：使用日期标签
FROM quay.io/jupyter/scipy-notebook:2026-07-28

# ⚠️ 开发环境可使用latest，但生产必须固定
FROM quay.io/jupyter/scipy-notebook:latest
```

### 2. 不要在镜像中硬编码密钥

```dockerfile
# ❌ 错误：密钥留在镜像层中
RUN pip install -r requirements.txt --extra-index-url https://user:password@private-repo.com/simple

# ✅ 正确：使用构建时密钥（BuildKit secret）
RUN --mount=type=secret,id=pipconfig,dst=/etc/pip.conf \
    pip install -r requirements.txt
```

或在运行时通过环境变量/挂载传入密钥。

### 3. 定期更新基础镜像

利用CI/CD的定时构建功能（模板默认配置每周一构建），自动获取基础镜像的安全更新。

### 4. 最小化安装原则

- 只安装真正需要的包
- 使用 `--no-install-recommends` 安装系统包
- 定期审查和移除不再使用的包

### 5. 设置Jupyter Token

```bash
# 生产环境设置固定token
docker run -e JUPYTER_TOKEN=your-secure-token my-image

# 或使用密码
docker run -e JUPYTER_PASSWORD=your-password my-image
```

不要在没有认证的情况下暴露Jupyter到公网。

## 镜像优化最佳实践

### 1. 使用多阶段构建（复杂场景）

```dockerfile
# 构建阶段：安装编译依赖
FROM quay.io/jupyter/scipy-notebook:2026-07-28 AS builder
USER root
RUN apt-get update && apt-get install -y --no-install-recommends build-essential
USER ${NB_UID}
RUN pip install --no-cache-dir some-package-with-c-extensions

# 最终阶段：只保留运行时
FROM quay.io/jupyter/scipy-notebook:2026-07-28
COPY --from=builder /opt/conda/ /opt/conda/
```

注意：多阶段构建在Jupyter镜像中使用较少，因为基础镜像已经较大，且编译依赖通常也是运行时需要的。

### 2. 禁用 __pycache__

在Dockerfile中添加环境变量：

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1
```

防止Python生成`.pyc`文件，减少镜像体积和运行时文件写入。

### 3. 检查镜像体积

```bash
# 查看镜像大小
docker images my-image

# 分析镜像层
docker history my-image

# 使用dive工具分析（推荐）
dive my-image
```

## 版本管理最佳实践

### 1. 使用Git标签标记镜像版本

```bash
git tag v1.0.0
git push --tags
```

CI/CD可以基于Git标签推送版本化的镜像。

### 2. 使用SHA标签保证可复现

模板CI/CD已经配置了commit SHA标签（前12位）。这意味着每个构建都有唯一标签，可以精确回溯到源代码版本。

### 3. 在镜像中标记版本信息

```dockerfile
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.revision=${GIT_COMMIT}
LABEL org.opencontainers.image.source="https://github.com/org/repo"
```

### 4. 记录pip freeze

在构建过程中记录所有包版本，用于可复现性审计：

```dockerfile
RUN pip freeze > /opt/conda/pip-freeze-${STACK_VERSION}.txt
```

## 测试最佳实践

### 1. 编写有意义的测试

除了默认的`test_secured_server`，添加以下测试：

```python
def test_key_packages_importable(container):
    """验证关键包可以成功导入"""
    packages = ["polars", "duckdb", "seaborn", "xgboost"]
    for pkg in packages:
        output = container.exec_cmd(f"python -c 'import {pkg}; print({pkg}.__version__)'")
        assert output.strip(), f"Package {pkg} not importable"

def test_custom_config_applied(container, http_client, free_host_port):
    """验证自定义配置生效"""
    container.run_detached(ports={"8888/tcp": free_host_port},
                          environment={"JUPYTER_TOKEN": "test"})
    resp = http_client.get(f"http://localhost:{free_host_port}/api",
                          headers={"Authorization": "token test"})
    assert resp.status_code == 200
```

### 2. 测试非root运行

```python
def test_runs_as_non_root(container):
    """验证容器以非root用户运行"""
    container.run_detached()
    output = container.exec_cmd("id -u")
    assert output.strip() == "1000"
```

### 3. 测试启动日志无错误

```python
def test_startup_no_errors(container):
    """验证启动日志无ERROR"""
    container.run_detached()
    import time
    time.sleep(10)
    logs = container.get_logs()
    errors = TrackedContainer.get_errors(logs)
    assert len(errors) == 0, f"Found errors: {errors}"
```

### 4. 本地测试后再推PR

```bash
# 构建镜像
docker build -t my-image image/

# 运行完整测试套件
TEST_IMAGE=my-image pytest tests/ -v

# 手动验证
docker run --rm -it -p 8888:8888 my-image
```

### 5. 测试并行化

对于多个测试文件，可以使用pytest-xdist并行运行：

```bash
pip install pytest-xdist
pytest tests/ -v -n auto  # 自动使用所有CPU核心
```

## CI/CD 最佳实践

### 1. 配置DOCKERHUB_TOKEN

在GitHub仓库Settings → Secrets中配置`DOCKERHUB_TOKEN`，不要使用密码。

### 2. 添加多架构支持

对于Apple Silicon用户，添加ARM64构建支持：

```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
```

### 3. 配置镜像安全扫描

```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.OWNER }}/${{ env.IMAGE_NAME }}
    format: 'table'
    exit-code: '1'
    severity: 'CRITICAL,HIGH'
```

### 4. 使用GitHub Container Registry作为备份

除了Docker Hub，同时推送到GHCR：

```yaml
- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### 5. 保护main分支

在GitHub仓库Settings → Branches中设置分支保护规则：
- 要求PR通过CI检查才能合并
- 要求至少一个review
- 要求分支最新才能合并

## 开发工作流最佳实践

### 1. 使用Dev Container

使用模板提供的Dev Container配置，保证开发环境一致。详见[Dev Container开发环境](07-devcontainer.md)。

### 2. 使用pre-commit

模板仓库自身配置了pre-commit钩子。如果你也想在自己的项目中使用：

```bash
pip install pre-commit
# 复制.pre-commit-config.yaml到你的项目
pre-commit install
```

### 3. 使用.gitattributes统一行尾

模板已配置`* text=auto eol=lf`，确保跨平台文件一致性。

### 4. 写好README

模板生成的README很简洁，建议添加：
- 镜像用途和包含的主要包
- 使用示例（docker run命令）
- 自定义配置说明
- 版本和更新日志

### 5. 更新文档与代码同步

每次修改Dockerfile添加新包时，同步更新README中的包列表和版本信息。

## 生产部署清单

部署自定义Jupyter镜像到生产前，检查以下清单：

- [ ] 基础镜像使用固定日期标签
- [ ] 容器以非root用户运行（UID 1000）
- [ ] 设置了JUPYTER_TOKEN或JUPYTER_PASSWORD
- [ ] 敏感信息不硬编码在镜像中
- [ ] 镜像体积合理（dive分析无异常大层）
- [ ] 所有测试通过
- [ ] CI/CD配置了定时构建获取安全更新
- [ ] 镜像标签包含版本信息（日期/Git SHA）
- [ ] 挂载了持久化存储（`-v`）到`/home/jovyan/work`
- [ ] 考虑了资源限制（`--memory`、`--cpus`）
- [ ] 配置了HTTPS（使用反向代理或GEN_CERT）

## 常见陷阱

| 陷阱 | 后果 | 预防 |
|------|------|------|
| 忘记切回`USER ${NB_UID}` | 容器以root运行，安全风险 | Dockerfile末尾检查，添加测试验证UID |
| 不清理apt缓存 | 镜像体积膨胀几十到几百MB | 每条apt-get后都clean和rm lists |
| 上层删除下层文件 | 文件仍在镜像中（不减小体积） | 创建和删除在同一RUN层 |
| 使用latest标签 | 不可复现，更新引入意外breakage | 生产使用固定日期标签 |
| COPY文件不设置chown | 文件属于root，jovyan无法写入 | 使用`--chown=${NB_UID}:${NB_GID}` |
| 以root安装Python包 | 权限冲突，jovyan无法更新 | Python包以jovyan用户安装 |
| 硬编码token/密码 | 密钥泄露 | 使用环境变量或BuildKit secrets |
| CI中DOCKERHUB_TOKEN未配置 | 推送失败但构建成功 | 提前配置secrets，检查CI日志 |

## 相关概念

- [Dockerfile模板与编写指南](04-dockerfile-template.md)
- [测试框架详解](05-testing-framework.md)
- [CI/CD工作流](06-cicd-workflow.md)
- [Dev Container开发环境](07-devcontainer.md)
