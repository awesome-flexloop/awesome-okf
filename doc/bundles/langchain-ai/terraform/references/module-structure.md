---
type: reference
scope: terraform
name: module-structure
version: "0.1.0"
source: https://github.com/langchain-ai/terraform
description: langchain-ai/terraform 模块结构索引——四云提供商 Terraform root、子模块矩阵、Helm values 示例与 CI 门禁
---

# Terraform 模块结构索引

## 仓库总览

| 路径 | 类型 | 说明 |
|---|---|---|
| `modules/aws/` | provider root | AWS EKS 部署（GA），含 infra/ + helm/ |
| `modules/azure/` | provider root | Azure AKS 部署（GA），含 infra/ + helm/ |
| `modules/gcp/` | provider root | GCP GKE 部署（GA），含 infra/ + helm/ |
| `modules/ocp/` | provider root | OpenShift 部署（Preview，stub 状态） |
| `modules/byoc/aws/langsmith-byoc-role/` | BYOC root | 客户侧 IAM 角色 + break-glass 角色（深一层） |
| `agents/check.sh` | CI 脚本 | terraform validate + tflint + shellcheck 统一门禁 |
| `.github/workflows/` | CI 工作流 | checks/tf_format/trivy/codeql/release/chart-line-check |

## 统一目录布局

每个 GA 提供商目录遵循相同布局（`modules/README.md:7-45`）：

```
modules/<provider>/
├── infra/
│   ├── main.tf                 # root 编排，provider 配置，子模块调用
│   ├── locals.tf               # 本地值（名称、标签、特性开关派生）
│   ├── variables.tf            # 输入变量（含 validation 块）
│   ├── outputs.tf              # 输出（集群端点、连接 URL 等）
│   ├── versions.tf             # terraform required_version + required_providers
│   ├── backend.tf.example      # 状态后端模板（S3/GCS/Azure Blob）
│   ├── terraform.tfvars.example
│   ├── scripts/                # 运维 shell 脚本（preflight/quickstart/tf-run 等）
│   └── modules/                # 内部子模块（非独立 root）
│       ├── <child>/
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
├── helm/
│   ├── scripts/                # deploy.sh / init-values.sh / preflight-check.sh 等
│   └── values/
│       ├── values.yaml         # 云特定默认值（checked in）
│       └── examples/           # 16 个场景化 values 示例
├── Makefile
├── README.md
├── ARCHITECTURE.md
├── QUICK_REFERENCE.md
├── SERVICES.md
├── TROUBLESHOOTING.md
├── TEARDOWN.md
└── .tflint.hcl
```

## 跨云子模块矩阵

| 子模块 | AWS | Azure | GCP | OCP | 云资源 |
|---|---|---|---|---|---|
| `networking` / `vpc` | ✅ `vpc` | ✅ `networking` | ✅ `networking` | stub | VPC / VNet |
| `k8s-cluster` / `eks` | ✅ `eks` | ✅ `k8s-cluster` | ✅ `k8s-cluster` | stub | EKS / AKS / GKE |
| `k8s-bootstrap` | ✅ | ✅ | ✅ | ✅ | namespaces / RBAC / Helm releases |
| `postgres` | ✅ | ✅ | ✅ | stub | RDS / Azure DB / Cloud SQL |
| `redis` | ✅ | ✅ | ✅ | stub | ElastiCache / Azure Cache / Memorystore |
| `storage` | ✅ | ✅ | ✅ | stub | S3 / Azure Blob / GCS |
| `dns` | ✅ | ✅ | ✅ | ✅ | Route53+ACM / Azure DNS / Cloud DNS / OCP Route |
| `secrets` / `keyvault` | via SSM+IRSA | ✅ `keyvault` | ✅ `secrets` | k8s Secret | Secrets Manager / Key Vault / Secret Manager |
| `iam` / `identity` | ✅ IRSA | ✅ Managed Identity | ✅ `iam` | ✅ `scc` | 工作负载身份 / SCC |
| `alb` / `ingress` | ✅ `alb` | — | ✅ `ingress` | — | ALB / GKE Ingress |
| `waf` | ✅ | ✅ | — | — | WAFv2 / Azure WAF |
| `bastion` | ✅ | ✅ | — | — | EC2 bastion / Azure Bastion |
| `firewall` | ✅ | — | — | — | AWS Network Firewall |
| `cloudtrail` / `diagnostics` | ✅ `cloudtrail` | ✅ `diagnostics` | — | — | CloudTrail / Azure Diagnostics |
| `cert-manager` | ✅ | — | — | — | cert-manager DNS-01 IRSA |
| `smithdb` | ✅ | — | ✅ `smithdb` + `smithdb-nodes` | — | SmithDB metastore + 节点池 |
| `storage` (ocp) | — | — | — | ✅ | OCP 存储 stub |
| `secrets` (ocp) | — | — | — | ✅ | k8s Secret stub |
| `scc` (ocp) | — | — | — | ✅ | SecurityContextConstraints |

## AWS 子模块详情

路径前缀：`modules/aws/infra/modules/`

| 子模块 | 核心资源 | 条件创建变量 |
|---|---|---|
| `vpc/` | VPC、公私子网、NAT 网关、路由表 | `create_vpc` |
| `firewall/` | AWS Network Firewall、FQDN 出口过滤 | `create_firewall`（需 create_vpc=true） |
| `eks/` | EKS 集群、节点组、Karpenter blueprints add-on、IRSA | 始终创建 |
| `redis/` | ElastiCache Redis（redis7 参数组） | `redis_source == "external"` |
| `postgres/` | RDS PostgreSQL（IAM 认证可选） | `postgres_source == "external"` |
| `storage/` | S3 桶、桶策略、TTL 生命周期、KMS、版本控制 | 始终创建 |
| `dns/` | Route53 hosted zone、ACM 证书、DNS 验证 | `langsmith_domain != "" && acm_certificate_arn == ""` |
| `alb/` | ALB、目标组、监听器、SG 规则 | 始终创建 |
| `waf/` | WAFv2 web ACL，关联 ALB | `create_waf` |
| `bastion/` | EC2 bastion（SSM Session Manager） | `create_bastion` |
| `cloudtrail/` | CloudTrail trail、S3 日志桶 | `create_cloudtrail` |
| `cert-manager/` | cert-manager IAM 角色 + Route53 策略 | `create_cert_manager_irsa` |
| `k8s-bootstrap/` | namespace、RBAC、ESO/KEDA Helm release、Secret | 始终创建 |
| `smithdb/` | RDS metastore、S3 桶、IRSA（含 irsa.tf/rds.tf/s3.tf 拆分） | `enable_smithdb` |

AWS root 还直接创建非模块资源：ESO IRSA 角色和 SSM 策略（`main.tf:371-409`）、ALB→网关 SG 规则（`:504-543`）、随机密码（`:603-607`）、Kubernetes Secret/Job（`:661-874`）、Karpenter EC2NodeClass/NodePool CR（`:986-1137`，通过 kubectl provider）。

## Azure 子模块详情

路径前缀：`modules/azure/infra/modules/`

| 子模块 | 核心资源 |
|---|---|
| `networking/` | VNet、子网、NSG |
| `k8s-cluster/` | AKS 集群（含独立 versions.tf） |
| `k8s-bootstrap/` | namespaces / RBAC |
| `postgres/` | Azure Database for PostgreSQL |
| `redis/` | Azure Cache for Redis（含独立 versions.tf，AMR 通过 azapi） |
| `storage/` | Azure Blob Storage |
| `dns/` | Azure DNS |
| `keyvault/` | Azure Key Vault（含 removed.tf 状态迁移、独立 versions.tf） |
| `waf/` | Azure WAF |
| `bastion/` | Azure Bastion |
| `diagnostics/` | Azure Monitor 诊断设置 |

## GCP 子模块详情

路径前缀：`modules/gcp/infra/modules/`

| 子模块 | 核心资源 |
|---|---|
| `networking/` | VPC、子网、Cloud NAT |
| `k8s-cluster/` | GKE 集群 |
| `k8s-bootstrap/` | namespaces / RBAC |
| `postgres/` | Cloud SQL for PostgreSQL |
| `redis/` | Memorystore for Redis |
| `storage/` | GCS 桶 |
| `dns/` | Cloud DNS + 托管证书 |
| `secrets/` | GCP Secret Manager |
| `iam/` | Workload Identity、IAM 绑定 |
| `ingress/` | GKE Ingress 配置 |
| `smithdb/` | Cloud SQL metastore + GCS 桶 + IAM（拆分为 cloudsql.tf/gcs.tf/iam.tf） |
| `smithdb-nodes/` | SmithDB 专用 GKE 节点池 |

## Helm values 示例

路径：`modules/<provider>/helm/values/examples/`

| 文件 | 场景 |
|---|---|
| `langsmith-values.yaml` | 基础默认值 |
| `langsmith-values-sizing-dev.yaml` | Dev/POC sizing |
| `langsmith-values-sizing-minimum.yaml` | 最小资源 sizing |
| `langsmith-values-sizing-production.yaml` | 生产 sizing |
| `langsmith-values-sizing-production-large.yaml` | 大规模生产 sizing |
| `langsmith-values-agent-builder.yaml` | Agent Builder 特性 |
| `langsmith-values-agent-deploys.yaml` | LangGraph Deployments 特性 |
| `langsmith-values-dataplane.yaml` | 多命名空间 dataplane 部署 |
| `langsmith-values-fleet.yaml` | Fleet 独立特性 |
| `langsmith-values-insights.yaml` | Insights（ClickHouse 分析） |
| `langsmith-values-standalone-insights.yaml` | 独立 Insights |
| `langsmith-values-polly.yaml` | Polly AI 评估监控 |
| `langsmith-values-standalone-polly.yaml` | 独立 Polly |
| `langsmith-values-smithdb.yaml` | SmithDB 集成 |
| `langsmith-values-ingress-envoy-gateway.yaml` | Envoy Gateway（Gateway API）入口 |
| `langsmith-values-ingress-istio.yaml` | Istio Gateway 入口 |
| `SIZING.md` | Sizing 指南文档 |

AWS 额外含 `langsmith-values-dataplane-rbac.yaml` 和 `langsmith-values-ingress-nginx.yaml`（NGINX Ingress）；Azure 额外含 `langsmith-values-ingress-agic.yaml`（AGIC）和 `letsencrypt-issuer-dns01.yaml`。

## 运维脚本

路径：`modules/<provider>/infra/scripts/`

| 脚本 | 用途 |
|---|---|
| `preflight.sh` | 部署前环境检查 |
| `quickstart.sh` | 交互式快速入门向导 |
| `setup-env.sh` | 环境变量设置（密码等） |
| `tf-run.sh` | Terraform 运行封装 |
| `status.sh` | 部署状态查询 |
| `clean.sh` | 资源清理 |
| `set-kubeconfig.sh`（AWS）/`get-kubeconfig.sh`（Azure/GCP） | 获取 kubeconfig |
| `hydrate-creds.sh`（AWS） | SSM 参数凭证填充 |
| `manage-ssm.sh` / `migrate-ssm.sh`（AWS） | SSM 参数管理/迁移 |
| `manage-keyvault.sh` / `seed-keyvault-secrets.sh`（Azure） | Key Vault 密钥管理 |
| `manage-secrets.sh`（GCP） | Secret Manager 管理 |
| `test-orchestrator.sh` / `test-permutations.sh` / `test-worker.sh`（AWS） | 部署排列测试 |

## CI 门禁

`agents/check.sh` 统一入口：

```bash
bash agents/check.sh                    # 所有 root + 所有脚本
bash agents/check.sh modules/aws        # 指定目录下的 root（仅 terraform）
bash agents/check.sh --scripts          # 所有 tracked *.sh（仅 shellcheck）
```

每个 root 执行：
1. `terraform init -backend=false`（无需云凭证）
2. `terraform validate`
3. `tflint --call-module-type=all`（使用 `modules/<provider>/.tflint.hcl` 规则集）

Shell 脚本全局执行 `shellcheck -S warning`（warning 级别门禁）。Root 通过查找 `versions.tf` 自动发现，排除 `*/modules/*` 子模块路径。

## 关键变量速查（AWS）

| 变量 | 默认值 | 说明 |
|---|---|---|
| `region` | `us-west-2` | AWS 区域 |
| `create_vpc` | `true` | 是否创建新 VPC |
| `postgres_source` | — | `in-cluster` 或 `external` |
| `redis_source` | — | `in-cluster` 或 `external` |
| `eks_cluster_version` | `1.34` | EKS K8s 版本 |
| `enable_deployments` | — | LangGraph Deployments 开关 |
| `enable_agent_builder` | — | Agent Builder（依赖 deployments） |
| `enable_fleet` | — | Fleet 独立特性（需外部 PG/Redis + deployments） |
| `enable_standalone_polly` | — | 独立 Polly（需外部 PG/Redis） |
| `enable_standalone_insights` | — | 独立 Insights（需外部 PG/Redis） |
| `enable_smithdb` | — | SmithDB 集成 |
| `enable_envoy_gateway` | 默认 true | Envoy Gateway 入口 |
| `enable_istio_gateway` | — | Istio Gateway 入口（三选一） |
| `enable_nginx_ingress` | — | NGINX Ingress 入口（三选一） |
| `tls_certificate_source` | — | `none`/`acm`/`letsencrypt` |
| `create_bastion` | — | SSM bastion |
| `create_firewall` | — | AWS Network Firewall |
| `create_waf` | — | WAFv2 |
| `create_cloudtrail` | — | CloudTrail |

完整变量列表见 `modules/aws/infra/variables.tf` 和 `terraform.tfvars.example`。
