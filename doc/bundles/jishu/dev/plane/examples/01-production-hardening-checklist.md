---
okf_version: "0.2"
type: Example
title: "清单：生产环境加固"
description: "把体验级部署变成可上生产的清单——外置数据库与对象存储、端口收敛、密钥轮换、SMTP、God mode、备份与升级窗口"
sources:
  - id: official-docker
    resource: https://developers.plane.so/self-hosting/methods/docker-compose
  - id: official-selfhosting-101
    resource: https://developers.plane.so/self-hosting/self-hosting-101
---

# 01 · 清单：生产环境加固

> ⚠️ **来源性质**：官方要求项（标 ✅ 已核验）+ 博文经验项（标 🟡 仅博文单源，需自行验证）。**非实测清单**，用作上生产前的自查表。

## A. 数据层（官方 WARNING 级）

| # | 项 | 性质 | 说明 |
|---|----|------|------|
| A1 | 数据库外置 | ✅ 官方强烈建议 | 「strongly recommended to configure external database and storage」；容器里那套机器一崩数据跟着没（F-040 / V20） |
| A2 | 对象存储外置 | ✅ 官方强烈建议 | 同上；官方支持 RDS / Cloud SQL / S3 / GCS 等托管服务 |
| A3 | 对象存储只认 S3 兼容 | 🟡 博文 | 地址不能填本机；密码勿含特殊字符，否则预签名上传失败（F-043） |
| A4 | 数据服务端口不外露 | 🟡 博文语境 + 通用实践 | 5432 / 6379 / 5672 / 9000 只在 docker 网络内，不要 publish 到宿主 |

外部化配置示例（社区版 `plane.env`）：

```bash
USE_MINIO=0
DATABASE_URL="postgresql://plane:<强密码>@<db-host>:5432/plane"
REDIS_URL="redis://<redis-host>:6379/"
AWS_REGION="us-east-1"
AWS_S3_ENDPOINT_URL="https://<s3-endpoint>"
AWS_S3_BUCKET_NAME="plane-uploads"
AWS_ACCESS_KEY_ID="<key>"
AWS_SECRET_ACCESS_KEY="<secret>"
```

## B. 配置与密钥

| # | 项 | 性质 | 说明 |
|---|----|------|------|
| B1 | 轮换默认密钥 | ✅ 官方注释 | 官方示例 `.env` 明确标注「Change in production!」：`SECRET_KEY`、`POSTGRES_PASSWORD`、`RABBITMQ_PASSWORD`、MinIO root 凭据 |
| B2 | `WEB_URL` 与 `CORS_ALLOWED_ORIGINS` 逐字符一致 | ✅ 官方明示 | 不一致会导致认证与 API 调用失败 |
| B3 | 先停服务再改 `plane.env` | ✅ 官方建议 | 菜单选 3 停止 → 改 → 选 2 启动 |
| B4 | 上传上限按需调整 | ✅ 已核验 | `FILE_SIZE_LIMIT` 默认 `5242880`（5 MB，F-042 / V25） |
| B5 | `plane.env` 文件权限收紧 | 🟡 通用实践 | 该文件承载全部密钥 |

## C. 容量与拓扑

| # | 项 | 性质 | 说明 |
|---|----|------|------|
| C1 | 内存按生产口径 | ✅ 官方 | 最低 2 核 4G，**生产推荐 8 GB**（F-038 / V19） |
| C2 | 别用单容器版上生产 | ✅ 官方 | 单容器版只适合体验（F-039） |
| C3 | K8s 路径写具体版本号 | 🟡 仅博文 | Helm 用 `PLANE_VERSION` 指定，**不要写 `stable`**（F-045 / V27，未核到官方原文） |

## D. 实例管理与可运维性

| # | 项 | 性质 | 说明 |
|---|----|------|------|
| D1 | 早配 SMTP | ✅ 官方功能项 | 否则邀请邮件发不出去（F-049）；入口在 God mode |
| D2 | God mode 逐项过一遍 | ✅ 官方 | 实例名与 ID、匿名遥测、SMTP、SSO 与 OAuth、免邀请注册、普通用户能否建工作区（F-047 / F-048 / V22） |
| D3 | 备份纳入常规 | ✅ 官方能力 | 菜单 7「Backup Data」；灾备方案官方要求**自托管方自己设计与运维** |
| D4 | 升级窗口写进日历 | ✅ 官方 | 升级时机由你决定；官方会发布配套安全公告，需及时打补丁 |
| D5 | worker / beat 纳入监控 | 🟡 推导 | 官方提示：邮件、通知、导入、webhook 依赖后台 worker；它们挂掉时前端仍可访问，易漏判 |

## E. 合规与许可

| # | 项 | 性质 | 说明 |
|---|----|------|------|
| E1 | 核对 AGPL 边界 | ✅ 官方 | 内部自用无碍；对外提供服务须公开修改源码；嵌入商业产品须合规或购商业授权（F-051 / V21） |
| E2 | 付费能力确认当期条款 | ✅ 官方 | SSO 在 Pro 及以上；审计日志 / SCIM 在 Business Plus；Airgapped 对应 Enterprise Grid（新购门槛条款 2026-04 曾拟设后延期） |

## 上线前最小集合

若时间有限，至少完成：**A1 + A2 + B1 + B2 + C1 + D1 + D3**。这七项覆盖了「数据不丢、密钥不裸奔、能用、能邀请人、能恢复」。

返回 → [examples 索引](index.md)
