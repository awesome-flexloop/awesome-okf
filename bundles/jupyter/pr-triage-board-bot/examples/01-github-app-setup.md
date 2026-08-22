---
okf_version: "0.2"
type: "example"
title: "GitHub App创建与配置完整流程"
description: "从零开始创建GitHub App、配置权限、获取凭证、安装到组织的完整步骤，附截图说明"
tags: [github-app, setup, permissions, authentication, how-to]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: concepts-auth
    resource: /concepts/03-auth-and-octokit.md
    title: "GitHub App认证与Octokit配置"
  - id: concepts-getting-started
    resource: /concepts/01-getting-started.md
    title: "5分钟快速上手"
---

# GitHub App创建与配置完整流程

本示例指导你从零开始创建并配置一个GitHub App用于pr-triage-board-bot。

## 前置条件

- GitHub组织账户（个人仓库也可以，但项目板通常用于组织）
- 组织Owner权限或App创建权限
- Node.js >23.0.0（本地测试用）

## 步骤1：创建GitHub App

1. 打开 **Settings → Developer settings → GitHub Apps → New GitHub App**
2. 填写基本信息：
   - **GitHub App name**: `pr-triage-bot`（或你的自定义名称）
   - **Homepage URL**: 可以填任意URL（如仓库地址）
   - **Webhook**: 取消勾选 "Active"（本bot不需要接收Webhook事件）
3. 配置权限（见下一步）
4. 点击 "Create GitHub App"

## 步骤2：配置Repository权限

在App设置页面的 **Permissions & events → Repository permissions** 中设置：

| 权限项 | 访问级别 | 说明 |
|--------|---------|------|
| **Checks** | Read-only | 读取CI状态 |
| **Contents** | Read-only | 读取协作者列表 |
| **Metadata** | Read-only | 基本信息（默认已有） |
| **Pull requests** | Read-only | 读取PR详情（reviews/状态/合并状态/变更统计） |

> 💡 本App只需要**读权限**，因为它不修改PR本身，只操作Project V2看板。

## 步骤3：配置Organization权限

在 **Organization permissions** 中设置：

| 权限项 | 访问级别 | 说明 |
|--------|---------|------|
| **Projects** | Read and write | 读写Project V2看板（创建字段、添加条目、设置值） |

> ⚠️ Projects权限是组织级别的，因为Project V2看板属于组织而非单个仓库。

## 步骤4：获取凭证

App创建后，在设置页面记录以下信息：

### App ID
- 在App设置页面顶部的 **About** 部分
- 一个数字，如 `1793875`

### 生成私钥
1. 滚动到 **Private keys** 部分
2. 点击 **Generate a private key**
3. 浏览器自动下载 `.pem` 文件，如 `pr-triage-bot.2024-01-01.private-key.pem`
4. **安全保存此文件**，它只下载一次，无法重新下载（只能生成新密钥）

## 步骤5：安装App到组织

1. 在左侧菜单点击 **Install App**
2. 点击目标组织旁的 **Install**
3. 选择安装范围：
   - **All repositories**：监控组织所有仓库的PR（推荐）
   - **Only select repositories**：选择特定仓库
4. 点击 **Install**
5. 安装后，浏览器URL变为 `https://github.com/organizations/<org>/settings/installations/<INSTALLATION_ID>`
6. **记录URL中的Installation ID**（数字）

## 步骤6：验证凭证

本地验证凭证是否有效：

```bash
# 克隆仓库
git clone https://github.com/yuvipanda/pr-triage-board-bot.git
cd pr-triage-board-bot

# 安装依赖并构建
npm install
npm run build

# dry run测试（不会修改任何内容）
node dist/src/main.js \
  --gh-app-id <你的APP_ID> \
  --gh-app-installation-id <你的INSTALLATION_ID> \
  --gh-app-pem-file <你的PEM文件路径> \
  --dry-run \
  <你的组织名> <项目板编号>
```

如果输出显示"Fetching open PRs..."和"Syncing project fields..."而没有401/403错误，说明凭证配置正确。

## 步骤7：在GitHub Secrets中配置私钥

对于GitHub Action部署：

1. 打开你的workflow仓库 → **Settings → Secrets and variables → Actions**
2. 点击 **New repository secret**
   - Name: `GH_APP_PRIVATE_KEY`
   - Value: 将 `.pem` 文件的完整内容粘贴进去（包括 `-----BEGIN...` 和 `-----END...` 行）
3. 保存

> ⚠️ 私钥内容包含换行符，确保完整复制。可以使用 `cat your-key.pem` 查看内容后复制。

## 常见问题排查

### 401 Unauthorized
- App ID错误
- 私钥文件格式错误（确保包含完整的BEGIN/END行）

### 403 Forbidden / Resource not accessible
- 未正确安装App到目标组织
- Projects权限未设置为Read and write
- Pull requests权限未设置为Read-only

### 404 Not Found
- Installation ID错误
- Project编号不存在
- App未安装到正确的组织

### 字段创建失败
- Projects权限缺少write权限
- 项目板不存在或编号错误

## 相关示例

- [添加自定义字段扩展](02-adding-custom-field.md)：配置完App后，扩展字段功能的完整步骤
- [GitHub Action部署workflow配置](03-github-action-workflow.md)：将bot部署为定时GitHub Action

## 相关概念

- [GitHub App认证与Octokit配置](../concepts/03-auth-and-octokit.md)：认证机制原理与Octokit客户端配置详解
- [5分钟快速上手](../concepts/01-getting-started.md)：包含App创建的快速入门指南
- [CLI与GitHub Action集成](../concepts/08-cli-and-action.md)：私钥安全、composite action、部署模式对比
