---
type: concept
title: Meoo 开放平台总览：能力域、三种身份与三条接入流程
description: 从「以谁的身份调用」出发理解 Meoo Open API——项目创建/AI 生成/云能力/发布四大能力域，团队系统集成、用户 API Key、OAuth 三种身份模式与全链路/仅部署/仅生成三条功能流程，以及 2026-10 时点的集成权益红线
tags: [meoo, miaowu, open-api, authentication, bearer-token]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
sources:
  - id: open
    resource: https://docs.meoo.com/open
    title: Meoo 开放平台
  - id: cli-open-guide
    resource: https://docs.meoo.com/open/guides/cli
    title: CLI 开放集成接入
---

# Meoo 开放平台总览：能力域、三种身份与三条接入流程

> 本篇是束 B 的导航起点。先建立开放平台的心智模型，再进入个人 CLI（[01](01-cli-positioning.md)）与团队集成（[06](06-team-skill-cli-integration.md)）两条具体故事线。

## 1. 它是什么：开放平台的能力边界

Meoo Open API 把秒悟平台的四类能力对外暴露（F-030）：

| 能力域 | 含义 | 典型去向 |
|---|---|---|
| 项目创建 | 以 API 方式建立项目实体 | 全链路接入 |
| AI 应用生成 | 让 Meoo 生成应用，产出过程、会话记录与预览 | 全链路 / 仅生成 |
| 云能力 | 数据库、文件、认证等云服务的开通与使用 | 全链路、Skill+CLI |
| 发布能力 | 托管发布构建产物，产出正式网站链接 | 全链路 / 仅部署 |

技术基线只有两个固定值（F-031）：生产环境地址 `https://meoo.com`，当前 API 版本 `v1`。

官方给的接入方法论是一句话（F-030）：**先确定「以谁的身份调用」，再选择需要的功能流程；只有需要核对字段时才进入 API 目录。** 身份选错，后面的凭证与隔离模型全部错位。

## 2. 第一步决策：以谁的身份调用

三种身份模式的区别，本质是「平台是否识别最终用户、凭证代表谁」（F-032）：

| 模式 | 适合谁 | 平台识别最终用户？ | 官方推荐度 |
|---|---|---|---|
| 团队系统集成 | 企业系统集成、单大账号或多租户 SaaS | 可选：Owner 模式不隔离；虚拟账号模式按 `member_id` 隔离 | **系统集成唯一推荐方式：团队版** |
| 用户 API Key | 个人测试、临时调试、个人 CLI | 否；始终代表 API Key 创建者 | 仅推荐个人和非生产场景 |
| OAuth 授权 | 第三方产品代 Meoo 用户操作 | 是；由用户登录并授权 | 由实际授权用户的账号版本决定 |

三条共同规则必须先记住（F-033）：

1. 三种模式**最终都使用 Bearer Token** 调用业务 API；
2. **团队 AK/SK 不是业务调用凭证**——它只用于成员管理和为团队 Owner 或虚拟成员签发短期 Token，不能直接调用项目、Agent 或 Release；
3. 系统集成场景**不再推荐直接使用用户 API Key**。

> 洞察（架构型）：秒悟把「凭证签发权」与「业务操作权」强制拆成两层——长期 AK/SK 锁在服务端，短期 token 流到任务环境。这使泄露面随 token 过期自动收敛，也让多租户 SaaS 能用 `member_id` 做租户隔离而不必为每个用户建账号。

## 3. 第二步决策：走哪条功能流程

身份确定后，按「你想让 Meoo 干多少活」选流程（F-034）：

| 目标 | 接入流程 | 最终结果 |
|---|---|---|
| 让 Meoo 生成应用**并**发布上线 | 全链路接入（`/open/guides/full-integration`，未转写） | 生成结果、预览地址和正式网站链接 |
| 已自行构建，只使用 Meoo 托管发布 | 仅部署接入（`/open/guides/deploy-only`，未转写） | 静态 zip 发布后的网站链接 |
| 只使用 AI 生成，不发布上线 | 仅生成接入（`/open/guides/generate-only`，未转写） | 生成过程、会话记录和临时预览地址 |

CLI 故事线是这张表之外的第四条实操路径：不用直接拼 HTTP，而是让本地或团队的 Agent 通过 Skill + CLI 承接同一批能力（见 [06](06-team-skill-cli-integration.md)，F-042）。

## 4. API 参考的四个入口

需要字段级细节时再查四类文档（F-035，均在本束抓取范围之外，仅登记）：

- **API 目录**（`/open/api`）：按资源查看接口、Scope 和字段说明；
- **源码导出 API**（`/open/reference/source-export`）：导出项目当前源码为 ZIP 并获取短期下载链接；
- **通用协议**（`/open/protocol`）：错误、分页、幂等、请求追踪和 SSE；
- **稳定性与安全**（`/open/security`）：凭证保管、重试、限流和上线检查。

## 5. 接入前必读：2026-10 时点的五条红线

以下为源页「接入前须知」原文口径，**全部带时效或条件限定**（F-036–F-041，核验状态见 [verification.md](../references/verification.md) 核验项八）：

1. **集成权益尚未正式开放**：当前限制较小，仅建议开发和预发联调；正式生产需等「集成版」权益套餐上线后按届时额度开通 ⚠️ dated；
2. **团队 AK/SK 不能自助创建**：暂未开放用户侧入口，现阶段联调联系秒悟团队人工创建并提供团队账号；Secret 仅创建时交付一次 ⚠️ dated；
3. **长期凭证四不入**：只能保存在接入方可信服务端，不能写入浏览器、移动端、代码仓库或构建产物（F-038）；
4. **OAuth 应用不能自行注册**：联系 Meoo 配置回调地址、允许账号版本和 Scope，获取 `client_id` 与 Client Secret ⚠️ dated；
5. **环境隔离**：测试和生产环境的账号、凭证、项目不能混用（F-041）。

补充一条易混淆点：用户 API Key 用户可在前端自行创建，但**不作系统集成凭证**；团队 AK/SK 由秒悟管理员内部后台创建，无公开创建接口（F-039）。

## 6. 坑点与边界

- **不要用 AK/SK 直调业务 API**：源页明确其不能调用项目、Agent、Release（F-033），正确姿势是先换成员短期 token（接口见 [06](06-team-skill-cli-integration.md)）。
- **Owner 模式不隔离**：多租户场景若用团队 Owner 身份跑所有任务，所有最终用户共享同一资源视野；需要按人隔离时用虚拟成员 `member_id`（F-032、F-044）。
- **联调环境凭证不能用于生产**：联调使用对应环境地址及该环境签发的凭证（F-047），地址与凭证必须成对。
- **本页不含字段细节**：HMAC 签名串接方式、完整错误码、三流程分步均在未抓取页面，见 [source-ledger.md](../references/source-ledger.md)「放弃核验清单」，勿据本页推断。

## 7. 延伸阅读

- 个人用户视角的 CLI 使用：[01 CLI 定位与适用场景](01-cli-positioning.md)
- 团队接入的完整六步（签 token → 装 Skill → 注入 → CI 发布）：[06 团队 Skill+CLI 集成](06-team-skill-cli-integration.md)
- 同组产品功能全景（AI 服务、云服务等平台能力的功能侧说明）：[miaowu-product-guide](../../miaowu-product-guide/index.md)
