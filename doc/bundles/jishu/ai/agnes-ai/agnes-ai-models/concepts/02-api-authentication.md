---
type: Concept
title: API认证与安全
description: AgnesAI API认证机制、API密钥管理最佳实践、安全规范与常见认证错误排查
tags: [认证, API密钥, 安全, Bearer Token, 最佳实践]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: model-catalog
    resource: /references/model-catalog.md
    title: Agnes AI 模型目录
---

# API认证与安全

AgnesAI API 使用标准的 Bearer Token 认证机制，所有API请求必须携带有效的API密钥。

## 认证机制

所有API请求必须在HTTP请求头中包含 `Authorization` 字段，格式为：

```http
Authorization: Bearer YOUR_API_KEY
```

- 请求头名称：`Authorization`（注意大小写）
- 认证方案：`Bearer`（后跟一个空格）
- 凭证：你的API密钥字符串

> 事实溯源：F-013、F-022~F-026

### Python SDK自动处理

使用OpenAI Python SDK时，只需在初始化客户端时传入 `api_key` 参数，SDK会自动为所有请求添加正确的Authorization头：

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",  # SDK自动处理Bearer头
    base_url="https://apihub.agnes-ai.com/v1",
)
```

### curl手动指定

使用curl时需要手动添加 `-H "Authorization: Bearer $AGNES_API_KEY"` 参数：

```bash
curl https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": "Hi"}]}'
```

> 事实溯源：F-013

## API密钥管理最佳实践

### 1. 使用环境变量（强烈推荐）

永远不要将API密钥硬编码在源代码中：

```python
# ✅ 正确：从环境变量读取
import os
client = OpenAI(api_key=os.getenv("AGNES_API_KEY"))

# ❌ 错误：硬编码密钥（泄露风险！）
client = OpenAI(api_key="sk-abc123def456...")
```

### 2. 服务端存储

API密钥必须仅保存在服务端环境中：
- ✅ 服务端环境变量、密钥管理服务（KMS）
- ❌ 禁止在前端JavaScript、移动端App、公开GitHub仓库中暴露密钥
- ❌ 禁止在客户端代码中拼接API请求

> 事实溯源：F-015

### 3. .gitignore保护

在项目根目录的 `.gitignore` 中添加：

```gitignore
.env
.env.local
.env.*.local
*secret*
*key*
*.pem
```

使用 `.env.example` 文件作为模板，只保留占位符，不包含真实密钥：

```env
# .env.example - 提交到版本库
AGNES_API_KEY=your_api_key_here
```

## 获取API密钥

1. 访问AgnesAI API平台：https://platform.agnes-ai.com/
2. 注册/登录账户
3. 在控制台中创建API密钥
4. 根据订阅计划选择合适的配额（Starter/Plus/Pro）

> 事实溯源：F-004、F-028~F-030

## 认证错误排查

### 401 Unauthorized

收到401状态码时，按以下顺序排查：

| 检查项 | 排查方法 | 常见问题 |
|--------|---------|---------|
| API密钥值 | 打印环境变量确认是否加载成功 | 拼写错误、多复制了空格、引号不匹配 |
| Bearer格式 | 检查请求头是否为 `Bearer <key>` 格式 | 漏掉"Bearer "前缀、Bearer拼写错误 |
| 环境变量加载 | 确认程序启动时环境变量已设置 | 使用dotenv但未调用load_dotenv()、不同终端环境不一致 |
| 账户状态 | 登录平台控制台检查 | 账户欠费、密钥被禁用、订阅过期 |

> 事实溯源：F-032

### 403 Forbidden

- 检查API密钥是否有对应模型的访问权限
- 确认账户订阅计划支持请求的模型
- 检查是否在被限制的地区访问

### 安全红线

1. **永远不要**把API密钥提交到公开代码仓库
2. **永远不要**在客户端代码（前端/APP）中使用API密钥
3. **永远不要**通过聊天、截图、邮件明文分享API密钥
4. 怀疑密钥泄露时，**立即**在控制台轮换密钥
5. 生产环境使用最小权限原则，为不同服务创建独立密钥

## 相关概念

- [5分钟快速开始](01-getting-started.md)
- [对话补全API](03-chat-completions.md)
- [速率限制与配额](06-rate-limits.md)
- [错误处理与重试](07-error-handling.md)
