---
type: Example
title: "手动升级nbviewer版本"
description: "手动检查nbviewer更新、修改版本号、提交PR、验证部署的完整操作指南"
tags: [nbviewer, deploy, upgrade, version, manual, pr]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: update-script
    resource: "/concepts/05-version-update.md"
    title: "版本更新机制"
  - id: cicd
    resource: "/concepts/04-cicd-and-automation.md"
    title: "CI/CD与自动化"
---

# 手动升级nbviewer版本

本文档演示如何手动检查和升级nbviewer版本。日常更新通常由watch-dependencies自动处理，但以下场景需要手动操作：
- 需要立即部署紧急修复
- 自动更新失败需要人工介入
- 需要验证特定commit的部署

## 前置知识

nbviewer版本存在于**两个位置**：

| 文件 | 变量 | 格式 | 示例 |
|------|------|------|------|
| `.github/workflows/cd.yml` | `NBVIEWER_VERSION` | 完整commit hash (40位) | `a53d108134e34e073344c1e2c6006a2eee86433a` |
| `config/nbviewer.yaml` | `image` | `jupyter/nbviewer:<short-hash>` | `jupyter/nbviewer:a53d108` |

两个版本号必须指向**同一个nbviewer commit**。

## 方法1：使用自动脚本（推荐）

```bash
# 1. 确保在main分支且最新
git checkout main
git pull

# 2. 创建新分支
git checkout -b update-nbviewer-manual

# 3. 运行更新脚本
python3 scripts/update-nbviewer.py

# 4. 查看变更
git diff
```

脚本输出示例：
```
chart_before='a53d108134e34e073344c1e2c6006a2eee86433a'
chart_after='b64e209245f45f84555d2f3d7117b3fff997544b'
chart_short='b64e209'
image_before='jupyter/nbviewer:a53d108'
image_after='jupyter/nbviewer:b64e209'
image_tag='b64e209'
Updating a53d108134e34e073344c1e2c6006a2eee86433a -> b64e209245f45f45f84555d2f3d7117b3fff997544b in .github/workflows/cd.yml
Updating jupyter/nbviewer:a53d108 -> jupyter/nbviewer:b64e209 in config/nbviewer.yaml
```

```bash
# 5. 提交并推送
git add .github/workflows/cd.yml config/nbviewer.yaml
git commit -m "Update nbviewer version to b64e209"
git push -u origin update-nbviewer-manual

# 6. 创建PR（使用gh CLI或GitHub UI）
gh pr create --title "Update nbviewer version to b64e209" \
    --body "Manual version update"
```

## 方法2：完全手动操作

如果脚本无法使用（如网络限制），可以手动更新：

### 步骤1：查找最新commit

访问 https://github.com/jupyter/nbviewer/commits/main ，找到要部署的commit，复制完整hash。

或使用git命令：
```bash
git ls-remote https://github.com/jupyter/nbviewer HEAD
# 输出: b64e209245f45f45f84555d2f3d7117b3fff997544b        HEAD
```

### 步骤2：查找对应的Docker镜像tag

访问 https://hub.docker.com/r/jupyter/nbviewer/tags ，找到对应commit的镜像tag。

nbviewer镜像tag通常是commit hash的前7位（如 `b64e209`）。

**重要**：等待Docker镜像构建完成（commit合并后几分钟），否则部署会因为镜像拉取失败而回滚。

### 步骤3：更新cd.yml

编辑 `.github/workflows/cd.yml`，找到 `env` 节的 `NBVIEWER_VERSION`：

```yaml
env:
  KUBECTL_VERSION: "v1.29.15"
  HELM_VERSION: "v3.12.0"
  KUBECONFIG: secrets/ovh-kubeconfig.yaml
  NBVIEWER_VERSION: "b64e209245f45f45f84555d2f3d7117b3fff997544b"  # 更新这里
  NBVIEWER_CHART: nbviewer/helm-chart/nbviewer
```

### 步骤4：更新config/nbviewer.yaml

编辑 `config/nbviewer.yaml`，更新 `image` 字段：

```yaml
replicas: 3
image: jupyter/nbviewer:b64e209  # 更新这里

memcached:
  # ... 其余配置不变
```

### 步骤5：提交PR

```bash
git checkout -b update-nbviewer-b64e209
git add .github/workflows/cd.yml config/nbviewer.yaml
git commit -m "Update nbviewer version to b64e209"
git push -u origin update-nbviewer-b64e209
gh pr create --title "Update nbviewer version to b64e209" \
    --body "- Updates nbviewer chart to jupyter/nbviewer@b64e209245f45f45f84555d2f3d7117b3fff997544b
- Update nbviewer image to \`jupyter/nbviewer:b64e209\`"
```

## 验证部署

PR合并后，CD流水线自动执行。可以通过以下方式验证：

### 1. 检查GitHub Actions

访问 https://github.com/jupyter/nbviewer.org-deploy/actions ，确认Deploy workflow：
- ✅ checkout步骤成功
- ✅ git-crypt解锁成功
- ✅ deploy.sh执行成功（helm upgrade + rollout status）
- ✅ pytest冒烟测试通过

### 2. 检查线上服务

```bash
# 运行冒烟测试
pytest tests/ -v

# 手动访问
curl -I https://nbviewer.org

# 检查首页示例notebook是否可访问
curl -I https://nbviewer.org/github/jupyter/notebook/blob/main/docs/source/examples/Notebook/Notebook%20Basics.ipynb
```

### 3. 检查Pod状态

```bash
export KUBECONFIG=secrets/ovh-kubeconfig.yaml
kubectl get pods -l app=nbviewer
# 所有Pod应为Running状态，且AGE显示刚刚创建
```

### 4. 确认版本

检查部署的镜像版本：
```bash
kubectl get deployment nbviewer -o jsonpath='{.spec.template.spec.containers[0].image}'
# 应输出: jupyter/nbviewer:b64e209
```

## 回滚（部署异常时）

如果新版本部署后出现问题：

### 快速回滚

```bash
# 方法1：Helm回滚
helm rollback nbviewer

# 方法2：revert PR
# 在GitHub上revert更新PR，合并后自动部署旧版本
```

### 回滚验证

回滚后：
1. 等待rollout完成：`kubectl rollout status -w deployment/nbviewer`
2. 运行冒烟测试：`pytest`
3. 确认旧版本正常服务

## 何时需要更新Fastly CDN

**常规版本更新不需要更新Fastly CDN。** 只有以下情况需要运行 `invoke fastly`：

- Kubernetes集群Service的外部IP变更
- 添加/移除后端节点
- 修改Fastly健康检查或超时配置

版本更新只改变Docker镜像tag，不改变后端IP地址，因此Fastly后端配置保持不变。

## 自动化替代方案

如果不是紧急更新，建议使用自动化流程：

1. **等待每日自动检查**：watch-dependencies每天UTC 5:00自动检查并创建PR
2. **手动触发workflow**：在GitHub UI上手动运行"Watch dependencies" workflow
3. **审查和合并**：审查自动生成的PR，确认变更合理后合并

自动化PR会包含版本间的PR列表摘要，方便审查变更内容。

## 相关文档

- [版本更新机制](../concepts/05-version-update.md)
- [CI/CD与自动化](../concepts/04-cicd-and-automation.md)
- [Helm部署流程](../concepts/06-helm-deploy-process.md)
- [本地部署调试](local-debug.md)
