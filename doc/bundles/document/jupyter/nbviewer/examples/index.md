# 示例文档索引

本目录包含 nbviewer 项目的实操示例文档，分为两大部分：**nbviewer应用使用示例**和 **nbviewer.org-deploy部署运维示例**。

## 第一部分：nbviewer 应用使用示例

| 示例 | 内容 |
|------|------|
| [基本配置示例](01-basic-config.md) | nbviewer常用配置文件示例，包括端口、缓存、限流、GitHub认证和CDN资源配置 |
| [本地文件服务配置](02-local-files.md) | 使用nbviewer服务本地Notebook文件的配置方法、安全选项、目录浏览和访问示例 |
| [自定义Provider开发](03-custom-provider.md) | 从零开发自定义nbviewer Provider的完整示例，包括轻量URL重写Provider和完整Handler Provider两种模式 |
| [Docker部署示例](04-docker-deploy.md) | nbviewer的Docker部署方案，包括单容器部署、docker-compose带Memcached、Nginx反向代理和生产环境配置 |

## 第二部分：nbviewer.org-deploy 部署运维示例

| 示例 | 内容 |
|------|------|
| [使用Invoke任务管理CDN](invoke-tasks.md) | invoke fastly同步Fastly CDN后端、invoke trigger-build触发Docker构建、invoke doitall完整流程的使用指南、可用/不可用任务清单、排错 |
| [本地部署调试](local-debug.md) | 如何在本地环境运行deploy.sh、helm diff预览变更、交互式确认部署、部署失败回滚、常见问题排查 |
| [手动升级nbviewer版本](manual-upgrade.md) | 手动检查nbviewer更新、使用update-nbviewer.py脚本、修改版本号、提交PR、验证部署、紧急回滚 |

## 快速参考

### nbviewer 应用常用命令

```bash
# 安装和启动
pip install nbviewer
python -m nbviewer                           # 默认启动（0.0.0.0:5000）
python -m nbviewer --port=8080 --processes=4  # 指定端口和进程数
python -m nbviewer --config-file=nbviewer_config.py  # 使用配置文件

# 生成配置
python -m nbviewer --generate-config

# Docker
docker run -p 8080:8080 jupyter/nbviewer
docker-compose up
```

### nbviewer.org-deploy 运维常用命令

```bash
# 部署
bash deploy.sh                     # 本地模式（预览+确认）
CI=true bash deploy.sh             # CI模式（直接部署）

# CDN管理
invoke fastly                      # 同步Fastly后端
invoke trigger-build               # 触发Docker Hub构建

# 测试
pytest                             # 运行线上冒烟测试

# 版本更新
python3 scripts/update-nbviewer.py # 检查并更新版本号

# Kubernetes
kubectl get pods -l app=nbviewer
kubectl rollout status -w deployment/nbviewer
helm history nbviewer
helm rollback nbviewer
```

```{toctree}
:maxdepth: 7

01-basic-config
02-local-files
03-custom-provider
04-docker-deploy
invoke-tasks
local-debug
manual-upgrade
```
