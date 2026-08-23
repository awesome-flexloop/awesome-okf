---
type: Concept
title: "Helm部署流程"
description: "deploy.sh脚本完整解析：KUBECONFIG设置、helm dep up、CI/本地双模式、helm diff、helm upgrade --cleanup-on-fail、kubectl rollout status"
tags: [nbviewer, deploy, helm, kubernetes, deploy-sh, ci, rollout]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: deploy-sh
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/deploy.sh"
    title: "deploy.sh"
  - id: cd-yml
    resource: "/references/cicd-source.md"
    title: "CI/CD信源"
---

# Helm部署流程

本文档详细解析 `deploy.sh` 部署脚本的执行流程，这是nbviewer.org部署的核心脚本。

## deploy.sh 完整源码

```bash
#!/bin/bash
set -euo pipefail

# TODO: move this to CI, don't make assumptions about local repo checkouts

export KUBECONFIG=$PWD/secrets/ovh-kubeconfig.yaml

nbviewer_chart="${NBVIEWER_CHART:-../nbviewer/helm-chart/nbviewer}"
echo "Is $nbviewer_chart up to date?"
helm dep up $nbviewer_chart

upgrade="upgrade nbviewer $nbviewer_chart -f config/nbviewer.yaml -f secrets/config/nbviewer.yaml"

if [[ -z "${CI:-}" ]]; then
  helm diff -C 5 $upgrade
  echo "Deploy these changes? (y|[N]) "
  read confirm

  if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "confirmed"
  else
    echo "Cancelled"
    exit 1
  fi
fi

echo "Upgrading..."
helm $upgrade --cleanup-on-fail

# watch deployment rollout
kubectl rollout status -w deployment/nbviewer
```

## 逐步骤解析

### 步骤0：错误处理

```bash
set -euo pipefail
```

| 选项 | 含义 |
|------|------|
| `-e` | 任何命令失败立即退出 |
| `-u` | 使用未定义变量时报错 |
| `-o pipefail` | 管道中任何命令失败则整个管道失败 |

这是严格的bash错误处理模式，确保部署过程中任何步骤失败都立即中止。

### 步骤1：设置KUBECONFIG

```bash
export KUBECONFIG=$PWD/secrets/ovh-kubeconfig.yaml
```

将kubeconfig路径设置为相对于当前工作目录的 `secrets/ovh-kubeconfig.yaml`。

**注意**：
- 路径使用 `$PWD`（绝对路径），不是相对路径
- kubeconfig文件通过git-crypt加密，必须先解锁
- 在GitHub Actions CI中，工作目录是checkout的仓库根目录

### 步骤2：确定Helm Chart路径

```bash
nbviewer_chart="${NBVIEWER_CHART:-../nbviewer/helm-chart/nbviewer}"
```

| 场景 | Chart路径 | 说明 |
|------|---------|------|
| 本地默认 | `../nbviewer/helm-chart/nbviewer` | 相对于部署仓库同级目录 |
| 设置了NBVIEWER_CHART | 使用环境变量值 | CI中使用 |
| CI环境（cd.yml） | `nbviewer/helm-chart/nbviewer` | checkout到`nbviewer/`子目录 |

在CI的cd.yml中，环境变量 `NBVIEWER_CHART: nbviewer/helm-chart/nbviewer` 指定了checkout到 `nbviewer/` 目录的chart路径。

### 步骤3：更新Chart依赖

```bash
helm dep up $nbviewer_chart
```

运行 `helm dependency update`，下载Chart依赖（如memcached等子chart）。确保依赖是最新的。

### 步骤4：构建Helm Upgrade命令

```bash
upgrade="upgrade nbviewer $nbviewer_chart -f config/nbviewer.yaml -f secrets/config/nbviewer.yaml"
```

构建Helm upgrade命令的核心部分（不含flag）：

| 参数 | 值 | 说明 |
|------|---|------|
| release名称 | `nbviewer` | Helm release名称 |
| Chart路径 | `$nbviewer_chart` | 本地Helm chart |
| Values文件1 | `-f config/nbviewer.yaml` | 公开配置 |
| Values文件2 | `-f secrets/config/nbviewer.yaml` | 加密密钥配置 |

**重要事实**：
- 命令中**不包含** `-f config/cdn.yaml` 或 `-f secrets/config/cdn.yaml`
- 命令中**不包含** `helm-values.deploy.yaml`（不生成合并values文件）
- 不使用 `GITHUB_REF_NAME` 等Git引用
- 两个values文件直接传递给helm，由helm合并

### 步骤5：双模式执行（CI vs 本地）

```bash
if [[ -z "${CI:-}" ]]; then
  # 本地模式：预览 + 确认
  helm diff -C 5 $upgrade
  echo "Deploy these changes? (y|[N]) "
  read confirm
  if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "confirmed"
  else
    echo "Cancelled"
    exit 1
  fi
fi
# CI模式：直接执行，跳过预览和确认
```

#### 本地模式（CI环境变量未设置）

1. 执行 `helm diff -C 5 $upgrade` 预览变更
   - 需要安装helm-diff插件
   - `-C 5` 显示变更上下文5行
   - 显示将要创建/更新/删除的Kubernetes资源
2. 交互式提示 "Deploy these changes? (y|[N])"
3. 输入 `y` 或 `Y` 继续，其他任何输入（包括空输入/回车）取消部署
4. 取消时输出 "Cancelled" 并以exit code 1退出

#### CI模式（CI环境变量已设置）

GitHub Actions 自动设置 `CI=true`，因此：
- 跳过 `helm diff` 预览
- 跳过交互式确认
- 直接执行部署

### 步骤6：执行Helm Upgrade

```bash
echo "Upgrading..."
helm $upgrade --cleanup-on-fail
```

执行实际的部署命令：

```bash
helm upgrade nbviewer <chart_path> \
    -f config/nbviewer.yaml \
    -f secrets/config/nbviewer.yaml \
    --cleanup-on-fail
```

**`--cleanup-on-fail` 标志**：如果升级失败（新Pod启动失败等），Helm会自动回滚到上一个成功版本，清理失败的新版本资源。这是一个重要的安全网。

**注意**：Helm upgrade是幂等操作——如果没有变更，不会重新部署。

### 步骤7：等待滚动更新完成

```bash
kubectl rollout status -w deployment/nbviewer
```

- `kubectl rollout status` 监视Deployment的滚动更新状态
- `-w`（watch）标志持续监视直到更新完成
- 当所有新Pod就绪且旧Pod终止后，命令返回成功
- 如果滚动更新失败（如镜像拉取失败、健康检查失败），此命令会超时或返回错误

## 本地vs CI执行对比

| 方面 | 本地模式 | CI模式 |
|------|---------|--------|
| CI环境变量 | 未设置 | `CI=true`（GitHub Actions自动） |
| Chart路径 | `../nbviewer/helm-chart/nbviewer` | `nbviewer/helm-chart/nbviewer`（通过env var） |
| helm diff | ✅ 执行预览（-C 5） | ❌ 跳过 |
| 交互式确认 | ✅ 需要输入y确认 | ❌ 跳过 |
| 部署执行 | `helm upgrade --cleanup-on-fail` | 相同 |
| 等待rollout | `kubectl rollout status -w` | 相同 |
| 失败处理 | exit 1 + set -e | exit 1 + set -e |
| CDN同步 | ❌ 不执行 | ❌ 不执行 |

## deploy.sh 不做的事情

根据源码确认，deploy.sh **不包含**以下操作：

| 操作 | 说明 |
|------|------|
| 生成helm-values.deploy.yaml | 不生成合并values文件，直接用两个-f参数 |
| 使用GITHUB_REF_NAME | 不读取Git分支/标签名 |
| 同步CDN（Fastly） | 不在部署后自动更新Fastly后端 |
| 运行测试 | pytest在cd.yml中单独执行，不在deploy.sh中 |
| 发送通知 | 不发送Slack/邮件通知 |
| 健康检查 | 不做自定义健康检查（依赖kubectl rollout status） |

## 部署后的手动步骤

deploy.sh执行成功后：
1. CI会自动运行 `pytest` 冒烟测试
2. 如果后端IP地址有变化（集群迁移等），需要手动运行 `invoke fastly` 更新CDN
3. Cloudflare DNS变更需要在Cloudflare Dashboard手动操作

## 相关文档

- [CI/CD与自动化](04-cicd-and-automation.md)
- [部署配置详解](03-deployment-config.md)
- [Fastly CDN管理](07-fastly-cdn.md)
- [本地调试示例](/examples/local-debug.md)
