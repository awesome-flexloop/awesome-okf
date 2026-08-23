# Facts: tiny-universe

> 来源：https://github.com/datawhalechina/tiny-universe
> 读取日期：2026-08-23
> 说明：本项目当前仅有 README.md，无独立源码文件可统计行数；以下事实均来自 README 原文。

## 项目总览

- 项目名称：大模型白盒子构建指南（tiny-universe）
- 定位：从原理出发、以"白盒"为导向、围绕大模型全链路的"手搓"大模型指南
- 目标读者：有传统深度学习基础、希望从底层原理独立复现大模型核心部分的学习者
- 技术栈：PyTorch 层为主，部分模块使用 NumPy
- 许可证：CC BY-NC-SA 4.0
- 维护组织：Datawhale

## 主体部分模块（经典技术从零实现）

| 序号 | 模块名 | 核心功能 | 关键技术点 | 代码行数 |
|------|--------|----------|------------|----------|
| 1 | TinyDiffusion | 手写图像生成模型（最简化 DDPM） | 扩散模型公式、前向加噪、反向去噪、训练与采样流程、两小时完成图像生成预训练 | README 未提供 |
| 2 | Qwen-Blog | 深入剖析大模型原理（以 Qwen2 为例） | 以输入 tensor 视角遍历 Model 各操作块、GQA、RoPE、Attention Mask | README 未提供 |
| 3 | TinyLlama3 | 逐步预训练一个手搓大模型 | Llama 预训练流程、模型加载推理、2G 显存即可完成 | README 未提供 |
| 4 | TinyEval | 大模型评估体系 | 选择式/判别式/生成式任务评测指标、客观评测、高考数学评测（选修） | README 未提供 |
| 5 | TinyRAG | 纯手工搭建 RAG 框架 | 文档检索、向量检索、提示词拼装、答案生成；抛弃封装框架从原理实现 | README 未提供 |
| 6 | TinyAgent | 手搓一个最小的 Agent 系统 | ReAct 结构、工具调用、自主理解/规划/执行；后续计划改为 SOP 结构 | README 未提供 |
| 7 | TinyTransformer | 深入理解大模型基础 | 基于《Attention is All You Need》在 PyTorch 层手工搭建完整 Transformer | README 未提供 |
| 8 | TinyGraphRAG | 手搓一个基本的 GraphRAG 系统 | 图构建、图检索、图推理、图生成；图数据库+向量检索+图算法+LLM 协同 | README 未提供 |

## 探索部分模块（学术作品/生产阶段作品复现）

| 序号 | 模块名 | 核心功能 | 关键技术点 | 代码行数 |
|------|--------|----------|------------|----------|
| 1 | CDDRS (ADVEI25) | 细粒度语义元素指导增强的 RAG 检索方法 | 细粒度语义元素、检索增强、学术复现 | README 未提供 |

## 项目结构章节中详述的模块

README"项目结构"部分单独展开介绍了以下模块：

1. **TinyGraphRAG**（路径 `./content/TinyGraphRAG/`）
   - 定位：最简化 GraphRAG，从原理公式与架构图到代码
   - 流程：数据准备 → 查询处理 → 生成整合
   - 2025.8.12 发布

2. **TinyDiffusion**（路径 `./content/TinyDiffusion/`）
   - 定位：最简化 DDPM 模型，从论文公式到训练与采样代码
   - 流程：训练 → 推理 → 评估
   - 2024.12.25 发布，两小时完成图像生成预训练

3. **Qwen-Blog**（路径 `./content/Qwen-blog/`）
   - 定位：以 Qwen2 为例拆解 LLM 内部结构
   - 配套讲解视频（腾讯会议录播）

4. **TinyRAG**（路径 `./content/TinyRAG/`）
   - 定位：抛弃封装框架，从零手搓 RAG
   - 配套讲解视频与 GPU 镜像

5. **TinyAgent**（路径 `./content/TinyAgent/`）
   - 定位：基于 ReAct 的最小 Agent 结构，侧重工具调用
   - Datawhale 视频号有录播

6. **TinyEval**（路径 `./content/TinyEval`）
   - 定位：完善的评测体系，量身定做评测指标
   - 配套讲解视频；含高考数学评测选修内容

7. **TinyLLM**（路径 `./content/TinyLLM`）
   - 定位：简单大语言模型全流程（训练 tokenizer → 训练模型 → 文本生成）
   - 仅用 NumPy 和 PyTorch，2G 显存，数小时完成训练
   - 注：主体部分中对应条目称为 TinyLlama3，项目结构中目录为 TinyLLM

8. **TinyTransformer**（路径 `./content/TinyTransformer`）
   - 定位：基于经典论文手工搭建完整可运行 Transformer
   - 2024.5.20 作为选修内容增加

## 项目时间线（News）

- 2025.8.12：发布 TinyGraphRAG
- 2024.12.25：发布 TinyDiffusion
- 2024.10.28：发布 TinyLlama3
- 2024.6.26：TinyEval 增加高考数学评测选修
- 2024.5.20：增加 TinyTransformer 选修
- 2024.5.1：发布 Tiny-Universe V1

## 项目亮点（README 原文归纳）

- 全流程从零手搓
- 覆盖 LLM 全栈：Model → RAG → Agent → Eval
- 代码简洁清晰，更"白盒子"，对初级开发者友好
- 持续迭代（TinyLlama3、垂直领域数据集等）
- 开放贡献

## 项目负责人

- 肖鸿儒（同济大学）
- 宋志学（中国矿业大学(北京)）
- 邹雨衡（对外经济贸易大学）
