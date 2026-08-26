# 概念文档

本目录包含 ai-lab-recipes 项目的核心概念讲解，帮助理解架构设计和关键组件。

## 学习路径

建议按以下顺序阅读：

1. **[配方架构概览](00-introduction.md)** → 理解双容器架构设计和目录结构
2. **[模型服务器选型](01-model-servers.md)** → 了解四种模型服务器的特点和适用场景
3. **[NLP配方概览](02-nlp-recipes.md)** → 掌握Chatbot/RAG/Agent等各类NLP应用
4. **[部署方式](03-deployment.md)** → 学习Quadlet/Bootc/Ansible三种部署方法

## 概念列表

| 文档 | 内容简介 |
|------|---------|
| [00-introduction.md](00-introduction.md) | 双容器架构（模型服务器+AI应用）、目录结构、架构优势 |
| [01-model-servers.md](01-model-servers.md) | llamacpp_python/ollama/whispercpp/object_detection 四种模型服务器对比 |
| [02-nlp-recipes.md](02-nlp-recipes.md) | Chatbot/RAG/Agent/Codegen/Function Calling/Summarizer 等NLP配方详解 |
| [03-deployment.md](03-deployment.md) | Quadlet本地部署、Bootc可启动容器、Ansible自动化部署三种方式 |
