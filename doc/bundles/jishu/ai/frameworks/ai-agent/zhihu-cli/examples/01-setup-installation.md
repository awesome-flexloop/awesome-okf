---
okf_version: "0.2"
type: Example
title: "注册与安装"
description: "从零开始完成知乎数据开放平台注册、CLI 安装、Access Secret 配置与验证的完整步骤。"
tags: ["注册", "安装", "配置", "Access Secret", "实名认证"]
generated: 2026-09-04
verified: 2026-09-04
status: verified
stale_after: "2026-12-31"
sources:
  - "F-031~F-050"
  - "F-044、F-048、F-049"
---

# 01 注册与安装

> 对应事实：F-031~F-040、F-044、F-048~F-050
> 知识层级：操作层

本文档从零开始，带你完成知乎数据开放平台的注册、CLI 安装、Access Secret 配置与验证。

## 一、前置准备

### 需要准备的材料

1. 一个知乎账号
2. 实名认证所需的身份信息
3. 一台可访问互联网的电脑（Windows / macOS / Linux 均可 [F-010]）

## 二、注册与获取 Access Secret

### 步骤 1：访问开放平台

打开知乎数据开放平台官网：**developer.zhihu.com** [F-048]

### 步骤 2：登录

使用知乎账号登录开放平台 [F-049]。

### 步骤 3：完成实名认证

获取 Access Secret 需要先完成实名认证 [F-044]。按照页面指引完成实名认证流程。

### 步骤 4：获取 Access Secret

实名认证通过后，在开放平台控制台获取你的 **Access Secret** [F-032]。

> ⚠️ **重要**：Access Secret 是调用开放平台接口的凭证 [F-045]，请妥善保管，不要泄露给他人。

## 三、CLI 安装

### 方式一：通过 Skill 自动安装（推荐 Agent 场景）

这是最常见的安装方式，由 Agent 自动完成下载和配置 [F-050]。

**安装流程** [F-031]：

1. 将 Zhihu CLI 的 Skill 文件发给你的 AI Agent
2. Agent 读取 Skill 指令后，自动下载安装 CLI 二进制
3. 按照 Agent 提示输入 Access Secret
4. Agent 自动完成验证，安装完成

### 方式二：手动安装（社区推荐方式）

⏰ 社区有文章推荐使用 `uv` 安装 CLI [F-033]。

> ⚠️ **核验说明**："官方推荐使用 uv 安装"的说法仅来自单一社区来源，未见官方文档明确推荐，标记为社区推荐方式 [P0-011]。

### 方式三：使用社区封装工具

社区有第三方封装的 zhihu-search 工具（作者 klarkxy）[F-034]，可供选择。

> 注意：第三方工具非官方出品，使用前请自行评估安全性。

## 四、配置 Access Secret

### 凭证存储方式

Access Secret 存储在系统原生凭证管理中，无明文落盘 [F-064]：

| 操作系统 | 凭证存储位置 |
|----------|-------------|
| macOS | Keychain（钥匙串）[F-035] |
| Windows | Credential Manager（凭证库）[F-036] |

配置过程中，Access Secret 会被安全地存入系统凭证管理，不会出现在配置文件或环境变量中。

## 五、验证安装

安装完成后，可以通过以下方式验证：

1. **额度查询**：执行 `quota` 命令，查看是否能正常返回额度信息 [F-019]
2. **简单搜索**：执行 `search zhihu` 命令搜索一个简单关键词，验证搜索功能正常 [F-015]
3. **热榜获取**：执行 `hot` 或 `trending` 命令，验证热榜数据获取正常 [F-016]

如果以上命令都能正常返回 JSON 格式的数据（stdout），说明安装和配置成功。

## 六、Windows 安装避坑

### PowerShell 5.1 UTF-8 BOM 问题

Windows 平台有一个已知的安装坑：**PowerShell 5.1 对 UTF-8 无 BOM 编码的 `.ps1` 文件会报解析错误** [F-040]。

**解决方案**：

1. **推荐方案**：升级到 PowerShell 7+
   - 下载地址：https://github.com/PowerShell/PowerShell
   - PowerShell 7 对 UTF-8 编码支持更好

2. **临时方案**：确保安装脚本使用 UTF-8 with BOM 编码
   - 用记事本打开脚本 → 另存为 → 编码选择"UTF-8 with BOM"

3. **替代方案**：直接下载 CLI 二进制文件，跳过脚本安装

## 七、安装流程总览

```
注册知乎账号 → 访问 developer.zhihu.com → 登录 → 实名认证 → 获取 Access Secret
    ↓
安装 CLI（自动/手动）→ 配置 Access Secret → 存入系统凭证库 → 验证功能
```

⏰ **时效性提示**：截至 2026 年 9 月，平台处于邀测阶段 [F-005]，免费额度为 5000 次/天 [F-006]（额度可能随时间调整 [E-002]）。
