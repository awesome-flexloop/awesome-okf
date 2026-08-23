---
type: bundle
okf_version: "0.2"
scope: terraform
name: terraform
version: "0.1.0"
source: https://github.com/langchain-ai/terraform
description: LangSmith 自托管部署的生产级 Terraform 模块——支持 AWS EKS/Azure AKS/GCP GKE/OpenShift 四大云平台，infra/ 两遍部署编排云基础（VPC/K8s/Postgres/Redis/对象存储/密钥/DNS），helm/ 部署 LangSmith chart；count 驱动条件编排 + plan 时 precondition 守卫覆盖 dev 到生产矩阵；当前 chart 线 0.16，全局标签 vMAJOR.MINOR.PATCH 版本策略
---

# terraform

**langchain-ai/terraform** 是 LangSmith 自托管部署的官方 Terraform 模块仓库，将云基础设施编排（网络、Kubernetes 集群、数据库、缓存、对象存储、密钥管理、DNS、WAF、堡垒机）与 LangSmith Helm chart 部署打包为可复用的生产级 IaC。它支持 AWS、Azure、GCP 三大云的 GA 部署和 OpenShift 的 Preview 部署，通过一套 root module + 变量矩阵覆盖从 dev/POC 到企业加固生产的全部场景。

- **源码**：<https://github.com/langchain-ai/terraform>
- **语言**：HCL（Terraform ≥ 1.11.0）+ Shell
- **许可证**：Apache 2.0
- **当前 chart 线**：0.16（`v0.16.*` 标签，`main` 分支）；0.15 维护线（`release/0.15` 分支）

## 四大云提供商

| 提供商 | 路径 | 集群 | 状态 | 子模块数 |
|---|---|---|---|---|
| AWS | [`modules/aws/`](references/module-structure#aws-子模块详情) | EKS | GA | 14 |
| Azure | [`modules/azure/`](references/module-structure#azure-子模块详情) | AKS | GA | 11 |
| GCP | [`modules/gcp/`](references/module-structure#gcp-子模块详情) | GKE | GA | 12 |
| OpenShift | `modules/ocp/` | OCP/ROSA | Preview | stub |

另有 BYOC（Bring Your Own Cloud）IAM 角色模块 `modules/byoc/aws/langsmith-byoc-role/`，为 LangChain 运维侧创建最小权限 IAM 角色和 break-glass 角色。

## 核心特性

- **两遍部署**：`infra/` 编排云基础（Terraform apply），`helm/scripts/` 安装 LangSmith chart（Helm deploy）。典型首次部署 20-30 分钟。
- **云原生密钥管理**：AWS SSM Parameter Store、Azure Key Vault、GCP Secret Manager，由 External Secrets Operator 同步到 K8s，git/tfvars 不含密钥。
- **count 驱动条件编排**：子模块通过 `count` 元参数条件创建，一套 root module 覆盖 in-cluster（dev）与 cloud-managed（production）部署层级切换。
- **plan 时前置条件守卫**：`terraform_data.validate_inputs` 资源承载 20+ `lifecycle.precondition`，在 plan 阶段校验跨变量依赖（特性依赖、凭证要求、互斥入口控制器、拓扑约束）。
- **三入口控制器互斥**：Envoy Gateway（默认，Gateway API）、Istio Gateway、NGINX Ingress 三选一，共享 ALB target group。
- **企业加固（AWS）**：Network Firewall（FQDN 出口过滤）、WAFv2、CloudTrail、私有 EKS API + SSM bastion、IRSA、KMS 加密。
- **Sizing profiles**：`dev`、`production`、`production-large`，单变量切换。
- **企业特性开关**：LangGraph Platform/Deployments、Agent Builder、Insights（ClickHouse 分析）、Polly（AI 评估）、Fleet、SmithDB。
- **SmithDB 支持**：专用 RDS metastore、S3 桶、Karpenter 本地 NVMe 节点池（RAID0 instance-store + compute 两类 NodePool）。
- **独立特性数据库编排**：Fleet/Polly/Insights 共享 RDS + ElastiCache，通过 K8s Job 幂等创建逻辑数据库，Redis 逻辑 DB 索引隔离（DB 0 主安装 / 1 Fleet / 2 Polly / 3 Insights）。

## 部署层级

| 层级 | Postgres | Redis | ClickHouse | 用途 |
|---|---|---|---|---|
| Dev/POC | 集群内 | 集群内 | 集群内 | 演示、评估 |
| Production | 云托管（RDS/Cloud SQL/Azure DB） | 云托管 | LangChain Managed ClickHouse | 可扩展、持久化 |

> Blob 存储（S3/GCS/Azure Blob）始终必需——trace payload 不能存在 ClickHouse 中。集群内 ClickHouse 仅用于 dev/POC。

## 版本策略

- 全局标签 `vMAJOR.MINOR.PATCH`，始终从标签部署，不从分支部署。
- `MAJOR.MINOR` 跟踪 Helm chart 线，deploy.sh 固定为 `~0.16.0`（最新 0.16.x，绝不静默跳到 0.17）。
- `PATCH` 是模块修订号，任何仓库变更递增，不等于 chart 版本。
- chart 线切换是显式操作（`git checkout v0.17.*`），旧线移至 `release/<line>` 维护分支继续发布补丁。

## 快速开始

```bash
git fetch --tags
git checkout "$(git tag -l 'v0.16.*' --sort=-v:refname | head -1)"

cd modules/aws              # 或 azure/ gcp/
cp infra/terraform.tfvars.example infra/terraform.tfvars
cp infra/backend.tf.example infra/backend.tf
# 编辑 tfvars 和 backend

make quickstart             # 交互式向导
make apply                  # 编排基础设施
make deploy                 # Helm 部署 LangSmith
```

## 文档导航

### 参考

- [模块结构索引](/ai/langchain-ai/terraform/references/module-structure) — 四云子模块矩阵、Helm values 示例、运维脚本、CI 门禁、关键变量速查

### 源码事实与洞察

- [事实清单](/ai/langchain-ai/terraform/spec/facts) — 56 条带文件行号的源码事实
- [架构洞察](/ai/langchain-ai/terraform/spec/insights) — count 驱动条件编排与 plan 时 precondition 守卫网

## 目录结构

```
terraform/
├── index.md                    # 本文件
├── log.md                      # 变更日志
├── spec/
│   ├── facts.md                # 源码事实验证清单（56 条）
│   └── insights.md             # 1 个架构洞察
└── references/                 # 参考（1 篇）
    ├── module-structure.md
    └── index.md
```

## 相关项目

| 项目 | 路径 | 关系 |
|---|---|---|
| LangSmith SDK | [/langchain-ai/langsmith-sdk/](/ai/langchain-ai/langsmith-sdk/) | Terraform 部署的 LangSmith 平台的客户端 SDK |
| LangSmith CLI | [/langchain-ai/langsmith-cli/](/ai/langchain-ai/langsmith-cli/) | 与部署的 LangSmith 实例交互的 CLI 工具 |
