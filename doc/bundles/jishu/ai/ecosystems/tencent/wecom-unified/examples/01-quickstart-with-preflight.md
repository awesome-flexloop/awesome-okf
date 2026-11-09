---
type: example
title: 带前置检查的首次接入
description: 从安装 Skill 到完成身份确认并成功检索一位同事的完整起步流程演示。
tags: [wecom, wecom-unified, example, quickstart]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# 带前置检查的首次接入

> **声明**：本示例为基于源码阅读整理的用法演示，**未在本机实跑**。下文所有命令输出、版本号与返回内容均为格式「示意」，不代表真实运行结果；实际输出以本机 `wecom-cli` 为准。

## 适用场景

第一次在开发机上使用 `wecom-unified`：需要安装 Skill、确认 `wecom-cli` 版本达标、完成扫码授权，并用一条只读查询验证「身份正确、链路通畅」。这条流程也是排查「Skill 装了但用不了」的标准起手式。

## 前置条件

| 条件 | 要求 | 证据 |
|---|---|---|
| 运行时 | Node.js >= 18 | F-103 |
| 操作系统 | macOS（x64/arm64）、Linux（x64/arm64）或 Windows（x64） | F-103 |
| 企业微信账号 | 可完成扫码授权 | F-031 |
| 网络 | 能访问 npm registry 与企业微信接口 | F-027 |

## 分步命令

**Step 1：安装 Skill**

```bash
npx skills add WecomTeam/wecom-unified -y -g
```

`-g` 表示全局安装；命令会自动检测已安装的宿主平台（F-102、F-104）。

**Step 2：检查 CLI 版本**

```bash
wecom-cli --version
```

期望输出版本号不低于 `1.2.1`（F-026、F-106）。

**Step 3：按需安装或升级 CLI**

```bash
npm install -g @wecom/cli
wecom-cli --version
```

安装后必须复验；若仍低于 `1.2.1`，停止后续操作并先修复环境（F-027、F-028）。

**Step 4：检查授权状态**

```bash
wecom-cli auth show --status
```

只有返回 `authorized` 才继续；`unauthorized` 进入 Step 5；报错或其它值应先排查环境（F-029、F-030）。

**Step 5：扫码授权（仅未授权时执行）**

```bash
wecom-cli auth init --noninteractive
wecom-cli auth show --status
```

命令会输出授权链接与二维码并阻塞等待扫码，成功后自动退出；只需执行一次，之后必须复验状态（F-031、F-032）。

**Step 6：确认当前身份**

```bash
wecom-cli identity whoami
```

**Step 7：执行一条只读查询**

```bash
wecom-cli contact users search --json '{"keywords": ["张三"]}'
```

`keywords` 为字符串数组，支持姓名、拼音、英文名、别名匹配，最多 10 个，多个关键词之间为 OR 关系（`wecomcli-contact.md:19`）。

## 预期结果（示意）

```text
$ wecom-cli --version
wecom-cli/1.2.1 ...            # 示意

$ wecom-cli auth show --status
authorized                     # 示意

$ wecom-cli identity whoami
姓名：张三
部门：示例事业部             # 示意，实际字段以命令输出为准

$ wecom-cli contact users search --json '{"keywords": ["张三"]}'
{
  "users": [
    {"name": "张三", "username": "zhangsan", "department": "示例事业部"}
  ]
}
```

交付给用户时应只呈现 `name`、`username`、部门名等可读字段，不输出 `userid`、`open_vid`、`department_id`、`chat_id` 等内部标识（F-035、F-036）。

## 失败排查

| 现象 | 可能原因 | 处置 | 证据 |
|---|---|---|---|
| `wecom-cli: command not found` | CLI 未安装或不在 `PATH` | 执行 `npm install -g @wecom/cli` 后复验 | F-027 |
| 版本低于 `1.2.1` | 安装了旧版本 | 升级后重跑 `--version`；仍不达标则停止 | F-028、F-106 |
| `auth show --status` 报错 | 配置损坏、网络异常或凭证文件不可读 | 不要立即初始化，先排查环境并原样上报 | F-030 |
| 二维码长时间无响应 | `--noninteractive` 仍在阻塞等待扫码 | 确认有人完成扫码；该命令不适合无人值守运行 | F-031、F-032 |
| 初始化成功但业务命令仍失败 | 未复验授权态，或版本已过期 | 重跑 `auth show --status`，再查版本 | F-032 |
| 查询结果只给 ID | 未按域文档换取可读名称 | 阅读 `wecomcli-contact.md` 的字段说明，换不到则用自然语言描述 | F-037 |

## 延伸阅读

- [前置检查与身份](../concepts/01-preflight-and-identity.md)：三步门禁的设计动机与分支语义。
- [套件定位与依赖](../concepts/00-overview.md)：为什么安装 Skill 不等于安装 CLI。
- [意图路由](../concepts/02-intent-routing.md)：验证通过后如何选择业务域。