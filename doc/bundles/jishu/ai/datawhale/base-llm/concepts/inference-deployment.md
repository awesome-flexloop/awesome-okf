---
type: concept
title: "量化推理与服务部署"
bundle: "/datawhale/base-llm"
description: "模型量化（INT8/INT4/PTQ/AWQ/GPTQ）、DeepSpeed 分布式训练（ZeRO）、FastAPI 模型服务化、uv/Linux 云部署、Docker Compose 容器化、Git+Jenkins CI/CD 自动化。"
sources:
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter13/01_quantization.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter13/02_deepspeed.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter14/01_fastapi.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter14/02_uv_linux.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter14/03_docker_deploy.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter15/01_Git.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter15/02_Jenkins.md
related:
  - /datawhale/base-llm/concepts/finetuning-alignment
  - /datawhale/base-llm/concepts/safety-multimodal
---

# 量化推理与服务部署

## 核心理解

大模型从训练完成到生产可用，需经过"压缩→服务化→容器化→自动化"的工程链路。量化降低模型显存和计算开销；DeepSpeed 解决大规模分布式训练；FastAPI 将模型封装为 HTTP 服务；uv 和 Linux 云服务器提供运行环境；Docker Compose 保证环境一致性；Git+Jenkins 实现持续集成与部署。`code/C14/ner_deployment/` 是一个完整的 NER 服务部署范例，串联了上述技术。

## 模型量化

### 为什么需要量化

- 大模型显存占用大：7B 模型 FP16 需 ~14GB，70B 需 ~140GB。
- 推理时内存带宽是瓶颈，降低精度可减少数据搬运。
- 量化将权重从 FP16/BF16 降至 INT8/INT4，显存减半至四分之一。

### 量化基础

| 精度 | 每参数字节 | 相对显存 | 说明 |
|------|-----------|---------|------|
| FP32 | 4 字节 | 4x | 训练默认精度 |
| FP16/BF16 | 2 字节 | 2x | 推理/混合精度训练 |
| INT8 | 1 字节 | 1x | 8-bit 量化 |
| INT4 | 0.5 字节 | 0.5x | 4-bit 量化 |

### 量化方法分类

- **PTQ（Post-Training Quantization，训练后量化）**：量化已训练好的模型，无需重训。包括 RTN（舍入到最近）、GPTQ、AWQ、HQQ 等。
- **QAT（Quantization-Aware Training，量化感知训练）**：训练时模拟量化误差，精度更高但成本大。
- **GPTQ**：基于二阶信息的逐层权重量化，精度损失小。
- **AWQ（Activation-aware Weight Quantization）**：识别重要权重通道并保护，4-bit 量化效果优异。

### LLM Compressor 实战

`code/C13/01_qwen2.5_llmcompressor.ipynb` 演示使用 LLM Compressor 工具对 Qwen2.5 进行量化：
- 加载模型和分词器。
- 配置量化方案（精度、校准数据集）。
- 执行 PTQ 校准。
- 保存量化模型并验证推理。

## DeepSpeed 分布式训练

### ZeRO（Zero Redundancy Optimizer）

DeepSpeed 的核心技术，通过切分优化器状态、梯度和参数消除数据并行中的内存冗余：

| 阶段 | 切分内容 | 显存节省 |
|------|---------|---------|
| **ZeRO-1** | 优化器状态 | 4x |
| **ZeRO-2** | 优化器状态 + 梯度 | 8x |
| **ZeRO-3** | 优化器状态 + 梯度 + 参数 | N x（GPU 数量） |

### 其他关键特性

- **混合精度训练**：FP16/BF16 计算 + FP32 主权重，节省显存并加速。
- **梯度累积**：通过多步累积模拟大 batch size。
- **梯度检查点（Gradient Checkpointing）**：用计算换显存，不保存中间激活。
- **Offload**：将优化器状态/参数卸载到 CPU/NVMe。
- **张量并行/流水线并行**：支持超大规模模型训练。

## FastAPI 模型服务化

### FastAPI 核心概念

- 基于 Starlette 和 Pydantic 的现代 Python Web 框架。
- 自动生成 OpenAPI 文档（/docs 和 /redoc）。
- 原生异步支持（async/await）。
- 类型提示驱动的数据验证。

### 模型服务模式

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
model = load_model()

class PredictRequest(BaseModel):
    text: str

@app.post("/predict")
async def predict(req: PredictRequest):
    result = model(req.text)
    return {"result": result}
```

- **同步推理**：适用于轻量模型，简单直接。
- **异步推理**：适用于 I/O 密集或需并发处理，使用 `async def`。
- **批量推理**：积累请求合并 batch，提升 GPU 利用率。

### NER 部署项目

`code/C14/ner_deployment/` 是完整的生产级 NER 服务：

| 文件/目录 | 作用 |
|-----------|------|
| `main.py` | FastAPI 应用入口，定义路由和请求/响应模型 |
| `predict.py` | 模型加载和推理逻辑 |
| `src/tokenizer/` | 自定义分词器（CharTokenizer/Vocabulary） |
| `src/utils/` | 文件 I/O 等工具函数 |
| `data/` | 类别和词表文件 |
| `checkpoints/config.json` | 模型检查点配置 |
| `pyproject.toml` | 项目依赖管理 |

## uv 与 Linux 云部署

### uv 包管理器

- Rust 编写的极速 Python 包管理器，替代 pip/poetry。
- `uv venv` 创建虚拟环境，`uv pip install` 安装依赖。
- `pyproject.toml` 声明依赖，`uv.lock` 锁定版本。
- 比 pip 快 10-100 倍。

### 云服务器部署流程

1. 购买 Linux 云服务器（Ubuntu/CentOS）。
2. 配置 SSH 密钥登录和防火墙。
3. 安装 Python/uv/GPU 驱动/CUDA。
4. 克隆代码、创建虚拟环境、安装依赖。
5. 使用 systemd 或 screen/tmux 管理服务进程。
6. 配置 Nginx 反向代理和 HTTPS。

## Docker Compose 容器化部署

### Docker 核心概念

- **镜像（Image）**：只读模板，包含代码、运行时、依赖。
- **容器（Container）**：镜像的运行实例。
- **Dockerfile**：定义镜像构建步骤。

### NER 项目的 Docker 配置

`code/C14/ner_deployment/Dockerfile`：
- 基于 Python 3.10 镜像。
- 设置工作目录、安装依赖、复制代码。
- 暴露服务端口、定义启动命令。

`code/C14/ner_deployment/docker-compose.yml`：
- 定义服务、端口映射、卷挂载、环境变量、重启策略。
- 支持多服务编排（如模型服务 + Redis + Nginx）。

### 容器化优势

- 环境一致性：开发/测试/生产环境完全相同。
- 隔离性：服务间不互相干扰。
- 可移植：一次构建，到处运行。
- 易于扩展：通过 docker-compose up --scale 水平扩展。

## Git 与 CI/CD 自动化

### Git 版本控制

- 分布式版本控制系统，追踪代码变更历史。
- 分支策略：main（生产）/develop（开发）/feature（功能）/hotfix（修复）。
- 协作流程：fork → branch → commit → PR → review → merge。

### Jenkins CI/CD

Jenkins 是开源自动化服务器，构建持续集成/持续部署流水线：

1. **持续集成（CI）**：代码推送后自动触发构建、测试、代码质量检查。
2. **持续交付（CD）**：通过测试后自动部署到测试/生产环境。
3. **Pipeline as Code**：用 Jenkinsfile 定义流水线阶段（build → test → package → deploy）。
4. **集成 Docker**：流水线中自动构建镜像、推送到镜像仓库、远程部署。

典型流水线：
```
代码推送到 GitHub
    → Jenkins webhook 触发
    → 拉取代码 → 安装依赖 → 运行测试
    → 构建 Docker 镜像 → 推送镜像仓库
    → SSH 到服务器 → docker-compose pull/up
    → 健康检查 → 通知结果
```

## 工程化全景

```
模型训练完成
    ↓
量化压缩（INT8/INT4，LLM Compressor）
    ↓
服务封装（FastAPI：路由/请求验证/异步推理）
    ↓
环境管理（uv + pyproject.toml）
    ↓
容器化（Dockerfile + docker-compose.yml）
    ↓
云部署（Linux 服务器 + Nginx 反向代理）
    ↓
自动化（Git 版本控制 + Jenkins CI/CD）
    ↓
生产监控与迭代
```

## 延伸阅读

- 前置：[参数高效微调与人类对齐](finetuning-alignment.md)
- 后续：[大模型安全与多模态前沿](safety-multimodal.md)
- 示例代码：[C14 部署代码](../examples/index.md#c14-服务部署)
