---
type: Concept
title: "快速上手"
description: "安装cookiecutter、使用模板生成项目、构建镜像、运行测试的完整流程"
tags: [cookiecutter, quickstart, install, build, test]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-readme, resource: "/references/template-files.md", title: "模板文件源码索引" }
  - { id: src-workflow, resource: "/references/workflow-source.md", title: "CI/CD工作流源码索引" }
  - { id: src-tests, resource: "/references/tests-source.md", title: "测试框架源码索引" }
---

# 快速上手

本章节带你从零开始，使用 cookiecutter-docker-stacks 创建你的第一个自定义 Jupyter Docker 镜像项目。

## 前置条件

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.12+ | cookiecutter 运行环境 |
| Docker | 20.10+ | 构建和运行镜像 |
| pip | 最新版 | Python包管理器 |
| Git | 任意 | 版本控制（可选） |

## 步骤1：安装 cookiecutter

```bash
pip install cookiecutter
```

验证安装：

```bash
cookiecutter --version
# 输出示例：Cookiecutter X.Y.Z
```

## 步骤2：生成项目

### 交互式生成（推荐首次使用）

```bash
cookiecutter https://github.com/jupyter/cookiecutter-docker-stacks
```

按提示依次输入：

1. **stack_name**：你的项目名（如 `my-datascience-stack`）
2. **stack_org**：你的Docker Hub用户名或组织名
3. **stack_base_image**：从14个官方镜像中选择（输入编号）
4. **stack_description**：项目描述（可直接回车使用默认值）

### 使用预设配置快速生成

如果你已经确定要使用的基础镜像，可以使用 `--config-file` 参数配合项目自带的预设配置：

```bash
# 使用scipy-notebook作为基础镜像
cookiecutter https://github.com/jupyter/cookiecutter-docker-stacks \
  --config-file configs/scipy.yaml \
  --no-input
```

预设配置文件存放在 [configs/](external/libs/jupyter/cookiecutter-docker-stacks/configs/) 目录，共14个，每个对应一个官方基础镜像。

### 本地生成

如果你已经克隆了模板仓库：

```bash
git clone https://github.com/jupyter/cookiecutter-docker-stacks.git
cd cookiecutter-docker-stacks
cookiecutter . --config-file configs/pytorch.yaml --no-input
```

## 步骤3：查看生成的项目

生成完成后，你会看到一个以 `stack_name` 命名的目录：

```bash
cd my-jupyter-stack
ls -la
```

目录结构如下：

```
my-jupyter-stack/
├── image/Dockerfile           # ← 在这里添加你的自定义内容
├── tests/                     # ← 测试代码
├── .devcontainer/             # ← VS Code开发容器配置
├── .github/workflows/docker.yml  # ← CI/CD流水线
├── requirements-dev.txt
├── README.md
├── .gitignore
└── .gitattributes
```

## 步骤4：构建镜像

```bash
docker build --rm --force-rm -t my-project/my-jupyter-stack image/
```

构建参数说明：
- `--rm`：构建成功后删除中间容器
- `--force-rm`：总是删除中间容器（即使构建失败）
- `-t`：指定镜像标签（格式为 `组织名/镜像名`）

启用 BuildKit（推荐）可以获得更快的构建速度和更好的缓存：

```bash
DOCKER_BUILDKIT=1 docker build --rm --force-rm -t my-project/my-jupyter-stack image/
```

## 步骤5：运行测试

安装测试依赖：

```bash
pip install -r requirements-dev.txt
```

运行测试（需要设置 TEST_IMAGE 环境变量）：

```bash
TEST_IMAGE=my-project/my-jupyter-stack pytest tests/ -v
```

默认测试 `test_secured_server` 会：
1. 启动一个容器映射8888端口到随机空闲端口
2. 发送HTTP请求到 Jupyter Server
3. 验证响应页面包含登录表单（`login_submit`）

预期输出：

```
collected 1 item

tests/test_notebook.py::test_secured_server PASSED
```

## 步骤6：运行镜像

```bash
docker run -it --rm -p 8888:8888 my-project/my-jupyter-stack
```

启动后你会看到类似输出：

```
    To access the server, open this file in a browser:
        ...
    Or copy and paste one of these URLs:
        http://127.0.0.1:8888/lab?token=<token>
     or http://<container-id>:8888/lab?token=<token>
```

在浏览器中打开带 token 的URL即可访问 JupyterLab。

## 步骤7：添加自定义内容

打开 `image/Dockerfile`，在注释指导下添加你的自定义内容：

```dockerfile
FROM quay.io/jupyter/scipy-notebook  # 你选择的基础镜像

# 以NB_USER安装Python包
RUN pip install <your-package>

# 如果需要安装系统包或修改权限，先切换到root
USER root
RUN apt-get update && apt-get install -y --no-install-recommends <system-package>
# ！！！务必在最后切回非特权用户！！！
USER ${NB_UID}
```

修改后重新构建镜像并测试：

```bash
docker build -t my-project/my-jupyter-stack image/
TEST_IMAGE=my-project/my-jupyter-stack pytest tests/ -v
```

## 步骤8：推送到 Docker Hub

1. 在 Docker Hub 创建账户和仓库
2. 本地登录 Docker：
   ```bash
   docker login
   ```
3. 推送镜像：
   ```bash
   docker push my-project/my-jupyter-stack
   ```

> **提示**：推送到 GitHub main 分支后，CI/CD 流水线会自动构建并推送镜像到 Docker Hub（需要配置 DOCKERHUB_TOKEN secret）。详见 [CI/CD工作流](06-cicd-workflow.md)。

## 一键命令汇总

```bash
# 安装cookiecutter
pip install cookiecutter

# 生成项目
cookiecutter https://github.com/jupyter/cookiecutter-docker-stacks

# 构建镜像
cd <stack_name>
docker build --rm -t <stack_org>/<stack_name> image/

# 运行测试
pip install -r requirements-dev.txt
TEST_IMAGE=<stack_org>/<stack_name> pytest tests/ -v

# 运行容器
docker run -it --rm -p 8888:8888 <stack_org>/<stack_name>
```

## 常见问题

### Q: 构建时出现权限错误？

A: 确保在安装系统包时使用 `USER root`，并且安装完成后切回 `USER ${NB_UID}`。详见 [Dockerfile编写指南](04-dockerfile-template.md)。

### Q: 测试无法连接到 Docker？

A: 确保 Docker daemon 正在运行。在 Linux 上检查 `docker info`，在 macOS/Windows 上启动 Docker Desktop。

### Q: 如何选择基础镜像？

A: 参见 [预设配置与基础镜像选择](08-config-presets.md) 中的镜像选择决策树。

## 相关概念

- [项目介绍](00-introduction.md)
- [模板结构解析](02-template-structure.md)
- [模板变量详解](03-cookiecutter-variables.md)
- [Dockerfile模板与编写指南](04-dockerfile-template.md)
- [测试框架详解](05-testing-framework.md)
