---
type: Example
title: 发起讨论示例
description: 在 TRAE GitHub Discussions 发起不同类型讨论的完整示例，包含 Q&A 提问和 Knowledge Sharing 分享两种场景
tags: [example, discussions, community, how-to-post, trae-discussions, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/discussions-source.md
    title: "Trae Discussions 源码信源"
---

# 发起讨论示例

本示例演示如何在 TRAE 社区 GitHub Discussions 上发起不同类型的讨论。

## 访问 Discussions

1. 打开 https://github.com/orgs/trae-community/discussions
2. 点击 "Discussions" 标签
3. 点击右侧绿色 "New Discussion" 按钮
4. 选择合适的分类（General / Ideas / Q&A / Knowledge Sharing / Collaboration）
5. 填写标题和内容，点击 "Start discussion"

## 示例一：Q&A 提问

### 场景

你在配置 TRAE 自定义 Agent 时遇到了问题——设置的 MCP 工具无法被 Agent 调用。

### 分类选择

❓ Q&A

### 标题

```
Agent 配置的 MCP 工具无法被调用，显示"工具不可用"
```

### 内容

```
## 环境信息

- TRAE 版本：v1.0.5
- 操作系统：Windows 11
- Agent 类型：自定义 Code Review Agent

## 问题描述

我按照文档创建了一个自定义 Agent，在工具配置中勾选了一个 MCP 服务器（filesystem MCP），但在对话中让 Agent 读取文件时，它回复"我没有文件系统访问工具"。

MCP 服务器在 IDE 设置中已正确配置，测试连接显示成功。其他内置工具（如终端命令）可以正常使用。

## 复现步骤

1. 创建自定义 Agent
2. 在工具配置中勾选 filesystem MCP
3. 保存 Agent 并开始新对话
4. 输入"请读取当前目录的 README.md 文件"
5. Agent 回复没有文件访问工具

## 已尝试的解决方案

- 重新创建 Agent → 问题依旧
- 重启 TRAE → 问题依旧
- 检查 MCP 配置 → 连接测试成功
- 搜索了 Issues 和 Discussions，未找到类似问题

## 截图

（附上 MCP 配置界面截图和 Agent 回复截图）

有人遇到过类似问题吗？是我漏了什么配置步骤吗？
```

### 这个提问为什么好

- ✅ 标题清晰描述问题
- ✅ 提供了完整环境信息
- ✅ 描述了期望和实际结果
- ✅ 给出了复现步骤
- ✅ 说明了已尝试的方案
- ✅ 附上截图辅助理解

## 示例二：Knowledge Sharing 分享

### 场景

你总结了一套使用 TRAE 进行测试驱动开发（TDD）的有效工作流，想分享给社区。

### 分类选择

📖 Knowledge Sharing

### 标题

```
分享：用 TRAE 实践 TDD（测试驱动开发）的 3 步工作流
```

### 内容

```
# 用 TRAE 实践 TDD 的 3 步工作流

最近一个月我在用 TRAE 做一个 Python 项目，尝试了 TDD 工作流，发现 TRAE + TDD 的组合效率很高。分享一下我的工作流：

## 工作流步骤

### 第 1 步：让 TRAE 先写测试

当我要开发一个新功能时，我先告诉 TRAE：

> "我要实现一个用户注册功能，包含邮箱验证和密码强度检查。请先帮我写测试用例，覆盖：正常注册、邮箱格式错误、密码太短、邮箱已存在这几个场景。"

TRAE 生成 pytest 测试用例，我审查后保存为 `test_auth.py`。

### 第 2 步：让 TRAE 实现代码让测试通过

然后告诉 TRAE：

> "现在请实现代码让这些测试通过。先运行测试看哪些失败，然后逐个修复。"

TRAE 会：
1. 运行测试看到失败
2. 编写实现代码
3. 再次运行测试验证
4. 迭代直到全绿

### 第 3 步：重构

测试通过后，让 TRAE 审查代码质量：

> "测试已通过。请审查这段代码，有没有可以重构的地方？注意保持测试通过。"

## 效果

- 代码质量明显提升（有测试覆盖）
- 我更专注于设计决策而非样板代码
- 重构时很安心（测试保护）

## 适用场景

- 后端 API 开发
- 工具类库开发
- 算法实现

不太适合前端 UI 开发（测试 UI 比较麻烦）。

欢迎大家补充你们的 TDD 经验！
```

### 这个分享为什么好

- ✅ 标题说明了主题和核心价值
- ✅ 有具体步骤和可复制的提示词
- ✅ 说明了适用场景和不适用场景
- ✅ 保持开放，邀请讨论

## 示例三：Ideas & Suggestions 建议

### 分类选择

💡 Ideas & Suggestions

### 标题

```
建议：Agent 配置支持导入/导出 JSON 功能
```

### 内容框架

1. **当前痛点**：换电脑或想分享 Agent 配置时，只能手动复制粘贴提示词
2. **建议方案**：增加"导出配置"按钮，生成 JSON 文件；"导入配置"按钮解析 JSON 自动填充
3. **使用场景**：备份配置、团队分享 Agent、社区共享配置
4. **类似参考**：VS Code 的 Profile 导入导出功能

## 示例四：Collaboration 协作招募

### 分类选择

🤝 Collaboration

### 标题

```
[招募] 寻找合作者一起做 TRAE 插件开发教程网站
```

### 内容框架

1. **项目是什么**：一个专门收集 TRAE 插件/Agent/MCP 开发教程的网站
2. **当前进度**：已做了原型，有 3 篇教程草稿
3. **需要什么角色**：前端（React）、内容作者、设计
4. **时间投入**：业余项目，每周 3-5 小时
5. **联系方式**：Discord 私信或回复本帖

## 发帖后注意事项

1. **及时回复**：有人回答或评论时及时回应
2. **标记答案**：Q&A 帖中，如果某个回答解决了问题，标记为答案
3. **更新信息**：如果问题自行解决了，回来更新帖子说明解决方案
4. **感谢帮助**：对帮助你的人表示感谢

## 相关链接

- [GitHub Discussions 作为社区论坛](../concepts/00-introduction.md)
- [讨论分类与使用指南](../concepts/01-discussion-categories.md)
- [社区礼仪与有效提问](../concepts/02-community-etiquette.md)
- [社区讨论仓库资源索引](../references/discussions-source.md)
