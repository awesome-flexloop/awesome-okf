---
type: Concept
title: 部署方式
description: ai-lab-recipes支持的三种部署方式：Quadlet本地systemd部署、Bootc可启动容器、Ansible自动化配置
tags: [部署, Quadlet, Bootc, Ansible, Podman, systemd]
generated: { by: "trae-ai", at: "2026-08-26T08:10:00Z" }
verified: { by: "process:source-code-to-okf-wiki", at: "2026-08-26T08:10:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: S-001
    resource: /references/readme-source.md
    title: 项目根目录 README.md
---

# 部署方式

ai-lab-recipes 为不同场景提供三种部署方式，覆盖从本地开发到生产环境设备 fleets 的全链路需求。

## 部署方式对比

| 部署方式 | 适用场景 | 复杂度 | 持久化 | 典型使用 |
|---------|---------|--------|--------|---------|
| Quadlet | 本地开发/单节点部署 | 低 | 容器重启需重新启动 | 开发者本地、快速验证 |
| Bootc | 设备fleets/不可变基础设施 | 中 | 操作系统级持久化 | 边缘设备、工厂设备、固定负载设备 |
| Ansible | 多节点自动化部署 | 中高 | 可配置持久化 | 服务器集群、标准化部署 |

## 方式一：Quadlet（本地systemd部署）

Quadlet 是 Podman 提供的 systemd 单元生成器，让容器可以像普通 systemd 服务一样管理。这是最简单的本地部署方式。

### 工作原理

1. `make quadlet` 生成 Kubernetes YAML 文件到 `build/` 目录
2. 使用 `podman kube play` 启动 Pod 和容器
3. 容器作为 systemd 服务运行，支持开机自启

### 部署步骤

```bash
# 进入配方目录
cd recipes/natural_language_processing/chatbot

# 生成Quadlet配置和Kubernetes YAML
make quadlet

# 启动Pod
podman kube play build/chatbot.yaml
```

### 管理命令

```bash
# 查看运行中的Pod
podman pod list
podman ps

# 查看日志
podman logs <container-name>

# 停止并删除Pod
podman pod stop chatbot
podman pod rm chatbot
```

### Quadlet 文件位置

每个配方的 `quadlet/` 目录包含：
- `<name>.image`：镜像定义
- `<name>.kube`：Kubernetes YAML 引用
- `<name>.yaml`：Kubernetes Pod 定义（包含模型服务器和应用两个容器）

### 访问应用

部署完成后，应用默认在 `http://localhost:8501` 提供服务（Streamlit 默认端口）。

## 方式二：Bootc（可启动容器）

Bootc（Bootable Containers）将应用直接嵌入操作系统镜像，实现"构建时嵌入、运行时不可变"的部署模式。特别适合边缘设备、工厂设备等固定负载场景。

### 核心概念

**可启动 OCI 容器**是将应用和操作系统打包在一起的容器镜像，可以直接作为操作系统启动。

**优势**：
- 不可变操作系统：运行时更少出错
- 原子更新：通过 `bootc switch` 一键更新整个系统+应用
- 可预测性：构建时确定所有组件，无运行时依赖安装
- 适合 fleets 设备批量管理

### 构建 Bootc 镜像

```bash
cd recipes/natural_language_processing/chatbot

# 构建默认bootc镜像
make bootc

# 自定义基础镜像和标签
make FROM=registry.redhat.io/rhel9/rhel-bootc:9.4 BOOTC_IMAGE=quay.io/your/chatbot-bootc:latest bootc

# 指定架构
make ARCH=x86_64 bootc
```

### 部署到 Bootc 系统

在已启用 bootc 的目标系统上：

```bash
# 切换到新镜像（原子更新）
bootc switch quay.io/ai-lab/chatbot-bootc:latest

# 重启系统后应用自动运行
sudo reboot

# 检查服务状态
sudo systemctl status chatbot
```

### 创建磁盘镜像

使用 bootc-image-builder 可将 bootc 镜像转换为各种磁盘格式（AMI、QCOW2、ISO等）：

```bash
make bootc-image-builder DISK_TYPE=ami
```

支持的磁盘类型见 `recipes/common/README_bootc_image_builder.md`。

## 方式三：Ansible（自动化配置）

Ansible 部署方式通过 playbook 自动化完成多节点部署配置，适合标准化服务器环境部署。

### Playbook 位置

每个支持 Ansible 的配方在 `provision/` 目录下提供：
- `playbook.yml`：主 playbook
- `requirements.yml`：Ansible 角色依赖

### 部署步骤

```bash
cd recipes/natural_language_processing/chatbot/provision

# 安装依赖角色
ansible-galaxy install -r requirements.yml

# 执行playbook
ansible-playbook playbook.yml
```

支持 Ansible 部署的配方包括：chatbot、chatbot-pydantic-ai、codegen、function_calling、graph-rag、rag 等。

## 快速开始推荐

对于大多数用户，推荐按以下顺序选择部署方式：

1. **首次体验**：使用 Podman Desktop AI Lab 扩展，图形化一键启动
2. **本地开发**：使用 `make quadlet && podman kube play build/*.yaml`
3. **单节点服务**：Quadlet + systemd 启用开机自启
4. **生产设备/边缘**：Bootc 可启动容器
5. **多节点集群**：Ansible 自动化部署

## 通用前置条件

无论使用哪种部署方式，都需要：

1. **安装 Podman**：容器运行时
2. **下载模型**：将 GGUF 模型文件放到 `models/` 目录
3. **（可选）Podman Desktop**：图形化管理界面 + AI Lab 扩展

### 下载模型示例

```bash
cd models

# 下载推荐的granite-7b-lab模型
curl -sLO https://huggingface.co/instructlab/granite-7b-lab-GGUF/resolve/main/granite-7b-lab-Q4_K_M.gguf

# 或使用make目标
make download-model-granite
```

## 端口说明

| 服务 | 默认端口 | 说明 |
|------|---------|------|
| AI应用（Streamlit） | 8501 | Web UI访问端口 |
| llamacpp_python API | 8001 | 模型服务API端口 |
| ChromaDB | 8000 | 向量数据库端口 |
| Milvus | 19530 | Milvus向量数据库端口 |

## 相关概念

- [配方架构概览](00-introduction.md)：理解双容器架构
- [模型服务器选型](01-model-servers.md)：了解要部署的模型服务器
- [NLP配方概览](02-nlp-recipes.md)：了解各类NLP应用的特点
