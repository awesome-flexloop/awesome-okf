---
type: spec
scope: terraform
name: facts
version: "0.1.0"
source: https://github.com/langchain-ai/terraform
description: langchain-ai/terraform 源码事实验证清单——从 Terraform HCL、Shell 脚本和文档中提取的编号事实
---

# terraform 事实清单

## 项目元信息与版本

F-001: 文件 `README.md` 第1-5行，仓库定位为"Terraform modules for deploying LangSmith Self-Hosted on AWS, Azure, GCP, and OpenShift"，将云基础（网络/集群/数据库/缓存/对象存储/密钥/DNS）与 LangSmith Helm 部署打包为可复用的生产级 Terraform。

F-002: 文件 `README.md` 第15-21行，支持四个云提供商：AWS（EKS，GA）、Azure（AKS，GA）、GCP（GKE，GA）、OpenShift（OCP/ROSA，Preview）。每个提供商目录是自包含部署，含 `Makefile`、`infra/` Terraform 布局、Helm values 和运维脚本。

F-003: 文件 `README.md` 第60-64行，版本标记为全局标签 `vMAJOR.MINOR.PATCH`：`MAJOR.MINOR` 跟踪所支持的 LangSmith Helm chart 线（deploy.sh 固定为 `~0.16.0`，即最新 0.16.x，绝不跳到 0.17）；`PATCH` 是模块修订号，任何仓库变更都递增，不等于 chart 版本。

F-004: 文件 `README.md` 第113-116行，当前 chart 线 0.16 从 `main` 分支发布（标签 `v0.16.*`）；0.15 为维护线，从 `release/0.15` 分支发布（标签 `v0.15.*`）。新线在 `cutover/<line>` 分支暂存，合并到 main 前不发布标签。

F-005: 文件 `CHANGELOG.md` 第1-8行，CHANGELOG 不由手工维护，每次合并到 `main` 和 `release/*` 分支时由 `.github/workflows/release.yml` 自动创建 GitHub Release。

F-006: 文件 `LICENSE`，许可证为 Apache 2.0。

## Terraform 版本与 Provider

F-007: 文件 `modules/aws/infra/versions.tf` 第2行，Terraform 核心版本要求 `>= 1.11.0`（Azure、GCP 同样要求 `>= 1.11.0`）。

F-008: 文件 `modules/aws/infra/versions.tf` 第4-33行，AWS root 所需 provider：`hashicorp/aws ~> 5.100`、`hashicorp/helm ~> 2.16`、`hashicorp/kubernetes ~> 2.37`、`gavinbunney/kubectl ~> 1.14`（用于 SmithDB Karpenter CR）、`hashicorp/random ~> 3.6`、`hashicorp/time ~> 0.10`。

F-009: 文件 `modules/azure/infra/versions.tf` 第4-36行，Azure root 所需 provider：`hashicorp/azurerm >= 4.27.0, < 5.0.0`（4.27 是接受 AGIC 子网 applicationGateways 委派名称的版本）、`Azure/azapi ~> 2.0`（Azure Managed Redis 通过 azapi 编排）、`hashicorp/kubernetes ~> 2.0`、`hashicorp/helm ~> 2.0`、`hashicorp/null ~> 3.0`、`hashicorp/time ~> 0.10`。

F-010: 文件 `modules/gcp/infra/versions.tf` 第4-37行，GCP root 所需 provider：`hashicorp/google ~> 5.0`、`hashicorp/google-beta ~> 5.0`、`hashicorp/kubernetes ~> 2.37`、`hashicorp/helm ~> 2.12`、`hashicorp/random ~> 3.6`、`hashicorp/time ~> 0.10`、`hashicorp/null ~> 3.2`、`hashicorp/local ~> 2.4`。

## 目录与模块结构

F-011: 文件 `modules/README.md` 第7-45行，每个提供商目录镜像统一布局：`infra/`（main.tf/locals.tf/variables.tf/outputs.tf/versions.tf/terraform.tfvars.example/backend.tf.example/modules/）、`helm/`（scripts/ + values/），以及 README.md/ARCHITECTURE.md/QUICK_REFERENCE.md/TROUBLESHOOTING.md/TEARDOWN.md。

F-012: 文件 `modules/README.md` 第58-68行，跨云子模块矩阵：networking（VPC/VNet/stub）、k8s-cluster（EKS/GKE/AKS/stub）、k8s-bootstrap（namespaces/RBAC）、postgres（RDS/Cloud SQL/Azure DB/stub）、redis（ElastiCache/Memorystore/Azure Cache/stub）、storage（S3/GCS/Azure Blob/stub）、dns（Route53+ACM/Cloud DNS/Azure DNS/OCP Route）、secrets（Secrets Manager/Secret Manager/Key Vault/k8s Secret）、iam/identity/scc（IRSA/Workload Identity/Managed Identity/SCC+RBAC）。

F-013: 文件 `AGENTS.md` 第9-13行，Terraform root 定义为拥有自己 `versions.tf` 的目录；`modules/<provider>/infra/modules/<child>/` 下的内部子模块不是 root，通过 `--call-module-type=all` 传递验证；两个携带 versions.tf 的子模块（azure keyvault、azure redis）仍为子模块，按路径而非深度识别。

F-014: 文件 `AGENTS.md` 第14-16行，`modules/ocp` 不进行 Terraform gate——OpenShift 移植版仍是 stub，没有 versions.tf；其 shell 脚本仍被 shellcheck 覆盖，HCL 仅运行 `terraform fmt -check`。

F-015: 文件 `modules/aws/infra/main.tf` 第190-1138行，AWS root 编排 14 个子模块：vpc、firewall、eks、redis、storage、postgres、cert_manager、dns、alb、cloudtrail、waf、bastion、k8s_bootstrap、smithdb，以及 kubectl_manifest 资源（Karpenter EC2NodeClass/NodePool）和 kubernetes_secret/job 资源。

F-016: 目录 `modules/byoc/aws/langsmith-byoc-role/`，第七个 Terraform root（比其他深一层），编排客户侧 IAM 角色和 break-glass 角色用于 BYOC（Bring Your Own Cloud），含 17 个 JSON policy 文件（acm/ec2-eni/eks/elasticache/elbv2/eventbridge/iam-karpenter/iam/kms/lambda/rds/route53/s3/secrets_manager/vpc 等）。

## 两遍部署与密钥管理

F-017: 文件 `README.md` 第26行，采用两遍部署：`infra/` 编排云基础，Helm 脚本安装 LangSmith chart。典型首次部署端到端需 20-30 分钟。

F-018: 文件 `README.md` 第27行，密钥通过云原生机密存储（AWS SSM Parameter Store、Azure Key Vault、GCP Secret Manager）管理，由 External Secrets Operator（ESO）同步到 Kubernetes，git 和 tfvars 中不含密钥。

F-019: 文件 `modules/aws/infra/main.tf` 第371-409行，AWS 创建专用 ESO IRSA 角色（`${local.base_name}-eso`），信任策略绑定 EKS OIDC provider 的 `system:serviceaccount:external-secrets:external-secrets` 服务账户，策略仅允许 `ssm:GetParameter`/`GetParameters`/`GetParametersByPath`，资源范围限定为 `arn:aws:ssm:${var.region}:*:parameter/langsmith/${local.base_name}/*`。

F-020: 文件 `modules/aws/infra/main.tf` 第15-35行，kubernetes 和 helm provider 均通过 EKS 集群端点 + CA 证书 + `aws eks get-token` exec 插件认证；kubectl provider 设置 `load_config_file = false`，同样使用 exec 插件。

## 部署层级与 Sizing

F-021: 文件 `README.md` 第39-43行，部署层级表：Dev/POC 层 Postgres/Redis/ClickHouse 均集群内；Production 层使用云托管 Postgres（RDS/Cloud SQL/Azure DB）和云托管 Redis，ClickHouse 推荐 LangChain Managed ClickHouse。

F-022: 文件 `README.md` 第44-46行，Blob 存储（S3/GCS/Azure Blob）始终必需——trace payload 不能存在 ClickHouse 中；集群内 ClickHouse 仅用于 dev/POC。

F-023: 文件 `README.md` 第29行，支持三种 sizing profile：`dev`、`production`、`production-large`，通过单个变量选择。

## 输入验证与特性开关

F-024: 文件 `modules/aws/infra/main.tf` 第56-188行，使用 `terraform_data.validate_inputs` 资源的 `lifecycle.precondition` 块在 plan 时执行跨变量校验（无法在单个 variable validation 块中表达的检查），共 20+ 条前置条件。

F-025: 文件 `modules/aws/infra/main.tf` 第59-61行，外部 Postgres 校验：`postgres_source == "external"` 时必须提供 `postgres_password`；外部 Redis 同理要求 `redis_auth_token` 且长度 ≥ 16。

F-026: 文件 `modules/aws/infra/main.tf` 第104-111行，特性依赖校验：`enable_agent_builder` 要求 `enable_deployments = true`；`enable_polly` 要求 `enable_deployments = true`。

F-027: 文件 `modules/aws/infra/main.tf` 第117-127行，Fleet 特性要求 `postgres_source == "external"` 且 `redis_source == "external"`，同时要求 `enable_deployments = true`（Fleet chat UI 通过 host-backend 解析 OAuth，host-backend 仅在 Deployments 启用时部署）。

F-028: 文件 `modules/aws/infra/main.tf` 第130-137行，standalone Polly 和 standalone Insights 同样要求外部 Postgres 和 Redis，但不要求 enable_deployments（它们运行独立的 api-server + queue）。

F-029: 文件 `modules/aws/infra/main.tf` 第182-186行，入口控制器互斥：Envoy Gateway、Istio Gateway、NGINX Ingress 三者最多启用一个（共享同一 ALB target group，第二个控制器会导致两者永久不健康）。Envoy Gateway 是默认值。

F-030: 文件 `modules/aws/infra/main.tf` 第140-142行，TLS 方式互斥：`tls_certificate_source = "letsencrypt"`（ALB HTTP-01）与 `create_cert_manager_irsa = true`（Route 53 DNS-01）不能同时为 true，两者都创建 ClusterIssuer/letsencrypt-prod。

F-031: 文件 `modules/aws/infra/variables.tf` 第7-16行，`region` 变量默认 `us-west-2`，带正则校验 `^[a-z]+-[a-z]+-[0-9]$`；`eks_cluster_version` 默认 `1.34`，校验格式 `^[0-9]+\.[0-9]+$`。

## 模块条件创建与状态迁移

F-032: 文件 `modules/aws/infra/main.tf` 第193行、208行、258行、315行，子模块普遍使用 `count` 条件创建：vpc/firewall 基于 `create_*` 布尔值，redis/postgres 基于 `*_source == "external"`，cert_manager/dns/cloudtrail/waf/bastion/smithdb 基于各自的 enable 开关。

F-033: 文件 `modules/aws/infra/main.tf` 第246-254行，使用 `moved` 块处理状态迁移：`module.postgres` → `module.postgres[0]`、`module.redis` → `module.redis[0]`，因引入 count 改变了模块地址，moved 块告知 Terraform 资源未变仅地址变更。

## 独立特性数据库编排

F-034: 文件 `modules/aws/infra/main.tf` 第619-622行，Redis 逻辑 DB 索引分配：DB 0 保留给主 LangSmith 安装，DB 1 给 Fleet，DB 2 给 Polly，DB 3 给 Insights。

F-035: 文件 `modules/aws/infra/main.tf` 第700-718行，standalone 特性连接 URL 构造：基于共享 RDS 管理员 URL 追加 `/langsmith_fleet`、`/langsmith_polly`、`/langsmith_insights` 数据库名；基于共享 ElastiCache URL 追加 `/1`、`/2`、`/3` 逻辑 DB 索引。

F-036: 文件 `modules/aws/infra/main.tf` 第724-792行，通过 `kubernetes_job_v1.standalone_db`（for_each 三个特性）运行幂等的 `postgres:16` Job 执行 `CREATE DATABASE`（先检查 `pg_database` 是否已存在），backoff_limit=6，ttl_seconds_after_finished=3600。管理员 URL 从 `langsmith-postgres` Secret 读取，不嵌入 Job 清单。

F-037: 文件 `modules/aws/infra/main.tf` 第798-874行，为每个启用的独立特性创建 pair of kubernetes Secret（`<feature>-postgres` 和 `<feature>-redis`），键名 `postgres_connection_url`/`redis_connection_url` 匹配 chart 的 existingSecretName 约定。

## SmithDB 编排

F-038: 文件 `modules/aws/infra/main.tf` 第877-927行，SmithDB（chart 0.16+）模块创建专用 metastore（RDS）、S3 bucket、IRSA 角色；SmithDB 共享 LangSmith namespace/release，不能独立运行，需要专用 metastore Postgres 和本地 NVMe 节点。

F-039: 文件 `modules/aws/infra/main.tf` 第961-972行，Karpenter 发现机制：子网通过 `karpenter.sh/discovery` 标签发现（VPC 创建时通过 `extra_private_subnet_tags` 打上，BYO VPC 时通过 `aws_ec2_tag` 资源打上）；安全组通过 EKS 托管集群标签 `kubernetes.io/cluster/<cluster>=owned` 发现（不自行在 node SG 上打 discovery 标签，避免 EKS 模块协调时丢弃）。

F-040: 文件 `modules/aws/infra/main.tf` 第986-1052行，创建两个 EC2NodeClass：`smithdb-instance-store`（`instanceStorePolicy = "RAID0"`，Karpenter 将本地 NVMe RAID0 用于 emptyDir 缓存）和 `smithdb-compute`（无本地 NVMe），均使用 gp3 加密根卷、IMDSv2（httpTokens required）、禁用公网 IP。

F-041: 文件 `modules/aws/infra/main.tf` 第1054-1137行，创建两个 NodePool：instance-store 节点带 `smithdb-local/instance-store=true` 标签和 NoSchedule taint，要求本地 NVMe ≥ 指定 GiB，disruption 策略 WhenEmpty（避免大缓存节点 churn）；compute 节点带 `smithdb-local/compute=true` 标签和 taint，disruption 策略 WhenEmptyOrUnderutilized。两者 expireAfter 均为 720h（30 天）。

## Helm 部署与 Chart 版本固定

F-042: 文件 `modules/aws/helm/scripts/deploy.sh`（目录存在），Helm 脚本包括 deploy.sh、init-values.sh、preflight-check.sh、setup-tls.sh、apply-eso.sh、uninstall.sh、test-e2e.sh 等。

F-043: 文件 `README.md` 第92-101行，0.16 chart 线携带 engineInsightsAgent、顶层 insights/polly 块，无 backend.agentBootstrap；deploy.sh 拒绝 0.16 线以外的任何 chart 版本（而非部署半配置版本），`CHART_VERSION` 环境变量只能收窄到 0.16 patch。

F-044: 目录 `modules/aws/helm/values/examples/`，提供 16 个 values 示例文件：langsmith-values.yaml（基础）、agent-builder、agent-deploys、dataplane、fleet、ingress-envoy-gateway、ingress-istio、insights、polly、sizing-dev/minimum/production/production-large、smithdb、standalone-insights、standalone-polly、dataplane-rbac，以及 SIZING.md 文档。

## CI 与质量门禁

F-045: 文件 `agents/check.sh` 第1-13行，机器评分脚本 `agents/check.sh`：无参数时检查所有 root + 所有脚本；`bash agents/check.sh modules/aws` 检查一个目录下的 root（仅 terraform）；`bash agents/check.sh --scripts` 对所有 tracked `*.sh` 运行 shellcheck（无 terraform，约 1 秒返回）。

F-046: 文件 `agents/check.sh` 第53-63行，`discover_roots()` 函数通过查找 `versions.tf` 发现 root（排除 `*/modules/*` 路径下的子模块），而非硬编码列表，确保新 root 不会被静默遗漏。

F-047: 文件 `agents/check.sh` 第22-23行，shellcheck 在 warning 级别门禁（仓库在该标准下干净）；tflint 仅在 error 级别门禁（HCL 仍有预存 warning）。CI 不覆盖级别设置，继承这些默认值，因此本地绿色即 PR 绿色。

F-048: 文件 `agents/check.sh` 第114-119行，每个 root 执行 `terraform init -backend=false`（无需云凭证或状态）后 `terraform validate`；tflint 使用提供商目录下的 `.tflint.hcl` 规则集，`--call-module-type=all` 验证所有子模块。

F-049: 文件 `AGENTS.md` 第32-35行，CI 工作流 `.github/workflows/checks.yaml` 每个 provider 一个 job 加一个 scripts job；新提供商目录需要在 `matrix.provider` 中添加入口；现有提供商下的新 root 无需修改工作流。

F-050: 文件 `.github/workflows/` 目录，包含 6 个 CI 工作流：checks.yaml（terraform validate + tflint + shellcheck）、tf_format.yaml（fmt 检查）、trivy.yml（漏洞扫描）、codeql.yml（代码分析）、release.yml（自动发布）、chart-line-check.yml。

## 安全加固

F-051: 文件 `README.md` 第34行，AWS 提供可选加固：AWS Network Firewall（FQDN 出口过滤）、WAFv2、CloudTrail、私有 EKS API 端点 + SSM bastion。

F-052: 文件 `modules/aws/infra/main.tf` 第504-543行，ALB 到网关代理的安全组规则按入口控制器类型条件创建：Envoy Gateway 端口 10080（非 root 偏移 10000）、Istio 端口 80（NET_BIND_SERVICE）、NGINX 端口 80；规则目标为 NODE 安全组（而非集群主安全组），因 VPC-CNI 将 SG 附加到 pod ENI。

F-053: 文件 `modules/aws/infra/main.tf` 第56-57行，provider 配置 `default_tags { tags = local.common_tags }`，所有 AWS 资源自动继承通用标签。

F-054: 文件 `modules/aws/infra/main.tf` 第592-595行，`time_sleep.wait_for_alb_webhook` 资源在 EKS 模块完成后等待 30 秒，让 AWS Load Balancer Controller 的 mutating webhook 就绪，否则 k8s-bootstrap 中的 Helm release（ESO、KEDA）会因 "no endpoints available for service aws-load-balancer-webhook-service" 失败。

## OpenShift 与 BYOC

F-055: 目录 `modules/ocp/`，OpenShift 移植版为 Preview 状态，infra 仅含 locals.tf、main.tf、backend.tf.example 和 dns 子模块（main.tf/outputs.tf/variables.tf），无 versions.tf；Helm 脚本含 deploy.sh、generate-secrets.sh、get-kubeconfig.sh、preflight-check.sh。

F-056: 文件 `modules/byoc/aws/langsmith-byoc-role/main.tf` 等，BYOC 角色模块创建 LangChain 运维 assumed 的 IAM 角色和 break-glass 角色，policies.tf 中定义细粒度权限策略，17 个 JSON policy 文件按服务拆分（acm.json、ec2-eni.json、eks.json、elasticache.json、elbv2.json、eventbridge.json、iam-karpenter-eks-profiles.json、iam.json、kms.json、lambda.json、rds.json、route53.json、route53_public.json、s3.json、secrets_manager.json、vpc.json、delete.json）。
