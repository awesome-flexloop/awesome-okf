---
type: Example
title: "本地部署调试"
description: "如何在本地环境运行deploy.sh、helm diff预览变更、交互式确认部署、安装helm-diff插件"
tags: [nbviewer, deploy, local-debug, helm, helm-diff, kubectl]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: deploy-sh
    resource: "/references/cicd-source.md#deploysh在ci中的行为"
    title: "deploy.sh信源"
---

# 本地部署调试

本文档演示如何在本地环境运行deploy.sh进行部署调试，包括helm diff预览、交互式确认和问题排查。

## 前提条件

| 工具 | 安装方式 |
|------|---------|
| Helm v3.12.0+ | `curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \| bash` |
| kubectl v1.29+ | 或使用 `azure/setup-kubectl` 脚本 |
| helm-diff插件 | `helm plugin install https://github.com/databus23/helm-diff` |
| git-crypt | 系统包管理器安装 |
| Python 3.12+ | 系统包管理器或pyenv |

还需要：
- 有效的kubeconfig（`secrets/ovh-kubeconfig.yaml`，需git-crypt解锁）
- 本地checkout的nbviewer仓库（在同级目录）
- 对Kubernetes集群的访问权限

## 示例1：完整本地部署流程

```bash
# 1. 进入部署仓库
cd nbviewer.org-deploy

# 2. 解锁密钥文件
git-crypt unlock

# 3. 确认nbviewer仓库在同级目录（默认chart路径）
ls ../nbviewer/helm-chart/nbviewer/
# 如果在其他位置，设置环境变量：
# export NBVIEWER_CHART=/path/to/nbviewer/helm-chart/nbviewer

# 4. 安装helm-diff插件（如果未安装）
helm plugin install https://github.com/databus23/helm-diff

# 5. 运行部署脚本
bash deploy.sh
```

### 预期输出

```
Is ../nbviewer/helm-chart/nbviewer up to date?
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "stable" chart repository
Update Complete. ⎈Happy Helming!⎈
Saving 2 charts
Downloading memcached from repo ...
Deleting outdated charts

# helm diff输出（变更预览）
default, nbviewer, Deployment (apps) has changed:
  # ... 详细的资源变更差异 ...

Deploy these changes? (y|[N])
y
confirmed
Upgrading...
Release "nbviewer" has been upgraded. Happy Helming!
NAME: nbviewer
LAST DEPLOYED: ...
NAMESPACE: default
STATUS: deployed
REVISION: 42
TEST SUITE: None
Waiting for deployment "nbviewer" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "nbviewer" rollout to finish: 3 of 3 updated replicas are available...
deployment "nbviewer" successfully rolled out
```

### 取消部署

如果在确认提示下输入 `N` 或直接回车：

```
Deploy these changes? (y|[N])
N
Cancelled
# 脚本以exit code 1退出
```

## 示例2：只预览变更不部署

```bash
# 设置环境变量模拟helm命令
nbviewer_chart="${NBVIEWER_CHART:-../nbviewer/helm-chart/nbviewer}"

# 更新chart依赖
helm dep up $nbviewer_chart

# 只运行diff，不执行upgrade
helm diff -C 5 upgrade nbviewer $nbviewer_chart \
    -f config/nbviewer.yaml \
    -f secrets/config/nbviewer.yaml
```

这会显示将要变更的Kubernetes资源差异，但不执行实际部署。

## 示例3：CI模式本地测试

如果想跳过交互式确认（如测试脚本行为）：

```bash
# 设置CI环境变量，跳过helm diff和确认
CI=true bash deploy.sh
```

此模式下deploy.sh会直接执行helm upgrade，不预览不确认。

## 示例4：部署后验证

```bash
# 检查Pod状态
export KUBECONFIG=$PWD/secrets/ovh-kubeconfig.yaml
kubectl get pods -l app=nbviewer

# 检查Deployment状态
kubectl get deployment nbviewer

# 检查滚动更新历史
kubectl rollout history deployment/nbviewer

# 运行冒烟测试
pip install -r requirements.txt
pytest tests/ -v

# 直接访问服务
kubectl port-forward svc/nbviewer 8080:80
# 浏览器访问 http://localhost:8080
```

## 示例5：部署失败回滚

```bash
# 查看部署历史
helm history nbviewer

# 回滚到上一个版本
helm rollback nbviewer

# 回滚到指定版本
helm rollback nbviewer <REVISION_NUMBER>

# 查看回滚状态
kubectl rollout status -w deployment/nbviewer
```

注意：deploy.sh使用了 `--cleanup-on-fail`，如果部署过程中失败（不是Helm层面成功后Pod启动失败），Helm会自动回滚。但如果Helm认为部署成功但Pod启动失败，需要手动回滚。

## 常见问题排查

### helm diff: command not found

```
Error: unknown command "diff" for "helm"
```

**解决**：安装helm-diff插件
```bash
helm plugin install https://github.com/databus23/helm-diff
```

### KUBECONFIG文件不存在或无权限

```
error: stat secrets/ovh-kubeconfig.yaml: no such file or directory
```

**解决**：
1. 确认已运行 `git-crypt unlock`
2. 检查文件是否存在：`ls -la secrets/ovh-kubeconfig.yaml`
3. 解密后的文件应该是YAML格式，不是二进制

### Chart路径错误

```
Error: path "../nbviewer/helm-chart/nbviewer" not found
```

**解决**：
1. 确认nbviewer仓库已clone到同级目录
2. 或设置环境变量指定路径：`export NBVIEWER_CHART=/correct/path`
3. CI环境中应使用 `nbviewer/helm-chart/nbviewer`（相对路径）

### Helm upgrade失败

常见原因：
- 镜像标签不存在（等待Docker Hub构建完成）
- Kubernetes资源不足
- 配置语法错误

排查步骤：
```bash
# 查看Helm状态
helm status nbviewer

# 查看Pod事件
kubectl describe pod -l app=nbviewer

# 查看Pod日志
kubectl logs -l app=nbviewer --tail=50
```

### kubectl rollout status超时

```
error: timed out waiting for the condition
```

**解决**：
1. 检查Pod是否正常启动：`kubectl get pods`
2. 查看Pod事件：`kubectl describe pod <pod-name>`
3. 检查镜像是否可拉取
4. 可能需要手动回滚：`helm rollback nbviewer`

## 注意事项

1. **deploy.sh不使用 `-f` 标志指定额外values文件**（除了config/nbviewer.yaml和secrets/config/nbviewer.yaml两个默认文件）
2. **deploy.sh不生成helm-values.deploy.yaml**合并文件——两个values文件直接传给helm
3. **deploy.sh不同步CDN**——Fastly后端更新需单独运行 `invoke fastly`
4. **本地部署会影响生产环境**——kubeconfig指向OVH集群，确认你的变更安全后再部署
5. **建议先PR再合并**：日常更新通过watch-dependencies PR + CI部署，本地部署仅用于紧急修复和调试

## 相关文档

- [Helm部署流程](/concepts/06-helm-deploy-process.md)
- [快速上手](/concepts/01-getting-started.md)
- [Invoke任务使用](invoke-tasks.md)
