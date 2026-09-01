---
type: Example
title: 部署 Second-Me
description: 使用 Docker Compose 部署 Second-Me 个人 AI 服务，包括前后端启动、API 调用、Flask 服务配置、以及模型服务接入。
tags: [second-me, example, deploy, docker, flask, api, deployment]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: Second-Me 源码事实清单
---

## 场景说明

你需要将训练好的 Second-Me 个人 AI 部署为可访问的服务。本示例覆盖：
1. Docker Compose 部署（CPU/GPU 两种模式）
2. 前后端服务启动和端口配置
3. Flask API 接口调用（聊天、文档、训练、Space）
4. 本地开发模式启动
5. 模型服务接入配置

## 架构概览

```
┌─────────────────────────────────────────┐
│            Browser (用户)                │
│              http://localhost:3000       │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│     Next.js Frontend (lpm_frontend/)     │
│     React + TypeScript + Ant Design      │
│     端口: 3000                            │
└──────────────────┬──────────────────────┘
                   │ REST API / SSE
┌──────────────────▼──────────────────────┐
│     Flask Backend (lpm_kernel/)          │
│     端口: 8002                            │
│     ├── Documents API (文件上传/分析)     │
│     ├── Train Process API (训练流水线)    │
│     ├── Talk API (SSE 流式聊天)           │
│     ├── Space API (多Agent讨论)           │
│     ├── Role API (角色CRUD)               │
│     └── Memories API (记忆管理)           │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│     Local LLM / External LLM API         │
│     (llama.cpp / vLLM / OpenAI API)      │
└─────────────────────────────────────────┘
```

## Docker Compose 部署

### 方式 1：CPU 模式部署

```yaml
# docker-compose.yml（项目自带，以下为关键配置说明）
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8002:8002"
    volumes:
      - ./data:/app/data           # 持久化训练数据
      - ./raw_data:/app/raw_data  # 原始文档目录
      - ./models:/app/models      # 模型文件目录
    environment:
      - FLASK_ENV=production
      - LLM_PROVIDER=openai       # 或 local
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL:-https://api.openai.com/v1}
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8002
    depends_on:
      - backend
    restart: unless-stopped
```

启动命令：

```bash
# 克隆仓库
git clone https://github.com/mindverse/Second-Me.git
cd Second-Me

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 LLM API Key
# OPENAI_API_KEY=sk-xxx
# 或使用本地模型

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

### 方式 2：GPU 模式部署

需要安装 NVIDIA Docker runtime：

```bash
# 安装 nvidia-docker2（Ubuntu/Debian）
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# 使用 GPU 版本的 compose 文件启动
docker-compose -f docker-compose-gpu.yml up -d
```

GPU 版本额外配置：
- 后端镜像基于 CUDA 基础镜像
- 自动检测 NVIDIA GPU 并配置 CUDA 环境
- 支持本地模型推理（llama.cpp CUDA 后端 / vLLM）
- 训练流水线自动使用 GPU 加速

```bash
# 验证 GPU 可用
docker-compose exec backend nvidia-smi

# 检查 CUDA 可用性（通过 API）
curl http://localhost:8002/api/kernel2/cuda/available
```

### 方式 3：本地开发模式

适合开发调试，不使用 Docker：

```bash
# 后端设置
cd lpm_kernel

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动 Flask 服务
python -m flask run --host 0.0.0.0 --port 8002
# 或
python app.py
```

```bash
# 前端设置（新终端）
cd lpm_frontend

# 安装依赖（使用 pnpm）
pnpm install

# 启动开发服务器
pnpm dev
# 前端运行在 http://localhost:3000
```

Flask 后端启动后输出：

```
* Running on http://0.0.0.0:8002
* Debug mode: on/off
```

## API 接口调用示例

### 1. 健康检查

```bash
curl http://localhost:8002/api/trainprocess/training_params
```

### 2. 文件上传与管理

```bash
# 上传记忆文件（支持 txt/pdf/md）
curl -X POST http://localhost:8002/api/memories/file \
  -F "file=@./my-notes.md"

# 获取文档列表
curl http://localhost:8002/api/documents/list

# 获取文档列表（含 L0 状态）
curl "http://localhost:8002/api/documents/list?include_l0=true"

# 扫描文档目录
curl -X POST http://localhost:8002/api/documents/scan

# 分析所有未处理文档（生成 L0 洞察）
curl -X POST http://localhost:8002/api/documents/analyze

# 删除文件
curl -X DELETE http://localhost:8002/api/memories/file/my-notes.md
```

### 3. 聊天对话（流式 SSE）

```bash
# 流式聊天（Server-Sent Events）
curl -X POST http://localhost:8002/api/talk/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，你是谁？",
    "system_prompt": "",
    "role_id": null,
    "history": [],
    "enable_l0_retrieval": true,
    "enable_l1_retrieval": true,
    "temperature": 0.7,
    "max_tokens": 2048
  }' \
  --no-buffer
```

SSE 响应格式：

```
data: {"type": "content", "content": "你好"}
data: {"type": "content", "content": "！我是你的"}
data: {"type": "content", "content": "AI 数字分身"}
data: {"type": "done", "content": ""}
```

```bash
# 非流式 JSON 响应
curl -X POST http://localhost:8002/api/talk/chat_json \
  -H "Content-Type: application/json" \
  -d '{
    "message": "用一句话介绍你自己",
    "enable_l0_retrieval": true,
    "enable_l1_retrieval": true
  }'
```

### 4. 训练控制

```bash
# 启动训练
curl -X POST http://localhost:8002/api/trainprocess/start \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "my-second-me",
    "learning_rate": 0.0002,
    "number_of_epochs": 3,
    "concurrency_threads": 2,
    "data_synthesis_mode": "full",
    "use_cuda": true,
    "is_cot": true
  }'

# 获取训练进度
curl http://localhost:8002/api/trainprocess/progress/my-second-me

# SSE 实时训练日志
curl http://localhost:8002/api/trainprocess/logs --no-buffer

# 停止训练
curl -X POST http://localhost:8002/api/trainprocess/stop

# 重新训练
curl -X POST http://localhost:8002/api/trainprocess/retrain
```

### 5. 角色管理

```bash
# 创建角色
curl -X POST http://localhost:8002/api/kernel2/roles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "编程助手",
    "system_prompt": "你是一个专业的编程助手...",
    "description": "帮助编写和审查代码"
  }'

# 获取所有角色
curl http://localhost:8002/api/kernel2/roles

# 获取指定角色
curl http://localhost:8002/api/kernel2/roles/{role_uuid}

# 更新角色
curl -X PUT http://localhost:8002/api/kernel2/roles/{role_uuid} \
  -H "Content-Type: application/json" \
  -d '{"system_prompt": "更新后的prompt"}'

# 删除角色
curl -X DELETE http://localhost:8002/api/kernel2/roles/{role_uuid}

# 分享角色到远程注册中心
curl -X POST http://localhost:8002/api/kernel2/roles/share \
  -H "Content-Type: application/json" \
  -d '{"role_id": "uuid"}'
```

### 6. Space 多Agent讨论

```bash
# 创建 Space（自动启动讨论）
curl -X POST http://localhost:8002/api/space/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "技术方案讨论",
    "objective": "讨论新功能的技术实现方案",
    "host": "http://localhost:8002",
    "participants": [
      "http://another-second-me:8002",
      "http://yet-another:8002"
    ]
  }'

# 获取 Space 详情
curl http://localhost:8002/api/space/{space_id}

# 获取所有 Space
curl http://localhost:8002/api/space/all

# 获取讨论状态
curl http://localhost:8002/api/space/{space_id}/status

# 手动启动讨论
curl -X POST http://localhost:8002/api/space/{space_id}/start

# 分享 Space
curl -X POST http://localhost:8002/api/space/{space_id}/share

# 删除 Space
curl -X DELETE http://localhost:8002/api/space/{space_id}
```

Space 讨论状态常量：
- `1`: STATUS_INITIALIZED（已初始化）
- `2`: STATUS_DISCUSSING（讨论中）
- `3`: STATUS_INTERRUPTED（已中断）
- `4`: STATUS_FINISHED（已完成）

## Flask 服务启动核心代码

后端使用 Flask Blueprint 组织路由：

```python
# lpm_kernel/api/ 目录结构（概念示意）
# domains/
#   ├── documents/routes.py    → document_bp (url_prefix=/api)
#   ├── memories/routes.py     → memories_bp (无 url_prefix)
#   ├── trainprocess/routes.py → trainprocess_bp (url_prefix=/api/trainprocess)
#   ├── kernel2/
#   │   ├── routes_talk.py     → talk_bp (url_prefix=/api/talk)
#   │   └── routes/
#   │       └── role_routes.py → role_bp (url_prefix=/api/kernel2/roles)
#   └── space/
#       └── space_routes.py   → space_bp (url_prefix=/api/space)
```

Flask 应用工厂模式示意：

```python
# 概念性启动代码（实际见 lpm_kernel/app.py）
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # 启用跨域，支持前端访问

    # 注册 Blueprints
    from lpm_kernel.api.domains.documents.routes import document_bp
    from lpm_kernel.api.domains.memories.routes import memories_bp
    from lpm_kernel.api.domains.trainprocess.routes import trainprocess_bp
    from lpm_kernel.api.domains.kernel2.routes_talk import talk_bp
    from lpm_kernel.api.domains.kernel2.routes.role_routes import role_bp
    from lpm_kernel.api.domains.space.space_routes import space_bp

    app.register_blueprint(document_bp)
    app.register_blueprint(memories_bp)
    app.register_blueprint(trainprocess_bp)
    app.register_blueprint(talk_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(space_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)
```

## 前端 Zustand Store 架构

前端使用 Zustand 管理状态：

```typescript
// lpm_frontend/src/store/ 目录
// ├── useLoadInfoStore.ts      — 加载信息
// ├── useModelConfigStore.ts   — 模型配置
// ├── useSpaceStore.ts         — Space 讨论状态
// ├── useTrainingStore.ts      — 训练进度状态
// └── useUploadStore.ts        — 文件上传状态
```

前端 API 调用封装（lpm_frontend/src/service/）：

```typescript
// service/train.ts — 训练相关 API
// startTrain() → POST /api/trainprocess/start
// getTrainProgress(modelName) → GET /api/trainprocess/progress/:model_name
// checkCudaAvailability() → GET /api/kernel2/cuda/available
// startService() → POST /api/kernel2/llama/start

// service/memory.ts — 记忆文件 API
// getMemoryList() → GET /api/documents/list
// uploadMemory(file) → POST /api/memories/file (multipart/form-data)
// deleteMemory(name) → DELETE /api/memories/file/:name

// service/space.ts — Space API
// createSpace(data) → POST /api/space/create
// getSpaceDetail(id) → GET /api/space/:id
// getAllSpaces() → GET /api/space/all
// startSpace(id) → POST /api/space/:id/start

// 使用自定义 useSSE Hook 处理 SSE 流
// import { useSSE } from '../hooks/useSSE'
```

## 持久化数据目录

部署时需要挂载以下目录以持久化数据：

| 容器路径 | 用途 | 备份策略 |
|---------|------|---------|
| `/app/raw_data` | 上传的原始文档 | 定期备份 |
| `/app/data` | L0/L1/L2 处理结果 | 定期备份 |
| `/app/models` | 下载的基础模型和微调权重 | 模型文件可重新下载 |

```bash
# 备份数据
docker-compose exec backend tar czf /backup/second-me-backup.tar.gz \
  /app/data /app/raw_data

# 恢复数据
docker-compose exec backend tar xzf /backup/second-me-backup.tar.gz -C /
```

## 常见部署问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 前端无法连接后端 | CORS 或网络问题 | 检查 `NEXT_PUBLIC_API_URL` 配置，确认 backend 容器健康 |
| 训练 OOM | 显存/内存不足 | 使用 GPU 模式或减小 lora_r/batch_size |
| 文件上传失败 | 格式不支持或权限问题 | 仅支持 txt/pdf/md，检查目录写入权限 |
| 聊天返回 500 | LLM 服务未启动 | 检查 LLM 配置（API Key 或本地模型路径） |
| Docker GPU 不可用 | nvidia-docker 未安装 | 安装 nvidia-docker2 并重启 Docker |
| 模型下载慢 | HuggingFace 网络问题 | 设置 `HF_ENDPOINT=https://hf-mirror.com` 镜像 |

## 生产环境建议

1. **使用反向代理**：Nginx 处理 HTTPS 和静态文件
2. **限制资源**：为 Docker 容器设置 memory/cpuset 限制
3. **定期备份**：备份 `data/` 和 `raw_data/` 目录
4. **监控日志**：配置日志收集（如 ELK/Loki）
5. **模型缓存**：挂载 `/root/.cache/huggingface` 避免重复下载
6. **API 认证**：生产环境添加 API Key 认证中间件

## 相关概念

- [Flask API 服务](../concepts/flask-api-server.md)
- [三层记忆架构 HMM](../concepts/three-layer-memory-hmm.md)
- [训练流水线](../concepts/training-pipeline.md)
- [L2 推理模型层](../concepts/l2-inference-model.md)
- [Space 策略模式](../concepts/space-strategy.md)
