---
type: Concept
title: 数据与 AI 模板
description: data-ai 分类包含 3 个模板：python-script（通用 Python 脚本标准样板）、jupyter-notebook（数据分析 Notebook 起点）、pytorch-starter（PyTorch 深度学习训练模板，自动 GPU 检测），覆盖数据处理和 AI 开发的核心场景。
tags: [trae-templates, data-ai, python, jupyter, pytorch, machine-learning]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 数据与 AI 模板总览

data-ai 分类包含 3 个 Python 生态模板，覆盖从脚本自动化到深度学习训练的核心场景：

| 模板 | 技术栈 | 用途 | 启动方式 |
|------|--------|------|----------|
| python-script | Python 3.8+、venv、logging | 通用脚本标准样板 | `python main.py` |
| jupyter-notebook | Python、Jupyter | 数据分析/探索 | `jupyter notebook` |
| pytorch-starter | Python、PyTorch | 深度学习模型训练 | `python train.py` |

三个模板代表了 Python 数据/AI 开发的三种典型模式：脚本式自动化、交互式探索、模型训练。

## python-script：通用 Python 脚本样板

**路径**：`templates/data-ai/python-script/`

Python 脚本标准样板，预配置虚拟环境、日志和依赖管理，适合自动化脚本和工具开发。

**文件结构**（5 个文件）：
```
python-script/
├── main.py           # 脚本主入口
├── requirements.txt  # Python 依赖
├── .gitignore        # Python 专用 .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Python 3.8+、venv（虚拟环境）、logging（日志模块）

**特性**：
- 预配置虚拟环境（venv）
- 内置日志配置（控制台输出 + 文件日志）
- 标准依赖管理（requirements.txt）
- Python 专用 .gitignore（排除 __pycache__/、*.pyc、venv/ 等）

**启动方式**：
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行脚本
python main.py
```

**设计要点**：
- 不指定 CLI 框架（argparse/click/typer 由开发者选择）
- 不指定日志框架配置（使用标准库 logging）
- 提供最基础的项目骨架，开发者按需扩展

## jupyter-notebook：数据分析 Notebook

**路径**：`templates/data-ai/jupyter-notebook/`

Jupyter Notebook 数据分析启动模板，适合数据探索、可视化和实验性分析。

**文件结构**（4 个文件）：
```
jupyter-notebook/
├── notebook.ipynb    # Jupyter Notebook 文件
├── requirements.txt  # jupyter 及数据分析依赖
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Python、Jupyter

**启动方式**：
```bash
pip install -r requirements.txt
jupyter notebook
# 浏览器自动打开，点击 notebook.ipynb
```

**适用场景**：
- 数据探索与清洗
- 数据可视化（matplotlib/seaborn/plotly）
- 统计分析
- 机器学习实验
- 教学和演示

**Jupyter Notebook 特点**：
- 代码和文档（Markdown）交替组织
- 单元格逐段执行，即时反馈
- 支持内联图表和可视化
- 适合探索性工作流，不适合生产代码

## pytorch-starter：PyTorch 深度学习训练

**路径**：`templates/data-ai/pytorch-starter/`

PyTorch 深度学习训练脚本模板，自动检测 CUDA 可用性。

**文件结构**（5 个文件）：
```
pytorch-starter/
├── train.py          # 训练脚本（含 GPU 自动检测）
├── requirements.txt  # torch、torchvision 等
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Python、PyTorch

**启动方式**：
```bash
pip install -r requirements.txt
python train.py
```

**核心特性**：自动检测 CUDA 可用性，将模型和数据自动移至 GPU（如果可用）。这是深度学习训练脚本的标准模式：

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
data = data.to(device)
```

**PyTorch 训练循环典型结构**（模板提供的基础框架）：
1. 数据加载（DataLoader）
2. 模型定义（nn.Module）
3. 损失函数和优化器
4. 训练循环（前向传播→计算损失→反向传播→参数更新）
5. 验证/评估
6. 模型保存

**适用场景**：
- 计算机视觉模型训练
- NLP 模型训练
- 推荐系统
- 迁移学习
- 模型微调

## 数据/AI 开发的三种模式

### 脚本模式（python-script）

**特点**：线性执行、确定性结果、可重复运行
**适用**：数据管道、ETL、自动化任务、定时脚本
**反模式**：不适合需要即时反馈和可视化的探索性工作

### Notebook 模式（jupyter-notebook）

**特点**：交互式执行、即时可视化、文档代码混合
**适用**：数据探索、实验分析、教学演示、原型验证
**反模式**：不适合生产代码、长时间运行任务、版本控制不友好

### 训练模式（pytorch-starter）

**特点**：GPU 加速、长时间运行、实验管理
**适用**：模型训练、超参数搜索、分布式训练
**反模式**：不适合轻量脚本或交互式探索

## 模板组合建议

实际数据/AI 项目中通常需要组合多个模板：

| 项目类型 | 推荐组合 |
|----------|----------|
| 数据分析项目 | jupyter-notebook + python-script（数据处理脚本）+ editor-config + gitignore |
| ML 模型开发 | pytorch-starter + jupyter-notebook（实验分析）+ superpowers-trae-init |
| 自动化数据管道 | python-script + docker-compose（数据库） |
| AI Web 应用 | nextjs-starter（前端）+ fastapi-service（模型 API）+ pytorch-starter（训练） |

## Python 生态模板的共性设计

三个模板都遵循以下设计原则：

1. **requirements.txt 而非 Pipfile/poetry.lock**：不锁定依赖版本，开发者自行选择包管理器
2. **单入口文件**：main.py、notebook.ipynb、train.py 都是明确的起点
3. **标准 .gitignore**：排除 Python 缓存和虚拟环境
4. **不预设框架**：不指定 pandas/numpy/scikit-learn 等具体数据科学库，按需安装

## 与后端模板的区别

data-ai 模板与 backend-service 的 fastapi-service 有区别：

| 维度 | python-script / pytorch-starter | fastapi-service |
|------|--------------------------------|-----------------|
| **定位** | 脚本/训练任务 | HTTP API 服务 |
| **运行方式** | 单次执行或训练循环 | 长期运行的服务器 |
| **端口** | 无 | 8000 |
| **IO 模式** | 文件读写/标准输出 | HTTP 请求/响应 |
| **适用场景** | 离线处理、模型训练 | 在线推理、REST API |

如果需要将训练好的模型部署为 API 服务，fastapi-service 是 pytorch-starter 的自然补充。

## 相关概念

- [五维分面分类体系](01-template-classification.md)
- [后端服务模板](03-backend-templates.md)
- [工具与 DevOps 模板](06-tools-devops-templates.md)
- [AGENTS.md 开发契约](07-agents-contract.md)

## 相关内容

- [源码信源索引](../references/templates-source.md)
