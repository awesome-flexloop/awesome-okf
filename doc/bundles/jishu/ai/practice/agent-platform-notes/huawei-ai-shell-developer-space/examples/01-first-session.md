---
type: Example
title: "首次会话：进入、探查与保存"
description: "用最小风险流程体验 AI Shell，先确认环境，再执行低风险任务并保存产物。"
tags: [example, ai-shell, onboarding, linux]
sources:
  - id: blog
    resource: "/references/article-source.md"
  - id: official
    resource: "https://developer.huaweicloud.com/aishell.html"
generated: { by: process:seven-concepts-e, at: "2026-09-20T00:00:00Z" }
verified: [{ by: process:seven-concepts-v, at: "2026-09-20T00:00:00Z" }]
status: stable
stale_after: "2026-12-31"
---

# 首次会话：进入、探查与保存

> 这是基于文章入口和官方产品页整理的非官方上手流程。控制台名称、体验时长和模型列表可能变化。

## 1. 进入环境

1. 打开 [AI Shell 产品页](https://developer.huaweicloud.com/aishell.html)。
2. 登录华为云并进入开发者空间。
3. 从侧边栏拉起 AI Shell；官方 FAQ 也确认该入口路径。
4. 阅读服务协议、隐私声明和凭据同步提示，再决定是否授权。

## 2. 先做只读探查

在对话框中发送：

```text
请先不要修改任何资源，告诉我当前环境的系统、架构、CPU、内存、磁盘、地域和可用目录，并列出将要执行的只读命令。
```

若 Agent 给出命令，可要求它逐条解释，然后在终端中执行或复制结果。也可以手动运行：

```bash
uname -m
cat /etc/os-release
df -h
free -h
pwd
```

把结果记录到项目的环境说明中，尤其标记 `aarch64`/`arm64`。

## 3. 执行低风险任务

例如：

```text
请在 /root/ai-shell-demo 创建一个最小 Python 项目，只生成 README.md、pyproject.toml 和一个 hello.py。
先输出计划，不要安装系统包，不要访问公网，不要删除文件；创建后运行 hello.py 并报告结果。
```

验收文件、运行结果和命令输出后，再决定是否继续安装依赖。

## 4. 保存与退出

- 将代码推送到版本库或复制到受控存储。
- 删除不必要的密钥、临时日志和缓存。
- 根据控制台提示确认是否需要关机或释放环境。
- 不要把“浏览器标签页关闭”当作“环境已停止”。
