# 00 Tushare 平台与 MCP

> Tushare 是什么、数据能力、认证方式、MCP/Skill 现状。

## Tushare 概述

**Tushare** 是一个免费开源的 Python 财经数据接口包，返回 Pandas DataFrame 格式数据（F-002）。

### 数据覆盖

- 股票（日线/分钟线/实时行情）
- 基金（净值/持仓）
- 期货（行情/仓单）
- 债券（国债/企业债）
- 外汇
- 宏观经济数据
- 龙虎榜、两融、涨停板等特色数据

### 认证机制

Tushare Pro 采用 **token 认证**：
1. 注册 Tushare 账号（tushare.pro）
2. 在"个人中心"获取 Token
3. 通过 `ts.set_token('your_token')` 配置
4. 调用数据接口

注册送 100 积分，完善信息送 20 积分，部分高频/高级接口需更高积分（如资金流接口需 2000 积分）（F-010）。

## Tushare MCP 现状

### MCP 配置方式

截至 2026-08-28 核验时，Tushare MCP **仍需手动配置**（F-028）：

1. 登录 Tushare 个人中心
2. 拷贝 MCP key
3. 手动添加到各 AI 工具的 MCP 配置中（如编辑 `~/.openclaw/openclaw.json`）

这属于"自定义连接器"范畴，并非开箱即用的预置连接器。

### 官方支持平台列表

Tushare 官方 MCP 文档（doc_id=463）列出的支持平台（F-027）：

| 类别 | 平台 |
|------|------|
| OpenClaw 龙虾系 | OpenClaw、WorkBuddy、KimiClaw、MaxClaw、CoPaw、悟空 |
| Vibe Coding 工具 | CodeBuddy、ClaudeCode、Cursor、**Trae**、Cline、Lingma |

> ⚠️ 注意：列表中是 **"Trae"**（编程 IDE），而非博文声称的 **"TraeWork"**（办公工作台）；列表中**没有千问办公/QwenWork**。

### Tushare 官方 Skill

Tushare 同时提供官方 Skill `tushare-data`（F-032）：
- GitHub: https://github.com/waditu-tushare/skills
- 安装：`clawhub install tushare-data` 或 `npx skills add`
- 最后更新：2026-07-09
- 仍需手动安装和配置 Token

### 三层 AI 适配架构

Tushare 官方文档（doc_id=473）描述了三层 AI 能力适配：
1. **SDK 层**：Python SDK 直接调用
2. **Skills 层**：Agent Skill 包
3. **MCP 层**：MCP Server 协议

## 博文声称 vs 实际状态

| 博文声称 | 核验实际 |
|----------|----------|
| "从野生插件走向官方预置连接器" | 仍为手动配置的 MCP/Skill，非官方预置 |
| "无需用户通过自定义连接器手动添加" | 官方文档仍指导用户手动拷贝 key 配置 |
| WorkBuddy 官方预置 | 有社区 Skill `tushare-finance`（作者 stanleychanh，非官方） |
| 千问办公官方预置 | 官方连接器列表无 Tushare |
| TraeWork 官方预置 | 官方文档列出"Trae"非"TraeWork" |

## 关键事实索引

- F-002：Tushare 平台描述
- F-007：从野生插件到官方预置（⚠️）
- F-010：Token 获取方式
- F-027：官方支持平台列表
- F-028：MCP 仍需手动配置
- F-032：官方 Skill tushare-data
