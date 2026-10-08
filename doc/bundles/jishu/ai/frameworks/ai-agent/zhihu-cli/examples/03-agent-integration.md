---
okf_version: "0.2"
type: Example
title: "Agent 接入配置"
description: "以 Claude Code 为例，详细说明如何在主流 AI Agent 中配置 Zhihu CLI 的 Skill 和 MCP 两种接入方式。"
tags: ["Agent接入", "Claude Code", "Skill配置", "MCP配置", "集成"]
generated: 2026-09-04
verified: 2026-09-04
status: verified
stale_after: "2026-12-31"
sources:
  - "F-031、F-037、F-041、F-042"
  - "F-096~F-102"
---

# 03 Agent 接入配置

> 对应事实：F-031、F-037、F-041、F-042、F-096~F-102
> 知识层级：操作层

Zhihu CLI 支持多种主流 AI Agent 集成 [F-041]，每种 Agent 均支持 Skill 和 MCP 两种接入方式 [F-042]。本文以 Claude Code 为例，演示两种接入方式的配置流程。

> **勘误说明**：除了 Skill 和 MCP 两种 Agent 接入方式外，底层还有 API 直接调用方式，共计三种接入方式 [E-001]。

## 一、接入方式选择

在开始配置之前，先了解两种 Agent 接入方式的区别：

| 维度 | Skill + CLI 方式 | 托管式 MCP 方式 |
|------|-----------------|-----------------|
| 本地安装 | 需要安装 CLI 二进制 | 不需要 |
| 工作原理 | Agent 读取 Skill → 调用本地 CLI → 调 API | Agent 通过 MCP 协议 → 托管服务 → 后端 API |
| 数据能力 | 完全一致 | 完全一致（共用后端）[F-102] |
| Access Secret | 需要 [F-047] | 需要 [F-047] |
| 调试便利 | stderr 直接可见 | 依赖 MCP 宿主日志 |
| 推荐场景 | 喜欢本地可控、需要调试 | 追求便捷、不想管理本地依赖 |

> 两种方式共用同一套 Access Secret [F-047] 和同一套后端接口 [F-055]。

---

## 二、方式一：Skill + CLI 接入

### 适用 Agent

Claude Code [F-097]、Cursor [F-098]、Codex [F-096] 等支持 Skill 机制的 Agent。

### 配置步骤（以 Claude Code 为例）

#### 步骤 1：获取 Skill 文件

从官方渠道获取 Zhihu CLI 的 Skill 文件 [F-061]：
- 确保从官方域名下载，保证供应链安全 [F-067]
- Skill 是约 42KB 的纯文本压缩包 [F-038]

#### 步骤 2：安装 Skill

将 Skill 文件安装到 Claude Code 的 Skills 目录中。

Skill 文件包含完整的调用指令规范 [F-053]，Agent 读取后就知道如何调用 Zhihu CLI。

#### 步骤 3：自动安装 CLI

将 Skill 发给 Agent 后，Agent 会自动下载安装 CLI 二进制 [F-031] [F-050]。

安装过程中，CLI 会进行供应链安全校验 [F-062]：
- 官方域名校验
- 文件大小校验
- SHA-256 哈希校验
- 二进制自报版本校验

> 这四道校验确保下载的 CLI 二进制是官方正版，未被篡改。

#### 步骤 4：配置 Access Secret

按照 Agent 的提示输入你的 Access Secret [F-031]。

Access Secret 会被安全地存储在系统凭证管理中 [F-064]：
- macOS：Keychain [F-035]
- Windows：Credential Manager [F-036]
- 无明文存储 [F-036]

#### 步骤 5：验证接入

在 Claude Code 中尝试一个简单的请求，例如：

> "帮我搜索一下知乎上关于 AI Agent 的讨论"

如果 Agent 能成功调用 Zhihu CLI 并返回搜索结果，说明配置成功。

---

## 三、方式二：MCP 接入

### 适用 Agent

支持 MCP（Model Context Protocol）协议的 Agent。

### 配置步骤

#### 步骤 1：获取 MCP 接入信息

从知乎开放平台控制台获取托管式 MCP 服务的接入信息。

#### 步骤 2：配置 MCP Server

在 Agent 的 MCP 配置中添加知乎 MCP Server。

具体配置方式取决于你使用的 Agent，通常需要在配置文件中添加 MCP Server 条目。

#### 步骤 3：配置 Access Secret

在 MCP 配置中填入你的 Access Secret [F-047]。

#### 步骤 4：重启 Agent 并验证

重启 Agent 后，尝试调用知乎相关工具，验证 MCP 接入是否正常。

---

## 四、验证与调试

### 验证接入成功

无论用哪种方式，都可以用以下方法验证：

1. **搜索测试**：让 Agent 搜索一个知乎话题，看是否返回结果
2. **热榜测试**：让 Agent 查看知乎热榜
3. **额度查询**：让 Agent 查询当前额度 [F-019]

### 常见问题排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|----------|
| 命令执行失败 | Access Secret 错误或过期 | 检查 Secret 是否正确配置 |
| 找不到命令 | CLI 未正确安装 | 确认 CLI 二进制存在 |
| 权限不足 | 凭证存储权限问题 | 检查系统凭证库权限 |
| 返回错误码 | 业务逻辑错误 | 查看 stderr 诊断信息 [F-022] |

### 使用 stderr 诊断信息

Zhihu CLI 将诊断信息输出到 stderr [F-022]，调试时可以：

1. 查看 stderr 输出获取详细错误信息
2. 根据错误码定位问题类型
3. 结合官方文档排查具体原因

### 供应链安全校验失败

如果 CLI 安装时安全校验失败 [F-062]：

1. 检查网络是否正常，是否能访问官方域名
2. 尝试重新下载（可能是下载过程中文件损坏）
3. 确认下载来源是官方域名 [F-067]

---

## 五、其他 Agent 平台

除了 Claude Code，Zhihu CLI 还支持以下 Agent [F-041]：

| Agent 平台 | Skill 接入 | MCP 接入 | 事实编号 |
|-----------|-----------|----------|----------|
| Codex | ✅ | ✅ | [F-096] |
| Cursor | ✅ | ✅ | [F-098] |

配置思路类似，具体操作细节请参考各 Agent 的 Skill/MCP 配置文档。
