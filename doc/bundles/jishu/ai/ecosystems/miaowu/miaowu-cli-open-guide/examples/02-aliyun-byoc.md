---
type: Example
title: 命令流二：部署到自有阿里云账号（BYOC）
description: 安装最新 CLI 与 aliyun CLI、aliyun configure 配置 RAM 专用凭证、环境检查、先询价后部署、update/status/delete/rollback 运维与 DELETE 确认的完整命令流（文档级复现）
tags: [meoo, miaowu, cli, aliyun, byoc, example]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
status: stable
stale_after: "2027-01-18"
sources:
  - id: cli-aliyun
    resource: https://docs.meoo.com/features/cli-aliyun
    title: MEOO CLI 进阶：部署到你自己的阿里云账号
---

# 命令流二：部署到自有阿里云账号（BYOC）

> **复现性质声明**：**文档级复现，未做运行验证（2026-10-18）**。命令与话术逐字摘自 [MEOO CLI 进阶页](https://docs.meoo.com/features/cli-aliyun)；本示例不产生任何真实云资源。原理与权限解释见 [05 自有阿里云 BYOC 部署](../concepts/05-aliyun-byoc-deploy.md)。

## 阶段 1：装齐两套 CLI

对本地 Agent 发送（F-062）：

```text
读取 meoo.com/skill-setup.md，并按照说明安装秒悟技能和最新版 meoo cli
```

安装 aliyun CLI：对 Agent 说「帮我安装 aliyun CLI」，或按官方文档手动安装 `https://help.aliyun.com/zh/cli/install-cli`（F-063）。

## 阶段 2：准备 RAM 专用 AccessKey

- 查看 AccessKey：`https://ram.console.aliyun.com/profile/access-keys`
- 创建文档：`https://help.aliyun.com/zh/ram/user-guide/create-an-accesskey-pair`

源页建议：在 RAM 中创建专用 AccessKey，不长期使用主账号 AccessKey（F-065）。权限基线（F-066）：

- 必需：ECS、ROS、OSS、STS；
- 可选：RDS（需要 MySQL 时）、SLB（高可用拓扑时）。

## 阶段 3：配置凭证

终端执行（F-064）：

```bash
aliyun configure
```

依次填写：AccessKey ID → AccessKey Secret → Region（如 `cn-hangzhou`）→ Output format（默认即可）。

## 阶段 4：环境检查（必做）

对 Agent 发送（F-067）：

```text
帮我检查一下阿里云部署环境
```

检查 aliyun CLI、账号身份、Region、OSS/ROS/ECS 能力是否可用。

## 阶段 5：先询价，不创建资源

对 Agent 发送（F-068）：

```text
先帮我估一下部署到我自己的阿里云账号大概要花多少钱，别真创建资源
```

此步只临时用 OSS 上传模板询价，不创建正式 ECS/RDS/SLB；输出含地域、拓扑、ECS 规格、小时单价、月度预估。

## 阶段 6：显式声明归属后部署

对 Agent 发送（F-069）：

```text
帮我把这个项目部署到我自己的阿里云账号上，费用我自己出
```

底层动作是 `meoo aliyun deploy`：CLI 生成并提交 ROS 资源栈，在你的账号下创建 ECS、EIP、可选 RDS/SLB（F-059、F-060）。成功后输出阿里云账号下的访问链接。

## 阶段 7：上线后运维

| 目的 | 对 Agent 说 | 实际命令（F-070） |
|---|---|---|
| 更新版本 | `帮我更新一下阿里云上那个部署` | `meoo aliyun update`（单机替换/高可用滚动） |
| 查看状态 | `看看我阿里云上部署的状态` | `meoo aliyun status --refresh` |
| 清理资源 | `把阿里云上这个部署清理掉` | `meoo aliyun delete`，**手动输入 `DELETE` 确认** |
| 健康检查失败 | `健康检查失败了，帮我看看状态` | 先等几分钟或 `meoo aliyun status --refresh`，不立刻删 |
| 回滚上一版 | `帮我回滚阿里云上的上一个版本` | `meoo aliyun rollback`（未 update 过可能无版本可滚） |

清理后无论 CLI 输出什么，再去阿里云控制台亲自核对 ECS、EIP、SLB、RDS、OSS 是否有残留计费资源（F-070）。

## 安全注意

- 数据库密码**不要**走命令行参数（会进 shell 历史/进程列表）；用交互式输入、环境变量或自动生成强密码存入权限收紧的本地文件（F-072）。
- 自动开通目前只支持 RDS MySQL；PostgreSQL/Redis/MongoDB 需自行配置后接入连接信息（F-073 ⚠️ dated）。
- 健康检查失败不等于部署失败：首次启动装环境依赖较慢，便宜机型更慢（F-074）。

## 与默认部署的切换

回到 Meoo 托管部署（`meoo login` + Meoo 计费 + CDN/函数计算）见 [命令流一](01-static-and-fullstack-deploy.md)；两者资源位置、计费方、登录要求对照见 F-071。
