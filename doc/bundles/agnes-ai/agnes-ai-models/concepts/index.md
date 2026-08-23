# 概念文档（Concepts）

本目录包含AgnesAI API网关的核心概念文档，按学习路径从入门到进阶排列。

## 入门篇

| 文档 | 简介 |
|------|------|
| [00 Agnes AI 简介](00-introduction.md) | AgnesAI平台定位、模型家族、核心能力、区域站点介绍 |
| [01 5分钟快速开始](01-getting-started.md) | 环境准备、依赖安装、第一个API调用（Python + curl） |
| [02 API认证与安全](02-api-authentication.md) | Bearer Token认证机制、API密钥管理最佳实践、安全红线 |

## 核心API篇

| 文档 | 简介 |
|------|------|
| [03 对话补全 API](03-chat-completions.md) | /v1/chat/completions接口完整说明：消息格式、流式输出、工具调用、图像理解 |
| [04 图像生成 API](04-image-generation.md) | /v1/images/generations接口：文生图、图生图、尺寸参数、输出格式 |
| [05 视频生成 API](05-video-generation.md) | /v1/videos异步接口：任务提交、轮询机制、文生视频、图生视频 |

## 生产环境篇

| 文档 | 简介 |
|------|------|
| [06 速率限制与配额](06-rate-limits.md) | RPM速率限制、订阅计划配额、429错误处理、指数退避重试、令牌桶实现 |
| [07 错误处理与调试](07-error-handling.md) | HTTP状态码详解、4xx/5xx错误排查、重试装饰器、调试技巧 |

## 学习路径建议

```
入门篇（00-02）→ 核心API篇（03-05）→ 生产环境篇（06-07）
     ↓                    ↓                     ↓
  了解平台           掌握API调用           上线生产环境
```
