# 实战示例（Examples）

本目录包含AgnesAI API的可运行示例代码，每个示例都是独立可直接运行的完整代码。

## 示例清单

| 示例 | 对应概念 | 难度 | 简介 |
|------|---------|------|------|
| [openai-compatible](openai-compatible.md) | 快速开始、认证 | ⭐ 入门 | 最小化OpenAI兼容客户端配置，演示如何无缝迁移现有OpenAI代码 |
| [chat-completion](chat-completion.md) | 对话补全API | ⭐ 入门 | 基础非流式对话补全，包含响应结构解析、多轮对话、System Prompt |
| [image-generation](image-generation.md) | 图像生成API | ⭐⭐ 基础 | 文生图完整流程，包含URL/Base64输出、图片下载保存、批量生成 |
| [video-generation](video-generation.md) | 视频生成API | ⭐⭐⭐ 进阶 | 异步视频生成完整流程：任务提交→轮询等待→下载保存，含重试逻辑 |
| [agent-workflow](agent-workflow.md) | 工具调用/Function Calling | ⭐⭐⭐⭐ 高级 | Agent工具调用完整工作流：工具定义→调用判断→执行→结果回传 |

## 学习路径

```
入门 → openai-compatible → chat-completion
         ↓                    ↓
    基础能力 →      image-generation
         ↓                    ↓
    进阶 →        video-generation
         ↓
    高级 →        agent-workflow
```

## 运行示例通用步骤

1. 安装依赖：`pip install openai>=1.40.0 requests>=2.32.0`
2. 设置API密钥：`export AGNES_API_KEY="your_key"`
3. 复制示例代码到本地运行，或根据示例修改适配你的项目

所有示例代码均基于官方examples目录下的代码扩展和注释，确保可运行性。

```{toctree}
:hidden:

agent-workflow
chat-completion
image-generation
openai-compatible
video-generation
```
