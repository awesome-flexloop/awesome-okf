---
type: spec
title: Helm Chart 部署配置事实清单
description: langchain-ai/helm 仓库源码事实清单
tags:
- helm
- kubernetes
- langchain
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: helm-chart-structure
  resource: /langchain-ai/helm/references/chart-structure.md
  title: Helm Chart 结构索引
---

# Helm Chart 部署配置事实清单

> R阶段产出。所有事实编号 F-xxx，仅记录源码中可验证的客观内容，不含推断。

## 仓库元数据

- F-001: 仓库根目录 `README.md` L1 声明标题为 "Langchain Helm Charts"，L3 描述为 "This repository contains Helm charts for deploying Langchain applications on Kubernetes."
- F-002: Helm 仓库地址为 `https://langchain-ai.github.io/helm/`，通过 `helm repo add langchain https://langchain-ai.github.io/helm/` 添加，定义于 `README.md` L10
- F-003: 许可证为 Apache License 2.0，版权 Copyright (c) 2023 Langchain Inc.，定义于 `README.md` L19-25 与 `LICENSE` 文件
- F-004: 仓库根目录包含 `Makefile`、`README.md`、`SECURITY.md`、`LICENSE`、`.gitignore`，以及 `charts/`、`.github/`、`hack/` 三个子目录
- F-005: `charts/` 目录下包含 5 个独立 Helm Chart：`langgraph-cloud`、`langgraph-dataplane`、`langsmith`、`langsmith-auth-proxy`、`langsmith-observability`

## Chart 版本信息（Chart.yaml）

- F-006: `langgraph-cloud` Chart 版本 `0.3.2`，appVersion `"0.2.3"`，类型 `application`，维护者 Ankush (ankush@langchain.dev)，定义于 `charts/langgraph-cloud/Chart.yaml`
- F-007: `langgraph-dataplane` Chart 版本 `0.2.22`，appVersion `"0.16.36"`，类型 `application`，维护者 Ankush (ankush@langchain.dev)，定义于 `charts/langgraph-dataplane/Chart.yaml`
- F-008: `langsmith` Chart 版本 `0.17.0-rc.12`，appVersion `"0.17.12rc1"`，类型 `application`，维护者 Ankush (ankush@langchain.dev)，定义于 `charts/langsmith/Chart.yaml`
- F-009: `langsmith-auth-proxy` Chart 版本 `0.0.11`，appVersion `"1.37.0"`，类型 `application`，维护者 Brian (brian@langchain.dev)，定义于 `charts/langsmith-auth-proxy/Chart.yaml`
- F-010: `langsmith-observability` Chart 版本 `0.2.0`，appVersion `"0.2.0"`，类型 `application`，维护者 Romain (romain@langchain.dev)，标记为 `deprecated: true`，定义于 `charts/langsmith-observability/Chart.yaml` L6-7

## Chart 依赖关系

- F-011: `langsmith-observability` 是唯一声明 `dependencies` 的 Chart，依赖 8 个子Chart：prometheus-postgres-exporter 6.10.2、prometheus-redis-exporter 6.11.0、prometheus-nginx-exporter 1.6.0、kube-state-metrics 5.37.0（均来自 prometheus-community 仓库）、grafana 9.2.6、loki 6.30.1、tempo 1.23.1（均来自 grafana 仓库），定义于 `charts/langsmith-observability/Chart.yaml` L11-46
- F-012: 所有依赖均通过 `condition` 字段控制启用（如 `postgres-exporter.enabled`、`grafana.enabled`），定义于 `charts/langsmith-observability/Chart.yaml` L16-45
- F-013: `langsmith-observability` 目录包含 `Chart.lock` 锁定文件

## langgraph-cloud Chart 结构

- F-014: `langgraph-cloud` templates 目录包含 5 个服务子目录：`api-server/`、`mongo/`、`postgres/`、`queue/`、`redis/`，以及根级模板 `_helpers.tpl`、`NOTES.txt`、`http_route.yaml`、`ingress.yaml`、`secrets.yaml`、`virtual_service.yaml`
- F-015: `api-server/` 模板包含 `deployment.yaml`、`hpa.yaml`、`pdb.yaml`、`scaled-object.yaml`、`service-account.yaml`、`service.yaml` 共 6 个文件
- F-016: `postgres/` 模板包含 `pdb.yaml`、`secrets.yaml`、`service-account.yaml`、`service.yaml`、`stateful-set.yaml` 共 5 个文件
- F-017: `redis/` 模板包含 `deployment.yaml`、`pdb.yaml`、`secrets.yaml`、`service-account.yaml`、`service.yaml` 共 5 个文件
- F-018: `mongo/` 模板包含 `secrets.yaml`、`service.yaml`、`stateful-set.yaml` 共 3 个文件
- F-019: `queue/` 模板包含 `deployment.yaml`、`hpa.yaml`、`pdb.yaml`、`scaled-object.yaml`、`service-account.yaml` 共 5 个文件（无独立 service.yaml）
- F-020: `langgraph-cloud` 包含 `ci/` 目录，含 7 个 CI 测试 values 文件：`dev-kind-external-mongo-checkpointer-values.yaml`、`dev-kind-mongo-checkpointer-values.yaml`、`dev-kind-values.yaml`、`lightweight-config-values.yaml`、`lightweight-config-with-queue-values.yaml`、`mongo-checkpointer-values.yaml`、`readonly-config-values.yaml`
- F-021: `langgraph-cloud` 包含 `tests/` 目录，含 5 个 helm-unittest 测试文件：`mongo_test.yaml`、`pdb_test.yaml`、`priority_class_name_test.yaml`、`statefulset_update_strategy_test.yaml`、`validate_test.yaml`

## langgraph-cloud values.yaml 配置

- F-022: 全局配置包含 `nameOverride`、`fullnameOverride`、`namespace`、`commonAnnotations`、`commonLabels`、`commonVolumes`、`commonVolumeMounts`、`commonDnsConfig`（默认 ndots:4）、`clusterDomain`（默认 "cluster.local"），定义于 `values.yaml` L3-25
- F-023: `images` 配置 4 个镜像：`apiServerImage`（docker.io/langchain/langgraph-api，tag "3.11-28c1407"）、`postgresImage`（pgvector/pgvector:pg16）、`redisImage`（docker.io/redis:6）、`mongoImage`（mongo:7），支持 `images.registry` 前缀和 `imagePullSecrets`，定义于 `values.yaml` L27-49
- F-024: `config` 段包含 `skipValidation`、`existingSecretName`、`langGraphCloudLicenseKey`、`apiKey`、`numberOfJobsPerWorker`（默认10）、`httpMaxRequestBodyBytes`、`auth`（含 enabled/langSmithAuthEndpoint/langSmithTenantId），定义于 `values.yaml` L51-66
- F-025: 支持三种互斥的入口方式：`ingress`（传统 Ingress）、`gateway`（Gateway API HTTPRoute）、`istioGateway`（Istio VirtualService），三者同一时间只能启用一个，定义于 `values.yaml` L68-108
- F-026: `apiServer` 组件配置包含 containerPort 8000、deployment（默认 replicaCount 1，CPU limit 2000m/memory 4Gi）、HPA autoscaling（含 KEDA 支持）、service（默认 LoadBalancer，httpPort 80/httpsPort 443）、serviceAccount、pdb，定义于 `values.yaml` L110-191
- F-027: `queue` 组件默认 `enabled: false`，与 apiServer 结构类似但无独立 service，containerPort 8000，探针使用 HTTP GET `/ok`，定义于 `values.yaml` L193-261
- F-028: `postgres` 组件支持 `external.enabled` 切换外部数据库，内置使用 pgvector/pgvector:pg16 StatefulSet，默认 PVC 8Gi，CPU limit 4000m/memory 16Gi，定义于 `values.yaml` L263-325
- F-029: `redis` 组件支持 `external.enabled` 切换外部 Redis，内置使用 redis:6 Deployment，CPU limit 2000m/memory 4Gi，探针使用 `redis-cli ping`，定义于 `values.yaml` L327-402
- F-030: `mongo` 组件默认 `enabled: false`，支持 `external.enabled` 切换外部 MongoDB，内置使用 mongo:7 StatefulSet（单节点副本集，面向本地开发/CI），默认 PVC 8Gi，定义于 `values.yaml` L404-430

## langgraph-dataplane Chart 结构

- F-031: `langgraph-dataplane` templates 目录包含 3 个服务子目录：`listener/`、`operator/`、`redis/`，以及根级 `_helpers.tpl`、`ingress.yaml`、`secrets.yaml`
- F-032: `listener/` 模板包含 `deployment.yaml`、`hpa.yaml`、`pdb.yaml`、`rbac.yaml`、`service-account.yaml` 共 5 个文件
- F-033: `operator/` 模板包含 `config-map.yaml`、`crds.yaml`、`deployment.yaml`、`pdb.yaml`、`rbac.yaml`、`service-account.yaml`、`service.yaml` 共 7 个文件
- F-034: `redis/` 模板包含 `pdb.yaml`、`secrets.yaml`、`service-account.yaml`、`service.yaml`、`stateful-set.yaml` 共 5 个文件
- F-035: `langgraph-dataplane` 包含 `tests/` 目录，含 3 个测试文件：`deployment_priority_class_name_test.yaml`、`pdb_test.yaml`、`priority_class_name_test.yaml`

## langgraph-dataplane values.yaml 配置

- F-036: `images` 配置 3 个镜像：`listenerImage`（docker.io/langchain/langsmith-backend:0.16.36）、`redisImage`（docker.io/redis:7）、`operatorImage`（docker.io/langchain/langgraph-operator:0.1.36），定义于 `values.yaml` L29-45
- F-037: `config` 段包含 `existingSecretName`、`langsmithApiKey`、`hostBackendUrl`（默认 "https://api.host.langchain.com"）、`smithBackendUrl`（默认 "https://api.smith.langchain.com"）、`langsmithWorkspaceId`、`langgraphListenerId`、`hostQueue`（默认 "host"）、`watchNamespaces`、`enableLGPDeploymentHealthCheck`（默认 true），定义于 `values.yaml` L85-95
- F-038: `listener` 组件 containerPort 8080，启动命令为 `host_backend_entrypoint.sh` + `./listener_entrypoint.sh`，探针使用 HTTP GET `/health`（startup/readiness）和 `saq ... --check`（liveness，periodSeconds 60），定义于 `values.yaml` L97-151
- F-039: `operator` 组件默认 `enabled: true`、`createCRDs: true`、`kedaEnabled: true`，包含 `templates` 字段内嵌 Deployment/Service/DB(StatefulSet)/Redis 四种资源模板（使用 `${name}`/`${namespace}`/`${image}` 等占位符），定义于 `values.yaml` L176-382
- F-040: operator 内嵌的 DB 模板使用 `pgvector/pgvector:pg15` 镜像，Redis 模板使用 `redis:6` 镜像，定义于 `values.yaml` L304 和 L360
- F-041: dataplane 的 `redis` 组件使用 StatefulSet（与 langgraph-cloud 的 Deployment 不同），默认 CPU limit 4000m/memory 8Gi，PVC 8Gi，定义于 `values.yaml` L384-471

## langsmith Chart 结构

- F-042: `langsmith` templates 目录包含服务子目录：`ace-backend/`、`agent-features/`（含 `fleet/`、`insights/`、`polly/` 三个子模块）、`agent-gateway/`、`backend/`、`clickhouse/`，以及根级 `_helpers.tpl`、`NOTES.txt`
- F-043: `backend/` 模板包含 `auth-bootstrap.yaml`、`backfill-check.yaml`、`clickhouse-migrations.yaml`、`deployment.yaml`、`e2e-test.yaml`、`hpa.yaml`、`pdb.yaml`、`postgres-migrations.yaml`、`scaled-object.yaml`、`service-account.yaml`、`service.yaml` 共 11 个文件
- F-044: `agent-features/fleet/` 包含 `api-server/`、`postgres/`、`queue/`、`redis/`、`tool-server/`、`trigger-server/` 共 6 个子服务
- F-045: `agent-features/insights/` 和 `agent-features/polly/` 各包含 `api-server/`、`postgres/`、`queue/`、`redis/` 共 4 个子服务
- F-046: `langsmith` 包含 `examples/` 目录，含 15 个示例 values 文件（basic_config、autoscaling_config、basic_auth、blob_storage_config、ingress_config、lightweight_config、medium_size、mixed_oauth、mtls_config、read_only_config、redis_cluster、smithdb_alloydb_auth_proxy、tracing_config 等）
- F-047: `langsmith` 包含 `docs/` 目录，含 12 个运维文档（DELETE-ORGANIZATION、DELETE-TRACES、DELETE-WORKSPACE、ENABLE-FEATURE-FLAG-FOR-ORGANIZATION、GET-CLICKHOUSE-STATS、GET-QUERY-STATS、MIGRATE-OAUTH、RUN-SUPPORT-QUERY-CH、RUN-SUPPORT-QUERY-PG、UPGRADE、UPGRADE-0.2.x）
- F-048: `langsmith` 包含 `scripts/` 目录，含 Dockerfile、backfill_clickhouse.sh、create_marketplace_version.sh、delete_organization_sh、delete_trace_by_id.sh、delete_workspace.sh、enable_feature_flag_for_organization.sh、get_clickhouse_stats.sh、get_k8s_debugging_info.sh、get_query_stats.sh、migrate_no_auth.sh、mirror_langsmith_images.sh、push_helm_chart.sh、run_script_kubernetes.yaml、run_support_query_ch.sh、run_support_query_pg.sh
- F-049: `langsmith` 包含 `scripts/support_queries/` 子目录，含 `clickhouse/`（8个SQL文件）和 `postgres/`（16个SQL文件）支持查询脚本

## langsmith values.yaml 配置（关键部分）

- F-050: `images` 配置 12+ 个镜像：`aceBackendImage`、`backendImage`、`engineInsightsAgentImage`、`frontendImage`、`operatorImage`、`postgresImage`（postgres:14.7）、`redisImage`（redis:7）、`clickhouseImage`（clickhouse/clickhouse-server:25.12）、`agentBuilderImage`、`pollyAgentImage`、`smithdbImage`、`presidioAnalyzerImage`（可选）、`sandboxHostImage`（可选），定义于 `values.yaml` L60-124
- F-051: `preInstallManifests` 字段支持在 pre-install/pre-upgrade hook 中渲染前置清单（典型用例 ExternalSecret），默认为空数组 `[]`，定义于 `values.yaml` L9-33
- F-052: `sandboxes` 配置段默认 `enabled: false`，包含 `callbackSigningJwk`、`serviceUrlBaseUrl`、`quotas`（maxCpuCores 16/maxMemoryGb 64/maxSandboxes 1000）、`proxyCa`（generatedSecret/existingSecret 两种模式）、`juicefs`（s3/gs 存储后端）、`juicefsFormatJob`、`sandboxHost`（privileged 容器，需 KVM 节点），定义于 `values.yaml` L151-282
- F-053: `fleet` 配置段默认 `enabled: false`，包含 `namePrefix`、`enableTracing`、`encryptionKey`、`oauth`（多 OAuth 提供商配置）、`apiServer`、`queue`（默认 enabled: true）等子组件，定义于 `values.yaml` L284+
- F-054: 全局配置包含 `commonEnv`、`commonVolumes`、`commonVolumeMounts`、`commonInitContainers`、`commonPodSecurityContext`、`commonPodAnnotations`、`commonDnsConfig`（ndots:4）、`clusterDomain`，定义于 `values.yaml` L34-58

## langsmith-auth-proxy Chart 结构

- F-055: `langsmith-auth-proxy` templates 目录包含 `auth-proxy/` 子目录（`config-map.yaml`、`deployment.yaml`、`hpa.yaml`、`pdb.yaml`、`service-account.yaml`、`service.yaml`）及根级 `_helpers.tpl`、`http_route.yaml`、`ingress.yaml`
- F-056: `langsmith-auth-proxy` 包含 `e2e/` 目录，含 4 个端到端测试场景：`basic/`、`http-proxy/`、`oauth/`、`transformer/`，每个场景含 README.md、test.sh 和 values 配置
- F-057: `langsmith-auth-proxy` 包含 `ci/` 目录，含 5 个 CI values 文件：`auth-proxy-proxy-values.yaml`、`auth-proxy-readonly-values.yaml`、`auth-proxy-transformer-values.yaml`、`auth-proxy-values.yaml`
- F-058: `langsmith-auth-proxy` 包含 `tests/` 目录，含 8 个测试文件：`allowed_upstream_headers_test.yaml`、`common-values.yaml`、`jwks_uri_test.yaml`、`jwt_audiences_test.yaml`、`pdb_test.yaml`、`priority_class_name_test.yaml`、`transformer_test.yaml`、`upstream_path_prefix_test.yaml`

## langsmith-auth-proxy values.yaml 配置

- F-059: 镜像为 `docker.io/envoyproxy/envoy:v1.37-latest`，定义于 `values.yaml` L27-30
- F-060: `authProxy` 段基于 Envoy，containerPort 10000，核心配置包括：`upstream`（LLM 提供商 URL）、`jwtIssuer`（默认 "langsmith"）、`jwtAudiences`（必填）、`jwksJson`/`jwksUri`（二选一，jwksUri 优先）、`jwksCacheDurationSeconds`（默认300）、`jwtValidation.enabled`，定义于 `values.yaml` L36-61
- F-061: `authProxy.streamIdleTimeout` 默认 "300s"，针对 SSE 流式响应优化，定义于 `values.yaml` L63
- F-062: `authProxy.httpProxy` 支持通过 HTTP CONNECT 代理路由上游流量（Envoy 不遵守 HTTP_PROXY 环境变量），含 host/port/noProxy 配置，定义于 `values.yaml` L65-79
- F-063: `authProxy.extAuthz` 支持外部授权服务（ext_authz filter），可注入 LLM 提供商认证头，含 serviceUrl/timeout/allowedHeadersRegex/disallowedHeadersRegex/headersToAdd/allowedUpstreamHeaders/sendBody/maxRequestBytes，定义于 `values.yaml` L81-104
- F-064: `authProxy.transformer` 支持 ext_proc gRPC 过滤器进行请求/响应变换（可修改 header 和 body），含 serviceUrl/timeout/failureModeAllow/processingMode（6 个阶段的 SEND/SKIP/NONE/BUFFERED/STREAMED 控制），定义于 `values.yaml` L106-147
- F-065: `authProxy.rollout` 支持 ArgoCD Rollouts（enabled 时创建 Rollout 而非 Deployment），定义于 `values.yaml` L149-150

## langsmith-observability Chart 结构

- F-066: `langsmith-observability` templates 目录包含 `grafana/`（grafana-dashboards-configmap.yaml）、`mimir/`（config-map.yaml、service.yaml、stateful-set.yaml）、`otel/`（gateway.yaml、logs-sidecar.yaml、rbac-gateway.yaml、rbac-sidecar.yaml）及 `_helpers.tpl`
- F-067: `langsmith-observability` 包含 `dashboards/` 目录，含 6 个 Grafana Dashboard JSON：clickhouse.json、kube-state-metrics.json、langsmith-services.json、nginx.json、postgres.json、redis.json
- F-068: `langsmith-observability` 包含 `examples/` 目录，含 2 个示例：`e2e-stack.yaml`、`metric-exporters-only.yaml`

## CI/CD 与开发工具链

- F-069: `.github/workflows/helm_checks.yaml` 在 push/PR/merge_group 时触发，对 langgraph-cloud、langsmith、langsmith-auth-proxy 三个 Chart 执行矩阵测试，使用 Helm v3.12.1、chart-testing-action v2.6.0、helm-unittest 0.7.0、kind-action v0.25.0（kind v0.25.0），定义于 L1-57
- F-070: CI 流程包含：ct lint 版本检查 → ct lint Chart 检查 → helm unittest → kind 集群创建 → 预拉取镜像（redis:7、postgres:14.7、clickhouse-server:25.4、mongo:7）→ ct install 安装测试，定义于 `helm_checks.yaml` L44-143
- F-071: LangSmith CI 特有步骤：创建自签名 CA 证书和 Redis TLS Secret，通过 Bitnami Redis Chart 部署 TLS Redis 用于自定义 CA 测试，定义于 `helm_checks.yaml` L68-134
- F-072: `.github/workflows/release_charts.yaml` 在 push 到 main 或 *-stable 分支时触发，使用 helm/chart-releaser-action@v1.5.0 发布 Chart，并触发自托管 changelog bot，定义于 L1-47
- F-073: `Makefile` 定义 8 个本地开发 target：`cloud-dev-check`、`cloud-dev-template`、`cloud-dev-up`、`cloud-dev-smoke`、`cloud-dev-connect`、`cloud-dev-logs`、`cloud-dev-status`、`cloud-dev-down`，默认 CHART_DIR 为 `charts/langgraph-cloud`，定义于 Makefile L21-53
- F-074: `hack/` 目录包含 8 个 Shell 脚本：`ensure-safe-kube-context.sh`、`kind-create.sh`、`kind-delete.sh`、`install-langgraph-cloud.sh`、`smoke-langgraph-cloud.sh`、`port-forward-langgraph-cloud.sh`、`dump-k8s-debug.sh`、`lib.sh`，及 `fixtures/mongo.yaml`

## 模板与命名约定

- F-075: 所有 Chart 使用 `_helpers.tpl` 定义命名模板，langgraph-cloud 的模板前缀为 `langGraphCloud.*`（如 `langGraphCloud.name`、`langGraphCloud.fullname`、`langGraphCloud.labels`、`langGraphCloud.selectorLabels`、`langGraphCloud.chart`、`langGraphCloud.secretsName`），定义于 `templates/_helpers.tpl`
- F-076: fullname 模板逻辑：若 `fullnameOverride` 非空则使用之；否则若 release name 包含 chart name 则直接使用 release name；否则拼接 `release-name-chart-name`，统一截断到 63 字符并去除尾部 `-`，定义于 `_helpers.tpl` L13-24
- F-077: labels 模板遵循 Kubernetes 推荐标签：`helm.sh/chart`、`app.kubernetes.io/name`、`app.kubernetes.io/instance`、`app.kubernetes.io/version`、`app.kubernetes.io/managed-by`，定义于 `_helpers.tpl` L36-46
- F-078: Secret 命名支持 `existingSecretName` 覆盖，默认命名为 `<fullname>-secrets`（chart 级）、`<fullname>-postgres`（postgres 级）、`<fullname>-redis`（redis 级），定义于 `_helpers.tpl` L75-100+
- F-079: 每个 Chart 包含 `.helmignore` 文件
- F-080: 每个 Chart 的 README 由 `README.md.gotmpl` 模板生成（使用 helm-docs 工具），README.md.gotmpl 存在于 langgraph-cloud、langgraph-dataplane、langsmith、langsmith-auth-proxy 四个 Chart 中

## 探针与健康检查模式

- F-081: langgraph-cloud apiServer 使用 exec 探针执行 `python /api/healthcheck.py`（startup/readiness/liveness 三者相同，failureThreshold 6，periodSeconds 10），定义于 `values.yaml` L138-164
- F-082: langgraph-cloud queue 使用 HTTP GET `/ok` 探针（port 8000），定义于 `values.yaml` L222-242
- F-083: langgraph-cloud postgres 无显式探针配置（依赖 Kubernetes 默认），redis 使用 `redis-cli ping` exec 探针，定义于 `values.yaml` L352-378
- F-084: langgraph-dataplane listener 使用 HTTP GET `/health`（startup/readiness）和 `saq app.workers.queues.host_worker.settings --check`（liveness），定义于 `values.yaml` L119-141
- F-085: 所有部署组件均支持 `pdb.enabled`（默认 false）和 `autoscaling.enabled`（默认 false，含 HPA 和可选 KEDA scaledObject）
