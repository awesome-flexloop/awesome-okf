# 信源登记簿（References）

本目录是AgnesAI-Models API网关知识束的信源登记，所有concepts和examples文档中引用的事实均可追溯到此处的原始信源。

## 信源清单

| 信源ID | 文档 | 原始来源 | 覆盖事实范围 |
|--------|------|---------|-------------|
| official-readme | [readme.md](readme.md) | 官方README.md | 项目介绍、快速开始、API端点、基础示例、安全规范 |
| model-catalog | [model-catalog.md](model-catalog.md) | MODEL_CATALOG.md | 完整模型列表、端点规范、能力矩阵、速率限制、配额、状态码处理 |

## 事实编号索引

- F-001 ~ F-015: README基础事实
- F-016 ~ F-030: 模型目录与端点事实
- F-031 ~ F-038: HTTP状态码处理事实

## 信源验证说明

所有事实均直接提取自官方仓库 `external/libs/models/AgnesAI/AgnesAI-Models/` 中的文档，未添加推断性内容。API调用示例与官方examples/目录下代码保持一致。
